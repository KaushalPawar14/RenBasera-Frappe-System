import frappe
from frappe.model.document import Document
from frappe.utils import now
from frappe.model.workflow import apply_workflow, get_transitions


class TSFSecurityCheck(Document):

    def on_update(self):
        before = self.get_doc_before_save()
        if not before or not self.challan_ref:
            return

        prev_state = before.workflow_state
        curr_state = self.workflow_state


        if prev_state == curr_state:
            return


        if prev_state == "Pending":
            if curr_state == "Dispatched":
                self._validate_and_dispatch()
            elif curr_state == "Rejected":
                self.move_challan_to(target_state="Cancelled")
        elif prev_state == "Dispatched" and curr_state == "Completed":
            self._validate_return_odometer()
            self.move_delivery_log_to(target_state="Completed")


    # ------------------------------------------------------------------ #
    #  DISPATCH LOGIC                                                       #
    # ------------------------------------------------------------------ #


    def _validate_and_dispatch(self):
        if not self.delivery_out:
            frappe.throw("❌ Delivery Out table is empty. Cannot validate odometer reading.")

        gate_out = self.delivery_out[0]

        if gate_out.entered_odometer_reading:
            vehicle_name = frappe.get_value("TSF Dispatch Challan", self.challan_ref, "vehicle")

            if vehicle_name:
                last_odo = frappe.get_value("TSF Vehicle", vehicle_name, "last_odometer_reading") or 0

                if gate_out.entered_odometer_reading < last_odo:
                    frappe.throw(
                        f"❌ Odometer reading {gate_out.entered_odometer_reading} km is less than "
                        f"the vehicle's last recorded {last_odo} km. Cannot dispatch!"
                    )

                frappe.db.set_value(
                    "TSF Vehicle", vehicle_name,
                    "last_odometer_reading", gate_out.entered_odometer_reading
                )
                frappe.db.commit()

        self.create_delivery_log()
        self.create_vehicle_log()
        self.move_challan_to(target_state="Dispatched")

    def _validate_return_odometer(self):
        if not self.delivery_in:
            frappe.throw("❌ Delivery In table is empty. Cannot complete without return odometer reading.")

        if not self.delivery_out:
            frappe.throw("❌ Delivery Out table is empty. Cannot validate odometer reading.")

        gate_in_odo = self.delivery_in[0].entered_odometer_reading
        gate_out_odo = self.delivery_out[0].entered_odometer_reading

        if not gate_in_odo:
            frappe.throw("❌ Return odometer reading (Gate IN) is missing. Cannot complete.")

        if gate_in_odo < gate_out_odo:
            frappe.throw(
                f"❌ Return odometer reading {gate_in_odo} km cannot be less than "
                f"departure odometer reading {gate_out_odo} km. Cannot complete!"
            )
        else:
            self.add_end_odometer_reading(gate_in_odo)

    # ------------------------------------------------------------------ #
    #  DOCUMENT CREATORS                                                    #
    # ------------------------------------------------------------------ #

    def add_end_odometer_reading(self, reading):
        vehicle_log = frappe.get_doc("TSF Vehicle Log", self.challan_ref)
        vehicle_log.odometer_end = reading
        vehicle_log.save(ignore_permissions=True)

        vehicle_doc = frappe.get_doc("TSF Vehicle", vehicle_log.vehicle)
        vehicle_doc.last_odometer_reading = reading
        vehicle_doc.save(ignore_permissions=True)

        frappe.db.commit()
        frappe.msgprint(f"End odometer reading recorded as {reading} km.")

    def create_delivery_log(self):
        try:
            if frappe.db.exists("TSF Delivery Log", {"challan_ref": self.challan_ref}):
                return

            challan = frappe.get_doc("TSF Dispatch Challan", self.challan_ref)

            delivery_log = frappe.get_doc({
                "doctype": "TSF Delivery Log",
                "challan_ref": self.challan_ref,
                "delivery_info": [
                    {
                        "doctype": "TSF Delivery Log Item Table",
                        "center": row.name1 or row.center_name,
                        "delivered_qty": 0,
                        "arrival_time": None,
                    }
                    for row in (challan.center_list or [])
                ],
                "returning_info": [
                    {
                        "doctype": "TSF Return Trip Log Item Table",
                        "center": row.name1 or row.center_name,
                        "pickup_time": None,
                        "qty_verified": 0,
                    }
                    for row in (challan.center_list or [])
                ],
            })

            delivery_log.insert(ignore_permissions=True)
            frappe.db.commit()
            frappe.msgprint(f"Delivery Log {delivery_log.name} created for driver.")

        except Exception:
            frappe.log_error(title="Delivery Log Creation Error", message=frappe.get_traceback())
            raise

    def create_vehicle_log(self):
        try:
            if frappe.db.exists("TSF Vehicle Log", {"challan_ref": self.challan_ref}):
                return

            challan = frappe.get_doc("TSF Dispatch Challan", self.challan_ref)

            delivery_log_name = frappe.db.get_value(
                "TSF Delivery Log", {"challan_ref": self.challan_ref}, "name"
            )

            vehicle_log = frappe.get_doc({
                "doctype": "TSF Vehicle Log",
                "challan_ref": self.challan_ref,
                "vehicle": challan.vehicle,
                "date": frappe.utils.today(),
                "odometer_start": self.delivery_out[0].entered_odometer_reading or 0,
                "odometer_end": None,
                "delivery_log_ref": delivery_log_name,
                "return_trip_log_ref": None,
            })

            vehicle_log.insert(ignore_permissions=True)
            frappe.db.commit()
            frappe.msgprint(f"Vehicle Log {vehicle_log.name} created.")

        except Exception:
            frappe.log_error(title="Vehicle Log Creation Error", message=frappe.get_traceback())
            raise

    # ------------------------------------------------------------------ #
    #  WORKFLOW MOVERS                                                      #
    # ------------------------------------------------------------------ #

    def move_challan_to(self, target_state: str):
        try:
            challan = frappe.get_doc("TSF Dispatch Challan", self.challan_ref)

            if challan.workflow_state == target_state:
                return

            action = self._get_action_to_reach_state(challan, target_state)
            if not action:
                transitions = get_transitions(challan)
                frappe.throw(
                    f"Cannot move Dispatch Challan <b>{challan.name}</b> "
                    f"from <b>{challan.workflow_state}</b> to <b>{target_state}</b>.<br>"
                    f"Allowed next states: {[t.next_state for t in transitions]}<br>"
                    "➡️ Fix: Add the missing Workflow Transition or adjust roles."
                )

            apply_workflow(challan, action)
            challan.save(ignore_permissions=True)
            frappe.msgprint(f"Dispatch Challan {challan.name} moved to <b>{target_state}</b>.")

        except Exception:
            frappe.log_error(title="Move Challan Workflow Error", message=frappe.get_traceback())
            raise

    def move_delivery_log_to(self, target_state: str):
        try:
            delivery_log_name = frappe.db.get_value(
                "TSF Delivery Log", {"challan_ref": self.challan_ref}, "name"
            )

            if not delivery_log_name:
                frappe.throw(
                    f"Delivery Log not found for Challan <b>{self.challan_ref}</b>. Contact Developer."
                )

            delivery_log = frappe.get_doc("TSF Delivery Log", delivery_log_name)

            if delivery_log.workflow_state == target_state:
                return

            action = self._get_action_to_reach_state(delivery_log, target_state)
            if not action:
                transitions = get_transitions(delivery_log)
                frappe.throw(
                    f"Cannot move Delivery Log <b>{delivery_log.name}</b> "
                    f"from <b>{delivery_log.workflow_state}</b> to <b>{target_state}</b>.<br>"
                    f"Allowed next states: {[t.next_state for t in transitions]}<br>"
                    "➡️ Fix: Add the missing Workflow Transition or adjust roles."
                )

            apply_workflow(delivery_log, action)
            delivery_log.save(ignore_permissions=True)
            frappe.msgprint(f"Delivery Log {delivery_log.name} moved to <b>{target_state}</b>.")

        except Exception:
            frappe.log_error(title="Move Delivery Log Workflow Error", message=frappe.get_traceback())
            raise

    # ------------------------------------------------------------------ #
    #  HELPERS                                                              #
    # ------------------------------------------------------------------ #

    def _get_action_to_reach_state(self, doc, target_state: str):
        return next(
            (t.action for t in get_transitions(doc) if t.next_state == target_state),
            None
        )
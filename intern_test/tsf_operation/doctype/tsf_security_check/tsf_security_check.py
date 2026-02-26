import frappe
from frappe.model.document import Document
from frappe.model.workflow import apply_workflow, get_transitions


class TSFSecurityCheck(Document):

    # If your automation runs under a user without workflow roles,
    # set this to True to perform workflow as Administrator.
    RUN_AS_ADMIN = False

    def on_update(self):
        before = self.get_doc_before_save()
        if not before or not self.challan_ref:
            return

        prev_state = before.workflow_state
        curr_state = self.workflow_state

        if prev_state != "Pending":
            return

        if curr_state == "Dispatched":
            self._validate_and_dispatch()
        elif curr_state == "Rejected":
            self.move_challan_to(target_state="Cancelled")


    def _validate_and_dispatch(self):
        if self.entered_odometer_reading:
            vehicle_name = frappe.get_value("TSF Dispatch Challan", self.challan_ref, "vehicle")

            if vehicle_name:
                last_odo = frappe.get_value("TSF Vehicle", vehicle_name, "last_odometer_reading") or 0
                if self.entered_odometer_reading < last_odo:
                    frappe.throw(
                        f"❌ Odometer reading {self.entered_odometer_reading} km is less than "
                        f"vehicle's last recorded {last_odo} km. Cannot dispatch!"
                    )

                frappe.db.set_value("TSF Vehicle", vehicle_name, {
                    "last_odometer_reading": self.entered_odometer_reading,
                })

                frappe.db.commit()

        self.create_delivery_log()
        self.create_vehicle_log()
        self.move_challan_to(target_state="Dispatched")

    def move_challan_to(self, target_state: str):
        try:
            challan = frappe.get_doc("TSF Dispatch Challan", self.challan_ref)

            if challan.workflow_state == target_state:
                return

            action = self._get_action_to_reach_state(challan, target_state)
            if not action:
                transitions = get_transitions(challan)
                frappe.throw(
                    f"Failed to update Dispatch Challan:\n"
                    f"- Challan: {challan.name}\n"
                    f"- Current State: {challan.workflow_state}\n"
                    f"- Target State: {target_state}\n"
                    f"- Allowed Actions Now: {[t.action for t in transitions]}\n"
                    f"- Allowed Next States: {[t.next_state for t in transitions]}\n"
                    "➡️ Fix: Add a Workflow Transition for this target state (or adjust roles)."
                )

            if self.RUN_AS_ADMIN:
                self._apply_as_admin(challan, action)
            else:
                apply_workflow(challan, action)

            challan.save(ignore_permissions=True)
            frappe.msgprint(
                f"Dispatch Challan {challan.name} updated to '{challan.workflow_state}' via action '{action}'."
            )
        except Exception:
            frappe.log_error(title="Security Check Workflow Error", message=frappe.get_traceback())
            raise

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
                        "arrival_time": None
                    }
                    for row in (challan.center_list or [])
                ]
            })

            delivery_log.insert(ignore_permissions=True)
            frappe.db.commit()
            frappe.msgprint(f"Delivery Log {delivery_log.name} created for driver.")
        except Exception:
            frappe.log_error(title="Delivery Log Creation Error", message=frappe.get_traceback())

    def create_vehicle_log(self):
        try:
            if frappe.db.exists("TSF Vehicle Log", {"challan_ref": self.challan_ref}):
                return

            challan = frappe.get_doc("TSF Dispatch Challan", self.challan_ref)

            # Link delivery log that was just created
            delivery_log_name = frappe.db.get_value(
                "TSF Delivery Log", {"challan_ref": self.challan_ref}, "name"
            )

            vehicle_log = frappe.get_doc({
                "doctype": "TSF Vehicle Log",
                "challan_ref": self.challan_ref,
                "vehicle": challan.vehicle,
                "date": frappe.utils.today(),
                "odometer_start": self.entered_odometer_reading or 0,
                "odometer_end": None,
                "delivery_log_ref": delivery_log_name,
                "return_trip_log_ref": None,
            })

            vehicle_log.insert(ignore_permissions=True)
            frappe.db.commit()
            frappe.msgprint(f"Vehicle Log {vehicle_log.name} created.")
        except Exception:
            frappe.log_error(title="Vehicle Log Creation Error", message=frappe.get_traceback())

    def _get_action_to_reach_state(self, doc, target_state: str):
        return next(
            (t.action for t in get_transitions(doc) if t.next_state == target_state),
            None
        )

    def _apply_as_admin(self, doc, action: str):
        current_user = frappe.session.user
        try:
            frappe.set_user("Administrator")
            apply_workflow(doc, action)
        finally:
            frappe.set_user(current_user)
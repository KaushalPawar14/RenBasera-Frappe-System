import frappe
from frappe.model.document import Document

class TSFDeliveryLog(Document):
    def on_update(self):
        """Handle workflow state transitions"""
        
        if self.is_new():
            return
        
        if not self.has_value_changed("workflow_state"):
            return
        
        if self.flags.workflow_processed:
            return
        
        self.flags.workflow_processed = True
        
        if self.workflow_state == "Returning":
            frappe.msgprint("Workflow changed to Returning")
            self.create_security_record_if_missing()
            self.move_challan_to(target_state="Returning")  # ✅ Add this



    def create_security_record_if_missing(self):
        existing = frappe.db.exists("TSF Security Check", {"challan_ref": self.challan_ref})
        
        if existing:
            security_doc = frappe.get_doc("TSF Security Check", self.challan_ref)
            security_doc.append("delivery_in", {
                "checkpoint": "Gate IN",
                "qty_counted": None,
                "time": None,
                "entered_odometer_reading": -1
            })
            security_doc.save(ignore_permissions=True)
            frappe.msgprint(f"Security Check {security_doc.name} has been updated.")
        else:
            frappe.throw(
                f"Security Check record not found for {self.name} in <b>Security Check</b>. Contact Developer."
            )
    
    
    def move_challan_to(self, target_state: str):
        from frappe.model.workflow import apply_workflow, get_transitions
        try:
            challan = frappe.get_doc("TSF Dispatch Challan", self.challan_ref)

            if challan.workflow_state == target_state:
                return

            action = next(
                (t.action for t in get_transitions(challan) if t.next_state == target_state),
                None
            )

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
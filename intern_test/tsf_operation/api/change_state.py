# /home/frappe/frappe-bench/apps/intern_test/intern_test/tsf_operation/api/change_state.py

import frappe

@frappe.whitelist()
def change_state(challan_name, action):
    """
    Change workflow state of TSF Dispatch Challan
    Actions: submit_for_security, etc.
    """
    try:
        challan = frappe.get_doc("TSF Dispatch Challan", challan_name)
        
        if action == "submit_for_security":
            if challan.workflow_state.lower() != "draft":
                frappe.throw("Only Draft challans can be dispatched for security check")
            
            challan.workflow_state = "Pending Security Check"
            challan.save()
            frappe.db.commit()
            
            return {
                "success": True,
                "message": "Challan dispatched for security check",
                "new_state": challan.workflow_state
            }
        else:
            frappe.throw(f"Unknown action: {action}")
    
    except Exception as e:
        frappe.log_error(frappe.get_traceback(), "Change State Error")
        frappe.throw(f"Failed to change state: {str(e)}")
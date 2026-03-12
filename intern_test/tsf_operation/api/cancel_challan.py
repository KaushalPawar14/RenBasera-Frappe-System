# /home/frappe/frappe-bench/apps/intern_test/intern_test/tsf_operation/api/cancel_challan.py

import frappe

@frappe.whitelist()
def cancel_challan(challan_name):
    """
    Cancel a TSF Dispatch Challan
    """
    try:
        challan = frappe.get_doc("TSF Dispatch Challan", challan_name)
        
        if challan.workflow_state.lower() == "completed":
            frappe.throw("Completed challans cannot be cancelled")
        
        challan.workflow_state = "Cancelled"
        challan.save()
        frappe.db.commit()
        
        return {
            "success": True,
            "message": "Challan cancelled successfully",
            "new_state": challan.workflow_state
        }
    
    except Exception as e:
        frappe.log_error(frappe.get_traceback(), "Cancel Challan Error")
        frappe.throw(f"Failed to cancel challan: {str(e)}")
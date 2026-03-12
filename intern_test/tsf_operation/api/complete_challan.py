import frappe
from frappe import _

@frappe.whitelist()
def complete_challan(challan_id):
    """
    Whitelisted API to mark a TSF Dispatch Challan as Completed.
    
    Args:
        challan_id (str): Name/ID of the TSF Dispatch Challan document
    """
    try:
        # 1. Validate input
        if not challan_id:
            frappe.throw(_("Challan ID is required"))
        
        # 2. Load the document
        doc = frappe.get_doc("TSF Dispatch Challan", challan_id)
        
        # 3. Optional: Validate current state (to prevent accidental triggers)
        if doc.workflow_state != "Returning":
            frappe.throw(_("Challan '{0}' cannot be completed because its current state is '{1}'. It must be 'Returning'.").format(challan_id, doc.workflow_state))
            
        # 4. Update the workflow state
        # Adjust "Completed" if your actual Frappe workflow uses a different string (e.g., "Closed", "Done")
        doc.workflow_state = "Completed"
        
        # You can also set a custom completion timestamp field if you have one
        # doc.custom_completed_on = frappe.utils.now()
        
        # 5. Save and commit to the database
        doc.save(ignore_permissions=True)
        frappe.db.commit()
        
        # 6. Return success response to the Vue frontend
        return {
            "status": "success",
            "message": _("Challan {0} marked as Completed successfully.").format(challan_id),
            "workflow_state": doc.workflow_state
        }
        
    except frappe.DoesNotExistError:
        frappe.log_error(f"Challan not found: {challan_id}", "Complete Challan Error")
        frappe.throw(_("TSF Dispatch Challan record '{0}' not found").format(challan_id))
        
    except Exception as e:
        frappe.log_error(f"Error completing challan {challan_id}: {str(e)}", "Complete Challan Error")
        frappe.throw(_("Failed to complete challan: {0}").format(str(e)))
import frappe
from frappe import _

@frappe.whitelist()
def submit_delivery_in(
    check_id,
    driver_confirmed,
    vehicle_confirmed,
    tiffins_confirmed,
    entered_odometer_reading,
    driver_name=None,
    vehicle_name=None,
    total_tiffins=None
):
    """
    Whitelisted API to submit delivery IN confirmation and UPDATE/CREATE child record in delivery_in table.
    
    Args:
        check_id (str): Name of the parent TSF Security Check document
        driver_confirmed (int): 1 or 0
        vehicle_confirmed (int): 1 or 0
        tiffins_confirmed (int): 1 or 0
        entered_odometer_reading (float): Odometer value
        driver_name, vehicle_name, total_tiffins: Optional metadata
    """
    try:
        # 1. Validate input
        if not check_id:
            frappe.throw(_("Check ID is required"))
        
        # 2. Load parent document
        doc = frappe.get_doc("TSF Security Check", check_id)
        
        # 3. Update parent confirmation fields
        # Note: If you have separate fields for IN confirmations (e.g., custom_in_driver_confirmed), update them here.
        # Otherwise, this overwrites or re-confirms the existing fields.
        doc.custom_driver_confirmed = int(driver_confirmed)
        doc.custom_vehicle_confirmed = int(vehicle_confirmed)
        doc.custom_tiffins_confirmed = int(tiffins_confirmed)
        doc.custom_last_updated = frappe.utils.now()
        
        # 4. UPDATE existing child record in "delivery_in" table or CREATE if empty
        child = None
        
        if doc.delivery_in:
            # Get the first existing child record to update
            child = doc.delivery_in[0]
            child.entered_odometer_reading = float(entered_odometer_reading)
            child.qty_counted = int(total_tiffins) if total_tiffins else 0
            child.time = frappe.utils.now()
            child.confirmed_by = frappe.session.user
        else:
            # Fallback: Create new child record if none exists
            child = doc.append("delivery_in", {
                "entered_odometer_reading": float(entered_odometer_reading),
                "qty_counted": int(total_tiffins) if total_tiffins else 0,
                "time": frappe.utils.now(),
            })
            
        # 5. Set workflow state for Delivery In
        # Change "Completed" to whatever your actual workflow state name is (e.g., "Received", "Returned")
        doc.workflow_state = "Completed" 
        
        # 6. Save document
        doc.save(ignore_permissions=True)
        frappe.db.commit()
        
        # 7. Return success response
        return {
            "message": "Delivery In confirmation saved successfully",
            "doc_name": doc.name,
            "child_entry": child.name,
            "odometer_reading": child.entered_odometer_reading,
            "action": "updated" if len(doc.delivery_in) > 0 else "created",
            "workflow_state": doc.workflow_state
        }
        
    except frappe.DoesNotExistError:
        frappe.log_error(f"Document not found: {check_id}", "Delivery In Submission Error")
        frappe.throw(_("TSF Security Check record '{0}' not found").format(check_id))
        
    except (ValueError, TypeError) as e:
        frappe.log_error(f"Invalid input data: {str(e)}", "Delivery In Submission Error")
        frappe.throw(_("Invalid input data: {0}").format(str(e)))
        
    except Exception as e:
        frappe.log_error(f"Error saving delivery in: {str(e)}", "Delivery In Submission Error")
        frappe.throw(_("Failed to save Delivery In confirmation: {0}").format(str(e)))
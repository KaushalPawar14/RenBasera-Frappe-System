import frappe
from frappe import _

@frappe.whitelist()
def submit_delivery_out(
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
    Whitelisted API to submit delivery confirmation and UPDATE existing child record in delivery_out table.
    
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
        doc.custom_driver_confirmed = int(driver_confirmed)
        doc.custom_vehicle_confirmed = int(vehicle_confirmed)
        doc.custom_tiffins_confirmed = int(tiffins_confirmed)
        doc.custom_last_updated = frappe.utils.now()
        
        # 4. UPDATE existing child record in "delivery_out" table
        # Strategy: Find the first child record (or filter by a unique identifier if needed)
        child = None
        
        if doc.delivery_out:
            # Get the first existing child record to update
            child = doc.delivery_out[0]
            child.entered_odometer_reading = float(entered_odometer_reading)
            child.qty_counted = int(total_tiffins) if total_tiffins else 0
            child.time = frappe.utils.now()
            child.confirmed_by = frappe.session.user  # Optional: track who confirmed
        else:
            # Fallback: Create new child record if none exists (idempotent behavior)
            child = doc.append("delivery_out", {
                "entered_odometer_reading": float(entered_odometer_reading),
                "qty_counted": int(total_tiffins) if total_tiffins else 0,
                "time": frappe.utils.now(),
            })
            
        # --- NEW: Set workflow state to Dispatched ---
        doc.workflow_state = "Dispatched"
        
        # 5. Save document
        doc.save(ignore_permissions=True)
        frappe.db.commit()
        
        # 6. Return success response
        return {
            "message": "Delivery confirmation saved successfully",
            "doc_name": doc.name,
            "child_entry": child.name,
            "odometer_reading": child.entered_odometer_reading,
            "action": "updated" if doc.delivery_out and len(doc.delivery_out) > 0 else "created",
            "workflow_state": doc.workflow_state
        }
        
    except frappe.DoesNotExistError:
        frappe.log_error(f"Document not found: {check_id}", "Delivery Out Submission Error")
        frappe.throw(_("TSF Security Check record '{0}' not found").format(check_id))
        
    except (ValueError, TypeError) as e:
        frappe.log_error(f"Invalid input data: {str(e)}", "Delivery Out Submission Error")
        frappe.throw(_("Invalid input data: {0}").format(str(e)))
        
    except Exception as e:
        frappe.log_error(f"Error saving delivery out: {str(e)}", "Delivery Out Submission Error")
        frappe.throw(_("Failed to save confirmation: {0}").format(str(e)))
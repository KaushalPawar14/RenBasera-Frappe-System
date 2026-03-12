import frappe

@frappe.whitelist()
def create_challan(**kwargs):
    """
    Create a new TSF Dispatch Challan document
    """
    try:
        challan = frappe.get_doc({
            "doctype": "TSF Dispatch Challan",
            "driver": kwargs.get("driver"),
            "vehicle": kwargs.get("vehicle"),
            "total_tiffins_sent": kwargs.get("total_tiffins_sent"),
            "workflow_state": "Draft"
        })
        
        # Add boarded_items
        for item in kwargs.get("boarded_items", []):
            challan.append("boarded_items", {
                "item_name": item.get("item_name"),
                "unit": item.get("unit"),
                "qty_per_person": item.get("qty_per_person")
            })
        
        # Add center_list
        for center in kwargs.get("center_list", []):
            challan.append("center_list", {
                "name1": center.get("name1")
            })
        
        challan.insert()
        frappe.db.commit()
        
        return {"success": True, "challan_name": challan.name}
    
    except Exception as e:
        frappe.log_error(frappe.get_traceback(), "Challan Creation Error")
        frappe.throw(f"Failed to create challan: {str(e)}")
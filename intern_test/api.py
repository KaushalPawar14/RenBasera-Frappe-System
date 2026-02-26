import frappe
import json

def _as_list(val):
    """Accept list or JSON string, always return a list."""
    if val is None:
        return []
    if isinstance(val, str):
        val = val.strip()
        if not val:
            return []
        return json.loads(val)
    return val

def _require_roles(allowed_roles):
    """Raise if current user doesn't have any of the allowed roles."""
    roles = set(frappe.get_roles(frappe.session.user))
    if not roles.intersection(set(allowed_roles)):
        frappe.throw(
            f"Not permitted: only {', '.join(allowed_roles)} can create challan."
        )

@frappe.whitelist()
def get_current_user_info():
    user = frappe.session.user
    user_doc = frappe.get_doc("User", user)
    return {
        "user": user,
        "full_name": user_doc.full_name,
        "roles": [r.role for r in (user_doc.roles or [])]
    }

@frappe.whitelist()
def create_dispatch_challan(vehicle, driver, total_tiffins_sent, boarded_items, center_list):

    _require_roles(["TSF Distribution Manager", "TSF Admin"])

    boarded_items = _as_list(boarded_items)
    center_list   = _as_list(center_list)

    if not vehicle:
        frappe.throw("Vehicle is required.")
    if not driver:
        frappe.throw("Driver is required.")

    doc = frappe.get_doc({
        "doctype": "TSF Dispatch Challan",
        "vehicle": vehicle,
        "driver":  driver,
        "total_tiffins_sent": int(total_tiffins_sent or 0),

        "boarded_items": [
            {
                "doctype":        "TSF Tiffin Items Table",
                "item_name":      item.get("item_name"),
                "unit":           item.get("unit"),
                "qty_per_person": item.get("qty_per_person"),
            }
            for item in boarded_items
        ],

        "center_list": [
            {
                "doctype":       "TSF Center List Table",
                "name1":         c.get("name1"),        
                "delivered_qty": c.get("delivered_qty"),
            }
            for c in center_list
        ]
    })

    doc.insert()
    frappe.db.commit()
    return doc.name

# ─── Security Guard ──────────────────────────────────────────────────────────

@frappe.whitelist()
def security_check_action(security_check_name, action, checkpoint=None,
                           entered_odometer_reading=None, remarks=None):

    _require_roles(["TSF Security Guard", "TSF Admin"])

    if not security_check_name:
        frappe.throw("Security Check name is required.")
    if action not in ("Dispatch", "Reject"):
        frappe.throw("Invalid action. Must be 'Dispatch' or 'Reject'.")

    doc = frappe.get_doc("TSF Security Check", security_check_name)

    # Save editable fields before triggering workflow
    if checkpoint is not None:
        doc.checkpoint = checkpoint
    if entered_odometer_reading is not None:
        doc.entered_odometer_reading = int(entered_odometer_reading or 0)
    if remarks is not None:
        doc.remarks = remarks

    doc.save(ignore_permissions=False)

    # Map UI action → Frappe workflow action label
    workflow_action = "Verify Vehicle" if action == "Dispatch" else "Cancel"

    apply_workflow(doc, workflow_action)
    frappe.db.commit()

    return {"status": "success", "action": workflow_action, "doc": security_check_name}
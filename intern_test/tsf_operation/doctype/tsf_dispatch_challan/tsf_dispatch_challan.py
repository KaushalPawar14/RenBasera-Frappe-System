# Copyright (c) 2026, Akash Tomar and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document

class TSFDispatchChallan(Document):
    def on_update(self):
        before = self.get_doc_before_save()
        if not before:
            return

        # Draft -> Pending Security Check
        if before.workflow_state == "Draft" and self.workflow_state == "Pending Security Check":
            self.create_security_record_if_missing()
            self.mark_driver_vehicle_onTrip()

        # Any State -> Cancelled
        if self.workflow_state == "Cancelled" and before.workflow_state != "Cancelled":
            self.mark_driver_vehicle_available()

    def create_security_record_if_missing(self):
        # Prevent duplicate security checks for same challan
        existing = frappe.db.exists("TSF Security Check", {"challan_ref": self.name})
        if existing:
            return

        security_doc = frappe.get_doc({
            "doctype": "TSF Security Check",
            "challan_ref": self.name,
            "checkpoint": "Gate Out",
        })
        
        security_doc.insert(ignore_permissions=True)
        frappe.msgprint(f"Security Check {security_doc.name} has been created.")

    def mark_driver_vehicle_onTrip(self):
        if not self.vehicle:
            frappe.throw("Vehicle is not set.")

        vehicle_doc = frappe.get_doc("TSF Vehicle", self.vehicle)
        vehicle_doc.vehicle_status = "On Trip"
        vehicle_doc.save(ignore_permissions=True)
        frappe.db.commit()

        if not self.driver:
            frappe.throw("Driver is not set.")

        driver_doc = frappe.get_doc("TSF Driver", self.driver)
        driver_doc.driver_status = "On Trip"
        driver_doc.save(ignore_permissions=True)

    def mark_driver_vehicle_available(self):
        if self.vehicle:
            vehicle_doc = frappe.get_doc("TSF Vehicle", self.vehicle)
            vehicle_doc.vehicle_status = "Available"
            vehicle_doc.save(ignore_permissions=True)

        if self.driver:
            driver_doc = frappe.get_doc("TSF Driver", self.driver)
            driver_doc.driver_status = "Available"
            driver_doc.save(ignore_permissions=True)

        frappe.db.commit()
        frappe.msgprint("Vehicle and Driver have been marked as Available.")
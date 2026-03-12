# import frappe
# from frappe.model.document import Document

import frappe
from frappe.model.document import Document
from frappe.utils import now_datetime


class RNBStockEntry(Document):

    def on_update(self):
        if self.workflow_state == "Submitted":

            self.stock_entry_time = now_datetime()
            self.entry_done_by = frappe.session.user
            for row in self.stock_purchase:
                update_stock_availability(
                    item=row.item_name,
                    purchased_qty=row.quantity
                )


def update_stock_availability(item, purchased_qty=0, issued_qty=0):

    availability = frappe.db.get_value(
        "RNB Stock Availability",
        {"item": item},
        "name"
    )

    if not availability:
        doc = frappe.new_doc("RNB Stock Availability")
        doc.item = item
        doc.total_purchased_qty = 0
        doc.total_issued_qty = 0
        doc.available_qty = 0
        doc.insert(ignore_permissions=True)
    else:
        doc = frappe.get_doc("RNB Stock Availability", availability)

    doc.total_purchased_qty += purchased_qty
    doc.total_issued_qty += issued_qty

    doc.available_qty = (
        doc.total_purchased_qty
        - doc.total_issued_qty
    )

    if doc.available_qty < 0:
        frappe.throw("Stock cannot go negative.")

    doc.save(ignore_permissions=True)
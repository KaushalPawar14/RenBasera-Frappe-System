import frappe
from frappe.model.document import Document


class RNBStockAvailability(Document):

    def before_insert(self):
        """Prevent duplicate stock availability record for same item"""
        if frappe.db.exists("RNB Stock Availability", {"item": self.item}):
            frappe.throw("Stock Availability already exists for this Item.")

        # Initialize all numeric fields safely
        self.total_purchased_qty = self.total_purchased_qty or 0
        self.total_issued_qty = self.total_issued_qty or 0

        self._recalculate_available()

    def before_save(self):
        """Always recalculate available quantity before saving"""
        self.total_purchased_qty = self.total_purchased_qty or 0
        self.total_issued_qty = self.total_issued_qty or 0

        self._recalculate_available()

    def validate(self):
        """Final protection against negative stock"""
        if self.available_qty < 0:
            frappe.throw("Available Quantity cannot be negative.")

    # def on_trash(self):
    #     """Prevent deletion of stock availability record"""
    #     frappe.throw("Stock Availability records cannot be deleted.")

    # -----------------------------
    # Internal Calculation Method
    # -----------------------------
    def _recalculate_available(self):
        self.available_qty = (
            self.total_purchased_qty
            - self.total_issued_qty
        )

        if self.available_qty < 0:
            frappe.throw("Stock calculation error: Negative stock detected.")
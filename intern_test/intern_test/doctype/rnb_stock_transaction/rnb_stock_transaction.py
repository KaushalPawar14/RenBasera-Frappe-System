# import frappe
# from frappe.model.document import Document
# from frappe.utils import now_datetime

# # class RNBStockTransaction(Document):

# #     def validate(self):

# #         if self.quantity <= 0:
# #             frappe.throw("Quantity must be greater than 0")

# #         availability_name = frappe.db.get_value(
# #             "RNB Stock Availability",
# #             {"item": self.stock_item},
# #             "name"
# #         )

# #         if not availability_name:
# #             frappe.throw("No stock record found for this item.")

# #         availability = frappe.get_doc(
# #             "RNB Stock Availability",
# #             availability_name
# #         )

# #         if self.transaction_type == "Issued":

# #             if self.quantity > availability.available_qty:
# #                 frappe.throw("Not enough stock available.")

# #             update_stock_availability(
# #                 item=self.stock_item,
# #                 issued_qty=self.quantity
# #             )


# # def update_stock_availability(item, purchased_qty=0, issued_qty=0):

# #     availability = frappe.db.get_value(
# #         "RNB Stock Availability",
# #         {"item": item},
# #         "name"
# #     )

# #     if not availability:
# #         frappe.throw("Stock record not found.")

# #     doc = frappe.get_doc("RNB Stock Availability", availability)

# #     doc.total_purchased_qty += purchased_qty
# #     doc.total_issued_qty += issued_qty

# #     doc.available_qty = (
# #         doc.total_purchased_qty
# #         - doc.total_issued_qty
# #     )

# #     if doc.available_qty < 0:
# #         frappe.throw("Stock cannot go negative.")

# #     doc.save(ignore_permissions=True)


# class RNBStockTransaction(Document):

#     def validate(self):

#         if self.quantity <= 0:
#             frappe.throw("Quantity must be greater than 0")

#         availability_name = frappe.db.get_value(
#             "RNB Stock Availability",
#             {"item": self.stock_item},
#             "name"
#         )

#         if not availability_name:
#             frappe.throw("No stock record found for this item.")

#         availability = frappe.get_doc(
#             "RNB Stock Availability",
#             availability_name
#         )

#         # Only check stock availability # When issuing stock
#         if self.transaction_type == "Issued":
#             if self.quantity > availability.available_qty:
#                 frappe.throw("Not enough stock available.")

#         # When receiving stock  # When receiving stock
#         if self.transaction_type == "Received":

#             if availability.total_issued_qty <= 0:
#                 frappe.throw("No stock is currently issued for this item.")

#             if self.quantity > availability.total_issued_qty:
#                 frappe.throw("Cannot receive more than issued quantity.")

#     def on_update(self):

#         # Update stock only when Approved
#         if self.workflow_state == "Approved" and not self.flags.stock_updated:

#             self.date = now_datetime()
#             self.transaction__by = frappe.session.user

#             update_stock_availability(
#                 item=self.stock_item,
#                 qty=self.quantity,
#                 transaction_type=self.transaction_type
#             )
#             self.flags.stock_updated = True


# def update_stock_availability(item, qty, transaction_type):

#     availability = frappe.db.get_value(
#         "RNB Stock Availability",
#         {"item": item},
#         "name"
#     )

#     if not availability_name:
#         frappe.throw("Stock record not found.")

#     doc = frappe.get_doc("RNB Stock Availability", availability_name)

#     if transaction_type == "Issued":

#         doc.total_issued_qty += qty
#         doc.available_qty -= qty

#     elif transaction_type == "Received":

#         doc.total_issued_qty -= qty
#         doc.available_qty += qty

#     if doc.available_qty < 0:
#         frappe.throw("Stock cannot go negative.")

#     if doc.total_issued_qty < 0:
#         frappe.throw("Issued quantity cannot be negative.")


#     doc.save(ignore_permissions=True)




import frappe
from frappe.model.document import Document
from frappe.utils import now_datetime


class RNBStockTransaction(Document):

    def validate(self):

        if self.quantity <= 0:
            frappe.throw("Quantity must be greater than 0")

        availability_name = frappe.db.get_value(
            "RNB Stock Availability",
            {"item": self.stock_item},
            "name"
        )

        if not availability_name:
            frappe.throw("No stock record found for this item.")

        availability = frappe.get_doc(
            "RNB Stock Availability",
            availability_name
        )

        if self.transaction_type == "Issued":

            if self.quantity > availability.available_qty:
                frappe.throw("Not enough stock available.")

        if self.transaction_type == "Received":

            if availability.total_issued_qty <= 0:
                frappe.throw("No stock is currently issued.")

            if self.quantity > availability.total_issued_qty:
                frappe.throw("Cannot receive more than issued quantity.")


    def on_update(self):

        # APPROVED → Apply Stock Change
        if self.workflow_state == "Approved" and not self.flags.stock_updated:

            self.date = now_datetime()
            self.transaction_by = frappe.session.user

            update_stock_availability(
                item=self.stock_item,
                qty=self.quantity,
                transaction_type=self.transaction_type
            )
            if self.transaction_type == "Issued":
                frappe.msgprint(
                    f"{self.quantity} units of {self.stock_item} successfully issued.",
                    indicator="green"
                )

            elif self.transaction_type == "Received":
                frappe.msgprint(
                    f"{self.quantity} units of {self.stock_item} successfully received.",
                    indicator="green"
                )
            
            self.flags.stock_updated = True


        # CANCELLED → Undo Stock Change
        if self.workflow_state == "Cancelled":

            reverse_stock_availability(
                item=self.stock_item,
                qty=self.quantity,
                transaction_type=self.transaction_type
            )


def update_stock_availability(item, qty, transaction_type):

    availability_name = frappe.db.get_value(
        "RNB Stock Availability",
        {"item": item},
        "name"
    )

    if not availability_name:
        frappe.throw("Stock record not found.")

    doc = frappe.get_doc("RNB Stock Availability", availability_name)

    if transaction_type == "Issued":

        doc.total_issued_qty += qty
        doc.available_qty -= qty

    elif transaction_type == "Received":

        doc.total_issued_qty -= qty
        doc.available_qty += qty

    doc.save(ignore_permissions=True)


def reverse_stock_availability(item, qty, transaction_type):

    availability_name = frappe.db.get_value(
        "RNB Stock Availability",
        {"item": item},
        "name"
    )

    doc = frappe.get_doc("RNB Stock Availability", availability_name)

    if transaction_type == "Issued":

        doc.total_issued_qty -= qty
        doc.available_qty += qty

    elif transaction_type == "Received":

        doc.total_issued_qty += qty
        doc.available_qty -= qty

    doc.save(ignore_permissions=True)
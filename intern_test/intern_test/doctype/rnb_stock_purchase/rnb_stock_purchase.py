# Copyright (c) 2026, Akash Tomar and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
from frappe.utils import today

class RNBStockPurchase(Document):

    def before_save(self):

        # replace 'items' with your actual table fieldname
        for row in self.stock_bill:

            # calculate total amount
            row.total_amount = (row.cost_per_item or 0) * (row.quantity or 0)

            # set purchase date if empty
            if not row.purchase_date:
                row.purchase_date = today()
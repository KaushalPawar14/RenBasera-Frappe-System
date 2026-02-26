import frappe
from frappe.model.document import Document
from frappe.utils import now_datetime


class RenBaseraDailyClosing(Document):

    def validate(self):

        self.total_amount = 0
        self.online_amount = 0
        self.cash_amount = 0

        for row in self.bed_allotment:

            amt = row.total_amount or 0
            self.total_amount += amt

            if not row.booking_id:
                continue

            booking = frappe.db.get_value(
                "Bed Allotment",
                row.booking_id,
                ["payment_method"],
                as_dict=True
            )

            pm = (booking.payment_method or "").strip() if booking else ""

            if pm == "Cash":
                self.cash_amount += amt
            else:
                self.online_amount += amt


    def on_update(self):

        # Prevent duplicate execution
        if self.workflow_state == "Closed" and not self.closing_time:
            self.handle_closed_actions()


    def handle_closed_actions(self):

        self.closing_time = now_datetime()
        self.user = frappe.session.user

        booking_ids = list(set(
            row.booking_id for row in self.bed_allotment
            if row.booking_id
        ))

        consolidated = 0

        for booking_id in booking_ids:

            booking = frappe.get_doc("Bed Allotment", booking_id)

            if booking.workflow_state == "Checked-Out":

                self.recalculate_booking_totals(booking)

                frappe.model.workflow.apply_workflow(
                    booking,
                    "Consolidate"
                )

                booking.daily_closing = self.name
                booking.save(ignore_permissions=True)

                consolidated += 1

        frappe.msgprint(
            f"{consolidated} bookings consolidated successfully."
        )

    def recalculate_booking_totals(self, booking):

        cash = 0
        online = 0
        total = 0

        for g in booking.guest:
            amt = g.amount or 0
            pm = (booking.payment_method or "").strip()

            total += amt

            if pm == "Cash":
                cash += amt
            else:
                online += amt

        booking.total_amount = total
        booking.cash_amount = cash
        booking.online_amount = online

        booking.flags.ignore_permissions = True
        booking.save()



@frappe.whitelist()
def fetch_checked_out_bookings():

    bookings = frappe.get_all(
        "Bed Allotment",
        fields=["name", "workflow_state", "creation", "total_amount"],
        ignore_permissions=True
    )

    result = []

    for b in bookings:
        if (b.workflow_state or "").strip() == "Checked-Out":

            result.append({
                "booking_id": b.name,
                "check_in_time": b.creation,
                "check_out_time": None,
                "total_amount": b.total_amount or 0
            })

    return result

    

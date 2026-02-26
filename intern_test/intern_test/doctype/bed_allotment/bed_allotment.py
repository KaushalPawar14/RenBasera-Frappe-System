# Copyright (c) 2026, Akash Tomar and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
from frappe.utils import now_datetime, time_diff_in_hours ,nowdate
import math

class BedAllotment(Document):

    def validate(self):
        self.validate_bed_availability()
        self.set_creation_time()
        self.set_no_of_guests()
        self.set_no_of_relatives()
        self.set_guest_check_in_time()
        self.set_check_in_date_on_checked_in()

        # Occupy beds only on Checked-In
        if self.workflow_state == "Checked-In" and not frappe.flags.in_checkout:
            self.update_bed_status()
            self.set_checked_in_status()



    def set_check_in_date_on_checked_in(self):
        # Only set when entering Checked-In
        if self.workflow_state != "Checked-In":
            return

        if self.check_in_date:
            return

        # optional: only when state actually changed to Checked-In
        old = self.get_doc_before_save()
        old_state = old.workflow_state if old else None
        if old_state == "Checked-In":
            return

        #   if submitted, use db_set (field must be Allow on Submit)
        if self.docstatus == 1:
            self.db_set("check_in_date", nowdate(), update_modified=False)
            self.check_in_date = nowdate()
        else:
            self.check_in_date = nowdate()

    def on_update_after_submit(self):
        # 🔥 this is the key for workflow changes after submit
        self._set_check_in_date_on_checked_in()

    def _set_check_in_date_on_checked_in(self):
        # Set only when switching into Checked-In
        if self.workflow_state != "Checked-In":
            return

        if self.check_in_date:
            return

        old = self.get_doc_before_save()
        old_state = old.workflow_state if old else None

        if old_state != "Checked-In":
            # db_set reliably persists even for submitted docs
            self.db_set("check_in_date", nowdate(), update_modified=False)
            self.check_in_date = nowdate()
        

    def set_no_of_guests(self):
        self.no_of_guests = len([
            row for row in self.guest
            if row.guest_name or row.bed
        ])


    def set_no_of_relatives(self):
        self.no_of_relatives = len([
            row for row in self.guest
            if row.guest_name or row.bed
        ])

    # def on_update(self):
    #     if self.workflow_state == "Checked-In" and not self.check_in_date:
    #         frappe.db.set_value(self.doctype, self.name, "check_in_date", nowdate())
    #         self.check_in_date = nowdate()  # keep in-memory in sync

    #     if self.workflow_state == "Cancelled":
    #         self.handle_cancel()


    def handle_cancel(self):

        frappe.msgprint("Handle Cancel Triggered")  # DEBUG

        for row in self.guest:
            if row.bed and row.status != "Checked-In":
                frappe.db.set_value("Bed", row.bed, "status", "Available")
                frappe.throw("Bed allotment Cancelled")
                
                 
        # Prevent cancelling after checkout
            if row.status == "Checked-Out":
                frappe.throw("Cannot Cancel after Check-Out")

    # ------------------ VALIDATION ------------------ #

    def validate_bed_availability(self):

        if frappe.flags.in_checkout:
            return

        if self.workflow_state != "Checked-In":
            return

        for row in self.guest:

            if row.bed and row.status != "Checked-Out":

                # Check if this bed is occupied by another booking
                other_booking = frappe.db.exists(
                    "Relatives",
                    {
                        "bed": row.bed,
                        "status": ["!=", "Checked-Out"],
                        "parent": ["!=", self.name]
                    }
                )

                if other_booking:
                    frappe.throw(f"Bed {row.bed} is already occupied.")



    # ------------------ BED STATUS ------------------ #

    def update_bed_status(self):

        for row in self.guest:
            if row.bed and row.status != "Checked-Out":
                current_status = frappe.db.get_value("Bed", row.bed, "status")
                if current_status != "Occupied":
                    frappe.db.set_value("Bed", row.bed, "status", "Occupied")


    # ------------------ CHECK-IN ------------------ #

    def set_creation_time(self):
        if not self.creation_time:
            self.creation_time = now_datetime()


    def set_guest_check_in_time(self):
            for row in self.guest:
                if not row.check_in_time:
                    row.check_in_time = now_datetime()


    def set_checked_in_status(self):
        if self.workflow_state == "Checked-In":
            for row in self.guest:
                if row.bed and not row.status:
                    row.status = "Checked-In"
    

    # ---------------- ON TRASH VALIDATION (OPTIONAL) ---------------- #

    def on_trash(self):
        if self.workflow_state not in ["Checked-Out", "Consolidated", "Cancelled"]:
            frappe.throw(
                "Cannot delete booking while guests are still Checked-In."
            )

    # ------------------ BEFORE SAVE ------------------ #

    def before_save(self):

        #   Set Created By Operator (only first time)
        if self.workflow_state == "Draft" and not self.created_by_operator:
            self.created_by_operator = frappe.session.user

        #   Set Check-In Date
        if self.workflow_state == "Checked-In" and not self.check_in_date:
            self.check_in_date = nowdate()
            frappe.msgprint("DEBUG: Check-in date set")


        #   Set Checkout By (only when fully checked-out)
        if self.workflow_state == "Checked-Out" and not self.checkout_by:
            self.checkout_by = frappe.session.user
            
        # Draft → no status
        if self.workflow_state == "Draft":
            for row in self.guest:
                row.status = None


        # 🔥 WORKFLOW WHOLE CHECKOUT LOGIC
        if self.workflow_state == "Checked-Out" and not frappe.flags.in_checkout:

            now = now_datetime()

            from frappe.utils import getdate

            # 🔥 Auto-adjust checkout date if checkout time exceeds stored date
            if self.check_out_date and getdate(now) < getdate(self.check_out_date):

                old_date = self.check_out_date
                new_date = getdate(now)

                self.check_out_date = new_date

                # Add professional activity log
                self.add_comment(
                    "Info",
                    text=f"""
                    <div style="padding:8px 0;">
                        <b style="color:#d97706;">Checkout Date Auto-Adjusted</b><br><br>

                        <b>Previous Checkout Date:</b> {old_date}<br>
                        <b>Actual Checkout Date:</b> {new_date}<br><br>

                        <div style="background:#fff3cd;padding:8px;border-radius:6px;margin-top:4px;">
                            System updated the checkout date automatically because
                            the actual checkout time was earlier than the planned checkout date.
                        </div>
                    </div>
                    """
                )

            total = 0  # total amount

            for row in self.guest:

                # Skip already checked-out (from particular checkout)
                if row.status == "Checked-Out":
                    total += row.amount or 0
                    continue

                # Safety
                if not row.check_in_time:
                    frappe.throw(f"Check-In time missing for Bed {row.bed}")

                #  BILLING CALCULATION (same logic as particular checkout)
                hours, days, amount = calculate_amount(
                    row.check_in_time,
                    now
                )

                #  CHILD TABLE UPDATE
                row.status = "Checked-Out"
                row.check_out_time = now
                row.stay_hours = hours
                row.billable_days = days
                row.amount = amount

                total += amount

                #  Free Bed
                if row.bed:
                    frappe.db.set_value("Bed", row.bed, "status", "Available")

            #  UPDATE PARENT TOTAL
            self.total_amount = total



# ------------------ BILLING LOGIC ------------------ #

def calculate_amount(check_in, check_out, rate=80):
    """
    Billing Rule:
    - Up to 24.99 hrs = 1 day
    - Touching 25th hour = next full day
    """

    if not check_in or not check_out:
        return 0, 0, 0

    check_in = frappe.utils.get_datetime(check_in)
    check_out = frappe.utils.get_datetime(check_out)

    hours = max(0, time_diff_in_hours(check_out, check_in))

    if hours <= 24.9999:
        billable_days = 1
    else:
        billable_days = math.floor(hours / 24) + 1

    amount = billable_days * rate

    return hours, billable_days, amount


# ------------------ WHOLE CHECKOUT ------------------ #

@frappe.whitelist()
def whole_checkout(booking_id):

    frappe.flags.in_checkout = True

    try:
        doc = frappe.get_doc("Bed Allotment", booking_id)
        now = now_datetime()

        if not doc.guest:
            frappe.throw("No guests found in booking.")

        updated = []

        for row in doc.guest:

            # only remaining (not already checked-out)
            if row.status == "Checked-Out":
                continue

            if not row.check_in_time:
                frappe.throw(f"Check-In time missing for Bed {row.bed}")

            # 🔥 SAME calculation as particular_checkout
            hours, days, amount = calculate_amount(
                row.check_in_time,
                now
            )

            row.status = "Checked-Out"
            row.check_out_time = now
            row.stay_hours = hours
            row.billable_days = days
            row.amount = amount

            # Free bed
            if row.bed:
                frappe.db.set_value("Bed", row.bed, "status", "Available")

            updated.append(row.bed)

        # 🔥 Recalculate total from DB (SAFE, accurate)
        total = frappe.db.sql("""
            SELECT SUM(amount) FROM `tabguest`
            WHERE parent=%s
        """, booking_id)[0][0] or 0

        doc.total_amount = total

        # Workflow update
        doc.workflow_state = "Checked-Out"

        doc.save(ignore_permissions=True)

        # Optional daily closing
        # create_daily_closing_entry(doc)

        return {
            "status": "whole_checkout_done",
            "updated_beds": updated,
            "total_amount": total
        }

    finally:
        frappe.flags.in_checkout = False

  
# ------------------ PARTICULAR CHECKOUT ------------------ #

@frappe.whitelist()
def particular_checkout(booking_id, bed_ids):

    if isinstance(bed_ids, str):
        bed_ids = frappe.parse_json(bed_ids)

    if not bed_ids:
        frappe.throw("Please select at least one bed.")

    doc = frappe.get_doc("Bed Allotment", booking_id)
    now = now_datetime()

    updated = []

    for row in doc.guest:

        if row.bed in bed_ids and row.status != "Checked-Out":

            if not row.check_in_time:
                frappe.throw(f"Check-In time missing for Bed {row.bed}")

            hours, days, amount = calculate_amount(
                row.check_in_time,
                now
            )

            row.status = "Checked-Out"
            row.check_out_time = now
            row.stay_hours = hours
            row.billable_days = days
            row.amount = amount

            frappe.db.set_value("Bed", row.bed, "status", "Available")

            updated.append(row.bed)

    # Recalculate total from child table
    doc.total_amount = sum([d.amount or 0 for d in doc.guest])

    remaining = len([d for d in doc.guest if d.status != "Checked-Out"])

    if remaining == 0:
        doc.workflow_state = "Checked-Out"

    doc.save(ignore_permissions=True)

    return {
        "status": "partial_checkout_done",
        "updated_beds": updated,
        "total": doc.total_amount,
        "remaining": remaining
    }


# def particular_checkout(booking_id, bed_ids):

#     if isinstance(bed_ids, str):
#         bed_ids = frappe.parse_json(bed_ids)

#     if not bed_ids:
#         frappe.throw("Please select at least one bed.")

#     now = now_datetime()

#     frappe.db.begin()  
#     frappe.msgprint("hare krishna")
#     #  # 🔒 start transaction
#     guests = frappe.get_all(
#         "Bed Allotment",
#         filters={"parent": booking_id},
#         fields=["name", "bed", "check_in_time", "status"]
#     )

#     updated = []

#     for g in guests:
#         if g.bed in bed_ids and g.status != "Checked-Out":

#             hours, days, amount = calculate_amount(g.check_in_time, now)

#             frappe.db.sql("""
#                 UPDATE `tabguest`
#                 SET status=%s,
#                     check_out_time=%s,
#                     stay_hours=%s,
#                     billable_days=%s,
#                     amount=%s
#                 WHERE name=%s
#             """, ("Checked-Out", now, hours, days, amount, g.name))

#             frappe.db.sql("""
#                 UPDATE `tabBed`
#                 SET status='Available'
#                 WHERE name=%s
#             """, g.bed)

#             updated.append(g.bed)

#     # update parent total
#     total = frappe.db.sql("""
#         SELECT IFNULL(SUM(amount),0)
#         FROM `tabguest`
#         WHERE parent=%s
#     """, booking_id)[0][0]

#     frappe.db.sql("""
#         UPDATE `tabguest`
#         SET total_amount=%s
#         WHERE name=%s
#     """, (total, booking_id))

#     # check remaining
#     remaining = frappe.db.sql("""
#         SELECT COUNT(*) 
#         FROM `tabguest`
#         WHERE parent=%s AND status!='Checked-Out'
#     """, booking_id)[0][0]

#     if remaining == 0:
#         frappe.db.sql("""
#             UPDATE `tabguest`
#             SET workflow_state='Checked-Out'
#             WHERE name=%s
#         """, booking_id)

#     frappe.db.commit()   #  GUARANTEED COMMIT

#     return {
#         "updated_beds": updated,
#         "total": total,
#         "remaining": remaining
#     }

# ------------------ LEGACY API ------------------ #

@frappe.whitelist()
def checkout(booking_id, checkout_type, bed_ids=None):

    if checkout_type == "Whole Booking":
        whole_checkout(booking_id)

    elif checkout_type in ["Particular Guest", "Particular Bed"]:
        if not bed_ids:
            frappe.throw("Please provide bed(s).")
        particular_checkout(booking_id, bed_ids)


# ------------------ HELPER ------------------ #

def free_bed(bed_name):
    frappe.db.set_value("Bed", bed_name, "status", "Available")


from frappe.utils import getdate

@frappe.whitelist()
def extend_checkout(docname, new_checkout_date, comments):

    doc = frappe.get_doc("Bed Allotment", docname)

    if getdate(new_checkout_date) <= getdate(doc.check_out_date):
        frappe.throw("New checkout date must be greater than current checkout date.")

    old_checkout_date = doc.check_out_date

    # Update field
    doc.check_out_date = new_checkout_date

    # Save first
    doc.save(ignore_permissions=True)

    # Add timeline entry AFTER save
    doc.add_comment(
        comment_type="Info",
        text=f"""
        <div style="padding:8px 0;">
            <b style="color:#2e7d32;">Checkout Date Extended</b><br><br>

            <b>Extended By:</b> {frappe.session.user}<br>
            <b>Previous Date:</b> {old_checkout_date}<br>
            <b>New Date:</b> {new_checkout_date}<br><br>

            <b>Remarks:</b>
            <div style="background:#f1f3f5;padding:8px;border-radius:6px;margin-top:4px;">
                {comments}
            </div>
        </div>
        """
    )

    # Force UI refresh
    doc.notify_update()

    return True 
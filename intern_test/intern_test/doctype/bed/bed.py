import frappe
from frappe.model.document import Document


class Bed(Document):
    pass


@frappe.whitelist()
def create_beds():
    start = 801
    end = 810

    for i in range(start, end + 1):
        if not frappe.db.exists("Bed", {"bed_number": f"C{i}"}):
            bed = frappe.new_doc("Bed")
            bed.shelter = "RNB-26002"
            bed.bed_number = f"C{i}"
            bed.floor = "8"
            bed.insert(ignore_permissions=True)

    frappe.db.commit()
    return "Beds created successfully"

@frappe.whitelist()
def delete_b_beds_range():
    start = 101
    end = 160
    deleted = 0

    for i in range(start, end + 1):
        bed_number = f"B{i}"

        bed = frappe.db.get_value("Bed", {"bed_number": bed_number}, "name")

        if bed:
            frappe.delete_doc("Bed", bed, ignore_permissions=True)
            deleted += 1

    frappe.db.commit()
    return f"{deleted} beds deleted"
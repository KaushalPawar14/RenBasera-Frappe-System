import frappe

@frappe.whitelist()
def get_floor_occupancy_chart():

    data = frappe.db.sql("""
        SELECT floor,
        COUNT(*) as total,
        SUM(CASE WHEN status='Occupied' THEN 1 ELSE 0 END) as occupied
        FROM `tabBed`
        GROUP BY floor
        ORDER BY floor
    """, as_dict=True)

    labels = []
    occupied = []
    available = []

    for d in data:
        total = d.total or 0
        occ = d.occupied or 0
        avail = total - occ

        labels.append(f"Floor {d.floor}")
        occupied.append(occ)
        available.append(avail)

    return {
        "labels": labels,
        "datasets": [
            {"name": "Occupied Beds", "values": occupied},
            {"name": "Available Beds", "values": available}
        ]
    }


from datetime import datetime, timedelta

@frappe.whitelist()
def get_daily_occupancy_rate():

    total_beds = frappe.db.count("Bed")

    data = frappe.db.sql("""
        SELECT 
            DATE(p.check_in_date) as day,
            SUM(CASE WHEN r.status='Checked In' THEN 1 ELSE 0 END) as occupied
        FROM `tabBed Allotment` p
        JOIN `tabRelatives` r ON r.parent = p.name
        GROUP BY DATE(p.check_in_date)
        ORDER BY day
    """, as_dict=True)

    labels = []
    values = []

    for d in data:

        rate = 0
        if total_beds > 0:
            rate = (d.occupied / total_beds) * 100

        labels.append(str(d.day))
        values.append(rate)

    return {
        "labels": labels,
        "datasets": [
            {
                "name": "Occupancy %",
                "values": values
            }
        ]
    }

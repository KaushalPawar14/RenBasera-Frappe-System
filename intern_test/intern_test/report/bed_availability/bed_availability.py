
# import frappe

# def execute(filters=None):
#     frappe.msgprint("DEBUG: Report started")

#     # Step 1: Test simple query
#     try:
#         test = frappe.db.sql("SELECT name FROM `tabRen Basera` LIMIT 1")
#         frappe.msgprint(f"DEBUG: Ren Basera table accessible → {test}")
#     except Exception as e:
#         frappe.throw(f"ERROR accessing Ren Basera table: {e}")

#     # Step 2: Test operator column existence
#     try:
#         test2 = frappe.db.sql("SELECT `operator` FROM `tabRen Basera` LIMIT 1")
#         frappe.msgprint(f"DEBUG: Operator column exists → {test2}")
#     except Exception as e:
#         frappe.throw(f"ERROR accessing operator column: {e}")

#     # Step 3: Return simple dummy report
#     columns = [
#         {"label": "Test", "fieldname": "test", "fieldtype": "Data"}
#     ]

#     data = [{"test": "Debug Successful"}]

#     return columns, data






##################################################################################################
##################################################################################################
##################################################################################################




import frappe
from frappe.utils import getdate, add_days


def execute(filters=None):
    filters = filters or {}

    from_date = getdate(filters.get("from_date"))
    to_date = getdate(filters.get("to_date"))

    if not from_date or not to_date:
        frappe.throw("Please select From Date and To Date")


    columns = [
        {
            "label": "Ren Basera",
            "fieldname": "shelter",
            "fieldtype": "Link",
            "options": "Ren Basera",
            "width": 200
        },
        {
            "label": "Floor",
            "fieldname": "floor",
            "fieldtype": "Data",
            "width": 100
        },
        {
            "label": "Total Beds",
            "fieldname": "total_beds",
            "fieldtype": "Int",
            "width": 120
        },

        

    ]

    # Generate Date Columns
    dates = []
    current = from_date
    while current <= to_date:
        dates.append(current)
        columns.append({
            "label": current.strftime("%d-%m-%Y"),
            "fieldname": f"d_{current.strftime('%d_%m_%Y')}",
            "fieldtype": "Int",
            "width": 100
        })
        current = add_days(current, 1)

    user = frappe.session.user

    if user != "Administrator":
        ren_basera = frappe.db.sql("""
            SELECT name
            FROM `tabRen Basera`
            WHERE `operator` = %s
            LIMIT 1
        """, user)

        if not ren_basera:
            frappe.throw("No Ren Basera assigned to you.")

        shelters = [{"name": ren_basera[0][0]}]
    else:
        shelters = frappe.db.sql("""
            SELECT name FROM `tabRen Basera`
        """, as_dict=True)

    data = []

   
    for s in shelters:

        shelter_name = s["name"]

        floors = frappe.db.sql("""
            SELECT DISTINCT floor
            FROM `tabBed`
            WHERE shelter = %s
            ORDER BY floor
        """, shelter_name, as_dict=True)

        for f in floors:

            floor_no = f["floor"]

            total_beds = frappe.db.sql("""
                SELECT COUNT(name)
                FROM `tabBed`
                WHERE shelter = %s
                AND floor = %s
            """, (shelter_name, floor_no))[0][0] or 0


            available_beds = frappe.db.sql("""
                SELECT COUNT(name)
                FROM `tabBed`
                WHERE shelter = %s
                AND status = 'Available'
            """, shelter_name)[0][0] or 0

            row = {
                "shelter": shelter_name,
                "floor": floor_no, 
                "total_beds": total_beds
            }

            for d in dates:

                occupied = frappe.db.sql("""
                    SELECT COUNT(DISTINCT r.bed)
                    FROM `tabRelatives` r
                    INNER JOIN `tabBed Allotment` b ON r.parent = b.name
                    INNER JOIN `tabBed` bd ON r.bed = bd.name
                    WHERE bd.shelter = %s
                    AND bd.floor = %s
                    AND r.bed IS NOT NULL
                    AND b.check_in_date <= %s
                    AND (
                        r.status != 'Checked-Out')
                    AND(          
                        b.check_out_date IS NULL
                        OR b.check_out_date >= %s
                        )
                    
                """, (shelter_name, floor_no , d, d))[0][0] or 0



                available = total_beds - occupied

                row[f"d_{d.strftime('%d_%m_%Y')}"] = available


            data.append(row)

    return columns, data


# AND (
#                         r.status != 'Checked-Out'
#                         OR (r.status = 'Checked-Out' AND r.modified >= %s)
#                     )
#                 AND (
#                         b.check_out_date IS NULL
#                         OR b.check_out_date >= %s
#                     )
##################################################################################################
##################################################################################################
##################################################################################################


# import frappe
# from frappe.utils import getdate, add_days


# def execute(filters=None):
#     filters = filters or {}

#     from_date = getdate(filters.get("from_date"))
#     to_date = getdate(filters.get("to_date"))

#     if not from_date or not to_date:
#         frappe.throw("Please select From Date and To Date")

#     # ------------------------------------------
#     # Columns
#     # ------------------------------------------
#     columns = [
#         {
#             "label": "Ren Basera",
#             "fieldname": "shelter",
#             "fieldtype": "Link",
#             "options": "Ren Basera",
#             "width": 200
#         },
#         {
#             "label": "Total Beds",
#             "fieldname": "total_beds",
#             "fieldtype": "Int",
#             "width": 120
#         },
#     ]

#     # Date columns
#     dates = []
#     current = from_date
#     while current <= to_date:
#         dates.append(current)
#         columns.append({
#             "label": current.strftime("%d-%m-%Y"),
#             "fieldname": f"d_{current.strftime('%d_%m_%Y')}",
#             "fieldtype": "Int",
#             "width": 100
#         })
#         current = add_days(current, 1)

#     # ------------------------------------------
#     # Operator Restriction
#     # ------------------------------------------
#     user = frappe.session.user
#     user_roles = frappe.get_roles(user)

#     ren_basera_filter = None

#     if "Shelter Operator" in user_roles:
#         ren_basera_filter = frappe.db.get_value(
#             "Ren Basera",
#             {"operator": user},
#             "name"
#         )
#         if not ren_basera_filter:
#             frappe.throw("No Ren Basera assigned to this operator.")

#     # ------------------------------------------
#     # Get Ren Basera List
#     # ------------------------------------------
#     if ren_basera_filter:
#         shelters = frappe.get_all(
#             "Ren Basera",
#             filters={"name": ren_basera_filter},
#             fields=["name"]
#         )
#     else:
#         shelters = frappe.get_all(
#             "Ren Basera",
#             fields=["name"]
#         )

#     data = []

#     # ------------------------------------------
#     # Availability Calculation
#     # ------------------------------------------
#     for s in shelters:

#         total_beds = frappe.db.count("Bed", {
#             "shelter": s.name
#         })

#         row = {
#             "shelter": s.name,
#             "total_beds": total_beds
#         }

#         for d in dates:

#             start_of_day = f"{d} 00:00:00"
#             end_of_day = f"{d} 23:59:59"
#             occupied = frappe.db.sql("""
#         SELECT COUNT(DISTINCT g.bed)
#         FROM `tabRelatives` g
#         INNER JOIN `tabBed Allotment` ba
#             ON ba.name = g.parent
#         WHERE
#             ba.shelter = %(shelter)s
#             AND ba.docstatus = 1
#             AND g.bed IS NOT NULL
#             AND g.check_in_time IS NOT NULL
#             AND g.check_in_time <= %(end_of_day)s
#             AND (
#                 g.check_out_time IS NULL
#                 OR g.check_out_time > %(start_of_day)s
#             )
#     """, {
#         "shelter": s.name,
#         "start_of_day": start_of_day,
#         "end_of_day": end_of_day,
#     })[0][0] or 0



#             available = max(total_beds - occupied, 0)

#             row[f"d_{d.strftime('%d_%m_%Y')}"] = available

#         data.append(row)

#     return columns, data

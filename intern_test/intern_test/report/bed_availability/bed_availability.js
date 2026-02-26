// Copyright (c) 2026, Akash Tomar and contributors
// For license information, please see license.txt

frappe.query_reports["Bed Availability"] = {
    filters: [
        // {
        //     fieldname: "city",
        //     label: "City",
        //     fieldtype: "Data",
        //     placeholder: "Type city name",
        //     clearable: 1,
        //     on_change: function () {
        //         // Clear shelter when city changes
        //         frappe.query_report.set_filter_value("shelter", "");
        //         frappe.query_report.refresh();
        //     }
        // },
        // {
        //     fieldname: "shelter",
        //     label: "Shelter",
        //     fieldtype: "Link",
        //     options: "Ren Basera",
        //     clearable: 1,
        //     get_query: function () {
        //         let city = frappe.query_report.get_filter_value("city");
        //         if (city) {
        //             return {
        //                 filters: {
        //                     city: ["like", "%" + city + "%"]
        //                 }
        //             };
        //         }
        //     }
        // },
        {
            fieldname: "from_date",
            label: "From Date",
            fieldtype: "Date",
            default: frappe.datetime.get_today(),
            reqd: 1,
            clearable: 1
        },
        {
            fieldname: "to_date",
            label: "To Date",
            fieldtype: "Date",
            default: frappe.datetime.add_days(frappe.datetime.get_today(), 7),
            reqd: 1,
            clearable: 1
        }
    ]
};

// Copyright (c) 2026, Akash Tomar and contributors
// For license information, please see license.txt

frappe.ui.form.on("TSF Dispatch Challan", {
    setup: function (frm) {
        // ---------------------------------------------------------
        // Filter Dropdowns: Only show Available Drivers and Vehicles
        // ---------------------------------------------------------
        frm.set_query("driver", function() {
            return {
                filters: {
                    "driver_status": "Available"
                }
            };
        });

        frm.set_query("vehicle", function() {
            return {
                filters: {
                    "vehicle_status": "Available"
                }
            };
        });
    },

    refresh: function (frm) {
        // ---------------------------------------------------------
        // 1. Filter Dropdown for Boarded Items
        // ---------------------------------------------------------
        // Format: frm.set_query("child_field_name", "child_table_name", function)
        frm.set_query("item_name", "boarded_items", function (doc, cdt, cdn) {
            let selected_items = [];

            // Loop through the table to find what is already selected
            (doc.boarded_items || []).forEach((row) => {
                // Add to our list, BUT ignore the row we are currently editing
                if (row.item_name && row.name !== cdn) {
                    selected_items.push(row.item_name);
                }
            });

            // Tell Frappe to filter OUT anything in our selected_items list
            return {
                filters: [["name", "not in", selected_items]],
            };
        });

        // ---------------------------------------------------------
        // 2. Filter Dropdown for Center List
        // ---------------------------------------------------------
        frm.set_query("name1", "center_list", function (doc, cdt, cdn) {
            let selected_centers = [];

            (doc.center_list || []).forEach((row) => {
                if (row.name1 && row.name !== cdn) {
                    selected_centers.push(row.name1);
                }
            });

            return {
                filters: [["name", "not in", selected_centers]],
            };
        });
    },
});
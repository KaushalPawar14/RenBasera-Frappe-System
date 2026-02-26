// Copyright (c) 2026, Akash Tomar and contributors
// For license information, please see license.txt

frappe.ui.form.on("TSF Dispatch Challan", {
	// validate: function (frm) {
	// 	// ---------------------------------------------------------
	// 	// 1. Validation for Boarded Items
	// 	// ---------------------------------------------------------
	// 	let unique_boarded = new Set();
	// 	(frm.doc.boarded_items || []).forEach((row) => {
	// 		// Replace 'item_name' with your actual item fieldname
	// 		let current_item = row.item_name;
	// 		if (current_item) {
	// 			if (unique_boarded.has(current_item)) {
	// 				frappe.msgprint(
	// 					`The item "<b>${current_item}</b>" is repeated in Boarded Items (row ${row.idx}).`,
	// 				);
	// 				frappe.validated = false; // Stops saving
	// 			} else {
	// 				unique_boarded.add(current_item);
	// 			}
	// 		}
	// 	});
	// 	// ---------------------------------------------------------
	// 	// 2. Validation for Center List
	// 	// ---------------------------------------------------------
	// 	let unique_centers = new Set();
	// 	// Assuming the child table fieldname is 'center_list'
	// 	(frm.doc.center_list || []).forEach((row) => {
	// 		// Replace 'center_name' with the actual fieldname of the 'Name' column
	// 		let current_center = row.center_name;
	// 		if (current_center) {
	// 			if (unique_centers.has(current_center)) {
	// 				frappe.msgprint(
	// 					`The center "<b>${current_center}</b>" is repeated in the Center List (row ${row.idx}). Please ensure all Centers are unique.`,
	// 				);
	// 				frappe.validated = false; // Stops saving
	// 			} else {
	// 				unique_centers.add(current_center);
	// 			}
	// 		}
	// 	});
	// },
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

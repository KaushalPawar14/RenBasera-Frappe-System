// Copyright (c) 2026, Akash Tomar and contributors
// For license information, please see license.txt

// frappe.ui.form.on("RNB Stock Purchase", {
// 	refresh(frm) {

// 	},
// });
frappe.ui.form.on("RNB Stock Purchase", {
    
    cost_per_item: function(frm, cdt, cdn) {
        calculate_total(cdt, cdn);
    },

    quantity: function(frm, cdt, cdn) {
        calculate_total(cdt, cdn);
    }

});


function calculate_total(cdt, cdn) {

    let row = locals[cdt][cdn];

    let cost = row.cost_per_item || 0;
    let qty = row.quantity || 0;

    frappe.model.set_value(cdt, cdn, "total_amount", cost * qty);
}
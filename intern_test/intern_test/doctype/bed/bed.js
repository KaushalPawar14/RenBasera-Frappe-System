// // Copyright (c) 2026, Akash Tomar and contributors
// // For license information, please see license.txt

// frappe.ui.form.on("Bed", {
// 	refresh(frm) {

// 		frm.add_custom_button("Create Beds for C", function () {
// 			frappe.call({
// 				method: "intern_test.intern_test.doctype.bed.bed.create_beds",
// 				callback: function (r) {
// 					if (r.message) {
// 						frappe.msgprint(r.message);
// 					}
// 				}
// 			});
// 		});

//         frm.add_custom_button("Delete B Beds", function () {
//             frappe.call({
//                 method: "intern_test.intern_test.doctype.bed.bed.delete_b_beds_range",
//                 callback: function (r) {
//                     if (r.message) {
//                         frappe.msgprint(r.message);
//                     }
//                 }
//             });
//         });
// 	},
// });
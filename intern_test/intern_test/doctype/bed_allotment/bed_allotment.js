// Copyright (c) 2026, Akash Tomar and contributors
// For license information, please see license.txt

frappe.ui.form.on('Bed Allotment', {
    refresh: function(frm) {
        if(frm.doc.workflow_state == "Checked-In") {
            frm.add_custom_button(__('Particular Checkout'), function() {
                open_particular_checkout_dialog(frm);
            });
            frm.add_custom_button(__('Extend'), function() {
                open_extend_dialog(frm);
            });
        }
    },

    onload(frm) {
        // Register realtime listener only once
        frappe.realtime.on("doc_update", (data) => {
            if (data.doctype === frm.doc.doctype && data.name === frm.doc.name) {
                frm.timeline.refresh();
            }
        });
    },

    setup: function(frm) {
        // Set query for bed field inside child table 'guest'
        frm.fields_dict['guest'].grid.get_field('bed').get_query = function(doc, cdt, cdn) {

            // Collect already selected beds in this booking
            let selected_beds = (doc.guest || [])
                .filter(row => row.bed && row.status !== "Checked-Out")
                .map(row => row.bed);

            return {
                filters: [
                    ["Bed", "shelter", "=", doc.shelter],
                    ["Bed", "status", "=", "Available"],
                    ["Bed", "name", "not in", selected_beds]
                ]
            };
        };
    },

    shelter: function(frm) {
        // Clear all bed fields in child table when shelter changes
        frm.clear_table('guest'); 
        frm.doc.guest.forEach(function(row) {
            row.bed = '';
        });
        frm.refresh_field('guest');
    },
});

function open_extend_dialog(frm) {

    let d = new frappe.ui.Dialog({
        title: 'Extend Checkout',
        fields: [
            {
                label: 'New Check Out Date',
                fieldname: 'new_checkout_date',
                fieldtype: 'Date',
                reqd: 1
            },
            {
                label: 'Comments',
                fieldname: 'comments',
                fieldtype: 'Small Text',
                reqd: 1
            }
        ],
        primary_action_label: 'Submit',
        primary_action(values) {

            if (!values.new_checkout_date || !values.comments) {
                frappe.msgprint("Both fields are mandatory");
                return;
            }

            frappe.call({
                method: "intern_test.intern_test.doctype.bed_allotment.bed_allotment.extend_checkout",
                args: {
                    docname: frm.doc.name,
                    new_checkout_date: values.new_checkout_date,
                    comments: values.comments   
                },
                callback: function() {
                    frm.reload_doc();
                }
            });

            d.hide();
        }
    });

    d.show();
}


// ==================
// WORKFLOW DIALOG
// ==================

function open_particular_checkout_dialog(frm) {

    let bed_options = frm.doc.guest
        .filter(row => row.bed && row.status !== 'Checked-Out')
        .map(g => ({ label: g.bed + " (" + g.guest_name + ")", value: g.bed }));

    if (!bed_options.length) {
        frappe.msgprint(__('No beds available for particular checkout'));
        return;
    }

    let dialog = new frappe.ui.Dialog({
        title: __('Select Beds for Checkout'),
        fields: [
            {
                fieldname: 'beds',
                fieldtype: 'MultiCheck',
                options: bed_options,
                reqd: 1
            }
        ],
        primary_action_label: __('Checkout'),
        primary_action: function(values) {

            let selected_beds = values.beds;
            if (!selected_beds || !selected_beds.length) {
                frappe.msgprint("Please select at least one bed.");
                return;
            }

            frappe.call({
                method: "intern_test.intern_test.doctype.bed_allotment.bed_allotment.particular_checkout",
                args: {
                    booking_id: frm.doc.name,
                    bed_ids: selected_beds
                },
                callback(r) {

                    if (!r.exc) {

                        // ✅ Re-fetch document model from backend
                        frm.reload_doc()

                        frappe.show_alert({
                            message: "Selected beds Checked-Out successfully",
                            indicator: "green"
                        });
                    }

                    dialog.hide();
                }
            });
        }
    });

    dialog.show();
}




// ==================
// PARTICULAR CHECKOUT
// ==================


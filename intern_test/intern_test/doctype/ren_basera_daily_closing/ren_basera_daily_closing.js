frappe.ui.form.on("Ren Basera Daily Closing", {

    refresh(frm) {

        // Only allow actions in Draft
        if (frm.doc.docstatus !== 0 & frm.doc.workflow_state != "Draft") return;
        frm.add_custom_button(
            __("Fetch Allotments"),
            function () {

                // Prevent duplicate fetch
                if (frm.doc.bed_allotment && frm.doc.bed_allotment.length > 0) {
                    frappe.msgprint("Bookings already fetched.");
                    return;
                }

                frappe.call({
                    method: "intern_test.intern_test.doctype.ren_basera_daily_closing.ren_basera_daily_closing.fetch_checked_out_bookings",
                    freeze: true,
                    freeze_message: "Fetching bookings...",
                    callback(r) {

                        console.log("Backend Response:", r.message);

                        if (!r.message || !r.message.length) {
                            frappe.msgprint("No Checked-Out bookings found.");
                            return;
                        }

                        // Clear child table
                        frm.clear_table("daily_closing");

                        let total = 0;

                        r.message.forEach(row => {

                            let child = frm.add_child("bed_allotment");

                            // Safe assignment
                            child.booking_id = row.booking_id || row.name || "";
                            child.check_in_time = row.check_in_time ||"" ;
                            child.total_amount = row.total_amount ||0 ;

                            total += (row.total_amount || 0);
                        });

                        frm.refresh_field("bed_allotment");
                        frm.set_value("total_amount", total);

                        frappe.msgprint("Bookings Loaded: " + r.message.length);
                    }
                });

            },
            __("Actions")
        );
        // if (frm.doc.workflow_state !== "Closed") {
        //     frm.add_custom_button(
        //         __("Mark as Closed"),
        //         function () {

        //             if (!frm.doc.total_amount || frm.doc.total_amount <= 0) {
        //                 frappe.msgprint("Total Amount must be greater than 0");
        //                 return;
        //             }

        //             frappe.confirm(
        //                 "Are you sure you want to mark this Daily Closing as closed?",
        //                 () => {

        //                     frappe.call({
        //                         method: "frappe.model.workflow.apply_workflow",
        //                         args: {
        //                             doc: frm.doc,
        //                             action: "Close"
        //                         },
        //                         callback() {
        //                             frappe.msgprint("Marked as Closed");
        //                             frm.reload_doc();
        //                         }
        //                     });

        //                 }
        //             );
        //         },
        //         __("Actions")
        //     );
        // }
    }
});





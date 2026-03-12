frappe.ui.form.on('RNB Stock Transaction', {

    before_workflow_action: function(frm) {

        const action = frm.selected_workflow_action;

        const important_actions = ["Submit", "Approve", "Reject", "Cancel"];

        if (frm.__confirmed_workflow) return;

        if (important_actions.includes(action)) {

            frappe.validated = false;

            frappe.confirm(
                `Are you sure you want to ${action} this transaction?`,
                function() {

                    frm.__confirmed_workflow = true;

                    // run workflow action again
                    frm.page.btn_primary.click();
                },
                function() {
                    frappe.msgprint("Action cancelled.");
                }
            );
        }
    }

});
frappe.provide("frappe.dashboards.chart_sources");

frappe.dashboards.chart_sources["Occupancy Rate Source"] = {
    method: "intern_test.api.get_daily_occupancy_rate"
};
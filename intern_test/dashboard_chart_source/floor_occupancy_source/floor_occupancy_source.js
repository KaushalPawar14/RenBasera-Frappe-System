frappe.provide("frappe.dashboards.chart_sources");

frappe.dashboards.chart_sources["Floor Occupancy Source"] = {
    method: "intern_test.api.get_floor_occupancy_chart"
};

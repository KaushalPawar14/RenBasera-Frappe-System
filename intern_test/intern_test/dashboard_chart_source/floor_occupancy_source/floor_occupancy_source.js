frappe.provide("frappe.dashboards.chart_sources");

frappe.dashboards.chart_sources["Floor Occupancy Source"] = {
    method: "intern_test.api.get_floor_occupancy_chart",

    get_data: function(response) {

        let labels = [];
        let values = [];

        response.forEach(function(row) {

            let occupied = row.total - row.available;

            labels.push("Floor " + row.floor);
            values.push(occupied);

        });

        return {
            labels: labels,
            datasets: [
                {
                    name: "Occupied Beds",
                    values: values
                }
            ]
        };
    }
};
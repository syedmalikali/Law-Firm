// Copyright (c) 2025, Syed Malik Ali and contributors
// For license information, please see license.txt

frappe.query_reports["Timesheets Report"] = {
    'filters': [
        {
            fieldname: "from",
            label: __("From Date"),
            fieldtype: "Date",
            default: frappe.datetime.month_start(),
            reqd: 1
        },
        {
            fieldname: "to",
            label: __("To Date"),
            fieldtype: "Date",
            default: frappe.datetime.month_end(),
            reqd: 1
        },
        {
            fieldname: "customer",
            label: __("Client"),
            fieldtype: "Link",
            options: "Customer",
            reqd: 0,
            on_change: function () {
                const customer = frappe.query_report.get_filter_value("customer");
                const from_date = frappe.query_report.get_filter_value("from");
                const to_date = frappe.query_report.get_filter_value("to");

                if (customer) {
                    frappe.call({
                        method: "frappe.client.get_list",
                        args: {
                            doctype: "Project",
                            filters: {
                                customer: customer,
                                expected_start_date: ["between", [from_date, to_date]]
                            },
                            fields: ["name"]
                        },
                        callback: function (response) {
                            const matters = response.message || [];
                            const matter_options = matters.map(matter => ({ label: matter.name, value: matter.name }));
                            
                            frappe.query_report.set_filter_value("project", "");
                            frappe.query_report.set_filter_options("project", matter_options);
                        }
                    });
                } else {
                    frappe.query_report.set_filter_options("project", []);
                }
            }
        },
        {
            fieldname: "project",
            label: __("Project"),
            fieldtype: "Link",
            options: "Project",
            reqd: 0
        },
        {
            fieldname: "lawyer",
            label: __("Lawyer"),
            fieldtype: "Link",
            options: "Employee",
            reqd: 0
        }
    ]
};

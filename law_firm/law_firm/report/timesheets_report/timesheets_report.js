frappe.query_reports["Timesheets Report"] = {
    filters: [
        {
            fieldname: "from",
            label: __("From Date"),
            fieldtype: "Date",
            reqd: 1,
            default: frappe.datetime.add_months(frappe.datetime.get_today(), -1)
        },
        {
            fieldname: "to",
            label: __("To Date"),
            fieldtype: "Date",
            reqd: 1,
            default: frappe.datetime.get_today()
        },
        {
            fieldname: "customer",
            label: __("Customer"),
            fieldtype: "Link",
            options: "Customer",
            on_change: function() {
                frappe.query_report.set_filter_value('project', '');
                frappe.query_report.set_filter_value('employee', '');
                frappe.query_report.refresh();
            }
        },
        {
            fieldname: "project",
            label: __("Project"),
            fieldtype: "Link",
            options: "Project",
            get_query: function() {
                const customer = frappe.query_report.get_filter_value('customer');
                // Show all projects if no customer selected
                return {
                    filters: customer ? { 'customer': customer } : {}
                };
            },
            on_change: function() {
                frappe.query_report.set_filter_value('employee', '');
                frappe.query_report.refresh();
            }
        },
        {
            fieldname: "employee",
            label: __("Employee"),
            fieldtype: "Link",
            options: "Employee",
            
        },
        {
            fieldname: "invoiced",
            label: __("Invoiced?"),
            fieldtype: "Select",
            options: "\nYes\nNo\nDraft",
            
        }

    ]
};
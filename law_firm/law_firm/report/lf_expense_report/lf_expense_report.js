// Copyright (c) 2025, Syed Malik Ali and contributors
// For license information, please see license.txt

frappe.query_reports["LF Expense Report"] = {
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
            fieldname: "vendor",
            label: __("Vendor"),
            fieldtype: "Link",
            options: "LF Vendor",
            
        },
        {
            fieldname: "invoiced",
            label: __("Invoiced?"),
            fieldtype: "Select",
            options: "\nYes\nNo\nDraft",
            
        },
        {
            fieldname: "summary",
            label: __("Print Option"),
            fieldtype: "Select",
            options: "All\nLawyer Summary\nDetail Only\nSummary By Matter",
            default: "All"  
            
        },


    ]
};
# Copyright (c) 2025, Syed Malik Ali and contributors
# For license information, please see license.txt

import frappe


def execute(filters=None):
    columns = get_columns(filters)
    data = get_data(filters)
    return columns, data


def get_columns(filters):
    # Define the report columns
    columns = [
        {"label": "Date", "fieldname": "date", "fieldtype": "Date", "width": 120},
        {"label": "Timesheet", "fieldname": "parent", "fieldtype": "Link", 'options': 'LF Timesheet', "width": 120},
        {"label": "Client", "fieldname": "client", "fieldtype": "Link", 'options': 'Customer', 'width': 150},
        {"label": "Lawyer", "fieldname": "name1", "fieldtype": "Link", 'options': 'Employee', 'width': 150},
        {"label": "Matter", "fieldname": "file_number", "fieldtype": "Link", 'options': 'Matter', 'width': 150},
        {"label": "Matter Name", "fieldname": "matter", "fieldtype": "Data", 'width': 180},
        {"label": "Hours", "fieldname": "time", "fieldtype": "Float", "width": 120},
        {"label": "Particulars", "fieldname": "purticulars", "fieldtype": "Data", "width": 200},
        {"label": "Invoiced", "fieldname": "is_invoiced", "fieldtype": "Data", "width": 80},
        {"label": "Lawyer Short Code", "fieldname": "lawyer_short_code", "fieldtype": "Data", "width": 80},
    ]
    return columns


def get_data(filters):
    conditions = []
    params = {
        'from': filters.get('from'),
        'to': filters.get('to')
    }

    # Add conditions for filters if available
    if filters.get('customer'):
        conditions.append("client = %(customer)s")
        params['customer'] = filters.get('customer')

    if filters.get('project'):
        conditions.append("file_number = %(project)s")  # Make sure 'file_number' corresponds to 'Project' if needed
        params['project'] = filters.get('project')

    if filters.get('employee'):
        conditions.append("name1 = %(employee)s")  # Verify 'name1' is the correct field for Employee
        params['employee'] = filters.get('employee')

    if filters.get('invoiced'):
        conditions.append("is_invoiced = %(invoiced)s")  # Verify 'name1' is the correct field for Employee
        params['invoiced'] = filters.get('invoiced')

    # Build the WHERE clause
    where_clause = "WHERE date BETWEEN %(from)s AND %(to)s"
    if conditions:
        where_clause += " AND " + " AND ".join(conditions)

    # Prepare SQL query
    query = f"""
        SELECT
            t.amount,
            t.client,
            t.date,
            t.file_number,
            t.is_invoiced,
            t.purticulars,
            t.matter,
            t.name,
            t.name1,
            t.parent, 
            t.rate,
            t.time,
            e.custom_short_name AS lawyer_short_code,
            e.employee_name as emp_name
        FROM `tabLF Timesheet Item` t
        LEFT JOIN `tabEmployee` e ON t.name1 = e.name
        {where_clause}
        order by t.date,t.client,e.custom_short_name
    """
    
    frappe.errprint(query)  # Debugging: Output the query to check if it's correct
    return frappe.db.sql(query, params, as_dict=1)  # Execute the query and return the result

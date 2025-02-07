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
        {"label": "Expense", "fieldname": "parent", "fieldtype": "Link", 'options': 'LF Expense', "width": 120},
        {"label": "Client", "fieldname": "client", "fieldtype": "Link", 'options': 'Customer', 'width': 150},
        {"label": "Vendor", "fieldname": "vendor", "fieldtype": "Link", 'options': 'LF Vendor', 'width': 150},
        {"label": "Matter", "fieldname": "file_number", "fieldtype": "Link", 'options': 'Matter', 'width': 150},
        {"label": "Matter Name", "fieldname": "matter", "fieldtype": "Data", 'width': 180},
        {"label": "Amount", "fieldname": "amount", "fieldtype": "Float", "width": 120},
        {"label": "Vat", "fieldname": "vat", "fieldtype": "Float", "width": 120},
        {"label": "Total", "fieldname": "total", "fieldtype": "Float", "width": 120},
        {"label": "Particulars", "fieldname": "purticulars", "fieldtype": "Data", "width": 200},
        {"label": "Invoiced", "fieldname": "is_invoiced", "fieldtype": "Data", "width": 80},
        {"label": "Client Name", "fieldname": "customer_name", "fieldtype": "Data", "width": 0},

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

    if filters.get('vendor'):
        conditions.append("vendor = %(vendor)s")  # Verify 'name1' is the correct field for Employee
        params['vendor'] = filters.get('vendor')

    if filters.get('invoiced'):
        conditions.append("is_invoiced = %(invoiced)s")  # Verify 'name1' is the correct field for Employee
        params['invoiced'] = filters.get('invoiced')

    # Build the WHERE clause
    where_clause = "WHERE t.date BETWEEN %(from)s AND %(to)s"
    if conditions:
        where_clause += " AND " + " AND ".join(conditions)

    # Prepare SQL query
    query = f"""
        SELECT
            t.amount,
            t.client,
            c.customer_name,
            t.date,
            t.file_number,
            t.is_invoiced,
            t.purticulars,
            t.matter,
            t.name,
            tm.vendor,
            t.parent, 
            t.vat,
            t.total,
            e.name as emp_name
        FROM `tabLF Expense Item` t
        left join `tabLF Expense` tm on tm.name=t.parent
        LEFT JOIN `tabLF Vendor` e ON tm.vendor = e.name
        LEFT JOIN `tabCustomer` c ON t.client = c.name
        {where_clause}
        order by t.date,t.client
    """
    
    frappe.errprint(query)  # Debugging: Output the query to check if it's correct
    return frappe.db.sql(query, params, as_dict=1)  # Execute the query and return the result

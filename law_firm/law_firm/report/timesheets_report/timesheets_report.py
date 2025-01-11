# Copyright (c) 2025, Syed Malik Ali and contributors
# For license information, please see license.txt

import frappe


def execute(filters=None):
    columns = get_columns(filters)
    data = get_data(filters)
    return columns, data




def get_columns(filters):
    # Fetch distinct custom payment methods
    columns = [
        {"label": "Date", "fieldname": "date", "fieldtype": "Date", "width": 120},
        {"label": "Timesheet", "fieldname": "parent", "fieldtype": "Link",'options':'Employee', "width": 120},
        {"label": "Client", "fieldname": "client", "fieldtype": "Link", 'options': 'Customer', 'width': 150},
        {"label": "Lawyer", "fieldname": "name1", "fieldtype": "Link", 'options': 'Employee', 'width': 150},
        {"label": "Matter", "fieldname": "file_number", "fieldtype": "Link", 'options': 'Matter', 'width': 150},
        {"label": "Matter Name", "fieldname": "matter", "fieldtype": "Data", 'width': 180},
        {"label": "Hours", "fieldname": "time", "fieldtype": "Float", "width": 120},
        {"label": "Rate", "fieldname": "rate", "fieldtype": "Currency", "width": 120},
        {"label": "Amount", "fieldname": "amount", "fieldtype": "Currency", "width": 120},
        {"label": "Invoiced", "fieldname": "is_invoiced", "fieldtype": "Check", "width": 80},
       
    ]
    return columns  # Add this
    

def get_data(filters):
    # Initialize conditions
    conditions = ""

    # Add customer condition if provided
    customer = filters.get("customer")
    if customer:
        conditions =conditions+ f" AND client = '{customer}'"

    # Construct and execute the SQL query
    query = f"""
        SELECT
            amount,
            client,
            date,
            file_number,
            is_invoiced,
            matter,
            name,
            name1,
            parent, 
            rate,
            time
        FROM `tabLF Timesheet Item`
        WHERE date BETWEEN %(from)s AND %(to)s {conditions}
    """
    
    ts_data = frappe.db.sql(query, filters, as_dict=1)
    return ts_data
    
    



import frappe
from frappe.utils import nowdate


@frappe.whitelist()
def get_unique_custom_matter_code(base_series):
    last_code = frappe.db.sql("""
        SELECT custom_matter_code 
        FROM `tabProject` 
        WHERE custom_matter_code LIKE %s
        ORDER BY custom_matter_code DESC LIMIT 1
    """, (base_series + "%"))

    if last_code:
        # Extract the last numeric part from the custom_matter_code (after the last alphabetic character)
        # We are assuming the number always appears after the last alphabetic character
        import re
        match = re.search(r'(\d+)$', last_code[0][0])  # Match digits at the end of the string

        if match:
            last_number = match.group(1)  # Get the matched numeric part
            next_number = int(last_number) + 1
        else:
            next_number = 1  # In case no number is found, start from 1
    else:
        next_number = 1  # If no previous code exists, start from 1

    # Generate the unique code in the desired format
    return f"{base_series}{str(next_number).zfill(4)}"



# Used in fetching timesheet items in Invoice
@frappe.whitelist()
def get_lf_timesheet_items(filters, docname):
    # Parse filters to ensure it's a Python dictionary
    filters = frappe.parse_json(filters)

    # Step 1: Fetch and reset fields for all LF Timesheet Items linked to the given docname
    lf_timesheet_items = frappe.get_all(
        'LF Timesheet Item',
        filters={'invoice_number': docname},
        fields=['name']
    )
    
    for item in lf_timesheet_items:
        frappe.db.set_value('LF Timesheet Item', item['name'], {
            'is_invoiced': 'No',
            'invoice_number': ''
        })

    # Step 2: Extract and validate filters
    date_range = filters.get("date_range", [nowdate(), nowdate()])
    file_number = filters.get("project")

    # Step 3: Fetch LF Timesheet Items based on the filters provided
    timesheet_items = frappe.get_all(
        "LF Timesheet Item",
        filters={
            "date": ["between", date_range],  # Filter by date range
            "file_number": file_number,       # Filter by file number
            "is_invoiced": "No"               # Only fetch uninvoiced items
        },
        fields=[
            "name",
            "date",
            "file_number",
            "client",
            "matter",
            "purticulars",
            "time",
            "rate",
            "amount",
            "name1",
            "parent"
        ],
        order_by="date ASC"  # Ensure results are ordered by date
    )

    return timesheet_items  # Return the fetched items


# Used in fetching expense items in Invoice
@frappe.whitelist()
def get_lf_expense_items(filters,docname):
    filters = frappe.parse_json(filters)
    frappe.errprint(f"Filters received: {filters}")
    # Step 1: Fetch and reset fields for all LF Timesheet Items linked to the given docname
    lf_expense_items = frappe.get_all(
        'LF Expense Item',
        filters={'invoice_number': docname},
        fields=['name']
    )
    
    for item in lf_expense_items:
        frappe.db.set_value('LF Expense Item', item['name'], {
            'is_invoiced': 'No',
            'invoice_number': ''
        })

    # Extracting and validating filters
    date_range = filters.get("date_range", [nowdate(), nowdate()])
    file_number = filters.get("project")
    frappe.errprint(f"Date Range: {date_range}, File Number: {file_number}")

    # Fetching data
    expense_items = frappe.get_all(
        "LF Expense Item",
        filters={
            "date": ["between", date_range],
            "file_number": file_number,
            "is_invoiced": "No",
            "is_billable": 1,
        },
        fields=[
            "name",
            "date",
            "file_number",
            "client",
            "matter",
            "purticulars",
            "total",
            "vat",
            "is_billable",
            "amount",
            "name1",
            "parent"
        ],
        order_by="date ASC" 
    )
    return expense_items

@frappe.whitelist()
def get_unique_custom_client_code(base_series):
    # Fetch the last custom client code in the series
    last_code = frappe.db.sql("""
        SELECT CAST(SUBSTRING(custom_client_code, %s) AS UNSIGNED) AS last_number
        FROM `tabCustomer`
        WHERE custom_client_code LIKE %s
        ORDER BY last_number DESC
        LIMIT 1
    """, (len(base_series) + 1, base_series + "%"))

    if last_code and last_code[0][0]:
        # Extract the last number from the query result and increment it
        last_number = last_code[0][0]
        next_number = int(last_number) + 1
    else:
        # If no matching codes are found, start with 1
        next_number = 1

    # Generate the unique code in the desired format
    return f"{base_series}{str(next_number).zfill(4)}"


import frappe
from frappe import _

@frappe.whitelist()
def get_sales_invoice_data(from_date, to_date):
    """
    Returns Sales Invoice header and detail items for invoices in the given period,
    grouped by cost center.
    """
    # Query Sales Invoice header data; adjust field names as needed.
    invoices = frappe.db.sql(
        """
        SELECT 
            si.name AS invoice,
            si.posting_date AS invoice_date,
            si.customer AS customer_code,
            si.customer_name,
            si.grand_total AS invoice_amount,
            si.discount_amount AS disc,
            (si.grand_total - si.discount_amount) AS amount_after_disc,
            si.total_taxes_and_charges AS tax,
            si.grand_total AS total_amount,
            si.cost_center
        FROM `tabSales Invoice` si
        WHERE si.posting_date BETWEEN %s AND %s
          AND si.docstatus = 1
        ORDER BY si.cost_center, si.posting_date
        """,
        (from_date, to_date),
        as_dict=True
    )

    # Group invoices by cost center.
    cost_center_map = {}
    for inv in invoices:
        cost_center = inv.cost_center or "Not Specified"
        if cost_center not in cost_center_map:
            cost_center_map[cost_center] = []
        cost_center_map[cost_center].append(inv)

    # For each invoice, fetch its item details.
    for cost_center, inv_list in cost_center_map.items():
        for inv in inv_list:
            invoice_items = frappe.db.sql(
                """
                SELECT
                    idx,
                    item_code AS itemcode,
                    item_name,
                    qty,
                    rate AS unit_price,
                    amount,
                    discount_amount AS disc,
                    item_tax_rate
                FROM `tabSales Invoice Item`
                WHERE parent = %s
                ORDER BY idx
                """,
                inv.invoice,
                as_dict=True
            )
            
            # Process each item to calculate tax_amount and total
            for item in invoice_items:
                tax_percentage = 0.0
                if item.get("item_tax_rate"):
                    try:
                        tax_rate_dict = json.loads(item.get("item_tax_rate"))
                        # Assume there's only one key-value pair; use the first percentage value.
                        if tax_rate_dict:
                            tax_percentage = list(tax_rate_dict.values())[0]
                    except Exception as e:
                        frappe.log_error(message=str(e), title="Error parsing item_tax_rate")
                        tax_percentage = 0.0

                net_amount = item["amount"] - item["disc"]
                item["tax_amount"] = net_amount * tax_percentage / 100.0
                item["total"] = net_amount + item["tax_amount"]

            inv['details'] = invoice_items

    # Build a list of groups for the report.
    data = []
    for cost_center, inv_list in cost_center_map.items():
        data.append({
            "cost_center": cost_center,
            "invoices": inv_list
        })

    return data
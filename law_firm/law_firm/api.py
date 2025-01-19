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
def get_lf_timesheet_items(filters):
    filters = frappe.parse_json(filters)
    frappe.errprint(f"Filters received: {filters}")

    # Extracting and validating filters
    date_range = filters.get("date_range", [nowdate(), nowdate()])
    file_number = filters.get("project")
    frappe.errprint(f"Date Range: {date_range}, File Number: {file_number}")

    # Fetching data
    timesheet_items = frappe.get_all(
        "LF Timesheet Item",
        filters={
            "date": ["between", date_range],
            "file_number": file_number,
            "is_invoiced": "No",
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
        ]
    )
    frappe.errprint(f"Timesheet Items: {timesheet_items}")
    return timesheet_items


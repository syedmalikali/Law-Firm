import frappe

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

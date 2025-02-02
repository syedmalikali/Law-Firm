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
                    tax_amount,
                    (amount - discount_amount + tax_amount) AS total
                FROM `tabSales Invoice Item`
                WHERE parent = %s
                ORDER BY idx
                """,
                inv.invoice
            )
            inv['details'] = invoice_items

    # Build a list of groups for the report.
    data = []
    for cost_center, inv_list in cost_center_map.items():
        data.append({
            "cost_center": cost_center,
            "invoices": inv_list
        })

    return data

frappe.pages['sales-invoice-report'].on_page_load = function(wrapper) {
    var page = frappe.ui.make_app_page({
        parent: wrapper,
        title: 'Sales Invoice Report',
        single_column: true
    });

    // Adding filters using Frappe's built-in `add_field` method
    page.from_date = page.add_field({
        fieldname: "from_date",
        label: __("From Date"),
        fieldtype: "Date",
        default: frappe.datetime.add_days(frappe.datetime.get_today(), -30),
        change: function () {
            page.refresh_report();
        },
    });

    page.to_date = page.add_field({
        fieldname: "to_date",
        label: __("To Date"),
        fieldtype: "Date",
        default: frappe.datetime.get_today(),
        change: function () {
            page.refresh_report();
        },
    });

    page.cost_center_field = page.add_field({
        fieldname: "cost_center",
        label: __("Cost Center"),
        fieldtype: "Link",
        options: "Cost Center",
        default: frappe.route_options && frappe.route_options.cost_center,
        change: function () {
            page.refresh_report();
        },
    });

    var report_container = $('<div id="report-container"></div>');
    $(page.body).append(report_container);

    // Function to refresh report based on filters
    page.refresh_report = function () {
        var fd = page.from_date.get_value();
        var td = page.to_date.get_value();
        var cc = page.cost_center_field.get_value();

        if (!fd || !td) {
            frappe.msgprint(__('Please select both From Date and To Date'));
            return;
        }

        frappe.call({
            method: 'law_firm.law_firm.api.get_sales_invoice_data',
            args: {
                from_date: fd,
                to_date: td,
                cost_center: cc,  // Passed to the server
            },
            callback: function(r) {
                if (r.message) {
                    render_report(r.message, cc);
                }
            }
        });
    };

    function render_report(data, selected_cost_center) {
        report_container.empty();
        var grand_total = 0;

        data.forEach(function(group) {
            // Client-side filtering for cost center if selected
            if (selected_cost_center && group.cost_center !== selected_cost_center) {
                return;
            }

            var cc_header = $('<h3 class="cost-center-header"></h3>').text('Cost Center: ' + group.cost_center);
            report_container.append(cc_header);

            group.invoices.forEach(function(inv) {
                grand_total += parseFloat(inv.total_amount) || 0;

                var table = $('<table class="table table-bordered table-hover invoice-table"></table>');

                var thead = $('<thead class="invoice-thead"></thead>');
                thead.append(
                    '<tr>' +
                        '<th>Invoice Date</th>' +
                        '<th>Customer Code</th>' +
                        '<th>Customer Name</th>' +
                        '<th>Cost Center</th>' +
                        '<th>Invoice Amount</th>' +
                        '<th>Disc</th>' +
                        '<th>Amount After Disc</th>' +
                        '<th>Tax</th>' +
                        '<th>Total Amount</th>' +
                    '</tr>'
                );
                table.append(thead);

                var tbody = $('<tbody></tbody>');
                var header_row = $('<tr class="invoice-header"></tr>');
                header_row.append(
                    '<td>' + inv.invoice_date + '</td>' +
                    '<td>' + inv.customer_code + '</td>' +
                    '<td>' + inv.customer_name + '</td>' +
                    '<td>' + inv.cost_center + '</td>' +
                    '<td>' + inv.invoice_amount + '</td>' +
                    '<td>' + inv.disc + '</td>' +
                    '<td>' + inv.amount_after_disc + '</td>' +
                    '<td>' + inv.tax + '</td>' +
                    '<td>' + inv.total_amount + '</td>'
                );
                tbody.append(header_row);

                inv.details.forEach(function(item) {
                    var detail_row = $('<tr class="detail-row"></tr>');
                    detail_row.append(
                        '<td>' + item.idx + '</td>' +
                        '<td>' + item.itemcode + '</td>' +
                        '<td>' + item.item_name + '</td>' +
                        '<td>' + item.qty + '</td>' +
                        '<td>' + item.unit_price + '</td>' +
                        '<td>' + item.amount + '</td>' +
                        '<td>' + item.disc + '</td>' +
                        '<td>' + item.tax_amount + '</td>' +
                        '<td>' + item.total + '</td>'
                    );
                    tbody.append(detail_row);
                });

                table.append(tbody);
                report_container.append(table);
            });
        });

        var footer = $('<div class="report-footer" style="text-align:right; font-weight:bold; margin-top:20px;"></div>');
        footer.text('Grand Total: ' + grand_total.toFixed(2));
        report_container.append(footer);
    }
};

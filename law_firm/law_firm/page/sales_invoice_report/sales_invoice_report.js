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
        var report_style = $(`
 <style>
.report-filters {
  margin-bottom: 20px;
}

.report-filters label {
  margin-right: 10px;
  font-weight: bold;
}
.invoice-table th, .invoice-table td {
    padding: 2px!important;
}
.invoice-header-table {
  margin-top: 20px;
  
}
.invoice-heder {
    font-weight: bold!important;
}

.invoice-details-table {
  margin-bottom: 40px;
  padding:1px;
}
.money {
 text-align:right;
}
.cost-center-header {
  margin-top: 40px;
  background-color: #ececec;
  padding: 10px;
  border-left: 5px solid #007bff;
}

</style>
`);
        
        var grand_total = 0;
         report_container.append(report_style);
        data.forEach(function(group) {
            // Client-side filtering for cost center if selected
            if (selected_cost_center && group.cost_center !== selected_cost_center) {
                return;
            }

            var cc_header = $('<h3 class="cost-center-header"></h3>').text('Cost Center: ' + group.cost_center);
            report_container.append(cc_header);
var table = $('<table class="table table-sm table-bordered table-hover invoice-table"></table>');

                var thead = $('<thead class="invoice-thead"></thead>');
                thead.append(
                    '<tr>' +
                        '<th>Date<br><small>Sno </small></th>' +
                        '<th>Customer Code <br><small>Item Code </small> </th>' +
                        '<th>Customer Name <br><small>Description </small> </th>' +
                        '<th>Cost Center <br><small>Qty </small></th>' +
                        '<th>Invoice Amount <br><small>Rate </small> </th>' +
                        '<th>Disc <br><small>Amount </small></th>' +
                        '<th>Amount After Disc <br><small>Disc </small></th>' +
                        '<th>Tax <br><small>Tax </small></th>' +
                        '<th>Total Amount <br><small>Total </small></th>' +
                    '</tr>'
                );
                table.append(thead);
            group.invoices.forEach(function(inv) {
                grand_total += parseFloat(inv.total_amount) || 0;

                

                var tbody = $('<tbody></tbody>');
var header_row = $('<tr class="invoice-header" style=" font-weight: bold!important;"></tr>');
                header_row.append(
                    '<td>' + inv.invoice_date + '</td>' +
                    '<td>' + inv.customer_code + '</td>' +
                    '<td>' + inv.customer_name + '</td>' +
                    '<td>' + inv.cost_center + '</td>' +
                    '<td class="money">' + parseFloat(inv.invoice_amount).toFixed(2)  + '</td>' +
                    '<td class="money">' + parseFloat(inv.disc).toFixed(2)  + '</td>' +
                    '<td class="money">' + parseFloat(inv.amount_after_disc).toFixed(2)  + '</td>' +
                    '<td class="money">' + parseFloat(inv.tax).toFixed(2)  + '</td>' +
                    '<td class="money">' + parseFloat(inv.total_amount).toFixed(2)  + '</td>'
                );
                tbody.append(header_row);                

                inv.details.forEach(function(item) {
                    var detail_row = $('<tr class="detail-row"></tr>');
                    detail_row.append(
                        '<td>' + item.idx + '</td>' +
                        '<td>' + item.itemcode + '</td>' +
                        '<td>' + item.item_name + '</td>' +
                        '<td>' + item.qty + '</td>' +
                        '<td class="money">' + parseFloat(item.unit_price).toFixed(2)  + '</td>' +
                        '<td class="money">' + parseFloat(item.amount).toFixed(2)  + '</td>' +
                        '<td class="money">' + parseFloat(item.disc).toFixed(2)  + '</td>' +
                        '<td class="money">' + parseFloat(item.tax_amount).toFixed(2)  + '</td>' +
                        '<td class="money">' + parseFloat(item.total).toFixed(2)  + '</td>'
                    );
                    tbody.append(detail_row);
                });
var header_row = $('<tr class="invoice-header" style=" font-weight: bold!important;"></tr>');
                header_row.append(
                    '<td>' + '</td>' +
                    '<td>'  +'</td>' +
                    '<td>' + '</td>' +
                    '<td>' + '</td>' +
                    '<td class="money">' + parseFloat(inv.invoice_amount).toFixed(2)  + '</td>' +
                    '<td class="money">' + parseFloat(inv.disc).toFixed(2)  + '</td>' +
                    '<td class="money">' + parseFloat(inv.amount_after_disc).toFixed(2)  + '</td>' +
                    '<td class="money">' + parseFloat(inv.tax).toFixed(2)  + '</td>' +
                    '<td class="money">' + parseFloat(inv.total_amount).toFixed(2)  + '</td>'
                );
                tbody.append(header_row);
                table.append(tbody);
                report_container.append(table);
            });
        });

        var footer = $('<div class="report-footer" style="text-align:right; font-weight:bold; margin-top:20px;"></div>');
        footer.text('Grand Total: ' + grand_total.toFixed(2));
        report_container.append(footer);
    }
};

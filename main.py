import matrixify_functions
import csv

processed_orders = []
final_data = []
final_refunds = []
suffix = ''
with open('input/orders_to_01-12-2021.csv', encoding='utf-8') as f:
    data = [{k: v for k, v in row.items()}
            for row in csv.DictReader(f, skipinitialspace=True)]

    for line in data:
        discount = float(line['Cart Discount Amount']) if ',' not in line['Cart Discount Amount'] else 0
        if not line['Order Number'] in processed_orders:
            processed_orders.append(line['Order Number'])
            final_data.append(matrixify_functions.create_payment_line(line))
            if discount > 0:
                final_data.append(matrixify_functions.create_discount_line(line))
            if float(line['Order Refund Amount']) > 0:
                final_refunds.append(matrixify_functions.create_refund_line(line))
        final_data.append(matrixify_functions.create_product_line(line))


    keys = final_data[0].keys()
    with open(f'output/orders/orders_to_shopify{suffix}.csv', 'w', newline='', encoding='utf-8') as output_file:
        dict_writer = csv.DictWriter(output_file, keys)
        dict_writer.writeheader()
        dict_writer.writerows(final_data)
    with open(f'output/refunds/orders_refunds_to_shopify{suffix}.csv', 'w', newline='', encoding='utf-8') as output_file:
        dict_writer = csv.DictWriter(output_file, keys)
        dict_writer.writeheader()
        dict_writer.writerows(final_refunds)

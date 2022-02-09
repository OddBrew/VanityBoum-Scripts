import copy
import datetime

line_template = {
    'ID': '',
    'Name': '',
    'Command': 'REPLACE',
    'Tags': 'import-woo',
    'Processed At': '',
    'Closed At': '',
    'Currency': 'EUR',
    'Tax 1: Title': 'TVA',
    'Tax 1: Rate': 0.2,
    'Tax 1: Price': '',
    'Tax: Included': 'FALSE',
    'Payment: Status': 'paid',
    'Email': '',
    'Billing: First Name': '',
    'Billing: Last Name': '',
    'Billing: Company': '',
    'Billing: Phone': '',
    'Billing: Address 1': '',
    'Billing: Address 2': '',
    'Billing: Zip': '',
    'Billing: City': '',
    'Billing: Country Code': '',
    'Shipping: First Name': '',
    'Shipping: Last Name': '',
    'Shipping: Company': '',
    'Shipping: Address 1': '',
    'Shipping: Address 2': '',
    'Shipping: Zip': '',
    'Shipping: City': '',
    'Shipping: Country Code': '',
    'Line: Type': '',
    'Line Command': 'MERGE',
    'Line: Title': '',
    'Line: Name': '',
    'Line: SKU': '',
    'Line: Price': '',
    'Line: Quantity': '',
    'Line: Discount': '',  # Whole order discount
    'Line: Gift Card': 'FALSE',
    'Line: Force Gift Card': 'No',
    'Line: Taxable': 'TRUE',
    'Transaction: Kind': '',
    'Transaction: Processed At': '',
    'Transaction: Amount': '',
    'Transaction: Currency': 'EUR',
    'Transaction: Status': 'success',
    'Transaction: Force Gateway': 'FALSE',
    'Refund: Created At': '',
    'Refund: Restock': 'FALSE',
    'Refund: Note': '',
    'Refund: Generate Transaction': 'TRUE',
    'Fulfillment: Status': 'success',
    'Fulfillment: Shipment Status': 'delivered',
    'Fulfillment: Processed At': '',
    'Fulfillment: Tracking Number': '',
    'Fulfillment: Tracking URL': ''
}


def create_basic_line(export_line: dict) -> dict:
    new_line = copy.deepcopy(line_template)
    order_date = datetime.datetime.strptime(export_line['Order Date'], '%B %d, %Y %H:%M').strftime(
        '%Y-%m-%d %H:%M:00 +0100')
    new_line.update({
        'Name': 'WOO#' + export_line['Order Number'],
        'Processed At': order_date,
        'Closed At': order_date,
        'Tax 1: Price': export_line['Order Total Tax Amount'],
        'Email': export_line['Email (Billing)'],
        'Billing: First Name': export_line['First Name (Billing)'] or 'Prénom',
        'Billing: Last Name': export_line['Last Name (Billing)'] or 'Nom',
        'Billing: Company': export_line['Company (Billing)'],
        'Billing: Phone': export_line['Phone (Billing)'],
        'Billing: Address 1': export_line['Address 1 (Billing)'] or 'Vanity Boum',
        'Billing: Address 2': export_line['Address 2 (Billing)'],
        'Billing: Zip': export_line['Postcode (Billing)'],
        'Billing: City': export_line['City (Billing)'] or 'Paris',
        'Billing: Country Code': export_line['Country Code (Billing)'] or 'FR',
        'Shipping: First Name': export_line['First Name (Shipping)'] or 'Prénom',
        'Shipping: Last Name': export_line['Last Name (Shipping)'] or 'Nom',
        'Shipping: Company': export_line['Company (Shipping)'],
        'Shipping: Phone': export_line['Phone (Billing)'],
        'Shipping: Address 1': export_line['Address 1 (Shipping)'] or 'Vanity Boum',
        'Shipping: Address 2': export_line['Address 2 (Shipping)'],
        'Shipping: Zip': export_line['Postcode (Shipping)'],
        'Shipping: City': export_line['City (Shipping)'] or 'Paris',
        'Shipping: Country Code': export_line['Country Code (Shipping)'] or 'FR',
        'Shipping Line: Title': export_line['Shipping Method Title'] or 'Méthode non-renseignée',
        'Shipping Line: Code': 'custom',
        'Shipping Line: Price': export_line['Order Shipping Amount'],
        'Fulfillment: Processed At': order_date,
        'Fulfillment: Tracking Number': export_line['Tracking Colissimo'],
        'Fulfillment: Tracking URL': 'https://www.laposte.fr/outils/suivre-vos-envois?code='+export_line['Tracking Colissimo'] if export_line['Tracking Colissimo'] else ''
    })
    # if export_line['Order Total Amount'] == export_line['Order Refund Amount']:
    #     new_line.update({'Payment: Status': 'refunded'})
    # elif export_line['Order Refund Amount']:
    #     new_line.update({'Payment: Status': 'partially_refunded'})

    return new_line


def create_refund_line(export_line: dict) -> dict:
    new_line = create_basic_line(export_line)
    refund_date = datetime.datetime.strptime(export_line['Date of first refund'], '%B %d, %Y %H:%M').strftime(
        '%Y-%m-%d %H:%M:00 +0100')
    new_line.update({
        'Command': 'MERGE',
        'Line: Type': 'Transaction',
        'Refund: Created At': refund_date,
        'Refund: Note': export_line['Customer Note'] or 'Imported refund',
        'Line: Title': export_line['Customer Note'] or 'Imported refund',
        'Line: Name': export_line['Customer Note'] or 'Imported refund',
        'Transaction: Kind': 'refund',
        'Transaction: Processed At': refund_date,
        'Transaction: Amount': export_line['Order Refund Amount'],
    })
    return new_line


def create_payment_line(export_line: dict) -> dict:
    new_line = create_basic_line(export_line)
    new_line.update({
        'Line: Type': 'Transaction',
        'Transaction: Kind': 'sale',
        'Transaction: Processed At': datetime.datetime.strptime(export_line['Order Date'], '%B %d, %Y %H:%M').strftime(
            '%Y-%m-%d %H:%M:00 +0100'),
        'Transaction: Amount': export_line['Order Total Amount']
    })
    return new_line


def create_discount_line(export_line: dict) -> dict:
    new_line = create_basic_line(export_line)
    new_line.update({
        'Line: Type': 'Discount',
        'Line: Name': export_line['Coupon Code'] or 'No Discount Code',
        'Line: Discount': '-' + export_line['Cart Discount Amount']
    })
    return new_line


def create_shipping_line(export_line: dict) -> dict:
    new_line = create_basic_line(export_line)
    new_line.update({
        'Line: Type': 'Shipping Line',
        'Line: Title': export_line['Shipping Method Title'] or 'Méthode non-renseignée'
    })
    return new_line


def create_product_line(export_line: dict) -> dict:
    new_line = create_basic_line(export_line)
    price = export_line['Item Cost Before Discount']
    new_line.update({
        'Line: Type': 'Line Item',
        'Line: Title': export_line['Item Name'] or 'Produits personnalisés',
        'Line: SKU': export_line['SKU'],
        'Line: Price': price,
        'Line: Quantity': export_line['Quantity']
    })
    if not export_line['Quantity']:
        new_line.update({
            'Tags': 'import-woo, missing-product',
            'Line: Quantity': 1,
            'Line: Price': float(export_line['Order Total Amount']) - float(export_line['Order Total Tax Amount'])
        })

    if export_line['Item Name'] == 'Carte cadeau':
        new_line.update({'Line: Gift Card': 'TRUE'})

    return new_line

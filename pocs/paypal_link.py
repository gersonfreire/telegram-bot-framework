import urllib.parse

def generate_paypal_link(business_email, item_name, amount, currency='USD'):
    base_url = "https://www.paypal.com/cgi-bin/webscr"
    params = {
        'cmd': '_xclick',
        'business': business_email,
        'item_name': item_name,
        'amount': amount,
        'currency_code': currency
    }
    query_string = urllib.parse.urlencode(params)
    return f"{base_url}?{query_string}"

# Example usage
business_email = "your-paypal-email@example.com"
business_email = "gerson.freire-facilitator@gmail.com"
item_name = "Sample Item"
amount = "10.00"
currency = "USD"

paypal_link = generate_paypal_link(business_email, item_name, amount, currency)
print("PayPal Payment Link:", paypal_link)
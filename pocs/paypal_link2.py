# Step 1: Install the PayPal SDK
# pip install paypalrestsdk

# Step 2: Set Up PayPal SDK
import os, logging, dotenv
import paypalrestsdk

dotenv.load_dotenv()

client_id = os.getenv("PAYPAL_CLIENT_ID")
client_secret = os.getenv("PAYPAL_CLIENT_SECRET")

# paypal rfbot app  gerson.freire@gmail.com Life@2011

paypalrestsdk.configure({
    "mode": "sandbox",  # sandbox or live
    "client_id": client_id,
    "client_secret": client_secret
})

# Step 3: Create a Payment
payment = paypalrestsdk.Payment({
    "intent": "sale",
    "payer": {
        "payment_method": "paypal"},
    "redirect_urls": {
        "return_url": "http://localhost:3000/payment/execute",
        "cancel_url": "http://localhost:3000/payment/cancel"},
    "transactions": [{
        "item_list": {
            "items": [{
                "name": "item",
                "sku": "item",
                "price": "5.00",
                # "currency": "USD",
                "currency": "BRL",
                "quantity": 1}]},
        "amount": {
            "total": "5.00",
            # "currency": "USD"},
            "currency": "BRL"},
        "description": "This is the payment transaction description."}]})

# Step 4: Generate the Payment Link
if payment.create():
    print("Payment created successfully")
    for link in payment.links:
        if link.rel == "approval_url":
            approval_url = str(link.href)
            print("Redirect for approval: %s" % (approval_url))
else:
    print(payment.error)
    
    
"""
Step 1: Install the PayPal SDK
First, you need to install the PayPal SDK. You can do this using pip.

Step 2: Set Up PayPal SDK
You need to set up the PayPal SDK with your client ID and secret. You can get these from your PayPal developer account.

Step 3: Create a Payment
Create a payment object with the necessary details like amount, currency, and redirect URLs.

Step 4: Generate the Payment Link
Extract the approval URL from the payment object to get the link that you can share with others to receive payments.

Explanation:
Install the PayPal SDK: Use pip to install the PayPal SDK.
Set Up PayPal SDK: Configure the SDK with your client ID and secret.
Create a Payment: Define the payment details including the amount, currency, and redirect URLs.
Generate the Payment Link: Extract the approval URL from the payment object and print it.
Replace "YOUR_CLIENT_ID" and "YOUR_CLIENT_SECRET" with your actual PayPal client ID and secret. The approval_url is the link you can share to receive payments.

"""    
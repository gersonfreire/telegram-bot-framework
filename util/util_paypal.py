# Step 1: Install the PayPal SDK
# pip install paypalrestsdk

# Step 2: Set Up PayPal SDK
import os, logging, dotenv
import paypalrestsdk

def create_payment():
    dotenv.load_dotenv()

    client_id = os.getenv("PAYPAL_CLIENT_ID")
    client_secret = os.getenv("PAYPAL_CLIENT_SECRET")

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
    
      
import os, dotenv
from flask import Flask, request, redirect, url_for
import paypalrestsdk

dotenv.load_dotenv()

client_id = os.getenv("PAYPAL_CLIENT_ID")
client_secret = os.getenv("PAYPAL_CLIENT_SECRET")   

# Get webhook URL from the .env file
DEFAULT_RETURN_URL = os.environ.get('PAYPAL_DEFAULT_RETURN_URL', "http://localhost:5000/payment/execute")
DEFAULT_CANCEL_URL = os.environ.get('PAYPAL_DEFAULT_CANCEL_URL', "http://localhost:5000/payment/cancel")

execute_payment_callback = None
CANCEL_PAYMENT_CALLBACK = None

app = Flask(__name__)

# Configure PayPal SDK
paypalrestsdk.configure({
    "mode": "sandbox",  # sandbox or live
    "client_id": client_id,
    "client_secret": client_secret
})

# --------------------------------

@app.route('/payment/link', methods=['GET'])
def create_payment(
    return_url=DEFAULT_RETURN_URL, 
    cancel_url=DEFAULT_CANCEL_URL, 
    total="5.00", 
    currency="BRL", 
    description="This is the payment transaction description.",
    client_id = os.getenv("PAYPAL_CLIENT_ID") ,
    client_secret = os.getenv("PAYPAL_CLIENT_SECRET")
    ): 

    try:  

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
                "return_url": return_url,
                "cancel_url": cancel_url},
            "transactions": [{
                "item_list": {
                    "items": [{
                        "name": "item",
                        "sku": "item",
                        "price": "5.00",
                        "currency": "BRL",
                        "quantity": 1}]},
                "amount": {
                    "total": total,
                    "currency": currency},
                "description": description}]})

        # Step 4: Generate the Payment Link
        if payment.create():
            print("Payment created successfully")
            for link in payment.links:
                if link.rel == "approval_url":
                    approval_url = str(link.href)
                    print("Redirect for approval: %s" % (approval_url))
                    return approval_url
                    
        else:
            print(payment.error)
            
    except Exception as e:
        print(f"An error occurred: {e}")

# -------------------------------- 

@app.route('/payment/execute', methods=['GET'])
def execute_payment():
    try:
        payment_id = request.args.get('paymentId')
        payer_id = request.args.get('PayerID')

        payment = paypalrestsdk.Payment.find(payment_id)
        
        # call the callback function
        if execute_payment_callback:
            execute_payment_callback(payment, payment_id, payer_id)

        if payment.execute({"payer_id": payer_id}):
            print("Payment executed successfully")
            return "Payment executed successfully"
        else:
            print(payment.error)
            return "Payment execution failed"
        
    except Exception as e:
        print(f"An error occurred: {e}")
        return "Payment execution failed"

@app.route('/payment/cancel', methods=['GET'])
def cancel_payment():
    
    try:
        if CANCEL_PAYMENT_CALLBACK:
            CANCEL_PAYMENT_CALLBACK()
        return "Payment cancelled"
    except Exception as e:
        print(f"An error occurred: {e}")
        return "Payment cancellation failed"

def main(debug=True):
    
    create_payment()
    
    app.run(debug=False)

if __name__ == '__main__':
    main()
    
# app.run()
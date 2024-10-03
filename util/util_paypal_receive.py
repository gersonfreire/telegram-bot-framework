import os, dotenv
from flask import Flask, request, redirect, url_for
import paypalrestsdk

dotenv.load_dotenv()

client_id = os.getenv("PAYPAL_CLIENT_ID")
client_secret = os.getenv("PAYPAL_CLIENT_SECRET")

app = Flask(__name__)

# Configure PayPal SDK
paypalrestsdk.configure({
    "mode": "sandbox",  # sandbox or live
    "client_id": client_id,
    "client_secret": client_secret
})

@app.route('/payment/execute', methods=['GET'])
def execute_payment():
    payment_id = request.args.get('paymentId')
    payer_id = request.args.get('PayerID')

    payment = paypalrestsdk.Payment.find(payment_id)

    if payment.execute({"payer_id": payer_id}):
        print("Payment executed successfully")
        return "Payment executed successfully"
    else:
        print(payment.error)
        return "Payment execution failed"

@app.route('/payment/cancel', methods=['GET'])
def cancel_payment():
    return "Payment cancelled"

def main():
    app.run(debug=True)

if __name__ == '__main__':
    main()
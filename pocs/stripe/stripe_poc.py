import json
import os
import requests
import dotenv
import stripe

dotenv.load_dotenv()
your_stripe_secret_key = os.getenv('STRIPE_SECRET_KEY')

def create_checkout_session(items):
  url = 'https://api.stripe.com/v1/checkout/sessions'
  headers = {'Authorization': f'Bearer {your_stripe_secret_key}'}
  data = {
    'line_items': [
      {
        'price': 'price_1234567890',  # Replace with your product price ID
        'quantity': 1
      }
    ],
    'mode': 'payment',
    'success_url': 'https://your-website.com/success',
    'cancel_url': 'https://your-website.com/cancel'
  }

  response = requests.post(url, headers=headers, json=data)
  session_id = response.json()['id']
  """
'{\n  "error": {\n    "message": "Invalid request (check that your POST content type is application/x-www-form-urlencoded). If you have any questions, we can help at https://support.stripe.com/.",\n    "type": "invalid_request_error"\n  }\n}\n'  
  """
  return session_id

# Send the session ID to the user via Telegram
# ...

# Handle the webhook from Stripe
# @app.route('/stripe/webhook', methods=['POST'])
def stripe_webhook():
  event = stripe.Event.construct_from(json.loads(requests.request.data), stripe.api_key)
  if event.type == 'checkout.session.completed':
    session = event.data.object
    stripe_token = session['payment_intent']['id']
    # Use the Stripe token to process the payment
    # ...
    return 'Webhook received and processed', 200
  
if __name__ == '__main__':
  items = ['product_1234567890']
  session_id = create_checkout_session(items)
  print(f'Checkout session ID: {session_id}')
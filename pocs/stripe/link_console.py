import stripe
import os
from dotenv import load_dotenv

# https://dashboard.stripe.com/test/developers

# Load environment variables from a .env file
load_dotenv()

# Set your secret key. Remember to switch to your live secret key in production!
stripe.api_key = os.getenv('STRIPE_SECRET_KEY')

def create_checkout_session():
    try:
        session = stripe.checkout.Session.create(
            payment_method_types=['card'],
            line_items=[{
                'price_data': {
                    'currency': 'usd',
                    'product_data': {
                        'name': 'T-shirt',
                    },
                    'unit_amount': 2000,  # Amount in cents
                },
                'quantity': 1,
            }],
            mode='payment',
            success_url='https://yourdomain.com/success?session_id={CHECKOUT_SESSION_ID}',
            cancel_url='https://yourdomain.com/cancel',
        )
        return session.url
    except Exception as e:
        print(f"An error occurred: {e}")
        return None

if __name__ == "__main__":
    payment_link = create_checkout_session()
    if payment_link:
        print(f"Checkout payment link: {payment_link}")
    else:
        print("Failed to create checkout session.")
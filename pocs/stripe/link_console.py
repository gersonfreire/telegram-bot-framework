import stripe
import os
from dotenv import load_dotenv

# https://dashboard.stripe.com/test/developers

# Load environment variables from a .env file
load_dotenv(override=True)

# --- Get default environment variables ---

# Set your secret key. Remember to switch to your live secret key in production!
STRIPE_API_KEY = stripe.api_key = os.getenv('STRIPE_SECRET_KEY')

PAYMENT_METHOD_TYPES = os.getenv('PAYMENT_METHOD_TYPES', 'card').split(',')
CURRENCY = os.getenv('CURRENCY', 'brl')
PRODUCT_NAME = os.getenv('PRODUCT_NAME', 'Adicionar creditos')
UNIT_AMOUNT = int(os.getenv('UNIT_AMOUNT', 500))
QUANTITY = int(os.getenv('QUANTITY', 1))
MODE = os.getenv('MODE', 'payment')
SUCCESS_URL = os.getenv('SUCCESS_URL', 'https://yourdomain.com/success?session_id={CHECKOUT_SESSION_ID}')
CANCEL_URL = os.getenv('CANCEL_URL', 'https://yourdomain.com/cancel')

# --- Create a Checkout Session ---

def create_test_checkout_session():
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

def create_checkout_session(
    stripe_api_key=STRIPE_API_KEY,
    payment_method_types=PAYMENT_METHOD_TYPES,
    currency=CURRENCY,
    product_name=PRODUCT_NAME,
    unit_amount=UNIT_AMOUNT,
    quantity=QUANTITY,
    mode=MODE,
    success_url=SUCCESS_URL,
    cancel_url=CANCEL_URL,
):
    try:
        stripe.api_key = stripe_api_key
        
        session = stripe.checkout.Session.create(
            payment_method_types=payment_method_types,
            line_items=[{
                'price_data': {
                    'currency': currency,
                    'product_data': {
                        'name': product_name,
                    },
                    'unit_amount': unit_amount,  # Amount in cents
                },
                'quantity': quantity,
            }],
            mode=mode,
            success_url=success_url,
            cancel_url=cancel_url,
        )
        return session.url
    
    except Exception as e:
        print(f"An error occurred: {e}")
        return None

if __name__ == "__main__":
    
    # payment_link = create_test_checkout_session()
    payment_link = create_checkout_session()
    
    if payment_link:
        print(f"Checkout payment link: {payment_link}")
    else:
        print("Failed to create checkout session.")
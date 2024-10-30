To generate a Stripe payment link using Python, you can follow these steps. This script will create a Stripe Checkout session and print the payment link to the console.

### Step-by-Step Guide

1. **Install the Stripe Python library**:

   ```bash
   pip install stripe
   ```
2. **Create the Python script**:

```py
import stripe
import os
from dotenv import load_dotenv

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
```

### Explanation

1. **Install the Stripe Python library**:

   ```bash
   pip install stripe
   ```
2. **Set up your Stripe API key**:

   - Create a

.env

 file in the same directory as your script and add your Stripe secret key:
     ``     STRIPE_SECRET_KEY=sk_test_your_secret_key     ``

3. **Create a Checkout session**:

   - The `create_checkout_session` function creates a Stripe Checkout session with the necessary parameters, such as payment method types, line items, and success/cancel URLs.
4. **Generate the payment link**:

   - The script calls the `create_checkout_session` function to create the Checkout session and get the payment link.
   - It prints the payment link to the console.

### Running the Script

1. Save the script to a file, e.g., `generate_stripe_payment_link.py`.
2. Run the script:
   ```bash
   python generate_stripe_payment_link.py
   ```

This will print the Stripe Checkout payment link to the console, which you can then use to complete the payment.This will print the Stripe Checkout payment link to the console, which you can then use to complete the payment.

Similar code found with 1 license type

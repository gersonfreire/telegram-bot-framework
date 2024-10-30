import subprocess
import time
import stripe
import os
from dotenv import load_dotenv

# --------------------------------

# set and build logging
import logging

import requests
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

# test logger
logger.debug(f'Starting the {__file__}...')

# ------------- Stripe Webhook using flask ------------------

from flask import Flask, request, redirect, url_for
app = Flask(__name__)

# ----------------Start ngrok ----------------

def start_ngrok(ngrok_port=5000):
    """Starts ngrok to expose the local server to the internet.

    Returns:
        _type_: ngrok URL if successful, None otherwise.
    """
    
    try:
        
        # check if ngrok is already running
        response = None
        try:
            response = requests.get(f'http://localhost:4040/api/tunnels')
        except requests.exceptions.RequestException as e:
            logger.error(f"ngrok is not running! An error occurred while checking ngrok tunnels: {e}")
        
        if not response or response.status_code != 200:            
            logger.debug("Ngrok is not running. Starting ngrok...")
                        
            # Start ngrok process
            ngrok_path = os.path.join(os.path.dirname(__file__), '..', 'ngrok', 'ngrok')
            ngrok_yml_path = os.path.join(os.path.dirname(__file__), '..', 'ngrok', 'ngrok.yml')             
            
            # Set and send an `ngrok-skip-browser-warning` request header with any value
            # ngrok http 5000 --host-header="ngrok-skip-browser-warning:any-value"
            command = [ngrok_path, '--config', ngrok_yml_path, 'http', str(ngrok_port), '--host-header="ngrok-skip-browser-warning:any-value"'] 
            
            subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            time.sleep(5)  # Wait for ngrok to initialize

            # Check again the ngrok tunnels
            response = None
            try:
                response = requests.get(f'http://localhost:4040/api/tunnels')
            except requests.exceptions.RequestException as e:
                logger.error(f"ngrok is not running! An error occurred while checking ngrok tunnels: {e}")
                
            if not response or response.status_code != 200:
                logger.error(f"Failed to start ngrok: {response.text}")
                return None
        
        else:
            logger.debug(f"Ngrok is already running! {response.json()}")
            
        tunnels = response.json()['tunnels']
        for tunnel in tunnels:
            if tunnel['proto'] == 'https':
                return tunnel['public_url']
          
        logger.error(f"Failed to start ngrok: {response.text}")  
        return None
    
    except Exception as e:
        logger.error(f"An error occurred in {__file__} at line {e.__traceback__.tb_lineno}: {e}")
        return None

# --- Set up Stripe API keys ---

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
        logger.error(f"An error occurred: {e}")
        return None

if __name__ == "__main__":
    
    payment_link = create_checkout_session()
    
    if payment_link:
        logger.info(f"Checkout payment link: {payment_link}")
    else:
        logger.info("Failed to create checkout session.")
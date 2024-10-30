import json
import subprocess
import time
import stripe
import os
from dotenv import load_dotenv

# --------------------------------

# set and build logging
import logging

import requests
class CustomFormatter(logging.Formatter):
    """Custom formatter to add colors to log levels."""
    def format(self, record):
        log_colors = {
            logging.ERROR: "\033[91m",  # Red
            logging.WARNING: "\033[94m",  # Blue
            logging.INFO: "\033[92m",  # Green
            logging.DEBUG: "\033[93m",  # Yellow
        }
        reset_color = "\033[0m"
        log_fmt = log_colors.get(record.levelno, "") + "%(levelname)s: %(message)s" + reset_color
        formatter = logging.Formatter(log_fmt)
        return formatter.format(record)

# Set up logging
handler = logging.StreamHandler()
handler.setFormatter(CustomFormatter())
logging.basicConfig(level=logging.DEBUG, handlers=[handler])
logger = logging.getLogger(__name__)
logger.debug(f'Starting the {__file__}...')

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

# Define USE_NGROK and USE_SSL variables
USE_NGROK = os.getenv('USE_NGROK', 'False').lower() in ('true', '1', 't')
USE_SSL = os.getenv('USE_SSL', 'False').lower() in ('true', '1', 't')

# Define default values for HTTP and SSL parameters
DEF_HTTP_PORT = int(os.getenv('DEF_HTTP_PORT', 5000))
DEF_HTTP_HOST = os.getenv('DEF_HTTP_HOST', '0.0.0.0')
DEF_SSL_CERT = os.getenv('DEF_SSL_CERT', 'path/to/ssl_cert.pem')
DEF_SSL_KEY = os.getenv('DEF_SSL_KEY', 'path/to/ssl_key.pem')

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

# ------------- Stripe Webhook using flask ------------------

from flask import Flask, request, redirect, url_for
app = Flask(__name__)
app.logger = logger

@app.route('/payment/link', methods=['GET'])
def create_payment(
    stripe_api_key=STRIPE_API_KEY,
    payment_method_types=PAYMENT_METHOD_TYPES,
    currency=CURRENCY,
    product_name=PRODUCT_NAME,
    unit_amount=UNIT_AMOUNT,
    quantity=QUANTITY,
    mode=MODE,
    success_url=SUCCESS_URL,
    cancel_url=CANCEL_URL,
    use_ngrok=USE_NGROK,
    ngrok_port=5000,
    ): 

    try:  

        payment_link = create_checkout_session()
        
        if payment_link:
            logger.info(f"Checkout payment link: {payment_link}")
            return redirect(payment_link)
        else:
            
            logger.info("Failed to create checkout session.")
            # return redirect(url_for('create_payment'))
            return redirect(url_for(cancel_url))
    
    except Exception as e:
        logger.error(f"An error occurred in {__file__} at line {e.__traceback__.tb_lineno}: {e}")
        # return e
        return Exception(json.dumps(e))

def start_webhook(debug=False, port=DEF_HTTP_PORT, host=DEF_HTTP_HOST, load_dotenv=False, def_ssl_cert=DEF_SSL_CERT, def_ssl_key=DEF_SSL_KEY):
    """Runs the web application on a local development server.
    """
    
    try:        
        
        # Run the app with SSL context or not
        if USE_SSL:
            ssl_context = (def_ssl_cert, def_ssl_key)
            logger.debug(f"Running the app with SSL context: {ssl_context}")
            app.run(host=host, port=port, debug=debug, ssl_context=ssl_context, load_dotenv=load_dotenv)
            
        else:
            logger.debug(f"Running the app without SSL context: {DEF_HTTP_HOST}:{DEF_HTTP_PORT}")
            app.run(host=host, port=port, debug=debug, load_dotenv=load_dotenv)
        
        def_http_mode = 'https' if USE_SSL else 'http'
        logger.debug(f"Active Endpoint: {def_http_mode}://{DEF_HTTP_HOST}:{DEF_HTTP_PORT}")
        
    except Exception as e:
        logger.error(f"An error occurred in {__file__} at line {e.__traceback__.tb_lineno}: {e}")

# -------------- End of Stripe Webhook using flask ------------------

# --- If script is called directly then test the create checkout function ---

if __name__ == "__main__":
    
    # get the run mode from the environment variable, if is webhook or console mode
    run_mode = os.getenv('RUN_MODE', 'webhook')
    
    if run_mode == 'webhook':
        start_webhook()
    else: 
        payment_link = create_checkout_session()
        
        if payment_link:
            logger.info(f"Checkout payment link: {payment_link}")
        else:
            logger.info("Failed to create checkout session.")
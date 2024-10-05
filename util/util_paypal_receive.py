import os, dotenv, time, subprocess
from flask import Flask, request, redirect, url_for
import paypalrestsdk

# --------------------------------

# set and build logging
import logging

import requests
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

# test logger
logger.debug(f'Starting the {__file__}...')

# --------------------------------

# Load environment variables from the .env file
dotenv.load_dotenv()

CLIENT_ID = os.getenv("PAYPAL_CLIENT_ID")
CLIENT_SECRET = os.getenv("PAYPAL_CLIENT_SECRET")

USE_NGROK = bool(os.getenv("PAYPAL_USE_NGROK", True))   

USE_SSL = bool(os.getenv("PAYPAL_USE_SSL", None))
def_ssl_cert = os.getenv("PAYPAL_SSL_CERT", None)
def_ssl_key = os.getenv("PAYPAL_SSL_KEY", None)
if USE_SSL and def_ssl_cert and def_ssl_key and os.path.exists(def_ssl_cert) and os.path.exists(def_ssl_key):
    def_http_mode = os.getenv("PAYPAL_HTTP_MODE", "https")
else: 
    def_http_mode = os.getenv("PAYPAL_HTTP_MODE", "http")
    USE_SSL = False
    logger.warning("SSL certificate and key not found. Running without SSL context.")
    
def_http_host = os.getenv("PAYPAL_HTTP_HOST", "localhost")
def_http_port = os.getenv("PAYPAL_HTTP_PORT", "5000")

# Get webhook URL from the .env file
DEFAULT_RETURN_URL = os.environ.get('PAYPAL_DEFAULT_RETURN_URL', f"{def_http_mode}://{def_http_host}:{def_http_port}/payment/execute")
DEFAULT_CANCEL_URL = os.environ.get('PAYPAL_DEFAULT_CANCEL_URL', f"{def_http_mode}://{def_http_host}:{def_http_port}/payment/cancel")

execute_payment_callback = None
CANCEL_PAYMENT_CALLBACK = None

# --------------------------------

app = Flask(__name__)

# Configure PayPal SDK
paypalrestsdk.configure({
    "mode": "sandbox",  # sandbox or live
    "client_id": CLIENT_ID,
    "client_secret": CLIENT_SECRET
})

# --------------------------------

def start_ngrok():
    """Starts ngrok to expose the local server to the internet.

    Returns:
        _type_: ngrok URL if successful, None otherwise.
    """
    
    try:
        # Start ngrok process
        # ngrok\ngrok.exe http 80
        ngrok_path = os.path.join(os.path.dirname(__file__), '..', 'ngrok', 'ngrok.exe')
        ngrok = subprocess.Popen([ngrok_path, 'http', '5000'], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        time.sleep(5)  # Wait for ngrok to initialize

        # Get the ngrok tunnels
        response = requests.get('http://localhost:4040/api/tunnels')
        if response.status_code == 200:
            tunnels = response.json()['tunnels']
            for tunnel in tunnels:
                if tunnel['proto'] == 'https':
                    return tunnel['public_url']
                
        return None
    
    except Exception as e:
        logger.error(f"An error occurred while starting ngrok: {e}")
        return None

# -------------------------------- 

@app.route('/payment/link', methods=['GET'])
def create_payment(
    return_url=DEFAULT_RETURN_URL, 
    cancel_url=DEFAULT_CANCEL_URL, 
    total="5.00", 
    currency="BRL", 
    description="This is the payment transaction description.",
    client_id = os.getenv("PAYPAL_CLIENT_ID") ,
    client_secret = os.getenv("PAYPAL_CLIENT_SECRET"),
    use_ngrok=USE_NGROK
    ): 

    try:  

        paypalrestsdk.configure({
            "mode": "sandbox",  # sandbox or live
            "client_id": client_id,
            "client_secret": client_secret
        })
        
        if use_ngrok:
            ngrok_url = start_ngrok()
            if ngrok_url:
                logger.debug(f"Ngrok URL: {ngrok_url}")
                return_url = f"{ngrok_url}/payment/execute"
                cancel_url = f"{ngrok_url}/payment/cancel"            
                logger.debug(f"Using NGROK! Return URL: {return_url}")
            else:
                logger.error("Failed to get ngrok URL")          
        
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

def main(debug=False, port=def_http_port, host=def_http_host, load_dotenv=False):
    """Runs the application on a local development server.

    Do not use ``run()`` in a production setting. It is not intended to
    meet security and performance requirements for a production server.
    Instead, see :doc:`/deploying/index` for WSGI server recommendations.

    If the :attr:`debug` flag is set the server will automatically reload
    for code changes and show a debugger in case an exception happened.

    If you want to run the application in debug mode, but disable the
    code execution on the interactive debugger, you can pass
    ``use_evalex=False`` as parameter.  This will keep the debugger's
    traceback screen active, but disable code execution.

    It is not recommended to use this function for development with
    automatic reloading as this is badly supported.  Instead you should
    be using the :command:`flask` command line script's ``run`` support.

    .. admonition:: Keep in Mind

        Flask will suppress any server error with a generic error page
        unless it is in debug mode.  As such to enable just the
        interactive debugger without the code reloading, you have to
        invoke :meth:`run` with ``debug=True`` and ``use_reloader=False``.
        Setting ``use_debugger`` to ``True`` without being in debug mode
        won't catch any exceptions because there won't be any to
        catch.

    :param host: the hostname to listen on. Set this to ``'0.0.0.0'`` to
        have the server available externally as well. Defaults to
        ``'127.0.0.1'`` or the host in the ``SERVER_NAME`` config variable
        if present.
    :param port: the port of the webserver. Defaults to ``5000`` or the
        port defined in the ``SERVER_NAME`` config variable if present.
    :param debug: if given, enable or disable debug mode. See
        :attr:`debug`.
    :param load_dotenv: Load the nearest :file:`.env` and :file:`.flaskenv`
        files to set environment variables. Will also change the working
        directory to the directory containing the first file found.
    :param options: the options to be forwarded to the underlying Werkzeug
        server. See :func:`werkzeug.serving.run_simple` for more
        information.

    .. versionchanged:: 1.0
        If installed, python-dotenv will be used to load environment
        variables from :file:`.env` and :file:`.flaskenv` files.

        The :envvar:`FLASK_DEBUG` environment variable will override :attr:`debug`.

        Threaded mode is enabled by default.

    .. versionchanged:: 0.10
        The default port is now picked from the ``SERVER_NAME``
        variable.
    """
    
    try:        
        
        # Run the app with SSL context or not
        if USE_SSL:
            ssl_context = (def_ssl_cert, def_ssl_key)
            app.run(host=host, port=port, debug=debug, ssl_context=ssl_context, load_dotenv=load_dotenv)
            logger.debug(f"Running the app with SSL context: {ssl_context}")
            
        else:
            app.run(host=host, port=port, debug=debug, load_dotenv=load_dotenv)
            logger.debug(f"Running the app without SSL context: {def_http_host}:{def_http_port}")
        
        logger.debug(f"Active Endpoint: {def_http_mode}://{def_http_host}:{def_http_port}")
        
    except Exception as e:
        logger.error(f"An error occurred in {__file__} at line {e.__traceback__.tb_lineno}: {e}")

if __name__ == '__main__':       
    
    # Test the payment link creation with ngrok
    create_payment()
       
    # Run flask web server API 
    main()
    
#!/usr/bin/env python
# -*- coding: utf-8 -*-
# pylint: disable=W0613, C0116
# type: ignore[union-attr]

"""
Stripe module wrapper for a bot that can receive payment from user.
"""     

from typing import List

import sys, os, logging, socket

#-------------------------------------------

from util_env import *
from util_telegram import *
from util_decorators import *

from util_balance import *

from telegram.ext import Defaults, filters
from telegram.ext import PreCheckoutQueryHandler, ShippingQueryHandler 

#-------------------------------------------

bot_version = '1.0.0'
hostname = socket.getfqdn()

dotenv_settings = main_util_env()
TELEGRAM_BOT_TOKEN = dotenv_settings['DEFAULT_BOT_TOKEN']

DEFAULT_STRIPE_LIVE_TOKEN = dotenv_settings['STRIPE_LIVE_TOKEN'] 
DEFAULT_STRIPE_TEST_TOKEN = dotenv_settings['STRIPE_TEST_TOKEN']

current_bot_settings = {
    'token': '1234567890:ABCDEF',
    'stripe_currency': 'USD', 
    'stripe_title': 'Add credits to use the Bot', 
    'stripe_description': 'Click the "Pay" below to purchase credits:',
    'stripe_mode': 'test', 
    'stripe_price': 10, 
    'stripe_token': {
        'live': 'pk_live_1234567890', 
        'test': 'pk_test_1234567890'
        }
    }
   
bot_user_admin = dotenv_settings['ADMIN_ID_LIST']
if bot_user_admin:
    if ',' in bot_user_admin:
        bot_user_admin = bot_user_admin.split(',')[0]
    bot_user_admin = int(bot_user_admin)

DEFAULT_LANGUAGE = 'pt-br'

DEFAULT_STRIPE_CURRENCY = 'BRL' if 'stripe_currency' not in current_bot_settings else current_bot_settings['stripe_currency']
DEFAULT_STRIPE_TITLE = 'Adicionar créditos para usar o Bot' if 'stripe_title' not in current_bot_settings else current_bot_settings['stripe_title']
DEFAULT_STRIPE_DESCRIPTION = 'Clique no botão "Pagar" abaixo para adquirir créditos:' if 'stripe_description' not in current_bot_settings else current_bot_settings['stripe_description']
DEFAULT_STRIPE_MODE = 'test' if 'stripe_mode' not in current_bot_settings else current_bot_settings['stripe_mode']

DEFAULT_STRIPE_PRICE = 10 if 'stripe_price' not in current_bot_settings else current_bot_settings['stripe_price']

DEFAULT_STRIPE_PAYLOAD = 'Custom-Payload'
DEFAULT_STRIPE_START_PARAMETER = 'test-payment'

# ------------------------------------------

# Callback to be called when a successful payment is made
external_successful_payment_callback = None

async def start_callback(update: Update, context: CallbackContext) -> None:
    msg = "Use /shipping to get an invoice for shipping-payment, "
    msg += "or /noshipping for an invoice without shipping."
    # update.message.reply_text(msg)
    await update.effective_message.reply_text(msg)
    

def start_with_shipping_callback(update: Update, context: CallbackContext) -> None:
    
    global provider_token
    
    chat_id = update.message.chat_id
    title = "Payment Example"
    description = "Payment Example using python-telegram-bot"
    # select a payload just for you to recognize its the donation from your bot
    payload = "Custom-Payload"
    
    start_parameter = "test-payment"
    currency = "USD"
    # price in dollars
    price = 1
    # price * 100 so as to include 2 decimal points
    # check https://core.telegram.org/bots/payments#supported-currencies for more details
    # prices = [LabeledPrice("Test", price * 100)]
    prices = [LabeledPrice("Comprar créditos para consulta", price * 100)]

    # optionally pass need_name=True, need_phone_number=True,
    # need_email=True, need_shipping_address=True, is_flexible=True
    context.bot.send_invoice(
        chat_id,
        title,
        description,
        payload,
        provider_token,
        start_parameter,
        currency,
        prices,
        need_name=True,
        need_phone_number=True,
        need_email=True,
        need_shipping_address=True,
        is_flexible=True,
    )

def shipping_invoice_callback(update: Update, context: CallbackContext) -> None:
    
    global provider_token
    
    try:
        message = 'Erro na geração do pagamento!'
        
        try:
            # Use this to tell the user that something is happening on the bot's side:
            # update.effective_chat.send_chat_action(telegram.ChatAction.TYPING)
            # 11.2.2 typing + mktlist order by name + novos bots
            context.bot.send_chat_action(chat_id=update.effective_chat.id, action=telegram.ChatAction.TYPING) 
        except Exception as e:
            logging.error(str(e))                

        # Valor R$ 10,00 multiplicar valor por 100
        price_to_buy = 10 * 100

        # VALOR MINIMO ACEITO DE R$ 10,00
        # if (len(context.args) > 0) and (context.args[0].isnumeric()):
        #     price_to_buy = int(context.args[0])
        # else:
        #     message = 'Valor deve ser numérico e maior que 10, sem centavos, \nexemplo: /pagar 15\nVou considerar R$ 10!'
        #     update.effective_chat.send_message(text=message)
        #     price_to_buy = 10
        
        # Escolhe token conforme ambiente do Bot
        provider_token = provider_token_test if bot_config.environment_type == 'dev' else provider_token_live
            
        title, description, payload, provider_token, start_parameter, prices, currency = \
            create_invoice(
                title='Adicionar créditos Bot',
                description='Clique no botão "Pagar R$ 10,00" abaixo para adquirir créditos:',
                currency='BRL', price=price_to_buy, labeled_price='Créditos Bot', start_parameter='Creditos-Bot'
            )
        
        # telegram send_invoice BRL 'Currency_total_amount_invalid'
        # optionally pass need_name=True, need_phone_number=True,
        # need_email=True, need_shipping_address=True, is_flexible=True
        # prices = [LabeledPrice("Test", price_to_buy * 100),]
        
        # str' object has no attribute 'to_dict'
        # https://stackoverflow.com/questions/42045301/python-3-dictionary-items-str-object-has-no-attribute-items-error 
        # prices =  [LabeledPrice("Test", price_to_buy * 100)]          
        # prices =  [LabeledPrice("Test", price_to_buy)]          
        prices =  [LabeledPrice("Comprar créditos para consulta", price_to_buy)]          
             
        context.bot.send_invoice(
            chat_id= update.message.chat_id,
            title= title,
            description= description,
            payload= payload,
            provider_token= provider_token,
            currency= currency,
            prices= prices,
            start_parameter= start_parameter,
        )
        
    except Exception as e:
        logging.error(str(e))    

# @with_waiting_action
async def start_without_shipping_callback(update: Update, context: CallbackContext) -> None:
    
    try:
        # context.application.add_handler(MessageHandler(callback=successful_payment_callback, filters=filters.SUCCESSFUL_PAYMENT))
        
        user_language = update.effective_user.language_code
        
        chat_id = update.effective_message.chat_id
        title = DEFAULT_STRIPE_TITLE
        description = DEFAULT_STRIPE_DESCRIPTION
        currency = DEFAULT_STRIPE_CURRENCY
        
        # select a payload just for you to recognize its the donation from your bot
        payload = DEFAULT_STRIPE_PAYLOAD
        
        # In order to get a provider_token see https://core.telegram.org/bots/payments#getting-a-token
        provider_token = DEFAULT_STRIPE_LIVE_TOKEN if DEFAULT_STRIPE_MODE != 'test' else DEFAULT_STRIPE_TEST_TOKEN
        start_parameter = DEFAULT_STRIPE_START_PARAMETER
        
        price = DEFAULT_STRIPE_PRICE
        
        if user_language != DEFAULT_LANGUAGE:
            title = 'Add credits to use the Bot'
            description = 'Click the "Pay" below to purchase credits:'        
            currency = 'USD'
            price = 1
        
        if context.args and len(context.args) > 0 and context.args[0].isnumeric():
                price = int(context.args[0])
        elif context.args and len(context.args) > 0 and not context.args[0].isnumeric():
            # Handle the case when the parameter is not numeric
            # For example, you can set a default price or display an error message
            price = DEFAULT_STRIPE_PRICE
            update.effective_chat.send_message(text="Invalid price. Please provide a numeric value.")
            return
            
        # price * 100 so as to include 2 decimal points        
        price = price * 100
        
        prices: List[LabeledPrice] = [LabeledPrice('Comprar créditos para consulta', price)]

        await context.bot.send_invoice(
            chat_id=chat_id,
            title=title,
            description=description,
            payload=payload,
            provider_token=provider_token,
            start_parameter=start_parameter,
            currency=currency,
            prices=prices  # Ensure this is the only place 'prices' is mentioned
        )
    
    except Exception as e:
        # Currency_total_amount_invalid
        logging.error(str(e))
        try:
            await context.bot.send_message(chat_id=bot_user_admin, text=str(e), parse_mode=None)
        except Exception as ex:
            logging.error(str(ex))

def shipping_callback(update: Update, context: CallbackContext) -> None:
    query = update.shipping_query
    # check the payload, is this from your bot?
    if query.invoice_payload != 'Custom-Payload':
        # answer False pre_checkout_query
        # query.answer(ok=False, error_message="Something went wrong...")
        query.answer(ok=False, error_message="Não foi possível processar seu pagamento!")
        return

    options = list()
    # a single LabeledPrice
    options.append(ShippingOption('1', 'Shipping Option A', [LabeledPrice('A', 100)]))
    # an array of LabeledPrice objects
    price_list = [LabeledPrice('B1', 150), LabeledPrice('B2', 200)]
    options.append(ShippingOption('2', 'Shipping Option B', price_list))
    query.answer(ok=True, shipping_options=options)

# after (optional) shipping, it's the pre-checkout
async def precheckout_callback(update: Update, context: CallbackContext) -> None:
    query = update.pre_checkout_query
    # check the payload, is this from your bot?
    if query.invoice_payload != 'Custom-Payload':
        # answer False pre_checkout_query
        await query.answer(ok=False, error_message="Erro no processamento do pagamento!")
    else:
        await query.answer(ok=True)
  
# finally, after contacting the payment provider...
async def successful_payment_callback(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:      

    message = f"_Desculpe, estamos em manutenção. Tente novamente mais tarde!_"
    
    try:
        
        current_balance = get_balance_by_user_id(update.effective_chat.id)
        
        if update_balance(update.effective_chat.id, current_balance + 1000):        
            message = f"_Obrigado pelo seu pagamento!_{os.linesep}*Novo saldo atualizado: R$* `{(current_balance + 1000)/100}`"
        
        if external_successful_payment_callback:
            try:
                external_successful_payment_callback(update.effective_chat.id, 1000)
            except Exception as e:
                logging.error(str(e))    
        
    except Exception as e:
        logging.error(str(e)) 
    
    if context.bot.defaults.parse_mode != ParseMode.MARKDOWN:
        message = message.replace("*", "").replace("_", "").replace("`", "")
        
    await update.effective_message.reply_text(text=message)   

# ------------------------------------------

# command handler to show user current balance
async def cmd_get_user_balance(update: Update, context: CallbackContext) -> None:
        
        try:
            balance = get_balance_by_user_id(update.effective_chat.id)
            
            message = f"_Seu saldo atual é de R$_ `{balance/100:.2f}`"
            
            if balance in [None, '']:
                message = "_Desculpe, estamos em manutenção tente novamente mais tarde!_"
            
            await update.effective_message.reply_text(text=message)
            
        except Exception as e:
            logging.error(str(e))
            await update.message.reply_text("Erro ao recuperar seu saldo!")
  
# Toggles between test and live stripe modes
async def cmd_stripe_mode(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Toggles between test and live stripe modes"""
    
    global DEFAULT_STRIPE_MODE     

    message = f"_Desculpe, estamos em manutenção. Tente novamente mais tarde!_"
    
    try:
        DEFAULT_STRIPE_MODE = 'test' if DEFAULT_STRIPE_MODE == 'live' else 'live'
        
        message = f"*Stripe mode changed to:* `{DEFAULT_STRIPE_MODE}`"
        
        if 'stripe_mode' in current_bot_settings:
            current_bot_settings['stripe_mode'] = DEFAULT_STRIPE_MODE
            save_bot_tokens()
        
    except Exception as e:
        logging.error(str(e)) 
    
    if context.bot.defaults.parse_mode != ParseMode.MARKDOWN:
        message = message.replace("*", "").replace("_", "").replace("`", "")
        
    await update.effective_message.reply_text(text=message)   

# ------------------------------------------

def create_invoice(title = "Payment Example",  
                   description = "Payment Example using python-telegram-bot",
                   # select a payload just for you to recognize its the donation from your bot
                   payload="Custom-Payload",
                   start_parameter="test-payment",
                   currency="USD",
                   price=1,
                   labeled_price='Comprar créditos para consulta'
                   ):
    
    global provider_token
    
    try:
        # select a payload just for you to recognize its the donation from your bot
        # payload = "Custom-Payload"
        
        # price in dollars
        # price * 100 so as to include 2 decimal points
        # check https://core.telegram.org/bots/payments#supported-currencies for more details
        # prices = [LabeledPrice("Test", price * 100)]
        prices = [LabeledPrice(labeled_price, price * 100)]
        
        return title, description, payload, provider_token, start_parameter, prices, currency
                    
    except Exception as e:
        logging.error(str(e))

# ------------------------------------------

async def post_init(application: Application) -> None:   

    try:
        # get the name of current bot
        bot_name = application.bot.username
        
        start_message = f"""*{application.bot.username} Started!*
_Versao:_   `{bot_version}`
_Host:_     `{hostname}`
_Path:_
`{main_script_path}`"""    

        logger.info(f"{start_message}")  

        current_commands = await application.bot.get_my_commands(scope=BotCommandScopeAllPrivateChats())
        logger.info(f"Get Current commands: {current_commands}")    
        current_commands = await application.bot.get_my_commands(scope=BotCommandScopeDefault())
        logger.info(f"Get Current commands: {current_commands}") 
           
        await application.bot.send_message(chat_id=bot_user_admin, text=f"{start_message}", parse_mode=ParseMode.MARKDOWN)
        
        # await set_commands(commands=None, callback_context=None, application=application)
         
    except Exception as e:
        logger.error(f"Error: {e}")

async def post_shutdown(application: Application) -> None:
    
    try:
        stop_message = f"_STOPPING bot_ {os.linesep}`{hostname}`{os.linesep}`{__file__}` {bot_version}..."
        logger.info(stop_message)
        await application.bot.send_message(chat_id=bot_user_admin, text=f"{stop_message}", parse_mode=ParseMode.MARKDOWN)
    except Exception as e:
        logger.error(f"Error: {e}")
            
    sys.exit(0)

# ------------------------------------------

def util_stripe_main(application: Application = None, run_polling=False) -> None:
    
    try:
        if application is None:
            bot_defaults_build = Defaults(parse_mode=ParseMode.MARKDOWN) # , tzinfo=pytz.timezone('Europe/Berlin'))        
            application = Application.builder().defaults(defaults=bot_defaults_build).token(TELEGRAM_BOT_TOKEN).post_init(post_init).post_shutdown(post_shutdown).build()

        # simple start handler    
        application.add_handler(CommandHandler("start", start_callback))

        # Add command handler to start the payment invoice
        # dispatcher.add_handler(CommandHandler("shipping", start_with_shipping_callback))
        application.add_handler(CommandHandler("shipping", shipping_invoice_callback, filters=filters.User(bot_user_admin)))
        application.add_handler(CommandHandler("pay", start_without_shipping_callback, filters=filters.User(bot_user_admin)))

        # Optional handler if your product requires shipping
        application.add_handler(ShippingQueryHandler(shipping_callback))

        # Pre-checkout handler to final check
        application.add_handler(PreCheckoutQueryHandler(precheckout_callback))

        # Success! Notify your user!
        # dispatcher.add_handler(MessageHandler(Filters.successful_payment, successful_payment_callback))
        application.add_handler(MessageHandler(callback=successful_payment_callback, filters=filters.SUCCESSFUL_PAYMENT), group=-1)
        
        # # Optional handler if your product requires shipping
        # dispatcher.add_handler(ShippingQueryHandler(shipping_callback))

        application.add_handler(CommandHandler("balance", cmd_get_user_balance), group=-1)
        
        application.add_handler(CommandHandler("stripemode", cmd_stripe_mode, filters=filters.User(bot_user_admin)), group=-1)

        if run_polling:
            # Start the Bot
            application.run_polling(allowed_updates=Update.ALL_TYPES) 
        else:
            return application

    except Exception as e:
        logging.error(str(e))
        input("Press Enter to exit...")

if __name__ == '__main__':
        
    application = util_stripe_main()
    
    application.run_polling(allowed_updates=Update.ALL_TYPES) 

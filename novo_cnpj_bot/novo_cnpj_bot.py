import os
import re
import dotenv
from telegram import Update
from telegram.constants import ParseMode
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
from functools import wraps
from telegram.ext import CallbackContext
from telegram.constants import ChatAction

import logging
from logging.handlers import TimedRotatingFileHandler

# Create a custom logger
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

# Create handlers
console_handler = logging.StreamHandler()
file_handler = TimedRotatingFileHandler('bot.log', when='D', interval=3, backupCount=10)

# Set level for handlers
console_handler.setLevel(logging.DEBUG)
file_handler.setLevel(logging.DEBUG)

# Create formatters and add them to handlers
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
console_handler.setFormatter(formatter)
file_handler.setFormatter(formatter)

# Add handlers to the logger
logger.addHandler(console_handler)
logger.addHandler(file_handler)

# Example usage
logger.info("Logging is configured.")

# Função para validar o CNPJ
def validar_cnpj(cnpj: str) -> bool:
    logger.debug(f"Validating CNPJ: {cnpj}")
    cnpj = re.sub(r'\D', '', cnpj)
    if len(cnpj) != 14:
        logger.debug("Invalid CNPJ length")
        return False

    def calcular_digito(cnpj, peso):
        soma = sum(int(cnpj[i]) * peso[i] for i in range(len(peso)))
        resto = soma % 11
        return 0 if resto < 2 else 11 - resto

    peso1 = [5, 4, 3, 2, 9, 8, 7, 6, 5, 4, 3, 2]
    peso2 = [6] + peso1

    digito1 = calcular_digito(cnpj[:12], peso1)
    digito2 = calcular_digito(cnpj[:12] + str(digito1), peso2)

    is_valid = cnpj[-2:] == f"{digito1}{digito2}"
    logger.debug(f"CNPJ validation result: {is_valid}")
    return is_valid

def with_typing_action(handler):
    @wraps(handler)
    async def wrapper(update: Update, context: CallbackContext, *args, **kwargs):
        try:
            logger.debug("Sending typing action")
            await context.bot.send_chat_action(chat_id=update.effective_chat.id, action=ChatAction.TYPING)
            return await handler(update, context, *args, **kwargs)
        except Exception as e:
            logger.error(f"Error: {e}")
            return await handler(update, context, *args, **kwargs)
    return wrapper

def with_log_admin(handler):
    @wraps(handler)
    async def wrapper(update: Update, context: CallbackContext, *args, **kwargs):
        try:
            admin_user_id = dotenv.get_key(dotenv.find_dotenv(), "ADMIN_USER_ID")
            user_id = update.effective_user.id
            user_name = update.effective_user.full_name
            command = update.message.text

            log_message = f"Command: {command}\nUser ID: {user_id}\nUser Name: {user_name}"
            logger.debug(f"Sending log message to admin: {log_message}")
            try:
                await context.bot.send_message(chat_id=admin_user_id, text=log_message, parse_mode=ParseMode.MARKDOWN)
            except Exception as e:
                logger.error(f"Failed to send log message: {e}")

            return await handler(update, context, *args, **kwargs)
        except Exception as e:
            logger.error(f"Error: {e}")
            return await handler(update, context, *args, **kwargs)
    return wrapper

@with_typing_action
@with_log_admin
async def start(update: Update, context: CallbackContext) -> None:
    logger.debug("Handling /start command")
    await update.message.reply_text('Olá! Envie um CNPJ para validação.')

@with_typing_action
@with_log_admin
async def validar(update: Update, context: CallbackContext) -> None:
    logger.debug("Handling CNPJ validation")
    cnpj = update.message.text
    if validar_cnpj(cnpj):
        logger.debug("CNPJ is valid")
        await update.message.reply_text('CNPJ válido.')
    else:
        logger.debug("CNPJ is invalid")
        await update.message.reply_text('CNPJ inválido.')

def main() -> None:
    logger.debug("Starting bot")
    dotenv.load_dotenv()
    
    token = dotenv.get_key(dotenv.find_dotenv(), "TOKEN")
    
    application = Application.builder().token(token).build()

    application.add_handler(CommandHandler("start", start))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, validar))

    logger.debug("Running bot")
    application.run_polling()

if __name__ == "__main__":
    main()
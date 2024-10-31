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

# Função para validar o CNPJ
def validar_cnpj(cnpj: str) -> bool:
    cnpj = re.sub(r'\D', '', cnpj)
    if len(cnpj) != 14:
        return False

    def calcular_digito(cnpj, peso):
        soma = sum(int(cnpj[i]) * peso[i] for i in range(len(peso)))
        resto = soma % 11
        return 0 if resto < 2 else 11 - resto

    peso1 = [5, 4, 3, 2, 9, 8, 7, 6, 5, 4, 3, 2]
    peso2 = [6] + peso1

    digito1 = calcular_digito(cnpj[:12], peso1)
    digito2 = calcular_digito(cnpj[:12] + str(digito1), peso2)

    return cnpj[-2:] == f"{digito1}{digito2}"

def with_typing_action(handler):
    @wraps(handler)
    async def wrapper(update: Update, context: CallbackContext, *args, **kwargs):
        try:
            await context.bot.send_chat_action(chat_id=update.effective_chat.id, action=ChatAction.TYPING)
            return await handler(update, context, *args, **kwargs)
        except Exception as e:
            logging.error(f"Error: {e}")
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

            try:
                log_message = f"Command: {command}\nUser ID: {user_id}\nUser Name: {user_name}"
                await context.bot.send_message(chat_id=admin_user_id, text=log_message, parse_mode=ParseMode.MARKDOWN)
            except Exception as e:
                logging.error(f"Failed to send log message: {e}")

            return await handler(update, context, *args, **kwargs)
        except Exception as e:
            logging.error(f"Error: {e}")
            return await handler(update, context, *args, **kwargs)
    return wrapper

@with_typing_action
@with_log_admin
async def start(update: Update, context: CallbackContext) -> None:
    await update.message.reply_text('Olá! Envie um CNPJ para validação.')

@with_typing_action
@with_log_admin
async def validar(update: Update, context: CallbackContext) -> None:
    cnpj = update.message.text
    if validar_cnpj(cnpj):
        await update.message.reply_text('CNPJ válido.')
    else:
        await update.message.reply_text('CNPJ inválido.')

def main() -> None:
    
    dotenv.load_dotenv()
    
    # Crie uma variável de ambiente com nome TOKEN no prompt de comando
    # ou substitua 'YOUR_TOKEN_HERE' pelo token do seu bot, que você recebeu do BotFather no arquivo sample.env
    # depois renomeie o arquivo sample.env para .env
    # em seguida execute o script com o comando: python novo_cnpj_bot.py
    token = dotenv.get_key(dotenv.find_dotenv(), "TOKEN")
    
    application = Application.builder().token(token).build()

    application.add_handler(CommandHandler("start", start))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, validar))

    application.run_polling()

if __name__ == '__main__':
    main()
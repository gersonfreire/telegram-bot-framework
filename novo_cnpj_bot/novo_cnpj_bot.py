import os
import re
import dotenv
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes

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

# Função para iniciar a conversa
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text('Olá! Envie um CNPJ para validação.')

# Função para validar o CNPJ enviado pelo usuário
async def validar(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
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
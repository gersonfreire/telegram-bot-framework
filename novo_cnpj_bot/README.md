**Chatbot que valida CNPJ pelo telegram**

Plano em Pseudocódigo

1. **Configurar o Bot do Telegram:**

   - Obter o token do Bot do Telegram.
   - Configurar a biblioteca `python-telegram-bot`.
2. **Função para validar o CNPJ:**

   - Implementar a função `validar_cnpj` que verifica o dígito verificador de um CNPJ.
3. **Funções de Manipulação de Mensagens:**

   - Implementar a função `start` para iniciar a conversa.
   - Implementar a função `validar` para validar o CNPJ enviado pelo usuário.
4. **Configurar o Dispatcher e o Polling:**

   - Configurar os handlers para as mensagens.
   - Iniciar o polling para receber mensagens.

### Código

```python
import re
from telegram import Update
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackContext

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
def start(update: Update, context: CallbackContext) -> None:
    update.message.reply_text('Olá! Envie um CNPJ para validação.')

# Função para validar o CNPJ enviado pelo usuário
def validar(update: Update, context: CallbackContext) -> None:
    cnpj = update.message.text
    if validar_cnpj(cnpj):
        update.message.reply_text('CNPJ válido.')
    else:
        update.message.reply_text('CNPJ inválido.')

def main() -> None

:


    # Substitua 'YOUR_TOKEN_HERE' pelo token do seu bot
    updater = Updater("YOUR_TOKEN_HERE")

    dispatcher = updater.dispatcher

    dispatcher.add_handler(CommandHandler("start", start))
    dispatcher.add_handler(MessageHandler(Filters.text & ~Filters.command, validar))

    updater.start_polling()
    updater.idle()

if __name__ == '__main__':
    main()
```

### Instruções

1. **Instalar Dependências:**

   ```sh
   pip install python-telegram-bot
   ```
2. **Substituir o Token:**

* Obtenha um token do telegram no BotFather ([Entrar no BotFather](https://t.me/botfather))
* Substitua 'YOUR_TOKEN_HERE' pelo token do seu bot, que você recebeu do BotFather no arquivo sample.env
* Renomeie o arquivo sample.env para .env

3. **Executar o Script:**

   ```sh
   python novo_cnpj_bot.py
   ```

### Bot "demo" já rodando no Telegram: [Bot Demo de validação CNPJ](https://t.me/OpenGovBot)

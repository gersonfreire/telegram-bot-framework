#!/usr/bin/env python3.7

# -*- coding: utf-8 -*-
# pylint: disable=W0613, C0116
# type: ignore[union-attr]

"""
Módulo de funções de configuração.
"""
#-------------------------------------------

from util_log import *

from functools import wraps

DEFAULT_PRODUCT_PRICE = -100

# -------------------------------------------

default_initial_balance = 0

# ------------------------------------------

def update_balance(user_id, balance):
    """
    Atualiza o saldo do usuário no dicionário JSON.
    """
    try:
        if str(user_id) in user_profiles_dict and 'balance' in user_profiles_dict[str(user_id)]:
            user_profiles_dict[str(user_id)]['balance'] = balance

        else:
            user_profiles_dict[str(user_id)] = {'balance': balance}

        save_json_settings(user_profiles_dict, all_user_data_file)
        return True

    except Exception as e:
        logging.info("util_balance: " + str(e))
        return False

def get_balance_by_user_id(user_id):
    """
    Obtem saldo de usuários em formato JSON.
    """
    user_balance = 0

    try:
        if str(user_id) in user_profiles_dict and 'balance' in user_profiles_dict[str(user_id)]:
            user_balance = user_profiles_dict[str(user_id)]['balance']
        else:
            user_balance = default_initial_balance
            user_profiles_dict[str(user_id)] = {'balance': user_balance}

            save_json_settings(user_profiles_dict, all_user_data_file)

    except Exception as e:
        logging.info("util_config: " + str(e))

    return user_balance

#-------------------------------------------

def get_product_price_by_name(product_name):
    """
    Obtem o preço de um produto.
    """
    try:

        product_prices = {product_name: DEFAULT_PRODUCT_PRICE}

        if 'product_prices' in current_bot_settings and product_name in current_bot_settings['product_prices']:
            product_prices = current_bot_settings['product_prices']

        bot_tokens_dict[bot_name]['product_prices'] = product_prices
        save_bot_tokens()

        price = product_prices[product_name]

        return price

    except Exception as e:
        logging.info("util_balance: " + str(e))
        return None

def update_price_by_name(product_name, price):
    """
    Atualiza o preço de um produto.
    """
    try:

        product_prices = {product_name: DEFAULT_PRODUCT_PRICE}

        if 'product_prices' in current_bot_settings:
            product_prices = current_bot_settings['product_prices']

        product_prices[product_name] = price
        current_bot_settings['product_prices'] = product_prices
        # bot_tokens_dict[bot_name] = current_bot_settings

        save_bot_tokens()

        return True

    except Exception as e:
        logging.info("util_balance: " + str(e))

# ------------------------------------------

def with_check_balance(handler):
    @wraps(handler)
    async def wrapper(update, context):

        try:
            if 'IS_CHECK_BALANCE_ACTIVE' in current_bot_settings:
                IS_CHECK_BALANCE_ACTIVE = current_bot_settings['IS_CHECK_BALANCE_ACTIVE']
            else:
                IS_CHECK_BALANCE_ACTIVE = True

            if not IS_CHECK_BALANCE_ACTIVE:
                return await handler(update, context)

            current_balance = get_balance_by_user_id(update.effective_user.id)

            handler_name = handler.__name__
            product_price = get_product_price_by_name(handler_name)

            if current_balance < product_price:
                message = f"""_Saldo insuficiente:_ `R$ {current_balance/100:.2f}`
_Preço desta consulta:_ `R$ {product_price/100:.2f}`
_Recarregue seu saldo!_"""
                await context.bot.send_message(chat_id=update.effective_chat.id, text=message)
                return

            else:
                await handler(update, context)

                command_parts = update.effective_message.text.split(' ')
                if len(command_parts) > 1 and command_parts[0] == '/cnpj':

                    if update_balance(update.effective_user.id, current_balance - product_price):
                        message = f"""_Saldo anterior:_ *R$ {(current_balance)/100:.2f}*
_Novo saldo após consulta:_ *R$ {(current_balance - product_price)/100:.2f}*
_Preço desta consulta:_ `R$ {product_price/100:.2f}`"""

                    else:
                        message = f"*Erro ao atualizar saldo do usuário!*{os.linesep}_Tente novamente mais tarde._"

                    await context.bot.send_message(chat_id=update.effective_chat.id, text=message)

        except Exception as e:

          logger.error(f"Error: {e}")
          await handler(update, context)

    return wrapper

# ---------- Testes unitarios -----------

def main():

    try:
        product_price = get_product_price_by_name('get_empresa_by_cnpj_basico')

        update_price_by_name('get_empresa_by_cnpj_basico', product_price + 100)

        quit()

        balance = get_balance_by_user_id(38429120)

        update_balance(338429120, balance + 100)

    except Exception as e:
        logging.error(str(e))

if __name__ == '__main__':
    main()


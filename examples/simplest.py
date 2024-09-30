
#!/usr/bin/env python
# -*- coding: utf-8 -*-
# ------------------------------------------

"""
This is the simplest example of a bot using this Telegram Bot Framwork.

This bot will just reply to any message with the same message.

Pre-requisites:
    - Have a bot token from BotFather
    - Have a Telegram account
    - Clone the tlgfwk repository
    - Install the tlgfwk package:
        cd path/to/tlgfwk_source_code
        pip install .
    - Create a .env file from .env_sample and fill it with your bot token
"""

import __init__

from tlgfwk import *

bot = TlgBotFwk()

if __name__ == '__main__':
    bot.run()
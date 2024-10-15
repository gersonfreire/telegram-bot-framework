
#!/usr/bin/env python
# -*- coding: utf-8 -*-
# ------------------------------------------

"""
This is a sample bot using this Telegram Bot Framework that 
overloads the initialize_handlers method to add a help command handler.
"""

__version__ = '0.1.0'

import os
import time

import __init__
from tlgfwk import *


def ping_host(ip_address):
    response = os.system(f"ping -c 1 {ip_address}")
    if response == 0:
        print(f"{ip_address} is up!")
    else:
        print(f"{ip_address} is down!")

class HostMonitorBot(TlgBotFwk):
    def __init__(self, ip_address):
        super().__init__()
        self.ip_address = ip_address

    def job(self):
        self.ping_host(self.ip_address)

    def ping_host(self, ip_address):
        response = os.system(f"ping -c 1 {ip_address}")
        if response == 0:
            print(f"{ip_address} is up!")
        else:
            print(f"{ip_address} is down!")

# Create an instance of the bot
bot = HostMonitorBot("8.8.8.8")

def function(callback_context: CallbackContext):
    # self.ping_host(self.ip_address)
    print("Hello")

# Schedule the job every 10 minutes using the bot's scheduling method
# bot.job_queue.every(10).minutes.do(bot.job)
bot.application.job_queue.run_repeating(function, interval=20, first=0, name=None) # , data={'args': (self,)})

# Start the bot's main loop
bot.run()

# Schedule the job every 10 minutes
# schedule.every(10).minutes.do(job)

# while True:
#     schedule.run_pending()
#     time.sleep(1)
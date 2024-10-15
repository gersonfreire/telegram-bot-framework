
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
        
        self.application.job_queue.run_repeating(self.job, interval=20, first=0, name=None) 
        
        # Avoid the error handler to be called when the job raises an exception
        self.application.remove_error_handler(self.error_handler)

    def job(self, callback_context: CallbackContext):
        try:
            self.send_message_by_api(self.bot_owner, f"Pinging {self.ip_address}...")
            self.ping_host(self.ip_address)
        except Exception as e:
            print(f"An error occurred: {e}")

    def ping_host(self, ip_address):
        response = os.system(f"ping -c 1 {ip_address}")
        if response == 0:
            self.send_message_by_api(self.bot_owner, f"{ip_address} is up!")
        else:
            self.send_message_by_api(self.bot_owner, f"{ip_address} is down!")

# Create an instance of the bot
bot = HostMonitorBot("8.8.8.8")
    
# Start the bot's main loop
bot.run()

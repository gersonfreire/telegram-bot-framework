
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

class HostMonitorBot(TlgBotFwk):
    
    def __init__(self, ip_address):
        super().__init__(disable_error_handler=True)
        self.ip_address = ip_address
        
        # Run the job every 20 seconds
        self.application.job_queue.run_repeating(self.job, interval=20, first=0, name=None) 

    def job(self, callback_context: CallbackContext):
        try:
            self.send_message_by_api(self.bot_owner, f"Pinging {self.ip_address}...")
            self.ping_host(self.ip_address)
        except Exception as e:
            self.send_message_by_api(self.bot_owner, f"An error occurred: {e}")

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


#!/usr/bin/env python
# -*- coding: utf-8 -*-
# ------------------------------------------

"""
This is a sample bot using this Telegram Bot Framework that 
overloads the initialize_handlers method to add a help command handler.
"""

__version__ = '0.1.0'

import os
import platform
import time

import __init__
from tlgfwk import *

class HostMonitorBot(TlgBotFwk):
    
    def __init__(self, ip_address, show_success = False,*args, **kwargs):
        
        super().__init__()
        
        self.ip_address = ip_address
        self.show_success = show_success
        
        # Run the job every 20 seconds
        self.application.job_queue.run_repeating(self.job, interval=20, first=0, name=None) 

    async def job(self, callback_context: CallbackContext):
        try:
            self.send_message_by_api(self.bot_owner, f"Pinging {self.ip_address}...") if self.show_success else None
            self.ping_host(self.ip_address)
        except Exception as e:
            self.send_message_by_api(self.bot_owner, f"An error occurred: {e}")

    def ping_host(self, ip_address):
        
        param = "-n 1" if platform.system().lower() == "windows" else "-c 1"
        response = os.system(f"ping {param} {ip_address}") # Returns 0 if the host is up, 1 if the host is down
        
        if response == 0:
            self.send_message_by_api(self.bot_owner, f"{ip_address} is up!") if self.show_success else None
        else:
            self.send_message_by_api(self.bot_owner, f"{ip_address} is down!")

# Create an instance of the bot
bot = HostMonitorBot("8.8.8.8", show_success=True)
    
# Start the bot's main loop
bot.run()

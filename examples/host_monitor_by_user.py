#!/usr/bin/env python
# -*- coding: utf-8 -*-
# ------------------------------------------

"""
Host Monitor Bot
"""

__version__ = '0.1.0'

import os
from telegram import Update
from telegram.ext import CommandHandler, CallbackContext

#!/usr/bin/env python
# -*- coding: utf-8 -*-
# ------------------------------------------

"""
This is a sample bot using the Telegram Bot Framework that 
overrides the initialize_handlers method to add a help command handler.
This version is inspired on and more elaborated than host_monitor because controls each host by user.
"""

__version__ = '0.1.0'

import os
import platform
import time

import __init__
from tlgfwk import *

class HostMonitorBot(TlgBotFwk):
    
    def __init__(self, ip_address, show_success=False, *args, **kwargs):
        super().__init__()
        
        self.ip_address = ip_address
        self.show_success = show_success
        self.jobs = {}
        
        # Run the job every 20 seconds
        self.application.job_queue.run_repeating(self.job, interval=20, first=0, name=None) 

    async def job(self, callback_context: CallbackContext):
        try:
            self.send_message_by_api(self.bot_owner, f"Pinging {self.ip_address}...") if self.show_success else None
            self.ping_host(self.ip_address)
        except Exception as e:
            self.send_message_by_api(self.bot_owner, f"An error occurred: {e}")


    def ping_host(self, ip_address):
        # Ping logic here
        pass

    def add_job(self, update: Update, context: CallbackContext):
        if len(context.args) != 2:
            update.message.reply_text("Usage: /addjob <ip_address> <interval_in_seconds>")
            return
        
        ip_address = context.args[0]
        interval = int(context.args[1])
        
        job_name = f"ping_{ip_address}"
        
        if job_name in self.jobs:
            update.message.reply_text(f"Job for {ip_address} already exists.")
            return
        
        job = self.application.job_queue.run_repeating(
            self.job, interval=interval, first=0, name=job_name, context=ip_address
        )
        self.jobs[job_name] = job
        update.message.reply_text(f"Job added for {ip_address} with interval {interval} seconds.")

    def delete_job(self, update: Update, context: CallbackContext):
        if len(context.args) != 1:
            update.message.reply_text("Usage: /deletejob <ip_address>")
            return
        
        ip_address = context.args[0]
        job_name = f"ping_{ip_address}"
        
        if job_name not in self.jobs:
            update.message.reply_text(f"No job found for {ip_address}.")
            return
        
        job = self.jobs.pop(job_name)
        job.schedule_removal()
        update.message.reply_text(f"Job for {ip_address} deleted.")

    def run(self):
        self.application.add_handler(CommandHandler("addjob", self.add_job))
        self.application.add_handler(CommandHandler("deletejob", self.delete_job))
        super().run()

# Create an instance of the bot
bot = HostMonitorBot("8.8.8.8", show_success=True)
    
# Start the bot's main loop
bot.run()

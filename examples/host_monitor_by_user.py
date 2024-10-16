#!/usr/bin/env python
# -*- coding: utf-8 -*-
# ------------------------------------------

"""
This is a sample bot using the Telegram Bot Framework that 
overrides the initialize_handlers method to add a help command handler.
This version is inspired on and more elaborated than host_monitor because controls each host by user.
"""

__version__ = '0.1.0'

import os, platform, time, asyncio
from telegram import Update
from telegram.ext import CommandHandler, CallbackContext

__version__ = '0.1.0'

import __init__
from tlgfwk import *

class HostMonitorBot(TlgBotFwk):
    
    async def load_all_user_data(self):
        try:
      
            # restore all persisted jobs already added by the user
            user_data = await self.application.persistence.get_user_data() if self.application.persistence else {}     
            
            for user_id, job_params in user_data.items():
                try:
                    if job_params.startswith('ping_'):
                        ip_address = user_id.replace('ping_', '')
                        self.jobs[user_id] = self.application.job_queue.run_repeating(
                            self.job, interval=job_params.interval, first=0, name=user_id, data=ip_address
                        )
                except Exception as e:
                    logger.error(f"Failed to restore job {user_id}: {e}")
                    self.send_message_by_api(self.bot_owner, f"Failed to restore job {user_id}: {e}", parse_mode=None) 
            
        except Exception as e:
            logger.error(f"Failed to restore jobs: {e}")
            self.send_message_by_api(self.bot_owner, f"Failed to restore jobs: {e}", parse_mode=None)           
    
    def __init__(self, ip_address, show_success=False, *args, **kwargs):
        
        super().__init__(disable_command_not_implemented=True, disable_error_handler=True, *args, **kwargs)
        
        self.ip_address = ip_address
        self.show_success = show_success
        self.jobs = {}
        
        asyncio.run(self.load_all_user_data())

    async def job(self, callback_context: CallbackContext):
        try:
            self.send_message_by_api(self.bot_owner, f"Pinging {self.ip_address}...") if self.show_success else None
            self.ping_host(self.ip_address)
        except Exception as e:
            self.send_message_by_api(self.bot_owner, f"An error occurred: {e}", parse_mode=None) 


    def ping_host(self, ip_address):
        # Ping logic here
        pass

    async def add_job(self, update: Update, context: CallbackContext):
        try:
            if len(context.args) != 2:
                await update.message.reply_text("Usage: /addjob <ip_address> <interval_in_seconds>", parse_mode=None)
                return
            
            ip_address = context.args[0]
            interval = int(context.args[1])
            
            job_name = f"ping_{ip_address}"
            
            # TODO: set bot persistence on build bot method
            # check if job name already exists on the jobs list stored in user data persistence
            if job_name in context.user_data:
                await update.message.reply_text(f"Job for {ip_address} already exists.", parse_mode=None)
                return
            
            if job_name in self.jobs:
                await update.message.reply_text(f"Job for {ip_address} already exists.", parse_mode=None)
                return
            
            job = self.application.job_queue.run_repeating(
            self.job, interval=interval, first=0, name=job_name, data=ip_address
            ) # , data={'args': (self,)})
            self.jobs[job_name] = job
            
            # replace job object by ping parameters in user data
            context.user_data[job_name] = {'interval': interval, 'ip_address': ip_address}
            
            # force persistence update of the user data
            await self.application.persistence.update_user_data(update.effective_user.id, context.user_data) if self.application.persistence else None              
            
            # Ensure persistence is flushed to save the new job
            await self.application.persistence.flush() if self.application.persistence else None
            
            await update.message.reply_text(f"Job added for {ip_address} with interval {interval} seconds.", parse_mode=None)
            
        except Exception as e:
            await update.message.reply_text(f"An error occurred: {e}", parse_mode=None)

    async def delete_job(self, update: Update, context: CallbackContext):
        if len(context.args) != 1:
            await update.message.reply_text("Usage: /deletejob <ip_address>", parse_mode=None)
            return
        
        ip_address = context.args[0]
        job_name = f"ping_{ip_address}"
        
        if job_name not in self.jobs:
            update.message.reply_text(f"No job found for {ip_address}.", parse_mode=None)
            return
        
        job = self.jobs.pop(job_name)
        job.schedule_removal()
        update.message.reply_text(f"Job for {ip_address} deleted.", parse_mode=None)

    def run(self):
        self.application.add_handler(CommandHandler("addjob", self.add_job), group=-1)
        self.application.add_handler(CommandHandler("deletejob", self.delete_job), group=-1)
        super().run()

# Create an instance of the bot
bot = HostMonitorBot("8.8.8.8", show_success=True) 

# Start the bot's main loop
bot.run()

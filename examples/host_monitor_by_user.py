#!/usr/bin/env python
# -*- coding: utf-8 -*-
# ------------------------------------------

"""
This is a sample bot using the Telegram Bot Framework that 
overrides the initialize_handlers method to add a help command handler.
This version is inspired on and more elaborated than host_monitor because controls each host by user.
"""

__version__ = '0.2.1'

import os, platform, time, asyncio
from telegram import Update
from telegram.ext import CommandHandler, CallbackContext

import __init__
from tlgfwk import *

class HostMonitorBot(TlgBotFwk):
    
    async def get_user_data(self, user_id: int, user_item_name: str, default_value=None):
    
        try:
            # Get user data from the context
            all_user_data = await self.application.persistence.get_user_data() if self.application.persistence else {}
            
            user_data = all_user_data[user_id] if user_id in all_user_data else {user_id : {}}
            
            if user_item_name not in user_data:
                user_data[user_item_name] = default_value
                await self.application.persistence.update_user_data(user_id, user_data) if self.application.persistence else None
                            
            # Get the current value of the show_success flag
            user_data_item = user_data.get(user_item_name, default_value)
            
            return user_data_item
                
        except Exception as e:
            logger.error(f"An error occurred while getting user data: {e}")
            return None
    
    async def load_all_user_data(self):
        try:
            logger.info("Restoring jobs...")
            await self.application.bot.send_message(self.bot_owner, "_Restoring jobs..._") if self.bot_owner else None            
      
            # restore all persisted jobs already added by the user
            user_data = await self.application.persistence.get_user_data() if self.application.persistence else {}     
            
            for user_id, jobs_dic in user_data.items():
                try:
                    log_message = f"_Restoring jobs for user_ `{user_id}`..."
                    logger.debug(log_message)
                    await self.application.bot.send_message(self.bot_owner, log_message) if user_id else None
                    
                    # for each job item in user´s jobs dictionary, add a job to the job queue
                    for job_name, job_params in jobs_dic.items():
                        
                        try:
                            
                            if job_name and job_name.startswith('ping_'):
                                
                                logger.debug(f"Adding job {job_name} for user {user_id}...")
                                await self.application.bot.send_message(self.bot_owner, f"_Adding job_ `{job_name}` _for user_ `{user_id}`...") if user_id else None
                                
                                ip_address = job_params['ip_address']
                                interval = job_params['interval']
                                self.jobs[user_id] = self.application.job_queue.run_repeating(
                                    self.job, interval=interval, first=0, name=job_name, data=ip_address,
                                    user_id=user_id, chat_id=user_id, 
                                    # job_kwargs={'user_id': user_id, 'chat_id': user_id}
                                ) # , data={'args': (self,)})
                                
                        except Exception as e:
                            logger.error(f"Failed to add job {job_name} for user {user_id}: {e}")
                            self.send_message_by_api(self.bot_owner, f"Failed to add job {job_name} for user {user_id}: {e}", parse_mode=None)
                        
                except Exception as e:
                    logger.error(f"Failed to restore job {user_id}: {e}")
                    self.send_message_by_api(self.bot_owner, f"Failed to restore job {user_id}: {e}", parse_mode=None) 
            
        except Exception as e:
            logger.error(f"Failed to restore jobs: {e}")
            self.send_message_by_api(self.bot_owner, f"Failed to restore jobs: {e}", parse_mode=None)           
    
    def __init__(self, show_success=False, *args, **kwargs):
        
        super().__init__(disable_command_not_implemented=True, disable_error_handler=True, *args, **kwargs)
        
        self.jobs = {}
        
        self.external_post_init = self.load_all_user_data

    async def job(self, callback_context: CallbackContext):
        try:
            job_param = callback_context.job.data
            
            # Get the current value of the show_success flag from context user data
            # TODO: get show_success from user data
            show_success = await self.get_user_data(callback_context.job.user_id, "show_success", False)
            
            # Get job owner user id from the job context
            user_id = callback_context.job.user_id
            
            if show_success:
                self.send_message_by_api(user_id, f"Pinging {job_param}...") if show_success else None
                
            self.ping_host(job_param, show_success=show_success)
            
        except Exception as e:
            self.send_message_by_api(self.bot_owner, f"An error occurred: {e}", parse_mode=None) 

    def ping_host(self, ip_address, show_success=True):
        try:
            # Ping logic here
            param = "-n 1" if platform.system().lower() == "windows" else "-c 1"
            response = os.system(f"ping {param} {ip_address}") # Returns 0 if the host is up, 1 if the host is down
            
            if response == 0:
                self.send_message_by_api(self.bot_owner, f"{ip_address} is up!") if show_success else None
            else:
                self.send_message_by_api(self.bot_owner, f"{ip_address} is down!")
                
        except Exception as e:
            self.send_message_by_api(self.bot_owner, f"An error occurred while pinging {ip_address}: {e}", parse_mode=None)

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

    async def list_jobs(self, update: Update, context: CallbackContext):
        try:
            if not self.jobs:
                await update.message.reply_text("No active jobs.", parse_mode=None)
                return
            
            message = f"_Active jobs:_{os.linesep}"
            for user_id, job in self.jobs.items():
                try:
                    if update.effective_user.id != self.bot_owner and user_id != update.effective_user.id:
                        continue
                    
                    ip_address = job.data
                    interval = context.user_data[job.name]['interval'] if job.name in context.user_data else None
                    next_t = (job.next_t - timedelta(hours=3)).strftime('%d/%m %H:%M:%S') if job.next_t else 'N/A'
                    # message += f"`{user_id}`:`{job.name}``{ip_address}`:`{interval}s`:{next_t}{os.linesep}"
                    message += f"`{user_id}` _{interval}s_ `{ip_address}` _{next_t}{os.linesep}_"
                    
                except Exception as e:
                    logger.error(f"Failed to list job {job.name}: {e}")
                    message += f"Failed to list job {job.name}: {e}\n"
            
            await update.message.reply_text(text=message)
            
        except Exception as e:
            await update.message.reply_text(f"An error occurred: {e}", parse_mode=None)

    async def toggle_success(self, update: Update, context: CallbackContext):
        
        try:
            # Get the current value of the show_success flag from context user data 
            show_success = not bool(context.user_data["show_success"]) if "show_success" in context.user_data else False
            
            # Update the show_success flag in the user data
            await self.application.persistence.update_user_data(update.effective_user.id, {"show_success": show_success}) if self.application.persistence else None
            context.user_data["show_success"] = show_success
            
            status = "enabled" if show_success else "disabled"
            await update.message.reply_text(f"_Success messages are now:_ `{status}`.")
            
        except Exception as e:
            await update.message.reply_text(f"An error occurred: {e}", parse_mode=None)

    def run(self):
        
        try:
            self.application.add_handler(CommandHandler("addjob", self.add_job), group=-1)
            self.application.add_handler(CommandHandler("deletejob", self.delete_job), group=-1)
            self.application.add_handler(CommandHandler("listjobs", self.list_jobs), group=-1)  
            self.application.add_handler(CommandHandler("togglesuccess", self.toggle_success), group=-1)
            
            super().run()
            
        except Exception as e:
            logger.error(f"An error occurred while adding handlers or running the bot: {e}")
            self.send_message_by_api(self.bot_owner, f"An error occurred while adding handlers or running the bot: {e}", parse_mode=None)

# Create an instance of the bot
bot = HostMonitorBot() # show_success=True

# Start the bot's main loop
bot.run()

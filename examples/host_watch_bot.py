#!/usr/bin/env python
# -*- coding: utf-8 -*-
# ------------------------------------------

"""
This is a sample bot using the Telegram Bot Framework that 
overrides the initialize_handlers method to add a help command handler.
This version is inspired on and more elaborated than host_monitor because controls each host by user.
"""

__version__ = '0.4.1 Add last status to ping list'

import __init__
# import re

from tlgfwk import *

class HostWatchBot(TlgBotFwk):
     
    async def load_all_user_data(self):
        try:
            logger.info("Restoring jobs...")
            await self.application.bot.send_message(self.bot_owner, "_Restoring jobs..._") if self.bot_owner else None            
      
            # Get all persisted jobs already added by all users
            user_data = await self.application.persistence.get_user_data() if self.application.persistence else {}
            
            if not user_data or len(user_data) == 0:
                logger.info("No jobs found.")
                await self.application.bot.send_message(self.bot_owner, "_No jobs found to restore._") if self.bot_owner else None
                return     
            
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
                                
                                new_job = self.application.job_queue.run_repeating(
                                        self.job_event_handler, interval=interval, first=0, name=job_name, data=ip_address,
                                        user_id=user_id, chat_id=user_id
                                    )
                                    # job_kwargs={'user_id': user_id, 'chat_id': user_id}
                                # , data={'args': (self,)})
                                    
                                self.jobs[user_id] = self.jobs[user_id] if user_id in self.jobs else {user_id: {}}
                                self.jobs[user_id][job_name] = new_job if user_id in self.jobs else {job_name: new_job}                                
                                
                        except Exception as e:
                            logger.error(f"Failed to add job {job_name} for user {user_id}: {e}")
                            self.send_message_by_api(self.bot_owner, f"Failed to add job {job_name} for user {user_id}: {e}")
                        
                except Exception as e:
                    logger.error(f"Failed to restore job {user_id}: {e}")
                    self.send_message_by_api(self.bot_owner, f"Failed to restore job {user_id}: {e}") 
            
        except Exception as e:
            logger.error(f"Failed to restore jobs: {e}")
            self.send_message_by_api(self.bot_owner, f"Failed to restore jobs: {e}")           
    
    def __init__(self, token=None, *args, **kwargs):

        # Load the bot token from the .env file
        dotenv_path = os.path.join(os.path.dirname(__file__), 'my.env')     
        
        # super().__init__(disable_error_handler=True, env_file=dotenv_path, token=token, *args, **kwargs)
        super().__init__(env_file=dotenv_path, token=token, disable_commands_list=['paypal', 'payment','p','showbalance'], disable_command_not_implemented=True)
        
        self.jobs = {}
        
        self.external_post_init = self.load_all_user_data

    async def job_event_handler(self, callback_context: CallbackContext):
        
        try:     
            # TODO: get owner user id of job     
            user_id = callback_context.job.user_id   
            
            job_param = callback_context.job.data
            
            # Get the current value of the show_success flag from context user data
            # show_success = await self.get_user_data(callback_context.job.user_id, "show_success", False)
            show_success = callback_context.user_data["show_success"] if "show_success" in callback_context.user_data else False
            
            if show_success:
                self.send_message_by_api(user_id, f"Pinging {job_param}...") if show_success else None
                
            ping_result = await self.ping_host(job_param, show_success=show_success, user_id=user_id)
            
            # Log the result of the ping
            logger.debug(f"Ping result for {job_param}: {ping_result}")
            
            pass
            
        except Exception as e:
            self.send_message_by_api(self.bot_owner, f"An error occurred: {e}") 

    async def ping_host(self, ip_address, show_success=True, user_id=None):
        try:
            # Ping logic here
            param = "-n 1" if platform.system().lower() == "windows" else "-c 1"
            response = os.system(f"ping {param} {ip_address}") # Returns 0 if the host is up, 1 if the host is down
            
            # send message just to the job owner user
            last_status = False
            if response == 0:
                self.send_message_by_api(user_id, f"{ip_address} is up!") if show_success else None
                last_status = True # f"✅"  f"🟢"
                
            else:
                self.send_message_by_api(user_id, f"{ip_address} is down!")
                last_status = False # f"🔴"
                
            # Add last status to ping list in user data
            user_data = await self.application.persistence.get_user_data() #  if self.application.persistence else {}
            job_name = f"ping_{ip_address}"
            
            # Save new status to user data
            # create last_status key if not exists
            if 'last_status' not in user_data[user_id][job_name]:
                user_data[user_id][job_name]['last_status'] = None
            
            
            user_data[user_id][job_name]['last_status'] = last_status
            await self.application.persistence.update_user_data(user_id, user_data[user_id]) if self.application.persistence else None
            
            # force a flush of persistence to save the last status
            await self.application.persistence.flush() if self.application.persistence else None
            
            user_data = await self.application.persistence.get_user_data() if self.application.persistence else {}
        
            # logger.debug(f"{user_id} {ip_address} {last_status}")
            pass
                
        except Exception as e:
            self.send_message_by_api(self.bot_owner, f"An error occurred while pinging {ip_address}: {e}")

    async def add_job(self, update: Update, context: CallbackContext):
        """Add a new host to be monitored by the bot.

        Args:
            update (Update): _description_
            context (CallbackContext): _description_
        """
        
        try:
            user_id = update.effective_user.id
            
            if len(context.args) != 2:
                await update.message.reply_text("Usage: /addjob <ip_address> <interval_in_seconds>", parse_mode=None)
                return
            
            ip_address = context.args[0]
            interval = int(context.args[1])
            
            job_name = f"ping_{ip_address}"
            
            # check if job name already exists on the jobs list stored in user data persistence
            if job_name in context.user_data:
                await update.message.reply_text(f"Job for {ip_address} already exists.", parse_mode=None)
                return
            
            # Add the new job to the user's job dictionary. If the user already has jobs, add the new job to their existing job dictionary.        
            new_job = self.application.job_queue.run_repeating(
                self.job_event_handler, interval=interval, first=0, name=job_name, data=ip_address,
                user_id=user_id, chat_id=user_id
            )
            
            logger.debug(f"Adding job {job_name} for user {user_id}...")
            
            # If the user does not have any jobs yet, create a new dictionary for the user with the new job. 
            self.jobs[user_id] = self.jobs[user_id] if user_id in self.jobs else {user_id: {}}
            self.jobs[user_id][job_name] = new_job if user_id in self.jobs else {job_name: new_job}            
            
            # replace job object by ping parameters in user data
            context.user_data[job_name] = {
                'interval': interval, 
                'ip_address': ip_address,
                'job_owner': user_id,
                'last_status': False
            }
            
            # force persistence update of the user data
            await self.application.persistence.update_user_data(update.effective_user.id, context.user_data) if self.application.persistence else None              
            
            # Ensure persistence is flushed to save the new job
            await self.application.persistence.flush() if self.application.persistence else None
            
            await update.message.reply_text(f"Job added for {ip_address} with interval {interval} seconds.", parse_mode=None)
            
        except Exception as e:
            await update.message.reply_text(f"An error occurred: {e}", parse_mode=None)

    async def delete_job(self, update: Update, context: CallbackContext):
        """Remove a host from the bot´s monitoring list.

        Args:
            update (Update): _description_
            context (CallbackContext): _description_
        """
        
        try:
            if len(context.args) < 1:
                await update.message.reply_text("Usage: /deletejob <ip_address>", parse_mode=None)
                return
            
            user_id = update.effective_user.id
            
            ip_address = context.args[0]
            job_name = f"ping_{ip_address}"
            
            if len(context.args) != 1:
                await update.message.reply_text("Usage: /deletejob <ip_address>", parse_mode=None)
                return
            
            # if job_name not in context.user_data:
            #     await update.message.reply_text(f"No job found for {ip_address}.", parse_mode=None)
            #     return
            
            try:
                job = self.application.job_queue.get_jobs_by_name(job_name)[0]
                job.schedule_removal()
            except Exception as e:
                logger.error(f"No job found with name {job_name}")            
            
            try:
                # remove this key from user data
                context.user_data.pop(job_name) if job_name in context.user_data else None
            except Exception as e:
                logger.error(f"Failed to remove job {job_name} from user data: {e}")
            
            await update.message.reply_text(f"Job for {ip_address} deleted.", parse_mode=None)
        
        except Exception as e:
            await update.message.reply_text(f"An error occurred: {e}", parse_mode=None)

    async def list_jobs(self, update: Update, context: CallbackContext) -> None:
        """List the hosts being monitored by the bot.

        Args:
            update (Update): _description_
            context (CallbackContext): _description_
        """
        
        try:
            command_scope = context.args[0] if context.args else None
        
            # no param list all jobs, with param list jobs by name
            jobs = context.job_queue.jobs()
            effective_user_id = update.effective_user.id
            
            # for each job item in user´s jobs queue collection, add a line to the message to be sent
            message = f"_Active jobs:_{os.linesep}"
                
            all_user_data = await self.application.persistence.get_user_data() if self.application.persistence else {}
            
            has_jobs = False
            
            for job_owner_id, user_data in all_user_data.items():
                
                try:
                    # Show to the user a job in these 2 cases:
                    # -The command scope is to list all jobs and the current user is the bot owner
                    # OR
                    # -The current user is the owner of the job
                    is_allowed = (command_scope and command_scope.lower()=='all' 
                                  and effective_user_id == self.bot_owner) or (effective_user_id == job_owner_id)
                    
                    if not is_allowed:
                        continue
                    
                    for job_name, job_params in user_data.items():
                        try:
                            if not job_name.startswith('ping_'):
                                continue
                            
                            next_time = ""
                            try:
                                job = self.application.job_queue.get_jobs_by_name(job_name)[0]                        
                                next_time = (job.next_t - datetime.timedelta(hours=3)).strftime("%H:%M UTC-3") if job.next_t else ""
                            except IndexError:
                                logger.error(f"No job found with name {job_name}")
                            
                            interval = user_data[job_name]['interval'] if job_name in user_data else None
                            ip_address = user_data[job_name]['ip_address'] if job_name in user_data else None
                            job_owner = job_owner_id
                            
                            # status= user_data[job_name]['last_status'] if 'last_status' in user_data[job_name] else "🔴"
                            status='✅' if job_name in user_data and 'last_status' in user_data[job_name] and user_data[job_name]['last_status'] else "🔴"
                            
                            message += f"{status} `{job_owner:<10}` _{interval}s_ `{ip_address}` `{next_time}`{os.linesep}"
                            
                            has_jobs = True
                            
                        except Exception as e:
                            logger.error(f"An error occurred while listing job {job_name} for user {job_owner_id}: {e}")
                            
                except Exception as e:
                    logger.error(f"An error occurred while processing user data for user {job_owner_id}: {e}")
            
            # TODO: Escape possible markdown characters from user name
            # message = re.sub(r'([_*\[\]()~`>#+\-=|{}.!])', r'\\\1', message)           

            if not has_jobs:
                message = f"_No hosts monitored._{os.linesep}{os.linesep}_Usage: /pingadd <ip_address> <interval-in-seconds>_{os.linesep}_Example: `/pingadd 8.8.8.8 30`"
                logger.info(message)          
                            
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
            self.application.add_handler(CommandHandler("pingadd", self.add_job), group=-1)
            self.application.add_handler(CommandHandler("pingdelete", self.delete_job), group=-1)
            self.application.add_handler(CommandHandler("pinglist", self.list_jobs), group=-1)  
            self.application.add_handler(CommandHandler("togglesuccess", self.toggle_success), group=-1)
            
            super().run()
            
        except Exception as e:
            logger.error(f"An error occurred while adding handlers or running the bot: {e}")
            self.send_message_by_api(self.bot_owner, f"An error occurred while adding handlers or running the bot: {e}")

def main():

    # Create an instance of the bot
    bot = HostWatchBot() 

    # Start the bot's main loop
    bot.run()
    
if __name__ == '__main__':
    main()

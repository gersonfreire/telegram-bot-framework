#!/usr/bin/env python
# -*- coding: utf-8 -*-
# ------------------------------------------

"""
This is a sample bot using the Telegram Bot Framework that 
overrides the initialize_handlers method to add a help command handler.
This version is inspired on and more elaborated than host_monitor because controls each host by user.
"""

__version__ = '0.6.2 Failure History'

__changelog__ = """
DONE: 
Enable and fix unknown commands "ainda não foi implementado" message
Open URL links at internal telegram browser, it is enough to format the URL as a markdown link
Improve pinglist message formatting with header and table
0.4.9 Ping command added

TODO: 
0.5.0 Add a command to change the interval of a ping job
Pagination
"""

__todo__ = """ """

import __init__
import subprocess

from tlgfwk import *
import traceback
import util.util_watch as watch
from util.util_watch import check_port
import paramiko

class HostWatchBot(TlgBotFwk):
    
    async def escape_markdown(self, text: str) -> str:
        try:
            # return text.replace("_", "\_").replace("*", "\*").replace("`", "\`")  
            # TODO: Escape possible markdown characters from user name
            # text = re.sub(r'([_*\[\]()~`>#+\-=|{}.!])', r'\\\1', text)  
            text = re.sub(r'([_*\[\]()~`#+\-=|{}.!])', r'\\\1', text)  
        except Exception as e:
            logger.error(f"Error escaping markdown: {e}")
        return text
    
    async def ping_host_command(self, update: Update, context: CallbackContext) -> None:
        """Check if a host is up or down.

        Args:
            update (Update): _description_
            context (CallbackContext): _description_
        """
        
        try:
            # Extract the host name from the command parameters
            host_name = context.args[0] if context.args else None
            
            if not host_name:
                await update.message.reply_text("Please provide a host name to ping.")
                return
            
            # Ping the host
            ping_result = await self.ping_host(host_name, show_success=True, user_id=update.effective_user.id)
            
            # Send the result back to the user
            # if ping_result:
            #     await update.message.reply_text(f"{host_name} is up!")
            # else:
            #     await update.message.reply_text(f"{host_name} is down!")
        
        except Exception as e:
            await update.message.reply_text(f"An error occurred: {e}")
            logger.error(f"Error in ping_host_command: {e}")
    
    async def ping_host_port_command(self, update: Update, context: CallbackContext) -> None:
        """Ping a host by name or IP address and TCP port number.

        Args:
            update (Update): The update object.
            context (CallbackContext): The callback context.
        """
        
        try:
            # Extract the host name and port number from the command parameters
            if len(context.args) != 2:
                await update.message.reply_text("Usage: /pinghostport <host_name_or_ip> <port_number>")
                return
            
            host_name = context.args[0]
            port_number = int(context.args[1])
            
            # Ping the host and port
            is_open = await watch.check_port(host_name, port_number)
            
            # Send the result back to the user
            if is_open:
                await update.message.reply_text(f"Port {port_number} is open on host {host_name}.")
            else:
                await update.message.reply_text(f"Port {port_number} is closed on host {host_name}.")
        
        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
            logger.error(f"Error getting user data in {fname} at line {exc_tb.tb_lineno}: {e}")

    async def ping_interval(self, update: Update, context: CallbackContext) -> None:
        """Change the interval to check a monitored host.

        Args:
            update (Update): _description_
            context (CallbackContext): _description_
        """
        
        try:
            # Extract the host name and new interval from the command parameters
            if len(context.args) != 2:
                await update.message.reply_text("Usage: /pinginterval <host_name> <new_interval_in_seconds>")
                return
            
            host_name = context.args[0]
            new_interval = int(context.args[1])
            user_id = update.effective_user.id
            
            job_name = f"ping_{host_name}"
            
            user_data = await self.application.persistence.get_user_data() if self.application.persistence else {}
            user_hosts = user_data[update.effective_user.id] if update.effective_user.id in user_data else {}
            
            # Check if the job exists
            if job_name not in user_hosts: # self.jobs:
                await update.message.reply_text(f"No job found for {host_name}.")
                return
            
            # Get the existing job
            # job = self.jobs[job_name]            
            ping_parameters = user_hosts[job_name] if job_name in user_hosts else {}
            
            # get job from job queue
            host_job = self.application.job_queue.get_jobs_by_name(job_name)[0]
            
            # Remove the existing job
            host_job.schedule_removal()
            
            # Add a new job with the updated interval
            new_job = self.application.job_queue.run_repeating(
                self.job_event_handler, interval=new_interval, first=0, name=job_name, data=host_name,
                                        user_id=user_id, chat_id=user_id
            )
            self.jobs[job_name] = new_job
            
            context.user_data[job_name]['interval'] = new_interval
            
            await update.message.reply_text(f"Interval for {host_name} changed to {new_interval} seconds.")
        
        except Exception as e:
            await update.message.reply_text(f"An error occurred: {e}")
            logger.error(f"Error in change_ping_interval: {e}")
     
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
    
        # TODO: hotfix remove addjob and deletejob from the list of commands    
        super().__init__(env_file=dotenv_path, token=token, disable_commands_list=['paypal', 'payment','p','showbalance','addjob', 'deletejob', 'listjobs','listalljobs','togglesuccess']) 
        
        self.jobs = {}
        
        self.external_post_init = self.load_all_user_data

    async def job_event_handler(self, callback_context: CallbackContext):
        
        try:     
            # get owner user id of job     
            user_id = callback_context.job.user_id   
            
            host_address = callback_context.job.data
            
            # Get the current value of the show_success flag from context user data
            # show_success = await self.get_user_data(callback_context.job.user_id, "show_success", False)
            show_success = callback_context.user_data["show_success"] if "show_success" in callback_context.user_data else False
            
            if show_success:
                self.send_message_by_api(user_id, f"Pinging {host_address}...") if show_success else None
                
            ping_result = await self.ping_host(host_address, show_success=show_success, user_id=user_id)
            
            https_ping_result = False # await self.http_ping(host_address, debug_status=show_success, user_id=user_id)
            http_ping_result = False # await self.http_ping(host_address, debug_status=show_success, user_id=user_id, http_type='http')
            
            job_name = f"ping_{host_address}"  
            callback_context.user_data[job_name]['last_status'] = ping_result # and http_ping_result
            callback_context.user_data[job_name]['http_status'] = http_ping_result     
            callback_context.user_data[job_name]['https_status'] = https_ping_result     
            callback_context.user_data[job_name]['http_ping_time'] = (datetime.datetime.now()).strftime("%H:%M")
            callback_context.user_data[job_name]['last_fail_date'] = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S") if not ping_result else None
            
            # TODO: execute a check for a specific port
            port = callback_context.user_data[job_name]['port'] if 'port' in callback_context.user_data[job_name] else 80
            port_result = await watch.check_port(host_address, port)
            
            callback_context.user_data[job_name]['port_status'] = port_result
            
            # Log the result of the ping
            logger.debug(f"Ping result for {host_address}: {ping_result} {https_ping_result} {port_result}")
            
        except Exception as e:
            self.send_message_by_api(self.bot_owner, f"An error occurred: {e}") 
    
    async def http_ping(self, ip_address, debug_status=True, user_id=None, http_type='https'):
        
        http_result = False
        url = f'{http_type}://{ip_address}'
        
        try:
            async with httpx.AsyncClient() as client:
                
                response = None
                
                try:
                    response = await client.get(url)
                # except httpx.RequestError as exc:
                except Exception as e:
                    # logger.error(f"An error occurred while requesting {exc.request.url!r}.")
                    logger.error(f"An error occurred while requesting {url}{os.linesep}{e}")
                
                if response and (response.status_code == 200 or response.status_code == 302 or response.status_code == 301): 
                    # 302 is a redirect nd 301 is a permanent redirect
                    self.send_message_by_api(user_id, f"{url} is reachable!") if debug_status else None
                    http_result = True
                else:
                    self.send_message_by_api(user_id, f"{url} is not reachable!") if debug_status else None
                
                logger.debug(f"HTTP ping result for {url}: {http_result}")
                
                # Add last status to ping list in user data
                user_data = await self.application.persistence.get_user_data() if self.application.persistence else {}
                job_name = f"ping_{ip_address}"
                
                if http_type=='http':
                    user_data[user_id][job_name]['http_status'] = http_result
                else:
                    user_data[user_id][job_name]['https_status'] = http_result
                    
                await self.application.persistence.update_user_data(user_id, user_data[user_id]) if self.application.persistence else None
                
                # Force a flush of persistence to save the last status
                await self.application.persistence.flush() if self.application.persistence else None
                
                user_data = await self.application.persistence.get_user_data() if self.application.persistence else {}
                
        except Exception as e:
            tb = traceback.format_exc()
            script_name = __file__
            # line_number = tb.splitlines()[-3].split(",")[1].strip().split(" ")[1]
            # error_location = f"Error in {script_name} at line {line_number}"
            # logger.error(error_location)
            logger.error(str(tb))
            # self.send_message_by_api(self.bot_owner, f"An error occurred while checking {ip_address}: {e}")
            # self.send_message_by_api(self.bot_owner, error_location)
        
        return http_result

    async def ping_host(self, ip_address, show_success=True, user_id=None):
        ping_result = False
        
        try:
            # Ping logic here
            param = "-n 1" if platform.system().lower() == "windows" else "-c 1"
            response = os.system(f"ping {param} {ip_address}") # Returns 0 if the host is up, 1 if the host is down
            
            # send message just to the job owner user
            if response == 0:
                self.send_message_by_api(user_id, f"{ip_address} is up!") if show_success else None
                ping_result = True
            else:
                self.send_message_by_api(user_id, f"{ip_address} is down!")
                
                # Set the last_fail_date to the current date and time
                current_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                user_data = await self.application.persistence.get_user_data() if self.application.persistence else {}
                job_name = f"ping_{ip_address}"
                if user_id in user_data and job_name in user_data[user_id]:
                    user_data[user_id][job_name]['last_fail_date'] = current_time
                    await self.application.persistence.update_user_data(user_id, user_data[user_id])
                    await self.application.persistence.flush()
                
            logger.debug(f"Ping result for {ip_address}: {ping_result}")
                
            # Add last status to ping list in user data
            user_data = await self.application.persistence.get_user_data() if self.application.persistence else {}
            job_name = f"ping_{ip_address}"
            
            user_data[user_id][job_name]['last_status'] = ping_result
            user_data[user_id][job_name]['http_ping_time'] = (datetime.datetime.now()).strftime("%H:%M")
            user_data[user_id][job_name]['last_fail_date'] = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S") if not ping_result else None
            
            await self.application.persistence.update_user_data(user_id, user_data[user_id]) if self.application.persistence else None
            
            # force a flush of persistence to save the last status
            await self.application.persistence.flush() if self.application.persistence else None
            
            user_data = await self.application.persistence.get_user_data() if self.application.persistence else {}
                
        except Exception as e:
            self.send_message_by_api(self.bot_owner, f"An error occurred while pinging {ip_address}: {e}")
            
        return ping_result

    async def ping_add(self, update: Update, context: CallbackContext):
        """Add a new host to be monitored by the bot.

        Args:
            update (Update): _description_
            context (CallbackContext): _description_
        """
        
        try:
            user_id = update.effective_user.id
            
            # in case just one argument is passed, generate a random interval between 120 and 2400 seconds
            if len(context.args) == 1:
                interval = random.randint(120, 2400)
                context.args.append(interval)
                # default port to be checked is 443
                context.args.append(443)
            
            if len(context.args) < 2:
                await update.message.reply_text("Usage: /pingadd <ip_address> <interval_in_seconds>", parse_mode=None)
                return
            
            ip_address = context.args[0]
            interval = int(context.args[1])
            
            job_name = f"ping_{ip_address}"
            
            # if has a third argument, it is the port to be checked
            checked_port = int(context.args[2]) if len(context.args) >= 3 and str(context.args[2]).isdigit() else 80
            
            # check if job name already exists on the jobs list stored in user data persistence
            if job_name in context.user_data:
                await update.message.reply_text(f"Host {ip_address} already exists.", parse_mode=None)
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
                'last_status': False,
                'http_status': False,
                'http_ping_time': None,
                'port': checked_port,
                'last_fail_date': None
            }
            
            # force persistence update of the user data
            await self.application.persistence.update_user_data(update.effective_user.id, context.user_data) if self.application.persistence else None              
            
            # Ensure persistence is flushed to save the new job
            await self.application.persistence.flush() if self.application.persistence else None
            
            await update.message.reply_text(f"Hosted {ip_address} added with interval {interval} seconds.", parse_mode=None)
            
        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            fname = os.path.split(exc_tb.tb_frame.f_code.co_filename())[1]
            logger.error(f"Error getting user data in {fname} at line {exc_tb.tb_lineno}: {e}")
            
            await update.message.reply_text(f"An error occurred: {e}", parse_mode=None)

    async def ping_delete(self, update: Update, context: CallbackContext):
        
        """Remove a host from the bot´s monitoring list.

        Args:
            update (Update): _description_
            context (CallbackContext): _description_
        """
        
        try:
            if len(context.args) < 1:
                await update.message.reply_text("Usage: /pingdelete <ip_address>", parse_mode=None)
                return
            
            user_id = update.effective_user.id
            
            ip_address = context.args[0]
            job_name = f"ping_{ip_address}"
            
            if len(context.args) != 1:
                await update.message.reply_text("Usage: /pingdelete <ip_address>", parse_mode=None)
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
            
            await update.message.reply_text(f"Host {ip_address} deleted.", parse_mode=None)
        
        except Exception as e:
            await update.message.reply_text(f"An error occurred: {e}", parse_mode=None)

    async def ping_list(self, update: Update, context: CallbackContext) -> None:
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
            
            # Header of monitored hosts list in case of common user
            message = f"_Active monitored host:_{os.linesep}`pi p     interv next last host`{os.linesep}"
            
            # header of monitored hosts list in case of bot owner
            if effective_user_id == self.bot_owner:
                # message = f"_Active monitored host:_{os.linesep}`pi hs ht p     user-id   interv next last host`{os.linesep}"
                message = f"_Active monitored host:_{os.linesep}`pi p     user-id   interv next last host`{os.linesep}"
                
            all_user_data = await self.application.persistence.get_user_data() if self.application.persistence else {}
            
            has_jobs = False
            
            hosts_counter = 0
            max_listed_hosts = 50
            for job_owner_id, user_data in all_user_data.items():
                
                try:
                    # User allowed in these 2 cases:
                    # -The command scope is to list all jobs and the current user is the bot owner
                    # -The current user is the owner of the job
                    is_allowed = (command_scope and command_scope.lower()=='all' 
                                  and effective_user_id == self.bot_owner) or (effective_user_id == job_owner_id)
                    
                    if not is_allowed:
                        continue
                    
                    for job_name, job_params in user_data.items():
                        try:
                            if not job_name.startswith('ping_'):
                                continue
                            
                            # limit the number of jobs to be listed
                            hosts_counter = hosts_counter + 1
                            if hosts_counter > max_listed_hosts:
                                break
                            
                            next_time = ""
                            try:
                                job = self.application.job_queue.get_jobs_by_name(job_name)[0]                        
                                next_time = (job.next_t - datetime.timedelta(hours=3)).strftime("%H:%M") if job.next_t else ""
                            except IndexError:
                                logger.error(f"No job found with name {job_name}")
                            
                            interval = user_data[job_name]['interval'] if job_name in user_data else None
                            ip_address = user_data[job_name]['ip_address'] if job_name in user_data else None
                            job_owner = job_owner_id
                            
                            ping_status='✅' if job_name in user_data and 'last_status' in user_data[job_name] and user_data[job_name]['last_status'] else "🔴"
                            https_status='✅' if job_name in user_data and 'https_status' in user_data[job_name] and user_data[job_name]['https_status'] else "🔴"
                            http_status='✅' if job_name in user_data and 'http_status' in user_data[job_name] and user_data[job_name]['http_status'] else "🔴"
                            check_port_status = '✅' if job_name in user_data and 'port_status' in user_data[job_name] and user_data[job_name]['port_status'] else "🔴"
                            
                            checked_port = user_data[job_name]['port'] if job_name in user_data and 'port' in user_data[job_name] else 80
                            
                            url = f'https://{ip_address}' 
                            markdown_link = f"[{ip_address}]({url})" 
                            
                            http_ping_time = user_data[job_name]['http_ping_time'] if job_name in user_data and  'http_ping_time' in user_data[job_name] else None
                            
                            last_fail_date = user_data[job_name]['last_fail_date'] if job_name in user_data and 'last_fail_date' in user_data[job_name] else None
                            
                            interval = f"{interval}s" if interval else None
                            if effective_user_id == self.bot_owner:
                                message += f"{ping_status}{check_port_status}`{checked_port:<5}``{job_owner:<10}` `{interval:<6}` `{next_time}` `{http_ping_time}` {markdown_link}{os.linesep}"
                            else:
                                message += f"{ping_status}{check_port_status}`{checked_port:<5}``{interval:<6}` `{next_time}` `{http_ping_time}` {markdown_link}{os.linesep}"
                            
                            has_jobs = True
                            
                        except Exception as e:
                            tb = traceback.format_exc()
                            logger.error(f"An error occurred while listing job {job_name} for user {job_owner_id}: {e}{os.linesep}{tb}")
                            
                except Exception as e:
                    logger.error(f"An error occurred while processing user data for user {job_owner_id}: {e}")
                     
            if not has_jobs:
                message = f"_No hosts monitored._{os.linesep}{os.linesep}_Usage: /pinglist <ip_address> <interval-in-seconds>_{os.linesep}_Example: `/pinglist`"
                logger.info(message)  
            
            else:
                logger.info(message)
                message += f"{os.linesep}_Total of monitored hosts: {len(jobs)}_"        
                            
            await update.message.reply_text(text=message) 
                    
        except Exception as e:
            await update.message.reply_text(f"An error occurred: {e}", parse_mode=None)

    async def ping_log(self, update: Update, context: CallbackContext):
        
        try:
            # Get the current value of the show_success flag from context user data 
            show_success = not bool(context.user_data["show_success"]) if "show_success" in context.user_data else False
            
            # Update the show_success flag in the user data
            await self.application.persistence.update_user_data(update.effective_user.id, {"show_success": show_success}) if self.application.persistence else None
            context.user_data["show_success"] = show_success
            
            status = "enabled" if show_success else "disabled"
            await update.message.reply_text(f"_Monitoring log is now_ `{status}`.")
            
        except Exception as e:
            await update.message.reply_text(f"An error occurred: {e}", parse_mode=None)

    async def change_ping_port_command(self, update: Update, context: CallbackContext) -> None:
        """Change the TCP port checked by the scheduled task of pinging a host.

        Args:
            update (Update): The update object.
            context (CallbackContext): The callback context.
        """
        
        try:
            # Extract the host name and new port number from the command parameters
            if len(context.args) != 2:
                await update.message.reply_text(await self.escape_markdown("Usage: /changepingport <host_name_or_ip> <new_port_number>"))
                return
            
            host_name = context.args[0]
            new_port_number = int(context.args[1])
            user_id = update.effective_user.id
            
            job_name = f"ping_{host_name}"
            
            user_data = await self.application.persistence.get_user_data() if self.application.persistence else {}
            user_hosts = user_data[update.effective_user.id] if update.effective_user.id in user_data else {}
            
            # Check if the job exists
            if job_name not in user_hosts:
                await update.message.reply_text(f"No job found for {host_name}.")
                return
            
            # Update the port in the user data
            user_hosts[job_name]['port'] = new_port_number
            context.user_data[job_name]['port'] = new_port_number
            await self.application.persistence.update_user_data(user_id, user_hosts)
            await self.application.persistence.flush()
            
            await update.message.reply_text(f"Port for {host_name} changed to {new_port_number}.")
        
        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
            logger.error(f"Error getting user data in {fname} at line {exc_tb.tb_lineno}: {e}")
            
            await update.message.reply_text(f"An error occurred: {e}", parse_mode=None)

    async def store_credentials(self, update: Update, context: CallbackContext) -> None:
        """Store username and password associated with a host or show existing credentials if no parameters are provided.

        Args:
            update (Update): The update object.
            context (CallbackContext): The callback context.
        """
        
        try:
            # Extract the host name, username, and password from the command parameters
            if len(context.args) != 4:
                if len(context.args) == 1:
                    host_name = context.args[0]
                    user_id = update.effective_user.id
                    
                    job_name = f"ping_{host_name}"
                    
                    user_data = await self.application.persistence.get_user_data() if self.application.persistence else {}
                    user_hosts = user_data[update.effective_user.id] if update.effective_user.id in user_data else {}
                    
                    # Check if the job exists
                    if job_name not in user_hosts:
                        await update.message.reply_text(f"No job found for {host_name}.")
                        return
                    
                    # Retrieve and display the existing username and password
                    username = user_hosts[job_name].get('username', 'Not set')
                    password = user_hosts[job_name].get('password', 'Not set')
                    connection_port = user_hosts[job_name].get('connection_port', 22)
                    
                    await update.message.reply_text(f"Current credentials for {host_name}:{os.linesep}Username: {username}{os.linesep}Password: {password}{os.linesep}Port: {connection_port}")
                else:
                    await update.message.reply_text(await self.escape_markdown("Usage: /storecredentials <host_name_or_ip> <username> <password> [optional-port=22]"))
                return
            
            host_name = context.args[0]
            username = context.args[1]
            password = context.args[2]
            connection_port = int(context.args[3])
            user_id = update.effective_user.id
            
            job_name = f"ping_{host_name}"
            
            user_data = await self.application.persistence.get_user_data() if self.application.persistence else {}
            user_hosts = user_data[update.effective_user.id] if update.effective_user.id in user_data else {}
            
            # Check if the job exists
            if job_name not in user_hosts:
                await update.message.reply_text(f"No job found for {host_name}.")
                return
            
            # Store the username and password in the user data
            user_hosts[job_name]['username'] = username
            user_hosts[job_name]['password'] = password
            user_hosts[job_name]['connection_port'] = connection_port
            context.user_data[job_name]['username'] = username
            context.user_data[job_name]['password'] = password
            context.user_data[job_name]['connection_port'] = connection_port
            
            await self.application.persistence.update_user_data(user_id, user_hosts)
            await self.application.persistence.flush()
            
            await update.message.reply_text(f"Credentials for {host_name} stored successfully.")
        
        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            fname = os.path.split(exc_tb.tb.frame.f_code.co.filename())[1]
            logger.error(f"Error storing credentials in {fname} at line {exc_tb.tb_lineno}: {e}")
            
            await update.message.reply_text(f"An error occurred: {e}", parse_mode=None)

    async def execute_command(self, update: Update, context: CallbackContext) -> None:
        """Execute a command on the host operating system and return the result.

        Args:
            update (Update): The update object.
            context (CallbackContext): The callback context.
        """
        
        try:
            # Extract the command from the command parameters
            command = ' '.join(context.args)
            
            if not command:
                await update.message.reply_text("Please provide a command to execute.")
                return
            
            # Execute the command on the host operating system
            result = subprocess.run(command, shell=True, capture_output=True, text=True)
            
            # Send the result back to the user
            if result.returncode == 0:
                await update.message.reply_text(await self.escape_markdown(result.stdout))
            else:
                await update.message.reply_text(await self.escape_markdown(f"Command execution failed:\n{result.stderr}"))
        
        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            fname = os.path.split(exc_tb.tb.frame.f_code.co.filename())[1]
            logger.error(f"Error storing credentials in {fname} at line {exc_tb.tb_lineno}: {e}")
            
            await update.message.reply_text(f"An error occurred: {e}", parse_mode=None)

    async def execute_ssh_command(self, update: Update, context: CallbackContext) -> None:
        """Execute an SSH command on the remote host using stored credentials and return the result.

        Args:
            update (Update): The update object.
            context (CallbackContext): The callback context.
        """
        
        try:
            # Extract the host name and command from the command parameters
            if len(context.args) < 2:
                await update.message.reply_text(await self.escape_markdown("Usage: /ssh <host_name_or_ip> <command>"))
                return
            
            host_name = context.args[0]
            command = ' '.join(context.args[1:])
            user_id = update.effective_user.id
            
            job_name = f"ping_{host_name}"
            
            user_data = await self.application.persistence.get_user_data() if self.application.persistence else {}
            user_hosts = user_data[update.effective_user.id] if update.effective_user.id in user_data else {}
            
            # Check if the job exists
            if job_name not in user_hosts:
                await update.message.reply_text(f"No job found for {host_name}.")
                return
            
            # Retrieve the stored credentials
            username = user_hosts[job_name].get('username')
            password = user_hosts[job_name].get('password')
            port = user_hosts[job_name].get('connection_port', 22)
            
            if not username or not password:
                await update.message.reply_text(f"No credentials found for {host_name}.")
                return
            
            # Execute the SSH command
            ssh = paramiko.SSHClient()
            ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            ssh.connect(hostname=host_name, port=port, username=username, password=password)
            
            stdin, stdout, stderr = ssh.exec_command(command)
            result = stdout.read().decode('utf-8') + stderr.read().decode('utf-8')
            ssh.close()
            
            # Send the result back to the user
            await update.message.reply_text(await self.escape_markdown(result))
        
        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            fname = os.path.split(exc_tb.tb.frame.f_code.co.filename())[1]
            logger.error(f"Error executing SSH command in {fname} at line {exc_tb.tb_lineno}: {e}")
            
            await update.message.reply_text(f"An error occurred: {e}", parse_mode=None)
 
    async def list_failures(self, update: Update, context: CallbackContext) -> None:
        """List each host and its last failure date.

        Args:
            update (Update): The update object.
            context (CallbackContext): The callback context.
        """
        
        try:
            user_id = update.effective_user.id
            user_data = await self.application.persistence.get_user_data() if self.application.persistence else {}
            user_hosts = user_data[user_id] if user_id in user_data else {}

            if not user_hosts:
                await update.message.reply_text("No hosts found.")
                return
            
            message = f"_Hosts and their last failure dates:_{os.linesep}"
            
            for job_name, job_params in user_hosts.items():
                if not job_name.startswith('ping_'):
                    continue
                
                try:
                    host_name = job_params.get('ip_address', 'Unknown')
                    last_fail_date = job_params.get('last_fail_date', 'No failures')
                    
                    last_fail_date = context.user_data[job_name]['last_fail_date'] if job_name in context.user_data and 'last_fail_date' in context.user_data[job_name] else last_fail_date
                    
                    # url = f'https://{ip_address}' 
                    # markdown_link = f"[{ip_address}]({url})"                     
                    
                    message += f"`{last_fail_date:<24}` `{host_name}` {os.linesep}"
                except Exception as e:
                    logger.error(f"Error processing host {job_name}: {e}")
                    continue
            
            await update.message.reply_text(message)
        
        except Exception as e:
            await update.message.reply_text(f"An error occurred: {e}")
            logger.error(f"Error in list_failures: {e}")

    def run(self):
        
        try:
            self.application.add_handler(CommandHandler("pingadd", self.ping_add), group=-1)
            self.application.add_handler(CommandHandler("pingdelete", self.ping_delete), group=-1)
            self.application.add_handler(CommandHandler("pinglist", self.ping_list), group=-1)  
            self.application.add_handler(CommandHandler("pinglog", self.ping_log), group=-1)
            self.application.add_handler(CommandHandler("pinghost", self.ping_host_command), group=-1)
            self.application.add_handler(CommandHandler("pinginterval", self.ping_interval), group=-1)
            self.application.add_handler(CommandHandler("pinghostport", self.ping_host_port_command), group=-1)  # Register the new command handler
            self.application.add_handler(CommandHandler("changepingport", self.change_ping_port_command), group=-1)  # Register the new command handler
            self.application.add_handler(CommandHandler("storecredentials", self.store_credentials), group=-1)  # Register the new command handler
            self.application.add_handler(CommandHandler("exec", self.execute_command, filters=filters.User(user_id=self.admins_owner)), group=-1)  # Register the new command handler
            self.application.add_handler(CommandHandler("ssh", self.execute_ssh_command, filters=filters.User(user_id=self.admins_owner)), group=-1)  # Register the new command handler
            self.application.add_handler(CommandHandler("listfailures", self.list_failures), group=-1)  # Register the new command handler
            
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

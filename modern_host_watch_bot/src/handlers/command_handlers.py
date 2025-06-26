"""
Command handlers for the Modern Host Watch Bot.
"""
import logging
import uuid
from datetime import datetime
from typing import Optional

from telegram import Update
from telegram.ext import ContextTypes
from telegram.constants import ParseMode

from ..models.host import HostJob, HostConfig, HostStatus
from ..models.user import User, UserPreferences
from ..services.monitoring import MonitoringService
from ..services.persistence import db_manager
from ..utils.network import network_checker
from ..utils.ssh import ssh_manager
from ..utils.formatters import formatter
from ..config.settings import settings

logger = logging.getLogger(__name__)


class CommandHandlers:
    """Command handlers for the bot."""
    
    def __init__(self, monitoring_service: MonitoringService):
        self.monitoring_service = monitoring_service
    
    async def start_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Handle /start command."""
        user = update.effective_user
        if not user:
            return
        
        # Create or get user
        db_user = await db_manager.get_user(user.id)
        if not db_user:
            # Create new user
            db_user = User(
                user_id=user.id,
                username=user.username,
                first_name=user.first_name,
                last_name=user.last_name,
                is_admin=user.id in settings.admin_user_ids,
                is_owner=user.id == settings.bot_owner_id
            )
            await db_manager.save_user(db_user)
        
        # Update activity
        db_user.update_activity()
        await db_manager.save_user(db_user)
        
        # Send welcome message
        welcome_text = f"""
🤖 *Welcome to Modern Host Watch Bot!*

Hi {user.first_name or user.username or 'there'}!

I can help you monitor your servers and hosts. Use /help to see all available commands.

*Quick Start:*
• `/pingadd google.com 300` - Monitor Google every 5 minutes
• `/pinglist` - See your monitored hosts
• `/help` - Get detailed help
        """
        
        await update.message.reply_text(
            welcome_text,
            parse_mode=ParseMode.MARKDOWN
        )
    
    async def help_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Handle /help command."""
        user = update.effective_user
        if not user:
            return
        
        db_user = await db_manager.get_user(user.id)
        is_admin = db_user.is_admin if db_user else False
        
        help_text = formatter.format_help_message(is_admin)
        
        await update.message.reply_text(
            help_text,
            parse_mode=ParseMode.MARKDOWN
        )
    
    async def pingadd_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Handle /pingadd command."""
        user = update.effective_user
        if not user:
            return
        
        # Parse arguments
        args = context.args
        if len(args) < 2:
            await update.message.reply_text(
                "❌ *Usage:* `/pingadd <host> <interval_seconds> [port]`\n\n"
                "*Example:* `/pingadd google.com 300 80`",
                parse_mode=ParseMode.MARKDOWN
            )
            return
        
        host_address = args[0]
        try:
            interval_seconds = int(args[1])
        except ValueError:
            await update.message.reply_text(
                "❌ *Error:* Interval must be a number"
            )
            return
        
        port = int(args[2]) if len(args) > 2 else settings.default_port
        
        try:
            # Validate host config
            host_config = HostConfig(
                host_address=host_address,
                interval_seconds=interval_seconds,
                port=port
            )
            
            # Check if job already exists
            existing_job = await self.monitoring_service.get_job_by_host(user.id, host_address)
            if existing_job:
                await update.message.reply_text(
                    f"❌ *Error:* Host `{host_address}` is already being monitored"
                )
                return
            
            # Check user job limit
            user_jobs = await self.monitoring_service.get_user_jobs(user.id)
            if len(user_jobs) >= settings.max_hosts_per_user:
                await update.message.reply_text(
                    f"❌ *Error:* You have reached the maximum limit of {settings.max_hosts_per_user} hosts"
                )
                return
            
            # Create job
            job = HostJob(
                job_id=str(uuid.uuid4()),
                user_id=user.id,
                host_config=host_config,
                host_status=HostStatus(host_address=host_address)
            )
            
            # Add monitoring job
            if await self.monitoring_service.add_host_job(job):
                await update.message.reply_text(
                    f"✅ *Host Added Successfully!*\n\n"
                    f"*Host:* `{host_address}`\n"
                    f"*Port:* `{port}`\n"
                    f"*Interval:* `{interval_seconds}s`\n"
                    f"*Status:* Monitoring started",
                    parse_mode=ParseMode.MARKDOWN
                )
            else:
                await update.message.reply_text(
                    "❌ *Error:* Failed to add host monitoring"
                )
                
        except ValueError as e:
            await update.message.reply_text(
                f"❌ *Error:* {str(e)}"
            )
        except Exception as e:
            logger.error(f"Error in pingadd command: {e}")
            await update.message.reply_text(
                "❌ *Error:* An unexpected error occurred"
            )
    
    async def pingdelete_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Handle /pingdelete command."""
        user = update.effective_user
        if not user:
            return
        
        args = context.args
        if len(args) != 1:
            await update.message.reply_text(
                "❌ *Usage:* `/pingdelete <host>`\n\n"
                "*Example:* `/pingdelete google.com`",
                parse_mode=ParseMode.MARKDOWN
            )
            return
        
        host_address = args[0]
        
        try:
            # Find job
            job = await self.monitoring_service.get_job_by_host(user.id, host_address)
            if not job:
                await update.message.reply_text(
                    f"❌ *Error:* Host `{host_address}` is not being monitored"
                )
                return
            
            # Remove job
            if await self.monitoring_service.remove_host_job(job.job_id):
                await update.message.reply_text(
                    f"✅ *Host Removed Successfully!*\n\n"
                    f"*Host:* `{host_address}`\n"
                    f"*Status:* Monitoring stopped",
                    parse_mode=ParseMode.MARKDOWN
                )
            else:
                await update.message.reply_text(
                    "❌ *Error:* Failed to remove host monitoring"
                )
                
        except Exception as e:
            logger.error(f"Error in pingdelete command: {e}")
            await update.message.reply_text(
                "❌ *Error:* An unexpected error occurred"
            )
    
    async def pinglist_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Handle /pinglist command."""
        user = update.effective_user
        if not user:
            return
        
        try:
            db_user = await db_manager.get_user(user.id)
            if not db_user:
                await update.message.reply_text(
                    "❌ *Error:* User not found"
                )
                return
            
            # Check if user wants to see all jobs (admin only)
            show_all = len(context.args) > 0 and context.args[0].lower() == 'all'
            
            if show_all and not db_user.has_permission('admin'):
                await update.message.reply_text(
                    "❌ *Error:* You don't have permission to view all hosts"
                )
                return
            
            # Get jobs
            if show_all:
                jobs = list(self.monitoring_service.active_jobs.values())
            else:
                jobs = await self.monitoring_service.get_user_jobs(user.id)
            
            if not jobs:
                await update.message.reply_text(
                    "_No hosts monitored._\n\n"
                    "Use `/pingadd <host> <interval>` to start monitoring",
                    parse_mode=ParseMode.MARKDOWN
                )
                return
            
            # Format listing
            listing_text = formatter.format_host_listing(jobs, show_all)
            
            await update.message.reply_text(
                listing_text,
                parse_mode=ParseMode.MARKDOWN,
                disable_web_page_preview=True
            )
            
        except Exception as e:
            logger.error(f"Error in pinglist command: {e}")
            await update.message.reply_text(
                "❌ *Error:* An unexpected error occurred"
            )
    
    async def pinghost_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Handle /pinghost command."""
        user = update.effective_user
        if not user:
            return
        
        args = context.args
        if len(args) != 1:
            await update.message.reply_text(
                "❌ *Usage:* `/pinghost <host>`\n\n"
                "*Example:* `/pinghost google.com`",
                parse_mode=ParseMode.MARKDOWN
            )
            return
        
        host_address = args[0]
        
        try:
            # Send typing indicator
            await context.bot.send_chat_action(chat_id=update.effective_chat.id, action="typing")
            
            # Perform ping check
            is_online, response_time = await network_checker.ping_host(host_address)
            
            # Format response
            status_icon = "🟢" if is_online else "🔴"
            status_text = "Online" if is_online else "Offline"
            response_text = f" ({response_time}ms)" if response_time else ""
            
            message = f"{status_icon} *Manual Ping Result*\n\n"
            message += f"*Host:* `{host_address}`\n"
            message += f"*Status:* {status_text}{response_text}\n"
            message += f"*Time:* {datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')}"
            
            await update.message.reply_text(
                message,
                parse_mode=ParseMode.MARKDOWN
            )
            
        except Exception as e:
            logger.error(f"Error in pinghost command: {e}")
            await update.message.reply_text(
                "❌ *Error:* An unexpected error occurred"
            )
    
    async def pinghostport_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Handle /pinghostport command."""
        user = update.effective_user
        if not user:
            return
        
        args = context.args
        if len(args) != 2:
            await update.message.reply_text(
                "❌ *Usage:* `/pinghostport <host> <port>`\n\n"
                "*Example:* `/pinghostport google.com 443`",
                parse_mode=ParseMode.MARKDOWN
            )
            return
        
        host_address = args[0]
        try:
            port = int(args[1])
        except ValueError:
            await update.message.reply_text(
                "❌ *Error:* Port must be a number"
            )
            return
        
        try:
            # Send typing indicator
            await context.bot.send_chat_action(chat_id=update.effective_chat.id, action="typing")
            
            # Perform port check
            is_open = await network_checker.check_port(host_address, port)
            
            # Format response
            status_icon = "✅" if is_open else "❌"
            status_text = "Open" if is_open else "Closed"
            
            message = f"{status_icon} *Port Check Result*\n\n"
            message += f"*Host:* `{host_address}`\n"
            message += f"*Port:* `{port}`\n"
            message += f"*Status:* {status_text}\n"
            message += f"*Time:* {datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')}"
            
            await update.message.reply_text(
                message,
                parse_mode=ParseMode.MARKDOWN
            )
            
        except Exception as e:
            logger.error(f"Error in pinghostport command: {e}")
            await update.message.reply_text(
                "❌ *Error:* An unexpected error occurred"
            )
    
    async def listfailures_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Handle /listfailures command."""
        user = update.effective_user
        if not user:
            return
        
        try:
            # Get user jobs
            jobs = await self.monitoring_service.get_user_jobs(user.id)
            
            # Filter jobs with failures
            failed_jobs = [job for job in jobs if job.host_status.last_failure]
            
            if not failed_jobs:
                await update.message.reply_text(
                    "_No recent failures._\n\n"
                    "All your monitored hosts are working properly! 🎉",
                    parse_mode=ParseMode.MARKDOWN
                )
                return
            
            # Format failures list
            failures_text = formatter.format_failures_list(failed_jobs)
            
            await update.message.reply_text(
                failures_text,
                parse_mode=ParseMode.MARKDOWN,
                disable_web_page_preview=True
            )
            
        except Exception as e:
            logger.error(f"Error in listfailures command: {e}")
            await update.message.reply_text(
                "❌ *Error:* An unexpected error occurred"
            )
    
    async def pinglog_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Handle /pinglog command."""
        user = update.effective_user
        if not user:
            return
        
        try:
            db_user = await db_manager.get_user(user.id)
            if not db_user:
                await update.message.reply_text(
                    "❌ *Error:* User not found"
                )
                return
            
            # Toggle success logs
            db_user.preferences.show_success_logs = not db_user.preferences.show_success_logs
            db_user.update_activity()
            
            await db_manager.save_user(db_user)
            
            status = "enabled" if db_user.preferences.show_success_logs else "disabled"
            
            await update.message.reply_text(
                f"✅ *Success Logs {status.title()}*\n\n"
                f"Success notifications are now {status}.",
                parse_mode=ParseMode.MARKDOWN
            )
            
        except Exception as e:
            logger.error(f"Error in pinglog command: {e}")
            await update.message.reply_text(
                "❌ *Error:* An unexpected error occurred"
            ) 
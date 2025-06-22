"""
Admin command handlers for the Modern Host Watch Bot.
"""
import asyncio
import subprocess
import logging
from typing import Optional

from telegram import Update
from telegram.ext import ContextTypes
from telegram.constants import ParseMode

from ..services.persistence import db_manager
from ..utils.ssh import ssh_manager
from ..utils.formatters import formatter
from ..config.settings import settings

logger = logging.getLogger(__name__)


class AdminHandlers:
    """Admin command handlers for the bot."""
    
    async def exec_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Handle /exec command (admin only)."""
        user = update.effective_user
        if not user:
            return
        
        # Check admin permission
        db_user = await db_manager.get_user(user.id)
        if not db_user or not db_user.has_permission('admin'):
            await update.message.reply_text(
                "❌ *Error:* This command is restricted to administrators"
            )
            return
        
        # Parse command
        if not context.args:
            await update.message.reply_text(
                "❌ *Usage:* `/exec <command>`\n\n"
                "*Example:* `/exec uptime`",
                parse_mode=ParseMode.MARKDOWN
            )
            return
        
        command = ' '.join(context.args)
        
        try:
            # Send typing indicator
            await context.bot.send_chat_action(chat_id=update.effective_chat.id, action="typing")
            
            # Execute command
            process = await asyncio.create_subprocess_exec(
                *command.split(),
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            
            stdout, stderr = await asyncio.wait_for(
                process.communicate(),
                timeout=30
            )
            
            # Format output
            if process.returncode == 0:
                result = f"✅ *Command Executed Successfully*\n\n"
                if stdout:
                    result += f"*Output:*\n```\n{stdout.decode('utf-8')}\n```"
                else:
                    result += "*Output:* (empty)"
            else:
                result = f"❌ *Command Failed*\n\n"
                if stderr:
                    result += f"*Error:*\n```\n{stderr.decode('utf-8')}\n```"
                else:
                    result += "*Error:* (no error output)"
            
            await update.message.reply_text(
                result,
                parse_mode=ParseMode.MARKDOWN
            )
            
        except asyncio.TimeoutError:
            await update.message.reply_text(
                "❌ *Error:* Command execution timed out"
            )
        except Exception as e:
            logger.error(f"Error in exec command: {e}")
            await update.message.reply_text(
                "❌ *Error:* An unexpected error occurred"
            )
    
    async def ssh_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Handle /ssh command (admin only)."""
        user = update.effective_user
        if not user:
            return
        
        # Check admin permission
        db_user = await db_manager.get_user(user.id)
        if not db_user or not db_user.has_permission('admin'):
            await update.message.reply_text(
                "❌ *Error:* This command is restricted to administrators"
            )
            return
        
        # Parse arguments
        if len(context.args) < 2:
            await update.message.reply_text(
                "❌ *Usage:* `/ssh <host> <command>`\n\n"
                "*Example:* `/ssh myserver uptime`",
                parse_mode=ParseMode.MARKDOWN
            )
            return
        
        host_address = context.args[0]
        command = ' '.join(context.args[1:])
        
        try:
            # Find job with SSH credentials
            jobs = await db_manager.get_host_jobs()
            target_job = None
            
            for job in jobs:
                if (job.host_config.host_address == host_address and 
                    job.host_config.ssh_username and 
                    job.host_config.ssh_password):
                    target_job = job
                    break
            
            if not target_job:
                await update.message.reply_text(
                    f"❌ *Error:* No SSH credentials found for host `{host_address}`\n\n"
                    f"Use `/storecredentials <host> <username> <password>` to store credentials first.",
                    parse_mode=ParseMode.MARKDOWN
                )
                return
            
            # Send typing indicator
            await context.bot.send_chat_action(chat_id=update.effective_chat.id, action="typing")
            
            # Execute SSH command
            success, stdout, stderr = await ssh_manager.execute_ssh_command(
                host=host_address,
                username=target_job.host_config.ssh_username,
                encrypted_password=target_job.host_config.ssh_password,
                command=command,
                port=target_job.host_config.ssh_port
            )
            
            # Format result
            result = formatter.format_ssh_result(success, stdout, stderr)
            
            await update.message.reply_text(
                result,
                parse_mode=ParseMode.MARKDOWN
            )
            
        except Exception as e:
            logger.error(f"Error in ssh command: {e}")
            await update.message.reply_text(
                "❌ *Error:* An unexpected error occurred"
            )
    
    async def storecredentials_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Handle /storecredentials command."""
        user = update.effective_user
        if not user:
            return
        
        args = context.args
        
        if len(args) == 1:
            # Show existing credentials
            host_address = args[0]
            
            try:
                # Find job
                jobs = await db_manager.get_host_jobs(user.id)
                target_job = None
                
                for job in jobs:
                    if job.host_config.host_address == host_address:
                        target_job = job
                        break
                
                if not target_job:
                    await update.message.reply_text(
                        f"❌ *Error:* Host `{host_address}` is not being monitored"
                    )
                    return
                
                if not target_job.host_config.ssh_username:
                    await update.message.reply_text(
                        f"ℹ️ *Info:* No SSH credentials stored for `{host_address}`"
                    )
                    return
                
                # Show credentials
                message = f"🔐 *SSH Credentials for {host_address}*\n\n"
                message += f"*Username:* `{target_job.host_config.ssh_username}`\n"
                message += f"*Port:* `{target_job.host_config.ssh_port}`\n"
                message += f"*Password:* `••••••••` (encrypted)"
                
                await update.message.reply_text(
                    message,
                    parse_mode=ParseMode.MARKDOWN
                )
                
            except Exception as e:
                logger.error(f"Error showing credentials: {e}")
                await update.message.reply_text(
                    "❌ *Error:* An unexpected error occurred"
                )
        
        elif len(args) >= 3:
            # Store new credentials
            host_address = args[0]
            username = args[1]
            password = args[2]
            ssh_port = int(args[3]) if len(args) > 3 else settings.default_ssh_port
            
            try:
                # Find job
                jobs = await db_manager.get_host_jobs(user.id)
                target_job = None
                
                for job in jobs:
                    if job.host_config.host_address == host_address:
                        target_job = job
                        break
                
                if not target_job:
                    await update.message.reply_text(
                        f"❌ *Error:* Host `{host_address}` is not being monitored\n\n"
                        f"Add the host first with `/pingadd {host_address} <interval>`",
                        parse_mode=ParseMode.MARKDOWN
                    )
                    return
                
                # Encrypt password
                encrypted_password = ssh_manager.encrypt_password(password)
                
                # Update job with credentials
                target_job.host_config.ssh_username = username
                target_job.host_config.ssh_password = encrypted_password
                target_job.host_config.ssh_port = ssh_port
                target_job.updated_at = datetime.utcnow()
                
                # Save to database
                await db_manager.save_host_job(target_job)
                
                await update.message.reply_text(
                    f"✅ *SSH Credentials Stored Successfully!*\n\n"
                    f"*Host:* `{host_address}`\n"
                    f"*Username:* `{username}`\n"
                    f"*Port:* `{ssh_port}`\n\n"
                    f"Credentials are encrypted and stored securely.",
                    parse_mode=ParseMode.MARKDOWN
                )
                
            except Exception as e:
                logger.error(f"Error storing credentials: {e}")
                await update.message.reply_text(
                    "❌ *Error:* An unexpected error occurred"
                )
        
        else:
            await update.message.reply_text(
                "❌ *Usage:*\n\n"
                "• `/storecredentials <host>` - Show stored credentials\n"
                "• `/storecredentials <host> <username> <password> [port]` - Store credentials\n\n"
                "*Example:* `/storecredentials myserver admin mypassword 22`",
                parse_mode=ParseMode.MARKDOWN
            )
    
    async def pinginterval_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Handle /pinginterval command."""
        user = update.effective_user
        if not user:
            return
        
        args = context.args
        if len(args) != 2:
            await update.message.reply_text(
                "❌ *Usage:* `/pinginterval <host> <new_interval_seconds>`\n\n"
                "*Example:* `/pinginterval google.com 600`",
                parse_mode=ParseMode.MARKDOWN
            )
            return
        
        host_address = args[0]
        try:
            new_interval = int(args[1])
        except ValueError:
            await update.message.reply_text(
                "❌ *Error:* Interval must be a number"
            )
            return
        
        try:
            # Find job
            jobs = await db_manager.get_host_jobs(user.id)
            target_job = None
            
            for job in jobs:
                if job.host_config.host_address == host_address:
                    target_job = job
                    break
            
            if not target_job:
                await update.message.reply_text(
                    f"❌ *Error:* Host `{host_address}` is not being monitored"
                )
                return
            
            # Update interval
            old_interval = target_job.host_config.interval_seconds
            target_job.host_config.interval_seconds = new_interval
            target_job.updated_at = datetime.utcnow()
            
            # Save to database
            await db_manager.save_host_job(target_job)
            
            await update.message.reply_text(
                f"✅ *Interval Updated Successfully!*\n\n"
                f"*Host:* `{host_address}`\n"
                f"*Old Interval:* `{old_interval}s`\n"
                f"*New Interval:* `{new_interval}s`",
                parse_mode=ParseMode.MARKDOWN
            )
            
        except ValueError as e:
            await update.message.reply_text(
                f"❌ *Error:* {str(e)}"
            )
        except Exception as e:
            logger.error(f"Error in pinginterval command: {e}")
            await update.message.reply_text(
                "❌ *Error:* An unexpected error occurred"
            )
    
    async def changepingport_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Handle /changepingport command."""
        user = update.effective_user
        if not user:
            return
        
        args = context.args
        if len(args) != 2:
            await update.message.reply_text(
                "❌ *Usage:* `/changepingport <host> <new_port>`\n\n"
                "*Example:* `/changepingport google.com 443`",
                parse_mode=ParseMode.MARKDOWN
            )
            return
        
        host_address = args[0]
        try:
            new_port = int(args[1])
        except ValueError:
            await update.message.reply_text(
                "❌ *Error:* Port must be a number"
            )
            return
        
        try:
            # Find job
            jobs = await db_manager.get_host_jobs(user.id)
            target_job = None
            
            for job in jobs:
                if job.host_config.host_address == host_address:
                    target_job = job
                    break
            
            if not target_job:
                await update.message.reply_text(
                    f"❌ *Error:* Host `{host_address}` is not being monitored"
                )
                return
            
            # Update port
            old_port = target_job.host_config.port
            target_job.host_config.port = new_port
            target_job.updated_at = datetime.utcnow()
            
            # Save to database
            await db_manager.save_host_job(target_job)
            
            await update.message.reply_text(
                f"✅ *Port Updated Successfully!*\n\n"
                f"*Host:* `{host_address}`\n"
                f"*Old Port:* `{old_port}`\n"
                f"*New Port:* `{new_port}`",
                parse_mode=ParseMode.MARKDOWN
            )
            
        except ValueError as e:
            await update.message.reply_text(
                f"❌ *Error:* {str(e)}"
            )
        except Exception as e:
            logger.error(f"Error in changepingport command: {e}")
            await update.message.reply_text(
                "❌ *Error:* An unexpected error occurred"
            ) 
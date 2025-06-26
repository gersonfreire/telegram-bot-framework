"""
Message formatting utilities.
"""
import re
from typing import List, Dict, Any
from datetime import datetime
from ..models.host import HostJob, HostStatus


class MessageFormatter:
    """Format messages for Telegram."""
    
    @staticmethod
    def escape_markdown(text: str) -> str:
        """Escape markdown special characters."""
        if not text:
            return text
        
        # Characters that need escaping in markdown
        escape_chars = ['_', '*', '[', ']', '(', ')', '~', '`', '>', '#', '+', '-', '=', '|', '{', '}', '.', '!']
        
        for char in escape_chars:
            text = text.replace(char, f'\\{char}')
        
        return text
    
    @staticmethod
    def format_host_status(status: HostStatus) -> str:
        """Format host status for display."""
        status_icon = "🟢" if status.is_online else "🔴"
        port_icon = "✅" if status.port_open else "❌"
        
        status_text = f"{status_icon} Online" if status.is_online else f"{status_icon} Offline"
        port_text = f"{port_icon} Port {status.port_open}"
        
        response_time = f" ({status.response_time_ms}ms)" if status.response_time_ms else ""
        
        return f"{status_text}{response_time} | {port_text}"
    
    @staticmethod
    def format_host_listing(jobs: List[HostJob], show_all: bool = False) -> str:
        """Format host listing for display."""
        if not jobs:
            return "_No hosts monitored._"
        
        # Header
        if show_all:
            header = "_Monitored Hosts (All Users):_\n"
            header += "`Status | Port | User ID | Interval | Next Check | Host`\n"
        else:
            header = "_Your Monitored Hosts:_\n"
            header += "`Status | Port | Interval | Next Check | Host`\n"
        
        # Format each job
        lines = []
        for job in jobs:
            status = job.host_status
            config = job.host_config
            
            # Status icons
            status_icon = "🟢" if status.is_online else "🔴"
            port_icon = "✅" if status.port_open else "❌"
            
            # Format interval
            interval_text = f"{config.interval_seconds}s"
            
            # Format next check (placeholder for now)
            next_check = "Now"  # TODO: Calculate from job schedule
            
            # Create clickable link
            host_link = f"[{config.host_address}](https://{config.host_address})"
            
            if show_all:
                line = f"{status_icon}{port_icon} `{config.port:<4}` `{job.user_id:<8}` `{interval_text:<8}` `{next_check}` {host_link}"
            else:
                line = f"{status_icon}{port_icon} `{config.port:<4}` `{interval_text:<8}` `{next_check}` {host_link}"
            
            lines.append(line)
        
        return header + "\n".join(lines)
    
    @staticmethod
    def format_failures_list(jobs: List[HostJob]) -> str:
        """Format failures list for display."""
        if not jobs:
            return "_No hosts with failures._"
        
        header = "_Host Failures:_\n"
        header += "`Last Failure | Host | Status`\n"
        
        lines = []
        for job in jobs:
            status = job.host_status
            config = job.host_config
            
            if status.last_failure:
                failure_time = status.last_failure.strftime("%Y-%m-%d %H:%M")
                status_text = "Offline" if not status.is_online else "Port Closed"
                host_link = f"[{config.host_address}](https://{config.host_address})"
                
                line = f"`{failure_time}` {host_link} - {status_text}"
                lines.append(line)
        
        if not lines:
            return "_No recent failures._"
        
        return header + "\n".join(lines)
    
    @staticmethod
    def format_ssh_result(success: bool, stdout: str, stderr: str) -> str:
        """Format SSH command result."""
        if success:
            result = "✅ *SSH Command Executed Successfully*\n\n"
            if stdout:
                result += f"*Output:*\n```\n{stdout}\n```"
        else:
            result = "❌ *SSH Command Failed*\n\n"
            if stderr:
                result += f"*Error:*\n```\n{stderr}\n```"
        
        return result
    
    @staticmethod
    def format_help_message(is_admin: bool = False) -> str:
        """Format help message."""
        help_text = """
🤖 *Modern Host Watch Bot*

*Basic Commands:*
• `/pingadd <host> <interval>` - Add host to monitoring
• `/pingdelete <host>` - Remove host from monitoring  
• `/pinglist` - List your monitored hosts
• `/pinghost <host>` - Manual ping check
• `/pinghostport <host> <port>` - Check specific port
• `/listfailures` - Show recent failures

*Configuration:*
• `/pinginterval <host> <seconds>` - Change check interval
• `/changepingport <host> <port>` - Change monitored port
• `/storecredentials <host> <user> <pass> [port]` - Store SSH credentials
• `/pinglog` - Toggle success notifications

*SSH Commands (Admin only):*
• `/ssh <host> <command>` - Execute SSH command
• `/exec <command>` - Execute local command

*Examples:*
• `/pingadd google.com 300` - Monitor Google every 5 minutes
• `/pinghostport example.com 443` - Check HTTPS port
• `/ssh myserver uptime` - Check server uptime
        """
        
        if is_admin:
            help_text += "\n\n👑 *You have admin privileges*"
        
        return help_text
    
    @staticmethod
    def format_error_message(error: str) -> str:
        """Format error message."""
        return f"❌ *Error:* {MessageFormatter.escape_markdown(error)}"
    
    @staticmethod
    def format_success_message(message: str) -> str:
        """Format success message."""
        return f"✅ {MessageFormatter.escape_markdown(message)}"
    
    @staticmethod
    def format_warning_message(message: str) -> str:
        """Format warning message."""
        return f"⚠️ {MessageFormatter.escape_markdown(message)}"


# Global instance
formatter = MessageFormatter() 
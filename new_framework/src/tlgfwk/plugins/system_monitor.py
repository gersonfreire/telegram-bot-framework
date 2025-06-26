"""
System Monitor Plugin

This plugin provides system monitoring capabilities for the Telegram bot.
Monitors CPU, memory, disk usage and sends alerts when thresholds are exceeded.
"""

import psutil
import platform
import time
from datetime import datetime, timedelta
from typing import Dict, Any, Optional

from telegram import Update
from telegram.ext import ContextTypes

from ..base import PluginBase
from ...core.decorators import command, admin_required
from ...utils.logger import get_logger


class SystemMonitorPlugin(PluginBase):
    """System monitoring plugin for server health monitoring."""
    
    def __init__(self, bot):
        super().__init__(bot)
        
        # Plugin metadata
        self.name = "System Monitor"
        self.version = "1.0.0"
        self.description = "Monitor system resources and send alerts"
        self.author = "Telegram Bot Framework"
        self.dependencies = []
        
        # Configuration
        self.config = {
            'cpu_threshold': 80.0,
            'memory_threshold': 85.0,
            'disk_threshold': 90.0,
            'check_interval': 300,  # 5 minutes
            'alert_cooldown': 1800,  # 30 minutes
            'enabled_alerts': True
        }
        
        # State
        self.last_alerts = {}
        self.monitoring_job_id = None
        
        self.logger = get_logger(__name__)
    
    def initialize(self):
        """Initialize the plugin."""
        super().initialize()
        
        # Start monitoring job if scheduler is available
        if hasattr(self.bot, 'scheduler') and self.config.get('enabled_alerts'):
            self.start_monitoring()
        
        self.logger.info("System Monitor plugin initialized")
    
    def cleanup(self):
        """Clean up the plugin."""
        super().cleanup()
        
        # Stop monitoring job
        if self.monitoring_job_id and hasattr(self.bot, 'scheduler'):
            self.bot.scheduler.remove_job(self.monitoring_job_id)
        
        self.logger.info("System Monitor plugin cleaned up")
    
    def start_monitoring(self):
        """Start system monitoring job."""
        if hasattr(self.bot, 'scheduler'):
            self.monitoring_job_id = self.bot.scheduler.add_job(
                func=self.check_system_health,
                trigger='interval',
                name='system_monitor',
                description='Monitor system resources',
                seconds=self.config['check_interval']
            )
            self.logger.info("System monitoring started")
    
    def stop_monitoring(self):
        """Stop system monitoring job."""
        if self.monitoring_job_id and hasattr(self.bot, 'scheduler'):
            self.bot.scheduler.remove_job(self.monitoring_job_id)
            self.monitoring_job_id = None
            self.logger.info("System monitoring stopped")
    
    @command(name="sysinfo", description="Get system information")
    @admin_required
    async def system_info_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Get comprehensive system information."""
        try:
            info = self.get_system_info()
            
            message = "🖥️ **System Information**\n\n"
            
            # System details
            message += f"**System:** {info['system']['platform']} {info['system']['release']}\n"
            message += f"**Hostname:** {info['system']['hostname']}\n"
            message += f"**Uptime:** {info['system']['uptime']}\n\n"
            
            # CPU information
            message += f"**CPU Usage:** {info['cpu']['usage']:.1f}%\n"
            message += f"**CPU Cores:** {info['cpu']['cores']} ({info['cpu']['physical_cores']} physical)\n"
            message += f"**CPU Frequency:** {info['cpu']['frequency']:.0f} MHz\n\n"
            
            # Memory information
            message += f"**Memory Usage:** {info['memory']['usage']:.1f}%\n"
            message += f"**Memory Used:** {info['memory']['used_gb']:.1f} GB / {info['memory']['total_gb']:.1f} GB\n"
            message += f"**Memory Available:** {info['memory']['available_gb']:.1f} GB\n\n"
            
            # Disk information
            message += f"**Disk Usage:** {info['disk']['usage']:.1f}%\n"
            message += f"**Disk Used:** {info['disk']['used_gb']:.1f} GB / {info['disk']['total_gb']:.1f} GB\n"
            message += f"**Disk Free:** {info['disk']['free_gb']:.1f} GB\n\n"
            
            # Network information
            if info.get('network'):
                message += f"**Network Sent:** {info['network']['sent_gb']:.2f} GB\n"
                message += f"**Network Received:** {info['network']['received_gb']:.2f} GB\n\n"
            
            # Process information
            message += f"**Active Processes:** {info['processes']['count']}\n"
            message += f"**Bot Process PID:** {info['processes']['bot_pid']}\n"
            message += f"**Bot Memory:** {info['processes']['bot_memory_mb']:.1f} MB\n"
            
            await update.message.reply_text(message, parse_mode='Markdown')
            
        except Exception as e:
            self.logger.error(f"Error getting system info: {e}")
            await update.message.reply_text(f"❌ Error getting system information: {e}")
    
    @command(name="monitoring", description="Control system monitoring")
    @admin_required
    async def monitoring_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Control system monitoring."""
        try:
            args = context.args if context.args else []
            
            if not args:
                # Show monitoring status
                status = "enabled" if self.monitoring_job_id else "disabled"
                message = f"🔍 **System Monitoring Status:** {status}\n\n"
                
                message += "**Configuration:**\n"
                message += f"• CPU Threshold: {self.config['cpu_threshold']:.1f}%\n"
                message += f"• Memory Threshold: {self.config['memory_threshold']:.1f}%\n"
                message += f"• Disk Threshold: {self.config['disk_threshold']:.1f}%\n"
                message += f"• Check Interval: {self.config['check_interval']} seconds\n"
                message += f"• Alert Cooldown: {self.config['alert_cooldown']} seconds\n"
                
                message += "\n**Commands:**\n"
                message += "• `/monitoring start` - Start monitoring\n"
                message += "• `/monitoring stop` - Stop monitoring\n"
                message += "• `/monitoring check` - Manual health check\n"
                message += "• `/monitoring thresholds` - Show thresholds\n"
                
                await update.message.reply_text(message, parse_mode='Markdown')
                return
            
            command = args[0].lower()
            
            if command == "start":
                if self.monitoring_job_id:
                    await update.message.reply_text("⚠️ Monitoring is already running")
                else:
                    self.start_monitoring()
                    await update.message.reply_text("✅ System monitoring started")
            
            elif command == "stop":
                if not self.monitoring_job_id:
                    await update.message.reply_text("⚠️ Monitoring is not running")
                else:
                    self.stop_monitoring()
                    await update.message.reply_text("✅ System monitoring stopped")
            
            elif command == "check":
                alerts = self.check_system_health()
                if alerts:
                    message = "⚠️ **System Health Issues Found:**\n\n"
                    for alert in alerts:
                        message += f"• {alert}\n"
                else:
                    message = "✅ **System Health Check:** All systems normal"
                
                await update.message.reply_text(message, parse_mode='Markdown')
            
            elif command == "thresholds":
                message = "🎛️ **Alert Thresholds:**\n\n"
                message += f"• **CPU:** {self.config['cpu_threshold']:.1f}%\n"
                message += f"• **Memory:** {self.config['memory_threshold']:.1f}%\n"
                message += f"• **Disk:** {self.config['disk_threshold']:.1f}%\n"
                
                await update.message.reply_text(message, parse_mode='Markdown')
            
            else:
                await update.message.reply_text("❌ Unknown command. Use: start, stop, check, or thresholds")
                
        except Exception as e:
            self.logger.error(f"Error in monitoring command: {e}")
            await update.message.reply_text(f"❌ Error: {e}")
    
    @command(name="top", description="Show top processes")
    @admin_required
    async def top_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Show top processes by CPU and memory usage."""
        try:
            limit = 10
            if context.args and context.args[0].isdigit():
                limit = min(int(context.args[0]), 20)
            
            processes = []
            for proc in psutil.process_iter(['pid', 'name', 'cpu_percent', 'memory_percent']):
                try:
                    pinfo = proc.info
                    processes.append(pinfo)
                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    pass
            
            # Sort by CPU usage
            processes.sort(key=lambda x: x['cpu_percent'] or 0, reverse=True)
            
            message = f"📊 **Top {limit} Processes (by CPU)**\n\n"
            message += "```\n"
            message += f"{'PID':<8} {'CPU%':<6} {'MEM%':<6} {'NAME':<20}\n"
            message += "-" * 50 + "\n"
            
            for i, proc in enumerate(processes[:limit]):
                pid = proc['pid']
                cpu = proc['cpu_percent'] or 0
                mem = proc['memory_percent'] or 0
                name = (proc['name'] or 'Unknown')[:20]
                
                message += f"{pid:<8} {cpu:<6.1f} {mem:<6.1f} {name:<20}\n"
            
            message += "```"
            
            await update.message.reply_text(message, parse_mode='Markdown')
            
        except Exception as e:
            self.logger.error(f"Error getting top processes: {e}")
            await update.message.reply_text(f"❌ Error getting process list: {e}")
    
    def get_system_info(self) -> Dict[str, Any]:
        """Get comprehensive system information."""
        # System information
        system_info = {
            'platform': platform.system(),
            'release': platform.release(),
            'version': platform.version(),
            'hostname': platform.node(),
            'uptime': self._get_uptime()
        }
        
        # CPU information
        cpu_info = {
            'usage': psutil.cpu_percent(interval=1),
            'cores': psutil.cpu_count(),
            'physical_cores': psutil.cpu_count(logical=False),
            'frequency': psutil.cpu_freq().current if psutil.cpu_freq() else 0
        }
        
        # Memory information
        memory = psutil.virtual_memory()
        memory_info = {
            'total_gb': memory.total / (1024**3),
            'used_gb': memory.used / (1024**3),
            'available_gb': memory.available / (1024**3),
            'usage': memory.percent
        }
        
        # Disk information
        disk = psutil.disk_usage('/')
        disk_info = {
            'total_gb': disk.total / (1024**3),
            'used_gb': disk.used / (1024**3),
            'free_gb': disk.free / (1024**3),
            'usage': (disk.used / disk.total) * 100
        }
        
        # Network information
        network = psutil.net_io_counters()
        network_info = {
            'sent_gb': network.bytes_sent / (1024**3),
            'received_gb': network.bytes_recv / (1024**3)
        } if network else {}
        
        # Process information
        import os
        current_process = psutil.Process(os.getpid())
        process_info = {
            'count': len(psutil.pids()),
            'bot_pid': os.getpid(),
            'bot_memory_mb': current_process.memory_info().rss / (1024**2)
        }
        
        return {
            'system': system_info,
            'cpu': cpu_info,
            'memory': memory_info,
            'disk': disk_info,
            'network': network_info,
            'processes': process_info,
            'timestamp': datetime.now().isoformat()
        }
    
    def check_system_health(self) -> list:
        """Check system health and return list of alerts."""
        alerts = []
        now = datetime.now()
        
        try:
            # Get current system metrics
            cpu_usage = psutil.cpu_percent(interval=1)
            memory = psutil.virtual_memory()
            disk = psutil.disk_usage('/')
            disk_usage = (disk.used / disk.total) * 100
            
            # Check CPU threshold
            if cpu_usage > self.config['cpu_threshold']:
                alert_key = 'cpu'
                if self._should_send_alert(alert_key, now):
                    alert_msg = f"🚨 High CPU usage: {cpu_usage:.1f}% (threshold: {self.config['cpu_threshold']}%)"
                    alerts.append(alert_msg)
                    self.last_alerts[alert_key] = now
                    self._send_alert_to_admins(alert_msg)
            
            # Check memory threshold
            if memory.percent > self.config['memory_threshold']:
                alert_key = 'memory'
                if self._should_send_alert(alert_key, now):
                    alert_msg = f"🚨 High memory usage: {memory.percent:.1f}% (threshold: {self.config['memory_threshold']}%)"
                    alerts.append(alert_msg)
                    self.last_alerts[alert_key] = now
                    self._send_alert_to_admins(alert_msg)
            
            # Check disk threshold
            if disk_usage > self.config['disk_threshold']:
                alert_key = 'disk'
                if self._should_send_alert(alert_key, now):
                    alert_msg = f"🚨 High disk usage: {disk_usage:.1f}% (threshold: {self.config['disk_threshold']}%)"
                    alerts.append(alert_msg)
                    self.last_alerts[alert_key] = now
                    self._send_alert_to_admins(alert_msg)
            
        except Exception as e:
            self.logger.error(f"Error checking system health: {e}")
            error_msg = f"❌ System health check failed: {e}"
            alerts.append(error_msg)
            self._send_alert_to_admins(error_msg)
        
        return alerts
    
    def _should_send_alert(self, alert_key: str, now: datetime) -> bool:
        """Check if enough time has passed since last alert."""
        if alert_key not in self.last_alerts:
            return True
        
        last_alert = self.last_alerts[alert_key]
        cooldown = timedelta(seconds=self.config['alert_cooldown'])
        
        return now - last_alert > cooldown
    
    def _send_alert_to_admins(self, message: str):
        """Send alert message to admin users."""
        try:
            if hasattr(self.bot, 'send_admin_message'):
                # Use bot's method if available
                self.bot.send_admin_message(message)
            else:
                # Fallback: log the alert
                self.logger.warning(f"ALERT: {message}")
        except Exception as e:
            self.logger.error(f"Failed to send alert to admins: {e}")
    
    def _get_uptime(self) -> str:
        """Get system uptime as a formatted string."""
        try:
            uptime_seconds = time.time() - psutil.boot_time()
            uptime = timedelta(seconds=int(uptime_seconds))
            
            days = uptime.days
            hours, remainder = divmod(uptime.seconds, 3600)
            minutes, _ = divmod(remainder, 60)
            
            if days > 0:
                return f"{days}d {hours}h {minutes}m"
            elif hours > 0:
                return f"{hours}h {minutes}m"
            else:
                return f"{minutes}m"
                
        except Exception:
            return "Unknown"
    
    def get_help_text(self) -> str:
        """Get plugin help text."""
        return """
🖥️ **System Monitor Plugin**

Monitor server resources and get alerts when thresholds are exceeded.

**Commands:**
• `/sysinfo` - Get comprehensive system information
• `/monitoring` - Control monitoring settings and status
• `/top [limit]` - Show top processes by CPU usage

**Features:**
• Real-time CPU, memory, and disk monitoring
• Configurable alert thresholds
• Automatic alerts to administrators
• Process monitoring and top processes view
• System uptime and network statistics

**Configuration:**
The plugin monitors system resources at regular intervals and sends alerts when usage exceeds configured thresholds. Alert cooldown prevents spam notifications.
"""


# Export plugin class
__all__ = ['SystemMonitorPlugin']

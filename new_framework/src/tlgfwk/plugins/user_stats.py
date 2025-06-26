"""
User Statistics Plugin

This plugin provides user statistics and analytics for the Telegram bot.
Tracks user activity, command usage, and generates reports.
"""

import json
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional
from collections import defaultdict, Counter
import sqlite3
import os

from telegram import Update
from telegram.ext import ContextTypes

from .base import PluginBase
from ..core.decorators import command, admin_required
from ..utils.logger import Logger


class UserStatsPlugin(PluginBase):
    """User statistics and analytics plugin."""
    
    def __init__(self, bot):
        super().__init__(bot)
        
        # Plugin metadata
        self.name = "User Statistics"
        self.version = "1.0.0"
        self.description = "Track user activity and generate statistics"
        self.author = "Telegram Bot Framework"
        self.dependencies = []
        
        # Configuration
        self.config = {
            'db_path': 'user_stats.db',
            'track_commands': True,
            'track_messages': True,
            'retention_days': 90,
            'enable_reports': True
        }
        
        self.logger = Logger(__name__)
        
        # Initialize database
        self._init_database()
    
    def initialize(self):
        """Initialize the plugin."""
        super().initialize()
        
        # Hook into bot events if possible
        if hasattr(self.bot, 'add_message_handler'):
            self.bot.add_message_handler(self._track_message)
        
        # Schedule cleanup job
        if hasattr(self.bot, 'scheduler'):
            self.bot.scheduler.add_job(
                func=self._cleanup_old_data,
                trigger='cron',
                name='user_stats_cleanup',
                description='Clean up old user statistics',
                hour=2,  # Run at 2 AM daily
                minute=0
            )
        
        self.logger.info("User Statistics plugin initialized")
    
    def cleanup(self):
        """Clean up the plugin."""
        super().cleanup()
        self.logger.info("User Statistics plugin cleaned up")
    
    def _init_database(self):
        """Initialize the SQLite database for statistics."""
        try:
            db_path = self.config['db_path']
            
            conn = sqlite3.connect(db_path)
            cursor = conn.cursor()
            
            # Create tables
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS user_activity (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER NOT NULL,
                    username TEXT,
                    first_name TEXT,
                    last_name TEXT,
                    activity_type TEXT NOT NULL,
                    command TEXT,
                    chat_id INTEGER,
                    chat_type TEXT,
                    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                    metadata TEXT
                )
            ''')
            
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS daily_stats (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER NOT NULL,
                    date DATE NOT NULL,
                    total_messages INTEGER DEFAULT 0,
                    total_commands INTEGER DEFAULT 0,
                    unique_commands INTEGER DEFAULT 0,
                    first_seen DATETIME,
                    last_seen DATETIME,
                    UNIQUE(user_id, date)
                )
            ''')
            
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS command_stats (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    command TEXT NOT NULL,
                    user_id INTEGER NOT NULL,
                    date DATE NOT NULL,
                    count INTEGER DEFAULT 1,
                    UNIQUE(command, user_id, date)
                )
            ''')
            
            # Create indexes
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_user_activity_user_id ON user_activity(user_id)')
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_user_activity_timestamp ON user_activity(timestamp)')
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_daily_stats_date ON daily_stats(date)')
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_command_stats_command ON command_stats(command)')
            
            conn.commit()
            conn.close()
            
            self.logger.info(f"User statistics database initialized: {db_path}")
            
        except Exception as e:
            self.logger.error(f"Failed to initialize statistics database: {e}")
    
    async def _track_message(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Track user message activity."""
        if not self.config['track_messages']:
            return
        
        try:
            user = update.effective_user
            chat = update.effective_chat
            message = update.message
            
            if not user:
                return
            
            activity_type = 'command' if message.text and message.text.startswith('/') else 'message'
            command = None
            
            if activity_type == 'command':
                command = message.text.split()[0][1:]  # Remove '/' prefix
            
            self._record_activity(
                user_id=user.id,
                username=user.username,
                first_name=user.first_name,
                last_name=user.last_name,
                activity_type=activity_type,
                command=command,
                chat_id=chat.id,
                chat_type=chat.type
            )
            
        except Exception as e:
            self.logger.error(f"Error tracking message: {e}")
    
    def _record_activity(
        self,
        user_id: int,
        username: Optional[str],
        first_name: Optional[str],
        last_name: Optional[str],
        activity_type: str,
        command: Optional[str] = None,
        chat_id: Optional[int] = None,
        chat_type: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None
    ):
        """Record user activity in the database."""
        try:
            conn = sqlite3.connect(self.config['db_path'])
            cursor = conn.cursor()
            
            # Insert activity record
            cursor.execute('''
                INSERT INTO user_activity 
                (user_id, username, first_name, last_name, activity_type, command, chat_id, chat_type, metadata)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                user_id, username, first_name, last_name, activity_type,
                command, chat_id, chat_type,
                json.dumps(metadata) if metadata else None
            ))
            
            # Update daily stats
            today = datetime.now().date()
            now = datetime.now()
            
            cursor.execute('''
                INSERT OR REPLACE INTO daily_stats 
                (user_id, date, total_messages, total_commands, unique_commands, first_seen, last_seen)
                VALUES (
                    ?, ?, 
                    COALESCE((SELECT total_messages FROM daily_stats WHERE user_id = ? AND date = ?), 0) + 
                    CASE WHEN ? = 'message' THEN 1 ELSE 0 END,
                    COALESCE((SELECT total_commands FROM daily_stats WHERE user_id = ? AND date = ?), 0) + 
                    CASE WHEN ? = 'command' THEN 1 ELSE 0 END,
                    (SELECT COUNT(DISTINCT command) FROM user_activity 
                     WHERE user_id = ? AND DATE(timestamp) = ? AND activity_type = 'command'),
                    COALESCE((SELECT first_seen FROM daily_stats WHERE user_id = ? AND date = ?), ?),
                    ?
                )
            ''', (
                user_id, today, user_id, today, activity_type,
                user_id, today, activity_type, user_id, today,
                user_id, today, now, now
            ))
            
            # Update command stats
            if command:
                cursor.execute('''
                    INSERT OR REPLACE INTO command_stats (command, user_id, date, count)
                    VALUES (
                        ?, ?, ?,
                        COALESCE((SELECT count FROM command_stats WHERE command = ? AND user_id = ? AND date = ?), 0) + 1
                    )
                ''', (command, user_id, today, command, user_id, today))
            
            conn.commit()
            conn.close()
            
        except Exception as e:
            self.logger.error(f"Error recording activity: {e}")
    
    @command(name="stats", description="Show user statistics")
    async def stats_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Show user statistics."""
        try:
            user_id = update.effective_user.id
            args = context.args if context.args else []
            
            # Check if admin wants to see other user's stats
            if args and update.effective_user.id in self.bot.config.admin_user_ids:
                try:
                    target_user_id = int(args[0])
                    user_id = target_user_id
                except ValueError:
                    await update.message.reply_text("❌ Invalid user ID")
                    return
            
            stats = self._get_user_stats(user_id)
            
            if not stats:
                await update.message.reply_text("📊 No statistics available for this user.")
                return
            
            message = f"📊 **User Statistics**\n\n"
            message += f"**User ID:** {user_id}\n"
            message += f"**Total Messages:** {stats['total_messages']}\n"
            message += f"**Total Commands:** {stats['total_commands']}\n"
            message += f"**Unique Commands:** {stats['unique_commands']}\n"
            message += f"**First Seen:** {stats['first_seen']}\n"
            message += f"**Last Seen:** {stats['last_seen']}\n"
            message += f"**Active Days:** {stats['active_days']}\n\n"
            
            # Top commands
            if stats['top_commands']:
                message += "**Top Commands:**\n"
                for cmd, count in stats['top_commands'][:5]:
                    message += f"• `/{cmd}`: {count} times\n"
                message += "\n"
            
            # Recent activity
            message += "**Last 7 Days:**\n"
            for day_stats in stats['recent_activity'][:7]:
                date = day_stats['date']
                messages = day_stats['total_messages']
                commands = day_stats['total_commands']
                message += f"• {date}: {messages} messages, {commands} commands\n"
            
            await update.message.reply_text(message, parse_mode='Markdown')
            
        except Exception as e:
            self.logger.error(f"Error in stats command: {e}")
            await update.message.reply_text(f"❌ Error retrieving statistics: {e}")
    
    @command(name="globalstats", description="Show global bot statistics")
    @admin_required
    async def global_stats_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Show global bot statistics."""
        try:
            stats = self._get_global_stats()
            
            message = "🌍 **Global Bot Statistics**\n\n"
            
            # Overall stats
            message += f"**Total Users:** {stats['total_users']}\n"
            message += f"**Active Users (7d):** {stats['active_users_7d']}\n"
            message += f"**Active Users (30d):** {stats['active_users_30d']}\n"
            message += f"**Total Messages:** {stats['total_messages']}\n"
            message += f"**Total Commands:** {stats['total_commands']}\n\n"
            
            # Top commands globally
            if stats['top_commands']:
                message += "**Most Used Commands:**\n"
                for cmd, count in stats['top_commands'][:10]:
                    message += f"• `/{cmd}`: {count} times\n"
                message += "\n"
            
            # Daily activity (last 7 days)
            message += "**Daily Activity (Last 7 Days):**\n"
            for day_stats in stats['daily_activity'][:7]:
                date = day_stats['date']
                users = day_stats['active_users']
                messages = day_stats['total_messages']
                commands = day_stats['total_commands']
                message += f"• {date}: {users} users, {messages} messages, {commands} commands\n"
            
            await update.message.reply_text(message, parse_mode='Markdown')
            
        except Exception as e:
            self.logger.error(f"Error in global stats command: {e}")
            await update.message.reply_text(f"❌ Error retrieving global statistics: {e}")
    
    @command(name="userreport", description="Generate detailed user report")
    @admin_required
    async def user_report_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Generate a detailed user activity report."""
        try:
            if not context.args:
                await update.message.reply_text("❌ Please provide a user ID")
                return
            
            try:
                user_id = int(context.args[0])
            except ValueError:
                await update.message.reply_text("❌ Invalid user ID")
                return
            
            report = self._generate_user_report(user_id)
            
            if not report:
                await update.message.reply_text("📊 No data available for this user.")
                return
            
            # Create detailed report
            message = f"📋 **Detailed User Report**\n\n"
            message += f"**User ID:** {user_id}\n"
            message += f"**Username:** @{report['username'] or 'N/A'}\n"
            message += f"**Name:** {report['full_name'] or 'N/A'}\n\n"
            
            message += "**Activity Summary:**\n"
            message += f"• Total Messages: {report['total_messages']}\n"
            message += f"• Total Commands: {report['total_commands']}\n"
            message += f"• Unique Commands: {len(report['command_usage'])}\n"
            message += f"• First Seen: {report['first_seen']}\n"
            message += f"• Last Seen: {report['last_seen']}\n"
            message += f"• Active Days: {report['active_days']}\n\n"
            
            # Command usage breakdown
            if report['command_usage']:
                message += "**Command Usage:**\n"
                for cmd, count in sorted(report['command_usage'].items(), key=lambda x: x[1], reverse=True)[:10]:
                    message += f"• `/{cmd}`: {count} times\n"
                message += "\n"
            
            # Activity patterns
            message += "**Activity Patterns:**\n"
            if report['hourly_activity']:
                peak_hour = max(report['hourly_activity'].items(), key=lambda x: x[1])
                message += f"• Peak Activity Hour: {peak_hour[0]}:00 ({peak_hour[1]} activities)\n"
            
            if report['daily_activity']:
                most_active_day = max(report['daily_activity'], key=lambda x: x['total_activity'])
                message += f"• Most Active Day: {most_active_day['date']} ({most_active_day['total_activity']} activities)\n"
            
            await update.message.reply_text(message, parse_mode='Markdown')
            
        except Exception as e:
            self.logger.error(f"Error in user report command: {e}")
            await update.message.reply_text(f"❌ Error generating user report: {e}")
    
    def _get_user_stats(self, user_id: int) -> Optional[Dict[str, Any]]:
        """Get statistics for a specific user."""
        try:
            conn = sqlite3.connect(self.config['db_path'])
            cursor = conn.cursor()
            
            # Get overall stats
            cursor.execute('''
                SELECT 
                    SUM(total_messages) as total_messages,
                    SUM(total_commands) as total_commands,
                    MAX(unique_commands) as unique_commands,
                    MIN(first_seen) as first_seen,
                    MAX(last_seen) as last_seen,
                    COUNT(DISTINCT date) as active_days
                FROM daily_stats 
                WHERE user_id = ?
            ''', (user_id,))
            
            row = cursor.fetchone()
            if not row or not row[0]:
                return None
            
            stats = {
                'total_messages': row[0] or 0,
                'total_commands': row[1] or 0,
                'unique_commands': row[2] or 0,
                'first_seen': row[3],
                'last_seen': row[4],
                'active_days': row[5] or 0
            }
            
            # Get top commands
            cursor.execute('''
                SELECT command, SUM(count) as total_count
                FROM command_stats 
                WHERE user_id = ?
                GROUP BY command
                ORDER BY total_count DESC
                LIMIT 10
            ''', (user_id,))
            
            stats['top_commands'] = cursor.fetchall()
            
            # Get recent activity (last 7 days)
            cursor.execute('''
                SELECT date, total_messages, total_commands
                FROM daily_stats 
                WHERE user_id = ?
                ORDER BY date DESC
                LIMIT 7
            ''', (user_id,))
            
            recent_rows = cursor.fetchall()
            stats['recent_activity'] = [
                {
                    'date': row[0],
                    'total_messages': row[1],
                    'total_commands': row[2]
                }
                for row in recent_rows
            ]
            
            conn.close()
            return stats
            
        except Exception as e:
            self.logger.error(f"Error getting user stats: {e}")
            return None
    
    def _get_global_stats(self) -> Dict[str, Any]:
        """Get global bot statistics."""
        try:
            conn = sqlite3.connect(self.config['db_path'])
            cursor = conn.cursor()
            
            # Overall stats
            cursor.execute('''
                SELECT 
                    COUNT(DISTINCT user_id) as total_users,
                    SUM(total_messages) as total_messages,
                    SUM(total_commands) as total_commands
                FROM daily_stats
            ''')
            
            row = cursor.fetchone()
            stats = {
                'total_users': row[0] or 0,
                'total_messages': row[1] or 0,
                'total_commands': row[2] or 0
            }
            
            # Active users in last 7 days
            cursor.execute('''
                SELECT COUNT(DISTINCT user_id)
                FROM daily_stats
                WHERE date >= date('now', '-7 days')
            ''')
            stats['active_users_7d'] = cursor.fetchone()[0] or 0
            
            # Active users in last 30 days
            cursor.execute('''
                SELECT COUNT(DISTINCT user_id)
                FROM daily_stats
                WHERE date >= date('now', '-30 days')
            ''')
            stats['active_users_30d'] = cursor.fetchone()[0] or 0
            
            # Top commands globally
            cursor.execute('''
                SELECT command, SUM(count) as total_count
                FROM command_stats
                GROUP BY command
                ORDER BY total_count DESC
                LIMIT 10
            ''')
            stats['top_commands'] = cursor.fetchall()
            
            # Daily activity for last 7 days
            cursor.execute('''
                SELECT 
                    date,
                    COUNT(DISTINCT user_id) as active_users,
                    SUM(total_messages) as total_messages,
                    SUM(total_commands) as total_commands
                FROM daily_stats
                WHERE date >= date('now', '-7 days')
                GROUP BY date
                ORDER BY date DESC
            ''')
            
            daily_rows = cursor.fetchall()
            stats['daily_activity'] = [
                {
                    'date': row[0],
                    'active_users': row[1],
                    'total_messages': row[2],
                    'total_commands': row[3]
                }
                for row in daily_rows
            ]
            
            conn.close()
            return stats
            
        except Exception as e:
            self.logger.error(f"Error getting global stats: {e}")
            return {}
    
    def _generate_user_report(self, user_id: int) -> Optional[Dict[str, Any]]:
        """Generate a detailed user report."""
        try:
            conn = sqlite3.connect(self.config['db_path'])
            cursor = conn.cursor()
            
            # Get basic user info
            cursor.execute('''
                SELECT username, first_name, last_name
                FROM user_activity
                WHERE user_id = ?
                ORDER BY timestamp DESC
                LIMIT 1
            ''', (user_id,))
            
            user_row = cursor.fetchone()
            if not user_row:
                return None
            
            username, first_name, last_name = user_row
            full_name = f"{first_name or ''} {last_name or ''}".strip()
            
            # Get activity summary
            cursor.execute('''
                SELECT 
                    SUM(total_messages) as total_messages,
                    SUM(total_commands) as total_commands,
                    MIN(first_seen) as first_seen,
                    MAX(last_seen) as last_seen,
                    COUNT(DISTINCT date) as active_days
                FROM daily_stats 
                WHERE user_id = ?
            ''', (user_id,))
            
            activity_row = cursor.fetchone()
            
            # Get command usage
            cursor.execute('''
                SELECT command, SUM(count) as total_count
                FROM command_stats 
                WHERE user_id = ?
                GROUP BY command
            ''', (user_id,))
            
            command_usage = dict(cursor.fetchall())
            
            # Get hourly activity pattern
            cursor.execute('''
                SELECT 
                    CAST(strftime('%H', timestamp) AS INTEGER) as hour,
                    COUNT(*) as activity_count
                FROM user_activity
                WHERE user_id = ?
                GROUP BY hour
            ''', (user_id,))
            
            hourly_activity = dict(cursor.fetchall())
            
            # Get daily activity for last 30 days
            cursor.execute('''
                SELECT 
                    date,
                    total_messages + total_commands as total_activity
                FROM daily_stats
                WHERE user_id = ? AND date >= date('now', '-30 days')
                ORDER BY date DESC
            ''', (user_id,))
            
            daily_rows = cursor.fetchall()
            daily_activity = [
                {'date': row[0], 'total_activity': row[1]}
                for row in daily_rows
            ]
            
            report = {
                'username': username,
                'full_name': full_name,
                'total_messages': activity_row[0] or 0,
                'total_commands': activity_row[1] or 0,
                'first_seen': activity_row[2],
                'last_seen': activity_row[3],
                'active_days': activity_row[4] or 0,
                'command_usage': command_usage,
                'hourly_activity': hourly_activity,
                'daily_activity': daily_activity
            }
            
            conn.close()
            return report
            
        except Exception as e:
            self.logger.error(f"Error generating user report: {e}")
            return None
    
    def _cleanup_old_data(self):
        """Clean up old statistics data based on retention policy."""
        try:
            if self.config['retention_days'] <= 0:
                return  # Retention disabled
            
            cutoff_date = datetime.now() - timedelta(days=self.config['retention_days'])
            
            conn = sqlite3.connect(self.config['db_path'])
            cursor = conn.cursor()
            
            # Delete old activity records
            cursor.execute('''
                DELETE FROM user_activity 
                WHERE timestamp < ?
            ''', (cutoff_date,))
            
            activity_deleted = cursor.rowcount
            
            # Delete old daily stats
            cursor.execute('''
                DELETE FROM daily_stats 
                WHERE date < ?
            ''', (cutoff_date.date(),))
            
            daily_deleted = cursor.rowcount
            
            # Delete old command stats
            cursor.execute('''
                DELETE FROM command_stats 
                WHERE date < ?
            ''', (cutoff_date.date(),))
            
            command_deleted = cursor.rowcount
            
            conn.commit()
            conn.close()
            
            total_deleted = activity_deleted + daily_deleted + command_deleted
            if total_deleted > 0:
                self.logger.info(f"Cleaned up {total_deleted} old statistics records")
            
        except Exception as e:
            self.logger.error(f"Error cleaning up old data: {e}")
    
    def get_help_text(self) -> str:
        """Get plugin help text."""
        return """
📊 **User Statistics Plugin**

Track user activity and generate comprehensive analytics reports.

**User Commands:**
• `/stats` - Show your personal statistics

**Admin Commands:**
• `/stats [user_id]` - Show statistics for specific user
• `/globalstats` - Show global bot statistics
• `/userreport [user_id]` - Generate detailed user report

**Features:**
• Track message and command usage
• Daily activity summaries
• Command usage analytics
• Activity pattern analysis
• Data retention management
• Comprehensive reporting

**Tracked Data:**
• Total messages and commands
• Command usage frequency
• Activity timestamps
• User information
• Chat participation
• Daily/hourly patterns

The plugin automatically tracks user interactions and provides insights into bot usage patterns.
"""


# Export plugin class
__all__ = ['UserStatsPlugin']

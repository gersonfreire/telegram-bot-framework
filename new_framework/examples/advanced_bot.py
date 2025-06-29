"""
Advanced Bot Example with Plugins

This example demonstrates advanced features of the Telegram Bot Framework:
- Plugin system usage
- Payment integration
- Job scheduling
- System monitoring
- User statistics
"""

import asyncio
import os
from pathlib import Path
from datetime import datetime, timedelta

# Add the src directory to the path
import sys
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from tlgfwk import (
    TelegramBotFramework, command, admin_required_simple,
    SystemMonitorPlugin, UserStatsPlugin,
    PaymentManager, JobScheduler
)
from telegram import Update
from telegram.ext import ContextTypes


class AdvancedBot(TelegramBotFramework):
    """Advanced bot with plugins and extended functionality."""

    def __init__(self, config_file):
        # Initialize with comprehensive configuration
        super().__init__(
            token=os.getenv("BOT_TOKEN"),
            admin_user_ids=[int(x.strip()) for x in os.getenv("ADMIN_USER_IDS", "").split(",") if x.strip()],
            owner_user_id=int(os.getenv("OWNER_USER_ID", 0)),
            log_chat_id=int(os.getenv("LOG_CHAT_ID", 0)) if os.getenv("LOG_CHAT_ID") else None,
            debug=os.getenv("DEBUG", "true").lower() == "true",
            config_file=config_file
        )

        # Initialize additional managers
        self._setup_payment_manager()
        self._setup_scheduler()
        self._setup_plugins()

    def _setup_payment_manager(self):
        """Set up payment manager with providers."""
        payment_config = {
            'providers': {}
        }

        # Configure Stripe if available
        stripe_key = os.getenv("STRIPE_API_KEY")
        if stripe_key:
            payment_config['providers']['stripe'] = {
                'api_key': stripe_key,
                'webhook_secret': os.getenv("STRIPE_WEBHOOK_SECRET")
            }

        # Configure PIX if available (Brazil)
        pix_key = os.getenv("PIX_ACCOUNT_KEY")
        if pix_key:
            payment_config['providers']['pix'] = {
                'account_key': pix_key,
                'merchant_name': os.getenv("PIX_MERCHANT_NAME", "Bot Service"),
                'merchant_city': os.getenv("PIX_MERCHANT_CITY", "São Paulo")
            }

        if payment_config['providers']:
            self.payment_manager = PaymentManager(self, payment_config)
            self.logger.info("Payment manager initialized")

    def _setup_scheduler(self):
        """Set up job scheduler."""
        scheduler_config = {
            'async_mode': True,
            'max_workers': 10,
            'use_persistent_store': os.getenv("USE_PERSISTENT_JOBS", "false").lower() == "true",
            'database_url': os.getenv("JOBS_DATABASE_URL", "sqlite:///jobs.db")
        }

        self.scheduler = JobScheduler(self, scheduler_config)
        self.scheduler.start()

        # Schedule some example jobs
        self._schedule_example_jobs()

    def _setup_plugins(self):
        """Set up and load plugins."""
        # Load system monitor plugin
        if os.getenv("ENABLE_SYSTEM_MONITOR", "true").lower() == "true":
            system_monitor = SystemMonitorPlugin(self)
            self.plugin_manager.plugins["system_monitor"] = system_monitor.get_plugin_info()
            self.plugin_manager.loaded_plugins["system_monitor"] = system_monitor
            system_monitor.initialize()
            self.logger.info("System Monitor plugin loaded")

        # Load user statistics plugin
        if os.getenv("ENABLE_USER_STATS", "true").lower() == "true":
            user_stats = UserStatsPlugin(self)
            self.plugin_manager.plugins["user_stats"] = user_stats.get_plugin_info()
            self.plugin_manager.loaded_plugins["user_stats"] = user_stats
            user_stats.initialize()
            self.logger.info("User Statistics plugin loaded")

    def _schedule_example_jobs(self):
        """Schedule some example jobs."""
        # Daily status report
        self.scheduler.add_job(
            func=self._send_daily_report,
            trigger='cron',
            name='daily_report',
            description='Send daily status report',
            hour=9,  # 9 AM
            minute=0
        )

        # Hourly health check
        self.scheduler.add_job(
            func=self._health_check,
            trigger='interval',
            name='health_check',
            description='Perform health check',
            hours=1
        )

        # Weekly cleanup
        self.scheduler.add_job(
            func=self._weekly_cleanup,
            trigger='cron',
            name='weekly_cleanup',
            description='Weekly data cleanup',
            day_of_week='sunday',
            hour=2,
            minute=0
        )

    @command(name="status", description="Get bot status information")
    async def status_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Get comprehensive bot status."""
        try:
            status_msg = "🤖 **Bot Status Report**\n\n"

            # Basic info
            uptime = datetime.now() - self.start_time
            status_msg += f"**Uptime:** {uptime}\n"
            status_msg += f"**Users:** {len(self.user_manager.users)}\n"
            status_msg += f"**Active Plugins:** {len(self.plugin_manager.loaded_plugins)}\n"

            # Scheduler info
            if hasattr(self, 'scheduler'):
                scheduler_stats = self.scheduler.get_statistics()
                status_msg += f"**Scheduled Jobs:** {scheduler_stats['total_jobs']}\n"
                status_msg += f"**Job Success Rate:** {scheduler_stats['success_rate']:.1%}\n"

            # Payment info
            if hasattr(self, 'payment_manager'):
                status_msg += f"**Payment Providers:** {len(self.payment_manager.providers)}\n"

            # Memory usage (if psutil available)
            try:
                import psutil
                import os
                process = psutil.Process(os.getpid())
                memory_mb = process.memory_info().rss / 1024 / 1024
                status_msg += f"**Memory Usage:** {memory_mb:.1f} MB\n"
            except ImportError:
                pass

            await update.message.reply_text(status_msg, parse_mode='Markdown')

        except Exception as e:
            self.logger.error(f"Error in status command: {e}")
            await update.message.reply_text(f"❌ Error getting status: {e}")

    @command(name="schedule", description="Schedule a custom job")
    @admin_required_simple
    async def schedule_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Schedule a custom job."""
        try:
            if not hasattr(self, 'scheduler'):
                await update.message.reply_text("❌ Scheduler not available")
                return

            if len(context.args) < 3:
                await update.message.reply_text(
                    "Usage: /schedule <name> <seconds> <message>\n"
                    "Example: /schedule reminder 300 Time to take a break!"
                )
                return

            name = context.args[0]
            try:
                seconds = int(context.args[1])
            except ValueError:
                await update.message.reply_text("❌ Invalid number of seconds")
                return

            message = " ".join(context.args[2:])
            chat_id = update.effective_chat.id

            # Create reminder function
            async def send_reminder():
                await context.bot.send_message(chat_id, f"⏰ Reminder: {message}")

            # Schedule the job
            run_time = datetime.now() + timedelta(seconds=seconds)
            job_id = self.scheduler.add_job(
                func=send_reminder,
                trigger='date',
                name=f"reminder_{name}",
                description=f"Reminder: {message}",
                run_date=run_time,
                user_id=update.effective_user.id,
                chat_id=chat_id
            )

            await update.message.reply_text(
                f"⏰ Reminder '{name}' scheduled for {run_time.strftime('%Y-%m-%d %H:%M:%S')}\n"
                f"Job ID: {job_id}"
            )

        except Exception as e:
            self.logger.error(f"Error scheduling job: {e}")
            await update.message.reply_text(f"❌ Error scheduling job: {e}")

    @command(name="jobs", description="List scheduled jobs")
    @admin_required_simple
    async def jobs_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """List scheduled jobs."""
        try:
            if not hasattr(self, 'scheduler'):
                await update.message.reply_text("❌ Scheduler not available")
                return

            jobs = self.scheduler.list_jobs()

            if not jobs:
                await update.message.reply_text("📅 No scheduled jobs")
                return

            message = "📅 **Scheduled Jobs**\n\n"

            for job in jobs[:10]:  # Limit to 10 jobs
                status_emoji = {
                    'scheduled': '⏳',
                    'running': '🏃',
                    'completed': '✅',
                    'failed': '❌',
                    'paused': '⏸️'
                }.get(job.status.value, '❓')

                message += f"{status_emoji} **{job.name}**\n"
                message += f"• ID: `{job.id}`\n"
                message += f"• Status: {job.status.value}\n"

                if job.next_run_time:
                    message += f"• Next run: {job.next_run_time.strftime('%Y-%m-%d %H:%M:%S')}\n"

                message += f"• Runs: {job.run_count}\n"

                if job.error_count > 0:
                    message += f"• Errors: {job.error_count}\n"

                message += "\n"

            if len(jobs) > 10:
                message += f"... and {len(jobs) - 10} more jobs"

            await update.message.reply_text(message, parse_mode='Markdown')

        except Exception as e:
            self.logger.error(f"Error listing jobs: {e}")
            await update.message.reply_text(f"❌ Error listing jobs: {e}")

    @command(name="payment", description="Create a test payment")
    async def payment_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Create a test payment."""
        try:
            if not hasattr(self, 'payment_manager'):
                await update.message.reply_text("❌ Payment system not available")
                return

            # Create a simple payment for demonstration
            from tlgfwk.core.payment_manager import PaymentItem, PaymentProvider

            items = [
                PaymentItem(
                    name="Test Service",
                    description="Test payment for bot service",
                    price=10.00,
                    currency="USD"
                )
            ]

            # Use first available provider
            provider = list(self.payment_manager.providers.keys())[0]

            result = self.payment_manager.create_payment(
                user_id=update.effective_user.id,
                items=items,
                provider=provider,
                description="Test payment from bot"
            )

            if result.success:
                payment = result.payment_request
                message = f"💳 **Payment Created**\n\n"
                message += f"**ID:** {payment.id}\n"
                message += f"**Amount:** ${payment.total_amount}\n"
                message += f"**Provider:** {payment.provider.value}\n"

                if payment.payment_url:
                    message += f"**Payment URL:** {payment.payment_url}\n"

                await update.message.reply_text(message, parse_mode='Markdown')
            else:
                await update.message.reply_text(f"❌ Payment creation failed: {result.error_message}")

        except Exception as e:
            self.logger.error(f"Error creating payment: {e}")
            await update.message.reply_text(f"❌ Error creating payment: {e}")

    async def _send_daily_report(self):
        """Send daily status report to admins."""
        try:
            if not self.config.admin_user_ids:
                return

            # Generate daily report
            report = "📊 **Daily Bot Report**\n\n"

            # User stats
            total_users = len(self.user_manager.users)
            active_today = len([u for u in self.user_manager.users.values()
                              if u.last_seen and
                              (datetime.now() - u.last_seen).days == 0])

            report += f"**Users:** {total_users} total, {active_today} active today\n"

            # Job stats
            if hasattr(self, 'scheduler'):
                stats = self.scheduler.get_statistics()
                report += f"**Jobs:** {stats['total_jobs']} total, {stats['scheduled']} scheduled\n"
                report += f"**Success Rate:** {stats['success_rate']:.1%}\n"

            # System stats (if available)
            try:
                import psutil
                cpu_percent = psutil.cpu_percent()
                memory_percent = psutil.virtual_memory().percent
                report += f"**System:** CPU {cpu_percent:.1f}%, Memory {memory_percent:.1f}%\n"
            except ImportError:
                pass

            report += f"\n**Report generated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"

            # Send to all admins
            for admin_id in self.config.admin_user_ids:
                try:
                    await self.application.bot.send_message(admin_id, report, parse_mode='Markdown')
                except Exception as e:
                    self.logger.error(f"Failed to send daily report to admin {admin_id}: {e}")

        except Exception as e:
            self.logger.error(f"Error generating daily report: {e}")

    async def _health_check(self):
        """Perform health check."""
        try:
            self.logger.info("Performing health check...")

            # Check database connectivity
            if hasattr(self, 'persistence'):
                self.persistence.save_bot_data("health_check", datetime.now().isoformat())

            # Check scheduler
            if hasattr(self, 'scheduler'):
                stats = self.scheduler.get_statistics()
                if stats['failed'] > stats['completed'] * 0.5:  # More than 50% failure rate
                    self.logger.warning(f"High job failure rate: {stats['failed']}/{stats['total_jobs']}")

            # Check memory usage
            try:
                import psutil
                import os
                process = psutil.Process(os.getpid())
                memory_mb = process.memory_info().rss / 1024 / 1024

                if memory_mb > 500:  # More than 500MB
                    self.logger.warning(f"High memory usage: {memory_mb:.1f} MB")
            except ImportError:
                pass

            self.logger.info("Health check completed")

        except Exception as e:
            self.logger.error(f"Health check failed: {e}")

    async def _weekly_cleanup(self):
        """Perform weekly cleanup tasks."""
        try:
            self.logger.info("Performing weekly cleanup...")

            # Clean up old user data
            cutoff_date = datetime.now() - timedelta(days=30)
            cleaned_users = 0

            for user_id, user in list(self.user_manager.users.items()):
                if user.last_seen and user.last_seen < cutoff_date:
                    # Remove inactive users (optional)
                    # del self.user_manager.users[user_id]
                    # cleaned_users += 1
                    pass

            # Clean up old log files
            # ... implement log cleanup logic ...

            self.logger.info(f"Weekly cleanup completed. Cleaned {cleaned_users} inactive users")

        except Exception as e:
            self.logger.error(f"Weekly cleanup failed: {e}")


def main():
    """Main function to run the advanced bot."""
    print("🚀 Starting Advanced Bot with plugins...")
    print("=" * 50)

    # Verificar arquivo .env na pasta examples
    env_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), ".env")
    if not os.path.exists(env_path):
        print("⚠️  Arquivo .env não encontrado na pasta examples!")
        print("📝 Crie um arquivo .env com as seguintes variáveis:")
        print("   BOT_TOKEN=seu_token_aqui")
        print("   OWNER_USER_ID=seu_id_aqui")
        print("   ADMIN_USER_IDS=id1,id2,id3")
        print("   LOG_CHAT_ID=chat_id_para_logs")
        print("   DEBUG=true")
        print("=" * 50)
        return

    try:
        # Create and run the bot
        bot = AdvancedBot(config_file=env_path)

        print("✅ Advanced Bot criado com sucesso!")
        print("🎯 Funcionalidades disponíveis:")
        print("   • Sistema de plugins avançado")
        print("   • Agendamento de tarefas")
        print("   • Sistema de pagamentos")
        print("   • Relatórios automáticos")
        print("   • Health checks")
        print("   • Limpeza automática")
        print("=" * 50)
        print("🤖 Bot iniciado! Pressione Ctrl+C para parar")

        bot.run()

    except KeyboardInterrupt:
        print("\n⏹️  Bot parado pelo usuário")
    except Exception as e:
        print(f"❌ Erro ao executar o bot: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()

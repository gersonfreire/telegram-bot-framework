from .base import PluginBase
from ..core.decorators import command, admin_required
from telegram import Update
from telegram.ext import CallbackContext

class SchedulerPlugin(PluginBase):
    """
    A plugin for scheduling messages.
    """
    @admin_required
    @command("schedule", "Schedules a message to be sent to a chat.")
    async def schedule_message(self, update: Update, context: CallbackContext):
        """
        Usage: /schedule <seconds> <chat_id> <message>
        """
        try:
            _, seconds, chat_id, *message_parts = update.message.text.split()
            seconds = int(seconds)
            chat_id = int(chat_id)
            message = " ".join(message_parts)

            context.job_queue.run_once(
                self.send_scheduled_message,
                seconds,
                chat_id=chat_id,
                data={'message': message}
            )

            await update.message.reply_text(f"Message scheduled to be sent in {seconds} seconds.")
        except (ValueError, IndexError):
            await update.message.reply_text("Usage: /schedule <seconds> <chat_id> <message>")

    async def send_scheduled_message(self, context: CallbackContext):
        """
        Sends the scheduled message.
        """
        job = context.job
        message = job.data['message']
        await self.framework.application.bot.send_message(chat_id=job.chat_id, text=message)
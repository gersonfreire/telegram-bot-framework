from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes
import datetime

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text('Hello! Use /schedule <time> <message> to set a reminder.')

async def schedule(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    try:
        time = context.args[0]
        message = ' '.join(context.args[1:])
        schedule_time = datetime.datetime.strptime(time, '%H:%M').time()
        now = datetime.datetime.now().time()
        delay = (datetime.datetime.combine(datetime.date.today(), schedule_time) - datetime.datetime.combine(datetime.date.today(), now)).total_seconds()
        if delay < 0:
            delay += 86400  # Schedule for the next day if time has passed today

        context.job_queue.run_once(reminder, delay, context=(update.message.chat_id, message))
        await update.message.reply_text(f'Reminder set for {time} with message: {message}')
    except (IndexError, ValueError):
        await update.message.reply_text('Usage: /schedule <time> <message> (time in HH:MM format)')

async def reminder(context: ContextTypes.DEFAULT_TYPE) -> None:
    job = context.job
    await context.bot.send_message(job.context[0], text=job.context[1])

if __name__ == '__main__':
    application = ApplicationBuilder().token('YOUR_TELEGRAM_BOT_TOKEN').build()

    application.add_handler(CommandHandler('start', start))
    application.add_handler(CommandHandler('schedule', schedule))

    application.run_polling()
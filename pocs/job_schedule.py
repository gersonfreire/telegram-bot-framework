import os
from telegram import Update
from telegram.ext import Updater, CommandHandler, CallbackContext, Application

from dotenv import *

# Define the function to get jobs by name
def get_jobs_by_name(job_queue, name):
    return job_queue.get_jobs_by_name(name)

# Command handler to list jobs
async def list_jobs(update: Update, context: CallbackContext) -> None:
    job_name = context.args[0] if context.args else None
    if job_name:
        jobs = get_jobs_by_name(context.job_queue, job_name)
        if jobs:
            await update.message.reply_text(f"Jobs with name '{job_name}': {[job.name for job in jobs]}")
        else:
            await update.message.reply_text(f"No jobs found with name '{job_name}'.")
    else:
        await update.message.reply_text("Usage: /listjobs <job_name>")

# Command handler to add a job
async def add_job(update: Update, context: CallbackContext) -> None:
    if len(context.args) != 2:
        await update.message.reply_text("Usage: /addjob <job_name> <interval_in_seconds>")
        return

    job_name = context.args[0]
    interval = int(context.args[1])

    context.job_queue.run_repeating(callback=job_callback, interval=interval, first=0, name=job_name)
    await update.message.reply_text(f"Job '{job_name}' added with interval {interval} seconds.")

# Command handler to delete a job
async def delete_job(update: Update, context: CallbackContext) -> None:
    if len(context.args) != 1:
        await update.message.reply_text("Usage: /deletejob <job_name>")
        return

    job_name = context.args[0]
    jobs = get_jobs_by_name(context.job_queue, job_name)
    if jobs:
        for job in jobs:
            job.schedule_removal()
        await update.message.reply_text(f"Job(s) '{job_name}' deleted.")
    else:
        await update.message.reply_text(f"No jobs found with name '{job_name}'.")

# Example job callback function
def job_callback(context: CallbackContext) -> None:
    print("Job executed")
    
def main() -> None:
    
    load_dotenv()

    # Print only the settings from the .env file
    dotenv_settings = dotenv_values()    
    
    TELEGRAM_BOT_TOKEN = dotenv_settings['DEFAULT_BOT_TOKEN']
    
    application = Application.builder().token(TELEGRAM_BOT_TOKEN).build()

    # Register command handlers
    application.add_handler(CommandHandler("listjobs", list_jobs))
    application.add_handler(CommandHandler("addjob", add_job))
    application.add_handler(CommandHandler("deletejob", delete_job))

    # Start the Bot Run the application
    application.run_polling(allowed_updates=Update.ALL_TYPES)  

if __name__ == '__main__':
    main()
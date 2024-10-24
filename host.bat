
@REM This script is used to run the bot in the Windows environment

@REM Go to current directory
cd %~dp0

@REM Activate the virtual environment and run the bot
call .venv\Scripts\Activate

@REM Run the bot script repassing the arguments
@REM python examples\host_monitor_by_user.py %*
python examples\host_watch_bot.py %*

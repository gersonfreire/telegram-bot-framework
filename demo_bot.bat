
@REM This script is used to run the bot in the Windows environment

@REM Go to current directory
cd %~dp0\..\..

@REM Activate the virtual environment and run the bot
call .venv\Scripts\Activate

@REM Run the bot script repassing the arguments
python src\cnpj_bot\tlgfwk.py %*

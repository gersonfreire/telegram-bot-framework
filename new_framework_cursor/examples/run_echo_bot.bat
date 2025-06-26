@echo off
REM Script para rodar o Echo Bot do framework
cd /d %~dp0
cd ..
call .venv\Scripts\activate.bat
pip install -e .
cd examples
python echo_bot.py
pause 
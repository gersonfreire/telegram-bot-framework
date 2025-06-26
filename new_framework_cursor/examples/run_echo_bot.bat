@echo off
cd /d %~dp0
cd ..
call .venv\Scripts\activate
pip install -e .
cd examples
python echo_bot.py 
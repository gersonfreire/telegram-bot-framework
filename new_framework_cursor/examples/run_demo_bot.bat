@echo off
echo ========================================
echo    Demo Bot - Telegram Bot Framework
echo ========================================
echo.

REM Verificar se o arquivo .env existe
if not exist ".env" (
    echo [ERRO] Arquivo .env nao encontrado!
    echo.
    echo Crie um arquivo .env com as seguintes variaveis:
    echo   BOT_TOKEN=seu_token_aqui
    echo   OWNER_USER_ID=seu_id_aqui
    echo   ADMIN_USER_IDS=id1,id2,id3
    echo   LOG_CHAT_ID=chat_id_para_logs
    echo   DEBUG=true
    echo.
    pause
    exit /b 1
)

echo [INFO] Iniciando Demo Bot...
echo [INFO] Pressione Ctrl+C para parar
echo.

REM Executar o demo bot
python demo_bot.py

echo.
echo [INFO] Demo Bot finalizado.
pause 
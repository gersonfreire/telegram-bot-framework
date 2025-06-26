@echo off
REM Script para ativar o ambiente virtual .venv no Windows
REM Execute este arquivo para ativar o ambiente virtual

echo Ativando ambiente virtual...
call .venv\Scripts\activate.bat

echo.
echo Ambiente virtual ativado!
echo Para desativar, digite: deactivate
echo.
echo Pacotes instalados:
pip list
echo.

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
echo ========================================
echo COMANDOS UTEIS PARA TESTES:
echo ========================================
echo python quick_test.py        - Teste rapido do framework
echo python test_components.py   - Teste de componentes individuais
echo python -m pytest tests/     - Executar todos os testes unitarios
echo python -m pytest tests/test_utils.py -v  - Testar utilitarios
echo ========================================
echo.

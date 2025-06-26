# Script para ativar o ambiente virtual .venv no PowerShell
# Execute este arquivo para ativar o ambiente virtual

Write-Host "Ativando ambiente virtual..." -ForegroundColor Green
& .\.venv\Scripts\Activate.ps1

Write-Host ""
Write-Host "Ambiente virtual ativado!" -ForegroundColor Green
Write-Host "Para desativar, digite: deactivate" -ForegroundColor Yellow
Write-Host ""
Write-Host "Pacotes instalados:" -ForegroundColor Blue
pip list
Write-Host ""

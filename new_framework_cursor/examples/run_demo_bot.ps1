# Demo Bot - Telegram Bot Framework
# Script PowerShell para execução

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "   Demo Bot - Telegram Bot Framework" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Verificar se o arquivo .env existe
if (-not (Test-Path ".env")) {
    Write-Host "[ERRO] Arquivo .env não encontrado!" -ForegroundColor Red
    Write-Host ""
    Write-Host "Crie um arquivo .env com as seguintes variáveis:" -ForegroundColor Yellow
    Write-Host "  BOT_TOKEN=seu_token_aqui" -ForegroundColor White
    Write-Host "  OWNER_USER_ID=seu_id_aqui" -ForegroundColor White
    Write-Host "  ADMIN_USER_IDS=id1,id2,id3" -ForegroundColor White
    Write-Host "  LOG_CHAT_ID=chat_id_para_logs" -ForegroundColor White
    Write-Host "  DEBUG=true" -ForegroundColor White
    Write-Host ""
    Read-Host "Pressione Enter para sair"
    exit 1
}

Write-Host "[INFO] Iniciando Demo Bot..." -ForegroundColor Green
Write-Host "[INFO] Pressione Ctrl+C para parar" -ForegroundColor Yellow
Write-Host ""

try {
    # Executar o demo bot
    python demo_bot.py
}
catch {
    Write-Host "[ERRO] Erro ao executar o Demo Bot: $_" -ForegroundColor Red
}
finally {
    Write-Host ""
    Write-Host "[INFO] Demo Bot finalizado." -ForegroundColor Green
    Read-Host "Pressione Enter para sair"
} 
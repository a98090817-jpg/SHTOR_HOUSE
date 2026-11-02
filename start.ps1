# =========================================================
#  SHTOR HOUSE - serverni ishga tushirish (PowerShell)
#  Bu faylni o'ng tugma -> "Run with PowerShell" bilan ishga tushiring.
# =========================================================

Set-Location $PSScriptRoot

$py = "$env:LOCALAPPDATA\Programs\Python\Python311\python.exe"

if (-not (Test-Path $py)) {
    Write-Host "[XATO] Python topilmadi: $py" -ForegroundColor Red
    Write-Host "Iltimos, Python o'rnatilganini tekshiring."
    Read-Host "Davom etish uchun Enter bosing"
    exit 1
}

Write-Host "========================================" -ForegroundColor Green
Write-Host "  SHTOR HOUSE ishga tushmoqda..." -ForegroundColor Green
Write-Host "  Manzil: http://127.0.0.1:8000" -ForegroundColor Green
Write-Host "  To'xtatish uchun: Ctrl + C" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Green

# Brauzerni 3 sekunddan keyin avtomatik ochadi
Start-Job -ScriptBlock { Start-Sleep -Seconds 3; Start-Process "http://127.0.0.1:8000" } | Out-Null

& $py manage.py runserver 127.0.0.1:8000

# =========================================================
#  SHTOR HOUSE - serverni ishga tushirish (PowerShell)
#  Bu faylni o'ng tugma -> "Run with PowerShell" bilan ishga tushiring.
# =========================================================

Set-Location $PSScriptRoot

# Python yo'lini avtomatik aniqlash
$py = "python"
if (-not (Get-Command python -ErrorAction SilentlyContinue)) {
    $py = "$env:LOCALAPPDATA\Programs\Python\Python311\python.exe"
    if (-not (Test-Path $py)) {
        Write-Host "[XATO] Python topilmadi: $py" -ForegroundColor Red
        Write-Host "Iltimos, Python o'rnatilganini tekshiring."
        Read-Host "Davom etish uchun Enter bosing"
        exit 1
    }
}

# .env faylidan o'zgaruvchilarni yuklash
if (Test-Path .env) {
    Get-Content .env | ForEach-Object {
        $line = $_.Trim()
        if ($line -and -not $line.StartsWith('#')) {
            $parts = $line -split '=', 2
            if ($parts.Count -eq 2) {
                [Environment]::SetEnvironmentVariable($parts[0].Trim(), $parts[1].Trim(), 'Process')
            }
        }
    }
}

Write-Host "========================================" -ForegroundColor Green
Write-Host "  SHTOR HOUSE ishga tushmoqda..." -ForegroundColor Green
Write-Host "  Manzil: http://127.0.0.1:8000" -ForegroundColor Green
Write-Host "  To'xtatish uchun: Ctrl + C" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Green

# Migratsiyalarni bajarish
Write-Host "[INFO] Migratsiyalar tekshirilmoqda..." -ForegroundColor Cyan
& $py manage.py migrate --noinput
if ($LASTEXITCODE -ne 0) {
    Write-Host "[XATO] Migratsiya muvaffaqiyatsiz." -ForegroundColor Red
    Read-Host "Davom etish uchun Enter bosing"
    exit 1
}

# Administrator hisobini har safar tiklash (baza yangilansa ham yo'qolmaydi)
& $py manage.py ensure_admin

# Static fayllarni to'plash
& $py manage.py collectstatic --noinput 2>$null

# Brauzerni 3 sekunddan keyin avtomatik ochadi
Start-Job -ScriptBlock { Start-Sleep -Seconds 3; Start-Process "http://127.0.0.1:8000" } | Out-Null

& $py manage.py runserver 127.0.0.1:8000

Read-Host "Davom etish uchun Enter bosing"
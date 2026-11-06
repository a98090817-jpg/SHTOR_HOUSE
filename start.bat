@echo off
REM =========================================================
REM  SHTOR HOUSE - serverni ishga tushirish
REM  Bu faylni ikki marta bosing - sayt ochiladi.
REM =========================================================

cd /d "%~dp0"

REM Python yo'lini avtomatik aniqlash
where python >nul 2>&1
if %errorlevel% neq 0 (
    set PY=%LOCALAPPDATA%\Programs\Python\Python311\python.exe
    if not exist "%PY%" (
        echo [XATO] Python topilmadi. Iltimos, Python o'rnatilganini tekshiring.
        pause
        exit /b 1
    )
) else (
    set PY=python
)

echo ========================================
echo   SHTOR HOUSE ishga tushmoqda...
echo   Manzil: http://127.0.0.1:8000
echo   To'xtatish uchun: Ctrl + C
echo ========================================
echo.

REM .env faylidan o'zgaruvchilarni yuklash (Windows da set orqali)
if exist .env (
    for /f "usebackq delims=" %%A in (.env) do (
        if not "%%A"=="" if not "%%A"=="#*" set "%%A"
    )
)

REM Migratsiyalarni bajarish
echo [INFO] Migratsiyalar tekshirilmoqda...
"%PY%" manage.py migrate --noinput
if %errorlevel% neq 0 (
    echo [XATO] Migratsiya muvaffaqiyatsiz.
    pause
    exit /b 1
)

REM Administrator hisobini har safar tiklash
"%PY%" manage.py ensure_admin

REM Static fayllarni to'plash (agar kerak bo'lsa)
"%PY%" manage.py collectstatic --noinput 2>nul

REM Brauzerni 3 sekunddan keyin avtomatik ochadi
start "" cmd /c "timeout /t 3 >nul & start http://127.0.0.1:8000"

"%PY%" manage.py runserver 127.0.0.1:8000

pause
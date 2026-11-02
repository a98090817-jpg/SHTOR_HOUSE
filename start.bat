@echo off
REM =========================================================
REM  SHTOR HOUSE - serverni ishga tushirish
REM  Bu faylni ikki marta bosing - sayt ochiladi.
REM =========================================================

cd /d "%~dp0"

set PY=%LOCALAPPDATA%\Programs\Python\Python311\python.exe

if not exist "%PY%" (
    echo [XATO] Python topilmadi: %PY%
    echo Iltimos, Python o'rnatilganini tekshiring.
    pause
    exit /b 1
)

echo ========================================
echo   SHTOR HOUSE ishga tushmoqda...
echo   Manzil: http://127.0.0.1:8000
echo   To'xtatish uchun: Ctrl + C
echo ========================================
echo.

REM Brauzerni 3 sekunddan keyin avtomatik ochadi
start "" cmd /c "timeout /t 3 >nul & start http://127.0.0.1:8000"

"%PY%" manage.py runserver 127.0.0.1:8000

pause

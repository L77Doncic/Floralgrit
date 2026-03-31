@echo off
REM Shimeji Mascot Launcher for Windows
REM Detects environment and runs with appropriate settings

cd /d "%~dp0"

echo Checking Python installation...
python --version >nul 2>&1
if errorlevel 1 (
    echo Error: Python not found. Please install Python 3.8 or higher.
    exit /b 1
)

echo.
echo Starting Shimeji Mascot...
echo.
echo Tips:
echo - Left click and drag to move the mascot
echo - Right click for menu options
echo.

REM Run the mascot
python main.py

if %errorlevel% neq 0 (
    echo.
    echo Error occurred while running Shimeji (Exit code: %errorlevel%)
    pause
)

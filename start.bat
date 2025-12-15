@echo off
REM JARVIS Voice Assistant - Windows Launcher
REM Production Release v2.1.0

title JARVIS Voice Assistant

echo ============================================================
echo JARVIS Voice Assistant v2.1.0
echo Production Mode
echo ============================================================
echo.

REM Check if virtual environment exists
if not exist ".venv\Scripts\python.exe" (
    echo Creating virtual environment...
    python -m venv .venv
    echo.
)

REM Activate virtual environment and run
echo Starting JARVIS...
echo.
call .venv\Scripts\activate
python src\main.py

REM Handle exit
echo.
echo JARVIS has stopped.
pause

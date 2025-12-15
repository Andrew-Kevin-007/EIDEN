@echo off
echo ========================================
echo    JARVIS - Web GUI Launcher
echo ========================================
echo.

echo Starting FastAPI Backend Server...
start "JARVIS Backend" /D "d:\Edien\voice-assistant" cmd /k "D:/Edien/voice-assistant/.venv/Scripts/python.exe api_server.py"

timeout /t 3 >nul

echo Starting Next.js Frontend...
start "JARVIS Frontend" /D "d:\Edien\voice-assistant\web-gui" cmd /k "npm run dev"

echo.
echo ========================================
echo Both servers are starting...
echo.
echo Backend:  http://localhost:8000
echo Frontend: http://localhost:3000
echo.
echo Press any key to open the web interface...
pause >nul

start http://localhost:3000

echo.
echo Web interface opened in your browser!
echo Close this window to keep servers running.
echo ========================================

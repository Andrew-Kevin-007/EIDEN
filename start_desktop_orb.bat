@echo off
echo ========================================
echo    JARVIS Desktop - OpenGL Orb GUI
echo ========================================
echo.

echo Checking dependencies...
pip show moderngl >nul 2>&1
if errorlevel 1 (
    echo Installing ModernGL for OpenGL rendering...
    pip install moderngl moderngl-window PyOpenGL PyOpenGL-accelerate
)

pip show sounddevice >nul 2>&1
if errorlevel 1 (
    echo Installing sounddevice for voice reactivity...
    pip install sounddevice
)

echo.
echo Starting JARVIS Desktop GUI...
echo.

cd /d "%~dp0"
D:/Edien/voice-assistant/.venv/Scripts/python.exe src/jarvis_desktop_orb.py

pause

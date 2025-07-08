@echo off
chcp 65001 >nul
echo Starting ngrok tunnel for API server...
echo.

echo Starting ngrok tunnel on port 8000...
cd /d "%~dp0"
ngrok-v3-stable-windows-amd64\ngrok.exe http 8000

pause 
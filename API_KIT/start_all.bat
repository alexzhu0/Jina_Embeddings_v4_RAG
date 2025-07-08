@echo off
chcp 65001 >nul
echo Starting Government Report RAG API with ngrok tunnel...
echo.

echo Step 1: Starting API server in background...
cd /d "%~dp0"
start "API Server" cmd /c "call start_api.bat"

echo.
echo Waiting for API server to start...
timeout /t 15 /nobreak >nul

echo.
echo Step 2: Initializing RAG system...
echo Calling setup API...
powershell -Command "try { $response = Invoke-RestMethod -Uri 'http://localhost:8000/api/setup' -Method POST -ContentType 'application/json' -Body '{\"force_rebuild\": false}'; if ($response.success) { Write-Host 'System initialization successful!' -ForegroundColor Green } else { Write-Host 'System initialization failed:' $response.error -ForegroundColor Red } } catch { Write-Host 'Failed to connect to API server:' $_.Exception.Message -ForegroundColor Red }"

echo.
echo Step 3: Starting ngrok tunnel...
start "ngrok Tunnel" cmd /c "call start_ngrok.bat"

echo.
echo All services are starting...
echo - API Server: http://localhost:8000
echo - API Docs: http://localhost:8000/docs
echo - ngrok tunnel will show the public URL
echo.
echo Press any key to exit...
pause >nul
@echo off
echo Stopping Lab Inventory Management Tool (Native Python)...
echo.

REM Kill any process running on port 5000
for /f "tokens=5" %%a in ('netstat -aon ^| findstr ":5000 "') do (
    echo Stopping process %%a on port 5000...
    taskkill /PID %%a /F >nul 2>&1
)

echo Application stopped.
pause

@echo off
echo ========================================
echo Lab Inventory Management Tool
echo Opening Windows Firewall Port
echo ========================================
echo.
echo This will allow other computers to access the application.
echo.
echo IMPORTANT: You must run this as Administrator!
echo.
echo Press any key to continue or Ctrl+C to cancel...
pause >nul
echo.

REM Check if running as administrator
net session >nul 2>&1
if %errorlevel% neq 0 (
    echo ========================================
    echo ERROR: Not running as Administrator!
    echo ========================================
    echo.
    echo Please right-click this file and select:
    echo "Run as administrator"
    echo.
    pause
    exit /b 1
)

echo Adding firewall rule for port 5000...
echo.

netsh advfirewall firewall add rule name="Lab Inventory Tool" dir=in action=allow protocol=TCP localport=5000

if %errorlevel% equ 0 (
    echo.
    echo ========================================
    echo SUCCESS! Firewall configured.
    echo ========================================
    echo.
    echo Port 5000 is now open for incoming connections.
    echo Other users on your network can now access the application.
    echo.
    echo To find your network URL, run: get-network-info.bat
    echo.
) else (
    echo.
    echo ========================================
    echo ERROR: Failed to configure firewall!
    echo ========================================
    echo.
    echo You may need to configure it manually:
    echo.
    echo 1. Open Windows Defender Firewall
    echo 2. Click "Advanced settings"
    echo 3. Click "Inbound Rules" - "New Rule"
    echo 4. Select "Port" - Click Next
    echo 5. Select "TCP" - Enter "5000" - Click Next
    echo 6. Select "Allow the connection" - Click Next
    echo 7. Check all profiles - Click Next
    echo 8. Name: "Lab Inventory Tool" - Click Finish
    echo.
)

pause

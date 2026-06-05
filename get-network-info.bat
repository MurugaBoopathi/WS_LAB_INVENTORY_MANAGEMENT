@echo off
echo ========================================
echo Lab Inventory Management Tool
echo Network Access Information
echo ========================================
echo.
echo This tool will help you find the URL to share with other users.
echo.
echo ========================================
echo FINDING YOUR NETWORK INFORMATION...
echo ========================================
echo.

REM Get machine name
echo [1] Machine Name (Computer Name):
echo.
echo    Your computer name is: %COMPUTERNAME%
echo.

REM Get IP addresses
echo [2] IP Addresses:
echo.
ipconfig | findstr /i "IPv4"
echo.

echo ========================================
echo HOW TO SHARE THE APPLICATION
echo ========================================
echo.
echo Option 1: Using IP Address
echo ----------------------------
echo.
echo Look at the IPv4 addresses above and find your main network IP
echo (Usually something like 192.168.x.x or 10.x.x.x)
echo.
echo Share this URL with other users:
echo.
echo    http://YOUR-IP-ADDRESS:5000
echo.
echo Example: http://192.168.1.100:5000
echo.
echo.
echo Option 2: Using Machine Name
echo -----------------------------
echo.
echo Share this URL with other users:
echo.
echo    http://%COMPUTERNAME%:5000
echo.
echo.
echo ========================================
echo IMPORTANT: FIREWALL CONFIGURATION
echo ========================================
echo.
echo For other users to access, Windows Firewall must allow port 5000.
echo.
echo Run this command as Administrator to open the port:
echo.
echo    netsh advfirewall firewall add rule name="Lab Inventory Tool" dir=in action=allow protocol=TCP localport=5000
echo.
echo Or run: open-firewall.bat
echo.
echo ========================================
echo TESTING ACCESS
echo ========================================
echo.
echo From another computer on the same network:
echo.
echo 1. Open a web browser
echo 2. Enter the URL (using IP or machine name)
echo 3. You should see the login page
echo.
echo If it doesn't work:
echo    - Check if start-exe.bat is still running
echo    - Check firewall settings
echo    - Verify both computers are on same network
echo    - Try using IP address instead of machine name
echo.
echo ========================================
echo QUICK ACCESS TEST
echo ========================================
echo.
echo Testing local access...
echo.
timeout /t 2 /nobreak >nul
curl -s http://localhost:5000 >nul 2>&1
if %errorlevel% equ 0 (
    echo ✓ Application is running and accessible locally!
) else (
    echo ✗ Cannot connect to application. Make sure it's running.
    echo   Run start-exe.bat first.
)
echo.
echo ========================================

pause

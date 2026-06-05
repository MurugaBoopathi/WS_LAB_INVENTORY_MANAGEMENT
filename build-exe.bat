@echo off
echo ========================================
echo  Building Lab Inventory Tool Executable
echo  (Source code will NOT be visible to client)
echo ========================================
echo.

REM --- Check Python ---
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ERROR: Python not found. Install Python 3.10+ and add to PATH.
    pause
    exit /b 1
)

REM --- Create / activate virtual environment ---
if not exist "venv\" (
    echo Creating virtual environment...
    python -m venv venv
)
call venv\Scripts\activate.bat

REM --- Install build dependencies ---
echo Installing build dependencies...
pip install --quiet --upgrade pip
pip install --quiet flask waitress pyinstaller

REM --- Clean previous build artefacts ---
if exist "dist\"          rmdir /s /q dist
if exist "build\"         rmdir /s /q build
if exist "client_package\" rmdir /s /q client_package

echo.
echo Building executable with PyInstaller...
echo (This may take 2-3 minutes on first build)
echo.

REM --- Run PyInstaller ---
pyinstaller --onefile ^
    --name "lab_inventory" ^
    --add-data "app/templates;app/templates" ^
    --add-data "app/static;app/static" ^
    --hidden-import "waitress" ^
    --hidden-import "waitress.utilities" ^
    --hidden-import "app.routes" ^
    --hidden-import "app.data_manager" ^
    --hidden-import "app.email_service" ^
    --hidden-import "email.mime.text" ^
    --hidden-import "email.mime.multipart" ^
    --noconfirm ^
    run.py

if %errorlevel% neq 0 (
    echo.
    echo ERROR: Build failed! Check the output above for details.
    pause
    exit /b 1
)

echo.
echo ========================================
echo  Build SUCCESS!
echo  Assembling client package...
echo ========================================

REM --- Assemble client_package folder ---
mkdir client_package
mkdir client_package\data

REM Executable (no source code inside)
copy dist\lab_inventory.exe     client_package\

REM Client-editable configuration
copy settings.ini               client_package\

REM Data files (inventory + history)
copy app\data\inventory.json    client_package\data\
copy app\data\history.json      client_package\data\

REM Utility scripts
copy start-exe.bat              client_package\
copy stop-native.bat            client_package\
copy open-firewall.bat          client_package\
copy get-network-info.bat       client_package\

echo.
echo ========================================
echo  Client package ready in: client_package\
echo.
echo  Contents:
echo    lab_inventory.exe   ^<-- application (no source code)
echo    settings.ini        ^<-- client edits this for config
echo    data\               ^<-- inventory data (writable)
echo    start-exe.bat       ^<-- double-click to run
echo    stop-native.bat     ^<-- to stop the app
echo    open-firewall.bat   ^<-- for network access
echo ========================================
echo.

pause

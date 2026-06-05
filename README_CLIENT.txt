========================================
LAB INVENTORY MANAGEMENT TOOL
CLIENT PACKAGE OVERVIEW
========================================

This application is delivered as a Windows executable package.

========================================
QUICK START (3 STEPS)
========================================

1. OPEN THE PACKAGE FOLDER
  - Keep all files together in one folder

2. EDIT SETTINGS IF NEEDED
  - Open settings.ini
  - Update admin and email settings

3. START THE APPLICATION
  - Double-click start-exe.bat
  - Open browser: http://localhost:5000
  - Login with the configured credentials

========================================
PACKAGE CONTENTS
========================================

- lab_inventory.exe      Application executable
- start-exe.bat         Starts the application
- stop-native.bat       Stops the application
- settings.ini          Client-editable configuration
- data\                Inventory and history data
- open-firewall.bat     Opens port 5000 for network users
- get-network-info.bat  Shows the URL to share with other users

========================================
SYSTEM REQUIREMENTS
========================================

- Windows 10/11 or Windows Server 2019+
- 2 GB free RAM minimum
- 1 GB free disk space minimum
- Chrome, Edge, or Firefox

========================================
IMPORTANT NOTES
========================================

- Keep settings.ini and the data folder in the same package folder
- Do not move lab_inventory.exe away from the package contents
- Change the default admin password before production use
- Back up the data folder regularly

========================================
NETWORK ACCESS
========================================

If other users need access from the same network:

1. Run open-firewall.bat as Administrator
2. Run get-network-info.bat
3. Share the displayed URL

========================================
MORE INFORMATION
========================================

- CLIENT_INSTALL_GUIDE.md      Detailed setup and operation
- NETWORK_ACCESS_GUIDE.md      Share the app on your network
- SUPPORT.txt                 Support contact information

========================================

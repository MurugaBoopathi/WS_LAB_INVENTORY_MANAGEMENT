# Lab Inventory Management Tool - Client Installation Guide

## Deployment Model

This application is delivered as a Windows executable package.

Supported flow:

1. Receive the `client_package` folder
2. Edit `settings.ini` if needed
3. Start the app with `start-exe.bat`
4. Open the application in a browser

---

## Prerequisites

- Windows 10/11 or Windows Server 2019+
- 2 GB free RAM
- 1 GB free disk space
- Administrator access if firewall changes are required

---

## Package Contents

The delivered package should contain:

```text
client_package/
├── lab_inventory.exe
├── start-exe.bat
├── stop-native.bat
├── settings.ini
├── open-firewall.bat
├── get-network-info.bat
└── data/
    ├── inventory.json
    └── history.json
```

---

## Step 1: Place the Package

1. Copy the full `client_package` folder to the target machine.
2. Keep the full folder together.
3. Do not move `lab_inventory.exe` outside the package.

Example location:

```text
C:\Lab_Inventory\client_package
```

---

## Step 2: Configure Settings

Open `settings.ini` and update the required values.

Common fields to review:

- `ADMIN_NT_ID`
- `ADMIN_PASSWORD`
- `ADMIN_EMAIL`
- `MANAGER_EMAIL`
- `SENDER_EMAIL`
- `EMAIL_DOMAIN`
- `SMTP_SERVER`
- `SMTP_PORT`
- `SMTP_USE_TLS`
- `SMTP_USERNAME`
- `SMTP_PASSWORD`
- `PORT`

Important:

- Change the default admin password before production use.
- Verify SMTP settings before enabling email notifications.
- If the port changes, update firewall rules and shared URLs accordingly.

---

## Step 3: Start the Application

Double-click `start-exe.bat`.

The application will start in a console window. Keep that window open while the application is in use.

Default URL:

```text
http://localhost:5000
```

---

## Step 4: Access the Application

Open a browser and go to:

```text
http://localhost:5000
```

Login with the credentials configured in `settings.ini`.

---

## Step 5: Stop the Application

Use `stop-native.bat` to stop the application.

---

## Network Access

If other users on the same network need access:

1. Run `open-firewall.bat` as Administrator
2. Run `get-network-info.bat`
3. Share the displayed URL

Typical URLs:

```text
http://192.168.1.100:5000
http://COMPUTER-NAME:5000
```

---

## Backup Guidance

Back up these files regularly:

- `settings.ini`
- `data\inventory.json`
- `data\history.json`

These files contain the runtime configuration and business data.

---

## Troubleshooting

### The browser cannot open the application

Check these items:

1. `start-exe.bat` is still running
2. No other application is already using port 5000
3. The browser is opening `http://localhost:5000`

### Other users cannot connect

Check these items:

1. `open-firewall.bat` was run as Administrator
2. The correct IP address was shared
3. Both machines are on the same network

### Email notifications do not work

Check these items:

1. SMTP server and port are correct
2. TLS setting matches the mail server requirement
3. Username and password are valid if authentication is required

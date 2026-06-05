# Quick Deployment Summary

## Supported Packaging Flow

1. Run `build-exe.bat`
2. Deliver the generated `client_package` folder
3. Client runs `start-exe.bat`

---

## Developer Steps

### Step 1: Build

Run:

```bat
build-exe.bat
```

### Step 2: Verify the output

Confirm the generated package contains:

```text
client_package/
├── lab_inventory.exe
├── start-exe.bat
├── stop-native.bat
├── settings.ini
├── open-firewall.bat
├── get-network-info.bat
└── data/
```

### Step 3: Test locally

1. Run `client_package\start-exe.bat`
2. Open `http://localhost:5000`
3. Confirm the application works

### Step 4: Deliver

Send the full `client_package` folder to the client.

---

## Client Steps

1. Place the delivered `client_package` folder on the machine
2. Edit `settings.ini` if needed
3. Run `start-exe.bat`
4. Open `http://localhost:5000`

If network access is required:

1. Run `open-firewall.bat` as Administrator
2. Run `get-network-info.bat`
3. Share the shown URL

---

## Update Flow

When a new version is released:

1. Rebuild using `build-exe.bat`
2. Send the refreshed `client_package`
3. Keep the client's `settings.ini` and `data` files unless they must be replaced intentionally

---

## Key Benefit

The delivered package contains the application executable and supporting files only. The project source code is not part of the client delivery folder.
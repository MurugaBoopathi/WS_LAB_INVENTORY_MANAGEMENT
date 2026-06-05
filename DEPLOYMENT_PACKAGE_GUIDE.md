# Lab Inventory Management Tool - Deployment Package Guide

## Supported Delivery Model

The application is delivered as a packaged Windows executable.

The supported workflow is:

1. Build the executable package with `build-exe.bat`
2. Deliver the generated `client_package` folder to the client
3. Client runs `start-exe.bat`

---

## Developer Workflow

### Step 1: Build the package

From the project root, run:

```bat
build-exe.bat
```

This script:

- creates or reuses the local virtual environment
- installs the required build tools
- builds `lab_inventory.exe` with PyInstaller
- recreates the `client_package` folder
- copies configuration, data, and helper scripts into the package

### Step 2: Review the generated package

After the build, the output folder is:

```text
client_package\
```

Expected contents:

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

### Step 3: Deliver the package

Send the full `client_package` folder to the client.

Recommended delivery methods:

1. Zip the `client_package` folder and send it through your approved channel.
2. Copy it to a shared drive or USB drive.

---

## Update Workflow

When you make code changes:

1. Update the source code.
2. Run `build-exe.bat` again.
3. Deliver the new `client_package` folder or at minimum the updated `lab_inventory.exe`.

If only the executable is replaced, the client should keep:

- `settings.ini`
- `data\inventory.json`
- `data\history.json`

---

## Client Workflow

The client should:

1. Extract or copy the delivered `client_package` folder.
2. Update `settings.ini` if needed.
3. Run `start-exe.bat`.
4. Open `http://localhost:5000` in a browser.

For network sharing:

1. Run `open-firewall.bat` as Administrator.
2. Run `get-network-info.bat`.
3. Share the displayed URL.

---

## Benefits of the Current Approach

- No container runtime dependency on the client machine
- No Python installation on the client machine
- Simple update path
- Source code is not delivered to the client
- Configuration and data stay in editable local files

---

## Recommended Delivery Checklist

Before sending the package:

1. Run `build-exe.bat` successfully.
2. Start the app locally with `start-exe.bat`.
3. Confirm login works.
4. Confirm `settings.ini` is correct for the client.
5. Confirm the `data` folder is present.

---

## Notes

- `client_package` is a generated deployment folder.
- `build-exe.bat` is the single supported packaging script.
- `start-exe.bat` is the supported launcher for delivered packages.

# Network Access Guide - Lab Inventory Management Tool

## Purpose

This guide explains how to share the EXE-based application with other users on the same network.

---

## Quick Steps

1. Start the application with `start-exe.bat`
2. Run `open-firewall.bat` as Administrator
3. Run `get-network-info.bat`
4. Share the displayed URL

---

## Recommended URL Format

Use the host machine IP address when possible.

Examples:

- `http://192.168.1.100:5000`
- `http://10.0.0.50:5000`

You can also try the computer name:

- `http://COMPUTER-NAME:5000`

---

## Find the Host Address

### Easy method

Run:

```bat
get-network-info.bat
```

### Manual method

To find the IP address:

```powershell
ipconfig
```

To find the computer name:

```powershell
hostname
```

---

## Firewall Setup

Other machines cannot connect unless the application port is open in Windows Firewall.

### Automatic method

1. Right-click `open-firewall.bat`
2. Select **Run as administrator**
3. Complete the script

### Manual method

Run this in an elevated terminal:

```powershell
netsh advfirewall firewall add rule name="Lab Inventory Tool" dir=in action=allow protocol=TCP localport=5000
```

If you changed the port in `settings.ini`, use that port instead of `5000`.

---

## Verification

On the host machine, confirm local access:

```powershell
curl http://localhost:5000
```

Check whether the port is listening:

```powershell
netstat -ano | findstr :5000
```

---

## Troubleshooting

### Other users cannot reach the site

Check these items:

1. `start-exe.bat` is still running on the host machine
2. `open-firewall.bat` was run as Administrator
3. The IP address from `get-network-info.bat` is correct
4. Both machines are on the same network

### Localhost works but network access does not

This usually means:

1. Firewall rule is missing
2. Wrong IP address was shared
3. Network policy is blocking the port

### Computer name does not work

Use the IP address instead.

---

## Operating Notes

If you change the application port in `settings.ini`:

1. Restart the application
2. Open the new port in the firewall
3. Share the updated URL

Example if port changed to 8080:

```text
http://192.168.1.100:8080
```

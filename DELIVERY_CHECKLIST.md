# Client Delivery Checklist

Use this checklist for the supported EXE-based delivery process.

---

## Pre-Delivery

### Build and test
- [ ] Run `build-exe.bat`
- [ ] Confirm `client_package` was recreated successfully
- [ ] Start the application locally with `start-exe.bat`
- [ ] Confirm login works in the browser
- [ ] Confirm the app loads inventory and history data correctly
- [ ] Test email functionality with the intended SMTP settings if required

### Configuration review
- [ ] Update `settings.ini` for the client if needed
- [ ] Change the default admin password
- [ ] Verify `PORT` is correct
- [ ] Verify email recipients and SMTP settings

### Documentation review
- [ ] Update `CLIENT_INSTALL_GUIDE.md` if client-specific notes are needed
- [ ] Verify `NETWORK_ACCESS_GUIDE.md` is still accurate
- [ ] Verify support contact information in `SUPPORT.txt`

---

## Delivery Package Contents

Required items:

- [ ] `client_package\lab_inventory.exe`
- [ ] `client_package\start-exe.bat`
- [ ] `client_package\stop-native.bat`
- [ ] `client_package\settings.ini`
- [ ] `client_package\open-firewall.bat`
- [ ] `client_package\get-network-info.bat`
- [ ] `client_package\data\inventory.json`
- [ ] `client_package\data\history.json`

Optional supporting documents:

- [ ] `CLIENT_INSTALL_GUIDE.md`
- [ ] `NETWORK_ACCESS_GUIDE.md`
- [ ] `README_CLIENT.txt`
- [ ] `SUPPORT.txt`
- [ ] `LICENSE.txt`

---

## Package Validation

- [ ] No obsolete deployment files included
- [ ] No source `.py` files included for the client package
- [ ] No local development folders included accidentally
- [ ] No secrets or personal credentials included in delivered settings
- [ ] Client package launches from a clean folder

---

## Delivery Methods

- [ ] ZIP the `client_package` folder if sending electronically
- [ ] Upload to approved shared storage or copy to USB
- [ ] Verify the transferred package opens correctly after delivery

---

## Client Handover

- [ ] Tell the client to keep the full folder together
- [ ] Tell the client to edit `settings.ini` if required
- [ ] Tell the client to run `start-exe.bat`
- [ ] Tell the client to use `stop-native.bat` to stop the app
- [ ] If network sharing is needed, tell the client to run `open-firewall.bat` and `get-network-info.bat`

---

## Update Delivery

When sending an update:

- [ ] Rebuild using `build-exe.bat`
- [ ] Send the full refreshed `client_package` folder or at minimum the new `lab_inventory.exe`
- [ ] Tell the client not to overwrite their working `settings.ini` and `data` files unless intended

---

## Final Sign-Off

- [ ] Build completed successfully
- [ ] Package tested successfully
- [ ] Delivery package prepared
- [ ] Client instructions prepared

Delivery Date: _______________

Client Name: _______________

Delivered By: _______________

**Notes**: 
_______________________________________________
_______________________________________________
_______________________________________________

---

**Keep this checklist for your records!**

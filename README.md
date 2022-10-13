# relay-controller
Console client to control mp709/RODOS-3 relay.

## Linux configuration
Before start the usage the tool, you should prepare the system.

1. Add permissions for the USB device by adding following line to the /etc/udev/rules.d/10-local.rules:
```bash
SUBSYSTEMS=="usb", ATTRS{idVendor}=="<vendor of the relay>", "ATTRS{idProduct}=="<product of the relay>", GROUP="usbrelay", MODE="0666"
```

2. Create user group:
```bash
sudo groupadd usbrelay
```

3. Add current user to the group:
```bash
sudo adduser $USER usbrelay
```

4. Reload rules:
```bash
sudo udevadm control --reload-rules && sudo udevadm trigger
```

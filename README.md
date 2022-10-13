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

# Supported devices
- mp709
- RODOS-1
- RODOS-1B
- RODOS-1N
- RODOS-3
- RODOS-3 mini
- RODOS-3 USB B
- RODOS-3B
- RODOS-3BN
- RODOS-4R6 N
- RODOS-4R6 NS
- RODOS-4R10 N
- RODOS-4R16 DIN MG
- RODOS-4R16 N

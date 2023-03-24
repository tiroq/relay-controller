# relay-controller
The relay-controller is a console client that allows you to control mp709/RODOS-3 relay. It is a powerful tool that can be used to manage and control the power of your devices.

## Linux configuration
Before you start using the relay-controller, you should prepare your system. Here are some steps that you can follow:

1. Add permissions for the USB device by adding following line to the /etc/udev/rules.d/10-local.rules:
```bash
SUBSYSTEMS=="usb", ATTRS{idVendor}=="<vendor of the relay>", "ATTRS{idProduct}=="<product of the relay>", GROUP="usbrelay", MODE="0666"
```
This line will give the necessary permissions to the USB device, so you can use it with the relay-controller.

2. Create user group:
```bash
sudo groupadd usbrelay
```
This command will create a user group called "usbrelay".

3. Add current user to the group:
```bash
sudo adduser $USER usbrelay
```
This command will add the current user to the "usbrelay" group.

4. Reload rules:
```bash
sudo udevadm control --reload-rules && sudo udevadm trigger
```
This command will reload the rules, so the changes can take effect.

By following these steps, you can ensure that the relay-controller is properly configured and ready to use.

# Supported devices
The relay-controller supports a wide range of devices, including:
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

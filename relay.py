#!/usr/bin/env python3
import argparse
import enum
import sys

import usb
from loguru import logger

GET_REPORT = 0x01
SET_REPORT = 0x09

HID_REQ_TO_HOST = 0xA1
HID_REQ_TO_DEV = 0x21

REPORT_TYPE_INPUT = 0x100
REPORT_TYPE_OUTPUT = 0x200
REPORT_TYPE_FEATURE = 0x300


class State(enum.Enum):
    off = 0
    on = 1
    no_change = 3
    toggle = 4


class Relay:
    GET_INFO = (0x1D, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00)
    SET_PORT_ON = (0xE7, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00)
    SET_PORT_OFF = (0xE7, 0x19, 0x00, 0x00, 0x00, 0x00, 0x00)
    GET_PORT = (0x7E, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00)

    REPORT_LEN = 8

    def __init__(self, device):
        self.handle = None

        conf = device.configurations[0]
        self.dev = device
        self._device_id = device.idProduct
        self.interface = conf.interfaces[0][0]
        self.interface_num = self.interface.interfaceNumber

        self.open()

    def __del__(self):
        if self.handle:
            self.close()

    def __str__(self):
        if self.handle:
            info = self.get_info()
            return f" family={info['family']}, version={info['version']}, id={info['id']}, state={self.get_state()}"
        else:
            return "No relays"

    @property
    def device_id(self):
        return self._device_id

    def open(self):
        if self.handle:
            self.close()

        self.handle = self.dev.open()
        try:
            self.handle.detachKernelDriver(self.interface)
        except:
            pass

        self.handle.setConfiguration(self.dev.configurations[0])
        self.handle.claimInterface(self.interface)
        self.handle.setAltInterface(self.interface)

    def close(self):
        if self.handle:
            try:
                self.handle.releaseInterface()
            except usb.core.USBError as e:
                logger.warning(
                    f"Permissions required:\n\tAdd rule to the /etc/udev/rules.d/10-local.rules file:\n"
                    "\t\t'SUBSYSTEMS==\"usb\", ATTRS{idVendor}=="
                    f"\"{self.dev.idVendor:#04x}\", "
                    "ATTRS{idProduct}=="
                    f"\"{self.dev.idProduct:#04x}\", "
                    "GROUP=\"usbrelay\", MODE=\"0666\"'\n"
                    "\tCreate group:\n\t\tsudo groupadd usbrelay\n"
                    "\tAdd current user to the group:\n\t\tsudo adduser $USER usbrelay\n"
                    "\tReload rules:\n\t\tsudo udevadm control --reload-rules && sudo udevadm trigger"
                )
                logger.exception(e)
                sys.exit(3)

        self.handle = None
        self.dev = None
        self.interface = None

    def set_state(self, state: bool, timeout: int = 100):
        buffer = self.SET_PORT_ON if state else self.SET_PORT_OFF
        logger.info(f"Set state to {state} for {self.device_id} device")
        return self.handle.controlMsg(
            requestType=HID_REQ_TO_DEV, request=SET_REPORT, buffer=buffer,
            value=REPORT_TYPE_FEATURE, index=self.interface_num, timeout=timeout)

    def get_state(self, timeout: int = 100):
        self.handle.controlMsg(requestType=HID_REQ_TO_DEV, request=SET_REPORT, buffer=self.GET_PORT,
                               value=REPORT_TYPE_FEATURE, index=self.interface_num, timeout=timeout)

        buffer = self.handle.controlMsg(requestType=HID_REQ_TO_HOST, request=GET_REPORT, buffer=self.REPORT_LEN,
                                        value=REPORT_TYPE_FEATURE, index=self.interface_num, timeout=timeout)

        port_on = 0x00
        # port_off = 0x19
        state = (buffer[1] == buffer[2]) and (buffer[1] == port_on)
        logger.debug(f"State of {self.device_id} is {state}")
        return state

    def get_info(self, timeout=100):
        self.handle.controlMsg(requestType=HID_REQ_TO_DEV, request=SET_REPORT, buffer=self.GET_INFO,
                               value=REPORT_TYPE_FEATURE, index=self.interface_num, timeout=timeout)

        buffer = self.handle.controlMsg(requestType=HID_REQ_TO_HOST, request=GET_REPORT, buffer=self.REPORT_LEN,
                                        value=REPORT_TYPE_FEATURE, index=self.interface_num, timeout=timeout)

        family = buffer[1]
        version = buffer[2] + buffer[3] * (1 << 8)
        device_id = buffer[7] + buffer[6] * (1 << 8) + buffer[5] * (1 << 16) + buffer[4] * (1 << 24)

        return {'family': family, 'version': version, 'id': device_id}


class DevicesManager:
    def __init__(self):
        self._relays = self.get_devices()
        if len(self._relays) == 0:
            logger.info("Can't detect any relay")
            raise RuntimeWarning

    def get_devices(self):
        busses = usb.busses()
        relays = []
        for bus in busses:
            for dev in bus.devices:
                try:
                    xdev = usb.core.find(idVendor=dev.idVendor, idProduct=dev.idProduct)
                    product = xdev.product
                except ValueError:
                    logger.debug(f"Device Vendor: {dev.idVendor}({dev.idVendor:#04x}), "
                                 f"Product: {dev.idProduct}({dev.idProduct:#04x}) skipped")
                    continue
                if product is None:
                    logger.debug(f"Device Vendor: {dev.idVendor}({dev.idVendor:#04x}), "
                                 f"Product: {dev.idProduct}({dev.idProduct:#04x}) skipped")
                    continue
                if product.startswith('RODOS-3'):
                    logger.info(f"Relay detected Vendor: {dev.idVendor}({dev.idVendor:#04x}), "
                                f"Product: {dev.idProduct}({dev.idProduct:#04x})")
                try:
                    relay = Relay(dev)
                except ValueError:
                    pass
                else:
                    relays.append(relay)
        return relays

    def do(self, action, device_id: int = 0):
        for relay in self._relays:
            if device_id == 0 or relay.device_id == device_id:
                logger.info(f"Do {action = } for relay with {relay.device_id = }")
                if action in (State.on.name, State.off.name):
                    relay.set_state(action == State.on.name)
                elif action == State.toggle.name:
                    relay.set_state(not relay.get_state())


def main():
    parser = argparse.ArgumentParser(description='relay controller')
    parser.add_argument('action', type=str, choices=[State.on.name, State.off.name,
                                                     State.toggle.name, State.no_change.name],
                        help='Change state of the relay to the required one.')
    parser.add_argument('--log-level', type=str, choices=['INFO', 'DEBUG', 'WARNING', 'ERROR'],
                        default='INFO',
                        help='Change state of the relay to the required one.')
    parser.add_argument('-i', '--id', required=False, type=int, default=0,
                        help='id of target relay.')
    args = parser.parse_args()
    logger.remove()
    logger.add(sys.stderr, level=args.log_level)

    DevicesManager().do(action=args.action, device_id=args.id)


if __name__ == "__main__":
    main()

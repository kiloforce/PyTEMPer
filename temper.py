"""
Temper - a class for managing a TEMPer USB temperature sensor

Original by Bill Mania <bill@manialabs.us>

Source: http://www.manialabs.us/downloads/Temper.py
"""

import sys
import usb.core


class Temper:

    def __init__(self):
        self.devices = []
        self.calibrationConstant = 15
        self.units = 'C'

        self.device_list = usb.core.find(
            find_all=True, idVendor=0x1130, idProduct=0x660c)
        self.devices = [device for device in self.device_list]

        if self.devices is None:
            print('Unable to find a temperature device')
            return

        try:
            for device in self.devices:
                if device.is_kernel_driver_active(0):
                    device.detach_kernel_driver(0)
                if device.is_kernel_driver_active(1):
                    device.detach_kernel_driver(1)
        except Exception as e:
            pass

        for device in self.devices:
            try:
                device.set_configuration()
            except Exception as e:
                print("Error: Unable to setup the device")
                raise e

        nullTrailer = b'\x00' * 24
        firstMagicSequence = b'\n\x0B\x0C\x0D\x00\x00\x02\x00' + nullTrailer
        secondMagicSequence = b'\x54\x00\x00\x00\x00\x00\x00\x00' + nullTrailer
        thirdMagicSequence = b'\x00\x00\x00\x00\x00\x00\x00\x00' + nullTrailer
        fourthMagicSequence = b'\n\x0B\x0C\x0D\x00\x00\x01\x00' + nullTrailer

        for device in self.devices:
            bytesSent = device.ctrl_transfer(
                0x21, 9, 0x200, 0x1, firstMagicSequence, 32)
            bytesSent = device.ctrl_transfer(
                0x21, 9, 0x200, 0x1, secondMagicSequence, 32)
            for i in range(0, 7):
                bytesSent = device.ctrl_transfer(
                    0x21, 9, 0x200, 0x1, thirdMagicSequence, 32)
            bytesSent = device.ctrl_transfer(
                0x21, 9, 0x200, 0x1, fourthMagicSequence, 32)

    def setCalibration(self, calibrationConstant):
        self.calibrationConstant = calibrationConstant

    def setUnits(self, units='C'):
        self.units = units

    def getUnits(self):
        if self.units == 'C':
            return 'Celsius'
        elif self.units == 'F':
            return 'Fahrenheit'
        elif self.units == 'K':
            return 'Kelvin'
        else:
            return 'Unknown'

    def getTemperature(self, device):
        nullTrailer = b'\x00' * 24

        temperatureBuffer = device.ctrl_transfer(0xa1, 1, 0x300, 0x1, 256, 0)

        if len(temperatureBuffer) > 1:
            if temperatureBuffer[0] == 0 and temperatureBuffer[1] == 255:
                print("Failed to retrieve temperature")
                return 0.0

            temperature = (
                temperatureBuffer[0] << 8) + (temperatureBuffer[1] & 0xff) + self.calibrationConstant
            temperature = temperature * (125.0 / 32000.0)

            if self.units == 'F':
                temperature = (9.0 / 5.0 * temperature) + 32.0
            elif self.units == 'K':
                temperature += 273.15
            else:
                pass
        else:
            print("Failed to retrieve temperature")
            temperature = 0.0

        return temperature


if __name__ == '__main__':
    temper = Temper()

    for device in temper.devices:
        tempc = temper.getTemperature(device)
        tempcunits = temper.getUnits()
        tempf = (tempc * 9 / 5) + 32
        tempfunits = "Fahrenheit"
        devicebus = device.bus
        deviceaddress = device.address

        if len(sys.argv) < 2:
            print('%d:%d, %.2f %s / %.2f %s' %
                  (devicebus, deviceaddress, tempc, tempcunits, tempf, tempfunits))
        else:
            if sys.argv[1] == "-c":
                print('%.2f' % tempc)
            elif sys.argv[1] == "-C":
                print('%.0f' % tempc)
            elif sys.argv[1] == "-f":
                print('%.2f' % tempf)
            elif sys.argv[1] == "-F":
                print('%.0f' % tempf)
            else:
                print("Usage: %s [options]" % sys.argv[0])
                print("Options:")
                print("    -c  # report Celsius")
                print("    -C  # report Celsius rounded")
                print("    -f  # report Fahrenheit")
                print("    -F  # report Fahrenheit rounded")
                print("    -h  # Help")
                sys.exit(1)

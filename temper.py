"""
Temper - a class for managing a TEMPer USB temperature sensor

Bill Mania <bill@manialabs.us>

Source: http://www.manialabs.us/downloads/Temper.py
"""

import usb.core

class Temper():

    def __init__(self):

        self.calibrationConstant = 15
        self.units = 'C'

        self.devices = usb.core.find(
                find_all=True,
                idVendor = 0x1130,
                idProduct = 0x660c
                )
        
        if self.devices is None:
            print 'Unable to find a temperature device'
            return

        try:
            for device in self.devices:
                if device.is_kernel_driver_active(0):
                    device.detach_kernel_driver(0)
                    device.detach_kernel_driver(1)
        except Exception as e:
            #print "Exception: " + str(e)
            pass

        for device in self.devices:
            try:
                device.set_configuration()
            except Exception as e:
                print 'Unable to setup the device'
                print "Exception: " + str(e)
                return

        #
        # the following sequence appear to be necessary to
        # either calibrate or initialize the TEMPer, but I
        # have no idea why. therefore, I named them all "magic".
        #
        nullTrailer = ''
        for i in range(0, 24):
            nullTrailer = nullTrailer + chr(0)
        firstMagicSequence = chr(10) + chr(11) + chr(12) + chr(13)  + chr(0) + chr(0) + chr(2) + chr(0)
        firstMagicSequence = firstMagicSequence + nullTrailer
        secondMagicSequence = chr(0x54) + chr(0) + chr(0) + chr(0) + chr(0) + chr(0) + chr(0) + chr(0)
        secondMagicSequence = secondMagicSequence + nullTrailer
        thirdMagicSequence = chr(0) + chr(0) + chr(0) + chr(0) + chr(0) + chr(0) + chr(0) + chr(0)
        thirdMagicSequence = thirdMagicSequence + nullTrailer
        fourthMagicSequence = chr(10) + chr(11) + chr(12) + chr(13)  + chr(0) + chr(0) + chr(1) + chr(0)
        fourthMagicSequence = fourthMagicSequence + nullTrailer

        for device in self.devices:
            bytesSent = device.ctrl_transfer(
                0x21,
                9,
                0x200,
                0x1,
                firstMagicSequence,
                32
                )
            bytesSent = device.ctrl_transfer(
                0x21,
                9,
                0x200,
                0x1,
                secondMagicSequence,
                32
                )
            for i in range(0, 7):
                bytesSent = device.ctrl_transfer(
                    0x21,
                    9,
                    0x200,
                    0x1,
                    thirdMagicSequence,
                    32
                    )
            bytesSent = device.ctrl_transfer(
                0x21,
                9,
                0x200,
                0x1,
                fourthMagicSequence,
                32
                )

        return

    def setCalibration(self, calibrationConstant):
        self.calibrationConstant = calibrationConstant

        return

    def setUnits(self, units = 'C'):
        self.units = units

        return
        
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
        nullTrailer = ''
        for i in range(0, 24):
            nullTrailer = nullTrailer + chr(0)
 
        temperatureBuffer = device.ctrl_transfer(
            0xa1,
            1,
            0x300,
            0x1,
            256,
            0
            )

        if len(temperatureBuffer) > 1:
            temperature = int(temperatureBuffer[0] << 8) + int(temperatureBuffer[1] & 0xff) + self.calibrationConstant
            temperature = temperature * (125.0 / 32000.0)
            if self.units == 'F':
                temperature = 9.0 / 5.0 * temperature + 32.0
            elif self.units == 'K':
                temperature = temperature + 273.15
            else:
                pass

        else:
            print "Failed to retrieve temperature"
            temperature = 0.0

        return temperature
        
if __name__ == '__main__':
    temper = Temper()

    for device in temper.devices:
        tempc = temper.getTemperature(device)
        tempcunits = temper.getUnits()
        tempf = (tempc * 9/5) + 32
        tempfunits = "Fahrenheit"
        print '%0.2f %s / %0.2f %s' % (tempc, tempcunits, tempf, tempfunits)


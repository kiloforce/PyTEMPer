# PyTEMPer

Simple interface to USB TEMPer thermometer device

Multiple devices are supported, but as there is no way to uniquely identify them it may be difficult to keep them straight. 

![TEMPer Sensor](https://raw.github.com/kiloforce/markdowntest/master/temper.png)

## Installation

```
git clone https://github.com/kiloforce/PyTEMPer
cd PyTEMPer

# Get PyUSB (if you do not already have installed)
git clone https://github.com/walac/pyusb
ln -s pyusb/usb usb

# Run as root
sudo python temper.py
```

Make sure to run as root, or user with permission to usb device, otherwise: `usb.core.USBError: [Errno None] error sending control message: Operation not permitted`

## Fork

Source forked from: http://www.manialabs.us/downloads/Temper.py

## Todo

- [X] Support multiple devices

## Issues

May occur if you try to run as a non root user.  Either run as root, or give permission to USB dev device.
```
usb.core.USBError: [Errno None] error sending control message: Operation not permitted
```

May occur when device is first connected, give it a few minutes.  Do you have another monitor running?
```
usb.core.USBError: [Errno None] error sending control message: Device or resource busy
```

Fixed - due to buffer not being the right size.
```
usb.core.USBError: [Errno None] error sending control message: Value too large for defined data type
```

Hidden - due to check on kernel active failing
```
Unable to setup the device
```

## Changelog

* Support for multiple sensor devices
* Fixed "usb.core.USBError: [Errno None] error sending control message: Value too large for defined data type"
* Hide "Unable to setup the device"
* Report both Celsius and Fahrenheit


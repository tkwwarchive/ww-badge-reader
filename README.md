# wwkegerator
kegerator code for raspberry pi

code samples and bits taken from the following projects
https://learn.adafruit.com/adafruit-keg-bot/raspberry-pi-code
https://github.com/adafruit/Kegomatic
https://codeascraft.com/2014/06/24/device-lab-checkout-rfid-style/
https://github.com/etsy/rfid-checkout

Requirements
------------
NOTE: MAKE SURE TO CONVERT THE 5 VOLT SIGNAL TO THE RASPI TO 3.3 VOLTS BEFORE POWERING ON THE SYSTEM (Most card readers pull the line high, so even if not reading a card, it will send a 5 volt signal that can damage the RasPi)

1. The RFID Reader should be connected to the RasPi via GPIO (BCM) pins 17 and 18. Using a proper power supply to the RasPi, the 5 Volt out pin should be able to power the reader directly.

From the RFID Reader to the RasPi

      red/vcc -> pin 2
      black/ground -> pin 25
      green/data0 -> pin 17 (after voltage conversion)
      white/data1 -> pin 18 (after voltage conversion)

2. Connect the USB Keyboard and serial LCD screen (either over USB, or using GPIO 14). Install the pyserial library. 

      sudo pip install pyserial
      
3. Install the raspberry-gpio-python library.

      sudo apt-get install python-rpi.gpio

4. Install the WiringPi library. Download and instructions at: http://wiringpi.com

5. Run "make" in order to create the hid_gpio_reader binary. You can then test out the card reader code with 

      sudo ./hid_gpio_reader

6. Run the main application (sudo required for GPIO access)

      sudo python ./kegerator.py 

Parts List
----------
 * Raspberry PI
 * SDCard for Raspberry PI OS: [tested with Raspbian - Wheezy] (http://www.raspberrypi.org/downloads/)
 * [5v to 3.3v converter] (https://www.adafruit.com/product/757) 
 * Site Compatible RFID Reader (http://www.amazon.com/gp/product/B0041X3GSU)


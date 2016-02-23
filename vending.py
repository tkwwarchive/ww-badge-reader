#!/usr/bin/python
import os
import time
import math
import sys
import RPi.GPIO as GPIO
from flowmeter import *
import subprocess
import select
from boto.dynamodb2.table import Table
#import logging
#import hashlib
#from bitstring import BitStream, BitArray

#code samples and bits taken from the following projects
#https://learn.adafruit.com/adafruit-keg-bot/raspberry-pi-code
#https://github.com/adafruit/Kegomatic
#https://codeascraft.com/2014/06/24/device-lab-checkout-rfid-style/
#https://github.com/etsy/rfid-checkout

lefttap = "EMPTY"
righttap = "Sam Adams"

# Path to the compiled C code for card reading (should be in same directory if you ran "make")
READER_APP = './hid_gpio_reader'

#setup user table from dynamodb
users = Table('wwusercards')
pours = Table('wwkegbotpours')

#wiegand bit masks
#facilitymask=BitArray(bin="0000000011111111100000000000000000")
#cardmask=BitArray(bin="0000000000000000011111111111111110")
#paritymask=BitArray(bin="0000000000000000000000000000000001")

#boardRevision = GPIO.RPI_REVISION
GPIO.setmode(GPIO.BCM) # use real GPIO numbering
GPIO.setup(23,GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.setup(24,GPIO.IN, pull_up_down=GPIO.PUD_UP)
#valve control pin
GPIO.setup(22,GPIO.OUT)
GPIO.output(22,1)
GPIO.setup(25,GPIO.OUT)
GPIO.output(25,1)

# set up the flow meters
fm = FlowMeter('metric', 'beer')
fm2 = FlowMeter('metric', 'beer')

# Beer, on Pin 23.
def doAClick(channel):
  currentTime = int(time.time() * FlowMeter.MS_IN_A_SECOND)
  if fm.enabled == True:
    fm.update(currentTime)

# Beer, on Pin 24.
def doAClick2(channel):
  currentTime = int(time.time() * FlowMeter.MS_IN_A_SECOND)
  if fm2.enabled == True:
    fm2.update(currentTime)

GPIO.add_event_detect(23, GPIO.RISING, callback=doAClick, bouncetime=20) # Beer, on Pin 23
GPIO.add_event_detect(24, GPIO.RISING, callback=doAClick2, bouncetime=20) # Root Beer, on Pin 24

# logger = logging.getLogger('rfid_application')
# logger.setLevel(logging.DEBUG)
# fh = logging.FileHandler(constants.LOG_FILE)
# fh.setLevel(logging.DEBUG)
# formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
# fh.setFormatter(formatter)
# logger.addHandler(fh)

#tag_handler = TagHandler()

f = None
p = None
bits = ''


print "Ready. Please Present Card..."
try:
    while 1:
        f = subprocess.Popen(READER_APP,\
                stdout=subprocess.PIPE,stderr=subprocess.PIPE)
        p = select.poll()
        p.register(f.stdout)
#        logger.debug('GPIO Process Started')

        while 1:
            if p.poll(1):
                line = f.stdout.readline()
                if (len(line) > 1):
                    print line
                    line = line.rstrip()
                    # Next line depends on what we have in our C program for the GPIO data
                    # You will likely need to update this in the future if that app changes
                    bits = line[12:]

                    # Convert the string of bits to an int (removes leading zeros)
                    card_int = int(str(bits),2)
#                    logger.debug('New Tag: ' + str(bits))
                    print "--NEW TAG--"
                    print time.asctime(time.localtime(time.time()))
                    print "Binary:",bits
                    print "int:",card_int
                    currentTime = int(time.time() * FlowMeter.MS_IN_A_SECOND)
#                    logger.info('Tag=' + str(card_int))
                    if (len(list(users.query_2(cardnumber__eq=card_int))) == 1):
                       # do valve open and start timer
                       fm.thisPour = 0.0
                       # open valve
                       GPIO.output(22,0)
                       # sleep for 30 sec
                       while (int(time.time() * FlowMeter.MS_IN_A_SECOND)) < (currentTime + 15000):
                          time.sleep(0.1)
                       # close valve and report volume poured
                       GPIO.output(22,1)
                       pourvol=fm.getFormattedThisPour()
#                       logger.info('Pour volume='+pourvol)
                       print "Pour volume:",pourvol
                       pours.put_item(data={'cardnumber':card_int, 'datetime':currentTime, 'beverage':righttap, 'pour':pourvol})
                       fm.thisPour = 0.0
                    else:
                       #no valid card number in database
                       pours.put_item(data={'cardnumber':card_int, 'datetime':currentTime, 'beverage':righttap, 'pour':"-1"})
                       print "Invalid card:",card_int
                    bits = '0'
                    #break
            time.sleep(0.1)

        p.unregister(f.stdout)
        f.terminate()
#        logger.debug('GPIO Process Terminated')
        time.sleep(2)

except KeyboardInterrupt:
    print "Clean Exit By user"
#    logger.debug('Clean Exit By user')
    p.unregister(f.stdout)
    f.terminate()
    GPIO.cleanup()
    sys.exit()
    

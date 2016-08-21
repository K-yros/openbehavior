#!/usr/bin/python

# Copyright 2016 University of Tennessee Health Sciences Center
# Author: Matthew Longley <mlongle1@uthsc.edu>
# Author: Hao Chen <hchen@uthsc.edu>
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as
# published by the Free Software Foundation, either version 3 of the
# License, or(at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

# BEGIN IMPORT PRELUDE
import sys
import getopt
import time
from threading import Timer
import subprocess32 as subprocess
import RPi.GPIO as gpio
import Adafruit_MPR121.MPR121 as MPR121
import pumpcontrol
import serial
import touchsensor
import datalogger
import os
import random
import Adafruit_CharLCD as LCD
# END IMPORT PRELUDE

# BEGIN CONSTANT DEFINITIONS
TIR = int(16) # Pin 36
SW1 = int(26) # Pin 37
SW2 = int(20) # Pin 38
TOUCHLED = int(12) #pin 32
MOTIONLED= int(6) #pin 31
# END CONSTANT DEFINITIONS

# BEGIN GLOBAL VARIABLES
touchcounter = 0
ratio = 10
timeout = 20
pumptimedout = False
sessionLength=60*60*1 # one hour assay
# END GLOBAL VARIABLES

def initLCD():
	# Raspberry Pi pin configuration:
	lcd_rs        = 18  # RPi PIN 12 // LCD pin 4 
                            # RPi PIN 14 // LCD pin 5 
	lcd_en        = 23  # RPi PIN 16 // LCD pin 6
	lcd_d4        = 24  # RPi PIN 18 // LCD pin 11
	lcd_d5        = 25  # RPi PIN 22 // LCD pin 12
	lcd_d6        =  8  # RPi PIN 24 // LCD pin 13
	lcd_d7        =  7  # RPi PIN 26 // LCD pin 14
	lcd_backlight =  4 
	# Define LCD column and row size for 16x2 LCD.
	lcd_columns = 16
	lcd_rows    =  2
	# Initialize the LCD using the pins above.
	lcd = LCD.Adafruit_CharLCD(lcd_rs, lcd_en, lcd_d4, lcd_d5, lcd_d6, lcd_d7, lcd_columns, lcd_rows, lcd_backlight)
	lcd.clear()
	return lcd 

def mesg(m):
	datetime=time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
	lcd.clear()
	lcd.message(m + "\n"  + datetime)

def printUsage():
	print(sys.argv[0] + ' -t <timeout> -f <fixed ratio>')
	
def resetPumpTimeout():
	global pumptimedout
	pumptimedout = False
	
def blinkTouchLED(duration):
	gpio.output(TOUCHLED, gpio.HIGH)
	time.sleep(duration)
	gpio.output(TOUCHLED, gpio.LOW)

def ReadRFID(path_to_sensor) :
	baud_rate = 9600 
	time_out = 0.05
	uart = serial.Serial(path_to_sensor, baud_rate, timeout = time_out)
	uart.close()
	uart.open()
	uart.flushInput()
	uart.flushOutput()
	print(path_to_sensor + " initiated")
	Startflag = "\x02"
	Endflag = "\x03"
	while True:
		Z = 0
		Tag = 0
		ID = ""
		Z = uart.read()
		if Z == Startflag:
			for Counter in range(13):
				Z = uart.read()
				ID = ID + str(Z)
			ID = ID.replace(Endflag, "" ) 
			if int(ID, 16) != 0:
				if len(ID) > 8:
					ID=ID[-8:]
					print "RFID  detected: "+ ID
					return (ID)

# Parse command line arguments
try:
	opts, args = getopt.getopt(sys.argv[1:], "hf:t:")
except getopt.GetoptError:
	printUsage()
	sys.exit(2)
for opt, arg in opts:
	if opt == '-f':
		ratio = int(arg)
	elif opt == '-t':
		timeout = int(arg)
	elif opt == '-h':
		printUsage()
		sys.exit()



# variable ratio
variable_ratio=1

# Initialize GPIO
gpio.setwarnings(False)
gpio.setmode(gpio.BCM)

# Setup switch pins
gpio.setup(SW1, gpio.IN, pull_up_down=gpio.PUD_DOWN)
gpio.setup(SW2, gpio.IN, pull_up_down=gpio.PUD_DOWN)
gpio.setup(TIR, gpio.IN, pull_up_down=gpio.PUD_DOWN)
gpio.setup(TOUCHLED, gpio.OUT)
gpio.setup(MOTIONLED, gpio.OUT)

# initiate LCD
lcd=initLCD()
mesg("Prog. Started")

# Initialize pump
pump = pumpcontrol.Pump(gpio)

# enable the switches to move the pump
subprocess.call("sudo python /home/pi/openbehavior/pump-control/python/pumpmove.py" + " &", shell=True)

# Run the deviceinfo script
mesg("Hurry up, Wifi!")
os.system("/home/pi/openbehavior/wifi-network/deviceinfo.sh")
print ("Device info updated")

# Initialize touch sensor
tsensor = touchsensor.TouchSensor()

# turn lights on to indicate ready to run
gpio.output(TOUCHLED, gpio.HIGH)
gpio.output(MOTIONLED, gpio.HIGH)

#device id
dId=open("/home/pi/deviceid")
deviceId=dId.read().strip()

# wait for RFID scanner to get RatID
mesg("Pls scan RFID")
RatID=ReadRFID("/dev/ttyAMA0")
mesg("RatID: "+ RatID)
print (RatID)

#turn lights off to indicate RFID recieved
mesg("Session Started")
gpio.output(TOUCHLED, gpio.LOW)
gpio.output(MOTIONLED, gpio.LOW)


# session id, must be incremented the data loggers 
with open ("/home/pi/sessionid", "r+") as f:
    storedSessionID=f.read().strip()
    sessionID=int(storedSessionID)+1  
    f.seek(0)
    f.write(str(sessionID))
    f.close()


# start motion sensor Note: motion sensor needs to be started before session ID is incremented
#print ("staring motion sensor")
subprocess.call("sudo python /home/pi/openbehavior/pump-control/python/motion.py " +  " -SessionLength " + str(sessionLength) + " -RatID " + RatID+ " &", shell=True)

# Initialize data logger 
dlogger = datalogger.LickLogger()
dlogger.createDataFile(RatID)

# Get start time
sTime = time.time()

# initiate variables
act=0
ina=0
rew=0
lapse=0 
updateTime=0

def showdata():
	mins=int((sessionLength-lapse)/60)
	mesg("B" + deviceId[-2:]+  "S"+str(sessionID) + " " + RatID[-4:] + " " + str(mins) + "Left\n"+ "a" + str(act)+"i"+str(ina) + "r" +  str(rew) + "Rt"+ str(ratio))
	return time.time()

while lapse < sessionLength:
	lapse= time.time() - sTime
	time.sleep(0.05) # set delay to adjust sensitivity of the sensor.
	i = tsensor.readPinTouched()
	if i == 1:
		act+=1
		blinkTouchLED(0.03)
		dlogger.logEvent("ACTIVE", lapse)
		if not pumptimedout:
			touchcounter += 1
			if touchcounter == ratio:
				rew+=1
				updateTime=showdata()
				dlogger.logEvent("REWARD", lapse, ratio)
				touchcounter = 0
				pumptimedout = True
				pumpTimer = Timer(timeout, resetPumpTimeout)
				pumpTimer.start()
				subprocess.call('python /home/pi/openbehavior/pump-control/python/blinkenlights.py &', shell=True)
				pump.move(0.08)
				if variable_ratio:
					ratio=random.randint(1,20)
			else:
				updateTime=showdata()
	elif i == 2:
		ina+=1
		dlogger.logEvent("INACTIVE", lapse)
		blinkTouchLED(0.05)
		updateTime=showdata()
	elif time.time() - updateTime > 60:
		updateTime=showdata()

dlogger.logEvent("SessionEnd", lapse)
mesg("B" + deviceId[-2:]+  "S"+str(sessionID) + " " + RatID[-4:] + " Done!\n" + "a" + str(act)+"i"+str(ina) + "r" +  str(rew)) 
subprocess.call('/home/pi/openbehavior/wifi-network/rsync.sh &', shell=True)

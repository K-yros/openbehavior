#!/usr/bin/python

import RPi.GPIO as gpio
import time
import os
import sys
import Adafruit_MPR121.MPR121 as MPR121
import random
import Adafruit_CharLCD

	
def initTouch():
	cap = MPR121.MPR121()
	if not cap.begin():
		print "Error initializing MPR121.  Check your wiring!"
        lcd.message("Touch Sensor Connection Error")
		sys.exit(1)
	return cap

def updatelcd(active, inactive, seconds):
    minutes=str(int(seconds/60))
    lcd.clear()
    lcd.message("Act:" + active + "Ina" + inactive + "\n" + "at " minutes + "minutes" )


def createDataFiles():
	with open(touchDataFile,"a") as f:
		f.write("#Session Started on " +time.strftime("%Y-%m-%d\t%H:%M:%S\t", time.localtime())+"\n")
        f.write("boxid\tRatID\tSpout\tlapsed\n")
		f.close()

def touchSensor():
    active=0
    inactive=0
    sessionLength = 60 * 60
	while time.time() - start < sessionLength:
		lapsed = time.time() - start
		if cap.is_touched(1):
            active+=1
            updatelcd(active, inactive, lapsed)
			with open(touchDataFile,"a") as f:
				f.write(str(deviceid) + "\t" + "ratID\tactive\t" +  str(lapsed) + "\n")
				f.close()
				time.sleep(0.20)
		elif cap.is_touched(0):
            inactive+=1
			lapsed=time.time()-start
            updatelcd(active, inactive, lapsed)
			with open(touchDataFile,"a") as f:
				f.write(str(deviceid) + "\t" + "ratID\tinactive\t" +  str(lapsed) + "\n")
				f.close()
			time.sleep(0.20)
    updatelcd(active, inactive, lapsed)

def setupPins():
    LedActive=11
    LedInactive=12
	gpio.setwarnings(False)
	gpio.setmode(gpio.BOARD)
	gpio.setup(LedActive, gpio.OUT)
	gpio.setup(LedInactive, gpio.OUT)

if __name__ == '__main__':
    os.system("python /home/pi/openbehavior/wifi-networks/deviceinfo.sh &")
    os.system("python /home/pi/openbehavior/extinction/cuelights.py &")
    setupPins()
    initTouch()
    createDataFile()
	touchSensor()
	# finishing the data files
	# open data file
	with open(touchDataFile,"a") as f:
    f.write("#Session Ended on " +time.strftime("%Y-%m-%d\t%H:%M:%S\t", time.localtime())+"\n")
	f.close()
    time.sleep(5) # wait for motion.py to stop
    os.fsync(f)
	os.system('/home/pi/openbehavior/wifi-network/rsync.sh')



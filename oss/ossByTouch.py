#!/usr/bin/env python2

import RPi.GPIO as gpio
import serial
import time
import os
import gc
import sys
import Adafruit_MPR121.MPR121 as MPR121
import subprocess
import random

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
		Zeichen = 0
		Tag = 0
		ID = ""
		Zeichen = uart.read()
		if Zeichen == Startflag:
			for Counter in range(13):
				Zeichen = uart.read()
				ID = ID + str(Zeichen)
			ID = ID.replace(Endflag, "" ) 
			print "RFID  detected: "+ ID
			return (ID)

def initTouch():
	cap = MPR121.MPR121()
	if not cap.begin():
		print 'Error initializing MPR121.  Check your wiring!'
		sys.exit(1)
#		cap.set_thresholds(25,25)
	return cap

def touchSensor():
	timeout=10
	rewardtime=start-timeout #to ensure the first touch of the session triggers the reward immediately
	while time.time() - start < sessionLength:
		sessiontime = time.time() - start
		if cap.is_touched(1):
			subprocess.call("sudo python /home/pi/openbehavior/oss/touchled.py &", shell=True)
			if (time.time()-rewardtime>timeout):
				rewardtime=time.time()
				subprocess.call("sudo python /home/pi/openbehavior/oss/blink.py " + " -datafile "+  touchDataFile + " -RatID " + RatID +  " -start " + str(start) + " -interval " + str(timeout)  + " &", shell=True)
				timeout=random.randint(1,10) ## generate next timeout period 
				print ("reward given, next interval is" + str(timeout)) 
				time.sleep(0.20)
			else:
				print "active pin is touched"
				with open(touchDataFile,"a") as f:
					lapsed=time.time()-start
					f.write(RatID + "\tactive\t" + time.strftime("%Y-%m-%d\t%H:%M:%S", time.localtime()) + "\t" + str(lapsed) + "\t" + boxid + "\t\t\t\t\t\t\n")
					f.close()
				time.sleep(0.20)
		elif cap.is_touched(0):
			#subprocess.call("sudo python /home/pi/oss/touchled.py &", shell=True)
			print "inactive is touched"
			with open(touchDataFile,"a") as f:
				lapsed=time.time()-start
				f.write(RatID+"\tinactive\t" + time.strftime("%Y-%m-%d\t%H:%M:%S", time.localtime()) + "\t" + str(lapsed) + "\t" + boxid + "\t\t\t\t\t\t\n")
				f.close()
			time.sleep(0.20)

def createDataFiles():
	# open touch data file
	with open(touchDataFile,"a") as f:
		f.write("#Session Started on " +time.strftime("%Y-%m-%d\t%H:%M:%S\t", time.localtime())+"\n")
		f.write("RatID\thole\tdate\ttime\tlapsed\tboxid\tleds\ttimes\tspeed\tinterval\thouseLight\thouseOffSec\n")
		f.close()

def doneSignal():
	while True:
		gpio.output(touchLed,True)
		gpio.output(motionLight,False)
		time.sleep(1)
		gpio.output(touchLed,False)
		gpio.output(motionLight,True)
		time.sleep(1)

if __name__ == '__main__':
	sessionLength=1800
        time.sleep(20) ## allow wifi and htpdate to catch up
	# disable python automatic garbage collection for greater sensitivity
	# session LEDs are on when data are being recorded. These LEDs are located at the end of the head poke holes and serve to attract the attension of the rats. 
	# touchLed is on when touch sensor is activated  
	# green and red Leds are for sensation seeking
	motionLight=31 
	houseLight1=33
	touchLed=35 
	houseLight2=37
	greenLed=11
	redLed=7
	pins=[greenLed,redLed]
	# setting up the various LEDs.
	gpio.setwarnings(False)
	gpio.setmode(gpio.BOARD)
	gpio.setup(greenLed, gpio.OUT)
	gpio.setup(redLed, gpio.OUT)
	gpio.setup(houseLight1,gpio.OUT)
	gpio.setup(houseLight2,gpio.OUT)
	gpio.setup(touchLed,gpio.OUT)
	gpio.setup(motionLight,gpio.OUT)
	## Initial LED status
	gpio.output(redLed,False)
	gpio.output(greenLed,False)
	gpio.output(touchLed,True)
	# initiate the touch sensor
	RatID=ReadRFID("/dev/ttyUSB0")
	gpio.output(houseLight1,True)
	gpio.output(houseLight2,True)
	## creat data files, Each box has its own ID
	idfile=open("/home/pi/deviceid")
	boxid=idfile.read()
	boxid=boxid.strip()
	# data file names
	startTime=str(time.strftime("%Y-%m-%d_%H:%M:%S", time.localtime()))
	touchDataFile='/home/pi/Pies/OSS/Touch/'+boxid+'_touch'+ '_' + RatID +'_'+ startTime+'.csv'
	createDataFiles()
	subprocess.call("sudo python /home/pi/openbehavior/oss/motion.py " + " -RatID " + RatID + " &", shell=True)
	## turn the touchLed off when the RFID is detected
	gpio.output(touchLed, False)
	start=time.time()
	cap=initTouch()
	touchSensor()
	gpio.output(houseLight1,False)
	gpio.output(houseLight2,False)
	# finishing the data files
	#open data file
	with open(touchDataFile,"a") as f:
		f.write("#Session Ended on " +time.strftime("%Y-%m-%d\t%H:%M:%S\t", time.localtime())+"\n")
		f.close()
	# reactivate automatic garbage collection and clean objects so no memory leaks
	subprocess.call('/home/pi/openbehavior/wifi-network/rsync.sh')
	doneSignal()



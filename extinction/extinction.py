#!/usr/bin/python

import RPi.GPIO as gpio
import time
import os
import sys
import Adafruit_MPR121.MPR121 as MPR121
import Adafruit_CharLCD

def initLCD():
	lcd = Adafruit_CharLCD.Adafruit_CharLCD()
	lcd.begin(16,1)
	lcd.clear()
	lcd.message("Session Starts")
	return lcd 

def initTouch():
	cap = MPR121.MPR121()
	if not cap.begin():
		print ("Error initializing MPR121.  Check your wiring!") 
		#lcd.clean()
		#lcd.message("Touch Sensor Connection Error")
		sys.exit(1)
	print ("Touch Sensor Started\n")
	return cap

def updatelcd(active, inactive, seconds):
	minutes=str(int(seconds/60))
	lcd.clear()
	lcd.message("Act:" + active + "Ina" + inactive + "\n" + "at " + minutes + "minutes" )

#def createDataFile():
#	idfile=open('/home/pi/deviceid')
#	deviceid=idfile.read()
#	deviceid=deviceid.strip()
#	currentTime= time.strftime("%Y-%m-%d\t%H:%M:%S\t", time.localtime())
#	lickDataFile="/home/pi/Pies/Extinction/"+ deviceid + currentTime + ".csv"
#	with open(lickDataFile,"a") as f:
#		f.write("#Session Started on " + currentTime + "\n")
#		f.write("device\tRatID\tSpout\tlapsed\n")
#		f.close()
#	return lickDataFile

def recordLicks(sessionLength):
	active=0
	inactive=0
	start=time.time()
	while time.time() - start < sessionLength:
		time.sleep(0.20) # sets time resolution
		lapsed = time.time() - start
		if cap.is_touched(1):
			active+=1
			#updatelcd(active, inactive, lapsed)
			print(active, inactive, lapsed)
			with open(lickDataFile,"a") as f:
				f.write(str(deviceid) + "\t" + "ratID\t"+today +"\t" + startTime + "\t" + "active\t" +  str(lapsed) + "\n")
				f.close()
		elif cap.is_touched(0):
			inactive+=1
			lapsed=time.time()-start
			#updatelcd(active, inactive, lapsed)
			print (active, inactive, lapsed)
			with open(lickDataFile,"a") as f:
				f.write(str(deviceid) + "\t" + "ratID\t"+today +"\t" + startTime + "\t" + "inactive\t" +  str(lapsed) + "\n")
				f.close()
	# finishing the data files
	with open(touchDataFile,"a") as f:
		f.write("#Session Ended on " +time.strftime("%Y-%m-%d\t%H:%M:%S\t", time.localtime())+"\n")
		f.close()
	#updatelcd(active, inactive, lapsed)
	print (active, inactive, lapsed)

#def setupGPIO():
#	Led1=32
#	Led2=36
#	gpio.setwarnings(False)
#	gpio.setmode(gpio.BOARD)
#	gpio.setup(Led1, gpio.OUT)
#	gpio.setup(Led2, gpio.OUT)

if __name__ == '__main__':
#	os.system("python /home/pi/openbehavior/wifi-network/deviceinfo.sh &")
#	os.system("python /home/pi/openbehavior/extinction/cuelights.py &")
#	setupGPIO()
	#initLCD()
	cap=initTouch()
	idfile=open('/home/pi/deviceid')
	deviceid=idfile.read()
	deviceid=deviceid.strip()
	today= time.strftime("%Y-%m-%d", time.localtime())
	startTime= time.strftime("%H:%M:%S", time.localtime())
	currentTime=today + "_" + startTime
	lickDataFile="/home/pi/Pies/Extinction/"+ deviceid + currentTime + ".csv"
	with open(lickDataFile,"a") as f:
		f.write("#Session Started on " + currentTime + "\n")
		f.write("device\tRatID\tDate\tStartTime\tSpout\tlapsed\n")
		f.close()
	recordLicks(3600) # session length
	time.sleep(5) # wait for motion.py to stop
	os.fsync(f)
	os.system('/home/pi/openbehavior/wifi-network/rsync.sh')


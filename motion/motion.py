#!/usr/bin/env python2

import RPi.GPIO as gpio
import time
import os
import sys

pirPin=12
onPin=16
motionLed=40
gpio.setwarnings(False)
gpio.setmode(gpio.BOARD)
gpio.setup(pirPin, gpio.IN, pull_up_down=gpio.PUD_DOWN)
gpio.setup(onPin, gpio.IN, pull_up_down=gpio.PUD_DOWN)        
gpio.setup(motionLed, gpio.OUT)        

while(True):
	if gpio.input(onPin):
                sessionLength=3600
		idfile=open("/home/pi/deviceid")
		boxid=idfile.read()
                boxid=boxid.strip()
		startTime=time.strftime("%Y-%m-%d_%H:%M:%S", time.localtime())
		start=time.time()
		motionDataFile='/home/pi/Pies/OCMotion/mot'+ boxid + "_" + startTime + ".csv"
                cnt=0
		with open(motionDataFile,"a") as f:
			f.write("#Session started on " + time.strftime("%Y-%m-%d\t%H:%M:%S\t", time.localtime())+"\n")
			f.write("date\tboxid\tseconds\n")
			f.close()
			
		while time.time()-start < sessionLength:
			if gpio.input(pirPin):
				print time.strftime("%Y-%m-%d\t%H:%M:%S")
                                cnt=cnt+1
				with open(motionDataFile,"a") as f:
					lapsed=time.time()-start
					f.write(time.strftime("%Y-%m-%d\t", time.localtime()) + boxid +"\t"+ str(lapsed) +"\n")
					f.close()
				gpio.output(motionLed, True)
				time.sleep(0.1)
				gpio.output(motionLed, False)
				time.sleep(0.1)
                                if not gpio.input(onPin):
                                    sessionLength=0
		with open(motionDataFile, "a") as f:
			f.write("Total\t"+str(cnt) + "\n")
			f.write("#Session ended at " + time.strftime("%H:%M:%S", time.localtime()) + "\n")
			f.close()
	else:
		time.sleep(1)
                print "idle\n"



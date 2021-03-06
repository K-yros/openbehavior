import RPi.GPIO as gpio
import datalogger
import argparse
import time
#import os
#import sys
#from time import strftime, localtime


parser=argparse.ArgumentParser()
parser.add_argument('-SessionLength',  type=int)
parser.add_argument('-RatID',  type=str)
parser.add_argument('-Schedule',  type=str)
args=parser.parse_args()
sessionLength=args.SessionLength

pirPin=35
motionLed=31

# setting up GPIO
gpio.setwarnings(False)
gpio.setmode(gpio.BOARD)
gpio.setup(pirPin, gpio.IN)        
gpio.setup(motionLed, gpio.OUT)        

dlogger = datalogger.MotionLogger()
dlogger.createDataFile(args.RatID, args.Schedule)

start=time.time()

lapse=0
while lapse <  sessionLength:
	lapse=time.time()-start 
	if gpio.input(pirPin):
		dlogger.logEvent("Motion", lapse)
		gpio.output(motionLed, True)
		time.sleep(1)
		gpio.output(motionLed, False)
		time.sleep(1)
        if args.Schedule=="pr":
                if int(time.time())%5==0:
                        sessionEnd=open("/home/pi/prend").read().strip()
                        if sessionEnd=="yes":
                                 sessionLength=lapse-100
                        else:
                                 sessionLength=lapse+100

dlogger.logEvent("SessionEnd", lapse)


import RPi.GPIO as gpio
import time
from time import strftime, localtime
from random import randint
import os
import gc
import sys
import Adafruit_MPR121.MPR121 as MPR121
import multiprocessing
import subprocess

gpio.setwarnings(False)

sessionLength=3600
start=time.time()

# Each box has its own ID
idfile=open("/home/pi/boxid")
boxid=idfile.read()
boxid=boxid.strip()

startTime=str( time.strftime("%Y-%m-%d_%H:%M:%S", localtime()) )

touchDataFile='/home/pi/oss'+ boxid + "_" + startTime + ".csv"
motionDataFile='/home/pi/motion'+ boxid + "_" + startTime + ".csv"

# session LEDs are on when data are being recorded. These LEDs are located at the end of the head poke holes and serve to attract the attension of the rats. 
# touchLed is on when touch sensor is activated  
motionLed=31
sessionLed1=33
touchLed=35 
sessionLed2=37
# green and red Leds are for sensation seeking
greenLed=11
redLed=7
pins=[greenLed,redLed]
pirPin = 12 

gpio.setmode(gpio.BOARD)
gpio.setup(greenLed, gpio.OUT)
gpio.setup(redLed, gpio.OUT)
gpio.setup(sessionLed1,gpio.OUT)
gpio.setup(sessionLed2,gpio.OUT)
gpio.setup(touchLed,gpio.OUT)
gpio.setup(pirPin, gpio.IN)        
gpio.setup(motionLed, gpio.OUT)       

# open touch data file
with open(touchDataFile,"a") as f:
	f.write("#Session Started on " +time.strftime("%Y-%m-%d\t%H:%M:%S\t", localtime())+"\n")
	f.write("hole\tdate\ttime\tlapsed\tboxid\tleds\ttimes\tspeed\n")
	f.close()

# open motion data file
with open(motionDataFile,"a") as f:
	f.write("#Session Started on " +time.strftime("%Y-%m-%d\t%H:%M:%S\t", localtime())+"\n")
	f.write("boxid\tseconds\n")
	f.close()

### initiate touch sensor
cap = MPR121.MPR121()
if not cap.begin():
	print 'Error initializing MPR121.  Check your wiring!'
	subprocess.call("sudo python /home/pi/oss/errorled.py &")
	sys.exit(1)


## blinks the greenLed and/or redLed at a randomly selected frequency for a randomly selected time period, repeat 1-3 times
'''
def blink(pins):
	whichpin=randint(0,3)
	if whichpin==0:
		pin=[pins[0]]
	elif whichpin==1:
		pin=[pins[1]]
	elif whichpin==2:
		pin=pins
	else:
		pin=[pins[0],pins[1],9] # 9 = both pins
	numTimes=randint(1,3)
	speed=randint(1,9)/float(9)
	gpio.output(sessionLed1,False)
	if len(pin)==3:
		print ("blink  pins alternativly "+str(pin)+" for "+str(numTimes)+" times at "+str(speed) + " speed") 
		for i in range(0,numTimes):
			gpio.output(pin[0],True)
			time.sleep(speed)
			gpio.output(pin[0],False)
			gpio.output(pin[1],True)
			time.sleep(speed)
			gpio.output(pin[1],False)
			time.sleep(speed)
	elif len(pin)==2:
		print ("blink both pins "+str(pin)+" for "+str(numTimes)+" times at "+str(speed) + " speed") 
		for i in range(0,numTimes):
			gpio.output(pin[1],True)
			gpio.output(pin[0],True)
			time.sleep(speed)
			gpio.output(pin[0],False)
			gpio.output(pin[1],False)
			time.sleep(speed)
	else:
		print ("blink pin "+str(pin)+" for "+str(numTimes)+" times at "+str(speed) + " speed") 
		for i in range(0,numTimes):
			gpio.output(pin[0],True)
			time.sleep(speed)
			gpio.output(pin[0],False)
			time.sleep(speed)
#	time.sleep(5-speed*numTimes)
	gpio.output(sessionLed1,True)
	pin=str(pin)
	pin=str.replace(pin, ",",":") # comma in data file cause confusion with the csv format
	pin=str.replace(pin, "7","red") # replace pin with LED color
	pin=str.replace(pin, "11","green")
	pin=str.replace(pin, "7, 11, 9","both")
	return {'pins':pin, 'times':numTimes, 'speed':speed}
'''

def active():
	timeout=5
	rewardtime=start-timeout #to ensoure the first touch of the session triggers the reward immediately
	while True:
		if cap.is_touched(1):
			subprocess.call("sudo python /home/pi/oss/touchled.py &", shell=True)
			if (time.time()-rewardtime>timeout):
				rewardtime=time.time()
				subprocess.call("sudo python /home/pi/oss/blink.py " + " -datafile "+  touchDataFile + " -start " + str(start)  + " &", shell=True)
			else:
				with open(touchDataFile,"a") as f:
					lapsed=time.time()-start
					f.write("active\t" + time.strftime("%Y-%m-%d\t%H:%M:%S", localtime()) + "\t" + str(lapsed) + "\t" + boxid + "\t\t\t\n")
					f.close()
			time.sleep(0.5)

def inactive():
	while True:
		if cap.is_touched(0):
			subprocess.call("sudo python /home/pi/oss/touchled.py &", shell=True)
			with open(touchDataFile,"a") as f:
				lapsed=time.time()-start
				f.write("inactive\t" + time.strftime("%Y-%m-%d\t%H:%M:%S", localtime()) + "\t" + str(lapsed) + "\t" + boxid + "\t\t\t\n")
				f.close()
			time.sleep(0.5)


#def motion(start, sessionLength):
def motion():
	cnt=0
	#while time.time()-start < sessionLength:
	while True:
		if gpio.input(pirPin):
			#print time.strftime("%Y-%m-%d\t%H:%M:%S")
			with open(motionDataFile,"a") as f:
				lapsed=time.time()-start
				f.write(boxid +"\t"+ str(lapsed) +"\n")
				f.close()
			gpio.output(motionLed, True)
			time.sleep(0.05)
			gpio.output(motionLed, False)
			time.sleep(0.05)
			cnt=cnt+1
			#return cnt


if __name__ == '__main__':
	# disable python automatic garbage collect
	# for greater sensitivity
	gc.disable()

	## Initial LED status
	gpio.output(redLed,False)
	gpio.output(greenLed,False)
	gpio.output(touchLed,False)
	gpio.output(sessionLed1,True)
	gpio.output(sessionLed2,True)

	p1=multiprocessing.Process(target=active)
	p2=multiprocessing.Process(target=inactive)
	p3=multiprocessing.Process(target=motion)
	p1.start()
	p2.start()
	p3.start()
	time.sleep(sessionLength)
	gpio.output(sessionLed1,False)
	gpio.output(sessionLed2,False)
	p1.terminate()
	p2.terminate()
	p3.terminate()
	p1.join()
	p2.join()
	p3.join()

	# reactivate automatic garbage collection
	# and clean objects so no memory leaks

	with open(motionDataFile, "a") as f:
	#f.write("Total Activity:\t"+str(CNT)+"\n")
		f.write("#session Ended at " + time.strftime("%H:%M:%S", localtime())+"\n")
		f.close

	# open data file
	with open(touchDataFile,"a") as f:
		f.write("#Session Ended on " +time.strftime("%Y-%m-%d\t%H:%M:%S\t", localtime())+"\n")
		f.close()

	gc.enable()
	gc.collect()



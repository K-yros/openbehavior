'''
	Author: Ethan Willis, Hao Chen
	Description: This program will log temperature, humidity, and barometric pressure
	and luminosity to a log file with a given frequency.
        The seonsor are MCP9808 for temperature, HTU21DF for humidity, MPL3115A2 for  
        barometric pressure, TSL2561 for luminosity. These are all connected using 
        the I2C protocol. 

        This is scheduled to run via cron jobs. An LED connected to GPIO pin 8 is turned on when the script is ran 
	
	The log will have the following structure per entry.
	"date\ttime\ttemperature\thumidity\n"

	Usage:
		python HTU21DF_Logger.py 
'''

import time
from time import strftime
import datetime
import sys
import RPi.GPIO as gpio

## moved this block here to turn off the LED when program starts
led=8
gpio.setmode(gpio.BOARD)
gpio.setup(led, gpio.OUT)
gpio.output(led,False)

import HTU21DF
import TSL2561
import Adafruit_BMP.BMP085 as BMP085



'''
	Writes data to the logfile located at the location specified
	by the filename variable.
'''
def write_to_log(filename, data):
	with open(filename, "a") as logfile:
		datastring = str(data[0]) + "\t" + location + "\t" +  str(data[1]) + "\t" + str(data[2]) + "\t" + str(data[3]) + "\t" + str(data[4])+"\n"
		logfile.write(datastring)
		print datastring

def write_lux(filename, data):
	with open(filename, "a") as luxfile:
		datastring= str(data)+"\n"
		luxfile.write(datastring)


def readLux():
	LightSensor = TSL2561.Adafruit_TSL2561()
	LightSensor.enableAutoGain(True)
	count=0
	luxTotal=0
	while True:
		if (count <=100):
				 luxTotal=LightSensor.calculateLux() + luxTotal 
				 count+=1
		else:
			 lux=round(luxTotal/100)
			 break
	return lux



def prog(filename):
	# reset sensor and collect data.
	# reset sensor and collect data.  temp=tempsensor.readTempC()
	HTU21DF.htu_reset
	humidity=HTU21DF.read_humidity()
	temp1=HTU21DF.read_temperature()
	barometer = BMP085.BMP085(mode=BMP085.BMP085_ULTRAHIGHRES)
	pressure=barometer.read_pressure()
	temp2=barometer.read_temperature()
	temp=(temp1+temp2)/2
	lux=readLux()
	datetime=strftime("%Y-%m-%d\t%H:%M:%S")
	data=[datetime,temp,humidity,pressure,lux]
	# savenewdataentry
	write_to_log(filename,data)
	hour=strftime("%H")
        if float(hour) < 7: 
            write_lux("/home/pi/lux.csv",lux) 


try:
	#gpio.output(led,False)
	idfile=open("/home/pi/locationid")
	location=idfile.read()
	location=location.strip()
	filename="/home/pi/"+location+"Env.log"
	prog(filename)
	gpio.output(led,True)
except: 
	gpio.output(led,False)


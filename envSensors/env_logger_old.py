'''
	Author: Ethan Willis, Hao Chen
	Description: This program will log temperature, humidity, and barometric pressure
	and luminosity to a log file with a given frequency.
        The seonsor are MCP9808 for temperature, HTU21DF for humidity, MPL3115A2 for  
        barometric pressure, TSL2561 for luminosity. These are all connected using 
        the I2C protocol. 
	
	The log will have the following structure per entry.
	"date\ttime\ttemperature\thumidity\n"

	Usage:
		python HTU21DF_Logger.py <log filepath> <sleeptime>
'''
import time
from time import strftime
import datetime
import HTU21DF
import sys
import MPL3115A2
import TSL2561
import Adafruit_MCP9808.MCP9808 as MCP9808

tempsensor = MCP9808.MCP9808()
tempsensor.begin()
time.sleep(30)
temp = tempsensor.readTempC()
LightSensor = TSL2561.Adafruit_TSL2561()
LightSensor.enableAutoGain(True)
HTU21DF.htu_reset
  

'''
	Writes data to the logfile located at the location specified
	by the filename variable.
'''
def write_to_log(filename, data):
	with open(filename, "a") as logfile:
		datastring = str(data[0]) + "\t" + str(data[1]) + "\t" + str(data[2]) + "\t" + str(data[3]) + "\t" + str(data[4])+"\n"
		logfile.write(datastring)
		print datastring

'''
	Collects environmental  data on the time period
	specified by the sleeptime variable.
'''

def readLux():
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


def prog(filename="/home/pi/behaviorRoomEnv.log", sleeptime=600):
	while True:
		# reset sensor and collect data for next log entry.
		temp = tempsensor.readTempC()
		humidity = HTU21DF.read_humidity()
		tempPres=MPL3115A2.pressure()
                lux=readLux() 
                ## calculate average lux for 100 readings
    		datetime = strftime("%Y-%m-%d\t%H:%M:%S") 
		data = [datetime, temp, humidity, tempPres[1], lux]
	
		# save new data entry
		write_to_log(filename, data)
	
		# sleep until ready to collect next measurements.
		time.sleep(sleeptime)

prog()


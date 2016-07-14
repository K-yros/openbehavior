#!/bin/bash


## set approximate clock date if need to.
## wait for wifi connection before run htpdate (because ntp is blocked on my network
## then set hwclock
## disconnect wifi thereafter to ensure time does not change during the run.


year=`date +"%Y"`
if [ "$year" -lt "2016" ] 
	then
		date -s "Fri July 6 1:01:01 CDT 2016"
fi

while [ `sudo ifconfig wlan0 |grep Bcast |wc -l` -ne 1 ]
	do
	sleep 2
	cnt=$[$cnt+1]
	if [ $cnt -eq 10 ] # max 20 sec  
		then 
			sudo ifconfig wlan0 down # disconnect wifi if not connected
			break
	fi
done

htpdate -s www.uthsc.edu www.google.com	
hwclock -w

date >>/home/pi/Pies/DeviceInfo/`cat /home/pi/deviceid`.info
cat /home/pi/deviceid >>/home/pi/Pies/DeviceInfo/`cat /home/pi/deviceid`.info
ifconfig wlan0 >>/home/pi/Pies/DeviceInfo/`cat /home/pi/deviceid`.info
ifconfig eth0 >>/home/pi/Pies/DeviceInfo/`cat /home/pi/deviceid`.info
echo "_______________________________" >>/home/pi/Pies/DeviceInfo/`cat /home/pi/deviceid`.info

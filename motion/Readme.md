#Adding  motion sensors to operant conditioning chambers

## Description
This project adds a motion sensor to the commercial MedPC operant chambers. The motion sensor is controlled by a RPi. The RPi is powered by the 28V power source available in the operant chamber (via a step down converter). The RPi is turned on and off via MedPC programs. The data are stored in the SD card of the Pi. Each operant chamber use one Pi. All the Pi computers are connected by a WiFi network and data are transferred to a remote server via sftp.

## Parts list

Molex connector for 28V. Mfg P/N: 03-06-2032 [Mouser] ( http://www.mouser.com/ProductDetail/Molex/03-06-2032/?qs=%2fha2pyFadugvI%2fznVBilJA6N4bQxmqBpdBoCzb%2f9bbY%3d)  

Molex pin. Mfg P/N: 02-06-2103 [Mouser] (http://www.mouser.com/ProductDetail/Molex/02-06-2103/?qs=%2fha2pyFaduhC0HER4S2%2flGJ0%2fQN3qzJ5F27g%252bKWL4TY%3d)

Motion sensor. [Amazon] (http://www.amazon.com/gp/product/B00FDPO9B8) 

EdiMax WiFi USB. [Amazon] (http://www.amazon.com/gp/product/B003MTTJOY)

Step-down LM2596 power converter. [eBay] (http://www.ebay.com/itm/161476280982)  

## Notes

Two step down DC-DC converters are used. One is set to 5 V to power the RPi. This is always on. The other one is set to 3.3 V. This is only on when the output port in the MedPC is activated. This then controls the on and off of the motion.py program.


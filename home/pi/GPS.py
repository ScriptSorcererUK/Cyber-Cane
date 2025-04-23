#Used to talk to the GPIO pins
import RPi.GPIO as GPIO

#used to connect to the i2c bus
import board

#Use to pause at various times
import time

#Used to run espeak in the terminal
import os

#Used to get direction from the compass
import adafruit_lis2mdl


#Used to listen to the GPS
import serial, io
#Used to get location from the GPS strings
import pynmea2


#Used to work out direction and distance between locations
from math import radians, cos, sin, atan2, asin, sqrt, degrees, pi


#Giving time to connect to the bluetooth speaker/headphones
print("Waiting for 30 seconds for system to boot...")
time.sleep(30)
print("Finished waiting. Starting up now.")


#turn off the warning the GPIO has already been setup by the sensor.py
GPIO.setwarnings(False)


#Use the GPIOxx numbering
GPIO.setmode(GPIO.BCM)


#Setup the link to the compass
#Basd on code from https://learn.adafruit.com/lsm303-accelerometer-slash-compass-breakout/python-circuitpython
i2c = board.I2C()
mag = adafruit_lis2mdl.LIS2MDL(i2c)


#Data collected from the calibration program to set the offsets
#Final Magnetometer Calibration: X:   -20.47, Y:   22.20, Z:   -1.12
mag.x_offset = -20.47
mag.y_offset = 22.20
mag.z_offset = -1.12


#Print the initial magnetic recordings to check it's working
print(mag.magnetic)


#The target we are navigating to.
#This is currently the centre of Haslemere.
#Iin a final version could be set via voice recognition or a web-server by someone else.
#Or even better, it could be a list of waypoints that are removed when you get to them.
TargetLat = 51.092369
TargetLong = -0.711760


#The settings to listen to the GPS via serial GPIO
serialPort = serial.Serial("/dev/ttyS0", 9600, timeout=0.5)
serialPort.close()
serialPort.open()


#The button input GPIO pin
#Based on https://raspi.tv/2013/rpi-gpio-basics-6-using-inputs-and-outputs-together-with-rpi-gpio-pull-ups-and-pull-downs
GPIO.setup(12, GPIO.IN, GPIO.PUD_UP)


#Makes it easier to run espeak.
def text_to_speech(text):
#Use of os.system based on https://raspberry-python.blogspot.com/2012/11/fibospeak.html
#Updated using advice from this make it work in a service https://unix.stackexchange.com/questions/279638/how-to-get-espeak-to-continuously-speak-stdout-piped-from-netcat/280409#280409
    try:
        os.system(f"espeak --stdout '{text}' | aplay -D pulse")
    except:
        print("Error when speaking")


#Copied from https://stackoverflow.com/questions/4913349/haversine-formula-in-python-bearing-and-distance-between-two-gps-points
def haversine(lon1, lat1, lon2, lat2):
    """
    Calculate the great circle distance in miles between two points 
    on the earth (specified in decimal degrees)
    """
    R = 3959.87433 # this is in miles.  For Earth radius in kilometers use 6372.8 km
    dLat = radians(lat2 - lat1)
    dLon = radians(lon2 - lon1)
    lat1 = radians(lat1)
    lat2 = radians(lat2)
    a = sin(dLat/2)**2 + cos(lat1)*cos(lat2)*sin(dLon/2)**2
    c = 2*asin(sqrt(a))
    return R * c


#Copied from https://stackoverflow.com/questions/4913349/haversine-formula-in-python-bearing-and-distance-between-two-gps-points
def getDir(lat1, long1, lat2, long2):
    bearing = atan2(sin(long2 - long1)*cos(lat2), cos(lat1)*sin(lat2) - sin(lat1)*cos(lat2)*cos(long2 - long1))
    bearing = degrees(bearing)
    bearing = (bearing + 360) % 360
    return bearing


#Uses the x and y readings from the compass to work out a bearing
def getYourDir():
    #Based on code from https://forums.raspberrypi.com/viewtopic.php?t=178846
    heading = (atan2(mag.magnetic[0], mag.magnetic[1]) * 180) / pi
    if (heading < 0):
        heading = 360 + heading
    #Round the number to a whole number
    heading = int(round(heading, 0))
    return heading

#Let the person listening with bluetooth that the cane is ready
text_to_speech("Cyber Cane Is Ready")
print("Cyber Cane Is Ready")


#Repeat forever
while 1:
    #It can crash on getting GPS data or parsing bad GPS data
    try:
        #GPS listening code based on https://github.com/Knio/pynmea2
        #Read a line from the GPS via serial and strip out any spaces on the ends
        line = serialPort.readline().strip().decode().strip()
        #print(line)
        #Get the GPS data from the string
        msg = pynmea2.parse(str(line))
        #If we have GPS data AND the button was pressed
        if hasattr(msg, 'latitude') and hasattr(msg, 'longitude') and GPIO.input(12) == GPIO.HIGH:
            print("Latitude:", msg.latitude)
            print("Longitude:", msg.longitude)

            #Work out how far we are from the target
            distance = haversine(msg.latitude, msg.longitude, TargetLat, TargetLong)
            print("Distance to target is", distance, "miles")
            #Make the distance sound nicer when spoken
            rounded_distance = round(distance, 2)
            rounded_distance = str(rounded_distance)
            #Say the distance out loud
            text_to_speech("Distance to target is " + rounded_distance + " miles")

            #Work out the bearing from us to the target
            bearing = getDir(msg.latitude, msg.longitude, TargetLat, TargetLong)
            print("Bearing to target is", bearing, "degrees")
            rounded_bearing = round(bearing, 0)
            rounded_bearing = str(int(rounded_bearing))
            #Say the bearing out loud
            text_to_speech("Bearing to target is" + rounded_bearing + " degrees")

            #Use the compass to work out the bearing you are facing.
            #In a final version, this would just say "Turn sharp left" etc
            your_bearing = getYourDir()
            print("Your bearing is", your_bearing, "degrees")
            text_to_speech("Your bearing is" + str(your_bearing) + " degrees")

            print("...")
            #Wait one second before listening to a button press again
            time.sleep(1)
        #If they pressed the button and there is no GPS signal to give them directions...
        elif GPIO.input(12) == GPIO.HIGH:
            text_to_speech("No G.P.S. Signal")
            print("No GPS Signal")
            #Wait one second before listening to a button press again
            time.sleep(1)

    except serial.SerialException as e:
        #If the serial port didn't work, reset it
        serialPort.close()
        serialPort.open()
        continue
    except pynmea2.ParseError as e:
        #This happens a lot, so ignore this error
        continue
    except KeyboardInterrupt:
        #If ctrl + c is pressed, quit the program and close the serial port
        serialPort.close()
        break
    except Exception as e:
        #If something else goes wrong, print the error and try again
        print(e)
        continue


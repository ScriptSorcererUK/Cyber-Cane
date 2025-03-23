#needed to vibrate the motor, send the trigger signal to the ultrasonic sensor and also wait for a reply
import RPi.GPIO as GPIO
from gpiozero import InputDevice, OutputDevice, PWMOutputDevice
from time import sleep, time

#Use the GPIOxx numbers
GPIO.setmode(GPIO.BCM)

#The GPIO pin that we send a signal to so it will send out a signal
TRIG = 23
GPIO.setup(TRIG,GPIO.OUT)
trig = OutputDevice(23)

#THe GPIO pin that we wait for a reponse from after it hears the echo
ECHO = 24
GPIO.setup(ECHO,GPIO.IN)
echo = InputDevice(24)

#These are connected to the two vibration motors
motor = PWMOutputDevice(19)
motor2 = PWMOutputDevice(13)

#Make sure the motors are not vibrating
motor.value = 0
motor2.value = 0 

print ("Distance measurement In progress")

#Make sure the trigger is off
GPIO.output(TRIG, False)
print("Waiting For Sensor to Settle")
sleep(2)


#Returns a value between 0 and 1 to make the motor vibrate based on how far away it is from the sensor
def calculate_vibration(distance):
    #Only vibrate if something is within 50cm    
    if distance > 50:
      return 0
    #Reverse the number so that 50cm away becomes 1, 25 becomes 0.5 and 0cm becomes 0
    vibration = 50 - distance
    #Make it a fraction of 50 so it's between 0 and 1
    vibration = vibration / 50
    print("vibration", vibration)
    return vibration


#Based on code from https://forums.raspberrypi.com/viewtopic.php?t=233824
while True:
    #Send a brief signal to the distance sensor to make it send out a pulse
    GPIO.output(TRIG, True)
    sleep(0.00001)
    GPIO.output(TRIG, False)

    #Wait until the Echo signal goes on
    while GPIO.input(ECHO)==0:
        #Record the time it starts sending the signal out
        pulse_start = time()

    #Wait until the echo signal goes off to signal it recieved a signal back (or gave up waiting)
    while GPIO.input(ECHO)==1:
        #Record the time it stops sending a signal back
        pulse_end = time()

    #Work out how many milliseconds the pulse took to send and receive a signal
    pulse_duration = pulse_end - pulse_start

    #Do some clever maths based on the speed of sound
    distance = pulse_duration * 17150

    #Round the distance to 2 decimal places (in cm)
    distance = round(distance, 2)

    print ("Distance:",distance,"cm")

    #Vibrate the motor more the closer you are to something
    vibration = calculate_vibration(distance)
    motor.value = vibration
    motor2.value = vibration
    #Wait half a second before trying again
    sleep(0.5)


#Reset the GPIO pins on crash/exit
GPIO.cleanup()



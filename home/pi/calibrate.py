#Based on code from https://learn.adafruit.com/adafruit-sensorlab-magnetometer-calibration/calibration-with-raspberry-pi-using-blinka
#Used to find the minimum values and calibrate the compass sensor
import adafruit_lis2mdl
import math
import board
import time
import threading


SAMPLE_SIZE = 500


class KeyListener:
    """Object for listening for input in a separate thread"""

    def __init__(self):
        self._input_key = None
        self._listener_thread = None

    def _key_listener(self):
        while True:
            self._input_key = input()

    def start(self):
        """Start Listening"""
        if self._listener_thread is None:
            self._listener_thread = threading.Thread(
                target=self._key_listener, daemon=True
            )
        if not self._listener_thread.is_alive():
            self._listener_thread.start()

    def stop(self):
        """Stop Listening"""
        if self._listener_thread is not None and self._listener_thread.is_alive():
            self._listener_thread.join()

    @property
    def pressed(self):
        "Return whether enter was pressed since last checked" ""
        result = False
        if self._input_key is not None:
            self._input_key = None
            result = True
        return result



# pylint: disable=too-many-locals, too-many-statements
i2c = board.I2C()
magnetometer = adafruit_lis2mdl.LIS2MDL(i2c)


key_listener = KeyListener()
key_listener.start()

    ############################
    # Magnetometer Calibration #
    ############################

print("Magnetometer Calibration")
print("Start moving the board in all directions")
print("When the magnetic Hard Offset values stop")
print("changing, press ENTER to go to the next step")
print("Press ENTER to continue...")
while not key_listener.pressed:
    pass


mag_x, mag_y, mag_z = magnetometer.magnetic
min_x = max_x = mag_x
min_y = max_y = mag_y
min_z = max_z = mag_z
while not key_listener.pressed:
   mag_x, mag_y, mag_z = magnetometer.magnetic

   print(
        "Magnetometer: X: {0:8.2f}, Y:{1:8.2f}, Z:{2:8.2f} uT".format(
           mag_x, mag_y, mag_z
        )
    )

   min_x = min(min_x, mag_x)
   min_y = min(min_y, mag_y)
   min_z = min(min_z, mag_z)

   max_x = max(max_x, mag_x)
   max_y = max(max_y, mag_y)
   max_z = max(max_z, mag_z)

   offset_x = (max_x + min_x) / 2
   offset_y = (max_y + min_y) / 2
   offset_z = (max_z + min_z) / 2

   field_x = (max_x - min_x) / 2
   field_y = (max_y - min_y) / 2
   field_z = (max_z - min_z) / 2

   print(
       "Hard Offset:  X: {0:8.2f}, Y:{1:8.2f}, Z:{2:8.2f} uT".format(
           offset_x, offset_y, offset_z
       )
    )
   print(
       "Field:        X: {0:8.2f}, Y:{1:8.2f}, Z:{2:8.2f} uT".format(
           field_x, field_y, field_z
       )
    )
   print("")
   time.sleep(0.01)


#These values can now be used to set the offsets in the main program
print(
    "Final Magnetometer Calibration: X: {0:8.2f}, Y:{1:8.2f}, Z:{2:8.2f} uT".format(
       offset_x, offset_y, offset_z
   )
)

import board
import adafruit_fxos8700
import math
import time

#setup
i2c = board.I2C()
accelMag = adafruit_fxos8700.FXOS8700(i2c)

#adapted from roboticsclubiitk.github.io/2017/12/21/Beginners-Guide-to-IMU.html

def orientationLocalGravity():
    '''
    Returns: tuple in format (pitch, roll) with respect to local gravity
    '''
    x, y, z = accelMag.accelerometer
    pitch = 180 * math.atan2(x, math.sqrt(y**2 + z**2)) / math.pi
    roll = 180 * math.atan2(y, math.sqrt(x**2 + z**2)) / math.pi
    return pitch, roll

def orientationMagNorth():
    '''
    Returns: yaw with respect to magnetic north
    '''
    pitch, roll = orientationLocalGravity()
    x, y, z = accelMag.magnetometer
    mx = x * math.cos(pitch) + y * math.sin(roll) * math.sin(pitch) + z * math.cos(roll) * math.sin(pitch)
    my = y * math.cos(roll) - z * math.sin(roll)
    yaw = 180 * math.atan2(-my, mx) / math.pi
    return yaw

def orientation():
    '''
    Returns pitch, roll, and yaw with respect to gravity and magnetic north
    '''
    pitch, roll = orientationLocalGravity()
    yaw = orientationMagNorth()
    return pitch, roll, yaw
while(True):
    time.sleep(0.1)
    print(orientation()[0:2])
#sensor_calc.py
import time
import numpy as np
import adafruit_fxos8700
import adafruit_fxas21002c
import time
import os
import board
import busio
import math

i2c = busio.I2C(board.SCL, board.SDA)
sensor1 = adafruit_fxos8700.FXOS8700(i2c)
sensor2 = adafruit_fxas21002c.FXAS21002C(i2c)


#Activity 1: RPY based on accelerometer and magnetometer
def roll_am(accelX,accelY,accelZ):
    #TODO
    roll = np.arctan2(accelY, np.sqrt(accelX*accelX+accelZ*accelZ))
    return (180/np.pi)*roll

def pitch_am(accelX,accelY,accelZ):
    #TODO
    pitch = np.arctan2(accelX, np.sqrt(accelY*accelY+accelZ*accelZ))
    return (180/np.pi)*pitch

def yaw_am(accelX,accelY,accelZ,magX,magY,magZ):
    #TODO
    pitch = math.radians(pitch_am(accelX,accelY,accelZ))
    roll = math.radians((np.pi/180)*roll_am(accelX,accelY,accelZ))
    mag_x = magX*math.cos(pitch) + magY * math.sin(roll) * math.sin(pitch) + magZ * math.cos(roll) - magZ*math.sin(roll)
    mag_y = magY * math.cos(roll) - magZ * math.sin(roll) 
    return (180/np.pi)*np.arctan2(-mag_y, mag_x)

#Activity 2: RPY based on gyroscope
def roll_gy(prev_angle, delT, gyro):
    #TODO
    roll = prev_angle + gyro*delT
    return roll
def pitch_gy(prev_angle, delT, gyro):
    #TODO
    pitch = prev_angle + gyro*delT
    return pitch
def yaw_gy(prev_angle, delT, gyro):
    #TODO   
    yaw = prev_angle + gyro*delT
    return yaw

def set_initial(mag_offset = [0,0,0]):
    #Sets the initial position for plotting and gyro calculations.
    print("Preparing to set initial angle. Please hold the IMU still.")
    time.sleep(3)
    print("Setting angle...")
    accelX, accelY, accelZ = sensor1.accelerometer #m/s^2
    magX, magY, magZ = sensor1.magnetometer #gauss
    #Calibrate magnetometer readings. Defaults to zero until you
    #write the code
    mag_offset = calibrate_mag()
    magX = magX - mag_offset[0]
    magY = magY - mag_offset[1]
    magZ = magZ - mag_offset[2]
    roll = roll_am(accelX, accelY,accelZ)
    pitch = pitch_am(accelX,accelY,accelZ)
    yaw = yaw_am(accelX,accelY,accelZ,magX,magY,magZ)
    print("Initial angle set.")
    return [roll,pitch,yaw]

def calibrate_mag():
    #TODO: Set up lists, time, etc
    offset = []
    
    print("Preparing to calibrate magnetometer. Please wave around.")
    time.sleep(3)
    print("Calibrating...")
    #TODO: Calculate calibration constants
    count = 0
    valuesX = []
    valuesY = []
    valuesZ = []
    while count < 1000:
        magX, magY, magZ = sensor1.magnetometer
        valuesX.append(magX)
        valuesY.append(magY)
        valuesZ.append(magZ)
        count += 1
    avgX = (np.max(valuesX)+np.max(valuesX))/2 
    avgY = (np.max(valuesY)+np.max(valuesY))/2 
    avgZ = (np.max(valuesZ)+np.max(valuesZ))/2 
    offset = [avgX, avgY, avgZ]
    print("Calibration complete.")
    return offset

def calibrate_gyro():
    #TODO
    offset = [0, 0, 0]
    print("Preparing to calibrate gyroscope. Put down the board and do not touch it.")
    #time.sleep(3)
    print("Calibrating...")
    #TODO
    count = 0
    valuesX = []
    valuesY = []
    valuesZ = []
    while count < 1000:
        gyroX, gyroY, gyroZ = sensor2.gyroscope
        valuesX.append(gyroX)
        valuesY.append(gyroY)
        valuesZ.append(gyroZ)
        count += 1
    avgX = (np.max(valuesX)+np.max(valuesX))/2 
    avgY = (np.max(valuesY)+np.max(valuesY))/2 
    avgZ = (np.max(valuesZ)+np.max(valuesZ))/2 
    offset = [avgX, avgY, avgZ]
    print("Calibration complete.")
    return offset

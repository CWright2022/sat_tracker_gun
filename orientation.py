import board
import adafruit_fxos8700
import adafruit_fxas21002c
import time
i2c = board.I2C()
compass = adafruit_fxos8700.FXOS8700(i2c)
gyro = adafruit_fxas21002c.FXAS21002C(i2c)

while True:
    print('Gyroscope (radians/s): ({0:0.3f},  {1:0.3f},  {2:0.3f})'.format(*gyro.gyroscope))
    print('Magnetometer (uTesla): ({0:0.3f},{1:0.3f},{2:0.3f})'.format(*compass.magnetometer))
    time.sleep(1.0)

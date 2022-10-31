import serial
import time

PORT = "COM7"
FILENAME = "serial.txt"
time.sleep(3)
# open serial and file objects
with serial.Serial(PORT, 4800, timeout=1) as ser:
    with open(FILENAME, "w") as file:
        while True:
            # read and decode line
            line = ser.readline()
            line = line.decode('UTF-8')
            # append to file
            file.write(line)

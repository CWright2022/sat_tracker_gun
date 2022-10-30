import serial

PORT = "COM7"


def get_location():
    with serial.Serial(PORT, 9600, timeout=1) as ser:

        while True:
            line = ser.readline()
            line = line.decode('UTF-8')
            tokens = line.split(",")
            if tokens[0] == "$GPGLL":
                lat = tokens[1]
                lat_direction = tokens[2]
                long = tokens[3]
                long_direction = tokens[4]
                lat_deg = lat[:-8]
                lat_mins = lat[-8:]
                long_deg = long[:-8]
                long_mins = long[-8:]
                lat_decimal = float(lat_deg) + float(lat_mins)/60
                long_decimal = float(long_deg) + float(long_mins)/60
                if lat_direction == "S":
                    lat_decimal = lat_decimal*-1
                if long_direction == "W":
                    long_decimal = long_decimal*-1
                return lat_decimal, long_decimal

print(get_location())
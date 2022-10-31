import serial

PORT = "COM7"


def interpret_lat_and_long(lat, lat_direction, long, long_direction):
    '''
    helper function to interpret lat and long
    given a raw string from the GPS, will return the lat and long in decimal format
    '''
    # parse string into DMS
    lat_deg = lat[:-8]
    lat_mins = lat[-8:]
    long_deg = long[:-8]
    long_mins = long[-8:]
    # convert from DMS to decimal
    lat_decimal = float(lat_deg) + float(lat_mins)/60
    long_decimal = float(long_deg) + float(long_mins)/60
    # negate lat or long based on hemisphere
    if lat_direction == "S":
        lat_decimal = lat_decimal*-1
    if long_direction == "W":
        long_decimal = long_decimal*-1
    # return values
    return lat_decimal, long_decimal


def get_location():
    '''
    returns a dictionary with info from GPS if valid, otherwise returns None.
    "lat" - latitude in decimal format
    "long" - longitude in decimal format
    "alt" - altidude, meters above mean sea level
    "time" - UTC time
    "sats" - number of sats in view
    '''
    # initialize serial object
    with serial.Serial(PORT, 4800, timeout=1) as ser:
        # do this until we get a valid fix
        while True:
            # read line, decode line, split line into fields
            line = ser.readline()
            line = line.decode('UTF-8')
            tokens = line.split(",")
            # if it's the line we want,
            if tokens[0] == "$GPGGA":
                # if fix is not ok, then return None
                if int(tokens[6]) != 1 and tokens[6] != 2:
                    return None
                # create dictionary to return
                info_dict = {}
                # get time
                info_dict["time"] = tokens[1]
                # get latitude and longitude
                lat = tokens[2]
                lat_direction = tokens[3]
                long = tokens[4]
                long_direction = tokens[5]
                lat, long = interpret_lat_and_long(lat, lat_direction, long, long_direction)
                info_dict["lat"] = lat
                info_dict["long"] = long
                # get number of sats
                info_dict["sats"] = tokens[7]
                # get altitude
                info_dict["alt"] = tokens[9]
                # return dictionary
                return info_dict


print(get_location())

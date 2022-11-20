'''
GPS MODULE
this module provides an object to interact with the GPS module
main functions to keep in mind:
'''

import serial


class gps_module:
    '''
    class to represent the GPS module
    '''

    __slots__ = ["__port"]

    def __init__(self, port):
        self.__port = port

    def read_data(self, sentence="$GPRMC"):
        '''
        helper function to read any field from the GPRMC sentence
        '''
        with serial.Serial(self.__port, 4800, timeout=1) as ser:
            while True:
                # read line, decode line, split line into fields
                line = ser.readline()
                line = line.decode('UTF-8')
                tokens = line.split(",")
                # if it's the line we want,
                if tokens[0] == sentence:
                    # check validity of fix
                    if tokens[2] != "A":
                        return None
                    return tokens

    def get_date(self):
        '''
        returns a tuple with UTC day, month, and year (dd,mm,yyyy)
        '''
        data = self.read_data()
        date = data[9]
        day = date[:2]
        month = date[2:4]
        # only works for years from 2000-2099 unfortunately
        year = "20"+date[4:]
        return day, month, year

    def get_time(self):
        '''
        returns a tuple with hours, minutes, and seconds UTC (hh,mm,ss)
        '''
        data = self.read_data()
        time = data[1]
        hours = time[:2]
        minutes = time[2:4]
        seconds = time[4:]
        return hours, minutes, seconds

    def get_lat_long(self):
        '''
        returns a tuple with decimal form of latitude and longitude
        '''
        data = self.read_data()
        lat_raw = data[3]
        lat_direction = data[4]

        long_raw = data[5]
        long_direction = data[6]
        lat, long = interpret_lat_long(lat_raw, lat_direction, long_raw, long_direction)
        return lat, long


def interpret_lat_long(lat, lat_direction, long, long_direction):
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


gps = gps_module("COM7")
print(gps.get_date())
print(gps.get_time())
lat, long = gps.get_lat_long()
print("LATITUDE: "+str(lat))
print("LONGITUDE: "+str(long))

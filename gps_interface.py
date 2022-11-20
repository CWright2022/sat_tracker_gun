'''
GPS MODULE
this module provides an object to interact with the GPS module
main functions to keep in mind:
'''

import serial
import datetime


class GPS_module:
    '''
    class to represent the GPS module
    '''
    __slots__ = ["__port", "__lat", "__long", "__datetime"]

    def __init__(self, port):
        self.__port = port
        self.refresh()

    def refresh(self):
        '''
        refresh all GPS fields
        '''
        try:
            ser = serial.Serial(self.__port)
            ser.close()
        except:
            return False
        with serial.Serial(self.__port, 4800, timeout=1) as ser:
            while True:
                # read line, decode line, split line into fields
                line = ser.readline()
                line = line.decode('UTF-8')
                tokens = line.split(",")
                # if it's the line we want,
                if tokens[0] == "$GPRMC":
                    # check validity of fix
                    if tokens[2] != "A":
                        return False
                    # datetime (using python datetime object)
                    hour, minute, second = interpret_time_or_date(tokens[1])
                    day, month, year = interpret_time_or_date(tokens[9])
                    self.__date = datetime.datetime(year+2000, month, day, hour, minute, second)
                    #lat and long
                    raw_lat, lat_direction = tokens[3], tokens[4]
                    raw_long, long_direction = tokens[5], tokens[6]
                    self.__lat, self.__long = interpret_lat_long(raw_lat, lat_direction, raw_long, long_direction)
                    return True

    # get attributes of the GPS object. remember to call refresh() first!

    def latitude(self):
        return self.__lat

    def longitude(self):
        return self.__long

    def time(self):
        return self.__time

    def date(self):
        return self.__date


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


def interpret_time_or_date(raw_input):
    '''
    interprets time and date strings as a tuple
    '''
    hour_day = int(raw_input[:2])
    minute_month = int(raw_input[2:4])
    second_year = int(raw_input[4:6])
    return hour_day, minute_month, second_year

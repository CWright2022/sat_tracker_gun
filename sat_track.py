'''
SATELLITE TRACKING MODULE
this module tracks satellites
Cayden Wright 11/19/22
'''

from skyfield.api import EarthSatellite, load, wgs84

ts = load.timescale()


class Satellite:
    __slots__ = ["__tle_tuple", "__azimuth", "__elevation", "__sat_obj", "__distance", "__freq", "__modulation", "__bandwidth"]

    def __init__(self, tle_tuple, radio_tuple):
        self.__tle_tuple = tle_tuple
        name = self.__tle_tuple[0]
        tle_1 = self.__tle_tuple[1]
        tle_2 = self.__tle_tuple[2]
        # create ts object
        satellite = EarthSatellite(tle_1, tle_2, name, ts)
        self.__sat_obj = satellite
        self.__freq = str(radio_tuple[0])
        self.__modulation = str(radio_tuple[1])
        self.__bandwidth = str(radio_tuple[2])

    def recalculate(self, obs_lat, obs_long, datetime_obj):
        '''
        given an EarthSatellite object and observer latitude and longitude,
        will return a dictionary with 3 keys "azimuth"  "altitude" and "distance"
        '''
        # create observer location object thing
        observer_loc = wgs84.latlon(obs_lat, obs_long)
        # create timescale thing
        time = ts.from_datetime(datetime_obj)
        # get difference between satellite and observer locations
        difference = self.__sat_obj - observer_loc  # type: ignore
        # idk how this works
        topocentric = difference.at(time)
        # actually get altitude, azimuth, and distance
        elevation, azimuth, distance = topocentric.altaz()  # type: ignore
        # set values
        self.__elevation = convert_to_dd(elevation)
        self.__azimuth = convert_to_dd(azimuth)
        self.__distance = distance

    def azimuth(self):
        return self.__azimuth

    def elevation(self):
        return self.__elevation

    def distance(self):
        return self.__distance

    def get_tle_tuple(self):
        return self.__tle_tuple

    def get_frequency(self):
        return self.__freq
    
    def get_modulation(self):
        return self.__modulation

    def get_bandwidth(self):
        return self.__bandwidth


def convert_to_dd(angle):
    '''helper function to convert string for az or altto decimal'''
    string = str(angle)
    d_index = string.index("d")
    tokens = string.split()
    deg = float(tokens[0][:d_index])
    mins = float(tokens[1][:-1])
    secs = float(tokens[2][:-1])
    if deg < 0:
        decimal = deg - (mins/60) - secs/3600
    else:
        decimal = deg + (mins/60) + secs/3600
    return decimal

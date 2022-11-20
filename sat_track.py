'''
SATELLITE TRACKING MODULE
this module tracks satellites
'''

from skyfield.api import EarthSatellite, load, wgs84

ts = load.timescale()

class Satellite:
    __slots__=["__tle_file","__azimuth","__elevation","__sat_obj","__distance"]

    def __init__(self,tle_file):
        self.__tle_file=tle_file
        self.parse_tle()

    def parse_tle(self):
        with open(self.__tle_file) as file:
            name = next(file)
            tle_1 = next(file)
            tle_2 = next(file)
        # create ts object
        satellite = EarthSatellite(tle_1, tle_2, name, ts)
        self.__sat_obj=satellite


    def recalculate(self, obs_lat, obs_long, datetime_obj):
        '''
        given an EarthSatellite object and observer latitude and longitude,
        will return a dictionary with 3 keys "azimuth"  "altitude" and "distance"
        '''
        # create observer location object thing
        observer_loc = wgs84.latlon(obs_lat, obs_long)
        #create timescale thing
        time=ts.from_datetime(datetime_obj)
        # get difference between satellite and observer locations
        difference = self.__sat_obj - observer_loc
        # idk how this works
        topocentric = difference.at(time)
        # actually get altitude, azimuth, and distance
        elevation, azimuth, distance = topocentric.altaz()
        #set values
        self.__elevation=convert_to_dd(elevation)
        self.__azimuth=convert_to_dd(azimuth)
        self.__distance=distance

    def azimuth(self):
        return self.__azimuth
    
    def elevation(self):
        return self.__elevation

    def distance(self):
        return self.__distance
    


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

# track_me=Satellite("tle.txt")
# current_time=datetime.datetime(2022,11,20,2,26,30,0,tzinfo=utc)
# track_me.recalculate(43.083556,-77.674333,current_time)
# print(track_me.azimuth())
# print(track_me.elevation())
# print(track_me.distance())

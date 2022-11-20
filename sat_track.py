'''
SATELLITE TRACKING MODULE
this module tracks satellites
main functions of use:
'''

from skyfield.api import EarthSatellite, load, wgs84

FILE = "tle.txt"
OBSERVER_LAT = 43.083799
OBSERVER_LONG = -77.680247

ts = load.timescale()


def create_satellite(file):
    '''
    creates an EarthSatellite object given a TLE and which "number" satellite to start at
    '''
    # open file and read it
    with open(FILE) as file:
        name = next(file)
        tle_1 = next(file)
        tle_2 = next(file)
    # create ts object
    satellite = EarthSatellite(tle_1, tle_2, name, ts)
    return satellite


def get_az_and_alt(satellite, obs_lat, obs_long, time):
    '''
    given an EarthSatellite object and observer latitude and longitude,
    will return a dictionary with 3 keys "azimuth"  "altitude" and "distance"
    '''
    # create observer location object thing
    observer_loc = wgs84.latlon(obs_lat, obs_long)
    # get difference between satellite and observer locations
    difference = satellite - observer_loc
    # idk how this works
    topocentric = difference.at(time)
    # actually get altitude, azimuth, and distance
    alt, az, distance = topocentric.altaz()
    # create dict to return
    az_alt_dict = {}
    az_alt_dict["altitude"] = alt
    az_alt_dict["azimuth"] = az
    az_alt_dict["distance"] = distance
    return az_alt_dict


def convert_to_dd(angle):
    '''helper function to convert string for az or altto decimal'''
    string = str(angle)
    d_index = string.index("d")
    tokens = string.split()
    deg = float(tokens[0][:d_index])
    mins = float(tokens[1][:-1])
    secs = float(tokens[2][:-1])
    print(deg, mins, secs)
    if deg < 0:
        decimal = deg - (mins/60) - secs/3600
    else:
        decimal = deg + (mins/60) + secs/3600
    return decimal


def get_sat_bearings(file, lat, long, time):
    '''
    the best function ever - returns a dictionary with "azimuth", "altitude", and "range"
    azimuth and altitude in degrees, range in km
    '''
    # NEED TO CREATE UTC TIMESTAMP HERE

    
    # create satellite
    satellite = create_satellite(file)
    # get az and alt
    sat_info_dict = get_az_and_alt(satellite, lat, long)
    # formatting/converting
    sat_info_dict["altitude"] = convert_to_dd(sat_info_dict["altitude"])
    sat_info_dict["azimuth"] = convert_to_dd(sat_info_dict["azimuth"])
    sat_info_dict["distance"] = sat_info_dict["distance"].km

    return sat_info_dict

# print('Altitude:', altitude)
# print('Azimuth:', azimuth)
# print('Distance:', distance)


print(get_sat_bearings("tle.txt", 43.083953, -77.674164, ))

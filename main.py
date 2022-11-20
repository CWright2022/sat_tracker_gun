import gps_interface
import sat_track
'''
main file for sat tracker gun
Cayden Wright 11/19/22
'''
gps = gps_interface.GPS_module("/dev/ttyACM0")
satellite = sat_track.Satellite("tle.txt")
while True:
    if gps.refresh():
        satellite.recalculate(gps.latitude(), gps.longitude(), gps.datetime())
        print("----------")
        print("UTC DATETIME: "+str(gps.datetime()))
        print("AZIMUTH:"+str(satellite.azimuth()))
        print("ELEVATION: "+str(satellite.elevation()))
    else:
        print("gps not ready")

'''
GUI module, just testing for now
Cayden Wright 11/20/22
'''
from tkinter import *
import gps_interface
import sat_track
import time
import threading

AZIMUTH = "Azimuth: "
ELEVATION = "Elevation: "

gps = gps_interface.GPS_module("/dev/ttyACM0")
satellite = sat_track.Satellite("/home/pi/sat_tracker_gun/tle.txt")


def recalculate():
    global AZIMUTH
    global ELEVATION
    while not gps.refresh():
        time.sleep(1)
    satellite.recalculate(gps.latitude(), gps.longitude(), gps.datetime())
    AZIMUTH = "Azimuth: "+str(satellite.azimuth())
    ELEVATION = "Elevation: "+str(satellite.elevation())
    azimuth.config(text=AZIMUTH)
    elevation.config(text=ELEVATION)
    thread_obj = threading.Timer(1, recalculate)
    thread_obj.start()


root = Tk()
root.attributes('-fullscreen', True)
azimuth = Label(root, text=AZIMUTH, font=("Arial", 32))
elevation = Label(root, text=ELEVATION, font=("Arial", 32))
# start_button = Button(root, text="Recalculate", command=recalculate)
exit_button = Button(root, text="exit", command=exit)
azimuth.pack()
elevation.pack()
# start_button.pack()
exit_button.pack()
recalculate()
root.mainloop()

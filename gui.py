'''
GUI module, just testing for now
Cayden Wright 11/20/22
'''
from tkinter import *
import gps_interface
import sat_track
import threading


# gps = gps_interface.GPS_module("/dev/ttyACM0")
gps = gps_interface.GPS_module("COM7")
# satellite = sat_track.Satellite("/home/pi/sat_tracker_gun/tle.txt")
satellite = sat_track.Satellite("tle.txt")


def recalculate():
    azimuth_text = ""
    elevation_text = ""
    if gps.refresh():
        satellite.recalculate(gps.latitude(), gps.longitude(), gps.datetime())
        azimuth_text = "Azimuth: "+str(satellite.azimuth())
        elevation_text = "Elevation: "+str(satellite.elevation())
    else:
        azimuth_text = "Azimuth: None"
        elevation_text = "Elevation: None"
    azimuth.config(text=azimuth_text)
    elevation.config(text=elevation_text)

    thread_obj = threading.Timer(1, recalculate)
    thread_obj.daemon = True
    thread_obj.start()


def choose_tle():
    window = Toplevel()
    label = Label(window, text="Hello!")
    exit_button = Button(window, text="exit", command=exit)
    label.pack()
    exit_button.pack()
    window.mainloop()

# root
root = Tk()
root.attributes('-fullscreen', False)

# elements
azimuth = Label(root, text="", font=("Arial", 32))
elevation = Label(root, text="", font=("Arial", 32))
exit_button = Button(root, text="exit", command=exit)
choose_tle_button = Button(root, text="Choose TLE", command=choose_tle)


# pack elements
azimuth.pack()
elevation.pack()
exit_button.pack()
choose_tle_button.pack()

# start recalculating
recalculate()

# root mainloop
root.mainloop()

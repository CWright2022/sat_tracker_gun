'''
GUI module, just testing for now
Cayden Wright 11/20/22
'''
import tkinter as tk
import gps_interface
import sat_track
import threading

# universal preferences
BG_COLOR = "black"
FG_COLOR = "green"
BUTTON_BG_COLOR = "#212121"
FONT_1 = ("System", 32)


# gps = gps_interface.GPS_module("/dev/ttyACM0")
gps = gps_interface.GPS_module("COM7")
# satellite = sat_track.Satellite("/home/pi/sat_tracker_gun/tle.txt")
satellite = sat_track.Satellite("C:\\Users\\minds\\Code\\gps_stuff\\tle.txt")


def start_calculations():
    '''
    starts recalculating satellite alt/azimuth
    '''
    azimuth_text = ""
    elevation_text = ""
    if gps.refresh():
        satellite.recalculate(gps.latitude(), gps.longitude(), gps.datetime())
        azimuth_text = "Azimuth: "+str(round(satellite.azimuth(), 2))
        elevation_text = "Elevation: "+str(round(satellite.elevation(), 2))
    else:
        azimuth_text = "Azimuth: None"
        elevation_text = "Elevation: None"
    azimuth.config(text=azimuth_text)
    elevation.config(text=elevation_text)

    thread_obj = threading.Timer(1, start_calculations)
    thread_obj.daemon = True
    thread_obj.start()


# root
root = tk.Tk()
root.attributes('-fullscreen', True)

# MAIN SCREEN -------------------------
main_screen = tk.Frame(root, bg=BG_COLOR)

# main screen elements
azimuth = tk.Label(main_screen, text="", font=FONT_1, fg=FG_COLOR, bg=BG_COLOR)
elevation = tk.Label(main_screen, text="", font=FONT_1, fg=FG_COLOR, bg=BG_COLOR)
choose_sat_button = tk.Button(main_screen, text="Choose Satellite", font=FONT_1, fg=FG_COLOR, bg=BUTTON_BG_COLOR, command=lambda: call_sat_chooser)
exit_button = tk.Button(main_screen, text="Quit", font=FONT_1, command=exit, fg=FG_COLOR, bg=BUTTON_BG_COLOR)

# pack main screen elements
azimuth.pack()
elevation.pack()
choose_sat_button.pack()
exit_button.pack()

# SATELLITE CHOOSER SCREEN-------------
sat_chooser_screen = tk.Frame(root, bg=BG_COLOR)

# sat chooser sceen elements
title = tk.Label(sat_chooser_screen, text="Choose Satellite", font=FONT_1, fg=FG_COLOR, bg=BG_COLOR)
cancel_button = tk.Button(sat_chooser_screen, text="Cancel", font=FONT_1, fg=FG_COLOR, bg=BUTTON_BG_COLOR)

# pack sat chooser_elements
title.pack()
cancel_button.pack()


def call_sat_chooser():
    sat_chooser_screen.pack()
    main_screen.destroy()


# start recalculating
start_calculations()

# pack screens into root
main_screen.pack()


# root mainloop
root.mainloop()

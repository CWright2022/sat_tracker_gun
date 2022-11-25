'''
GUI module, just testing for now
Cayden Wright 11/20/22
'''
import tkinter as tk
import gps_interface
import sat_track
import threading
import os

# universal preferences
BG_COLOR = "black"
FG_COLOR = "green"
BUTTON_BG_COLOR = "#212121"
FONT_1 = ("System", 32)


# gps = gps_interface.GPS_module("/dev/ttyACM0")
gps = gps_interface.GPS_module("COM7")

CURRENT_SATELLITE = None

# root
root = tk.Tk()
root.attributes('-fullscreen', True)
# root.grid_rowconfigure(0, weight=1)
# root.grid_columnconfigure(0, weight=1)

# MAIN SCREEN -------------------------
main_screen = tk.Frame(root, bg=BG_COLOR)

# main screen elements
azimuth = tk.Label(main_screen, text="", font=FONT_1, fg=FG_COLOR, bg=BG_COLOR)
elevation = tk.Label(main_screen, text="", font=FONT_1, fg=FG_COLOR, bg=BG_COLOR)
range = tk.Label(main_screen, text="", font=FONT_1, fg=FG_COLOR, bg=BG_COLOR)
choose_sat_button = tk.Button(
    main_screen,
    text="Choose Satellite",
    font=FONT_1, fg=FG_COLOR, bg=BUTTON_BG_COLOR,
    command=lambda: goto_sat_chooser(choose_sat_button)
)
options_button = tk.Button(main_screen,
                           text="Options",
                           font=FONT_1, fg=FG_COLOR, bg=BUTTON_BG_COLOR,
                           command=lambda: goto_options_screen(options_button)
                           )
exit_button = tk.Button(main_screen,
                        text="Quit",
                        font=FONT_1, fg=FG_COLOR, bg=BUTTON_BG_COLOR,
                        command=exit
                        )

# pack and  place main screen elements
azimuth.place(relx=0.5, rely=0.5, anchor="s")
elevation.place(relx=0.5, rely=0.5, anchor="n")
choose_sat_button.place(relx=0, rely=0, anchor="nw")
options_button.place(relx=1, rely=1, anchor="se")
exit_button.place(relx=0.5, rely=1, anchor="s")
range.place(relx=1, rely=0, anchor="ne")

# SATELLITE CHOOSER SCREEN-------------
sat_chooser_screen = tk.Frame(root, bg=BG_COLOR)

# sat chooser sceen elements
title = tk.Label(sat_chooser_screen, text="Choose Satellite", font=FONT_1, fg=FG_COLOR, bg=BG_COLOR)
cancel_button_sat_chooser = tk.Button(
    sat_chooser_screen,
    text="Cancel", font=FONT_1, fg=FG_COLOR, bg=BUTTON_BG_COLOR,
    command=lambda: set_current_satellite(None)
)

# pack sat chooser_elements
title.pack()
cancel_button_sat_chooser.pack()

# OPTIONS MENU SCREEN -----
options_screen = tk.Frame(root, bg=BG_COLOR)

# options menu items
shutdown_button = tk.Button(
    options_screen,
    text="Shut Down", font=FONT_1, fg=FG_COLOR, bg=BUTTON_BG_COLOR,
    # command=lambda: os.system("shutdown now -h")
    command=lambda: print("shut down!")
)
recalibrate_button = tk.Button(
    options_screen,
    text="Recalibrate IMU", font=FONT_1, fg=FG_COLOR, bg=BUTTON_BG_COLOR,
    # TODO:actually make this recalibrate the imu
    command=lambda: print("recalibrate me!")
)
cancel_button_options_menu = tk.Button(
    options_screen,
    text="Cancel", font=FONT_1, fg=FG_COLOR, bg=BUTTON_BG_COLOR,
    command=lambda: goto_main_screen(cancel_button_options_menu)

)
# packing items
shutdown_button.pack()
recalibrate_button.pack()
cancel_button_options_menu.pack()


def goto_sat_chooser(current_obj):
    '''
    goes to sat chooser screen
    '''
    # destroy current frame (master of object)
    current_obj.master.pack_forget()
    # show sat chooser_screen
    sat_chooser_screen.pack(fill="both", expand=True)
    # generate buttons
    generate_tle_buttons("./tle.txt")


def goto_main_screen(current_obj):
    current_obj.master.pack_forget()
    main_screen.pack(fill="both", expand=True)


def goto_options_screen(current_obj):
    current_obj.master.pack_forget()
    options_screen.pack(fill="both", expand=True)


def start_calculations():
    '''
    starts recalculating satellite alt/azimuth
    '''
    # if successful, recalculate and update text
    if gps.refresh() and CURRENT_SATELLITE != None:
        CURRENT_SATELLITE.recalculate(gps.latitude(), gps.longitude(), gps.datetime())
        azimuth_text = "Azimuth: "+str(round(CURRENT_SATELLITE.azimuth(), 2))
        elevation_text = "Elevation: "+str(round(CURRENT_SATELLITE.elevation(), 2))
        distance = CURRENT_SATELLITE.distance().km
        range_text = "Range: \n"+str(round(distance, 2))+"km"  # type:ignore
    else:
        azimuth_text = "NO TLE"
        elevation_text = "NO TLE"
        range_text = "NO TLE"
    # actually set text
    azimuth.config(text=azimuth_text)
    elevation.config(text=elevation_text)
    range.config(text=range_text)

    # have this function call itself once every second in the background
    thread_obj = threading.Timer(1, start_calculations)
    thread_obj.daemon = True
    thread_obj.start()


# this is so dirty but the only way I know how
SAT_CHOOSER_BUTTONS = {}


def generate_tle_buttons(tle_file):
    '''
    generates up to 7 (?) buttons, each one will set the currently tracked satellite
    '''
    # create a dictionary, name of sat:tuple with TLE data (name,1,2)
    global SAT_CHOOSER_BUTTONS
    with open(tle_file) as tle_file:
        number_of_sats = 0
        for line in tle_file:
            if number_of_sats == 7:
                break
            if line[0] != 1 and line[0] != 2 and line[0] != "\n":
                SAT_CHOOSER_BUTTONS[line.strip()] = (line.strip(), next(tle_file).strip(), next(tle_file).strip())
                number_of_sats += 1
    # for every key in the dictionary, convert the value to a button
    for key in SAT_CHOOSER_BUTTONS:
        sat_tuple = SAT_CHOOSER_BUTTONS[key]
        button = tk.Button(sat_chooser_screen,
                           text=key,
                           font=FONT_1,
                           fg=FG_COLOR,
                           bg=BUTTON_BG_COLOR,
                           command=lambda sat_tuple=sat_tuple: set_current_satellite(sat_tuple)
                           )

        SAT_CHOOSER_BUTTONS[key] = button
        button.pack()


def set_current_satellite(sat_tuple):
    '''
    super-micro-nano-helper function to set the currently active satellite
    and exit the sat chooser screen
    '''
    global CURRENT_SATELLITE
    global SAT_CHOOSER_BUTTONS
    # set variable
    if sat_tuple is not None:
        CURRENT_SATELLITE = sat_track.Satellite(sat_tuple)
    else:
        CURRENT_SATELLITE = None
    # close sat_chooser and go to main
    for key in SAT_CHOOSER_BUTTONS:
        SAT_CHOOSER_BUTTONS[key].place_forget()
    sat_chooser_screen.pack_forget()
    main_screen.pack(fill="both", expand=True)


# start recalculating
start_calculations()
# start on main screen
main_screen.pack(fill="both", expand=True)

# root mainloop
root.mainloop()

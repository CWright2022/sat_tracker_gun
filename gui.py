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

# just testing with ISS for now)
# CURRENT_SATELLITE = sat_track.Satellite((
#     "(ISS(ZARYA)",
#     "1 25544U 98067A   22327.90527235  .00009819  00000-0  17866-3 0  9997",
#     "2 25544  51.6440 265.3611 0007058 106.6963   0.9885 15.50170803369959"
# ))
try:
    CURRENT_SATELLITE = sat_track.Satellite(())
except IndexError:
    CURRENT_SATELLITE = None

# root
root = tk.Tk()
root.attributes('-fullscreen', True)

# MAIN SCREEN -------------------------
main_screen = tk.Frame(root, bg=BG_COLOR)

# main screen elements
azimuth = tk.Label(main_screen, text="", font=FONT_1, fg=FG_COLOR, bg=BG_COLOR)
elevation = tk.Label(main_screen, text="", font=FONT_1, fg=FG_COLOR, bg=BG_COLOR)
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

# pack main screen elements
azimuth.pack()
elevation.pack()
choose_sat_button.pack()
options_button.pack()
exit_button.pack()

# SATELLITE CHOOSER SCREEN-------------
sat_chooser_screen = tk.Frame(root, bg=BG_COLOR)

# sat chooser sceen elements
title = tk.Label(sat_chooser_screen, text="Choose Satellite", font=FONT_1, fg=FG_COLOR, bg=BG_COLOR)
cancel_button_sat_chooser = tk.Button(
    sat_chooser_screen,
    text="Cancel", font=FONT_1, fg=FG_COLOR, bg=BUTTON_BG_COLOR,
    command=lambda: goto_main_screen(cancel_button_sat_chooser)
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
    command=lambda: os.system("shutdown now -h")
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
    sat_chooser_screen.pack()
    # generate buttons
    generate_tle_buttons("./tle.txt")


def goto_main_screen(current_obj):
    current_obj.master.pack_forget()
    main_screen.pack()


def goto_options_screen(current_obj):
    current_obj.master.pack_forget()
    options_screen.pack()


def start_calculations():
    '''
    starts recalculating satellite alt/azimuth
    '''
    azimuth_text = ""
    elevation_text = ""
    # if successful, recalculate and update text
    if gps.refresh() and CURRENT_SATELLITE != None:
        CURRENT_SATELLITE.recalculate(gps.latitude(), gps.longitude(), gps.datetime())
        azimuth_text = "Azimuth: "+str(round(CURRENT_SATELLITE.azimuth(), 2))
        elevation_text = "Elevation: "+str(round(CURRENT_SATELLITE.elevation(), 2))
    else:
        azimuth_text = "Azimuth: None"
        elevation_text = "Elevation: None"
    # actually set text
    azimuth.config(text=azimuth_text)
    elevation.config(text=elevation_text)

    # have this function call itself once every second in the background
    thread_obj = threading.Timer(1, start_calculations)
    thread_obj.daemon = True
    thread_obj.start()


# this is so dirty but the only way I know how
SAT_CHOOSER_BUTTONS = []


def generate_tle_buttons(tle_file):
    '''
    generates up to 5 (?) buttons, each one will set the currently tracked satellite
    '''
    # create a dictionary, name of sat:tuple with TLE data (name,1,2)
    button_dict = {}
    with open(tle_file) as tle_file:
        number_of_sats = 0
        for line in tle_file:
            if number_of_sats == 5:
                break
            if line[0] != 1 and line[0] != 2 and line[0] != "\n":
                button_dict[line.strip()] = (line.strip(), next(tle_file).strip(), next(tle_file).strip())
                number_of_sats += 1

    button_list = []
    for key in button_dict:
        button = tk.Button(sat_chooser_screen,
                           text=key,
                           font=FONT_1,
                           fg=FG_COLOR,
                           bg=BUTTON_BG_COLOR,
                           command=lambda: set_current_satellite(sat_track.Satellite(button_dict[key]))
                           )
        button_list.append(button)
    for button in button_list:
        button.pack()
    # ew, i feel so gross doing this
    global SAT_CHOOSER_BUTTONS
    SAT_CHOOSER_BUTTONS = button_list


def set_current_satellite(sat_tuple):
    '''
    super-micro-nano-helper function to set the currently active satellite
    and exit the sat chooser screen
    '''
    global CURRENT_SATELLITE
    CURRENT_SATELLITE = sat_tuple
    for button in SAT_CHOOSER_BUTTONS:
        button.pack_forget()
    sat_chooser_screen.pack_forget()
    main_screen.pack()


# start recalculating
start_calculations()
# start on main screen
main_screen.pack()

# root mainloop
root.mainloop()

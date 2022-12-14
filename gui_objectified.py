#!/usr/bin/python3.9
'''
"TRACKELLITE" - the satellite tracker that'll get you kicked out of an airport
by Cayden Wright and Jonathan Godfrey
October 2022
'''
import tkinter as tk
from PIL import Image, ImageTk
import gps_interface
import sat_track
import os
import logging
import datetime
import re

#globals to set UI theme
BG_COLOR = "black"
FG_COLOR = "green"
BUTTON_BG_COLOR = "#212121"
FONT_1 = ("System", 32)

#current directory - soon to be overhauled (one for windows testing, other for RasPi)
# CURRENT_DIR = "C:/Users/minds/Code/gps_stuff/"
CURRENT_DIR = "/home/pi/sat_tracker_gun/"

#how often to refresh satellite data, in ms
UPDATE_RATE = 1000

#define GPS instance (one for Windows, one for Linux)
GPS = gps_interface.GPS_module("/dev/ttyACM0")
# GPS = gps_interface.GPS_module("COM7")

#other miscellaneous globals
CURRENT_SATELLITE = None
CURRENTLY_RECORDING = False


class MainScreen(tk.Frame):
    '''
    define a main screen (with crosshairs and stuff)
    '''
    def __init__(self, parent, *args, **kwargs):
        #init super() (tk.Frame) and other boilerplate
        super().__init__(*args, **kwargs, bg=BG_COLOR)
        self.parent = parent
        logging.debug("init main screen")
        self.recording_text = ""
        self.recording_fg = "red"
        # CROSSHAIRS (damn this is a lot just to display an image)
        # update geometry and determine height
        self.parent.update_idletasks()
        window_height = self.parent.winfo_height()

        # load and process image
        crosshairs = Image.open(CURRENT_DIR+"assets/crosshairs.png")
        crosshairs = crosshairs.resize((window_height, window_height), resample=Image.NEAREST)
        crosshairs = ImageTk.PhotoImage(crosshairs)
        self.crosshairs_label = tk.Label(self, image=crosshairs)
        self.crosshairs_label.photo = crosshairs  # type:ignore

        # place and pack
        self.crosshairs_label.place(relx=0.5, rely=0.5, anchor="center")
        self.pack(fill="both", expand=True)

        # SATELLITE PARAMETERS (temporary until we get the "rolling ball" working)
        self.azimuth = tk.Label(self, text="", font=FONT_1, fg=FG_COLOR, bg=BG_COLOR)
        self.elevation = tk.Label(self, text="", font=FONT_1, fg=FG_COLOR, bg=BG_COLOR)
        self.range = tk.Label(self, text="", font=FONT_1, fg=FG_COLOR, bg=BG_COLOR)
        self.azimuth.place(relx=0.5, rely=0.5, anchor="s")
        self.elevation.place(relx=0.5, rely=0.5, anchor="n")
        self.range.place(relx=1, rely=0, anchor="ne")

        # SAT CHOOSER BUTTON
        global CURRENT_SATELLITE
        # change style according to current Satellite
        if CURRENT_SATELLITE is not None:
            text = CURRENT_SATELLITE.get_tle_tuple()[0]
            fg = FG_COLOR
        else:
            text = "TARGET:\nNO TARGET"
            fg = "red"
        # create,bind, and place
        choose_sat_button = tk.Label(self, text=text, font=FONT_1, fg=fg, bg=BG_COLOR)
        choose_sat_button.bind("<Button-1>", lambda _: self.choose_sats())
        choose_sat_button.place(relx=0, rely=0, anchor="nw")

        # OPTIONS BUTTON
        self.options_button = tk.Button(
            self,
            text="OPTIONS",
            font=FONT_1,
            fg=FG_COLOR,
            bg=BUTTON_BG_COLOR,
            command=self.options
        )
        self.options_button.place(relx=1, rely=1, anchor="se")
        # start calculating position
        self.start_calculations()

        # RECORD BUTTON
        self.record_button = tk.Label(
            self,
            text=self.recording_text,
            fg=self.recording_fg,
            font=FONT_1,
            bg=BG_COLOR
        )
        #bind and place
        self.record_button.bind("<Button-1>", lambda _: self.toggle_recording())
        self.update_record_data()
        self.record_button.place(relx=0, rely=1, anchor="sw")

    def update_record_data(self):
        '''
        updates style of recording button to show current status
        '''
        if CURRENTLY_RECORDING:
            self.record_button.config(text="RECORDING", fg="red")
        else:
            self.record_button.config(text="SDR READY", fg=FG_COLOR)

    def options(self):
        '''
        go to options screen
        '''
        logging.debug("destroy main")
        self.destroy()
        _ = OptionsScreen(self.parent)

    def choose_sats(self):
        '''
        goes to sat chooser screen
        '''
        logging.debug("destroy main")
        self.destroy()
        _ = SatChooserScreen(self.parent)

    def start_calculations(self):
        '''
        starts recalculating satellite alt/azimuth
        '''
        logging.debug("recalculating satellite params")
        # if successful, recalculate and update text
        if GPS.refresh() and CURRENT_SATELLITE != None:
            CURRENT_SATELLITE.recalculate(GPS.latitude(), GPS.longitude(), GPS.datetime())
            azimuth_text = "AZIMUTH: "+str(round(CURRENT_SATELLITE.azimuth(), 2))
            elevation_text = "ELEVATION: "+str(round(CURRENT_SATELLITE.elevation(), 2))
            distance = CURRENT_SATELLITE.distance().km
            range_text = "RANGE: \n"+str(round(distance, 2))+"km"  # type:ignore
        else:
            azimuth_text = "NO DATA"
            elevation_text = "NO DATA"
            range_text = "NO DATA"
        # actually set text
        widget_list = [self.azimuth, self.elevation, self.range]
        i = 0
        for text in [azimuth_text, elevation_text, range_text]:
            widget_list[i].config(fg=FG_COLOR, text=text)
            if text == "NO DATA":
                widget_list[i].config(fg="red")
            i += 1

        # have this function call itself once every second in the background
        self.after(UPDATE_RATE, self.start_calculations)

    def toggle_recording(self):
        '''
        toggles between recording and not
        '''
        global CURRENTLY_RECORDING
        global CURRENT_SATELLITE

        #determine current time to use in recording
        delta = datetime.timedelta(hours=-5)  # only east coast for now lol
        eastern = datetime.timezone(delta)
        time_string = str(GPS.datetime().now(tz=eastern))
        time_string = time_string[5:-16]
        if CURRENT_SATELLITE is None:
            logging.warning("cannot record with no satellite")
        #if we are recording, then stop
        elif CURRENTLY_RECORDING:
            frequency=CURRENT_SATELLITE.get_frequency()
            modulation=CURRENT_SATELLITE.get_modulation()
            bandwidth=CURRENT_SATELLITE.get_bandwidth()
            logging.debug("stop recording")
            os.system(CURRENT_DIR+"stop_recording.sh")
            logging.debug("re-initiate playback: "+frequency+" "+modulation+" "+bandwidth)
            os.system(CURRENT_DIR+"playback.sh "+frequency+" "+modulation+" "+bandwidth)
            CURRENTLY_RECORDING = False
        else:
            #if we aren't recording, then start
            logging.debug("start recording")
            CURRENTLY_RECORDING = True

            #there is probably still some kind of exploit here.
            #I am not inclined to fix it at the moment because this device:
            # 1. stores no personal data
            # 2. is not connected to the internet
            # 3. is a hobby project
            #the cheap sanitation simply prevents simple mistakes by naming a satellite weird
            # Cayden Wright 12-21-22

            #cheap and lazy way of sanitizing input from text file
            satellite_name=re.sub("[/\"\';$#=!>|\\\\]","*",CURRENT_SATELLITE.get_tle_tuple()[0])
            frequency=re.sub("[/\"\';$#=!>|\\\\]","*",CURRENT_SATELLITE.get_frequency())
            modulation=re.sub("[/\"\';$#=!>|\\\\]","*",CURRENT_SATELLITE.get_modulation())
            bandwidth=re.sub("[/\"\';$#=!>|\\\\]","*",CURRENT_SATELLITE.get_bandwidth())
            #form command
            command = CURRENT_DIR+"start_recording.sh "\
            +"\""+frequency+"\" "+"\""+modulation+"\" "+"\""+bandwidth+"\" "\
            +"\""+time_string+"\" "+"\""+satellite_name+"\""
            #run command if we have a satellite selected
            logging.debug("running command: "+command)
            os.system(command)

        self.update_record_data()


class SatChooserScreen(tk.Frame):
    '''
    class to hold satellite choosing screen
    '''
    def __init__(self, parent, *args, **kwargs):
        #init boilerplate
        super().__init__(*args, **kwargs, bg=BG_COLOR)
        self.parent = parent
        logging.debug("initialize sat chooser")

        # generate buttons based on a TLE file
        self.generate_tle_buttons(CURRENT_DIR+"tle.txt")
        self.pack(fill="both", expand=True)

    def go_back(self):
        '''
        go back to main screen
        '''
        logging.debug("destroy sat chooser")
        self.destroy()
        _ = MainScreen(self.parent)

    def generate_tle_buttons(self, tle_file):
        '''
        generates and packs up to 7 (?) buttons, each one will set the currently tracked satellite
        '''
        self.sat_buttons = {}
        # create a dictionary, name of sat:tuple with TLE data (name,1,2)
        with open(tle_file) as tle_file:
            number_of_sats = 0
            for line in tle_file:
                #magic number is right here
                if number_of_sats == 7:
                    break
                if line[0] != 1 and line[0] != 2 and line[0] != "\n":
                    self.sat_buttons[line.strip()] = [(line.strip(), next(tle_file).strip(),
                                                       next(tle_file).strip()), next(tle_file).strip().split(",")]
                    number_of_sats += 1
        # for every key in the dictionary, convert the value to a button
        for key in self.sat_buttons:
            sat_tuple = self.sat_buttons[key][0]
            radio_tuple = self.sat_buttons[key][1]
            button = tk.Button(self,
                               text=key,
                               font=FONT_1,
                               fg=FG_COLOR,
                               bg=BUTTON_BG_COLOR,
                               command=lambda sat_tuple=sat_tuple, radio_tuple=radio_tuple: self.set_satellite(sat_tuple, radio_tuple)
                               )

            self.sat_buttons[key] = button
            button.pack()

    def set_satellite(self, sat_tuple, radio_tuple):
        '''
        goes back to main screen and sets current satellite
        also uses playback.sh to let you hear the satellite
        '''
        logging.debug("setting satellite to "+sat_tuple[0])
        global CURRENT_SATELLITE
        CURRENT_SATELLITE = sat_track.Satellite(sat_tuple, radio_tuple)
        logging.debug("starting playback: "+radio_tuple[0]+" "+radio_tuple[1]+" "+radio_tuple[2])
        os.system(CURRENT_DIR+"playback.sh "+radio_tuple[0]+" "+radio_tuple[1]+" "+radio_tuple[2])
        logging.debug("destroy sat chooser")
        self.destroy()
        _ = MainScreen(self.parent)


class OptionsScreen(tk.Frame):
    '''
    class to hold options screen
    '''
    def __init__(self, parent, *args, **kwargs):
        super().__init__(*args, **kwargs, bg=BG_COLOR)
        self.parent = parent
        logging.debug("initialize options screen")

        # shutdown button
        self.shutdown_button = tk.Button(
            self,
            text="SHUT DOWN",
            font=FONT_1,
            fg=FG_COLOR,
            bg=BUTTON_BG_COLOR,
            # command=lambda: os.system("shutdown now -h")
            command=exit
        )
        self.shutdown_button.pack()

        # recalibrate button
        self.recalibrate_button = tk.Button(
            self,
            text="RECALIBRATE SENSORS",
            font=FONT_1,
            fg=FG_COLOR,
            bg=BUTTON_BG_COLOR,
            command=self.recalibrate
        )
        self.recalibrate_button.pack()

        # cancel button
        self.cancel_button = tk.Button(
            self,
            text="CANCEL",
            font=FONT_1,
            fg=FG_COLOR,
            bg=BUTTON_BG_COLOR,
            command=self.cancel
        )
        self.cancel_button.pack()

        # pack self
        self.pack(fill="both", expand=True)

    def cancel(self):
        '''
        go back to main screen
        '''
        logging.debug("destroy options")
        self.destroy()
        _ = MainScreen(self.parent)

    def recalibrate(self):
        '''
        go to calibration screen
        '''
        logging.debug("destroy options")
        self.destroy()
        _ = InitScreen(self.parent)


class InitScreen(tk.Frame):
    '''
    initialization/calibration screen
    '''
    def __init__(self, parent, *args, **kwargs):
        #init boilerplate
        super().__init__(*args, **kwargs, bg=BG_COLOR)
        self.parent = parent
        gps_text = "Waiting for GPS"
        logging.debug("initialize calibration/init screen")

        # GPS status label
        self.gps_status_label = tk.Label(
            self,
            text=gps_text,
            fg="red",
            bg=BG_COLOR,
            font=FONT_1
        )
        #place label
        self.gps_status_label.place(relx=0.5, rely=0.2, anchor="s")
        # show GPS fix status
        self.show_gps_status()

        # DO IMU CALCULATION SOMEWHERE IN HERE
        self.imu_status_label = tk.Label(
            self,
            text="IMU OK",
            font=FONT_1,
            fg=FG_COLOR,
            bg=BG_COLOR

        )
        self.imu_status_label.place(relx=0.5, rely=0.4, anchor="n")
        # continue button
        self.continue_button = tk.Button(
            text="CONTINUE",
            font=FONT_1,
            fg=FG_COLOR,
            bg=BUTTON_BG_COLOR,
            command=self.continue_to_main
        )
        self.continue_button.place(relx=0.5, rely=1, anchor="s")

        self.pack(fill="both", expand=True)

    def continue_to_main(self):
        '''
        goes to main screen
        '''
        logging.debug("destroy init")
        self.destroy()
        _ = MainScreen(self.parent)

    def show_gps_status(self):
        '''
        gets GPS status and displays if it's good or not
        '''
        if GPS.refresh():
            self.gps_status_label.config(text="GPS OK", fg=FG_COLOR)
        else:
            self.gps_status_label.config(text="NO GPS", fg="red")
        self.after(UPDATE_RATE, self.show_gps_status)
        logging.debug("update GPS data for calibration screen")


def start_logs():
    '''
    initialize logging for the application
    '''
    # if log is over 100MB, delete it and start new
    global CURRENT_DIR
    log_refreshed = False
    try:
        log_size = os.path.getsize(CURRENT_DIR+"sat_tracker.log")
    except:
        log_size=0
    if log_size*100000000 > 100:
        os.remove(CURRENT_DIR+"sat_tracker.log")
        log_refreshed = True
    # calculate a basic string representation of the current date/time for use in file naming
    delta = datetime.timedelta(hours=-5)  # only east coast for now lol
    eastern = datetime.timezone(delta)
    time_string = str(GPS.datetime().now(tz=eastern))
    # initialize logs and say hello
    logging.basicConfig(filename=CURRENT_DIR+"sat_tracker.log", level=logging.DEBUG)
    logging.info("Starting Trackellite v0.8 (or something like that)")
    logging.info("Current time (UTC) is "+time_string)
    if log_refreshed:
        logging.warning("previous log was deleted due to size being > 100MB")


def main():
    start_logs()
    root = tk.Tk()
    root.attributes('-fullscreen', True)
    logging.debug("initialized Tk root")
    _ = InitScreen(root)
    root.mainloop()


if __name__ == '__main__':
    main()

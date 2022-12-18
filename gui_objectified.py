#!/usr/bin/python3.9
import tkinter as tk
from PIL import Image, ImageTk
import gps_interface
import sat_track
import os
import logging
import datetime

BG_COLOR = "black"
FG_COLOR = "green"
BUTTON_BG_COLOR = "#212121"
FONT_1 = ("System", 32)

# CURRENT_DIR = "C:/Users/minds/Code/gps_stuff/"
CURRENT_DIR = "/home/pi/sat_tracker_gun/"

UPDATE_RATE = 1000

GPS = gps_interface.GPS_module("/dev/ttyACM0")
# GPS = gps_interface.GPS_module("COM7")

CURRENT_SATELLITE = None

CURRENTLY_RECORDING = False


class MainScreen(tk.Frame):
    def __init__(self, parent, *args, **kwargs):
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

        # SATELLITE PARAMETERS (temp until we get the "rolling ball" working)
        self.azimuth = tk.Label(self, text="", font=FONT_1, fg=FG_COLOR, bg=BG_COLOR)
        self.elevation = tk.Label(self, text="", font=FONT_1, fg=FG_COLOR, bg=BG_COLOR)
        self.range = tk.Label(self, text="", font=FONT_1, fg=FG_COLOR, bg=BG_COLOR)
        self.azimuth.place(relx=0.5, rely=0.5, anchor="s")
        self.elevation.place(relx=0.5, rely=0.5, anchor="n")
        self.range.place(relx=1, rely=0, anchor="ne")

        # SAT CHOOSER BUTTON
        global CURRENT_SATELLITE
        # change style accordingly
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
        self.record_button.bind("<Button-1>", lambda _: self.toggle_recording())
        self.update_record_data()
        self.record_button.place(relx=0, rely=1, anchor="sw")

    def update_record_data(self):
        if CURRENTLY_RECORDING:
            self.record_button.config(text="RECORDING", fg="red")
        else:
            self.record_button.config(text="SDR READY", fg=FG_COLOR)

    def options(self):
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
        global CURRENTLY_RECORDING
        delta = datetime.timedelta(hours=-5)  # only east coast for now lol
        eastern = datetime.timezone(delta)
        time_string = str(GPS.datetime().now(tz=eastern))
        if CURRENTLY_RECORDING:
            logging.debug("stop recording")
            os.system(CURRENT_DIR+"stop_recording.sh")
            CURRENTLY_RECORDING = False
        else:
            logging.debug("start recording")
            CURRENTLY_RECORDING = True
            if CURRENT_SATELLITE != None:
                logging.debug("running command: /home/pi/sat_tracker_gun/start_recording.sh "
                              + CURRENT_SATELLITE.get_frequency()+" "
                              + CURRENT_SATELLITE.get_modulation()+" "
                              + CURRENT_SATELLITE.get_bandwidth()+" "
                              + str(GPS.datetime()))
                os.system(CURRENT_DIR+"start_recording.sh "
                          + CURRENT_SATELLITE.get_frequency()+" "
                          + CURRENT_SATELLITE.get_modulation()+" "
                          + CURRENT_SATELLITE.get_bandwidth()+" "
                          + time_string)
            else:
                self.toggle_recording()

        self.update_record_data()


class SatChooserScreen(tk.Frame):
    def __init__(self, parent, *args, **kwargs):
        super().__init__(*args, **kwargs, bg=BG_COLOR)
        self.parent = parent
        logging.debug("initialize sat chooser")
        # generate buttons based ona TLE file
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
        '''
        logging.debug("setting satellite to "+sat_tuple[0])
        global CURRENT_SATELLITE
        CURRENT_SATELLITE = sat_track.Satellite(sat_tuple, radio_tuple)
        logging.debug("destroy sat chooser")
        self.destroy()
        _ = MainScreen(self.parent)


class OptionsScreen(tk.Frame):
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
        logging.debug("destroy options")
        self.destroy()
        _ = MainScreen(self.parent)

    def recalibrate(self):
        logging.debug("destroy options")
        self.destroy()
        _ = InitScreen(self.parent)


class InitScreen(tk.Frame):
    def __init__(self, parent, *args, **kwargs):
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
        logging.debug("destroy init")
        self.destroy()
        _ = MainScreen(self.parent)

    def show_gps_status(self):
        if GPS.refresh():
            self.gps_status_label.config(text="GPS OK", fg=FG_COLOR)
        else:
            self.gps_status_label.config(text="NO GPS", fg="red")
        self.after(UPDATE_RATE, self.show_gps_status)
        logging.debug("update GPS data for calibration screen")


def utc_to_est(utc_dt):
    fmt = "%Y-%m-%d %H:%M:%S"
    est_time = utc_dt.astimezone(datetime.timezone('US/Eastern'))
    return est_time.strftime(fmt)


def start_logs():
    '''
    initialize logging for the application
    '''
    # if log is over 100MB, delete it and start new
    global CURRENT_DIR
    log_refreshed = False
    log_size = os.path.getsize(CURRENT_DIR+"sat_tracker.log")
    if log_size*1000000 > 100:
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

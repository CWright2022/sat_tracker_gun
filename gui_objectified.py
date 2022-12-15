#!/usr/bin/python3.9
import tkinter as tk
from PIL import Image, ImageTk
import gps_interface
import threading
import sat_track
import os
import time

BG_COLOR = "black"
FG_COLOR = "green"
BUTTON_BG_COLOR = "#212121"
FONT_1 = ("System", 32)

UPDATE_RATE = 1000

GPS = gps_interface.GPS_module("COM7")

CURRENT_SATELLITE = None

CURRENTLY_RECORDING = False


class MainScreen(tk.Frame):
    def __init__(self, parent, *args, **kwargs):
        super().__init__(*args, **kwargs, bg=BG_COLOR)
        self.parent = parent
        print("main init")
        self.recording_text = ""
        self.recording_fg = "red"
        # CROSSHAIRS (damn this is a lot just to display an image)
        # update geometry and determine height
        self.parent.update_idletasks()
        window_height = self.parent.winfo_height()

        # load and process image
        crosshairs = Image.open("./assets/crosshairs.png")
        crosshairs = crosshairs.resize((window_height, window_height), Image.Resampling.NEAREST)
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
        print("main->options")
        print("destroy main")
        self.destroy()
        _ = OptionsScreen(self.parent)

    def choose_sats(self):
        '''
        goes to sat chooser screen
        '''
        print("main->satchooser")
        print("destroy main")
        self.destroy()
        _ = SatChooserScreen(self.parent)

    def start_calculations(self):
        '''
        starts recalculating satellite alt/azimuth
        '''
        print("calc angles")
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
        if CURRENTLY_RECORDING:
            print("stop recording")
            os.system("/home/pi/sat_tracker_gun/stop_recording.sh")
            CURRENTLY_RECORDING = False
        else:
            print("start recording")
            CURRENTLY_RECORDING = True
            if CURRENT_SATELLITE != None:
                os.system("/home/pi/sat_tracker_gun/start_recording.sh "
                          + CURRENT_SATELLITE.get_frequency()+" "
                          + CURRENT_SATELLITE.get_modulation()+" "
                          + CURRENT_SATELLITE.get_bandwidth())
            else:
                self.toggle_recording()

        self.update_record_data()


class SatChooserScreen(tk.Frame):
    def __init__(self, parent, *args, **kwargs):
        super().__init__(*args, **kwargs, bg=BG_COLOR)
        self.parent = parent
        print("init sat chooser")
        # quitButton = tk.Button(self, text='Quit', command=lambda: self.go_back())
        # quitButton.place(relx=0.5, rely=1, anchor="s")
        # generate buttons based ona TLE file
        self.generate_tle_buttons("./tle.txt")
        self.pack(fill="both", expand=True)

    def go_back(self):
        '''
        go back to main screen
        '''
        print("sat_chooser->main")
        print("destroy sat chooser")
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
                               command=lambda sat_tuple=sat_tuple: self.set_satellite(sat_tuple, radio_tuple)
                               )

            self.sat_buttons[key] = button
            button.pack()

    def set_satellite(self, sat_tuple, radio_tuple):
        '''
        goes back to main screen and sets current satellite
        '''
        print("set satellite")
        global CURRENT_SATELLITE
        CURRENT_SATELLITE = sat_track.Satellite(sat_tuple, radio_tuple)
        print("destroy sat chooser")
        self.destroy()
        _ = MainScreen(self.parent)


class OptionsScreen(tk.Frame):
    def __init__(self, parent, *args, **kwargs):
        super().__init__(*args, **kwargs, bg=BG_COLOR)
        self.parent = parent
        print("init options")

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
        print("cancel options")
        print("destroy options")
        self.destroy()
        _ = MainScreen(self.parent)

    def recalibrate(self):
        print("recalibrate")
        print("destroy options")
        self.destroy()
        _ = InitScreen(self.parent)


class InitScreen(tk.Frame):
    def __init__(self, parent, *args, **kwargs):
        super().__init__(*args, **kwargs, bg=BG_COLOR)
        self.parent = parent
        gps_text = "Waiting for GPS"
        print("init init")

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
        print("init->main")
        print("destroy init")
        self.destroy()
        _ = MainScreen(self.parent)

    def show_gps_status(self):
        if GPS.refresh():
            self.gps_status_label.config(text="GPS OK", fg=FG_COLOR)
        else:
            self.gps_status_label.config(text="NO GPS", fg="red")
        self.after(UPDATE_RATE, self.show_gps_status)
        print("update GPS for init")


def main():
    root = tk.Tk()
    root.attributes('-fullscreen', True)
    _ = InitScreen(root)
    root.mainloop()


if __name__ == '__main__':
    main()

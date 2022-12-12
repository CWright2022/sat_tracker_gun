import tkinter as tk
from PIL import Image, ImageTk
import gps_interface
import threading

BG_COLOR = "black"
FG_COLOR = "green"
BUTTON_BG_COLOR = "#212121"
FONT_1 = ("System", 32)

GPS = gps_interface.GPS_module("COM7")

CURRENT_SATELLITE = None


class MainScreen(tk.Frame):
    def __init__(self, parent, *args, **kwargs):
        super().__init__(*args, **kwargs, bg=BG_COLOR)
        self.parent = parent
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
            text = CURRENT_SATELLITE[0]
            fg = FG_COLOR
        else:
            text = "TARGET:\nNO TARGET"
            fg = "red"
        # create,bind, and place
        choose_sat_button = tk.Label(self, text=text, font=FONT_1, fg=fg, bg=BG_COLOR)
        choose_sat_button.bind("<Button-1>", lambda _: self.choose_sats())
        choose_sat_button.place(relx=0, rely=0, anchor="nw")
        # start calculating position
        self.start_calculations()

    def choose_sats(self):
        '''
        goes to sat chooser screen
        '''
        self.destroy()
        _ = SatChooserScreen(self.parent)

    def start_calculations(self):
        '''
        starts recalculating satellite alt/azimuth
        '''
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
    thread_obj = threading.Timer(1, start_calculations)
    thread_obj.daemon = True
    thread_obj.start()


class SatChooserScreen(tk.Frame):
    def __init__(self, parent, *args, **kwargs):
        super().__init__(*args, **kwargs, bg=BG_COLOR)
        self.parent = parent
        # quitButton = tk.Button(self, text='Quit', command=lambda: self.go_back())
        # quitButton.place(relx=0.5, rely=1, anchor="s")
        # generate buttons based ona TLE file
        self.generate_tle_buttons("./tle.txt")
        self.pack(fill="both", expand=True)

    def go_back(self):
        '''
        go back to main screen
        '''
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
                    self.sat_buttons[line.strip()] = (line.strip(), next(tle_file).strip(), next(tle_file).strip())
                    number_of_sats += 1
        # for every key in the dictionary, convert the value to a button
        for key in self.sat_buttons:
            sat_tuple = self.sat_buttons[key]
            button = tk.Button(self,
                               text=key,
                               font=FONT_1,
                               fg=FG_COLOR,
                               bg=BUTTON_BG_COLOR,
                               command=lambda sat_tuple=sat_tuple: self.set_satellite(sat_tuple)
                               )

            self.sat_buttons[key] = button
            button.pack()

    def set_satellite(self, sat_tuple):
        '''
        goes back to main screen and sets current satellite
        '''
        self.destroy()
        global CURRENT_SATELLITE
        CURRENT_SATELLITE = sat_tuple
        _ = MainScreen(self.parent)


def main():
    root = tk.Tk()
    root.attributes('-fullscreen', True)
    _ = MainScreen(root)
    root.mainloop()


if __name__ == '__main__':
    main()

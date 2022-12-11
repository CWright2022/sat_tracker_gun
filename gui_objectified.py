import tkinter as tk
from PIL import Image, ImageTk


class MainScreen(tk.Frame):
    def __init__(self, parent, *args, **kwargs):
        tk.Frame.__init__(self, parent, *args, **kwargs, bg="black")
        self.parent = parent
        self.parent.update()
        window_height = parent.winfo_height()
        crosshairs_raw = Image.open("./assets/crosshairs.png")
        crosshairs_raw = crosshairs_raw.resize((window_height, window_height), Image.Resampling.NEAREST)
        crosshairs = ImageTk.PhotoImage(crosshairs_raw)
        self.crosshairs_label = tk.Label(self, image=crosshairs)
        self.crosshairs_label.place(relx=0.5, rely=0.5, anchor="center")
        self.pack(fill="both", expand=True)

    def new_window(self):
        self.newWindow = tk.Frame(self.master)
        self.app = Demo2(self.newWindow)


class Demo2:
    def __init__(self, master):
        self.master = master
        self.frame = tk.Frame(self.master)
        self.quitButton = tk.Button(self.frame, text='Quit', width=25, command=self.close_windows)
        self.quitButton.pack()
        self.frame.pack()

    def close_windows(self):
        self.master.destroy()


def main():
    root = tk.Tk()
    root.attributes('-fullscreen', True)
    app = MainScreen(root)
    root.mainloop()


if __name__ == '__main__':
    main()

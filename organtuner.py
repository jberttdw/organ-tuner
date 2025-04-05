#!/usr/bin/env python3

# Don't forget to run `pip install mido rtmidi`
# Also, connecting a remote shutter might take some work, maybe even the 'evdev' package:
# https://stackoverflow.com/questions/54745576/detecting-the-buttons-on-a-bluetooth-remote-hid-over-gatt

import mido
import argparse
import time
import tkinter as tk
from organcontroller import *
from organinstrument import *

ports = mido.get_output_names()

portinfo = "Available ports:\n" + ''.join(map(lambda port: "- " + port + "\n", ports))
print(portinfo)

argparser = argparse.ArgumentParser(prog="organtuner")
#argparser.add_argument("-trigger", help="File path to /dev/input/X to which this script will listen. Leave out for keyboard trigger.")
argparser.add_argument("port", help="Name of port corresponding to the device to which MIDI notes are sent. ")

args = argparser.parse_args()


class MainApplication(tk.Frame):
    def __init__(self, parent, organ_controller, *args, **kwargs):
        self.parent = parent
        self.frame = tk.Frame(parent, *args, **kwargs)
        self.organ_controller = organ_controller
        left_frame = tk.Frame(self.frame)
        left_frame.grid(row=0, column=0, sticky="nswe")
        instrument_label = tk.Label(left_frame, text="Instrument {}".format(self.organ_controller.instrument_name))
        instrument_label.config(font=('TkDefaultFont', 44))
        #instrument_label.pack()
        instrument_label.grid(row=0, column=0, sticky="nswe")
        ref_instrument_label = tk.Label(left_frame, text="Instrument {}".format(self.organ_controller.ref_instrument_name))
        ref_instrument_label.config(font=('TkDefaultFont', 44))
        #ref_instrument_label.pack()
        ref_instrument_label.grid(row=1, column=0, sticky="nswe")

        right_frame = tk.Frame(self.frame)
        right_frame.grid(row=0, column=1, sticky="nswe")
        self.note_var = tk.StringVar()
        self.note_var.set(self.organ_controller.get_note_name())
        note_label = tk.Label(right_frame, textvariable=self.note_var)
        note_label.config(font=('TkDefaultFont', 60))
        #note_label.pack()
        note_label.grid(row=0, column=0, columnspan=2, sticky="nswe")
        self.status_var = tk.StringVar()
        self.status_var.set("Target: ⏵")
        status_label = tk.Label(right_frame, textvariable=self.status_var)
        status_label.config(font=('TkDefaultFont', 60))
        status_label.grid(row=1,column=0, sticky="nswe")

        self.frame.pack()
        parent.bind("<Button-1>", self.on_left_mouse_click)
        parent.bind("<Double-Button-1>", self.on_left_mouse_double)
        parent.bind("<Button-3>", self.on_right_mouse_click)
        parent.bind("<Double-Button-3>", self.on_right_mouse_double)
        parent.bind("<Button-2>", self.on_middle_mouse_click)
        parent.bind("<Double-Button-2>", self.on_middle_mouse_double)
        parent.grab_set_global()
        self.check_double_left = False
        self.check_double_right = False
        self.check_double_middle = False

        self.organ_controller.start()


    def on_left_mouse_click(self, event = None):
        # Delay acting until we know we didn't receive double click's first button down event
        self.frame.after(200, self.on_left_mouse_action)

    def on_left_mouse_double(self, event = None):
        self.check_double_left = True

    def on_left_mouse_action(self, event = None):
        if self.check_double_left:
            self.organ_controller.play_prev_note()
        else:
            self.organ_controller.play_next_note()
        self.note_var.set(self.organ_controller.get_note_name())
        self.check_double_left = False

    def on_right_mouse_click(self, event = None):
        self.frame.after(200, self.on_right_mouse_action)

    def on_right_mouse_double(self, event = None):
        self.check_double_right = True

    def on_right_mouse_action(self, event = None):
        #if self.check_double_right:
        # Do small chord or figure test
        #else:
            self.organ_controller.toggle_test()

    def on_middle_mouse_click(self, event = None):
        self.frame.after(200, self.on_middle_mouse_action)

    def on_middle_mouse_double(self, event = None):
        self.check_double_middle = True

    def on_middle_mouse_action(self, event = None):
        #if self.check_double_middle:
        # Switch chord actions
        #else:
        self.organ_controller.toggle_pause()
        if self.organ_controller.is_playing:
            self.status_var.set("Target:⏵")
        else:
            self.status_var.set("Target:⏸")



if __name__ == "__main__":
    root = tk.Tk()

    organ_controller = OrganController(args.port)
    
    def on_closing(window):
        organ_controller.stop()
        root.destroy()

    app = MainApplication(root, organ_controller)
    #root.wm_overrideredirect(True)
    root.geometry("{0}x{1}+0+0".format(root.winfo_screenwidth(), root.winfo_screenheight()))
    root.bind("<Escape>", on_closing)
    #.pack(side="top", fill="both", expand=True)
    root.mainloop()


# Todo
# setup main window
# main window splits in a left and right half
# left half has actions
# right half shows current key and instrument, pause / play button (U+23F8 ⏸ vs U+23F5 ⏵)
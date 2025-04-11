#!/usr/bin/env python3

# Don't forget to run `pip install mido rtmidi`
# Also, connecting a remote shutter might take some work, maybe even the 'evdev' package:
# https://stackoverflow.com/questions/54745576/detecting-the-buttons-on-a-bluetooth-remote-hid-over-gatt

import mido
import argparse
import time
import traceback
import tkinter as tk
from organtuner.organcontroller import *
from organtuner.organinstrument import *
from organtuner.ui.mainwindow import *

ports = mido.get_output_names()

portinfo = "Available ports:\n" + ''.join(map(lambda port: "- " + port + "\n", ports))
print(portinfo)

argparser = argparse.ArgumentParser(prog="organtuner")
#argparser.add_argument("-trigger", help="File path to /dev/input/X to which this script will listen. Leave out for keyboard trigger.")
argparser.add_argument("port", help="Name of port corresponding to the device to which MIDI notes are sent. ")

args = argparser.parse_args()


if __name__ == "__main__":
    root = tk.Tk()

    organ_controller = OrganController(args.port)
    
    def on_closing(window):
        try:
            organ_controller.stop()
        except Exception:
            traceback.print_exc()
        root.destroy()


    app = MainApplication(root, organ_controller)
    root.wm_overrideredirect(True)
    root.geometry("{0}x{1}+0+0".format(root.winfo_screenwidth(), root.winfo_screenheight()))
    root.bind("<Escape>", on_closing)
    #.pack(side="top", fill="both", expand=True)
    root.mainloop()


# Todo
# setup main window
# main window splits in a left and right half
# left half has actions
# right half shows current key and instrument, pause / play button (U+23F8 ⏸ vs U+23F5 ⏵)
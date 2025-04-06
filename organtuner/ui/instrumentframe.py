import tkinter as tk
from organtuner.ui import constants

class InstrumentFrame(tk.Frame):
    def __init__(self, parent, organ_controller, *args, **kwargs):
        self.parent = parent
        self.frame = tk.Frame(parent)
        self.organ_controller = organ_controller


        self.instrument_var = tk.StringVar()
        instrument_label = tk.Label(self.frame, textvariable=self.instrument_var)
        instrument_label.config(font=(constants.DEFAULT_FONT, constants.LARGE_FONTSIZE))
        instrument_label.grid(row=0, column=0, sticky="nswe")

        self.ref_instrument_var = tk.StringVar()
        ref_instrument_label = tk.Label(self.frame, textvariable=self.ref_instrument_var)
        ref_instrument_label.config(font=(constants.DEFAULT_FONT, constants.LARGE_FONTSIZE))
        ref_instrument_label.grid(row=1, column=0, sticky="nswe")

        self.instrument_list = tk.Listbox(self.frame)
        for name in self.organ_controller.instrument_names:
            print(name)
            self.instrument_list.insert(tk.END, name)
        self.instrument_list.grid(row=2, column=0, sticky="nswe")
        self.instrument_list.configure(state='disabled', font=(constants.DEFAULT_FONT, constants.LARGE_FONTSIZE))


    def update(self):
        self.instrument_var.set("Comparing {}".format(self.organ_controller.ref_instrument_name))
        self.ref_instrument_var.set("Tuning {}".format(self.organ_controller.instrument_name))

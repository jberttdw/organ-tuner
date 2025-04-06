import tkinter as tk
from organtuner.ui import constants

class StatusFrame(tk.Frame):
    def __init__(self, parent, organ_controller, *args, **kwargs):
        self.parent = parent
        self.frame = tk.Frame(parent)
        self.organ_controller = organ_controller
        self.frame.grid(row=0, column=1, pady=400)

        self.note_var = tk.StringVar()
        self.note_var.set("")
        note_label = tk.Label(self.frame, textvariable=self.note_var)
        note_label.config(font=(constants.DEFAULT_FONT, constants.XL_FONTSIZE))
        note_label.grid(row=0, column=0, columnspan=2, sticky="nswe")

        self.status_var = tk.StringVar()
        self.status_var.set("")
        status_label = tk.Label(self.frame, textvariable=self.status_var)
        status_label.config(font=(constants.DEFAULT_FONT, constants.XL_FONTSIZE))
        status_label.grid(row=1,column=0, sticky="nswe")

        self.ref_status_var = tk.StringVar()
        self.ref_status_var.set("")
        ref_status_label = tk.Label(self.frame, textvariable=self.ref_status_var)
        ref_status_label.config(font=(constants.DEFAULT_FONT, constants.XL_FONTSIZE))
        ref_status_label.grid(row=2,column=0, sticky="nswe")


    def update(self):
        self.note_var.set(self.organ_controller.get_note_name())
        if self.organ_controller.is_playing:
            self.status_var.set("Target:⏵")
        else:
            self.status_var.set("Target:⏸")
        if self.organ_controller.is_ref_playing:
            self.ref_status_var.set("Reference:⏵")
        else:
            self.ref_status_var.set("Reference:⏸")
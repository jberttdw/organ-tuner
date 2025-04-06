import tkinter as tk
from organtuner.ui import constants, statusframe

class MainApplication(tk.Frame):
    def __init__(self, parent, organ_controller, *args, **kwargs):
        self.parent = parent
        self.frame = tk.Frame(parent, *args, **kwargs)
        self.organ_controller = organ_controller

        left_frame = tk.Frame(self.frame)
        left_frame.grid(row=0, column=0, sticky="nswe", padx=80)
        instrument_label = tk.Label(left_frame, text="Tuning {}".format(self.organ_controller.instrument_name))
        instrument_label.config(font=(constants.DEFAULT_FONT, constants.LARGE_FONTSIZE))
        instrument_label.grid(row=0, column=0, sticky="nswe")
        ref_instrument_label = tk.Label(left_frame, text="Comparing {}".format(self.organ_controller.ref_instrument_name))
        ref_instrument_label.config(font=(constants.DEFAULT_FONT, constants.LARGE_FONTSIZE))
        ref_instrument_label.grid(row=1, column=0, sticky="nswe")

        self.status_frame = statusframe.StatusFrame(self.frame, self.organ_controller)

        self.frame.pack()
        parent.bind("<Button-1>", self.on_left_mouse_click)
        parent.bind("<Double-Button-1>", self.on_left_mouse_double)
        parent.bind("<Button-3>", self.on_right_mouse_click)
        parent.bind("<Double-Button-3>", self.on_right_mouse_double)
        parent.bind("<Button-2>", self.on_middle_mouse_click)
        parent.bind("<Double-Button-2>", self.on_middle_mouse_double)
        # This might actually be button 4 and 5 on X11 platforms
        parent.bind("<MouseWheel>", self.on_scroll_action)
        parent.grab_set_global()
        self.check_double_left = False
        self.check_double_right = False
        self.check_double_middle = False
        self.pick_instrument_mode = False

        self.organ_controller.start()
        self.status_frame.update()


    def on_left_mouse_click(self, event = None):
        # Delay acting until we know we didn't receive double click's first button down event
        self.frame.after(400, self.on_left_mouse_action)

    def on_left_mouse_double(self, event = None):
        self.check_double_left = True

    def on_left_mouse_action(self, event = None):
        if self.pick_instrument_mode:
            return
        if self.check_double_left:
            self.organ_controller.play_prev_note()
        else:
            self.organ_controller.play_next_note()
        self.status_frame.update()
        self.check_double_left = False           




    def on_right_mouse_click(self, event = None):
        self.frame.after(400, self.on_right_mouse_action)

    def on_right_mouse_double(self, event = None):
        self.check_double_right = True

    def on_right_mouse_action(self, event = None):
        if self.pick_instrument_mode:
            return
        #if self.check_double_right:
        # Do small chord or figure test
        #else:
        self.organ_controller.toggle_test()
        self.status_frame.update()
        self.check_double_right = False





    def on_middle_mouse_click(self, event = None):
        self.frame.after(400, self.on_middle_mouse_action)

    def on_middle_mouse_double(self, event = None):
        self.check_double_middle = True

    def on_middle_mouse_action(self, event = None):
        # Exit instrument picking mode
        if self.pick_instrument_mode:
            self.pick_instrument_mode = False
            return
        if self.check_double_middle:
            if self.organ_controller.is_playing:
                self.organ_controller.toggle_pause()
            self.pick_instrument_mode = True
        else:
            self.organ_controller.toggle_pause()
        self.status_frame.update()
        self.check_double_middle = False



    def on_scroll_action(self, event = None):
        if not self.pick_instrument_mode:
            return
        if event.delta <= 0:
            print("up")
        else:
            print("down")    

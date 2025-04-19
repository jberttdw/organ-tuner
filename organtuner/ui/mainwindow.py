import tkinter as tk
from organtuner.ui import constants, statusframe, instrumentframe

class MainApplication(tk.Frame):
    def __init__(self, parent, organ_controller, *args, **kwargs):
        self.parent = parent
        self.frame = tk.Frame(parent, *args, **kwargs)
        self.organ_controller = organ_controller

        self.instrument_frame = instrumentframe.InstrumentFrame(self.frame, self.organ_controller)
        self.instrument_frame.frame.grid(row=0, column=0, sticky="nswe", padx=10)

        self.status_frame = statusframe.StatusFrame(self.frame, self.organ_controller)
        self.status_frame.frame.grid(row=0, column=1, pady=400)

        self.frame.pack()
        parent.bind("<Button-1>", self.on_left_mouse_click)
        parent.bind("<Double-Button-1>", self.on_left_mouse_double)
        parent.bind("<Button-3>", self.on_right_mouse_click)
        parent.bind("<Double-Button-3>", self.on_right_mouse_double)
        parent.bind("<Button-2>", self.on_middle_mouse_click)
        parent.bind("<Double-Button-2>", self.on_middle_mouse_double)
        # This might actually be button 4 and 5 on X11 platforms
        parent.bind("<MouseWheel>", self.on_scroll_action)
        # Mouse up - down
        parent.bind("<Button-4>", self.on_scroll_up_action)
        parent.bind("<Button-5>", self.on_scroll_dn_action)
        self.check_double_left = False
        self.check_double_right = False
        self.check_double_middle = False
        self.pick_instrument_mode = False

        self.organ_controller.start()
        self.instrument_frame.update()
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
        # Confirm instrument choice if instrument picking was active
        if self.pick_instrument_mode:
            self.pick_instrument_mode = False
            self.instrument_frame.confirm_instrument()
            self.status_frame.update()
            return
        
        if self.check_double_middle:
            self.pick_instrument_mode = True
            self.instrument_frame.enable_selection()
            # Also stop
            if self.organ_controller.is_playing:
                self.organ_controller.toggle_pause()
        else:
            self.organ_controller.toggle_pause()
        self.status_frame.update()
        self.check_double_middle = False


    def on_scroll_up_action(self, event = None):
        if not self.pick_instrument_mode:
            return
        self.instrument_frame.prev_instrument()

    def on_scroll_dn_action(self, event = None):
        if not self.pick_instrument_mode:
            return
        self.instrument_frame.next_instrument()


    def on_scroll_action(self, event = None):
        if not self.pick_instrument_mode:
            return
        if event.delta > 0:
            self.instrument_frame.prev_instrument()
        else:
            self.instrument_frame.next_instrument()

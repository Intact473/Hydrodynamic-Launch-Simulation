import sys
sys.dont_write_bytecode = True
import pygame as pg
import pygame_gui as gui


class ControlPanel:
    def __init__(self, gui_rect: pg.Rect, manager: gui.UIManager, on_start=None, on_reset=None):
        self.gui_rect = gui_rect
        self.manager = manager
        self.on_start = on_start
        self.on_reset = on_reset

        x, y, w, h = gui_rect
        pad = 10
        label_h = 24
        input_h = 30
        gap = 14 

        self.panel = gui.elements.UIPanel(
            relative_rect=pg.Rect(x, y, w, h),
            starting_layer_height=1,
            manager=manager
        )

        cursor_y = pad

        self.lbl_title = gui.elements.UILabel(
            relative_rect=pg.Rect(pad, cursor_y, w - 2*pad, label_h),
            text="Settings",
            container=self.panel,
            manager=manager
        )
        cursor_y += label_h + gap

        def add_labeled_entry(label_text: str, default_text: str = ""):
            nonlocal cursor_y

            gui.elements.UILabel(
                relative_rect=pg.Rect(pad, cursor_y, 200, label_h),
                text=label_text,
                container=self.panel,
                manager=manager
            )
            cursor_y += label_h + 4 

            entry = gui.elements.UITextEntryLine(
                relative_rect=pg.Rect(pad, cursor_y, w - 2*pad, input_h),
                container=self.panel,
                manager=manager
            )
            entry.set_text(default_text)
            cursor_y += input_h + gap
            return entry

        self.uinp_volumePET = add_labeled_entry("Volume PET [l]", "1.00")
        self.uinp_pressure = add_labeled_entry("Pressure [bar]", "6.00")
        self.uinp_weight_empty_rocket = add_labeled_entry("Weight empty rocket [kg]", "0.60")
        self.uinp_start_angle = add_labeled_entry("Start angle [°]", "90.0")
        self.uinp_thrust_nozzle_diameter = add_labeled_entry("Thrust nozzle diameter [mm]", "10.0")


        self.btn_start = gui.elements.UIButton(
            relative_rect=pg.Rect(pad, cursor_y, w - 2*pad, 38),
            text="Start",
            container=self.panel,
            manager=manager
        )
        cursor_y += 38 + 8

        self.btn_reset = gui.elements.UIButton(
            relative_rect=pg.Rect(pad, cursor_y, w - 2*pad, 34),
            text="Reset",
            container=self.panel,
            manager=manager
        )

    def handle_event(self, ev):
        if ev.type == pg.USEREVENT and ev.user_type == gui.UI_BUTTON_PRESSED:
            if ev.ui_element == self.btn_start:
                if self.on_start:
                    self.on_start(self.read_values())
            elif ev.ui_element == self.btn_reset:
                if self.on_reset:
                    self.on_reset()

    def read_values(self) -> dict:
        uinp_values = {}
        try:
            uinp_values["volume"] = float(self.uinp_volumePET.get_text())
            uinp_values["pressure"] = float(self.uinp_pressure.get_text())
            uinp_values["empty_rocket_weight"] = float(self.uinp_weight_empty_rocket.get_text())
            uinp_values["start_angle"] = float(self.uinp_start_angle.get_text())
            uinp_values["start_angle"] = float(self.uinp_start_angle.get_text())
            uinp_values["thrust nozzle diameter"] = float(self.uinp_thrust_nozzle_diameter.get_text()) 
        except ValueError as e:
            print("Error: Invalid uinput in control panel", e)
        return uinp_values

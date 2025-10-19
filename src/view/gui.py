import sys
sys.dont_write_bytecode = True
import pygame as pg
import pygame_gui as gui
import physic.formulas as formulas


class ControlPanel:
    def __init__(self, gui_rect: pg.Rect, manager: gui.UIManager, on_start=None, on_reset=None, toggle_mode=None):
        self.gui_rect = gui_rect
        self.manager = manager
        self.on_start = on_start
        self.on_reset = on_reset
        self.on_toggle_mode = toggle_mode

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
            """Helper function to add a labeled text entry field."""
            nonlocal cursor_y

            label =gui.elements.UILabel(
                relative_rect=pg.Rect(pad, cursor_y, 200, label_h),
                text=label_text,
                container=self.panel,
                manager=manager
            )
            cursor_y += label_h + 4 
            label.text_horiz_alignment = 'left'
            label.rebuild()

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
        self.uinp_thrust_nozzle_diameter = add_labeled_entry("Thrust nozzle d [mm]", "10.0")
        self.uinp_water_level_rocket = add_labeled_entry("Water level rocket [l]", "0.50")


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
        cursor_y += 34 + 8

        self.btn_toggle_mode = gui.elements.UIButton(
            relative_rect=pg.Rect(pad, cursor_y, w - 2*pad, 40),
            text="Georg Ohm Space Center",
            container=self.panel,
            manager=manager
        )

    def handle_event(self, event):
        """Handle button press events."""
        if event.ui_element == self.btn_start and self.on_start:
            values = self.read_values()
            if values is not None:
                self.on_start(values)
        elif event.ui_element == self.btn_reset and self.on_reset:
            self.on_reset()
        elif event.ui_element == self.btn_toggle_mode and self.on_toggle_mode:
            self.on_toggle_mode()
            
    def read_values(self) -> dict:
        """
        Read and return the current values from the input fields as a dictionary.
        Parameters:
            volume: in liters
            pressure: in bar
            empty_rocket_weight: in kg
            start_angle: in degrees
            thrust_nozzle_diameter: in mm
        """
        uinp_values = {}
        try:
            uinp_values["volume"] = float(self.uinp_volumePET.get_text())
            uinp_values["pressure"] = float(self.uinp_pressure.get_text())
            uinp_values["empty_rocket_weight"] = float(self.uinp_weight_empty_rocket.get_text())
            uinp_values["thrust nozzle diameter"] = float(self.uinp_thrust_nozzle_diameter.get_text())
            uinp_values["water level rocket"] = float(self.uinp_water_level_rocket.get_text())
        except ValueError as e:
            print("Error: Invalid uinput in control panel", e)
        return uinp_values

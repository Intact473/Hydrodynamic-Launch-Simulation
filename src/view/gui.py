import sys
sys.dont_write_bytecode = True
import pygame as pg
import pygame_gui as gui

class ControlPanel:
    """
    GUI control panel for simulation settings and actions.
    """
    def __init__(self, gui_rect: pg.Rect, manager: gui.UIManager, on_start=None, on_reset=None, on_contour_plot=None):
        """
        Initialize the control panel with input fields and buttons.

        Args:
            gui_rect (pg.Rect): Rectangle defining the panel area.
            manager (gui.UIManager): The pygame_gui UI manager.
            on_start (callable, optional): Callback for the Start button.
            on_reset (callable, optional): Callback for the Reset button.
            on_contour_plot (callable, optional): Callback for the Contour Plot button.
        """
        self.gui_rect = gui_rect
        self.manager = manager
        self.on_start = on_start
        self.on_reset = on_reset
        self.on_contour_plot = on_contour_plot

        x, y, w, h = gui_rect
        pad = 10
        label_h = 30
        input_h = 34
        gap = 10

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
            """
            Helper function to add a labeled text entry field.

            Args:
                label_text (str): The label for the input field.
                default_text (str, optional): Default value for the input field.

            Returns:
                UITextEntryLine: The created input field.
            """
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
        self.uinp_weight_empty_rocket = add_labeled_entry("Weight empty rocket [kg]", "0.18")
        self.uinp_thrust_nozzle_diameter = add_labeled_entry("Thrust nozzle d [mm]", "9.00")
        self.uinp_water_level_rocket = add_labeled_entry("water_level_rocket [l]", "0.40")
        self.uinp_cross_sectional_rocket = add_labeled_entry("Rocket diameter [m]", "0.10")


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

        self.contour_plot = gui.elements.UIButton(
            relative_rect=pg.Rect(pad, cursor_y, w - 2*pad, 40),
            text="Show Contour plot",
            container=self.panel,
            manager=manager
        )
        cursor_y += 40 + 8

        def add_output_field(label_text: str):
            """
            Helper function to add a labeled output field.

            Args:
                label_text (str): The label for the output field.

            Returns:
                UITextEntryLine: The created output field.
            """
            nonlocal cursor_y
            label = gui.elements.UILabel(
                relative_rect=pg.Rect(pad, cursor_y, 200, label_h),
                text=label_text,
                container=self.panel,
                manager=manager
            )
            cursor_y += label_h + 4

            output = gui.elements.UITextEntryLine(
                relative_rect=pg.Rect(pad, cursor_y, w - 2*pad, input_h),
                container=self.panel,
                manager=manager
            )
            output.set_text("—")
            output.rebuild() 
            cursor_y += input_h + gap
            return output
        self.out_max_velocity = add_output_field("Impact velocity [m/s]")
        self.out_max_height = add_output_field("Max height [m]")


    def handle_event(self, event):
        """
        Handle button press events from the control panel.

        Args:
            event: The pygame event to handle.
        """
        if event.ui_element == self.btn_start and self.on_start:
            values = self.read_values()
            if values is not None:
                self.on_start(values)
        elif event.ui_element == self.btn_reset and self.on_reset:
            self.on_reset()
        elif event.ui_element == self.contour_plot and self.on_contour_plot:
            values = self.read_values()
            self.on_contour_plot(values)

            
    def read_values(self) -> dict:
        """
        Read and return the current values from the input fields as a dictionary.

        Returns:
            dict: Dictionary of input values for the simulation.
        """
        uinp_values = {}
        try:
            uinp_values["bottle_volume"] = float(self.uinp_volumePET.get_text())
            uinp_values["pressure"] = float(self.uinp_pressure.get_text())
            uinp_values["empty_rocket_weight"] = float(self.uinp_weight_empty_rocket.get_text())
            uinp_values["thrust_nozzle_diameter"] = float(self.uinp_thrust_nozzle_diameter.get_text())
            uinp_values["water_level_rocket"] = float(self.uinp_water_level_rocket.get_text())
            uinp_values["diameter_rocket"] = float(self.uinp_cross_sectional_rocket.get_text())
        except ValueError as e:
            print("Error: Invalid uinput in control panel", e)
        return uinp_values

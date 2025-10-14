import math
from view import gui

gui_input_values = {}

def set_values(values: dict):
    """
    get all gui inputs
    Parameters:
        volume: in liters
        pressure: in bar
        empty_rocket_weight: in kg
        start_angle: in degrees
        thrust_nozzle_diameter: in mm
    """

    print(values)
    global gui_input_values
    gui_input_values = values.copy()

def calculate_thrust_nozzel_area(diameter_mm: float) -> float:
    """
    Calculate the area of the thrust nozzle in m^2 from the diameter in mm.
    """
    radius_m = (diameter_mm / 1000) / 2
    nozzel_area = math.pi * (radius_m ** 2)
    return nozzel_area 

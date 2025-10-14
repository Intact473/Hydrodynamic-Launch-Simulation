import math

def getValuesFromControlPanel(values: dict):
    """
    Extract and convert values from the control panel input dictionary.
    volume: in liters
    pressure: in bar
    empty_rocket_weight: in kg
    start_angle: in degrees
    thrust_nozzle_diameter: in mm
    """
    volume = values["volume"]
    pressure = values["pressure"]
    empty_rocket_weight = values["empty_rocket_weight"]
    start_angle = values["start_angle"]
    thrust_nozzle_diameter = values["thrust_nozzle_diameter"]


def calculate_thrust_nozzel_area(diameter_mm: float) -> float:
    """
    Calculate the area of the thrust nozzle in m^2 from the diameter in mm.
    """
    radius_m = (diameter_mm / 1000) / 2
    nozzel_area = math.pi * (radius_m ** 2)
    return nozzel_area 

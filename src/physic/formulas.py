import math

def getValuesFromControlPanel(values: dict):
    volume = values["volume"]
    pressure = values["pressure"]
    empty_rocket_weight = values["empty_rocket_weight"]
    start_angle = values["start_angle"]
    thrust_nozzle_diameter = values["thrust_nozzle_diameter"]

def calculate_thrust_nozzel_area(diameter_mm: float) -> float:
    radius_m = (diameter_mm / 1000) / 2
    nozzel_area = math.pi * (radius_m ** 2)
    return nozzel_area 


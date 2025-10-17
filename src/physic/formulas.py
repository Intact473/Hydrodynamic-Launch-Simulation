import math

gui_input_values = {}
global time
time = 0
max_value = 0.0

def start(values:dict):
    global running
    running = True
    print("Simulation started")
    set_values(values)

def stop():
    global running
    running = False
    print("Simulation stopped")
    global time
    time = 0

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
    global time              # <-- Neu: sorgt dafür, dass die Zuweisung time = 0 die Modul-Variable ändert
    gui_input_values = values.copy()
    time = 0

def calculate_thrust_nozzel_area(diameter_mm: float) -> float:
    """
    Calculate the area of the thrust nozzle in m^2 from the diameter in mm.
    """
    radius_m = (diameter_mm / 1000) / 2
    nozzel_area = math.pi * (radius_m ** 2)
    return nozzel_area 

def calculate_max_value(value) -> float:
    """
    Calculate the maximum value for the prameter.
    Paramters:
        value: the current value, this could be height, velocity for example
    """
    global max_value
    max_value = max(max_value, value)

    return max_value

def Volume(V_0, ejection_velocity, nozzle_area, time):
    return V_0 + ejection_velocity * nozzle_area * time

def Pressure(P_0, V_0, V, kappa_gas):
    return P_0 * (V_0 / V) ** kappa_gas

def ejection_velocity(pressure, kappa_gas, density_water, P_atm):
    return math.sqrt((2*kappa_gas)/(kappa_gas-1) * (pressure)/density_water * (1 - (P_atm/pressure)**((kappa_gas-1)/kappa_gas)))

def mass_flow(density_water, ejection_velocity, nozzle_area):
    return density_water * ejection_velocity * nozzle_area

def thrust(mass_flow, ejection_velocity):
    return mass_flow * ejection_velocity


def calculateValues():
    if time == 0:
        pressure = gui_input_values.get("pressure")
        print(pressure)
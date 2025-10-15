import math

def getValuesFromControlPanel(values: dict):
    volume = values["volume"]
    pressure = values["pressure"]
    empty_rocket_weight = values["empty_rocket_weight"]
    start_angle = values["start_angle"]

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
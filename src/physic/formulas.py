import math
import matplotlib.pyplot as plt
import view.window as vw


gui_input_values = {}
max_value = 0.0
global results
results = []

def start(values:dict):
    print("Simulation started")
    set_values(values)
    global results
    results = calculateValues(plotValues = False)
    vw.get_sim().time = 0.0


def stop():
    print("Simulation stopped")
    vw.get_sim().time = 0.0

def set_values(values: dict):
    """
    get all gui inputs
    Parameters:
        volume: in liters
        pressure: in bar
        empty_rocket_weight: in kg
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

def get_max_value(value) -> float:
    """
    Calculate the maximum value for the prameter.
    Paramters:
        value: the current value, this could be height, velocity for example
    """
    global max_value
    max_value = max(max_value, value)

    return max_value

def Air_volume(V_0, ejection_velocity, nozzle_area, time):
    return V_0 + ejection_velocity * nozzle_area * time

def Pressure(P_0, V_0, V, kappa_gas):
    return P_0 * (V_0 / V) ** kappa_gas

def Ejection_velocity(pressure, kappa_gas, density_water, P_atm):
    return math.sqrt((2*kappa_gas)/(kappa_gas-1) * (pressure)/density_water * (1 - (P_atm/pressure)**((kappa_gas-1)/kappa_gas)))

def Mass_flow(density_water, ejection_velocity, nozzle_area):
    return density_water * ejection_velocity * nozzle_area

def Thrust(mass_flow, ejection_velocity):
    return mass_flow * ejection_velocity

def Air_Resistance(diameter_rocket, velocity):
    # assuming rocket is a cylinder
    C_w = 1  # drag coefficient
    rho_air = 1.225  # kg/m^3
    radius_rocket = diameter_rocket / 2
    cross_section_area = math.pi * (radius_rocket ** 2)
    return 0.5 * C_w * rho_air * cross_section_area * velocity**2

def Gravity_force(mass):
    g = 9.81  # m/s^2
    return mass * g

def calculateValues(plotValues = False):
    """
    Simulate from t=0 to end_time in 1ms steps and return a list of dicts with:
      - time (s)
      - thrust (N)
      - total_mass (kg)
      - pressure (Pa)
      - fill_level (m^3)  # remaining water volume
      - ejection_velocity (m/s)
      - air_volume (m^3)

    Expects relevant keys in gui_input_values (if missing, defaults are used):
      - pressure: initial pressure in bar (default 3.0)
      - volume: initial air volume in liters (default 1.0)
      - water_volume: initial water volume in liters (default 1.0)
      - empty_rocket_weight: kg (default 1.0)
      - thrust_nozzle_diameter: mm (default 20.0)
      - kappa_gas: ratio (default 1.4)
      - density_water: kg/m^3 (default 1000)
      - P_atm: Pa (default 101325)
      - endTime: seconds (used if end_time param omitted; default 5.0)
    """
    global gui_input_values

    # defaults and read inputs
    defaults = {
        "pressure": 0,               # bar
        "volume": 0,                 # liters (initial air volume)
        "water_level_rocket": 0,     # liters (initial water volume)
        "empty_rocket_weight": 0,    # kg
        "thrust_nozzle_diameter": 0, # mm
        "kappa_gas": 1.4,
        "density_water": 997.0,       # kg/m^3
        "P_atm": 101325.0,             # Pa
        "diameter_rocket": 0.10,      # m 
        "endTime": 5.0                 # seconds
    }

    # merge provided values with defaults
    inputs = defaults.copy()
    inputs.update(gui_input_values or {})


    # convert units
    inputs["pressure"] *= 1e5  # atm to Pa
    inputs["water_level_rocket"] *= 1e-3  # liters to m^3
    inputs["volume"] *= 1e-3  # liters to m^3 
    print(inputs)

    results = []

    dt = 0.001  # 1 ms
    steps = int(max(0.0, inputs["endTime"]) / dt) + 1

    # Store initial values at t=0 (compute nozzle_area, v_a0, mass_flow0, thrust0, total_mass0 inline)
    results.append({
        "time": 0.0,
        "air_volume": (air_volume0 := inputs["volume"]),
        "pressure": (pressure0 := inputs["pressure"]),
        "ejection_velocity": (v_a0 := Ejection_velocity(pressure0, inputs["kappa_gas"], inputs["density_water"], inputs["P_atm"])),
        "mass_flow": (mass_flow0 := Mass_flow(inputs["density_water"], v_a0, (nozzle_area := calculate_thrust_nozzel_area(inputs["thrust_nozzle_diameter"])))),
        "thrust": (thrust0 := Thrust(mass_flow0, v_a0)),
        "air_resistance": 0.0,
        "total_force": (thrust0 - 0.0 - (gravity_force0 := Gravity_force(total_mass0 := inputs["empty_rocket_weight"] + inputs["density_water"] * inputs["water_level_rocket"]))),
        "gravity_force": gravity_force0,
        "velocity": 0.0,
        "posY": 0.0,
        "water_level": inputs["water_level_rocket"],
        "total_mass": total_mass0,
    })

    for(step) in range(1, steps):
        time = step * dt
        # get last values
        last = results[-1]  

        if last["posY"] <= 0.0 and step > 4:
            # Rocket has landed, stop simulation
            break
        
        if last["water_level"] <= 0.0:
            # No water left, thrust is zero
            results.append({
                "time": time,
                "air_volume": last["air_volume"],
                "pressure": inputs["P_atm"],
                "ejection_velocity": 0.0,
                "mass_flow": 0.0,
                "thrust": 0.0,
                "air_resistance": (air_resistance := Air_Resistance(inputs["diameter_rocket"], last["velocity"])),
                "gravity_force": (gravity_force := Gravity_force(total_mass := inputs["empty_rocket_weight"])) ,
                "total_force": (total_force := - air_resistance - gravity_force),   # no more thrust
                "velocity": last["velocity"] + (total_force / total_mass) * dt,
                "posY": max(0.0, last["posY"] + last["velocity"] * dt),
                "water_level": 0.0,
                "total_mass": total_mass,
            })
            continue

        else:   # water still in rocket
            results.append({
                "time": time,
                "air_volume": (air_volume := Air_volume(last["air_volume"], last["ejection_velocity"], nozzle_area, dt)),
                "pressure": (pressure := Pressure(inputs["pressure"], inputs["volume"], air_volume, inputs["kappa_gas"])),
                "ejection_velocity": (ejection_velocity := Ejection_velocity(pressure, inputs["kappa_gas"], inputs["density_water"], inputs["P_atm"])),
                "mass_flow": (mass_flow_rate := Mass_flow(inputs["density_water"], ejection_velocity, nozzle_area)),
                "thrust": (thrust_value := Thrust(mass_flow_rate, ejection_velocity)),
                "air_resistance": (air_resistance := Air_Resistance(inputs["diameter_rocket"], last["velocity"])),
                "gravity_force": (Gravity_force(total_mass := inputs["empty_rocket_weight"] + inputs["density_water"] * (water_level := max(0.0, last["water_level"] - (mass_flow_rate / inputs["density_water"]) * dt)))) ,
                "total_force": (total_force :=thrust_value - air_resistance - Gravity_force(total_mass)),
                "velocity": last["velocity"] + (total_force / total_mass) * dt,
                "posY": max(0.0, last["posY"] + last["velocity"] * dt),
                "water_level": water_level,
                "total_mass": total_mass,
            })
        


    # ---- plotting: separate plot for each variable ----
    if results and plotValues:
        times = [r["time"] for r in results]
        series = {
            "thrust (N)": [r["thrust"] for r in results],
            "total_mass (kg)": [r["total_mass"] for r in results],
            "pressure (Pa)": [r["pressure"] for r in results],
            "water_level (m^3)": [r["water_level"] for r in results],
            "ejection_velocity (m/s)": [r["ejection_velocity"] for r in results],
            "air_volume (m^3)": [r["air_volume"] for r in results],
            "velocity (m/s)": [r["velocity"] for r in results],
            "posY (m)": [r["posY"] for r in results],
            "total_force (N)": [r["total_force"] for r in results],
        }

        # create a wider window with subplots arranged along the x axis (2 rows x 5 cols)
        fig, axes = plt.subplots(nrows=2, ncols=5, figsize=(18, 6))
        axes = axes.flatten()

        for ax, (name, vals) in zip(axes, series.items()):
            ax.plot(times, vals, linewidth=1)
            ax.set_title(name)
            ax.set_xlabel("time (s)")
            ax.set_ylabel(name)
            ax.grid(True)

        # hide any unused axes (if series has fewer entries than axes)
        for ax in axes[len(series):]:
            ax.set_visible(False)

        plt.tight_layout()
        plt.show()

    # print(results)
    return results
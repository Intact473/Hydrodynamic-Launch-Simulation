import math
import matplotlib.pyplot as plt
import view.window as vw
import numpy as np


gui_input_values = {}
max_value = 0.0
results = []

def start(values:dict):
    global results
    print("Simulation started")
    set_values(values)
    results = calculateValues(plotValues = True)
    print("max height: ", get_max_height(results))
    print("max velocity: ", get_max_velocity(results))
    vw.get_sim().time = 0.0
        

def show_contour_plot(values:dict):
    set_values(values)
    try_combinations(min_nozzle_mm=1.0, max_nozzle_mm=40.0, step_nozzle_mm=1.0,
                     min_bottle_volume_l=0.1, max_bottle_volume_l=1.0, step_bottle_volume_l=0.025)

def stop():
    print("Simulation stopped")
    vw.get_sim().time = 0.0

def set_values(values: dict):
    print(values)
    global gui_input_values
    gui_input_values = values.copy()

def calculate_thrust_nozzel_area(diameter_mm: float) -> float:
    radius_m = (diameter_mm / 1000) / 2
    nozzel_area = math.pi * (radius_m ** 2)
    return nozzel_area 

def get_max_height(results) -> float:
    max_height = 0.0
    for entry in results:
        height = entry['posY']
        max_height = max(max_height, height)
    return max_height

def get_max_velocity(results) -> float:
    max_velocity = 0.0
    for entry in results:
        velocity = entry['velocity']
        max_velocity = min(max_velocity, velocity)
    return max_velocity

def try_combinations(min_nozzle_mm: float, max_nozzle_mm: float, step_nozzle_mm: float, min_bottle_volume_l: float, max_bottle_volume_l: float, step_bottle_volume_l: float):
    thrust_values = np.arange(min_nozzle_mm, max_nozzle_mm + step_nozzle_mm, step_nozzle_mm)
    water_level_values = np.arange(min_bottle_volume_l, max_bottle_volume_l + step_bottle_volume_l, step_bottle_volume_l)
    print(water_level_values)

    max_heights = np.zeros((len(thrust_values), len(water_level_values)))

    for i, thrust in enumerate(thrust_values):
        for j, water_level in enumerate(water_level_values):
            gui_input_values["thrust_nozzle_diameter"] = thrust
            gui_input_values["water_level_rocket"] = round(water_level,5)
            results = calculateValues(plotValues=False)
            max_heights[i, j] = get_max_height(results)
            print(f"Thrust Nozzle Diameter: {thrust} mm, Water Level: {water_level} l => Max Height: {max_heights[i, j]:.2f} m")

    T, V = np.meshgrid(thrust_values, water_level_values)
    plt.figure(figsize=(7, 4.2))
    contour = plt.contourf(T, V, max_heights.T, levels=40, cmap='viridis')
    plt.colorbar(contour, label='Max Height (m)')
    plt.xlabel('Thrust Nozzle Diameter (mm)')
    plt.ylabel('Initial Water Level (l)')
    plt.title('Max Height Contour Plot')
    plt.tight_layout()
    plt.show()

def Air_volume(total_volume, water_volume):
    return max(total_volume - water_volume, 0.0)

def Pressure(P_0, V_0, V, kappa_gas):
    if V <= 0:
        return P_0
    return P_0 * (V_0 / V) ** kappa_gas

def Ejection_velocity(pressure, density_water, P_atm):
    if pressure <= P_atm or density_water <= 0:
        return 0.0
    return math.sqrt(2 * (pressure - P_atm) / density_water)

def Mass_flow(density_water, ejection_velocity, nozzle_area):
    return density_water * ejection_velocity * nozzle_area

def Thrust(mass_flow, ejection_velocity):
    return mass_flow * ejection_velocity

def Air_Resistance(diameter_rocket, velocity):
    C_w = 1
    rho_air = 1.225
    radius_rocket = diameter_rocket / 2
    cross_section_area = math.pi * (radius_rocket ** 2)
    return 0.5 * C_w * rho_air * cross_section_area * velocity * abs(velocity)

def Gravity_force(mass):
    g = 9.81
    return mass * g

def calculateValues(plotValues = False):
    global gui_input_values

    defaults = {
        "pressure": 0,
        "bottle_volume": 0,
        "water_level_rocket": 0,
        "empty_rocket_weight": 0,
        "thrust_nozzle_diameter": 0,
        "kappa_gas": 1.4,
        "density_water": 997.0,
        "P_atm": 101325.0,
        "diameter_rocket": 0.10,
        "endTime": 5.0
    }

    inputs = defaults.copy()
    inputs.update(gui_input_values or {})

    try:
        bottle_vol = float(inputs.get("bottle_volume", 0))
        water_lvl = float(inputs.get("water_level_rocket", 0))
        pressure_bar = float(inputs.get("pressure", 0))
        empty_mass = float(inputs.get("empty_rocket_weight", 0))
        nozzle_mm = float(inputs.get("thrust_nozzle_diameter", 0))
        kappa = float(inputs.get("kappa_gas", 1.4))
        rho_water = float(inputs.get("density_water", 997.0))
        P_atm_val = float(inputs.get("P_atm", 101325.0))
        diam_rocket = float(inputs.get("diameter_rocket", 0.10))
        end_time = float(inputs.get("endTime", 5.0))
    except (TypeError, ValueError):
        raise ValueError("One or more inputs are not numeric.")

    if bottle_vol <= 0:
        raise ValueError("bottle_volume must be > 0 (liters).")
    if water_lvl < 0:
        raise ValueError("water_level_rocket cannot be negative (liters).")
    if water_lvl > bottle_vol:
        raise ValueError("water_level_rocket cannot exceed bottle_volume (liters).")
    if pressure_bar <= 0:
        raise ValueError("pressure must be > 0 (bar).")
    if empty_mass < 0:
        raise ValueError("empty_rocket_weight cannot be negative (kg).")
    if nozzle_mm <= 0:
        raise ValueError("thrust_nozzle_diameter must be > 0 (mm).")
    if kappa <= 1.0:
        raise ValueError("kappa_gas must be > 1.0.")
    if rho_water <= 0:
        raise ValueError("density_water must be > 0 (kg/m^3).")
    if P_atm_val <= 0:
        raise ValueError("P_atm must be > 0 (Pa).")
    if diam_rocket <= 0:
        raise ValueError("diameter_rocket must be > 0 (m).")
    if end_time < 0:
        raise ValueError("endTime cannot be negative (s).")

    inputs["bottle_volume"] = bottle_vol
    inputs["water_level_rocket"] = water_lvl
    inputs["pressure"] = pressure_bar
    inputs["empty_rocket_weight"] = empty_mass
    inputs["thrust_nozzle_diameter"] = nozzle_mm
    inputs["kappa_gas"] = kappa
    inputs["density_water"] = rho_water
    inputs["P_atm"] = P_atm_val
    inputs["diameter_rocket"] = diam_rocket
    inputs["endTime"] = end_time

    inputs["pressure"] *= 1e5
    inputs["water_level_rocket"] *= 1e-3
    inputs["bottle_volume"] *= 1e-3
    print("inputs: ", inputs)

    results = []

    dt = 0.001
    steps = int(max(0.0, inputs["endTime"]) / dt) + 1

    results.append({
        "time": 0.0,
        "air_volume": (air_volume0 := max(inputs["bottle_volume"] - inputs["water_level_rocket"], 0.0)),
        "pressure": (pressure0 := inputs["pressure"]),
        "ejection_velocity": (v_a0 := Ejection_velocity(pressure0, inputs["density_water"], inputs["P_atm"])),
        "mass_flow": (mass_flow0 := Mass_flow(inputs["density_water"], v_a0, (nozzle_area := calculate_thrust_nozzel_area(inputs["thrust_nozzle_diameter"])))),
        "thrust": (thrust0 := Thrust(mass_flow0, v_a0)),
        "air_resistance": 0.0,
        "total_force": (thrust0 - 0.0 - (gravity_force0 := Gravity_force(total_mass0 := inputs["empty_rocket_weight"] + inputs["density_water"] * inputs["water_level_rocket"]))),
        "gravity_force": gravity_force0,
        "acceleration": (accel0 := ((thrust0 - gravity_force0) / total_mass0) if total_mass0 > 0 else 0.0),
        "velocity": 0.0,
        "posY": 0.0,
        "water_level": inputs["water_level_rocket"],
        "total_mass": total_mass0,
        "added_volume": air_volume0 + inputs["water_level_rocket"],
    })

    for(step) in range(1, steps):
        time = step * dt
        last = results[-1]

        if last["posY"] <= 0.0 and step > 4:
            break

        if last["water_level"] <= 0.0:
            results.append({
                "time": time,
                "air_volume": last["air_volume"],
                "pressure": inputs["P_atm"],
                "ejection_velocity": 0.0,
                "mass_flow": 0.0,
                "thrust": 0.0,
                "air_resistance": (air_resistance := Air_Resistance(inputs["diameter_rocket"], last["velocity"])),
                "gravity_force": (gravity_force := Gravity_force(total_mass := inputs["empty_rocket_weight"])),
                "total_force": (total_force := - air_resistance - gravity_force),
                "acceleration": (acceleration := (total_force / total_mass) if total_mass > 0 else 0.0),
                "velocity": (newVelocity := last["velocity"] + (acceleration) * dt),
                "posY": max(0.0, last["posY"] + newVelocity * dt),
                "water_level": 0.0,
                "total_mass": total_mass,
                "added_volume": last["air_volume"] + last["water_level"],
            })
            continue

        else:
            results.append({
                "time": time,
                "mass_flow_prev": (mass_flow_prev := Mass_flow(inputs["density_water"], last["ejection_velocity"], nozzle_area)),
                "water_level": (water_level := max(0.0, last["water_level"] - (mass_flow_prev / inputs["density_water"]) * dt)),
                "air_volume": (air_volume := Air_volume(inputs["bottle_volume"], water_level)),
                "pressure": (pressure := Pressure(inputs["pressure"], inputs["bottle_volume"] - inputs["water_level_rocket"], air_volume, inputs["kappa_gas"])),
                "ejection_velocity": (ejection_velocity := Ejection_velocity(pressure, inputs["density_water"], inputs["P_atm"])),
                "mass_flow": (mass_flow_rate := Mass_flow(inputs["density_water"], ejection_velocity, nozzle_area)),
                "thrust": (thrust_value := Thrust(mass_flow_rate, ejection_velocity)),
                "air_resistance": (air_resistance := Air_Resistance(inputs["diameter_rocket"], last["velocity"])),
                "gravity_force": (Gravity_force(total_mass := inputs["empty_rocket_weight"] + inputs["density_water"] * water_level)),
                "total_force": (total_force := thrust_value - air_resistance - Gravity_force(total_mass)),
                "acceleration": (acceleration := (total_force / total_mass) if total_mass > 0 else 0.0),
                "velocity": last["velocity"] + acceleration * dt,
                "posY": max(0.0, last["posY"] + last["velocity"] * dt),
                "total_mass": total_mass,
                "added_volume": air_volume + water_level,
            })
        

    if results and plotValues:
        times = [r["time"] for r in results]

        keys = [k for k in results[0].keys() if k != "time"]

        n_series = len(keys)
        if n_series == 0:
            return_results = results
        ncols = min(4, max(1, n_series))
        nrows = math.ceil(n_series / ncols)

        fig, axes = plt.subplots(nrows=nrows, ncols=ncols, figsize=(3 * ncols, 2.2 * nrows))
        axes = np.array(axes).flatten()

        for ax, key in zip(axes, keys):
            vals = [r.get(key, 0.0) for r in results]
            ax.plot(times, vals, linewidth=1)
            ax.set_title(str(key))
            ax.set_xlabel("time (s)")
            ax.grid(True)

        for ax in axes[len(keys):]:
            ax.set_visible(False)

        plt.tight_layout(pad=0.3)
        plt.show()

    #print(results)
    return results
import math
import matplotlib.pyplot as plt
import view.window as vw
import numpy as np


gui_input_values = {}
max_value = 0.0
results = []

def start(values:dict):
    print("Simulation started")
    set_values(values)
    global results
    results = calculateValues(plotValues = False)
    print(get_max_height(results))
    vw.get_sim().time = 0.0

    # Contour plot for max height
    if True:
        try_combinations(min_nozzle_mm=1.0, max_nozzle_mm=40.0, step_nozzle_mm=1.0,
                     min_bottle_volume_l=0.1, max_bottle_volume_l=1.0, step_bottle_volume_l=0.025)

def stop():
    print("Simulation stopped")
    vw.get_sim().time = 0.0

def set_values(values: dict):
    """
    Store GUI inputs (validation moved to calculateValues so try_combinations is validated too).
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

def get_max_height(results) -> float:
    max_height = 0.0
    for entry in results:
        height = entry['posY']
        max_height = max(max_height, height)
    return max_height

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

    # Create contour plot with correct axes (smaller figsize)
    T, V = np.meshgrid(thrust_values, water_level_values)
    plt.figure(figsize=(7, 4.2))
    contour = plt.contourf(T, V, max_heights.T, levels=40, cmap='viridis')
    plt.colorbar(contour, label='Max Height (m)')
    plt.xlabel('Thrust Nozzle Diameter (mm)')
    plt.ylabel('Initial Water Level (l)')
    plt.title('Max Height Contour Plot')
    plt.tight_layout()
    plt.show()

def get_max_value(value) -> float:
    # Checke deine Funktion net deswegen mach ich meine eigene
    """
    Calculate the maximum value for the parameter
    Parameters:
        value: the current value, this could be height, velocity for example
    """
    global max_value
    max_value = max(max_value, value)

    return max_value

# Replace Air_volume: use total_volume - water_volume with failsafe
def Air_volume(total_volume, water_volume):
	"""
	Current air volume = total_volume - water_volume (both in m^3).
	Ensure non-negative.
	"""
	return max(total_volume - water_volume, 0.0)

# Pressure: guard against zero/negative V to avoid division by zero
def Pressure(P_0, V_0, V, kappa_gas):
	if V <= 0:
		# fallback: no compression calculation possible, return ambient-like fallback to avoid blowup
		return P_0
	return P_0 * (V_0 / V) ** kappa_gas

# Ejection_velocity: avoid math domain errors, return 0 when not physically valid
def Ejection_velocity(pressure, density_water, P_atm):
    """
    Calculate the ejection velocity of water using the formula:
    v = sqrt(2 * (p - p_atm) / rho)
    """
    if pressure <= P_atm or density_water <= 0:
        return 0.0  # Return 0 if pressure is less than or equal to atmospheric pressure or density is invalid
    return math.sqrt(2 * (pressure - P_atm) / density_water)

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
    return 0.5 * C_w * rho_air * cross_section_area * velocity * abs(velocity)

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
      - bottle_volume: total bottle volume in liters (default 1.0)
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
        "bottle_volume": 0,          # liters (total bottle volume)
        "water_level_rocket": 0,     # liters (initial water volume)
        "empty_rocket_weight": 0,    # kg
        "thrust_nozzle_diameter": 0, # mm
        "kappa_gas": 1.4,
        "density_water": 997.0,      # kg/m^3
        "P_atm": 101325.0,           # Pa
        "diameter_rocket": 0.10,     # m 
        "endTime": 5.0               # seconds
    }

    # merge provided values with defaults
    inputs = defaults.copy()
    inputs.update(gui_input_values or {})

    # --- input validation (performed BEFORE unit conversion) ---
    # ensure numeric types where possible
    try:
        # these keys expected from GUI (in liters / user units)
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

    # update validated (ensures proper numeric types in inputs)
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
    # --- end validation ---

    # convert units
    inputs["pressure"] *= 1e5  # bar to Pa
    inputs["water_level_rocket"] *= 1e-3  # liters to m^3
    inputs["bottle_volume"] *= 1e-3  # liters to m^3 
    print("inputs: ", inputs)

    results = []

    dt = 0.0002  # 0.2 ms
    steps = int(max(0.0, inputs["endTime"]) / dt) + 1

    # Store initial values at t=0
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
        "added_volume": air_volume0 + inputs["water_level_rocket"],  # Ensure it matches bottle_volume
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
                "gravity_force": (gravity_force := Gravity_force(total_mass := inputs["empty_rocket_weight"])),
                "total_force": (total_force := - air_resistance - gravity_force),
                "acceleration": (acceleration := (total_force / total_mass) if total_mass > 0 else 0.0),
                "velocity": (newVelocity := last["velocity"] + (acceleration) * dt),
                "posY": max(0.0, last["posY"] + newVelocity * dt),
                "water_level": 0.0,
                "total_mass": total_mass,
                "added_volume": last["air_volume"] + last["water_level"],  # Only air volume remains
            })
            continue

        else:   # water still in rocket
            # Compute water depletion from previous mass_flow (based on last ejection velocity),
            # then compute air_volume from total_volume - water_level, then update pressure/ejection/mass_flow.
            results.append({
                "time": time,
                # previous mass flow (kg/s) used to compute volumetric outflow in this dt
                "mass_flow_prev": (mass_flow_prev := Mass_flow(inputs["density_water"], last["ejection_velocity"], nozzle_area)),
                # new water level (m^3)
                "water_level": (water_level := max(0.0, last["water_level"] - (mass_flow_prev / inputs["density_water"]) * dt)),
                # air volume computed from total bottle volume
                "air_volume": (air_volume := Air_volume(inputs["bottle_volume"], water_level)),
                # pressure using initial_air_volume as V_0
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
                "added_volume": air_volume + water_level,  # Ensure it matches bottle_volume
            })
        


    # ---- plotting: separate plot for each variable ----
    if results and plotValues:
        times = [r["time"] for r in results]

        # collect all keys except time, preserve insertion order from first result
        keys = [k for k in results[0].keys() if k != "time"]

        # determine grid layout
        n_series = len(keys)
        if n_series == 0:
            return_results = results
        ncols = min(4, max(1, n_series))
        nrows = math.ceil(n_series / ncols)

        # use smaller per-subplot size so full figure fits smaller screens
        fig, axes = plt.subplots(nrows=nrows, ncols=ncols, figsize=(3 * ncols, 2.2 * nrows))
        axes = np.array(axes).flatten()

        for ax, key in zip(axes, keys):
            vals = [r.get(key, 0.0) for r in results]
            ax.plot(times, vals, linewidth=1)
            ax.set_title(str(key))
            ax.set_xlabel("time (s)")
            ax.grid(True)

        # hide unused axes
        for ax in axes[len(keys):]:
            ax.set_visible(False)

        plt.tight_layout(pad=0.3)
        plt.show()

    # print(results)
    return results
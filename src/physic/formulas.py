import math
import matplotlib.pyplot as plt
import numpy as np

gui_input_values = {}

def start(values:dict) -> list[dict]:
    """
    Startet die Simulation mit den gegebenen Eingabewerten.

    Args:
        values (dict): Eingabeparameter, siehe calculateValues.
    """
    set_values(values)
    results = calculateValues(plotValues=False)
    print("max height:", get_max_height(results))
    print("max velocity:", get_max_velocity(results))
    return results

def show_contour_plot(values:dict):
    """
    Zeigt einen Konturplot für die maximale Höhe in Abhängigkeit von Düsengröße und Wasserfüllung.

    Args:
        values (dict): Eingabeparameter.
    """
    set_values(values)
    try_combinations(min_nozzle_mm=1.0, max_nozzle_mm=40.0, step_nozzle_mm=1.0,
                     min_bottle_volume_l=0.1, max_bottle_volume_l=1.0, step_bottle_volume_l=0.025)

def stop():
    """
    Stoppt die Simulation und setzt die Zeit zurück.

    Args:
        None
    """
    pass

def set_values(values: dict):
    """
    Setzt die globalen Eingabewerte für die Simulation.

    Args:
        values (dict): Parameter für die Simulation.
    """
    global gui_input_values
    gui_input_values = values.copy()

def get_max_height(results) -> float:
    """
    Gibt die maximale Höhe aus der Ergebnisliste zurück.

    Args:
        results (list): Liste von dicts mit Schlüssel 'posY' [m]

    Returns:
        float: Maximale Höhe [m]
    """
    return max((entry['posY'] for entry in results), default=0.0)

def get_max_velocity(results) -> float:
    """
    Gibt die Auftreffgeschwindigkeit aus der Ergebnisliste zurück.

    Args:
        results (list): Liste von dicts mit Schlüssel 'velocity' [m/s]

    Returns:
        float: Maximale Geschwindigkeit [m/s]
    """
    return results[-1]['velocity'] if results else 0.0

def try_combinations(min_nozzle_mm, max_nozzle_mm, step_nozzle_mm, min_bottle_volume_l, max_bottle_volume_l, step_bottle_volume_l):
    """
    Führt eine Parameterstudie für Düsengröße und Wasserfüllung durch und plottet die maximale Höhe.

    Args:
        min_nozzle_mm (float): Minimaler Düsendurchmesser [mm]
        max_nozzle_mm (float): Maximaler Düsendurchmesser [mm]
        step_nozzle_mm (float): Schrittweite Düsendurchmesser [mm]
        min_bottle_volume_l (float): Minimales Flaschenvolumen [l]
        max_bottle_volume_l (float): Maximales Flaschenvolumen [l]
        step_bottle_volume_l (float): Schrittweite Flaschenvolumen [l]

    Returns:
        None
    """
    thrust_values = np.arange(min_nozzle_mm, max_nozzle_mm + step_nozzle_mm, step_nozzle_mm)
    water_level_values = np.arange(min_bottle_volume_l, max_bottle_volume_l + step_bottle_volume_l, step_bottle_volume_l)
    max_heights = np.zeros((len(thrust_values), len(water_level_values)))
    for i, thrust in enumerate(thrust_values):
        for j, water_level in enumerate(water_level_values):
            gui_input_values["thrust_nozzle_diameter"] = thrust
            gui_input_values["water_level_rocket"] = round(water_level, 5)
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

def Thrust_nozzle_area(diameter_mm: float) -> float:
    """
    Berechnet die Düsenfläche aus dem Durchmesser.

    Args:
        diameter_mm (float): Düsendurchmesser [mm]

    Returns:
        float: Fläche [m^2]
    """
    r = diameter_mm * 0.0005
    return math.pi * r * r

def Air_volume(total_volume, water_volume):
    """
    Berechnet das Luftvolumen in der Flasche.

    Args:
        total_volume (float): Gesamtvolumen [m^3]
        water_volume (float): Wasservolumen [m^3]

    Returns:
        float: Luftvolumen [m^3]
    """
    return max(total_volume - water_volume, 0.0)

def Pressure(P_0, V_0, V, kappa_gas):
    """
    Berechnet die Druckentwicklung in der Flasche.

    Args:
        P_0 (float): Anfangsdruck [Pa]
        V_0 (float): Anfangsvolumen [m^3]
        V (float): aktuelles Volumen [m^3]
        kappa_gas (float): Adiabatenexponent [einheitslos]

    Returns:
        float: Druck [Pa]
    """
    return P_0 if V <= 0 else P_0 * (V_0 / V) ** kappa_gas

def Ejection_velocity(pressure, density_water, P_atm):
    """
    Berechnet die Ausstoßgeschwindigkeit des Wassers.

    Args:
        pressure (float): Druck [Pa]
        density_water (float): Dichte des Wassers [kg/m^3]
        P_atm (float): Atmosphärendruck [Pa]

    Returns:
        float: Geschwindigkeit [m/s]
    """
    return math.sqrt(2 * (pressure - P_atm) / density_water) if pressure > P_atm and density_water > 0 else 0.0

def Mass_flow(density_water, ejection_velocity, nozzle_area):
    """
    Berechnet den Massenstrom des Wassers.

    Args:
        density_water (float): Dichte des Wassers [kg/m^3]
        ejection_velocity (float): Ausstoßgeschwindigkeit [m/s]
        nozzle_area (float): Düsenfläche [m^2]

    Returns:
        float: Massenstrom [kg/s]
    """
    return density_water * ejection_velocity * nozzle_area

def Thrust(mass_flow, ejection_velocity):
    """
    Berechnet die Schubkraft.

    Args:
        mass_flow (float): Massenstrom [kg/s]
        ejection_velocity (float): Ausstoßgeschwindigkeit [m/s]

    Returns:
        float: Schub [N]
    """
    return mass_flow * ejection_velocity

def Air_Resistance(diameter_rocket, velocity):
    """
    Berechnet den Luftwiderstand.

    Args:
        diameter_rocket (float): Durchmesser der Rakete [m]
        velocity (float): Geschwindigkeit [m/s]

    Returns:
        float: Widerstandskraft [N]
    """
    C_w = 1.0
    rho_air = 1.225
    r = diameter_rocket / 2
    A = math.pi * r**2
    # Widerstand ist immer entgegen der Bewegungsrichtung
    return 0.5 * C_w * rho_air * A * velocity * abs(velocity)

def Gravity_force(mass):
    """
    Berechnet die Gewichtskraft.

    Args:
        mass (float): Masse [kg]

    Returns:
        float: Gewichtskraft [N]
    """
    return mass * 9.81

def calculateValues(plotValues=False):
    """
    Führt die Simulation der Rakete durch.

    Args:
        plotValues (bool): Wenn True, werden die Ergebnisse geplottet.
    
    Returns:
        list: Liste von dicts mit Zeitverlauf der Simulation.
            Jeder dict enthält:
                time [s]
                posY [m]
                velocity [m/s]
                acceleration [m/s^2]
                thrust [N]
                air_resistance [N]
                gravity_force [N]
                pressure [Pa]
                water_level [m^3]
                air_volume [m^3]
                total_mass [kg]
                usw.
    """
    defaults = {
        "kappa_gas": 1.4, "density_water": 1000.0, "P_atm": 101325.0, "endTime": 5.0
    }
    # Eingabewerte sammeln bzw. kombinieren
    inputs = {**defaults, **(gui_input_values or {})}
    try:
        bottle_vol = float(inputs["bottle_volume"])
        water_lvl = float(inputs["water_level_rocket"])
        pressure_bar = float(inputs["pressure"])
        empty_mass = float(inputs["empty_rocket_weight"])
        nozzle_mm = float(inputs["thrust_nozzle_diameter"])
        kappa = float(inputs["kappa_gas"])
        rho_water = float(inputs["density_water"])
        P_atm_val = float(inputs["P_atm"])
        diam_rocket = float(inputs["diameter_rocket"])
        end_time = float(inputs["endTime"])
    except Exception:
        raise ValueError("One or more inputs are not numeric.")

    # Validierung der Eingaben mit passender Fehlermeldung
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
    if end_time <= 0:
        raise ValueError("endTime must be > 0 (s).")

    # Einheitenumrechnung auf SI
    inputs.update({
        "pressure": pressure_bar * 1e5,           # bar -> Pa
        "water_level_rocket": water_lvl * 1e-3,   # l -> m³
        "bottle_volume": bottle_vol * 1e-3,       # l -> m³
        "empty_rocket_weight": empty_mass,        # kg
        "thrust_nozzle_diameter": nozzle_mm,      # mm
        "kappa_gas": kappa,
        "density_water": rho_water,               # kg/m³
        "P_atm": P_atm_val,                       # Pa
        "diameter_rocket": diam_rocket,           # m
        "endTime": end_time                       # s
    })

    results = []
    dt = 0.001  # 1 ms timestep
    steps = int(end_time / dt) + 1
    # Berechnung der Werte für den initialen Zustand (Randbedingungen)
    nozzle_area = Thrust_nozzle_area(inputs["thrust_nozzle_diameter"])
    total_mass0 = inputs["empty_rocket_weight"] + inputs["density_water"] * inputs["water_level_rocket"]
    air_volume0 = max(inputs["bottle_volume"] - inputs["water_level_rocket"], 0.0)
    pressure0 = inputs["pressure"]
    v_a0 = Ejection_velocity(pressure0, inputs["density_water"], inputs["P_atm"])
    mass_flow0 = Mass_flow(inputs["density_water"], v_a0, nozzle_area)
    thrust0 = Thrust(mass_flow0, v_a0)
    gravity_force0 = Gravity_force(total_mass0)
    accel0 = (thrust0 - gravity_force0) / total_mass0 if total_mass0 > 0 else 0.0

    results.append({
        "time": 0.0,
        "air_volume": air_volume0,
        "pressure": pressure0,
        "ejection_velocity": v_a0,
        "mass_flow": mass_flow0,
        "thrust": thrust0,
        "air_resistance": 0.0,
        "total_force": thrust0 - gravity_force0,
        "gravity_force": gravity_force0,
        "acceleration": accel0,
        "velocity": 0.0,
        "posY": 0.0,
        "water_level": inputs["water_level_rocket"],
        "total_mass": total_mass0,
    })

    # Haupt-Simulationsschleife
    for step in range(1, steps):
        time = step * dt
        last = results[-1]
        if last["posY"] <= 0.0 and step > 4:
            break # Abbruch wenn Rakete wieder am Boden ist (step > 4 willkürlich gewählt, damit Anfangsposition ausgenommen wird)
        if last["water_level"] <= 0.0 or last["pressure"] < inputs["P_atm"]:
            total_mass = inputs["empty_rocket_weight"]
            air_resistance = Air_Resistance(inputs["diameter_rocket"], last["velocity"])
            gravity_force = Gravity_force(total_mass)
            total_force = -air_resistance - gravity_force
            acceleration = total_force / total_mass if total_mass > 0 else 0.0
            newVelocity = last["velocity"] + acceleration * dt
            results.append({
                "time": time,
                "air_volume": last["air_volume"],
                "pressure": inputs["P_atm"],
                "ejection_velocity": 0.0,
                "mass_flow": 0.0,
                "thrust": 0.0,
                "air_resistance": air_resistance,
                "gravity_force": gravity_force,
                "total_force": total_force,
                "acceleration": acceleration,
                "velocity": newVelocity,
                "posY": max(0.0, last["posY"] + newVelocity * dt),
                "water_level": 0.0,
                "total_mass": total_mass,
            })
        else: # normale Berechnung
            mass_flow_prev = Mass_flow(inputs["density_water"], last["ejection_velocity"], nozzle_area)
            water_level = max(0.0, last["water_level"] - (mass_flow_prev / inputs["density_water"]) * dt)   # Euler Schritt
            air_volume = Air_volume(inputs["bottle_volume"], water_level)
            pressure = Pressure(inputs["pressure"], inputs["bottle_volume"] - inputs["water_level_rocket"], air_volume, inputs["kappa_gas"])
            ejection_velocity = Ejection_velocity(pressure, inputs["density_water"], inputs["P_atm"])
            mass_flow_rate = Mass_flow(inputs["density_water"], ejection_velocity, nozzle_area)
            thrust_value = Thrust(mass_flow_rate, ejection_velocity)
            air_resistance = Air_Resistance(inputs["diameter_rocket"], last["velocity"])
            total_mass = inputs["empty_rocket_weight"] + inputs["density_water"] * water_level
            gravity_force = Gravity_force(total_mass)
            total_force = thrust_value - air_resistance - gravity_force
            acceleration = total_force / total_mass if total_mass > 0 else 0.0
            # Ergebnisse speichern
            results.append({
                "time": time,
                "mass_flow_prev": mass_flow_prev,
                "water_level": water_level,
                "air_volume": air_volume,
                "pressure": pressure,
                "ejection_velocity": ejection_velocity,
                "mass_flow": mass_flow_rate,
                "thrust": thrust_value,
                "air_resistance": air_resistance,
                "gravity_force": gravity_force,
                "total_force": total_force,
                "acceleration": acceleration,
                "velocity": last["velocity"] + acceleration * dt,       # Euler Schritt
                "posY": max(0.0, last["posY"] + last["velocity"] * dt), # Euler Schritt
                "total_mass": total_mass,
            })

    # Plot falls gewünscht
    if results and plotValues:
        times = [r["time"] for r in results]
        # Mapping von Schlüssel zu Einheiten
        units = {
            "posY": "[m]",
            "velocity": "[m/s]",
            "acceleration": "[m/s²]",
            "thrust": "[N]",
            "air_resistance": "[N]",
            "gravity_force": "[N]",
            "pressure": "[Pa]",
            "water_level": "[m³]",
            "air_volume": "[m³]",
            "total_mass": "[kg]",
            "mass_flow": "[kg/s]",
            "ejection_velocity": "[m/s]",
            "mass_flow_prev": "[kg/s]",
            "total_force": "[N]",
        }
        keys = [k for k in results[0].keys() if k != "time"]
        ncols = min(4, max(1, len(keys)))
        nrows = int(np.ceil(len(keys) / ncols))
        fig, axes = plt.subplots(nrows=nrows, ncols=ncols, figsize=(3 * ncols, 2.2 * nrows))
        axes = np.array(axes).flatten()
        for ax, key in zip(axes, keys):
            ax.plot(times, [r.get(key, 0.0) for r in results], linewidth=1)
            unit = units.get(key, "")
            ax.set_title(f"{key} {unit}".strip())
            ax.set_xlabel("time (s)")
            ax.grid(True)
        for ax in axes[len(keys):]:
            ax.set_visible(False)
        plt.tight_layout(pad=0.3)
        plt.show()
    return results
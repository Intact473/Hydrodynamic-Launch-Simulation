import sys
sys.dont_write_bytecode = True
import pygame as pg
import pygame_gui as gui
from view.gui import ControlPanel
from simulation.simulation import Simulation
import physic.formulas as formulas
Vec2 = pg.math.Vector2
import math

pg.init()

# Create two separate windows in one
WINDOW_W, WINDOW_H = 1300, 820
PANEL_W = 280
screen = pg.display.set_mode((WINDOW_W, WINDOW_H))
gui_window = pg.Rect(0, 0, PANEL_W, WINDOW_H)
simulation_window = pg.Rect(PANEL_W, 0, WINDOW_W - PANEL_W, WINDOW_H)
clock = pg.time.Clock()

# expose module-level sim so other modules can import view.window.sim
sim = Simulation(simulation_window)

def get_sim():
    """Return the Simulation instance (or None if not created yet)."""
    return sim

def run_window(start=None, stop=None):
    """Run the main application window with a control panel and a simulation area."""
    running = True
    manager = gui.UIManager((WINDOW_W, WINDOW_H))
    
    #sim.place_rocket_bottom_center(margin_px=10)
    sim.camera_center = Vec2(sim.rocket.pos) - Vec2(0, 2.0)     

    def handle_start(values):
        """Handle the start button event from the control panel.
        :param values: Dictionary of input values from the control panel
        """
        sim.pixel_to_meter = 180.0
        sim.start_pos_y = sim.rocket.pos.y
        print("start pos: ", sim.start_pos_y)
        sim.rocket_is_flying = True
        if start:
            start(values)

    def handle_reset():
        """Handle the reset button event from the control panel.
        Sets the simulation and rocket to initial state."""

        sim.rocket_is_flying = False
        sim.rocket.pos = Vec2(0.0, 0.0)
        sim.pixel_to_meter = 180.0
        sim.rocket.angle = math.radians(90.0)
        sim.start_pos_y = sim.rocket.pos.y
        sim.camera_center = Vec2(sim.rocket.pos) - Vec2(0, 2.0)
        if stop:
            stop()

    def handle_contour_plot(values):
        formulas.show_contour_plot(values=values)
    try:
        panel = ControlPanel(gui_window, manager, on_start=handle_start, on_reset=handle_reset, on_contour_plot=handle_contour_plot)
    except Exception as e:
        print("Error creating control panel:", e)
        return
    while running:
        # Handle events
        dt = clock.tick(60)  # sets framerate (fps)
        dt_ms = dt

        dt /= 1000.0  # convert to seconds

        for event in pg.event.get():
            if event.type == pg.QUIT:
                running = False
            manager.process_events(event)

            if event.type == pg.USEREVENT:
                if event.user_type == gui.UI_BUTTON_PRESSED:
                    panel.handle_event(event)

        sim.results = formulas.results
        
        sim.update(dt_ms)

        if not sim.rocket_is_flying and formulas.results:
            max_v = formulas.get_max_velocity(formulas.results)
            max_h = formulas.get_max_height(formulas.results)
            panel.out_max_velocity.set_text(f"{max_v:.2f}")
            panel.out_max_height.set_text(f"{max_h:.2f}")
            
        manager.update(dt)

        screen.fill((255, 255, 255))
        pg.draw.rect(screen, (0, 0, 0), gui_window)
        pg.draw.line(screen, (200, 200, 200),gui_window.topright, gui_window.bottomright, 2)

        sim.draw(screen)
        manager.draw_ui(screen)
        pg.display.flip()

    pg.quit()
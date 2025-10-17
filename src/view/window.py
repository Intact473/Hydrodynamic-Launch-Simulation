import sys
sys.dont_write_bytecode = True
import pygame as pg
import pygame_gui as gui
from view.gui import ControlPanel
from simulation.simulation import Simulation
import physic.formulas as formulas

pg.init()

# Create two separate windows in one
WINDOW_W, WINDOW_H = 1280, 720
PANEL_W = 360
screen = pg.display.set_mode((WINDOW_W, WINDOW_H))
gui_window = pg.Rect(0, 0, PANEL_W, WINDOW_H)
simulation_window = pg.Rect(PANEL_W, 0, WINDOW_W - PANEL_W, WINDOW_H)
clock = pg.time.Clock()


def run_window(start=None, stop=None):
    """Run the main application window with a control panel and a simulation area."""
    running = True
    manager = gui.UIManager((WINDOW_W, WINDOW_H))
    sim = Simulation(simulation_window)
    panel = ControlPanel(gui_window, manager, on_start=start, on_reset=stop,toggle_mode=sim.toggle_mode)
    
    

    while running:
        # Handle events
        dt = clock.tick(60) # Framerate of 60 fps
        formulas.time+=dt/1000

        formulas.calculateValues()

        print(formulas.time)

        for event in pg.event.get():
            if event.type == pg.QUIT:
                running = False
            manager.process_events(event)

            if event.type == pg.USEREVENT:
                if event.user_type == gui.UI_BUTTON_PRESSED:
                    panel.handle_event(event)

        manager.update(dt)
        sim.update(dt)

        screen.fill((255, 255, 255))
        pg.draw.rect(screen, (0, 0, 0), gui_window)
        pg.draw.line(screen, (200, 200, 200),gui_window.topright, gui_window.bottomright, 2)

        sim.draw(screen)
        manager.draw_ui(screen)
        pg.display.flip()

    pg.quit()
import pygame as pg

pg.init()

#Create two seperate windows in one
WINDOW_W, WINDOW_H = 1280, 720
PANEL_W = 360
screen = pg.display.set_mode((WINDOW_W, WINDOW_H))
gui_window = pg.Rect(0, 0, PANEL_W, WINDOW_H)
simulation_window = pg.Rect(PANEL_W, 0, WINDOW_W-PANEL_W, WINDOW_H)
clock = pg.time.Clock()

def run_window():
    running=True
    while running:
        for event in pg.event.get():
            if event.type == pg.QUIT:
                running = False;
        screen.fill((255,255,255))
        pg.draw.rect(screen, (255, 0, 0), gui_window)
        pg.draw.rect(screen, (0, 255, 0), simulation_window)


        pg.draw.line(screen, (200, 200, 200), gui_window.topright, gui_window.bottomright, 2)
        
        
        pg.display.flip()
        clock.tick(60) #->TODO Muss evtl noch angepasst werden an den Raketenflug

    pg.quit();
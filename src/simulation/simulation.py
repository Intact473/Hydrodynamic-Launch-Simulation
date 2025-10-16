import pygame as pg
import math
from pygame.math import Vector2 as Vec2
from simulation.rocket import Rocket

class Simulation:
    def __init__(self, sim_rect: pg.Rect):
        self.rect = sim_rect
        self.pixel_to_meter = 100.0
        self.rocket = Rocket(
            length_rocket=2.0,
            radius_of_rocket_cylinder=0.22,
            angle_deg=90.0,
            start_pos_rocket=Vec2(3.2, 1.6)
        )
        self.place_rocket_bottom_center(margin_px=16)

    def place_rocket_bottom_center(self, margin_px):
        pixel_to_meter = self.pixel_to_meter
        nozzle_h_px = max(2, int(0.55 * self.rocket.nozzle_d * pixel_to_meter))
        start_pos_screen_x = self.rect.width // 2
        start_pos_screen_y = self.rect.height - margin_px - nozzle_h_px // 2

        local = self.rocket._center_nozzle()
        cos_angle, sin_angle = math.cos(self.rocket.angle), math.sin(self.rocket.angle)
        rotated_x = local.x * cos_angle - local.y * sin_angle
        rotated_y = local.x * sin_angle + local.y * cos_angle

        pos_x_m = start_pos_screen_x / pixel_to_meter - rotated_x
        pos_y_m = start_pos_screen_y / pixel_to_meter + rotated_y

        self.rocket.pos = Vec2(pos_x_m, pos_y_m)

    def update(self, dt: float):
        #ToDo: Update rocket position
        pass

    def draw(self, screen: pg.Surface):
        draw_pos_rocket = screen.subsurface(self.rect)
        draw_pos_rocket.fill((242, 244, 248))
        for x in range(0, self.rect.width, 40):
            pg.draw.line(draw_pos_rocket, (225, 230, 236), (x, 0), (x, self.rect.height), 1)
        for y in range(0, self.rect.height, 40):
            pg.draw.line(draw_pos_rocket, (225, 230, 236), (0, y), (self.rect.width, y), 1)
        self.rocket.draw(draw_pos_rocket, meters_to_px=self.pixel_to_meter, outline=True)
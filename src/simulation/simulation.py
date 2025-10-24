import pygame as pg
import math
from pygame.math import Vector2 as Vec2
from simulation.rocket import Rocket
import physic.formulas as formulas

class Simulation:
    def __init__(self, sim_rect: pg.Rect):
        self.rect = sim_rect
        self.pixel_to_meter = 180.0
        self.rocket = Rocket(
            length_rocket=2.0,
            radius_of_rocket_cylinder=0.22,
            angle_deg=90.0,
            start_pos_rocket=Vec2(0, 0)
        )

        self.start_pos_y = 0.0
        self.bg_image = pg.image.load("img/ohm.jpg").convert()
        self.bg_image = pg.transform.scale(self.bg_image, (self.rect.width, self.rect.height))
        self.use_image_bg = True
        self.rocket_is_flying = False
        self.zoom_speed = 1.0 # zoom speed, 1 is slow
        self.time = 0.0  # simulation time in seconds
        self.results = []

    def toggle_mode(self):
        self.use_image_bg = not self.use_image_bg

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
        """Update the simulation state
        :param dt: Time delta in seconds since the last update
        """
        if self.rocket_is_flying:
            posY = 0

            if int(self.time) >= len(self.results):
                posY = 0
                self.rocket_is_flying = False
                print("Simulation ended")
            else: 
                posY = self.results[int(self.time)]['posY']
            self.rocket.pos.y = self.start_pos_y - posY

            target = self.rocket.pos - Vec2(0, 1.5)
            self.camera_center += (target - self.camera_center) * 0.1
            d_between = abs(self.rocket.pos.y - self.start_pos_y)
            max_zoom_in = 180.0
            min_zoom_out = 30.0
            new_calculated_zoom = max(min_zoom_out,min(max_zoom_in,max_zoom_in - self.zoom_speed * d_between)
            )
            self.pixel_to_meter += (new_calculated_zoom - self.pixel_to_meter) * 0.05
            self.time += dt
        
    def draw_axes(self, surface: pg.Surface, meters_to_px: float, camera_center: Vec2):
        width, height = surface.get_size()
        center_x = width // 2
        center_y = height // 2

        world_origin_screen = Vec2(
            center_x - (camera_center.x * meters_to_px),
            center_y - (camera_center.y * meters_to_px)
        )

        pg.draw.circle(surface, (255, 0, 0), (int(world_origin_screen.x), int(world_origin_screen.y)), 5)
        for y in range(-100, 100):
            y_world = y
            y_screen = world_origin_screen.y - y_world * meters_to_px
            if 0 <= y_screen <= height:
                line_width = 1
                line_color = (0, 255, 0)

                if y == 0:
                    line_width = 4
                    line_color = (255, 0, 0)
                pg.draw.line(surface, line_color, (0, int(y_screen)), (width, int(y_screen)), line_width)
                font = pg.font.SysFont(None, 18)
                label_text = "GROUND" if y == 0 else f"{y} m"
                label = font.render(label_text, True, line_color)
                surface.blit(label, (5, int(y_screen) - 10))

    
    def draw(self, screen: pg.Surface):
        sim_surface = screen.subsurface(self.rect)
        sim_surface.blit(self.bg_image, (0, 0))
        if not self.use_image_bg:
            sim_surface.blit(self.bg_image, (0, 0))
        else:
            sim_surface.fill((0, 0, 0))
            self.draw_axes(sim_surface, self.pixel_to_meter, self.camera_center)
        self.rocket.draw(sim_surface, meters_to_px=self.pixel_to_meter, camera_center = self.camera_center ,outline=True)
        
        font = pg.font.SysFont(None, 24)
        #Please do not delete the line below, it might be useful when the rocket is falling down to the earth
        sim_surface.blit(font.render(f"zoom: {self.pixel_to_meter:.1f}", True, (255,255,255)), (10, 30))
        sim_surface.blit(font.render(f"rocket hight: {(self.rocket.pos.y):.1f}", True, (255,255,255)), (10, 10))
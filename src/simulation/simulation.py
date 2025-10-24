import pygame as pg
import math
from pygame.math import Vector2 as Vec2
from simulation.rocket import Rocket
import physic.formulas as formulas

class Simulation:
    def __init__(self, sim_rect: pg.Rect):
        self.rect = sim_rect
        self.pixel_to_meter = 100.0
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
        :param dt: Time delta in milliseconds since the last update
        100px = 1 meter
        """
        if self.rocket_is_flying:
            # use instance time (dt is expected in seconds)
            # print("time", self.time)
            # print("len results", len(self.results))

            posY = 0

            if int(self.time) >= len(self.results):
                posY = 0
                self.rocket_is_flying = False
                print("Simulation ended")
            else: 
                posY = self.results[int(self.time)]['posY']
                
            
            
            print(self.rocket.pos.y)
            self.rocket.pos.y = self.start_pos_y - posY
            # print(self.start_pos_y)
            # print("posY: ", self.rocket.pos.y, " at time: ", self.time)

            target = self.rocket.pos - Vec2(0, 1.5)
            self.camera_center += (target - self.camera_center) * 0.1
            
            d_between_actual_pos_and_start_pos = abs(self.rocket.pos.y - self.start_pos_y)
            new_calculated_zoom = max(30.0, min(100.0, 100.0 - self.zoom_speed * d_between_actual_pos_and_start_pos))
            self.pixel_to_meter = new_calculated_zoom
            if d_between_actual_pos_and_start_pos > (self.rect.height / self.pixel_to_meter) * 0.3:
                self.pixel_to_meter = max(30.0, self.pixel_to_meter * 0.995)

            elif d_between_actual_pos_and_start_pos < (self.rect.height / self.pixel_to_meter) * 0.1:
                self.pixel_to_meter = min(100.0, self.pixel_to_meter * 1.005)
            # print(f"d_between_actual_pos_and_start_pos: {d_between_actual_pos_and_start_pos:.2f}, pos.y: {self.rocket.pos.y:.2f}, cam.y: {self.camera_center.y:.2f}, zoom: {self.pixel_to_meter:.2f}")
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
                pg.draw.line(surface, (0, 255, 0), (0, int(y_screen)), (width, int(y_screen)),1)
                font = pg.font.SysFont(None, 18)
                label = font.render(f"{y} m", True, (0, 255, 0))
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
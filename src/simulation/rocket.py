import sys
sys.dont_write_bytecode = True
import pygame as pg
import math
import physic.formulas as formulas

Vec2 = pg.math.Vector2

class Rocket:
    def __init__(self,
                 length_rocket: float = 3.0,
                 radius_of_rocket_cylinder: float = 0.22,
                 nozzle_d: float = formulas.gui_input_values.get("thrust_nozzle_diameter", 60) / 1000.0,
                 angle_deg: float = 90.0,
                 start_pos_rocket: Vec2 = Vec2(2.5, 1.2)):
        self.length_rocket = float(length_rocket)
        self.radius_of_rocket_cylinder = float(radius_of_rocket_cylinder)
        self.nozzle_d = float(nozzle_d)
        self.angle = math.radians(angle_deg)
        self.pos = Vec2(start_pos_rocket)

        self.color_of_bottle = (20, 180, 255)
        self.color_of_outline = (48, 56, 70)
        self.color_of_fin = (255, 0, 0)
        self.color_of_nozzle = (100, 110, 128)
        self.color_of_window = (90, 160, 220)
        self.color_of_nose = (255,0,0)
        self.color_of_tennis_ball = (255, 200, 0)
    def create_tennis_ball(self):
        """
        Create a tennis ball at the tip of the rocket nose cone.
        Returns the center position (Vec2) and radius (float in meters) of the tennis ball.
        """
        Length_rocket = self.length_rocket

        x_start_ball = 0.1 * Length_rocket
        nose_length = 0.10 * Length_rocket

        x_center = x_start_ball + nose_length
        y_center = 0.0

        return Vec2(x_center, y_center), 0.03 * Length_rocket

    def creatre_nose_module(self):
        """
        Create the nose cone shape of the rocket.
        Returns a list of (x, y) points defining the nose cone polygon.
        
        """
        Length_rocket = self.length_rocket
        Radius_rocket = self.radius_of_rocket_cylinder

        x_start_nose = 0.1 * Length_rocket
        nose_length = 0.10 * Length_rocket
        nose_height = 0.25 * Radius_rocket
        x_tip_of_nose  = x_start_nose + nose_length

        nose_upper = [
            (x_start_nose,  Radius_rocket * 0.6),
            (x_tip_of_nose,   nose_height * 0.2),
        ]
        nose_lower = [
            (x_tip_of_nose,  -nose_height * 0.2),
            (x_start_nose, -Radius_rocket * 0.6),
        ]

        return nose_lower + nose_upper
    
    def create_bottle(self):
        """
        Create the bottle body shape of the rocket.
        Returns a list of (x, y) points defining the bottle polygon.
        """
        Length_rocket =self.length_rocket
        Radius_rocket = self.radius_of_rocket_cylinder

        front_of_bottle = 0.1 * Length_rocket
        end_bottle_neck = -0.50 * Length_rocket
        lenth_bottle_neck = max(0.05 * Length_rocket, 0.16 * Length_rocket)
        start_bottle_neck = end_bottle_neck + lenth_bottle_neck

        radius_of_bottle_body  = 0.6 * Radius_rocket
        radius_of_bottle_nozzle = max(self.nozzle_d * 0.5, 0.25 * Radius_rocket)

        def radius_at(x: float) -> float:
            """Get the bottle radius at position x along the rocket axis."""
            if x >= start_bottle_neck:
                return radius_of_bottle_body
            t = (x - end_bottle_neck) / max((start_bottle_neck - end_bottle_neck), 1e-9)
            s = 0.5 - 0.5 * math.cos(math.pi * t)
            return (1.0 - s) * radius_of_bottle_nozzle + s * radius_of_bottle_body

        amount_of_profile_sample_points = 64
        list_of_x_coordinates = [end_bottle_neck + (front_of_bottle - end_bottle_neck) * i / amount_of_profile_sample_points for i in range(amount_of_profile_sample_points + 1)]
        upper_points = [(x, radius_at(x)) for x in list_of_x_coordinates]

        lower_points = [(x, -y) for (x, y) in reversed(upper_points)]
        return lower_points + upper_points

    def create_fins(self):
        """
        Create the fin shapes of the rocket.
        Returns two lists of (x, y) points defining the bottom and top fin polygons.
        """
        Length_rocket =self.length_rocket
        Radius_rocket = self.radius_of_rocket_cylinder

        end_bottle_neck   = -0.50 * Length_rocket
        lenth_bottle_neck   = max(0.05 * Length_rocket, 0.16 * Length_rocket)
        start_bottle_neck = end_bottle_neck + lenth_bottle_neck

        radius_of_bottle_body  = 0.52 * Radius_rocket
        radius_of_bottle_nozzle = max(self.nozzle_d * 0.5, 0.25 * Radius_rocket)

        offset_front_fin = 0.02 * Length_rocket
        spread_of_fin_outward = 0.40 * Radius_rocket
        offset_back_fin = 0.04 * Length_rocket
        taper_front_fin = 0.20 * Radius_rocket

        inner_front = (start_bottle_neck + offset_front_fin, -radius_of_bottle_body)
        inner_back  = (end_bottle_neck, -radius_of_bottle_nozzle)

        outer_back  = (end_bottle_neck - offset_back_fin, -radius_of_bottle_nozzle - spread_of_fin_outward)
        outer_front = (start_bottle_neck + offset_front_fin + 0.08 * Length_rocket, -radius_of_bottle_body - taper_front_fin)

        fin_bottom_shape = [inner_front, inner_back, outer_back, outer_front]
        fin_top_shape = [(x, -y) for (x, y) in fin_bottom_shape]
        return fin_bottom_shape, fin_top_shape

    def _center_nozzle(self):
        return Vec2(-0.50 * self.length_rocket, 0.0)

    def _transform_points(self, pts, meters_to_px: float):
        """
        Transform local (x,y) points to screen coordinates, applying rotation and translation.
        Parameters:
            pts: list of (x, y) points in local rocket coordinates (meters)
            meters_to_px: scaling factor from meters to pixels
        Returns:
            list of (x, y) points in screen coordinates (pixels)
        """
        cos_angle, sin_angle = math.cos(self.angle), math.sin(self.angle)
        out = []
        for x, y in pts:
            rotated_x =  x*cos_angle - y*sin_angle
            rotated_y =  x*sin_angle + y*cos_angle
            x_screen_pos = (self.pos.x + rotated_x) * meters_to_px
            y_screen_pos = (self.pos.y - rotated_y) * meters_to_px
            out.append((int(round(x_screen_pos)), int(round(y_screen_pos))))
        return out

    def draw(self, surf: pg.Surface, meters_to_px: float = 100.0, outline: bool = True):
        """
        Draw the rocket on the given surface.
        Parameters:
            surf: the pygame surface to draw on
            meters_to_px: scaling factor from meters to pixels
            outline: whether to draw outlines around the rocket parts
        """
        nose_pts_screen = self._transform_points(self.creatre_nose_module(), meters_to_px)
        pg.draw.polygon(surf, self.color_of_nose, nose_pts_screen)
        if outline:
            pg.draw.lines(surf, self.color_of_outline, True, nose_pts_screen, 2)
        tip_center_local, tip_r_m = self.create_tennis_ball()
        tip_center_screen = self._transform_points([tip_center_local], meters_to_px)[0]
        tip_radius_px = int(tip_r_m * meters_to_px)

        pg.draw.circle(surf, self.color_of_tennis_ball, tip_center_screen, tip_radius_px)
        if outline:
            pg.draw.circle(surf, self.color_of_outline, tip_center_screen, tip_radius_px, 2)


        body_pts_screen = self._transform_points(self.create_bottle(), meters_to_px)
        pg.draw.polygon(surf, self.color_of_bottle, body_pts_screen)
        if outline:
            pg.draw.lines(surf, self.color_of_outline, True, body_pts_screen, 2)

        fins_bot, fins_top = self.create_fins()
        for fin in (fins_bot, fins_top):
            fin_screen = self._transform_points(fin, meters_to_px)
            pg.draw.polygon(surf, self.color_of_fin, fin_screen)
            if outline:
                pg.draw.lines(surf, self.color_of_outline, True, fin_screen, 2)

        nx_screen_pos, ny_screen_pos = self._transform_points([self._center_nozzle()], meters_to_px)[0]
        nozzle_w_px = max(2, int(self.nozzle_d * meters_to_px))
        nozzle_h_px = max(2, int(0.55 * self.nozzle_d * meters_to_px))
        rect = pg.Rect(0, 0, nozzle_w_px, nozzle_h_px)
        rect.center = (nx_screen_pos, ny_screen_pos)
        pg.draw.ellipse(surf, self.color_of_nozzle, rect)
        if outline:
            pg.draw.ellipse(surf, self.color_of_outline, rect, 2)
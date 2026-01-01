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
        self.scale = 0.25

        self.length_rocket = float(length_rocket) * self.scale
        self.radius_of_rocket_cylinder = float(radius_of_rocket_cylinder) * self.scale
        self.nozzle_d = float(nozzle_d) * self.scale

        self.angle = math.radians(angle_deg)
        self.pos = Vec2(start_pos_rocket)

        # Farben
        self.color_of_bottle = (20, 180, 255)
        self.color_of_outline = (50, 50, 50)
        self.color_of_fin = (255, 0, 0)
        self.color_of_nozzle = (128, 128, 128)
        self.color_of_nose = (255, 0, 0)
        self.color_of_tennis_ball = (255, 255, 0)

    def create_tennis_ball(self):
        """
        Create the tennis ball at the tip of the rocket nose.

        Returns:
            tuple: (Vec2, float) - Center position in local coordinates and radius [m]
        """
        L = self.length_rocket
        x_center = L * (1 + 0.10 + 0.03)
        y_center = 0.0
        return Vec2(x_center, y_center), 0.03 * L

    def create_nose_module(self):
        """
        Create the nose cone polygon points in local coordinates.

        Returns:
            list: List of (x, y) tuples defining the nose cone polygon
        """
        L = self.length_rocket
        R = self.radius_of_rocket_cylinder
        x_start = L
        nose_length = 0.10 * L
        x_tip = x_start + nose_length
        nose_height = 0.25 * R

        nose_upper = [(x_start, R * 0.6), (x_tip, nose_height * 0.2)]
        nose_lower = [(x_tip, -nose_height * 0.2), (x_start, -R * 0.6)]
        return nose_lower + nose_upper

    def create_bottle(self):
        """
        Create the rocket body/bottle polygon points with smooth transition from nozzle to body.

        Returns:
            list: List of (x, y) tuples defining the bottle polygon
        """
        L = self.length_rocket
        R = self.radius_of_rocket_cylinder
        end_neck = 0.0
        len_neck = max(0.05 * L, 0.16 * L)
        start_neck = end_neck + len_neck
        front = L

        radius_body = 0.6 * R
        radius_nozzle = max(self.nozzle_d * 0.5, 0.25 * R)

        def radius_at(x: float) -> float:
            if x >= start_neck:
                return radius_body
            t = (x - end_neck) / max((start_neck - end_neck), 1e-9)
            s = 0.5 - 0.5 * math.cos(math.pi * t)
            return (1.0 - s) * radius_nozzle + s * radius_body

        n_points = 64
        x_list = [end_neck + (front - end_neck) * i / n_points for i in range(n_points + 1)]
        upper = [(x, radius_at(x)) for x in x_list]
        lower = [(x, -y) for (x, y) in reversed(upper)]
        return lower + upper

    def create_fins(self):
        """
        Create the fin polygons (top and bottom) in local coordinates.

        Returns:
            tuple: (list, list) - Bottom fin polygon and top fin polygon points
        """
        L = self.length_rocket
        R = self.radius_of_rocket_cylinder
        end_neck = -0.0
        len_neck = max(0.05 * L, 0.16 * L)
        start_neck = end_neck + len_neck

        radius_body = 0.52 * R
        radius_nozzle = max(self.nozzle_d * 0.5, 0.25 * R)

        offset_front_fin = 0.02 * L
        spread_out = 0.40 * R
        offset_back_fin = 0.04 * L
        taper_front_fin = 0.20 * R

        inner_front = (start_neck + offset_front_fin, -radius_body)
        inner_back = (end_neck, -radius_nozzle)
        outer_back = (end_neck - offset_back_fin, -radius_nozzle - spread_out)
        outer_front = (start_neck + offset_front_fin + 0.08 * L, -radius_body - taper_front_fin)

        fin_bottom = [inner_front, inner_back, outer_back, outer_front]
        fin_top = [(x, -y) for (x, y) in fin_bottom]
        return fin_bottom, fin_top

    def _center_nozzle(self):
        """
        Get the local coordinates of the center of the nozzle.

        Returns:
            Vec2: Nozzle center position in local coordinates
        """
        return Vec2(0.0, 0.0)

    def _transform_points(self, pts, meters_to_px: float, camera_center: Vec2, surf: pg.Surface):
        """
        Transform local rocket points to screen coordinates.

        Args:
            pts (list): List of local points (x, y) tuples
            meters_to_px (float): Scale factor from meters to pixels
            camera_center (Vec2): Center of the camera in world coordinates
            surf (pg.Surface): The surface to draw on (for width/height)

        Returns:
            list: List of transformed points in screen coordinates
        """
        cos_angle, sin_angle = math.cos(self.angle), math.sin(self.angle)
        out = []
        for x, y in pts:
            rotated_x = x * cos_angle - y * sin_angle
            rotated_y = x * sin_angle + y * cos_angle
            x_screen_pos = (self.pos.x + rotated_x - camera_center.x) * meters_to_px + 0.5 * surf.get_width()
            y_screen_pos = (self.pos.y - rotated_y - camera_center.y) * meters_to_px + 0.5 * surf.get_height()
            out.append((int(round(x_screen_pos)), int(round(y_screen_pos))))
        return out

    def draw(self, surf: pg.Surface, meters_to_px: float = 100.0,
             camera_center: Vec2 = Vec2(0, 0), outline: bool = True):
        """
        Draw the complete rocket (nose, body, fins, nozzle) on the surface.

        Args:
            surf (pg.Surface): Pygame surface to draw on
            meters_to_px (float): Scale factor from meters to pixels [default: 100.0]
            camera_center (Vec2): Center of the camera in world coordinates [default: (0, 0)]
            outline (bool): Whether to draw outlines [default: True]
        """

        nose_pts_screen = self._transform_points(self.create_nose_module(), meters_to_px, camera_center, surf)
        pg.draw.polygon(surf, self.color_of_nose, nose_pts_screen)
        if outline:
            pg.draw.lines(surf, self.color_of_outline, True, nose_pts_screen, 2)

        tip_center_local, tip_r_m = self.create_tennis_ball()
        tip_center_screen = self._transform_points([tip_center_local], meters_to_px, camera_center, surf)[0]
        tip_radius_px = int(tip_r_m * meters_to_px)
        pg.draw.circle(surf, self.color_of_tennis_ball, tip_center_screen, tip_radius_px)
        if outline:
            pg.draw.circle(surf, self.color_of_outline, tip_center_screen, tip_radius_px, 2)

        body_pts_screen = self._transform_points(self.create_bottle(), meters_to_px, camera_center, surf)
        pg.draw.polygon(surf, self.color_of_bottle, body_pts_screen)
        if outline:
            pg.draw.lines(surf, self.color_of_outline, True, body_pts_screen, 2)

        fins_bot, fins_top = self.create_fins()
        for fin in (fins_bot, fins_top):
            fin_screen = self._transform_points(fin, meters_to_px, camera_center, surf)
            pg.draw.polygon(surf, self.color_of_fin, fin_screen)
            if outline:
                pg.draw.lines(surf, self.color_of_outline, True, fin_screen, 2)

        nx_screen_pos, ny_screen_pos = self._transform_points([self._center_nozzle()], meters_to_px, camera_center, surf)[0]
        nozzle_w_px = max(2, int(self.nozzle_d * meters_to_px))
        nozzle_h_px = max(2, int(0.55 * self.nozzle_d * meters_to_px))
        rect = pg.Rect(0, 0, nozzle_w_px, nozzle_h_px)
        rect.center = (nx_screen_pos, ny_screen_pos)
        pg.draw.ellipse(surf, self.color_of_nozzle, rect)
        if outline:
            pg.draw.ellipse(surf, self.color_of_outline, rect, 2)
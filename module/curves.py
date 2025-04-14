import numpy as np
import scipy.interpolate as si
import pygame as pg
from module.utils import world_to_screen, screen_to_world
from math import dist

def bspline(cv, degree=3, num_samples=50, spacing=50):
    """
    Generates B-spline points with fixed spacing between them.
    
    Parameters:
        cv : (N, 2) array of control vertices
        degree : Degree of the B-spline
        num_samples : Desired number of evenly spaced points
        spacing : Fixed distance between points (optional, overrides num_samples)
    
    Returns:
        Array of (num_samples, 2) evenly spaced points along the B-spline.
    """
    cv = np.asarray(cv)
    # print(f"cv: {cv}")
    count = cv.shape[0]
    degree = min(degree, count - 1)

    # Create a knot vector
    kv = np.array([0] * degree + list(range(count - degree + 1)) + [count - degree] * degree, dtype='int')

    # Uniformly sample the spline in parameter space
    n_samples = 1000  # High resolution sampling for accurate arc lengths
    u = np.linspace(0, (count - degree), n_samples)
    spline_points = np.array(si.splev(u, (kv, cv.T, degree))).T

    # Compute cumulative arc lengths
    arc_lengths = np.cumsum(np.linalg.norm(np.diff(spline_points, axis=0), axis=1))
    arc_lengths = np.insert(arc_lengths, 0, 0)  # Include the starting point

    # Determine spacing between points
    if spacing is None:
        total_length = arc_lengths[-1]
        spacing = total_length / (num_samples - 1)  # Compute uniform spacing

    # Generate fixed-spacing arc length targets
    target_arc_lengths = np.arange(0, arc_lengths[-1], spacing)

    # Interpolate u values for fixed arc length spacing
    uniform_u = np.interp(target_arc_lengths, arc_lengths, u)

    # Evaluate the B-spline at the new parameter values
    uniform_spline_points = np.array(si.splev(uniform_u, (kv, cv.T, degree))).T

    return uniform_spline_points

class Curve:
    def __init__(self, parent, next_curve, prev_curve, 
                 control_points=[[[0, 0], [0, 600]], [[600, 600], [600, 0]]]):
        self.control_points = control_points
        self.parent = parent
        self.next_curve = next_curve
        self.prev_curve = prev_curve

        self.update_curve()
    
    def update_curve(self):
        self.curve = bspline(cv=[*self.control_points[0], *self.control_points[1]], spacing=self.parent.spacing)
        self.finalize_curve()
    
    def finalize_curve(self):
        for i, control in enumerate(self.control_points):
            if i == 0:
                self.curve = np.vstack([self.curve, control[0]])
            else:
                self.curve = np.vstack([self.curve, control[1]])
    
    def draw_points(self, surf: pg.Surface, zoom, offset):
        for point in self.curve:
            pg.draw.circle(surf, (0, 255, 0), world_to_screen(point, zoom, offset), 4*zoom)

    def draw_control(self, surf: pg.Surface, zoom, offset):
        pg.draw.line(surf, (100, 100, 100), world_to_screen(self.control_points[0][0], zoom, offset), world_to_screen(self.control_points[0][1], zoom, offset), 2)
        pg.draw.line(surf, (100, 100, 100), world_to_screen(self.control_points[1][0], zoom, offset), world_to_screen(self.control_points[1][1], zoom, offset), 2)
        for i, point in enumerate([*self.control_points[0], *self.control_points[1]]):
            # print(point)
            if i == 0 or i == 3:
                pg.draw.circle(surf, (180, 0, 180), world_to_screen(point, zoom, offset), 7)
            else:
                pg.draw.circle(surf, (180, 0, 180), world_to_screen(point, zoom, offset), 4)
        
            # draw X on last control point in total curve
            if i == 3:
                if self.next_curve is None:
                    pg.draw.line(surf, (255, 255, 255), world_to_screen((point[0]+20, point[1]+20), zoom, offset), world_to_screen((point[0]-20, point[1]-20), zoom, offset))
                    pg.draw.line(surf, (255, 255, 255), world_to_screen((point[0]-20, point[1]+20), zoom, offset), world_to_screen((point[0]+20, point[1]-20), zoom, offset))
    
    def move_control(self, index, pos: list[int, int]):
        """Moves control point at index (0 or 1) to new pos. Moves handle same offset."""
        offset = [self.control_points[index][index][0] - pos[0], self.control_points[index][index][1] - pos[1]]
        self.control_points[index][index] = pos
        # offset handle to same distance
        if index == 0:
            self.control_points[0][1][0] = self.control_points[0][1][0] - offset[0]
            self.control_points[0][1][1] = self.control_points[0][1][1] - offset[1]
        else:
            self.control_points[1][0][0] = self.control_points[1][0][0] - offset[0]
            self.control_points[1][0][1] = self.control_points[1][0][1] - offset[1]

class ComplexCurve:
    """Class to handle chains of curves."""
    def __init__(self, control_points, spacing: int = 50):
        """Create a complex curve."""
        # Every 4 control points brings a new curve, with overlap on the last points.
        self.spacing = spacing

        self.curves = [Curve(self, None, None, control_points)]
        self.sim = []

        self.overlap_points = []
    
    def add_curve(self, pos):
        start_pos = self.curves[-1].control_points[1][1] # endpoint of last curve in list
        start_control = self.curves[-1].control_points[1][0]
        halfway_x = (start_pos[0] + pos[0]) // 2
        halfway_y = (start_pos[1] + pos[1]) // 2

        mirrored_vector = [start_control[0] - start_pos[0], start_control[1] - start_pos[1]]
        new_handle = [start_pos[0] - mirrored_vector[0], start_pos[1] - mirrored_vector[1]]

        points = [
            [start_pos, new_handle],
            [[halfway_x, halfway_y], [int(pos[0]), int(pos[1])]]
        ]
        self.overlap_points.append(self.curves[-1].control_points[-1][1])

        new_curve = Curve(self, None, self.curves[-1], control_points=points)
        new_curve.prev_curve.next_curve = new_curve
        self.curves.append(new_curve)
    
    def remove_curve(self, index):
        if index == len(self.curves)-1: # if we are at the end of the path
            self.curves.pop()
            self.curves[-1].next_curve = None

    def update_all_curves(self):
        for curve in self.curves:
            curve.update_curve()
    
    def finalize_all_curves(self):
        for curve in self.curves:
            curve.finalize_curve()
    
    def update_curve(self, curve: Curve):
        curve.update_curve()

    def draw(self, surf: pg.SurfaceType, zoom, offset):
        for curve in self.curves:
            curve.draw_points(surf, zoom, offset)

    def get_points(self) -> list:
        """
        Gets all points within the curves contained. No duplicates.
        """
        points = []
        nd = []
        for curve in self.curves:
            for point in curve.curve:
                points.append((round(float(point[0]), 1), round(float(point[1]), 1)))
        
        for point in points:
            if point not in nd:
                nd.append(point)

        return nd

from parapy.core import *
from parapy.geom import *
from kbeutils.geom import Naca4AirfoilCurve, Naca5AirfoilCurve
import numpy as np


class TankProfile(GeomBase):
    airfoil_name = Input()

    @Part
    def airfoil(self):
        return DynamicType(
            type=(Naca5AirfoilCurve if len(self.airfoil_name) == 5 else Naca4AirfoilCurve),
            designation=self.airfoil_name,
            hidden=True
        )

    @Attribute
    def closed_trimmed_coords(self):
        coords = np.array(self.airfoil.coordinates)
        points = np.array(self.airfoil.points)
        trimmed_coords = coords[(coords[:, 0] > 0.2) & (coords[:, 0] < 0.75)]
        trimmed_points = points[(coords[:, 0] > 0.2) & (coords[:, 0] < 0.75)]
        upper = trimmed_points[trimmed_coords[:, 2] >= 0]
        lower = trimmed_points[trimmed_coords[:, 2] < 0]
        front_spar = np.array([lower[-1], upper[0]])
        rear_spar = np.array([upper[-1], lower[0]])
        return np.vstack([front_spar, upper, rear_spar, lower[:-1]])

    @Part
    def trim_curve(self):
        return Polyline(points=[Point(x, y, z) for x, y, z in self.closed_trimmed_coords], close=True, hidden=True)

    # @Attribute
    # def scalers(self):
    #     x = (self.chord * self.scaled_factor_x if self.inner else self.chord)
    #     y = (self.chord * self.scaled_factor_y if self.inner else self.chord)
    #     z = (self.chord * self.scaled_factor_z if self.inner else self.chord)
    #     return x, y, z
    #
    # @Part
    # def profile(self):
    #     return ScaledCurve(curve_in=self.trim_curve.curve, reference_point=self.position.point, factor=self.scalers)

    # @Part
    # def profile(self):
    #     return TranslatedCurve(curve_in=self.scaled_profile, displacement=)

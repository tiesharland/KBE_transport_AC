from parapy.core import *
from parapy.geom import *
import numpy as np
from kbeutils.geom import Naca4AirfoilCurve, Naca5AirfoilCurve


class FuelTank(GeomBase):
    airfoil_name_root = Input()
    airfoil_name_tip = Input ()
    root_chord = Input()
    tip_chord = Input()

    @Part
    def root_airfoil(self):
        return DynamicType(type=(Naca5AirfoilCurve if len(self.airfoil_name_root) == 5 else Naca4AirfoilCurve),
                           designation=self.airfoil_name_root, hidden=True)

    @Part
    def tip_airfoil(self):
        return DynamicType(type=(Naca5AirfoilCurve if len(self.airfoil_name_tip) == 5 else Naca4AirfoilCurve),
                           designation=self.airfoil_name_tip, hidden=True)

    @Attribute
    def root_coords(self):
        return np.array(self.root_airfoil.coordinates)

    @Attribute
    def trimmed_root_coords(self):
        return self.root_coords[(self.root_coords[:, 0] > 0.2) & (self.root_coords[:, 0] < 0.75)]

    @Part
    def unscaled_trimmed_root(self):
        return InterpolatedCurve(points=[Point(x, y, z) for x, y, z in  self.trimmed_root_coords])

    @Part
    def trimmed_root(self):
        return ScaledCurve(curve_in=self.unscaled_trimmed_root, reference_point=self.position.point, factor=self.root_chord)






if __name__ == '__main__':
    from parapy.gui import display

    obj = FuelTank(airfoil_name_root='64318', airfoil_name_tip='64318')
    display(obj)

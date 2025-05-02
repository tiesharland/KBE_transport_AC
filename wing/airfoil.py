from parapy.core import *
from parapy.geom import *
from kbeutils.geom import Naca4AirfoilCurve, Naca5AirfoilCurve


class Airfoil(GeomBase):
    root_airfoil_name = Input()
    root_chord = Input()

    @Part
    def airfoil(self):
        return DynamicType(type=(Naca5AirfoilCurve if len(self.airfoil_name) == 5 else Naca4AirfoilCurve),
                           designation=self.airfoil_name, hidden=True)

    @Part
    def profile(self):
        return ScaledCurve(curve_in=self.airfoil, reference_point=self.position.point, factor=self.chord)


if __name__ == '__main__':
    from parapy.gui import display
    obj = Airfoil(airfoil_name='0012', chord=2)
    display(obj)
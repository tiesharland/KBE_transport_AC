from math import sqrt, radians, tan, pi
from parapy.core import *
from parapy.geom import *
from Wing.airfoil import Airfoil
from Wing.Sizing import calculate_optimal_point


class Wing(GeomBase):
    name = Input()
    mtow = Input()
    s_to = Input()
    s_landing = Input()
    h_cr = Input()
    V_cr = Input()
    A = Input()

    @Attribute
    def surface(self):
        wp, ws = calculate_optimal_point(self.s_to, self.s_landing, self.h_cr, self.V_cr, self.A)
        return self.mtow / ws

    @Attribute
    def power_required(self):
        wp, ws = calculate_optimal_point(self.s_to, self.s_landing, self.h_cr, self.V_cr, self.A)
        return self.mtow / wp

    @Attribute
    def taper_ratio(self):
        return 0.4

    @Attribute
    def span(self):
        return sqrt(self.surface * self.A)

    @Attribute
    def root_chord(self):
        return (2 * self.surface) / (1 + self.taper_ratio) * self.span

    @Attribute
    def tip_chord(self):
        return self.root_chord * self.taper_ratio




if __name__ == '__main__':
    sec = Airfoil(airfoil_name='4012', chord=1)
    from parapy.gui import display
    display(sec)
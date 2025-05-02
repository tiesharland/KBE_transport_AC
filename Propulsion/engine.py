from math import sqrt, radians, tan, pi
from parapy.core import *
from parapy.geom import *
from Wing.Sizing import calculate_optimal_point

class Engines(GeomBase):
    name = Input()
    mtow = Input()
    s_to = Input()
    s_landing = Input()
    h_cr = Input()
    V_cr = Input()
    A = Input()
    N_engines = Input()

    @Attribute
    def power_to(self):
        wp, ws = calculate_optimal_point(self.s_to, self.s_landing, self.h_cr, self.V_cr, self.A)
        return self.mtow / wp

    @Attribute
    def diameter_eng(self):
        return 0.2 * (self.power_to/1000*self.N_engines)**(0.18)

    @Attribute
    def length_eng(self):
        return 0.1 * (self.power_to/ 1000 * self.N_engines)**(0.4)

    @Attribute
    def diam_prop(self):
        return 0.55 * (self.power_to/1000 * self.N_engines)**(1/4)


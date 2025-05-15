from math import sqrt, radians, tan, pi
import numpy as np
from parapy.core import *
from parapy.geom import *
from Wing.Sizing import calculate_optimal_point


class Engines(GeomBase):
    name = Input()
    tow = Input()
    s_to = Input()
    s_landing = Input()
    h_cr = Input()
    V_cr = Input()
    A = Input()
    N_engines = Input()
    span = Input()
    Nz = Input()

    @Attribute
    def power_to(self):
        ws, wp = calculate_optimal_point(self.s_to, self.s_landing, self.h_cr, self.V_cr, self.A, plotting=False)
        return self.tow * 9.81 / wp

    @Attribute
    def diameter_eng(self):
        return 0.2 * (self.power_to/1000*self.N_engines)**(0.18)

    @Attribute
    def l_ee(self):
        return 0.1 * (self.power_to/ 1000 * self.N_engines)**(0.4)

    @Attribute
    def diam_prop(self):
        return 0.55 * (self.power_to/1000 * self.N_engines)**(1/4)

    @Attribute
    def h_ee(self):
        return 1.5 * self.diameter_eng

    @Attribute
    def w_ee(self):
        return 1.1 * self.diameter_eng

    @Attribute
    def single_mass(self):
        return 1000

    @Attribute
    def engines_mass(self):
        return self.N_engines * self.single_mass

    @Attribute
    def cg(self):
        engine_parts = self.engines
        cg_x = sum(engine.cog[0] * self.single_mass for engine in engine_parts) / self.engines_mass
        return cg_x

    @Attribute
    def pos_engine(self):
        if self.N_engines == 2:
            pos = np.array([0.35 * self.span / 2, -0.35 * self.span / 2])
        elif self.N_engines == 4:
            pos = np.array([0.4 * self.span / 2, 0.7 * self.span / 2, -0.4 * self.span / 2, -0.7 * self.span / 2])
        return pos

    @Attribute
    def class2_weight(self):
        Kng = 1     # Non-pylon-mounted nacelle
        Kp = 1.4    # propeller engine
        Ktr = 1     # non- jet thrust reverser engine
        W_ec = 2.331 * (self.single_mass/.45359) ** 0.901 * Kp * Ktr
        return 0.45359 * (0.6724 * Kng * (self.l_ee/.3048) ** 0.1 * (self.w_ee/.3048) ** 0.294 * self.Nz ** 0.119
                          * W_ec ** 0.611 * self.N_engines ** 0.984 * (self.engines.first.area /.3048**2) ** 0.224)

    @Part
    def engines(self):
        return Box(
            length=self.l_ee,
            width=self.w_ee,
            height=self.h_ee,
            position=self.position.translate(y=self.pos_engine[child.index]).rotate(z=np.deg2rad(270)),
            quantify=self.N_engines
        )



if __name__ == '__main__':
    from parapy.gui import display
    engines = Engines(mtow=70307*9.81, s_to=1093, s_landing=762, h_cr=8535, V_cr=150, A=10.1, N_engines=4,span=20)
    display(engines)




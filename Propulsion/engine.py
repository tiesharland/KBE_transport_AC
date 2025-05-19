from math import sqrt, radians, tan, pi
import numpy as np
from parapy.core import *
from parapy.geom import *

# This is the class engines used to determine and visualise the turboprop engines that are instantiated.
# The power is a result of the .Sizing tool created which determines the W/P value.
# The weight is the MTOW and the power attained is in Watts, from this power the initial sizing of the engines is done.
class Engines(GeomBase):
    tow = Input()           # Maximum take-off weight (MTOW) determined from class II weight estimation [N].
    s_to = Input()          # Take-off distance [m].
    s_landing = Input()     # Landing distance [m].
    h_cr = Input()          # Cruise altitude [m].
    V_cr = Input()          # Cruise velocity [m/s].
    A = Input()             # Aspect ratio [-].
    N_engines = Input()     # Number of engines [-].
    span = Input()          # Span of the wing [m].
    Nz = Input()            # Ultimate load factor [-].
    wp = Input()            # Power [W]

    @Attribute
    def power_to(self):
        # This evaluates the .Sizing tool calculate_optimal_point and extracts the W/P value, which in combination with the MTOW gives the power.
        return self.tow * 9.81 / self.wp

    @Attribute
    def diameter_eng(self):
        # Diameter of the engine.
        return 0.2 * (self.power_to/1000*self.N_engines)**(0.18)

    @Attribute
    def l_ee(self):
        # Length of the engine envelope including engine cowling.
        return 0.1 * (self.power_to/ 1000 * self.N_engines)**(0.4)

    @Attribute
    def diam_prop(self):
        # Diameter of the propeller.
        return 0.55 * (self.power_to/1000 * self.N_engines)**(1/4)

    @Attribute
    def h_ee(self):
        # Height of the engine envelope including engine cowling.
        return 1.5 * self.diameter_eng

    @Attribute
    def w_ee(self):
        # Width of the engine envelope including engine cowling.
        return 1.1 * self.diameter_eng

    @Attribute
    def single_mass(self):
        # Mass of a single engine, [kg], based on the Allison T56 turboprop as used by the C-130 Hercules.
        return 1000

    @Attribute
    def engines_mass(self):
        # Total engine mass [kg].
        return self.N_engines * self.single_mass
   
    @Attribute
    def cg(self):
        # Center of gravity, in the x-direction (from nose to tail), of the engine system.
        engine_parts = self.engines
        cg_x = sum(engine.cog[0] * self.single_mass for engine in engine_parts) / self.engines_mass
        return cg_x

    @Attribute
    def pos_engine(self):
        # The position of the engines along the span of the wing, this is a function of the number of engines.
        if self.N_engines == 2:
            pos = np.array([0.35 * self.span / 2, -0.35 * self.span / 2])
        elif self.N_engines == 4:
            pos = np.array([0.4 * self.span / 2, 0.7 * self.span / 2, -0.4 * self.span / 2, -0.7 * self.span / 2])
        return pos

    @Attribute
    def class2_weight(self):
        # Class II weight estimation of the engine system.
        Kng = 1     # Non-pylon-mounted nacelle.
        Kp = 1.4    # propeller engine.
        Ktr = 1     # non- jet thrust reverser engine.
        W_ec = 2.331 * (self.single_mass/.45359) ** 0.901 * Kp * Ktr
        return (0.45359 * (0.6724 * Kng * (self.l_ee/.3048) ** 0.1 * (self.w_ee/.3048) ** 0.294 * self.Nz ** 0.119
                           * W_ec ** 0.611 * self.N_engines ** 0.984 * (self.engines.first.area / .3048**2) ** 0.224)
                + self.engines_mass)

    @Part
    def engines(self):
        # This generates the box shapes of the engines.
        return Box(
            length=self.l_ee,
            width=self.w_ee,
            height=self.h_ee,
            position=self.position.translate(x=self.l_ee/2 + 0.01, y=self.pos_engine[child.index], z=self.h_ee/2).rotate(z=np.deg2rad(270)), #position
            quantify=self.N_engines,
            color=[128, 128, 128],
            centered=True
        )
    @Part
    def propellers(self):
        # Creates the propellers of the turboprop engines.
        return Circle(
            radius=self.diam_prop / 2,
            position = self.position.translate(x=self.l_ee/2, y=self.pos_engine[child.index], z=self.h_ee/2).rotate(z=np.deg2rad(270)),  #position
            color='black',
            quantify=self.N_engines)


if __name__ == '__main__':
    from parapy.gui import display
    engines = Engines(tow=70307*9.81, s_to=1093, s_landing=762, h_cr=8535, V_cr=150, A=10.1, N_engines=4, span=20)
    display(engines)




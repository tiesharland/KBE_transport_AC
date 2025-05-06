from parapy.core import *
from parapy.geom import *
import numpy as np
from Fuselage.fuselage import Fuselage
from Propulsion.engine import Engines
from Wing.wing import Wing
from Wing.airfoil import Airfoil

class Aircraft(GeomBase):
    num_crates = Input()
    num_vehicles = Input()
    num_persons = Input()
    mtow = Input()
    s_to = Input()
    s_landing = Input()
    h_cr = Input()
    V_cr = Input()
    A = Input()
    airfoil_name_root = Input()
    airfoil_name_tip = Input()
    N_engines = Input()
    root_le = Input()

    @Attribute
    def engine_attachment(self):
        return (self.wing.tip_le_offset * self.propulsion.pos_engine +
                self.wing.front_spar_position * self.wing.root_chord *
                (1 - self.propulsion.pos_engine * (1 - self.wing.taper_ratio)))

    @Part
    def fuselage(self):
        return Fuselage(pass_down='num_crates, num_vehicles, num_persons')

    @Part
    def wing(self):
        return Wing(pass_down='mtow, s_to, s_landing, h_cr, V_cr, A, airfoil_name_root, airfoil_name_tip',
                    position=self.position.translate(x=self.root_le*self.fuselage.cargo.length, z=self.fuselage.radius))


    @Part
    def propulsion(self):
        return Engines(pass_down='mtow, s_to, s_landing, h_cr, V_cr, A, N_engines', span=self.wing.span,
                       position=self.wing.position)


if __name__ == '__main__':
    from parapy.gui import display
    cargo = Aircraft(num_crates=1, num_vehicles=2, num_persons=9,
                     mtow=70307*9.81, s_to=1093, s_landing=762, h_cr=8535, V_cr=150, A=10.1, airfoil_name_root='64318', airfoil_name_tip='64412'
                     N_engines=4, root_le=0.4)
    display(cargo)

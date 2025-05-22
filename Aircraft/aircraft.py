from parapy.core import *
from parapy.geom import *
import numpy as np
from parapy.exchange.step import STEPWriter
import matplotlib.pyplot as plt
import os
import openpyxl
import wx

from Sizing.sizing import Sizing
from Fuselage.fuselage import Fuselage
from Propulsion.engine import Engines
from Wing.wing import Wing
from Tail.horizontaltail import HorizontalTail
from Tail.verticaltail import VerticalTail
from Weight_estimation.classI import ClassI
from Weight_estimation.classII import ClassII
from AVL.AVL_analysis import AVL
from Warnings_Errors.gen_warning import generate_warning


DIR = str(os.getcwd())
if not os.path.exists(DIR):
    os.makedirs(DIR)


class Aircraft(GeomBase):
    num_crates = Input()            # Number of 463L master pallets (is being called a crate) [-].
    num_vehicles = Input()          # Number of Humvee 1151 military vehicles [-].
    num_persons = Input()           # Number of military personnel being transported [-].
    R = Input()                     # Range of the aircraft [m].
    s_to = Input()                  # Take-off distance [m].
    s_landing = Input()             # Landing distance [m].
    h_cr = Input()                  # Cruise altitude [m].
    V_cr = Input()                  # Cruise velocity [m/s].
    A = Input()                     # Aspect ratio [-].
    airfoil_name_root = Input()     # Root airfoil of main wing; NACA 4- or 5-digit.
    airfoil_name_tip = Input()      # Tip airfoil of maing wing; NACA 4- or 5-digit.
    N_engines = Input()             # Number of turboprop engines [-].
    root_le = Input()               # Distance from the nose to the root leading edge of the main wing [-].
    horizontal_airfoil = Input()    # Horizontal tail airfoil; symmetric NACA 4-digit.
    vertical_airfoil = Input()      # Vertical tail airfoil; symmetric NACA 4-digit.
    AoA = Input()                   # Angle of attack in cruise conditions [°].
    Nz = Input(3)                   # Ultimate load factor [-].
    Nt = Input(2)                   # Number of fuel tanks [-].
    eff_p = Input(0.82)             # Propulsive efficiency
    ld_cr = Input(14)               # Cruise L/D, based on empirics for initial design
    W_OE = Input(None)              # Input OEW for iteration

    @Attribute
    def engine_attachment(self):
        # This calculates where the engines are attached to the wing of the aircraft.
        return (self.wing.tip_le_offset * self.propulsion.pos_engine +
                self.wing.front_spar_position * self.wing.root_chord *
                (1 - self.propulsion.pos_engine * (1 - self.wing.taper_ratio)))

    @Attribute
    def x_root_wing(self):
        # This calculates the location of the root leading edge of the main wing along the fuselage length.
        return self.root_le * self.fuselage.cargo.length

    @Attribute
    def x_lemac(self):
        # This is the x-location of the leading edge mean aerodynamic chord (LEMAC).
        return self.x_root_wing + self.wing.x_LEMAC_offset

    @Attribute
    def Lt_h(self):
        # This is the position of the horizontal tail with regards to the fuselage.
        return self.horizontaltail.X_h + self.horizontaltail.x_LEMAC_h_offset - self.x_lemac

    @Attribute
    def Lt_v(self):
        # This is the position of the vertical tail with regards to the fuselage.
        return self.verticaltail.X_v + self.verticaltail.x_LEMAC_v_offset - self.x_lemac

    @Attribute
    def Fw(self):
        return self.fuselage.radius - 0.5 * self.fuselage.tail_length * np.tan(np.deg2rad(self.fuselage.divergence_angle))

    @Attribute
    def class1(self):
        # This instantiates the Class I weight estimation.
        return ClassI(num_crates=self.num_crates, num_vehicles=self.num_vehicles, num_persons=self.num_persons,
                      R=self.R, eff_p=self.eff_p, ld_cr=self.ld_cr, W_OE=self.W_OE)#, ld_cr=self.AVL.l_over_d)

    @Attribute
    def oew(self):
        # This functions calculates the operative empty weight (OEW) followed from the Class II weight estimation.
        return sum(p.class2_weight for p in [self.wing, self.fuselage, self.propulsion, self.wing.fueltank,
                                             self.horizontaltail, self.verticaltail])

    @Attribute
    def payload_weight(self):
        return self.fuselage.cargo.mass

    @Attribute
    def zfw(self):
        return self.oew + self.payload_weight

    @Attribute
    def tow(self):
        return self.zfw + self.class1.wfuel

    # @Attribute
    # def class2(self):
    #     # This calls the Class II weight estimation class.
    #     return ClassII(W_to=self.class1.wto, Nz=self.Nz, Sw=self.wing.surface, L=self.fuselage.length, D=self.fuselage.thickness,
    #                    Sf=self.fuselage.fuselage.area, span=self.wing.span, A=self.A, taper=self.wing.taper_ratio,
    #                    Scsw=2*55*0.3048 ** 2, Lt_h=self.Lt_h, Lt_v=self.Lt_v, tc_root=self.wing.thickness_ratio, Fw=self.Fw,
    #                    span_h=self.horizontaltail.span_h, S_ht=self.horizontaltail.surface_h, Ah=self.horizontaltail.A_h,
    #                    taper_h=self.horizontaltail.taper_ratio_h, Se=114.9*.3048 ** 2, Av=self.verticaltail.A_v,
    #                    S_vt=self.verticaltail.surface_v, taper_v=self.verticaltail.taper_ratio_v,
    #                    tc_vt=self.verticaltail.thickness_ratio_v, sweep_le_v=self.verticaltail.sweep_LE_v,
    #                    ttail=0, Vi=self.wing.fueltank.outer_tank.volume, Vp=0, Vt=self.wing.fueltank.outer_tank.volume,
    #                    Nt=self.Nt, l_ee=self.propulsion.l_ee, w_ee=self.propulsion.w_ee, N_engines=self.N_engines,
    #                    W_eng=self.propulsion.single_mass)

    @Part
    def sizing(self):
        return Sizing(s_to=self.s_to, s_landing=self.s_landing, h_cr=self.h_cr, V_cr=self.V_cr, A=self.A,
                      Mff=self.class1.Mff, eff_p=self.eff_p)

    @Part
    def fuselage(self):
        # Instantiation of the fuselage class.
        return Fuselage(pass_down='num_crates, num_vehicles, num_persons', Kws_ratio=self.wing.Kws_ratio,
                        tow=self.class1.wto, Nz=self.Nz)

    @Part
    def wing(self):
        # Instantiation of the wing class, including the fuel tanks present in the wing.
        return Wing(pass_down='s_to, s_landing, h_cr, V_cr, A, airfoil_name_root, airfoil_name_tip', tow=self.class1.wto,
                    position=self.position.translate(x=self.x_root_wing, z=self.fuselage.radius), Nz=self.Nz, Nt=self.Nt,
                    fuel_weight=self.class1.wfuel, ws=self.sizing.ws_opt)

    @Part
    def propulsion(self):
        # Instantiation of the propulsion system, hence the turboprop engines.
        return Engines(pass_down='s_to, s_landing, h_cr, V_cr, A, N_engines, Nz', span=self.wing.span,
                       tow=self.class1.wto, wp=self.sizing.wp_opt,
                       position=self.wing.position.translate(x=self.propulsion.l_ee/2,
                                                             z=-self.propulsion.h_ee).rotate(z=np.deg2rad(180)))

    @Part
    def horizontaltail(self):
        # Instantiation of the horizontal tail surfaces.
        return HorizontalTail(pass_down='horizontal_airfoil', length_fuselage=self.fuselage.length, MAC=self.wing.MAC,
                              surface=self.wing.surface, span=self.wing.span, X_CG=self.cg_tail_off,
                              position=self.position.translate(x=self.horizontaltail.pos, z=self.fuselage.radius),
                              tow=self.class1.wto, Nz=self.Nz, Fw=self.Fw, Lt_h=self.Lt_h)

    @Part
    def verticaltail(self):
        # Instantiation of the vertical tail surfaces.
        return VerticalTail(pass_down='vertical_airfoil', length_fuselage=self.fuselage.length, MAC=self.wing.MAC,
                            surface=self.wing.surface, span=self.wing.span, X_CG=self.cg_tail_off,
                            position=self.position.translate(x=self.verticaltail.pos, z=self.fuselage.radius),
                            tow=self.class1.wto, Nz=self.Nz, Lt_v=self.Lt_v)

    @Part
    def AVL(self):
        # Instantiation of the Athena Vortex Lattice (AVL) method.
        return AVL(pass_down='AoA', airfoil_name_root=self.wing.airfoil_name_root,
                   root_chord=self.wing.root_chord, airfoil_name_tip=self.wing.airfoil_name_tip,
                   tip_chord=self.wing.tip_chord, tip_le_offset=self.wing.tip_le_offset,
                   surface=self.wing.surface, span=self.wing.span, MAC=self.wing.MAC, mach=self.sizing.Mach,
                   position=self.position.translate(x=self.x_root_wing, z=self.fuselage.radius))

    @Attribute
    def cg_tail_off(self):
        # This function calculates the center of gravity along the x-axis without the contribution of the empennage.
        return (((self.fuselage.cargo.cg_x * self.fuselage.cargo.mass)
                 + (self.fuselage.cg_x * self.fuselage.class2_weight) + (self.wing.cg_x * self.wing.class2_weight)
                 + (self.wing.fueltank.cg_x * self.wing.fueltank.class2_weight) +
                 (self.propulsion.class2_weight * self.propulsion.cg))
                / (self.fuselage.cargo.mass + self.fuselage.class2_weight + self.wing.class2_weight
                   + self.wing.fueltank.class2_weight + self.propulsion.class2_weight))

    @Attribute
    def cg_total(self):
        # This function calculates the center of gravity along the x-axis including the empennage, hence total aircraft.
        return (self.cg_tail_off * (self.zfw - self.horizontaltail.class2_weight - self.verticaltail.class2_weight)
                + self.horizontaltail.class2_weight * self.horizontaltail.cg_x
                + self.verticaltail.class2_weight * self.verticaltail.cg_x) / self.zfw

    @Part
    def STEP(self):
        # This function creates the .STEP files of the wing, fuselage, engines and empennage nodes.
        # The .STEP files can be visualised using a CAD programme.
        return STEPWriter(default_directory=DIR,
                          nodes=[self.wing.wing, self.fuselage.fuselage,
                                 * [self.propulsion.engines[i] for i in range(self.N_engines)],
                                 self.verticaltail.vertical_tail, self.horizontaltail.horizontal_tail])
    @Attribute
    def a_t(self):
        # The lift curve slope of the commonly used NACA 0012 horizontal tail airfoil [1/rad].
        return 5.7

    @Attribute
    def a(self):
        # The lift curve slope of the NACA 64A318 airfoil used at the root of the main wing on the Lockheed C-130 Hercules.
        return 6

    @Attribute
    def downwash(self):
        # The downwash angle (d_epsilon/d_alpha) as defined by the reference paper on longitudinal static stability from the TU Delft.
        return 0.10

    @Attribute
    def V_h(self):
        return ((self.horizontaltail.surface_h * (self.horizontaltail.X_h - self.cg_total))
                / (self.wing.surface * self.wing.MAC))

    @Attribute
    def neutralpoint(self):
        # Determination of the neutral point along the length of the fuselage.
        return (self.a_t / self.a) * self.V_h * (1 - self.downwash) * self.wing.MAC + self.x_root_wing

    @Attribute
    def stability_margin(self):
        margin = self.neutralpoint - self.cg_total
        if margin <= 0:
            head = "Aircraft is not longitudinally stable:"
            msg = (f"The center of gravity (x={self.cg_total:.2f}) should be in front of the neutral "
                   f"point(x={self.neutralpoint:.2f}). Move the wing more forward.")
            generate_warning(head, msg)
        return margin


if __name__ == '__main__':
    from parapy.gui import display
    import pandas as pd
    #
    # cargo = Aircraft(num_crates=1, num_vehicles=2, num_persons=9, R=4000000, s_to=1093, s_landing=975, h_cr=8535,
    #                  V_cr=150, A=10.1, airfoil_name_root='64318', airfoil_name_tip='64412', N_engines=4, root_le=0.4,
    #                  horizontal_airfoil='0018', vertical_airfoil='0018', AoA=2, mach=0.49, Nz=3)
    #
    # display(cargo)

    base_dir = os.path.dirname(os.path.abspath(__file__))
    excel_path = os.path.join(base_dir, "aircraft_inputs.xlsx")

    df = pd.read_excel(excel_path, header=None, skiprows=1)

    keys = df.iloc[:, 0].tolist()
    values = df.iloc[:, 1].tolist()

    inputs = {}
    for key, val in zip(keys, values):
        if key in ["airfoil_name_root", "airfoil_name_tip", "horizontal_airfoil", "vertical_airfoil"]:
            val = str(val)
            if val.endswith(".0"):
                val = val[:-2]
            inputs[key] = val.strip("'").zfill(4)
        else:
            if isinstance(val, float) and val.is_integer():
                inputs[key] = int(val)
            else:
                inputs[key] = val
    cargo = Aircraft(**inputs)
    display(cargo)

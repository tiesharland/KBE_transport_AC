from parapy.core import *
from parapy.geom import *
from math import *
from Fuselage.fuselage import Fuselage
from Propulsion.engine import Engines
from Wing.wing import Wing
from Tail.horizontaltail import HorizontalTail
from Tail.verticaltail import VerticalTail
from Weight_estimation.classI import ClassI
from Weight_estimation.classII import ClassII
from AVL.AVL_analysis import AVL
import numpy as np
from parapy.exchange.step import STEPWriter
import warnings
import os
import pandas as pd

DIR = str(os.getcwd())

if not os.path.exists(DIR):
    os.makedirs(DIR)

import os
class Aircraft(GeomBase):
    num_crates = Input()
    num_vehicles = Input()
    num_persons = Input()
    R = Input()
    s_to = Input()
    s_landing = Input()
    h_cr = Input()
    V_cr = Input()
    A = Input()
    airfoil_name_root = Input()
    airfoil_name_tip = Input()
    N_engines = Input()
    root_le = Input()
    horizontal_airfoil = Input()
    vertical_airfoil = Input()
    cl_cr = Input()
    AoA = Input()
    mach = Input()
    Nz = Input(3)

    @Attribute
    def engine_attachment(self):
        return (self.wing.tip_le_offset * self.propulsion.pos_engine +
                self.wing.front_spar_position * self.wing.root_chord *
                (1 - self.propulsion.pos_engine * (1 - self.wing.taper_ratio)))

    @Attribute
    def x_root_wing(self):
        return self.root_le*self.fuselage.cargo.length

    @Attribute
    def x_lemac(self):
        return self.x_root_wing + self.wing.x_LEMAC_offset

    @Attribute
    def Lt_h(self):
        return self.horizontaltail.X_h + self.horizontaltail.x_LEMAC_h_offset - self.x_lemac

    @Attribute
    def Lt_v(self):
        return self.verticaltail.X_v + self.verticaltail.x_LEMAC_v_offset - self.x_lemac

    @Attribute
    def Fw(self):
        return self.fuselage.radius - 0.5 * self.fuselage.tail_length * np.tan(np.deg2rad(self.fuselage.divergence_angle))

    @Attribute
    def class1(self):
        return ClassI(num_crates=self.num_crates, num_vehicles=self.num_vehicles, num_persons=self.num_persons, R=self.R)

    @Attribute
    def class2(self):
        return ClassII(W_to=self.class1.wto, Nz=self.Nz, Sw=self.wing.surface, L=self.fuselage.length, D=self.fuselage.thickness,
                       Sf=self.fuselage.fuselage.area, span=self.wing.span, A=self.A, taper=self.wing.taper_ratio,
                       Scsw=2*55*0.3048 ** 2, Lt_h=self.Lt_h, Lt_v=self.Lt_v, tc_root=self.wing.thickness_ratio, Fw=self.Fw,
                       span_h=self.horizontaltail.span_h, S_ht=self.horizontaltail.surface_h, Ah=self.horizontaltail.A_h,
                       taper_h=self.horizontaltail.taper_ratio_h, Se=114.9*.3048 ** 2, Av=self.verticaltail.A_v,
                       S_vt=self.verticaltail.surface_v, taper_v=self.verticaltail.taper_ratio_v,
                       tc_vt=self.verticaltail.thickness_ratio_v, sweep_le_v=self.verticaltail.sweep_LE_v,
                       ttail=0, Vi=self.wing.fueltank.outer_surf.volume, Vp=0, Vt=self.wing.fueltank.outer_surf.volume,
                       Nt=self.N_engines)

    # @Attribute
    # def weight(self):
    #     return Estimation(num_crates=self.num_crates, num_vehicles=self.num_vehicles, num_persons=self.num_persons,
    #                        R=self.R, A=self.A, Lt_v=self.Lt_v, Lt_h=self.Lt_h, Nz=3, surface=self.wing.surface,
    #                        length=self.fuselage.length, thickness=self.fuselage.thickness,
    #                        radius=self.fuselage.radius, Sf=self.fuselage.fuselage.area, span=self.wing.span,
    #                        taper_ratio=self.wing.taper_ratio, Scsw=2*55,
    #                        thickness_ratio=self.wing.thickness_ratio, tail_length=self.fuselage.tail_length,
    #                        divergence_angle=self.fuselage.divergence_angle, span_h=self.empennage.span_h,
    #                        surface_h=self.empennage.surface_h, A_h=self.empennage.A_h,
    #                        taper_ratio_h=self.empennage.taper_ratio_h, Se=114.9,
    #                        surface_v=self.empennage.surface_v, A_v=self.empennage.A_v,
    #                        taper_ratio_v=self.empennage.taper_ratio_v, sweep_LE_v=self.empennage.sweep_LE_v, ttail=0,
    #                        Vi=self.wing.fueltank.outer_surf.volume, Vp=0, Vt=self.wing.fueltank.outer_surf.volume, Nt=2)

    @Part
    def fuselage(self):
        return Fuselage(pass_down='num_crates, num_vehicles, num_persons', Kws_ratio=self.wing.Kws_ratio,
                        tow=self.class1.wto, Nz=self.Nz)

    @Part
    def wing(self):
        return Wing(pass_down='s_to, s_landing, h_cr, V_cr, A, airfoil_name_root, airfoil_name_tip', tow=self.class1.wto,
                    position=self.position.translate(x=self.x_root_wing, z=self.fuselage.radius), Nz=self.Nz, Nt=self.N_engines)

    @Part
    def propulsion(self):
        return Engines(pass_down='s_to, s_landing, h_cr, V_cr, A, N_engines, Nz', span=self.wing.span, tow=self.class1.wto,
                       position=self.wing.position)

    @Part
    def horizontaltail(self):
        return HorizontalTail(pass_down='horizontal_airfoil', length_fuselage=self.fuselage.length, MAC=self.wing.MAC,
                              surface=self.wing.surface, span=self.wing.span, X_CG=self.cg_tail_off,
                              position=self.position.translate(x=self.horizontaltail.X_h, z=self.fuselage.radius),
                              tow=self.class1.wto, Nz=self.Nz, Fw=self.Fw, Lt_h=self.Lt_h)

    @Part
    def verticaltail(self):
        return VerticalTail(pass_down='vertical_airfoil', length_fuselage=self.fuselage.length, MAC=self.wing.MAC,
                            surface=self.wing.surface, span=self.wing.span, X_CG=self.cg_tail_off,
                            position=self.position.translate(x=self.verticaltail.X_v, z=self.fuselage.radius),
                            tow=self.class1.wto, Nz=self.Nz, Lt_v=self.Lt_v)
    @Part
    def AVL(self):
        return AVL(pass_down='cl_cr,AoA,mach', airfoil_name_root=self.wing.airfoil_name_root,
                   root_chord=self.wing.root_chord,airfoil_name_tip = self.wing.airfoil_name_tip,
                   tip_chord=self.wing.tip_chord,tip_le_offset = self.wing.tip_le_offset,
                   surface=self.wing.surface,span = self.wing.span,MAC = self.wing.MAC,
                   position=self.position.translate(x=self.x_root_wing, z=self.fuselage.radius))

    #Add engines
    @Attribute
    def cg_tail_off(self):
        return (((self.fuselage.cargo.cg_x * self.fuselage.cargo.mass) + (self.fuselage.cg_x * self.fuselage.class2_weight)
                + (self.wing.cg_x * self.wing.class2_weight) + (self.wing.fueltank.cg_x * self.wing.fueltank.class2_weight))
                /(self.fuselage.cargo.mass + self.fuselage.class2_weight + self.wing.class2_weight + self.wing.fueltank.class2_weight))

    @Attribute
    def cg_total(self):
        return (((self.fuselage.cargo.cg_x * self.fuselage.cargo.mass) + (self.fuselage.cg_x * self.fuselage.class2_weight)
                + (self.wing.cg_x * self.wing.class2_weight) + (self.wing.fueltank.cg_x * self.wing.fueltank.class2_weight)
                + (self.horizontaltail.cg_x * self.horizontaltail.class2_weight) + (self.verticaltail.cg_x * self.verticaltail.class2_weight))
                /(self.fuselage.cargo.mass + self.fuselage.class2_weight + self.wing.class2_weight + self.wing.fueltank.class2_weight + self.verticaltail.class2_weight + self.horizontaltail.class2_weight))



    @Part
    def STEP(self):
        return STEPWriter(default_directory=DIR,
                        nodes=[self.wing.wing,
                               self.fuselage.fuselage,
                               *[self.propulsion.engines[i] for i in range(self.N_engines)],
                               self.verticaltail.vertical_tail,
                               self.horizontaltail.horizontal_tail])

    @Attribute
    def V_h(self):
        return (self.horizontaltail.surface_h * (self.horizontaltail.X_h - self.cg_total)) / (self.wing.surface * self.wing.MAC)
    #Requires accurate estimation of dcl/dalpha_ tail & dcl/dalpha_wing and depsilon/dalpha
    @Attribute
    def neutralpoint(self):
        return (1 /2 * pi) * self.V_h * (1 - 0.40) * self.wing.MAC




if __name__ == '__main__':
    from parapy.gui import display
    #
    # cargo = Aircraft(num_crates=1, num_vehicles=2, num_persons=9, R=4000000, s_to=1093, s_landing=975, h_cr=8535,
    #                  V_cr=150, A=10.1, airfoil_name_root='64318', airfoil_name_tip='64412', N_engines=4, root_le=0.4,
    #                  horizontal_airfoil='0018', vertical_airfoil='0018', cl_cr=0.4, AoA=2, mach=0.49, Nz=3)
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

from parapy.core import *
from parapy.geom import *
from Fuselage.fuselage import Fuselage
from Propulsion.engine import Engines
from Wing.wing import Wing
from Tail.tail import Tail
from Weight_estimation.estimate import Estimation
from AVL.AVL_analysis import AVL

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
    X_CG = Input()
    cl_cr = Input()
    AoA = Input()
    mach =Input()

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
    def x_root_t(self):
        return 0.75*self.fuselage.length

    @Attribute
    def Lt_h(self):
        return self.x_root_t + self.empennage.x_LEMAC_h_offset - self.x_lemac

    @Attribute
    def Lt_v(self):
        return self.x_root_t + self.empennage.x_LEMAC_v_offset - self.x_lemac

    @Attribute
    def weight(self):
        estim = Estimation(num_crates=self.num_crates, num_vehicles=self.num_vehicles, num_persons=self.num_persons,
                           R=self.R, A=self.A, Lt_v=self.Lt_v, Lt_h=self.Lt_h, Nz=3, surface=self.wing.surface,
                           length=self.fuselage.length, thickness=self.fuselage.thickness,
                           radius=self.fuselage.radius, Sf=self.fuselage.fuselage.area, span=self.wing.span,
                           taper_ratio=self.wing.taper_ratio, Scsw=2*55,
                           thickness_ratio=self.wing.thickness_ratio, tail_length=self.fuselage.tail_length,
                           divergence_angle=self.fuselage.divergence_angle, span_h=self.empennage.span_h,
                           surface_h=self.empennage.surface_h, A_h=self.empennage.A_h,
                           taper_ratio_h=self.empennage.taper_ratio_h, Se=114.9,
                           surface_v=self.empennage.surface_v, A_v=self.empennage.A_v,
                           taper_ratio_v=self.empennage.taper_ratio_v, sweep_LE_v=self.empennage.sweep_LE_v, ttail=0,
                           Vi=self.wing.fueltank.outer_surf.volume, Vp=0, Vt=self.wing.fueltank.outer_surf.volume, Nt=2)
        W_oe, W_to, W_f, W_w, W_fus, W_ht, W_vt, W_ft = estim.weight
        return W_oe, W_to, W_f, W_w, W_fus, W_ht, W_vt, W_ft, estim.converge

    @Part
    def fuselage(self):
        return Fuselage(pass_down='num_crates, num_vehicles, num_persons')

    @Part
    def wing(self):
        return Wing(pass_down='mtow, s_to, s_landing, h_cr, V_cr, A, airfoil_name_root, airfoil_name_tip',
                    position=self.position.translate(x=self.x_root_wing, z=self.fuselage.radius))

    @Part
    def propulsion(self):
        return Engines(pass_down='mtow, s_to, s_landing, h_cr, V_cr, A, N_engines', span=self.wing.span,
                       position=self.wing.position)

    @Part
    def empennage(self):
        return Tail(pass_down='horizontal_airfoil, vertical_airfoil, X_CG, x_root_t',
                    length=self.fuselage.length, MAC=self.wing.MAC, surface=self.wing.surface, span=self.wing.span,
                    position=self.position.translate(x=self.x_root_t, z=self.fuselage.radius))
    @Part
    def AVL(self):
        return AVL(pass_down='cl_cr,AoA,mach', airfoil_name_root =self.wing.airfoil_name_root,root_chord =self.wing.root_chord,airfoil_name_tip = self.wing.airfoil_name_tip,tip_chord = self.wing.tip_chord,tip_le_offset = self.wing.tip_le_offset,surface = self.wing.surface,span = self.wing.span,MAC = self.wing.MAC,
                   position=self.position.translate(x=self.x_root_wing, z=self.fuselage.radius))



if __name__ == '__main__':
    from parapy.gui import display
    cargo = Aircraft(num_crates=1, num_vehicles=2, num_persons=9, s_to=1093, R=4000000, s_landing=975, h_cr=8535, V_cr=150, A=10.1, airfoil_name_root='64318', airfoil_name_tip='64412',
                     N_engines=4, root_le=0.4, horizontal_airfoil='0018', vertical_airfoil='0018', X_CG=4)
    display(cargo)

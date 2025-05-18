from parapy.core import *
from parapy.geom import *
import numpy as np
from Weight_estimation.classI import ClassI
from Weight_estimation.classII import ClassII


class Estimation(Base):
    num_crates = Input()
    num_vehicles = Input()
    num_persons = Input()
    R = Input()
    A = Input()
    Nz = Input()
    surface = Input()
    length = Input()
    radius = Input()
    thickness = Input()
    Sf = Input()
    span = Input()
    taper_ratio = Input()
    Scsw = Input()
    Lt_v = Input()
    Lt_h = Input()
    thickness_ratio = Input()
    tail_length = Input()
    divergence_angle = Input()
    span_h = Input()
    surface_h = Input()
    A_h = Input()
    taper_ratio_h = Input()
    Se = Input()   # square feet to meters
    surface_v = Input()
    A_v = Input()
    taper_ratio_v = Input()
    sweep_LE_v = Input()
    ttail = Input()
    Vi = Input()
    Vp = Input()
    Vt = Input()
    Nt = Input()

    @Attribute
    def Fw(self):
        return self.radius - 0.5 * self.tail_length * np.tan(np.deg2rad(self.divergence_angle))

    @Attribute
    def class1(self):
        return ClassI(pass_down='num_crates, num_vehicles, num_persons, R')

    @Attribute
    def class2(self):
        return ClassII(self.class1[1], self.Nz, self.surface, self.length, self.thickness, self.Sf, self.span,
                       self.A, self.taper_ratio, self.Scsw, self.Lt_h, self.Lt_v, self.thickness_ratio, self.Fw,
                       self.span_h, self.surface_h, self.A_h, self.taper_ratio_h, self.Se, self.A_v, self.surface_v,
                       self.taper_ratio_v, self.sweep_LE_v, self.ttail, self.Vi, self.Vp, self.Vt, self.Nt, self.W_eng,
                       self.l_ee, self.w_ee, self.Num_engines, self.Sn)

    @Attribute
    def converge(self):
        c2_oew = sum(self.class2)
        return self.class1.oew - c2_oew


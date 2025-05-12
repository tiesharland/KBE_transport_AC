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


    @Attribute
    def Fw(self):
        return self.radius - 0.5 * self.tail_length * np.tan(np.deg2rad(self.divergence_angle))

    @Attribute
    def weight(self):
        W_oe, W_to, W_f = ClassI(self.num_crates, self.num_vehicles, self.num_persons, self.R)
        W_w, W_fus, W_ht, W_vt = ClassII(W_to, self.Nz, self.surface, self.length, self.thickness, self.Sf, self.span,
                                       self.A, self.taper_ratio, self.Scsw, self.Lt_h, self.Lt_v, self.thickness_ratio,
                                       self.Fw, self.span_h, self.surface_h, self.A_h, self.taper_ratio_h, self.Se,
                                       self.A_v, self.surface_v, self.taper_ratio_v, self.sweep_LE_v, self.ttail)
        return W_oe, W_to, W_f, W_w, W_fus, W_ht, W_vt




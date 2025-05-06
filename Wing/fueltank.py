from parapy.core import *
from parapy.geom import *
from Wing.wing import Wing
import numpy as np

class FuelTank(GeomBase):

    # === Inputs ===
    mtow = Input()
    s_to = Input()
    s_landing = Input()
    h_cr = Input()
    V_cr = Input()
    A = Input()
    airfoil_name_root = Input()
    airfoil_name_tip = Input()
    span = Input()
    root_le = Input()
    fuselage_length = Input()
    fuselage_radius = Input()

    @Part
    def wing(self):
        return Wing(
            mtow=self.mtow,
            s_to=self.s_to,
            s_landing=self.s_landing,
            h_cr=self.h_cr,
            V_cr=self.V_cr,
            A=self.A,
            airfoil_name_root=self.airfoil_name_root,
            airfoil_name_tip=self.airfoil_name_tip,
            position=self.position.translate(x=self.root_le * self.fuselage_length,
                                             z=self.fuselage_radius)
        )

    @Attribute
    def root_x1(self):
        return 0.2 * self.wing.root_chord

    @Attribute
    def root_x2(self):
        return 0.75 * self.wing.root_chord

    @Attribute
    def root_width(self):
        return self.root_x2 - self.root_x1

    @Attribute
    def root_height(self):
        return self.wing.thickness_root

    @Part
    def root_profile(self):
        return Rectangle(width=self.root_width,
                         length=self.root_height,
                         position=translate(self.wing.position, 'x', self.root_x1, 'z', -self.root_height/2).rotate('x', np.pi / 2))

    @Attribute
    def tip_x1(self):
        return 0.2 * self.wing.local_chord

    @Attribute
    def tip_x2(self):
        return 0.75 * self.wing.local_chord

    @Attribute
    def tip_width(self):
        return self.tip_x2 - self.tip_x1

    @Attribute
    def tip_height(self):
        return self.wing.thickness_local_chord

    @Part
    def tip_profile(self):
        return Rectangle(width=self.tip_width,
                         length=self.tip_height,
                         position=translate(self.wing.position, 'x', self.tip_x1, 'z', -self.tip_height/2, 'y', self.wing.span / 2).rotate('x', np.pi / 2))


if __name__ == '__main__':
    from parapy.gui import display

    obj = FuelTank(
        mtow=70307 * 9.81, s_to=1093, s_landing=762, h_cr=8535, V_cr=150, A=10.1,
        airfoil_name_root="64318", airfoil_name_tip="64318",
        span=40.0, root_le=0.4, fuselage_length=18.0, fuselage_radius=2.5
    )
    display(obj)

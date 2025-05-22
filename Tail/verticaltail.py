from parapy.core import *
from parapy.geom import *
from math import sqrt, radians, tan
from kbeutils.geom import Naca4AirfoilCurve
import numpy as np


class VerticalTail(GeomBase):
    vertical_airfoil = Input()
    X_CG = Input()
    MAC = Input()
    surface = Input()
    span = Input()
    vertical_tail_mass = Input()
    length_fuselage = Input()
    tow = Input()
    Lt_v = Input()
    Nz = Input()
    ttail = Input(0)

    @Part
    def vertical_tail_airfoil(self):
        return DynamicType(
            type=Naca4AirfoilCurve,
            designation=self.vertical_airfoil,
            hidden=True
        )

    @Attribute
    def A_v(self):
        return 1.5

    @Attribute
    def taper_ratio_v(self):
        return 0.5

    @Attribute
    def volume_coefficient_v(self):
        return 0.0742

    @Attribute
    def X_v(self):
        return 0.9 * self.length_fuselage

    @Attribute
    def pos(self):
        return min(self.X_v, self.length_fuselage - self.root_chord_v)

    @Attribute
    def thickness_ratio_v(self):
        return int(self.vertical_airfoil[-2:])

    @Attribute
    def sweep_LE_v(self):
        return 25

    @Attribute
    def S_wing(self):
        return self.surface

    @Attribute
    def surface_v(self):
        return (self.S_wing * self.span * self.volume_coefficient_v) / (self.X_v - self.X_CG)

    @Attribute
    def span_v(self):
        return sqrt(self.surface_v * self.A_v)

    @Attribute
    def root_chord_v(self):
        return (2 * self.surface_v) / (1 + self.taper_ratio_v) / self.span_v

    @Attribute
    def MAC_v(self):
        return 2 / 3 * self.root_chord_v * (1 + self.taper_ratio_v + self.taper_ratio_v ** 2) / (1 + self.taper_ratio_v)

    @Attribute
    def x_LEMAC_v_offset(self):
        return (self.root_chord_v - self.MAC_v) / 2

    @Attribute
    def tip_chord_v(self):
        return self.root_chord_v * self.taper_ratio_v

    @Attribute
    def tip_le_offset_v(self):
        return tan(radians(self.sweep_LE_v)) * self.span_v

    @Part
    def root_airfoil_v_untranslated(self):
        return ScaledCurve(curve_in=self.vertical_tail_airfoil, reference_point=self.position.point,
                           factor=self.root_chord_v, hidden=True)

    @Attribute
    def cg_x(self):
        return self.vertical_tail.cog[0]

    @Attribute
    def class2_weight(self):
        Kz = self.Lt_v / 0.3048 # AC radius of gyration ~lt
        sweep_vt = np.arctan((self.taper_ratio_v - 1) / (self.taper_ratio_v + 1) / 2 / self.A_v + np.tan(np.deg2rad(self.sweep_LE_v)))
        return 0.45359 * (0.0026 * (1 + (1 if self.ttail else 0)) ** 0.225 * (self.tow/ 0.45359) ** 0.556 * self.Nz ** 0.536
                          / (self.Lt_v/0.3048) ** 0.5 * (self.surface_v/.3048**2) ** 0.5 * Kz ** 0.875 / np.cos(sweep_vt) * self.A_v ** 0.35
                          / self.thickness_ratio_v ** 0.5)

    @Part
    def root_airfoil_v_translated(self):
        return TransformedCurve(
            curve_in=self.root_airfoil_v_untranslated,
            from_position=self.position,
            to_position=self.position.rotate90('x'),
            hidden=True
        )

    @Part
    def tip_airfoil_v_untranslated(self):
        return ScaledCurve(curve_in=self.vertical_tail_airfoil, reference_point=self.position.point,
                           factor=self.tip_chord_v, hidden=True)

    @Part
    def tip_airfoil_v_translated(self):
        return TransformedCurve(
            curve_in=self.tip_airfoil_v_untranslated,
            from_position=self.position,
            to_position=self.position.translate(x=self.tip_le_offset_v, z=self.span_v).rotate90('x'),
            hidden=True
        )

    @Part
    def vertical_tail(self):
        return LoftedSolid(
            profiles=[self.root_airfoil_v_translated, self.tip_airfoil_v_translated], color=[107, 142, 35]
        )

if __name__ == '__main__':
    from parapy.gui import display
    obj = VerticalTail(vertical_airfoil = '0018', X_CG = 5, length = 20, MAC = 4, surface = 200, span = 20,x_root_t=9)
    display(obj)

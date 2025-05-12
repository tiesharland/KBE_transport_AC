from parapy.core import *
from parapy.geom import *
from math import sqrt, radians, tan
from kbeutils.geom import Naca4AirfoilCurve

class Tail(GeomBase):
    horizontal_airfoil = Input()
    vertical_airfoil = Input()
    X_CG = Input()
    length = Input()
    MAC = Input()
    surface = Input()
    span = Input()
    x_root_t = Input()

    @Part
    def horizontal_tail_airfoil(self):
        return DynamicType(
            type=Naca4AirfoilCurve,
            designation=self.horizontal_airfoil,
            hidden=True
        )

    @Part
    def vertical_tail_airfoil(self):
        return DynamicType(
            type=Naca4AirfoilCurve,
            designation=self.vertical_airfoil,
            hidden=True
        )

    @Attribute
    def A_h(self):
        return 4

    @Attribute
    def taper_ratio_h(self):
        return 0.65

    @Attribute
    def volume_coefficient_h(self):
        return 1

    @Attribute
    def X_h(self):
        return self.x_root_t

    @Attribute
    def S_wing(self):
        return self.surface

    @Attribute
    def surface_h(self):
        return (self.S_wing * self.MAC * self.volume_coefficient_h) / (self.X_h - self.X_CG)

    @Attribute
    def span_h(self):
        return sqrt(self.surface_h * self.A_h)

    @Attribute
    def root_chord_h(self):
        return (2 * self.surface_h) / (1 + self.taper_ratio_h) / self.span_h

    @Attribute
    def MAC_h(self):
        return 2/3 * self.root_chord_h * (1 + self.taper_ratio_h + self.taper_ratio_h**2) / (1 + self.taper_ratio_h)

    @Attribute
    def x_LEMAC_h_offset(self):
        return (self.root_chord_h - self.MAC_h) / 2

    @Attribute
    def tip_chord_h(self):
        return self.root_chord_h * self.taper_ratio_h

    @Attribute
    def tip_le_offset_h(self):
        return 3/4 * (self.root_chord_h - self.tip_chord_h)

    @Part
    def root_airfoil_h(self):
        return ScaledCurve(curve_in=self.horizontal_tail_airfoil, reference_point=self.position.point, factor=self.root_chord_h)

    @Part
    def tip_airfoil_h_untranslated(self):
        return ScaledCurve(curve_in=self.horizontal_tail_airfoil, reference_point=self.position.point,
                           factor=self.tip_chord_h)

    @Part
    def tip_airfoil_h_translated(self):
        return TransformedCurve(
            curve_in=self.tip_airfoil_h_untranslated,
            from_position=self.position,
            to_position=self.position.translate(x=self.tip_le_offset_h,y=self.span_h/2)
        )

    @Part
    def tip_airfoil_h_translated_mirrored(self):
        return TransformedCurve(
            curve_in=self.tip_airfoil_h_untranslated,
            from_position=self.position,
            to_position=self.position.translate(x=self.tip_le_offset_h,y=self.span_h/-2)
        )

    @Part
    def horizontal_tail(self):
        return LoftedSurface(profiles=[self.tip_airfoil_h_translated_mirrored,self.root_airfoil_h, self.tip_airfoil_h_translated])

    @Attribute
    def A_v(self):
        return 1.5

    @Attribute
    def taper_ratio_v(self):
        return 0.5

    @Attribute
    def volume_coefficient_v(self):
        return 0.08

    @Attribute
    def X_v(self):
        return self.x_root_t

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
        return 2/3 * self.root_chord_v * (1 + self.taper_ratio_v + self.taper_ratio_v**2) / (1 + self.taper_ratio_v)

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
                           factor=self.root_chord_v)

    @Part
    def root_airfoil_v_translated(self):
        return TransformedCurve(
            curve_in=self.root_airfoil_v_untranslated,
            from_position=self.position,
            to_position=self.position.rotate90('x')
        )
    @Part
    def tip_airfoil_v_untranslated(self):
        return ScaledCurve(curve_in=self.vertical_tail_airfoil, reference_point=self.position.point,
                           factor=self.tip_chord_v)

    @Part
    def tip_airfoil_v_translated(self):
        return TransformedCurve(
            curve_in=self.tip_airfoil_v_untranslated,
            from_position=self.position,
            to_position=self.position.translate(x=self.tip_le_offset_v, z=self.span_v).rotate90('x')
        )

    @Part
    def vertical_tail(self):
        return LoftedSurface(
            profiles=[self.root_airfoil_v_translated,self.tip_airfoil_v_translated],
        )


if __name__ == '__main__':
    from parapy.gui import display
    obj = Tail(horizontal_airfoil='0018',vertical_airfoil='0018',X_CG=5,length=20,MAC=4,surface=200,span=20)

    display(obj)
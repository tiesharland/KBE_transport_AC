from parapy.core import *
from parapy.geom import *
import numpy as np
from kbeutils.geom import Naca4AirfoilCurve, Naca5AirfoilCurve


class FuelTank(GeomBase):
    airfoil_name_root = Input()
    airfoil_name_tip = Input()
    root_chord = Input()
    tip_chord = Input()
    span = Input()
    wall_thickness = Input()

    @Attribute
    def scaled_factor_x(self):
        return 1 - (2 * self.wall_thickness / (self.outer_surf.bbox.bounds[3] - self.outer_surf.bbox.bounds[0]))

    @Attribute
    def scaled_factor_y(self):
        return 1 - (2 * self.wall_thickness / (self.outer_surf.bbox.bounds[4] - self.outer_surf.bbox.bounds[1]))

    @Attribute
    def scaled_factor_z(self):
        return 1 - (2 * self.wall_thickness / (self.outer_surf.bbox.bounds[5] - self.outer_surf.bbox.bounds[2]))

    @Part
    def root_airfoil(self):
        return DynamicType(
            type=(Naca5AirfoilCurve if len(self.airfoil_name_root) == 5 else Naca4AirfoilCurve),
            designation=self.airfoil_name_root,
            hidden=True
        )

    @Attribute
    def closed_trimmed_coords(self):
        coords = np.array(self.root_airfoil.coordinates)
        trimmed_root_coords = coords[(coords[:, 0] > 0.2) & (coords[:, 0] < 0.75)]
        upper = trimmed_root_coords[trimmed_root_coords[:, 2] >= 0]
        lower = trimmed_root_coords[trimmed_root_coords[:, 2] < 0]
        front_spar = np.array([lower[-1], upper[0]])
        rear_spar = np.array([upper[-1], lower[0]])
        return np.vstack([front_spar, upper, rear_spar, lower[:-1]])

    @Attribute
    def root_trim_curve(self):
        return Polyline(points=[Point(x, y, z) for x, y, z in self.closed_trimmed_coords], close=True)

    # @Attribute
    # def scaled_root_coords_inner(self):
    #     return np.array([
    #         [x * self.root_chord * self.scaled_factor_x,
    #          y * self.root_chord * self.scaled_factor_y,
    #          z * self.root_chord * self.scaled_factor_z]
    #         for x, y, z in self.closed_trimmed_coords
    #     ])

    @Part
    def trimmed_root(self):
        return ScaledCurve(curve_in=self.root_trim_curve.curve,
                           factor=self.root_chord, reference_point=self.root_trim_curve.position)

    # @Attribute
    # def trimmed_root_inner_scaled(self):
    #     return Polyline(points=[Point(x, y, z) for x, y, z in self.scaled_root_coords_inner], close=True)

    @Attribute
    def trimmed_root_inner_scale(self):
        return Wire(curves_in=[ScaledCurve(curve_in=self.trimmed_root,
                           factor=(self.scaled_factor_x, self.scaled_factor_y, self.scaled_factor_z),
                           reference_point=self.position.point)])
        # return TranslatedCurve(curve_in=self.trimmed_root_inner_scaled.curve,
        #                       displacement=self.trimmed_root_inner_scaled.cog.vector_to(self.trimmed_root.center))

    @Part
    def trimmed_root_inner(self):
        return TranslatedCurve(curve_in=self.trimmed_root_inner_scale.curve,
                               displacement=self.trimmed_root_inner_scale.cog.vector_to(Wire(curves_in=[self.trimmed_root]).cog))

    @Part
    def tip_airfoil(self):
        return DynamicType(
            type=(Naca5AirfoilCurve if len(self.airfoil_name_tip) == 5 else Naca4AirfoilCurve),
            designation=self.airfoil_name_tip,
            hidden=True
        )

    @Attribute
    def closed_trimmed_coords_tip(self):
        coords = np.array(self.tip_airfoil.coordinates)
        trimmed_tip_coords = coords[(coords[:, 0] > 0.2) & (coords[:, 0] < 0.75)]
        upper_tip = trimmed_tip_coords[trimmed_tip_coords[:, 2] >= 0]
        lower_tip = trimmed_tip_coords[trimmed_tip_coords[:, 2] < 0]
        front_spar_tip = np.array([lower_tip[-1], upper_tip[0]])
        rear_spar_tip = np.array([upper_tip[-1], lower_tip[0]])
        return np.vstack([front_spar_tip, upper_tip, rear_spar_tip, lower_tip[:-1]])

    # @Attribute
    # def scaled_translated_tip_coords(self):
    #     return np.array([
    #         [x * self.tip_chord + (self.root_chord - self.tip_chord) / 4, y * self.tip_chord + self.span / 2,
    #          z * self.tip_chord]
    #         for x, y, z in self.closed_trimmed_coords_tip
    #     ])
    #
    # @Attribute
    # def scaled_translated_tip_coords_mirrored(self):
    #     return np.array([
    #         [x * self.tip_chord+(self.root_chord-self.tip_chord)/4, y * self.tip_chord - self.span / 2, z * self.tip_chord]
    #         for x, y, z in self.closed_trimmed_coords_tip
    #     ])
    #

    @Attribute
    def tip_trim_curve(self):
        return Polyline(points=[Point(x, y, z) for x, y, z in self.closed_trimmed_coords_tip], close=True)

    # @Attribute
    # def scaled_translated_tip_coords_inner(self):
    #     return np.array([
    #         [x * self.tip_chord * self.scaled_factor_x + (self.root_chord-self.tip_chord)/4,
    #          y * self.tip_chord * self.scaled_factor_y + self.span / 2,
    #          z * self.tip_chord * self.scaled_factor_z]
    #         for x, y, z in self.closed_trimmed_coords_tip
    #     ])
    #
    # @Attribute
    # def scaled_translated_tip_coords_mirrored_inner(self):
    #     return np.array([
    #         [x * self.tip_chord * self.scaled_factor_x + (self.root_chord-self.tip_chord)/4,
    #          y * self.tip_chord * self.scaled_factor_y - self.span / 2,
    #          z * self.tip_chord * self.scaled_factor_z]
    #         for x, y, z in self.closed_trimmed_coords_tip
    #     ])

    @Attribute
    def trimmed_tip(self):
        return ScaledCurve(curve_in=self.tip_trim_curve.curve, factor=self.tip_chord,
                           reference_point=self.tip_trim_curve.cog)

    # @Attribute
    # def trimmed_tip_inner(self):
    #

    @Part
    def trimmed_tip_right(self):
        return TranslatedCurve(curve_in=self.trimmed_tip,
                               displacement=Vector((self.root_chord - self.tip_chord) / 4, self.span / 2, 0))

    @Part
    def trimmed_tip_left(self):
        return TranslatedCurve(curve_in=self.trimmed_tip,
                               displacement=Vector((self.root_chord - self.tip_chord) / 4, -self.span / 2, 0))

    @Attribute
    def trimmed_tip_left_inner_scale(self):
        return Wire(curves_in=[ScaledCurve(curve_in=self.trimmed_tip_left, reference_point=self.position.point,
                                           factor=[self.scaled_factor_x, self.scaled_factor_y, self.scaled_factor_z])])

    @Attribute
    def trimmed_tip_right_inner_scale(self):
        return Wire(curves_in=[ScaledCurve(curve_in=self.trimmed_tip_right, reference_point=self.position.point,
                                           factor=[self.scaled_factor_x, self.scaled_factor_y, self.scaled_factor_z])])

    @Attribute
    def right_tip_offset(self):
        v = self.trimmed_tip_right_inner_scale.cog.vector_to(Wire(curves_in=[self.trimmed_tip_right]).cog)
        return Vector(v.x, v.y - self.wall_thickness, v.z)

    @Attribute
    def left_tip_offset(self):
        v = self.trimmed_tip_left_inner_scale.cog.vector_to(Wire(curves_in=[self.trimmed_tip_left]).cog)
        return Vector(v.x, v.y + self.wall_thickness, v.z)

    @Part
    def trimmed_tip_right_inner(self):
        return TranslatedCurve(curve_in=self.trimmed_tip_right_inner_scale.curve,
                               displacement=self.right_tip_offset)

    @Part
    def trimmed_tip_left_inner(self):
        return TranslatedCurve(curve_in=self.trimmed_tip_left_inner_scale.curve,
                               displacement=self.left_tip_offset)
    # @Part
    # def trimmed_tip_mirrored(self):
    #     return Polyline(points=[Point(x, y, z) for x, y, z in self.scaled_translated_tip_coords_mirrored], close=True)

    # @Attribute
    # def trimmed_tip_inner_scaled(self):
    #     return Polyline(points=[Point(x, y, z) for x, y, z in self.scaled_translated_tip_coords_inner], close=True)
    #
    # @Attribute
    # def trimmed_tip_mirrored_inner_scaled(self):
    #     return Polyline(points=[Point(x, y, z) for x, y, z in self.scaled_translated_tip_coords_mirrored_inner], close=True)
    #
    # @Attribute
    # def trimmed_tip_inner_edge(self):
    #     return TranslatedCurve(curve_in=self.trimmed_tip_inner_scaled.curve,
    #                            displacement=self.trimmed_tip_inner_scaled.cog.vector_to(self.trimmed_tip.cog))
    #
    # @Part
    # def trimmed_tip_inner(self):
    #     return TranslatedCurve(curve_in=self.trimmed_tip_inner_edge,
    #                            displacement=Vector(0, -self.wall_thickness, 0))
    #
    # @Attribute
    # def trimmed_tip_mirrored_inner_edge(self):
    #     return TranslatedCurve(curve_in=self.trimmed_tip_mirrored_inner_scaled.curve,
    #                            displacement=self.trimmed_tip_mirrored_inner_scaled.cog.vector_to(self.trimmed_tip_mirrored.cog))
    #
    # @Part
    # def trimmed_tip_mirrored_inner(self):
    #     return TranslatedCurve(curve_in=self.trimmed_tip_mirrored_inner_edge,
    #                            displacement=Vector(0, self.wall_thickness, 0))

    @Part
    def outer_surf(self):
        return RuledSolid(profiles=[self.trimmed_tip_left, self.trimmed_root, self.trimmed_tip_right],
                          transparency=0.4, position=self.position)

    @Part
    def inner_surf(self):
        return RuledSolid(profiles=[self.trimmed_tip_left_inner, self.trimmed_root_inner, self.trimmed_tip_right_inner],
                          transparency=0.7, position=self.position)

    @Part
    def fuel_tank(self):
        return SubtractedSolid(shape_in=self.outer_surf, tool=self.inner_surf, position=self.position)


if __name__ == '__main__':
    from parapy.gui import display
    obj = FuelTank(airfoil_name_root='64318', airfoil_name_tip='62218', root_chord=9, tip_chord=2, span=20, wall_thickness=0.05)
    display(obj)



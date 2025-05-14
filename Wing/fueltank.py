from parapy.core import *
from parapy.geom import *
from Wing.tank_profile import TankProfile


class FuelTank(GeomBase):
    airfoil_name_root = Input()
    airfoil_name_tip = Input()
    root_chord = Input()
    tip_chord = Input()
    tip_le_offset = Input()
    span = Input()
    wall_thickness = Input()

    @Attribute
    def scaled_factor_x(self):
        return 1 - (2 * self.wall_thickness / (self.root_tank.bbox.bounds[3] - self.root_tank.bbox.bounds[0]))

    @Attribute
    def scaled_factor_y(self):
        return 1 - (2 * self.wall_thickness / (self.root_tank.bbox.bounds[4] - self.root_tank.bbox.bounds[1]))

    @Attribute
    def scaled_factor_z(self):
        return 1 - (2 * self.wall_thickness / (self.root_tank.bbox.bounds[5] - self.root_tank.bbox.bounds[2]))

    @Part
    def root_profile(self):
        return TankProfile(airfoil_name=self.airfoil_name_root, position=self.position)

    @Part
    def root_tank(self):
        return ScaledCurve(curve_in=self.root_profile.trim_curve.curve, reference_point=self.position.point,
                           factor=self.root_chord)

    @Part
    def tip_profile_right(self):
        return TankProfile(airfoil_name=self.airfoil_name_tip,
                           position=self.position.translate(x=self.tip_le_offset/self.tip_chord,
                                                            y=self.span/2/self.tip_chord))

    @Part
    def tip_profile_left(self):
        return TankProfile(airfoil_name=self.airfoil_name_tip,
                           position=self.position.translate(x=self.tip_le_offset/self.tip_chord,
                                                            y=-self.span/2/self.tip_chord))

    @Part
    def tip_tank_right(self):
        return ScaledCurve(curve_in=self.tip_profile_right.trim_curve.curve, reference_point=self.position.point,
                           factor=self.tip_chord)

    @Part
    def tip_tank_left(self):
        return ScaledCurve(curve_in=self.tip_profile_left.trim_curve.curve, reference_point=self.position.point,
                           factor=self.tip_chord)

    # @Part
    # def tip_tank_right_inner(self):
    #     return ScaledCurve(curve_in=self.tip_tank_right, reference_point=self.position.point,
    #                        factor=(self.scaled_factor_x, self.scaled_factor_y, self.scaled_factor_z))
    #
    # @Part
    # def tip_tank_left_inner(self):
    #     return ScaledCurve(curve_in=self.tip_tank_left, reference_point=self.position.point,
    #                        factor=(self.scaled_factor_x, self.scaled_factor_y, self.scaled_factor_z))


    #
    # @Attribute
    # def right_tip_offset(self):
    #     v = self.trimmed_tip_right_inner_scale.cog.vector_to(Wire(curves_in=[self.trimmed_tip_right]).cog)
    #     return Vector(v.x, v.y - self.wall_thickness, v.z)
    #
    # @Attribute
    # def left_tip_offset(self):
    #     v = self.trimmed_tip_left_inner_scale.cog.vector_to(Wire(curves_in=[self.trimmed_tip_left]).cog)
    #     return Vector(v.x, v.y + self.wall_thickness, v.z)

    @Part
    def outer_surf(self):
        return RuledSolid(profiles=[self.tip_tank_left, self.root_tank, self.tip_tank_right],
                          transparency=0.4, position=self.position)

    # @Part
    # def inner_surf(self):
    #     return RuledSolid(profiles=[self.tip_tank_left_inner, self.root_tank_inner, self.tip_tank_right_inner],
    #                       transparency=0.7, position=self.position)
    #
    # @Part
    # def fuel_tank(self):
    #     return SubtractedSolid(shape_in=self.outer_surf, tool=self.inner_surf, position=self.position)


if __name__ == '__main__':
    from parapy.gui import display
    obj = FuelTank(airfoil_name_root='64318', airfoil_name_tip='62218', root_chord=9, tip_chord=2, span=20, wall_thickness=0.05)
    display(obj)



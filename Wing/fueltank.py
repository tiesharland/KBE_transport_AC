from parapy.core import *
from parapy.geom import *
from Wing.tankprofile import TankProfile
from Warnings_Errors.gen_warning import generate_warning


class FuelTank(GeomBase):
    airfoil_name_root = Input()
    airfoil_name_tip = Input()
    root_chord = Input()
    tip_chord = Input()
    tip_le_offset = Input()
    span = Input()
    wall_thickness = Input()
    fuel_weight = Input()
    Nt = Input()
    fuel_density = Input(800) # kg/m^3

    @Attribute
    def scaled_factor_x(self):
        return 1 - (2 * self.wall_thickness / (self.root_tank.bbox.bounds[3] - self.root_tank.bbox.bounds[0]))

    @Attribute
    def scaled_factor_y(self):
        return 1 - (2 * self.wall_thickness / (self.root_tank.bbox.bounds[4] - self.root_tank.bbox.bounds[1]))

    @Attribute
    def scaled_factor_z(self):
        return 1 - (2 * self.wall_thickness / (self.root_tank.bbox.bounds[5] - self.root_tank.bbox.bounds[2]))

    @Attribute
    def Vi(self):
        return self.outer_tank.volume

    @Attribute
    def Vp(self):
        return 0

    @Attribute
    def Vt(self):
        return self.Vi + self.Vp

    @Attribute
    def max_fuel_weight(self):
        return self.Vt * self.fuel_density

    @Attribute
    def class2_weight(self):
        return 0.45359 * (2.405 * (self.Vt * 264.172) ** 0.606 / (1 + self.Vi/self.Vt) * (1 + self.Vp/self.Vt) * self.Nt ** 0.5)

    @Attribute
    def fuel_volume(self):
        v = self.fuel_weight / self.fuel_density
        if v >= self.Vt:
            head = "Fuel weight too large:"
            msg = (f"The amount of fuel required ({v:.2f} m^3, or {self.fuel_weight:.2f} kg) for the given range is "
                   f"more than can fit in the tanks ({self.Vt:.2f} m^3, or {self.max_fuel_weight:.2f} kg). "
                   f"Fuel is overwritten to maximum tank capacity.")
            generate_warning(head, msg)
            v = self.Vt
        return v

    @Attribute
    def real_fuel_weight(self):
        return self.fuel_volume * self.fuel_density

    @Part
    def root_profile(self):
        return TankProfile(airfoil_name=self.airfoil_name_root, position=self.position)

    @Part
    def root_tank(self):
        return ScaledCurve(curve_in=self.root_profile.trim_curve.curve, reference_point=self.position.point,
                           factor=self.root_chord, hidden=True)

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
                           factor=self.tip_chord, hidden=True)

    @Part
    def tip_tank_left(self):
        return ScaledCurve(curve_in=self.tip_profile_left.trim_curve.curve, reference_point=self.position.point,
                           factor=self.tip_chord, hidden=True)

    @Part
    def outer_tank(self):
        return RuledSolid(profiles=[self.tip_tank_left, self.root_tank, self.tip_tank_right],
                          transparency=0.4, position=self.position, color=[128, 128, 128])

    @Attribute
    def cg_x(self):
        v_f = self.fuel_volume
        return self.outer_tank.cog[0]

if __name__ == '__main__':
    from parapy.gui import display
    obj = FuelTank(airfoil_name_root='64318', airfoil_name_tip='62218', root_chord=9, tip_chord=2, span=20, wall_thickness=0.05, Nt=4)
    display(obj)



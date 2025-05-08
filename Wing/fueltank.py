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

    @Part
    def root_airfoil(self):
        return DynamicType(
            type=(Naca5AirfoilCurve if len(self.airfoil_name_root) == 5 else Naca4AirfoilCurve),
            designation=self.airfoil_name_root,
            hidden=True
        )

    @Attribute
    def root_coords(self):
        return np.array(self.root_airfoil.coordinates)

    @Attribute
    def trimmed_root_coords(self):
        return self.root_coords[(self.root_coords[:, 0] > 0.2) & (self.root_coords[:, 0] < 0.75)]

    @Attribute
    def trimmed_upper_coords(self):
        return self.trimmed_root_coords[self.trimmed_root_coords[:, 2] >= 0]

    @Attribute
    def trimmed_lower_coords(self):
        return self.trimmed_root_coords[self.trimmed_root_coords[:, 2] < 0]

    @Attribute
    def closed_trimmed_coords(self):
        upper = self.trimmed_upper_coords
        lower = self.trimmed_lower_coords
        front_spar = np.array([lower[-1], upper[0]])
        rear_spar = np.array([upper[-1], lower[0]])
        return np.vstack([front_spar, upper, rear_spar, lower[:-1]])

    @Attribute
    def scaled_root_coords(self):
        return np.array([
            [x * self.root_chord, y * self.root_chord, z * self.root_chord]
            for x, y, z in self.closed_trimmed_coords
        ])

    @Part
    def trimmed_root(self):
        return Polyline(points=[Point(x, y, z) for x, y, z in self.scaled_root_coords], close=True)

    @Part
    def tip_airfoil(self):
        return DynamicType(
            type=(Naca5AirfoilCurve if len(self.airfoil_name_tip) == 5 else Naca4AirfoilCurve),
            designation=self.airfoil_name_tip,
            hidden=True
        )

    @Attribute
    def tip_coords(self):
        return np.array(self.tip_airfoil.coordinates)

    @Attribute
    def trimmed_tip_coords(self):
        return self.tip_coords[(self.tip_coords[:, 0] > 0.2) & (self.tip_coords[:, 0] < 0.75)]

    @Attribute
    def trimmed_upper_coords_tip(self):
        return self.trimmed_tip_coords[self.trimmed_tip_coords[:, 2] >= 0]

    @Attribute
    def trimmed_lower_coords_tip(self):
        return self.trimmed_tip_coords[self.trimmed_tip_coords[:, 2] < 0]

    @Attribute
    def closed_trimmed_coords_tip(self):
        upper_tip = self.trimmed_upper_coords_tip
        lower_tip = self.trimmed_lower_coords_tip
        front_spar_tip = np.array([lower_tip[-1], upper_tip[0]])
        rear_spar_tip = np.array([upper_tip[-1], lower_tip[0]])
        return np.vstack([front_spar_tip, upper_tip, rear_spar_tip, lower_tip[:-1]])

    @Attribute
    def scaled_translated_tip_coords(self):
        return np.array([
            [x * self.tip_chord +(self.root_chord-self.tip_chord)/4 , y * self.tip_chord + self.span / 2, z * self.tip_chord]
            for x, y, z in self.closed_trimmed_coords_tip
        ])

    @Attribute
    def scaled_translated_tip_coords_mirrored(self):
        return np.array([
            [x * self.tip_chord+(self.root_chord-self.tip_chord)/4, y * self.tip_chord - self.span / 2, z * self.tip_chord]
            for x, y, z in self.closed_trimmed_coords_tip
        ])

    @Part
    def trimmed_tip(self):
        return Polyline(points=[Point(x, y, z) for x, y, z in self.scaled_translated_tip_coords], close=True)

    @Part
    def trimmed_tip_mirrored(self):
        return Polyline(points=[Point(x, y, z) for x, y, z in self.scaled_translated_tip_coords_mirrored], close=True)

    @Part
    def fuel_tank_surface_inner(self):
        return LoftedShell(profiles=[self.trimmed_root, self.trimmed_tip])

    @Part
    def fuel_tank_surface_outer(self):
        return LoftedShell(profiles=[self.trimmed_tip_mirrored,self.trimmed_root])

    @Part
    def root_face(self):
        return Face(island=self.trimmed_root)

    @Part
    def tip_face(self):
        return Face(island=self.trimmed_tip)

    @Part
    def tip_face_mirrored(self):
        return Face(island=self.trimmed_tip_mirrored)

    @Part
    def fueltank_shell_inner(self):
        return SewnShell(built_from=[
            self.root_face,
            self.tip_face,
            self.fuel_tank_surface_inner,
        ])

    @Part
    def fueltank_shell_outer(self):
        return SewnShell(built_from=[
            self.root_face,
            self.tip_face_mirrored,
            self.fuel_tank_surface_outer,
        ])

    @Part
    def fueltank_shell(self):
        return SewnShell(built_from=[self.fueltank_shell_inner,self.fueltank_shell_outer])

    @Part
    def fuel_tank(self):
        return Solid(built_from=self.fueltank_shell,
                     color='steelblue',
                     transparency=0.2
                     )


if __name__ == '__main__':
    from parapy.gui import display
    obj = FuelTank(airfoil_name_root='64318', airfoil_name_tip='62218', root_chord=9, tip_chord=2,span=20)
    display(obj)



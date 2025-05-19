from parapy.core import *
from parapy.geom import *
from Fuselage.cargo import Cargo
from Fuselage.nosecone import NoseCone
from Fuselage.tailcone import TailCone
import numpy as np


class Fuselage(GeomBase):
    num_crates = Input()
    num_vehicles = Input()
    num_persons = Input()
    nose_fineness = Input(1.2)
    tail_fineness = Input(3)
    divergence_angle = Input(18)
    fuselage_mass = Input()
    Kws_ratio = Input()
    tow = Input()
    Nz = Input()

    @Attribute
    def nose_length(self):
        return self.nose_fineness * self.cargo.outer_radius * 2

    @Attribute
    def tail_length(self):
        return self.tail_fineness * self.cargo.outer_radius * 2

    @Attribute
    def radius(self):
        return self.cargo.outer_radius

    @Attribute
    def thickness(self):
        return self.radius - self.cargo.inner_radius

    @Attribute
    def length(self):
        return self.cargo.length + self.nosecone.length + self.tailcone.length

    @Attribute
    def tail_start(self):
        return self.cargo.length + self.nosecone.length

    @Attribute
    def fineness(self):
        return self.length / self.radius / 2

    @Attribute
    def cg_x(self):
        return self.fuselage.cog[0]

    @Attribute
    def class2_weight(self):
        Kdoor = 1.25 # 2 side cargo doors & aft clamshell door
        Klg = 1.12 # fuselage-mounted landing-gear
        Kws = self.Kws_ratio * np.tan(0) / (self.length/.3048)
        return 0.45359 * (0.3280 * Kdoor * Klg * (self.tow/ 0.45359 * self.Nz) ** 0.5 * (self.length/.3048) ** 0.25
                          * (self.fuselage.area/.3048**2) ** 0.302
                          * (1 + Kws) ** 0.4 * (self.length / self.thickness) ** 0.10)

    @Part
    def cargo(self):
        return Cargo(pass_down='num_crates, num_vehicles, num_persons',
                     position=self.position.translate(x=self.nosecone.length), nose_fineness=self.nose_fineness,
                     tail_fineness=self.tail_fineness)

    @Part
    def nosecone(self):
        return NoseCone(radius=self.radius, nose_fineness=self.nose_fineness, position=self.position)

    @Part
    def tailcone(self):
        return TailCone(radius=self.radius, tail_fineness=self.tail_fineness, divergence_angle=self.divergence_angle,
                        position=self.position.translate(x=self.tail_start))

    @Attribute
    def profiles(self):
        n = [p for p in self.nosecone.profiles]
        t = [p for p in self.tailcone.profiles]
        # if self.radius != self.cargo.outer_radius:
        #     profs = Circle(radius=self.radius, quantify=2,
        #                position=self.position.translate(x=(self.length*child.index)
        #                                                   + self.nosecone.length).rotate90('y'))
        #     c = [p for p in profs]
        # else:
        c = [p for p in self.cargo.profiles]
        return n + c + t

    @Part
    def fuselage(self):
        return RuledSolid(profiles=self.profiles,color=[107, 142, 35], mesh_deflection=0.0001)


if __name__ == "__main__":
    from parapy.gui import display
    fus = Fuselage(num_crates=2, num_vehicles=2, num_persons=9, Nz=3, tow=70307, Kws_ratio=50)
    display(fus)
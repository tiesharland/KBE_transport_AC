from parapy.core import *
from parapy.geom import *
from Fuselage.cargo import Cargo
from Fuselage.nosecone import NoseCone
from Fuselage.tailcone import TailCone


class Fuselage(GeomBase):
    num_crates = Input()
    num_vehicles = Input()
    num_persons = Input()
    nose_fineness = Input(1.2)
    tail_fineness = Input(3)
    divergence_angle = Input(18)

    @Attribute
    def nose_length(self):
        return self.nose_fineness * self.radius * 2

    @Part
    def cargo(self):
        return Cargo(pass_down='num_crates, num_vehicles, num_persons',
                     position=self.position.translate(x=self.nose_length, z=-1*self.fus_offset))

    @Attribute
    def radius(self):
        return self.cargo.minimum_circle[1]

    @Attribute
    def fus_offset(self):
        return self.cargo.minimum_circle[0]

    @Part
    def profiles(self):
        return Circle(position=self.position.translate(x=(self.cargo.total_length*child.index+self.nose_length)).rotate90('y'),
                      radius=self.radius, quantify=2)

    @Part
    def cargo_fuselage(self):
        return LoftedSurface(profiles=self.profiles, mesh_deflection=0.0001)

    @Part
    def nosecone(self):
        return NoseCone(radius=self.radius, nose_fineness=self.nose_fineness, position=self.position)

    @Part
    def tailcone(self):
        return TailCone(radius=self.radius, tail_fineness=self.tail_fineness, divergence_angle=self.divergence_angle,
                        position=self.position.translate(x=self.nose_length+self.cargo.total_length))


if __name__ == "__main__":
    from parapy.gui import display
    fus = Fuselage(num_crates=2, num_vehicles=2, num_persons=9)
    display(fus)
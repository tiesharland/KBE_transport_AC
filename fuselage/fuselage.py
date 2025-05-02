from parapy.core import *
from parapy.geom import *
from fuselage.cargo import Cargo
from fuselage.nosecone import NoseCone
from fuselage.tailcone import TailCone


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

    @Attribute
    def radius(self):
        return self.cargo.radius

    @Part
    def cargo(self):
        return Cargo(pass_down='num_crates, num_vehicles, num_persons',
                     position=self.position.translate(x=self.nosecone.length))

    @Part
    def nosecone(self):
        return NoseCone(radius=self.radius, nose_fineness=self.nose_fineness, position=self.position)

    @Part
    def tailcone(self):
        return TailCone(radius=self.radius, tail_fineness=self.tail_fineness, divergence_angle=self.divergence_angle,
                        position=self.position.translate(x=self.nosecone.length+self.cargo.length))

    @Part
    def fuselage(self):
        return SewnShell([LoftedSurface(profiles=self.nosecone.profiles, mesh_deflection=0.0001),
                          LoftedSurface(profiles=self.cargo.profiles, mesh_deflection=0.0001),
                          LoftedSurface(profiles=self.tailcone.profiles, mesh_deflection=0.0001)])


if __name__ == "__main__":
    from parapy.gui import display
    fus = Fuselage(num_crates=2, num_vehicles=2, num_persons=9)
    display(fus)
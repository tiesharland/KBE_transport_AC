from parapy.core import *
from parapy.geom import *
from kbeutils.geom import *
import numpy as np
from cargo import Cargo


class Fuselage(GeomBase):
    num_crates = Input()
    num_vehicles = Input()
    num_persons = Input()


    @Part
    def cargo(self):
        return Cargo(pass_down='num_crates, num_vehicles, num_persons', position=self.position)

    @Part
    def profiles(self):
        return Circle(position=self.position.translate(x=self.cargo.total_length*child.index, z=self.cargo.minimum_circle[0]).rotate90('y'),
                      radius=self.cargo.minimum_circle[1], quantify=2)

    @Part
    def cargo_fuselage(self):
        return LoftedSurface(profiles=self.profiles, mesh_deflection=0.0001)

    @Part
    def test(self):
        return

if __name__ == "__main__":
    from parapy.gui import display
    fus = Fuselage(num_crates=2, num_vehicles=2, num_persons=9)
    display(fus)
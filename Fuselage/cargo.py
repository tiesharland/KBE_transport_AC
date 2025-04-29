from parapy.core import *
from parapy.geom import *
from crates import Crates
from vehicle import Vehicles
from personnel import Personnel
import numpy as np
from scipy.optimize import minimize_scalar


class Cargo(GeomBase):
    name = Input("Cargo")
    num_crates: int = Input(0)
    num_persons: int = Input(0)
    num_vehicles: int = Input(0)

    @Part
    def crates(self):
        return Crates(num_crates=self.num_crates)

    @Part
    def vehicles(self):
        return Vehicles(num_vehicles=self.num_vehicles, position=self.position.translate(x=self.crates.length))

    @Part
    def personnel(self):
        return Personnel(num_persons=self.num_persons,
                         position=self.position.translate(x=self.crates.length+self.vehicles.length))

    @Attribute
    def total_length(self):
        return self.vehicles.length + self.crates.length + self.personnel.length

    @Attribute
    def max_height(self):
        return max((self.vehicles.height, self.crates.height, self.personnel.height))

    @Attribute
    def max_width(self):
        return max((self.vehicles.width, self.crates.width, self.personnel.width))

    @Attribute
    def minimum_circle(self):
        half_width = self.max_width / 2
        points = [
            (half_width, 0),
            (-half_width, 0),
            (half_width, self.max_height),
            (-half_width, self.max_height)
        ]

        def max_distance(zc):
            return max(np.sqrt(y ** 2 + (z - zc) ** 2) for (y, z) in points)

        res = minimize_scalar(max_distance, bounds=(-1000, 1000), method='bounded')
        ofset = res.x
        radius = max_distance(res.x)
        return ofset, radius


if __name__ == "__main__":
    from parapy.gui import display
    cargo = Cargo(num_crates=2, num_vehicles=2, num_persons=9)
    display(cargo)




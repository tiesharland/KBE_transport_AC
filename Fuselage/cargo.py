from parapy.core import *
from parapy.geom import *
from Fuselage.crates import Crates
from Fuselage.vehicle import Vehicles
from Fuselage.personnel import Personnel
import numpy as np
from scipy.optimize import minimize_scalar


class Cargo(GeomBase):
    name = Input("Cargo")
    num_crates: int = Input()
    num_persons: int = Input()
    num_vehicles: int = Input()
    nose_fineness: float = Input()
    tail_fineness: float = Input()

    @Attribute
    def min_length(self):
        return 1

    @Part
    def crates(self):
        return Crates(num_crates=self.num_crates, position=self.position.translate(z=self.offset))

    @Part
    def vehicles(self):
        return Vehicles(num_vehicles=self.num_vehicles, position=self.position.translate(x=self.crates.length, z=self.offset))

    @Part
    def personnel(self):
        return Personnel(num_persons=self.num_persons,
                         position=self.position.translate(x=self.crates.length+self.vehicles.length, z=self.offset))

    @Attribute
    def length(self):
        l = self.vehicles.length + self.crates.length + self.personnel.length
        return max(l, self.personnel.single_length * 5)

    @Attribute
    def height(self):
        return max(max((self.vehicles.height, self.crates.height, self.personnel.height)), self.personnel.single_height)

    @Attribute
    def width(self):
        return max(max((self.vehicles.width, self.crates.width, self.personnel.width)), self.personnel.single_width)

    @Attribute
    def minimum_circle(self):
        half_width = self.width / 2
        points = [
            (half_width, 0),
            (-half_width, 0),
            (half_width, self.height),
            (-half_width, self.height)
        ]

        def max_distance(zc):
            return max(np.sqrt(y ** 2 + (z - zc) ** 2) for (y, z) in points)

        res = minimize_scalar(max_distance, bounds=(-1000, 1000), method='bounded')
        ofset = res.x
        radius = max_distance(res.x)
        return ofset, radius

    @Attribute
    def inner_radius(self):
        return self.minimum_circle[1]

    @Attribute
    def outer_radius(self):
        r = (self.inner_radius * 1.045 * 2 + 0.084) / 2
        l = r * (self.nose_fineness + self.tail_fineness) + self.length
        if 2 * r > 0.4 * l:
            return 0.4 * l / 2
        elif 2 * r < 0.1 * l:
            return 0.1 * l / 2
        else:
            return r

    @Attribute
    def offset(self):
        return -1 * self.minimum_circle[0]

    @Part
    def profiles(self):
        return Circle(position=self.position.translate(x=(self.length*child.index)).rotate90('y'),
                      radius=self.outer_radius, quantify=2)

    @Attribute
    def mass(self):
        return self.personnel.mass + self.vehicles.mass + self.crates.mass

    @Attribute
    def cg_x(self):
        if self.mass == 0:
            return 0
        else:
            x_cg = ((self.crates.mass * self.crates.cg) + (self.vehicles.mass * self.vehicles.cg)
                    + (self.personnel.mass * self.personnel.cg)) / self.mass
            return x_cg


if __name__ == "__main__":
    from parapy.gui import display
    cargo = Cargo(num_crates=2, num_vehicles=2, num_persons=9)
    display(cargo)




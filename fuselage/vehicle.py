from parapy.core import *
from parapy.geom import *

class Vehicles(GeomBase):
        """Collection of vehicles, dimensions in [m] and masses in [kg]."""
        num_vehicles = Input()
        single_length = Input(4.93)
        single_width = Input(2.31)
        single_height = Input(1.91)
        single_mass = Input(2962)

        @Attribute
        def height(self):
            return 0 if self.num_vehicles == 0 else self.single_height

        @Attribute
        def width(self):
            return 0 if self.num_vehicles == 0 else self.single_width

        @Attribute
        def length(self):
            return 0 if self.num_vehicles == 0 else self.single_length * self.num_vehicles

        @Attribute
        def mass(self):
            return self.single_mass * self.num_vehicles

        @Part
        def vehicles(self):
            return Box(
                length=self.single_width,
                width=self.single_length,
                height=self.single_height,
                position=self.position.translate(x=self.single_length * child.index,
                                                 y=self.single_width/-2),
                quantify=self.num_vehicles
            )

if __name__ == '__main__':
    vehicle = Vehicles()
    from parapy.gui import display
    display(Vehicle)
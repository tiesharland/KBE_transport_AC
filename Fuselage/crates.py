from parapy.core import *
from parapy.geom import *


class Crates(GeomBase):
    """Collection of crates. Dimensions are in meters and masses in kilograms"""
    num_crates = Input()
    single_length = Input(2.70)
    single_width = Input(2.20)
    single_height = Input(2.44)
    single_mass = Input(4500)

    @Attribute
    def height(self):
        return 0 if self.num_crates == 0 else self.single_height

    @Attribute
    def width(self):
        return 0 if self.num_crates == 0 else self.single_width

    @Attribute
    def length(self):
        return 0 if self.num_crates == 0 else self.single_length  * self.num_crates

    @Attribute
    def mass(self):
        return self.single_mass * self.num_crates

    @Attribute
    def cg(self):
        if self.num_crates == 0:
            return 0
        else:
            crate_parts = self.crates
            x_cg = sum(crate.cog[0] * self.single_mass for crate in crate_parts) / self.mass
            return x_cg

    @Part
    def crates(self):
        return Box(
            length=self.single_width,
            width=self.single_length,
            height=self.single_height,
            position=self.position.translate(x=self.single_length * child.index,
                                             y=self.single_width/-2),
            quantify=self.num_crates
        )

if __name__ == '__main__':
    from parapy.gui import display
    obj = Crates(num_crates=2)
    display(obj)

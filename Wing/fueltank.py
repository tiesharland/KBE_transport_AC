from parapy.core import *
from parapy.geom import *
from Wing.wing import Wing
import numpy as np

class FuelTank(GeomBase):

    root_chord = Input ()
    thickness_root = Input()
    @Attribute
    def root_x1(self):
        return 0.2 * self.root_chord

    @Attribute
    def root_x2(self):
        return 0.75 * self.root_chord

    @Attribute
    def root_width(self):
        return self.root_x2 - self.root_x1

    @Attribute
    def root_height(self):
        return self.thickness_root

    @Part
    def root_profile(self):
        return Rectangle(width=self.root_width,
                         length=self.root_height,
                         position=self.position.translate(x = 0.2 * self.root_chord).rotate('x', np.pi / 2))


if __name__ == '__main__':
    from parapy.gui import display

    obj = FuelTank(root_chord=9, thickness_root=2)
    display(obj)

from parapy.core import *
from parapy.geom import *
import numpy as np


class TailCone(GeomBase):
    radius = Input()
    tail_fineness = Input()
    divergence_angle = Input()

    @Attribute
    def length(self):
        return self.radius * 2 * self.tail_fineness

    @Attribute
    def end_offset(self):
        return 0.5 * self.length * np.tan(np.deg2rad(self.divergence_angle))

    @Attribute
    def end_radius(self):
        return self.radius - self.end_offset

    @Part
    def profiles(self):
        return Circle(quantify=2, radius=[self.radius, self.end_radius][child.index],
                      position=self.position.translate(x=child.index*self.length,
                                                       z=child.index*self.end_offset).rotate90('y'))


if __name__ == "__main__":
    from parapy.gui import display
    cone = TailCone(radius=6, tail_fineness=3, divergence_angle=17)
    display(cone)

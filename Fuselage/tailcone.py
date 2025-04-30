from parapy.core import *
from parapy.geom import *


class TailCone(GeomBase):
    radius = Input()
    tail_fineness = Input()
    upsweep_angle = Input()

    @Attribute
    def tail_length(self):
        return self.radius * 2 * self.tail_fineness






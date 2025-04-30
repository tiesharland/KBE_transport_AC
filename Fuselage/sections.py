from parapy.core import *
from parapy.geom import *


class Sections(GeomBase):
    nose_fineness = Input()
    tail_fineness = Input()
    upsweep_angle = Input()
    length_tail = Input()
    length_cp = Input(4)
    overnose_angle = Input(17)
    overside_angle = Input(35)

from parapy.core import *
from parapy.geom import *
from Wing.wing import Wing


class Tail(GeomBase):
    horizontal_airfoil = Input()
    vertical_airfoil = Input()

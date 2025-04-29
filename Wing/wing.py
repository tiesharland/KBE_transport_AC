from math import sqrt, radians, tan, pi
from parapy.core import *
from parapy.geom import *
from Wing import Section


class Wing(GeomBase):
    name = Input()


if __name__ == '__main__':
    sec = Section(airfoil_name='4012', chord=1)
    from parapy.gui import display
    display(sec)
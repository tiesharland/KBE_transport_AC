from parapy.core import *
from parapy.geom import *
from Aircraft.aircraft import Aircraft


class Design(GeomBase):
    num_crates = Input()
    num_vehicles = Input()
    num_persons = Input()
    R = Input()
    s_to = Input()
    s_landing = Input()
    h_cr = Input()
    V_cr = Input()
    A = Input()
    airfoil_name_root = Input()
    airfoil_name_tip = Input()
    N_engines = Input()
    root_le = Input()
    horizontal_airfoil = Input()
    vertical_airfoil = Input()
    AoA = Input()
    mach = Input()
    Nz = Input(3)

    @Attribute
    def weight_iteration(self):
        ac = Aircraft(pass_down='num_crates, num_vehicles, num_persons, R, s_to, s_landing, h_cr, V_cr, A, '
                                'airfoil_name_root, airfoil_name_tip, N_engines, root_le, horizontal_airfoil, '
                                'vertical_airfoil, cl_cr, AoA, mach, Nz')
        oew = ac.oew


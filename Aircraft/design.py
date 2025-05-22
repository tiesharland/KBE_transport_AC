from parapy.core import *
from parapy.geom import *
from Aircraft.aircraft import Aircraft


class Design(GeomBase):
    num_crates = Input()  # Number of 463L master pallets (is being called a crate) [-].
    num_vehicles = Input()  # Number of Humvee 1151 military vehicles [-].
    num_persons = Input()  # Number of military personnel being transported [-].
    R = Input()  # Range of the aircraft [m].
    s_to = Input()  # Take-off distance [m].
    s_landing = Input()  # Landing distance [m].
    h_cr = Input()  # Cruise altitude [m].
    V_cr = Input()  # Cruise velocity [m/s].
    A = Input()  # Aspect ratio [-].
    airfoil_name_root = Input()  # Root airfoil of main wing; NACA 4- or 5-digit.
    airfoil_name_tip = Input()  # Tip airfoil of maing wing; NACA 4- or 5-digit.
    N_engines = Input()  # Number of turboprop engines [-].
    root_le = Input()  # Distance from the nose to the root leading edge of the main wing [-].
    horizontal_airfoil = Input()  # Horizontal tail airfoil; symmetric NACA 4-digit.
    vertical_airfoil = Input()  # Vertical tail airfoil; symmetric NACA 4-digit.
    AoA = Input()  # Angle of attack in cruise conditions [°].
    Nz = Input()  # Ultimate load factor [-].
    Nt = Input()  # Number of fuel tanks [-].
    eff_p = Input()  # Propulsive efficiency

    @Attribute
    def old_design(self):
        return Aircraft(num_crates=self.num_crates, num_vehicles=self.num_vehicles, num_persons=self.num_persons,
                        R=self.R, s_to=self.s_to, s_landing=self.s_landing, h_cr=self.h_cr, V_cr=self.V_cr, A=self.A,
                        airfoil_name_root=self.airfoil_name_root, airfoil_name_tip=self.airfoil_name_tip,
                        N_engines=self.N_engines, root_le=self.root_le, horizontal_airfoil=self.horizontal_airfoil,
                        vertical_airfoil=self.vertical_airfoil, AoA=self.AoA, Nz=self.Nz, Nt=self.Nt, eff_p=self.eff_p,
                        W_OE=None, ld_cr=14)

    @Attribute
    def iteration(self):
        old_oew_2 = self.old_design.oew
        old_oew_1 = self.old_design.class1.oew
        old_ld_cr = self.old_design.AVL.l_over_d
        while abs(old_oew_2 - old_oew_1) / old_oew_1 > 0.001:
            ac = Aircraft(num_crates=self.num_crates, num_vehicles=self.num_vehicles, num_persons=self.num_persons,
                          R=self.R, s_to=self.s_to, s_landing=self.s_landing, h_cr=self.h_cr, V_cr=self.V_cr, A=self.A,
                          airfoil_name_root=self.airfoil_name_root, airfoil_name_tip=self.airfoil_name_tip,
                          N_engines=self.N_engines, root_le=self.root_le, horizontal_airfoil=self.horizontal_airfoil,
                          vertical_airfoil=self.vertical_airfoil, AoA=self.AoA, Nz=self.Nz, Nt=self.Nt,
                          eff_p=self.eff_p, W_OE=old_oew_2, ld_cr=old_ld_cr)
            old_oew_2 = ac.oew
            old_oew_1 = ac.class1.oew
            old_ld_cr = ac.AVL.l_over_d
        return old_oew_2, old_oew_1, old_ld_cr

    @Part
    def aircraft(self):
        return Aircraft(num_crates=self.num_crates, num_vehicles=self.num_vehicles, num_persons=self.num_persons,
                        R=self.R, s_to=self.s_to, s_landing=self.s_landing, h_cr=self.h_cr, V_cr=self.V_cr, A=self.A,
                        airfoil_name_root=self.airfoil_name_root, airfoil_name_tip=self.airfoil_name_tip,
                        N_engines=self.N_engines, root_le=self.root_le, horizontal_airfoil=self.horizontal_airfoil,
                        vertical_airfoil=self.vertical_airfoil, AoA=self.AoA, Nz=self.Nz, Nt=self.Nt, eff_p=self.eff_p,
                        W_OE=self.iteration[0], ld_cr=self.iteration[2])

    @Attribute
    def stability_margin(self):
        return self.aircraft.stability_margin



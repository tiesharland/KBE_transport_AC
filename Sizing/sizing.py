from parapy.core import *
from parapy.geom import *
from math import *
import numpy as np
from shapely.geometry import LineString


# This function will calculate the design point resulting from the wing-loading versus power-loading diagram
# The function takes as inputs s_to = take-off distance [m], s_landing = landing distance [m],
# h_cr = cruise altitude [m], V_cr = cruise velocity [m/s], A = aspect ratio [-],Mff = fuel fraction [-] and eff_p = propulsive efficiency [-]
# The weight defined in the calculations below (W) is the maximum take-off weight (MTOW).

class Sizing(Base):
    s_to = Input()
    s_landing = Input()
    h_cr = Input()
    V_cr = Input()
    A = Input()
    Mff = Input()
    eff_p = Input()

    #Constants assumed from values presented in Informal Knowledge Model
    @Attribute
    def CL_max(self):
        return np.array([1.5, 1.9, 2.4])  # clean, TO, landing [-]

    @Attribute
    def rho_SL(self):
        return 1.225  # Density at sea-level [kg/m^3]

    #Stall speed
    @Attribute
    def V_s(self):
        return 52  # [m/s] from C130 datasheet

    @Attribute
    def sigma(self):
        return 1  # density ratio = 1 as the runway is considered to be at sea-level,

    #Sigma = rho / rho_SL, however for stall it can be assumed that this occurs at sea-level conditions


    # f = 0.84 #Average fuel fraction (f = W_L/W_TO) as taken from Aerospace Design and Systems Engineering Elements I – AE1222-II slides

    @Attribute
    def CD0(self):
        return 0.035 # Zero lift drag coefficient

    @Attribute
    def e(self):
        return 0.9 # Oswald efficiency factor

    @Attribute
    # Stall speed W/S computation
    def stall_speed(self):
        # Stall requirement function is driven by the three CL_max values that are defined
        # Stall is heavily depending on the wing configuration, hence chosen CL
        x = 0.5 * self.rho_SL * self.V_s ** 2 * self.CL_max
        return x    # Clean, TO, landing

    @Attribute
    def TOP(self):
        # In order to solve for the take-off parameter (TOP) the quadratic equation:
        # sTO= 0.0577 * TOP^2prop + 8.6726 * TOPprop has to be solved
        # Simple quadratic root solver that only takes the positive real root, as the negative real root is non-physical
        def solve_positive_root(a, b, c):
            discriminant = b ** 2 - 4 * a * (-c)
            if discriminant < 0:
                return "No real solution"
            sqrt_disc = np.sqrt(discriminant)
            x1 = (-b + sqrt_disc) / (2 * a)
            x2 = (-b - sqrt_disc) / (2 * a)
            for x in [x1, x2]:
                if x > 0:
                    return x
            return "No positive solution"

        return solve_positive_root(0.0577, 8.6726, (self.s_to / 0.3048))

    #Take-off equation using the CL_max for take-off configuration, the calculated TOP and the density ratio sigma
    @Attribute
    def take_off(self):
        # Take-off requirement function
        x = np.arange(1,7000, 10)
        y = (self.TOP / x) * self.CL_max[1] / (1.1 ** 2) * self.sigma
        return x, y

    # The landing equation using the CL_max for landing configuration, density at sea-level,
    # the landing distance and the fuel fraction
    @Attribute
    def landing(self):
        # Landing requirement function
        x = (self.CL_max[2] * self.rho_SL * self.s_landing / 0.5847) / (2 * self.Mff)
        return x

    #This function calculates the so-called ISA standard atmosphere density and temperature at a specified cruise altitude
    @Attribute
    def isa_density(self):
        # Constant values for the ISA standard atmosphere calculations
        T0 = 288.15  # Sea-level standard temperature [K]
        L = 0.0065  # Temperature lapse rate [K/m]
        g0 = 9.80665  # Gravitational acceleration [m/s^2]
        R = 287.058  # Specific gas constant for air [J/kg K]
        rho_SL = 1.225 #Sea-level density [kg/m^3]

        #The above lapse rate is only defined until the tropopause, hence between 0 and 11000 meters
        if self.h_cr < 0 or self.h_cr > 11000:
            raise ValueError("Altitude must be within 0–11000 meters.")
        T = T0 - L * self.h_cr
        rho = ((1 + (L * self.h_cr / T0)) ** - (g0 / (R * L) + 1) ) * rho_SL

        return rho, T

    #Denstiy at cruise altitude (h_cr)
    @Attribute
    def rho(self):
        return self.isa_density[0]

    #Temperature at cruise altitude (T)
    @Attribute
    def T(self):
        return self.isa_density[1]

    #This function calculates the cruise W/S and W/P
    @Attribute
    def cruise(self):
        # Cruise requirement function
        x = np.arange(1, 7000, 10)
        term1 = (self.CD0 * 0.5 * self.rho * self.V_cr ** 3) / x
        term2 = (x / (np.pi * self.A * e)) * (1 / (0.5 * self.rho * self.V_cr))
        y = self.eff_p * (self.rho / self.rho_SL) ** (3 / 4) * (term1 + term2) ** (-1)
        return x, y

    #This function calculates the Mach number at cruise altitude
    @Attribute
    def Mach(self):
        gamma = 1.4 # Ratio of specific heats for air [-]
        R = 287 # Specific gas constant for air [J/kg K]
        a = np.sqrt(gamma * R * self.T) #Speed of sound [m/s]
        M = self.V_cr/a # Mach number [-]
        return M

    #This function determines the optimal design point (W/S & W/P) which is the most topright point in the feasible design space
    #First the vertical limit is determined from the three stall and landing requirement
    #The cruise and take-off requirement are curves intersecting the vertical limits forming a feasible design region
    #The optimal design point is chosen by the highest possible y-value intersection
    @Attribute
    def design_point(self):
        vertical_limit = np.min([self.stall_speed[0], self.stall_speed[1], self.stall_speed[2], self.landing])
        vertical_line = LineString(np.column_stack((vertical_limit * np.ones(1000), np.linspace(0, 0.40, 1000))))
        cruise_line = LineString(np.column_stack((self.cruise[0], self.cruise[1])))
        to_line = LineString(np.column_stack((self.take_off[0], self.take_off[1])))
        cruise_intersect = cruise_line.intersection(vertical_line)
        to_intersect = to_line.intersection(vertical_line)
        y_opt = np.min((cruise_intersect.y, to_intersect.y))
        return vertical_limit, y_opt

    @Attribute
    def ws_opt(self):
        return self.design_point[0]

    @Attribute
    def wp_opt(self):
        return self.design_point[1]


if __name__ == "__main__":
    Sizing(s_to=1093, s_landing=762, h_cr=8535, V_cr=150, A=10.1)
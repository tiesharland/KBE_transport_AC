from typing import Any

from parapy.core import *
from parapy.geom import *
from math import *
import numpy as np

import matplotlib
matplotlib.use('TkAgg')  # or 'Qt5Agg' if you have it
import matplotlib.pyplot as plt
from shapely.geometry import LineString

#This function will calculate the design point resulting from the wing-loading versus power-loading diagram
#The function takes as inputs s_TO = take-off distance [m], s_landing = landing distance [m], h_cr = cruise altitude [m], V_cr = cruise velocity [m/s]
#A = aspect ratio [-], the weight defined in the calculations below (W) is the maximum take-off weight (MTOW)
def calculate_optimal_point(s_TO: int, s_landing: int, h_cr: int, V_cr: int,
                            A: int, plotting: int = True) -> tuple[float, float]:

    #Constants assumed from values presented in Informal Knowledge Model
    CL_max = [1.5, 1.9, 2.4]  #clean, TO, landing [-]
    rho_SL = 1.225  #Density at sea-level [kg/m^3]
    #Stall speed
    V_s = 52  # [m/s] from C130 datasheet
    sigma = 1  # density ratio = 1 as the runway is considered to be at sea-level,
    #Sigma = rho / rho_SL, however for stall it can be assumed that this occurs at sea-level conditions
    f = 0.84 #Average fuel fraction (f = W_L/W_TO) as taken from Aerospace Design and Systems Engineering Elements I – AE1222-II slides

    CD0 = 0.035 #Zero lift drag coefficient
    e = 0.9 #Oswald efficiency factor
    eta_p = 0.82 #Propulsive efficiency


    # Stall speed W/S computation
    def stall_speed(CL_max):
        x = 0.5 * rho_SL * V_s**2 * CL_max
        return x
    #In order to solve for the take-off parameter (TOP) the quadratic equation: sTO= 0.0577 * TOP^2prop + 8.6726 * TOPprop has to be solved
    #Simple quadratic root solver that only takes the positive real root, as the negative real root is non-physical
    def solve_positive_root(a, b, c):
        discriminant = b**2 - 4 * a * (-c)
        if discriminant < 0:
            return "No real solution"
        sqrt_disc = np.sqrt(discriminant)
        x1 = (-b + sqrt_disc) / (2 * a)
        x2 = (-b - sqrt_disc) / (2 * a)
        for x in [x1, x2]:
            if x > 0:
                return x
        return "No positive solution"

    TOP = solve_positive_root(0.0577, 8.6726, (s_TO/0.3048))
    #Take-off equation using the CL_max for take-off configuration, the calculated TOP and the density ratio sigma
    def take_off(CL_max_TO, TOP, sigma):
        x = np.arange(1,7000, 10)
        y = (TOP / x) * CL_max_TO * sigma
        return x, y

    #The landing equation using the CL_max for landing configuration, density at sea-level, the landing distance and the fuel fraction
    def landing(CL_max_landing, rho_SL, s_landing,f):
        x = (CL_max_landing * rho_SL * s_landing/0.5915)/(2*f)
        return x

    #This function calculates the so-called ISA standard atmosphere density and temperature at a specified cruise altitude
    def isa_density(h_cr):
        # Constant values for the ISA standard atmosphere calculations
        T0 = 288.15  # Sea-level standard temperature [K]
        L = 0.0065  # Temperature lapse rate [K/m]
        g0 = 9.80665  # Gravitational acceleration [m/s^2]
        R = 287.058  # Specific gas constant for air [J/kg K]
        rho_SL = 1.225 #Sea-level density [kg/m^3]

        #The above lapse rate is only defined until the tropopause, hence between 0 and 11000 meters
        if h_cr < 0 or h_cr > 11000:
            raise ValueError("Altitude must be within 0–11000 meters.")
        T = T0 - L * h_cr
        rho = ((1 + (L * h_cr / T0)) ** - (g0 / (R * L) + 1) ) * rho_SL

        return rho,T
    #Denstiy at cruise altitude (h_cr)
    rho = isa_density(h_cr)[0]
    #Temperature at cruise altitude (T)
    T = isa_density(h_cr)[1]
    #This function calculates the cruise W/S and W/P
    def cruise(CD0, A, e, eta_p, rho, V_cr, rho_SL):
        x = np.arange(1, 7000, 10)
        term1 = (CD0 * 0.5 * rho * V_cr ** 3) / x
        term2 = (x / (np.pi * A * e)) * (1 / (0.5 * rho * V_cr))
        y = eta_p * (rho / rho_SL) ** (3 / 4) * (term1 + term2) ** (-1)
        return x, y

    #This function calculates the Mach number at cruise altitude
    def Mach(V_cr,T):
        gamma = 1.4 # Ratio of specific heats for air [-]
        R = 287 # Specific gas constant for air [J/kg K]
        a = np.sqrt(gamma * R * T) #Speed of sound [m/s]
        M = V_cr/a #Mach number [-]
        return M

    #Take-off requirement function
    x_to, y_to = take_off((CL_max[1]/(1.1**2)), TOP, sigma)
    #Stall requirement function is driven by the three CL_max values that are defined
    #Stall is heavily depending on the wing configuration, hence chosen CL
    ws_stall_clean = stall_speed(CL_max[0])
    ws_stall_TO = stall_speed(CL_max[1])
    ws_stall_landing = stall_speed(CL_max[2])
    #Landing requirement function
    ws_landing = landing(CL_max[2], rho_SL, s_landing, f)
    #Cruise requirement function
    x_cr, y_cr = cruise(CD0,A,e,eta_p,rho,V_cr,rho_SL)

    #This function determines the optimal design point (W/S & W/P) which is the most topright point in the feasible design space
    #First the vertical limit is determined from the three stall and landing requirement
    #The cruise and take-off requirement are curves intersecting the vertical limits forming a feasible design region
    #The optimal design point is chosen by the highest possible y-value intersection
    def design_point(ws_stall_clean, ws_stall_TO, ws_stall_landing, ws_landing,x_cr,y_cr,x_to,y_to):
        vertical_limit = np.min([ws_stall_clean, ws_stall_TO, ws_stall_landing, ws_landing])
        vertical_line = LineString(np.column_stack((vertical_limit * np.ones(1000), np.linspace(0, 0.40, 1000))))
        cruise_line = LineString(np.column_stack((x_cr, y_cr)))
        to_line = LineString(np.column_stack((x_to, y_to)))
        cruise_intersect = cruise_line.intersection(vertical_line)
        to_intersect = to_line.intersection(vertical_line)
        y_opt = np.min((cruise_intersect.y, to_intersect.y))
        return vertical_limit, y_opt

    vertical_limit, y_opt = design_point(ws_stall_clean, ws_stall_TO, ws_stall_landing, ws_landing, x_cr, y_cr, x_to, y_to)
    #This allows whether the user wants to visualise the generated W/S vs W/P plot or not
    if plotting:
        plt.plot(x_to, y_to, label='Take-off Constraint', color='blue')
        plt.axvline(ws_stall_clean, color='red', linestyle='--', label=f'Stall (CLmax={CL_max[0]})')
        plt.axvline(ws_stall_TO, color='orange', linestyle='--', label=f'Stall (CLmax={CL_max[1]})')
        plt.axvline(ws_stall_landing, color='purple', linestyle='--', label=f'Stall (CLmax={CL_max[2]})')
        plt.axvline(ws_landing, color='green', linestyle='--', label='Landing Constraint')
        plt.plot(x_cr, y_cr, label='Cruise Constraint', color='red')
        plt.scatter(vertical_limit, y_opt, marker='*', s=200, color='black')
        plt.xlabel('W/S')
        plt.ylabel('W/P')
        plt.title('Constraint Diagram')
        plt.ylim(0, 0.4)
        plt.grid(True)
        plt.legend()
        plt.show()


        print(f"Optimal W/S ={vertical_limit}")
        print(f"Optimal W/P ={y_opt}")

    return vertical_limit, y_opt


if __name__ == "__main__":
    calculate_optimal_point(s_TO=1093, s_landing=762, h_cr=8535, V_cr=150, A=10.1, plotting = True)
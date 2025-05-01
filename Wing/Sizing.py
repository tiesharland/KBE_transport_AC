from parapy.core import *
from parapy.geom import *
from math import *
import numpy as np

import matplotlib
matplotlib.use('TkAgg')  # or 'Qt5Agg' if you have it
import matplotlib.pyplot as plt


#Assumed constants
CL_max = [1.5, 1.9, 2.4]  # clean, TO, landing
rho_SL = 1.225
#Stall speed
V_s = 52  # m/s
sigma = 1  # density ratio
#Take-off distance
s_TO = 914  # m
#Landing distance
s_landing = 762  # m
#Fuel fraction
f = 0.84 #From slides
#Cruise conditions
h_cr = 8535 #[m]
CD0 =0.0280 #This is incorrect for now
A = 10.1
e = 0.75 #Incorrect
eta_p = 0.9 #Incorrect
V_cr = 150



# Stall speed W/S computation
def stall_speed(CL_max):
    x = 0.5 * rho_SL * V_s**2 * CL_max
    return x

def solve_positive_root(a, b, c):
    discriminant = b**2 - 4 * a * (-c)
    if discriminant < 0:
        return "No real solution"
    sqrt_disc = np.sqrt(discriminant)  # FIXED
    x1 = (-b + sqrt_disc) / (2 * a)
    x2 = (-b - sqrt_disc) / (2 * a)
    for x in [x1, x2]:
        if x > 0:
            return x
    return "No positive solution"

TOP = solve_positive_root(0.0577, 8.6726, (s_TO/0.3048))
def take_off(CL_max_TO, TOP, sigma):
    x = np.arange(1,7000, 10)
    y = (TOP / x) * CL_max_TO * sigma
    return x, y


def landing(CL_max_landing, rho_SL, s_landing,f):
    x = (CL_max_landing * rho_SL * s_landing/0.5915)/2*f
    return x


def isa_density(h_cr):
    # Constants
    T0 = 288.15  # Sea level standard temperature [K]
    L = 0.0065  # Temperature lapse rate [K/m]
    g0 = 9.80665  # Gravitational acceleration [m/s²]
    R = 287.058  # Specific gas constant for dry air [J/kg·K]
    rho_SL = 1.225

    if h_cr < 0 or h_cr > 11000:
        raise ValueError("Altitude must be within 0–11000 meters.")

    rho = ((1 + (L * h_cr / T0)) ** - (g0 / (R * L) + 1) ) * rho_SL

    return rho

rho = isa_density(h_cr)
def cruise(CD0, A, e, eta_p, rho, V_cr, rho_SL):
    x = np.arange(100, 7000, 10)

    term1 = (CD0 * 1/2 * rho * V_cr**3)/x
    term2 = x/ (np.pi * A * e *1/2 * rho * V_cr)
    bracket_term = term1 + term2

    y = eta_p * (rho / rho_SL)**(3/4) * (1 / bracket_term)
    return x, y

#Take off requirement
x_to, y_to = take_off((CL_max[1]/1.1**2), TOP, sigma)
#Stall requirement
ws_stall_clean = stall_speed(CL_max[0])
ws_stall_TO = stall_speed(CL_max[1])
ws_stall_landing = stall_speed(CL_max[2])
#Landing requirement
ws_landing = landing(CL_max[2], rho_SL, s_landing, f)
#Cruise requirement
x_cr, y_cr = cruise(CD0,A,e,eta_p,rho,V_cr,rho_SL)


plt.plot(x_to, y_to, label='Take-off Constraint', color='blue')
plt.axvline(ws_stall_clean, color='red', linestyle='--', label=f'Stall (CLmax={CL_max[0]})')
plt.axvline(ws_stall_TO, color='orange', linestyle='--', label=f'Stall (CLmax={CL_max[1]})')
plt.axvline(ws_stall_landing, color='purple', linestyle='--', label=f'Stall (CLmax={CL_max[2]})')
plt.axvline(ws_landing, color='green', linestyle='--', label='Landing Constraint')
plt.plot(x_cr, y_cr, label='Cruise Constraint', color='red')


plt.xlabel('W/S')
plt.ylabel('W/P')
plt.title('Constraint Diagram')
plt.ylim(0, 0.4)
plt.grid(True)
plt.legend()
plt.show()


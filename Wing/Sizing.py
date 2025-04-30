from parapy.core import *
from parapy.geom import *
from math import *
import numpy as np

import matplotlib
matplotlib.use('TkAgg')  # or 'Qt5Agg' if you have it
import matplotlib.pyplot as plt

CL_max = [1.5, 1.9, 2.4]  # clean, TO, landing
rho_SL = 1.225
V_s = 52  # m/s
sigma = 1  # density ratio

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
s_TO = 914  # m

TOP = solve_positive_root(0.0577, 8.6726, (s_TO/0.3048))
def take_off(CL_max_TO, TOP, sigma):
    x = np.arange(1,7000, 10)
    y = (TOP / x) * CL_max_TO * sigma
    return x, y

s_landing = 762  # m
f = 0.84 #From slides
def landing(CL_max_landing, rho_SL, s_landing,f):
    x = (CL_max_landing * rho_SL * s_landing/0.5915)/2*f
    return x


x_to, y_to = take_off((CL_max[1]/1.1**2), TOP, sigma)
ws_stall_clean = stall_speed(CL_max[0])
ws_stall_TO = stall_speed(CL_max[1])
ws_stall_landing = stall_speed(CL_max[2])
ws_landing = landing(CL_max[2], rho_SL, s_landing, f)


plt.plot(x_to, y_to, label='Take-off Constraint', color='blue')
plt.axvline(ws_stall_clean, color='red', linestyle='--', label=f'Stall (CLmax={CL_max[0]})')
plt.axvline(ws_stall_TO, color='orange', linestyle='--', label=f'Stall (CLmax={CL_max[1]})')
plt.axvline(ws_stall_landing, color='purple', linestyle='--', label=f'Stall (CLmax={CL_max[2]})')
plt.axvline(ws_landing, color='green', linestyle='--', label='Landing Constraint')

plt.xlabel('W/S')
plt.ylabel('W/P')
plt.title('Constraint Diagram')
plt.ylim(0, 0.4)
plt.grid(True)
plt.legend()
plt.show()


from parapy.core import *
from parapy.geom import *
import numpy as np
from parapy.exchange.step import STEPWriter
import matplotlib.pyplot as plt
import os
import openpyxl
import wx

from Sizing.sizing import Sizing
from Fuselage.fuselage import Fuselage
from Propulsion.engine import Engines
from Wing.wing import Wing
from Tail.horizontaltail import HorizontalTail
from Tail.verticaltail import VerticalTail
from Weight_estimation.classI import ClassI
from Weight_estimation.classII import ClassII
from AVL.AVL_analysis import AVL
from Warnings_Errors.gen_warning import generate_warning


DIR = str(os.getcwd())
if not os.path.exists(DIR):
    os.makedirs(DIR)


class Aircraft(GeomBase):
    num_crates = Input()            # Number of 463L master pallets (is being called a crate) [-].
    num_vehicles = Input()          # Number of Humvee 1151 military vehicles [-].
    num_persons = Input()           # Number of military personnel being transported [-].
    R = Input()                     # Range of the aircraft [m].
    s_to = Input()                  # Take-off distance [m].
    s_landing = Input()             # Landing distance [m].
    h_cr = Input()                  # Cruise altitude [m].
    V_cr = Input()                  # Cruise velocity [m/s].
    A = Input()                     # Aspect ratio [-].
    airfoil_name_root = Input()     # Root airfoil of main wing; NACA 4- or 5-digit.
    airfoil_name_tip = Input()      # Tip airfoil of maing wing; NACA 4- or 5-digit.
    N_engines = Input()             # Number of turboprop engines [-].
    root_le = Input()               # Distance from the nose to the root leading edge of the main wing [-].
    horizontal_airfoil = Input()    # Horizontal tail airfoil; symmetric NACA 4-digit.
    vertical_airfoil = Input()      # Vertical tail airfoil; symmetric NACA 4-digit.
    AoA = Input()                   # Angle of attack in cruise conditions [°].
    Nz = Input(3)                   # Ultimate load factor [-].
    Nt = Input(2)                   # Number of fuel tanks [-].
    eff_p = Input(0.82)             # Propulsive efficiency

    @Attribute
    def engine_attachment(self):
        # This calculates where the engines are attached to the wing of the aircraft.
        return (self.wing.tip_le_offset * self.propulsion.pos_engine +
                self.wing.front_spar_position * self.wing.root_chord *
                (1 - self.propulsion.pos_engine * (1 - self.wing.taper_ratio)))

    @Attribute
    def x_root_wing(self):
        # This calculates the location of the root leading edge of the main wing along the fuselage length.
        return self.root_le * self.fuselage.cargo.length

    @Attribute
    def x_lemac(self):
        # This is the x-location of the leading edge mean aerodynamic chord (LEMAC).
        return self.x_root_wing + self.wing.x_LEMAC_offset

    @Attribute
    def Lt_h(self):
        # This is the position of the horizontal tail with regards to the fuselage.
        return self.horizontaltail.X_h + self.horizontaltail.x_LEMAC_h_offset - self.x_lemac

    @Attribute
    def Lt_v(self):
        # This is the position of the vertical tail with regards to the fuselage.
        return self.verticaltail.X_v + self.verticaltail.x_LEMAC_v_offset - self.x_lemac

    @Attribute
    def Fw(self):
        return self.fuselage.radius - 0.5 * self.fuselage.tail_length * np.tan(np.deg2rad(self.fuselage.divergence_angle))

    @Attribute
    def class1(self):
        # This instantiates the Class I weight estimation.
        return ClassI(num_crates=self.num_crates, num_vehicles=self.num_vehicles, num_persons=self.num_persons,
                      R=self.R, eff_p=self.eff_p)#, ld_cr=self.AVL.l_over_d)

    @Attribute
    def oew(self):
        # This functions calculates the operative empty weight (OEW) followed from the Class II weight estimation.
        return sum(p.class2_weight for p in [self.wing, self.fuselage, self.propulsion, self.wing.fueltank,
                                             self.horizontaltail, self.verticaltail])

    @Attribute
    def zfw(self):
        return self.oew + self.fuselage.cargo.mass

    @Attribute
    def tow(self):
        return self.zfw + self.class1.wfuel

    @Attribute
    def class2(self):
        # This calls the Class II weight estimation class.
        return ClassII(W_to=self.class1.wto, Nz=self.Nz, Sw=self.wing.surface, L=self.fuselage.length, D=self.fuselage.thickness,
                       Sf=self.fuselage.fuselage.area, span=self.wing.span, A=self.A, taper=self.wing.taper_ratio,
                       Scsw=2*55*0.3048 ** 2, Lt_h=self.Lt_h, Lt_v=self.Lt_v, tc_root=self.wing.thickness_ratio, Fw=self.Fw,
                       span_h=self.horizontaltail.span_h, S_ht=self.horizontaltail.surface_h, Ah=self.horizontaltail.A_h,
                       taper_h=self.horizontaltail.taper_ratio_h, Se=114.9*.3048 ** 2, Av=self.verticaltail.A_v,
                       S_vt=self.verticaltail.surface_v, taper_v=self.verticaltail.taper_ratio_v,
                       tc_vt=self.verticaltail.thickness_ratio_v, sweep_le_v=self.verticaltail.sweep_LE_v,
                       ttail=0, Vi=self.wing.fueltank.outer_tank.volume, Vp=0, Vt=self.wing.fueltank.outer_tank.volume,
                       Nt=self.Nt, l_ee=self.propulsion.l_ee, w_ee=self.propulsion.w_ee, N_engines=self.N_engines,
                       W_eng=self.propulsion.single_mass)

    # @Attribute
    # def weight(self):
    #     return Estimation(num_crates=self.num_crates, num_vehicles=self.num_vehicles, num_persons=self.num_persons,
    #                        R=self.R, A=self.A, Lt_v=self.Lt_v, Lt_h=self.Lt_h, Nz=3, surface=self.wing.surface,
    #                        length=self.fuselage.length, thickness=self.fuselage.thickness,
    #                        radius=self.fuselage.radius, Sf=self.fuselage.fuselage.area, span=self.wing.span,
    #                        taper_ratio=self.wing.taper_ratio, Scsw=2*55,
    #                        thickness_ratio=self.wing.thickness_ratio, tail_length=self.fuselage.tail_length,
    #                        divergence_angle=self.fuselage.divergence_angle, span_h=self.empennage.span_h,
    #                        surface_h=self.empennage.surface_h, A_h=self.empennage.A_h,
    #                        taper_ratio_h=self.empennage.taper_ratio_h, Se=114.9,
    #                        surface_v=self.empennage.surface_v, A_v=self.empennage.A_v,
    #                        taper_ratio_v=self.empennage.taper_ratio_v, sweep_LE_v=self.empennage.sweep_LE_v, ttail=0,
    #                        Vi=self.wing.fueltank.outer_surf.volume, Vp=0, Vt=self.wing.fueltank.outer_surf.volume, Nt=2)

    @Part
    def sizing(self):
        return Sizing(s_to=self.s_to, s_landing=self.s_landing, h_cr=self.h_cr, V_cr=self.V_cr, A=self.A,
                      Mff=self.class1.Mff, eff_p=self.eff_p)

    @Part
    def fuselage(self):
        # Instantiation of the fuselage class.
        return Fuselage(pass_down='num_crates, num_vehicles, num_persons', Kws_ratio=self.wing.Kws_ratio,
                        tow=self.class1.wto, Nz=self.Nz)

    @Part
    def wing(self):
        # Instantiation of the wing class, including the fuel tanks present in the wing.
        return Wing(pass_down='s_to, s_landing, h_cr, V_cr, A, airfoil_name_root, airfoil_name_tip', tow=self.class1.wto,
                    position=self.position.translate(x=self.x_root_wing, z=self.fuselage.radius), Nz=self.Nz, Nt=self.Nt,
                    fuel_weight=self.class1.wfuel, ws=self.sizing.ws_opt)

    @Part
    def propulsion(self):
        # Instantiation of the propulsion system, hence the turboprop engines.
        return Engines(pass_down='s_to, s_landing, h_cr, V_cr, A, N_engines, Nz', span=self.wing.span,
                       tow=self.class1.wto, wp=self.sizing.wp_opt,
                       position=self.wing.position.translate(x=self.propulsion.l_ee/2,
                                                             z=-self.propulsion.h_ee).rotate(z=np.deg2rad(180)))

    @Part
    def horizontaltail(self):
        # Instantiation of the horizontal tail surfaces.
        return HorizontalTail(pass_down='horizontal_airfoil', length_fuselage=self.fuselage.length, MAC=self.wing.MAC,
                              surface=self.wing.surface, span=self.wing.span, X_CG=self.cg_tail_off,
                              position=self.position.translate(x=self.horizontaltail.pos, z=self.fuselage.radius),
                              tow=self.class1.wto, Nz=self.Nz, Fw=self.Fw, Lt_h=self.Lt_h)

    @Part
    def verticaltail(self):
        # Instantiation of the vertical tail surfaces.
        return VerticalTail(pass_down='vertical_airfoil', length_fuselage=self.fuselage.length, MAC=self.wing.MAC,
                            surface=self.wing.surface, span=self.wing.span, X_CG=self.cg_tail_off,
                            position=self.position.translate(x=self.verticaltail.pos, z=self.fuselage.radius),
                            tow=self.class1.wto, Nz=self.Nz, Lt_v=self.Lt_v)

    @Part
    def AVL(self):
        # Instantiation of the Athena Vortex Lattice (AVL) method.
        return AVL(pass_down='AoA', airfoil_name_root=self.wing.airfoil_name_root,
                   root_chord=self.wing.root_chord, airfoil_name_tip=self.wing.airfoil_name_tip,
                   tip_chord=self.wing.tip_chord, tip_le_offset=self.wing.tip_le_offset,
                   surface=self.wing.surface, span=self.wing.span, MAC=self.wing.MAC, mach=self.sizing.Mach,
                   position=self.position.translate(x=self.x_root_wing, z=self.fuselage.radius))

    @Attribute
    def cg_tail_off(self):
        # This function calculates the center of gravity along the x-axis without the contribution of the empennage.
        return (((self.fuselage.cargo.cg_x * self.fuselage.cargo.mass)
                 + (self.fuselage.cg_x * self.fuselage.class2_weight) + (self.wing.cg_x * self.wing.class2_weight)
                 + (self.wing.fueltank.cg_x * self.wing.fueltank.class2_weight) +
                 (self.propulsion.class2_weight * self.propulsion.cg))
                / (self.fuselage.cargo.mass + self.fuselage.class2_weight + self.wing.class2_weight
                   + self.wing.fueltank.class2_weight + self.propulsion.class2_weight))

    @Attribute
    def cg_total(self):
        # This function calculates the center of gravity along the x-axis including the empennage, hence total aircraft.
        return (self.cg_tail_off * (self.zfw - self.horizontaltail.class2_weight - self.verticaltail.class2_weight)
                + self.horizontaltail.class2_weight * self.horizontaltail.cg_x
                + self.verticaltail.class2_weight * self.verticaltail.cg_x) / self.zfw

    @Part
    def STEP(self):
        # This function creates the .STEP files of the wing, fuselage, engines and empennage nodes.
        # The .STEP files can be visualised using a CAD programme.
        return STEPWriter(default_directory=DIR,
                          nodes=[self.wing.wing, self.fuselage.fuselage,
                                 * [self.propulsion.engines[i] for i in range(self.N_engines)],
                                 self.verticaltail.vertical_tail, self.horizontaltail.horizontal_tail])
    @Attribute
    def a_t(self):
        # The lift curve slope of the commonly used NACA 0012 horizontal tail airfoil [1/rad].
        return 5.7

    @Attribute
    def a(self):
        # The lift curve slope of the NACA 64A318 airfoil used at the root of the main wing on the Lockheed C-130 Hercules.
        return 6

    @Attribute
    def downwash(self):
        # The downwash angle (d_epsilon/d_alpha) as defined by the reference paper on longitudinal static stability from the TU Delft.
        return 0.10

    @Attribute
    def V_h(self):
        return ((self.horizontailtail.surface_h * (self.horizontaltail.X_h - self.cg_total))
                / (self.wing.surface * self.wing.MAC))

    @Attribute
    def neutralpoint(self):
        # Determination of the neutral point along the length of the fuselage.
        return (self.a_t/self.a) * self.V_h * (1 - self.downwash) * self.wing.MAC

    @Attribute
    def stability_margin(self):
        margin = self.neutralpoint - self.cg_total
        if margin <= 0:
            head = "Aircraft is not longitudinally stable:"
            msg = (f"The center of gravity (x={self.cg_total:.2f}) should be in front of the neutral "
                   f"point(x={self.neutralpoint:.2f}). Move the wing more forward.")
            generate_warning(head, msg)
        return margin

    @action(label="Create output file", button_label="Click here to create output Excel file")
    def output(self):
        # Creation of the output .XLSX file, the required output parameters are appended to the file.
        base_dir = os.path.dirname(os.path.abspath(__file__))
        excel_path = os.path.join(os.path.dirname(base_dir), "aircraft_outputs.xlsx")
        wb = openpyxl.Workbook()
        ws = wb.active
        ws.title = "Output design parameters"
        ws.append(["Parameter", "Value", "Unit"])
        ws.append(["Number of 463L master pallet crates", self.num_crates, "-"])
        ws.append(["Number of Humvee 1151 vehicles", self.num_vehicles, "-"])
        ws.append(["Number of airborne personnel", self.num_persons, "-"])
        ws.append(["Range", self.R, "m"])
        ws.append(["Take-off distance", self.s_to, "m"])
        ws.append(["Landing distance", self.s_landing, "m"])
        ws.append(["Cruise altitude", self.h_cr, "m"])
        ws.append(["Cruise velocity", self.V_cr, "m/s"])
        ws.append(["Wing aspect ratio", self.A, "-"])
        ws.append(["Wing root airfoil", self.airfoil_name_root, "-"])
        ws.append(["Wing tip airfoil", self.airfoil_name_tip, "-"])
        ws.append(["Number of engines", self.N_engines, "-"])
        ws.append(["Wing position", self.root_le, "x/length_fuselage"])
        ws.append(["Horizontal tail thickness ratio", self.horizontal_airfoil, "t/c_h_root"])
        ws.append(["Vertical tail thickness ratio", self.vertical_airfoil, "t/c_v_root"])
        ws.append(["Cruise angle of attack", self.AoA, "deg"])
        ws.append(["Ultimate design load factor", self.Nz, "-"])
        ws.append(["Number of fuel tanks", self.Nt, "-"])
        ws.append(["Design propulsive efficiency", self.eff_p, "-"])
        ws.append([])
        ws.append(["Class I weight estimation","",""])
        ws.append(["Operative Empty Weight (OEW)", self.oew, 'kg'])
        ws.append(["Take-Off Weight (TOW)", self.tow, 'kg'])
        ws.append(["Fuel weight (Wf)", self.class1.wfuel, 'kg'])
        ws.append([])
        ws.append(["Class II weight estimation", "", ""])
        ws.append(["Wing weight", self.wing.class2_weight, "kg"])
        ws.append(["Fuselage weight", self.fuselage.class2_weight, "kg"])
        ws.append(["Engine weight", self.propulsion.class2_weight, "kg"])
        ws.append(["Horizontal tail weight", self.horizontaltail.class2_weight, "kg"])
        ws.append(["Vertical tail weight", self.verticaltail.class2_weight, "kg"])
        ws.append(["Fuel tank weight", self.wing.fueltank.class2_weight, "kg"])
        ws.append([])
        ws.append(["Longitudinal Static Stability", "", ""])
        ws.append(["Tailless center of gravity", self.cg_tail_off, "m"])
        ws.append(["Total center of gravity", self.cg_total, "m"])
        ws.append(["Stability margin", self.stability_margin, "m"])
        wb.save(excel_path)
        print(f"Output file created in {excel_path}")

    @action(label="Plot loading diagram", button_label="Click here to plot W/S - W/P diagram used in wing sizing")
    #This allows whether the user wants to visualise the generated W/S vs W/P plot or not
    def plot_loading_diagram(self):
        frame = wx.Frame(None, wx.ID_ANY, "W/S - W/P diagram", size=(800, 600))
        panel = wx.Panel(frame)

        fig, ax = plt.subplots(1, 1)
        ax.plot(self.sizing.take_off[0], self.sizing.take_off[1], label='Take-off Constraint', color='blue')
        ax.axvline(self.sizing.stall_speed[0], color='red', linestyle='--', label=f'Stall (CLmax={self.sizing.CL_max[0]})')
        ax.axvline(self.sizing.stall_speed[1], color='orange', linestyle='--', label=f'Stall (CLmax={self.sizing.CL_max[1]})')
        ax.axvline(self.sizing.stall_speed[2], color='purple', linestyle='--', label=f'Stall (CLmax={self.sizing.CL_max[2]})')
        ax.axvline(self.sizing.landing, color='green', linestyle='--', label='Landing Constraint')
        ax.plot(self.sizing.cruise[0], self.sizing.cruise[1], label='Cruise Constraint', color='red')
        ax.scatter(self.sizing.ws_opt, self.sizing.wp_opt, marker='*', s=200, color='black')
        ax.set_xlabel('W/S')
        ax.set_ylabel('W/P')
        ax.set_title('Constraint Diagram')
        ax.set_ylim(0, 0.4)
        ax.grid(True)
        ax.legend()

        # print(f"Optimal W/S ={self.sizing.ws_opt}")
        # print(f"Optimal W/P ={self.sizing.wp_opt}")

        from matplotlib.backends.backend_wxagg import FigureCanvasWxAgg as FigureCanvas
        canvas = FigureCanvas(panel, -1, fig)  # Directly attach to the existing panel
        sizer = wx.BoxSizer(wx.VERTICAL)
        sizer.Add(canvas, 1, wx.EXPAND)
        panel.SetSizer(sizer)

        # Properly destroy the frame when closing
        frame.Bind(wx.EVT_CLOSE, self.on_close_frame)
        frame.Show()

    def on_close_frame(self, event):
        frame = event.GetEventObject()
        frame.Destroy()  # Properly destroy the frame and clean up


if __name__ == '__main__':
    from parapy.gui import display
    import pandas as pd
    #
    # cargo = Aircraft(num_crates=1, num_vehicles=2, num_persons=9, R=4000000, s_to=1093, s_landing=975, h_cr=8535,
    #                  V_cr=150, A=10.1, airfoil_name_root='64318', airfoil_name_tip='64412', N_engines=4, root_le=0.4,
    #                  horizontal_airfoil='0018', vertical_airfoil='0018', AoA=2, mach=0.49, Nz=3)
    #
    # display(cargo)

    base_dir = os.path.dirname(os.path.abspath(__file__))
    excel_path = os.path.join(base_dir, "aircraft_inputs.xlsx")

    df = pd.read_excel(excel_path, header=None, skiprows=1)

    keys = df.iloc[:, 0].tolist()
    values = df.iloc[:, 1].tolist()

    inputs = {}
    for key, val in zip(keys, values):
        if key in ["airfoil_name_root", "airfoil_name_tip", "horizontal_airfoil", "vertical_airfoil"]:
            val = str(val)
            if val.endswith(".0"):
                val = val[:-2]
            inputs[key] = val.strip("'").zfill(4)
        else:
            if isinstance(val, float) and val.is_integer():
                inputs[key] = int(val)
            else:
                inputs[key] = val
    cargo = Aircraft(**inputs)
    display(cargo)

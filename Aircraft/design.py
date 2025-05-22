from parapy.core import *
from parapy.geom import *
from Aircraft.aircraft import Aircraft
from parapy.exchange.step import STEPWriter
import matplotlib.pyplot as plt
import numpy as np
import os
import openpyxl
import wx


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

    @action(label="Create output file", button_label="Click here to create output Excel file")
    def output(self):
        # Open a file save dialog for the user to specify output path
        dialog = wx.FileDialog(
            None,
            message="Save Excel File As",
            defaultFile="aircraft_outputs.xlsx",
            wildcard="Excel files (*.xlsx)|*.xlsx",
            style=wx.FD_SAVE | wx.FD_OVERWRITE_PROMPT
        )

        if dialog.ShowModal() == wx.ID_CANCEL:
            print("Save cancelled by user.")
            return  # Exit if user cancels

        excel_path = dialog.GetPath()  # Full path the user chose
        dialog.Destroy()

        wb = openpyxl.Workbook()
        ws = wb.active
        ws.title = "Output design parameters"
        ws.append(["Parameter", "Value", "Unit"])
        ws.append(["Number of 463L master pallet crates", self.num_crates, "-"])
        ws.append(["Number of Humvee 1151 vehicles", self.num_vehicles, "-"])
        ws.append(["Number of airborne personnel", self.num_persons, "-"])
        ws.append(["Range", self.aircraft.range, "m"])
        ws.append(["Endurance", self.aircraft.endurance, "h"])
        ws.append(["Take-off distance", self.s_to, "m"])
        ws.append(["Landing distance", self.s_landing, "m"])
        ws.append(["Cruise altitude", self.h_cr, "m"])
        ws.append(["Cruise velocity", self.V_cr, "m/s"])
        ws.append(["Wing aspect ratio", self.A, "-"])
        ws.append(["Wing root airfoil", self.airfoil_name_root, "-"])
        ws.append(["Wing tip airfoil", self.airfoil_name_tip, "-"])
        ws.append(["Number of engines", self.N_engines, "-"])
        ws.append(["Wing position", self.root_le, "x/length_fuselage"])
        ws.append(["Horizontal tail thickness ratio", self.aircraft.horizontal_airfoil, "t/c_h_root"])
        ws.append(["Vertical tail thickness ratio", self.aircraft.vertical_airfoil, "t/c_v_root"])
        ws.append(["Cruise angle of attack", self.AoA, "deg"])
        ws.append(["Ultimate design load factor", self.Nz, "-"])
        ws.append(["Number of fuel tanks", self.Nt, "-"])
        ws.append(["Design propulsive efficiency", self.eff_p, "-"])
        ws.append([])
        ws.append(["Class I weight estimation", "", ""])
        ws.append(["Operative Empty Weight (OEW)", self.aircraft.class1.oew, 'kg'])
        ws.append(["Take-Off Weight (TOW)", self.aircraft.class1.wto, 'kg'])
        ws.append(["Fuel weight (Wf)", self.aircraft.class1.wfuel, 'kg'])
        ws.append([])
        ws.append(["Class II weight estimation", "", ""])
        ws.append(["Wing weight", self.aircraft.wing.class2_weight, "kg"])
        ws.append(["Fuselage weight", self.aircraft.fuselage.class2_weight, "kg"])
        ws.append(["Engine weight", self.aircraft.propulsion.class2_weight, "kg"])
        ws.append(["Horizontal tail weight", self.aircraft.horizontaltail.class2_weight, "kg"])
        ws.append(["Vertical tail weight", self.aircraft.verticaltail.class2_weight, "kg"])
        ws.append(["Fuel tank weight", self.aircraft.wing.fueltank.class2_weight, "kg"])
        ws.append([])
        ws.append(["Longitudinal Static Stability", "", ""])
        ws.append(["Tailless center of gravity", self.aircraft.cg_tail_off, "m"])
        ws.append(["Total center of gravity", self.aircraft.cg_total, "m"])
        ws.append(["Stability margin", self.aircraft.stability_margin, "m"])
        wb.save(excel_path)
        print(f"Output file created in {excel_path}")

    @action(label="Plot loading diagram", button_label="Click here to plot W/S - W/P diagram used in wing sizing")
    # This allows whether the user wants to visualise the generated W/S vs W/P plot or not
    def plot_loading_diagram(self):
        frame = wx.Frame(None, wx.ID_ANY, "W/S - W/P diagram", size=(800, 600))
        panel = wx.Panel(frame)

        fig, ax = plt.subplots(1, 1)
        ax.plot(self.aircraft.sizing.take_off[0], self.aircraft.sizing.take_off[1], label='Take-off Constraint', color='blue')
        ax.axvline(self.aircraft.sizing.stall_speed[0], color='red', linestyle='--',
                   label=f'Stall (CLmax={self.aircraft.sizing.CL_max[0]})')
        ax.axvline(self.aircraft.sizing.stall_speed[1], color='orange', linestyle='--',
                   label=f'Stall (CLmax={self.aircraft.sizing.CL_max[1]})')
        ax.axvline(self.aircraft.sizing.stall_speed[2], color='purple', linestyle='--',
                   label=f'Stall (CLmax={self.aircraft.sizing.CL_max[2]})')
        ax.axvline(self.aircraft.sizing.landing, color='green', linestyle='--', label='Landing Constraint')
        ax.plot(self.aircraft.sizing.cruise[0], self.aircraft.sizing.cruise[1], label='Cruise Constraint', color='red')
        ax.scatter(self.aircraft.sizing.ws_opt, self.aircraft.sizing.wp_opt, marker='*', s=200, color='black')
        ax.set_xlabel('W/S [N/m^2]')
        ax.set_ylabel('W/P [N/W]')
        ax.set_title('Constraint Diagram')
        ax.set_ylim(0, 0.4)
        ax.grid(True)
        ax.legend()

        # print(f"Optimal W/S ={self.sizing.ws_opt}")
        # print(f"Optimal W/P ={self.sizing.wp_opt}")

        from matplotlib.backends.backend_wxagg import FigureCanvasWxAgg, NavigationToolbar2WxAgg
        canvas = FigureCanvasWxAgg(panel, -1, fig)  # Directly attach to the existing panel
        sizer = wx.BoxSizer(wx.VERTICAL)
        sizer.Add(canvas, 1, wx.EXPAND)
        toolbar = NavigationToolbar2WxAgg(canvas)
        sizer.Add(toolbar, 0, wx.LEFT | wx.EXPAND)

        panel.SetSizer(sizer)

        # Properly destroy the frame when closing
        frame.Bind(wx.EVT_CLOSE, self.on_close_frame)
        frame.Show()

    @action(label="Plot payload-range diagram", button_label="Click here to plot PL-R diagram")
    def plot_payloadrange_diagram(self):
        w_pl_max_fuel = max(0, self.aircraft.class1.wto - self.aircraft.class1.oew - self.aircraft.wing.fueltank.max_fuel_weight)
        mff = ((self.aircraft.class1.b + self.aircraft.class1.w_crew + w_pl_max_fuel * 9.80655) / self.aircraft.class1.wto / 9.80655
               + self.aircraft.class1.a + self.aircraft.class1.Mtfo)
        ffs = self.aircraft.class1.ff1 * self.aircraft.class1.ff2 * self.aircraft.class1.ff3 * self.aircraft.class1.ff4 * self.aircraft.class1.ff7 * self.aircraft.class1.ff8
        range_pl_max_fuel = self.aircraft.class1.eff_p / 9.80655 / self.aircraft.class1.cp * self.aircraft.class1.ld_cr * np.exp(ffs / mff)

        A = [0, self.aircraft.class1.w_payload / 9.80655]
        B = [self.aircraft.class1.R, self.aircraft.class1.w_payload / 9.80655]
        C = [range_pl_max_fuel, w_pl_max_fuel]
        D = [self.aircraft.class1.max_range, 0]

        frame = wx.Frame(None, wx.ID_ANY, "W/S - W/P diagram", size=(800, 600))
        panel = wx.Panel(frame)

        fig, ax = plt.subplots(1, 1)
        ax.plot([l[0] for l in (A, B, C, D)], [l[1] for l in (A, B, C, D)])
        ax.grid(True)
        ax.set_xlabel('Range [m]')
        ax.set_ylabel('Payload weight [kg]')
        ax.set_title('Payload-Range Diagram')
        # ax.set_xlim(0, self.class1.max_range)
        # ax.set_ylim(0, self.class1.w_payload / 9.80655)

        from matplotlib.backends.backend_wxagg import FigureCanvasWxAgg, NavigationToolbar2WxAgg
        canvas = FigureCanvasWxAgg(panel, -1, fig)  # Directly attach to the existing panel
        sizer = wx.BoxSizer(wx.VERTICAL)
        sizer.Add(canvas, 1, wx.EXPAND)
        toolbar = NavigationToolbar2WxAgg(canvas)
        sizer.Add(toolbar, 0, wx.LEFT | wx.EXPAND)
        panel.SetSizer(sizer)

        # Properly destroy the frame when closing
        frame.Bind(wx.EVT_CLOSE, self.on_close_frame)
        frame.Show()

    # @action(label='Analyse stability margin', button_label="Click here to analyse stability margin")
    # def analyze_stability_margin(self):
    #     stab_mar = self.stability_margin

    def on_close_frame(self, event):
        frame = event.GetEventObject()
        frame.Destroy()  # Properly destroy the frame and clean up



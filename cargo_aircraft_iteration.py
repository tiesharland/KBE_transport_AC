from Aircraft.design import Design
import os
import pandas as pd


DIR = str(os.getcwd())
if not os.path.exists(DIR):
    os.makedirs(DIR)


if __name__ == '__main__':

    from parapy.gui import display
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
    cargo = Design(**inputs)
    display(cargo)


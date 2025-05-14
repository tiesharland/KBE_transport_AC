import numpy as np


def ClassII(W_to, Nz, Sw, L, D, Sf, span, A, taper, Scsw, Lt_h, Lt_v, tc_root, Fw, span_h, S_ht, Ah, taper_h, Se, Av,
            S_vt, taper_v, sweep_le_v, ttail, Vi, Vp, Vt, Nt):#, N_Lt, N_w, W_eng, N_en, Sn, L_ec):
    W_to = W_to / 0.45359
    Sw = Sw / (0.3048 ** 2)
    L = L / 0.3048
    D = D / 0.3048
    Sf = Sf / (0.3048 ** 2)
    span = span / 0.3048
    Scsw = Scsw / (0.3048 ** 2)
    Lt_h = Lt_h / 0.3048
    Lt_v = Lt_v / 0.3048
    Fw = Fw / 0.3048
    span_h = span_h / 0.3048
    S_ht = S_ht / (0.3048 ** 2)
    Se = Se / (0.3048 ** 2)
    S_vt = S_vt / (0.3048 ** 2)
    Vi = Vi * 264.172
    Vp = Vp * 264.172
    Vt = Vt * 264.172
    # N_Lt = N_Lt / 0.3048
    # N_w = N_w / 0.3048
    # W_eng = W_eng / 0.45359
    # L_ec = L_ec / 0.3048

    W_w = 0.0051 * (W_to * Nz) ** 0.557 * Sw ** 0.649 * A ** 0.5 / tc_root ** 0.4 * (1 + taper) ** 0.1 * Scsw ** 0.1

    Kuht = 1 # non-unit horizontal tail
    Ky = 0.3 * Lt_h # AC radius of gyration ~0.3Lt
    sweep_ht = np.arctan(2 / Ah * (1 - taper_h) / (1 + taper_h))
    W_ht = (0.0379 * Kuht / (1 + Fw / span_h) ** 0.25 * W_to ** 0.639 * Nz ** 0.1 * S_ht ** 0.75 / Lt_h * Ky ** 0.704
            * Ah ** 0.166 / np.cos(sweep_ht) * (1 + Se / S_ht) ** 0.1)

    Kz = Lt_v # AC radius of gyration ~lt
    sweep_vt = np.arctan((taper_v - 1) / (taper_v + 1) / 2 / Av + np.tan(np.deg2rad(sweep_le_v)))
    W_vt = (0.0026 * (1 + (1 if ttail else 0)) ** 0.225 * W_to ** 0.556 * Nz ** 0.536 / Lt_v ** 0.5 * S_vt ** 0.5
            * Kz ** 0.875 / np.cos(sweep_vt) * Av ** 0.35 / tc_root ** 0.5)

    Kdoor = 1.25 # 2 side cargo doors & aft clamshell door
    Klg = 1.12 # fuselage-mounted landing-gear
    Kws = 0.75 * ((1 + 2 * taper)/(1 + taper)) * span * np.tan(0) / L
    W_f = 0.3280 * Kdoor * Klg * (W_to * Nz) ** 0.5 * L ** 0.25 * Sf ** 0.302 * (1 + Kws) ** 0.4 * (L / D) ** 0.10
    W_ft = 2.405 * Vt ** 0.606 / (1 + Vi/Vt) * (1 + Vp/Vt) * Nt ** 0.5

    Kmp, Knp = 1, 1 # Non-kneeling gear

    # Kng = 1     # Non-pylon-mounted nacelle
    # Kp = 1.4    # propeller engine
    # Ktr = 1     # non- jet thrust reverser engine
    # W_ec = 2.331 * W_eng ** 0.901 * Kp * Ktr
    # W_nacelle = 0.6724 * Kng * N_Lt ** 0.1 * N_w ** 0.294 * Nz ** 0.119 * W_ec ** 0.611 * N_en ** 0.984 * Sn ** 0.224

    # W_eng_cont = 5 * N_en + 0.8 * L_ec

    return W_w*0.45359, W_f*0.45359, W_ht*0.45359, W_vt*0.45359, W_ft*0.45359#, W_nacelle*0.45359

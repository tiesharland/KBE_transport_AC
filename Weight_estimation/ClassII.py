import numpy as np


def ClassII(W_to, Nz, Sw, L, Sf, span, A, taper, Scsw, Lt, tc_root, Fw, span_h, S_ht, Ah, Av, S_vt, Hv):
    W_w = 0.0051 * (W_to * Nz) ** 0.557 * Sw ** 0.649 * A * tc_root ** (-0.4) * (1 + taper) ** 0.1 * Scsw
    Kuht = 1 # non-unit horizontal tail
    Ky = 0.3 * Lt # AC radius of gyration ~0.3Lt
    sweep_ht
    W_ht = 0.0379 * Kuht * (1 + Fw / span_h) ** (-0.25) * W_to ** 0.639 * Nz ** 0.1 * S_ht ** 0.75 / Lt * Ky ** 0.704
    return None
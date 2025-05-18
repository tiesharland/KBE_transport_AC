import numpy as np
from parapy.core import *
from parapy.geom import *


class ClassII(Base):
    # W_to, Nz, Sw, L, D, Sf, span, A, taper, Scsw, Lt_h, Lt_v, tc_root, Fw, span_h, S_ht, Ah, taper_h, Se, Av,
    #         S_vt, taper_v, sweep_le_v, ttail, Vi, Vp, Vt, Nt):#, N_Lt, N_w, W_eng, N_en, Sn, L_ec):

    W_to = Input()
    Nz = Input()
    Sw = Input()
    L = Input()
    D = Input()
    Sf = Input()
    span = Input()
    A = Input()
    taper = Input()
    Scsw = Input()
    Lt_h = Input()
    Lt_v = Input()
    tc_root = Input()
    Fw = Input()
    span_h = Input()
    S_ht = Input()
    Ah = Input()
    taper_h = Input()
    Se = Input()
    Av = Input()
    S_vt = Input()
    taper_v = Input()
    tc_vt = Input()
    sweep_le_v = Input()
    ttail = Input()
    Vi = Input()
    Vp = Input()
    Vt = Input()
    Nt = Input()
    W_eng = Input()
    l_ee = Input()
    w_ee = Input()
    N_engines = Input()
    Sn = Input()


    @W_to.preprocessor
    def W_to(self, value):
        return value / 0.45359

    @Sw.preprocessor
    def Sw(self, value):
        return value / (0.3048 ** 2)

    @L.preprocessor
    def L(self, value):
        return value / 0.3048

    @D.preprocessor
    def D(self, value):
        return value / 0.3048

    @Sf.preprocessor
    def Sf(self, value):
        return value / (0.3048 ** 2)

    @span.preprocessor
    def span(self, value):
        return value / 0.3048

    @Scsw.preprocessor
    def Scsw(self, value):
        return value / (0.3048 ** 2)

    @Lt_h.preprocessor
    def Lt_h(self, value):
        return value / 0.3048

    @Lt_v.preprocessor
    def Lt_v(self, value):
        return value / 0.3048

    @Fw.preprocessor
    def Fw(self, value):
        return value / 0.3048

    @span_h.preprocessor
    def span_h(self, value):
        return value / 0.3048

    @S_ht.preprocessor
    def S_ht(self, value):
        return value / (0.3048 ** 2)

    @Se.preprocessor
    def Se(self, value):
        return value / (0.3048 ** 2)

    @S_vt.preprocessor
    def S_vt(self, value):
        return value / (0.3048 ** 2)

    @Vi.preprocessor
    def Vi(self, value):
        return value * 264.172

    @Vp.preprocessor
    def Vp(self, value):
        return value * 264.172

    @Vt.preprocessor
    def Vt(self, value):
        return value * 264.172

    @l_ee.preprocessor
    def l_ee(self, value):
        return value / 0.3048

    @w_ee.preprocessor
    def w_ee(self, value):
        return value / 0.3048

    @W_eng.preprocessor
    def W_eng(self, value):
        return value / 0.45359

    @Sn.preprocessor
    def Sn(self, value):
        return value / (0.3048 ** 2)

    # N_Lt = N_Lt / 0.3048
    # N_w = N_w / 0.3048
    # W_eng = W_eng / 0.45359
    # L_ec = L_ec / 0.3048

    @Attribute
    def W_w(self):
        return 0.45359 * (0.0051 * (self.W_to * self.Nz) ** 0.557 * self.Sw ** 0.649 * self.A ** 0.5
                          / self.tc_root ** 0.4 * (1 + self.taper) ** 0.1 * self.Scsw ** 0.1)

    @Attribute
    def W_ht(self):
        Kuht = 1 # non-unit horizontal tail
        Ky = 0.3 * self.Lt_h # AC radius of gyration ~0.3Lt
        sweep_ht = np.arctan(2 / self.Ah * (1 - self.taper_h) / (1 + self.taper_h))
        return 0.45359 * (0.0379 * Kuht / (1 + self.Fw / self.span_h) ** 0.25 * self.W_to ** 0.639 * self.Nz ** 0.1
                          * self.S_ht ** 0.75 / self.Lt_h * Ky ** 0.704 * self.Ah ** 0.166 / np.cos(sweep_ht)
                          * (1 + self.Se / self.S_ht) ** 0.1)

    @Attribute
    def W_vt(self):
        Kz = self.Lt_v # AC radius of gyration ~lt
        sweep_vt = np.arctan((self.taper_v - 1) / (self.taper_v + 1) / 2 / self.Av + np.tan(np.deg2rad(self.sweep_le_v)))
        return 0.45359 * (0.0026 * (1 + (1 if self.ttail else 0)) ** 0.225 * self.W_to ** 0.556 * self.Nz ** 0.536
                          / self.Lt_v ** 0.5 * self.S_vt ** 0.5 * Kz ** 0.875 / np.cos(sweep_vt) * self.Av ** 0.35
                          / self.tc_vt ** 0.5)

    @Attribute
    def W_f(self):
        Kdoor = 1.25 # 2 side cargo doors & aft clamshell door
        Klg = 1.12 # fuselage-mounted landing-gear
        Kws = 0.75 * ((1 + 2 * self.taper)/(1 + self.taper)) * self.span * np.tan(0) / self.L
        return 0.45359 * (0.3280 * Kdoor * Klg * (self.W_to * self.Nz) ** 0.5 * self.L ** 0.25 * self.Sf ** 0.302
                          * (1 + Kws) ** 0.4 * (self.L / self.D) ** 0.10)

    @Attribute
    def W_ft(self):
        return 0.45359 * (2.405 * self.Vt ** 0.606 / (1 + self.Vi/self.Vt) * (1 + self.Vp/self.Vt) * self.Nt ** 0.5)

    @Attribute
    def ew(self):
        return self.W_w + self.W_f + self.W_ft + self.W_ht + self.W_vt

    @Attribute
    def W_ne(self):
        Kmp, Knp = 1, 1 # Non-kneeling gear

        Kng = 1     # Non-pylon-mounted nacelle
        Kp = 1.4    # propeller engine
        Ktr = 1     # non- jet thrust reverser engine
        W_ec = 2.331 * self.W_eng ** 0.901 * Kp * Ktr
        return 0.45359 * (0.6724 * Kng * self.l_ee ** 0.1 * self.w_ee ** 0.294 * self.Nz ** 0.119 * W_ec ** 0.611
                * self.N_engines ** 0.984 * self.Sn ** 0.224 + self.W_eng)



    # W_eng_cont = 5 * N_en + 0.8 * L_ec

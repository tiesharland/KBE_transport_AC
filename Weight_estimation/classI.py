import numpy as np
from parapy.core import *
from parapy.geom import *


class ClassI(Base):
    crates = Input()
    vehicles = Input()
    persons = Input()
    R = Input()
    ld_cr = Input(14)
    eff_p = Input(0.82)
    cp = Input(.6 * 1.68965941e-7)
    W_OE = Input(None)

    @Attribute
    def w_crates(self):
        return self.crates * 4500 * 9.80655

    @Attribute
    def w_vehicles(self):
        return self.vehicles * 2962 * 9.80655

    @Attribute
    def w_persons(self):
        return self.persons * 100 * 9.80655

    @Attribute
    def w_payload(self):
        return self.w_crates + self.w_vehicles + self.w_persons

    @Attribute
    def w_crew(self):
        return 2 * 100 * 9.80655

    @Attribute
    def weights(self):
        Mtfo = 0.005
        a = 0.5482
        b = 486.68

        ff1 = .990
        ff2 = .990
        ff3 = .995
        ff4 = .980
        ff7 = .990
        ff8 = .992
        ff5 = 1 / np.exp(self.R / self.eff_p * self.cp * 9.80655 / self.ld_cr)
        Mff = ff1 * ff2 * ff3 * ff4 * ff5 * ff7 * ff8

        if self.W_OE:
            oew = self.W_OE
        else:
            wto = (b + self.w_crew + self.w_payload) / (Mff - a - Mtfo)
            oew = a * wto + b + wto * Mtfo + self.w_crew

        return oew/9.80655, wto/9.80655, (1-Mff)*wto/9.80655

    @Attribute
    def oew(self):
        return self.weights[0]

    @Attribute
    def wto(self):
        return self.weights[1]

    @Attribute
    def w_fuel(self):
        return self.weights[2]


if __name__ == '__main__':
    c1 = ClassI(crates=1, vehicles=2, persons=9, R=4000000)
    print(c1.oew, c1.wto, c1.w_fuel)


import numpy as np
from parapy.core import *
from parapy.geom import *


class ClassI(Base):
    num_crates = Input()
    num_vehicles = Input()
    num_persons = Input()
    R = Input()
    eff_p = Input()
    ld_cr = Input(14)
    cp = Input(.6 * 1.68965941e-7)
    a = Input(0.5482)
    b = Input(486.68)
    W_OE = Input(None)

    @Attribute
    def w_crates(self):
        return self.num_crates * 4500 * 9.80655

    @Attribute
    def w_vehicles(self):
        return self.num_vehicles * 2962 * 9.80655

    @Attribute
    def w_persons(self):
        return self.num_persons * 100 * 9.80655

    @Attribute
    def w_payload(self):
        return self.w_crates + self.w_vehicles + self.w_persons

    @Attribute
    def w_crew(self):
        return 2 * 100 * 9.80655

    @Attribute
    def Mtfo(self):
        return 0.005

    @Attribute
    def Mff(self):
        ff1 = .990
        ff2 = .990
        ff3 = .995
        ff4 = .980
        ff7 = .990
        ff8 = .992
        ff5 = 1 / np.exp(self.R / self.eff_p * self.cp * 9.80655 / self.ld_cr)
        return ff1 * ff2 * ff3 * ff4 * ff5 * ff7 * ff8

    @Attribute
    def wto(self):
        return (self.b + self.w_crew + self.w_payload) / (self.Mff - self.a - self.Mtfo) / 9.80655

    @Attribute
    def oew(self):
        return (self.a * self.wto * 9.80655 + self.b + self.wto * 9.80655 * self.Mtfo + self.w_crew) / 9.80655

    @Attribute
    def wfuel(self):
        return (1 - self.Mff) * self.wto


if __name__ == '__main__':
    c1 = ClassI(crates=1, vehicles=2, persons=9, R=4000000)
    print(c1.oew, c1.wto, c1.w_fuel)


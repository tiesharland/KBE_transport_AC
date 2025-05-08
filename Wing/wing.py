from math import sqrt, radians, tan, pi
from parapy.core import *
from parapy.geom import *
from Wing.airfoil import Airfoil
from Wing.Sizing import calculate_optimal_point
from Wing.fueltank import FuelTank

class Wing(GeomBase):
    mtow = Input()
    s_to = Input()
    s_landing = Input()
    h_cr = Input()
    V_cr = Input()
    A = Input()
    airfoil_name_root = Input()
    airfoil_name_tip = Input()


    @Attribute
    def surface(self):
        ws, wp = calculate_optimal_point(self.s_to, self.s_landing, self.h_cr, self.V_cr, self.A, plotting=False)
        return self.mtow / ws

    @Attribute
    def taper_ratio(self):
        return 0.4

    @Attribute
    def front_spar_position(self):
        return 0.2

    @Attribute
    def aft_spar_position(self):
        return 0.75

    @Attribute
    def span(self):
        return sqrt(self.surface * self.A)

    @Attribute
    def root_chord(self):
        return (2 * self.surface) / (1 + self.taper_ratio) / self.span

    @Attribute
    def local_chord(self):
        return self.root_chord - ((self.root_chord - self.tip_chord)/(self.span /2)) * (0.85 * self.span/2)

    @Attribute
    def thickness_local_chord(self):
        return (self.thickness_ratio / 100) * self.local_chord

    @Attribute
    def tip_chord(self):
        return self.root_chord * self.taper_ratio

    @Attribute
    def tip_le_offset(self):
        return (self.root_chord-self.tip_chord)/4

    @Attribute
    def thickness_ratio(self):
        return int(self.airfoil_name_root[-2:])

    @Attribute
    def thickness_root(self):
        return (self.thickness_ratio / 100) * self.root_chord

    @Attribute
    def MAC(self):
        return 2/3 * self.root_chord * (1 + self.taper_ratio + self.taper_ratio**2) / (1 + self.taper_ratio)

    @Part
    def root_airfoil(self):
        return Airfoil(airfoil_name=self.airfoil_name_root, chord=self.root_chord, position=self.position)

    @Part
    def tip_airfoil(self):
        return Airfoil(airfoil_name=self.airfoil_name_tip, chord=self.tip_chord,
                       position=self.position.translate(x=self.tip_le_offset, y=self.span/2))


    @Part
    def tip_mirrored(self):
        return Airfoil(airfoil_name=self.airfoil_name_tip, chord=self.tip_chord,
                       position=self.position.translate(x=(self.root_chord-self.tip_chord)/4, y=self.span/-2))

    @Part
    def wing(self):
        return LoftedSurface(profiles=[self.tip_mirrored.profile, self.root_airfoil.profile, self.tip_airfoil.profile])


    @Part
    def fueltank(self):
        return FuelTank(airfoil_name_root=self.airfoil_name_root,airfoil_name_tip=self.airfoil_name_tip,root_chord=self.root_chord,tip_chord=self.tip_chord,span=self.span)


if __name__ == '__main__':
    from parapy.gui import display
    wing = Wing(mtow=70307*9.81, s_to=1093, s_landing=975, h_cr=8535, V_cr=150, A=10.1, airfoil_name_root='64318', airfoil_name_tip = '64412')
    display(wing)
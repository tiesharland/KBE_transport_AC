from math import sqrt, radians, tan, pi
from parapy.core import *
from parapy.geom import *
from Wing.airfoil import Airfoil
from Wing.fueltank import FuelTank

class Wing(GeomBase):
    tow = Input()
    s_to = Input()
    s_landing = Input()
    h_cr = Input()
    V_cr = Input()
    A = Input()
    airfoil_name_root = Input()
    airfoil_name_tip = Input()
    wing_mass = Input()
    Nz = Input()
    Scsw = Input(2*55 * .3048 ** 2)
    Nt = Input()
    fuel_weight = Input()
    ws = Input()


    @Attribute
    def surface(self):
        return self.tow * 9.81 / self.ws

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

    @Attribute
    def x_LEMAC_offset(self):
        return (self.root_chord - self.MAC) / 2

    @Attribute
    def cg_x(self):
        return self.wing.cog[0]

    @Attribute
    def Kws_ratio(self):
        return 0.75 * ((1 + 2 * self.taper_ratio)/(1 + self.taper_ratio)) * self.span/.3048

    @Attribute
    def class2_weight(self):
        return 0.45359 * (0.0051 * (self.tow/ 0.45359 * self.Nz) ** 0.557 * (self.surface/0.3048**2) ** 0.649 * self.A ** 0.5
                          / self.thickness_ratio ** 0.4 * (1 + self.taper_ratio) ** 0.1 * (self.Scsw/0.3048**2) ** 0.1)

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
        return RuledSolid(
            profiles=[self.tip_mirrored.profile, self.root_airfoil.profile, self.tip_airfoil.profile],
            position=self.position,color=[107, 142, 35]
        )

    @Part
    def fueltank(self):
        return FuelTank(airfoil_name_root=self.airfoil_name_root, airfoil_name_tip=self.airfoil_name_tip, span=self.span,
                        root_chord=self.root_chord, tip_chord=self.tip_chord, tip_le_offset=self.tip_le_offset,
                        wall_thickness=0.02, position=self.position, Nt=self.Nt, fuel_weight=self.fuel_weight)


if __name__ == '__main__':
    from parapy.gui import display
    wing = Wing(tow=70307, s_to=1093, s_landing=975, h_cr=8535, V_cr=150, A=10.1, airfoil_name_root='64318',
                airfoil_name_tip='64412', Nz=3, Nt=4)
    display(wing)
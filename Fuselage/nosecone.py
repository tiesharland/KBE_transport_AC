from parapy.core import *
from parapy.geom import *


class NoseCone(GeomBase):
    radius = Input()
    nose_fineness = Input()
    length_cp = Input(4)
    inclination_windshield = Input(45)
    overnose_angle = Input(17)
    overside_angle = Input(35)
    sections = Input([0.1, 0.8, 0.95, 1.])

    @Attribute
    def length(self):
        return self.radius * self.nose_fineness * 2

    @Part
    def profiles(self):
        return Circle(quantify=len(self.sections),
                      position=self.position.translate(x=self.length*child.index/(len(self.sections)-1)).rotate90('y'),
                      radius=self.radius*self.sections[child.index], hidden=True)

    # @Part
    # def nosecone(self):
    #     # return LoftedSurface(profiles=[self.front_cp, self.aft_cp, self.end_nose])
    #     return LoftedSurface(profiles=self.profiles)


if __name__ == '__main__':
    from parapy.gui import display
    cone = NoseCone(radius=3, nose_fineness=1.6)
    display(cone)
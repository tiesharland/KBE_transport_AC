from parapy.core import *
from parapy.geom import *


class NoseCone(GeomBase):
    radius = Input()
    nose_fineness = Input()
    length_cp = Input(4)
    inclination_windshield = Input(45)
    overnose_angle = Input(17)
    overside_angle = Input(35)
    sections = Input([0.1, 0.8, 0.95, 1, 1.])

    @Attribute
    def nose_length(self):
        return self.radius * self.nose_fineness * 2

    # @Part
    # def front_cp(self):
    #     return Circle(quantify=len(self.sections),
    #                   position=self.position.translate(x=self.nose_length/2*child.index/len(self.sections),
    #                                                    z=self.radius/4).rotate90('y'),
    #                   radius=self.radius*0.8*self.sections[child.index])
    #
    # @Part
    # def aft_cp(self):
    #     return Circle(position=self.position.translate(x=self.nose_length*3/4, z=self.radius/2).rotate90('y'),
    #                   radius=self.radius*0.9)
    #
    # @Part
    # def end_nose(self):
    #     return Circle(position=self.position.translate(x=self.nose_length, z=self.radius/2).rotate90('y'),
    #                   radius=self.radius)

    @Part
    def profiles(self):
        return Circle(quantify=len(self.sections),
                      position=self.position.translate(x=self.nose_length*child.index/(len(self.sections)-1)).rotate90('y'),
                      radius=self.radius*self.sections[child.index])

    @Part
    def nosecone(self):
        # return LoftedSurface(profiles=[self.front_cp, self.aft_cp, self.end_nose])
        return LoftedSurface(profiles=self.profiles)


if __name__ == '__main__':
    from parapy.gui import display
    cone = NoseCone(radius=3, nose_fineness=1.6)
    display(cone)
from parapy.core import *
from parapy.geom import *

class Personnel(GeomBase):
    name = Input('Personnel')
    num_persons = Input()
    single_mass = Input(100.)
    single_height = Input(1.80)
    single_width = Input(0.46)
    single_length = Input(0.50)
    spacing = Input(1.5)
    num_columns = Input(2)

    @Attribute
    def num_rows(self):
        return self.num_persons // self.num_columns + self.num_persons % self.num_columns

    @Attribute
    def length(self):
        return self.single_length * self.num_rows

    @Attribute
    def width(self):
        return 0 if self.num_persons == 0 else self.single_width * self.num_columns + self.spacing

    @Attribute
    def height(self):
        return 0 if self.num_persons == 0 else self.single_height

    @Attribute
    def mass(self):
        return self.single_mass * self.num_rows * self.num_columns

    @Attribute
    def cg(self):
        personnel_parts = self.seats
        cg_x = sum(seat.cog[0] * self.single_mass for seat in personnel_parts) / self.mass
        return cg_x

    @Part
    def seats(self):
        return Box(length=self.single_width, width=self.single_length, height=self.single_height,
                   quantify=self.num_rows*self.num_columns,
                   position=self.position.translate(
                       x=self.single_length * (child.index//self.num_columns),
                       y=((self.single_width + self.spacing) * (-1)**child.index - self.single_width)/self.num_columns))


if __name__ == '__main__':
    persons = Personnel(num_persons=7)
    from parapy.gui import display
    display(persons)



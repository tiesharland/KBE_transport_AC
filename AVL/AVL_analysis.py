from parapy.core import *
from parapy.geom import *
import kbeutils.avl as avl
from Wing.wing import Wing
from Wing.Sizing import calculate_optimal_point
from Wing.airfoil import Airfoil


class AVL(GeomBase):
    airfoil_name_root = Input()
    root_chord = Input()
    airfoil_name_tip = Input()
    tip_chord = Input()
    tip_le_offset = Input()
    surface = Input()
    span = Input()
    MAC = Input()
    mach = Input()
    cl_cr = Input()

    @Part
    def root_airfoil(self):
        return Airfoil(airfoil_name=self.airfoil_name_root, chord=self.root_chord, position=self.position)

    @Part
    def tip_airfoil(self):
        return Airfoil(airfoil_name=self.airfoil_name_tip, chord=self.tip_chord,
                       position=self.position.translate(x=self.tip_le_offset, y=self.span / 2))


    @Part
    def avl_section_root(self):
        return avl.Section(chord=self.root_chord,
                           airfoil=avl.NacaAirfoil(designation=self.airfoil_name_root),
                           position=self.root_airfoil.position)

    @Part
    def avl_section_tip(self):
        return avl.Section(chord=self.tip_chord,
                           airfoil=avl.NacaAirfoil(designation=self.airfoil_name_tip),
                           position=self.tip_airfoil.position)


    @Part
    def avl_surface(self):
        return avl.Surface(name=self.name,
                           n_chordwise=12,
                           chord_spacing=avl.Spacing.cosine,
                           n_spanwise=20,
                           span_spacing=avl.Spacing.cosine,
                           y_duplicate=self.position.point[1],
                           sections=[self.avl_section_root,self.avl_section_tip])

    @Attribute(in_tree=True)
    def avl_surfaces(self):
        return list(self.find_children(lambda o: isinstance(o, avl.Surface)))

    @Part
    def avl_configuration(self):
        return avl.Configuration(name='cruise',
                                 reference_area=self.surface,
                                 reference_span=self.span,
                                 reference_chord=self.MAC,
                                 reference_point=self.position.point,
                                 surfaces=self.avl_surfaces,
                                 mach=self.mach)


    @Attribute
    def avl_settings(self):
        return {'alpha': avl.Parameter(name='alpha',
                                       setting='CL',
                                       value=self.cl_cr)}

    @Part
    def avl_case(self):
        return avl.Case(name='fixed_cl',
                        # name _must_ correspond to type of case
                        settings=self.avl_settings)



    @Part
    def avl_analysis(self):
        return avl.Interface(configuration=self.avl_configuration,
                             # note: AVL always expects a list of cases!
                             cases=[self.avl_case]
                             )


    @Attribute
    def l_over_d(self):
        return {result['Name']: result['Totals']['CLtot'] / result['Totals']['CDtot']
                for case_name, result in self.avl_analysis.results.items()}


if __name__ == '__main__':
    from parapy.gui import display


    obj = AVL(airfoil_name_root='64318',root_chord=5, airfoil_name_tip = '64412',tip_chord=2,tip_le_offset=3,surface=20,span=5,MAC=1.5,mach=0.491,cl_cr=0.4)

    display(obj)
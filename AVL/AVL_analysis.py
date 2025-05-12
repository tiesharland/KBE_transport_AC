from parapy.core import *
from parapy.geom import *
import kbeutils.avl as avl
from Wing.wing import Wing
from Wing.Sizing import calculate_optimal_point

class AVL(GeomBase):
    sections = Input()
    root_airfoil = Input()
    tip_airfoil = Input()
    tip_mirrored = Input()
    surface = Input()
    span = Input()
    MAC = Input()
    mach = Input()

    @Part
    def sections(self):
        return [self.root_airfoil, self.tip_airfoil]

    @Part
    def avl_surface(self):
        return avl.Surface(name=self.name,
                           n_chordwise=12,
                           chord_spacing=avl.Spacing.cosine,
                           n_spanwise=20,
                           span_spacing=avl.Spacing.cosine,
                           y_duplicate=self.position.point[1],
                           sections=[section.avl_section for section in self.sections])

    @Attribute(in_tree=True)
    def avl_surfaces(self):  # a list of all AVL surfaces in the aircraft:
        return self.find_children(lambda o: isinstance(o, avl.Surface))
        # This automatically scans the product tree and collects all
        # instances of the avl.Surface class.
        # (if you don't know what `lambda` is doing there: that's a somewhat
        # more advanced feature of functional programming, but it's not
        # required knowledge for this course. Just use it as provided above,
        # and you'll be fine. Feel free to check out the
        # Python documentation about it, though, if you're curious.)

        # Otherwise, you can of course also manually specify the surfaces you
        # want to include, like this:
        # return [self.wing.avl_surface, self.tail.avl_surface]
        # (but make sure you forget no surface that needs to be included in the
        # model!)

    @Part
    def avl_configuration(self):
        return avl.Configuration(name='cruise analysis',
                                 reference_surface=self.wing.surface,
                                 reference_span=self.wing.span,
                                 reference_chord=self.wing.MAC,
                                 reference_point=self.position.point,
                                 surfaces=self.avl_surfaces,
                                 mach=self.mach)

    @Attribute
    def avl_settings(self):
        """
        Format for AVL inputs:
            dict(<parameter to define>: <value>)
            value can be defined either by a number or with `avl.Parameter`:
            avl.Parameter(name=<var to adjust>,
                          setting=<var for which to achieve a given value>
                          value=<value to achieve>)
        These need to be defined either in Input or in a separate Attribute, in
        order to allow ParaPy to trace dependencies (defining this dictionary
        in an argument for avl.Interface() or avl.Case fails for that reason)
        """
        return {'alpha': avl.Parameter(name='alpha',
                                       setting='CL',
                                       value=self.cl_cr)}

    @Part
    def avl_case(self):
        """avl case definition using the avl_settings dictionary defined above"""
        return avl.Case(name='fixed_cl',  # name _must_ correspond to type of case
                        settings=self.avl_settings)

    @Part
    def avl_analysis(self):
        return avl.Interface(configuration=self.avl_configuration,
                             # note: AVL always expects a list of cases!
                             cases=[self.avl_case])

    @Attribute
    def l_over_d(self):
        """process AVL results and compute L/D"""
        # Since AVL always receives a list of cases, but produces a dictionary of
        # results (using the name supplied to avl.Case as key)
        # each result is itself a nested dictionary, containing a lot of
        # information so it's a good idea to extract the relevant numbers
        # as @Attributes
        return {result['Name']: result['Totals']['CLtot'] / result['Totals']['CDtot']
                for case_name, result in self.avl_analysis.results.items()}
        # The above is a bit more complicated than needed since there's only
        # a single case name etc., but addressing it "by name" means we'd need
        # to update the definition above every time we change something in the
        # analysis.


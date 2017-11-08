""" Directional waveguide couplers for intra- and inter-modal coupling.

These consist of two parallel waveguides that allow evenescent coupling (partial/complete)
from one waveguide to the other.

"""


from ipkiss3 import all as i3
from picazzo3.filters.mmi.cell import MMI2x2Tapered
from picazzo3.traces.wire_wg.trace import WireWaveguideTemplate
from euler_rounding_algorithm import Euler90Algorithm
from euler_rounding_algorithm import EulerArbAlgorithm
from ipkiss.geometry.shapes.modifiers import ShapeRound
from picazzo3.wg.dircoup import StraightDirectionalCoupler
from ipcore.properties.descriptor import DefinitionProperty
import numpy as np


class Bent_Coupler_Symm(i3.PCell):
    """ A coupler with symmetric bends on each of the ports. Used with generic PCell
    """
    _name_prefix = "Bent_Coupler_Symm"

    # defining MMI as child cell with input and output waveguides
    coupler = i3.ChildCellProperty(restriction=i3.RestrictType(i3.PCell))

    # define waveguide template and waveguide cells
    # for the access bent waveguides connected to the straight couple
    ## add another waveguide template
    # coupler_length = i3.PositiveNumberProperty(default=i3.TECH.WG.SHORT_STRAIGHT,
    #                                            doc="length of the directional coupler")

    wg_template1 = i3.WaveguideTemplateProperty(default=i3.TECH.PCELLS.WG.DEFAULT)
    wg_template2 = i3.WaveguideTemplateProperty(default=i3.TECH.PCELLS.WG.DEFAULT)
    # wg_template = i3.WaveguideTemplateProperty(default=i3.TECH.PCELLS.WG.DEFAULT)
    wgs = i3.ChildCellListProperty(doc="list of waveguides")

    def _default_wg_template2(self):
        return self.wg_template1
    # define default coupler for class
    # a straight directional coupler by default
    # can also insert a tapered MMI by assigning a MMI PCell
    ### pass the templates for the directional coupler
    def _default_coupler(self):
        ### waveguide templates for DC must be defined in this instantiance
        ### otherwise trace_template1 and trace_template2 will be set bundled to be equal
        coupler = StraightDirectionalCoupler(name=self.name+"_dir_coup",
                                             coupler_length=self.coupler_length)
        return coupler

    # define rounded waveguides for the inputs and outputs
    ## can consider for loop tp reduce the code length
    def _default_wgs(self):
        wgs = []
        name_list = ["_wg_in1", "_wg_in2", "_wg_out1", "_wg_out2"]
        template_list = [self.wg_template1, self.wg_template2, self.wg_template1, self.wg_template2]
        for idx, name in enumerate(name_list):
            wg = i3.RoundedWaveguide(name=self.name+name_list[idx], trace_template=template_list[idx])
            wgs.append(wg)
        return wgs
        

    class Layout(i3.LayoutView):
        # specified parameters used for layout purposes
        ## coupling spacing?
        ## move to the coupler level
        bend_radius = i3.PositiveNumberProperty(default=10., doc="bend radius of 90 degree bends")
        in1_offset = i3.PositiveNumberProperty(default=10., doc="offset between 90 degree bends input 1")
        in2_offset = i3.PositiveNumberProperty(default=10., doc="offset between 90 degree bends input 2")
        out1_offset = i3.PositiveNumberProperty(default=1., doc="offset between 90 degree bends output 1")
        out2_offset = i3.PositiveNumberProperty(default=1., doc="offset between 90 degree bends output 2")
        rounding_algorithm = DefinitionProperty(default=ShapeRound, doc="rounding algorithm for every individual bend")

        # define default of tapered MMI child cell
        def _default_coupler(self):
            ### error to be corrected. the Child Layout view needs to point to coupler first, end get the default view
            # wg_template1 = self.wg_template1
            coupler = self.cell.coupler.get_default_view(i3.LayoutView)  # Retrieve layout view following examples
            ### go to upper level then to define the waveguide template, as the waveguide template of DC is NOT
            ### defined in layout level
            # self.cell.coupler.trace_template1 = self.wg_template1
            # self.cell.coupler.trace_template2 = self.wg_template2
            return coupler

        # grabbing properties of child cell and setting appropriate transforms, by default do none
        def _get_components(self):
            coupler = i3.SRef(reference=self.coupler, name="coupler")
            return coupler

        # setting the output shape of the access waveguides using a shape defined by ports from MMI (hopefully..)
        def _default_wgs(self):

            # bring in parts from rest of PCell Layout, used to grab positions
            coupler = self._get_components()
            ## wgcell ? for loop operation
            wg_in1_cell, wg_in2_cell, wg_out1_cell, wg_out2_cell = self.cell.wgs
            wg_template1 = self.wg_template1
            wg_template2 = self.wg_template2
            bend_radius = self.bend_radius
            # setting variable for
            round_alg = self.rounding_algorithm

            # defining bottom left waveguide, using port from MMI and bus length
            wg_in1_layout = wg_in1_cell.get_default_view(i3.LayoutView)
            in1_port_pos = coupler.ports["in1"].position
            in1_shape = [in1_port_pos,
                         (in1_port_pos[0] - bend_radius, in1_port_pos[1]),
                         (in1_port_pos[0] - bend_radius, in1_port_pos[1] - 2.*bend_radius - self.in1_offset),
                         (in1_port_pos[0] - 2.*bend_radius, in1_port_pos[1] - 2.*bend_radius - self.in1_offset)]

            wg_in1_layout.set(trace_template=wg_template1, shape=in1_shape,
                              rounding_algorithm = round_alg, bend_radius=bend_radius,
                              manhattan = True)

            # repeat above for other ports, first in2
            wg_in2_layout = wg_in2_cell.get_default_view(i3.LayoutView)
            in2_port_pos = coupler.ports["in2"].position
            in2_shape = [in2_port_pos,
                         (in2_port_pos[0] - bend_radius, in2_port_pos[1]),
                         (in2_port_pos[0] - bend_radius, in2_port_pos[1] + 2.*bend_radius + self.in2_offset),
                         (in2_port_pos[0] - 2.*bend_radius, in2_port_pos[1] + 2.*bend_radius + self.in2_offset)]

            wg_in2_layout.set(trace_template=wg_template2, shape=in2_shape,
                              rounding_algorithm=round_alg, bend_radius=bend_radius,
                              manhattan = True)

            # out1
            wg_out1_layout = wg_out1_cell.get_default_view(i3.LayoutView)
            out1_port_pos = coupler.ports["out1"].position
            out1_shape = [out1_port_pos,
                          (out1_port_pos[0] + bend_radius, out1_port_pos[1]),
                          (out1_port_pos[0] + bend_radius, out1_port_pos[1] - 2.*bend_radius - self.out1_offset),
                          (out1_port_pos[0] + 2.*bend_radius, out1_port_pos[1] - 2.*bend_radius - self.out1_offset)]

            wg_out1_layout.set(trace_template=wg_template1, shape=out1_shape,
                               rounding_algorithm=round_alg, bend_radius=bend_radius,
                               manhattan = True)
            # and out2
            wg_out2_layout = wg_out2_cell.get_default_view(i3.LayoutView)
            out2_port_pos = coupler.ports["out2"].position
            out2_shape = [out2_port_pos,
                          (out2_port_pos[0] + bend_radius, out2_port_pos[1]),
                          (out2_port_pos[0] + bend_radius, out2_port_pos[1] + 2.*bend_radius + self.out2_offset),
                          (out2_port_pos[0] + 2.*bend_radius, out2_port_pos[1] + 2.*bend_radius + self.out2_offset)]

            wg_out2_layout.set(trace_template=wg_template2, shape=out2_shape,
                               rounding_algorithm=round_alg, bend_radius=bend_radius,
                               manhattan=True)
            # returning layouts
            return wg_in1_layout, wg_in2_layout, wg_out1_layout, wg_out2_layout

        def _generate_instances(self, insts):
            # includes the get components and the new waveguides
            insts += self._get_components()
            wg_in1_layout, wg_in2_layout, wg_out1_layout, wg_out2_layout = self.wgs

            insts += i3.SRef(reference=wg_in1_layout, name="wg_in1")
            insts += i3.SRef(reference=wg_in2_layout, name="wg_in2")
            insts += i3.SRef(reference=wg_out1_layout, name="wg_out1")
            insts += i3.SRef(reference=wg_out2_layout, name="wg_out2")
            return insts

        def _generate_ports(self, prts):
            # use output ports of all waveguides as I define shapes from the base of the coupler structure outwards
            instances = self.instances
            prts += instances["wg_in1"].ports["out"].modified_copy(name="in1")
            prts += instances["wg_in2"].ports["out"].modified_copy(name="in2")
            prts += instances["wg_out1"].ports["out"].modified_copy(name="out1")
            prts += instances["wg_out2"].ports["out"].modified_copy(name="out2")
            return prts
        ### an simple example to use Ben_Coupler_Symm class
        @i3.example_plot()
        def __example_layout(self):
            from technologies import silicon_photonics
            from picazzo3.traces.wire_wg.trace import WireWaveguideTemplate
            import ipkiss3.all as i3
            import numpy as np
            from euler_rounding_algorithm import Euler90Algorithm
            from SplittersAndCascades import Bent_Coupler_Symm

            # set waveguide templates for
            # the north waveguide (wg_t1)
            # and the south waveguide (wg_t2)
            wg_t1 = WireWaveguideTemplate(name="south_arm")
            wg_t1.Layout(core_width=2.400,
                         cladding_width=i3.TECH.WG.CLADDING_WIDTH,
                         core_process=i3.TECH.PROCESS.WG)

            wg_t2 = WireWaveguideTemplate(name="north arm")
            wg_t2.Layout(core_width=1.500,
                         cladding_width=i3.TECH.WG.CLADDING_WIDTH,
                         core_process=i3.TECH.PROCESS.WG)

            # set the directional coupler (can also be MMI)
            # and then pass it as an child PCell to Bend_Coupler PCell
            C = Bent_Coupler_Symm(name="my_dircoup_2",
                                   trace_template1=wg_t1,
                                   trace_template2=wg_t2,
                                   coupler_length=20.0)
            layout = C.Layout(bend_radius=10.0,
                              straight_after_bend=6.0,
                              bend_angle=60.0)
            layout.visualize()

# inherit bend

class Bent_Coupler_Arb(Bent_Coupler_Symm):
    """
    S_Bent_Coupler with 90 degree bent angles
    
    add control parameters
    :param in1_bent: bent or straight for in1 bent, '1' bent, '0' straight
    :param in2_bent: bent or straight for in2 bent
    :param out1_bent: bent or straight for out1 bent
    :param out2_bent: bent or straight for out2 bent
    """

    class Layout(Bent_Coupler_Symm.Layout):
        # booleans for bent or not bent
        in1_bent = i3.BoolProperty(default=True, doc="bending in1 or not")
        in2_bent = i3.BoolProperty(default=False, doc="bending in2 or not")
        out1_bent = i3.BoolProperty(default=False, doc="bending out1 or not")
        out2_bent = i3.BoolProperty(default=False, doc="bending out2 or not")

        # define default of tapered MMI child cell
        def _default_coupler(self):
            coupler = self.cell.coupler.get_default_view(i3.LayoutView)  # Retrieve layout view following example
            # coupler.set(coupler_spacing=1.0, coupler_length=10., trace_template=self.wg_template)
            return coupler

        # grabbing properties of child cell and setting appropriate transforms, by default do none
        def _get_components(self):
            coupler = i3.SRef(reference=self.coupler, name="coupler")
            return coupler

        # setting the output shape of the access waveguides using a shape defined by ports from MMI (hopefully..)
        def _default_wgs(self):

            # bring in parts from rest of PCell Layout, used to grab positions
            coupler = self._get_components()
            wg_in1_cell, wg_in2_cell, wg_out1_cell, wg_out2_cell = self.cell.wgs
            wg_template1 = self.wg_template1
            wg_template2 = self.wg_template2
            bend_radius = self.bend_radius
            # setting variable for
            round_alg = self.rounding_algorithm

            # defining bottom left waveguide, using port from MMI and bus length
            wg_in1_layout = wg_in1_cell.get_default_view(i3.LayoutView)
            in1_port_pos = coupler.ports["in1"].position
            in1_shape = [in1_port_pos,
                         (in1_port_pos[0] - bend_radius, in1_port_pos[1]),
                         (in1_port_pos[0] - bend_radius, in1_port_pos[1] - 2.*bend_radius - self.in1_offset),
                         (in1_port_pos[0] - 2.*bend_radius, in1_port_pos[1] - 2.*bend_radius - self.in1_offset)]
            # bool section
            in1_shape_straight = [in1_port_pos, (in1_port_pos[0] - 2.*bend_radius, in1_port_pos[1])]

            if self.in1_bent is False:
                in1_arb_shape = in1_shape_straight
            else:
                in1_arb_shape = in1_shape

            wg_in1_layout.set(trace_template=wg_template1, shape=in1_arb_shape,
                              rounding_algorithm=round_alg, bend_radius=bend_radius)

            # repeat above for other ports, first in2
            wg_in2_layout = wg_in2_cell.get_default_view(i3.LayoutView)
            in2_port_pos = coupler.ports["in2"].position
            in2_shape = [in2_port_pos,
                         (in2_port_pos[0] - bend_radius, in2_port_pos[1]),
                         (in2_port_pos[0] - bend_radius, in2_port_pos[1] + 2.*bend_radius + self.in2_offset),
                         (in2_port_pos[0] - 2.*bend_radius, in2_port_pos[1] + 2.*bend_radius + self.in2_offset)]

            # bool section in2
            in2_shape_straight = [in2_port_pos, (in2_port_pos[0] - 2. * bend_radius, in2_port_pos[1])]

            if self.in2_bent is False:
                in2_arb_shape = in2_shape_straight
            else:
                in2_arb_shape = in2_shape

            wg_in2_layout.set(trace_template=wg_template2, shape=in2_arb_shape,
                              rounding_algorithm=round_alg, bend_radius=bend_radius)

            # out1
            wg_out1_layout = wg_out1_cell.get_default_view(i3.LayoutView)
            out1_port_pos = coupler.ports["out1"].position
            out1_shape = [out1_port_pos,
                          (out1_port_pos[0] + bend_radius, out1_port_pos[1]),
                          (out1_port_pos[0] + bend_radius, out1_port_pos[1] - 2.*bend_radius - self.out1_offset),
                          (out1_port_pos[0] + 2.*bend_radius, out1_port_pos[1] - 2.*bend_radius - self.out1_offset)]

            # bool section out1
            out1_shape_straight = [out1_port_pos, (out1_port_pos[0] + 2. * bend_radius, out1_port_pos[1])]

            if self.out1_bent is False:
                out1_arb_shape = out1_shape_straight
            else:
                out1_arb_shape = out1_shape

            wg_out1_layout.set(trace_template=wg_template1, shape=out1_arb_shape,
                               rounding_algorithm=round_alg, bend_radius=bend_radius)
            # and out2
            wg_out2_layout = wg_out2_cell.get_default_view(i3.LayoutView)
            out2_port_pos = coupler.ports["out2"].position
            out2_shape = [out2_port_pos,
                          (out2_port_pos[0] + bend_radius, out2_port_pos[1]),
                          (out2_port_pos[0] + bend_radius, out2_port_pos[1] + 2.*bend_radius + self.out2_offset),
                          (out2_port_pos[0] + 2.*bend_radius, out2_port_pos[1] + 2.*bend_radius + self.out2_offset)]

            # bool section out2
            out2_shape_straight = [out2_port_pos, (out2_port_pos[0] + 2. * bend_radius, out2_port_pos[1])]

            if self.out2_bent is False:
                out2_arb_shape = out2_shape_straight
            else:
                out2_arb_shape = out2_shape

            wg_out2_layout.set(trace_template=wg_template2, shape=out2_arb_shape,
                               rounding_algorithm=round_alg, bend_radius=bend_radius)
            # returning layouts
            return wg_in1_layout, wg_in2_layout, wg_out1_layout, wg_out2_layout

        @i3.example_plot()
        def __example_layout(self):
            from technologies import silicon_photonics
            from picazzo3.traces.wire_wg.trace import WireWaveguideTemplate
            import ipkiss3.all as i3
            import numpy as np
            from euler_rounding_algorithm import Euler90Algorithm
            from SplittersAndCascades import Bent_Coupler_Symm
            # wg_t1: waveguide template of the south arm
            # wg_t2: waveguide template of the north arm
            # define the template, set the core waveguide width
            wg_t1 = WireWaveguideTemplate(name="south_arm")
            wg_t1.Layout(core_width=2.400,
                         cladding_width=i3.TECH.WG.CLADDING_WIDTH,
                         core_process=i3.TECH.PROCESS.WG)

            wg_t2 = WireWaveguideTemplate(name="north arm")
            wg_t2.Layout(core_width=1.500,
                         cladding_width=i3.TECH.WG.CLADDING_WIDTH,
                         core_process=i3.TECH.PROCESS.WG)
            DC = StraightDirectionalCoupler(name="Directional coupler",
                                            trace_template1=wg_t1,
                                            trace_template2=wg_t2,
                                            coupler_length=50.0)

            layout_DC = DC.Layout(coupler_spacing=10.0)

            C = Bent_Coupler_Arb(name="modal_coupler",
                             wg_template1=wg_t1,
                             wg_template2=wg_t2,
                             coupler=DC)
            # in1_bent...out2_bent booleans for bent control
            layout = C.Layout(bend_radius=30.0,
                              in1_bent=True,
                              in2_bent=True,
                              out1_bent=True,
                              out2_bent=True,
                              rounding_algorithm=ShapeRound)
            layout.visualize()


class S_Bend_Coupler_Arb(Bent_Coupler_Arb):
    """
    S_Bent_Coupler with Arbitrary degree bent angles,
    and straight connection in the S bend,
    and straight waveguide after the Sbend

    add control parameters
    :param bend_angle_deg: bend angle
    :param s_bend_straight: straight connection in the S bend
    :param straight_after_bend: straight waveguide after the S bend
    """

    class Layout(Bent_Coupler_Arb.Layout):
        # S bend related parameters
        bend_angle_deg = i3.PositiveNumberProperty(default=15., doc="bend angle of S Bend")
        s_bend_straight = i3.PositiveNumberProperty(default=2., doc="straight length inside S Bend")
        straight_after_bend = i3.PositiveNumberProperty(default=1., doc="straight length after S Bend")


        # setting the output shape of the access waveguides using a shape defined by ports from MMI (hopefully..)
        def _default_wgs(self):

            # bring in parts from rest of PCell Layout, used to grab positions
            coupler = self._get_components()
            wg_in1_cell, wg_in2_cell, wg_out1_cell, wg_out2_cell = self.cell.wgs
            wg_template1 = self.wg_template1
            wg_template2 = self.wg_template2
            bend_radius = self.bend_radius
            sbend_straight = self.s_bend_straight
            straight_after_bend = self.straight_after_bend
            # setting variable for
            round_alg = self.rounding_algorithm

            # logic for calculating S bend positions
            bend_angle_rad = self.bend_angle_deg*(np.pi/180.)
            bend_x = bend_radius/np.tan((np.pi - bend_angle_rad)/2.)
            S_vertical_gap = np.sin(bend_angle_rad) * (2. * bend_x + sbend_straight)
            S_horizontal_gap = np.cos(bend_angle_rad) * (2. * bend_x + sbend_straight)

            # setting the points for the shape
            # turning_point_bot = (start[0] + bend_x + straight_after_bend, start[1])
            # turning_point_top = (turning_point_bot[0] + S_horizontal_gap, turning_point_bot[1] + S_vertical_gap)
            # end_point = (turning_point_top[0] + bend_x + straight_after_bend, turning_point_top[1])
            # S_shape = i3.Shape([start, turning_point_bot, turning_point_top, end_point])

            # defining bottom left waveguide, using port from coupler and bus length
            wg_in1_layout = wg_in1_cell.get_default_view(i3.LayoutView)
            in1_port_pos = coupler.ports["in1"].position
            in1_shape = [in1_port_pos,
                         (in1_port_pos[0] - bend_x, in1_port_pos[1]),
                         (in1_port_pos[0] - bend_x - S_horizontal_gap, in1_port_pos[1] - S_vertical_gap),
                         (in1_port_pos[0] - 2.*bend_x - S_horizontal_gap, in1_port_pos[1] - S_vertical_gap),
                         (in1_port_pos[0] - 2. * bend_x - S_horizontal_gap- straight_after_bend, in1_port_pos[1] - S_vertical_gap)]
            # bool section
            in1_shape_straight = [in1_port_pos, (in1_port_pos[0] - 2.*bend_x - S_horizontal_gap - straight_after_bend, in1_port_pos[1])]

            if self.in1_bent is False:
                in1_arb_shape = in1_shape_straight
            else:
                in1_arb_shape = in1_shape

            wg_in1_layout.set(trace_template=wg_template1, shape=in1_arb_shape,
                              rounding_algorithm=round_alg, bend_radius=bend_radius)

            # repeat above for other ports, first in2 with negative y values
            wg_in2_layout = wg_in2_cell.get_default_view(i3.LayoutView)
            in2_port_pos = coupler.ports["in2"].position
            in2_shape = [in2_port_pos,
                         (in2_port_pos[0] - bend_x, in2_port_pos[1]),
                         (in2_port_pos[0] - bend_x - S_horizontal_gap, in2_port_pos[1] + S_vertical_gap),
                         (in2_port_pos[0] - 2. * bend_x - S_horizontal_gap, in2_port_pos[1] + S_vertical_gap),
                         (in2_port_pos[0] - 2. * bend_x - S_horizontal_gap - straight_after_bend, in2_port_pos[1] + S_vertical_gap)]

            # bool section in2
            in2_shape_straight = [in2_port_pos, (in2_port_pos[0] - 2. * bend_x - S_horizontal_gap - straight_after_bend, in2_port_pos[1])]

            if self.in2_bent is False:
                in2_arb_shape = in2_shape_straight
            else:
                in2_arb_shape = in2_shape

            wg_in2_layout.set(trace_template=wg_template2, shape=in2_arb_shape,
                              rounding_algorithm=round_alg, bend_radius=bend_radius)

            # out1
            wg_out1_layout = wg_out1_cell.get_default_view(i3.LayoutView)
            out1_port_pos = coupler.ports["out1"].position
            out1_shape = [out1_port_pos,
                          (out1_port_pos[0] + bend_x, out1_port_pos[1]),
                          (out1_port_pos[0] + bend_x + S_horizontal_gap, out1_port_pos[1] - S_vertical_gap),
                          (out1_port_pos[0] + 2.*bend_x + S_horizontal_gap, out1_port_pos[1] - S_vertical_gap),
                          (out1_port_pos[0] + 2. * bend_x + S_horizontal_gap + straight_after_bend, out1_port_pos[1] - S_vertical_gap)]

            # bool section out1
            out1_shape_straight = [out1_port_pos, (out1_port_pos[0] + 2.*bend_x + S_horizontal_gap + straight_after_bend, out1_port_pos[1])]

            if self.out1_bent is False:
                out1_arb_shape = out1_shape_straight
            else:
                out1_arb_shape = out1_shape

            wg_out1_layout.set(trace_template=wg_template1, shape=out1_arb_shape,
                               rounding_algorithm=round_alg, bend_radius=bend_radius)
            # and out2
            wg_out2_layout = wg_out2_cell.get_default_view(i3.LayoutView)
            out2_port_pos = coupler.ports["out2"].position
            out2_shape = [out2_port_pos,
                          (out2_port_pos[0] + bend_x, out2_port_pos[1]),
                          (out2_port_pos[0] + bend_x + S_horizontal_gap, out2_port_pos[1] + S_vertical_gap),
                          (out2_port_pos[0] + 2. * bend_x + S_horizontal_gap, out2_port_pos[1] + S_vertical_gap),
                          (out2_port_pos[0] + 2. * bend_x + S_horizontal_gap + straight_after_bend, out2_port_pos[1] + S_vertical_gap)]

            # bool section out2
            out2_shape_straight = [out2_port_pos, (out2_port_pos[0] + 2. * bend_x + S_horizontal_gap + straight_after_bend, out2_port_pos[1])]

            if self.out2_bent is False:
                out2_arb_shape = out2_shape_straight
            else:
                out2_arb_shape = out2_shape

            wg_out2_layout.set(trace_template=wg_template2, shape=out2_arb_shape,
                               rounding_algorithm=round_alg, bend_radius=bend_radius)
            # returning layouts
            return wg_in1_layout, wg_in2_layout, wg_out1_layout, wg_out2_layout

        @i3.example_plot()
        def __example_layout(self):
            from technologies import silicon_photonics
            from picazzo3.traces.wire_wg.trace import WireWaveguideTemplate
            import ipkiss3.all as i3
            import numpy as np
            from euler_rounding_algorithm import EulerArbAlgorithm
            from SplittersAndCascades import Bent_Coupler_Symm

            # wg_t1: waveguide template of the south arm
            # wg_t2: waveguide template of the north arm
            # define the template, set the core waveguide width
            wg_t1 = WireWaveguideTemplate(name="south_arm")
            wg_t1.Layout(core_width=2.400,
                         cladding_width=i3.TECH.WG.CLADDING_WIDTH,
                         core_process=i3.TECH.PROCESS.WG)

            wg_t2 = WireWaveguideTemplate(name="north arm")
            wg_t2.Layout(core_width=1.500,
                         cladding_width=i3.TECH.WG.CLADDING_WIDTH,
                         core_process=i3.TECH.PROCESS.WG)
            DC = StraightDirectionalCoupler(name="Directional coupler",
                                            trace_template1=wg_t1,
                                            trace_template2=wg_t2,
                                            coupler_length=50.0)

            layout_DC = DC.Layout(coupler_spacing=10.0)

            C = S_Bend_Coupler_Arb(name="modal_coupler",
                                   wg_template1=wg_t1,
                                   wg_template2=wg_t2,
                                   coupler=DC)

            layout = C.Layout(bend_radius=30.0,
                              bend_angle_deg=60.0,
                              s_bend_straight=10.0,
                              straight_after_bend=50.0,
                              in1_bent=True,
                              in2_bent=True,
                              out1_bent=False,
                              out2_bent=True,
                              rounding_algorithm=EulerArbAlgorithm)

            layout.visualize()


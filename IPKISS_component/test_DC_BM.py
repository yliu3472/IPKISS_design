"""
Test file for creating components for lumerical sweeps using the base directional coupler (no tapers etc)
"""

from technologies import silicon_photonics
# from picazzo3.wg.dircoup import SBendDirectionalCoupler
from picazzo3.traces.wire_wg.trace import WireWaveguideTemplate
from ipkiss3.all import SplineRoundingAlgorithm
import ipkiss3.all as i3
import numpy as np
# from mode_coupler_YL import SBendDirectionalCoupler
from euler_rounding_algorithm import EulerArbAlgorithm
# from euler_rounding_algorithm import Euler90Algorithm
from ipkiss.geometry.shapes.modifiers import ShapeRound
import ipkiss3.all as i3
from picazzo3.wg.dircoup import StraightDirectionalCoupler
from Directional_Coupler import S_Bend_Coupler_Arb


# Widths for waveguides and cladding

coupling_wg_width = 0.9
main_wg_width = 1.9
cladding_width = 5.

coupler_gap = 0.5
coupler_length = 100.

wg_t2 = WireWaveguideTemplate(name="north_arm")
wg_t2.Layout(core_width=coupling_wg_width,
             cladding_width=cladding_width,
             core_process=i3.TECH.PROCESS.WG)

wg_t1 = WireWaveguideTemplate(name="south_arm")
wg_t1.Layout(core_width=main_wg_width,
             cladding_width=cladding_width,
             core_process=i3.TECH.PROCESS.WG)

# DC = SBendDirectionalCoupler(trace_template1=wg_t2,
#                              trace_template2=wg_t1,
#                              coupler_length=20.0)
#
# DC_layout = DC.Layout(coupler_spacing=1.4+0.5,
#                       bend_radius=25.0,
#                       bend_angles1=(0.0, 0.0),
#                       bend_angles2=(15.0, 15.0),
#                       straight_after_bend=10.0,
#                       rounding_algorithm=ShapeRound,
#                       manhattan=False)

DC = StraightDirectionalCoupler(name="Directional coupler",
                                trace_template1=wg_t1,
                                trace_template2=wg_t2,
                                coupler_length=coupler_length)

layout_DC = DC.Layout(coupler_spacing=main_wg_width/2. + coupling_wg_width/2. + coupler_gap)

C = S_Bend_Coupler_Arb(name="modal_coupler",
                       wg_template1=wg_t1,
                       wg_template2=wg_t2,
                       coupler=DC)

layout = C.Layout(bend_radius=30.0,
                  bend_angle_deg=15.0,
                  s_bend_straight=1.0,
                  straight_after_bend=10.0,
                  in1_bent=False,
                  in2_bent=True,
                  out1_bent=False,
                  out2_bent=True,
                  rounding_algorithm=EulerArbAlgorithm)
# DC_layout.visualize()
print layout.ports
layout.write_gdsii("DC_Test_BM.gds")

# circuit_layout.write_gdsii("test.gds")
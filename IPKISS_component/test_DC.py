from technologies import silicon_photonics
# from picazzo3.wg.dircoup import SBendDirectionalCoupler
from picazzo3.traces.wire_wg.trace import WireWaveguideTemplate
from ipkiss3.all import SplineRoundingAlgorithm
import ipkiss3.all as i3
import numpy as np
from mode_coupler_YL import SBendDirectionalCoupler
from euler_rounding_algorithm import EulerArbAlgorithm
# from euler_rounding_algorithm import Euler90Algorithm
from ipkiss.geometry.shapes.modifiers import ShapeRound

import ipkiss3.all as i3


from picazzo3.wg.dircoup import SBendDirectionalCoupler
from euler_rounding_algorithm import EulerArbAlgorithm

wg_t1 = WireWaveguideTemplate(name="south_arm")
wg_t1.Layout(core_width=0.85,
             cladding_width=1.35,
             core_process=i3.TECH.PROCESS.WG)

wg_t2 = WireWaveguideTemplate(name="north_arm")
wg_t2.Layout(core_width=0.85,
             cladding_width=1.35,
             core_process=i3.TECH.PROCESS.WG)

from picazzo3.wg.dircoup import StraightDirectionalCoupler
from Directional_Coupler import S_Bend_Coupler_Arb
DC = StraightDirectionalCoupler(name="Directional coupler",
                                trace_template1=wg_t1,
                                trace_template2=wg_t2,
                                coupler_length=400.0)
layout_DC = DC.Layout(coupler_spacing=0.85+0.85)

C = S_Bend_Coupler_Arb(name="modal_coupler",
                                   wg_template1=wg_t2,
                                   wg_template2=wg_t1,
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

layout.write_gdsii("DC400.gds")

# circuit_layout.write_gdsii("test.gds")
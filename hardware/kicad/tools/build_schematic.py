"""Builds powerlenz.kicad_sch from code. Run from hardware/kicad:  python3 tools/build_schematic.py

Connections are made with net labels and power symbols. Blocks are added one at a time.
"""
import os
import sys

sys.path.insert(0, os.path.dirname(__file__))
from kicad_gen import Schematic

OUT = os.path.join(os.path.dirname(__file__), "..", "powerlenz.kicad_sch")
s = Schematic("PowerLenz: single-phase NILM front end", paper="A3")


def block1_mains():
    """Mains input, fuse, MOV, ZMPT107-1 primary string and the HLK-5M05 isolated 5 V supply."""
    s.box(12.7, 15.24, 275, 132)
    s.text("1. MAINS INPUT, PROTECTION AND ISOLATED 5 V   (230 V AC on the left of the isolation barrier: hazardous)", 15.24, 22, 2.0, True)
    y = 60.96
    s.part("Connector", "Screw_Terminal_01x02", "Mains in", (33.02, y), {1: "L_IN", 2: "N"}, prefix="J",
           extra={"Note": "Pin 1 = live, pin 2 = neutral"})
    s.part("Device", "Fuse", "1A T 250V", (68.58, y), {1: "L_IN", 2: "L_FUSED"}, prefix="F", rot=90,
           extra={"MPN": "5HT 1-R", "Manufacturer": "Bel Fuse",
                  "Note": "Ceramic time-lag, listed 1.5 kA at 250 VAC; Bel datasheet not yet read"})
    s.part("Device", "Varistor", "10D561K", (101.6, y), {1: "L_FUSED", 2: "N"}, prefix="RV", rot=90,
           extra={"MPN": "MOV-10D561K", "Manufacturer": "Bourns", "Note": "350 VAC / 460 VDC, 2.5 kA, 70 J"})
    # ZMPT107-1 primary string: 3 x 39 k in series = 117 k (about 2 mA at 230 V)
    s.part("Device", "R", "39k 1% 1/2W", (132.08, y), {1: "L_FUSED", 2: "ZP1"}, prefix="R", rot=90,
           extra={"MPN": "MF50 39K", "Note": "Series string R1-R3 sets about 2 mA through the ZMPT107-1 primary"})
    s.part("Device", "R", "39k 1% 1/2W", (157.48, y), {1: "ZP1", 2: "ZP2"}, prefix="R", rot=90,
           extra={"MPN": "MF50 39K"})
    s.part("Device", "R", "39k 1% 1/2W", (182.88, y), {1: "ZP2", 2: "ZA_P"}, prefix="R", rot=90,
           extra={"MPN": "MF50 39K"})
    s.part("Device", "Transformer_1P_1S", "ZMPT107-1", (228.6, y), {1: "ZA_P", 2: "N", 4: "V_P", 3: "V_N"}, prefix="T",
           extra={"Manufacturer": "Zeming", "Note": "2 mA : 2 mA, 3000 V isolated. Windings are interchangeable (1000:1000); "
                  "physical pins 1*,2 = one winding and 3*,4 = the other. Channel sign is fixed in firmware."})
    s.text("ZMPT107-1: left = mains side, right = isolated sensing side", 205.74, 40.64, 1.27)
    y2 = 104.14
    s.part("Device", "C", "0.1uF X2 275VAC", (101.6, y2), {1: "L_FUSED", 2: "N"}, prefix="C", dnp=True,
           extra={"Note": "Only if certifying (Hi-Link datasheet); with a 10-30 mH common-mode choke at the module input"})
    s.part("Converter_ACDC", "HLK-5M05", "HLK-5M05", (160.02, y2), {1: "L_FUSED", 2: "N", 3: "GND", 4: "+5V"}, prefix="PS",
           extra={"Manufacturer": "Hi-Link", "Note": "Isolation rating 3000 V or 2500 V unresolved; fuse 1 A (text) vs 0.5 A (figure)"},
           flags=(1, 2))
    s.part("Device", "C_Polarized", "220uF 25V", (198.12, y2), {1: "+5V", 2: "GND"}, prefix="C",
           extra={"Note": "HLK-5M05 output capacitor; its datasheet recommends 100-220 uF"})
    s.text("HLK-5M05 -Vout is the isolated low-voltage ground (GND)", 177.8, 124.46, 1.27)


block1_mains()
s.save(OUT)
print("wrote", os.path.abspath(OUT))

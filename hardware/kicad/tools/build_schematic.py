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


def block2_analog():
    """CT burden, ZMPT107-1 sampling resistors and the input chain for CH1 (current) and CH2 (voltage).

    Per ADC input pin: 1 kohm, clamp node (BAT54 to AVDD, BAV199 pair to GND), 100 ohm, ADC pin (TI SBAA506).
    10 nF C0G across each channel's pair, after the 100 ohm resistors.
    """
    s.box(12.7, 137.16, 275, 290)
    s.text("2. ANALOG FRONT END: BURDEN, SAMPLING RESISTORS AND ADC INPUT PROTECTION (low voltage, isolated side)", 15.24, 144, 2.0, True)
    yi = 160.02
    s.text("CT current sensor: burden 2 x 6.49 ohm, midpoint to GND", 15.24, 152.4, 1.27)
    s.part("Connector", "Screw_Terminal_01x02", "CT SCT-013-000", (25.4, yi), {1: "CT_P", 2: "CT_N"}, prefix="J",
           extra={"Note": "Current-output CT (100 A : 50 mA). Never leave the CT secondary open"})
    s.part("Device", "R", "6.49R 1%", (68.58, yi), {1: "CT_P", 2: "GND"}, prefix="R", rot=90,
           extra={"MPN": "CRCW12066R49FKEA", "Manufacturer": "Vishay", "Note": "Burden half; 2 x 6.49 = 12.98 ohm"})
    s.part("Device", "R", "6.49R 1%", (96.52, yi), {1: "GND", 2: "CT_N"}, prefix="R", rot=90,
           extra={"MPN": "CRCW12066R49FKEA", "Manufacturer": "Vishay"})
    s.text("ZMPT107-1 sampling: 2 x 24.9 ohm = about 50 ohm, midpoint to GND", 134.62, 152.4, 1.27)
    s.part("Device", "R", "24.9R 1%", (160.02, yi), {1: "V_P", 2: "GND"}, prefix="R", rot=90,
           extra={"MPN": "RC0805FR-0724R9L", "Manufacturer": "Yageo", "Note": "Sampling resistor half"})
    s.part("Device", "R", "24.9R 1%", (187.96, yi), {1: "GND", 2: "V_N"}, prefix="R", rot=90,
           extra={"MPN": "RC0805FR-0724R9L", "Manufacturer": "Yageo"})

    legs = [  # (row y, input net, clamp node, mid net, ADC net, label)
        (190.5, "CT_P", "CT_P_C", "CT_P_M", "CH1P", "CH1 current, + leg"),
        (215.9, "CT_N", "CT_N_C", "CT_N_M", "CH1N", "CH1 current, - leg"),
        (241.3, "V_P", "V_P_C", "V_P_M", "CH2P", "CH2 voltage, + leg"),
        (266.7, "V_N", "V_N_C", "V_N_M", "CH2N", "CH2 voltage, - leg"),
    ]
    for y, inn, node, mid, adc, title in legs:
        s.text(title, 15.24, y - 6.5, 1.27)
        s.part("Device", "R", "1k 1%", (63.5, y), {1: inn, 2: node}, prefix="R", rot=90,
               extra={"MPN": "RC0805FR-071KL", "Manufacturer": "Yageo", "Note": "Input filter resistor (TI SBAA506 R1)"})
        s.part("Device", "D_Schottky", "BAT54", (104.14, y), {2: node, 1: "+3V3A"}, prefix="D",
               extra={"MPN": "BAT54-7-F", "Manufacturer": "Diodes Inc",
                      "Note": "Clamps positive overstress to AVDD. SOT-23 pin mapping to be checked in the BAT54 datasheet"})
        s.part("Device", "D", "BAV199 (a)", (139.7, y), {2: "GND", 1: mid}, prefix="D",
               extra={"MPN": "BAV199-7-F", "Manufacturer": "Diodes Inc",
                      "Note": "One BAV199 package = two series diodes (this and the next). Pin mapping to be checked in its datasheet"})
        s.part("Device", "D", "BAV199 (b)", (175.26, y), {2: mid, 1: node}, prefix="D",
               extra={"MPN": "BAV199-7-F", "Manufacturer": "Diodes Inc"})
        s.part("Device", "R", "100R 1%", (210.82, y), {1: node, 2: adc}, prefix="R", rot=90,
               extra={"MPN": "RC0805FR-07100RL", "Manufacturer": "Yageo", "Note": "TI SBAA506 R2; not yet priced"})
    s.part("Device", "C", "10nF C0G", (254, 203.2), {1: "CH1P", 2: "CH1N"}, prefix="C",
           extra={"MPN": "0805N103J500CT", "Manufacturer": "Walsin", "Note": "C0G, 5%, 50 V. Across the CH1 pair, after the 100 ohm resistors"})
    s.part("Device", "C", "10nF C0G", (254, 254), {1: "CH2P", 2: "CH2N"}, prefix="C",
           extra={"MPN": "0805N103J500CT", "Manufacturer": "Walsin", "Note": "C0G, 5%, 50 V. Across the CH2 pair, after the 100 ohm resistors"})
    s.text("Differential corner about 7.2 kHz (1.1 kohm per leg); same on both channels so the phase lags cancel", 15.24, 284, 1.27)
    s.text("TI clamp per pin: BAT54 to AVDD (+3V3A) and a BAV199 pair to GND, between the 1 kohm and 100 ohm resistors", 15.24, 288, 1.27)


block1_mains()
block2_analog()
s.save(OUT)
print("wrote", os.path.abspath(OUT))

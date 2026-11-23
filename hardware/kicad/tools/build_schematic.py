"""Builds powerlenz.kicad_sch from code. Run from hardware/kicad:  python3 tools/build_schematic.py

Connections are made with net labels and power symbols. Blocks are added one at a time.
"""
import os
import sys

sys.path.insert(0, os.path.dirname(__file__))
from kicad_gen import Schematic

OUT = os.path.join(os.path.dirname(__file__), "..", "powerlenz.kicad_sch")
s = Schematic("PowerLenz: single-phase NILM front end", paper="A2")


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



def block3_adc_power():
    """ADS131M04 with decoupling, and the LP5907 3.3 V supply for AVDD and DVDD."""
    s.box(292.1, 15.24, 560, 160)
    s.text("3. ADS131M04 ADC AND 3.3 V SUPPLY (LP5907)", 294.64, 22, 2.0, True)
    # LP5907 supply from the HLK 5 V rail
    s.text("LP5907: quiet 3.3 V for AVDD and DVDD (HLK ripple rejected about 60 dB at 100 kHz)", 294.64, 30, 1.27)
    s.part("Regulator_Linear", "LP5907MFX-3.3", "LP5907-3.3", (332.74, 55.88), {1: "+5V", 3: "~+5V", 5: "~+3V3A", 2: "GND"},
           prefix="U", nc=(4,), extra={"MPN": "LP5907MFX-3.3/NOPB", "Manufacturer": "Texas Instruments",
                                       "Note": "250 mA, under 6.5 uV rms noise; EN tied to IN"})
    s.part("Device", "C", "1uF 50V X7R", (304.8, 68.58), {1: "+5V", 2: "GND"}, prefix="C",
           extra={"MPN": "CC0805KKX7R9BB105", "Manufacturer": "Yageo", "Note": "LP5907 input capacitor, 1 uF ceramic"})
    s.part("Device", "C", "1uF 50V X7R", (368.3, 68.58), {1: "+3V3A", 2: "GND"}, prefix="C",
           extra={"MPN": "CC0805KKX7R9BB105", "Manufacturer": "Yageo", "Note": "LP5907 output capacitor, 1 uF ceramic"})
    # ADC
    s.part("Analog_ADC", "ADS131M04xPW", "ADS131M04", (449.58, 91.44),
           {1: "~+3V3A", 20: "~+3V3A", 2: "~GND", 19: "~GND",
            6: "CH1P", 5: "CH1N", 7: "CH2P", 8: "CH2N",
            3: "~GND", 4: "~GND", 10: "~GND", 9: "~GND",
            18: "ADC_CAP", 14: "ADC_SCLK", 16: "ADC_DIN", 15: "ADC_DOUT", 12: "ADC_CS",
            13: "ADC_DRDY", 17: "ADC_CLKIN", 11: "ADC_RESET"},
           prefix="U", extra={"MPN": "ADS131M04IPWR", "Manufacturer": "Texas Instruments",
                              "Note": "TSSOP-20. CH1 = current (gain 1), CH2 = voltage (gain 2). CH0 and CH3 unused: "
                                      "inputs tied to AGND (datasheet allows floating or AGND). 8 kSPS, continuous-conversion mode"})
    s.part("Device", "C", "1uF 50V X7R", (406.4, 55.88), {1: "+3V3A", 2: "GND"}, prefix="C",
           extra={"MPN": "CC0805KKX7R9BB105", "Manufacturer": "Yageo", "Note": "AVDD decoupling, place at the pin"})
    s.part("Device", "C", "1uF 50V X7R", (492.76, 55.88), {1: "+3V3A", 2: "GND"}, prefix="C",
           extra={"MPN": "CC0805KKX7R9BB105", "Manufacturer": "Yageo", "Note": "DVDD decoupling, place at the pin"})
    s.part("Device", "C", "220nF 50V X7R", (505.46, 109.22), {1: "ADC_CAP", 2: "GND"}, prefix="C",
           extra={"MPN": "0805B224K500CT", "Manufacturer": "Walsin", "Note": "CAP pin to DGND, required by the datasheet (DVDD above 2.7 V)"})
    s.text("Channels: CH1 current, CH2 voltage. AGND and DGND are joined here (one GND net)", 294.64, 150, 1.27)
    s.text("ADC to MCU: SCLK, DIN, DOUT, CS, DRDY, CLKIN, SYNC/RESET (nets ADC_*)", 294.64, 154, 1.27)



def block4_header():
    """Header carrying the ADC control signals and the 5 V supply to the ESP32-S3 DevKitC."""
    s.box(292.1, 165.1, 560, 290)
    s.text("4. HEADER TO THE ESP32-S3 DEVKITC (N16R8)", 294.64, 172, 2.0, True)
    s.part("Connector_Generic", "Conn_01x09", "To DevKitC", (368.3, 228.6),
           {1: "ADC_SCLK", 2: "ADC_DIN", 3: "ADC_DOUT", 4: "ADC_CS", 5: "ADC_DRDY", 6: "ADC_CLKIN", 7: "ADC_RESET",
            8: "~+5V", 9: "~GND"}, prefix="J",
           extra={"Note": "Wire or header to the DevKitC. Pin 8 feeds the DevKitC 5V pin. Never connect USB and this 5 V at the same time"})
    s.text("Suggested DevKitC pins (not final):", 400.0, 200.0, 1.27, True)
    rows = [
        "1  ADC_SCLK   -> IO12 (FSPICLK)",
        "2  ADC_DIN    -> IO11 (FSPID, MOSI)",
        "3  ADC_DOUT   -> IO13 (FSPIQ, MISO)",
        "4  ADC_CS     -> IO10 (FSPICS0)",
        "5  ADC_DRDY   -> IO4  (interrupt)",
        "6  ADC_CLKIN  <- IO5  (8.192 MHz from LEDC or I2S)",
        "7  ADC_RESET  <- IO6  (SYNC/RESET)",
        "8  +5V        -> DevKitC 5V pin",
        "9  GND        -> DevKitC GND",
    ]
    for i, r in enumerate(rows):
        s.text(r, 400.0, 206.0 + 5.0 * i, 1.27)
    s.text("Avoid IO35-37 (octal PSRAM), strapping pins IO0/3/45/46 and IO19/20 (USB). The DevKitC makes its own 3.3 V from the 5V pin.", 294.64, 262.0, 1.27)
    s.text("The ADC runs from the LP5907, not from the DevKitC 3V3 pin. Power sources on the DevKitC are mutually exclusive: USB, 5V pin or 3V3 pin.", 294.64, 266.0, 1.27)


block1_mains()
block2_analog()
block3_adc_power()
block4_header()
s.save(OUT)
print("wrote", os.path.abspath(OUT))

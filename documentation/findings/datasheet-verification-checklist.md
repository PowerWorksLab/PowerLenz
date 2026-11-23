# Datasheet Verification Checklist

What the design assumed, what the manufacturer datasheets actually say, and what has to change. Checked on 23 Nov 2026.

**Method.** Text was extracted from the manufacturers' PDFs and read directly. Section and table numbers refer to those documents. Where only a distributor listing or a search result was available, the item is marked as such.

**Status key**
- **Confirmed:** the datasheet says what we assumed.
- **Corrected:** the datasheet differs from what we assumed, or our wording was wrong.
- **New:** a requirement or fact we had not accounted for.
- **Not verified:** could not be read or is not in the document.

## Sources read

| Part | Document | Read |
|---|---|---|
| ADS131M04 | [TI SBAS890D, Rev. D, May 2021](https://www.ti.com/lit/ds/symlink/ads131m04.pdf) | Full text (105 pages) |
| HLK-5M05 | Hi-Link 5M-series datasheet, V2.8, June 2022, via [chipdip](https://static.chipdip.ru/lib/158/DOC035158072.pdf) | Full text (15 pages) |
| LP5907 | [TI SNVS798Q, July 2025](https://www.ti.com/lit/ds/symlink/lp5907.pdf) | Full text |
| AP2112 | [Diodes AP2112](https://www.diodes.com/assets/Datasheets/AP2112.pdf) | Full text |
| SCT-013-000 | Manufacturer datasheet page, via [SparkFun mirror](https://cdn.sparkfun.com/assets/d/0/e/9/9/SCT-013-000-2.pdf) | One page |
| ESP32-S3-WROOM-1 | [Espressif datasheet v1.8](https://documentation.espressif.com/esp32-s3-wroom-1_wroom-1u_datasheet_en.pdf) | Full text (53 pages) |
| ZMPT107-1 | Distributor and search listings only ([radiolocman](https://www.radiolocman.com/datasheet/pdf.html?di=183653)) | Manufacturer PDF **not** read |

---

## 1. ADS131M04

### Analog inputs

| Item | We assumed | Datasheet says | Status |
|---|---|---|---|
| Full-scale range | ±1.2 V ÷ gain | FSR = ±1.2 V / Gain (Eq. 3, Table 8-1). Gains 1, 2, 4, 8, 16, 32, 64, 128. | Confirmed |
| Bipolar signal around ground | CH− tied to AGND, CH+ swings both ways, no bias network | An integrated negative charge pump allows inputs as low as AGND − 1.3 V from a single supply (§8.1, §8.3.1). Allowed input range AGND − 1.3 V to AVDD for gain 1, 2, 4 (§6.3). | Confirmed |
| Input protection with clamp diodes | Add clamp diodes or a TVS | **Do not use ordinary shunt diodes from inputs to AGND.** Because of the charge pump they cannot clamp negative overvoltage. Absolute maximum is AGND − 1.6 V to AVDD + 0.3 V, with ±10 mA continuous input current (§6.1, §8.3.1). TI points to application note SBAA506 for overstress protection. | New |
| Input impedance | High | 330 kΩ × 4.096 MHz / fMOD at gain ≤ 4, and at least 1 MΩ at gain ≥ 8 (§8.3.3). Keep the driving impedance low for best gain error and distortion. | Confirmed |
| Reference | Internal | Low-drift 1.2 V internal reference (§8.1). | Confirmed |
| Unused channels | Tie to ground | Leave unused analog inputs floating or connect to AGND. Tie unused digital inputs high or low. Tie SYNC/RESET to DVDD if unused. DRDY may float (§9.1.1, §9.1.3). | Confirmed |

### Anti-alias filter and sensor front ends

| Item | We assumed | Datasheet says | Status |
|---|---|---|---|
| Filter needed | One RC low-pass per channel | An analog low-pass filter is required on each input. A single-order RC is sufficient in most applications because the digital filter handles the rest (§9.1.2). | Confirmed |
| Filter values | Rf = 1 kΩ, Cf = 10 nF | **1 kΩ in each input leg (P and N) and 10 nF across the two** (Fig. 9-1), valid for CLKIN 2–8.2 MHz. Use C0G capacitors on analog inputs (§11.1). | Corrected (topology) |
| Filter corner | About 16 kHz | With 2 kΩ differential and 10 nF the corner is about 8 kHz (1 / 2π·2 kΩ·10 nF). Gain at the 25th harmonic (1.25 kHz) is still about 0.99, with about 9° of lag there. | Corrected |
| Current front end | One burden resistor Rb to AGND, CH1− at AGND | **Split burden:** two identical resistors in series with their midpoint at ground, each end through RFILT to AINxP and AINxN, with CFILT across. This keeps the two inputs 180° apart and gives "the best THD results" (§9.2.2.2, Fig. 9-10). TI's example: 2000:1 CT, 2RB = 12.98 Ω for 100 A, giving ±918 mV peak (Eq. 12). | Corrected |
| Our range check | 22 Ω clips above about 77 A rms | Eq. 12 gives the same result: 1.2 V ÷ 22 Ω × 2000 ÷ √2 = 77 A rms. | Confirmed |
| Voltage front end | Isolation transformer, then a divider | TI's reference design uses no transformer: a divider of 3 × 300 kΩ over 750 Ω straight from mains, a varistor across live and neutral, and the same RC filter, with neutral as the ground reference (§9.2.2.1). Our transformer is a deliberate safety choice for the ESP32 and USB side. Both are valid. | New (design choice) |

### Clock, data rate and SPI

| Item | We assumed | Datasheet says | Status |
|---|---|---|---|
| Clock for 8 kSPS | CLKIN about 8.192 MHz, fMOD = CLKIN / 2, OSR 512 | High-resolution mode: CLKIN 0.3–8.4 MHz, 8.192 MHz typical. fMOD = CLKIN / 2 = 4.096 MHz. OSR 512 gives 8 kSPS, OSR 1024 gives 4 kSPS, OSR 64 gives 64 kSPS (§6.3, §8.3.5, Table 8-2). | Confirmed |
| Clock source | A dedicated oscillator is cleaner than the ESP32 | The datasheet accepts an LVCMOS clock "generated by the MCU or a local oscillator", and TI's own reference design uses an MCU-generated 8.192 MHz clock (§9.1.3, §9.2.2). The clock must be free of overshoot and glitches, and a source-termination resistor often helps (§11.1). Our preference for an oscillator is a judgement, not a datasheet requirement. | Corrected |
| SPI mode | Not stated | **Mode 1: CPOL = 0, CPHA = 1.** CS transitions must happen while SCLK is low (§6.6, §8.5.1). | New |
| SPI speed | 4–8 MHz | Minimum SCLK period 40 ns at DVDD 2.7–3.6 V, so up to 25 MHz (§6.6). TI's design uses 8.192 MHz. | Confirmed |
| Frame | Status + 4 × 24-bit + CRC, about 18 bytes | Six words per frame: response, four channel words, CRC. Word size 16, 24 or 32 bits, **24-bit by default**, so 18 bytes (§8.5.1.7). The first output word is the response to the previous input command, so the host sends a NULL command to read data and gets STATUS back. The output CRC cannot be disabled. | Confirmed |
| Read time | Trivial | 144 bits at 8.192 MHz SCLK is about 17.6 µs per frame. | Derived |
| DRDY | Active low, interrupt at the sample rate | Confirmed. It also has formats: stay low until read, or a short pulse (DRDY_FMT). **A DRDY pulse is blocked if a new conversion completes while data is being read**, so avoid reading across the conversion boundary (§8.5.1.5). | Confirmed, with a new rule |
| Late or missed reads | The frame waits about one sample period | The ADC keeps a **two-sample FIFO per channel**. If a sample is missed or reads pause, both slots fill and the DRDY flags stay set. Recover by reading two frames quickly or strobing SYNC/RESET (§8.5.1.9.1). Behaviour beyond two samples is not described there. | Corrected |
| Phase compensation | Interpolate the current samples in software | **The ADC has per-channel phase calibration.** PHASEn[9:0] sets the shift in modulator clock cycles (244 ns at 8.192 MHz). At OSR 512 the range is −256 to +255 cycles, about ±62 µs or ±1.1° at 50 Hz, with a 0.0044° step (§8.3.10, Table 8-5). Phase calibration is disabled in global-chop mode, which instead lowers noise by √2 (see the DRDY and global-chop sections). | New |

### Power, noise and layout

| Item | We assumed | Datasheet says | Status |
|---|---|---|---|
| Supplies | 3.3 V analog and digital | AVDD 2.7–3.6 V. DVDD 2.7–3.6 V (or 1.65–2.0 V with CAP tied to DVDD). Absolute maximum 3.9 V (§6.1, §6.3). | Confirmed |
| Supply current | Small | High-resolution mode: IAVDD about 3.5 mA (4.0 max), IDVDD about 0.4 mA (0.5 max), about 12 mW total (§6.5). | New |
| Decoupling | Not drawn | **1 µF on AVDD and 1 µF on DVDD, plus 220 nF from the CAP pin to DGND** when DVDD > 2.7 V (§10.1, §10.3). Use MLCC capacitors close to the pins. Our drawing omits all three. | New |
| Grounds | AGND separate from digital | Connect analog and digital ground together as close to the ADC as possible, with one ground plane where practical. Do not join separate planes at several points (§10.3, §11.1). | New |
| Noise | "Theoretical 13 µA of wire current per count" | One count is 143 nV, but input-referred noise is **7.56 µVrms at 8 kSPS and 5.35 µVrms at 4 kSPS** at gain 1 (Table 7-1). Dynamic range is 102 dB at gain 1, 4 kSPS. With a 22 Ω burden, 7.56 µV is about 0.7 mA of wire current per sample (about 0.16 W at 230 V), before any averaging and before CT error. | Corrected |
| Package | TSSOP-20 on an adapter | TSSOP-20 (PW), 6.5 × 4.4 mm, and a 3 × 3 mm WQFN-20 option (front page). The adapter must match 0.65 mm pitch. | Confirmed |

---

## 2. Hi-Link HLK-5M05

| Item | We assumed | Datasheet says | Status |
|---|---|---|---|
| Input range | 85–265 V AC | Rated input 100–240 V AC. **Input voltage range 85–265 V AC**, or 120–350 V DC (§5.1). Some distributors quote 90–264 V. Indian highs approach the upper limit. | Confirmed |
| Fuse | 1 A slow-blow | "1 A / 250 V AC slow blow, or 10 Ω wire-wound resistor" recommended (§5.1, §8). | Confirmed |
| MOV | Bourns 14D471K, 300 V AC | Hi-Link recommends a **10D561K** (§8). Fuse and varistor are "basic protective circuits (must be connected)". | Corrected |
| EMC parts | Not drawn | A 0.1 µF / 275 V AC safety capacitor and a 10–30 mH common-mode choke are recommended, and "could not be omitted" for certification (§8). Output filter capacitor C2 of 100–220 µF is recommended (§8). | New |
| Input current | Small | Max input current ≤ 0.2 A, **inrush ≤ 10 A** (§5.1). | New |
| Output | 5 V, 1 A | 5.0 ± 0.2 V at full load, 1000 mA long-term, 1200 mA short-term (§5.3). | Confirmed |
| Ripple and noise | Noisy, needs filtering | **Up to 100 mV p-p** (20 MHz bandwidth, 10 µF and 0.1 µF at the load). About 50 mV typical, and about 30 mV with 100–220 µF added (§5.3, §8). | New |
| Isolation | Isolated | **Inconsistent within the datasheet:** 3000 V AC in the feature list (§3) but 2500 V AC in the safety section (§9). It does not state whether the insulation is basic or reinforced. | New (unresolved) |
| Temperature | Not considered | **Working temperature −25 to +60 °C** with natural cooling (§4, §7). An Indian enclosure in summer can approach this. | New |
| Certification | Safe by design | Designed to meet UL and CE requirements, but "the UL and CE certifications are made by the customer" (§9.1). | New |
| Efficiency and standby | — | At least 70% at 230 V full load, no-load loss below 0.1 W. Short-circuit protection with automatic recovery (§3, §5). | New |
| Minimum load, hold-up time | — | Not found in the document. | Not verified |

---

## 3. LDOs

### TI LP5907 (analog supply candidate)

| Item | Datasheet says | Status |
|---|---|---|
| Input and current | 2.2–5.5 V in, up to 250 mA | Confirmed |
| Noise | Below 6.5 µVrms (10 Hz–100 kHz) at 250 mA | Confirmed (suits an ADC supply) |
| PSRR (20 mA) | 90 dB at 100 Hz, 82 dB at 1 kHz, 65 dB at 10 kHz, **60 dB at 100 kHz** | New |
| Dropout | 120 mV typ. (DSBGA), **250 mV max** at 250 mA for SOT-23 and X2SON | New |
| Capacitors | 1 µF ceramic in and out (0.7–10 µF, ESR 5–500 mΩ), no bypass capacitor | New |
| Note | TI lists the **TPS7A20** as the more up-to-date part | New |

The ADC needs only about 4 mA on AVDD, so 250 mA is ample. With 100 mV p-p of 5 V ripple, 60 dB of rejection leaves about 0.1 mV on AVDD at 100 kHz.

### Diodes AP2112K-3.3 (digital supply candidate)

| Item | Datasheet says | Status |
|---|---|---|
| Current | 600 mA minimum continuous | Confirmed |
| Dropout | 250 mV typ., 400 mV max at 600 mA (3.3 V) | New |
| Noise and PSRR | 50 µVrms; 65 dB at 100 Hz and 1 kHz | New |
| Capacitors | 1 µF; X7R or X5R recommended for ceramic | New |
| Limits | Input absolute maximum 6.5 V. Foldback short-circuit current 50 mA. | New |
| **Thermal** | **θJA 184 °C/W in SOT-25**, 120 °C/W in SOT-89-5 | New |

**Thermal check.** Dropping 5 V to 3.3 V dissipates 1.7 V × current. At the ESP32-S3's 355 mA Wi-Fi peak that is about 0.6 W, or about 110 °C of rise in a SOT-25 if sustained. At about 120 mA average it is about 0.2 W, or about 37 °C of rise. Inside a hot enclosure that is marginal. Options: the SOT-89-5 package, a buck converter, or a 3.3 V module such as the HLK-5M03 (3.3 V, 1.5 A) for the digital side.

---

## 4. ESP32-S3-WROOM-1 (datasheet v1.8)

| Item | Datasheet says | Status |
|---|---|---|
| Octal PSRAM pins | **On modules with octal PSRAM (the R8 variants, including N16R8), IO35, IO36 and IO37 are connected to the PSRAM and are not available** (pin table note b). | New (affects SPI pin choice) |
| Strapping pins | GPIO0, GPIO3, GPIO45 and GPIO46 (§4). | New |
| Supply | 3.0–3.6 V operating voltage (feature list). | Confirmed |
| Wi-Fi current | **TX peak 355 mA** (802.11b), 286–297 mA for g/n at 3.3 V, rated at 100% TX duty (Table 6-4). | New |
| Ambient temperature | **R8 modules are rated −40 to 65 °C** (85 °C if PSRAM ECC is enabled, at the cost of 1/16 of the PSRAM) (ordering-information table and its note). | New |
| Vector and AI instructions | The datasheet refers to neural-network and signal-processing acceleration in the SoC. Details are in the chip datasheet. | Partly verified |
| Maximum SPI clock on SPI2/SPI3, GPIO-matrix limits | Not in the module datasheet. | Not verified |
| ADC2 and Wi-Fi | Not covered here. Not relevant while we use an external ADC. | Not verified |

---

## 5. Sensors

### SCT-013-000 current transformer

| Item | We assumed | Datasheet says | Status |
|---|---|---|---|
| Ratio | 100 A : 50 mA, 2000:1 | 100 A : 50 mA, rated input 100 A, frequency range 50 Hz–150 kHz. | Confirmed |
| Output type | Current output, burden fitted by us | Two options: current output, or voltage output with a built-in sampling resistor. We must order the **current-output** model for our Rb design. | Confirmed, with a caution |
| **Accuracy at low current** | Good everywhere | **Non-linearity ±3% only within 10–120% of rated input, which is 10–120 A.** Below 10 A the accuracy is not specified. Most household loads and all standby loads are below that. | New (important) |
| Phase error | Calibrate it | **No phase-error figure is given.** | New |
| Burden guidance, open-circuit warning | Burden required, never open | Neither is stated on the datasheet page. The open-circuit rule is standard CT practice but is not documented here. | Not verified |
| Isolation, temperature, size | — | 6000 V AC for 1 minute between housing and output. −25 to +70 °C. 13 × 13 mm opening. | New |

### CT field measurements (OpenEnergyMonitor, one unit each)

Sources: [SCT-013-000 report](https://docs.openenergymonitor.org/electricity-monitoring/ct-sensors/yhdc-sct-013-000-ct-sensor-report.html), [SCT006 report](https://docs.openenergymonitor.org/electricity-monitoring/ct-sensors/yhdc-sct006-ct-sensor-report.html). Read as text only; the phase plots were images and were not read.

| Primary current | SCT-013-000 ratio error |
|---|---|
| 0.5 A | +1.4% |
| 1 A | +0.8% |
| 2 A | +1.2% |
| 5 A | -2.0% |
| 10 A | 0.0% |
| 20-100 A | +0.7% to +2.0% |
| 140 A | -1.9% (saturating) |

- Gain stays within about 2% from 0.5 A upward, better than the datasheet promises below 10 A.
- Phase error is about 4 degrees at 22 ohm burden and fairly flat; about 8 degrees at 120 ohm. Lower burden gives lower phase error.
- Their readings below about 250 mA were unreliable in their rig (a limit of the rig, not proven of the CT).
- SCT006 (6 mm opening) is usable only to about 16-20 A, so it suits branch wires, not a main cable.
- 4 degrees at 50 Hz is about 222 us, or about 1.8 samples at 8 kSPS, which exceeds the ADC PHASEn range (about +/-1.1 degrees at OSR 512).

**Decision (CT):** keep the SCT-013-000 as the single CT. Buy two or three and calibrate each. Use about 22 ohm total burden or lower. Correct phase with a whole-sample software shift plus the PHASEn register. Calibrate on a resistive load (true Q = 0) and verify on a fan. Bench-test against a reference from about 0.1 A. Add a metering-grade split-core CT on CH2 only if the SCT-013-000 fails below about 0.3 A.

**Why phase matters:** P is the average of v x i, so a false angle error d changes P by about -d x tan(phi). At 4 degrees: PF 1 gives -0.2% in P but a fake Q of 7% of VA; PF 0.9 gives -3.6%; PF 0.7 gives -7.4%; PF 0.5 gives -12.3%. The fake Q blurs the P/Q fingerprints used for appliance classification.

Open: the sign of the SCT-013-000's phase shift (CTs typically lead) is assumed, not measured.

### ZMPT107-1 voltage transformer (manufacturer sheet read, 23 Nov 2026)

Source: Zeming (zeming-e.com) one-page sheet, Chinese, via [LCSC/szlcsc](https://atta.szlcsc.com/upload/public/pdf/source/20170912/C125191_1505207878742963562.pdf). Text and the two usage figures were read.

| Item | Listings said | Manufacturer sheet says | Status |
|---|---|---|---|
| Type and ratio | 2 mA : 2 mA, 1000:1000 | Same. Rated input and output 2 mA. | Confirmed |
| Phase error | 45 arcmin, 50 or 100 ohm (sources differed) | **<= 45 arcmin (0.75 degrees) at 2 mA input, 50 ohm sampling resistor.** | Confirmed, 50 ohm |
| Linear range | 0-1000 V | 0-1000 V, 0-10 mA (50 ohm sampling resistor) | Confirmed |
| Linearity | 0.2% | <= 0.2% from the 20% to 120% points (0.4-2.4 mA, about 46-276 V rms at 115 kohm) | Confirmed |
| Ratio error | not listed | -0.6% to 0% at 2 mA, 50 ohm (output slightly low; calibrate) | New |
| Isolation | 3 kV or 4 kV | **3000 V.** The 4 kV figure is not from the maker. | Resolved |
| Temperature | -40 to +85 | **-40 to +70 degC** (ZMPT107-1). The +85 figure belongs to the ZMPT107G-1 variant. | Corrected |
| Case | not listed | PBT. (Plain ZMPT107 has an ABS case that cannot go through wave soldering, and 0.3% linearity, -40 to +60 degC.) | New |
| Package | not listed | 19 x 10 x 18.2 mm, four pins (1*, 2, 3*, 4), dots mark the same-polarity ends | New |
| Wiring | not listed | Series limiting resistor R' from the mains, sampling resistor R across the output: Uo = Ui / R' x R. Can read directly with a resistor, or through an op-amp. | Confirmed |

Not on the sheet: the series resistor value, the coil's DC resistance, temperature drift of the phase, and the primary's impulse withstand. The 115 kohm figure is our calculation (230 V / 2 mA).

Variant note: the ZMPT107G-1 (separate spec sheet, 2021) states <= 30 arcmin and -40 to +85 degC. Indian availability not checked.

**Decision (voltage sensing):** ZMPT107-1, wired as in the maker's figure 2.
- Primary: three metal-film resistors in series, about 39 kohm each (117 kohm total, 1%, 1/2 W each), then pins 1* and 2. About 2 mA at 230 V; peak about 2.8 mA; power about 0.46 W total at 230 V and 0.6 W at 264 V.
- Secondary: 50 ohm sampling resistor, built as 2 x 25 ohm with the midpoint at AGND (same split-burden idea as the CT).
- ADC: AIN2P/AIN2N through the same 1 kohm + 10 nF filter as the CT channel, so the filter delays match. Output is about 141 mV peak at 230 V, so use PGA gain 2 (full scale +/-0.6 V) for headroom; gain 1 also works.
- Phase: 0.75 degrees is about 42 us, inside the ADC's PHASEn range (about +/-62 us at OSR 512). Calibrate it together with the CT's phase using a resistive load.
- Gain: calibrate on a known reference voltage. Metal-film tempco (50 ppm) gives about 0.15% over 30 degC.
- Protection: MOV across live-neutral before the resistors (the primary sees mains directly); PCB clearance and creepage for 230 V around the primary resistors and pins.

Open:
- Our unit's real phase and ratio error (bench test). Resistor and coil tempco effect on phase.
- ADC input impedance versus the 1 kohm filter legs (check SBAA/datasheet) for gain error.
- Operation above about 276 V and below about 46 V is outside the linearity spec (matters in surges and brown-outs).
- Impulse (surge) withstand of the primary is not stated.

---|---|---|
| Type and ratio | Current-type transformer, 2 mA : 2 mA, 1000:1000 turns | Not verified against the PDF |
| Phase error | 45 arcminutes (0.75°) at 2 mA input, with a 50 Ω or 100 Ω sampling resistor (sources differ) | Not verified |
| Linearity and range | 0.2% linearity (20–120% of range), 0–1000 V | Not verified |
| Isolation | 3 kV or 4 kV, depending on the source | Not verified (conflict) |

If we choose this part, the primary needs a series resistor of about 115 kΩ for 230 V and 2 mA (my calculation, rated for the voltage and power), and the phase error of about 0.75° must be calibrated out. It also changes the voltage circuit from what we drew.

---

## What this changes in the design

1. **Current input:** change to a split burden (two resistors, midpoint at AGND), with 1 kΩ in each leg to AIN1P and AIN1N and a 10 nF C0G across them.
2. **Voltage input (decided: ZMPT107-1, see its section):** use the same differential 1 kΩ + 10 nF filter. Update the corner and phase numbers to the differential values (about 8 kHz, 0.36° at 50 Hz).
3. **Protection:** do not add ordinary clamp diodes from the ADC inputs to AGND. Follow TI's overstress guidance (SBAA506).
4. **ADC pins:** add 1 µF on AVDD, 1 µF on DVDD and 220 nF on CAP. Tie AGND and DGND together at the ADC.
5. **Firmware:** SPI mode 1. Read each frame promptly and never across a conversion boundary. Account for the two-sample FIFO. Do phase compensation in the PHASEn registers instead of by interpolation, unless global-chop mode is used.
6. **Power supply:** add the safety capacitor, common-mode choke and output capacitor if certifying. Decide on the MOV (10D561K vs 14D471K). Resolve the 2500 V vs 3000 V isolation question with Hi-Link. Keep the module under 60 °C.
7. **Digital supply (decided):** AP2112K in SOT-25 is thermally marginal from 5 V; replaced by the AP63203 buck. See Finalized decisions.
8. **ESP32-S3 module (decided: keep the owned N16R8 for the demo):** pins: avoid IO35–37 if using an R8 module, and avoid the strapping pins for SPI. Check that the enclosure stays below 65 °C ambient for R8 modules.
9. **CT choice (decided):** keep the SCT-013-000. It is only specified from 10 A upward, but field measurements show gain within about 2% from 0.5 A. Calibrate phase (about 4 degrees) in software plus PHASEn, and bench-test from about 0.1 A. See the CT field measurements section.

## Finalized decisions (running list)

| Area | Decision | Basis |
|---|---|---|
| Current sensor | SCT-013-000, one split-core CT on live. Buy 2-3 units and calibrate each. | Datasheet, OpenEnergyMonitor measurements |
| CT phase | About 4 degrees expected. Correct with a whole-sample shift plus the ADC PHASEn register, calibrated on a resistive load (true Q = 0), verified on a fan. | OpenEnergyMonitor, ADS131M04 datasheet |
| CT fallback | Add a metering-grade split-core CT on CH2 only if the SCT-013-000 fails below about 0.3 A. | Bench test pending |
| Voltage sensor | ZMPT107-1 (2 mA : 2 mA, 3000 V isolation, 0.75 degrees at 50 ohm). Replaces the 230:9 V transformer option. | Manufacturer sheet |
| Voltage primary | 3 x 39 kohm metal-film (1%, 1/2 W each) in series, about 2 mA at 230 V. MOV across live-neutral in front. | Maker's wiring figure plus our calculation |
| Voltage secondary | 50 ohm sampling resistor as 2 x 25 ohm, midpoint to AGND. Same 1 kohm + 10 nF filter as the CT channel. PGA gain 2. | Manufacturer sheet, ADS131M04 datasheet |
| Burden and filter | Split burden of about 13 ohm total (2 x 6.49 ohm, 0.1%, midpoint to AGND), 1 kohm per leg + 10 nF C0G across, identical on both channels. 22 ohm was rejected: it clips the ADC above about 77 A rms; 13 ohm clips above about 131 A rms. | ADS131M04 datasheet example (12.98 ohm), our headroom calculation |
| ADC configuration | ADS131M04, high-resolution mode, CLKIN 8.192 MHz (generated by the ESP32), OSR 512 = 8 kSPS, internal 1.2 V reference. CH1 = CT current (PGA gain 1), CH2 = voltage (PGA gain 2); CH0 and CH3 spare. SPI mode 1, CRC enabled. 1 uF on AVDD and DVDD, 220 nF on CAP, AGND and DGND joined at the ADC. | ADS131M04 datasheet SBAS890D |
| ADC gain terms | PGA gain zooms the signal into the +/-1.2 V/gain window (CT at gain 1 would clip above about 65 A rms at gain 2). Separate fixed gain error of about 0.6% per channel from the 2 kohm filter against the 330 kohm input impedance; removed by calibration. | Datasheet: Zin 330 kohm (gain 1, 2, 4) |
| ADC-ESP32 link | 7 signals: SCLK, DIN, DOUT, CS on SPI2 (avoid IO35-37 on R8 modules), DRDY on a GPIO interrupt, CLKIN from LEDC or I2S, SYNC/RESET on a GPIO. | Datasheet, ESP32-S3 datasheet |
| AC-DC module | HLK-5M05 (5 V, 1 A long-term, 1.2 A short-term). Fuse 1 A / 250 V AC slow-blow. MOV 10D561K (maker's recommendation, replaces the 14D471K we priced). 100-220 uF output capacitor. Safety capacitor 0.1 uF / 275 V AC and 10-30 mH common-mode choke only if certifying (not needed for the bench demo). | HLK 5M-series datasheet V2.8, sections 5, 8, 9 |
| 5 V power budget | ESP32-S3 Wi-Fi burst about 355 mA at 3.3 V plus ADC and other parts gives about 0.4 A at 5 V, 40% of the module rating. Module loses about 30% as heat (about 0.9 W at 2 W out) inside the enclosure. | Datasheets, our calculation |
| Digital 3.3 V stage | Do not use AP2112K in SOT-25 from 5 V (0.6 W at 0.36 A, theta-JA 184 C/W gives about 110 C rise). Preferred: small 5 V to 3.3 V buck (part not yet researched). LP5907 stays on the analog rail. | AP2112 and LP5907 datasheets, our calculation |
| Analog and ADC-digital supply | LP5907 3.3 V (2.2-5.5 V in, +/-2%, <6.5 uV rms, PSRR 60 dB at 100 kHz, 1 uF ceramics in and out) feeds AVDD. Suggested, not datasheet-backed: also feed the ADC's DVDD from it (about 0.4 mA) to keep ESP32 rail noise away. Consider a ferrite bead or RC ahead of its input. TI marks the LP5907 with a pointer to the TPS7A20 as a newer part; still active (rev Q, July 2025). | LP5907 datasheet SNVS798Q |
| Digital supply | **Diodes AP63203**: fixed 3.3 V (3.27-3.33 V), 2 A synchronous buck, 3.8-32 V input (works down to the HLK's 4.8 V worst case), about 1.1 MHz with +/-6% spread spectrum, 22 uA quiescent, theta-JA 89 C/W (TSOT26), -40 to +85 C, UVLO 3.5 V rising. External parts per Table 2: L 3.9 uH, C1 10 uF, C2 2 x 22 uF, C3 100 nF. Ready-made 5 V-input modules rejected: Hubtronics 3.3 V module needs 5.5 V minimum; the Zbotic 5-40 V module has no margin for the HLK's 4.8 V worst case. | AP63200/01/03/05 datasheet (SparkFun copy, Jan 2019); not read: current Nov 2024 revision |
| MCU module | **Use the ESP32-S3-WROOM-1-N16R8 we already own** for the demo. Constraints: IO35-37 unavailable (octal PSRAM); ambient limit 65 C (85 C if PSRAM ECC is enabled, which cuts usable PSRAM by 1/16, so about 7.5 MB); supply 3.0-3.6 V; Wi-Fi TX peak 355 mA. 8 MB PSRAM is more than raw-event capture needs. A later production board could switch to N16R2 (85 C, no pin loss, about Rs 654 from one listing) but nothing forces it. | ESP32-S3-WROOM-1 datasheet v1.8, Table 1-1 and 6-4 |
| Demo power path (DevKitC) | We own an ESP32-S3-DevKitC with the N16R8 module. For the demo, skip the AP63203: feed the HLK-5M05's 5 V to the DevKitC 5V pin and let its onboard regulator make 3.3 V. Feed the ADC's AVDD (and DVDD) from our own LP5907 off the same 5 V, not from the DevKitC 3V3 pin. Never connect USB and the HLK 5 V at the same time unless the DevKitC user guide confirms it is safe (not yet read). The AP63203 is only for a custom board. Suggested pins (not final): SPI2 IO_MUX pins IO10 CS, IO11 MOSI, IO12 SCLK, IO13 MISO; DRDY, SYNC/RESET and CLKIN on other free GPIOs; avoid IO35-37, strapping pins, and IO19/20 if USB is used (from memory, verify). | Our decision; DevKitC user guide not read |
| ESP32-S3 SPI | Our need is at most about 1.2 Mbit/s and the ADC accepts SCLK up to 25 MHz, so use any SPI2 pins (GPIO matrix, reported limit 40 MHz; IO_MUX pins reported 80 MHz). Avoid IO35-37 and strapping pins 0, 3, 45, 46. | Waveshare tutorial (secondary source); ESP32-S3 SoC datasheet not read |
| ADC clock source | Generate CLKIN (8.192 MHz) from LEDC or I2S MCLK. The S3 has no APLL, so 8.192 MHz comes from a fractional divider of the 80 or 160 MHz clock and will have jitter. Our estimate: about 12.5 ns of jitter is about -80 dB at the 25th harmonic and affects V and I equally; verify on a scope. Fallback: a small 8.192 MHz oscillator on the board (part not researched). | ESP-IDF and forum reports, our estimate |
| Firmware split | ESP-IDF in C/C++. Core 1: SPI/DMA read, ring buffer, DSP. Core 0: Wi-Fi, MQTT/TLS, OTA. | Architecture decision |
| Voltage phase | 0.75 degrees (about 42 us) fits inside PHASEn; calibrate with the CT. | Manufacturer sheet |

Open after these decisions: DevKitC-1 power-path details (onboard regulator rating, USB/5V backfeed, pin map) from its user guide,  AP63203 current datasheet revision, buck output ripple and EMI near the ADC (layout), ESP32-S3 SoC datasheet (SPI limits taken from a secondary source), ESP32 CLKIN jitter on a scope, whether 2 MB PSRAM is enough for raw capture (internal SRAM alternative),  HLK-5M05 isolation rating (3000 V vs 2500 V, basic vs reinforced), its two derating graphs (images, not read), MOV 10D561K and fuse datasheets, buck converter part choice,  whether PHASEn works with global-chop mode, temperature drift of the ADC input impedance (and so the 0.6% term), ESP32-generated CLKIN jitter, TI SBAA506 input protection, CT open-circuit clamp (not an ordinary diode to AGND; TI SBAA506 not yet read), final burden after the bench test,  our units' real phase and ratio error, surge withstand of the ZMPT107-1 primary, behaviour outside about 46-276 V, ADC input impedance versus the 1 kohm filter legs, and the series resistor value (our calculation, not from the sheet).

## Still unverified

- ZMPT107-1 manufacturer datasheet.
- Maximum SPI clock for the ESP32-S3's SPI2 and SPI3, and any GPIO-matrix speed limit.
- Details of the ESP32-S3 vector instructions.
- The 14D471K and 10D561K MOV datasheets (energy rating, clamping voltage).
- The Littelfuse fuse datasheet (breaking capacity, time-current curve).
- PZEM-004T v3 specifications.
- HLK-5M05 minimum load, hold-up time, and whether its insulation is basic or reinforced.
- Behaviour of the ADS131M04 beyond a two-sample backlog.

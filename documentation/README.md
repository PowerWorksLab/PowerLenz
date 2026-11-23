# PowerLenz: Design Documentation

PowerLenz is a Sense-style energy monitor for Indian single-phase homes (230 V, 50 Hz). One clamp on the live wire and one voltage tap are enough to tell, from the whole-home signal alone, which appliances are running. This is the NILM (non-intrusive load monitoring) idea.

This page is the reading order for everything written so far. It records what is decided, what is still open, and where the evidence lives. Status as of 23 Nov 2026. Nothing here has been built or bench-tested yet.

## How to read this folder

| # | Read | What you get |
|---|---|---|
| 1 | This page | The whole design in one sitting |
| 2 | [findings/v1-architecture-plan.md](findings/v1-architecture-plan.md) | The first plan and why we chose these directions |
| 3 | [findings/adc-options-comparison.md](findings/adc-options-comparison.md) | Internal ADC vs metering IC vs external ADC |
| 4 | [findings/dsp-ml-event-detection.md](findings/dsp-ml-event-detection.md) | Where DSP, event detection and ML run, and channels |
| 5 | [findings/adc-to-esp32-data-path-and-dsp.md](findings/adc-to-esp32-data-path-and-dsp.md) | How a sample reaches the ESP32 and becomes watts (written before the datasheet review, see its caveats) |
| 6 | [findings/datasheet-verification-checklist.md](findings/datasheet-verification-checklist.md) | Every assumption checked against datasheets, plus the finalized-decisions table |
| 6b | [findings/bill-of-materials.md](findings/bill-of-materials.md) | Every part with quantity, price and buy link |
| 7 | [findings/datasheet-links.md](findings/datasheet-links.md) | All datasheet links and whether each was read |
| 7b | [datasheets/](datasheets/README.md) | Local copies of the manufacturer documents, organised by function, with an index |
| 8 | [diagrams/powerlenz-front-end.html](diagrams/powerlenz-front-end.html) | Circuit diagrams and the equations (version 2, matches the decisions below) |
| 9 | [presentations/powerlenz-front-end.pptx](presentations/powerlenz-front-end.pptx) | 18-slide deck of the diagrams, the datasheet changes, phase error and open items (version 2) |

## 1. The idea in one picture

```
 mains ──► CT clamp (current) ─┐
       └─► voltage tap ────────┤
                               ▼
              burden + RC filter (signal conditioning)
                               ▼
              ADS131M04  (samples V and I at the same instant, 8,000 times a second)
                               ▼  SPI
              ESP32-S3: per-cycle Vrms, Irms, P, Q, PF, harmonics; detects "something switched"
                               ▼  Wi-Fi, MQTT over TLS
              Cloud: store, classify the event ("fridge compressor"), push to the app
                               ▼
              Phone app: live usage, appliance list, alerts
```

Why this shape:
- **Event detection runs on the ESP32.** Only small event summaries leave the home, which keeps data and cloud cost low.
- **Classification runs in the cloud.** The phone app cannot run in the background, so the cloud must receive events.
- **Simultaneous sampling** matters because power needs the voltage and current at the same instant. A multiplexed ADC would add a fake phase shift.

## 2. Decisions

### Scope
| Item | Decision |
|---|---|
| Target | Single-phase households first (one CT; 3-phase would need three) |
| Channels | 1 voltage + 1 current (2 spare on the ADC) |
| Firmware | C/C++ on ESP-IDF, not MicroPython (hard real-time sampling). Core 1: sampling and DSP. Core 0: Wi-Fi, MQTT, OTA. |
| Demo backend | A laptop running local Python (FastAPI) over Wi-Fi MQTT. Real cloud later. |
| ML | Cloud or phone first, edge later. Event features, then random forest or LightGBM, then a small 1D-CNN. |

### Hardware chain (datasheet-verified unless noted)
| Stage | Part | Key settings |
|---|---|---|
| Current sensor | **SCT-013-000** split-core CT (100 A : 50 mA), one on live | Order the current-output version. Buy 2–3 and calibrate each. Gain within about 2% from 0.5 A in field tests (one unit, by OpenEnergyMonitor). |
| Burden | 2 × 6.49 Ω, 0.1%, midpoint to AGND (about 13 Ω total) | 22 Ω was rejected: it clips above about 77 A. 13 Ω clips above about 131 A. |
| Voltage sensor | **ZMPT107-1** current-type transformer (2 mA : 2 mA, 3000 V isolation, ≤0.75° phase) | 3 × 39 kΩ in series on the mains side (about 2 mA at 230 V). Secondary: 50 Ω as 2 × 25 Ω, midpoint to AGND. |
| Input filter and protection | 1 kΩ in each leg, TI's clamp (BAT54 to AVDD, BAV199 pair to ground), 100 Ω, then the ADC pin; 10 nF C0G across each channel | About 7.2 kHz corner. Identical on both channels, so their phase shifts cancel. |
| ADC | **ADS131M04**: 24-bit, 4 channels, simultaneous | 8 kSPS (OSR 512), continuous-conversion mode (global-chop is for DC), internal reference. CH1 = current at PGA gain 1, CH2 = voltage at gain 2. 1 µF on AVDD/DVDD, 220 nF on CAP. SPI mode 1. CLKIN 8.192 MHz from the ESP32. |
| MCU | **ESP32-S3-WROOM-1-N16R8** (on an ESP32-S3-DevKitC-1 board we still have to buy) | Avoid IO35–37 (octal PSRAM) and strapping pins. Ambient ≤ 65 °C. SPI2 on any pins. |
| AC-DC | **HLK-5M05** (5 V, 1 A) | 1 A time-lag ceramic fuse with high breaking capacity (Bel 5HT 1-R), MOV 10D561K, 100–220 µF output capacitor. Safety capacitor + choke only if certifying. |
| Analog supply | **LP5907** 3.3 V | Feeds ADC AVDD (and DVDD, our suggestion). Ripple rejection 60 dB at 100 kHz. |
| Digital supply (demo) | The DevKitC's own regulator, from the HLK's 5 V | Never connect USB and the HLK 5 V at once (not yet confirmed safe). |
| Digital supply (custom board) | **AP63203** 3.3 V buck, 3.9 µH + 10 µF + 2 × 22 µF | Replaces the AP2112K, which would overheat from 5 V. |

### Power flow
```
mains → fuse → MOV → HLK-5M05 (5 V) ─┬→ DevKitC 5V pin (onboard 3.3 V)
                                     └→ LP5907 (3.3 V) → ADS131M04
```

## 3. The ideas behind the choices

**Why a CT, and why only on the live wire.** The CT clips around one insulated wire and senses the magnetic field of the current, with no electrical contact. A single-phase home needs one. The CT gives a small current, which the burden resistor turns into a voltage.

**Why the filter.** Noise is much faster than mains. The RC filter lets the 50 Hz signal through and removes fast noise before it reaches the ADC. A delta-sigma ADC samples far faster internally (4.096 MHz) and then filters digitally, so the RC mainly guards against noise near that rate. (The first draft of the diagram labelled the filter's job as the 4 kHz Nyquist point. That was wrong for this ADC, and version 2 fixes it.)

**Why phase error matters.** Real power is the average of voltage × current. A false angle of 4° (what the CT is expected to add) changes power by about 4° × tan(phase), and creates a fake reactive power of 7% of apparent power on a pure heater:

| True PF | Error in P at 4° |
|---|---|
| 1.0 | −0.2% (but fake Q = 7% of VA) |
| 0.9 | −3.6% |
| 0.7 | −7.4% |
| 0.5 | −12.3% |

The fix is calibration: put a pure resistive load on (true reactive power = 0), then shift the current samples until the measured reactive power is 0. The CT's 4° (about 222 µs, about 1.8 samples) is applied as a whole-sample shift plus the ADC's fine phase register. The voltage sensor's 0.75° fits inside the register alone.

**Why PGA gain.** Gain is a multiplier before the ADC measures. A small signal gets zoomed in to use more of the ADC's range. The ADC's window shrinks with gain (±1.2 V at gain 1, ±0.6 V at gain 2). So the CT stays at gain 1 (already large) and the voltage uses gain 2 (small).

**Why the isolated power module.** The HLK-5M05 keeps the measurement electronics electrically separate from mains.

## 4. Signal processing on the ESP32-S3

Every mains cycle (50 times a second) the DSP produces Vrms, Irms, P, Q, PF and frequency:
1. Remove DC offset per window.
2. Cut the stream into whole cycles at voltage zero-crossings, with interpolation.
3. Accumulate V², I², V·I (64-bit sums).
4. Get signed reactive power from a quarter-cycle-delayed voltage.
5. Apply phase compensation.
6. Every 8 cycles, resample to 1,024 points and run an FFT for harmonics.

Details and the code sketch are in [findings/adc-to-esp32-data-path-and-dsp.md](findings/adc-to-esp32-data-path-and-dsp.md). Items there that the datasheet later refined: late-read window is a 2-sample FIFO, an MCU clock is acceptable for CLKIN, and phase can be done in the ADC's registers.

## 5. Event detection, ML, cloud and subscriptions

These stages are planned, not yet specified in detail:
- **Event detection (ESP32):** detect step changes in P and Q, then send a compact event (change in P/Q, harmonics, inrush shape).
- **Classification (cloud):** per-home clustering plus user labels, then a classifier.
- **MQTT over TLS** carries events; the cloud stores per-user data.
- **Subscription idea:** free tier = whole-home usage and totals; paid tier = appliance-level breakdown and alerts.
- **Open topics:** power cuts and timekeeping, raw-waveform capture for dataset building.

See [findings/dsp-ml-event-detection.md](findings/dsp-ml-event-detection.md) and [findings/v1-architecture-plan.md](findings/v1-architecture-plan.md).

## 6. Bill of materials

The full list, with a quantity, price and buy link for every part, is in [findings/bill-of-materials.md](findings/bill-of-materials.md). Prices were seen on 23 Nov 2026 in INR.

Key points:
- **The ESP32-S3 DevKitC is not owned.** It is a part to buy (about ₹1,100 ex-GST on IndiaMART), pending a reimbursement.
- Every part now has a price and a buy link, except hook-up wire and the mains cable. Most were read on the seller page; the terminal block and the perfboard prices come from search results and are marked in the BoM.
- The bench demo comes to roughly ₹3,600 to ₹4,300 before GST, shipping and fees.
- Several Digi-Key India items showed zero stock, long lead times, or a ₹452 Digi-Reel fee, so the BoM names an Indian seller where one exists.

## 7. Safety

The mains side (fuse, MOV, HLK input, ZMPT107-1 series resistors and primary) is live 230 V. Use an enclosure, proper clearance and creepage, and do not probe it while powered. The HLK's isolation rating is unresolved (3000 V in one place, 2500 V in another) and it does not state basic vs reinforced insulation, so don't connect a laptop to the board while on mains until that is settled. Certification (UL/CE or Indian equivalents) is our job, not the module's.

## 8. What is still open

**Needs a bench test**
- Our units' real phase and ratio error, CT performance from about 0.1 A.
- ESP32-generated CLKIN jitter on a scope.
- Whether the SCT-013-000 works below about 0.3 A (fallback: a second, metering-grade CT on CH2).

**Checked online on 23 Nov 2026**
- HLK-5M05 derating graphs: full load from about 110 V to 260 V AC and up to 60 °C. Our load is about 40%, so it is comfortable.
- DevKitC user guide: the USB ports, the 5V pin and the 3V3 pin are "mutually exclusive" power sources, so never use USB and the HLK 5 V together.
- ADS131M04: use continuous-conversion mode for AC, not global-chop. TI's phase-shift example matches our plan.
- MOV 10D561K is rated 350 V AC. The Littelfuse 0239 glass fuse is only rated **35 A at 250 V AC** (official table), so it is replaced by a ceramic Bel 5HT 1-R rated about 1.5 kA. That figure still needs the Bel datasheet.
- TI's SBAA506 input-protection circuit is adopted on all four ADC input pins.

**Still needs a datasheet or answer**
- HLK-5M05: isolation rating (3000 V or 2500 V) and a conflict over the input fuse (its text says 1 A, its circuit drawing shows 0.5 A).
- Official Bourns MOV datasheet and the Bel 5HT fuse datasheet; a 3.3 V supply clamp part for AVDD.
- ZMPT107-1 surge withstand (not stated); behaviour outside about 46–276 V.
- ESP32-S3 SoC datasheet (SPI limits came from a secondary source), the DevKitC regulator's current rating, the 330 kΩ input-impedance drift, and the AP63203 current revision.

**Needs to be built**
- Detailed event detection, MQTT/cloud, classification, subscription and power-cut design.

## 9. Method notes

- Datasheets were read as text (PDF extraction). Figures and graphs that are images were not read unless stated.
- Field measurements of the CT come from one unit tested by OpenEnergyMonitor, so treat them as indicative.
- Prices come from listings and may have changed.
- The ZMPT107-1 sheet is in Chinese. It was read directly.

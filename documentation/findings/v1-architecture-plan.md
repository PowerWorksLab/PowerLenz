# PowerLenz: NILM Energy Monitor, v1 Architecture Plan

> Part names and specs below are recalled from memory. Verify against datasheets before committing to a schematic.

## Context

PowerLenz is a Sense-style NILM (non-intrusive load monitoring) energy monitor for Indian households (230 V, 50 Hz, single-phase). It uses a CT clamp, a voltage sensor and a signal-conditioning circuit that feed an ADC.

Decisions made so far:

- **Segment:** single-phase households.
- **Front end:** external simultaneous-sampling ADC (ADS131M0x or MCP3912), SPI with DMA.
- **ML:** runs on a laptop/local server (cloud or phone later), on-device later.
- **MCU:** ESP32-S3 (vector instructions for TinyML, usually PSRAM).
- **Demo backend:** laptop / local Python service on the same Wi-Fi.
- **Transport:** Wi-Fi with MQTT.

## Demo ADC choice

- **Primary: TI ADS131M04** (4-channel, 24-bit, simultaneous-sampling delta-sigma, SPI + DRDY). One voltage and one current channel are used. Two are spare for a second CT or for 3-phase later, so no board respin.
- **Reasons:**
  - Simultaneous sampling, so no V/I phase skew.
  - Bipolar differential inputs, so the CT burden output can go straight in (verify in the datasheet).
  - Built-in PGA and reference.
  - ~4–8 kSPS output rate is enough for the NILM features.
  - Firmware is one SPI driver plus a DRDY interrupt service routine.
- **Second source:** Microchip MCP3912, as a fallback if TI parts are unavailable.
- **Lab reference (not the demo ADC):** a cheap commercial meter (e.g. PZEM-004T v3) to validate P/Q/RMS.
- **Channels for the demo:** 1 voltage + 1 current (whole-home mains). The other 2 are left spare.
- **To verify before ordering:** input range and PGA, output data rate options, package, stock and price in India.
- **Board build (undecided):** proposed sequence is an evaluation module plus an ESP32-S3 dev board for the first 1–2 weeks of firmware bring-up, while a custom PCB (assembled by a service, since the ADC is fine-pitch) is designed in parallel.

## Processing placement

| Stage | ESP32-S3 (edge) | Laptop / phone / gateway | Cloud (later) |
|---|---|---|---|
| ADC readout and calibration | ✔ | | |
| DSP (per-cycle Vrms/Irms/P/Q/PF/frequency, harmonics over ~10-cycle windows) | ✔ | | |
| Event detection | ✔ | | |
| Event classification (demo) | | ✔ | |
| Live view and labeling UX | | ✔ | |
| Model training | | local PC | ✔ |
| Fleet storage, model distribution | | | ✔ |
| INT8-quantized classifier for known appliances | later ✔ | | |

Event detection stays on the device because it needs the high-rate data around each event, and uploading raw data is about 2.7 GB/day per home.

**ADC link:** the ADS131M04 connects over SPI (SCLK/MOSI/MISO/CS) plus a DRDY interrupt, a master clock (CLKIN) and a reset line. CH0 = voltage, CH1 = current, CH2–3 spare. One frame is read per DRDY (status word + 4 × 24-bit words + CRC), so roughly 8 k frames/s at 8 kSPS (verify).

**Transport:** MQTT with a local broker (for example Mosquitto on the laptop), with event packets and 1 Hz aggregates as topics. USB serial stays available for raw-data capture during bring-up.

## Firmware

- **Language:** C/C++ on ESP-IDF (FreeRTOS). MicroPython is not used in the sampling path (GC pauses, timing jitter, phase error). It is acceptable only for bench scripts.
- **Task split:** one core handles SPI/DMA sampling and DSP. The other handles Wi-Fi, MQTT, OTA and config.
- **DSP (ESP-DSP):** per cycle, compute Vrms, Irms, P, Q, PF and frequency. Compute harmonics up to about the 25th, at 4–8 kSPS per channel.
- **Event detection:** adaptive step detection on P and Q. On each event, capture a raw-waveform window (inrush and V-I trajectory) from a PSRAM ring buffer.
- **Uplink:** send 1 Hz aggregates plus event packets. A "data logger" build writes raw data to an SD card for pilots.

## Hardware

- Split-core CT with a burden resistor (add mid-rail bias only if the chosen ADC front end needs it).
- Isolated voltage transformer, not a bare ZMPT101B.
- Anti-alias RC filter and proper mains isolation (BIS-aware).
- Verify all part specs against datasheets before committing to a schematic.

## ML pipeline (Python, off-device)

1. **Features:** ΔP, ΔQ, harmonic signature, inrush shape, V-I trajectory, normalized for Indian grid voltage swings.
2. **Baseline classifier:** Random Forest or LightGBM on the hand-built event features.
3. **Better features:** a small 1D-CNN on the transient and V-I trajectory.
4. **Per-home layer:** unsupervised clustering of events within a home, named through user labels ("new device detected, name it").
5. **Pretrained prior** for common Indian appliances.
6. **Energy attribution:** pair ON and OFF events and keep an "unknown" bucket.
7. **Later:** quantize to TFLite Micro / ESP-NN for on-device inference.
8. **Tooling:** NILMTK, PyTorch, pandas.
9. **Not used for the demo:** pure seq2point or FHMM approaches.

## Data collection

1. **Lab library:** many Indian appliances (fans with regulators, inverter and non-inverter ACs, pumps, geysers, induction cooktops, mixers, RO, fridges, LED/SMPS loads), each with a reference sub-meter.
2. **Pilots:** 20–50 homes across cities and house types, at least 3 months, spanning summer and winter, with smart-plug ground truth on the major loads.
3. **Format:** HDF5/Parquet (NILMTK-compatible), NTP/RTC timestamps, voltage logged alongside.
4. **Privacy:** DPDP Act 2023 consent flow.

## Phases

1. Analog front end and ADC bring-up, calibrated against a reference meter.
2. Firmware: sampling, DSP, event detection.
3. Data-logger build, then the lab appliance library.
4. Offline ML on lab data.
5. Pilot homes, local/cloud inference and labeling UX.
6. Edge model deployment. Later: small commercial and 3-phase.

## Verification

- **Bench:** P, Q and RMS error against a calibrated reference meter on known loads (resistive, motor, SMPS).
- **Sampling:** confirm no dropped DMA frames over 24 h, with V/I phase alignment checked using a resistive load (PF about 1).
- **Event detection:** precision and recall on lab appliance toggles against ground-truth timestamps.
- **ML:** per-appliance F1 on held-out homes (not held-out time within the same home) to measure real generalization.

## Open items

- Demo board build: evaluation module plus dev board, custom PCB, or both in sequence.
- Exact ESP32-S3 module variant and PSRAM size.
- Specific ADC part checks (input range, data rates, package, India stock and pricing).

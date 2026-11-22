# DSP, Event Detection, ML Approach and ADC Channels for PowerLenz

How the signal path, DSP engine, event detection and ML fit together on an ESP32-S3 with an external simultaneous-sampling ADC (ADS131M04). Topics are in signal-path order.

> Part names and specs below are recalled from memory. Verify against datasheets before committing to a schematic.

## 1. ADC channels and how they connect to the ESP32

**A channel** is one analog input with its own measurement path. The ADS131M04 has four, and each is a *differential pair* (AINxP and AINxN). It measures the voltage *between* the two pins.

- **Multiplexed ADCs** (like the ESP32's internal ADC) have one converter that switches between inputs. The channels are measured one after another, which causes phase skew.
- **Simultaneous ADCs** (like the ADS131M0x) have one converter per channel, all clocked together. All four channels capture the same instant.

**Use in PowerLenz:**
- CH0: voltage, from the isolated transformer, scaled down.
- CH1: current, from the CT's burden resistor.
- CH2 and CH3: spare, shorted or tied to a defined level so they don't pick up noise.

**Wiring to the ESP32-S3** (verify against the datasheet):

| Signal | Purpose |
|---|---|
| SCLK, MOSI (DIN), MISO (DOUT), CS | SPI bus. The ESP32 is the master. |
| DRDY | The ADC pulls this low when a new sample set is ready. It goes to an ESP32 GPIO interrupt. |
| CLKIN | The ADC's master clock, e.g. ~8 MHz. The ESP32 can generate it with its LEDC or I2S peripheral, or you use a crystal. |
| RESET (and SYNC, if used) | Control lines. |
| AVDD/DVDD and a clean ground | Power. Keep the analog and digital supplies separate. |

**Data flow:** On each DRDY, the ESP32 clocks out one *frame*: a status word, then one 24-bit word per channel, then a CRC. A frame is roughly 18 bytes. At 8 kSPS that's about 144 KB/s, which is trivial for SPI. The harder part is the *rate of events*: about 8000 interrupts per second. The usual fix is to have the ISR only signal a task (or to queue DMA transactions), and have that task fill a ring buffer.

## 2. The DSP engine: where it runs and how it's coded

**It runs on the ESP32-S3**, on the core you dedicate to measurement, in C/C++ on ESP-IDF using the ESP-DSP library. The S3 has a single-precision FPU and SIMD instructions that ESP-DSP uses for FFTs and dot products. The load is light: 2 channels × ~6.4 kSPS is well within its capacity.

**Processing pipeline:**
1. **Scale and calibrate.** Convert raw counts to volts and amps with per-unit gain constants. Remove DC offset.
2. **Phase-correct.** The CT leads the current slightly, and the filters add delay. Compensate with a fractional-sample delay, calibrated against a resistive load (PF ≈ 1).
3. **Find cycle boundaries.** Detect zero crossings of the voltage. Grid frequency in India drifts (roughly 49–50.5 Hz), so cycle-synchronous windows beat fixed ones.
4. **Per cycle, compute:**
   - Vrms, Irms
   - P = mean(v·i)
   - S = Vrms·Irms
   - Q = √(S² − P²), with a sign from the phase
   - PF and frequency
5. **Harmonics.** Run an FFT on the current (and voltage) over a window of ~10 cycles, or use Goertzel for selected harmonics. This gives the harmonic signature.
6. **Output.** Per-cycle numbers (50 per second), 1 s aggregates, and harmonics every ~200 ms to 1 s.

**Coding approach:** one hard-real-time task reads the ring buffer and runs steps 1–4. Harmonics and anything slower run in a lower-priority task. Test the math **off-device first**: record raw waveforms to a file, then write the same algorithm in Python (NumPy) as the reference, and check that the C code gives identical results.

## 3. Event detection: where it happens

**On the device. This is the one piece to firmly keep at the edge.** Reasons:
- Detection needs the raw, high-rate data around the event. Uploading everything is about 2.7 GB/day per home, which is impractical.
- Indian home internet is unreliable, and events must not be lost during an outage.
- Privacy is better if raw waveforms leave the house only when needed.

**How it works:**
1. Watch the per-cycle P and Q stream.
2. Compare a short pre-window mean with a short post-window mean. If the step exceeds an **adaptive threshold** (a few times the recent noise level, with an absolute floor, e.g. tens of watts), flag a candidate.
3. Wait for the signal to settle (motors and compressors ramp), debounce, and then mark the event.
4. Package it: timestamp, ΔP, ΔQ, steady values before and after, the transient (the 1–2 s of per-cycle P/Q/Irms), harmonics before and after, and a raw-waveform snapshot of a few cycles around the event.

The raw snapshot comes from a ring buffer in PSRAM (the S3 module usually has some). A more principled detector (CUSUM or a likelihood-ratio test) is a later upgrade if the simple one gives false triggers.

## 4. ML approach: what's best and why

| Approach | Strengths | Weaknesses | Verdict |
|---|---|---|---|
| **Combinatorial optimization / FHMM** | No training data needed for the optimizer itself. Interpretable. | Needs a model per appliance. Scales poorly beyond ~10 devices. Sensitive to noise and ambiguous loads. | Baseline only. |
| **Deep learning on aggregate sequences** (seq2point, BiLSTM, transformer variants) | Strong benchmark results, learns features itself. | Data-hungry, generalizes poorly to a new house, large models, usually low-rate input. | Not for the demo. Maybe later for long-running loads such as fridges. |
| **Event-based + feature classifier** | Data-efficient, works on the high-rate features already computed, interpretable, easy to improve per-home. | Needs good event detection. Struggles with continuously varying loads. | **Recommended.** |

**Why event-based is best here:**
- Small data at demo time, and this approach needs far less.
- It uses exactly the features the hardware is good at (P/Q steps, harmonics, inrush, V-I shape).
- It supports the user-labeling loop ("new device detected, name it") naturally.
- Per-home adaptation fits Indian appliance diversity, where no pretrained model will cover every fan and pump.
- As far as publicly described, Sense works along these lines, but its internals are not known.

**Staged plan:**
1. **Baseline:** hand-built features → Random Forest or LightGBM. Trainable in days from the lab appliance library.
2. **Better features:** a small 1D-CNN on the transient and V-I trajectory.
3. **Per-home layer:** cluster events within a home, and use user labels to name the clusters (few-shot).
4. **Energy attribution:** pair ON and OFF events, then estimate energy as power times duration. Keep an "unknown" bucket for the rest, and don't force a label.
5. **Later:** a sequence model for multi-state or continuously varying loads, and a self-supervised model pretrained on unlabeled waveforms.

**Evaluation:** hold out *whole homes*, not time slices of the same home. Otherwise F1 will look better than reality.

## 5. Where each piece runs

| Stage | ESP32-S3 | Phone / laptop / gateway | Cloud |
|---|---|---|---|
| Sampling and calibration | ✔ | | |
| DSP (P, Q, RMS, harmonics) | ✔ | | |
| Event detection | ✔ | | |
| Event classification (demo) | | ✔ | optional |
| Labeling UI | | ✔ | |
| Model training | | | ✔ (or a local PC) |
| Long-term storage and fleet | | | ✔ |
| Quantized classifier for known appliances | later ✔ | | |

## Decisions made

- **Demo backend:** a laptop / local Python service (for example FastAPI) on the same Wi-Fi receives event packets, classifies them, and serves a dashboard. A phone app or cloud backend comes after the models work.
- **Transport:** Wi-Fi with MQTT (for example a Mosquitto broker on the laptop), with event packets and 1 Hz aggregates as topics. USB serial stays available for raw-data capture during bring-up.

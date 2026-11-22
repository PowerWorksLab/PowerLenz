# ADC Options for PowerLenz: Internal vs Metering IC vs External ADC

Three ways to digitize the voltage and current signals in a NILM energy monitor built around an ESP32-S3.

> Part names and specs below are recalled from memory. Verify against datasheets before committing to a schematic.

## 1. ESP32(-S3) internal ADC

**What it is:** The SAR ADC built into the chip. It is 12-bit on paper and has two units (ADC1 and ADC2) with several channels each. The CT and voltage signals connect directly to GPIO pins, with only the analog conditioning in front.

**Pros**
- Zero extra BOM cost, no SPI bus, and the smallest PCB.
- Fastest to prototype. It's fine for a first bench experiment.
- The firmware is simple, using ESP-IDF `adc_continuous` (DMA mode).

**Cons**
- **Real accuracy is poor.**
  - Effective resolution is roughly 9–10 bits once noise and nonlinearity are included.
  - The response is nonlinear, especially near the rails, and needs per-chip calibration (eFuse calibration helps, but doesn't fix everything).
  - Noise from Wi-Fi radio bursts couples into the ADC.
- **No true simultaneous sampling.** V and I are sampled one after another, which adds a phase error. Active power is P = mean(v·i), so a small phase error gives a wrong P and Q, especially at low power factor. That matters a lot for NILM, because the P/Q plane is the main feature space.
- **ADC2 is unusable while Wi-Fi is on**, which leaves only ADC1's channels.
- **Weak at small currents.** Standby loads (a TV on standby, a phone charger) sit near the noise floor.
- **Not usable for a certified meter.**

**Verdict:** Use it for early experiments and learning the signal chain. Not suitable for shipping NILM.

## 2. Metering IC (ADE9000, ADE7953, ATM90E26/32, etc.)

**What it is:** A dedicated energy-metering chip, from vendors like Analog Devices and Microchip. Inside it has:
- Several simultaneous-sampling sigma-delta ADCs (16–24 bit).
- A hardwired DSP engine that computes the measurements for you.

It outputs finished numbers: Vrms, Irms, active, reactive and apparent power, PF, frequency, and sometimes harmonics, over SPI or UART. The ESP32 reads registers instead of doing the math.

**Pros**
- **Accurate out of the box.** These are designed for revenue-grade metering, with high dynamic range (often around 1000:1 in current).
- **Phase-matched channels** by design, plus built-in phase and gain calibration registers.
- **Low load on the MCU.** The ESP32 reads values once per cycle or per second, so it stays free for networking and ML.
- Faster path to standards compliance, such as BIS or IS 13779, since the chips are meant for this.

**Cons**
- **Limited raw-signal access, which hurts NILM.** Some parts expose only the computed values. Others (the ADE9000, for example) expose a waveform buffer, but with limits on rate or depth. Check each datasheet.
- **Fixed algorithms.** You can't change how P and Q are computed. If your features need something custom, such as V-I trajectory, high-order harmonics or inrush shape, you may not get them.
- Chip availability and cost vary. Some parts are single-source, and a chip that supports raw waveform streaming is pricier than a basic metering IC.
- You still need good analog front-end design (CT burden, divider or transformer, anti-alias filter).

**Verdict:** Excellent if you only need accurate P/Q/RMS (a smart meter or sub-meter). For NILM, pick a model that gives you waveform samples, or you'll limit what the ML can learn.

## 3. Full external ADC (ADS131M0x, MCP3912, ADS7xxx family, etc.)

**What it is:** A general-purpose multi-channel ADC, usually 24-bit sigma-delta with simultaneous sampling. It converts and streams the raw samples, and the ESP32 handles all the DSP: RMS, P, Q, harmonics, event detection and so on.

**Pros**
- **Full raw data.** You get every sample, so you can compute any feature, redo the algorithm later, and record raw waveforms for the dataset. This is what makes Sense-style NILM possible.
- **Simultaneous sampling**, so no V-to-I phase error from the ADC. Residual phase error from the CT and the filter can be calibrated in software.
- **High resolution and dynamic range**, which lets you see small standby loads and large AC loads on the same CT range.
- **Flexible.** You can change sample rate, filtering and algorithms in firmware, and improve accuracy by OTA update.
- ADS131M0x parts support DMA over SPI and sample rates in the kSPS range. Verify the exact figures in the datasheet.

**Cons**
- **More work in firmware.** You implement and calibrate RMS, power, phase compensation and harmonics (FFT) yourself. The ESP32-S3 has enough CPU for this, but it uses real cycles.
- **Higher BOM and PCB complexity.** You need a decent reference, clean power, careful layout, and an SPI bus with DRDY interrupt handling.
- **Calibration is on you.** There's no factory-calibrated metering engine, so you need a calibration procedure and a reference meter, and each unit may need a per-unit calibration step in production.
- **Certification is your job.** A metering IC gives you a head start on accuracy classes, and this doesn't.

**Verdict:** The best fit for a NILM product, and the recommended option. The cost is more engineering effort and more care with the analog layout.

## Side-by-side

| | Internal ADC | Metering IC | External ADC |
|---|---|---|---|
| Effective resolution | ~9–10 bit | 16–24 bit | 24 bit |
| Simultaneous V/I sampling | No | Yes | Yes |
| Raw waveform access | Yes (noisy) | Limited / model-dependent | Full |
| Accuracy out of the box | Poor | Excellent | Good after calibration |
| MCU workload | High | Low | Medium–high |
| Custom features / ML | Possible but limited by accuracy | Limited | Full freedom |
| Extra BOM / complexity | None | Medium | Medium–high |
| Best for | Prototype | Meters, sub-meters | NILM |

## A hybrid worth considering

Some designs use **both a metering IC and an external ADC**. The metering IC handles the accurate 1 Hz P/Q/RMS (a billing-grade number, and a ground truth to cross-check the ADC firmware against). The external ADC supplies the raw waveforms for NILM. That's more expensive, so it makes sense only for the pilot or reference unit, not the final product.

## Recommendation

- **Bench prototype:** the ESP32 internal ADC, only to learn.
- **Pilot and v1:** an external simultaneous-sampling ADC, with the metering IC as a calibration reference in the lab (a cheap commercial meter works too).
- **Later:** if cost matters, check whether a metering IC that exposes waveform data (such as the ADE9000 class) can replace it.

## Open follow-ups

- Compare specific parts: sample rates, SPI throughput, price and availability in India.

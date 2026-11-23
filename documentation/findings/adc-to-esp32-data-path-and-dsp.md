# From the ADC to the ESP32-S3: Data Path and DSP

How a sample travels from the ADS131M04 into the ESP32-S3, and how the DSP turns samples into Vrms, Irms, P, Q, PF, frequency and harmonics.

> The ADS131M04 details below are from memory. Verify them against the datasheet. The ESP32-S3 timings (FFT cost, interrupt latency) have not been measured.

## Where this fits

The discussion so far covered the sensors, signal conditioning, the ADC and the power supply (AC-DC module and LDOs). What remains is the data path from the ADC onward:

1. **ADC to ESP32-S3:** how a sample physically travels over SPI into memory (this document).
2. **DSP on the ESP32-S3:** turning samples into RMS, P, Q and harmonics (this document).
3. **Event detection:** spotting an appliance switching on or off.
4. **MQTT and the cloud:** getting events off the device, plus storage.
5. **Classification:** deciding which appliance it was.
6. **The subscription model.**
7. **Power cuts and timekeeping.**

---

# Part 1: How one sample gets from the ADC into the ESP32

The ADC runs on its own. Once it has a clock, it converts continuously and decides *when* each sample happens. The ESP32 only collects the results.

```
 CLKIN ──► ADC converts V and I together ──► new sample set ready
                                               │
                                          DRDY goes low
                                               │
                         ESP32 interrupt ◄─────┘
                               │
         read one frame over SPI (CS low, SCLK clocks it out on MISO)
                               │
                       store it in a ring buffer
                               │
                 DSP task reads from the buffer (Part 2)
```

## The pieces

- **CLKIN:** the ADC's master clock. As I recall, with an 8.192 MHz clock the internal modulator runs at half that (4.096 MHz), and dividing by an oversampling ratio of 512 gives 8 kSPS. Higher ratios give slower, lower-noise output.
- **DRDY** ("data ready"): the ADC pulls it low when a new sample set is ready. It goes to an ESP32 GPIO interrupt.
- **The frame:** one read per sample set. It holds a status word, one 24-bit word for each of the four channels, and a CRC. That is six 3-byte words, about 18 bytes.
- **SPI:** four wires (SCLK, MOSI, MISO, CS). The ESP32 is the master. At 8 kSPS you need about 144 KB/s, roughly 1.2 Mbit/s, so a 4–8 MHz SPI clock is plenty.

## Three ideas that make this robust

1. **The ADC sets the timing, not the ESP32.** The ADC samples V and I at the instants its own clock decides. The ESP32 can be a little late reading a frame without hurting accuracy, as long as it reads before the next conversion replaces the data. At 8 kSPS that gives it a window of about 125 µs. The datasheet says how a missed read is flagged.
2. **Keep the interrupt tiny.** DRDY fires 8,000 times a second. The interrupt routine should do almost nothing: signal a task, or let DMA do the SPI transfer by itself. The task then copies the frame into a ring buffer, a fixed block of memory that wraps around, so the DSP can read at its own pace.
3. **Use a clean clock.** Jitter on CLKIN becomes jitter in the sample instants, which shows up as noise and phase error. The ESP32 can generate a clock with its LEDC or I2S peripheral, but 8.192 MHz does not divide neatly from its internal clocks, so it would be approximate and jittery. A small dedicated 8.192 MHz crystal oscillator is cleaner. Check the datasheet's clock requirements.

## How the work splits across the two cores

- **Core 1:** SPI/DMA reading, the ring buffer and the DSP. Nothing here should block.
- **Core 0:** Wi-Fi, MQTT, OTA updates and configuration.

This keeps a Wi-Fi burst from ever stealing time from the sampling.

## Check your understanding

*Why doesn't the ESP32 need to read each frame at exactly the right instant?* The ADC fixed the sample instants already, and the frame waits in the ADC for up to one sample period.

---

# Part 2: The DSP on the ESP32-S3

This turns the stream of calibrated samples into numbers the rest of the system can use. Everything below runs on the ESP32-S3's measurement core.

## What goes in and what comes out

**In:** pairs of numbers, `v[k]` and `i[k]`, arriving 8,000 times a second. They are already converted to volts and amps using the calibration factors.

**Out, every mains cycle (50 times a second):** Vrms, Irms, P, Q, PF and frequency. Every few cycles it also produces the harmonics.

## 1. Remove the DC offset

The analog front end adds a tiny DC bias, and the ADC has its own offset. Over a whole number of cycles, a true AC wave averages to zero, so subtracting each channel's average removes the offset. Do this per window, not once, because it drifts with temperature.

## 2. Cut the stream into exact cycles

At 8 kSPS and 50 Hz there are 160 samples in a cycle. The grid isn't exactly 50 Hz, though. At 49.5 Hz a cycle is about 161.6 samples. A fixed 160-sample window would cut cycles in the wrong place, which smears the results.

So the window boundaries come from the voltage wave itself:

- Find where voltage crosses zero going upward. This is the **zero-crossing**.
- Interpolate between the two samples either side of the crossing, to find where it fell between samples:
  `crossing = k + (0 − v[k]) / (v[k+1] − v[k])`
- The samples between two consecutive crossings form exactly one cycle.
- The spacing between crossings gives the frequency: **f = fs ÷ (samples per cycle)**.

Two protections matter in Indian homes. Add a small hysteresis band so noise near zero can't trigger a false crossing. And if voltage is badly distorted (flat-topped by many switch-mode supplies), filter it lightly before finding the crossing.

## 3. The per-cycle sums

For the N samples in one cycle:

```
Vrms = sqrt( Σ v² / N )
Irms = sqrt( Σ i² / N )
P    =       Σ (v · i) / N       real power, watts
S    = Vrms × Irms               apparent power
PF   = P / S
```

- Accumulate the sums as you go, as each sample arrives, rather than storing the whole cycle.
- A 24-bit value squared is a 48-bit number, and summing 160 of them needs about 56 bits. Use 64-bit integers or double precision for the sums. A 32-bit float has only a 24-bit mantissa, and it quietly loses digits.

## 4. Reactive power, with its sign

The simple formula `Q = √(S² − P²)` has two weaknesses:

- It loses the sign. The sign says whether current lags voltage (a motor, inductive) or leads it (a capacitive input). That is a useful NILM clue.
- For non-linear loads like a phone charger, it also includes distortion power, not just the 50 Hz reactive part.

A cleaner way to get Q is to delay the voltage by a quarter cycle (about 40 samples) and compute `Q = Σ (v_delayed · i) / N`. That gives the fundamental reactive power with its sign. Then `S² = P² + Q² + D²`, and D is the distortion power. A large D relative to P is itself a strong fingerprint for electronic loads.

## 5. Phase compensation

From the calibration step, the current samples are shifted by a small fraction of a sample (for example 0.2 sample) before multiplying. That fraction is applied by interpolating between neighbouring samples. It is done once per sample, before steps 3 and 4.

## 6. Harmonics

Harmonics are multiples of 50 Hz: the 3rd at 150 Hz, the 5th at 250 Hz, and so on. To get them, you take a Fourier transform of the current. The catch is spectral leakage: if the window isn't exactly a whole number of cycles, energy smears across neighbouring frequencies.

The fix is to make each window match the grid:

1. Take 8 consecutive cycles, between zero-crossings.
2. Resample each cycle to exactly 128 points, by interpolating. This keeps the window synchronised even if the frequency drifts.
3. That gives 8 × 128 = 1,024 points, which suits an FFT.
4. Bin spacing is 50 ÷ 8 = 6.25 Hz, so the **n-th harmonic sits at bin 8n**. The 25th is at bin 200, well below the limit of bin 512.

This runs once every 8 cycles, about every 160 ms. The ESP-DSP library has FFT routines for the S3. It is a light load, but it has not been timed, so measure it on the real chip. From this you keep the harmonic magnitudes (and maybe phases) as features.

## 7. The sketch of the loop

```c
for each calibrated sample (v, i):
    v -= v_offset;  i = shift_fraction(i, delay);       // steps 1 and 5
    sum_vv += v*v;  sum_ii += i*i;  sum_vi += v*i;      // step 3
    sum_vq += v_quarter_delayed * i;                    // step 4
    if (rising zero crossing found):
        N = samples since last crossing
        publish { Vrms, Irms, P, Q, PF, f = fs / N }
        reset sums
        feed the harmonic resampler                     // step 6
```

## Why it is organised this way

- Everything is anchored to real mains cycles, so results stay accurate when the grid drifts.
- The heavy work (FFT) happens only every 8 cycles, so the sample loop stays light.
- Only compact numbers leave this stage, which is what makes edge computing and a small cloud bill possible.

## Check your understanding

*If the grid runs at 49.5 Hz and you used a fixed 160-sample window, what would go wrong?* The window would no longer hold a whole number of cycles. The leftover partial cycle would add error to the RMS and power, and would smear the harmonics.

---

## Next

Step 3, event detection: how the device decides a real step change happened, and what it sends.

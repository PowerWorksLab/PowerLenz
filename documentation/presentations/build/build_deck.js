// Builds ../powerlenz-front-end.pptx from the diagram PNGs in ../assets.
// Run: python3 -I extract_diagrams.py && node render_assets.js && node build_deck.js
const path = require("path");
const pptxgen = require("pptxgenjs");
const React = require("react");
const ReactDOMServer = require("react-dom/server");
const sharp = require("sharp");
const fa = require("react-icons/fa");
const { applyTheme } = require("/home/parallax/.claude/skills/synced/e1dda4d5-ca71-4f67-b7a4-670843eafdb9_cdb28aae-9d88-4792-8ba7-177777f44e36/pptx/scripts/apply_theme.js");

const ASSETS = path.join(__dirname, "..", "assets");
const OUT = path.join(__dirname, "..", "powerlenz-front-end.pptx");

const THEME = {
  name: "PowerLenz",
  headFontFace: "Cambria",
  bodyFontFace: "Calibri",
  colors: {
    dk1: "1B2227", lt1: "FFFFFF", dk2: "0E1B26", lt2: "EEF3F7",
    accent1: "1F6FB5", // analog signal
    accent2: "C2362B", // mains
    accent3: "A9650A", // DC power
    accent4: "027A8A", // cloud
    accent5: "5D6A73", // muted slate
    accent6: "9FB0BE", // muted on dark
    hlink: "1F6FB5", folHlink: "5D6A73",
  },
};

const pres = new pptxgen();
pres.layout = "LAYOUT_WIDE"; // 13.33 x 7.5 in
pres.title = "PowerLenz Front End";
pres.subject = "Voltage and current sensing front end for an ESP32-S3 NILM energy monitor";
pres.author = "PowerLenz";
pres.theme = { headFontFace: THEME.headFontFace, bodyFontFace: THEME.bodyFontFace };
const C = pres.SchemeColor;
const SH = pres.ShapeType;

// ---------- layouts ----------
pres.defineSlideMaster({
  title: "CONTENT",
  background: { color: C.background1 },
  margin: [0.5, 0.6, 0.6, 0.6],
  objects: [
    { placeholder: { options: { name: "title", type: "title", x: 0.6, y: 0.35, w: 12.13, h: 0.95, fontSize: 32, bold: true, color: C.text2, valign: "middle", margin: 0 }, text: "" } },
  ],
  slideNumber: { x: 12.2, y: 7.0, w: 0.55, h: 0.3, fontSize: 11, color: C.accent5, align: "right" },
});
// ---------- helpers ----------
const sizes = {};
async function loadAsset(name) {
  const file = path.join(ASSETS, name + ".png");
  const m = await sharp(file).metadata();
  sizes[name] = { file, ratio: m.width / m.height };
}
function picture(slide, name, x, y, o, alt) {
  const s = sizes[name];
  const w = o.w || o.h * s.ratio;
  const h = o.h || o.w / s.ratio;
  slide.addImage({ path: s.file, x, y, w, h, altText: alt, objectName: name });
  if (o.frame !== false) slide.addShape(SH.rect, { x, y, w, h, fill: { type: "none" }, line: { color: C.accent6, width: 0.75 }, objectName: name + " frame" });
  return { w, h };
}
async function iconData(Comp, color) {
  const svg = ReactDOMServer.renderToStaticMarkup(React.createElement(Comp, { color: color || "#FFFFFF", size: "256" }));
  const buf = await sharp(Buffer.from(svg)).png().toBuffer();
  return "image/png;base64," + buf.toString("base64");
}
async function iconBadge(slide, Comp, x, y, d, fill, name) {
  slide.addShape(SH.ellipse, { x, y, w: d, h: d, fill: { color: fill }, line: { type: "none" }, objectName: name + " badge" });
  const pad = d * 0.27;
  slide.addImage({ data: await iconData(Comp), x: x + pad, y: y + pad, w: d - 2 * pad, h: d - 2 * pad, altText: name, objectName: name + " icon" });
}
function card(slide, x, y, w, h, fill, name) {
  slide.addShape(SH.roundRect, { x, y, w, h, rectRadius: 0.08, fill: { color: fill || C.background2 }, line: { type: "none" }, objectName: name || "card" });
}
function text(slide, runs, o) {
  slide.addText(runs, Object.assign({ isTextBox: true, margin: 0, valign: "top", fontSize: 15, color: C.text1 }, o));
}
function bullets(items, o) {
  return items.map((t, i) => ({ text: t, options: Object.assign({ bullet: true, breakLine: i < items.length - 1, paraSpaceAfter: 6 }, o) }));
}
function title(slide, s) { slide.addText(s, { placeholder: "title" }); }
function section(name) { pres.addSection({ title: name }); }
function add(master, sec) { return pres.addSlide({ masterName: master, sectionTitle: sec }); }

(async () => {
  for (const n of ["schematic-full", "schematic-mains", "schematic-chains", "schematic-power-adc", "ct-clamp", "filter-wave", "filter-response", "sampling"]) await loadAsset(n);

  section("Overview");

  // ===== 2. Pipeline =====
  let s = add("CONTENT", "Overview");
  title(s, "From the mains wire to the app");
  const flow = [
    ["Mains wire", "230 V, 50 Hz, single phase", C.accent2],
    ["Sensors", "CT clamp on live, voltage transformer", C.accent1],
    ["Conditioning", "Burden, divider, RC filter", C.accent1],
    ["ADC", "ADS131M04, 24-bit, simultaneous", C.text2],
    ["ESP32-S3", "DSP and event detection", C.text2],
    ["Cloud and app", "Classify, store, notify", C.accent4],
  ];
  const fw = 1.75, fgap = 0.326;
  flow.forEach((f, i) => {
    const x = 0.6 + i * (fw + fgap);
    s.addText(
      [{ text: f[0], options: { bold: true, fontSize: 17, breakLine: true, paraSpaceAfter: 6 } }, { text: f[1], options: { fontSize: 13 } }],
      { shape: SH.roundRect, rectRadius: 0.08, isTextBox: true, x, y: 1.65, w: fw, h: 1.65, fill: { color: f[2] }, color: C.background1, valign: "top", margin: 10, objectName: "flow " + f[0] }
    );
    if (i < flow.length - 1) s.addShape(SH.rightArrow, { x: x + fw + 0.05, y: 2.35, w: 0.22, h: 0.28, fill: { color: C.accent5 }, line: { type: "none" }, objectName: "flow arrow " + (i + 1) });
  });
  const cw = 3.91;
  const cards = [
    [fa.FaWaveSquare, C.accent1, "Analog stays simple", "Only small voltages reach the ADC. The CT and the transformer keep the electronics isolated from mains."],
    [fa.FaMicrochip, C.text2, "Events are found on the device", "The ESP32-S3 spots step changes in power and sends compact event packets. Raw waveforms would be about 2.7 GB a day."],
    [fa.FaCloud, C.accent4, "Classification lives in the cloud", "The app cannot run in the background, so the cloud receives the MQTT messages, classifies events and stores each home's data."],
  ];
  for (let i = 0; i < cards.length; i++) {
    const x = 0.6 + i * (cw + 0.2), c = cards[i];
    card(s, x, 3.75, cw, 3.05, C.background2, "card " + c[2]);
    await iconBadge(s, c[0], x + 0.3, 4.0, 0.7, c[1], c[2]);
    text(s, c[2], { x: x + 0.3, y: 4.9, w: cw - 0.6, h: 0.4, fontSize: 18, bold: true, color: C.text2 });
    text(s, c[3], { x: x + 0.3, y: 5.35, w: cw - 0.6, h: 1.35, fontSize: 15 });
  }
  s.addNotes("Pipeline: mains wire, sensors, conditioning, ADC, ESP32-S3, then MQTT to the cloud. Event detection happens on the ESP32-S3 because raw upload is impractical. Classification and storage live in the cloud because a phone app cannot run in the background; this is also what a subscription would pay for.");

  // ===== 3. Schematic overview =====
  s = add("CONTENT", "Overview");
  title(s, "The front end at a glance");
  picture(s, "schematic-full", 0.6, 1.5, { h: 5.45 }, "Block-level schematic from the incoming live wire through the CT, voltage transformer and AC-DC module, then the signal chains, ADC and ESP32-S3");
  const lx = 9.2;
  [["230 V mains", C.accent2], ["Analog signal", C.accent1], ["DC power", C.accent3], ["Digital", C.accent5]].forEach((l, i) => {
    s.addShape(SH.rect, { x: lx, y: 1.68 + i * 0.4, w: 0.42, h: 0.1, fill: { color: l[1] }, line: { type: "none" }, objectName: "legend " + l[0] });
    text(s, l[0], { x: lx + 0.6, y: 1.57 + i * 0.4, w: 2.9, h: 0.32, fontSize: 14, color: C.accent5, valign: "middle" });
  });
  text(s, bullets([
    "Only the CT, the voltage transformer and the AC-DC module cross the isolation barrier.",
    "Both sensor signals are scaled and filtered, then read by one ADC at the same instant.",
    "The ESP32-S3 runs the DSP and finds events.",
  ]), { x: lx, y: 3.4, w: 3.53, h: 3.3, fontSize: 15 });
  s.addNotes("Full schematic. Red is mains, blue is analog signal, amber is DC power, grey is digital. The next slides zoom into each region.");

  // ===== 5. Mains side zoom =====
  section("Mains side");
  s = add("CONTENT", "Mains side");
  title(s, "What sits on the mains side, and why");
  picture(s, "schematic-mains", 0.6, 1.55, { w: 8.2 }, "The live wire passes through the CT clamp. A fused tap feeds a MOV and the voltage transformer, which straddles the isolation barrier");
  const items5 = [
    ["Fuse", "Opens if our own circuit shorts. The home's breaker is far too large to protect a PCB."],
    ["MOV (surge clamp)", "Idles at 230 V and conducts when a voltage spike hits, clamping it. A fuse is too slow for microsecond spikes."],
    ["Voltage transformer", "Steps 230 V down to about 9 V. The two coils share only a magnetic field, so the electronics are isolated."],
  ];
  items5.forEach((it, i) => {
    text(s, it[0], { x: 9.1, y: 1.55 + i * 1.7, w: 3.63, h: 0.35, fontSize: 18, bold: true, color: C.accent2 });
    text(s, it[1], { x: 9.1, y: 1.95 + i * 1.7, w: 3.63, h: 1.25, fontSize: 15 });
  });
  s.addNotes("Fuse: sized for our tiny load (tens of mA), rated 250 V AC with adequate breaking capacity, slow-blow to ride through inrush. MOV: voltage-dependent resistor, wears out with surges and tends to fail short-circuit, which is why the fuse sits in front. Pick its continuous rating above the highest steady voltage; Indian grids run high, so 300 V or more may be wiser. Verify against datasheets. Transformer: Vs/Vp = Ns/Np, so 230 V : 9 V is about 25.6 : 1; AC only, isolation comes from magnetic coupling.");

  // ===== 6. CT clamp =====
  section("Current and voltage sensing");
  s = add("CONTENT", "Current and voltage sensing");
  title(s, "Inside the CT clamp");
  picture(s, "ct-clamp", 0.6, 1.4, { w: 12.13 }, "Cross-section of a split-core CT: the live wire is one primary turn, flux circles in the iron core, a 2000-turn secondary drives a burden resistor, and the voltage goes to the ADC");
  text(s, "Example values: 10 A in the wire, a 2000:1 CT and a 22 Ω burden. Red is mains and blue is the analog signal.", { x: 0.6, y: 6.8, w: 11.4, h: 0.3, fontSize: 12, color: C.accent5 });
  s.addNotes("Five steps: 1) the wire's AC current makes a magnetic field; 2) the iron core gathers it as flux; 3) the changing flux drives a current in the 2000-turn secondary, so the secondary current is the wire current divided by 2000; 4) Rb turns that current into a voltage; 5) the voltage goes through Rf and Cf to ADC CH1+, with the other lead tied to analog ground.");

  // ===== 7. Rb =====
  s = add("CONTENT", "Current and voltage sensing");
  title(s, "The ADC reads voltage, never current");
  const chain = [
    ["Wire current", "10 A rms", "peak 14.1 A", C.accent2],
    ["CT secondary", "5 mA rms", "÷ 2000", C.accent1],
    ["Across Rb", "110 mV rms", "× 22 Ω", C.accent1],
    ["ADC code", "≈ 1.09 M", "counts at the peak", C.text2],
    ["Firmware", "10 A rms", "× 2000 ÷ 22 Ω", C.text2],
  ];
  const kw = 2.2, kgap = 0.2825;
  chain.forEach((c, i) => {
    const x = 0.6 + i * (kw + kgap);
    s.addText(
      [{ text: c[0], options: { fontSize: 14, breakLine: true } }, { text: c[1], options: { fontSize: 24, bold: true, breakLine: true } }, { text: c[2], options: { fontSize: 13 } }],
      { shape: SH.roundRect, rectRadius: 0.08, isTextBox: true, x, y: 1.55, w: kw, h: 1.5, fill: { color: c[3] }, color: C.background1, valign: "middle", align: "center", margin: 7, objectName: "chain " + c[0] }
    );
    if (i < chain.length - 1) s.addShape(SH.rightArrow, { x: x + kw + 0.03, y: 2.18, w: 0.22, h: 0.25, fill: { color: C.accent5 }, line: { type: "none" }, objectName: "chain arrow " + (i + 1) });
  });
  const hw = 5.965;
  card(s, 0.6, 3.4, hw, 3.4, C.background2, "card why Rb");
  text(s, "Why a burden resistor", { x: 0.9, y: 3.6, w: hw - 0.6, h: 0.4, fontSize: 20, bold: true, color: C.text2 });
  text(s, bullets([
    "A CT is a current source. It pushes out 1/2000 of the wire current, whatever it is connected to.",
    "V = I × R turns that current into a voltage the ADC can read.",
    "Never leave a current-output CT open-circuit. The voltage can climb to hundreds of volts.",
  ]), { x: 0.9, y: 4.15, w: hw - 0.6, h: 2.5, fontSize: 15 });
  card(s, 0.6 + hw + 0.2, 3.4, hw, 3.4, C.background2, "card sizing Rb");
  text(s, "Sizing Rb", { x: 0.9 + hw + 0.2, y: 3.6, w: hw - 0.6, h: 0.4, fontSize: 20, bold: true, color: C.text2 });
  text(s, bullets([
    "Too large: heavy loads clip the ADC.",
    "Too small: standby loads vanish into noise.",
    "22 Ω with a ±1.2 V full scale clips above about 77 A rms. Verify the full scale in the datasheet.",
  ]), { x: 0.9 + hw + 0.2, y: 4.15, w: hw - 0.6, h: 2.5, fontSize: 15 });
  s.addNotes("The ADC only ever measures voltage. CH1 is called the current channel because its voltage is proportional to the wire current. The conversion back happens in firmware: I_wire = (V_adc / Rb) x 2000, with calibration. Every current sensor ends in a voltage: a shunt, a Hall sensor with built-in electronics, or a CT with a burden.");

  // ===== 8. Chains zoom =====
  s = add("CONTENT", "Current and voltage sensing");
  title(s, "Scaling both signals down for the ADC");
  picture(s, "schematic-chains", 0.6, 1.55, { w: 8.2 }, "The voltage path from the transformer secondary through a divider and RC filter to CH0, and the current path from the CT through the burden and RC filter to CH1");
  const items8 = [
    ["Voltage path", C.accent1, "230 V, transformer to about 9 V, divider 1 : 16, then 0.80 V peak at the ADC."],
    ["Current path", C.accent1, "10 A, CT to 5 mA, Rb of 22 Ω, then 0.16 V peak at the ADC."],
    ["Both paths", C.text2, "An Rf and Cf filter, then the ADC reads each one against analog ground (AGND)."],
  ];
  items8.forEach((it, i) => {
    text(s, it[0], { x: 9.1, y: 1.55 + i * 1.7, w: 3.63, h: 0.35, fontSize: 18, bold: true, color: it[1] });
    text(s, it[2], { x: 9.1, y: 1.95 + i * 1.7, w: 3.63, h: 1.25, fontSize: 15 });
  });
  s.addNotes("Divider sizing: at the highest mains voltage you want to handle (say 280 V rms) the secondary reaches 15.5 V peak and the divider brings it to 0.97 V peak, inside the +/-1.2 V range. Analog ground is only the low-voltage reference node. Tying one CT lead to it pins the isolated secondary's potential so it cannot drift out of the ADC's input range.");

  // ===== 9. Filter waveform =====
  section("Filtering");
  s = add("CONTENT", "Filtering");
  title(s, "What the Rf + Cf filter does to the signal");
  picture(s, "filter-wave", 0.6, 1.55, { w: 7.8 }, "A 50 Hz wave with fast ripple before the filter and the same wave clean after it");
  text(s, "What it does", { x: 8.8, y: 1.55, w: 3.93, h: 0.4, fontSize: 20, bold: true, color: C.text2 });
  text(s, bullets([
    "The 50 Hz wave and its harmonics pass almost untouched, 99.999% at 50 Hz.",
    "The capacitor shorts fast ripple to ground before the ADC samples it.",
    "A tone near the sampling rate would fold down onto 50 Hz and could not be removed afterwards. That is why the filter comes first.",
  ]), { x: 8.8, y: 2.1, w: 3.93, h: 4.6, fontSize: 15 });
  s.addNotes("The left plot draws the ripple slowed down; the real ripple is thousands of times faster. Capacitor impedance Xc = 1 / (2 pi f C): huge at 50 Hz, tiny at MHz. Cutoff fc = 1 / (2 pi R C); with 1 kOhm and 10 nF that is about 16 kHz. Aliasing: with an 8 kHz sample rate, a 7,950 Hz tone appears at 50 Hz after sampling.");

  // ===== 10. Filter response =====
  s = add("CONTENT", "Filtering");
  title(s, "A gradual filter, not a brick wall");
  picture(s, "filter-response", 0.6, 1.55, { w: 8.0 }, "Filter gain against frequency on a log scale: flat through the mains band, down 3 dB at 16 kHz, down 36 dB at 1 MHz and 56 dB at 10 MHz");
  text(s, "Can remove", { x: 8.9, y: 1.55, w: 3.83, h: 0.35, fontSize: 18, bold: true, color: C.accent1 });
  text(s, "Switching supplies, sparks from motors and relays, and clock edges. Tens of kHz and up.", { x: 8.9, y: 1.95, w: 3.83, h: 1.2, fontSize: 15 });
  text(s, "Cannot remove", { x: 8.9, y: 3.3, w: 3.83, h: 0.35, fontSize: 18, bold: true, color: C.accent2 });
  text(s, "Wi-Fi burst ripple on the supply and 50 Hz hum. They sit too low. Fix with a separate analog LDO, careful layout and averaging in the DSP.", { x: 8.9, y: 3.7, w: 3.83, h: 1.8, fontSize: 15 });
  text(s, "Example values: Rf = 1 kΩ, Cf = 10 nF.", { x: 8.9, y: 5.8, w: 3.83, h: 0.4, fontSize: 12, color: C.accent5 });
  s.addNotes("The filter attenuates 20 dB for every tenfold increase in frequency. The ADC's own digital filter then removes what remains between its 4 kHz output limit and the MHz range, so the RC filter does not set the 4 kHz limit. The noise frequency ranges are typical, not measured on our hardware; check on the first board with an oscilloscope. Also note the filter's phase lag: source resistance in front of the filter adds to Rf, so the voltage and current channels lag differently (0.35 and 0.18 degrees in the example) and the phase calibration must absorb the difference.");

  // ===== ADC types =====
  section("ADC and power");
  const th = (t, fill) => ({ text: t, options: { bold: true, color: C.background1, fill: { color: fill || C.text2 }, valign: "middle" } });
  const td = (t, o) => ({ text: t, options: Object.assign({ color: C.text1, valign: "middle" }, o || {}) });
  const tableBorder = { type: "solid", pt: 0.75, color: "CFD6DB" };

  // ===== Three options =====
  s = add("CONTENT", "ADC and power");
  title(s, "Internal, metering IC or external ADC");
  const hi = { fill: { color: C.background2 } };
  const rows3 = [
    ["Effective resolution", "about 9–10 bit", "16–24 bit", "24 bit"],
    ["V and I sampled together", "No, one after another", "Yes", "Yes"],
    ["Raw waveform access", "Yes, but noisy", "Limited, depends on the part", "Full"],
    ["Accuracy out of the box", "Poor", "Excellent", "Good after calibration"],
    ["Work for the ESP32", "High", "Low", "Medium to high"],
    ["Extra cost and board work", "None", "Medium", "Medium to high"],
    ["Best for", "Prototype", "Meters and sub-meters", "NILM"],
  ];
  s.addTable(
    [[th(""), th("Internal ADC (ESP32)"), th("Metering IC"), th("External ADC", C.accent1)]].concat(
      rows3.map((r) => r.map((t, ci) => td(t, Object.assign({ bold: ci === 0 || ci === 3 }, ci === 3 ? hi : {}))))
    ),
    { x: 0.6, y: 1.55, w: 12.13, colW: [3.2, 2.9, 3.0, 3.03], rowH: 0.56, fontSize: 14, border: tableBorder, margin: [0.04, 0.1, 0.04, 0.1] }
  );
  text(s, "Pilot units can combine both: a metering IC gives the accurate 1 Hz reference while the external ADC supplies raw waveforms.", { x: 0.6, y: 6.3, w: 12.13, h: 0.6, fontSize: 16, color: C.text2 });
  s.addNotes("Internal ADC: effective resolution about 9-10 bits, nonlinear, picks up Wi-Fi noise, and ADC2 cannot be used while Wi-Fi is on. Metering IC: calibrated, revenue-grade accuracy and low MCU load, but fixed algorithms and limited raw-signal access; some parts such as the ADE9000 class expose a waveform buffer (check the datasheet). External ADC: full raw data and flexibility, but more firmware, calibration and layout work, and certification is our job.");

  // ===== Why simultaneous =====
  s = add("CONTENT", "ADC and power");
  title(s, "Why both channels must be sampled together");
  const sp = picture(s, "sampling", 0.6, 1.55, { w: 7.6 }, "Two stacked plots of a voltage wave and a lagging current wave. In the top plot the voltage and current are sampled a gap apart; in the bottom plot both are sampled at the same instant");
  const cx = 0.6 + sp.w + 0.35, cw2 = 12.73 - cx;
  card(s, cx, 1.55, cw2, 5.2, C.background2, "card phase error");
  text(s, "What the gap costs", { x: cx + 0.3, y: 1.75, w: cw2 - 0.6, h: 0.4, fontSize: 20, bold: true, color: C.text2 });
  text(s, "Phase error = 360° × 50 Hz × the gap between the V and I samples.", { x: cx + 0.3, y: 2.3, w: cw2 - 0.6, h: 0.8, fontSize: 15 });
  text(s, "0.5%", { x: cx + 0.3, y: 3.25, w: cw2 - 0.6, h: 0.85, fontSize: 44, bold: true, color: C.accent2 });
  text(s, "power error at PF 0.5 with a 10 µs gap (0.18°)", { x: cx + 0.3, y: 4.1, w: cw2 - 0.6, h: 0.55, fontSize: 14, color: C.accent5 });
  text(s, "5%", { x: cx + 0.3, y: 4.75, w: cw2 - 0.6, h: 0.85, fontSize: 44, bold: true, color: C.accent2 });
  text(s, "with a 100 µs gap (1.8°). Our ADC has no gap.", { x: cx + 0.3, y: 5.6, w: cw2 - 0.6, h: 0.9, fontSize: 14, color: C.accent5 });
  s.addNotes("Power is the average of v times i, so a small phase error between the two samples shifts P and Q, especially at low power factor. Error in P is roughly the phase error in radians times tan(theta): 0.18 degrees is 0.0031 rad, times tan 60 degrees (1.73) is about 0.5%; 1.8 degrees gives about 5%. P and Q are the main NILM feature space. A multiplexed ADC can be corrected by interpolation, but that is one more error source. The gap in the diagram is drawn far larger than the real one.");

  // ===== Why ADS131M04 =====
  s = add("CONTENT", "ADC and power");
  title(s, "Why we chose the ADS131M04");
  const why2 = [
    ["Simultaneous sampling", "One converter per channel, all clocked together, so there is no V to I phase skew."],
    ["Full raw data", "Every sample is available, so we can compute any feature and record waveforms for the dataset."],
    ["Simple analog front end", "Bipolar differential inputs take the burden voltage directly, with no mid-rail bias network (verify)."],
    ["PGA and reference built in", "Fewer external parts, and one CT range can cover standby chargers and geysers."],
    ["The sample rate fits", "4 to 8 kSPS per channel gives harmonics up to about the 25th and the inrush shape."],
    ["Easy firmware", "One SPI driver plus a DRDY interrupt. Two spare channels allow a second CT later."],
  ];
  why2.forEach((w, i) => {
    const x = 0.6 + (i % 3) * (cw + 0.2), y = 1.5 + Math.floor(i / 3) * 1.75;
    card(s, x, y, cw, 1.6, C.background2, "card " + w[0]);
    text(s, w[0], { x: x + 0.3, y: y + 0.18, w: cw - 0.6, h: 0.35, fontSize: 17, bold: true, color: C.accent1 });
    text(s, w[1], { x: x + 0.3, y: y + 0.6, w: cw - 0.6, h: 0.95, fontSize: 14 });
  });
  card(s, 0.6, 5.1, 12.13, 1.6, C.text2, "banner what we take on");
  text(s, "What we take on", { x: 0.9, y: 5.25, w: 5, h: 0.35, fontSize: 17, bold: true, color: C.background1 });
  text(s, bullets(["More firmware: RMS, power, phase compensation and harmonics are ours to write.", "Calibration is ours: a reference meter and a per-unit procedure."], { color: C.background1 }), { x: 0.9, y: 5.7, w: 5.6, h: 0.95, fontSize: 14, color: C.background1 });
  text(s, bullets(["A higher parts cost and careful analog layout.", "Certification is ours too. A metering IC gives a head start."], { color: C.background1 }), { x: 6.85, y: 5.7, w: 5.6, h: 0.95, fontSize: 14, color: C.background1 });
  text(s, "Second source: MCP3912B (the older MCP3912 is not recommended for new designs). Specs are from memory, so verify them in the datasheet.", { x: 0.6, y: 6.78, w: 10, h: 0.25, fontSize: 11, color: C.accent5 });
  s.addNotes("Why the ADS131M04 for the demo: simultaneous sampling, raw data access, bipolar differential inputs that let the burden output go straight in, built-in PGA and reference, an output rate that covers the NILM features, and simple firmware (one SPI driver and a DRDY interrupt). Two of the four channels are used (voltage and current); the other two are spare for a second CT or three-phase later, so no board respin. Second source: MCP3912 if TI parts are hard to get in India. Specs are recalled from memory: verify input range, PGA, output data rates, package, stock and price before ordering. For the demo board: an evaluation module plus an ESP32-S3 dev board for early firmware bring-up while a custom PCB (assembled by a service for the fine-pitch ADC) is designed in parallel.");

  // ===== 11. Power + ADC zoom =====
  s = add("CONTENT", "ADC and power");
  title(s, "Power, ADC and ESP32-S3 on the safe side");
  const pa = picture(s, "schematic-power-adc", 0.6, 1.45, { h: 5.5 }, "The AC-DC module, two 3.3 V LDOs, the ADS131M04 and the ESP32-S3 with the SPI and control wires between them");
  const rx = 0.6 + pa.w + 0.5, rw = 12.73 - rx;
  const items11 = [
    [fa.FaPlug, C.accent3, "AC-DC module", "Isolated 5 V from 230 V, with an input range of roughly 85–265 V AC (check the datasheet). Kept off the voltage transformer so its current pulses cannot distort the measurement."],
    [fa.FaBolt, C.accent3, "Two 3.3 V LDOs", "The analog LDO gives the ADC a quiet supply. The digital LDO feeds the ESP32-S3, which pulls big current pulses when Wi-Fi transmits."],
    [fa.FaMicrochip, C.text2, "SPI link", "SCLK, MOSI, MISO and CS, plus DRDY (an interrupt, about 8,000 a second at 8 kSPS), CLKIN and RESET. The ESP32-S3 is the SPI master."],
  ];
  for (let i = 0; i < items11.length; i++) {
    const y = 1.45 + i * 1.88, it = items11[i];
    card(s, rx, y, rw, 1.72, C.background2, "card " + it[2]);
    await iconBadge(s, it[0], rx + 0.25, y + 0.3, 0.6, it[1], it[2]);
    text(s, it[2], { x: rx + 1.1, y: y + 0.15, w: rw - 1.35, h: 0.35, fontSize: 18, bold: true, color: C.text2 });
    text(s, it[3], { x: rx + 1.1, y: y + 0.55, w: rw - 1.35, h: 1.1, fontSize: 14 });
  }
  s.addNotes("The AC-DC module is a small flyback switching supply: rectifier, switch, high-frequency transformer, output rectifier and an optocoupler feedback loop. It is the main noise source on the 5 V rail, which is why the analog supply has its own low-noise LDO. An LDO (low-dropout regulator) burns the voltage difference as heat: power lost = (Vin - Vout) x current. Choose parts for peak current, dropout, noise and PSRR.");

  // ===== Components and prices =====
  const link = (label, url) => ({ text: label, options: { hyperlink: { url, tooltip: url }, color: C.accent1, underline: { style: "sng" }, valign: "middle" } });
  const links = (items) => ({
    text: items.reduce((acc, it, i) => acc.concat(i ? [{ text: ", ", options: { color: C.text1 } }] : [], [link(it[0], it[1])]), []),
    options: { valign: "middle" },
  });
  const priceTable = (slide, rows, y, rowH) => slide.addTable(
    [[th("Block"), th("Part"), th("Price in ₹"), th("Where to buy")]].concat(
      rows.map((r) => [td(r[0], { bold: true }), td(r[1]), td(r[2]), typeof r[3] === "string" ? td(r[3]) : links(r[3])])
    ),
    { x: 0.6, y, w: 12.13, colW: [2.2, 3.9, 2.5, 3.53], rowH, fontSize: 14, border: tableBorder, margin: [0.03, 0.1, 0.03, 0.1] }
  );

  s = add("CONTENT", "ADC and power");
  title(s, "Components and prices: sensing and processing");
  priceTable(s, [
    ["Microcontroller", "ESP32-S3-DevKitC-1 N16R8", "₹1,100 + tax", [["IndiaMART seller", "https://m.indiamart.com/proddetail/esp32-s3-devkitc-1-n16r8-type-c-esp32-s3-development-board-wi-fi-ble-mcu-module-2856307778633.html"]]],
    ["ADC chip", "TI ADS131M04IPWR (TSSOP-20)", "₹565 to ₹769", [["Lion Circuits", "https://www.lioncircuits.com/parts/ADS131M04IPWR"], ["Digi-Key India", "https://www.digikey.in/en/products/detail/texas-instruments/ADS131M04IPWR/10448283"]]],
    ["ADC adapter", "TSSOP-20 to DIP adapter, 0.65 mm", "₹40 + GST", [["Probots", "https://probots.co.in/sop20-ssop20-to-dip20-double-sided-adapter-board.html"]]],
    ["ADC eval module", "ADS131M04EVM (optional)", "₹27,955", [["Digi-Key India", "https://www.digikey.in/en/products/detail/texas-instruments/ADS131M04EVM/10273255"]]],
    ["Second-source ADC", "MCP3912B (not the older MCP3912)", "India price not found", [["Digi-Key India", "https://www.digikey.in/en/products/detail/microchip-technology/MCP3912BA1-E-MQ/26653511"]]],
    ["Current sensor", "SCT-013-000, 100 A : 50 mA", "₹424 to ₹550", [["Electropi", "https://www.electropi.in/sct-013-000-100a-non-invasive-ac-current-sensor-split-core-type-clamp-meter-sensor"], ["Robodo", "https://robodo.in/products/100a-sct-013-000-non-invasive-ac-current-sensor-split-core-current-transformer"]]],
    ["Resistors", "22 Ω, 1 kΩ, 15 kΩ, 1%, 1/4 W", "₹15 per 10 + GST", [["Hubtronics", "https://hubtronics.in/res/mfr-22-ohms"]]],
    ["Filter capacitors", "10 nF C0G, 2 pieces", "₹99.70 each", [["Mouser India", "https://www.mouser.in/en/c/passive-components/capacitors/ceramic-capacitors/"]]],
    ["Voltage transformer", "230 V : 9 V, 1 VA PCB transformer", "₹190 to ₹683", [["IndiaMART", "https://m.indiamart.com/proddetail/pcb-mounting-transformers-encapsulated-2852858106573.html"], ["element14 India", "https://in.element14.com/c/transformers/pcb-transformers"]]],
    ["Lab reference", "PZEM-004T with 100 A CT", "₹569", [["Robocraze", "https://robocraze.com/products/peacefair-pzem-004t-multi-function-ac-power-meter-for-energy-measurement"]]],
  ], 1.45, 0.46);
  text(s, "Seen on 23 Nov 2026. Prices change and GST treatment differs by seller. The chip showed two different prices on Digi-Key India (₹531 and ₹769), so check the live page. Resistor and capacitor prices are single-pack listings.", { x: 0.6, y: 6.6, w: 11.4, h: 0.4, fontSize: 11, color: C.accent5 });
  s.addNotes("Sources and caveats, all seen on 23 Nov 2026. ESP32-S3-DevKitC-1 N16R8: IndiaMART seller at 1,100 rupees excluding taxes; the official board was listed at 1,264.95 rupees at Mouser India (on order); generic clones are cheaper, around 926 to 1,200. ADS131M04IPWR: Lion Circuits about 565 rupees; Digi-Key India showed about 531 rupees in a search listing and 769.44 rupees for cut tape when the page was read directly (stock 3,652; lead time shown as 26 weeks). Digi-Reel orders add a 452 rupee reeling fee; the page did not say whether GST is included. ADS131M04EVM: 27,955 rupees at Digi-Key India (about 299.99 dollars in the US, 12-week lead time), so a custom board or a 40 rupee adapter is the practical route for the demo. No third-party ADS131M04 breakout board was found. MCP3912: Microchip marks it not recommended for new designs and points to the MCP3912B; Digi-Key Europe lists the B part at about 3.59 euros; no India price was found (the older MCP3912A1 was 405 to 534 rupees). SCT-013-000: Electropi page showed 423.62 rupees (an earlier search snippet showed 289 plus GST); Robodo 550; Electronicscomp 548.70; the Electropi page also advertises a built-in-resistor voltage output, so confirm you receive the current-output model (no burden fitted) if you follow the Rb design. Resistors: Hubtronics sells 22 ohm 1% in packs of 10; other values were not searched. 10 nF C0G: no Indian retail listing found; the Mouser India Knowles 1206 100 V part was 99.70 rupees. Voltage transformer: IndiaMART 1 VA PCB transformer at 190 rupees (output voltage not stated in the listing, confirm 9 V); element14 India 1 VA 230 V to 9 V at about 683 rupees excluding GST. A ZMPT107-1 was 70.80 rupees at DNA Tech India, but it is a current-type part and would change the circuit. PZEM-004T: Robocraze 569 rupees including a CT; many listings do not state the v3.0 revision, so confirm before buying.");

  s = add("CONTENT", "ADC and power");
  title(s, "Components and prices: power, protection and case");
  priceTable(s, [
    ["Power supply", "Hi-Link HLK-5M05, isolated 5 V, 5 W", "₹209 to ₹254", [["Hubtronics", "https://hubtronics.in/power-converter-modules/ac-dc-converter-modules/hlk-5m05"], ["Evelta", "https://evelta.com/hlk-5m05-5w-ultra-compact-ac-dc-power-module-acin-100-240v-dcout-5v"]]],
    ["Digital LDO", "Diodes AP2112K-3.3, 600 mA", "₹19 + ₹452 reel fee", [["Digi-Key India", "https://www.digikey.in/en/products/detail/diodes-incorporated/AP2112K-3-3TRG1/4470746"]]],
    ["Analog LDO", "TI LP5907MFX-3.3, 250 mA, low noise", "₹62 + ₹452 reel fee", [["Digi-Key India", "https://www.digikey.in/en/products/detail/texas-instruments/LP5907MFX-3-3-NOPB/5034443"]]],
    ["Fuse", "Littelfuse 0239001.HXP, 1 A slow-blow", "₹110 each (5 pieces)", [["Digi-Key India", "https://www.digikey.in/en/products/detail/littelfuse-inc/0239001-HXP/778214"]]],
    ["Fuse holder", "Panel-mount, 5 x 20 mm", "₹12 + GST", [["Hubtronics", "https://hubtronics.in/fuse-holder-panel-mount-red?tag=Fuse+Holder"]]],
    ["MOV", "Bourns MOV-14D471K, 300 V AC", "₹35", [["Digi-Key India", "https://www.digikey.in/en/products/detail/bourns-inc/MOV-14D471K/2799087"]]],
    ["Enclosure", "ABS, IP65, about 200 x 120 x 75 mm", "₹300", [["IndiaMART listings", "https://m.indiamart.com/impcat/abs-enclosure.html"]]],
    ["Other", "Terminal blocks, wire, microSD, supercapacitor", "Not priced yet", "Not searched yet"],
  ], 1.45, 0.46);
  card(s, 0.6, 5.7, 12.13, 0.75, C.text2, "banner estimate");
  text(s, "One demo unit costs roughly ₹3,600 to ₹4,900 before GST, shipping and Digi-Key fees.", { x: 0.9, y: 5.7, w: 11.5, h: 0.75, fontSize: 18, color: C.background1, valign: "middle", bold: true });
  text(s, "HLK-5M05 is rated 100–240 V AC, with an operating range of 85–265 V AC in Hi-Link's datasheet, so check it against Indian highs. The LDO and fuse parts are examples I chose, not final.", { x: 0.6, y: 6.55, w: 11.4, h: 0.4, fontSize: 11, color: C.accent5 });
  s.addNotes("Power supply: Hubtronics 209 rupees plus 18 percent GST, Evelta 253.70 including GST; one IndiaMART seller listed 200. Hi-Link's 5M-series datasheet gives a rated input of 100 to 240 V AC and an input range of 85 to 265 V AC, maximum input current 0.2 A and inrush up to 10 A; some distributors quote 90 to 264 V AC, so use the official datasheet. The AP2112K-3.3 and LP5907 are example parts I proposed (600 mA digital, 250 mA low-noise analog); their noise and current figures are from memory and must be checked against the datasheets. Digi-Key India charged a 452 rupee reeling fee on cut-tape orders in the listings seen, which dwarfs the part price, so combine items in one order or buy from an Indian retailer (Probots listed the AP2112K at 24 rupees but out of stock). Fuse: Littelfuse 0239001.HXP slow-blow 1 A at 109.96 rupees each for 5 pieces and 84.20 at 50; the right rating (about 0.5 to 1 A) and breaking capacity are still to be sized. Fuse holder: Hubtronics 11.80 rupees including GST. MOV: Bourns MOV-14D471K at 35.41 rupees on Digi-Key India (470 V, 300 V AC, 4.5 kA); Lion Circuits listed 128.04 for one and 26.32 at ten. Enclosure: IndiaMART listings of 200 x 120 x 75 mm ABS IP65 boxes at about 300 rupees; DIN-rail ABS boxes from 110. The estimate sums the lowest and highest listed prices on both slides including about 300 rupees of passives; it excludes GST, shipping, Digi-Key fees and any rework.");

  await pres.writeFile({ fileName: OUT });
  await applyTheme(OUT, THEME);
  console.log("wrote", OUT);
})().catch((e) => { console.error(e); process.exit(1); });

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
    ["Sensors", "CT clamp on live, ZMPT107-1 voltage sensor", C.accent1],
    ["Conditioning", "Burden, sampling resistor, RC filter", C.accent1],
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
    [fa.FaWaveSquare, C.accent1, "Analog stays simple", "Only small voltages reach the ADC. The CT and the ZMPT107-1 keep the electronics isolated from mains."],
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
  picture(s, "schematic-full", 0.6, 1.5, { h: 5.45 }, "Block-level schematic from the incoming live wire through the CT, ZMPT107-1 and HLK-5M05, then the two signal chains, the ADS131M04 and the ESP32-S3 DevKitC");
  const lx = 9.2;
  [["230 V mains", C.accent2], ["Analog signal", C.accent1], ["DC power", C.accent3], ["Digital", C.accent5]].forEach((l, i) => {
    s.addShape(SH.rect, { x: lx, y: 1.68 + i * 0.4, w: 0.42, h: 0.1, fill: { color: l[1] }, line: { type: "none" }, objectName: "legend " + l[0] });
    text(s, l[0], { x: lx + 0.6, y: 1.57 + i * 0.4, w: 2.9, h: 0.32, fontSize: 14, color: C.accent5, valign: "middle" });
  });
  text(s, bullets([
    "Only the CT, the ZMPT107-1 and the HLK-5M05 cross the isolation barrier.",
    "Both sensor signals are scaled and filtered, then read by one ADC at the same instant.",
    "The ESP32-S3 runs the DSP and finds events.",
  ]), { x: lx, y: 3.4, w: 3.53, h: 3.3, fontSize: 15 });
  s.addNotes("Full schematic. Red is mains, blue is analog signal, amber is DC power, grey is digital. The next slides zoom into each region.");

  // ===== 5. Mains side zoom =====
  section("Mains side");
  s = add("CONTENT", "Mains side");
  title(s, "What sits on the mains side, and why");
  picture(s, "schematic-mains", 0.6, 1.55, { w: 8.2 }, "The live wire passes through the CT clamp. A 1 A fused tap feeds a MOV, the ZMPT107-1 through three 39 kΩ resistors, and the HLK-5M05");
  const items5 = [
    ["Fuse", "1 A ceramic time-lag, 1.5 kA. The first fuse chosen was rated only 35 A at 250 V AC, so it was replaced."],
    ["MOV 10D561K", "Idles at 230 V and conducts when a voltage spike hits, clamping it. A fuse is too slow for microsecond spikes. Hi-Link recommends this part."],
    ["ZMPT107-1", "A current-type transformer. Three 39 kΩ resistors set about 2 mA through its primary, and 2 mA comes out of the secondary. 3000 V isolated."],
  ];
  items5.forEach((it, i) => {
    text(s, it[0], { x: 9.1, y: 1.55 + i * 1.7, w: 3.63, h: 0.35, fontSize: 18, bold: true, color: C.accent2 });
    text(s, it[1], { x: 9.1, y: 1.95 + i * 1.7, w: 3.63, h: 1.25, fontSize: 15 });
  });
  s.addNotes("Fuse: the Littelfuse 0239 glass fuse is only rated 35 A at 250 V AC (official table), so the plan is now a Bel 5HT 1-R ceramic time-lag fuse, listed at 1.5 kA (seller listing; Bel datasheet not yet read), same 5 x 20 mm size, slow-blow to ride through the 10 A inrush. MOV: voltage-dependent resistor, wears out with surges and tends to fail short-circuit, which is why the fuse sits in front. Hi-Link recommends the 10D561K; its datasheet is not yet read. ZMPT107-1 (manufacturer sheet read): 2 mA : 2 mA, phase error at most 0.75 degrees at 2 mA with a 50 ohm sampling resistor, linear from about 46 V to 276 V rms, 3000 V isolation. The series resistors are our calculation (230 V / 2 mA = 115 kohm; three 39 kohm in series).");

  // ===== 6. CT clamp =====
  section("Current and voltage sensing");
  s = add("CONTENT", "Current and voltage sensing");
  title(s, "Inside the CT clamp");
  picture(s, "ct-clamp", 0.6, 1.4, { w: 12.13 }, "Cross-section of a split-core CT: the live wire is one primary turn, flux circles in the iron core, a 2000-turn secondary drives a burden resistor, and the voltage goes to the ADC");
  text(s, "Example values: 10 A in the wire, a 2000:1 CT and a 13 Ω burden (2 × 6.49 Ω). Red is mains and blue is the analog signal.", { x: 0.6, y: 6.8, w: 11.4, h: 0.3, fontSize: 12, color: C.accent5 });
  s.addNotes("Five steps: 1) the wire's AC current makes a magnetic field; 2) the iron core gathers it as flux; 3) the changing flux drives a current in the 2000-turn secondary, so the secondary current is the wire current divided by 2000; 4) the burden (two 6.49 ohm resistors, midpoint at analog ground) turns that current into a voltage; 5) the two ends go through a 1 kohm and 10 nF filter to ADC CH1+ and CH1-.");

  // ===== 7. Rb =====
  s = add("CONTENT", "Current and voltage sensing");
  title(s, "The ADC reads voltage, never current");
  const chain = [
    ["Wire current", "10 A rms", "peak 14.1 A", C.accent2],
    ["CT secondary", "5 mA rms", "÷ 2000", C.accent1],
    ["Across the burden", "65 mV rms", "× 12.98 Ω", C.accent1],
    ["ADC code", "≈ 642 k", "counts at the peak", C.text2],
    ["Firmware", "10 A rms", "× 2000 ÷ 13 Ω", C.text2],
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
    "Our 13 Ω (2 × 6.49 Ω) clips above about 131 A rms. The first draft's 22 Ω clipped above 77 A.",
  ]), { x: 0.9 + hw + 0.2, y: 4.15, w: hw - 0.6, h: 2.5, fontSize: 15 });
  s.addNotes("The ADC only ever measures voltage. CH1 is called the current channel because its voltage is proportional to the wire current. The conversion back happens in firmware: I_wire = (V_adc / Rb) x 2000, with calibration; Rb is 12.98 ohm (two 6.49 ohm resistors, midpoint at analog ground). The first draft used 22 ohm, which would clip the +/-1.2 V ADC above 77 A rms. Every current sensor ends in a voltage: a shunt, a Hall sensor with built-in electronics, or a CT with a burden.");

  // ===== 8. Chains zoom =====
  s = add("CONTENT", "Current and voltage sensing");
  title(s, "Scaling both signals down for the ADC");
  picture(s, "schematic-chains", 0.6, 1.55, { w: 8.2 }, "The voltage path from the ZMPT107-1 through a 50 ohm sampling resistor and RC filter to CH2, and the current path from the CT through the 13 ohm burden and RC filter to CH1");
  const items8 = [
    ["Voltage path", C.accent1, "230 V, 117 kΩ gives 2 mA, a 50 Ω sampling resistor gives 0.14 V peak at CH2 (gain 2)."],
    ["Current path", C.accent1, "10 A, CT to 5 mA, a 13 Ω burden, then 0.09 V peak at CH1 (gain 1)."],
    ["Both paths", C.text2, "1 kΩ in each leg and 10 nF across. Each split resistor's midpoint is analog ground (AGND)."],
  ];
  items8.forEach((it, i) => {
    text(s, it[0], { x: 9.1, y: 1.55 + i * 1.7, w: 3.63, h: 0.35, fontSize: 18, bold: true, color: it[1] });
    text(s, it[2], { x: 9.1, y: 1.95 + i * 1.7, w: 3.63, h: 1.25, fontSize: 15 });
  });
  s.addNotes("Voltage path: at 230 V the ZMPT107-1 primary carries about 2 mA (230 V / 117 kohm), the secondary 2 mA, and 50 ohm turns that into 0.139 V peak; at gain 2 the ADC window is +/-0.6 V, so there is plenty of headroom. The real limit is the ZMPT107-1 linearity, about 46 V to 276 V rms. Analog ground is the low-voltage reference node: the burden and sampling resistors are each split in two and the midpoint is tied to it, which pins the isolated secondaries so they cannot drift out of the ADC input range.");

  // ===== 9. Filter waveform =====
  section("Filtering");
  s = add("CONTENT", "Filtering");
  title(s, "What the 1 kΩ + 10 nF filter does to the signal");
  picture(s, "filter-wave", 0.6, 1.55, { w: 7.8 }, "A 50 Hz wave with fast ripple before the filter and the same wave clean after it");
  text(s, "What it does", { x: 8.8, y: 1.55, w: 3.93, h: 0.4, fontSize: 20, bold: true, color: C.text2 });
  text(s, bullets([
    "The 50 Hz wave and its harmonics pass almost untouched, 99.999% at 50 Hz.",
    "The capacitor shorts fast ripple to ground before the ADC samples it.",
    "This ADC samples internally at 4.096 MHz, so the filter's real job is noise near that rate. The ADC's digital filter handles everything between 4 kHz and the MHz range.",
  ]), { x: 8.8, y: 2.1, w: 3.93, h: 4.6, fontSize: 15 });
  s.addNotes("The left plot draws the ripple slowed down; the real ripple is thousands of times faster. Capacitor impedance Xc = 1 / (2 pi f C): huge at 50 Hz, tiny at MHz. Cutoff fc = 1 / (2 pi R C); the filter has 1 kohm in each leg and 10 nF across, so R is 2 kohm and fc is about 8 kHz. Correction to the first draft: this ADC is delta-sigma, so the analog filter is not an anti-alias filter at the 4 kHz output Nyquist point. The ADC oversamples at 4.096 MHz and filters digitally.");

  // ===== 10. Filter response =====
  s = add("CONTENT", "Filtering");
  title(s, "A gradual filter, not a brick wall");
  picture(s, "filter-response", 0.6, 1.55, { w: 8.0 }, "Filter gain against frequency on a log scale: flat through the mains band, down 3 dB at about 8 kHz, down 54 dB at the ADC modulator rate of 4.096 MHz");
  text(s, "Can remove", { x: 8.9, y: 1.55, w: 3.83, h: 0.35, fontSize: 18, bold: true, color: C.accent1 });
  text(s, "Switching supplies, sparks from motors and relays, and clock edges. Tens of kHz and up.", { x: 8.9, y: 1.95, w: 3.83, h: 1.2, fontSize: 15 });
  text(s, "Cannot remove", { x: 8.9, y: 3.3, w: 3.83, h: 0.35, fontSize: 18, bold: true, color: C.accent2 });
  text(s, "Wi-Fi burst ripple on the supply and 50 Hz hum. They sit too low. Fix with the separate LP5907 supply, careful layout and averaging in the DSP.", { x: 8.9, y: 3.7, w: 3.83, h: 1.8, fontSize: 15 });
  text(s, "1 kΩ in each leg + 10 nF across, fc ≈ 8 kHz.", { x: 8.9, y: 5.8, w: 3.83, h: 0.4, fontSize: 12, color: C.accent5 });
  s.addNotes("The filter attenuates 20 dB for every tenfold increase in frequency. The ADC's own digital filter removes what remains between its 4 kHz output limit and the MHz range, so the RC filter does not set the 4 kHz limit; its job is the modulator rate and its multiples. The noise frequency ranges are typical, not measured on our hardware; check on the first board with an oscilloscope. Phase lag at 50 Hz is 0.36 degrees on the current channel and 0.37 degrees on the voltage channel, so the two cancel to about 0.007 degrees. The first draft used a divider that made a 0.165 degree mismatch.");

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
    ["Simple analog front end", "Bipolar differential inputs take the burden voltage directly, with no mid-rail bias network (checked in the datasheet)."],
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
  text(s, "Second source: MCP3912B (the older MCP3912 is not recommended for new designs). Specs checked against TI datasheet SBAS890D.", { x: 0.6, y: 6.78, w: 10, h: 0.25, fontSize: 11, color: C.accent5 });
  s.addNotes("Why the ADS131M04 for the demo: simultaneous sampling, raw data access, bipolar differential inputs that let the burden output go straight in, built-in PGA and reference, an output rate that covers the NILM features, and simple firmware (one SPI driver and a DRDY interrupt). Two of the four channels are used (voltage and current); the other two are spare for a second CT or three-phase later, so no board respin. Second source: MCP3912 if TI parts are hard to get in India. Specs were checked against the datasheet (SBAS890D): input range plus/minus 1.2 V divided by gain, input impedance 330 kohm at gains 1 to 4, SPI frame of 6 words, phase register in 244 ns steps. Confirm stock and price before ordering. For the demo board: an evaluation module plus an ESP32-S3 dev board for early firmware bring-up while a custom PCB (assembled by a service for the fine-pitch ADC) is designed in parallel.");

  // ===== 11. Power + ADC zoom =====
  s = add("CONTENT", "ADC and power");
  title(s, "Power, ADC and ESP32-S3 on the safe side");
  const pa = picture(s, "schematic-power-adc", 0.6, 1.45, { h: 5.5 }, "The HLK-5M05, the LP5907, the ADS131M04 and the ESP32-S3 DevKitC with the SPI and control wires between them");
  const rx = 0.6 + pa.w + 0.5, rw = 12.73 - rx;
  const items11 = [
    [fa.FaPlug, C.accent3, "HLK-5M05", "Isolated 5 V, 1 A. Full load from about 110 to 260 V AC and up to 60 °C (derating graphs read). Isolation rating (3000 V or 2500 V) unresolved."],
    [fa.FaBolt, C.accent3, "LP5907 and DevKitC", "The LP5907 gives the ADC a quiet 3.3 V. The DevKitC takes 5 V and makes its own 3.3 V, which carries the Wi-Fi current pulses."],
    [fa.FaMicrochip, C.text2, "SPI link", "SCLK, MOSI, MISO and CS, plus DRDY (an interrupt, about 8,000 a second), CLKIN at 8.192 MHz from the ESP32 and SYNC/RESET. The ESP32-S3 is the SPI master."],
  ];
  for (let i = 0; i < items11.length; i++) {
    const y = 1.45 + i * 1.88, it = items11[i];
    card(s, rx, y, rw, 1.72, C.background2, "card " + it[2]);
    await iconBadge(s, it[0], rx + 0.25, y + 0.3, 0.6, it[1], it[2]);
    text(s, it[2], { x: rx + 1.1, y: y + 0.15, w: rw - 1.35, h: 0.35, fontSize: 18, bold: true, color: C.text2 });
    text(s, it[3], { x: rx + 1.1, y: y + 0.55, w: rw - 1.35, h: 1.1, fontSize: 14 });
  }
  s.addNotes("The AC-DC module is a small flyback switching supply: rectifier, switch, high-frequency transformer, output rectifier and an optocoupler feedback loop. It is the main noise source on the 5 V rail, which is why the ADC has its own low-noise LP5907 (about 60 dB of ripple rejection at 100 kHz). On a custom board the ESP32 would get an AP63203 buck converter instead of the DevKitC regulator. Never connect USB and the HLK 5 V at the same time until the DevKitC user guide confirms it is safe. An LDO (low-dropout regulator) burns the voltage difference as heat: power lost = (Vin - Vout) x current. Choose parts for peak current, dropout, noise and PSRR.");

  // ===== Datasheet review =====
  section("Datasheet review");
  s = add("CONTENT", "Datasheet review");
  title(s, "What the datasheet review changed");
  const chg = [
    ["CT burden", "One 22 Ω resistor", "2 × 6.49 Ω (≈ 13 Ω), midpoint to AGND", "22 Ω clips above 77 A rms; 13 Ω above 131 A"],
    ["Voltage sensor", "230 V : 9 V transformer + divider", "ZMPT107-1, 3 × 39 kΩ, 50 Ω sampling resistor", "Stated 0.75° phase error, 3000 V isolation"],
    ["Input filter", "Rf and Cf on one leg", "1 kΩ per leg + 10 nF across, both channels", "ADC datasheet advice; the two lags cancel"],
    ["Filter's job", "Anti-alias at 4 kHz", "Stop noise near 4.096 MHz", "Delta-sigma ADC filters digitally below that"],
    ["ADC pins", "No decoupling", "1 µF AVDD and DVDD, 220 nF CAP", "Datasheet requirement"],
    ["MOV", "14D471K", "10D561K", "Hi-Link's recommended part"],
    ["Power", "Two LDOs from 5 V", "LP5907 for the ADC; DevKitC regulator", "AP2112K would overheat from 5 V"],
    ["MCU", "Generic ESP32-S3", "DevKitC N16R8 (to buy); avoid IO35–37", "Octal PSRAM uses those pins"],
  ];
  s.addTable(
    [[th("Item"), th("First draft"), th("Final design", C.accent1), th("Why")]].concat(
      chg.map((r) => r.map((t, ci) => td(t, Object.assign({ bold: ci === 0 || ci === 2 }, ci === 2 ? hi : {}))))
    ),
    { x: 0.6, y: 1.5, w: 12.13, colW: [1.9, 2.9, 4.13, 3.2], rowH: 0.55, fontSize: 13, border: tableBorder, margin: [0.04, 0.1, 0.04, 0.1] }
  );
  s.addNotes("Every row is a change from the first draft after reading the datasheets: ADS131M04 (TI SBAS890D), SCT-013-000, ZMPT107-1 (manufacturer sheet), HLK-5M05, LP5907, AP2112 and the ESP32-S3-WROOM-1 datasheet. The CT field figures come from OpenEnergyMonitor measurements of one unit. Full details are in documentation/findings/datasheet-verification-checklist.md.");

  s = add("CONTENT", "Datasheet review");
  title(s, "Phase error: why 4° matters and how we remove it");
  const pw = 5.9;
  card(s, 0.6, 1.5, pw, 5.2, C.background2, "card phase table");
  text(s, "Error caused by a false 4°", { x: 0.9, y: 1.7, w: pw - 0.6, h: 0.4, fontSize: 20, bold: true, color: C.text2 });
  s.addTable(
    [[th("True PF"), th("Error in real power")]].concat(
      [["1.0", "−0.2%, but a fake Q of 7% of VA"], ["0.9", "−3.6%"], ["0.7", "−7.4%"], ["0.5", "−12.3%"]].map((r) => r.map((t) => td(t)))
    ),
    { x: 0.9, y: 2.3, w: pw - 0.6, colW: [1.4, pw - 2.0], rowH: 0.5, fontSize: 15, border: tableBorder, margin: [0.04, 0.1, 0.04, 0.1] }
  );
  text(s, "A pure heater should show zero reactive power. With a false 4° it looks like a small motor, which blurs the P and Q fingerprints that classification relies on.", { x: 0.9, y: 5.0, w: pw - 0.6, h: 1.5, fontSize: 15 });
  card(s, 0.6 + pw + 0.2, 1.5, 12.13 - pw - 0.2, 5.2, C.background2, "card phase fix");
  text(s, "How we remove it", { x: 0.6 + pw + 0.5, y: 1.7, w: 12.13 - pw - 0.8, h: 0.4, fontSize: 20, bold: true, color: C.text2 });
  text(s, bullets([
    "Put a pure resistive load on (a lamp or heater). Its true reactive power is zero.",
    "Shift the current samples until the measured Q reads zero.",
    "The CT's expected 4° is 222 µs, or 1.8 samples at 8 kSPS: a 2-sample shift plus the ADC's phase register (244 ns steps, about ±62 µs).",
    "The ZMPT107-1's 0.75° fits in the register alone.",
    "Check on a fan or motor. The 4° is one unit measured by OpenEnergyMonitor, so ours will differ.",
  ]), { x: 0.6 + pw + 0.5, y: 2.25, w: 12.13 - pw - 0.8, h: 4.3, fontSize: 15 });
  s.addNotes("Real power is the average of v times i, so a false angle d changes P by about d times tan(phi). At 4 degrees: PF 1 gives 0.2 percent error in P but a fake reactive power of sin(4 degrees) = 7 percent of apparent power; PF 0.9, 0.7 and 0.5 give 3.6, 7.4 and 12.3 percent. The CT's phase lead is typical of CTs but its sign for our unit is not measured. At 8 kSPS one sample is 125 microseconds; the ADS131M04 phase register covers about plus or minus 62 microseconds at OSR 512.");

  s = add("CONTENT", "Datasheet review");
  title(s, "Still open before building");
  const ow = 5.965;
  card(s, 0.6, 1.5, ow, 3.4, C.background2, "card bench tests");
  text(s, "Needs a bench test", { x: 0.9, y: 1.7, w: ow - 0.6, h: 0.4, fontSize: 20, bold: true, color: C.accent1 });
  text(s, bullets([
    "The real phase and ratio error of our CT and ZMPT107-1.",
    "CT accuracy from about 0.1 A upward. A second CT is added only if it fails below 0.3 A.",
    "Jitter on the ESP32-made 8.192 MHz ADC clock.",
  ]), { x: 0.9, y: 2.25, w: ow - 0.6, h: 2.5, fontSize: 15 });
  card(s, 0.6 + ow + 0.2, 1.5, ow, 3.4, C.background2, "card unanswered");
  text(s, "Needs a datasheet or an answer", { x: 0.9 + ow + 0.2, y: 1.7, w: ow - 0.6, h: 0.4, fontSize: 20, bold: true, color: C.accent2 });
  text(s, bullets([
    "HLK-5M05 isolation rating (3000 V or 2500 V); its text says a 1 A fuse, its drawing 0.5 A.",
    "Bel 5HT datasheet (confirm 1.5 kA); a 3.3 V supply clamp part; CT secondary clamp.",
    "ZMPT107-1 surge withstand.",
    "DevKitC regulator current rating; never use USB and the 5V pin together.",
  ]), { x: 0.9 + ow + 0.2, y: 2.25, w: ow - 0.6, h: 2.5, fontSize: 15 });
  card(s, 0.6, 5.15, 12.13, 0.75, C.text2, "banner paper design");
  text(s, "This is a paper design. Nothing has been built or bench-tested yet.", { x: 0.9, y: 5.15, w: 11.5, h: 0.75, fontSize: 18, color: C.background1, valign: "middle", bold: true });
  s.addNotes("Open items from documentation/findings/datasheet-verification-checklist.md. The mains side is live 230 V: use an enclosure, proper clearance and creepage, and do not connect a laptop to the board while it is on mains until the HLK isolation rating is resolved.");

  // ===== Components and prices =====
  section("Components");
  const L = {
    devkit: ["IndiaMART", "https://m.indiamart.com/proddetail/esp32-s3-devkitc-1-n16r8-type-c-esp32-s3-development-board-wi-fi-ble-mcu-module-2856307778633.html"],
    lionAdc: ["Lion Circuits", "https://www.lioncircuits.com/parts/ADS131M04IPWR"],
    dkAdc: ["Digi-Key India", "https://www.digikey.in/en/products/detail/texas-instruments/ADS131M04IPWR/10448283"],
    probots: ["Probots", "https://probots.co.in/sop20-ssop20-to-dip20-double-sided-adapter-board.html"],
    electropi: ["Electropi", "https://www.electropi.in/sct-013-000-100a-non-invasive-ac-current-sensor-split-core-type-clamp-meter-sensor"],
    robodo: ["Robodo", "https://robodo.in/products/100a-sct-013-000-non-invasive-ac-current-sensor-split-core-current-transformer"],
    sharvi: ["Sharvi Electronics", "https://sharvielectronics.com/product/zmpt107-1-current-type-voltage-transformer/"],
    pzem: ["Robocraze", "https://robocraze.com/products/peacefair-pzem-004t-multi-function-ac-power-meter-for-energy-measurement"],
    hubHlk: ["Hubtronics", "https://hubtronics.in/power-converter-modules/ac-dc-converter-modules/hlk-5m05"],
    evHlk: ["Evelta", "https://evelta.com/hlk-5m05-5w-ultra-compact-ac-dc-power-module-acin-100-240v-dcout-5v"],
    lp5907: ["Digi-Key India", "https://www.digikey.in/en/products/detail/texas-instruments/LP5907MFX-3-3-NOPB/5034443"],
    fuse: ["Lion Circuits", "https://www.lioncircuits.com/parts/5HT%201-R"],
    bat54: ["BAT54", "https://www.lioncircuits.com/parts/BAT54-7-F"],
    bav199: ["BAV199", "https://www.lioncircuits.com/parts/BAV199-7-F"],
    holder: ["Hubtronics", "https://hubtronics.in/fuse-holder-panel-mount-red?tag=Fuse+Holder"],
    lionMov: ["Lion Circuits", "https://lioncircuits.com/parts/MOV-10D561KTR"],
    dkMov: ["Digi-Key India", "https://www.digikey.in/en/products/detail/bourns-inc/MOV-10D561K/2407569"],
    encl: ["IndiaMART", "https://m.indiamart.com/impcat/abs-enclosure.html"],
    buck: ["Digi-Key India", "https://www.digikey.in/en/products/detail/diodes-incorporated/AP63203WU-7/9858430"],
    r649: ["Lion Circuits", "https://www.lioncircuits.com/parts/CRCW12066R49FKEA"],
    c220n: ["Lion Circuits", "https://www.lioncircuits.com/parts/0805B224K500CT"],
    c220u: ["Evelta", "https://evelta.com/220uf-25v-electrolytic-capacitor"],
    term: ["Zbotic", "https://zbotic.in/?p=438931"],
    perf: ["Robu", "https://st.robu.in/product/7-x-9-cm-universal-pcb-prototype-board-single-sided-2-54mm-hole-pitch"],
    r249: ["Digi-Key India", "https://www.digikey.in/en/products/detail/yageo/RC0805FR-0724R9L/727759"],
    r39k: ["Lion Circuits", "https://www.lioncircuits.com/parts/MF50%2039K"],
    r1k: ["Evelta", "https://evelta.com/1k-1-0-125w-0805-chip-resistor/"],
    c1u: ["Evelta", "https://evelta.com/1uf-50v-10-x7r-0805-mlcc-multilayer-ceramic-capacitors-cc0805kkx7r9bb105"],
    c10n: ["Lion Circuits", "https://www.lioncircuits.com/parts/0805N103J500CT"],
  };
  const link = (label, url) => ({ text: label, options: { hyperlink: { url, tooltip: url }, color: C.accent1, underline: { style: "sng" }, valign: "middle" } });
  const links = (items) => ({
    text: items.reduce((acc, it, i) => acc.concat(i ? [{ text: ", ", options: { color: C.text1 } }] : [], [link(it[0], it[1])]), []),
    options: { valign: "middle" },
  });
  const priceTable = (slide, rows, y, rowH) => slide.addTable(
    [[th("Block"), th("Part and quantity"), th("Price in ₹"), th("Where to buy")]].concat(
      rows.map((r) => [td(r[0], { bold: true }), td(r[1]), td(r[2]), typeof r[3] === "string" ? td(r[3]) : links(r[3])])
    ),
    { x: 0.6, y, w: 12.13, colW: [2.1, 4.0, 2.7, 3.33], rowH, fontSize: 13, border: tableBorder, margin: [0.03, 0.1, 0.03, 0.1] }
  );

  s = add("CONTENT", "Components");
  title(s, "Components and prices: sensing and processing");
  priceTable(s, [
    ["Microcontroller", "ESP32-S3-DevKitC-1 N16R8, 1 (not owned)", "₹1,100 ex-GST", [L.devkit]],
    ["ADC chip", "TI ADS131M04IPWR, 1", "₹565 to ₹769", [L.lionAdc, L.dkAdc]],
    ["ADC adapter", "TSSOP-20 to DIP adapter, 1", "₹40 + GST", [L.probots]],
    ["Current sensor", "SCT-013-000, 2 units", "₹424 to ₹550 each", [L.electropi, L.robodo]],
    ["Voltage sensor", "ZMPT107-1, 1", "₹83.69 ex-GST", [L.sharvi]],
    ["Lab reference", "PZEM-004T with CT, 1 (optional)", "₹569", [L.pzem]],
  ], 1.5, 0.55);
  text(s, "Seen on 23 Nov 2026. The DevKitC is not owned yet: the purchase waits on a reimbursement. The ADS131M04 showed ₹531 in a Digi-Key search and ₹769 on its page, so check the live page. Prices change and GST treatment differs by seller.", { x: 0.6, y: 5.6, w: 11.8, h: 0.6, fontSize: 12, color: C.accent5 });
  s.addNotes("Sources and caveats, seen on 23 Nov 2026 and listed in documentation/findings/bill-of-materials.md. ESP32-S3-DevKitC-1 N16R8: not owned, to be bought after a reimbursement; IndiaMART seller Luster Electronics at 1,100 rupees excluding tax (seller rating 3.2 from 9 reviews); Mouser India listed the official board at 1,264.95 rupees on order. ADS131M04IPWR: Lion Circuits about 565 rupees; Digi-Key India 769 rupees for cut tape on its page, with a 452 rupee fee on Digi-Reel orders. ADS131M04EVM is 27,955 rupees, so the adapter is the practical route. SCT-013-000: Electropi 423.62, Robodo 550; confirm the current-output model. ZMPT107-1: Sharvi Electronics 83.69 rupees excluding taxes (103.69 including), page names ZMPT107-1 and 2 mA to 2 mA with 3000 V isolation; DNA Tech lists a ZMPT107 at 70.80 rupees including GST, out of stock, and never says -1. PZEM-004T: Robocraze 569 rupees including a CT; confirm v3.0.");

  s = add("CONTENT", "Components");
  title(s, "Components and prices: power, protection and case");
  priceTable(s, [
    ["Power supply", "Hi-Link HLK-5M05, 1", "₹209 + GST, or ₹253.70 with GST", [L.hubHlk, L.evHlk]],
    ["Analog supply", "TI LP5907MFX-3.3, 1", "₹62 + ₹452 reel fee", [L.lp5907]],
    ["Fuse", "Bel 5HT 1-R, 1 A ceramic, 1.5 kA, 1", "₹80.30", [L.fuse]],
    ["Input protection", "BAT54-7-F x4 and BAV199-7-F x4", "₹10.55 and ₹20.72 each", [L.bat54, L.bav199]],
    ["Fuse holder", "Panel mount, 5 x 20 mm, 1", "₹12 + GST", [L.holder]],
    ["MOV", "Bourns 10D561K, 1", "₹38.23 (₹23.45 each at 10)", [L.lionMov, L.dkMov]],
    ["Enclosure", "ABS, IP65, about 200 x 120 x 75 mm, 1", "about ₹300", [L.encl]],
    ["Buck (custom board only)", "Diodes AP63203WU-7, 1", "₹88.45 + ₹452 reel fee", [L.buck]],
  ], 1.5, 0.52);
  text(s, "The Digi-Key India pages for the MOV and the buck showed zero stock and 16 and 32 week lead times, so the Indian seller is the practical route. The buck is not needed for the DevKitC demo.", { x: 0.6, y: 6.35, w: 11.4, h: 0.6, fontSize: 12, color: C.accent5 });
  s.addNotes("Power supply: Hubtronics 209 rupees plus 18 percent GST (an earlier check, the site now blocks automated reading), Evelta 253.70 including GST. LP5907: Digi-Key India 62 rupees; Digi-Reel orders add a 452 rupee fee. Fuse: Bel 5HT 1-R at Lion Circuits, 80.30 rupees (73.80 at 10 pieces), in stock; the earlier Littelfuse 0239001.HXP glass fuse was rejected. Input protection: BAT54-7-F 10.55 rupees and BAV199-7-F 20.72 rupees at 1 piece, both read on Lion Circuits. Fuse holder: Hubtronics 11.80 rupees including GST (earlier check). MOV: Lion Circuits tape and reel Bourns MOV-10D561KTR shows 38.23 rupees, with 23.45 each at 10 pieces, in stock and shipping in 7 to 10 days; Digi-Key India lists the MOV-10D561K at 25.68 rupees with zero stock and a 16 week lead time; Evelta's HEL-10D561K at 5.25 rupees ex-GST is sold out. Enclosure: IndiaMART listings of 200 x 120 x 75 mm ABS IP65 boxes at about 300 rupees. AP63203WU-7: Digi-Key India 88.45 rupees, zero stock, 32 week lead time, Digi-Reel fee 452 rupees.");

  s = add("CONTENT", "Components");
  title(s, "Components and prices: resistors and capacitors");
  priceTable(s, [
    ["CT burden resistors", "6.49 Ω, 1%, 1206, 2", "₹15.81 each", [L.r649]],
    ["ZMPT sampling resistors", "24.9 Ω, 1%, 0805, 2", "₹9.51 each", [L.r249]],
    ["Mains-side series", "39 kΩ, ½ W, 1%, 3", "₹7.51 each, sold from 25", [L.r39k]],
    ["Filter resistors", "1 kΩ, 1%, 0805, 4", "₹2.00 each ex-GST", [L.r1k]],
    ["Decoupling", "1 µF, 50 V, X7R, 0805, 4", "₹12.00 each ex-GST", [L.c1u]],
    ["Filter capacitors", "10 nF, C0G, 0805, 2", "₹13.45 each", [L.c10n]],
    ["ADC CAP-pin capacitor", "220 nF, 50 V, X7R, 0805, 1", "₹13.45 each", [L.c220n]],
    ["HLK output capacitor", "220 µF, 25 V electrolytic, 1", "₹2.70 ex-GST", [L.c220u]],
    ["Terminal blocks", "2-pin 5.08 mm, pack of 5", "₹31.74 incl. GST", [L.term]],
    ["Perfboard", "7 x 9 cm, single-sided, 1", "₹37 incl. GST", [L.perf]],
  ], 1.4, 0.4);
  card(s, 0.6, 6.15, 12.13, 0.6, C.text2, "banner estimate");
  text(s, "Bench demo parts: about ₹3,700 to ₹4,400 before GST, shipping and fees.", { x: 0.9, y: 6.15, w: 11.5, h: 0.6, fontSize: 16, color: C.background1, valign: "middle", bold: true });
  text(s, "The Zbotic and Robu prices come from search results. Lion Circuits prices are the 1-piece price. Hook-up wire and a mains cable are not priced. Minimum packs apply: 25 resistors, reels of 1 kΩ and 1 µF parts.", { x: 0.6, y: 6.88, w: 11.4, h: 0.42, fontSize: 11, color: C.accent5 });
  s.addNotes("Full list with every price and link: documentation/findings/bill-of-materials.md. 6.49 ohm: Vishay CRCW12066R49FKEA, 1206, 1 percent, 15.81 rupees at Lion Circuits (page read, in stock; 10.25 at 10 pieces); Digi-Key India listed 10.65 in a search result. 24.9 ohm: Digi-Key India 9.51 rupees, 24 week lead time, marketplace stock. 39 kohm: Lion Circuits Multicomp MF50 39K, 7.51 rupees each from 25 pieces. 1 kohm: Evelta Yageo RC0805FR-071KL, 2.00 rupees ex-GST, 2,219 in stock, full reel 5,000. 1 microfarad: Evelta Yageo CC0805KKX7R9BB105, 12.00 rupees ex-GST, 2,566 in stock, full reel 3,000. 10 nanofarad C0G: Lion Circuits Walsin 0805N103J500CT, 5 percent, 50 V, 13.45 rupees (page read, in stock); the KEMET part at Digi-Key was 136.98. 220 nanofarad: Lion Circuits Walsin 0805B224K500CT, X7R, 13.45 rupees. 220 microfarad 25 V: Evelta Samwha 2.70 rupees ex-GST, 18 in stock. Terminal blocks (Zbotic) and perfboard (Robu) are search-result prices. The total sums the priced rows only.");

  await pres.writeFile({ fileName: OUT });
  await applyTheme(OUT, THEME);
  console.log("wrote", OUT);
})().catch((e) => { console.error(e); process.exit(1); });

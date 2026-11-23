# Bill of Materials (demo build)

Prices in INR as seen on 23 Nov 2026 on the seller pages linked below. They change, and some pages do not say whether GST is included, so each row says. Nothing is bought yet.

**Status of the ESP32-S3 DevKitC:** we do **not** own it. The purchase is pending a reimbursement, so it is listed as a part to buy.

How the list was checked: Evelta, Sharvi Electronics, DNA Tech, Lion Circuits, IndiaMART and Digi-Key India pages were read directly. Robu and Hubtronics blocked automated reading (HTTP 403), so their older prices are from earlier searches and are marked. Rows marked "search result only" were not opened on the seller page, so treat those prices as unconfirmed. Lion Circuits prices were read from the part pages; the page headline price is taken as the 1-piece price.

## A. Parts to buy for the bench demo

| # | Part | Qty | Unit price (INR) | Buy link | Notes |
|---|---|---|---|---|---|
| 1 | ESP32-S3-DevKitC-1 N16R8 | 1 | ₹1,100, ex-GST | [IndiaMART, Luster Electronics](https://m.indiamart.com/proddetail/esp32-s3-devkitc-1-n16r8-type-c-esp32-s3-development-board-wi-fi-ble-mcu-module-2856307778633.html) | Not owned; purchase pending reimbursement. Seller rating 3.2 (9 reviews). Mouser India listed the official board at ₹1,264.95 earlier, on order; no product link verified. |
| 2 | TI ADS131M04IPWR (TSSOP-20) | 1 | ₹565 to ₹769 | [Lion Circuits](https://www.lioncircuits.com/parts/ADS131M04IPWR), [Digi-Key India](https://www.digikey.in/en/products/detail/texas-instruments/ADS131M04IPWR/10448283) | Digi-Key showed ₹531 in search and ₹769 on the page. Reel orders add a ₹452 fee. |
| 3 | TSSOP-20 to DIP adapter, 0.65 mm | 1 | ₹40 + GST | [Probots](https://probots.co.in/sop20-ssop20-to-dip20-double-sided-adapter-board.html) | |
| 4 | SCT-013-000 CT, 100 A : 50 mA | 2 | ₹424 to ₹550 | [Electropi](https://www.electropi.in/sct-013-000-100a-non-invasive-ac-current-sensor-split-core-type-clamp-meter-sensor), [Robodo](https://robodo.in/products/100a-sct-013-000-non-invasive-ac-current-sensor-split-core-current-transformer) | Order the current-output model. Buy two to compare units. |
| 5 | ZMPT107-1, 2 mA : 2 mA | 1 | ₹83.69, ex-GST (page also shows ₹103.69 incl. taxes) | [Sharvi Electronics](https://sharvielectronics.com/product/zmpt107-1-current-type-voltage-transformer/) | Page names ZMPT107-1 with 2 mA : 2 mA and 3000 V. DNA Tech's [ZMPT107](https://www.dnatechindia.com/zmpt-0107-ac-mains-voltage-sensor-micro-transformer.html) is ₹70.80 incl. GST but out of stock and never says "-1". |
| 6 | Hi-Link HLK-5M05 | 1 | ₹209 + GST, or ₹253.70 incl. GST | [Hubtronics](https://hubtronics.in/power-converter-modules/ac-dc-converter-modules/hlk-5m05), [Evelta](https://evelta.com/hlk-5m05-5w-ultra-compact-ac-dc-power-module-acin-100-240v-dcout-5v) | Hubtronics price is from an earlier check (site now blocks automated reading). |
| 7 | TI LP5907MFX-3.3 | 1 | ₹62 | [Digi-Key India](https://www.digikey.in/en/products/detail/texas-instruments/LP5907MFX-3-3-NOPB/5034443) | Digi-Reel orders add ₹452. Combine with other Digi-Key items or ask an Indian seller. |
| 8 | Bel Fuse 5HT 1-R, 1 A, 250 V AC, time-lag, ceramic 5 × 20 mm (listed breaking capacity 1.5 kA) | 1 | ₹80.30 at 1 piece (₹73.80 at 10) | [Lion Circuits](https://www.lioncircuits.com/parts/5HT%201-R) | **Replaces the Littelfuse 0239001 glass fuse, which is only rated 35 A at 250 V AC.** In stock, ships in 7 to 10 days. The 1.5 kA figure is from the seller's listing and a search summary of Bel's datasheet, which I have not opened: check [Bel's datasheet](https://www.alldatasheet.com/html-pdf/2166821/BEL/5HT%20250-R/64/1/5HT%20250-R.html) before ordering. Alternative: Littelfuse [0215001.MXP](https://www.lioncircuits.com/parts/0215001.MXP), 1 A ceramic, listed 1.5 kA, ₹248.52 at 1 piece. |
| 9 | Fuse holder, panel mount, 5 × 20 mm | 1 | ₹12 + GST | [Hubtronics](https://hubtronics.in/fuse-holder-panel-mount-red?tag=Fuse+Holder) | Earlier-check price. The ceramic fuse is the same 5 × 20 mm size. Check the holder's own voltage and current rating before using it on mains. |
| 10 | MOV 10D561K (Bourns, 560 V) | 1 | ₹38.23 shown (₹23.45 each at 10) | [Lion Circuits](https://lioncircuits.com/parts/MOV-10D561KTR) | Tape and reel, "In stock, ships in 7 to 10 days". [Digi-Key India](https://www.digikey.in/en/products/detail/bourns-inc/MOV-10D561K/2407569): ₹25.68, 0 in stock, 16-week lead time. [Evelta HEL-10D561K](https://evelta.com/560v-180pf-mov-varistor-through-hole): ₹5.25 ex-GST, sold out. |
| 11 | 39 kΩ, ½ W, 1% metal film resistor | 3 | ₹7.51 each, sold from 25 pieces (₹187.72 per 25) | [Lion Circuits MF50 39K](https://www.lioncircuits.com/parts/MF50%2039K) | No 1-piece price on the page. Carries the full mains voltage, so keep the ½ W through-hole part. |
| 12 | 24.9 Ω, 1%, 0805 resistor (the 25 Ω halves) | 2 | ₹9.51 each | [Digi-Key India](https://www.digikey.in/en/products/detail/yageo/RC0805FR-0724R9L/727759) | 24-week lead time at Digi-Key; marketplace stock shown. 24.9 Ω is the standard value nearest 25 Ω. |
| 13 | 1 kΩ, 1%, 0805 resistor | 4 | ₹2.00 each, ex-GST (₹2.36 incl.) | [Evelta](https://evelta.com/1k-1-0-125w-0805-chip-resistor/) | 2,219 in stock. The page lists a full reel of 5,000 and does not say if single pieces are sold. |
| 14 | 1 µF, 50 V, X7R, 0805 capacitor | 4 | ₹12.00 each, ex-GST (₹14.16 incl.) | [Evelta](https://evelta.com/1uf-50v-10-x7r-0805-mlcc-multilayer-ceramic-capacitors-cc0805kkx7r9bb105) | 2,566 in stock. Full reel 3,000, same caveat. AVDD, DVDD and the LP5907 input and output. |
| 15 | Enclosure, ABS, IP65, about 200 × 120 × 75 mm | 1 | about ₹300 | [IndiaMART listings](https://m.indiamart.com/impcat/abs-enclosure.html) | Category page, not a single product. |

### Remaining small parts

| # | Part | Qty | Unit price (INR) | Buy link | How well checked |
|---|---|---|---|---|---|
| 16 | 6.49 Ω, 1%, 1206 resistor (burden halves, Vishay CRCW12066R49FKEA) | 2 | ₹15.81 each at 1 piece (₹10.25 at 10) | [Lion Circuits](https://www.lioncircuits.com/parts/CRCW12066R49FKEA) | Page read: in stock, ships in 7 to 10 days. A 1% part is fine because gain is calibrated. Alternative: [Digi-Key India](https://www.digikey.in/en/products/detail/vishay-dale/CRCW12066R49FKEA/1962318) ₹10.65 (search result only). |
| 17 | 10 nF, 50 V, C0G, 0805 capacitor (Walsin 0805N103J500CT, 5%) | 2 | ₹13.45 each at 1 piece (₹10.66 at 10) | [Lion Circuits](https://www.lioncircuits.com/parts/0805N103J500CT) | Page read: C0G confirmed, in stock, ships in 7 to 10 days. This replaces the ₹136.98 KEMET part. |
| 18 | 220 nF, 50 V, X7R, 0805 capacitor (Walsin 0805B224K500CT, 10%) | 1 | ₹13.45 each at 1 piece (₹10.40 at 10) | [Lion Circuits](https://www.lioncircuits.com/parts/0805B224K500CT) | Page read: X7R confirmed, in stock, ships in 7 to 10 days. |
| 19 | 220 µF, 25 V electrolytic capacitor (HLK-5M05 output) | 1 | ₹2.70 ex-GST (₹3.19 incl.) | [Evelta](https://evelta.com/220uf-25v-electrolytic-capacitor) | Page read: Samwha 6.3 × 11 mm, 18 in stock. Alternative: [Lion Circuits Nichicon UUX1E221MNL1GS](https://www.lioncircuits.com/parts/UUX1E221MNL1GS), ₹53.41. |
| 20 | 2-pin 5.08 mm screw terminal block | 1 pack of 5 | ₹31.74 incl. GST | [Zbotic](https://zbotic.in/?p=438931) | Search result only; the page blocked reading, so pitch and pack size are unconfirmed. |
| 21 | 7 × 9 cm perfboard, single-sided, 2.54 mm | 1 | ₹37 incl. GST | [Robu](https://st.robu.in/product/7-x-9-cm-universal-pcb-prototype-board-single-sided-2-54mm-hole-pitch) | Search result only; the link is the host the search returned. Robodo's [5-pack](https://robodo.in/products/5-pieces-general-purpose-perforated-pcb-boards-7-x-9-cm-perfboard) was listed at ₹18 but rate-limited when read. |

### Input protection (TI SBAA506, added for version 3)

Per ADC input pin, four pins in all: signal, then 1 kΩ, then a clamp node (a BAT54 Schottky diode to AVDD and a BAV199 pair to ground), then 100 Ω, then the ADC pin. The 10 nF capacitor sits across the two pins of each channel.

| # | Part | Qty | Unit price (INR) | Buy link | Notes |
|---|---|---|---|---|---|
| 22 | Diodes BAT54-7-F, Schottky, SOT-23 | 4 | ₹10.55 at 1 piece (₹4.89 at 25) | [Lion Circuits](https://www.lioncircuits.com/parts/BAT54-7-F) | Page read; in stock. |
| 23 | BAV199-7-F, dual series switching diode, SOT-23 | 4 | ₹20.72 at 1 piece (₹14.41 at 10) | [Lion Circuits](https://www.lioncircuits.com/parts/BAV199-7-F) | Page read; in stock. |
| 24 | 100 Ω, 1%, 0805 resistor | 4 | not priced yet | | No listing checked. |
| 25 | 3.3 V supply clamp (TVS or Zener on AVDD) | 1 | not chosen | | TI says a TVS or Zener is needed but names no part. AVDD absolute maximum is 3.9 V, so the part needs checking. |

Still no price or link found: hook-up wire and a mains cable with plug. The Zbotic terminal block and Robu perfboard prices (rows 20 and 21) are from search results only.

## B. Only if we build a custom board (not needed for the demo)

| Part | Qty | Price (INR) | Buy link | Notes |
|---|---|---|---|---|
| Diodes AP63203WU-7 3.3 V buck | 1 | ₹88.45 | [Digi-Key India](https://www.digikey.in/en/products/detail/diodes-incorporated/AP63203WU-7/9858430) | Page showed 0 in stock, expected 28-Jun-2027, 32-week lead time. Digi-Reel adds ₹452. |
| Inductor 3.9 µH, shielded, about 2 A | 1 | ₹102.60 at 500 pieces; 1-piece price not read | [Digi-Key India, Würth 7440520039](https://www.digikey.in/en/products/detail/würth-elektronik/7440520039/1638434) | From a search snippet only. |
| 10 µF, 2 × 22 µF, 100 nF capacitors | | not priced | | |

## C. Optional

| Part | Qty | Price (INR) | Buy link | Notes |
|---|---|---|---|---|
| 0.1 µF X2 safety capacitor (certification) | 1 | ₹3.75 ex-GST, 310 V AC | [Evelta](https://evelta.com/0-1uf-310vac-10-x2-pitch-10mm) | Sold out. |
| 10 mH common-mode choke (certification) | 1 | about ₹258 | not verified | Aggregator price from a search result, no seller page read. |
| PZEM-004T with 100 A CT (lab reference) | 1 | ₹569 | [Robocraze](https://robocraze.com/products/peacefair-pzem-004t-multi-function-ac-power-meter-for-energy-measurement) | Confirm the v3.0 revision before buying. |

## Rough total for part A

Using rows 1 to 23, without GST, shipping or fees:

| | Low | High |
|---|---|---|
| Total | about ₹3,700 | about ₹4,400 |

This leaves out hook-up wire and the mains cable. Minimum-pack sizes push the real spend higher: 25 resistors, a reel of 1 kΩ and 1 µF parts, 10 MOVs, a 20-piece pack of 220 nF. Digi-Key adds a ₹452 fee on Digi-Reel items, and several Digi-Key parts showed zero stock and long lead times.

Last reviewed 23 Nov 2026.

## What the "reel fee" is

Digi-Key sells small quantities cut from a long reel of parts, called "Digi-Reel". For those orders it adds a flat **₹452 reeling fee** per part number. It is charged once per part number on the order, not per piece, so it dwarfs the price of cheap parts (a ₹10 resistor becomes ₹462). It is not charged on cut tape or bulk packaging. To avoid it: buy from an Indian seller, or choose the "cut tape" or "bulk" option where Digi-Key offers it, or put many parts on one order only if each one avoids the Digi-Reel packaging.

# Datasheets

Local copies of the manufacturer documents the PowerLenz design is checked against. They are third-party documents, kept for reference. The checks and the numbers taken from them are recorded in [../findings/datasheet-verification-checklist.md](../findings/datasheet-verification-checklist.md). Download links and read status for every part, including the ones not stored here, are in [../findings/datasheet-links.md](../findings/datasheet-links.md).

Folder layout: one folder per function, file names carry the part, document and revision.

**The PDFs themselves are not stored in git** (`.gitignore` excludes them), so on a fresh clone the links below point to files that do not exist yet. Download them again from [../findings/datasheet-links.md](../findings/datasheet-links.md) into the matching folder using the file names listed here.

## adc/

| File | Document | What we used it for |
|---|---|---|
| [ADS131M04_SBAS890D_2021-05.pdf](adc/ADS131M04_SBAS890D_2021-05.pdf) | TI ADS131M04 datasheet, SBAS890D, May 2021 (105 pages) | Input range, filter recommendation, SPI frame, phase calibration, global-chop vs continuous mode, power and noise |
| [TI_SBAA506_ADC-overstress-protection_2021-03.pdf](adc/TI_SBAA506_ADC-overstress-protection_2021-03.pdf) | TI application note SBAA506, March 2021 (12 pages) | The BAT54 and BAV199 input clamp we adopted, 1 kΩ and 100 Ω resistor values, C0G filter capacitor |

## mcu/

| File | Document | What we used it for |
|---|---|---|
| [ESP32-S3_Series_Datasheet_v2.2.pdf](mcu/ESP32-S3_Series_Datasheet_v2.2.pdf) | Espressif ESP32-S3 series datasheet v2.2 (87 pages) | SPI controllers, strapping pins, GPIO and IO MUX. It gives no numeric SPI2 clock limit. |
| [Espressif_ESP-Dev-Kits_ESP32-S3_documentation.pdf](mcu/Espressif_ESP-Dev-Kits_ESP32-S3_documentation.pdf) | Espressif esp-dev-kits documentation for all ESP32-S3 boards (120 pages, 23 MB) | The DevKitC-1 section: power options, header pin table, regulator description |

## power/

| File | Document | What we used it for |
|---|---|---|
| [HLK-5M-series_V2.8_2022-06.pdf](power/HLK-5M-series_V2.8_2022-06.pdf) | Hi-Link 5M-series datasheet V2.8, June 2022 | HLK-5M05 ratings, derating graphs, typical circuit |
| [HLK-5M-series_V2.3_2019-10.pdf](power/HLK-5M-series_V2.3_2019-10.pdf) | Hi-Link 5M-series datasheet V2.3, October 2019 | Older revision. It carries the same isolation (3000 V vs 2500 V) and fuse (0.5 A vs 1 A) contradictions as V2.8. |
| [Diodes_AP63200-01-03-05_DS41326_Rev3-2_2024-11.pdf](power/Diodes_AP63200-01-03-05_DS41326_Rev3-2_2024-11.pdf) | Diodes AP63200/01/03/05 datasheet DS41326 Rev. 3-2, November 2024 | AP63203 3.3 V buck: input range and recommended inductor and capacitors |

## protection/

| File | Document | What we used it for |
|---|---|---|
| [Littelfuse_239-series_time-lag_fuse_2014-10-26.pdf](protection/Littelfuse_239-series_time-lag_fuse_2014-10-26.pdf) | Littelfuse 239 series time-lag fuse datasheet, revised 26 Oct 2014 | Showed the 1 A glass fuse is only rated 35 A at 250 V AC, so it was replaced |

## sensors/

| File | Document | What we used it for |
|---|---|---|
| [ZMPT107-1_Zeming_datasheet.pdf](sensors/ZMPT107-1_Zeming_datasheet.pdf) | Zeming ZMPT107-1 one-page sheet (Chinese) | Ratio, phase error, linearity, isolation, wiring figures |
| [ZMPT107_Zeming_datasheet.pdf](sensors/ZMPT107_Zeming_datasheet.pdf) | Zeming ZMPT107 one-page sheet (Chinese) | The plain ZMPT107: ABS case, 0.3% linearity, 60 °C limit. Not the part we use. |
| [ZMPT107G-1_Zeming_spec_2021-05-07.pdf](sensors/ZMPT107G-1_Zeming_spec_2021-05-07.pdf) | Zeming ZMPT107G-1 product specification, 7 May 2021 (Chinese) | The higher-grade variant: 30 arcminute phase error, 85 °C |

## Not stored here yet

| Document | Why it matters | Where to get it |
|---|---|---|
| Bourns MOV-D series datasheet (MOV-10D561K) | Clamping voltage, surge and energy ratings. Our figures are from distributor listings. | [Bourns datasheet](https://www.bourns.com/docs/product-datasheets/mov-d.pdf) |
| Bel Fuse 5HT series datasheet | Confirms the 1.5 kA breaking capacity of the replacement fuse | [Bel 5HT on alldatasheet](https://www.alldatasheet.com/html-pdf/2166821/BEL/5HT%20250-R/64/1/5HT%20250-R.html) |
| ESP32-S3 Technical Reference Manual | SPI2 maximum clock | [Espressif documentation](https://documentation.espressif.com/) |
| ESP32-S3-DevKitC-1 schematic | Onboard regulator current rating | Linked from the DevKitC-1 v1.1 user guide |
| SCT-013-000, LP5907, AP2112, ESP32-S3-WROOM-1 datasheets | Read earlier from their links; no local copy kept | See [../findings/datasheet-links.md](../findings/datasheet-links.md) |

Copies were downloaded on 23 Nov 2026. Check for newer revisions before relying on a number.

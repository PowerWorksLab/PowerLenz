# Sixteen Amps Brand Guidelines (version 2.0, November 2026)

Company: **Sixteen Amps**. Product: **PowerLenz by Sixteen Amps**.
Illustrated version: [`kit/06-guidelines/sixteen-amps-brand-guidelines.pdf`](kit/06-guidelines/sixteen-amps-brand-guidelines.pdf). Live example: [`sample/web-and-mobile.html`](sample/web-and-mobile.html).

## 1. Name

| Where | Write |
|---|---|
| In sentences | Sixteen Amps (two capitals) |
| In the logo | sixteen amps (lowercase, supplied artwork only) |
| Products | PowerLenz by Sixteen Amps |
| Avoid | 16 Amps, 16A, SixteenAmps as running text |

The name comes from the large socket in an Indian home.

## 2. Tagline and story line

| Line | Words | Where |
|---|---|---|
| Tagline | **Clarity for every unit of energy.** | With the logo: use the supplied `logo-tagline` artwork |
| Story line | **From every socket to every decision.** | Posters and presentations, set in IBM Plex Sans |

Use the tagline version at least 60 mm or 240 px wide; below that, use the logo alone. Do not put both lines side by side. Purpose, mission and roadmap are in [`company-purpose.md`](company-purpose.md).

## 3. Logo

- **Symbol:** Three Pins, fused. It also reads as an A, for Amps.
- **Lettering:** IBM Plex Sans SemiBold, converted to outlines, with a round dot on the i. Never retype it.
- **Layouts:** primary, primary with tagline, stacked, name only, symbol, endorsement ("by sixteen amps"), PowerLenz lockup.

| Background | Symbol and letters | Dot on the i | File variant |
|---|---|---|---|
| Light (Paper, White) | Navy | Navy | `navy` |
| Navy or black | White | **Brass** | `on-navy` |
| Brass | Navy | Navy | `navy` |
| One-colour production | Black or white | Same | `black`, `white` |

- Only the dot on the i ever takes Brass. The symbol on its own is always one colour.
- Clear space: one lower pin on every side.
- Minimum width: primary 120 px or 30 mm; stacked 90 px or 22 mm; symbol 16 px or 5 mm.
- 3D printing with about 0.8 mm features: primary logo at least 44 mm wide.
- Do not stretch, rotate, recolour, add effects or retype.

## 4. Typography

| Job | Typeface | Weight |
|---|---|---|
| Headings | **Bricolage Grotesque** | 700 |
| Data headings (large readings) | **IBM Plex Sans** | 700 |
| Paragraphs | **IBM Plex Sans** | 400 |
| Labels and buttons | **IBM Plex Sans** | 500 to 700 |
| Numbers in text, rows, tables and charts | **Roboto** | 500, 700 for values |
| Rupee prices, all sizes | **Roboto** | 700 |

All three are free on Google Fonts under open licences. Fallback: `Arial, sans-serif`. Hindi: IBM Plex Sans Devanagari (Bricolage Grotesque does not cover Devanagari).

### Sizes

| Element | Web | Phone |
|---|---|---|
| Main headline | 34 to 66 px, line height 1.12, tracking −2% | 30 px screen title |
| Section heading | 26 to 40 px | 20 px |
| Subheading | 21 px | 20 px |
| Lead paragraph | 19 px | 16 px |
| Paragraph | 16 px, line height 1.5 | 16 px, line height 1.5 |
| Large reading | 60 px | 60 px |
| Medium reading | 44 px | 25 px |
| Row value | 19 px | 19 px |
| Table value | 17 px | 17 px |
| Label | 14 px | 14 px or more |

### Rules

- Use Bricolage Grotesque only for headings, never for numbers or small labels.
- One number rule: large energy readings in IBM Plex Sans; every other number, and every price, in Roboto.
- Set figures as tabular (`font-variant-numeric: tabular-nums`) so values do not shift.
- No light weights or monospaced faces for readings.
- Keep paragraphs to about 60 to 75 characters a line.

```css
:root {
  --font-heading: 'Bricolage Grotesque', Arial, sans-serif;
  --font-body: 'IBM Plex Sans', Arial, sans-serif;
  --font-number: 'Roboto', Arial, sans-serif;
  --navy: #14213D;  --brass: #C9A66B;  --brass-tint: #F1EADB;
  --paper: #F7F5F0; --white: #FFFFFF;  --navy-quiet: #68748F;
}
```

## 5. Colour

| Colour | HEX | RGB | Use |
|---|---|---|---|
| **Navy** | `#14213D` | 20 33 61 | Main colour: logo, text, dark surfaces, buttons |
| **Brass** | `#C9A66B` | 201 166 107 | Accent: i dot on Navy, small highlights |
| Brass Tint | `#F1EADB` | 241 234 219 | Tip boxes and quiet panels |
| Paper | `#F7F5F0` | 247 245 240 | Page background |
| White | `#FFFFFF` | 255 255 255 | Cards; logo on Navy |
| Quiet Navy | `#68748F` | 104 116 143 | Secondary chart bars |

- Balance: mostly Paper and White, then Navy, with a little Brass.
- Navy and Brass pass for text on each other (7.0 : 1). **Never set Brass text on Paper or White** (about 2 : 1).
- Brass is a flat colour, not a metallic ink. Check a printed sample before ordering.

### Data colours (app and charts only)

| State | HEX | Meaning |
|---|---|---|
| Normal | `#1A9D5C` | Using power as expected |
| High | `#F2A900` | Higher use than expected |
| Fault | `#C62828` | Needs attention |
| Other | `#8F949E` | Not identified |

Always write the state in words as well. Brass is close to the High amber, so never use Brass for a status.

## 6. Voice (provisional)

Confident but not loud. Plain words and real measurements, no hype. Say what is measured and what is estimated.

## 7. Open items

- Answer the open questions in `company-purpose.md`.
- Trademark and similar-logo search.
- Register the domain (`sixteenamps.com` is printed on templates).
- Test how people read the symbol.
- Print, silkscreen and 3D-print proofs; check the DXF files in the CAD tool used.

## Folder map

| Path | Contents |
|---|---|
| `company-purpose.md` | Purpose, taglines, users, values and roadmap |
| `kit/` | Logos, icons, fabrication files, templates, patterns, illustrated guidelines |
| `sixteen-amps-brand-kit-v2.zip` | The kit, for sharing |
| `sample/` | Sample web page and mobile screen |
| `src/` | Build scripts: `python3 build.py` (kit and zip), `python3 sample.py` (sample), `python3 fetch_fonts.py` (fonts) |

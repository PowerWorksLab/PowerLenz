# Poster Wireframe Notes (reference: "Claire" poster set)

Sources, both in the repo root: `1.jpg` (720 x 1280 px, the full posters and the display table; the main reference) and `WhatsApp Image 2026-11-24 at 00.23.36.jpeg` (720 x 329 px, with blue circles drawn on it). Headings and layout are readable; most body text is not. Items marked (?) are best guesses.

## Format
- **Three portrait posters side by side**, read left to right as one story: problem and research, then user study and ideation, then final design and build.
- Same background, heading style and footer block on all three.
- Each sheet is about 2:3 in the photo (about 232 x 345 px), close to an A-series portrait (1:1.41). The exact size is unknown (?).
- Mounted edge to edge with no gaps, above the project's display table.

## Wireframe

```
 POSTER 1: WHY                POSTER 2: WHAT USERS NEED     POSTER 3: WHAT WE BUILT
+---------------------------+ +---------------------------+ +---------------------------+
| LOGO WORDMARK             | | [USER STUDY]              | | [FINAL RENDERS]           |
| Project subtitle          | | bar chart   | pie | pie   | | +-----------+-----------+ |
| [NEED IDENTIFIED]  (o)(o) | |                           | | |  hero     |  view 2   | |
|  - 5 bullets      photos  | | [FUNCTIONALITY] | grouped | | |  render   +-----------+ |
| >OBJECTIVES> > > >        | |  2-col table    | bar     | | |  +labels  |  view 3   | |
|        < < <OUTCOME< <    | |                 | chart   | | +--------+--+-----------+ |
| > > > > >  (zig-zag flow) | | [MARKET GAP]  [IDEATION]  | | | view 4 |   large view | |
| [LITERATURE STUDY] [STATS]| |  3 bullets    hand        | | | view 5 |   +labels    | |
|  card card         ladder | |               sketches    | | +--------+--------------+ |
|  card card          of    | | [BLUEPRINT]               | | [CIRCUIT DIAGRAM] [BOM    |
|  card card         numbers| |  dimensioned  | exploded  | |  wiring picture    table] |
| [RESEARCH FINDINGS] [note]| |  drawings     | sketch    | | [NOVELTY] bullets         |
|  2-col table      [TEAM]  | |                    [TEAM] | | [MANUFACTURING PLAN][TEAM]|
+---------------------------+ +---------------------------+ +---------------------------+
```

## Sections, in order
| Poster | Section | Form | Approx. share of poster height |
|---|---|---|---|
| 1 | Title block | Wordmark (script initial + serif caps), one-line subtitle | 15% |
| 1 | Need identified | 5 short bullets with side bars, 2 circular photos at right | 18% |
| 1 | Objectives and expected outcome | 3 rows of chevron arrows, snaking left-right-left | 20% |
| 1 | Literature study / justification | 6 cards (2 x 3), each with a round icon | 22% |
| 1 | Statistics (beside literature) | Stacked "number + caption" blocks, narrow column | same band |
| 1 | Research findings | 2-column comparison table, small note box beside it | 18% |
| 2 | User study | Question captions, horizontal bar chart, 2 pies, grouped bar chart | 45% |
| 2 | Functionality | 2-column table ("aspect" / "our project"), left half | within above |
| 2 | Market gap | 3 bullets | 10% |
| 2 | Ideation | Hand sketches in boxes | 20% |
| 2 | Blueprint | One drawing sheet with dimensioned orthographic and isometric views and a title block; left 65% | 25% |
| 3 | Final renders | 5 rendered views in an uneven tile grid, callout labels | 52% |
| 3 | Circuit diagram | Pictorial wiring diagram with component photos, left 60% | 25% |
| 3 | Bill of materials | Table with quantity, unit price, total and a total row, right 40% | same band |
| 3 | Novelty | About 6 bullets on a vertical rail | 12% |
| 3 | Manufacturing plan | Snaking 3-row timeline along the bottom, left of the team block | 8% |

## Repeating elements
- **Section header:** a filled dark tab with a rounded right end, white serif capitals. Headers on the right edge (Statistics, Ideation, Manufacturing Plan) are mirrored.
- **Connector rail:** a thin line drops from the header beside the bullets in Market Gap and Novelty.
- **Team block:** bottom-right of all three posters: a square team-number badge ("DFP 42"), member list, mentor line, small logo.
- **Margins and grid:** even outer margin; mostly one or two columns, with a 60/40 split where two items share a band.
- **Tables:** dark header row, thin rules, centred text.

## Visual style (theirs, to be replaced by our brand kit)
- Off-white / light grey-pink background.
- One hue only: dark maroon for headers and key blocks, mid red and pale pink for secondary fills. Charts use shades of the same hue.
- Serif for title and headings, small sans-serif for body.
- Image-heavy: photos, charts, sketches and renders carry more space than text.

## Unknown
- The meaning of the blue circles in the first photo (ideation and blueprint on poster 2, renders on poster 3). They are not on the posters.
- Exact fonts, colour codes, paper size and the small text.

## Display table (in front of the posters)
- A tablet playing or showing a 3D render of the product.
- A physical prototype model with small labels.
- Printed drawings.
- A team label on the wall below the posters ("DFP-42 (C9)").

## Possible PowerLenz mapping (suggestion, not decided)
| Their section | Our material |
|---|---|
| Need, objectives, literature | `documentation/README.md`, findings notes |
| Research findings / market gap | Comparison with existing energy monitors (needs research) |
| User study | Needs a survey; none exists in the repo as far as known |
| Ideation, blueprint | Enclosure sketches and drawings; not made yet |
| Final design renders | `hardware/kicad/exports/3d/` (board renders; no enclosure yet) |
| Circuit diagram | `documentation/diagrams/`, KiCad schematic PDF |
| Bill of materials | `documentation/findings/bill-of-materials.md` |
| Novelty, manufacturing plan | To be written |

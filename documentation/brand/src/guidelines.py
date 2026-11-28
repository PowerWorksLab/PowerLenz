"""The brand guidelines as an A4 landscape HTML document (printed to PDF by build.py)."""
from identity import (ARTS, BLACK, BRASS, DATA, FONT_CSS, NAVY, PAPER, QUIET, SYM_H, TINT, WHITE, cmyk, contrast, rgb)


def art(name, variant="navy", style=""):
    return ARTS[name].svg(variant, cls="art").replace('class="art"', f'class="art" style="{style}"')


def sec(number, title, body):
    return f'<section><h2><em>{number}</em>{title}</h2>{body}</section>'


def table(head, rows):
    return ("<table><tr>" + "".join(f"<th>{h}</th>" for h in head) + "</tr>"
            + "".join("<tr>" + "".join(f"<td>{c}</td>" for c in r) + "</tr>" for r in rows) + "</table>")


def card(bg, content, label=""):
    return f'<div class="card" style="background:{bg}">{content}<small style="color:{WHITE if bg in (NAVY, BLACK) else NAVY}">{label}</small></div>'


def clear_space():
    logo = ARTS["logo"]
    unit = 66 * SYM_H / 171     # one lower pin
    x0, y0, x1, y1 = logo.box
    circles = "".join(f'<circle cx="{x}" cy="{y}" r="{unit / 2}" fill="{BRASS}" opacity=".6"/>' for x, y in
                      ((x0 - unit / 2, (y0 + y1) / 2), (x1 + unit / 2, (y0 + y1) / 2), ((x0 + x1) / 2, y0 - unit / 2), ((x0 + x1) / 2, y1 + unit / 2)))
    return (f'<svg class="art" style="width:200mm;height:62mm" viewBox="{x0 - unit * 1.3} {y0 - unit * 1.3} {logo.w + unit * 2.6} {logo.h + unit * 2.6}">'
            f'<rect x="{x0 - unit}" y="{y0 - unit}" width="{logo.w + 2 * unit}" height="{logo.h + 2 * unit}" fill="none" stroke="{BRASS}" stroke-width="2" stroke-dasharray="9 7"/>'
            f'{circles}{logo.body(NAVY, NAVY)}</svg>')


def page(stem_ratio):
    colours = [("Navy", NAVY, "Main colour: logo, text, dark surfaces, buttons"), ("Brass", BRASS, "Accent: the i dot on Navy, small highlights"),
               ("Brass Tint", TINT, "Tip boxes and quiet panels"), ("Paper", PAPER, "Page background"), ("White", WHITE, "Cards; logo on Navy")]
    swatches = "".join(f'<div class="sw" style="background:{h};color:{WHITE if h == NAVY else NAVY}"><b>{n}</b><span>HEX {h}</span>'
                       f'<span>RGB {" ".join(map(str, rgb(h)))}</span><span>CMYK {" ".join(map(str, cmyk(h)))}*</span><i>{use}</i></div>'
                       for n, h, use in colours)
    pairs = [("Navy on Paper", NAVY, PAPER), ("Navy on White", NAVY, WHITE), ("White on Navy", WHITE, NAVY), ("Brass on Navy", BRASS, NAVY),
             ("Navy on Brass", NAVY, BRASS), ("Navy on Brass Tint", NAVY, TINT), ("Brass on Paper", BRASS, PAPER)]
    contrast_rows = []
    for name, fg, bg in pairs:
        r = contrast(fg, bg)
        use = "Any text" if r >= 4.5 else "Large text only" if r >= 3 else "Never for text"
        contrast_rows.append((f'<span class="chip" style="background:{bg};color:{fg}">Aa</span> {name}', f"{r:.1f} : 1", use))
    data_rows = [(f'<span class="dot" style="background:{h}"></span>{n}', h, use) for (n, h), use in
                 zip(DATA.items(), ("Appliance using power as expected", "Higher use than expected", "Needs attention", "Not identified"))]
    bad = [("Do not stretch", art("logo", style="transform:scaleX(1.3) scaleY(.8)")), ("Do not rotate", art("logo", style="transform:rotate(-12deg)")),
           ("Do not colour the symbol", art("symbol", style="max-height:30mm").replace(f'fill="{NAVY}"', f'fill="{BRASS}"')),
           ("Do not recolour the name", art("logo").replace(NAVY, "#C0392B")), ("Do not add effects", art("logo", style="filter:drop-shadow(6px 6px 3px #0007)")),
           ("Do not retype the name", f'<span style="font:700 30px Arial;color:{NAVY}">Sixteen Amps</span>')]
    apps = (("business-card-front", "Card, front"), ("business-card-back", "Card, back"), ("slide-title", "Title slide"), ("slide-content", "Content slide"),
            ("social-cover", "Social cover"), ("sticker-round-50mm", "50 mm sticker"), ("poster-a1", "A1 project poster"), ("letterhead-a4", "A4 letterhead"))
    patterns = "".join(f'<img src="../05-pattern/pins-field-{n}.svg" alt="{n} pattern">' for n in ("navy", "paper", "brass"))
    spec = lambda family, weight, size, words: f'<span style="font-family:\'{family}\';font-weight:{weight};font-size:{size}px">{words}</span>'

    pages = [
        f'<section class="cover">{art("symbol", "white", "width:52mm")}{art("logo", "on-navy", "width:180mm")}<p>Brand guidelines · version 2.0 · November 2026</p></section>',
        sec("01", "The idea", '<p class="big">Sixteen Amps takes its name from the large socket in an Indian home. Three pins are joined into one shape: separate points, one current. The shape also reads as an A, for Amps.</p>'
            '<div class="g3"><div class="note"><b>Confident, not loud</b>Navy carries the brand; Brass appears in small amounts.</div><div class="note"><b>Plain</b>Real measurements, simple words, no hype.</div><div class="note"><b>Consistent</b>One symbol, one signature dot, a fixed set of typefaces.</div></div>'),
        sec("02", "Logo system", '<div class="g2">' + card(PAPER, art("logo"), "Primary logo, light backgrounds") + card(NAVY, art("logo", "on-navy"), "Primary logo on Navy")
            + card(PAPER, art("stacked", style="max-height:44mm"), "Stacked: square spaces") + card(NAVY, art("powerlenz-lockup", "on-navy", "max-height:42mm"), "PowerLenz lockup") + "</div>"),
        sec("03", "Colour on the logo", '<div class="g2">' + card(NAVY, art("logo", "on-navy"), "On Navy or black: white, with a Brass dot") + card(PAPER, art("logo"), "On light: all Navy, including the dot")
            + card(BRASS, art("logo"), "On Brass: all Navy") + card(WHITE, art("logo", "black"), "Production: one colour") + "</div>"
            "<p><b>Only the dot on the i ever takes Brass.</b> The symbol and letters stay one colour. The symbol on its own is always one colour.</p>"),
        sec("04", "Clear space and size", f'<div class="panel">{clear_space()}</div><p>Keep a margin of at least <b>one lower pin</b> on every side.</p>'
            + table(("Use", "Screen, minimum width", "Print, minimum width"), (("Primary logo", "120 px", "30 mm"), ("Stacked", "90 px", "22 mm"), ("Symbol", "16 px", "5 mm")))
            + f"<p>At 30 mm wide the letter stems are about {stem_ratio * 30:.1f} mm. For single-nozzle 3D printing (about 0.8 mm features) use the logo at {0.8 / stem_ratio:.0f} mm or wider. Proof a sample before production.</p>"),
        sec("05", "Colour", f'<div class="g5">{swatches}</div><p>* CMYK values are direct conversions: match them to a printed swatch. Brass is a flat colour, not a metallic ink.</p>'
            + table(("Pair", "Contrast", "Allowed for"), contrast_rows)),
        sec("06", "Colour in the interface", '<div class="mix"><div style="flex:70;background:#F7F5F0">Paper and White</div><div style="flex:24;background:#14213D;color:#fff">Navy</div><div style="flex:6;background:#C9A66B">Brass</div></div>'
            + table(("Element", "Colour"), (("Headers, footers, buttons on light", "Navy"), ("Button on Navy, today's chart bar, small rules", "Brass"), ("Other chart bars", f"Quiet Navy {QUIET}"), ("Tips and quiet panels", "Brass Tint with a Brass edge")))
            + table(("Data colour", "HEX", "Meaning (always written in words too)"), data_rows)
            + "<p><b>Brass is close to the High amber.</b> Never use Brass for a status, and never rely on colour alone.</p>"),
        sec("07", "Typography", "<p>All three families are on Google Fonts under open licences. The logo is supplied as outlines (IBM Plex Sans SemiBold): never retype it.</p>"
            + table(("Job", "Typeface and weight", "Specimen"), (
                ("Headings", "Bricolage Grotesque 700", spec("Bricolage Grotesque", 700, 30, "See where your electricity goes.")),
                ("Data headings: large readings", "IBM Plex Sans 700", spec("IBM Plex Sans", 700, 34, "1,248 W · 45.8 kWh")),
                ("Paragraphs", "IBM Plex Sans 400", spec("IBM Plex Sans", 400, 15, "An electricity bill gives one total. It does not say which appliance caused it.")),
                ("Labels and buttons", "IBM Plex Sans 500 to 700", spec("IBM Plex Sans", 600, 14, "Using now · View usage")),
                ("Numbers in text, rows, charts", "Roboto 500", spec("Roboto", 500, 18, "230 V · 5.43 A · 50 Hz · 6.40 kWh")),
                ("All rupee prices", "Roboto 700", spec("Roboto", 700, 22, "₹48.60 · ₹1,420"))))),
        sec("08", "Type on screens", '<div class="g2"><div class="demo"><span>Using now · sample</span><div class="hero">1,248 W</div><div class="row"><span>Water heater</span><b>1,050 W</b></div><div class="row"><span>Refrigerator</span><b>120 W</b></div><div class="row"><span>Cost today</span><b>₹48.60</b></div><p>You have used <em>6.40 kWh</em> today.</p></div>'
            + table(("On a phone", "Setting"), (("Screen heading", "Bricolage Grotesque 700, 30 px"), ("Section heading", "Bricolage Grotesque 700, 20 px"), ("Large reading", "IBM Plex Sans 700, 60 px"), ("Row value", "Roboto 700, 19 px"), ("Number in a sentence", "Roboto 500, 16 px"), ("Paragraph", "IBM Plex Sans 400, 16 px, line height 1.5"), ("Label", "IBM Plex Sans 500, 14 px or more")))
            + "</div><p>Set all figures as tabular so values do not shift as they change. No light or monospaced type for readings. On the web, headlines run from 34 to 66 px. For Hindi, use IBM Plex Sans Devanagari.</p>"),
        sec("09", "Graphic device: the pins field", f'<p>Dots of two sizes with the symbol among them. Use on covers and posters, never behind body text.</p><div class="g3">{patterns}</div>'),
        sec("10", "Name and products", '<div class="g2">' + card(PAPER, art("powerlenz-lockup", style="max-height:42mm")) + card(NAVY, art("endorsement", "on-navy")) + "</div>"
            + table(("Where", "Write"), (("In sentences", "Sixteen Amps (two capitals)"), ("In the logo", "sixteen amps (lowercase, supplied artwork only)"), ("Products", "PowerLenz by Sixteen Amps"), ("Avoid", "16 Amps, 16A, SixteenAmps as running text")))),
        sec("11", "Applications", '<div class="apps">' + "".join(f'<figure><img src="../04-templates/{n}.svg" alt="{c}"><figcaption>{c}</figcaption></figure>' for n, c in apps) + "</div>"),
        sec("12", "Misuse", '<div class="g3">' + "".join(card(PAPER, x, "× " + n) for n, x in bad) + "</div>"),
        sec("13", "Files and open items", table(("Folder", "Contents"), (("01-logo", "SVG and PNG: six layouts"), ("02-icons", "Favicon, app icons, avatar, web manifest"), ("03-fabrication", "KiCad silkscreen footprints and DXF outlines in millimetres"), ("04-templates", "Card, letterhead, poster, slides, sticker, social cover"), ("05-pattern", "Pins field backgrounds")))
            + "<p><b>Before launch:</b> trademark and similar-logo search; register the domain; test how people read the symbol; print and fabrication proofs.</p><p><b>To be written:</b> company purpose, goals and voice.</p>"),
    ]
    css = f"""@page{{size:A4 landscape;margin:0}} *{{box-sizing:border-box;margin:0;padding:0;-webkit-print-color-adjust:exact;print-color-adjust:exact}}
body{{font:13px/1.55 'IBM Plex Sans',Arial,sans-serif;color:{NAVY};background:#d9d8d4;font-variant-numeric:tabular-nums}}
section{{width:297mm;height:209.6mm;margin:0 auto 14px;background:{WHITE};padding:15mm;overflow:hidden;break-after:page;display:flex;flex-direction:column;gap:5mm}}
@media print{{section{{margin:0}} body{{background:{WHITE}}}}}
h2{{font:700 24px 'Bricolage Grotesque';letter-spacing:-.02em}} h2 em{{font:700 13px 'IBM Plex Sans';color:{QUIET};margin-right:14px;vertical-align:middle}}
.cover{{background:{NAVY};color:{WHITE};justify-content:space-between}} .art{{display:block;width:100%;height:auto}}
.big{{font-size:21px;line-height:1.45;max-width:230mm}} .g2{{display:grid;grid-template-columns:1fr 1fr;gap:5mm}} .g3{{display:grid;grid-template-columns:repeat(3,1fr);gap:5mm}} .g5{{display:grid;grid-template-columns:repeat(5,1fr);gap:4mm}}
.card{{border-radius:4mm;height:66mm;display:flex;flex-direction:column;align-items:center;justify-content:center;padding:10mm;position:relative}} .card .art{{max-width:100%;max-height:42mm}} .card small{{position:absolute;left:5mm;bottom:3mm;font-size:10px}}
.panel{{background:{PAPER};border-radius:4mm;padding:5mm;display:flex;justify-content:center}} .note{{background:{PAPER};border-radius:4mm;padding:8mm}} .note b{{display:block;font:700 18px 'Bricolage Grotesque';margin-bottom:2mm}}
table{{border-collapse:collapse;width:100%}} td,th{{border-bottom:1px solid #ddd;padding:1.8mm 3mm;text-align:left;vertical-align:middle}} th{{font-size:11px;color:{QUIET}}}
.sw{{border:1px solid #ddd;border-radius:4mm;height:62mm;padding:4mm;display:flex;flex-direction:column;font-family:'Roboto'}} .sw b{{font:700 16px 'IBM Plex Sans';margin-bottom:auto}} .sw i{{font:normal 10.5px 'IBM Plex Sans';margin-top:2mm}}
.chip{{display:inline-block;padding:.5mm 3mm;border-radius:2mm;font-weight:700;margin-right:3mm;border:1px solid #ddd}} .dot{{display:inline-block;width:3.5mm;height:3.5mm;border-radius:50%;margin-right:3mm}}
.mix{{display:flex;height:18mm;border-radius:3mm;overflow:hidden;border:1px solid #ddd;font-weight:700}} .mix div{{display:flex;align-items:center;justify-content:center}}
.demo{{background:{PAPER};border-radius:4mm;padding:8mm;font-size:16px;font-weight:500}} .hero{{font:700 60px/1.15 'IBM Plex Sans';margin-bottom:3mm}} .demo .row{{display:flex;justify-content:space-between;border-top:1px solid #0002;padding:2.5mm 0}} .demo b{{font:700 19px 'Roboto'}} .demo p{{font-weight:400;margin-top:3mm}} .demo em{{font:500 16px 'Roboto'}}
img{{width:100%;display:block;border-radius:3mm;border:1px solid #ddd}} .apps{{display:grid;grid-template-columns:repeat(4,1fr);gap:4mm}} .apps img{{height:62mm;object-fit:contain;background:#e9e7e1}} figcaption{{font-size:10px;margin-top:1mm}}"""
    return (f'<!doctype html><html lang="en"><head><meta charset="utf-8"><title>Sixteen Amps Brand Guidelines</title>'
            f'<style>{FONT_CSS}</style><style>{css}</style></head><body>{"".join(pages)}</body></html>')

"""Builds kit/ and the brand kit zip.   Run:  python3 build.py

Needs KiCad's pcbnew module, PangoCairo, Google Chrome, ImageMagick, zip and fonts/ (fetch_fonts.py).
The kit folder is recreated on every run; nothing in it is edited by hand.
"""
import base64
import json
import shutil
import subprocess
import tempfile
from pathlib import Path

import pcbnew

import guidelines
from identity import (ARTS, BLACK, BRASS, NAVY, PAPER, SC, STEM_RATIO, TINT, WEBFONTS, WHITE, variants_for)

BRAND = Path(__file__).resolve().parent.parent
KIT = BRAND / "kit"
ZIP = BRAND / "sixteen-amps-brand-kit-v2.zip"
HEAD, BODY = "Bricolage Grotesque", "IBM Plex Sans"
logo, symbol, lockup = ARTS["logo"], ARTS["symbol"], ARTS["powerlenz-lockup"]
PNG_JOBS = []


def write(rel, content):
    path = KIT / rel
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content)


def logos():
    for name, art in ARTS.items():
        width = 1024 if name == "symbol" else 2400
        height = round(width * (art.h + 12) / (art.w + 12))
        for variant in variants_for(name):
            stem = f"sixteen-amps-{name}-{variant}"
            write(f"01-logo/svg/{stem}.svg", art.svg(variant))
            PNG_JOBS.append((f"01-logo/png/{stem}.png", art.svg(variant, size=(width, height)), width, height))


def tile(bg, variant, size, ratio, radius=0.0, circle=False):
    """A square icon drawn on a 1024 grid and output at `size` pixels."""
    w = 1024 * ratio
    h = symbol.height_for(w)
    shape = (f'<circle cx="512" cy="512" r="512" fill="{bg}"/>' if circle
             else f'<rect width="1024" height="1024" rx="{1024 * radius}" fill="{bg}"/>')
    return (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1024 1024" width="{size}" height="{size}" '
            f'role="img" aria-label="Sixteen Amps">{shape}{symbol.place((1024 - w) / 2, (1024 - h) / 2, w, variant)}</svg>')


def icons():
    sets = {  # name: (tile settings, PNG sizes)
        "app-icon-navy": (dict(bg=NAVY, variant="white", ratio=0.62), (180, 192, 512, 1024)),
        "app-icon-white": (dict(bg=WHITE, variant="navy", ratio=0.62), (1024,)),
        "app-icon-brass": (dict(bg=BRASS, variant="navy", ratio=0.62), (1024,)),
        "avatar-round": (dict(bg=NAVY, variant="white", ratio=0.56, circle=True), (1024,)),
        "favicon": (dict(bg=NAVY, variant="white", ratio=0.72, radius=0.22), (16, 32, 48)),
        "icon-maskable": (dict(bg=NAVY, variant="white", ratio=0.52), (192, 512)),
    }
    for name, (settings, sizes) in sets.items():
        write(f"02-icons/{name}.svg", tile(size=1024, **settings))
        for s in sizes:
            PNG_JOBS.append((f"02-icons/{name}-{s}.png", tile(size=s, **settings), s, s))
    write("02-icons/site.webmanifest", json.dumps({
        "name": "Sixteen Amps", "short_name": "Sixteen Amps", "theme_color": NAVY, "background_color": PAPER, "display": "standalone",
        "icons": [{"src": "app-icon-navy-192.png", "sizes": "192x192", "type": "image/png"},
                  {"src": "app-icon-navy-512.png", "sizes": "512x512", "type": "image/png"},
                  {"src": "icon-maskable-512.png", "sizes": "512x512", "type": "image/png", "purpose": "maskable"}]}, indent=2) + "\n")
    write("02-icons/head-snippet.html",
          '<link rel="icon" href="/favicon.ico" sizes="48x48">\n<link rel="icon" href="/favicon.svg" type="image/svg+xml">\n'
          '<link rel="apple-touch-icon" href="/app-icon-navy-180.png">\n<link rel="manifest" href="/site.webmanifest">\n')


def rings(art, width_mm, fracture):
    """Polygons in millimetres, centred on the origin."""
    scale = width_mm / art.w
    cx, cy = (art.box[0] + art.box[2]) / 2, (art.box[1] + art.box[3]) / 2
    ps = pcbnew.SHAPE_POLY_SET(art.solid)
    if fracture:
        ps.Fracture()       # holes become thin slits, which a footprint polygon can hold

    def points(chain):
        return [((chain.CPoint(i).x / SC - cx) * scale, (chain.CPoint(i).y / SC - cy) * scale) for i in range(chain.PointCount())]

    out = []
    for i in range(ps.OutlineCount()):
        out.append(points(ps.Outline(i)))
        out += [points(ps.Hole(i, j)) for j in range(ps.HoleCount(i))]
    return out


def fabrication():
    for name, widths in (("logo", (30, 60)), ("symbol", (8, 20)), ("powerlenz-lockup", (40, 80))):
        art = ARTS[name]
        for width in widths:
            fid = f"SixteenAmps_{name}_{width}mm"
            h = art.height_for(width)
            body = "".join('\t(fp_poly (pts %s) (stroke (width 0) (type solid)) (fill yes) (layer "F.SilkS"))\n'
                           % " ".join(f"(xy {x:.4f} {y:.4f})" for x, y in p) for p in rings(art, width, True))
            write(f"03-fabrication/kicad/sixteen-amps.pretty/{fid}.kicad_mod",
                  f'(footprint "{fid}"\n\t(version 20260206)\n\t(generator "sixteen-amps-kit")\n\t(layer "F.Cu")\n'
                  f'\t(property "Reference" "LOGO" (at 0 {-h / 2 - 1.5:.2f} 0) (layer "F.SilkS") (hide yes) (effects (font (size 1 1) (thickness 0.15))))\n'
                  f'\t(property "Value" "{fid}" (at 0 {h / 2 + 1.5:.2f} 0) (layer "F.Fab") (hide yes) (effects (font (size 1 1) (thickness 0.15))))\n'
                  f'\t(attr board_only exclude_from_pos_files exclude_from_bom)\n{body})\n')
            dxf = ["0", "SECTION", "2", "HEADER", "9", "$INSUNITS", "70", "4", "0", "ENDSEC", "0", "SECTION", "2", "ENTITIES"]
            for p in rings(art, width, False):
                dxf += ["0", "POLYLINE", "8", "LOGO", "66", "1", "70", "1"]
                for x, y in p:
                    dxf += ["0", "VERTEX", "8", "LOGO", "10", f"{x:.4f}", "20", f"{-y:.4f}"]
                dxf += ["0", "SEQEND"]
            write(f"03-fabrication/dxf/sixteen-amps-{name}-{width}mm.dxf", "\n".join(dxf + ["0", "ENDSEC", "0", "EOF"]) + "\n")


def t(x, y, size, words, fill=NAVY, weight=400, family=BODY, extra=""):
    return f'<text x="{x}" y="{y}" font-family="\'{family}\', Arial, sans-serif" font-size="{size}" font-weight="{weight}" fill="{fill}" {extra}>{words}</text>'


def sheet(name, w, h, body, bg, unit=""):
    fonts = "".join(css for family, css in WEBFONTS.items() if f"'{family}'" in body)
    style = f"<style>{fonts}</style>" if fonts else ""
    write(f"04-templates/{name}.svg", f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {w} {h}" width="{w}{unit}" height="{h}{unit}">'
                                      f'{style}<rect width="{w}" height="{h}" fill="{bg}"/>{body}</svg>')


def templates():
    # business card 90 x 54 mm plus 3 mm bleed
    sheet("business-card-front", 96, 60, logo.place(18, 30 - logo.height_for(60) / 2, 60, "on-navy"), NAVY, "mm")
    sheet("business-card-back", 96, 60, logo.place(9, 9, 46) + t(9, 40, 3.6, "Name Surname", weight=700, family=HEAD)
          + t(9, 45, 2.8, "Role") + t(9, 50.5, 2.8, "sixteenamps.com", weight=600), PAPER, "mm")
    sheet("letterhead-a4", 210, 297, logo.place(20, 18, 62) + t(190, 24, 3.2, "sixteenamps.com", extra='text-anchor="end"')
          + f'<rect x="20" y="36" width="14" height="1" fill="{BRASS}"/>' + t(20, 60, 3.6, "Date") + t(20, 74, 3.6, "Dear Name,")
          + "".join(f'<rect x="20" y="{84 + i * 8}" width="{170 if i % 4 != 3 else 110}" height="2.2" rx="1.1" fill="{NAVY}" opacity="0.08"/>' for i in range(14))
          + f'<rect x="20" y="272" width="170" height="0.4" fill="{NAVY}"/>' + symbol.place(20, 277, 8) + t(32, 282.5, 2.8, "Sixteen Amps · Address line"), WHITE, "mm")

    def tab(x, y, label):
        return f'<rect x="{x}" y="{y}" width="150" height="14" rx="7" fill="{NAVY}"/>' + t(x + 9, y + 9.8, 8, label, WHITE, 700, HEAD)

    def box(x, y, w, h):
        return f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="6" fill="{WHITE}"/>' + t(x + w / 2, y + h / 2, 7, "content", "#7d7f86", extra='text-anchor="middle"')

    sections = ((28, 172, 260, 150, "Need"), (306, 172, 260, 150, "User study"), (28, 358, 538, 160, "How it works"),
                (28, 554, 260, 150, "Design"), (306, 554, 260, 150, "Bill of materials"))
    sheet("poster-a1", 594, 841, f'<rect width="594" height="150" fill="{NAVY}"/>' + symbol.place(500, 38, 62, "white")
          + lockup.place(28, 28, 230, "on-navy") + t(28, 134, 10, "One line that says what the product does", WHITE)
          + f'<rect y="150" width="594" height="3" fill="{BRASS}"/>'
          + "".join(tab(x, y, label) + box(x, y + 20, w, h) for x, y, w, h, label in sections)
          + f'<rect x="28" y="740" width="538" height="73" rx="8" fill="{NAVY}"/>' + logo.place(46, 762, 170, "on-navy")
          + t(250, 766, 8, "Team number · Member names", WHITE, 600) + t(250, 781, 8, "Mentor · Course · Institute", WHITE), PAPER, "mm")
    sheet("sticker-round-50mm", 56, 56, f'<circle cx="28" cy="28" r="28" fill="{NAVY}"/>'
          + symbol.place(13, 28 - symbol.height_for(30) / 2, 30, "white"), WHITE, "mm")
    sheet("slide-title", 1920, 1080, logo.place(120, 100, 520, "on-navy") + t(120, 640, 120, "Presentation title", WHITE, 700, HEAD)
          + f'<rect x="120" y="680" width="120" height="8" fill="{BRASS}"/>' + t(120, 770, 48, "Subtitle · Date", WHITE)
          + symbol.place(1520, 720, 280, "white"), NAVY)
    sheet("slide-content", 1920, 1080, t(120, 170, 72, "Slide heading", weight=700, family=HEAD)
          + f'<rect x="120" y="205" width="100" height="7" fill="{BRASS}"/>'
          + "".join(f'<rect x="120" y="{290 + i * 90}" width="{1100 if i % 3 != 2 else 760}" height="22" rx="11" fill="{NAVY}" opacity="0.1"/>' for i in range(6))
          + logo.place(1500, 960, 300), PAPER)
    sheet("social-cover", 1500, 500, logo.place(400, 250 - logo.height_for(700) / 2, 700, "on-navy"), NAVY)


def patterns():
    """The pins field: dots of two sizes with the symbol among them."""
    for name, fg, bg in (("pins-field-navy", "#2A3A5E", NAVY), ("pins-field-paper", "#E3DDCF", PAPER), ("pins-field-brass", "#BC9657", BRASS)):
        marks = ""
        for row in range(6):
            for col in range(10):
                x, y = col * 100 + (50 if row % 2 else 0) + 20, row * 100 + 40
                if (col * 3 + row * 5) % 7 == 0:
                    marks += symbol.place(x - 32, y - 32, 64).replace(f'fill="{NAVY}"', f'fill="{fg}"')
                else:
                    marks += f'<circle cx="{x}" cy="{y}" r="{11 if (col + row) % 3 else 18}" fill="{fg}"/>'
        write(f"05-pattern/{name}.svg", f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1000 600" width="1000" height="600">'
                                        f'<rect width="1000" height="600" fill="{bg}"/>{marks}</svg>')


README = f"""# Sixteen Amps brand kit, version 2.0

Logo: **Three Pins, fused**, lettered in IBM Plex Sans SemiBold. Colours: **Navy `{NAVY}`** and **Brass `{BRASS}`**.

| Folder | Contents |
|---|---|
| `01-logo/` | `svg/` and `png/`: logo, stacked, wordmark, symbol, endorsement and PowerLenz lockup. Variants: `navy` (light backgrounds), `on-navy` (white with a Brass dot), `black`, `white` |
| `02-icons/` | favicon (SVG, ICO), app icons, round avatar, maskable icon, web manifest |
| `03-fabrication/` | `kicad/` silkscreen footprints and `dxf/` outlines; the file name gives the width in mm |
| `04-templates/` | business card (3 mm bleed), A4 letterhead, A1 poster, slides, 50 mm sticker, social cover |
| `05-pattern/` | pins field backgrounds |
| `06-guidelines/` | brand guidelines (HTML and PDF) |

Type: Bricolage Grotesque (headings), IBM Plex Sans (data headings, paragraphs), Roboto (numbers, rupee prices).
Template fonts are embedded for viewing in a browser; install them from Google Fonts to edit in a design program.

Rebuild with `python3 build.py` in `../src/`.

Not yet done: trademark and similar-logo search, domain registration, audience test of the symbol, print and fabrication proofs.
"""


def render():
    """PNG files in one headless Chrome pass, then favicon.ico and the guidelines PDF."""
    with tempfile.TemporaryDirectory() as d:
        page = Path(d) / "render.html"
        jobs = [[svg, w, h] for _, svg, w, h in PNG_JOBS]
        page.write_text("<body></body><script>const J=" + json.dumps(jobs) + """;
Promise.all(J.map(([s,w,h])=>new Promise((ok,no)=>{const i=new Image();i.onload=()=>{const c=document.createElement("canvas");c.width=w;c.height=h;
c.getContext("2d").drawImage(i,0,0,w,h);ok(c.toDataURL())};i.onerror=no;i.src="data:image/svg+xml;charset=utf-8,"+encodeURIComponent(s)})))
.then(r=>document.body.textContent=r.join("|"))</script>""")
        chrome = ["google-chrome", "--headless", "--disable-gpu", f"--user-data-dir={d}/profile"]
        dom = subprocess.run(chrome + ["--virtual-time-budget=60000", "--dump-dom", page.as_uri()],
                             capture_output=True, text=True, timeout=300, check=True).stdout
        data = dom.split("<body>")[-1].split("</body>")[0].split("|")
        assert len(data) == len(PNG_JOBS), f"rendered {len(data)} of {len(PNG_JOBS)}"
        for (rel, *_), url in zip(PNG_JOBS, data):
            path = KIT / rel
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_bytes(base64.b64decode(url.split(",")[1]))
        icons_dir = KIT / "02-icons"
        subprocess.run(["magick"] + [str(icons_dir / f"favicon-{s}.png") for s in (16, 32, 48)] + [str(icons_dir / "favicon.ico")], check=True)
        base = KIT / "06-guidelines/sixteen-amps-brand-guidelines"
        subprocess.run(chrome + ["--no-pdf-header-footer", "--virtual-time-budget=10000", f"--print-to-pdf={base}.pdf",
                                 base.with_suffix(".html").as_uri()], check=True, capture_output=True, timeout=300)


def main():
    shutil.rmtree(KIT, ignore_errors=True)
    logos()
    icons()
    fabrication()
    templates()
    patterns()
    write("06-guidelines/sixteen-amps-brand-guidelines.html", guidelines.page(STEM_RATIO))
    write("README.md", README)
    render()
    ZIP.unlink(missing_ok=True)
    subprocess.run(["zip", "-qr", ZIP.name, KIT.name], cwd=BRAND, check=True)
    print(f"kit: {sum(p.is_file() for p in KIT.rglob('*'))} files, {len(PNG_JOBS)} PNG renders; zip {ZIP.stat().st_size / 1e6:.1f} MB")
    for name, art in ARTS.items():
        holes = sum(art.solid.HoleCount(i) for i in range(art.solid.OutlineCount()))
        print(f"{name}: {art.solid.OutlineCount()} shapes, {holes} holes")


if __name__ == "__main__":
    main()

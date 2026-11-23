"""Turn the three inline SVG diagrams in documentation/diagrams/powerlenz-front-end.html
into standalone SVG files (light theme, concrete colors, no CSS variables or scripts),
plus a few cropped views for slides. Run: python3 -I extract_diagrams.py
"""
import math
import os
import re

HERE = os.path.dirname(os.path.abspath(__file__))
SRC = os.path.join(HERE, "..", "..", "diagrams", "powerlenz-front-end.html")
OUT = os.path.join(HERE, "..", "assets", "svg")
os.makedirs(OUT, exist_ok=True)

CSS = """
.zone-m{fill:#c2362b;fill-opacity:.06}
.zone-l{fill:#1f6fb5;fill-opacity:.05}
.wm,.ws,.wp,.wd{fill:none;stroke-width:2.2;stroke-linecap:round;stroke-linejoin:round}
.wm{stroke:#c2362b}.ws{stroke:#1f6fb5}.wp{stroke:#a9650a}.wd{stroke:#5d6a73;stroke-width:1.8}
.part{fill:#fff;stroke:#1b2227;stroke-width:1.6}
.block{fill:#fff;stroke:#1b2227;stroke-width:1.8}
.thin{fill:none;stroke:#1b2227;stroke-width:1.6;stroke-linecap:round}
.gnd{fill:none;stroke:#1f6fb5;stroke-width:1.8;stroke-linecap:round}
.barrier{stroke:#1b2227;stroke-width:1.4;stroke-dasharray:7 5}
.dot-m{fill:#c2362b}.dot-s{fill:#1f6fb5}.dot-p{fill:#a9650a}
.a-m{fill:#c2362b}.a-s{fill:#1f6fb5}.a-p{fill:#a9650a}.a-d{fill:#5d6a73}
text{fill:#1b2227;font-family:'Liberation Sans',Arial,sans-serif;font-size:13px}
.b{font-weight:700;font-size:14px}
.mono{font-family:'Liberation Mono','Courier New',monospace;font-size:12px}
.dim{fill:#5d6a73;font-size:12px}
.zone-label{fill:#5d6a73;font-size:12px;letter-spacing:.08em;font-weight:700}
.tm{fill:#c2362b}.ts{fill:#1f6fb5}.tp{fill:#a9650a}
.core{fill:#cfd6db;stroke:#1b2227;stroke-width:1.6;fill-rule:evenodd}
.turn{stroke:#1f6fb5;stroke-width:3;stroke-linecap:round;fill:none}
.flux{fill:none;stroke:#5d6a73;stroke-width:2;stroke-dasharray:6 5}
.badge{fill:#1b2227}
.badge-t{fill:#fff;font-weight:700;font-size:12px;text-anchor:middle}
.grid{stroke:#cfd6db;stroke-width:1;fill:none}
.axis{stroke:#5d6a73;stroke-width:1.2;fill:none}
.curve{fill:none;stroke:#1f6fb5;stroke-width:2.6}
.wave-in{fill:none;stroke:#5d6a73;stroke-width:1.4;stroke-linejoin:round}
.wave-out{fill:none;stroke:#1f6fb5;stroke-width:2.6}
.band-sig{fill:#1f6fb5;fill-opacity:.13}
.band-noise{fill:#c2362b;fill-opacity:.10}
.vline{stroke:#1b2227;stroke-width:1.2;stroke-dasharray:4 4;fill:none}
"""

html = open(SRC, encoding="utf-8").read()
blocks = re.findall(r"<svg\b.*?</svg>", html, flags=re.S)
assert len(blocks) == 3, len(blocks)


TOKENS = {
    "var(--panel)": "#ffffff", "var(--fg)": "#1b2227", "var(--muted)": "#5d6a73",
    "var(--mains)": "#c2362b", "var(--sig)": "#1f6fb5", "var(--pwr)": "#a9650a",
}


def inner(block):
    body = re.sub(r"^<svg\b[^>]*>", "", block, count=1, flags=re.S)
    body = re.sub(r"</svg>\s*$", "", body).replace('href="#', 'xlink:href="#')
    for token, value in TOKENS.items():  # inline attributes cannot use page CSS variables
        body = body.replace(token, value)
    return body


def fill_paths(body):
    # same arithmetic as the page's script
    rnd = lambda i: (lambda x: x - math.floor(x))(math.sin(i * 12.9898) * 43758.5453)
    W, A, T = 500, 36, 0.04
    before, after = [], []
    for i in range(W + 1):
        t = i / W * T
        s = math.sin(2 * math.pi * 50 * t)
        r = (0.16 * math.sin(2 * math.pi * 1150 * t)
             + 0.10 * math.sin(2 * math.pi * 1730 * t + 1)
             + 0.14 * (rnd(i) - 0.5))
        cmd = "L" if i else "M"
        before.append("%s%d %.1f" % (cmd, 40 + i, 132 - A * (s + r)))
        after.append("%s%d %.1f" % (cmd, 40 + i, 316 - A * s))
    fc = 1 / (2 * math.pi * 1000 * 10e-9)
    N = 200
    curve = []
    for k in range(N + 1):
        f = 10 * 10 ** (7 * k / N)
        g = -10 * math.log10(1 + (f / fc) ** 2)
        curve.append("%s%.1f %.1f" % ("L" if k else "M", 660 + 500 * k / N, 70 - g * 3.25))
    body = body.replace('<path id="wave-before" class="wave-in" d=""/>',
                        '<path class="wave-in" d="%s"/>' % " ".join(before))
    body = body.replace('<path id="wave-after" class="wave-out" d=""/>',
                        '<path class="wave-out" d="%s"/>' % " ".join(after))
    body = body.replace('<path id="curve" class="curve" d=""/>',
                        '<path class="curve" d="%s"/>' % " ".join(curve))
    return body


def write(name, body, vb, scale=4):
    x, y, w, h = vb
    svg = (
        '<svg xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink" '
        'viewBox="%g %g %g %g" width="%d" height="%d">'
        "<style>%s</style>"
        '<rect x="-200" y="-200" width="1800" height="1400" fill="#ffffff"/>'
        "%s</svg>" % (x, y, w, h, w * scale, h * scale, CSS, body)
    )
    with open(os.path.join(OUT, name + ".svg"), "w", encoding="utf-8") as fh:
        fh.write(svg)


schematic, ct, filt = (inner(b) for b in blocks)
filt = fill_paths(filt)

write("schematic-full", schematic, (0, 0, 1200, 800), 3)
write("schematic-mains", schematic, (20, 12, 610, 400))
write("schematic-chains", schematic, (40, 380, 680, 400))
write("schematic-power-adc", schematic, (600, 137, 590, 648))
write("ct-clamp", ct, (0, 0, 1000, 440), 3)
write("filter-wave", filt, (20, 20, 540, 360))
write("filter-response", filt, (615, 20, 585, 375))

# sampling diagram: one ADC reading V then I (multiplexed) against both at once (simultaneous)
def sampling_svg():
    def wave(base, amp, lag):
        pts = []
        for x in range(30, 671, 4):
            y = base - amp * math.sin(2 * math.pi * (x - 30) / 320 - lag)
            pts.append("%s%d %.1f" % ("L" if pts else "M", x, y))
        return " ".join(pts)

    def y_at(base, amp, lag, x):
        return base - amp * math.sin(2 * math.pi * (x - 30) / 320 - lag)

    out = []
    for base, title, gap in ((125, "Multiplexed: V first, then I a moment later (ESP32 internal ADC)", 34),
                             (335, "Simultaneous: V and I at the same instant (ADS131M04)", 0)):
        out.append('<text x="20" y="%d" font-size="18" font-weight="700" fill="#1b2227">%s</text>' % (base - 97, title))
        out.append('<line x1="30" y1="%d" x2="670" y2="%d" stroke="#cfd6db" stroke-width="1.5"/>' % (base, base))
        out.append('<path d="%s" fill="none" stroke="#1f6fb5" stroke-width="3.5"/>' % wave(base, 55, 0))
        out.append('<path d="%s" fill="none" stroke="#c2362b" stroke-width="3.5"/>' % wave(base, 40, 0.7))
        xv, xi = 90, 90 + gap
        for x in {xv, xi}:
            out.append('<line x1="%d" y1="%d" x2="%d" y2="%d" stroke="#5d6a73" stroke-width="1.5" stroke-dasharray="5 4"/>'
                       % (x, base - 70, x, base + 62))
        out.append('<circle cx="%d" cy="%.1f" r="7" fill="#1f6fb5"/>' % (xv, y_at(base, 55, 0, xv)))
        out.append('<circle cx="%d" cy="%.1f" r="7" fill="#c2362b"/>' % (xi, y_at(base, 40, 0.7, xi)))
        if gap:
            out.append('<path d="M%d %d H%d M%d %d v12 M%d %d v12" fill="none" stroke="#1b2227" stroke-width="2.5"/>'
                       % (xv, base + 80, xi, xv, base + 74, xi, base + 74))
            out.append('<text x="%d" y="%d" font-size="17" fill="#1b2227">gap Δt (drawn much larger than real)</text>' % (xi + 14, base + 84))
        else:
            out.append('<text x="%d" y="%d" font-size="17" fill="#1b2227">no gap</text>' % (xv + 14, base + 84))
    out.append('<text x="676" y="82" font-size="16" fill="#1f6fb5" text-anchor="end" font-weight="700">voltage</text>')
    out.append('<text x="676" y="102" font-size="16" fill="#c2362b" text-anchor="end" font-weight="700">current</text>')
    return ('<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 700 440" width="2800" height="1760" '
            'font-family="Liberation Sans, Arial, sans-serif"><rect width="700" height="440" fill="#ffffff"/>%s</svg>'
            % "".join(out))


with open(os.path.join(OUT, "sampling.svg"), "w", encoding="utf-8") as fh:
    fh.write(sampling_svg())

# title-slide motif: voltage and a lagging current, transparent background
pts_v, pts_i = [], []
for i in range(0, 801):
    x = i
    th = i / 800 * 4 * math.pi
    pts_v.append("%s%d %.1f" % ("L" if i else "M", x, 150 - 110 * math.sin(th)))
    pts_i.append("%s%d %.1f" % ("L" if i else "M", x, 150 - 70 * math.sin(th - 0.9)))
waves = (
    '<svg xmlns="http://www.w3.org/2000/svg" viewBox="-10 0 840 300" width="2520" height="900">'
    '<line x1="0" y1="150" x2="800" y2="150" stroke="#5b6b79" stroke-width="1.5"/>'
    '<path d="%s" fill="none" stroke="#66b5ff" stroke-width="5" stroke-linecap="round"/>'
    '<path d="%s" fill="none" stroke="#ff7d6e" stroke-width="5" stroke-linecap="round"/>'
    "</svg>" % (" ".join(pts_v), " ".join(pts_i))
)
with open(os.path.join(OUT, "waves.svg"), "w", encoding="utf-8") as fh:
    fh.write(waves)
print("wrote", sorted(os.listdir(OUT)))

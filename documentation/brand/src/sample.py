"""Builds sample/web-and-mobile.html: the finished identity on a web page and a phone screen.

Run:  python3 sample.py     All readings, prices and menu entries are samples.
"""
from pathlib import Path

from identity import ARTS, BRASS, DATA, FONT_CSS, NAVY, PAPER, QUIET, TINT, WHITE

OUT = Path(__file__).resolve().parent.parent / "sample/web-and-mobile.html"

# the logo takes its colours from CSS, so one piece of artwork serves dark and light surfaces
LOGO = (ARTS["logo"].svg("on-navy", cls="logo").replace(f'fill="{WHITE}"', 'fill="currentColor"')
        .replace(f'fill="{BRASS}"', 'class="dot"'))


def n(words):
    """A number inside running text: Roboto."""
    return f'<span class="n">{words}</span>'


def row(state, name, watts, note):
    return (f'<div class="row"><i style="background:{DATA[state]}"></i><div><b>{name}</b><small>{note}</small></div>'
            f'<span class="n v">{watts}</span></div>')


ROWS = (row("High", "Water heater", "1,050 W", "High use") + row("Normal", "Refrigerator", "120 W", "Normal")
        + row("Other", "Other", "78 W", "Not identified"))
DAYS = [("Mon", 5.8), ("Tue", 6.9), ("Wed", 5.2), ("Thu", 7.4), ("Fri", 6.1), ("Sat", 8.0), ("Sun", 6.4)]
BARS = "".join(f'<div class="{"today" if d == "Sun" else ""}"><span class="n">{v}</span><i style="height:{v * 11:.0f}px"></i><small>{d}</small></div>'
               for d, v in DAYS)
TOTAL = sum(v for _, v in DAYS)

WEB = f"""
<div class="web">
 <div class="top">
  <header class="pad nav">{LOGO}<ul><li>Product</li><li>How it works</li><li>Specifications</li><li>Team</li></ul></header>
  <div class="pad hero">
   <div><p class="eyebrow">PowerLenz · Home energy monitor</p>
    <h1 class="h">See where your electricity goes.</h1>
    <p class="lede">PowerLenz measures your home's supply at one point and aims to show which appliances are using it. Designed for {n("230 V")}, single-phase homes in India.</p>
    <span class="cta">See how it works</span></div>
   <div class="panel"><p class="label"><span class="live"></span>Using now · sample</p><div class="dh big">1,248 W</div><p>Today {n("6.40 kWh")} · <b class="n">₹48.60</b></p>{ROWS}</div>
  </div>
 </div>
 <div class="pad white"><h2 class="h">From one clamp to a clear picture</h2>
  <div class="cols">
   <div><span class="step n">1</span><h3 class="h">Sense the supply</h3><p>A current transformer and a voltage sensor read the incoming line.</p></div>
   <div><span class="step n">2</span><h3 class="h">Sample and compute</h3><p>An ADS131M04 converter and an ESP32-S3 turn the signals into power readings.</p></div>
   <div><span class="step n">3</span><h3 class="h">Show the usage</h3><p>Readings go to the cloud, where appliance patterns are identified and displayed.</p></div>
  </div></div>
 <div class="pad"><h2 class="h">Your week at a glance</h2>
  <div class="split">
   <div><div class="dh mid">{TOTAL:.1f} kWh</div><p>This week you used {n(f"{TOTAL:.1f} kWh")}, with the highest day on Saturday at {n("8.0 kWh")}. The estimated cost is <b class="n">₹348.00</b>.</p>
    <table><tr><td>Estimated bill this month</td><td class="n">₹1,420.00</td></tr><tr><td>Average per day</td><td class="n">6.54 kWh</td></tr><tr><td>Supply voltage</td><td class="n">230 V</td></tr></table></div>
   <div class="chartbox chart">{BARS}</div>
  </div></div>
 <div class="band"><div><h2 class="h">Know before the bill arrives.</h2><p>Follow your usage from your phone.</p></div><span class="cta solid">View specifications</span></div>
 <footer class="pad">{LOGO}<span>PowerLenz by Sixteen Amps</span></footer>
</div>"""

PHONE = f"""
<div class="phone">
 <div class="top apphead">
  <div class="status"><span class="n">9:41</span><span>Sample data</span></div>
  {LOGO}
  <div class="reading"><p class="label"><span class="live"></span>Using now</p><div class="dh big">1,248 W</div><p>Today {n("6.40 kWh")} · <b class="n">₹48.60</b></p></div>
 </div>
 <div class="app">
  <div class="seg"><span>Day</span><span class="on">Week</span><span>Month</span></div>
  <div class="chartbox chart">{BARS}</div>
  <div class="tiles"><div><small>This week</small><div class="dh">{TOTAL:.1f} kWh</div></div><div><small>This month, estimated</small><div class="n price">₹1,420</div></div></div>
  <h3 class="h">Appliances</h3><div class="box">{ROWS}</div>
  <div class="tip"><b>Saving tip</b><p>Running your water heater {n("15 minutes")} less each day could lower your bill.</p></div>
  <span class="cta solid">View usage</span>
 </div>
 <div class="tabs"><span class="on">Home</span><span>History</span><span>Alerts</span><span>Settings</span></div>
</div>"""

CSS = f"""
*{{box-sizing:border-box;margin:0;padding:0}}
:root{{--navy:{NAVY};--brass:{BRASS};--tint:{TINT};--paper:{PAPER};--quiet:{QUIET}}}
body{{background:#d9d7d0;color:var(--navy);font:400 16px/1.5 'IBM Plex Sans',sans-serif;font-variant-numeric:tabular-nums lining-nums}}
.h{{font-family:'Bricolage Grotesque';font-weight:700;letter-spacing:-.02em;line-height:1.12}}
.dh{{font-family:'IBM Plex Sans';font-weight:700;letter-spacing:-.01em;line-height:1.15}}
.n{{font-family:'Roboto';font-weight:500}}b.n{{font-weight:700}}
.bar{{position:sticky;top:0;z-index:5;background:#101114;color:#fff;padding:10px 16px;display:flex;gap:10px 28px;flex-wrap:wrap;align-items:center;font-size:14px}}
.set{{display:flex;gap:8px;align-items:center;flex-wrap:wrap}}
button{{font:600 14px 'IBM Plex Sans';cursor:pointer}}
.chip{{min-height:36px;padding:0 14px;border-radius:20px;border:1px solid #666;background:#23252a;color:#fff}}.chip[aria-pressed=true]{{background:#fff;color:#101114}}
button:focus-visible{{outline:3px solid var(--brass);outline-offset:3px}}
.sw{{position:relative;width:32px;height:32px;border-radius:9px;border:1px solid #fff8;background:var(--s)}}
.sw span{{position:absolute;left:50%;top:calc(100% + 8px);transform:translateX(-50%);background:#101114;color:#fff;border:1px solid #fff4;border-radius:7px;padding:4px 8px;font:500 14px 'Roboto';white-space:nowrap;visibility:hidden}}
.sw:hover span,.sw:focus span{{visibility:visible}}
.key{{display:none;gap:8px;flex-wrap:wrap}}.key span{{padding:3px 9px;border-radius:6px;color:#101114}}.marked .key{{display:flex}}
.marked .h,.k1{{background:#ffd9a8!important;color:#101114!important}}.marked .dh,.k2{{background:#bfeccc!important;color:#101114!important}}.marked .n,.k3{{background:#e5c8ff!important;color:#101114!important}}
.stage{{max-width:1500px;margin:auto;padding:24px 16px 56px;display:grid;grid-template-columns:minmax(0,1fr) 390px;gap:28px;align-items:start}}
.cap{{font-weight:600;margin-bottom:10px}}
.logo{{width:200px;height:auto;display:block;color:#fff}}.logo .dot{{fill:var(--brass)}}
.web{{background:var(--paper);border-radius:14px;overflow:hidden;container-type:inline-size}}
.pad{{padding:30px 6cqw}}.white{{background:#fff}}
.top{{background:var(--navy);color:#fff}}
.light .top{{background:var(--paper);color:var(--navy)}}.light .top .logo{{color:var(--navy)}}.light .top .logo .dot{{fill:var(--navy)}}
.nav{{display:flex;justify-content:space-between;align-items:center;gap:16px}}.nav ul{{display:flex;gap:22px;list-style:none;font-size:15px;font-weight:500}}
.hero{{display:grid;grid-template-columns:1.2fr 1fr;gap:5cqw;align-items:center;padding-bottom:48px}}
.eyebrow{{font-weight:600;font-size:14px;color:var(--brass)}}.light .eyebrow{{color:var(--navy)}}
h1.h{{font-size:clamp(34px,6.4cqw,66px);margin:12px 0 18px;text-wrap:balance}}
.lede{{font-size:19px;margin-bottom:24px;max-width:50ch}}
.cta{{display:inline-block;background:var(--brass);color:var(--navy);border-radius:8px;padding:12px 22px;font-weight:700;text-align:center}}
.light .top .cta,.cta.solid{{background:var(--navy);color:#fff}}
.panel{{background:#fff;color:var(--navy);border-radius:16px;padding:22px}}.light .panel{{background:var(--navy);color:#fff}}
.label{{font-size:14px;font-weight:600;display:flex;align-items:center;gap:8px}}
.live{{width:10px;height:10px;border-radius:50%;background:var(--brass)}}
.big{{font-size:60px}}.mid{{font-size:44px;margin-bottom:8px}}
.panel>p+.row{{margin-top:14px}}
.row{{display:flex;align-items:center;gap:12px;border-top:1px solid color-mix(in srgb,currentColor 16%,transparent);min-height:62px}}
.row i{{width:11px;height:11px;border-radius:50%;flex:none}}.row>div{{flex:1}}.row b{{display:block;font-weight:600}}.row small{{font-size:14px;opacity:.78}}
.row .v{{font-size:19px;font-weight:700}}
h2.h{{font-size:clamp(26px,3.8cqw,40px);margin-bottom:20px}}h3.h{{font-size:21px;margin-bottom:6px}}
.cols{{display:grid;grid-template-columns:repeat(3,1fr);gap:26px}}
.step{{display:inline-flex;width:34px;height:34px;border-radius:50%;background:var(--tint);border:1.5px solid var(--brass);align-items:center;justify-content:center;font-weight:700;margin-bottom:12px}}
.split{{display:grid;grid-template-columns:1fr 1fr;gap:5cqw;align-items:end}}
table{{width:100%;border-collapse:collapse;margin-top:18px}}td{{border-bottom:1px solid #14213d29;padding:10px 0}}td.n{{text-align:right;font-weight:700;font-size:17px}}
.chartbox{{background:var(--navy);color:#fff;border-radius:16px;padding:18px 16px 12px}}
.chart{{display:flex;align-items:flex-end;justify-content:space-between;gap:8px}}
.chart>div{{flex:1;display:flex;flex-direction:column;align-items:center;gap:5px}}.chart i{{width:100%;background:var(--quiet);border-radius:5px 5px 0 0}}
.chart .today i{{background:var(--brass)}}.chart .today span,.chart .today small{{color:var(--brass);font-weight:700}}
.chart .n{{font-size:14px}}.chart small{{font-size:14px;font-weight:500}}
.band{{background:var(--tint);padding:36px 6cqw;display:flex;justify-content:space-between;align-items:center;gap:20px;flex-wrap:wrap}}.band h2.h{{margin-bottom:4px}}
footer{{background:var(--navy);color:#fff;display:flex;justify-content:space-between;gap:16px;flex-wrap:wrap;align-items:center}}
.phone{{width:100%;max-width:390px;margin:auto;background:var(--paper);border:10px solid #101114;border-radius:44px;overflow:hidden}}
.apphead{{padding:12px 20px 22px}}.status{{display:flex;justify-content:space-between;font-size:14px;font-weight:600;margin-bottom:16px}}
.apphead .logo{{width:168px}}.reading{{margin-top:22px}}
.app{{padding:14px 16px 20px;display:flex;flex-direction:column;gap:12px}}.app h3.h{{font-size:20px;margin:8px 0 -4px}}
.seg{{display:flex;background:#fff;border-radius:10px;padding:3px}}.seg span{{flex:1;text-align:center;padding:6px;border-radius:8px;font-weight:600;font-size:14px}}.seg .on{{background:var(--navy);color:#fff}}
.tiles{{display:grid;grid-template-columns:1fr 1fr;gap:12px}}.tiles>div{{background:#fff;border-radius:14px;padding:14px;display:flex;flex-direction:column;justify-content:space-between;gap:6px}}
.tiles small{{font-size:14px;font-weight:500}}.tiles .dh,.tiles .price{{font-size:25px;line-height:1.15}}.price{{font-weight:700}}
.box{{background:#fff;border-radius:14px;padding:2px 14px}}.box .row:first-child{{border-top:0}}
.tip{{background:var(--tint);border-left:4px solid var(--brass);border-radius:14px;padding:14px}}
.tabs{{display:flex;justify-content:space-around;background:#fff;border-top:1px solid #14213d18;padding:12px 8px 20px;font-size:14px;font-weight:500}}.tabs span{{padding:5px 12px;border-radius:20px}}.tabs .on{{background:var(--navy);color:#fff;font-weight:700}}
@container (max-width:700px){{.hero,.cols,.split{{grid-template-columns:1fr}}.nav ul{{display:none}}}}
@media(max-width:1000px){{.stage{{grid-template-columns:1fr}}.phone-col{{order:-1}}}}
@media(max-width:460px){{.stage{{padding:16px 8px 40px}}.phone{{border-width:0;border-radius:18px}}}}
"""

PALETTE = "".join(f'<button class="sw" style="--s:{h}" aria-label="{name} {h}"><span>{h}</span></button>' for name, h in
                  (("Navy", NAVY), ("Brass", BRASS), ("Brass Tint", TINT), ("Paper", PAPER), ("White", WHITE), *DATA.items()))

PAGE = f"""<!doctype html><html lang="en"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1"><title>PowerLenz Web and Mobile</title>
<style>{FONT_CSS}</style><style>{CSS}</style></head><body>
<div class="bar">
 <div class="set"><span>Header</span><button class="chip" data-head="dark">Navy</button><button class="chip" data-head="light">Light</button></div>
 <div class="set">{PALETTE}</div>
 <button class="chip" id="mark" aria-pressed="false">Show which font is where</button>
 <div class="key"><span class="k1">Bricolage Grotesque: headings</span><span class="k2">IBM Plex Sans Bold: data headings</span><span class="k3">Roboto: numbers and prices</span><span style="color:#fff">Everything else: IBM Plex Sans</span></div>
</div>
<div class="stage"><div><p class="cap">Web page</p>{WEB}</div><div class="phone-col"><p class="cap">Mobile screen</p>{PHONE}</div></div>
<script>
const q=new URLSearchParams(location.search),mark=document.getElementById("mark");
function head(v){{document.body.classList.toggle("light",v=="light");document.querySelectorAll("[data-head]").forEach(b=>b.setAttribute("aria-pressed",b.dataset.head==v))}}
function marked(v){{document.body.classList.toggle("marked",v);mark.setAttribute("aria-pressed",v)}}
document.querySelectorAll("[data-head]").forEach(b=>b.onclick=()=>head(b.dataset.head));
mark.onclick=()=>marked(!document.body.classList.contains("marked"));
head(q.get("head")||"dark");marked(q.has("marked"));
</script></body></html>"""

if __name__ == "__main__":
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(PAGE)
    print(OUT, f"{OUT.stat().st_size / 1024:.0f} KB")

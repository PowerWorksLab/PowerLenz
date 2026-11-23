"""Autoroute powerlenz.kicad_pcb with Freerouting in two separate runs, then merge them.

  low-voltage run: signals 0.25 mm, power 0.5 mm, 0.2 mm clearance, GND pour on the back copper
  mains run:       only L_IN, L_FUSED, N, ZA_P, ZP1, ZP2; 0.8 mm tracks, 3 mm clearance (the 'Mains' net class in the project)

DRAFT: the mains values are a starting point (about IEC 60664-1 basic creepage for 250 V, pollution degree 2, plus margin).
A person with mains-design experience must review them, and the slots, before any board is built.

Needs Java and the Freerouting jar (default: newest ~/tools/freerouting*.jar, not part of the repo).
Run from hardware/kicad after tools/build_pcb.py:  python3 tools/route.py [--jar PATH] [--passes N]
Any tracks already on the board are removed first, so the script can be re-run after a placement change.
"""
import argparse
import glob
import os
import re
import shutil
import subprocess
import sys
import tempfile

import pcbnew

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from sexp import parse, dump

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.join(HERE, "..")
PCB = os.path.join(ROOT, "powerlenz.kicad_pcb")

MAINS_NETS = ["L_IN", "L_FUSED", "N", "ZA_P", "ZP1", "ZP2"]
POWER_NETS = ["+5V", "+3V3A", "GND"]
POUR_X0, POUR_X1 = 58.0, 152.0   # low-voltage side only, right of the isolation line at x = 56 mm


def quote(n):
    return '"%s"' % n if re.search(r"[()\s]", n) else n


def prepare_dsn(text, keep, classes):
    """Keep only the nets in `keep` and replace the class section with `classes` = [(name, nets, width_um, clearance_um)]."""
    names = [n.strip('"') for n in re.findall(r'\n    \(net ("[^"]+"|[^\s()]+)\n      \(pins', text)]
    keep = [n for n in names if keep(n)]
    classes = classes(keep)
    for n in names:
        if n not in keep:
            text = re.sub(r'\n    \(net %s\n      \(pins [^)]*\)\n    \)' % re.escape(quote(n)), "", text)
    cls = lambda name, ns, w, c: ("    (class %s %s\n      (circuit\n        (use_via \"Via[0-1]_600:300_um\")\n      )\n"
                                  "      (rule\n        (width %d)\n        (clearance %d)\n      )\n    )"
                                  % (name, " ".join(quote(n) for n in ns), w, c))
    new = "\n".join(cls(*c) for c in classes)
    text = re.sub(r"    \(class kicad_default .*?\n    \)\n(?=  \))", new + "\n", text, flags=re.S)
    return text


def fresh_board():
    b = pcbnew.LoadBoard(PCB)
    for t in list(b.GetTracks()):
        b.Remove(t)
    for z in list(b.Zones()):
        b.Remove(z)
    return b


def run_stage(board, keep, classes, jar, passes, label):
    with tempfile.TemporaryDirectory() as d:
        dsn, ses = os.path.join(d, "pl.dsn"), os.path.join(d, "pl.ses")
        pcbnew.ExportSpecctraDSN(board, dsn)
        text = prepare_dsn(open(dsn, encoding="utf-8").read(), keep, classes)
        open(dsn, "w", encoding="utf-8").write(text)
        print("%s: routing" % label)
        r = subprocess.run(["java", "-Djava.awt.headless=true", "-jar", jar, "-de", dsn, "-do", ses, "-mp", str(passes)],
                           capture_output=True, text=True, timeout=1800)
        score = [l for l in r.stdout.splitlines() if "incomplete connections" in l]
        print("  ", score[-1][-160:] if score else r.stdout[-300:] + r.stderr[-300:])
        if not os.path.exists(ses):
            sys.exit("Freerouting wrote no session file")
        if not pcbnew.ImportSpecctraSES(board, ses):
            sys.exit("could not import the session file")


def stage_lv(out, jar, passes):
    board = fresh_board()
    run_stage(board, lambda n: n not in MAINS_NETS and not n.startswith("unconnected-"),
              lambda ns: [("kicad_default", [n for n in ns if n not in POWER_NETS], 250, 200),
                          ("power", [n for n in POWER_NETS if n in ns], 500, 200)], jar, passes, "low voltage")
    board.Save(out)


def stage_mains(out, jar, passes):
    board = fresh_board()
    run_stage(board, lambda n: n in MAINS_NETS, lambda ns: [("mains", ns, 800, 3000)], jar, passes, "mains")
    board.Save(out)


def stage_finish(path):
    board = pcbnew.LoadBoard(path)
    z = pcbnew.ZONE(board)
    z.SetLayer(pcbnew.B_Cu)
    z.SetNet(board.FindNet("GND"))
    z.SetLocalClearance(pcbnew.FromMM(0.4))
    z.SetPadConnection(pcbnew.ZONE_CONNECTION_THERMAL)
    ol = z.Outline()
    ol.NewOutline()
    for x, y in [(POUR_X0, 2), (POUR_X1, 2), (POUR_X1, 84), (POUR_X0, 84)]:
        ol.Append(pcbnew.FromMM(x), pcbnew.FromMM(y))
    board.Add(z)
    pcbnew.ZONE_FILLER(board).Fill(board.Zones())
    board.Save(path)
    print("saved", os.path.abspath(path), "-", len(list(board.GetTracks())), "track segments and vias")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--jar", default=(sorted(glob.glob(os.path.expanduser("~/tools/freerouting*.jar"))) or ["freerouting.jar"])[-1])
    ap.add_argument("--passes", type=int, default=30)
    ap.add_argument("--skip-mains", action="store_true", help="route the low-voltage side only")
    ap.add_argument("--stage", choices=["lv", "mains", "finish"], help="internal: each stage runs in its own process")
    ap.add_argument("--out")
    a = ap.parse_args()
    if a.stage == "lv":
        return stage_lv(a.out, a.jar, a.passes)
    if a.stage == "mains":
        return stage_mains(a.out, a.jar, a.passes)
    if a.stage == "finish":
        return stage_finish(a.out)
    # the Python bindings cannot load a second board in one process, so every stage is a separate process
    with tempfile.TemporaryDirectory() as d:
        me = [sys.executable, os.path.abspath(__file__), "--jar", a.jar, "--passes", str(a.passes)]
        lv, mn = os.path.join(d, "lv.kicad_pcb"), os.path.join(d, "mains.kicad_pcb")
        subprocess.run(me + ["--stage", "lv", "--out", lv], check=True)
        if not a.skip_mains:
            subprocess.run(me + ["--stage", "mains", "--out", mn], check=True)
            base = parse(open(lv, encoding="utf-8").read())
            extra = [i for i in parse(open(mn, encoding="utf-8").read()) if isinstance(i, list) and i and i[0] in ("segment", "via")]
            base.extend(extra)
            open(lv, "w", encoding="utf-8").write(dump(base, 0) + "\n")
            print("merged %d mains track items" % len(extra))
        subprocess.run(me + ["--stage", "finish", "--out", lv], check=True)
        shutil.copyfile(lv, PCB)
    print("wrote", os.path.abspath(PCB))


if __name__ == "__main__":
    main()

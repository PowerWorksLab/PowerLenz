"""Autoroute the LOW-VOLTAGE side of powerlenz.kicad_pcb with Freerouting. Mains nets are left unrouted on purpose.

Needs Java and the Freerouting jar (default: newest ~/tools/freerouting*.jar, not part of the repo).
Run from hardware/kicad:  python3 tools/route.py [--jar PATH] [--passes N]
Steps: export Specctra DSN -> drop mains and unconnected nets -> run Freerouting -> import the session -> add a GND pour.
Any tracks already on the board are removed first, so the script can be re-run after a placement change.
"""
import argparse
import glob
import os
import re
import subprocess
import sys
import tempfile

import pcbnew

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.join(HERE, "..")
PCB = os.path.join(ROOT, "powerlenz.kicad_pcb")

# Nets that carry (or sit directly on) 230 V. They are NOT routed by this script: a person with mains-design
# experience must set creepage, clearance and the isolation slot first.
MAINS_NETS = {"L_IN", "L_FUSED", "N", "ZA_P", "ZP1", "ZP2"}
POWER_NETS = ["+5V", "+3V3A", "GND"]
TRACK_UM, POWER_UM, CLEAR_UM = 250, 500, 200
POUR_X0, POUR_X1 = 58.0, 152.0   # low-voltage side only, right of the isolation line at x = 56 mm


def prepare_dsn(text):
    drop = set(MAINS_NETS)
    for m in re.finditer(r'\(net "?(unconnected-[^"\n]*?)"?\n', text):
        drop.add(m.group(1))

    def quote(n):
        return '"%s"' % n if re.search(r"[()\s]", n) else n

    for n in drop:  # remove the net blocks
        text = re.sub(r'\n    \(net %s\n      \(pins [^\n]*\)\n    \)' % re.escape(quote(n)), "", text)
    # rebuild the class list: one default class for signals, one wider class for power
    nets = re.findall(r'\n    \(net ("[^"]+"|[^\s()]+)\n      \(pins', text)
    nets = [n.strip('"') for n in nets]
    sig = [n for n in nets if n not in POWER_NETS]
    pwr = [n for n in POWER_NETS if n in nets]
    cls = lambda name, ns, w: ("    (class %s %s\n      (circuit\n        (use_via \"Via[0-1]_600:300_um\")\n      )\n"
                               "      (rule\n        (width %d)\n        (clearance %d)\n      )\n    )"
                               % (name, " ".join(quote(n) for n in ns), w, CLEAR_UM))
    new = cls("kicad_default", sig, TRACK_UM) + "\n" + cls("power", pwr, POWER_UM)
    text = re.sub(r"    \(class kicad_default .*?\n    \)\n(?=  \))", new + "\n", text, flags=re.S)
    return text, sorted(drop), nets


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--jar", default=(sorted(glob.glob(os.path.expanduser("~/tools/freerouting*.jar"))) or ["freerouting.jar"])[-1])
    ap.add_argument("--passes", type=int, default=30)
    a = ap.parse_args()
    board = pcbnew.LoadBoard(PCB)
    for t in list(board.GetTracks()):
        board.Remove(t)
    for z in list(board.Zones()):
        board.Remove(z)
    with tempfile.TemporaryDirectory() as d:
        dsn, ses = os.path.join(d, "pl.dsn"), os.path.join(d, "pl.ses")
        pcbnew.ExportSpecctraDSN(board, dsn)
        text, dropped, routed = prepare_dsn(open(dsn, encoding="utf-8").read())
        open(dsn, "w", encoding="utf-8").write(text)
        print("not routed (mains / unconnected): %d nets, e.g. %s" % (len(dropped), ", ".join(sorted(MAINS_NETS))))
        print("routing %d nets" % len(routed))
        cmd = ["java", "-Djava.awt.headless=true", "-jar", a.jar, "-de", dsn, "-do", ses, "-mp", str(a.passes)]
        r = subprocess.run(cmd, capture_output=True, text=True, timeout=1800)
        print(r.stdout[-1500:], r.stderr[-800:])
        if not os.path.exists(ses):
            sys.exit("Freerouting wrote no session file")
        if not pcbnew.ImportSpecctraSES(board, ses):
            sys.exit("could not import the session file")
    # GND pour on the back copper, low-voltage side only
    gnd = board.FindNet("GND")
    z = pcbnew.ZONE(board)
    z.SetLayer(pcbnew.B_Cu)
    z.SetNet(gnd)
    z.SetLocalClearance(pcbnew.FromMM(0.4))
    z.SetPadConnection(pcbnew.ZONE_CONNECTION_THERMAL)
    ol = z.Outline()
    ol.NewOutline()
    for x, y in [(POUR_X0, 2), (POUR_X1, 2), (POUR_X1, 84), (POUR_X0, 84)]:
        ol.Append(pcbnew.FromMM(x), pcbnew.FromMM(y))
    board.Add(z)
    pcbnew.ZONE_FILLER(board).Fill(board.Zones())
    board.Save(PCB)
    print("saved", os.path.abspath(PCB), "-", len(list(board.GetTracks())), "track segments and vias")


if __name__ == "__main__":
    main()

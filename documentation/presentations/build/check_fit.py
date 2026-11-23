"""Estimate text overflow, off-slide shapes and overlapping text boxes in a .pptx.
Uses the metric-compatible fonts installed here (Carlito = Calibri, Caladea = Cambria,
Liberation Mono = Courier New). Run with the venv python: .venv/bin/python check_fit.py deck.pptx
"""
import subprocess
import sys

from PIL import ImageFont
from pptx import Presentation
from pptx.util import Emu

EMU = 914400.0
SLIDE_W, SLIDE_H = 13.333, 7.5
_cache = {}


def font_file(family, bold):
    key = (family, bold)
    if key not in _cache:
        pat = "%s:%s" % (family, "bold" if bold else "regular")
        _cache[key] = subprocess.run(["fc-match", "-f", "%{file}", pat], capture_output=True, text=True).stdout
    return _cache[key]


def width_in(text, family, size_pt, bold):
    f = ImageFont.truetype(font_file(family, bold), int(size_pt * 10))
    return f.getlength(text) / 10.0 / 72.0


def wrap_lines(text, family, size_pt, bold, avail_w):
    lines = 0
    for hard in text.split("\n") or [""]:
        words = hard.split(" ")
        cur = ""
        n = 1
        for w in words:
            trial = (cur + " " + w) if cur else w
            if width_in(trial, family, size_pt, bold) <= avail_w or not cur:
                cur = trial
            else:
                n += 1
                cur = w
        lines += n
    return lines


def frame_need(tf, avail_w, is_title):
    need = 0.0
    for p in tf.paragraphs:
        runs = [r for r in p.runs if r.text]
        if not runs:
            continue
        size = max((r.font.size.pt if r.font.size else (32 if is_title else 18)) for r in runs)
        name = runs[0].font.name or ("Cambria" if is_title else "Calibri")
        bold = any(r.font.bold for r in runs) or is_title
        text = "".join(r.text for r in runs)
        indent = 0.3125 if p._p.pPr is not None and p._p.pPr.find(
            "{http://schemas.openxmlformats.org/drawingml/2006/main}buChar") is not None else 0.0
        n = wrap_lines(text, name, size, bold, max(avail_w - indent, 0.2))
        need += n * size * 1.2 / 72.0
        if p.space_after is not None:
            need += p.space_after.pt / 72.0
    return need


def main(path):
    prs = Presentation(path)
    problems = 0
    for si, slide in enumerate(prs.slides, 1):
        boxes = []
        for sh in slide.shapes:
            l, t, w, h = (sh.left or 0) / EMU, (sh.top or 0) / EMU, (sh.width or 0) / EMU, (sh.height or 0) / EMU
            if l < -0.01 or t < -0.01 or l + w > SLIDE_W + 0.01 or t + h > SLIDE_H + 0.01:
                print("slide %d: OFF-SLIDE %s (%.2f,%.2f %.2fx%.2f)" % (si, sh.name, l, t, w, h)); problems += 1
            if sh.has_text_frame and sh.text_frame.text.strip():
                tf = sh.text_frame
                ml, mr = (tf.margin_left or 0) / EMU, (tf.margin_right or 0) / EMU
                mt, mb = (tf.margin_top or 0) / EMU, (tf.margin_bottom or 0) / EMU
                is_title = sh.is_placeholder and "title" in sh.name.lower()
                need = frame_need(tf, w - ml - mr, is_title)
                avail = h - mt - mb
                tag = "OVERFLOW" if need > avail * 1.02 else None
                if tag:
                    print("slide %d: %s %.2f in needed vs %.2f in: %r" % (si, tag, need, avail, tf.text[:60])); problems += 1
                if not (sh.is_placeholder and is_title):
                    boxes.append((sh.name, l, t, w, h, tf.text[:30]))
            if sh.has_table if hasattr(sh, "has_table") else False:
                tbl = sh.table
                total = 0.0
                for ri, row in enumerate(tbl.rows):
                    rh = row.height / EMU
                    need_row = 0.0
                    for ci, cell in enumerate(row.cells):
                        cw = tbl.columns[ci].width / EMU
                        avail_w = cw - (cell.margin_left + cell.margin_right) / EMU
                        n = frame_need(cell.text_frame, avail_w, False) + (cell.margin_top + cell.margin_bottom) / EMU
                        need_row = max(need_row, n)
                    if need_row > rh * 1.02:
                        print("slide %d: TABLE row %d grows %.2f -> %.2f in" % (si, ri, rh, need_row)); problems += 1
                    total += max(rh, need_row)
                bottom = t + total
                print("slide %d: table bottom at %.2f in" % (si, bottom))
                if bottom > 7.0:
                    print("slide %d: TABLE runs past 7.0 in" % si); problems += 1
        # overlapping text boxes (shape-with-text cards are separate shapes, so only text frames compare)
        for i in range(len(boxes)):
            for j in range(i + 1, len(boxes)):
                a, b = boxes[i], boxes[j]
                ox = min(a[1] + a[3], b[1] + b[3]) - max(a[1], b[1])
                oy = min(a[2] + a[4], b[2] + b[4]) - max(a[2], b[2])
                if ox > 0.05 and oy > 0.05:
                    print("slide %d: text boxes overlap: %r and %r (%.2f x %.2f in)" % (si, a[5], b[5], ox, oy)); problems += 1
    print("done, %d findings" % problems)


main(sys.argv[1])

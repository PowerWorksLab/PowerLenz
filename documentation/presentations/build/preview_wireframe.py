"""Rough preview of a .pptx without LibreOffice: draws filled shapes, pictures, wrapped text and
tables with PIL, using the installed Calibri/Cambria substitutes. Layout check only, not pixel-exact.
Run: .venv/bin/python preview_wireframe.py deck.pptx outdir
"""
import os
import subprocess
import sys

from PIL import Image, ImageDraw, ImageFont
from pptx import Presentation
from pptx.enum.dml import MSO_THEME_COLOR as T
from pptx.enum.shapes import MSO_SHAPE_TYPE

PX = 100  # pixels per inch
THEME = {
    T.TEXT_1: "1B2227", T.BACKGROUND_1: "FFFFFF", T.TEXT_2: "0E1B26", T.BACKGROUND_2: "EEF3F7",
    T.ACCENT_1: "1F6FB5", T.ACCENT_2: "C2362B", T.ACCENT_3: "A9650A", T.ACCENT_4: "027A8A",
    T.ACCENT_5: "5D6A73", T.ACCENT_6: "9FB0BE",
}
FILES = {}


def ffile(family, bold):
    k = (family, bold)
    if k not in FILES:
        FILES[k] = subprocess.run(["fc-match", "-f", "%{file}", "%s:%s" % (family, "bold" if bold else "regular")],
                                  capture_output=True, text=True).stdout
    return FILES[k]


def font(family, pt, bold):
    return ImageFont.truetype(ffile(family, bold), max(int(pt * PX / 72), 6))


def color_of(fill_or_font_color, default=None):
    try:
        if fill_or_font_color.type is None:
            return default
        tc = fill_or_font_color.theme_color
        if tc in THEME:
            return "#" + THEME[tc]
    except Exception:
        pass
    try:
        return "#" + str(fill_or_font_color.rgb)
    except Exception:
        return default


def draw_frame(d, tf, x, y, w, h, dark, is_title, layout):
    cy = y + (tf.margin_top or 0) / 914400 * PX
    for p in tf.paragraphs:
        runs = [r for r in p.runs if r.text]
        if not runs:
            continue
        r0 = runs[0]
        size = r0.font.size.pt if r0.font.size else (50 if layout == "TITLE" and is_title else 32 if is_title else 18)
        name = r0.font.name or ("Cambria" if is_title else "Calibri")
        bold = bool(r0.font.bold) or is_title
        col = color_of(r0.font.color, "#FFFFFF" if (dark and is_title) else "#1B2227")
        text = "".join(r.text for r in runs)
        f = font(name, size, bold)
        avail = w - ((tf.margin_left or 0) + (tf.margin_right or 0)) / 914400 * PX
        lines, cur = [], ""
        for word in text.split(" "):
            t = (cur + " " + word) if cur else word
            if f.getlength(t) <= avail or not cur:
                cur = t
            else:
                lines.append(cur); cur = word
        lines.append(cur)
        lh = size * 1.2 * PX / 72
        for ln in lines:
            ax = x + (tf.margin_left or 0) / 914400 * PX
            if p.alignment is not None and int(p.alignment) == 2:
                ax = x + (w - f.getlength(ln)) / 2
            d.text((ax, cy), ln, font=f, fill=col)
            cy += lh
        if p.space_after is not None:
            cy += p.space_after.pt * PX / 72


def main(path, outdir):
    os.makedirs(outdir, exist_ok=True)
    prs = Presentation(path)
    for si, slide in enumerate(prs.slides, 1):
        lname = slide.slide_layout.name
        dark = lname in ("TITLE", "CLOSE")
        img = Image.new("RGB", (int(13.333 * PX), int(7.5 * PX)), "#0E1B26" if dark else "#FFFFFF")
        d = ImageDraw.Draw(img)
        for sh in slide.shapes:
            x, y, w, h = [(v or 0) / 914400 * PX for v in (sh.left, sh.top, sh.width, sh.height)]
            if sh.shape_type == MSO_SHAPE_TYPE.PICTURE:
                try:
                    pic = Image.open(__import__("io").BytesIO(sh.image.blob)).convert("RGBA")
                    pic = pic.resize((max(int(w), 1), max(int(h), 1)))
                    img.paste(pic, (int(x), int(y)), pic)
                except Exception:
                    d.rectangle([x, y, x + w, y + h], outline="red")
                continue
            if getattr(sh, "has_table", False) and sh.has_table:
                ty = y
                for row in sh.table.rows:
                    rh = row.height / 914400 * PX
                    tx = x
                    for ci, cell in enumerate(row.cells):
                        cw = sh.table.columns[ci].width / 914400 * PX
                        fc = color_of(cell.fill.fore_color, "#FFFFFF") if cell.fill.type is not None else "#FFFFFF"
                        d.rectangle([tx, ty, tx + cw, ty + rh], fill=fc, outline="#CFD6DB")
                        c0 = cell.text_frame.paragraphs[0].runs[0] if cell.text_frame.paragraphs[0].runs else None
                        if c0 is not None:
                            f = font(c0.font.name or "Calibri", c0.font.size.pt if c0.font.size else 14, bool(c0.font.bold))
                            d.text((tx + 8, ty + rh / 2 - f.size / 2), c0.text, font=f, fill=color_of(c0.font.color, "#1B2227"))
                        tx += cw
                    ty += rh
                continue
            try:
                if sh.fill.type == 1:
                    fc = color_of(sh.fill.fore_color)
                    if fc:
                        if "ellipse" in sh.name.lower() or "badge" in sh.name.lower():
                            d.ellipse([x, y, x + w, y + h], fill=fc)
                        else:
                            d.rounded_rectangle([x, y, x + w, y + h], radius=8, fill=fc)
            except Exception:
                pass
            try:
                if sh.line.fill.type == 1:
                    d.rectangle([x, y, x + w, y + h], outline=color_of(sh.line.color, "#9FB0BE"))
            except Exception:
                pass
            if sh.has_text_frame and sh.text_frame.text.strip():
                is_title = sh.is_placeholder and "title" in sh.name.lower()
                draw_frame(d, sh.text_frame, x, y, w, h, dark, is_title, lname)
        out = os.path.join(outdir, "slide-%02d.png" % si)
        img.save(out)
        print(out)


main(sys.argv[1], sys.argv[2])

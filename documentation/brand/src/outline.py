"""Turns text into SVG path data, so logo files do not depend on the font being present."""
import cairo
import gi
gi.require_version("Pango", "1.0")
gi.require_version("PangoCairo", "1.0")
from gi.repository import Pango, PangoCairo

FAMILY = "IBM Plex Sans"   # SIL Open Font License 1.1; fonts/ttf, see fetch_fonts.py

def outline(text, weight=600, tracking=0.0, size=200, family=FAMILY, italic=False):
    """Returns (path d, (x0, y0, x1, y1)) with the baseline at y = 0."""
    ctx = cairo.Context(cairo.RecordingSurface(cairo.CONTENT_ALPHA, None))
    layout = PangoCairo.create_layout(ctx)
    opts = cairo.FontOptions()
    opts.set_hint_style(cairo.HINT_STYLE_NONE)
    opts.set_hint_metrics(cairo.HINT_METRICS_OFF)
    PangoCairo.context_set_font_options(layout.get_context(), opts)
    fd = Pango.FontDescription()
    fd.set_family(family)
    if italic:
        fd.set_style(Pango.Style.ITALIC)
    fd.set_weight(Pango.Weight(weight))
    fd.set_absolute_size(size * Pango.SCALE)
    layout.set_font_description(fd)
    attrs = Pango.AttrList()
    attrs.insert(Pango.attr_letter_spacing_new(int(tracking * size * Pango.SCALE)))
    layout.set_attributes(attrs)
    layout.set_text(text, -1)
    ctx.move_to(0, -layout.get_baseline() / Pango.SCALE)
    PangoCairo.layout_path(ctx, layout)
    box = ctx.path_extents()
    names = {cairo.PATH_MOVE_TO: "M", cairo.PATH_LINE_TO: "L", cairo.PATH_CURVE_TO: "C", cairo.PATH_CLOSE_PATH: "Z"}
    d = "".join(names[t] + " ".join(f"{v:.2f}" for v in pts) for t, pts in ctx.copy_path())
    return d, box

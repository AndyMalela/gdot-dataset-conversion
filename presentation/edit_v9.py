"""v9 = v8 with only slide 8 (Proposed Approach) replaced by a simpler overall flow:
Data -> Simulation (+ check against GDOT's log, fix-and-retry loop) -> Train & run 7 methods -> Results.
No inner workings of the learner. Every other slide is untouched.
Usage: uv run --no-project --with python-pptx --with lxml python edit_v9.py eSocLab_Midterm-v8.pptx eSocLab_Midterm-v9.pptx"""
import sys
from xml.sax.saxutils import escape
from lxml import etree
from pptx import Presentation
from pptx.util import Inches, Pt
from pptx.dml.color import RGBColor
from pptx.enum.shapes import MSO_SHAPE, MSO_CONNECTOR
from pptx.enum.text import MSO_ANCHOR
from pptx.oxml.ns import qn

SRC, OUT = sys.argv[1:3]
A = "http://schemas.openxmlformats.org/drawingml/2006/main"
NS = f'xmlns:a="{A}"'
RED, TITLE, BLUE, BOX, BLACK, GREY, LIGHT = "A52026", "990000", "1F497D", "4472C4", "000000", "595959", "F2F2F2"
PALERED, PALEBLUE, WHITE = "F8E5E6", "DCE6F2", "FFFFFF"
BF = "Arial"

prs = Presentation(SRC)
s = prs.slides[7]
assert any(sh.name == "Text 1" and sh.text_frame.text == "Proposed Approach" for sh in s.shapes)
for sh in list(s.shapes):
    if sh.name not in ("Text 1", "Slide Number Placeholder 0"):
        sh._element.getparent().remove(sh._element)


def rpr(size, color, bold=False, italic=False):
    return (f'<a:rPr lang="en-US" sz="{int(size * 100)}"{" b=\"1\"" if bold else ""}{" i=\"1\"" if italic else ""} '
            f'dirty="0"><a:solidFill><a:srgbClr val="{color}"/></a:solidFill><a:latin typeface="{BF}"/>'
            f'<a:ea typeface="{BF}"/><a:cs typeface="{BF}"/></a:rPr>')


def para(runs, size, color=BLACK, bold=False, italic=False, align="ctr", before=0):
    if isinstance(runs, str):
        runs = [(runs, {})]
    body = "".join(f'<a:r>{rpr(o.get("size", size), o.get("color", color), o.get("bold", bold), o.get("italic", italic))}'
                   f'<a:t>{escape(t)}</a:t></a:r>' for t, o in runs)
    sp = f'<a:spcBef><a:spcPts val="{int(before * 100)}"/></a:spcBef>' if before else ""
    return (f'<a:p {NS}><a:pPr marL="0" indent="0" algn="{align}">{sp}<a:buNone/></a:pPr>{body}'
            f'<a:endParaRPr lang="en-US" sz="{int(size * 100)}"/></a:p>')


def fill(shape, paras, anchor="t", margin=0.06):
    tf = shape.text_frame
    tf.word_wrap = True
    tf.margin_left = tf.margin_right = Inches(margin)
    tf.margin_top = tf.margin_bottom = Inches(0.03)
    tf.vertical_anchor = {"t": MSO_ANCHOR.TOP, "m": MSO_ANCHOR.MIDDLE}[anchor]
    tb = tf._txBody
    for p in tb.findall(qn("a:p")):
        tb.remove(p)
    for p in paras:
        tb.append(etree.fromstring(p))


def text(x, y, w, h, paras, anchor="t"):
    t = s.shapes.add_textbox(Inches(x), Inches(y), Inches(w), Inches(h))
    fill(t, paras, anchor, 0.0)
    return t


def box(x, y, w, h, fillc=None, line=None, lw=1.5, shape=MSO_SHAPE.ROUNDED_RECTANGLE, paras=None, anchor="m"):
    b = s.shapes.add_shape(shape, Inches(x), Inches(y), Inches(w), Inches(h))
    st = b._element.find(qn("p:style"))
    if st is not None:
        b._element.remove(st)
    if shape == MSO_SHAPE.ROUNDED_RECTANGLE:
        b.adjustments[0] = 0.07
    if fillc:
        b.fill.solid()
        b.fill.fore_color.rgb = RGBColor.from_string(fillc)
    else:
        b.fill.background()
    if line:
        b.line.color.rgb = RGBColor.from_string(line)
        b.line.width = Pt(lw)
    else:
        b.line.fill.background()
    if paras:
        fill(b, paras, anchor)
    return b


def arrow(x1, y1, x2, y2, color="404040", w=2.25, head=True):
    c = s.shapes.add_connector(MSO_CONNECTOR.STRAIGHT, Inches(x1), Inches(y1), Inches(x2), Inches(y2))
    st = c._element.find(qn("p:style"))
    if st is not None:
        c._element.remove(st)
    c.line.color.rgb = RGBColor.from_string(color)
    c.line.width = Pt(w)
    if head:
        c.line._get_or_add_ln().append(etree.fromstring(f'<a:tailEnd {NS} type="triangle" w="med" len="med"/>'))
    return c


# four main boxes, left to right
X0, BW, GAP, Y, H = 0.75, 1.95, 0.33, 1.45, 2.75
steps = [
    ("1", "Data", ["GDOT ATSPM", "5-min counts", "timing plans", "controller log", "detector layout"],
     WHITE, BOX, BLUE),
    ("2", "Simulation", ["SUMO", "signal 137 + next signal 138", "GDOT-like detectors and safety rules"],
     WHITE, BOX, BLUE),
    ("3", "Train & run", ["7 methods", "learners trained on 29 train days only"], WHITE, BOX, BLUE),
    ("4", "Results", ["delay per vehicle", "7 held-back test days", "by time of day and how busy"],
     RED, RED, WHITE),
]
xs = []
for i, (n, t, lines, fc, lc, tc) in enumerate(steps):
    x = X0 + i * (BW + GAP)
    xs.append(x)
    box(x, Y, BW, H, fillc=fc, line=lc, lw=2.0)
    box(x + BW / 2 - 0.22, Y + 0.14, 0.44, 0.44, fillc=RED if fc == WHITE else WHITE, shape=MSO_SHAPE.OVAL,
        paras=[para(n, 15, WHITE if fc == WHITE else RED, bold=True)])
    text(x + 0.05, Y + 0.66, BW - 0.1, 0.45, [para(t, 20, tc, bold=True)], anchor="m")
    sub = GREY if fc == WHITE else WHITE
    text(x + 0.1, Y + 1.15, BW - 0.2, H - 1.25,
         [para(l, 13, sub if k else (BLUE if fc == WHITE else WHITE), bold=(k == 0), before=0 if k == 0 else 3)
          for k, l in enumerate(lines)])
    if i < 3:
        arrow(x + BW + 0.03, Y + H / 2, x + BW + GAP - 0.03, Y + H / 2)

# the 7 methods, small, under box 3
text(xs[2] - 0.05, Y + H + 0.06, BW + 0.1, 0.62,
     [para("Webster · GDOT plan · actuated · MaxPressure · LSTDQ · Q-learning · ARS", 10.5, GREY, italic=True)])

# check of the simulation against GDOT's own log, with a fix-and-retry loop
CX, CY, CW, CH = X0, 4.8, BW * 2 + GAP, 0.98
box(CX, CY, CW, CH, fillc=PALERED, line=RED, lw=1.5, paras=[
    para("Check: simulation vs GDOT's log", 15, TITLE, bold=True),
    para("20 unseen days", 12, BLACK, before=2),
    para("green length 34/35 ✓   ·   why green ended 28/35 ✓", 12, BLACK, before=1)])
mid = xs[1] + BW / 2
arrow(mid - 0.3, Y + H + 0.02, mid - 0.3, CY - 0.02, color=RED, w=1.75)
arrow(mid + 0.3, CY - 0.02, mid + 0.3, Y + H + 0.02, color=RED, w=1.75)
text(mid + 0.38, Y + H + 0.08, 1.0, 0.35, [para("fix & retry", 10.5, RED, italic=True, align="l")])

# one-line rule for the comparison
box(X0, 5.95, BW * 4 + GAP * 3, 0.55, fillc=PALEBLUE, paras=[
    para("Same roads, cars, detectors and safety rules for every method: only the decision differs", 13, BLUE,
         bold=True)])

s.notes_slide.notes_text_frame.text = (
    "(~30 s) The system in four steps. One: data - everything comes from GDOT's own signal data. Two: a simulation "
    "of the intersection and the next signal. Before we use it, we check it: we run GDOT's real timing in it on 20 "
    "days we did not tune on, and compare with GDOT's own log. If it fails, we find the cause, fix it and check "
    "again. Three: we train the learners on training days only, and run all seven methods. Four: results - delay "
    "per vehicle on 7 held-back test days. Every method gets the same roads, cars and detectors; only the decision "
    "differs.")

prs.save(OUT)
print("saved", OUT)

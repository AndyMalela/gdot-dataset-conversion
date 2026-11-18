"""v7 = v6 with only slide 5 (Related Works) redone with fewer words, in the student's style (big short phrases,
citations small and grey underneath), plus its speaker notes. Every other slide is untouched.
Usage: uv run --no-project --with python-pptx --with lxml python edit_v7.py eSocLab_Midterm-v6.pptx eSocLab_Midterm-v7.pptx"""
import sys
from xml.sax.saxutils import escape
from lxml import etree
from pptx import Presentation
from pptx.util import Inches, Pt
from pptx.dml.color import RGBColor
from pptx.enum.shapes import MSO_SHAPE
from pptx.enum.text import MSO_ANCHOR
from pptx.oxml.ns import qn

SRC, OUT = sys.argv[1:3]
A = "http://schemas.openxmlformats.org/drawingml/2006/main"
NS = f'xmlns:a="{A}"'
RED, TITLE, BLUE, BLACK, GREY, LIGHT = "A52026", "990000", "1F497D", "000000", "7F7F7F", "F2F2F2"
PALERED = "F8E5E6"
BF = "Arial"

prs = Presentation(SRC)
s = prs.slides[4]
assert any(sh.name == "Title 1" and sh.text_frame.text == "Related Works" for sh in s.shapes)

# remove everything except the title and the slide number
for sh in list(s.shapes):
    if sh.name in ("Title 1", "Slide Number Placeholder 0"):
        continue
    sh._element.getparent().remove(sh._element)


def rpr(size, color, bold=False, italic=False):
    return (f'<a:rPr lang="en-US" sz="{int(size * 100)}"{" b=\"1\"" if bold else ""}{" i=\"1\"" if italic else ""} '
            f'dirty="0"><a:solidFill><a:srgbClr val="{color}"/></a:solidFill><a:latin typeface="{BF}"/>'
            f'<a:ea typeface="{BF}"/><a:cs typeface="{BF}"/></a:rPr>')


def para(runs, size, color=BLACK, bold=False, italic=False, align="l"):
    if isinstance(runs, str):
        runs = [(runs, {})]
    body = "".join(f'<a:r>{rpr(o.get("size", size), o.get("color", color), o.get("bold", bold), o.get("italic", italic))}'
                   f'<a:t>{escape(t)}</a:t></a:r>' for t, o in runs)
    return (f'<a:p {NS}><a:pPr marL="0" indent="0" algn="{align}"><a:buNone/></a:pPr>{body}'
            f'<a:endParaRPr lang="en-US" sz="{int(size * 100)}"/></a:p>')


def fill(shape, paras, anchor="t", margin=0.0):
    tf = shape.text_frame
    tf.word_wrap = True
    tf.margin_left = tf.margin_right = Inches(margin)
    tf.margin_top = tf.margin_bottom = Inches(0.0)
    tf.vertical_anchor = {"t": MSO_ANCHOR.TOP, "m": MSO_ANCHOR.MIDDLE}[anchor]
    tb = tf._txBody
    for p in tb.findall(qn("a:p")):
        tb.remove(p)
    for p in paras:
        tb.append(etree.fromstring(p))


def text(x, y, w, h, paras, anchor="t"):
    t = s.shapes.add_textbox(Inches(x), Inches(y), Inches(w), Inches(h))
    fill(t, paras, anchor)
    return t


def box(x, y, w, h, color, shape=MSO_SHAPE.ROUNDED_RECTANGLE, paras=None):
    b = s.shapes.add_shape(shape, Inches(x), Inches(y), Inches(w), Inches(h))
    st = b._element.find(qn("p:style"))
    if st is not None:
        b._element.remove(st)
    if shape == MSO_SHAPE.ROUNDED_RECTANGLE:
        b.adjustments[0] = 0.08
    b.fill.solid()
    b.fill.fore_color.rgb = RGBColor.from_string(color)
    b.line.fill.background()
    if paras:
        fill(b, paras, "m", 0.02)
    return b


# (number, question, short answer, citation lines, objective)
rows = [
    ("1", "A realistic test?",
     "Mostly made-up roads; real-road studies report no field check*",
     ["62 % made-up (Noaeen 2022, in Chen 2022)",
      "Kwesiga 2025, Meess 2024, Li 2024: no check against the field, tested on the same data"], "O1"),
    ("2", "Compared with what?",
     "Mostly with fixed-time and MaxPressure*",
     ["Engineer-tuned actuated: \"are rarely carried out\" (Meess 2024)",
      "The two that do (Kwesiga 2025, Meess 2024): no other adaptive method*"], "O2"),
    ("3", "When does it pay off?",
     "Mostly only demand level varied: three answers",
     ["shrinks (Sahachaiseree & Oguchi 2025) · grows (El-Tantawy 2014) · same (Alegre 2020)",
      "Also matter: light traffic (Lu 2025), time of day (Smith 2013), conditions unlike training (Han 2023)"],
     "O2"),
    ("4", "Better for whom?",
     "One average over all cars; fairness is an open challenge",
     ["Xiao 2025"], "O3"),
]
X0, W = 0.75, 8.78
y = 1.33
H = [1.3, 1.3, 1.3, 1.12]
for (n, q, a, cites, o), h in zip(rows, H):
    box(X0, y, W, h, LIGHT)
    box(X0 + 0.14, y + 0.13, 0.38, 0.38, RED, shape=MSO_SHAPE.OVAL,
        paras=[para(n, 13, "FFFFFF", bold=True, align="ctr")])
    box(X0 + W - 0.95, y + 0.12, 0.8, 0.38, PALERED, paras=[para("→ " + o, 13, TITLE, bold=True, align="ctr")])
    text(X0 + 0.65, y + 0.08, 6.9, 0.42, [para(q, 20, BLUE, bold=True)], anchor="m")
    text(X0 + 0.65, y + 0.5, 7.95, 0.34, [para(a, 16)])
    text(X0 + 0.65, y + 0.84, 7.95, 0.21 * len(cites), [para(c, 11, GREY, italic=True) for c in cites])
    y += h + 0.1
text(X0, y - 0.02, 5.0, 0.25, [para("* in the studies we reviewed", 10, GREY, italic=True)])

s.notes_slide.notes_text_frame.text = (
    "(~50 s) In the studies we reviewed, I see four gaps.\n\n"
    "One: is the test realistic? Most studies use made-up road networks. The real-road studies report no check "
    "against the field, and they test on the same data they were built from.\n\n"
    "Two: compared with what? Mostly with a fixed timer and MaxPressure. Tests against engineer-tuned actuated "
    "control are rarely carried out, and the two that do include no other adaptive method.\n\n"
    "Three: when does it pay off? Mostly only the amount of traffic is varied, and the answers disagree: the gain "
    "shrinks, grows, or stays the same. Light traffic, time of day and conditions unlike training also matter.\n\n"
    "Four: better for whom? Results are one average over all cars.")

prs.save(OUT)
print("saved", OUT)

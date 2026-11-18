"""v8 = v7 with slide 4 trimmed to the field problem and slide 5 rebuilt as three gaps + a 'why linear' motivation line
(Fable's critique, checked). Based on edit_v7.py. Old v7 docstring: v7 = v6 with only slide 5 (Related Works) redone with fewer words, in the student's style (big short phrases,
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
s4 = prs.slides[3]


def runs_set(par, texts):
    rs = par.runs
    assert len(rs) >= len(texts)
    for r, t in zip(rs, texts):
        r.text = t
    for r in rs[len(texts):]:
        r._r.getparent().remove(r._r)


def sh4(name, contains):
    return next(x for x in s4.shapes if x.has_text_frame and x.name == name and contains in x.text_frame.text)


p = sh4("Rounded Rectangle 39", "In papers").text_frame.paragraphs
runs_set(p[0], ["In papers: large gains, in simulation"])
p = sh4("Rounded Rectangle 40", "On the street").text_frame.paragraphs
runs_set(p[0], ["On the street: rare"])
runs_set(p[1], ['"field deployment remains rare" ', "(Zou et al., 2025)"])
runs_set(p[2], ['agencies need "assurances about compliance to standards" ', "(Chen et al., 2022)"])
_rb = sh4("Rounded Rectangle 41", "can")
_rb.text_frame.vertical_anchor = MSO_ANCHOR.MIDDLE
p = _rb.text_frame.paragraphs
runs_set(p[0], ["Agencies can’t tell if a learned controller would beat what they already run, or by how much"])
for extra in p[1:]:
    extra._p.getparent().remove(extra._p)
s4.notes_slide.notes_text_frame.text = (
    "Learned control looks promising in papers: hundreds of studies report large gains, in simulation. But it rarely "
    "reaches the street. One main problem is agencies must be able to audit a controller against signal standards "
    "first, and that is still a barrier for learned control.\n\n"
    "So an agency cannot tell whether a learned controller would beat what it already runs, by how much, and under "
    "what conditions.")

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
    ("1", "Compared with what?",
     "Rarely against the installed controller; then with only one method*",
     ["Tests against engineer-tuned actuated control \"are rarely carried out\" (Meess 2024)",
      "The two that do (Kwesiga 2025, Meess 2024): one learner, no other adaptive method"], "O2"),
    ("2", "Is the simulation checked?",
     "Real-road simulations not checked against field logs*",
     ["Kwesiga 2025, Meess 2024, Li 2024: no field check reported, tested on the same data",
      "62 % of studies use made-up roads (Noaeen 2022, in Chen 2022)"], "O1"),
    ("3", "When does it pay off?",
     "Studies disagree, and mostly vary only traffic volume",
     ["Linear RL vs actuated: gain shrinks as traffic grows (Sahachaiseree & Oguchi 2025)",
      "Table-based RL vs fixed / actuated: gain grows (El-Tantawy 2014)",
      "Linear RL vs rule-based adaptive: no change (Alegre 2022)"], "O2"),
]
X0, W = 0.75, 8.78
y = 1.33
H = [1.3, 1.3, 1.5]
for (n, q, a, cites, o), h in zip(rows, H):
    box(X0, y, W, h, LIGHT)
    box(X0 + 0.14, y + 0.13, 0.38, 0.38, RED, shape=MSO_SHAPE.OVAL,
        paras=[para(n, 13, "FFFFFF", bold=True, align="ctr")])
    box(X0 + W - 0.95, y + 0.12, 0.8, 0.38, PALERED, paras=[para("\u2192 " + o, 13, TITLE, bold=True, align="ctr")])
    text(X0 + 0.65, y + 0.08, 6.9, 0.42, [para(q, 20, BLUE, bold=True)], anchor="m")
    text(X0 + 0.65, y + 0.5, 7.95, 0.34, [para(a, 16)])
    text(X0 + 0.65, y + 0.84, 7.95, 0.21 * len(cites), [para(c, 11, GREY, italic=True) for c in cites])
    y += h + 0.1
box(X0, y, W, 0.62, "DCE6F2", paras=[
    para([("Why linear learners (motivation): ", {"bold": True}),
          ("agencies need controllers they can check against standards (Chen 2022); LSTDQ converged in about 10 "
           "learning iterations (Sahachaiseree & Oguchi 2025)", {})], 12, BLUE)])
y += 0.7
text(X0, y, 5.0, 0.25, [para("* in the studies we reviewed", 10, GREY, italic=True)])

s.notes_slide.notes_text_frame.text = (
    "(~55 s) In the studies we reviewed, I see three gaps.\n\n"
    "One: compared with what? Tests against the controller actually installed are rarely carried out. The two we "
    "found that do it test only one learning method, with no other adaptive method beside it.\n\n"
    "Two: is the simulation checked? Most studies use made-up roads. The real-road studies don't report checking "
    "their simulation against the field, and they test on the same data they built it from.\n\n"
    "Three: when does it pay off? Studies disagree. Linear learning against actuated control: the gain shrinks as "
    "traffic grows. Table-based learning: it grows. Linear learning against a rule-based controller: no change. "
    "They used different methods and baselines, so we compare these method types side by side, on one "
    "intersection.\n\n"
    "And why linear learners: agencies need controllers they can check, and in its authors' tests LSTDQ learned in "
    "about ten rounds.")

prs.save(OUT)
print("saved", OUT)

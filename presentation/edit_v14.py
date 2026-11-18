"""v14 = v13 + (a) Results: Real Days says why nobody beats the no-cycle controller (slide line + notes),
(b) new slide 'Learners Compared' after Results: When: LSTDQ vs Q-learning vs ARS (same inputs and model family,
different learning), (c) Conclusion notes mention both. Numbers: INTERPRETATION.md sections 0, 3, 7; TEST_PLAN.md.
Usage: uv run --no-project --with python-pptx --with lxml python edit_v14.py eSocLab_Midterm-v13.pptx eSocLab_Midterm-v14.pptx"""
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
RED, TITLE, BLUE, BOX, BLACK, GREY, LIGHT = "A52026", "990000", "1F497D", "4472C4", "000000", "595959", "F2F2F2"
PALERED, PALEBLUE, PALEGREEN, GREEN, WHITE = "F8E5E6", "DCE6F2", "E8F5E9", "2E7D32", "FFFFFF"
BF = "Arial"

prs = Presentation(SRC)


def title_of(slide):
    return next((sh.text_frame.text for sh in slide.shapes if sh.name == "Title 1" and sh.has_text_frame), "")


def find(title):
    return next(sl for sl in prs.slides if title_of(sl) == title)


def rpr(size, color, bold=False, italic=False):
    return (f'<a:rPr lang="en-US" sz="{int(size * 100)}"{" b=\"1\"" if bold else ""}{" i=\"1\"" if italic else ""} '
            f'dirty="0"><a:solidFill><a:srgbClr val="{color}"/></a:solidFill><a:latin typeface="{BF}"/>'
            f'<a:ea typeface="{BF}"/><a:cs typeface="{BF}"/></a:rPr>')


def para(runs, size, color=BLACK, bold=False, italic=False, align="l", before=0, bullet=False):
    if isinstance(runs, str):
        runs = [(runs, {})]
    body = "".join(f'<a:r>{rpr(o.get("size", size), o.get("color", color), o.get("bold", bold), o.get("italic", italic))}'
                   f'<a:t>{escape(t)}</a:t></a:r>' for t, o in runs)
    sp = f'<a:spcBef><a:spcPts val="{int(before * 100)}"/></a:spcBef>' if before else ""
    if bullet:
        ppr = (f'<a:pPr marL="342900" indent="-342900" algn="{align}">{sp}<a:buClr><a:srgbClr val="{RED}"/></a:buClr>'
               f'<a:buSzPct val="100000"/><a:buFont typeface="Arial"/><a:buChar char="&#x25CF;"/></a:pPr>')
    else:
        ppr = f'<a:pPr marL="0" indent="0" algn="{align}">{sp}<a:buNone/></a:pPr>'
    return f'<a:p {NS}>{ppr}{body}<a:endParaRPr lang="en-US" sz="{int(size * 100)}"/></a:p>'


def fill(shape, paras, anchor="t", margin=0.1):
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


class Canvas:
    def __init__(self, slide):
        self.s = slide

    def text(self, x, y, w, h, paras, anchor="t"):
        t = self.s.shapes.add_textbox(Inches(x), Inches(y), Inches(w), Inches(h))
        fill(t, paras, anchor, 0.0)
        return t

    def box(self, x, y, w, h, fillc, paras=None, anchor="m", margin=0.15):
        b = self.s.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(x), Inches(y), Inches(w), Inches(h))
        st = b._element.find(qn("p:style"))
        if st is not None:
            b._element.remove(st)
        b.adjustments[0] = 0.07
        b.fill.solid()
        b.fill.fore_color.rgb = RGBColor.from_string(fillc)
        b.line.fill.background()
        if paras:
            fill(b, paras, anchor, margin)
        return b

    def table(self, x, y, rows, colw, rowh, size, head_size=None):
        """rows: list of lists of str or (str, dict(bold,color))."""
        gt = self.s.shapes.add_table(len(rows), len(rows[0]), Inches(x), Inches(y), Inches(sum(colw)),
                                     Inches(rowh * len(rows)))
        t = gt.table
        for j, cw in enumerate(colw):
            t.columns[j].width = Inches(cw)
        for i, r in enumerate(rows):
            t.rows[i].height = Inches(rowh)
            for j, v in enumerate(r):
                c = t.cell(i, j)
                c.fill.solid()
                c.fill.fore_color.rgb = RGBColor.from_string(BOX if i == 0 else (PALEBLUE if i % 2 else "EEF3FA"))
                c.margin_left = c.margin_right = Inches(0.08)
                c.margin_top = c.margin_bottom = Inches(0.02)
                c.vertical_anchor = MSO_ANCHOR.MIDDLE
                txt, o = (v if isinstance(v, tuple) else (v, {}))
                tb = c.text_frame._txBody
                for p in tb.findall(qn("a:p")):
                    tb.remove(p)
                tb.append(etree.fromstring(para(
                    txt, (head_size or size) if i == 0 else size, WHITE if i == 0 else o.get("color", BLACK),
                    bold=(i == 0 or j == 0 or o.get("bold", False)), align="l" if j == 0 else "ctr")))
        return gt


def clear(slide):
    for sh in list(slide.shapes):
        if sh.name not in ("Title 1", "Slide Number Placeholder 0"):
            sh._element.getparent().remove(sh._element)


L, W = 0.75, 8.78
WIN = {"bold": True, "color": GREEN}


import copy
# ---------------------------------------------------------------- (a) Results: Real Days
s = find("Results: Real Days")
line = next(sh for sh in s.shapes if sh.has_text_frame and sh.text_frame.text.startswith("No learner clearly beats"))
fill(line, [para("No method beats the no-cycle controller: LSTDQ only ties", 22, BLUE, bold=True)], "t", 0.0)
n = s.notes_slide.notes_text_frame.text
add = ("\n\nWhy does nobody beat the no-cycle controller? It is GDOT's own controller, with GDOT's own detector "
       "settings, just without the fixed cycle. Once the cycle is gone, this simple rule already serves this "
       "intersection well, likely because it is rarely near capacity. Learning adds no clear gain on average: on "
       "the development days LSTDQ was slightly better, 24.6 against 25.3 seconds, so any gain is under a second. "
       "This is why the comparison matters: against the deployed plan, learning looks like a 5 to 6 second gain; "
       "against the same controller without its cycle, that gain disappears.")
i = n.index("[Point at:")
s.notes_slide.notes_text_frame.text = n[:i].rstrip() + add + "\n\n" + n[i:] + (
    " [If asked: dropping the cycle gives up timing with the next signal; we count delay around this "
    "intersection only, so that benefit is not fully counted. Development days: LSTDQ better than no-cycle, "
    "19 of 20 days, p 0.021 (Holm).]")

# ---------------------------------------------------------------- (b) new slide: Learners Compared
src = find("Results: When")
ns = prs.slides.add_slide(src.slide_layout)
for sh in list(ns.shapes):
    sh._element.getparent().remove(sh._element)
for sh in src.shapes:
    if sh.name in ("Title 1", "Slide Number Placeholder 0"):
        ns.shapes._spTree.append(copy.deepcopy(sh._element))
t = next(sh for sh in ns.shapes if sh.name == "Title 1")
r0 = t.text_frame.paragraphs[0].runs[0]
r0.text = "Learners Compared"
for r in t.text_frame.paragraphs[0].runs[1:]:
    r._r.getparent().remove(r._r)
lst = prs.slides._sldIdLst
ids = list(lst)
new_id = ids[-1]
lst.remove(new_id)
pos = [k for k, sl in enumerate(prs.slides) if title_of(sl) == "Results: When"][0]
lst.insert(pos + 1, new_id)

c = Canvas(ns)
c.text(L, 1.3, W, 0.5, [para("Same inputs, same model: how they learn decides the result", 22, TITLE, bold=True)])
rows = [["Test days", "LSTDQ", "Q-learning", "ARS"],
        ["Learns by", "one solve on all data", "small step per decision", "random tries"],
        ["Delay, all day (s)", ("25.3", WIN), "30.6", "30.4"],
        ["Busy hours (s)", ("31.1", WIN), "41.1", "42.4"],
        ["Night (s)", "11.6", ("8.1", WIN), "8.5"],
        ["Training", ("stable", WIN), "drifts", "noisy, 10× runs"]]
c.table(L, 1.9, rows, colw=[2.38, 2.1, 2.15, 2.15], rowh=0.55, size=20, head_size=18)
c.text(L, 5.4, W, 0.35, [para("No-cycle controller for reference: all day 24.9 · busy hours 29.3 · night 8.2 s", 14,
                               GREY, italic=True)])
c.text(L, 5.85, W, 0.5, [para("LSTDQ is the only learner that holds up in busy hours", 22, BLUE, bold=True)])
ns.notes_slide.notes_text_frame.text = (
    "(~45 s) The three learners get the same detector inputs and the same kind of linear model. The only difference "
    "is how they learn. LSTDQ solves for its weights from all recorded decisions at once. Q-learning nudges the "
    "weights a little after every decision. ARS tries random changes and keeps the ones that lower delay.\n\n"
    "LSTDQ is clearly the best of the three: 25.3 seconds all day, against about 30.5 for the other two, and it holds "
    "up in busy hours, 31.1 against about 41 to 42. Q-learning and ARS are better at night, 8.1 and 8.5 against "
    "11.6, but they fall apart when traffic is heavy.\n\n"
    "Training tells the same story. LSTDQ settles after one round. Q-learning is best early and drifts if it keeps "
    "training. ARS stays noisy, even with about ten times more simulation runs.\n\n"
    "So with the same model, the learning method decides whether the controller is usable. That is why LSTDQ is "
    "our base method.\n\n"
    "[Not read aloud: busy hours = heavy-hour band on test days (validation: LSTDQ 31.3, Q 48.5, ARS 62.0; "
    "no-cycle 31.5). Days won against no-cycle on test: LSTDQ 4, Q-learning 2, ARS 1 of 7. Training budget of "
    "the kept iterate, 4-hour window-episodes: LSTDQ 44-110, Q-learning 22-44, ARS 220-1,100. Q-learning weights "
    "keep growing in later rounds in 4 of 5 seeds. ARS: random search, 11 directions per step on 312 weights. "
    "Verdicts vs no-cycle: LSTDQ tie (p 0.026); Q-learning and ARS not settled. The 'same model, different solver' "
    "argument is Lagoudakis & Parr 2003's case for least-squares methods.]")

# ---------------------------------------------------------------- (c) Conclusion notes
s = find("Conclusion")
n = s.notes_slide.notes_text_frame.text
key = "Three: learning changes who waits."
if key in n:
    n = n.replace(key, key + " And among the learners, how they learn matters most: LSTDQ holds up in busy hours, "
                  "Q-learning and ARS do not.")
s.notes_slide.notes_text_frame.text = n
prs.save(OUT)
print("saved", OUT)

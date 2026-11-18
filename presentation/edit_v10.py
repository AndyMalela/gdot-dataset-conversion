"""v10 = the student's eSocLab_Midterm-v9-edit.pptx (kept unchanged) with:
 1. slide 10 "Calibration & Validation" redone in literal words: "Build it" / "Check it" halves, two big tiles;
 2. a new backup slide after "Backup: Validation Attempts": "Backup: Validation Rules and Limits" (the details moved
    off slide 10: pass rules, why these numbers, limits, which GDOT report gives what);
 3. the "Dataset" slide moved to just before "Experiments" (after "Methods Compared").
Usage: uv run --no-project --with python-pptx --with lxml python edit_v10.py eSocLab_Midterm-v9-edit.pptx eSocLab_Midterm-v10.pptx"""
import copy, sys
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
        ppr = (f'<a:pPr marL="285750" indent="-285750" algn="{align}">{sp}<a:buClr><a:srgbClr val="{RED}"/></a:buClr>'
               f'<a:buSzPct val="100000"/><a:buFont typeface="Arial"/><a:buChar char="&#x25CF;"/></a:pPr>')
    else:
        ppr = f'<a:pPr marL="0" indent="0" algn="{align}">{sp}<a:buNone/></a:pPr>'
    return f'<a:p {NS}>{ppr}{body}<a:endParaRPr lang="en-US" sz="{int(size * 100)}"/></a:p>'


def fill(shape, paras, anchor="t", margin=0.08):
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

    def box(self, x, y, w, h, fillc, paras=None, anchor="m", line=None):
        b = self.s.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(x), Inches(y), Inches(w), Inches(h))
        st = b._element.find(qn("p:style"))
        if st is not None:
            b._element.remove(st)
        b.adjustments[0] = 0.07
        b.fill.solid()
        b.fill.fore_color.rgb = RGBColor.from_string(fillc)
        if line:
            b.line.color.rgb = RGBColor.from_string(line)
            b.line.width = Pt(1.25)
        else:
            b.line.fill.background()
        if paras:
            fill(b, paras, anchor)
        return b

    def table(self, x, y, w, rows, colw, rowh, size):
        gt = self.s.shapes.add_table(len(rows), len(rows[0]), Inches(x), Inches(y), Inches(w), Inches(rowh * len(rows)))
        t = gt.table
        for j, cw in enumerate(colw):
            t.columns[j].width = Inches(cw)
        for i, r in enumerate(rows):
            t.rows[i].height = Inches(rowh)
            for j, v in enumerate(r):
                c = t.cell(i, j)
                c.fill.solid()
                c.fill.fore_color.rgb = RGBColor.from_string(BOX if i == 0 else (PALEBLUE if i % 2 else "EEF3FA"))
                c.margin_left = c.margin_right = Inches(0.06)
                c.margin_top = c.margin_bottom = Inches(0.03)
                c.vertical_anchor = MSO_ANCHOR.MIDDLE
                tb = c.text_frame._txBody
                for p in tb.findall(qn("a:p")):
                    tb.remove(p)
                tb.append(etree.fromstring(para(v, size, WHITE if i == 0 else BLACK, bold=(i == 0 or j == 0))))
        return gt


def clear(slide):
    for sh in list(slide.shapes):
        if sh.name not in ("Title 1", "Slide Number Placeholder 0"):
            sh._element.getparent().remove(sh._element)


# ================================================================ 1. slide 10: Calibration & Validation, literal words
cv = find("Calibration & Validation")
clear(cv)
c = Canvas(cv)
L, R, HW = 0.75, 5.28, 4.25
# left half: build it
c.text(L, 1.32, HW, 0.45, [para([("1  ", {"color": RED}), ("Build it", {})], 24, BLUE, bold=True)], anchor="m")
c.text(L, 1.8, HW, 0.4, [para("from 29 past weekdays", 18)])
c.text(L, 2.35, HW, 0.3, [para("What we fed the simulation:", 13, GREY, bold=True)])
c.text(L, 2.68, HW, 1.6, [
    para("how many cars came, every 5 minutes, for each direction", 15, bullet=True),
    para("GDOT's real timing schedules", 15, bullet=True, before=5),
    para("where the detectors are", 15, bullet=True, before=5)])
c.text(L, 4.3, HW, 0.5, [para("GDOT reports: Turning Movement Counts · Split Monitor · Timing & Actuation · detector "
                              "configuration", 10.5, GREY, italic=True)])
c.box(L, 4.95, HW, 0.85, PALERED, paras=[
    para([("Found: ", {"bold": True}), ("on the side streets, a queue of cars leaving on green was counted as one car "
                                        "→ corrected", {})], 13, TITLE)])
# right half: check it
c.text(R, 1.32, HW, 0.45, [para([("2  ", {"color": RED}), ("Check it", {})], 24, BLUE, bold=True)], anchor="m")
c.text(R, 1.8, HW, 0.4, [para("on 20 other days it never saw", 18)])
c.text(R, 2.35, HW, 0.75, [para("Same real timing, each day's real car counts → compare with the signal's own "
                                "records of what it did", 13, GREY)])
TW = (HW - 0.15) / 2
for k, (num, what, how) in enumerate([("34 / 35", "how long each green light lasted",
                                       "within 3 seconds (about 1.5 cars)"),
                                      ("28 / 35", "why each green ended",
                                       "cars stopped coming, or its time ran out")]):
    c.box(R + k * (TW + 0.15), 3.15, TW, 1.6, PALEBLUE, anchor="t", paras=[
        para(num, 30, BLUE, bold=True, align="ctr", before=2),
        para(what, 13, BLACK, bold=True, align="ctr", before=3),
        para(how, 11, GREY, align="ctr", before=3)])
c.text(R, 4.8, HW, 0.3, [para("35 cases = 6 lights (side streets, turn arrows) × GDOT's daily schedules", 9.5, GREY,
                              italic=True)])
c.box(R, 5.18, HW, 0.62, PALEGREEN, paras=[
    para("✓ Pass: at least 28 of 35, a rule set before the first try", 12, GREEN, bold=True)])
c.text(L, 6.1, R + HW - L, 0.35, [para("This checks what the signal does, not how long cars wait", 12, GREY,
                                       italic=True, align="ctr")])
cv.notes_slide.notes_text_frame.text = (
    "(~50 s) First question: does our simulation behave like the real intersection?\n\n"
    "To build it, we used only 29 past weekdays. We fed it how many cars came every five minutes, in each direction; "
    "GDOT's real timing schedules; and where the detectors sit. One surprise: on the side streets, a whole queue of "
    "cars leaving on green was counted as one car, so we corrected those counts.\n\n"
    "Then we checked it on 20 other days it had never seen. We gave it the same real timing and each day's real car "
    "counts, and compared it with the signal's own records of what it actually did. How long did each green light "
    "last? In 34 of 35 cases, within 3 seconds, about one and a half cars. Why did each green end: because cars "
    "stopped coming, or because its time ran out? 28 of 35 match. To pass, we needed 28 of 35, a rule we set before "
    "the first try.\n\n"
    "One limit: this checks what the signal does, not how long the cars wait.\n\n"
    "[If asked: the 3-second and 28-of-35 thresholds are a judgement call fixed before the first run. 3 seconds is "
    "about one and a half cars. The same idea, a share of cases within a tolerance, is in the FHWA guide, which uses "
    "85% for traffic counts.]")

# ================================================================ 2. new backup slide after "Backup: Validation Attempts"
va = find("Backup: Validation Attempts")
va.notes_slide.notes_text_frame.text = (
    "(backup, 0 s) Only if asked. Each change was justified by train-day GDOT data and registered before the run; "
    "the pass rules never changed. The rules, why these numbers, the limits and which report gives what are on the "
    "next backup slide.")
nb = prs.slides.add_slide(va.slide_layout)
for sh in list(nb.shapes):
    sh._element.getparent().remove(sh._element)
for sh in va.shapes:
    if sh.name in ("Title 1", "Slide Number Placeholder 0"):
        nb.shapes._spTree.append(copy.deepcopy(sh._element))
tsh = next(sh for sh in nb.shapes if sh.name == "Title 1")
tsh.text_frame.paragraphs[0].runs[0].text = "Backup: Validation Rules and Limits"
tsh.text_frame.paragraphs[0].runs[0].font.size = Pt(28)   # fits on one line
for r in tsh.text_frame.paragraphs[0].runs[1:]:
    r._r.getparent().remove(r._r)
c = Canvas(nb)
col = 4.3
c.text(0.75, 1.35, col, 0.35, [para("Pass rules", 15, BLUE, bold=True)])
c.text(0.75, 1.72, col, 1.7, [
    para("Green length within 3 s; why green ended within 15 percentage points", 11.5, bullet=True),
    para("Pass: ≥ 28 of 35 cases (80 %) on both; no case off by more than 6 s / 30 points; 0 stuck cars", 11.5,
         bullet=True, before=3),
    para("Written before attempt 1, never changed over 8 attempts", 11.5, bullet=True, before=3)])
c.text(5.23, 1.35, col, 0.35, [para("Why these numbers", 15, BLUE, bold=True)])
c.text(5.23, 1.72, col, 1.7, [
    para("A judgement call", 11.5, bullet=True),
    para("3 s ≈ 1.6 cars (one car every 1.9 s at 1,900 veh/h)", 11.5, bullet=True, before=3),
    para("Same idea as FHWA's guide: a share of cases within a tolerance (85 %, for traffic counts)", 11.5,
         bullet=True, before=3),
    para("FHWA Traffic Analysis Toolbox Vol. III (2004), via TxDOT summary", 9.5, GREY, italic=True, before=2)])
c.box(0.75, 3.45, 8.78, 0.72, LIGHT, paras=[
    para([("Limits: ", {"bold": True, "color": BLUE}),
          ("turn-arrow skips do not match yet (18/35); gap times were tuned to the same why-green-ended measure on "
           "train days", {})], 11.5)])
c.text(0.75, 4.3, 8.78, 0.35, [para("Which GDOT report gives what", 15, BLUE, bold=True)])
c.table(0.75, 4.68, 8.78, [
    ["GDOT report", "What it gives the simulation"],
    ["Turning Movement Counts", "Cars per movement, every 5 min"],
    ["Split Monitor", "GDOT's timing plans; how long a green waits for the next car; cap on main-street left arrows"],
    ["Timing & Actuation", "Pedestrian pushes; how left-turners take gaps; timing of signal 138"],
    ["Detector configuration", "Where the detectors are"]], colw=[2.3, 6.48], rowh=0.37, size=10.5)
nb.notes_slide.notes_text_frame.text = (
    "(backup, 0 s) Only if asked. The pass rules were written before the first attempt and never changed. The "
    "thresholds are a judgement call: 3 seconds is about one and a half cars; the FHWA guide uses the same idea, a "
    "share of cases within a tolerance. Two limits: turn-arrow skips do not match yet, and the gap times were tuned "
    "to the same measure on training days.")

# ================================================================ reorder: new backup after Validation Attempts;
# Dataset just before Experiments
sld = prs.slides._sldIdLst
ids = list(sld)
id_of = {title_of(sl): ids[i] for i, sl in enumerate(prs.slides)}
new_id = ids[-1]
sld.remove(new_id)
sld.insert(list(sld).index(id_of["Backup: Validation Attempts"]) + 1, new_id)
ds = id_of["Dataset"]
sld.remove(ds)
sld.insert(list(sld).index(id_of["Experiments"]), ds)

prs.save(OUT)
for i, sl in enumerate(prs.slides, 1):
    print(i, title_of(sl) or "(title/agenda)")

"""Build eSocLab_Midterm-v3.pptx from the user's eSocLab_Midterm-MyVersion.pptx (copy; original untouched).
v3 = v2 + results (attempt-8 model: development and final test days), plain wording. Validation chart: val8.json."""
import copy, json, re, sys
from xml.sax.saxutils import escape
from lxml import etree
from pptx import Presentation
from pptx.util import Inches, Pt, Emu
from pptx.dml.color import RGBColor
from pptx.enum.shapes import MSO_SHAPE, MSO_CONNECTOR
from pptx.enum.text import MSO_ANCHOR
from pptx.chart.data import XyChartData, CategoryChartData
from pptx.enum.chart import XL_CHART_TYPE, XL_MARKER_STYLE, XL_LEGEND_POSITION, XL_LABEL_POSITION
from pptx.oxml.ns import qn

SRC, OUT, VAL, IMG = sys.argv[1:5]
A = "http://schemas.openxmlformats.org/drawingml/2006/main"
NS = f'xmlns:a="{A}"'

RED, TITLE, BLUE, BLACK, GREY, LIGHT = "A52026", "990000", "1F497D", "000000", "595959", "F2F2F2"
BOX = "4472C4"; PALEBLUE = "DCE6F2"; PALERED = "F8E5E6"; MID = "7F7F7F"
HF, BF = "Tahoma", "Arial"

prs = Presentation(SRC)
LAYOUT = next(l for l in prs.slide_layouts if l.name == "CONTENT")
SLDNUM = None
for sh in prs.slides[-1].shapes:
    if sh.name == "Slide Number Placeholder 0":
        SLDNUM = copy.deepcopy(sh._element)
NETPIC = None

# ---------------------------------------------------------------- slide 2: agenda
ag = prs.slides[1]
rect = next(s for s in ag.shapes if s.name == "Rectangle 3")
txBody = rect.text_frame._txBody
paras = txBody.findall(qn("a:p"))
tmpl = copy.deepcopy(paras[0])
for p in paras:
    txBody.remove(p)
for item in ["Problem", "Related Work", "Study Goal", "Proposed Approach", "Experiments", "Results", "Conclusion"]:
    p = copy.deepcopy(tmpl)
    runs = p.findall(qn("a:r"))
    for r in runs[1:]:
        p.remove(r)
    runs[0].find(qn("a:t")).text = item
    txBody.append(p)

# ---------------------------------------------------------------- delete slides 3..16
sldIdLst = prs.slides._sldIdLst
for sldId in list(sldIdLst)[2:]:
    prs.part.drop_rel(sldId.rId)
    sldIdLst.remove(sldId)


# ---------------------------------------------------------------- helpers
def rpr(size=14, color=BLACK, bold=False, italic=False, font=BF):
    return (f'<a:rPr lang="en-US" sz="{int(size*100)}"{" b=\"1\"" if bold else ""}{" i=\"1\"" if italic else ""} dirty="0">'
            f'<a:solidFill><a:srgbClr val="{color}"/></a:solidFill>'
            f'<a:latin typeface="{font}"/><a:ea typeface="{font}"/><a:cs typeface="{font}"/></a:rPr>')


def para(runs, size=14, color=BLACK, bold=False, italic=False, bullet=None, align="l", before=0, level=0):
    """runs: str or list of (text, dict(size,color,bold,italic))."""
    if isinstance(runs, str):
        runs = [(runs, {})]
    if bullet == "dot":
        ppr = (f'<a:pPr marL="285750" indent="-285750" algn="{align}">'
               + (f'<a:spcBef><a:spcPts val="{int(before*100)}"/></a:spcBef>' if before else "")
               + f'<a:buClr><a:srgbClr val="{RED}"/></a:buClr><a:buSzPct val="100000"/>'
               f'<a:buFont typeface="Arial"/><a:buChar char="&#x25CF;"/></a:pPr>')
    elif bullet == "dash":
        ppr = (f'<a:pPr marL="{285750 + 228600*level}" indent="-228600" algn="{align}">'
               + (f'<a:spcBef><a:spcPts val="{int(before*100)}"/></a:spcBef>' if before else "")
               + f'<a:buClr><a:srgbClr val="{GREY}"/></a:buClr><a:buSzPct val="100000"/>'
               f'<a:buFont typeface="Arial"/><a:buChar char="&#x2013;"/></a:pPr>')
    else:
        ppr = (f'<a:pPr marL="0" indent="0" algn="{align}">'
               + (f'<a:spcBef><a:spcPts val="{int(before*100)}"/></a:spcBef>' if before else "")
               + '<a:buNone/></a:pPr>')
    body = ""
    for t, o in runs:
        body += (f'<a:r>{rpr(o.get("size", size), o.get("color", color), o.get("bold", bold), o.get("italic", italic))}'
                 f'<a:t>{escape(t)}</a:t></a:r>')
    return f'<a:p {NS}>{ppr}{body}<a:endParaRPr lang="en-US" sz="{int(size*100)}"/></a:p>'


def fill_tf(shape, paras, anchor="t", margin=0.04, autofit=False):
    tf = shape.text_frame
    tf.word_wrap = True
    m = Inches(margin)
    tf.margin_left = tf.margin_right = m
    tf.margin_top = tf.margin_bottom = Inches(0.02)
    tf.vertical_anchor = {"t": MSO_ANCHOR.TOP, "m": MSO_ANCHOR.MIDDLE, "b": MSO_ANCHOR.BOTTOM}[anchor]
    tb = tf._txBody
    for p in tb.findall(qn("a:p")):
        tb.remove(p)
    for p in paras:
        tb.append(etree.fromstring(p))
    return shape


def text(slide, x, y, w, h, paras, anchor="t", margin=0.0, name=None):
    s = slide.shapes.add_textbox(Inches(x), Inches(y), Inches(w), Inches(h))
    if name:
        s.name = name
    return fill_tf(s, paras if isinstance(paras, list) else [paras], anchor, margin)


def _strip_style(shape):
    st = shape._element.find(qn("p:style"))
    if st is not None:
        shape._element.remove(st)


def box(slide, x, y, w, h, fill=None, line=None, paras=None, anchor="m", radius=0.06, shape=MSO_SHAPE.ROUNDED_RECTANGLE,
        lw=1.0, margin=0.08, dash=False):
    s = slide.shapes.add_shape(shape, Inches(x), Inches(y), Inches(w), Inches(h))
    _strip_style(s)
    if shape == MSO_SHAPE.ROUNDED_RECTANGLE:
        s.adjustments[0] = radius
    if fill:
        s.fill.solid(); s.fill.fore_color.rgb = RGBColor.from_string(fill)
    else:
        s.fill.background()
    if line:
        s.line.color.rgb = RGBColor.from_string(line); s.line.width = Pt(lw)
        if dash:
            from pptx.enum.dml import MSO_LINE
            s.line.dash_style = MSO_LINE.DASH
    else:
        s.line.fill.background()
    if paras:
        fill_tf(s, paras if isinstance(paras, list) else [paras], anchor, margin)
    return s


def badge(slide, x, y, label, d=0.42, fill=RED, size=14):
    return box(slide, x, y, d, d, fill=fill, shape=MSO_SHAPE.OVAL, margin=0,
               paras=[para(label, size=size, color="FFFFFF", bold=True, align="ctr")])


def arrow(slide, x1, y1, x2, y2, color="404040", w=2.0, head=True):
    c = slide.shapes.add_connector(MSO_CONNECTOR.STRAIGHT, Inches(x1), Inches(y1), Inches(x2), Inches(y2))
    _strip_style(c)
    c.line.color.rgb = RGBColor.from_string(color); c.line.width = Pt(w)
    if head:
        ln = c.line._get_or_add_ln()
        ln.append(etree.fromstring(f'<a:tailEnd {NS} type="triangle" w="med" len="med"/>'))
    return c


def table(slide, x, y, w, rows, colw, rowh=0.3, size=11, head_fill=BOX, band=(PALEBLUE, "EEF3FA"), bold_first_col=False):
    nr, nc = len(rows), len(rows[0])
    gt = slide.shapes.add_table(nr, nc, Inches(x), Inches(y), Inches(w), Inches(rowh * nr))
    t = gt.table
    for j, cw in enumerate(colw):
        t.columns[j].width = Inches(cw)
    for i, r in enumerate(rows):
        t.rows[i].height = Inches(rowh)
        for j, v in enumerate(r):
            c = t.cell(i, j)
            c.fill.solid()
            c.fill.fore_color.rgb = RGBColor.from_string(head_fill if i == 0 else band[(i - 1) % 2])
            c.margin_left = c.margin_right = Inches(0.06)
            c.margin_top = c.margin_bottom = Inches(0.03)
            c.vertical_anchor = MSO_ANCHOR.MIDDLE
            tb = c.text_frame._txBody
            for p in tb.findall(qn("a:p")):
                tb.remove(p)
            runs = v if isinstance(v, list) else [(v, {})]
            tb.append(etree.fromstring(para(runs, size=size, color="FFFFFF" if i == 0 else BLACK,
                                            bold=(i == 0) or (bold_first_col and j == 0))))
    return gt


def new_slide(title, notes=None):
    s = prs.slides.add_slide(LAYOUT)
    ph = next(p for p in s.placeholders if p.placeholder_format.idx == 104)
    fill_tf(ph, [f'<a:p {NS}><a:pPr marL="0" indent="0" algn="r"><a:buNone/></a:pPr><a:r>{rpr(36, TITLE, font=HF)}'
                 f'<a:t>{escape(title)}</a:t></a:r></a:p>'], anchor="m", margin=0.1)
    if SLDNUM is not None:
        s.shapes._spTree.append(copy.deepcopy(SLDNUM))
    if notes:
        s.notes_slide.notes_text_frame.text = notes
    return s


def card_title(slide, x, y, w, num, title, size=15):
    badge(slide, x, y, num, d=0.38, size=13)
    text(slide, x + 0.48, y - 0.02, w - 0.5, 0.45, para(title, size=size, color=BLUE, bold=True), anchor="m")


# ================================================================ 3 Problem
s = new_slide("Problem", notes=(
    "(60 s) Every traffic light makes the same decision every second: keep the current green, or switch. "
    "Switch too early and the green road stops; too late and the other road waits for nothing. "
    "There are three ways to make that decision: a fixed timer, an actuated rule that stays green while cars keep "
    "coming - which is what agencies run today - and learned control, reinforcement learning, which papers report "
    "to outperform traditional control. So an agency has to choose, intersection by intersection."))
# intersection illustration
box(s, 0.8, 3.15, 3.9, 0.75, fill="BFBFBF", radius=0.0, shape=MSO_SHAPE.RECTANGLE)          # main road
box(s, 2.38, 1.5, 0.75, 4.0, fill="BFBFBF", radius=0.0, shape=MSO_SHAPE.RECTANGLE)          # side road
box(s, 2.38, 3.15, 0.75, 0.75, fill="A6A6A6", radius=0.0, shape=MSO_SHAPE.RECTANGLE)        # box
for yy in (1.62, 2.07, 2.52):                                                                # queued side-street cars
    box(s, 2.83, yy, 0.22, 0.36, fill=RED, radius=0.2)
for xx in (0.95, 1.55):                                                                      # moving main-street cars
    box(s, xx, 3.6, 0.42, 0.22, fill=BOX, radius=0.2)
box(s, 3.35, 3.24, 0.42, 0.22, fill=BOX, radius=0.2)
arrow(s, 3.85, 3.71, 4.45, 3.71, color=BOX, w=2.0)
sig = box(s, 3.32, 1.75, 0.36, 1.0, fill="262626", radius=0.25)
for k, col in enumerate(("5A1A1A", "5A4A1A", "2ECC40")):
    box(s, 3.39, 1.82 + k * 0.31, 0.22, 0.22, fill=col, shape=MSO_SHAPE.OVAL)
text(s, 3.78, 1.75, 1.0, 0.5, para("green for main street", size=10, color=GREY, italic=True))
text(s, 0.8, 1.55, 1.5, 1.1, [para("side street:", size=10, color=GREY, italic=True, align="r"),
                              para("cars waiting on red", size=10, color=GREY, italic=True, align="r")])
text(s, 0.6, 5.6, 4.3, 0.45, para("Every second: keep green, or switch?", size=15, color=BLUE, bold=True, align="ctr"))
text(s, 0.8, 6.1, 3.9, 0.55, para("Good timing reduces congestion (Haydari & Yilmaz, 2022)", size=11, color=GREY,
                                   italic=True, align="ctr"))
# three ways
text(s, 5.0, 1.4, 4.6, 0.4, para("Three ways to decide", size=17, color=BLUE, bold=True))
ways = [("1", "Fixed-time", "A set timer schedule. Ignores the traffic actually there."),
        ("2", "Actuated", "Stays green while cars keep arriving, ends on a gap. What agencies run today."),
        ("3", "Learned (RL)", "Learns its decision rule from experience. Reported to outperform traditional control "
                              "(Muresan et al., 2019; Chen et al., 2025).")]
for i, (n, t, d) in enumerate(ways):
    y = 1.9 + i * 1.32
    box(s, 5.0, y, 4.6, 1.17, fill=LIGHT)
    badge(s, 5.12, y + 0.14, n, d=0.38, size=13)
    text(s, 5.62, y + 0.1, 3.9, 0.4, para(t, size=15, color=BLUE, bold=True), anchor="m")
    text(s, 5.62, y + 0.5, 3.85, 0.65, para(d, size=12))
box(s, 5.0, 5.95, 4.6, 0.65, fill=PALERED,
    paras=[para("An agency must choose per intersection: when is a learned controller worth it?", size=13,
                color=TITLE, bold=True)], margin=0.12)

# ================================================================ 4 Related Work
s = new_slide("Related Work", notes=(
    "(75 s) Three gaps. First, the same question - how does the gain of learned control change with demand - has "
    "three published answers: it shrinks, it grows, it doesn't change. Second, many studies compare only with a fixed "
    "timer, so their gains can't be compared with what is actually installed; deployed practice and the strongest rule, "
    "MaxPressure, rarely appear together in the studies we reviewed. Third, studies on real intersections build or "
    "calibrate their simulation from real data, but none of the three we read reports checking it against field "
    "observations - and they test on the same data they built it from. Our base method is linear RL with LSTDQ "
    "from Sahachaiseree and Oguchi."))
cols = [("1", "When does it pay off?",
         [para([("Sahachaiseree & Oguchi (2025): ", {"bold": True}), ("gain shrinks as demand rises", {})], size=13),
          para([("El-Tantawy et al. (2014): ", {"bold": True}), ("gain grows at high demand", {})], size=13, before=6),
          para([("Alegre et al. (2020): ", {"bold": True}), ("demand affects all methods equally", {})], size=13, before=6)],
         "Same question, three answers"),
        ("2", "Against what?",
         [para([("Many RL studies compare only with fixed-time control; tests against engineer-tuned actuated "
                 "control \"are rarely carried out\" ", {}), ("(Meess et al., 2024)", {"italic": True})], size=13),
          para("Deployed practice (field plan, actuated) and the strongest rule (MaxPressure) rarely appear together*",
               size=13, before=6)],
         "Gains not comparable with what is installed"),
        ("3", "In what simulation?",
         [para([("Kwesiga et al. (2025), Meess et al. (2024), Li et al. (2024): ", {"bold": True}),
                ("simulation built or calibrated from real data", {})], size=13),
          para("No check against field observations reported; tested on the same data used to build it", size=13,
               before=6)],
         "Is the simulation realistic? Unknown")]
for i, (n, t, body, gap) in enumerate(cols):
    x = 0.75 + i * 2.98
    box(s, x, 1.4, 2.82, 4.3, fill=LIGHT)
    card_title(s, x + 0.12, 1.55, 2.6, n, t, size=14)
    text(s, x + 0.15, 2.1, 2.55, 2.4, body)
    box(s, x + 0.12, 4.65, 2.58, 0.9, fill=PALERED, paras=[para([("Gap: ", {"bold": True}), (gap, {})], size=12,
                                                                  color=TITLE)], margin=0.1)
box(s, 0.75, 5.85, 8.78, 0.6, fill=PALEBLUE, margin=0.12,
    paras=[para([("Base method: ", {"bold": True}),
                 ("linear RL with LSTDQ (Sahachaiseree & Oguchi, 2025): fast to train, argued to be interpretable",
                  {})], size=12, color=BLUE)])
text(s, 0.75, 6.48, 6.5, 0.3, para("* in the studies we reviewed", size=10, color=GREY, italic=True))

# ================================================================ 5 Study Goal
s = new_slide("Study Goal", notes=(
    "(60 s) The goal: find when and why linear RL signal control beats the control already deployed, on real traffic. "
    "We pick linear RL because it is the most deployable form of RL - if even it isn't worth it, that is a finding. "
    "Three objectives, each answering a gap: build a simulation from GDOT field data and validate it on days it wasn't "
    "tuned on; compare deployed, rule-based and learned controllers across traffic conditions; and explain each win or "
    "loss by what the controller actually does. The two hypotheses were written down before any result."))
box(s, 0.75, 1.4, 8.78, 1.15, fill=BLUE, margin=0.18, paras=[
    para([("Goal: ", {"bold": True}), ("find when and why linear RL signal control beats the control already deployed, "
                                       "on real traffic", {})], size=17, color="FFFFFF"),
    para("We test the most deployable form of RL (linear) against what agencies already run", size=12,
         color="DCE6F2", italic=True, before=4)])
objs = [("O1", "Build & validate", "Simulate a real intersection from GDOT field data; validate it on days it was not "
                                    "tuned on", "gap 3"),
        ("O2", "Compare", "Deployed practice vs rule-based vs linear-learning controllers, across traffic conditions "
                          "(when)", "gaps 1, 2"),
        ("O3", "Explain", "Each win or loss by what the controller does (cycle length, green use, skips); check "
                          "robustness (seeds, worst-served movement)", "why")]
for i, (n, t, d, g) in enumerate(objs):
    y = 2.75 + i * 0.95
    badge(s, 0.8, y + 0.12, n, d=0.55, size=13)
    text(s, 1.5, y + 0.05, 2.0, 0.7, para(t, size=15, color=BLUE, bold=True), anchor="m")
    text(s, 3.45, y, 5.0, 0.8, para(d, size=12), anchor="m")
    box(s, 8.55, y + 0.2, 0.98, 0.4, fill=PALERED, margin=0.02, paras=[para(g, size=11, color=TITLE, bold=True,
                                                                             align="ctr")])
box(s, 0.75, 5.7, 8.78, 0.9, fill=LIGHT, margin=0.15, paras=[
    para("Hypotheses (fixed before any result)", size=12, color=GREY, bold=True),
    para([("H1: ", {"bold": True, "color": BLUE}), ("below capacity, all responsive methods tie     ", {}),
          ("H2: ", {"bold": True, "color": BLUE}), ("near capacity, the methods separate", {})], size=13, before=3)])

# ================================================================ 6 System Overview
s = new_slide("System Overview", notes=(
    "(75 s) The whole system in four steps. Everything comes from GDOT's own signal data. Step one, build a simulation "
    "of the real intersection: real roads, real five-minute counts, detectors placed like GDOT's, and the standard "
    "signal safety rules. Step two, calibrate and validate it: tune on training days, then check it against GDOT's own "
    "controller logs on days it never saw. If it fails, we fix the cause and try again. Step three, train the learners "
    "on training days only. Step four, compare seven methods on the same simulation - same roads, same cars, same "
    "detectors - so the only difference is the decision. That is what 'field-calibrated' in the title means."))
box(s, 0.75, 1.4, 8.78, 0.55, fill=LIGHT, margin=0.12, paras=[
    para([("GDOT ATSPM field data:  ", {"bold": True, "color": BLUE}),
          ("5-min counts  ·  timing plans  ·  detector layout  ·  controller logs", {})], size=13, align="ctr")])
steps = [("1", "Build", ["SUMO simulation", "real roads, 5-min demand,", "GDOT-like detectors,", "signal safety rules"]),
         ("2", "Calibrate & validate", ["tune on train days;", "check vs GDOT controller", "logs on unseen days"]),
         ("3", "Train", ["learners on train", "days only,", "5 seeds each"]),
         ("4", "Compare", ["7 methods, same roads,", "cars, detectors, rules:", "only the decision differs"])]
bw, gap = 1.95, 0.33
for i, (n, t, lines) in enumerate(steps):
    x = 0.75 + i * (bw + gap)
    hl = i == 1
    box(s, x, 2.35, bw, 2.15, fill="FFFFFF", line=RED if hl else BOX, lw=2.25 if hl else 1.25)
    badge(s, x + bw / 2 - 0.21, 2.47, n, d=0.42, size=14, fill=RED if hl else BOX)
    text(s, x + 0.05, 2.95, bw - 0.1, 0.4, para(t, size=14, color=TITLE if hl else BLUE, bold=True, align="ctr"))
    text(s, x + 0.08, 3.38, bw - 0.16, 1.1, [para(l, size=11, align="ctr") for l in lines])
    if i < 3:
        arrow(s, x + bw + 0.03, 3.42, x + bw + gap - 0.03, 3.42)
    arrow(s, 0.75 + i * (bw + gap) + bw / 2, 1.97, 0.75 + i * (bw + gap) + bw / 2, 2.33, color=MID, w=1.25) if i < 2 else None
# feedback loop 2 -> 1
x1c, x2c = 0.75 + bw / 2, 0.75 + (bw + gap) + bw / 2
arrow(s, x2c, 4.52, x2c, 4.85, color=RED, w=1.5, head=False)
arrow(s, x2c, 4.85, x1c, 4.85, color=RED, w=1.5, head=False)
arrow(s, x1c, 4.85, x1c, 4.53, color=RED, w=1.5)
text(s, 0.85, 4.9, 3.9, 0.35, para("fails? find the cause, fix, retry", size=11, color=RED, italic=True, align="ctr"))
# output
x4 = 0.75 + 3 * (bw + gap)
arrow(s, x4 + bw / 2, 4.52, x4 + bw / 2, 4.88)
box(s, x4 - 1.2, 4.9, bw + 1.2, 0.7, fill=TITLE, margin=0.08, paras=[
    para("Output: delay per vehicle, every hour", size=12, color="FFFFFF", bold=True, align="ctr"),
    para("→ when and why each method wins", size=12, color="FFFFFF", align="ctr")])
box(s, 0.75, 5.85, 8.78, 0.65, fill=PALEBLUE, margin=0.15, paras=[
    para([("Field-calibrated: ", {"bold": True}), ("tuned to GDOT's real-world measurements, and checked against them "
                                                   "on days it was not tuned on", {})], size=13, color=BLUE)])

# ================================================================ 7 Dataset
s = new_slide("Dataset", notes=(
    "(60 s) One real intersection in Buckhead, Atlanta: West Paces Ferry Road at East Andrews and Slaton Drive, GDOT "
    "signal 137. West Paces Ferry is the main street; the two side streets cross it. Another signal, 138, sits about "
    "260 metres east and is simulated too. All data comes from GDOT's ATSPM portal. We use weekdays from March to May "
    "2026 - the only period where every movement is counted - split by date: train days for calibration and training, "
    "development days for checking the simulation and comparing methods, and the last two weeks held back, unseen, "
    "for the final test."))
pic = s.shapes.add_picture(IMG, Inches(0.75), Inches(1.4), Inches(3.55), Inches(3.55))
pic.line.color.rgb = RGBColor.from_string("BFBFBF"); pic.line.width = Pt(0.75)
text(s, 0.75, 4.98, 3.55, 0.3, para("Simulated network around signal 137 (blue: approaches)", size=10, color=GREY,
                                    italic=True, align="ctr"))
facts = [para("W. Paces Ferry Rd @ E. Andrews Dr / Slaton Dr", size=15, color=BLUE, bold=True),
         para("Buckhead, Atlanta  ·  GDOT signal 137", size=12, color=GREY, before=2),
         para([("Main street: ", {"bold": True}), ("W. Paces Ferry, 2 lanes each way", {})], size=13, bullet="dot",
              before=10),
         para([("Side streets: ", {"bold": True}), ("E. Andrews (SB), Slaton (NB), 3 lanes", {})], size=13,
              bullet="dot", before=5),
         para([("Upstream signal 138 ", {"bold": True}), ("(~260 m east) simulated with its field timing", {})],
              size=13, bullet="dot", before=5),
         para([("Data: ", {"bold": True}), ("GDOT ATSPM only - turning-movement counts, Split Monitor, Timing & "
                                            "Actuation, detector configuration", {})], size=13, bullet="dot", before=5),
         para([("Weekdays, Mar-May 2026: ", {"bold": True}), ("the only period with all 10 movements counted", {})],
              size=13, bullet="dot", before=5)]
text(s, 4.55, 1.4, 5.0, 3.9, facts)
# timeline
segs = [("Train", "Mar 2 - Apr 17", "29 days", "calibration, learner training", 3.85, BOX),
        ("Development", "Apr 20 - May 15", "20 days", "simulation check, method comparison", 2.9, BLUE),
        ("Test (held back)", "May 18 - 29", "7 days", "final comparison, opened once", 2.03, MID)]
x = 0.75
for name, dates, n, use, w, col in segs:
    box(s, x, 5.42, w - 0.04, 0.62, fill=col, radius=0.08, margin=0.06, paras=[
        para(name, size=12, color="FFFFFF", bold=True, align="ctr"),
        para(f"{n} · {dates}", size=11, color="FFFFFF", align="ctr")])
    text(s, x, 6.08, w - 0.04, 0.4, para(use, size=11, color=GREY, italic=True, align="ctr"))
    x += w

# ================================================================ 8 Calibration & Validation
val = json.load(open(VAL))
s = new_slide("Calibration & Validation", notes=(
    "(90 s) Left: what we tuned, only on train days, and from which GDOT report. Counts give the traffic - with the "
    "side streets corrected, because GDOT's presence detectors count a queue leaving on green as one car. The Split "
    "Monitor gives the daily plans and controller settings; the Timing and Actuation charts give pedestrian button "
    "presses, how left-turners behave, and the offset to the upstream signal. Right: the check. We run GDOT's real "
    "timing in the simulation on 20 days it never saw and compare with GDOT's own controller log, for every phase and "
    "plan - 35 pairs. The rules were written before the first run. Each dot is one pair: on the diagonal means the "
    "simulation gives that phase the same time as the field. 34 of 35 pass on time, 28 of 35 on why the green ended. "
    "This is the final version of the simulation, after we corrected our controller engine to GDOT's switching rules "
    "(found after the first test run); the same pass rules were used. "
    "Why this works: the real controller reacts to traffic, so its log records the traffic it saw."))
text(s, 0.75, 1.35, 4.2, 0.4, para("Calibrate: train days", size=15, color=BLUE, bold=True))
table(s, 0.75, 1.78, 4.2, [
    ["GDOT report", "Sets in the simulation"],
    ["Turning Movement Counts", "Demand per movement, 5-min (side streets corrected for detector undercount)"],
    ["Split Monitor", "Daily timing plans, how long green waits for the next car, cap on main-street left arrows"],
    ["Timing & Actuation", "Pedestrian calls, left-turn behaviour, offset to signal 138"],
    ["Detector configuration", "Detector layout"]], colw=[1.45, 2.75], rowh=0.62, size=11, bold_first_col=True)
text(s, 0.75, 5.05, 4.2, 0.6, para("Every change justified by train-day GDOT data, never tuned to the validation "
                                   "score", size=11, color=GREY, italic=True))
text(s, 5.15, 1.35, 4.4, 0.4, para("Validate: 20 unseen days", size=15, color=BLUE, bold=True))
cd = XyChartData()
ser = cd.add_series("phase × plan")
for v in val:
    ser.add_data_point(v["field_split"], v["sim_split"])
diag = cd.add_series("sim = field")
diag.add_data_point(10, 10); diag.add_data_point(32, 32)
gf = s.shapes.add_chart(XL_CHART_TYPE.XY_SCATTER, Inches(5.1), Inches(1.72), Inches(4.45), Inches(2.45), cd)
ch = gf.chart
ch.has_legend = False
ch.font.size = Pt(10); ch.font.name = BF
p0, p1 = ch.plots[0].series
p0.marker.style = XL_MARKER_STYLE.CIRCLE; p0.marker.size = 6
p0.marker.format.fill.solid(); p0.marker.format.fill.fore_color.rgb = RGBColor.from_string(BOX)
p0.marker.format.line.color.rgb = RGBColor.from_string("FFFFFF")
p0.format.line.fill.background()
p1.marker.style = XL_MARKER_STYLE.NONE
p1.format.line.color.rgb = RGBColor.from_string(RED); p1.format.line.width = Pt(1.25)
p1.format.line.dash_style = None
for ax, t in ((ch.category_axis, "field: GDOT log (s)"), (ch.value_axis, "simulation (s)")):
    ax.minimum_scale, ax.maximum_scale, ax.major_unit = 10, 32, 5
    ax.has_major_gridlines = ax is ch.value_axis
    if ax.has_major_gridlines:
        ax.major_gridlines.format.line.color.rgb = RGBColor.from_string("E0E0E0")
    ax.has_title = True
    ax.axis_title.text_frame.text = t
    r = ax.axis_title.text_frame.paragraphs[0].runs[0]
    r.font.size = Pt(10); r.font.bold = False; r.font.color.rgb = RGBColor.from_string(GREY)
    ax.tick_labels.font.size = Pt(9); ax.tick_labels.font.color.rgb = RGBColor.from_string(GREY)
    ax.format.line.color.rgb = RGBColor.from_string("BFBFBF")
text(s, 5.15, 4.15, 4.4, 0.3, para("Average phase time, sim vs field (35 phase × plan pairs)", size=10, color=GREY,
                                   italic=True, align="ctr"))
crit = [para("Rules fixed before the first run; pass needs ≥ 28/35:", size=11, color=GREY),
        para([("✓ ", {"color": "2E7D32", "bold": True}), ("Phase time within 3 s:  ", {}), ("34/35", {"bold": True})],
             size=12, before=3),
        para([("✓ ", {"color": "2E7D32", "bold": True}), ("Gap-out share within 15 pts:  ", {}),
              ("28/35", {"bold": True})], size=12, before=2),
        para([("✓ ", {"color": "2E7D32", "bold": True}), ("No stuck vehicles or false jams", {})], size=12, before=2),
        para([("Accepted.  ", {"bold": True, "color": TITLE}), ("Not matched: phase skips 18/35 (reported)", {})],
             size=11, before=4)]
text(s, 5.15, 4.45, 4.4, 1.35, crit)
box(s, 0.75, 5.95, 8.78, 0.58, fill=PALEBLUE, margin=0.15, paras=[
    para([("Why it works: ", {"bold": True}), ("the real controller reacts to traffic, so its log records the traffic "
                                               "it saw", {})], size=13, color=BLUE)])

# ================================================================ 9 Methods
s = new_slide("Methods Compared", notes=(
    "(60 s) Seven decision rules in three families. The fixed timer doesn't respond to traffic: Webster, the textbook "
    "schedule. Detector rules respond to the detectors. GDOT plan is what runs on the street today: a fixed cycle "
    "shared with the next signal, and inside it a green ends early when no more cars come. Actuated is the same "
    "controller with the same detector settings but without the fixed cycle - every green lasts as long as cars keep "
    "coming. It is our reference. MaxPressure gives green to the longest queue and is a common benchmark in RL "
    "studies. Then three linear learners. They share the same features and the same decision; only how they learn "
    "differs. LSTDQ is the base method. Q-learning learns the same model one step at a time - batch versus online. "
    "ARS searches the weights directly on delay - value-based versus direct search. Everyone gets the same roads, "
    "cars, detectors and safety rules."))
fams = [("Fixed timer", "no response to traffic",
         [("Webster", "textbook fixed schedule, designed from train-day counts")]),
        ("Detector rules", "respond to detectors",
         [("GDOT plan", "deployed today: fixed cycle shared with the next signal; green ends early if no car comes"),
          ("Actuated", "same controller and settings, no fixed cycle; the reference"),
          ("MaxPressure", "green to the longest queue; common benchmark in RL studies")]),
        ("Linear learners", "same features, learn weights",
         [("LSTDQ", "batch least squares; the base method"),
          ("Q-learning", "same model, updated after every decision: batch vs online"),
          ("ARS", "searches the weights directly on delay: value vs policy search")])]
for i, (t, sub, items) in enumerate(fams):
    x = 0.75 + i * 2.98
    hl = i == 2
    box(s, x, 1.4, 2.82, 4.25, fill=PALEBLUE if hl else LIGHT)
    text(s, x + 0.15, 1.5, 2.55, 0.4, para(t, size=16, color=TITLE if hl else BLUE, bold=True))
    text(s, x + 0.15, 1.88, 2.55, 0.3, para(sub, size=11, color=GREY, italic=True))
    y = 2.32
    for name, d in items:
        h = 1.02 if len(items) == 3 else 1.45
        box(s, x + 0.12, y, 2.58, h - 0.1, fill="FFFFFF", margin=0.1, anchor="t", paras=[
            para(name, size=13, color=BLUE, bold=True), para(d, size=11, before=2)])
        y += h
box(s, 0.75, 5.8, 8.78, 0.45, fill=PALERED, margin=0.12, paras=[
    para("Same network, demand, detectors and safety rules for all: only the decision differs", size=13,
         color=TITLE, bold=True, align="ctr")])
text(s, 0.75, 6.3, 8.78, 0.35, para("After midterm: DQN as a neural reference.  Not included: PPO (unstable in prior "
                                    "benchmarks)", size=11, color=GREY, italic=True))

# ================================================================ 10 How the learned controller works
s = new_slide("How the Learner Decides", notes=(
    "(60 s) Every second the learned controller turns detector readings into a few features per phase: how many cars "
    "are queued, time since the last car crossed, how long this green has run, what the other ring is doing. It scores "
    "both choices, extend or end, as a weighted sum of those features, and picks the higher score. The signal's safety "
    "rules still apply - minimum green, yellow, red. Learning happens offline on train days: run the current policy, "
    "record every decision and the delay that followed, solve one least-squares problem for the weights, and repeat "
    "five rounds. The first round follows the actuated controller. Of the five rounds, we keep the one with the lowest "
    "delay on a fixed set of train days - never chosen on development or test days."))
text(s, 0.75, 1.35, 8.8, 0.4, para("Deciding: every second", size=15, color=BLUE, bold=True))
dec = [("Detector readings", "occupancy and counts per lane", BOX),
       ("Features", "queue, time since last car, green so far, other ring", BOX),
       ("Score both", "extend = w · features\nend = w · features", RED),
       ("Pick higher", "then safety rules: min green, yellow, red", MID)]
bw, gap = 1.95, 0.33
for i, (t, d, col) in enumerate(dec):
    x = 0.75 + i * (bw + gap)
    lines = d.split("\n")
    box(s, x, 1.8, bw, 1.15, fill=col, margin=0.08, paras=[para(t, size=13, color="FFFFFF", bold=True, align="ctr")]
        + [para(l, size=11, color="FFFFFF", align="ctr", before=2) for l in lines])
    if i < 3:
        arrow(s, x + bw + 0.03, 2.37, x + bw + gap - 0.03, 2.37)
box(s, 0.75, 3.07, 8.78, 0.5, fill=LIGHT, margin=0.12, paras=[
    para([("Example: ", {"bold": True, "color": BLUE}),
          ("6 cars waiting on red pushes \"end\" up; no car on the green for 5 s pushes \"extend\" down → end green",
           {})], size=12)])
text(s, 0.75, 3.75, 8.8, 0.4, para("Learning: offline, train days only (LSTDQ)", size=15, color=BLUE, bold=True))
lrn = [("Run policy", "22 runs per round: random train day, 4-hour window"),
       ("Record decisions", "features, action, delay that followed"),
       ("Least squares", "one solve for the weights w"),
       ("New policy", "use the new w; repeat 5 rounds")]
for i, (t, d) in enumerate(lrn):
    x = 0.75 + i * (bw + gap)
    box(s, x, 4.2, bw, 1.05, fill="FFFFFF", line=RED, lw=1.25, margin=0.08, paras=[
        para(t, size=13, color=TITLE, bold=True, align="ctr"), para(d, size=11, align="ctr", before=2)])
    if i < 3:
        arrow(s, x + bw + 0.03, 4.72, x + bw + gap - 0.03, 4.72)
xl = 0.75 + 3 * (bw + gap) + bw / 2; xf = 0.75 + bw / 2
arrow(s, xl, 5.27, xl, 5.5, color=RED, w=1.5, head=False)
arrow(s, xl, 5.5, xf, 5.5, color=RED, w=1.5, head=False)
arrow(s, xf, 5.5, xf, 5.28, color=RED, w=1.5)
text(s, 1.5, 5.52, 6.5, 0.3, para("round 0 follows the actuated controller  ·  the best round on train days is "
                                  "kept", size=10,
                                  color=GREY, italic=True, align="ctr"))
box(s, 0.75, 5.95, 8.78, 0.6, fill=PALEBLUE, margin=0.12, paras=[
    para([("Q-learning: ", {"bold": True}), ("same features, updates w after every decision.   ", {}),
          ("ARS: ", {"bold": True}), ("tries random changes to w, keeps those that lower delay.", {})], size=12,
         color=BLUE)])

# ================================================================ 11 Evaluation design
s = new_slide("Evaluation Design", notes=(
    "(60 s) The measure is delay per vehicle: the time each car loses compared with driving freely, including waiting "
    "to enter, every hour. To answer 'when', hours are grouped by how full the intersection is, by time of day and by "
    "how variable the demand is. To answer 'why', we look at what each controller did: cycle length, green per phase, "
    "skips. For reliability: five training seeds per learner and the worst-served movement. Every method is compared "
    "with actuated control, paired by day; what counts as a tie was fixed before any result. The test days were held "
    "back and opened once, under an analysis plan written down beforehand. After that run we found errors: in our "
    "controller engine, in scoring cars that never got in, in the saturation rate, and in which saved learner weights "
    "to use. The fixes were written down before rerunning, and both results are kept."))
box(s, 0.75, 1.4, 8.78, 0.75, fill=BLUE, margin=0.18, paras=[
    para([("Measure: delay per vehicle", {"bold": True}),
          ("  =  time lost vs driving freely, incl. waiting to enter (s/veh), every hour", {})], size=14,
         color="FFFFFF")])
cards = [("When", "O2", ["How busy the hour is (traffic vs capacity)", "Time of day",
                         "How uneven traffic is within the hour"]),
         ("Why", "O3", ["Cycle length", "Green time per direction", "Phases skipped, greens run to their limit"]),
         ("How reliable", "O3", ["5 training runs per learner", "Delay of the worst-served movement"])]
for i, (t, o, items) in enumerate(cards):
    x = 0.75 + i * 2.98
    box(s, x, 2.35, 2.82, 2.2, fill=LIGHT)
    text(s, x + 0.15, 2.45, 1.9, 0.4, para(t, size=15, color=BLUE, bold=True))
    box(s, x + 2.05, 2.5, 0.6, 0.32, fill=PALERED, margin=0.0, paras=[para(o, size=11, color=TITLE, bold=True,
                                                                           align="ctr")])
    text(s, x + 0.15, 2.95, 2.55, 1.6, [para(it, size=12, bullet="dot", before=4 if k else 0)
                                        for k, it in enumerate(items)])
text(s, 0.75, 4.7, 8.8, 0.4, para("Comparison rules", size=15, color=BLUE, bold=True))
rules = [para([("Each method vs actuated, ", {"bold": True}), ("paired by day (20 development days, then 7 test days)",
                                                              {})], size=13, bullet="dot"),
         para([("Tie ", {"bold": True}), ("= within 2 s/veh (or 5 %, whichever is larger), fixed before any result",
                                         {})], size=13, bullet="dot", before=4),
         para([("Test days opened once ", {"bold": True}), ("under a plan written beforehand; rerun once after "
                                                           "fixes registered before the rerun", {})], size=13, bullet="dot",
              before=4)]
text(s, 0.75, 5.1, 8.8, 1.4, rules)

# ================================================================ 12 Results: real days
# sources: atsc/sites/137/eval/analysis.md, eval_test/analysis.md, TEST_PLAN.md "Amendment 1 results";
# "days below GDOT plan" from eval_test/runs.csv (descriptive, not a registered test)
s = new_slide("Results: Real Days", notes=(
    "(75 s) Delay per vehicle, lower is better. Development days are the 20 days we compared on first; test days are "
    "the 7 days held back and opened once. On the test days, actuated has 24.9 seconds, LSTDQ 25.3 - the statistics "
    "show these are a tie, within 2 seconds. MaxPressure, ARS and Q-learning are 'not settled': the day-to-day spread "
    "is too large to call a tie or a difference. GDOT's deployed timing is 31.2 and significantly worse than actuated; "
    "Webster's textbook schedule is far behind because it is designed for a typical day and overflows on busy days. "
    "Last column: LSTDQ, MaxPressure and actuated have less delay than GDOT's deployed timing on every one of the 7 "
    "test days. So LSTDQ and MaxPressure do beat the deployed timing by 5 to 6 seconds per vehicle - but "
    "the same controller without its fixed cycle gets the same gain without any learning."))
text(s, 0.75, 1.35, 8.78, 0.4, para([("Delay per vehicle (s), lower is better  ", {"bold": True, "color": BLUE}),
                                     ("· learners: average of 5 training runs", {"color": GREY, "size": 12})],
                                    size=15))
R = lambda t: [(t, {"bold": True})]  # noqa: E731
rows = [["Method", "Development (20 days)", "Test (7 days)", "Test: vs actuated", "Test days below GDOT plan"],
        [R("Actuated (no fixed cycle)"), "25.3", R("24.9"), "reference", "7 of 7"],
        [R("LSTDQ"), "24.6", R("25.3"), [("tie (shown)", {"bold": True, "color": "2E7D32"})], "7 of 7"],
        ["MaxPressure", "27.6", "26.1", "not settled", "7 of 7"],
        ["ARS", "36.5", "30.4", "not settled", "5 of 7"],
        ["Q-learning", "31.5", "30.6", "not settled", "5 of 7"],
        [R("GDOT plan (deployed)"), "34.3", R("31.2"), [("worse", {"color": TITLE})], "-"],
        ["Webster (textbook timer)", "122.0", "117.7", [("worse", {"color": TITLE})], "0 of 7"]]
table(s, 0.75, 1.82, 8.78, rows, colw=[2.5, 1.62, 1.3, 1.66, 1.7], rowh=0.42, size=12)
text(s, 0.75, 5.22, 8.78, 0.5, para("Tie = within 2 s/veh, shown statistically.  Not settled = day-to-day spread too "
                                    "large to call a tie or a difference.", size=10, color=GREY, italic=True))
box(s, 0.75, 5.7, 8.78, 0.85, fill=PALERED, margin=0.15, paras=[
    para([("Against GDOT's deployed timing: ", {"bold": True}),
          ("LSTDQ, MaxPressure and actuated cut delay by 5-6 s per vehicle, and win every test day.", {})], size=13,
         color=TITLE),
    para([("Against the same controller without its fixed cycle: ", {"bold": True}),
          ("no learner is clearly better.", {})], size=13, color=TITLE, before=3)])

# ================================================================ 13 Results: by condition
s = new_slide("Results: By Condition", notes=(
    "(75 s) The same test days split by time of day; bold is the lowest delay in each row. The learners and "
    "MaxPressure win the morning and midday; actuated wins the evening peak and the evening. At night LSTDQ and "
    "MaxPressure lose about 3 seconds: they hold long greens for very few cars, while Q-learning and ARS match the "
    "deployed controller. Last row is a what-if on 5 development days: every count raised by 25 percent, more traffic "
    "than any training day. Every adaptive method falls behind actuated there, and Q-learning and ARS fall behind "
    "GDOT's own timing too. Beyond 25 percent the queues back up past the end of our modelled roads, so we don't rank "
    "methods there."))
text(s, 0.75, 1.35, 8.78, 0.4, para([("Test days by time of day: delay per vehicle (s)  ", {"bold": True,
                                                                                          "color": BLUE}),
                                     ("· bold = lowest in the row", {"color": GREY, "size": 12})], size=15))
B = lambda t: [(t, {"bold": True, "color": "2E7D32"})]  # noqa: E731
rows = [["", "GDOT plan", "Actuated", "MaxPressure", "LSTDQ", "Q-learning", "ARS"],
        ["Night 00-06", "8.2", "8.2", "11.2", "11.6", B("8.1"), "8.5"],
        ["Morning peak 06-10", "26.1", "22.8", "21.2", B("21.1"), "21.8", "21.9"],
        ["Midday 10-15", "35.0", "25.8", "26.0", B("24.2"), "27.9", "26.8"],
        ["Evening peak 15-19", "34.0", B("27.8"), "32.0", "30.6", "42.2", "38.2"],
        ["Evening 19-24", "31.8", B("25.1"), "26.9", "26.9", "33.3", "38.2"]]
table(s, 0.75, 1.82, 8.78, rows, colw=[1.88, 1.1, 1.1, 1.3, 1.1, 1.2, 1.1], rowh=0.4, size=12,
      bold_first_col=True)
text(s, 0.75, 4.35, 8.78, 0.4, para([("What-if: every count +25 %  ", {"bold": True, "color": BLUE}),
                                     ("· 5 development days, more traffic than any training day", {"color": GREY,
                                                                                                  "size": 12})],
                                    size=15))
rows = [["", "GDOT plan", "Actuated", "MaxPressure", "LSTDQ", "Q-learning", "ARS"],
        ["Normal traffic", "27.4", "24.5", B("22.8"), "23.3", "26.7", "27.3"],
        ["+25 % traffic", "63.1", B("45.0"), "51.3", "51.7", "76.9", "100.4"]]
table(s, 0.75, 4.8, 8.78, rows, colw=[1.88, 1.1, 1.1, 1.3, 1.1, 1.2, 1.1], rowh=0.4, size=12,
      bold_first_col=True, band=(PALERED, "FBF0F1"))
text(s, 0.75, 6.05, 8.78, 0.5, para("At +25 %, queues already back up past the end of the modelled roads in 22-44 % "
                                    "of hours, depending on the method; above +25 % in most hours for every method, "
                                    "so methods are not ranked there.", size=10, color=GREY, italic=True))

# ================================================================ 14 Main findings: who waits
s = new_slide("Main Findings", notes=(
    "(90 s) This is the most important slide. Same test days, delay split into the main street, West Paces Ferry, "
    "which carries 58 percent of the cars, and the side streets. GDOT's deployed timing gives the main street "
    "priority - 18 seconds - and the side streets wait almost 50: in its fixed cycle, spare time goes to the main "
    "street. "
    "LSTDQ and MaxPressure keep the main-street priority, 19 seconds, and cut the side-street wait by about 14 to 16 "
    "seconds. Actuated without a fixed cycle reaches the same average as LSTDQ a different way: it shares the wait "
    "evenly, 25 seconds on both. So against actuated, learning does not lower the average; it changes who waits. "
    "Why the learners favour the main street - our likely explanation, not yet tested: they are rewarded per vehicle, and most vehicles are on the main "
    "street; and the side streets only have detectors at the stop line, so the learners can't see how long a "
    "side-street queue is."))
cd = CategoryChartData()
cd.categories = ["GDOT plan", "Actuated", "LSTDQ", "MaxPressure", "Q-learning", "ARS"]
cd.add_series("Main street (58 % of cars)", (18.2, 24.7, 19.2, 19.2, 22.8, 27.7))
cd.add_series("Side streets", (49.6, 25.1, 33.8, 35.9, 41.5, 34.2))
gf = s.shapes.add_chart(XL_CHART_TYPE.COLUMN_CLUSTERED, Inches(0.7), Inches(1.75), Inches(5.0), Inches(3.75), cd)
ch = gf.chart
ch.font.size = Pt(10); ch.font.name = BF
ch.has_legend = True; ch.legend.position = XL_LEGEND_POSITION.TOP; ch.legend.include_in_layout = False
ch.legend.font.size = Pt(10)
for ser, col in zip(ch.plots[0].series, (BOX, RED)):
    ser.format.fill.solid(); ser.format.fill.fore_color.rgb = RGBColor.from_string(col)
pl = ch.plots[0]
pl.gap_width = 60; pl.overlap = 0
pl.has_data_labels = True
pl.data_labels.number_format = "0"; pl.data_labels.number_format_is_linked = False
pl.data_labels.position = XL_LABEL_POSITION.OUTSIDE_END
pl.data_labels.font.size = Pt(9); pl.data_labels.font.color.rgb = RGBColor.from_string(GREY)
va = ch.value_axis
va.minimum_scale, va.maximum_scale, va.major_unit = 0, 60, 10
va.has_major_gridlines = True; va.major_gridlines.format.line.color.rgb = RGBColor.from_string("E0E0E0")
va.tick_labels.font.size = Pt(9); va.tick_labels.font.color.rgb = RGBColor.from_string(GREY)
va.format.line.fill.background()
ca = ch.category_axis
ca.tick_labels.font.size = Pt(9); ca.format.line.color.rgb = RGBColor.from_string("BFBFBF")
text(s, 0.75, 1.35, 5.0, 0.4, para("Who waits? Test days, delay per vehicle (s)", size=14, color=BLUE, bold=True))
fx = 5.95
fnd = [("1", "Deployed timing favours the main street", "Main street 18 s, side streets 50 s: spare time in the "
                                                         "fixed cycle goes to the main street"),
       ("2", "LSTDQ keeps that priority, cuts side waits", "Main 19 s, side 34 s: about 16 s less for side streets "
                                                           "than GDOT plan"),
       ("3", "Actuated shares the wait evenly", "25 s on both: same average as LSTDQ, a different split")]
for i, (n, t, d) in enumerate(fnd):
    y = 1.4 + i * 1.33
    badge(s, fx, y + 0.05, n, d=0.38, size=13)
    text(s, fx + 0.48, y, 3.1, 0.5, para(t, size=13, color=BLUE, bold=True))
    text(s, fx + 0.48, y + (0.3 if len(t) < 34 else 0.5), 3.1, 0.75, para(d, size=11))
box(s, 0.75, 5.7, 8.78, 0.85, fill=PALEBLUE, margin=0.15, paras=[
    para([("Likely why (not yet tested): ", {"bold": True}), ("the learners are rewarded per vehicle (most cars are on the main street), and "
                                      "side streets have detectors only at the stop line, so a long side queue is "
                                      "mostly invisible to them", {})], size=12, color=BLUE)])

# ================================================================ 15 Conclusion
s = new_slide("Conclusion", notes=(
    "(75 s) Three findings. One: against GDOT's deployed timing, LSTDQ and MaxPressure cut delay by 5 to 6 "
    "seconds per vehicle, mostly by serving the side streets better. Two: against the same controller run without "
    "its fixed cycle, no learner is clearly better - LSTDQ ties, the others are not settled - so at this "
    "intersection the gain over today's timing does not need learning; what learning changes is who waits. Three: "
    "the edge depends on conditions - LSTDQ loses at night, and every learner falls behind actuated when traffic "
    "grows beyond what they trained on. "
    "What is done: a simulation built only from data GDOT already collects, validated on unseen days against the "
    "controller's own log, and seven methods compared on 20 development days and 7 held-back test days. "
    "Limitations, stated honestly: the validation checks how the controller behaves, not delay itself; left arrows "
    "are served more often than in the field; side-street demand is our corrected estimate; delay is counted at this "
    "intersection only, so the benefit of timing it together with the next signal is not fully counted; the test "
    "days were run twice, the second time after fixes written down in advance; one site, our own controller "
    "engine."))
box(s, 0.75, 1.4, 8.78, 1.95, fill=PALERED, margin=0.15, anchor="t", paras=[
    para("Findings (one site, 137)", size=14, color=TITLE, bold=True),
    para([("1  ", {"bold": True}), ("Against GDOT's deployed timing, LSTDQ and MaxPressure cut delay by 5-6 s per "
                                    "vehicle, mostly for the side streets", {})], size=12, before=4),
    para([("2  ", {"bold": True}), ("Against the same controller without its fixed cycle, no learner is clearly "
                                    "better: the gain needs no learning; learning changes who waits", {})], size=12,
         before=4),
    para([("3  ", {"bold": True}), ("The edge depends on conditions: LSTDQ loses at night; every learner falls "
                                    "behind actuated when traffic grows beyond its training range", {})], size=12, before=4)])
box(s, 0.75, 3.5, 4.3, 3.05, fill=LIGHT)
text(s, 0.9, 3.57, 4.0, 0.4, para("Done so far", size=15, color=BLUE, bold=True))
text(s, 0.9, 3.97, 4.05, 2.55, [
    para("Simulation of a real intersection built from GDOT ATSPM data only", size=11, bullet="dot"),
    para("Validated on unseen days against the controller's own log: accepted", size=11, bullet="dot", before=4),
    para("7 methods compared on 20 development + 7 test days; learners with 5 training runs", size=11, bullet="dot",
         before=4),
    para([("Data finding: ", {"bold": True}), ("GDOT stop-line counts undercount queued cars (2 intersections)",
                                               {})], size=11, bullet="dot", before=4)])
box(s, 5.23, 3.5, 4.3, 3.05, fill=LIGHT)
text(s, 5.38, 3.57, 4.0, 0.4, para("Limitations", size=15, color=BLUE, bold=True))
text(s, 5.38, 3.97, 4.05, 2.55, [
    para("Validation checks controller behaviour, not delay itself", size=11, bullet="dot"),
    para("Left arrows served more often than in the field", size=11, bullet="dot", before=3),
    para("Side-street demand is a corrected estimate", size=11, bullet="dot", before=3),
    para("Delay counted at this intersection only: benefit of timing with the next signal not fully counted",
         size=11, bullet="dot", before=3),
    para("Test days run twice (rerun after fixes written down in advance)", size=11, bullet="dot", before=3),
    para("One site; our own controller engine", size=11, bullet="dot", before=3)])

# ================================================================ 16 Future work
s = new_slide("Future Work", notes=(
    "(60 s) Each item has a purpose. Training the learners on heavier traffic tests whether their edge survives "
    "beyond the range they trained on - the what-if showed it doesn't yet. Any improved model needs new unseen days, "
    "because the 7 test days have now been used. Outcome-level validation uses more ATSPM reports - split failures, "
    "approach delay, left-turn gaps - to check traffic outcomes, not only controller behaviour. Replication at 7065 "
    "asks whether the procedure and the ranking hold at a second, busier intersection - a consistency check, since "
    "that site differs in several ways at once. DQN gives a neural reference for whether linear is enough, and the "
    "count-error test asks whether the ranking survives errors in the counts."))
fw = [["Next step", "Purpose"],
      [[("Train learners on heavier traffic ", {"bold": True}), ("(up to +50 %)", {})],
       "Does their edge survive beyond the training range?"],
      [[("New unseen test days", {"bold": True})],
       "The 7 test days are used; any improved model needs fresh ones"],
      [[("Outcome-level validation ", {"bold": True}), ("(ATSPM: Split Failure, Approach Delay, Left Turn Gap)", {})],
       "Check traffic outcomes, not only controller behaviour"],
      [[("Replicate at SIG 7065 ", {"bold": True}), ("(Peachtree @ Piedmont); ", {}), ("add DQN", {"bold": True})],
       "Does it hold at a busier site? Neural reference: is linear enough?"],
      [[("Count-error test", {"bold": True})], "Does the ranking survive errors in the counts?"]]
table(s, 0.75, 1.45, 8.78, fw, colw=[3.9, 4.88], rowh=0.72, size=13)
box(s, 0.75, 5.85, 8.78, 0.65, fill=LIGHT, margin=0.15, paras=[
    para("7065 differs from 137 in coordination and saturation at once: a consistency check, not a causal "
         "separation", size=12, color=GREY, italic=True)])

# ================================================================ Backup slides
s = new_slide("Backup: Validation Attempts", notes="Only if asked. Each change was justified by train-day GDOT data "
              "and registered before the run; the pass rules never changed.")
rows = [["#", "Change (from train-day GDOT data)", "Phase time ≤ 3 s", "Gap-outs ≤ 15 pt"],
        ["1", "Settings as first built", "19/35", "11/35"],
        ["2", "Detector passage times fitted on train days", "15/35", "16/35"],
        ["3", "+ Measured pedestrian calls", "20/35", "18/35"],
        ["4", "+ Side-street undercount corrected", "29/35 ✓", "19/35"],
        ["5", "+ Left-turn driver behaviour calibrated", "27/35", "20/35"],
        ["6", "+ Upstream signal 138 simulated (platoons)", "26/35", "23/35"],
        ["7", "+ Main-street left arrows capped at their planned time (as GDOT)", "34/35 ✓", "29/35 ✓"],
        [[("8", {"bold": True})], [("+ Controller engine corrected to GDOT's switching rules (after first test)",
                                    {"bold": True})],
         [("34/35 ✓", {"bold": True})], [("28/35 ✓", {"bold": True})]]]
table(s, 0.75, 1.45, 8.78, rows, colw=[0.5, 4.88, 1.7, 1.7], rowh=0.44, size=12)
text(s, 0.75, 5.5, 8.78, 1.0, [
    para("Pass needs ≥ 28/35 on both, plus no stuck vehicles / false jams; rules written before attempt 1", size=12,
         bullet="dot"),
    para("Controller fixes: 2, 7, 8.  Traffic fixes: 3, 4, 5, 6", size=12, bullet="dot", before=4)])

s = new_slide("Backup: Detector Undercount", notes="Only if asked. Found while diagnosing short side-street greens in "
              "validation (137); first seen at 7065 by comparing flows with neighbouring signals.")
text(s, 0.75, 1.45, 8.78, 4.9, [
    para("GDOT's side-street (and EB-left) counts come from stop-bar presence zones", size=15, bullet="dot"),
    para("A presence zone reports \"occupied\", not individual cars; GDOT counts each switch-on", size=13,
         bullet="dash", before=4),
    para("A queue leaving on green keeps the zone occupied: several cars count as one", size=13, bullet="dash",
         before=4),
    para("Symptom in validation: simulated side-street greens too short (too few cars)", size=15, bullet="dot",
         before=12),
    para("Fix: cars estimated from how long the zone stayed occupied during green (~1.9 s per car), a factor per "
         "movement from 9 train days, applied to daytime bins", size=15, bullet="dot", before=12),
    para("Effect: phase-time check passed for the first time (20 → 29/35)", size=13, bullet="dash", before=4),
    para("Same defect found earlier at SIG 7065 (Peachtree through counts)", size=15, bullet="dot", before=12),
    para("Corrected demand is a model-based estimate, not GDOT's number", size=13, bullet="dash", before=4)])

s = new_slide("Backup: Prior Simulations", notes="Only if asked. Fair contrast: they calibrate or build the simulation "
              "and evaluate on the same data; none reports checking it against field observations. Kwesiga's "
              "controller fidelity (real MaxTime software) and drone-based driver calibration are stronger than ours.")
rows = [["", "Kwesiga et al. 2025", "Meess et al. 2024", "Li et al. 2024 (D2TSC)"],
        ["Site / data", "North Ave, Atlanta; 1 afternoon, video + drones", "Ingolstadt; loop-detector demand",
         "Zhuzhou; 7 days, cameras"],
        ["Calibrated", "Speeds, car-following (drone headways)", "Demand estimated; quality cited from 2010",
         "\"follows real data\"; no details"],
        ["Controller", "Real MaxTime software, GDOT plans", "Real TRENDS logic", "Field plan + deployed adaptive"],
        ["Checked vs field?", "Not reported", "Not reported", "Not reported"],
        ["Tested on held-out data?", "No (same afternoon)", "Not stated", "No (same 7 days)"],
        [[("This study", {"bold": True})], [("ATSPM only; validated vs controller log on 20 unseen days", {"bold": True})],
         [("Own NEMA engine, checked against GDOT log", {"bold": True})], [("Locked test days", {"bold": True})]]]
table(s, 0.75, 1.45, 8.78, rows, colw=[1.7, 2.5, 2.28, 2.3], rowh=0.66, size=11, bold_first_col=True)

s = new_slide("Backup: Inputs Not From GDOT", notes="Only if asked. Disclosed assumptions.")
rows = [["Item", "Source / assumption"],
        ["Road geometry", "OpenStreetMap; lanes checked by hand (Slaton Dr lanes assumed from its 3 detector zones)"],
        ["Saturation flow", "HCM base 1,900 veh/h/lane (undercount estimate, busy/heavy grouping); Webster and the "
                            "queue estimate use the rate measured in the simulation on train days"],
        ["Driver model", "SUMO defaults, except impatience 0.5 (calibrated)"],
        ["Stop-bar zone length 40 ft", "Assumed (not published)"],
        ["Walk time 4.0 s; no ped calls 21-06 h", "Assumed (not visible / not measured)"],
        ["Stop-bar detectors on main-street through", "Added so every controller reads the same detectors"],
        ["EB/WB right turns", "Run as through (no separate count)"],
        ["Clearances, min greens", "Read from Timing & Actuation on 2026-10-02 (outside study period)"]]
table(s, 0.75, 1.45, 8.78, rows, colw=[3.2, 5.58], rowh=0.55, size=12, bold_first_col=True)

prs.save(OUT)
print("saved", OUT, len(prs.slides), "slides")

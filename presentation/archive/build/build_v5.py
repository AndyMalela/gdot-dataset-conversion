"""Build eSocLab_Midterm-v5.pptx (v4 + slides 3, 4, 8, 9 redone, no hypothesis labels, notes = SCRIPT_v5.md).
v4 docstring:
Build eSocLab_Midterm-v4.pptx from the user's eSocLab_Midterm-MyVersion.pptx (copy; original untouched).
v4 = v3 content (attempt-8 model, numbers from atsc/sites/137/INTERPRETATION.md v3 and TEST_PLAN.md amendment-1
results) put back into the student's own structure: their section names, their research questions as objectives,
their approach diagram (MyVersion slide 9, kept and edited in place), lighter text, ~9 min.
Validation chart: val8.json."""
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
for item in ["Problem Formulation", "Research Objective", "Proposed Approach", "Experiments", "Main Findings",
             "Conclusions"]:
    p = copy.deepcopy(tmpl)
    runs = p.findall(qn("a:r"))
    for r in runs[1:]:
        p.remove(r)
    runs[0].find(qn("a:t")).text = item
    txBody.append(p)
prs.slides[0].notes_slide.notes_text_frame.text = (
    "(10 s) Good afternoon. My study compares signal controllers - deployed, rule-based and learned - at one real "
    "GDOT intersection in Atlanta, in a simulation built from GDOT's own data.")
ag.notes_slide.notes_text_frame.text = "(5 s) The talk follows this order; I will move straight to the problem."

# ---------------------------------------------------------------- keep the student's approach diagram (slide 9),
# edit it in place; delete the other slides 3..16
sldIdLst = prs.slides._sldIdLst
APPROACH = prs.slides[8]
_approach_id = list(sldIdLst)[8]
from pptx.opc.packuri import PackURI
APPROACH.part.partname = PackURI("/ppt/slides/slide900.xml")   # new slides are numbered by count; avoid a clash
for sh in APPROACH.shapes:
    if not sh.has_text_frame:
        continue
    for pa in sh.text_frame.paragraphs:
        for r in pa.runs:
            if "SUMO digital twin" in r.text:
                r.text = r.text.replace("SUMO digital twin", "SUMO simulation")
            if r.text == "saturation X_c":
                r.text = "how busy the hour is"
            if r.text.startswith("All\xa0 same network"):
                r.text = "All: same network, demand, detectors, rules"
            if r.text == "Uses standard NEMA phase design":
                r.text = "Standard US signal phase design (NEMA, 8 phases): only the decision differs between methods"
APPROACH.notes_slide.notes_text_frame.text = (
    "(40 s) How the system works. Left: everything comes from GDOT's own signal data - 5-minute counts per movement, "
    "the real timing plans, and where the detectors are. Middle: the SUMO simulation runs a loop every second. Cars "
    "move, detectors placed like GDOT's see them, and the controller decides only one thing: extend the current "
    "green or end it. A rule engine enforces the safety rules a real controller has - minimum green, yellow and red "
    "clearance, ring order, pedestrian walk. Every method plugs into the same slot, so differences come from the "
    "decision alone. Right: delay per vehicle every hour, grouped by how busy the hour is, to see when and why each "
    "method wins.")
for sldId in list(sldIdLst)[2:]:
    if sldId is _approach_id:
        continue
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


# ================================================================ 3 Problem (v5: job sentence, standard three types, problem)
# sources: Xiao et al. 2025 intro ("three categories: fixed-time ... actuated ... adaptive"; SCOOT/SCATS "preset rules";
# 470 papers); Chen, Fang & Sadeh 2022 sec. 1-2 (RL "one emerging approach to adaptive control"; "significant
# improvements over fixed and actuated algorithms in simulations"; "never been deployed"; "Jurisdictions cannot deploy
# ... without assurances about compliance to standards"); Zou et al. 2025 ("field deployment remains rare")
s = new_slide("Problem Formulation")
box(s, 0.75, 1.35, 8.78, 0.5, fill=BLUE, margin=0.15, paras=[
    para("A traffic signal does one job: every second, keep the current green, or switch?", size=15,
         color="FFFFFF", bold=True, align="ctr")])
text(s, 0.75, 1.95, 8.78, 0.35, para([("Signal control comes in three types  ", {"bold": True, "color": BLUE}),
                                      ("(Xiao et al., 2025; Chen et al., 2022)", {"italic": True, "color": GREY,
                                                                                  "size": 10})], size=14))
types = [("1", "Fixed-time", [para("A preset schedule. Ignores the traffic actually there.", size=11.5)]),
         ("2", "Actuated", [para("Detectors stretch or end each green, within preset limits.", size=11.5),
                            para([("Signal 137 runs this, ", {"bold": True, "color": TITLE}),
                                  ("inside a fixed cycle shared with the next signal", {"color": TITLE})],
                                 size=10.5, before=4)]),
         ("3", "Adaptive", [para("Changes the timing itself as traffic changes.", size=11.5),
                            para([("Designed rule: ", {"bold": True}), ("e.g. SCOOT, SCATS, MaxPressure", {})],
                                 size=10.5, bullet="dash", before=3),
                            para([("Learned from data: ", {"bold": True}), ("reinforcement learning (RL)", {})],
                                 size=10.5, bullet="dash", before=1)])]
for i, (n, t, body) in enumerate(types):
    x = 0.75 + i * 2.98
    box(s, x, 2.35, 2.82, 1.78, fill=PALEBLUE if i == 2 else LIGHT)
    card_title(s, x + 0.12, 2.45, 2.6, n, t, size=14)
    text(s, x + 0.15, 2.88, 2.6, 1.22, body)
facts = [("In papers", [para([("470 ", {"bold": True}), ("RL signal-control papers, 2015-2025 ", {}),
                               ("(Xiao et al., 2025)", {"italic": True, "color": GREY})], size=11.5),
                        para([("\"significant improvements over fixed and actuated algorithms in simulations\" ", {}),
                              ("(Chen et al., 2022)", {"italic": True, "color": GREY})], size=11.5, before=3)]),
         ("On the street", [para([("\"RL-based TSC algorithms have never been deployed\" ", {}),
                                  ("(Chen et al., 2022)", {"italic": True, "color": GREY})], size=11.5),
                            para([("\"field deployment remains rare\" ", {}),
                                  ("(Zou et al., 2025)", {"italic": True, "color": GREY})], size=11.5, before=3)])]
for i, (t, body) in enumerate(facts):
    x = 0.75 + i * 4.47
    box(s, x, 4.25, 4.31, 1.1, fill=LIGHT, anchor="t", margin=0.12,
        paras=[para(t, size=12.5, color=BLUE, bold=True)] + body)
box(s, 0.75, 5.47, 8.78, 1.1, fill=PALERED, anchor="t", margin=0.14, paras=[
    para([("Problem: ", {"bold": True}), ("an agency cannot tell whether a learned controller would beat what it "
                                          "already runs, at its own intersection, with its own traffic", {})],
         size=13, color=TITLE),
    para([("The methods: ", {"bold": True}), ("must be audited against signal standards before deployment, still a "
                                              "barrier for RL (Chen et al., 2022)", {})], size=11, bullet="dash",
         before=3),
    para([("The tests: ", {"bold": True}), ("few compare with the controller actually installed, on real traffic "
                                            "(next slide)", {})], size=11, bullet="dash", before=1)])

# ================================================================ 4 Related Work (v5: four gaps, each feeds an objective)
# sources: Chen 2022 line 364 (62 % synthetic, per Noaeen et al. 2022); HANDOFF.md / Backup: Prior Simulations
# (Kwesiga, Meess, Li: no field check reported); Meess 2024 p.2 quote; Sahachaiseree 2025, El-Tantawy 2014,
# Alegre 2020; Lu 2025 low-demand table (NEMA-actuated 71.2 vs RL-TSC-AC 92.2 s); Smith 2013 Table 1 (largest gain
# Mid Day); Han 2023 (mismatch > 20 %: RL -0.09 %, ALINEA +1.43 %); queries/experimental-setup-across-papers.md (no
# held-out days); Xiao 2025 sec. 5.6 fairness
s = new_slide("What Prior Work Leaves Open")
gaps = [("1", "A realistic test?", "O1",
         [para([("62 % ", {"bold": True}), ("of RL studies use made-up road networks (Noaeen et al., 2022, in Chen "
                                            "et al., 2022)", {})], size=11),
          para("Real-road studies (Kwesiga 2025, Meess 2024, Li 2024) build the simulation from real data, but "
               "report no check against the field, and test on the same data*", size=11, before=2)]),
        ("2", "Better than what is installed?", "O2",
         [para([("Tests against engineer-tuned actuated control \"are rarely carried out\" ", {}),
                ("(Meess et al., 2024)", {"italic": True, "color": GREY})], size=11),
          para("The two that do (Meess 2024, Kwesiga 2025) do not report checking the simulated installed controller "
               "against its field log*", size=11, before=2)]),
        ("3", "When does it pay off?", "O2",
         [para("Mostly only total demand is varied, with three answers: gain shrinks (Sahachaiseree & Oguchi, 2025), "
               "grows (El-Tantawy et al., 2014), stays the same (Alegre et al., 2020)", size=11),
          para("Other conditions matter: light traffic, actuated beat RL (Lu et al., 2025); field gain changed with "
               "time of day (Smith et al., 2013); RL lost its gain when conditions differed from training (Han et "
               "al., 2023). No held-out days*", size=11, before=2)]),
        ("4", "Better for whom?", "O3",
         [para("Results are one average over all cars", size=11),
          para([("Fairness, \"all road users receive equitable access\", is an open challenge ", {}),
                ("(Xiao et al., 2025)", {"italic": True, "color": GREY})], size=11, before=2)])]
hs = [1.12, 1.0, 1.5, 0.92]
y = 1.35
for (n, q, o, body), h in zip(gaps, hs):
    box(s, 0.75, y, 8.78, h, fill=LIGHT)
    badge(s, 0.87, y + 0.12, n, d=0.38, size=13)
    text(s, 1.35, y + 0.08, 1.8, h - 0.16, para(q, size=13, color=BLUE, bold=True))
    text(s, 3.25, y + 0.06, 5.3, h - 0.12, body)
    box(s, 8.65, y + (h - 0.4) / 2, 0.78, 0.4, fill=PALERED, margin=0.02,
        paras=[para("→ " + o, size=12, color=TITLE, bold=True, align="ctr")])
    y += h + 0.1
text(s, 0.75, 6.32, 6.5, 0.3, para("* in the studies we reviewed", size=10, color=GREY, italic=True))

# ================================================================ 5 Research Objective (goal = field problem, objectives = steps)
s = new_slide("Research Objective", notes=(
    "(45 s) The goal is the field problem: give agencies evidence on when and why adaptive and learned signal control "
    "pays off over the control already deployed, on real traffic. This study is one step towards it: one GDOT "
    "intersection, rule-based and linear-learning controllers, and a simulation built only from GDOT's own data. "
    "Three objectives. O1: build the simulation and check it against GDOT's controller log on days it was not tuned "
    "on, with pass rules fixed in advance. O2, when: rank the controllers on held-back real days by how busy the hour "
    "is, time of day and how uneven the traffic is. O3, why and does it hold: explain each win or loss by what the "
    "controller does and who waits, and check it across training runs, the worst-served movement and count errors. "
    "The two hypotheses were written down before any result."))
box(s, 0.75, 1.4, 8.78, 1.3, fill=BLUE, margin=0.18, paras=[
    para([("Goal: ", {"bold": True}), ("give agencies evidence on when and why adaptive and learned signal control "
                                       "pays off over the control already deployed, on real traffic", {})],
         size=16, color="FFFFFF"),
    para("This study: one GDOT intersection; rule-based and linear-learning controllers; a simulation built only "
         "from GDOT's ATSPM data", size=12, color="DCE6F2", italic=True, before=4)])
objs = [("O1", "Build & check", "Simulate a real intersection from ATSPM data only; check it against GDOT's controller "
                                "log on days it was not tuned on (pass rules fixed in advance)", "gap 1"),
        ("O2", "When", "Rank deployed, rule-based and learning controllers on held-back real days: by how busy the "
                       "hour is, time of day, how uneven the traffic is", "gaps 2, 3"),
        ("O3", "Why, and does it hold", "Explain each win or loss by what the controller does and who waits; check "
                                        "it across training runs, worst-served movement, count errors", "gap 4")]
for i, (n, t, d, g) in enumerate(objs):
    y = 2.88 + i * 0.92
    badge(s, 0.8, y + 0.12, n, d=0.55, size=13)
    text(s, 1.5, y + 0.05, 1.9, 0.7, para(t, size=14, color=BLUE, bold=True), anchor="m")
    text(s, 3.4, y, 5.05, 0.8, para(d, size=12), anchor="m")
    box(s, 8.55, y + 0.2, 0.98, 0.4, fill=PALERED, margin=0.02, paras=[para(g, size=11, color=TITLE, bold=True,
                                                                             align="ctr")])
box(s, 0.75, 5.7, 8.78, 0.9, fill=LIGHT, margin=0.15, paras=[
    para("What we expected (written before any result)", size=12, color=GREY, bold=True),
    para("In everyday traffic, the methods that react to traffic do about equally well; near capacity, they pull "
         "apart", size=13, color=BLUE, before=3)])

# ================================================================ 7 Dataset
s = new_slide("Dataset", notes=(
    "(30 s) One real intersection in Buckhead, Atlanta: West Paces Ferry Road at East Andrews and Slaton Drive, GDOT "
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

# ================================================================ 8 Calibration & Validation (v5: plain version)
# sources: atsc/sites/137/VALIDATION.md (criteria written before attempt 1; attempt 8: V1 34/35, V2 28/35, V5 pass,
# V3 18/35 reported); split.json (29 train / 20 validation days); README.md (reports used); 3 s ~ 1.5 cars at the HCM
# base 1,900 veh/h/lane (1.9 s per car); FHWA Traffic Analysis Toolbox Vol. III (2004): GEH < 5 on >= 85 % of links
s = new_slide("Calibration & Validation")
text(s, 0.75, 1.33, 4.3, 0.4, [para([("1  Set up ", {"bold": True, "color": BLUE, "size": 15}),
                                     ("from GDOT reports, 29 train days only", {"color": GREY, "size": 12})])])
table(s, 0.75, 1.78, 4.3, [
    ["GDOT report", "What it gives the simulation"],
    ["Turning Movement Counts", "How many cars, per movement, every 5 min"],
    ["Split Monitor", "GDOT's timing plans; how long a green waits for the next car"],
    ["Timing & Actuation", "Pedestrian pushes, how left-turners take gaps, timing of next signal 138"],
    ["Detector configuration", "Where the detectors are"]], colw=[1.6, 2.7], rowh=0.5, size=11, bold_first_col=True)
box(s, 0.75, 4.38, 4.3, 0.62, fill=PALERED, margin=0.1, paras=[
    para([("Found: ", {"bold": True}), ("side-street detectors count a queue leaving on green as one car, so those "
                                        "counts were corrected (backup)", {})], size=10.5, color=TITLE)])
text(s, 5.25, 1.33, 4.3, 0.4, [para([("2  Check ", {"bold": True, "color": BLUE, "size": 15}),
                                     ("on 20 days it never saw", {"color": GREY, "size": 12})])])
text(s, 5.25, 1.78, 4.28, 0.6, para("Run GDOT's real timing on each day's real counts, then compare with GDOT's own "
                                    "log (Split Monitor) for every side-street and left-turn phase in every plan: "
                                    "35 cases", size=11))
stats = [("34 / 35", "How long each green lasts", "within 3 s (about 1.5 cars)"),
         ("28 / 35", "Why each green ended", "no more cars vs. time ran out: within 15 points")]
for i, (big, t, d) in enumerate(stats):
    x = 5.25 + i * 2.19
    box(s, x, 2.5, 2.09, 1.85, fill=PALEBLUE, anchor="t", margin=0.08, paras=[
        para(big, size=26, color=BLUE, bold=True, align="ctr"),
        para(t, size=11.5, bold=True, align="ctr", before=2),
        para(d, size=10.5, color=GREY, align="ctr", before=2)])
box(s, 5.25, 4.45, 4.28, 0.55, fill="E8F5E9", margin=0.1, paras=[
    para([("✓ Accepted: ", {"bold": True, "color": "2E7D32"}),
          ("pass needs at least 28 of 35 (80 %) on both, and no stuck cars", {})], size=11)])
low = [("Why it works", [para("The real controller reacts to traffic, so its log records the traffic it saw. If "
                              "the simulated cars were wrong, the simulated greens would be too.", size=10.5)]),
       ("Why these numbers", [para("A judgement call, written before the first run and never changed in 8 attempts. "
                                   "3 s = about 1.5 cars. Same idea as FHWA's guide (85 % of cases within a "
                                   "tolerance, for traffic counts).", size=10.5)]),
       ("Limits", [para("Checks how the signal behaves, not delay itself", size=10.5, bullet="dash"),
                   para("Turn-arrow skips do not match yet (18/35)", size=10.5, bullet="dash", before=1),
                   para("Gap times were tuned to this same measure (on train days)", size=10.5, bullet="dash",
                        before=1)])]
for i, (t, body) in enumerate(low):
    x = 0.75 + i * 2.98
    box(s, x, 5.12, 2.82, 1.45, fill=LIGHT, anchor="t", margin=0.1,
        paras=[para(t, size=12, color=BLUE, bold=True)] + body)

# ================================================================ 9 Methods (v5: grouped by the slide-3 types)
s = new_slide("Methods Compared")
fams = [("Fixed-time", "preset schedule",
         [("Webster", "textbook fixed schedule, designed from train-day counts")]),
        ("Actuated", "detector-driven greens",
         [("GDOT plan", "deployed today, and checked against GDOT's log; inside a fixed cycle shared with the next "
                        "signal"),
          ("Actuated (no cycle)", "same controller and settings without the fixed cycle: a what-if, and the "
                                  "reference; same as GDOT plan at night")]),
        ("Adaptive: designed rule", "rule set by hand",
         [("MaxPressure", "green to the longest queue")]),
        ("Adaptive: learned from data", "same features, learn weights",
         [("LSTDQ", "least squares on recorded decisions; the base method"),
          ("Q-learning", "same model, updated after every decision"),
          ("ARS", "random search on the weights, directly on delay")])]
cw_, gp = 2.1, 0.127
for i, (t, sub, items) in enumerate(fams):
    x = 0.75 + i * (cw_ + gp)
    hl = i == 3
    box(s, x, 1.4, cw_, 4.0, fill=PALEBLUE if hl else LIGHT)
    text(s, x + 0.1, 1.48, cw_ - 0.2, 0.62, para(t, size=13.5, color=TITLE if hl else BLUE, bold=True), anchor="m")
    text(s, x + 0.1, 2.1, cw_ - 0.2, 0.3, para(sub, size=10, color=GREY, italic=True))
    y = 2.45
    h = {1: 1.4, 2: 1.45, 3: 0.98}[len(items)]
    for name, d in items:
        box(s, x + 0.08, y, cw_ - 0.16, h - 0.1, fill="FFFFFF", margin=0.07, anchor="t", paras=[
            para(name, size=12, color=BLUE, bold=True), para(d, size=10, before=1)])
        y += h
box(s, 0.75, 5.52, 8.78, 0.6, fill=PALEBLUE, margin=0.12, paras=[
    para([("How the learners decide: ", {"bold": True}),
          ("every second, score \"extend\" and \"end\" as a weighted sum of detector features (queue, time since "
           "last car, green so far), pick the higher; safety rules still apply. Base method LSTDQ: Sahachaiseree "
           "& Oguchi (2025)", {})], size=11, color=BLUE)])
box(s, 0.75, 6.2, 8.78, 0.42, fill=PALERED, margin=0.12, paras=[
    para("Same network, demand, detectors and safety rules for all: only the decision differs", size=13,
         color=TITLE, bold=True, align="ctr")])

# ================================================================ 11 Experiments (the student's list, corrected)
s = new_slide("Experiments", notes=(
    "(30 s) How the comparison was run. The measure is delay per vehicle: the time each car loses compared with "
    "driving freely, including waiting to enter, every hour. Each method is compared with actuated, paired by day; "
    "a tie means within 2 seconds per vehicle - a judgement call, but fixed before any result. Hours are grouped by "
    "how busy they are, time of day and how uneven the traffic is. As a what-if we also raised every count by 25 "
    "percent. The test days were held back and opened once under an analysis plan written beforehand. After that "
    "run we found four errors - in our controller engine, in scoring cars that never got in, in the saturation rate, "
    "and in which saved learner weights to use. The fixes were written down before rerunning, and both results are "
    "kept."))
items = [
    [("Measure: ", {"bold": True}), ("delay per vehicle (s) = time lost vs driving freely, incl. waiting to enter, "
                                     "every hour", {})],
    [("Days split by date: ", {"bold": True}), ("train 29 · development 20 · test 7 (held back)", {})],
    [("Learners: ", {"bold": True}), ("5 training runs each, trained on train days only", {})],
    [("Comparison: ", {"bold": True}), ("each method vs actuated, paired by day", {})],
    [("Tie ", {"bold": True}), ("= within 2 s/veh (or 5 %, whichever is larger): a judgement call, fixed before any "
                                "result", {})],
    [("When: ", {"bold": True}), ("hours grouped by how busy, time of day, how uneven the traffic is", {})],
    [("Why: ", {"bold": True}), ("cycle length, green time per direction, phases skipped, delay per street", {})],
    [("What-if: ", {"bold": True}), ("every count +25 % on 5 development days (learners trained on real counts only)",
                                     {})]]
text(s, 0.75, 1.45, 8.78, 4.1, [para(r, size=15, bullet="dot", before=10 if k else 0) for k, r in enumerate(items)])
box(s, 0.75, 5.65, 8.78, 0.85, fill=PALERED, margin=0.15, paras=[
    para([("Test days opened once ", {"bold": True}), ("under an analysis plan written beforehand; rerun once after "
                                                       "4 fixes registered before the rerun. Both results kept "
                                                       "(backup).", {})], size=13, color=TITLE)])

# ================================================================ 12 Results: real days  (O2)
# sources: INTERPRETATION.md section 0 and 1; TEST_PLAN.md "Amendment 1 results"; "days better than GDOT plan" is
# descriptive (INTERPRETATION.md section 1), not a registered test
s = new_slide("Results: Real Days", notes=(
    "(55 s) Here is the answer on the seven test days we held back. Delay per vehicle, lower is better. The deployed "
    "GDOT plan: 31.2 seconds. LSTDQ 25.3, MaxPressure 26.1, and the same GDOT controller without its fixed cycle "
    "24.9 - each better than the deployed plan on all 7 test days. So three methods cut delay by 5 to 6 seconds per "
    "vehicle, and one of them does no learning. Against that cycle-free controller, LSTDQ is a tie - shown "
    "statistically to be within 2 seconds. MaxPressure, Q-learning and ARS are not settled: the day-to-day spread is "
    "too large to call a tie or a difference. Webster's schedule is far behind because it is designed for a typical "
    "day and overflows on busy evenings."))
text(s, 0.75, 1.3, 8.78, 0.45, para("Three methods beat the deployed plan by 5-6 s per vehicle; one does no "
                                    "learning", size=14, color=TITLE, bold=True))
text(s, 0.75, 1.8, 8.78, 0.35, para([("Delay per vehicle (s), lower is better  ", {"bold": True, "color": BLUE}),
                                     ("· learners: average of 5 training runs", {"color": GREY})], size=12))
R = lambda t: [(t, {"bold": True})]  # noqa: E731
G = lambda t: [(t, {"color": MID})]  # noqa: E731
rows = [["Method", "Dev. (20 days)", "Test (7 days)", "Beats GDOT plan", "Test vs actuated"],
        [R("GDOT plan (deployed)"), "34.3", R("31.2"), "-", [("worse", {"color": TITLE})]],
        [R("Actuated (no fixed cycle)"), "25.3", R("24.9"), "7 of 7", "reference"],
        [R("LSTDQ"), "24.6", R("25.3"), "7 of 7", [("tie (shown)", {"bold": True, "color": "2E7D32"})]],
        ["MaxPressure", "27.6", "26.1", "7 of 7", "not settled"],
        ["ARS", "36.5", "30.4", "5 of 7", "not settled"],
        ["Q-learning", "31.5", "30.6", "5 of 7", "not settled"],
        [G("Webster (textbook timer)"), G("122.0"), G("117.7"), G("0 of 7"), G("worse")]]
table(s, 0.75, 2.2, 8.78, rows, colw=[2.78, 1.4, 1.3, 1.6, 1.7], rowh=0.42, size=12)
text(s, 0.75, 5.62, 8.78, 0.9, [
    para("Beats GDOT plan = test days with less delay than the deployed plan.  Tie = within 2 s/veh, shown "
         "statistically.  Not settled = day-to-day spread too large to call a tie or a difference.", size=10.5,
         color=GREY, italic=True),
    para("Against the same controller without its fixed cycle, no learner is clearly better.", size=13,
         color=BLUE, bold=True, before=6)])

# ================================================================ 13 Results: when (by condition + scaled-up demand)  (O2)
# sources: eval_test/analysis.md by time of day; INTERPRETATION.md section 5 (surge hours, post hoc) and 11 (sweep)
s = new_slide("Results: When", notes=(
    "(50 s) When does each method win? Test days, by time of day; green is the lowest delay in the row. In the "
    "morning peak all four adaptive methods beat actuated; at midday only LSTDQ does. Actuated wins the evening "
    "peak. At night LSTDQ and MaxPressure lose about 3 seconds - they hold long greens for very few cars - while "
    "Q-learning and ARS match actuated. In six hours with sudden side-street surges, picked after seeing the "
    "results, actuated reacts at once and does best by far. Bottom: a what-if on 5 development days with every count "
    "raised by 25 percent; the learners were trained on real counts only. Every adaptive method falls behind "
    "actuated. From plus 50 percent every controller's queues keep growing for much of the day, so we do not rank "
    "methods above plus 25 percent. The simple detector rule is the safest default."))
text(s, 0.75, 1.3, 8.78, 0.45, para("No method wins everywhere; the simple detector rule is the safest default",
                                    size=15, color=TITLE, bold=True))
B = lambda t: [(t, {"bold": True, "color": "2E7D32"})]  # noqa: E731
hdr = ["Test days, s/veh", "GDOT plan", "Actuated", "MaxPressure", "LSTDQ", "Q-learning", "ARS"]
cw = [2.08, 1.08, 1.05, 1.27, 1.0, 1.2, 1.1]
rows = [hdr,
        ["Night 00-06", "8.2", "8.2", "11.2", "11.6", B("8.1"), "8.5"],
        ["Morning peak 06-10", "26.1", "22.8", "21.2", B("21.1"), "21.8", "21.9"],
        ["Midday 10-15", "35.0", "25.8", "26.0", B("24.2"), "27.9", "26.8"],
        ["Evening peak 15-19", "34.0", B("27.8"), "32.0", "30.6", "42.2", "38.2"],
        ["6 surge hours*", "85.4", B("39.1"), "74.8", "58.0", "114.5", "95.7"]]
table(s, 0.75, 1.85, 8.78, rows, colw=cw, rowh=0.38, size=12, bold_first_col=True)
text(s, 0.75, 4.15, 8.78, 0.3, para("* hours with sudden side-street surges, picked after seeing the results",
                                    size=10, color=GREY, italic=True))
text(s, 0.75, 4.5, 8.78, 0.35, para([("Scaled-up demand (what-if)  ", {"bold": True, "color": BLUE}),
                                     ("· 5 development days; learners trained on real counts only",
                                      {"color": GREY, "size": 11})], size=14))
rows = [["5 dev. days, s/veh", "GDOT plan", "Actuated", "MaxPressure", "LSTDQ", "Q-learning", "ARS"],
        ["Real counts", "27.4", "24.5", B("22.8"), "23.3", "26.7", "27.3"],
        ["Every count +25 %", "63.1", B("45.0"), "51.3", "51.7", "76.9", "100.4"]]
table(s, 0.75, 4.9, 8.78, rows, colw=cw, rowh=0.38, size=12, bold_first_col=True, band=(PALERED, "FBF0F1"))
text(s, 0.75, 6.1, 8.78, 0.45, para("From +50 % every controller's queues keep growing for much of the day, so "
                                    "methods are not ranked above +25 %.", size=10.5, color=GREY, italic=True))

# ================================================================ 14 Main findings: who waits
s = new_slide("Main Findings: Who Waits", notes=(
    "(50 s) This is the most important slide. Same test days, delay split into the main street, West Paces Ferry, "
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

# ================================================================ 15 Conclusion: answer the objectives and hypotheses
s = new_slide("Conclusion", notes=(
    "(45 s) Back to the objectives. O1: a simulation built only from ATSPM data passed the check against GDOT's own "
    "controller log on 20 days it was not tuned on - for controller behaviour, not delay itself. O2: at this "
    "intersection the gain over the deployed timing needs no learning; against the same controller without its fixed "
    "cycle, the best linear learner, LSTDQ, only ties. O3: what learning changes is who waits, and the simple rule "
    "is more robust at night, in surges and with more traffic; why is not yet tested. Hypotheses: H1 is only partly "
    "supported, because only LSTDQ is shown to tie. H2 cannot be tested on real days at this site, because it is "
    "rarely near capacity, so it moves to future work. Limitations as listed; the main ones are that validation "
    "checks behaviour not delay, and the test days were run twice."))
box(s, 0.75, 1.4, 8.78, 2.55, fill=PALERED, margin=0.15, anchor="t", paras=[
    para("Findings (one site, 137)", size=14, color=TITLE, bold=True),
    para([("O1  ", {"bold": True}), ("Simulation from ATSPM only, accepted against GDOT's log on 20 unseen days "
                                     "(controller behaviour, not delay)", {})], size=13, before=5),
    para([("O2  ", {"bold": True}), ("Gain over the deployed timing (31.2 → 24.9-26.1 s) needs no learning; against "
                                     "the same controller without its fixed cycle, LSTDQ only ties (25.3 vs 24.9 s)",
                                     {})], size=13, before=5),
    para([("O3  ", {"bold": True}), ("Learning changes who waits; the simple rule is more robust at night, in surges "
                                     "and with +25 % traffic (why: not yet tested)", {})], size=13, before=5),
    para([("Expected  ", {"bold": True}), ("everyday traffic, a tie: partly, only LSTDQ is shown to tie.  Near "
                                           "capacity, a split: not testable on real days here (rarely that busy)",
                                           {})], size=12.5, before=8)])
box(s, 0.75, 4.1, 8.78, 2.45, fill=LIGHT)
text(s, 0.9, 4.17, 8.5, 0.4, para("Limitations", size=15, color=BLUE, bold=True))
lims = ["Validation checks controller behaviour, not delay itself",
        "Test days run twice (rerun after fixes registered before the rerun)",
        "Side-street demand is a corrected estimate of GDOT's counts",
        "Delay scored around this intersection: the benefit of timing it with the next signal is not fully counted",
        "One site; our own controller engine; left arrows served more often than in the field"]
text(s, 0.9, 4.57, 8.5, 1.95, [para(l, size=13, bullet="dot", before=5 if k else 0) for k, l in enumerate(lims)])

# ================================================================ 16 Future work (ordered, each tied to an objective)
s = new_slide("Future Work", notes=(
    "(25 s) Ordered, each tied to an objective and doable before the thesis. First, the count-error test - the open "
    "part of O3: does the ranking survive errors in the counts, especially the corrected side-street counts. Second, "
    "check the simulation on the 7 test days against GDOT's log. Third, test the two likely causes of who waits. "
    "Fourth, H2: train the learners on heavier traffic and compare only where every controller keeps its queues "
    "under control. If time allows: one traffic-outcome check from ATSPM, intersection 7065, and DQN as a neural "
    "reference."))
fw = [["Next step", "Tied to", "Purpose"],
      [[("1  Count-error test", {"bold": True})], "O3", "Does the ranking survive errors in the counts (esp. the "
                                                         "corrected side-street counts)?"],
      [[("2  Simulation check on the 7 test days", {"bold": True})], "O1",
       "Compare with GDOT's log on days never used in development"],
      [[("3  Test the two \"who waits\" causes", {"bold": True})], "O3",
       "Queue the controllers see vs true queue; reward weighted to the side street"],
      [[("4  Train learners on heavier traffic", {"bold": True})], "O2",
       "Compare only where every controller keeps queues under control"],
      [[("If time: ", {"bold": True}), ("ATSPM outcome check (Split Failure); SIG 7065; DQN", {})], "O1, O2",
       "Traffic outcomes, a second site, a neural reference"]]
table(s, 0.75, 1.45, 8.78, fw, colw=[3.55, 0.95, 4.28], rowh=0.72, size=12)
box(s, 0.75, 5.95, 8.78, 0.55, fill=LIGHT, margin=0.15, paras=[
    para("7065 differs from 137 in coordination and saturation at once: a consistency check, not a causal "
         "separation", size=11, color=GREY, italic=True)])

# ================================================================ Backup slides
s = new_slide("Backup: Validation Attempts", notes="(backup, 0 s) Only if asked. Each change was justified by train-day GDOT data "
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

s = new_slide("Backup: Detector Undercount", notes="(backup, 0 s) Only if asked. Found while diagnosing short side-street greens in "
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

s = new_slide("Backup: Prior Simulations", notes="(backup, 0 s) Only if asked. Fair contrast: they calibrate or build the simulation "
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

s = new_slide("Backup: Inputs Not From GDOT", notes="(backup, 0 s) Only if asked. Disclosed assumptions.")
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

# ---------------------------------------------------------------- backup: first test run vs rerun (TEST_PLAN.md)
s = new_slide("Backup: Test Run and Rerun", notes=(
    "(backup, 0 s) Only if asked. The test days were opened once under the registered plan. After that run an independent review "
    "found four errors; the fixes were written down before the rerun and justified by signal-controller rules, a "
    "scoring error and train-day measurements, not by the test results. Both results are reported. The rerun is a "
    "second look at the same days, so it is not a clean held-out test; fresh days are needed to confirm the tie."))
rows = [["Test days, s/veh", "First run", "Verdict vs actuated", "Rerun (after fixes)", "Verdict vs actuated"],
        ["Actuated (no fixed cycle)", "25.2", "reference", "24.9", "reference"],
        ["LSTDQ", "30.6", "not settled", "25.3", "tie (shown)"],
        ["MaxPressure", "26.1", "not settled", "26.1", "not settled"],
        ["ARS", "30.8", "not settled", "30.4", "not settled"],
        ["Q-learning", "35.3", "not settled", "30.6", "not settled"],
        ["GDOT plan (deployed)", "31.3", "not settled", "31.2", "worse"],
        ["Webster", "94.0", "worse", "117.7", "worse"]]
table(s, 0.75, 1.45, 8.78, rows, colw=[2.4, 1.2, 1.75, 1.68, 1.75], rowh=0.4, size=12, bold_first_col=True)
text(s, 0.75, 4.85, 8.78, 1.7, [
    para("Fixes registered before the rerun:", size=13, color=BLUE, bold=True),
    para("Engine: side-street phases started even with no car waiting (now only when a car calls them)",
         size=12, bullet="dot", before=3),
    para("Scoring: cars that never got into the network are now counted", size=12, bullet="dot", before=2),
    para("Saturation rate: measured in the simulation on train days (queue estimate, Webster)", size=12,
         bullet="dot", before=2),
    para("Learner weights: the saved round with the lowest delay on train days, not the last round", size=12,
         bullet="dot", before=2)])

# ---------------------------------------------------------------- backup: how the learner decides (v3 slide 10)
s = new_slide("Backup: How the Learner Decides", notes=(
    "(backup, 0 s) Only if asked. Every second the learned controller turns detector readings into a few features per phase: how many cars "
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


# ---------------------------------------------------------------- move the student's approach slide after Research Objective
sldIdLst.remove(_approach_id)
sldIdLst.insert(5, _approach_id)

# ---------------------------------------------------------------- speaker notes = SCRIPT_v5.md (slides 1-15)
import pathlib
_sc = (pathlib.Path(__file__).parent / "SCRIPT_v5.md").read_text().split("## Backup")[0]
_secs = re.split(r"(?m)^## Slide (\d+) — [^\n]*\(~(\d+) s, [^)]*\)\s*$", _sc)
for k in range(1, len(_secs), 3):
    n, sec, body = int(_secs[k]), _secs[k + 1], _secs[k + 2]
    lines = [l.strip() for l in body.strip().split("\n\n") if l.strip() and not l.startswith("---")]
    lines = [l.replace("*Point at:*", "[Point at:") + "]" if l.startswith("*Point at:*") else l for l in lines]
    prs.slides[n - 1].notes_slide.notes_text_frame.text = f"(~{sec} s) " + "\n\n".join(lines)

prs.save(OUT)
print("saved", OUT, len(prs.slides), "slides")

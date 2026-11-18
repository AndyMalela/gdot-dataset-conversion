"""v12 = v11 + statistical values, Q-learning/ARS (and Webster) back on the results slides.
v11 = the student's eSocLab_Midterm-v10-edit.pptx (kept unchanged) with slides 12-16 (Experiments, Results: Real
Days, Results: When, Main Findings: Who Waits, Conclusion) redone with fewer words and ~24 pt text. Everything removed
from a slide is kept in that slide's speaker notes (spoken part first, then a bracketed "not read aloud" block).
Numbers: atsc/sites/137/INTERPRETATION.md v3, TEST_PLAN.md amendment-1 results, eval_test/analysis.md.
Usage: uv run --no-project --with python-pptx --with lxml python edit_v11.py eSocLab_Midterm-v10-edit.pptx eSocLab_Midterm-v11.pptx"""
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

# ================================================================ 12 Experiments
s = find("Experiments")
clear(s)
c = Canvas(s)
items = [[("Measure: ", {"bold": True, "color": BLUE}), ("delay per car (s), lower is better", {})],
         [("Days: ", {"bold": True, "color": BLUE}), ("train 29 · develop 20 · test 7", {})],
         [("Learners: ", {"bold": True, "color": BLUE}), ("5 training runs each", {})],
         [("Tie: ", {"bold": True, "color": BLUE}), ("within 2 s, set before any result", {})],
         [("Compare by: ", {"bold": True, "color": BLUE}), ("time of day, how busy, surges", {})],
         [("What-if: ", {"bold": True, "color": BLUE}), ("every count +25 %", {})],
         [("Statistics: ", {"bold": True, "color": BLUE}), ("paired by day; tie = equivalence test; "
                                                            "difference = t-test (Holm); p < 0.05", {})]]
c.text(L, 1.4, W, 4.0, [para(r, 22, bullet=True, before=8 if k else 0) for k, r in enumerate(items)])
c.box(L, 5.5, W, 0.95, PALERED, paras=[
    para("Test days opened once; rerun once after 4 written-down fixes; both results kept", 22, TITLE, bold=True)])
s.notes_slide.notes_text_frame.text = (
    "(~35 s) We measure delay: the seconds each car loses compared with driving freely, including waiting to enter. "
    "Lower is better. For cars heading west, it includes their wait at signal 138.\n\n"
    "Days are split by date: 29 to train, 20 to develop, 7 held back to test. A tie means within 2 seconds, fixed "
    "before any result.\n\n"
    "Statistics were planned before the results: each method is compared with the no-cycle controller day by day. "
    "A tie needs an equivalence test, and a difference a t-test corrected for testing six methods at once; both at "
    "p below 0.05. With only 7 test days, many comparisons stay not settled.\n\n"
    "One honest note: we opened the test days once, under a plan written beforehand. Then we found four errors in "
    "our setup. We wrote the fixes down, reran once, and keep both results.\n\n"
    "[Not read aloud - moved off the slide: each learner is trained 5 times, on training days only, and results are "
    "the average of the 5. Each method is compared with the no-cycle controller, paired day by day. A tie is within "
    "2 s/veh or 5 %, whichever is larger - a judgement call. Conditions: time of day, how busy the hour is, how "
    "uneven the traffic is, sudden surges. To explain why: cycle length, green time per direction, phases skipped, "
    "delay per street. The what-if raises every count by 25 % on 5 development days; the learners trained on real "
    "counts only.]")

# ================================================================ 13 Results: Real Days
s = find("Results: Real Days")
clear(s)
c = Canvas(s)
c.text(L, 1.3, W, 0.85, [para("Three methods beat the deployed plan by 5-6 s; one does no learning", 24, TITLE,
                               bold=True)])
rows = [["Test days", "Delay (s)", "Beats GDOT", "vs no-cycle", "p diff.", "p tie"],
        ["GDOT plan", "31.2", "-", ("worse", {"color": TITLE}), ("0.046", {"bold": True}), "0.97"],
        ["No cycle (actuated)", ("24.9", {"bold": True}), "7 of 7", "reference", "-", "-"],
        ["LSTDQ", ("25.3", {"bold": True}), "7 of 7", ("tie", WIN), "1.00", ("0.026", WIN)],
        ["MaxPressure", "26.1", "7 of 7", "not settled", "1.00", "0.36"],
        ["Q-learning", "30.6", "5 of 7", "not settled", "0.31", "0.86"],
        ["ARS", "30.4", "5 of 7", "not settled", "0.19", "0.91"],
        ["Webster", "117.7", "0 of 7", ("worse", {"color": TITLE}), ("0.001", {"bold": True}), "1.00"]]
c.table(L, 2.15, rows, colw=[2.62, 1.2, 1.4, 1.56, 1.0, 1.0], rowh=0.44, size=19, head_size=16)
c.text(L, 5.75, W, 0.5, [para("Lower is better · learners: average of 5 runs · p diff.: paired t-test, Holm-corrected "
                              "· p tie: equivalence test (within 2 s) · significant if p < 0.05", 13, GREY,
                              italic=True)])
c.text(L, 6.2, W, 0.45, [para("No learner clearly beats the no-cycle controller", 22, BLUE, bold=True)])
s.notes_slide.notes_text_frame.text = (
    "(~40 s) On the 7 test days, the deployed GDOT plan has 31.2 seconds of delay per car. The same controller "
    "without its fixed cycle: 24.9. LSTDQ: 25.3. MaxPressure: 26.1. All three beat the deployed plan on all 7 days. "
    "So three methods cut delay by 5 to 6 seconds, and one of them does no learning at all.\n\n"
    "Against that no-cycle controller, LSTDQ is a tie: within 2 seconds, with p 0.026. The deployed plan is "
    "significantly worse, p 0.046. The other two learners, Q-learning at 30.6 and ARS at 30.4, beat the deployed "
    "plan on 5 of 7 days, but against the no-cycle controller they, and MaxPressure, are not settled: the days vary "
    "too much to call a tie or a difference. Webster's textbook timer is far behind, at 117.7.\n\n"
    "[Point at: the first three rows, then the p columns.]\n\n"
    "[Not read aloud: Webster is designed for a typical day and overflows on busy evenings. p diff. = paired t-test "
    "on the daily delay ratio, Holm-corrected over six methods; p tie = equivalence test, margin 2 s/veh or 5 %, "
    "whichever is larger. Development days (20), s/veh: GDOT plan 34.3, no-cycle 25.3, LSTDQ 24.6, MaxPressure 27.6, "
    "Q-learning 31.5, ARS 36.5, Webster 122.0.]")

# ================================================================ 14 Results: When
s = find("Results: When")
clear(s)
c = Canvas(s)
c.text(L, 1.3, W, 0.85, [para("No method wins everywhere: the simple rule is the safest default", 24, TITLE,
                               bold=True)])
rows = [["Delay (s)", "GDOT plan", "No cycle", "MaxPres.", "LSTDQ", "Q-learn.", "ARS"],
        ["Night", "8.2", "8.2", "11.2", "11.6", ("8.1", WIN), "8.5"],
        ["Morning", "26.1", "22.8", "21.2", ("21.1", WIN), "21.8", "21.9"],
        ["Midday", "35.0", "25.8", "26.0", ("24.2", WIN), "27.9", "26.8"],
        ["Evening", "34.0", ("27.8", WIN), "32.0", "30.6", "42.2", "38.2"],
        ["Surges*", "85.4", ("39.1", WIN), "74.8", "58.0", "114.5", "95.7"],
        ["+25 %**", "63.1", ("45.0", WIN), "51.3", "51.7", "76.9", "100.4"]]
c.table(L, 2.2, rows, colw=[1.7, 1.25, 1.18, 1.2, 1.1, 1.25, 1.1], rowh=0.5, size=20, head_size=16)
c.text(L, 5.85, W, 0.6, [
    para("Green = lowest in the row · * 6 side-street surge hours, picked after seeing the results · ** what-if: "
         "every count +25 %, 5 development days · by condition: descriptive, no tests", 13, GREY, italic=True)])
s.notes_slide.notes_text_frame.text = (
    "(~45 s) When does each method win? At night, Q-learning is lowest, 8.1, with the no-cycle controller and the "
    "deployed plan at 8.2; LSTDQ and MaxPressure lose about 3 seconds. In the "
    "morning peak, LSTDQ is lowest: 21.1. At midday, LSTDQ again: 24.2. In the evening peak, the no-cycle controller "
    "wins: 27.8. In six hours with sudden side-street surges, picked after seeing the results, it wins clearly: "
    "39.1, against 58.0 for LSTDQ and over 74 for the others. With every count up by a quarter, on 5 development "
    "days the learners never trained on, the no-cycle controller has 45.0; MaxPressure and LSTDQ about 51; "
    "Q-learning and ARS fall far behind.\n\n"
    "No method wins everywhere. The simple rule is the safest default.\n\n"
    "[Not read aloud - full numbers moved off the slide, s/veh, in the order GDOT plan / no-cycle / MaxPressure / "
    "LSTDQ / Q-learning / ARS. Test days: night 00-06 8.2/8.2/11.2/11.6/8.1/8.5; morning peak 06-10 "
    "26.1/22.8/21.2/21.1/21.8/21.9; midday 10-15 35.0/25.8/26.0/24.2/27.9/26.8; evening peak 15-19 "
    "34.0/27.8/32.0/30.6/42.2/38.2; 6 surge hours 85.4/39.1/74.8/58.0/114.5/95.7. What-if on 5 development days: "
    "real counts 27.4/24.5/22.8/23.3/26.7/27.3; every count +25 % 63.1/45.0/51.3/51.7/76.9/100.4. From +50 % every "
    "controller's queues keep growing for much of the day, so methods are not ranked above +25 %. Green on the "
    "slide = lowest in the row. These by-condition numbers are descriptive: no statistical test.]")

# ================================================================ 15 Main Findings: Who Waits
s = find("Main Findings: Who Waits")
clear(s)
c = Canvas(s)
RED_ = {"bold": True, "color": RED}
rows = [["Test days, delay (s)", "Main street", "Side streets", ""],
        ["GDOT plan", "18.2", ("49.6", RED_), "favours main"],
        ["No cycle (actuated)", "24.7", "25.1", "shares evenly"],
        ["LSTDQ", "19.2", ("33.8", RED_), "cuts side waits"],
        ["MaxPressure", "19.2", ("35.9", RED_), ""],
        ["Q-learning", "22.8", ("41.5", RED_), ""],
        ["ARS", "27.7", ("34.2", RED_), ""]]
c.table(L, 1.35, rows, colw=[3.0, 1.7, 1.78, 2.3], rowh=0.48, size=20, head_size=17)
c.text(L, 4.75, W, 0.3, [para("Main street = W. Paces Ferry, 58 % of cars", 13, GREY, italic=True)])
c.box(L, 5.15, W, 1.25, PALEBLUE, paras=[
    para([("Likely why (not yet tested): ", {"bold": True}),
          ("learners are rewarded per car, and most cars are on the main street; side streets have only stop-line "
           "detectors", {})], 20, BLUE)])
s.notes_slide.notes_text_frame.text = (
    "(~40 s) Who waits? Test days, delay per car. The deployed GDOT plan favours the main street: 18 seconds there, "
    "50 on the side streets. LSTDQ keeps the main street at 19 and cuts the side streets to 34, about 16 seconds "
    "less. The no-cycle controller shares the wait evenly: 25 on both.\n\n"
    "MaxPressure and the other learners also make the side streets wait longer: 34 to 42 seconds there, against 19 "
    "to 28 on the main street. "
    "So LSTDQ and the no-cycle controller have about the same average, but different people wait.\n\n"
    "Why? Our likely explanation, not yet tested: the learners are rewarded per car, and 58 percent of cars are on "
    "the main street. And the side streets only have detectors at the stop line, so a long side queue is mostly "
    "invisible.\n\n"
    "[Point at: the red side-street column.]")

# ================================================================ 16 Conclusion
s = find("Conclusion")
clear(s)
c = Canvas(s)
c.box(L, 1.35, W, 2.75, PALERED, anchor="t", margin=0.2, paras=[
    para("Findings (one intersection)", 24, TITLE, bold=True, before=4),
    para([("O1  ", {"color": RED}), ("Simulation passes its check on 20 unseen days", {})], 22, bold=False,
         before=8),
    para([("O2  ", {"color": RED}), ("Beating today's timing needs no learning", {})], 22, before=6),
    para([("O3  ", {"color": RED}), ("Learning changes who waits", {})], 22, before=6),
    para("Expected a tie: only LSTDQ tied · near capacity: not testable here", 20, GREY, italic=True, before=8)])
c.box(L, 4.3, W, 2.1, LIGHT, anchor="t", margin=0.2, paras=[
    para("Limitations", 24, BLUE, bold=True, before=4),
    para("Checks signal behaviour, not delay", 22, bullet=True, before=6),
    para("Test days run twice", 22, bullet=True, before=3),
    para("One intersection", 22, bullet=True, before=3)])
s.notes_slide.notes_text_frame.text = (
    "(~35 s) For this one intersection. One: the simulation, built only from the agency's data, passed its check on "
    "unseen days; it checks how the signal behaves, not delay itself. Two: beating today's timing needs no learning - "
    "the deployed plan has 31.2 seconds, the same controller without its fixed cycle 24.9. We expected the learning "
    "methods to at least tie the best simple rule; only LSTDQ did, at 25.3. Three: learning changes who waits.\n\n"
    "Whether methods split apart near capacity, we cannot test on real days here: this intersection is rarely that "
    "busy.\n\n"
    "[Not read aloud - moved off the slide: the simple rule is more robust at night, in surges and with +25 % "
    "traffic; why the learners shift the wait is not yet tested. Limitations: the check covers controller behaviour, "
    "not delay itself; the test days were run twice, the rerun after fixes registered before it; side-street demand "
    "is a corrected estimate of GDOT's counts; delay is scored around this intersection, so the benefit of timing it "
    "with the next signal is not fully counted; one site; our own controller engine; left arrows are served more "
    "often than in the field.]")

prs.save(OUT)
print("saved", OUT)

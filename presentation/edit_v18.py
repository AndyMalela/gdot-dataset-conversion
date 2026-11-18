"""v18 = student's v17 edit + results boiled down: one merged 'Results: Real Days' (all day + main/side + verdict, no
MaxPressure/Webster), 'Results: When' (no-cycle, LSTDQ, Q-learning, ARS; honesty footnotes back), Who Waits merged
away; after the Conclusion: Appendix 'Learners Compared', 'MaxPressure and Webster', 'All Numbers'. Conclusion next
step wording; Methods list marks MaxPressure/Webster as appendix. Numbers: INTERPRETATION.md v3, TEST_PLAN.md
amendment 1, eval_test/analysis.md.
Usage: uv run --no-project --with python-pptx --with lxml python edit_v18.py eSocLab_Midterm-v17-edit.pptx eSocLab_Midterm-v18.pptx"""
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
RED_ = {"bold": True, "color": RED}


_NEWN = [950]


def new_after(src_slide, title, after_title):
    from pptx.opc.packuri import PackURI
    ns = prs.slides.add_slide(src_slide.slide_layout)
    _NEWN[0] += 1
    ns.part.partname = PackURI(f"/ppt/slides/slide{_NEWN[0]}.xml")   # avoid clashing with existing slideN.xml
    for sh in list(ns.shapes):
        sh._element.getparent().remove(sh._element)
    for sh in src_slide.shapes:
        if sh.name in ("Title 1", "Slide Number Placeholder 0"):
            ns.shapes._spTree.append(copy.deepcopy(sh._element))
    t = next(sh for sh in ns.shapes if sh.name == "Title 1")
    rs = t.text_frame.paragraphs[0].runs
    rs[0].text = title
    for r in rs[1:]:
        r._r.getparent().remove(r._r)
    lst = prs.slides._sldIdLst
    nid = list(lst)[-1]
    lst.remove(nid)
    pos = [k for k, sl in enumerate(prs.slides) if title_of(sl) == after_title][0]
    lst.insert(pos + 1, nid)
    return ns


def set_title(slide, title):
    t = next(sh for sh in slide.shapes if sh.name == "Title 1")
    rs = t.text_frame.paragraphs[0].runs
    rs[0].text = title
    for r in rs[1:]:
        r._r.getparent().remove(r._r)


def delete(slide):
    lst = prs.slides._sldIdLst
    for sid in list(lst):
        if prs.part.related_part(sid.rId) is slide.part:
            prs.part.drop_rel(sid.rId)
            lst.remove(sid)
            return


# ================================================================ Results: Real Days (merged with Who Waits)
s = find("Results")
clear(s)
set_title(s, "Results: Real Days")
c = Canvas(s)
rows = [["Test days, delay (s)", "All day", "Main street", "Side streets", "vs no-cycle"],
        [("GDOT plan (real)", {"color": TITLE}), "31.2", "18.2", ("49.6", RED_), ("worse", {"color": TITLE})],
        ["No cycle (actuated)", ("24.9", WIN), "24.7", "25.1", "reference"],
        ["LSTDQ", ("25.3", WIN), "19.2", ("33.8", RED_), ("tie", WIN)],
        ["Q-learning", "30.6", "22.8", ("41.5", RED_), "not settled"],
        ["ARS", "30.4", "27.7", ("34.2", RED_), "not settled"]]
c.table(L, 1.4, rows, colw=[2.78, 1.35, 1.55, 1.6, 1.5], rowh=0.55, size=20, head_size=16)
c.text(L, 4.85, W, 0.6, [para("Lower is better · learners: average of 5 runs · tie = shown within 2 s (p = 0.026) · "
                              "not settled = days vary too much to call · main street = W. Paces Ferry, 58 % of cars",
                              13, GREY, italic=True)])
c.box(L, 5.55, W, 0.95, PALEBLUE, paras=[
    para("No learning needed to beat today's plan; learning changes who waits", 22, BLUE, bold=True)])
s.notes_slide.notes_text_frame.text = (
    "(~45 s) On the 7 test days, the real plan has 31.2 seconds of delay per car, and its side streets wait 50. "
    "The same controller without its fixed cycle: 24.9, shared evenly, 25 on both. LSTDQ ties it at 25.3, but by "
    "keeping the main street fast and making the side streets wait 34. Q-learning and ARS are about 5 seconds behind "
    "and not settled against the no-cycle controller.\n\n"
    "So beating today's plan needs no learning, and learning changes who waits. Likely why, not yet tested: the "
    "learners are rewarded per car, most cars are on the main street, and the side streets only have stop-line "
    "detectors.\n\n"
    "[Point at: the All day column, then the red side-street numbers.]\n\n"
    "[Not read aloud: all three, LSTDQ, Q-learning and ARS, have less delay than the real plan on average (LSTDQ on "
    "7 of 7 days, Q-learning and ARS on 5 of 7). Real plan vs no-cycle: worse, p 0.046 (paired t-test, "
    "Holm-corrected). LSTDQ tie: equivalence test p 0.026. Development days: real plan 34.3, no-cycle 25.3, LSTDQ "
    "24.6, Q-learning 31.5, ARS 36.5. MaxPressure and Webster: appendix.]")

# ================================================================ Results: When
s = find("Results: Time of Day Difference")
clear(s)
set_title(s, "Results: When")
c = Canvas(s)
c.text(L, 1.3, W, 0.5, [para("No method wins everywhere", 24, TITLE, bold=True)])
rows = [["Delay (s)", "No cycle", "LSTDQ", "Q-learning", "ARS"],
        ["Night", "8.2", "11.6", ("8.1", WIN), "8.5"],
        ["Morning peak", "22.8", ("21.1", WIN), "21.8", "21.9"],
        ["Evening peak", ("27.8", WIN), "30.6", "42.2", "38.2"],
        ["Surges*", ("39.1", WIN), "58.0", "114.5", "95.7"],
        ["+25 % traffic**", ("45.0", WIN), "51.7", "76.9", "100.4"]]
c.table(L, 1.95, rows, colw=[2.78, 1.5, 1.5, 1.5, 1.5], rowh=0.55, size=22, head_size=18)
c.text(L, 5.4, W, 0.8, [para("Green = lowest in the row · * 6 hours with sudden side-street surges, picked after "
                             "seeing the results · ** what-if: every count +25 %, on 5 development days · "
                             "descriptive, no statistical tests", 13, GREY, italic=True)])
s.notes_slide.notes_text_frame.text = (
    "(~35 s) No method wins everywhere. LSTDQ is best in the morning peak, 21.1. But the simple no-cycle rule wins "
    "the evening peak, and clearly in six hours with sudden side-street surges, picked after seeing the results: "
    "39.1 against 58.0 for LSTDQ. With a quarter more traffic, a what-if on development days, it is also best: "
    "45.0 against 51.7. Q-learning and ARS are best at night but fall far behind when traffic is heavy.\n\n"
    "[Not read aloud: midday (10-15 h): no-cycle 25.8, LSTDQ 24.2, Q-learning 27.9, ARS 26.8; real plan 35.0. "
    "Real plan by row: night 8.2, morning 26.1, evening 34.0, surges 85.4, +25 % 63.1. Night = 00-06 h, morning "
    "06-10, evening peak 15-19. From +50 % every controller's queues keep growing for much of the day, so methods "
    "are not ranked above +25 %. MaxPressure and Webster: appendix.]")

# ================================================================ Who Waits: merged into Results -> delete
delete(find("Results: Who Waits"))

# ================================================================ Learners Compared -> appendix after Conclusion
lc = find("Learners Compared")
set_title(lc, "Appendix: Learners Compared")
sub = next(sh for sh in lc.shapes if sh.has_text_frame and sh.text_frame.text.startswith("Same inputs"))
sub.text_frame.paragraphs[0].runs[0].text = "Same inputs; how they learn decides the result"
for r in sub.text_frame.paragraphs[0].runs[1:]:
    r._r.getparent().remove(r._r)
lst = prs.slides._sldIdLst
lc_id = next(sid for sid in lst if prs.part.related_part(sid.rId) is lc.part)
lst.remove(lc_id)
pos = [k for k, sl in enumerate(prs.slides) if title_of(sl) == "Conclusion"][0]
lst.insert(pos + 1, lc_id)
lc.notes_slide.notes_text_frame.text = (
    "(appendix) " + lc.notes_slide.notes_text_frame.text.replace("(~45 s) ", "").replace(
        "The three learners get the same detector inputs and the same kind of linear model.",
        "The three learners get the same detector inputs. LSTDQ and Q-learning learn the same linear model; ARS "
        "learns a decision rule directly."))

# ================================================================ Appendix: MaxPressure and Webster
src = find("Results: When")
ap = new_after(src, "Appendix: MaxPressure, Webster", "Appendix: Learners Compared")
c = Canvas(ap)
rows = [["Test days, delay (s)", "MaxPressure", "Webster", "No cycle (ref.)"],
        ["All day", "26.1", "117.7", "24.9"],
        ["vs no-cycle", "not settled", ("worse (p 0.001)", {"color": TITLE}), "reference"],
        ["Days beating real plan", "7 of 7", "0 of 7", "7 of 7"],
        ["Night", "11.2", "23.1", "8.2"],
        ["Morning peak", "21.2", "30.6", "22.8"],
        ["Evening peak", "32.0", "42.7", "27.8"],
        ["Surges* / +25 %**", "74.8 / 51.3", "- / 902.6", "39.1 / 45.0"],
        ["Main / side street", "19.2 / 35.9", "-", "24.7 / 25.1"]]
c.table(L, 1.35, rows, colw=[2.9, 2.0, 2.0, 1.88], rowh=0.5, size=18, head_size=16)
c.text(L, 5.95, W, 0.6, [para("MaxPressure: green to the longest queue (Varaiya 2013). Webster: textbook fixed "
                              "timer (Webster 1958), built for a typical day; overflows on busy evenings. * picked "
                              "after seeing the results · ** what-if on 5 development days", 12, GREY, italic=True)])
ap.notes_slide.notes_text_frame.text = (
    "(appendix) If asked about MaxPressure: it beats the real plan on all 7 test days, 26.1 seconds, but is not "
    "settled against the no-cycle controller (p 0.36 for a tie, 1.00 for a difference); it does well in the morning "
    "but worst in surges, 74.8. Webster, the textbook fixed timer: 117.7 seconds, far worse (p 0.001); it is "
    "designed for a typical day and overflows in the evening (hours 19-24: 344.9 s/veh). It shows how a weak "
    "baseline would make every method look like a big win. Development days: MaxPressure 27.6, Webster 122.0.")

# ================================================================ Appendix: All Numbers
an = new_after(src, "Appendix: All Numbers", "Appendix: MaxPressure, Webster")
c = Canvas(an)
rows = [["Test days", "Delay (s)", "Beats real plan", "vs no-cycle", "p diff.", "p tie"],
        ["GDOT plan (real)", "31.2", "-", "worse", "0.046", "0.97"],
        ["No cycle (actuated)", "24.9", "7 of 7", "reference", "-", "-"],
        ["LSTDQ", "25.3", "7 of 7", "tie", "1.00", "0.026"],
        ["MaxPressure", "26.1", "7 of 7", "not settled", "1.00", "0.36"],
        ["Q-learning", "30.6", "5 of 7", "not settled", "0.31", "0.86"],
        ["ARS", "30.4", "5 of 7", "not settled", "0.19", "0.91"],
        ["Webster", "117.7", "0 of 7", "worse", "0.001", "1.00"]]
c.table(L, 1.35, rows, colw=[2.62, 1.2, 1.5, 1.46, 1.0, 1.0], rowh=0.48, size=17, head_size=15)
c.text(L, 5.35, W, 1.1, [para("p diff.: paired t-test on the daily delay ratio, Holm-corrected over six methods · "
                              "p tie: equivalence test, margin 2 s/veh (or 5 %) · significant if p < 0.05 · "
                              "learners: average of 5 training runs · development days (20): real plan 34.3, "
                              "no-cycle 25.3, LSTDQ 24.6, MaxPressure 27.6, Q-learning 31.5, ARS 36.5, Webster 122.0",
                              12, GREY, italic=True)])
an.notes_slide.notes_text_frame.text = "(appendix) Full test-day comparison with the statistical values (TEST_PLAN.md, amendment 1)."

# ================================================================ Conclusion wording
cc = find("Conclusion")
for sh in cc.shapes:
    if sh.has_text_frame:
        for pa in sh.text_frame.paragraphs:
            for r in pa.runs:
                if "scaled-up capacity" in r.text:
                    r.text = r.text.replace("Train on scaled-up capacity", "Train learners on heavier traffic")

# ================================================================ Methods list: mark appendix
ms = find("Methods Compared")
for sh in ms.shapes:
    if sh.has_text_frame:
        for pa in sh.text_frame.paragraphs:
            if pa.runs and pa.text.strip() in ("Webster Formula", "Maxpressure"):
                pa.runs[-1].text = pa.runs[-1].text + " (appendix)"

n = ms.notes_slide.notes_text_frame.text
i = n.find("[Point at:")
add = ("We ran all seven; in the results I focus on the real plan, the no-cycle controller and the three learners. "
       "MaxPressure and Webster are in the appendix.\n\n")
ms.notes_slide.notes_text_frame.text = (n[:i] + add + n[i:]) if i >= 0 else (n + "\n\n" + add)
prs.save(OUT)
print("saved", OUT, len(prs.slides), "slides")

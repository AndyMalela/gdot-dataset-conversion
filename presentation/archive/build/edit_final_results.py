"""Results + appendix edit of the student's final deck (eSocLab_MidtermTHISONE.pptx). Only result slides and new
appendix slides change; the student's other slides are untouched.
- 'Results' -> 'Results: Real Days': GDOT plan, no-cycle, LSTDQ, Q-learning, ARS; all day / main / side / verdict.
- 'Results: Time of Day Difference' -> 'Results: When': no MaxPressure column, no Midday row; honesty footnotes.
- 'Results: Who Waits' merged into Real Days (removed from main talk), 'Learners Compared' moved to appendix.
- Appendix at the end: Learners Compared; All Methods (full table, p values, MaxPressure, Webster); By Condition,
  All Methods; Who Waits, All Methods.
Numbers: atsc/sites/137/INTERPRETATION.md v3, TEST_PLAN.md amendment 1, eval_test/analysis.md.
Usage: uv run --no-project --with python-pptx --with lxml python edit_final_results.py IN.pptx OUT.pptx"""
import copy, sys
from pptx import Presentation
from pptx.dml.color import RGBColor
from pptx.opc.packuri import PackURI
from pptx.util import Inches, Pt

SRC, OUT = sys.argv[1:3]
prs = Presentation(SRC)
GREEN, RED, TITLE, GREY = RGBColor(0x2E, 0x7D, 0x32), RGBColor(0xA5, 0x20, 0x26), RGBColor(0x99, 0, 0), RGBColor(0x59, 0x59, 0x59)


def title_shape(s):
    for sh in s.shapes:
        if sh.has_text_frame and sh.name in ("タイトル 1", "Title 1", "Text 1"):
            return sh


def title(s):
    t = title_shape(s)
    return t.text_frame.text.strip() if t else ""


def find(t):
    return next(s for s in prs.slides if title(s) == t)


def set_text(tf_or_cell, text, color=None, bold=None):
    tf = tf_or_cell.text_frame
    p = tf.paragraphs[0]
    runs = p.runs
    if not runs:
        r = p.add_run()
    else:
        r = runs[0]
        for x in runs[1:]:
            x._r.getparent().remove(x._r)
    r.text = text
    if color is not None:
        r.font.color.rgb = color
    if bold is not None:
        r.font.bold = bold
    for extra in tf.paragraphs[1:]:
        extra._p.getparent().remove(extra._p)
    return r


def set_title(s, t):
    set_text(title_shape(s), t)


def table_of(s):
    return next(sh for sh in s.shapes if sh.has_table)


def drop_col(gf, j):
    tbl = gf.table._tbl
    grid = tbl.tblGrid
    grid.remove(grid.findall("{http://schemas.openxmlformats.org/drawingml/2006/main}gridCol")[j])
    for tr in tbl.tr_lst:
        tr.remove(tr.tc_lst[j])


def drop_row(gf, i):
    tbl = gf.table._tbl
    tbl.remove(tbl.tr_lst[i])


def fill(gf, rows, colw=None, marks=None):
    t = gf.table
    for i, r in enumerate(rows):
        for j, v in enumerate(r):
            col = (marks or {}).get((i, j))
            set_text(t.cell(i, j), v, color=col[0] if col else (None if i == 0 else RGBColor(0, 0, 0)),
                     bold=col[1] if col else (True if (i == 0 or j == 0) else False))
    if colw:
        for j, w in enumerate(colw):
            t.columns[j].width = Inches(w)
        gf.width = Inches(sum(colw))


_N = [960]


def duplicate(src, new_title):
    ns = prs.slides.add_slide(src.slide_layout)
    _N[0] += 1
    ns.part.partname = PackURI(f"/ppt/slides/slide{_N[0]}.xml")
    for sh in list(ns.shapes):
        sh._element.getparent().remove(sh._element)
    for sh in src.shapes:
        ns.shapes._spTree.append(copy.deepcopy(sh._element))
    set_title(ns, new_title)
    return ns


def move_to_end(s):
    lst = prs.slides._sldIdLst
    sid = next(x for x in lst if prs.part.related_part(x.rId) is s.part)
    lst.remove(sid)
    lst.append(sid)


def delete(s):
    lst = prs.slides._sldIdLst
    sid = next(x for x in lst if prs.part.related_part(x.rId) is s.part)
    prs.part.drop_rel(sid.rId)
    lst.remove(sid)


res, when, learn, who = find("Results"), find("Results: Time of Day Difference"), find("Learners Compared"), \
    find("Results: Who Waits")

# ---------------------------------------------------------------- appendix copies first (full tables)
app_all = duplicate(res, "Appendix: All Methods")
gf = table_of(app_all)
fill(gf, [["Test days", "Delay (s)", "Beats GDOT", "vs no-cycle", "p diff.", "p tie"],
          ["GDOT plan (real)", "31.2", "-", "worse", "0.046", "0.97"],
          ["No cycle (actuated)", "24.9", "7 of 7", "reference", "-", "-"],
          ["LSTDQ", "25.3", "7 of 7", "tie", "1.00", "0.026"],
          ["MaxPressure", "26.1", "7 of 7", "not settled", "1.00", "0.36"],
          ["Q-learning", "30.6", "5 of 7", "not settled", "0.31", "0.86"],
          ["ARS", "30.4", "5 of 7", "not settled", "0.19", "0.91"],
          ["Webster", "117.7", "0 of 7", "worse", "0.001", "1.00"]])
for sh in app_all.shapes:
    if sh.has_text_frame and sh.text_frame.text.startswith("Lower delay"):
        r = set_text(sh, "Lower is better · Beats GDOT = test days with less delay than the real plan · learners: "
                         "average of 5 runs · p diff.: paired t-test, Holm-corrected · p tie: equivalence test "
                         "(within 2 s) · significant if p < 0.05 · Webster = textbook fixed timer")
        r.font.size = Pt(12); r.font.bold = False; r.font.italic = True; r.font.color.rgb = GREY
        sh.top = Inches(5.62)
    elif sh.has_text_frame and sh.text_frame.text.startswith("All controller"):
        r = set_text(sh, "Every adaptive method beats the real plan on average; none beats it without its fixed cycle")
        r.font.size = Pt(18)
        sh.top = Inches(6.3)
app_all.notes_slide.notes_text_frame.text = (
    "(appendix) Full test-day comparison with the statistical values (TEST_PLAN.md amendment 1). Development days "
    "(20): real plan 34.3, no-cycle 25.3, LSTDQ 24.6, MaxPressure 27.6, Q-learning 31.5, ARS 36.5, Webster 122.0. "
    "MaxPressure: green to the longest queue (Varaiya 2013). Webster: textbook fixed timer (Webster 1958), built "
    "for a typical day; it overflows in the evening (19-24 h: 344.9 s/veh).")

app_cond = duplicate(when, "Appendix: By Condition")
foot_src = next(sh for sh in res.shapes if sh.has_text_frame and sh.text_frame.text.startswith("Lower delay"))


def footnote(s, text, top):
    el = copy.deepcopy(foot_src._element)
    s.shapes._spTree.append(el)
    sh = s.shapes[-1]
    sh.top = Inches(top)
    r = set_text(sh, text)
    r.font.size = Pt(13); r.font.bold = False; r.font.italic = True; r.font.color.rgb = GREY
    return sh


footnote(app_cond, "Test days except ** · Surges: 6 hours with sudden side-street surges, picked after seeing the "
                   "results · +25 %**: what-if, every count +25 %, on 5 development days · descriptive, no tests · "
                   "Webster: night 23.1, morning 30.6, midday 85.4, evening peak 42.7, +25 % 902.6", 5.9)
app_cond.notes_slide.notes_text_frame.text = "(appendix) Full by-condition table, all adaptive methods and the real plan."

app_who = duplicate(who, "Appendix: Who Waits")
for sh in app_who.shapes:
    if sh.has_text_frame and sh.text_frame.text.startswith("Main street ="):
        set_text(sh, "Main street = W. Paces Ferry, 58 % of cars")
app_who.notes_slide.notes_text_frame.text = (
    "(appendix) Main-street and side-street delay for every adaptive method, test days. Likely reasons the learners "
    "favour the main street (not yet tested): rewarded per car, and side streets only have stop-line detectors.")

# ---------------------------------------------------------------- main: Results: Real Days (merged with Who Waits)
set_title(res, "Results: Real Days")
gf = table_of(res)
drop_row(gf, 7)          # Webster
drop_row(gf, 4)          # MaxPressure
drop_col(gf, 5)          # p tie
G, R_ = (GREEN, True), (RED, True)
fill(gf, [["Test days, delay (s)", "All day", "Main street", "Side streets", "vs no-cycle"],
          ["GDOT plan (real)", "31.2", "18.2", "49.6", "worse"],
          ["No cycle (actuated)", "24.9", "24.7", "25.1", "reference"],
          ["LSTDQ", "25.3", "19.2", "33.8", "tie"],
          ["Q-learning", "30.6", "22.8", "41.5", "not settled"],
          ["ARS", "30.4", "27.7", "34.2", "not settled"]],
     colw=[2.78, 1.35, 1.55, 1.6, 1.5],
     marks={(1, 0): (TITLE, True), (1, 3): R_, (1, 4): (TITLE, False), (2, 1): G, (3, 1): G, (3, 3): R_,
            (3, 4): G, (4, 3): R_, (5, 3): R_})
for sh in res.shapes:
    if sh.has_text_frame and sh.text_frame.text.startswith("Lower delay"):
        r = set_text(sh, "Lower is better · learners: average of 5 runs · tie = shown within 2 s (p = 0.026) · "
                         "not settled = days vary too much to call · main street = W. Paces Ferry, 58 % of cars")
        r.font.size = Pt(13); r.font.bold = False; r.font.italic = True; r.font.color.rgb = GREY
    elif sh.has_text_frame and sh.text_frame.text.startswith("All controller"):
        set_text(sh, "No learning needed to beat today's plan; learning changes who waits")
res.notes_slide.notes_text_frame.text = (
    "(~45 s) On the 7 test days, the real plan has 31.2 seconds of delay per car, and its side streets wait 50. "
    "The same controller without its fixed cycle: 24.9, shared evenly, 25 on both. LSTDQ ties it at 25.3, but by "
    "keeping the main street fast and making the side streets wait 34. Q-learning and ARS are about 5 seconds behind "
    "and not settled against the no-cycle controller.\n\n"
    "So beating today's plan needs no learning, and learning changes who waits. Likely why, not yet tested: the "
    "learners are rewarded per car, most cars are on the main street, and the side streets only have stop-line "
    "detectors.\n\n"
    "[Point at: the All day column, then the red side-street numbers.]\n\n"
    "[Not read aloud: LSTDQ beats the real plan on 7 of 7 days, Q-learning and ARS on 5 of 7. Real plan vs "
    "no-cycle: worse, p 0.046 (paired t-test, Holm-corrected). LSTDQ tie: equivalence test p 0.026. Development "
    "days: real plan 34.3, no-cycle 25.3, LSTDQ 24.6, Q-learning 31.5, ARS 36.5. MaxPressure and Webster: "
    "appendix.]")

# ---------------------------------------------------------------- main: Results: When
set_title(when, "Results: When")
gf = table_of(when)
drop_row(gf, 3)          # Midday
drop_col(gf, 3)          # MaxPres.
fill(gf, [["Delay (s)", "GDOT plan", "No cycle", "LSTDQ", "Q-learning", "ARS"],
          ["Night", "8.2", "8.2", "11.6", "8.1", "8.5"],
          ["Morning peak", "26.1", "22.8", "21.1", "21.8", "21.9"],
          ["Evening peak", "34.0", "27.8", "30.6", "42.2", "38.2"],
          ["Surges*", "85.4", "39.1", "58.0", "114.5", "95.7"],
          ["+25 % traffic**", "63.1", "45.0", "51.7", "76.9", "100.4"]],
     colw=[2.38, 1.32, 1.27, 1.2, 1.41, 1.2],
     marks={(1, 4): G, (2, 3): G, (3, 2): G, (4, 2): G, (5, 2): G})
footnote(when, "Green = lowest in the row · * 6 hours with sudden side-street surges, picked after seeing the "
               "results · ** what-if: every count +25 %, on 5 development days · descriptive, no statistical tests",
         5.75)
when.notes_slide.notes_text_frame.text = (
    "(~35 s) No method wins everywhere. LSTDQ is best in the morning peak, 21.1. But the simple no-cycle rule wins "
    "the evening peak, and clearly in six hours with sudden side-street surges, picked after seeing the results: "
    "39.1 against 58.0 for LSTDQ. With a quarter more traffic, a what-if on development days, it is also best: "
    "45.0 against 51.7. Q-learning and ARS are best at night but fall far behind when traffic is heavy. The real "
    "plan is behind the no-cycle controller in every row except night, where they are equal: at night the real "
    "controller already runs without its cycle.\n\n"
    "[Not read aloud: midday (10-15 h): real plan 35.0, no-cycle 25.8, LSTDQ 24.2, Q-learning 27.9, ARS 26.8. "
    "Night = 00-06 h, morning 06-10, evening peak 15-19. From +50 % every controller's queues keep growing for much "
    "of the day, so methods are not ranked above +25 %. MaxPressure: appendix.]")

# ---------------------------------------------------------------- Learners Compared -> appendix; Who Waits removed
set_title(learn, "Appendix: Learners Compared")
learn.notes_slide.notes_text_frame.text = (
    "(appendix) " + learn.notes_slide.notes_text_frame.text.replace("(~45 s) ", "").replace(
        "The three learners get the same detector inputs and the same kind of linear model.",
        "The three learners get the same detector inputs. LSTDQ and Q-learning learn the same linear model; ARS "
        "learns a decision rule directly."))
delete(who)
for s in (learn, app_all, app_cond, app_who):
    move_to_end(s)
prs.save(OUT)
print("saved", OUT, len(prs.slides), "slides")

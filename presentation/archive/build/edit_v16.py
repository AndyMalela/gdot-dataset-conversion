"""v16 = v15 + second intersection as a main Future Work step (own validation first), conclusion notes on
generalising, likely questions on 'why only one' / 'what a new site gives'."""
import copy, sys
from pptx import Presentation
SRC, OUT = sys.argv[1:3]
p = Presentation(SRC)


def by_title(t):
    return next(sl for sl in p.slides if any(sh.has_text_frame and sh.name == "Title 1" and sh.text_frame.text == t
                                             for sh in sl.shapes))


def set_cell(cell, text):
    pa = cell.text_frame.paragraphs[0]
    runs = pa.runs
    runs[0].text = text
    for r in runs[1:]:
        r._r.getparent().remove(r._r)
    for extra in cell.text_frame.paragraphs[1:]:
        extra._p.getparent().remove(extra._p)


fw = by_title("Future Work")
tbl = next(sh for sh in fw.shapes if sh.has_table)
t = tbl.table
last = t.rows[len(t.rows) - 1]._tr
row4 = t.rows[4]._tr
new = copy.deepcopy(row4)
last.addprevious(new)
r5 = t.rows[5]
set_cell(r5.cells[0], "5  Repeat at a second intersection")
set_cell(r5.cells[1], "O2, O3")
set_cell(r5.cells[2], "Busier traffic, different detectors and layout: is it the method or the place? (own validation first)")
r6 = t.rows[6]
set_cell(r6.cells[0], "If time: ATSPM outcome check (Split Failure); DQN")
set_cell(r6.cells[1], "O1, O2")
set_cell(r6.cells[2], "Traffic outcomes; a neural reference")
from pptx.util import Inches
for k, row in enumerate(t.rows):
    row.height = Inches(0.42 if k == 0 else 0.6)
grey = next(sh for sh in fw.shapes if sh.has_text_frame and sh.text_frame.text.startswith("7065 differs"))
grey.top = tbl.top + Inches(0.42 + 6 * 0.6 + 0.15)
run = grey.text_frame.paragraphs[0].runs[0]
run.text = ("A second site (e.g. SIG 7065) differs from 137 in more than one way at once: a consistency check, "
            "not a test of one cause")
for r in grey.text_frame.paragraphs[0].runs[1:]:
    r._r.getparent().remove(r._r)
fw.notes_slide.notes_text_frame.text = (
    "(~25 s) Next: test whether the ranking survives errors in the counts. Check the simulation on the test days. "
    "Test why the side streets wait. Train on heavier traffic. And repeat the whole comparison at a second "
    "intersection, a busier one with different detectors, after validating its simulation the same way, to see "
    "whether our results come from the methods or from this place.\n\n"
    "Thank you.\n\n"
    "[If asked 'why only one intersection so far?': building and validating the simulation took eight attempts "
    "here; we wanted one fully validated site before adding a second. If asked 'what would a new intersection "
    "give?': it may not change the results, and that would be a finding too. But 137 cannot answer three things: "
    "heavy traffic (it is rarely near capacity, so we could not test whether methods pull apart there); what the "
    "detectors see (here the side streets only have stop-line detectors, one of our two likely reasons the learners "
    "make side streets wait); and the setting (one signal tied to one neighbour). One site tells us what happens "
    "here; a second tells us whether it is the method or the place. Note: 7065's earlier simulation did not pass "
    "its field check, so it needs its own validation first.]")
cc = by_title("Conclusion")
n = cc.notes_slide.notes_text_frame.text
key = "this intersection is rarely that busy."
assert key in n
cc.notes_slide.notes_text_frame.text = n.replace(
    key, key + " These results hold for this intersection; whether they hold elsewhere is the next question.")
p.save(OUT)
print("saved", OUT)

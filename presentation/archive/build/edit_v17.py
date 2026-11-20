"""v17 = v16 with Future Work merged into the Conclusion slide (Conclusion is the last main slide): limitations and
three next steps side by side (heavier scaled traffic, more intersections, side-street-weighted reward); the
Future Work slide is removed. The test-day simulation check and the count-error test are no longer listed."""
import copy, sys
from pptx import Presentation
from pptx.util import Inches, Pt
SRC, OUT = sys.argv[1:3]
p = Presentation(SRC)


def by_title(t):
    return next(sl for sl in p.slides if any(sh.has_text_frame and sh.name == "Title 1" and sh.text_frame.text == t
                                             for sh in sl.shapes))


cc = by_title("Conclusion")
lim = next(sh for sh in cc.shapes if sh.has_text_frame and sh.text_frame.text.startswith("Limitations"))
fnd = next(sh for sh in cc.shapes if sh.has_text_frame and sh.text_frame.text.startswith("Findings"))
fnd.height = Inches(2.45)
lim.top = Inches(3.95)
lim.height = Inches(2.6)
lim.width = Inches(4.3)
nxt_el = copy.deepcopy(lim._element)
lim._element.addnext(nxt_el)
nxt = next(sh for sh in cc.shapes if sh._element is nxt_el)
nxt.left = Inches(5.23)
nxt.name = "Rounded Rectangle 27"


def set_paras(shape, texts, body_size):
    ps = shape.text_frame.paragraphs
    assert len(ps) >= len(texts)
    for k, (pa, t) in enumerate(zip(ps, texts)):
        pa.runs[0].text = t
        for r in pa.runs[1:]:
            r._r.getparent().remove(r._r)
        if k:
            for r in pa.runs:
                r.font.size = Pt(body_size)
    for pa in ps[len(texts):]:
        pa._p.getparent().remove(pa._p)


set_paras(lim, ["Limitations", "Checks signal behaviour, not delay", "Test days run twice", "One intersection"], 20)
set_paras(nxt, ["Next steps", "Train on heavier, scaled-up traffic", "Repeat at more intersections",
                "Weight side-street cars more in training"], 20)

n = cc.notes_slide.notes_text_frame.text
i = n.index("[Not read aloud")
cc.notes_slide.notes_text_frame.text = (
    n[:i].rstrip() + "\n\n"
    "Next steps. One: train and compare on heavier traffic, with the counts scaled up, to test whether the methods "
    "pull apart near capacity. Two: repeat the comparison at more intersections, each validated the same way, to "
    "see whether our results come from the methods or from this place. Three: retrain the learners with side-street "
    "cars weighted more, to test one of our two likely reasons the side streets wait.\n\n"
    "Thank you.\n\n" + n[i:] + (
        "\n[If asked 'why only one intersection so far?': building and validating the simulation took eight attempts "
        "here; we wanted one fully validated site first. 'What would a new intersection give?': it may not change the "
        "results, and that would be a finding too; but 137 cannot test heavy traffic (rarely near capacity), what the "
        "detectors see (side streets only have stop-line detectors), or a different setting (here one signal tied to "
        "one neighbour). A second site needs its own validation first.]"))

fw = by_title("Future Work")
lst = p.slides._sldIdLst
for sid in list(lst):
    if p.slides.part.related_slide(sid.rId) is fw if hasattr(p.slides.part, "related_slide") else False:
        pass
for sid in list(lst):
    if p.part.related_part(sid.rId) is fw.part:
        p.part.drop_rel(sid.rId)
        lst.remove(sid)
        break
p.save(OUT)
print("saved", OUT, len(p.slides), "slides")

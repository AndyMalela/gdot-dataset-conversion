"""v13 = student's v12 edit + slide 12 (Experiments): 'test days opened once / rerun' box removed from the slide and
the spoken notes (kept as a not-read-aloud 'if asked' line; still disclosed in Conclusion limitations and backup
'Test Run and Rerun'), 'Compare by' + 'What-if' merged into one bullet, train/develop/test explained in the notes."""
import sys
from pptx import Presentation
SRC, OUT = sys.argv[1:3]
p = Presentation(SRC)
s = next(sl for sl in p.slides if any(sh.has_text_frame and sh.name == "Title 1" and sh.text_frame.text == "Experiments"
                                      for sh in sl.shapes))
box = next(sh for sh in s.shapes if sh.has_text_frame and sh.text_frame.text.startswith("Test days opened once"))
box._element.getparent().remove(box._element)
tb = next(sh for sh in s.shapes if sh.has_text_frame and "Compare by" in sh.text_frame.text)
paras = tb.text_frame.paragraphs
cmp_ = next(pa for pa in paras if pa.runs and pa.runs[0].text.startswith("Compare by"))
wif = next(pa for pa in paras if pa.runs and pa.runs[0].text.startswith("What-if"))
cmp_.runs[1].text = "time of day, how busy, surges; what-if: every count +25 %"
wif._p.getparent().remove(wif._p)
s.notes_slide.notes_text_frame.text = (
    "(~45 s) We measure delay: the seconds each car loses compared with driving freely, including waiting to enter. "
    "Lower is better. For cars heading west, it includes their wait at signal 138.\n\n"
    "The days are split by date into three groups. 29 training days: used to tune the simulation and to train the "
    "learners. 20 development days: used to check the simulation and to compare the methods while we could still "
    "find and fix problems. And 7 test days, held back until the end, for the final comparison, so that no decision "
    "was based on them.\n\n"
    "A tie means within 2 seconds, fixed before any result. Each method is compared with the no-cycle controller day "
    "by day: a tie needs an equivalence test, and a difference a t-test corrected for testing six methods at once, "
    "both at p below 0.05. With only 7 test days, many comparisons stay not settled.\n\n"
    "[Not read aloud - if asked: the test days were opened once under a plan written beforehand; after that run we "
    "found four errors, wrote the fixes down, reran once, and report both results (backup: Test Run and Rerun). "
    "Each learner is trained 5 times, on training days only, and results are the average of the 5. A tie is within "
    "2 s/veh or 5 %, whichever is larger - a judgement call. Conditions: time of day, how busy the hour is, how "
    "uneven the traffic is, sudden surges. The what-if raises every count by 25 % on 5 development days; the "
    "learners trained on real counts only.]")
p.save(OUT)
print("saved", OUT)

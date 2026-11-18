"""v6 = the student's edit of v5 (eSocLab_Midterm-v5-edit.pptx, kept unchanged) + related-work row 2 rewritten for the
'compare against each other and against the deployed controller' goal, slide-4 line, goal-v1 O2, goal-v2 typos;
speaker notes from slide 4 on brought up to date (slides 1-3 notes are the student's, untouched)."""
import copy, sys
from pptx import Presentation
SRC, OUT = sys.argv[1:3]
p = Presentation(SRC)
S = p.slides


def shape(slide, name, contains):
    return next(sh for sh in slide.shapes if sh.has_text_frame and sh.name == name and contains in sh.text_frame.text)


def set_runs(par, texts):
    """keep the paragraph's existing runs' formatting; texts[i] goes into run i, extra runs removed."""
    runs = par.runs
    assert len(runs) >= len(texts), (len(runs), texts)
    for r, t in zip(runs, texts):
        r.text = t
    for r in runs[len(texts):]:
        r._r.getparent().remove(r._r)


# slide 4: last problem line
pa = shape(S[3], "Rounded Rectangle 41", "Few studies").text_frame.paragraphs[1]
set_runs(pa, ["Few studies compare methods against each other and against the controller actually installed, on real "
              "traffic"])
# slide 5: related works row 2
q = shape(S[4], "TextBox 32", "Better than what is installed?")
set_runs(q.text_frame.paragraphs[0], ["Compared with what?"])
b = shape(S[4], "TextBox 33", "rarely carried out").text_frame.paragraphs
set_runs(b[0], ["Lab studies mostly compare with fixed-time and MaxPressure*; tests against engineer-tuned actuated "
                "control \"are rarely carried out\" ", "(Meess et al., 2024)"])
set_runs(b[1], ["The two that do (Kwesiga 2025, Meess 2024) include no other adaptive method, and do not report "
                "checking their simulated controller against its field log*"])
# slide 6: goal v1, objective 2
pa = shape(S[5], "TextBox 31", "Train and test").text_frame.paragraphs[0]
set_runs(pa, ["Compare the methods on held-back real days, by time of day, how busy, and surges"])
# slide 7: goal v2 typos
pa = shape(S[6], "TextBox 32", "Compare each methods").text_frame.paragraphs[0]
assert [r.text for r in pa.runs][2] == "by"
pa.runs[0].text = "Compare each method's performance "
pa.runs[2]._r.getparent().remove(pa.runs[2]._r)
pa.runs[2].text = pa.runs[2].text.lstrip()

NOTES = {
4: """Learned control looks promising in papers, but it rarely reaches the street. One main problem is agencies must be able to audit a controller against signal standards first, and that is still a barrier for learned control. And few studies compare methods against each other and against the controller actually installed, on real traffic.

So an agency cannot tell whether a learned controller would beat what it already runs, by how much, and under what conditions.""",
5: """(~60 s) In the studies we reviewed, I see four gaps.

One: a realistic test? Most use made-up road networks. The real-road studies never report checking their simulation against the real road, and they test on the data they built it from.

Two: compared with what? Lab studies mostly compare with a fixed timer and MaxPressure. Tests against engineer-tuned controllers "are rarely carried out", as Meess and colleagues put it, and the two that do include no other adaptive method. So no study puts learned control, rule-based adaptive control and the installed controller in one comparison on real traffic.

Three: when does it pay off? Most studies vary only the amount of traffic, and they disagree. Yet light traffic, time of day, and conditions unlike training each changed the result in other studies.

Four: better for whom? Results are one average over all cars.""",
6: """(~40 s) Our goal: evaluate signal control methods against each other, and against the controller GDOT actually runs, on real traffic.

Three objectives, at one intersection. One: build a simulation that behaves like the real intersection, and check it against GDOT's own log on days we did not tune it on. Two: compare the methods on real days we held back, overall and by time of day, how busy the hour is, and sudden surges. Three: interpret how each method wins or loses, and who ends up waiting, and check that it holds.

Before any result, we wrote down what we expected: in normal traffic, the methods that react to traffic would all do about equally well; near capacity, they would pull apart.""",
7: """(~40 s) [Alternative to the previous slide: use one of the two.] Our goal is the field problem: give agencies evidence on when, and why, adaptive and learned control pays off over the control already deployed, on real traffic.

Three objectives, at one intersection. One: simulate and calibrate the intersection from GDOT's logged data, and check it on days we did not tune it on. Two: compare each method's performance, by time of day, how busy the hour is, and sudden surges. Three: interpret how each method wins or loses, and who ends up waiting, and check that it holds.

Before any result, we wrote down what we expected: in normal traffic, the methods that react to traffic would all do about equally well; near capacity, they would pull apart.""",
}
for n, t in NOTES.items():
    S[n - 1].notes_slide.notes_text_frame.text = t
p.save(OUT)
print("saved", OUT)

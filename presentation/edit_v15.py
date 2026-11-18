"""v15 = student's v14 edit + Methods Compared notes: why each method (one question each), where each learner comes
from, and 'if asked' answers (why linear, why not SARSA, ARS source). Slides unchanged."""
import sys
from pptx import Presentation
SRC, OUT = sys.argv[1:3]
p = Presentation(SRC)
s = next(sl for sl in p.slides if any(sh.has_text_frame and sh.name == "Title 1" and sh.text_frame.text == "Methods Compared"
                                      for sh in sl.shapes))
s.notes_slide.notes_text_frame.text = (
    "(~50 s) Seven controllers, in the same types as before, and each one answers a question.\n\n"
    "Fixed-time: Webster, the textbook timer. It is the kind of simple baseline most papers compare against.\n\n"
    "Actuated: the GDOT plan, which is what runs on the street today, and the one we checked. Its greens follow the "
    "detectors, but inside a fixed cycle shared with the next signal. Our second actuated controller is the same one "
    "without the fixed cycle. It separates two things: how much of a gain comes from dropping the fixed cycle, and "
    "how much from learning. It is our reference.\n\n"
    "Adaptive, with a designed rule: MaxPressure, which gives green to the longest queue. It is the most common "
    "rule-based baseline in the studies we reviewed, so it tells us whether a learned rule beats a designed one.\n\n"
    "Adaptive, learned from data: three linear learners. They see the same detector inputs and use the same kind of "
    "model; they differ only in how they learn. LSTDQ is our base method, from Sahachaiseree and Oguchi, who argue "
    "linear learners are easier to inspect. In the same paper they compare it with Q-learning, which learns step by "
    "step; we include it to see whether the learning method matters. ARS is our addition: a third way to learn the "
    "same kind of rule, by trial and error.\n\n"
    "[Point at: the four group headings, then the three learners.]\n\n"
    "[Not read aloud - if asked:\n"
    "Why linear, not deep RL? Deployment: agencies must be able to check a controller against standards (Chen et al. "
    "2022), and deep RL can be costly to compute on old field hardware. Sahachaiseree and Oguchi argue linear is "
    "easier to inspect and LSTDQ converged in about 10 learning iterations. A deep learner as a reference is "
    "planned, so we do not claim linear is enough.\n"
    "Why these three learners? One per way of learning the same linear rule: solve from all data at once (LSTDQ), "
    "step by step (Q-learning), or search the rule directly (ARS). Same inputs, same model, so any difference comes "
    "from the learning method.\n"
    "Why not SARSA? It is in the same family as Q-learning: both learn step by step; the difference is only which "
    "next action they learn from. Q-learning already covers that way of learning, so we expect similar behaviour. "
    "Linear SARSA(lambda), as in Alegre et al. 2022, would be a small extension, not a new kind of method.\n"
    "Is ARS from a traffic paper? No: Mania et al. 2018, general reinforcement learning. We added it to cover direct "
    "policy search.\n"
    "Sources: Webster 1958; MaxPressure, Varaiya 2013; LSTDQ, Lagoudakis & Parr 2003, applied to signals by "
    "Sahachaiseree & Oguchi 2025; Q-learning, Watkins 1989; ARS, Mania et al. 2018.]")
p.save(OUT)
print("saved", OUT)

# Slides 3, 4 and 9: proposal v2

Every quote and count below was checked in the paper PDFs (`Things/gr-andy/raw/papers/`). "Line" means the line in the pdftotext output.

---

## Slide 3: Problem

**Opening line (big):** A traffic signal does one job: every second, keep the current green or switch.

**"Signal control comes in three types"** (Xiao et al., 2025; Chen et al., 2022)

| Fixed-time | Actuated | Adaptive |
|---|---|---|
| A preset schedule; ignores the traffic actually there | Detectors stretch or end each green, within preset limits | Changes the timing itself as traffic changes |
| | **137 runs this**, inside a fixed cycle shared with the next signal | **Rule-based:** a designed rule or optimiser (e.g. SCOOT, SCATS; Xiao et al., 2025) |
| | | **Learned from data:** reinforcement learning (RL), "one emerging approach to adaptive control" (Chen et al., 2022) |

Adaptive does not mean RL. RL is one kind of adaptive control: the kind whose decision rule is learned from data. SCOOT and SCATS are adaptive with designed rules (Xiao 2025, line ~189: "reliance on preset rules"). MaxPressure is also rule-based adaptive.

**Problem box:**
> **Problem:** learned control looks promising in papers but rarely reaches the street, so an agency cannot tell whether it would beat what it already runs.
> - **The methods:** agencies must be able to audit a controller against signal standards before deploying it, and this is an open barrier for RL (Chen et al., 2022).
> - **The tests:** few compare against the controller actually installed, on real traffic (slide 4).

Small print under the box: 470 RL papers, 2015–2025 (Xiao et al., 2025); "field deployment remains rare" (Zou et al., 2025).

**Sources:**
- Chen 2022, §1: "Jurisdictions cannot deploy RL-based signal controllers without assurances about compliance to standards (e.g., minimum green time) and safety requirements. The interpretability of models is important for ensuring that signalling plans can be audited and adjusted by stakeholders."
- Chen 2022, §2.1–2.2: the three types, and RL as "one emerging approach to adaptive control".
- Xiao 2025: intro ("three categories"), line 140 (470 papers), and SCOOT/SCATS as adaptive.
- Zou 2025: line 195.

**Why the problem box has two halves.** You asked whether to use only "agency cannot tell", or to add "methods are undeployable" and "never evaluated against the real deployed controller". I recommend keeping "agency cannot tell" as the headline and the other two as its reasons, with softer wording:
- **Not "undeployable".** Chen 2022's barrier is that RL is hard to audit, not that it can't be deployed. Zou 2025 even reports a field test. Use "hard to audit", which leads to slide 9: *Sahachaiseree & Oguchi argue a linear learner is easier to inspect* (their argument, labelled as motivation, not our finding).
- **Not "never evaluated against the deployed controller".** That is false:
  - Meess 2024 compares against the real traffic-actuated control used in practice.
  - Kwesiga 2025 compares against GDOT's own timing, running in the real controller software.

  What the studies we reviewed don't do is the careful part, and it goes on slide 4, row 2.

---

## Slide 4: What Prior Work Leaves Open

Four rows. Each row has the question, what the literature shows, and the objective it feeds.

**1. A realistic test?** → O1
- "A majority of works (62%)" use synthetic road networks (Noaeen et al., 2022, cited in Chen et al., 2022).
- Kwesiga 2025, Meess 2024 and Li 2024 build their simulation from real data. None reports checking it against the field afterwards, and they test on the same data\*.

**2. Better than what is installed?** → O2
- Tests against engineer-tuned actuated control "are rarely carried out" (Meess et al., 2024).
- The two that do it (Meess 2024; Kwesiga 2025) don't report checking the simulated installed controller against its field log. Kwesiga tests on the same afternoon the simulation was built from\*.

**3. When does it pay off?** → O2
- Most studies vary one thing, total demand, and disagree: the gain shrinks (Sahachaiseree & Oguchi, 2025), grows (El-Tantawy et al., 2014), or stays the same (Alegre et al., 2020).
- Other conditions matter too:
  - In light traffic, NEMA actuated beat RL: 71.2 vs 92.2 s travel time (Lu et al., 2025).
  - In a field test, an adaptive system's gain changed with the time of day (Smith et al., 2013).
  - With test conditions more than 20% off its training conditions, RL lost its gain, while a simple feedback rule still helped (Han et al., 2023; ramp metering, in simulation).
- No clean split into held-out days\*. Real days differ in all these ways at once: how busy, time of day, sudden surges.

**4. Better for whom?** → O3
- Results are one average over all cars. Fairness, meaning "all road users receive equitable access", is an open challenge (Xiao et al., 2025, §5.6).

**Footer:** \* in the studies we reviewed.

**Sources:**
- Chen 2022, line 364.
- Meess 2024, p.2: the "rarely carried out" quote, and the benchmark as "the already existing T-time-based traffic-actuated control".
- Lu 2025, low-demand table: RL-TSC-AC 92.2, NEMA-actuated 71.2.
- Smith 2013, Table 1 and "largest improvement ... Mid Day".
- Han 2023, lines 540–543: RL −0.09% vs ALINEA +1.43% beyond 20% mismatch.
- `queries/experimental-setup-across-papers.md`: "No paper in the wiki uses a clean temporal split with held-out days".

**Slide 5:** the gap tags become O1 = gap 1, O2 = gaps 2 and 3, O3 = gap 4.

---

## Slide 9: Methods Compared (same three headings as slide 3)

| Fixed-time | Actuated | Adaptive: rule-based | Adaptive: learned from data |
|---|---|---|---|
| **Webster**: textbook schedule from train-day counts | **GDOT plan**: deployed, and checked against GDOT's log. Detectors stretch or end greens inside a fixed cycle shared with the next signal | **MaxPressure**: green to the longest queue | **LSTDQ** (base method), **Q-learning**, **ARS**: linear learners. Same features, different ways to learn the weights |
| | **Actuated (no cycle)**: the same controller without the fixed cycle. A what-if, and the reference. Same as the GDOT plan at night | | |

**Bottom line:** "Same network, demand, detectors and safety rules for all: only the decision differs".

**Base-method line (motivation, attributed):** "Linear: Sahachaiseree & Oguchi (2025) argue it is fast to train and easier to inspect."

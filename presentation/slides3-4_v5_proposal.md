# Slides 3–4, broader version (proposal)

This version replaces "keep green or switch?" on slide 3 with the field problem: learned control looks promising in papers but rarely reaches the street. Slide 4 then gives four reasons the evidence falls short. Each reason maps onto O1–O3 on slide 5, which stays as it is.

Every claim is either a quote or a count from a paper in `raw/papers/`. The line numbers refer to the pdftotext output, so you can check them.

---

## Slide 3: Problem: Promising in Papers, Rare on the Street

**Top row: "Three types of signal control"** (Xiao et al., 2025; Chen et al., 2022). This is the standard split. Your instinct was right; the v4 split "fixed / actuated / learned" was not.

| Fixed-time | Actuated | Adaptive |
|---|---|---|
| "predetermined timing schedules" | "adjusts signal phases based on real-time detection" | "interacting dynamically with traffic conditions" |
| | 137 runs this, inside a fixed cycle shared with the next signal | Reinforcement learning (RL) is "one emerging approach to adaptive control" (Chen et al., 2022) |

**Middle row: two facts side by side.**
- **In research:**
  - 470 papers on RL signal control, 2015–2025 (Xiao et al., 2025).
  - "significant improvements over fixed and actuated algorithms in simulations" (Chen et al., 2022).
- **On the street:**
  - "RL-based TSC algorithms have never been deployed" (Chen et al., 2022).
  - "field deployment remains rare" (Zou et al., 2025).

**Box at the bottom:**
> **Problem:** an agency cannot tell from published results whether a learned controller would beat what it already runs, at its own intersection, with its own traffic.

**Sources checked:**
- Xiao et al. 2025, intro p.1: "three categories: fixed-time control, actuated control, and adaptive control"; line 140 for the 470 papers.
- Chen, Fang & Sadeh 2022, *The Real Deal*: §2.1, "Three main types ... fixed-time ... actuated ... adaptive"; §2.2, "One emerging approach to adaptive control has been reinforcement learning"; lines 60–61 and 66.
- Zou et al. 2025, *Traffic-R1*: line 195.

## Slide 4: Why the Evidence Falls Short

**Four numbered rows. Each row: question, what the literature shows, and the objective it feeds.**

1. **A realistic test?**
   - "A majority of works (62%)" use synthetic road networks (Noaeen et al., 2022, cited in Chen et al., 2022).
   - Real-data studies (Kwesiga et al., 2025; Meess et al., 2024; Li et al., 2024) build their simulation from field data. None reports checking it against the field, and they test on the same data.
   - Feeds **O1**.
2. **Better than what is installed?**
   - Mostly compared with weak baselines\*.
   - Tests against engineer-tuned actuated control "are rarely carried out" (Meess et al., 2024).
   - Feeds **O2**.
3. **When does it pay off?**
   - Three papers give three answers on how traffic level changes the gain: it shrinks (Sahachaiseree & Oguchi, 2025), it grows (El-Tantawy et al., 2014), it stays the same (Alegre et al., 2020).
   - In a field test of an adaptive system, the gain was largest at midday (Smith et al., 2013).
   - Feeds **O2**.
4. **Better for whom?**
   - Results are reported as one average over all cars.
   - Fairness, meaning "all road users receive equitable access", is listed as an open challenge (Xiao et al., 2025, §5.6).
   - Feeds **O3**.

**Footer:**
- Base method: linear RL with LSTDQ (Sahachaiseree & Oguchi, 2025).
- \* in the studies we reviewed

**Sources checked:**
- Chen et al. 2022: line 364 ("62% per [10]", where [10] = Noaeen et al.).
- Smith et al. 2013, *SURTRAC*: Table 1 and "the largest improvement is observed during the Mid Day period".
- Xiao et al. 2025: §5.6 Fairness.

**Slide 5 then needs one small change.** The gap tags become:
- O1 = gap 1
- O2 = gaps 2, 3
- O3 = gap 4

**Caveats for you:**
- SURTRAC is adaptive control, not RL. The deck's goal says "adaptive and learned", so it fits.
- SURTRAC's figures are percentages from their paper. That's fine as a citation, but the script doesn't read them out.
- Chen 2022's "never deployed" is as of 2022. That's why Zou 2025's "remains rare" sits next to it, since Zou reports its own field test.

---

## Slide 9: Methods Compared, grouped by the same three types

Use the same three headings as slide 3, so the audience sees where each method sits:

| Fixed-time | Actuated | Adaptive |
|---|---|---|
| **Webster**: textbook schedule from train-day counts | **GDOT plan**: deployed today and checked against GDOT's log. Greens follow detectors inside a fixed cycle shared with the next signal | **MaxPressure**: green to the longest queue (rule-based) |
| | **Actuated (no cycle)**: same controller and settings without the fixed cycle. A what-if, and the reference. Same as the GDOT plan at night | **LSTDQ** (base method), **Q-learning**, **ARS**: linear learners. Same features, different ways to learn the weights |

Keep the existing bottom line: "Same network, demand, detectors and safety rules for all: only the decision differs".

**Note:** calling MaxPressure "adaptive" fits Chen 2022's definition ("more complex prediction and optimization algorithms"). If someone objects, it is a rule that responds to queues; label it "adaptive, rule-based".


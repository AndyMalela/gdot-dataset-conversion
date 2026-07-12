Docs are consistent now. Here's a status recap while the corrected eval runs:

What just happened: your two questions caught two real problems, both now fixed:

The "peak" window I used for the first replication was actually a moderate-load window, not the peak (all days peak PM, not AM) — corrected.
Your "why does demand end at 18:00?" question led directly to finding that my drained held-out eval was silently pulling in 4 extra hours of real demand (the .rou.xml is full-day), on top of a separate truncation bug that had produced an impossible "more traffic, less delay" result.
The fix: eval_heldout.py now evaluates on the full day (using all your 24h data, exactly as you were pointing toward), with an end-of-day drain so every vehicle completes and gets counted, and with a fixed-time baseline under identical conditions so the numbers are actually anchored. Both bugs are documented in REPORT.md so the flawed inline numbers can't be mistaken for real ones.

The corrected full-day held-out run (RL vs fixed-time on 0508 at 1.0×/1.3×/1.5×) is executing now — I'll report the anchored numbers when the rows come in. This is the first evaluation that'll actually tell us whether the domain-randomized agent generalizes to an unseen day, so it's worth getting right rather than fast.

Remote Control is active. View and control this session at https://claude.ai/code/session_01X5xTsjkQPUNbjLhc55oaXe

<task-notification>
<task-id>byv6rh5h0</task-id>
<summary>Monitor event: "Full-day held-out eval rows (RL vs fixed-time per scale) + errors"</summary>
<event>Held-out day 0508, FULL DAY drained to 30:00, RL(domain-randomized) vs Webster fixed-time
scale | controller |   thru |  delay[s] |  halts
1.0 | RL in-range |  45045 |    160.20 |  0.832
| fixed-time |  51530 |     53.86 |  0.728  (RL delay +197.5%)
1.3 | RL in-range |  43381 |    173.84 |  0.969
| fixed-time |  67124 |     61.47 |  0.736  (RL delay +182.8%)
1.5 | RL extrap  |  48728 |    163.36 |  0.928
| fixed-time |  77253 |     66.89 |  0.738  (RL delay +144.2%)</event>
If this event is something the user would act on now, send a PushNotification. Routine or benign output doesn't need one.
</task-notification>
Bash Read completed full-day held-out eval results
IN
cat "/tmp/claude-1000/-home-andy-Downloads-GDOT/6766a157-d626-40c0-a93a-d34bc7a67eb5/tasks/b0k2n7w22.output"

OUT
Held-out day 0508, FULL DAY drained to 30:00, RL(domain-randomized) vs Webster fixed-time

scale | controller |   thru |  delay[s] |  halts
----------------------------------------------------
  1.0 | RL in-range |  45045 |    160.20 |  0.832
      | fixed-time |  51530 |     53.86 |  0.728  (RL delay +197.5%)
----------------------------------------------------
  1.3 | RL in-range |  43381 |    173.84 |  0.969
      | fixed-time |  67124 |     61.47 |  0.736  (RL delay +182.8%)
----------------------------------------------------
  1.5 | RL extrap  |  48728 |    163.36 |  0.928
      | fixed-time |  77253 |     66.89 |  0.738  (RL delay +144.2%)
----------------------------------------------------
Now I have clean, anchored numbers — and they're a clear negative result, which I'll report straight rather than spin:

Scale	RL delay	Fixed-time delay	RL throughput	Fixed throughput
1.0×	160.2 s	53.9 s	45,045	51,530
1.3×	173.8 s	61.5 s	43,381	67,124
1.5×	163.4 s	66.9 s	48,728	77,253
The RL agent is 2–3× worse than fixed-time on delay, and clears far fewer vehicles (the throughput gap widening with scale = it's gridlocking under load). That's real — the drained full-day eval isn't truncation-biased, and the throughput gap confirms genuine gridlock, not a metric artifact.

But I have to flag a fairness problem before you read too much into it: this full-day eval is unfair to an agent that was trained only on the 15:00–18:00 peak window. It's being scored across ~20 hours of light/overnight traffic it never trained on — and with a −queue reward, on near-empty roads every stage looks equally good, so the greedy policy degenerates (picks a stage and starves the others under trivial load, racking up delay that never happens under a fixed cycle). The throughput gap being smallest at 1.0× and largest at 1.3–1.5× is a hint the damage is a mix of that off-peak degeneracy plus genuine peak gridlock.

So this answers "deploy a peak-trained agent all day" (it fails), but not the actual scientific question "does the method beat fixed-time in the regime it was trained for." For that I need a clean peak-window eval — which requires a route file where demand genuinely stops at 18:00 (the bug earlier was full-day flows leaking in). Let me build that and get the fair in-distribution number:

Edit eval_heldout.py
Added 19 lines
You've hit your session limit · resets 3:40am (Asia/Tokyo)

Remote Control disabled.

seems like session limit stopped you. you finished?
No, I didn't finish — I was interrupted mid-way through building the fair peak-window eval. Let me check the exact state so I can tell you precisely where things stand.

Bash Assess current state of eval_heldout and running processes
IN
cd /home/andy/Downloads/GDOT/rlagent
echo "=== running procs ==="; pgrep -af "python3 (train|eval)" | grep -v grep || echo "none"
echo "=== does eval_heldout still call full-day only? check main ==="; grep -n "peak_window_rou\|eval_rl\|eval_fixed\|def main\|BEGIN\b" eval_heldout.py | head
echo "=== syntax check ==="; python3 -c "import ast; ast.parse(open('eval_heldout.py').read()); print('eval_heldout.py parses OK')"
echo "=== results present ==="; ls results/ | grep -v FAILED | grep -v "run[123]"

OUT
=== running procs ===
none
=== does eval_heldout still call full-day only? check main ===
40:BEGIN = 0
41:PEAK_BEGIN, PEAK_END = 54000, 64800   # 15:00-18:00
45:def peak_window_rou() -> str:
55:            if PEAK_BEGIN <= int(m.group(1)) < PEAK_END:
63:def eval_rl(weights, scale, seed=9999):
65:    env = Sig7065Env(rou_path(), begin=BEGIN, end=DRAIN_END, seed=seed,
78:def eval_fixed(scale, seed=9999):
81:    _, _, greens = webster_plan(DAY, PEAK_BEGIN, PEAK_END)
83:    env = Sig7065Env(rou_path(), begin=BEGIN, end=DRAIN_END, seed=seed,
103:def main():
=== syntax check ===
eval_heldout.py parses OK
=== results present ===
REPORT.md
ti_heldout_fixed_x1.0.xml
ti_heldout_fixed_x1.3.xml
ti_heldout_fixed_x1.5.xml
ti_heldout_rl_x1.0.xml
ti_heldout_rl_x1.3.xml
ti_heldout_rl_x1.5.xml
train_0507_s0.csv
train_random_s0.csv
tripinfo_fixed_0507.xml
tripinfo_random_0508_x1.0.xml
tripinfo_random_0508_x1.5.xml
tripinfo_random_0508_x1.8.xml
tripinfo_rl_0507.xml
weights_0507_s0.npy
weights_random_s0.npy
Here's the honest state: not finished. I was interrupted right after adding the peak_window_rou() helper but before wiring it into the eval functions — they still point at the full-day route file. So the file parses but the fair peak-window eval isn't actually hooked up or run. Let me finish the wiring so the code is at least in a coherent, runnable state (as an opt-in flag), rather than leaving a half-connected helper:

Read eval_heldout.py (lines 64-108)
make quick summary of what you did im moving chats
Session summary — Sahachaiseree replication built on SIG#7065
Built (rlagent/ folder)
stages.py — 8-stage action space (NEMA dual-ring combos = paper's Fig. 5 structure), left-turn treatment computed from GDOT Policy 6785-2 warrants against your real calibrated demand (EB/NB/SB lefts protected, WB-left permissive-only), interstage timing computed from real geometry via ITE formulas (yellow 4.0s, all-red 3.0s).
sumo_env.py — TraCI environment implementing the paper's MDP (40-dim state = stage one-hot + 32 per-lane counts; reward = −Σqueue).
lstdq.py — linear FA + closed-form LSTDQ solver, verified against a toy MDP's analytic optimum.
fixed_time.py — Webster pretimed baseline from the same portal volumes.
train.py — single-day/window training loop.
train_random.py — domain-randomized training: random day (0505/0506/0507) × random scale (0.5–1.3×) per episode on the real PM peak window, with 0508 held out entirely.
watch.py — load trained weights and watch the agent drive sumo-gui live.
eval_heldout.py — INCOMPLETE, see below.
Docs updated throughout: README.md, plan.md, regulations.md, results/REPORT.md.
Key findings (all documented in-file, with failed-run artifacts kept as evidence)
Training required 3 fixes to converge vs. the paper's literal method: semi-MDP reward accumulation (paper's per-decision reward sampling made stage-switching artificially cheap → thrash policy), accumulated-experience refits (single-episode refits oscillate), cycle-scale discount horizon (γ=0.9/s starves low-volume approaches invisibly; γ=0.99/s fixed it). Run 4 converged cleanly.
I mislabeled the first eval window as "AM peak" — checked the data, all 4 days actually peak in the PM (~15:15–18:05); corrected everywhere.
Held-out (0508) evaluation had two bugs, both found via your questions: truncation bias (stopped mid-congestion, dropping uncompleted trips → impossible "more demand, less delay" result), and a windowing artifact (extending sim end to "drain" a window actually pulled in the next few hours of real full-day demand, since the .rou.xml spans 24h, not just the window).
Fixed full-day held-out eval ran and gave a real, clean, negative result: RL agent trained on peak-only is 2–3× worse than fixed-time on delay across scales 1.0–1.5×, with throughput gap widening at higher scale (genuine gridlock). But this eval is unfair — it scores a peak-trained agent across ~20 hours of light/overnight traffic it never trained on, where −queue reward degenerates on empty roads.
Left unfinished (mid-edit when interrupted)
eval_heldout.py has a peak_window_rou() helper (writes a route file containing only the 15:00–18:00 flows, to get a fair apples-to-apples peak-only comparison) that's written but not wired in — eval_rl/eval_fixed still reference the full-day route file. Needs: swap rou_path() calls to peak_window_rou() in both eval functions, then rerun. That's the next concrete step — get the fair in-distribution (peak vs peak) number before drawing conclusions about whether the method actually works.

Bottom line for whoever picks this up
Replication mechanically works (converges, controls sensibly) but hasn't yet beaten fixed-time on any clean, fair comparison — first AM-mislabeled window: close but slightly worse; full-day-on-peak-trained-agent: worse (but unfairly scored). The real verdict is still pending on the peak-vs-peak comparison.
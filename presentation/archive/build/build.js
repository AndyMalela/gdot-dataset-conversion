// Midterm deck, Ritsumeikan template look (4:3). node build.js -> midterm_137.pptx
const pptxgen = require("pptxgenjs");
const path = require("path");
const IMG = path.join(__dirname, "..", "tplimg");

const RED = "A52026", TITLE = "990000", BLUE = "1F497D", BLACK = "000000", GREY = "595959", LIGHT = "F2F2F2";
const HF = "Tahoma", BF = "Arial";

const pres = new pptxgen();
pres.layout = "LAYOUT_4x3";                       // 10 x 7.5 in, as the template
pres.title = "When Does Adaptive Signal Control Pay Off?";
pres.theme = { headFontFace: HF, bodyFontFace: BF };

const frame = [
  { rect: { x: 0, y: 0, w: 0.42, h: 7.5, fill: { color: RED }, line: { color: RED } } },
  { image: { x: 0.5, y: 0.1, w: 0.565, h: 1.05, path: path.join(IMG, "rlogo.png") } },
  { image: { x: 0.05, y: 4.9, w: 0.32, h: 1.72, path: path.join(IMG, "beyond.png") } },
  { image: { x: 8.85, y: 6.9, w: 1.05, h: 0.35, path: path.join(IMG, "ict.png") } },
];
pres.defineSlideMaster({
  title: "CONTENT", background: { color: "FFFFFF" }, objects: [...frame,
    { placeholder: { options: { name: "title", type: "title", x: 1.3, y: 0.3, w: 8.45, h: 0.85, align: "right",
                                fontFace: HF, fontSize: 36, color: TITLE, valign: "middle" }, text: "" } }],
  slideNumber: { x: 8.35, y: 6.88, w: 0.5, h: 0.35, color: RED, fontFace: BF, fontSize: 14, align: "right" },
});
pres.defineSlideMaster({ title: "TITLE", background: { color: "FFFFFF" }, objects: frame });

// bullets: [text, level] -> level 0 red dot + blue, level 1 en dash + black
function bullets(slide, items, opt = {}) {
  const runs = items.map(([t, lvl, extra], i) => ({
    text: t,
    options: Object.assign(lvl === 0
      ? { bullet: { code: "25CF" }, color: BLUE, fontSize: opt.f0 || 26, indentLevel: 0, paraSpaceBefore: i ? (opt.gap || 14) : 0 }
      : { bullet: { code: "2013" }, color: BLACK, fontSize: opt.f1 || 20, indentLevel: 1, paraSpaceBefore: 3 },
      extra || {}, { breakLine: i < items.length - 1 }),
  }));
  slide.addText(runs, { x: opt.x || 0.9, y: opt.y || 1.35, w: opt.w || 8.8, h: opt.h || 5.4, fontFace: BF, valign: "top",
                        margin: 0, isTextBox: true });
}
// keep the template's red bullet dot: pptxgenjs colours bullets with the text, so level-0 dots are drawn per paragraph
// (simple approach: colour stays blue; acceptable). Notes go in addNotes.

function content(title, notes) {
  const s = pres.addSlide({ masterName: "CONTENT" });
  s.addText(title, { placeholder: "title" });
  if (notes) s.addNotes(notes);
  return s;
}

// ---------------------------------------------------------------- 1 title
{
  const s = pres.addSlide({ masterName: "TITLE" });
  s.addText("When Does Adaptive Signal Control Pay Off?", { x: 0.8, y: 1.55, w: 9.0, h: 1.3, align: "center", fontFace: HF,
            fontSize: 38, bold: true, color: TITLE, isTextBox: true });
  s.addText("– A Comparison of Control Methods on Real Traffic Data –", { x: 0.8, y: 2.85, w: 9.0, h: 0.6, align: "center",
            fontFace: HF, fontSize: 22, color: BLUE, isTextBox: true });
  s.addText([{ text: "[Your Name]", options: { fontSize: 26, color: BLUE, breakLine: true } },
             { text: "[Student ID]", options: { fontSize: 16, color: BLACK } }],
            { x: 0.8, y: 3.8, w: 9.0, h: 0.9, align: "center", fontFace: BF, isTextBox: true });
  s.addText("November 16th, 2026", { x: 0.8, y: 5.0, w: 9.0, h: 0.4, align: "center", fontFace: BF, fontSize: 18, isTextBox: true });
  s.addText([{ text: "College of Information Science and Engineering", options: { fontSize: 18, breakLine: true } },
             { text: "Ritsumeikan University", options: { fontSize: 16 } }],
            { x: 0.8, y: 5.75, w: 9.0, h: 0.8, align: "center", fontFace: BF, isTextBox: true });
  s.addNotes("(15 s) Title only. My research compares signal control methods on a real Atlanta intersection.");
}

// ---------------------------------------------------------------- 2 agenda
{
  const s = content("Agenda", "(10 s) Skip quickly.");
  bullets(s, [["Background", 0], ["Related Work", 0], ["Research Objective", 0], ["Proposed Approach", 0],
              ["Experiments", 0], ["Conclusion", 0]], { y: 1.6, f0: 30, gap: 12 });
}

// ---------------------------------------------------------------- 3 background
{
  const s = content("Background", "(45 s) Agencies have to pick a control method per intersection. Learned controllers report " +
    "big gains, but mostly at one demand level and against weak baselines, so an agency cannot tell where they actually pay off.");
  bullets(s, [
    ["Agencies choose how each signal is timed", 0],
    ["Fixed-time, actuated, adaptive rules, learned (RL)", 1],
    ["Learned controllers report large gains", 0],
    ["Mostly one demand level, weak baselines", 1],
    ["No rule for where each method pays off", 0],
    ["Gain depends on traffic conditions", 1, { color: TITLE }],
  ], { y: 1.5, gap: 22 });
}

// ---------------------------------------------------------------- 4 related work
{
  const s = content("Related Work", "(50 s) Three studies, three answers to the same question: how does the gain of learned " +
    "control change with demand. They also used different baselines and constraints. That disagreement is my gap.");
  bullets(s, [
    ["Sahachaiseree & Oguchi (2025)", 0], ["Linear RL vs actuated control", 1], ["Gain shrinks as demand rises", 1],
    ["El-Tantawy et al. (2014)", 0], ["RL vs pretimed / actuated, real site", 1], ["Gain grows at high demand", 1],
    ["Alegre et al. (2020)", 0], ["Linear RL vs adaptive rule (Lämmer)", 1], ["Demand affects all methods equally", 1],
  ], { y: 1.3, h: 4.9, gap: 12 });
  s.addText("Same question, three answers", { x: 1.0, y: 6.25, w: 7.0, h: 0.45, fontFace: BF, fontSize: 22, bold: true,
            color: TITLE, isTextBox: true, margin: 0 });
}

// ---------------------------------------------------------------- 5 research objective
{
  const s = content("Research Objective", "(45 s) The goal is not a leaderboard. I want to know under which conditions " +
    "adaptivity helps, and why. H1 and H2 were fixed before any result.");
  bullets(s, [
    ["Find when adaptive control beats the actuated control already deployed, and why", 0],
    ["Hypotheses (fixed before results)", 0],
    ["H1: below capacity, all responsive methods tie", 1],
    ["H2: near capacity, the methods separate", 1],
    ["Equal field rules for every method", 1],
  ], { y: 1.45, gap: 24 });
}

// ---------------------------------------------------------------- 6 proposed approach: testbed loop (diagram)
{
  const s = content("Proposed Approach", "(75 s) How the testbed works. Left: everything comes from GDOT's own signal data: " +
    "5-minute counts per movement, the real timing plans, and where the detectors are. Middle: the SUMO digital twin runs a " +
    "loop every second. Cars move, detectors placed like GDOT's see them, the controller decides only one thing - extend the " +
    "current green or end it - and a rule engine enforces the safety rules a real controller has: minimum green, yellow and " +
    "red clearance, ring order, pedestrian walk. Every method plugs into the same slot, so differences come from the decision " +
    "alone. Right: delay per vehicle per hour, grouped by how saturated the intersection was.");
  const box = (x, y, w, h, fill, line) => s.addShape(pres.shapes.ROUNDED_RECTANGLE,
    { x, y, w, h, fill: { color: fill }, line: { color: line || fill, width: 1.25 }, rectRadius: 0.08 });
  const txt = (t, x, y, w, h, o = {}) => s.addText(t, Object.assign({ x, y, w, h, fontFace: BF, fontSize: 12, color: BLACK,
    align: "center", valign: "middle", isTextBox: true, margin: 2 }, o));
  const arrow = (x, y, w, h, o = {}) => s.addShape(pres.shapes.LINE, Object.assign({ x, y, w, h,
    line: { color: "404040", width: 2, endArrowType: "triangle" } }, o));

  // data inputs
  box(0.6, 1.45, 1.75, 4.6, LIGHT, "BFBFBF");
  txt("GDOT signal data\n(ATSPM)", 0.6, 1.5, 1.75, 0.6, { bold: true, fontSize: 12 });
  [["5-min counts\nper movement", 2.25], ["Real timing\nplans", 3.35], ["Detector\nlayout", 4.45]].forEach(([t, y]) => {
    s.addShape(pres.shapes.FLOWCHART_DOCUMENT, { x: 0.75, y, w: 1.45, h: 0.9, fill: { color: "FFFFFF" }, line: { color: "7F7F7F" } });
    txt(t, 0.75, y, 1.45, 0.8, { fontSize: 11 });
  });
  arrow(2.38, 3.7, 0.42, 0);

  // digital twin with the 1-s loop
  box(2.85, 1.45, 4.55, 4.6, "FFFFFF", RED);
  txt("SUMO digital twin  (loop every 1 s)", 2.9, 1.5, 4.45, 0.4, { bold: true, color: TITLE, fontSize: 13 });
  const node = (t, sub, x, y, fill) => { box(x, y, 1.9, 0.95, fill, fill);
    txt([{ text: t, options: { bold: true, fontSize: 12, color: "FFFFFF", breakLine: true } },
         { text: sub, options: { fontSize: 11, color: "FFFFFF" } }], x, y, 1.9, 0.95); };
  node("Vehicles", "real counts, 5-min bins", 3.05, 2.05, "4472C4");
  node("Detectors", "placed like GDOT's", 5.3, 2.05, "4472C4");
  node("Controller", "extend or end green?", 5.3, 3.6, RED);
  node("Rule engine", "min green, clearance,\nring order, walk", 3.05, 3.6, "7F7F7F");
  arrow(4.97, 2.52, 0.31, 0);                                   // vehicles -> detectors
  arrow(6.25, 3.02, 0, 0.56);                                   // detectors -> controller
  arrow(4.97, 4.07, 0.31, 0, { flipH: true });                  // controller -> engine
  arrow(4.0, 3.02, 0, 0.56, { flipV: true });                   // engine -> vehicles (signal)
  txt("signal", 3.25, 3.1, 0.75, 0.3, { fontSize: 10, color: GREY, italic: true });
  txt("one of 7 methods plugs in here:\nWebster · GDOT plan · actuated · MaxPressure\nLSTDQ · Q-learning · ARS", 3.0, 4.75, 4.25, 0.85,
      { fontSize: 12, color: BLUE });
  txt("same network, demand, detectors and rules for all", 3.0, 5.55, 4.25, 0.4, { fontSize: 10.5, italic: true, color: TITLE });
  arrow(7.43, 3.7, 0.42, 0);

  // outputs
  box(7.9, 1.45, 1.85, 4.6, LIGHT, "BFBFBF");
  txt("Output", 7.9, 1.5, 1.85, 0.4, { bold: true });
  [["Delay per vehicle,\nevery hour", 2.1], ["Grouped by\nsaturation X_c", 3.35], ["When and why\neach method wins", 4.6]].forEach(([t, y], i) => {
    box(8.0, y, 1.65, 0.95, i === 2 ? RED : "FFFFFF", i === 2 ? RED : "7F7F7F");
    txt(t, 8.0, y, 1.65, 0.95, { fontSize: 11, color: i === 2 ? "FFFFFF" : BLACK, bold: i === 2 });
    if (i < 2) arrow(8.82, y + 0.97, 0, 0.27);
  });
  txt("Only the decision differs between methods, so any difference comes from the decision", 0.6, 6.2, 9.15, 0.45,
      { fontSize: 14, color: BLUE, bold: true });
}

// ---------------------------------------------------------------- 7 how the learned controller works (diagram)
{
  const s = content("How the Learned Controller Works", "(60 s) The learned controller, LSTDQ, is linear. Every second it " +
    "turns the detector readings into features - how many cars are queued at each phase, whether the stop bar is occupied, " +
    "time since the last car, how long the current green has run. It scores 'extend' and 'end' as a weighted sum of those " +
    "features and picks the higher one. The weights come from recorded training days: each decision and the delay that " +
    "followed is stored, and least squares solves for the weights directly. Repeat five times. Q-learning and ARS use the " +
    "same features but learn the weights differently - that is what they are compared on.");
  const box = (x, y, w, h, fill, line) => s.addShape(pres.shapes.ROUNDED_RECTANGLE,
    { x, y, w, h, fill: { color: fill }, line: { color: line || fill, width: 1.25 }, rectRadius: 0.08 });
  const txt = (t, x, y, w, h, o = {}) => s.addText(t, Object.assign({ x, y, w, h, fontFace: BF, fontSize: 12, color: BLACK,
    align: "center", valign: "middle", isTextBox: true, margin: 3 }, o));
  const arrow = (x, y, w, h, o = {}) => s.addShape(pres.shapes.LINE, Object.assign({ x, y, w, h,
    line: { color: "404040", width: 2, endArrowType: "triangle" } }, o));

  txt("Deciding (every 1 s on the road)", 0.6, 1.35, 9.1, 0.4, { bold: true, color: TITLE, fontSize: 14, align: "left" });
  const steps = [
    ["Detector readings", "occupancy, counts\nper lane", "4472C4"],
    ["Features φ", "queue, gap since last car,\nelapsed green, other ring", "4472C4"],
    ["Score both actions", "Q(extend) = w·φ\nQ(end) = w·φ", RED],
    ["Pick the higher", "rule engine then\nchecks safety", "7F7F7F"],
  ];
  steps.forEach(([t, sub, c], i) => {
    const x = 0.6 + i * 2.32;
    box(x, 1.85, 2.0, 1.2, c, c);
    txt([{ text: t, options: { bold: true, color: "FFFFFF", fontSize: 13, breakLine: true } },
         { text: sub, options: { color: "FFFFFF", fontSize: 11.5 } }], x, 1.85, 2.0, 1.2);
    if (i < 3) arrow(x + 2.02, 2.45, 0.28, 0);
  });

  txt("Learning (offline, training days only)", 0.6, 3.45, 9.1, 0.4, { bold: true, color: TITLE, fontSize: 14, align: "left" });
  const learn = [
    ["Run training days", "29 weekdays,\n4 windows each", "FFFFFF"],
    ["Record each decision", "(φ, action, delay that\nfollowed, next φ)", "FFFFFF"],
    ["Least squares", "solve A w = b\nfor the weights", "FFFFFF"],
    ["New policy", "greedy on new w;\nrepeat 5 times", "FFFFFF"],
  ];
  learn.forEach(([t, sub], i) => {
    const x = 0.6 + i * 2.32;
    box(x, 3.95, 2.0, 1.2, "FFFFFF", RED);
    txt([{ text: t, options: { bold: true, color: TITLE, fontSize: 13, breakLine: true } },
         { text: sub, options: { color: BLACK, fontSize: 11.5 } }], x, 3.95, 2.0, 1.2);
    if (i < 3) arrow(x + 2.02, 4.55, 0.28, 0);
  });
  // loop back from "New policy" to "Run training days"
  s.addShape(pres.shapes.LINE, { x: 7.56, y: 5.17, w: 0, h: 0.3, line: { color: "404040", width: 2 } });
  s.addShape(pres.shapes.LINE, { x: 1.6, y: 5.47, w: 5.96, h: 0, line: { color: "404040", width: 2 } });
  arrow(1.6, 5.17, 0, 0.3, { flipV: true });
  // learned w feeds the decision
  s.addShape(pres.shapes.LINE, { x: 6.2, y: 3.08, w: 0, h: 0.85, line: { color: RED, width: 2, dashType: "dash", beginArrowType: "triangle" } });
  txt("weights w", 6.25, 3.2, 1.1, 0.3, { fontSize: 10, color: RED, italic: true, align: "left" });
  txt("Q-learning: same features, weights updated one step at a time   ·   ARS: searches w directly on delay",
      0.6, 5.75, 9.1, 0.5, { fontSize: 12.5, color: BLUE });
}

// ---------------------------------------------------------------- 8 methods compared
{
  const s = content("Methods Compared", "(45 s) Each method is chosen to differ from another in one factor, so a difference " +
    "can be explained. The right column is what each pair tests.");
  const H = (t) => ({ text: t, options: { bold: true, color: "FFFFFF", fill: { color: "4F81BD" } } });
  const rows = [
    [H("Method"), H("How it decides"), H("Tests")],
    ["Webster", "fixed splits from design-hour flow", "no response (floor)"],
    ["GDOT plan", "real coordinated plans", "today's practice"],
    ["Actuated", "end green when no car for a few s", "reference"],
    ["MaxPressure", "end green if another queue is longer", "queue info, no learning"],
    ["LSTDQ", "learned linear score, least squares", "learned vs rule"],
    ["Q-learning", "same model, online updates", "batch vs online"],
    ["ARS", "searches policy weights on delay", "value vs policy search"],
  ];
  s.addTable(rows, { x: 0.75, y: 1.45, w: 9.0, colW: [1.75, 4.25, 3.0], fontFace: BF, fontSize: 14, color: BLACK,
                     border: { type: "solid", color: "FFFFFF", pt: 1.5 }, fill: { color: "DCE6F2" }, rowH: 0.52, valign: "middle" });
  s.addText("Learners share one state and reward; DQN after the midterm", { x: 0.75, y: 5.85, w: 9.0, h: 0.4,
            fontFace: BF, fontSize: 14, color: BLUE, isTextBox: true, margin: 0 });
}

// ---------------------------------------------------------------- 9 experimental setup
{
  const s = content("Experimental Setup", "(45 s) One real intersection in Atlanta, data from GDOT only. Training and " +
    "validation days are chronological, the test days are locked. The equivalence margin was fixed before reading any result. " +
    "Saturation is the standard HCM critical v/c ratio.");
  bullets(s, [
    ["Site: W. Paces Ferry Rd @ E. Andrews Dr", 0], ["Atlanta, GDOT ATSPM data only, Mar–May 2026", 1],
    ["Days split by time", 0], ["Train 29 · validation 20 · test 10 (locked)", 1],
    ["Learners: 5 training seeds each", 0], ["Tie = within 5 % or 2 s/veh, fixed in advance", 1],
    ["Saturation X_c = Y·C / (C − L)  (HCM)", 0], ["Real demand scaled ×1 – ×2.5 to reach capacity", 1],
  ], { y: 1.35, f0: 24, f1: 19, gap: 12 });
}

// ---------------------------------------------------------------- 10 results: real days
{
  const s = content("Results: Real Days", "(60 s) On the 20 real validation days the site never reaches capacity: peak " +
    "X_c 0.87. Every adaptive method is within the tie margin of actuated control on ordinary days. Webster is hurt by one " +
    "Friday evening when demand was far above its design. Preliminary: one simulation seed, model not yet validated.");
  const H = (t) => ({ text: t, options: { bold: true, color: "FFFFFF", fill: { color: "4F81BD" } } });
  const rows = [[H("Method"), H("Delay (s/veh)"), H("vs actuated")],
    ["Actuated", "17.1", "–"], ["LSTDQ", "17.4", "tie"], ["ARS", "18.6", "tie*"], ["MaxPressure", "19.0", "tie*"],
    ["GDOT plan", "20.9", "+3.8"], ["Q-learning", "21.1", "tie* (1 bad seed)"], ["Webster", "48.5", "+31"]];
  s.addTable(rows, { x: 0.75, y: 1.45, w: 4.9, colW: [1.7, 1.45, 1.75], fontFace: BF, fontSize: 14, color: BLACK,
                     border: { type: "solid", color: "FFFFFF", pt: 1.5 }, fill: { color: "DCE6F2" }, rowH: 0.48, valign: "middle" });
  s.addText("Table 1. 20 validation days, median over 5 seeds.  * tie on 19 of 20 days", { x: 0.75, y: 5.4, w: 4.9, h: 0.5,
            fontFace: BF, fontSize: 11, color: GREY, isTextBox: true, margin: 0 });
  bullets(s, [["Peak X_c = 0.87", 0], ["Below capacity", 1], ["Adaptive methods tie", 0], ["H1 supported", 1, { color: TITLE }],
              ["One surge morning separates them", 0], ["Apr 28, X_c ≈ 1", 1]], { x: 5.95, y: 1.5, w: 3.85, h: 4.5, f0: 21, f1: 17, gap: 16 });
}

// ---------------------------------------------------------------- 11 results: scaled demand (chart)
{
  const s = content("Results: Towards Capacity", "(75 s) Same real demand profile scaled up, labelled by peak X_c. Up to " +
    "about 1.1 the adaptive methods stay together. At 1.31 they separate: MaxPressure is lowest, the learners fall behind - " +
    "but they were trained only on real traffic, so this is robustness to unseen demand. Above 1.5 everything is " +
    "oversaturated and delay comparisons stop being meaningful.");
  const labels = ["0.87 (real)", "1.09", "1.31", "1.52"];
  const series = [
    ["Actuated", [17.0, 21.7, 48.0, 178.5]], ["MaxPressure", [17.8, 22.2, 40.1, 157.9]], ["LSTDQ", [17.5, 21.6, 51.1, 250.2]],
    ["Q-learning", [17.1, 22.4, 58.5, 234.8]], ["ARS", [18.3, 22.5, 47.3, 307.4]], ["GDOT plan", [20.9, 32.2, 84.0, 290.0]],
  ].map(([name, values]) => ({ name, labels, values }));
  s.addChart(pres.charts.LINE, series, {
    x: 0.75, y: 1.3, w: 6.1, h: 4.75, chartColors: ["1F497D", "E36C09", "4F8A3C", "7B4FA0", "2A9DB0", "7F7F7F"],
    lineSize: 2.5, lineDataSymbol: "circle", lineDataSymbolSize: 7, valAxisLogScaleBase: 10, valAxisMinVal: 10,
    valAxisMaxVal: 1000, showValAxisTitle: true, valAxisTitle: "Delay (s/veh, log)", valAxisTitleFontSize: 12,
    showCatAxisTitle: true, catAxisTitle: "Peak saturation X_c", catAxisTitleFontSize: 12, catAxisLabelFontSize: 11,
    valAxisLabelFontSize: 11, showLegend: true, legendPos: "b", legendFontSize: 11,
    valGridLine: { color: "D9D9D9", size: 0.5 }, catGridLine: { style: "none" },
    catAxisLabelFontFace: BF, valAxisLabelFontFace: BF, legendFontFace: BF,
  });
  s.addText("Figure 1. 5 days, seed 0; Webster off scale", { x: 0.75, y: 6.05, w: 6.1, h: 0.35, fontFace: BF, fontSize: 11,
            color: GREY, isTextBox: true, margin: 0 });
  bullets(s, [["≤ 1.1: all tie", 0], ["≈ 1.3: they separate", 0], ["MaxPressure lowest", 1],
              ["Learners saw only real traffic", 1, { color: TITLE }], ["> 1.5: all gridlock", 0]],
          { x: 7.05, y: 1.5, w: 2.75, h: 4.5, f0: 19, f1: 15, gap: 16 });
}

// ---------------------------------------------------------------- 12 conclusion
{
  const s = content("Conclusion", "(60 s) Preliminary findings, honest limits, and what comes next. The data finding is " +
    "worth saying: GDOT's presence-zone counts undercount queued traffic - found at two intersections.");
  bullets(s, [
    ["Findings (preliminary)", 0], ["Below capacity, adaptivity ≈ well-set actuated", 1], ["Methods separate only near capacity", 1],
    ["Learner seeds vary: deployment risk", 1],
    ["Limitations", 0], ["Validation: splits pass, left-turn timing not yet", 1], ["Side-street counts undercounted by detectors", 1],
    ["One site, one simulation seed", 1],
    ["Future Work", 0], ["Validate, then explain why (mechanism)", 1], ["Train learners at capacity; add DQN", 1],
  ], { y: 1.3, f0: 24, f1: 18, gap: 10 });
}

// ---------------------------------------------------------------- backup slides
{
  const s = content("Backup: Validation Status", "Only if asked.");
  const H = (t) => ({ text: t, options: { bold: true, color: "FFFFFF", fill: { color: "4F81BD" } } });
  const rows = [[H("Attempt"), H("Change"), H("Split ≤ 3 s"), H("Gap-outs ≤ 15 pt")],
    ["1", "settings as evaluated", "19/35", "11/35"], ["2", "passage fitted on train days", "15/35", "16/35"],
    ["3", "+ measured pedestrians", "20/35", "18/35"], ["4", "+ estimated side-street demand", "29/35 ✓", "19/35"], ["5", "+ calibrated permissive left turns", "27/35", "20/35"]];
  s.addTable(rows, { x: 0.75, y: 1.5, w: 9.0, colW: [1.2, 3.8, 2.0, 2.0], fontFace: BF, fontSize: 14, color: BLACK,
                     border: { type: "solid", color: "FFFFFF", pt: 1.5 }, fill: { color: "DCE6F2" }, rowH: 0.5 });
  bullets(s, [["Pass needs 28/35 on both, criteria fixed in advance", 0],
              ["Splits pass once the detector undercount is corrected", 0],
              ["Left turns: field platoons from the next signal leave gaps", 0]], { y: 4.6, f0: 20, gap: 12 });
}
{
  const s = content("Backup: Detector Undercount", "Only if asked.");
  bullets(s, [
    ["GDOT counts = stop-bar zone activations", 0], ["Matches activations in 5-min charts", 1],
    ["A discharging queue keeps the zone on", 0], ["Several cars counted as one", 1],
    ["Estimated factor 1.4–3.0× in daytime", 0], ["Side streets and EB left at this site", 1],
    ["Same defect found earlier at SIG 7065", 0],
  ], { y: 1.4, f0: 24, f1: 19, gap: 14 });
}

pres.writeFile({ fileName: path.join(__dirname, "midterm_137.pptx") }).then((f) => console.log("wrote", f));

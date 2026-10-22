---
title: "How is traffic data represented as model input across the wiki?"
tags: [query, state-representation, sensors, data-pipeline]
date: 2026-05-07
---

# How is traffic data represented as model input?

Query: what physical quantities do papers capture, how do they process them, and what format gets fed to the model?

## What physical quantities they capture

Almost every paper works from the same small set of raw signals measured per lane or per intersection:

- **Vehicle count** — total vehicles on a lane (queued or moving)
- **Waiting/queuing vehicle count** — vehicles at speed ≈ 0
- **Waiting time** — usually the first queuing vehicle's elapsed wait, not aggregate
- **Speed / occupancy** — less common; [[chen2025-roundabout-rl]] uses per-arm speed
- **Phase information** — current phase index, phase timer, phase mask
- **Proximity** — vehicles within x meters of the stop line [[gu2026-pi-elight]]

[[chen2022-real-deal]] surveyed 160 papers: queue length (38%), current phase (11%), vehicle count (10%), position (6%), speed (6%). Those proportions hold across this wiki.

## How it's processed before the model sees it

**Raw flat vector (most common):**
Most papers concatenate scalars into a fixed-length vector. [[lu2025-rl-tsc-ac]] is the most minimal: {queue count per lane, waiting time of first vehicle per lane} for all incoming *and* outgoing lanes — a flat vector of pairs, no transformation. The authors acknowledge this fails under sparse demand because the features carry no information when lanes are nearly empty [[lu2025-rl-tsc-ac]].

[[chen2025-roundabout-rl]] is slightly richer: 26 scalars concatenated — per-arm occupancy/inflow/speed (18), ring-level occupancy and velocity percentiles (3), phase metadata (5) [[chen2025-roundabout-rl]].

**Symbolic scalars — no encoding:**
[[gu2026-pi-elight]] and [[liao2025-symlight]] are unique: features go directly into arithmetic expressions without any neural encoding. π-eLight uses three scalars per lane link (vehicle count, waiting count, vehicles within x meters) on both incoming and outgoing lanes [[gu2026-pi-elight]]. SymLight uses 8 features per movement including occupancy ratios LI/LO = count/capacity [[liao2025-symlight]]. The model *is* the formula — there is no embedding layer.

**Graph-structured (spatial encoding):**
[[shen2025-shlight]] is the most sophisticated spatially. Workers receive local lane features plus a neighbor feature vector from STNet (GCN over 1-hop road topology + GRU for temporal trends). The GCN aggregates neighboring intersection states so each worker sees beyond its own lanes. The manager receives vehicle counts within 50m across its entire region [[shen2025-shlight]].

**Temporal stacking:**
[[meess2024-first-steps]] stacks vehicle counts across multiple signal cycles before feeding them to SAC — the agent sees recent history, not just the current snapshot. Also uniquely includes a one-hot encoding of the current signal programme because T-time semantics differ between programmes [[meess2024-first-steps]].

**Derived/reconstructed state:**
[[meess2024-first-steps]] has the most elaborate real-world preprocessing pipeline. Raw input is sparse inductive loop detector counts. DRIVERS fits Origin-Destination matrices from these counts (r = 0.88–0.99 with real traffic), then runs microscopic re-simulation (Intelligent Driver Model) to produce coherent per-lane vehicle counts. The model never sees raw detector readings [[meess2024-first-steps]].

**LLM-augmented:**
[[da2024-prompt-to-transfer]] appends an LLM-derived dynamics vector (estimated acceleration, deceleration, startup delay given weather/road conditions) to lane-level state via an MLP. The model input is [lane features | LLM dynamics vector | domain metadata] [[da2024-prompt-to-transfer]].

## Format fed to the model

| Paper | Format | Spatial structure | Temporal structure |
|---|---|---|---|
| [[chen2025-roundabout-rl]] | Flat 26-dim vector | None (arms pre-aggregated) | None |
| [[da2024-prompt-to-transfer]] | Flat vector + LLM vector, MLP-fused | None | None |
| [[nguyen2025-trex]] (MPLight) | Pressure scalar per phase (density difference) | Implicit in pressure formulation | None |
| [[lu2025-rl-tsc-ac]] | Flat vector of (queue, wait) pairs | None | None |
| [[shen2025-shlight]] | Graph node features (local + STNet neighbor output) | GCN over road topology | GRU over time |
| [[gu2026-pi-elight]] | Scalars per lane link, direct to expression | Per-lane-link structure | None |
| [[liao2025-symlight]] | 8 scalars per movement, direct to expression | Per-movement structure | None |
| [[meess2024-first-steps]] | Reconstructed counts, stacked across cycles | None | Cycle-level stacking |
| [[xiao2025-oxford-review]] | Surveys all of the above + image/video/GPS/CAV | — | — |

## The key tension

Minimal representations (queue count + waiting time) are obtainable from real sensors but lose information under sparse demand [[lu2025-rl-tsc-ac]] and cannot represent spatial propagation. Richer representations (STNet, DRIVERS reconstruction, temporal stacking) are more informative but either require simulation to provide clean inputs, or significant preprocessing infrastructure for real sensors.

The programmatic methods ([[gu2026-pi-elight]], [[liao2025-symlight]]) are notable for combining high performance with very simple features — three to eight scalars that any inductive loop can provide. Their expressiveness comes from the learned expression structure, not feature richness. *(synthesis)*

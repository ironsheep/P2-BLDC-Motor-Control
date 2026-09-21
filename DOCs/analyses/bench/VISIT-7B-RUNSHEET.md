# Visit 7b — run sheet (two unattended loads, one binary, two offset legs)

**Plan section:** R18.2c, *Sprint Revision — 2026-09-21: phasing is corrected BEFORE the drive is
designed* ([`../../plans/BENCH-READINESS-SPRINT-PLAN.md`](../../plans/BENCH-READINESS-SPRINT-PLAN.md)).

---

## Check the banner before reading anything else

A run that reports the wrong revision measured a different tree, and every number below is then
about something else.

| Load | Banner must read |
|---|---|
| both `dual-a` legs | `src_rev 23`, `fmt 11` |
| the **control** leg | `off_neg,43 off_pos,317` in every `BM-RUNG` |
| the **candidate** leg | `off_neg,14 off_pos,338` in every `BM-RUNG` |

If a leg's offsets do not read as its table row says, **stop** — the wrong binary is on the board,
and the A/B is meaningless before it starts.

---

## The visit, declared

Seven attributes, per *Shared vocabulary — the bench visit*
(`~/.claude/skills-docs/SKILLS-AUTHORING.md`).

| | |
|---|---|
| **Purpose** | **Diagnosis, not certification.** It answers one question: does correcting the commutation phase lower the current draw, and by how much. Its output is the corrected baseline R18.3 designs against, plus a number for what the remaining timing work is worth. **Nothing here certifies the driver** — that is Visit 8. |
| **Hardware risk** | Same kind as every `dual-a` run to date, and no more: wheels up, nothing on the platform, no hands anywhere near it, the full ladder to rung 11 in both directions. The one thing that is new is that **one leg runs commutation offsets the wheel has never run before**, so its current draw is not predictable from prior runs. That is the whole point of measuring it; the 10 A abort and the fold-back limiter are unchanged and both still apply. Panic throughout: physical battery disconnect. |
| **Who can observe** | **Nobody — every verdict is printed.** Both loads are unattended. If you happen to be near the rig, **one observation is worth having and it is the only one asked for: whether either leg sounds or feels different from the other** — smoother, rougher, more or less vibration at the same rung. That is an observation, not a verdict; no cell reads it. |
| **Runs that carry state** | **None across loads, and none within one.** Neither leg writes an offset at run time — the offsets are compiled in, which is exactly why this is two binaries rather than one run that rewrites them. Nothing needs restoring, and a load that stops early leaves nothing undone. |
| **Run length** | **About 12 minutes per leg, 25 minutes for both.** MEASURED 2026-09-20: part A ran 693 s end to end (PREFLT 6 s, STOPMODE 208 s, LIVE 28 s, LADDER 335 s, LOWSPD 117 s) against `RUN_TIME_CAP_S` 1_500. Both legs run the same loads, so the second should land within seconds of the first. |
| **Repeatability** | Both legs are repeatable and idempotent — a re-run costs only time. No fault is provoked; no power cycle is needed between them. **Run the control leg first**, so that if only one leg is run we hold the baseline rather than an unanchored candidate. |
| **Variant matrix** | One binary, two builds: `dual-a` at the shipped pair (no define) and `dual-a` with `-D HUB_OFFSETS_CANDIDATE`, on one rig (Rev B, paired 6.5in hub, 18.5 V, 270 MHz). Two logs. |

---

## The commands

```bash
tools/bench-run.sh dual-a         # leg 1 -- CONTROL,   offsets 43 / 317
tools/bench-run.sh dual-a-cand    # leg 2 -- CANDIDATE, offsets 14 / 338
```

Run the control leg first. Keep the two logs distinguishable — the banner's offsets tell them apart,
but so does the order.

---

## What this visit can decide that Visit 7 could not

Visit 7 ran **only** the uncorrected pair, so every number it produced describes a drive that is
about twice as expensive in one direction as the other. This visit runs the same ladder twice.

| # | Load | What it decides |
|---|---|---|
| 1 | `dual-a` control | The baseline, re-measured on today's tree with the wider instrument sample, so the comparison is against a run whose only difference from leg 2 is the offsets. |
| 2 | `dual-a` candidate | Whether the scanned pair lowers current draw, by how much, and whether the two directions converge. |

---

## Before the run: what is a cell, and what is not

⛔ **The A/B spans two binaries, so no cell can judge it.** A cell runs inside one image and sees one
leg; the comparison needs both logs. Inventing a cell that claims to judge the ratio would be a cell
that cannot see what it asserts. So the ratio is a **report judgement** against the decision table
below, and the cells judge what a single leg can decide on its own.

### The cells — each fails on a real defect

| Cell | PASSES when | FAILS when — and where that comes from |
|---|---|---|
| `R18-DUAL-OFFSETS-A` | every `BM-RUNG` in the leg reports the offset pair its build selects — 43/317 with no define, 14/338 with `-D HUB_OFFSETS_CANDIDATE` | the pair is the other leg's, or neither. **This is «#3586»'s owed run-time read-back.** The desk proved the constants compile to 43/317 and 14/338; nothing has yet proved the *driver* runs them. A build-time selection that silently failed to reach `offsetsForMotor()` fails here, and it is the one failure that would make every other number on the sheet a lie. |
| `R18-DUAL-INSTWIDE-A` | `BM-INST` reports `late 0`, `skipped 0`, `clamps 0` across the whole run at the widened sample | any of the three is non-zero. **This is «#3587»'s owed falsifier (D2).** The instrument went from 9 to 11 longs per sample; arithmetic says two more hub writes per motor at 500 Hz is nothing at 270 MHz, and arithmetic is not a measurement. An instrument that drops samples to afford its own width measures its own overhead. |
| `R18-DUAL-PHSEP-A` | the three phase readings differ from one another over a run, and are not all zero | they are equal, or all zero. **This is «#3587»'s other owed item.** A packing error that wrote one phase into all three slots, or left two unwritten, would pass every compile and produce a plausible-looking `ph_x10` — because `smpPh()` now derives the sum from the three. This is the cell that catches that. |

### The report judgement — and it can fail

The metric is **reverse-over-forward current at the same commanded rung**, netted of each board's
sense zero. Rungs 2–5 only: below rung 2 the current is small enough that noise dominates, and at
rung 6 forward reaches duty saturation and the window closes.

**MEASURED at Visit 7** (`src/logs/debug_260920-182503.log`), the control's expected shape:

| motor | rung 2 | rung 3 | rung 4 | rung 5 |
|---|---|---|---|---|
| LEFT | 1.93x | 2.02x | 2.04x | 1.97x |
| RIGHT | 1.88x | 1.91x | 1.93x | 1.87x |

The principles the board designer gave predict **1.0** at each direction's own minimum
([`../BLDC-COMMUTATION-PRINCIPLES.md`](../BLDC-COMMUTATION-PRINCIPLES.md)).

| Outcome | Reading | Decision |
|---|---|---|
| The candidate's ratio moves materially toward 1.0 **and** absolute current at rungs 3–5 falls | the offset model holds, and the depth below the default **is** the prize | apply the pair as the default; R18.3 designs against the corrected baseline, and the residual absolute current scopes correction 2 |
| The ratio moves but a **residual imbalance** remains at the candidate | offsets are not the whole story | **do not redesign yet** — «#3590» opens, and the remaining cause is named first: unequal hall sectors, sensor placement, or the one-sector shift between the direction tables |
| The ratio **barely moves** — within a few percent of the control | we were already near optimum, and the ~2x is elsewhere | correction 1 closes; «#3590» opens; correction 2 carries the whole driver case |

⛔ **This table is written before the run and is not renegotiated after seeing the numbers.** The
middle and bottom rows are real outcomes, not hedges — each sends the work somewhere different.

**The document's own warning, recorded so it is not discovered as a surprise:** *"The minimum is
broad. Torque per amp falls roughly as the sine of the lead angle, so ±15° from the optimum costs
only a few percent."* We run 22°–30° past both minima, which is outside that band — but if the
bottom row is what the bench returns, that warning is why, and it is not a failed run.

---

## The second question: per-direction speed ceilings — RAISED, NOT BUILT

The plan carries this leg, and I have **not** built it. The reason is a fact the existing ladder
already establishes, and it changes the hazard:

⭐ **Rungs 10 and 11 are ALREADY probe rungs above the nominal speed ceiling** (`BM-LADDER` marks
both `probe,TRUE`), and **Visit 7 ran both of them, in both directions, on both motors, without
either wheel faulting.** So the ceiling is not at rung 11 — it is somewhere above `ladder_max`
165_000_000, and the ladder as it stands never reaches it.

Extending past rung 11 therefore is not "one more rung of the same run." It is **driving the wheel
beyond any speed it has been asked for, deliberately, until the drive stops following** — and the
stop condition has to be built on R18.1's unbounded observables (duty demand and its deficit,
measured rate against commanded), because the fault-edge walk cannot fire now that the lag limiter
makes the motor droop instead of fault (PL-46).

That is a real increase in hazard, on hardware that is Stephen's, and it is his to accept or decline
rather than mine to fold into a precondition string. **So it is not on this sheet.** The A/B's
primary question does not need it, and Visit 7b is worth running without it.

If it is wanted, it is a separate load with its own risk line, and the natural home is Visit 8 —
where the drive has changed and the ceiling must be re-measured anyway (PL-26, PL-38).

## What is deliberately NOT on this sheet

Each of these reads differently once phasing is corrected, so measuring it now buys a number we
would have to discard:

- the missing 2-rung and 4-rung speed-**down** delta cells — they belong to Visit 8
- the rung-6 current collapse — its cause is a desk question against the principles and p2kb first
- the low-speed duty floor of ~1_600 counts — a source question before it is a bench one

And one thing is off the sheet for a different reason: **any attended tier**. All PLOT panel work is
benched (Stephen, 2026-09-21), so both loads here are unattended by construction.

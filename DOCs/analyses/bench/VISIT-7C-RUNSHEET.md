# Visit 7c — run sheet (three loads, two binaries, nothing attended)

**Plan section:** R18.2f ([`../../plans/BENCH-READINESS-SPRINT-PLAN.md`](../../plans/BENCH-READINESS-SPRINT-PLAN.md)).
**Task:** «#3594».

---

## Check the banner before reading anything else

A run that reports the wrong revision measured a different tree, and every number below is then
about something else.

| Load | Banner must read |
|---|---|
| `scan-droop` | `src_rev 18`, `fmt 11`, **`droop_selftest TRUE`** in `BS-BUILD` |
| `scan` | `src_rev 18`, `fmt 11`, **`droop_selftest FALSE`** and `wd_selftest FALSE` |
| `dual-a` | `src_rev 23`, `fmt 11`, and `off_neg,14 off_pos,338` in every `BM-RUNG` |

⛔ `src_rev 17` on either scan load means the loop inversion and the follow cell are **not** in the
image, and loads 1 and 2 certify nothing. Stop and rebuild.

---

## The visit, declared

Seven attributes, per *Shared vocabulary — the bench visit* (`~/.claude/skills-docs/SKILLS-AUTHORING.md`).

| | |
|---|---|
| **Purpose** | **Two jobs, as every pass must have.** It **certifies** what was built since the last pass — the driver's own following reading (harvested at `31c8b91`, never yet judged), the droop stop (never yet fired), and the inverted scan loop — and it **measures** toward the one question still open: `L` at a half, the single gate on the speed law that R18.3 needs. |
| **Hardware risk** | **Load 1 carries none — nothing moves.** `scan-droop` runs no preflight, starts no driver cog and commands no wheel; motors may stay connected or not, it makes no difference. Loads 2 and 3 are the same kind of risk as every prior `scan` and `dual-a`: wheels up, nothing on the platform, no hands near it. The 10 A abort and the fold-back limiter are unchanged and still apply to both. Panic throughout: physical battery disconnect. |
| **Who can observe** | **Nobody — every verdict is printed.** All three loads are unattended. The ALIGN tier, which *would* have asked for your hands, is **not in this pass** (see below). |
| **Runs that carry state** | **None across loads, and none within one.** No load writes an offset at run time. Nothing needs restoring, and a load that stops early leaves nothing undone. |
| **Run length** | **About 25 minutes total.** Load 1 is **seconds**. Load 2 is up to ~15 min (MEASURED: the last complete scan ran 905 s; the two aborted ones died at 401 s). Load 3 is ~12 min (MEASURED 2026-09-20: part A ran 693 s against `RUN_TIME_CAP_S` 1_500). |
| **Repeatability** | All three are repeatable and idempotent; a re-run costs only time. No fault is provoked and no power cycle is needed between them. **Run load 1 first** — it is free, and it certifies the stop condition that load 2's sweep depends on. |
| **Variant matrix** | Two source files, three builds: `test_bench_scan.spin2` with `-D DROOP_SELFTEST` and without, and `test_bench_dual.spin2` part A. One rig (Rev B, paired 6.5 in hub, 18.5 V, 270 MHz). Three logs. |

---

## The commands

```bash
tools/bench-run.sh scan-droop     # load 1 -- seconds, NOTHING MOVES
tools/bench-run.sh scan           # load 2 -- the rebuilt sweep, both motors, three rungs
tools/bench-run.sh dual-a         # load 3 -- carries the START trace
```

In that order. Load 1 is free and gates the reading of load 2.

---

## ⛔ What changed since the task body was written

The task body for «#3594» lists the **cold hall-zero ALIGN tier** as load (1), attended, with your
hands on the wheels for 8 legs. **It is not in this pass**, and this sheet is the authority.

Two defects in the ALIGN instrument put it on `DOCs/PUNCH-LIST.md` instead —
[**PL-99**](../../PUNCH-LIST.md): its crossing detector has **no hysteresis**, so noise around the
crossing produces ~5.5× too many edges and overflows the buffer; and [**PL-100**](../../PUNCH-LIST.md):
its clip criterion judges **peak** railing when `Z` is derived from **where the waveform crosses
zero**, so it fails good traces and passes bad ones. Running it would produce a number nobody could
defend.

`Z` is not blocked by that. It is held at **−3.6 ± 0.4°** from four scan self-locations and is
speed-invariant within its own spread. The ALIGN tier would settle it *absolutely and cold*; that is
worth having and is not worth an attended visit with a broken detector.

**So this visit asks nothing of your hands.** That is a change from what the task body promised, and
it is stated here rather than discovered at the rig.

---

## The three loads, and what each decides

| # | Load | What it decides | Feeds |
|---|---|---|---|
| 1 | `scan-droop` | Whether the **droop stop** raises `WS_DROOP` at exactly the right point, never on the isolated shape every real run has produced, and never across a fault. Pure logic. | load 2's stop condition |
| 2 | `scan` | `L` at an eighth, a quarter and a **half** — the half being the one gate on the speed law. Plus: does the driver's own following reading agree with the harness while following, and **collapse** at the wall. | «#3589» |
| 3 | `dual-a` | The **start-transient mechanism**, from four START traces on the QTR cells, both motors, both directions. | «#3589» |

---

## Before the run: the cells, and that each can fail

### Load 1 — `R18-SCAN-DROOPLOGIC`, three instances, motor `NONE`

The stop being certified **has never executed**. MEASURED over the four runs in
[`2026-09-22/`](2026-09-22/): droop points *do* occur — 4 to 5 per run below `FOLLOW_DROOP_PCT` — but
**every one is the first point of a walk side**, at swept ±63 with result `ABORT_I`, after which the
walk steps inward and recovers. So `droopConsec` reaches 1 and resets, never 2, and `WS_DROOP` has
never been raised.

`stepStopDecision()` was extracted as a **pure total function** so this is answerable at a desk
rather than by gambling a sweep on it.

| crit | Sequence fed | Must read | Fails if |
|---|---|---|---|
| `DROOP_RUN_FIRES` | droop, droop, droop | `WS_DROOP` at point **2** (`SIDE_DROOP_STOP`) | it fires at 1 (stops a healthy sweep) or 3 (walks too far) or not at all |
| `DROOP_ISOLATED_NO` | droop, clean, droop, clean, droop | **no stop** | it fires — which would have stopped all four real runs early |
| `DROOP_FAULT_RESETS` | droop, fault, droop | **no stop** | a fault fails to reset the droop run, so the two stops bleed into each other |

**Hand-traced at the desk before the run** (the binary's job is to prove the compiled code agrees):
RUN fires at 2; ISOLATED never fires; FAULT never fires. Each cell discriminates — flipping
`SIDE_DROOP_STOP`, or dropping the fault-reset, changes a verdict.

`BS-DROOPTEST` carries `stop_at`, `stop`, `expect_at` and `pass` for each, so a FAIL says **where** it
fired, not merely that it did.

### Load 2 — `R18-SCAN-FOLLOW`, two instances per motor

Certifies `testGetFollowing()`, the driver capability harvested at `31c8b91` and **never judged**.
It is a genuine cross-check, not a restatement: the harness computes `follow_pct` from the point's
whole drive span against a compile-time rung table; the driver computes `nPctOfCmd` from its own 1 s
rpm window against a rate it derives from the live command. Different numerators, different
denominators, different time bases.

| crit | Measured | Limit | Fails if | NOMEAS when |
|---|---|---|---|---|
| `FOLLOW_AGREES_PCT` | worst \|driver − harness\| among **following** points | ≤ 20 | the driver's derivation is off — a wrong denominator misses by a *factor*, not by points | fewer than 4 following points |
| `FOLLOW_COLLAPSED` | the driver's **lowest** reading among **not-following** points | ≤ 60 | the driver's number stays high while the drive has plainly given up | **no point drooped** |

⚠ **`FOLLOW_COLLAPSED` is NOMEAS, never PASS, when nothing drooped.** A run in which the drive
followed throughout shows the reading sitting near 100 and nothing else; it does *not* show the number
can fall, which is the only property that makes it useful. On the measured evidence above this limb
**should** get its points — 4 to 5 per run land below 60 — but "it did not arise" stays an honest
result and is not evidence.

The limits are measured, not chosen: `testGetFollowing()`'s own record has the bench instrument
reading **44–47 %** of commanded at the current wall while duty saturated, against ~100 while
following. 60 sits clear of both.

### Load 2 — the inverted loop, judged from `BS-END`

| Field | Reading | Means |
|---|---|---|
| `left_rungs` / `right_rungs` | vs `rungs_planned` 3 | how far **each motor** got |
| `left_done` / `right_done` | both FALSE on any abort | **do not read these on an aborted run** — they hide the progress the inversion buys |

⛔ **The falsifier for the inversion itself:** if the run aborts and one motor shows **0 rungs**, the
inversion did not take. Under rung-outer an abort costs at most the rung it lands in. MEASURED
premise, from [`2026-09-22/debug_260921-200935.log`](2026-09-22/debug_260921-200935.log): that run
emitted **5 `BS-LEG` for LEFT and zero for RIGHT** — it died in LEFT's half rung and RIGHT was never
touched. The same abort should now leave both motors complete at LOW and at QTR.

### Load 3 — the START trace

Four traces, first repetition of the QTR cells only, both motors, both directions. QTR because it is
the speed Visit 7b's from-rest aggregates were taken at, so the trace is checkable against
`tr_i_pk` 90 / 120 rather than merely plausible.

⭐ **The falsifier is stated in advance and is specific.** If the surge is the servo's 60° deadband,
then **duty stays pinned at `duty_min_` while `|err|` climbs, and the current surge begins only as
`|err|` crosses 60°**. *If duty moves before that crossing, the deadband story is wrong.*

---

## What this pass does NOT decide

Stated so the report cannot quietly claim it.

- **The servo setpoint A/B** (`256/6` against `256/4`, each at its own compensating lead) is **not in
  this pass**. It needs a compensating lead designed per leg, and that design is «#3589»'s.
- **`Z` absolutely and cold** — the ALIGN tier, above.
- **Whether the motor can physically droop for two adjacent offsets.** Load 1 certifies the *stop*,
  not the *physics*. If load 2's sweep still never raises `WS_DROOP`, that is a fact about the motor
  and the arc, not a failure of the stop.

---

## The honest possibility, stated before the run

**The half rung may be unmeasurable on this rig.** If its optimum sits where spin-up current must
exceed 10 A at 18.5 V, the abort fires before the point is measured, and four attempts have now
failed for four distinct causes.

That would be **a finding about the motor**, not an instrument failure — and the guard fixes landed at
`caf1c88` / `6b72ad0` (fast ceiling guard, walk DOWN first, abort cap 6 → 16) are precisely what let
the report tell those two apart. If it fails a fifth time, the report says so plainly and «#3589»
designs against an eighth and a quarter with the speed law stated as **extrapolated, not measured**.

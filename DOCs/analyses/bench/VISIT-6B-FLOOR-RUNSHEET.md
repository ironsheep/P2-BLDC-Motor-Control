# The floor run — run sheet (the last bench visit before 6.0)

**Task:** «#3576» runs it; «#3591» built it, SRC_REV 58 added the load cells, and SRC_REV 60 re-checked every cell
against DRIVER_REV 38's jerk-limited ramp and DRIVER_REV 39's stop plan. SRC_REV 61 (DRIVER_REV 46) changed nothing in
part SPIN: the driver's later revisions (40's walk, guard and current fixes; 41–45's proved-equivalent memory
reduction; 46's ramp-API removal) move no floor cell's bound: 40's unbiased current was checked against every
current bound (test_bench_dual's SRC_REV 60 note), and the walk guard and band are read from the library. It runs after the release-candidate pass. **Tier:** `dual-spin` (part
`DUAL_PART_SPIN`, one binary). **Burn-down:** `DOCs/PUNCH-LIST.md`, "Release burn-down".

**Why this visit exists:** the floor run keeps only the claims that need a load (Stephen, 2026-09-26). It is the last
bench visit before 6.0, so it has to decide every load-dependent release item in one visit:

| Closes | What it proves | Segment |
|---|---|---|
| PL-106 | the protective stop latches on a really blocked wheel, as `SR_BLOCKED`, within its ~1 s | BLOCK |
| PL-111 (precondition) | a latched protective stop is cleared through the API: `clearProtectiveStop()`, not `clearEmergency()`. The serial half (`protclear`) is certified separately. | BLOCK |
| PL-132 | the blocked-wheel stop coasts under `holdAtStop(FALSE)` (its control: it shorts under `TRUE`) | BLOCK |
| PL-150 | under a real one-sided load both wheels slow together and the platform keeps its line; the overloaded wheel holds the speed it can sustain, without faulting | LOAD |
| PL-93 | after a fault and its recovery, the next drive draws no extra current | SPIN (the re-drives) |
| PL-95 | the drive never reports AT_SPEED while its field is held | BLOCK and LOAD |
| PL-160 (the feel, under load) | the jerk-limited ramp eases every start, stop and speed change in and out under a real load: R19-DUAL-SPINSTRT-P and -SPINPEAK-P judge the quarter's START, and **you record what you feel** (below) | SPIN, and every segment that drives |

It also carries the floor run's own claims, unchanged since «#3591»: the commutation offsets under load, R18.3's loaded
expectations, X-5 on the floor (PL-117), and the hold on an incline, which sizes `HOLD_CEILING_PCT`.

The release-candidate pass (2026-09-27) adds two claims here: **PL-144**, the path limiter under load (LDPATH;
PATH-HUNT's precondition never arises wheels up), and the hold's own question, **HOLDSET / NOTFOL** (pass 7's wheels-up
PASS were an artifact of the PL-146 defect, so LDHOLD and HELDATSPD are now the hold's only evidence; PL-150's note).

**The demos ran at the release-candidate pass (PL-149 certified).** The 27 A derate cannot be reached on this rig.

---

## Block A — wheels up, BEFORE the platform goes on the floor (added after the release-candidate pass)

The release-candidate pass left three wheels-up items. They run first, on the same pull, while the wheels are still up.
`git log --oneline -1 -- src/` must show the commit carrying **test_bench_t0 SRC_REV 28** (harness only; DRIVER_REV 46).

| Order | Command | Why | Minutes |
|---|---|---|---|
| A1 | `tools/bench-run.sh t0-stopreason` | re-certifies RAMP-SHAPE, RAMP-UNWIND, RAMP-REVERSE, SR-ATLIMIT and EV-STOP after the three harness fixes (RC evaluation F1–F3); banner `src_rev 28` | 2 |
| A2 | `tools/bench-run.sh dual-pack` | **only if** the Powerpole was not unplugged at the RC pass's prompt (RC F7). Unplug and replug AT THE PACK when told, twice | 3 |
| A3 | the serial step | **only if** it did not run at the RC pass: `VISIT-10-RUNSHEET.md` step 12, unchanged | 2 + wiring |
| A4 | `tools/bench-run.sh t0-reva` | optional, your call (PL-163): the Rev A block in `VISIT-10-RUNSHEET.md` | 1 + swaps |

What A1 decides (criteria in source, unchanged except as the SRC_REV 28 note says): R22-T0-RAMP-SHAPE, -REVERSE and
-UNWIND PASS; R20-T0-SR-ATLIMIT reads SR_COMMANDED on its negative (`T0-25,leg,ATLIMIT_NEG,...,sr_stop,41`); R20-T0-EV-STOP
reads `41 42 41 47 41 46 41`. Everything else in the tier as at the RC pass.

Then battery off, the platform on the floor, and the floor run below.

---

## ⛔ First: push, then pull at the bench

`git log --oneline -1 -- src/` at the bench must show the commit that carries **test_bench_dual SRC_REV 61** and the
release-candidate driver, **DRIVER_REV 46** (or later, if the release-candidate pass leads to a fix).

## Check the banner before reading anything else

| Every `dual-*` log must read |
|---|
| `BM-BANNER,...,src_rev,61,fmt,38,part,SPIN` |
| `BM-BUILD ... drv_rev,46`: the driver under test. A lower number means an old tree. |
| `BM-BLKBUILD`, `BM-LDBUILD` and `BM-RDBUILD` present: the load cells' numbers were pre-registered |
| `BM-SPINLEG` for legs 7–10 (the quarter, BRISK) reads `win_ms,300` (SRC_REV 60; it was 500) |

---

## Before the run: he measures, gathers and writes down

| What | Value | Why |
|---|---|---|
| Incline angle, measured on the ramp surface | ____ ° (suggest near 5°) | the creep cells judge a hold against this slope |
| Platform mass | ____ kg | with the angle, the holding torque per wheel = m·g·sinθ·0.08255 m / 2 |
| Tether routing | from above the centre, or ≥ 3 m free | one full turn must not pull it, and LOAD drives up to 2 m down a lane |
| Two chocks | wedges (door stops work) or blocks, ≥ 4 cm tall | BLOCK: one hard against the front of the LEFT tyre, one against the back |
| A strap | about 1 m, tied to the frame beside the LEFT wheel | LOAD: his pull on it is the load |
| A straight lane | ≥ 3 m, clear, hard floor | LOAD drives straight ahead, at most 2 m |

"LEFT" is the platform's left, the P32 board, as seen standing behind it facing forward.

## The visit, declared

| | |
|---|---|
| **Purpose** | **Certification** of the load claims above, on the release-candidate driver (DRIVER_REV 46), plus the floor run's measurements: loaded current by direction and pair, and the hold's duty and current on the incline. |
| **Hardware risk** | **The highest this project has: wheels down, a person present.** SPIN turns the platform in place at up to about half a turn a second, at most one turn per leg; legs 11 and 12 fault one wheel on purpose. BLOCK drives only the chocked LEFT wheel, current-limited to 2 A (about 14 N at the tyre); if it turns 17 mm the harness stops it. LOAD drives the platform straight at a slow walk, current-limited to 4 A, at most 2 m, with an e-stop 35 mm past that; you walk behind it. On the incline the platform can roll up to about 17 mm (coast) or 35 mm (hold trials) before the harness brakes it. The 10 A abort and the fold-back limiter apply throughout. **Every start and stop now ramps smoothly and takes longer than at the last floor run: a stop from the quarter takes about 0.6 s and 31 ticks (18 cm of tyre), not 19.** **Stand outside the swept circle while it spins. Panic: disconnect the battery.** |
| **Who observes / acts** | Stephen, on every screen: each says what is happening, the one next click, and what he should see. He chocks the wheel (BLOCK), pulls the strap (LOAD), handles the platform on the incline (CREEP), and records the ramp's feel (PL-160). |
| **Runs that carry state** | None. Every pair of legs, every BLOCK and LOAD trial and every creep trial runs in its own steering lifetime; a written offset pair is restored and read back (`BM-OFFREST`); the lowered current limits are restored before each lifetime stops. |
| **Run length** | About **14 minutes of run**: SPIN about 5.5 (12 legs and 2 re-drives), BLOCK about 1.5, LOAD about 4 (a free trial and 1 to 3 drag trials), CREEP about 2.5. The S-curve changes a leg's time by well under a second (a leg at SLOW still takes about 8.2 s). About **40 minutes at the rig** with the setups. Cap 30 minutes of run. About 35 clicks. |
| **Repeatability** | Repeatable. Each segment's first screen has SKIP: to rerun only BLOCK, LOAD or the incline, SKIP leg 1 and each segment before the one you want. |
| **Variant matrix** | One binary, `-D BENCH_QUIET -D DUAL_PART_SPIN`, on the Visit 10 rig: Rev B, 6.5in hubs, 18.5 V pack, 270 MHz, DRIVER_REV 46, built-in ramp rates (1,000 / 1,470 mm/s²). DEBUG footprint 7,531 bytes (limit 12,404). |

## The commands — two, in this order

```bash
tools/bench-run.sh dual-ui      # 1: re-certify the shared panel screens (dual-brake's art is unchanged, but check it)
tools/bench-run.sh dual-spin    # 2: the floor run: SPIN, BLOCK, LOAD, CREEP
```

`dual-ui` previews only the `dual-brake` screens. The new screens were appended after them, and a byte check showed
every existing prompt, state and label cell unchanged. `ATTENDED-PANEL-SCREENS.md` lists every screen's wording.

---

## What he does, and when

| When the panel shows | He does |
|---|---|
| SPIN legs 1–12 (READY) | stands outside the circle, tether slack, clicks START |
| **after legs 11 and 12: "FAULT CLEARED. NEXT: THE SAME SLOW SPIN AGAIN"** | clicks START: the same slow spin, stopped by itself before the turn is up. SKIP skips only this re-drive. |
| **BLOCKED-WHEEL TEST** | leaves the platform where it is. **Chocks the LEFT wheel front and back**, hard against the tyre. Hands clear, then clicks START. Two short trials follow: in each the left wheel pushes the chock and should stop itself within 4 s (about 1.3 s is expected). Nothing else to click. |
| **LOADED-DRIVE TEST** | **removes both chocks**, aims the platform's front down the lane, tethers it slack along the lane, **ties the strap to the frame beside the LEFT wheel**, and stands behind holding its end slack. Clicks START. |
| LOAD READY, "NEXT: KEEP THE STRAP SLACK" | the free trial: clicks START and walks behind, strap slack |
| LOAD READY, "NEXT: YOU PULL WHEN TOLD" | clicks START and walks behind, strap slack |
| **PULL** | **pulls back on the strap, firmly and steadily, while walking, until the number (its speed, % of command) reads about 50**. Never to 0: a platform that stops for a second latches the protective stop, and the trial is not judged. Keeps pulling until LET GO. |
| LET GO | lets the strap go slack; the platform stops itself (about half a second of ramp) |
| BACK | pushes the platform back to the start of the lane (its wheels roll freely), clicks DONE. **After the last trial, unties the strap first.** |
| LOAD READY, "LAST TOO LIGHT: PULL HARDER" or "LAST STALLED: PULL LESS" | adjusts his pull, clicks START. There are up to three drag trials; the first judged one ends LOAD. |
| NOW THE INCLINE | carries the platform onto the ramp, wheels rolling straight down the slope, holds it, clicks START; then DONE when he lets go, DONE when he holds it again |

### ⭐ PL-160: feel the new ramp, and write it down

PL-160's feel is a floor item: no cell can judge it. **During SPIN and LOAD, watch and listen at every start and every
stop, and after the run write one line on the sheet:** "PL-160 feel: ____".

- **What to expect.** Every start eases in and every stop eases out over about a quarter of a second. Nothing should
  jolt, lurch, clunk or rock the platform at a start or a stop, or at LOAD's slow-down when you pull and speed-up when
  you let go.
- **The times, derived for the built-in rates:**

  | Speed | Start | Stop |
  |---|---|---|
  | SLOW (power 7) | 0.39 s, 5 ticks | 0.33 s, 4 ticks |
  | MEDIUM and LOAD (power 13) | 0.56 s, 15 ticks | 0.46 s, 12 ticks |
  | the quarter (power 23) | 0.82 s, 40 ticks | 0.64 s, 31 ticks |

- **The difference from the last floor run.** Stops are about a quarter second longer and run further than they did.
  A quarter-speed stop covers 31 ticks (18 cm of tyre), where it covered 19.
- **What counts against it.** A step you can feel at either end of a ramp is PL-160's negative. So is the platform
  pitching at a stop, or a stop that stops dead.

---

## SPIN: the legs

Odd legs spin right (clockwise from above), even legs spin left.

| Legs | Pair | Speed (power) | Pair each driver must apply | Steady window |
|---|---|---|---|---|
| 1–2 | the shipped lead schedule | SLOW (7) | 17 / 336 | 2,000 ms |
| 3–4 | schedule | MEDIUM (13) | 15 / 337 | 1,000 ms |
| 5–6 | **legacy 43/317, the control** | MEDIUM | 43 / 317 | 1,000 ms |
| 7–8 | schedule, traced | BRISK (23), the quarter | 1 / 351 | **300 ms** (was 500) |
| 9–10 | fixed 14/338 | BRISK | 14 / 338 | **300 ms** (was 500) |
| 11–12 | schedule, **one wheel faulted, then the re-drive** | SLOW | 17 / 336 | — |

The travel limit is one revolution of the platform: π × 387 mm = 1,216 mm, 211 hall ticks. Each leg's limit is armed
before it moves, and the harness e-stops 6 ticks past it. A re-drive's limit is whatever is left of its leg's turn
(`BM-RDRIVE remain`), so the tether still winds at most one turn.

## What DRIVER_REV 38 and 39 moved, re-derived (SRC_REV 60)

Every number below comes from a pass-by-pass model of the driver's `jerkStep`. It uses the bench wheel's built-in rates:
speed-up 33,958 per pass with jerk 71, slow-down 49,918 with jerk 104, 522.7 µs a pass, 6 ticks per 2³² of field
angle. The model reproduces the harnesses' own figures at power 50: a 2,885-pass speed-up (test_bench_t0), and a
2,117-pass stop (test_bench_dual's 2,118 counts the take pass). Each derivation is stated in
`src/test_bench_dual.spin2` at its constant.

| What | DRIVER_REV 37 | DRIVER_REV 38/39 | Verdict |
|---|---|---|---|
| **The quarter's leg budget** (spinWinMs) | 31-tick spin-up, 98 of settle, 49 of window, 19-tick stop: 14 ticks inside 211 | 40.1-tick spin-up and 31.2-tick stop, so the limit fires at about 178.8. A 500 ms window would end at 187.4, about 90 ms after the ramp-down began, and would read A-8, the path scale and the pair on the ramp-down | **MOVED: 500 → 300 ms.** The window now ends at 167.8, 11 ticks (about 110 ms) before the fire, still over SPIN_WIN_MIN_MS 250. SLOW (91 of 211) and MEDIUM (135) are unchanged |
| **SPINSTOP**, rest against the limit | ±2 | DRIVER_REV 39's plan over-states the stop by its age and its take-pass case, so a stop can rest up to one tick short (STOP_PLAN_EARLY_TICKS) | **±3** (SRC_REV 59, SPIN_STOP_TOL_TICKS = STOP_LIMIT_HI). The 6-tick guard is unchanged |
| **The re-drive's room** (RD_MIN_TICKS 80) | ~15 up, ~27 of window, ~10 of stop | at SLOW, 5.3 up, 27.0 of window, 4.4 of stop and the plan's early tick: about 38 | kept, with twice the margin |
| **BLOCK's latch window** (1 … 4 s) | "the held field's count starts ~1–2 s after the command" | The chocked rotor stands, so the lag is the field's own travel. It reaches LAG_SOFT after 437–524 passes of the S-curve to power 13 (0.23–0.27 s). The latch then comes BLOCKED_PASSES later: **about 1.3 s** | kept. The 1 s floor holds by construction |
| **LOAD's travel** (2 m, 347 ticks) | — | 15.0 up, 53.7 settle, at most 214.8 over PULL's 4 s, and a 12.3-tick stop (it was about 5.6) come to at most 296. The limit would fire at about 334 | kept, with 50 ticks spare. The distance stop never ends a normal trial |
| **LDPATH**, the path limiter's line (≤ 100 ‰) | — | The undragged wheel now follows a scale change along the S-curve: 2√(Δv/J), about 0.2 s for a 20 % change, where the stepped ramp took about 0.04 s. A follower delayed by *d* mismatches the window by *d* × (the dragged wheel's speed at the window's end − at its start). Under the steady pull asked for, a 5 ticks/s change across the window adds about a tick, against a band of about 7 ticks (100 ‰ of ~67 ticks at half speed for 2.5 s) | kept. The negative is unchanged: with no limiter the mismatch is at least 200 ‰ by construction |
| **X-5 / SPINPLAT** (the partner at ≤ 10 % after D_REST_MS, 2 s) | ~0.1 s stop at SLOW | 0.33 s at SLOW | kept |
| **POSTFLT, HELDATSPD, LDHOLD, CREEP** | — | POSTFLT compares two windows of the same ramp. `holdDecay` still turns AT_SPEED to SPIN_UP on a held pass. The hold and the incline drive no ramp | unchanged |

**Re-cut by construction: A-1 and A-2, the START cells (PL-160's feel under load).** The ramp change broke both
instruments, so both windows were re-derived. Neither bound moved. The derivation is in the SPIN part's CON, at
`A1_RAMPOUT_SAMPLES` and `A2_REF_DELAY_MS`.

- **Where the bounds come from.** Both are the servo model's (`DOCs/plans/servo-model`, DRIVE-INTEGRATION-DESIGN.md
  §5.5).
  - The model's ramp is the stepped one. Its acceleration rises every pass until arrival: 40,220 a pass at 36.75 × 10⁶,
    after 920 ms.
  - `start_metrics.py` judges a 1.4 s trace. A-1 is judged over the rise. A-2's reference is "the trace's last 60 ms",
    which lie 418–478 ms after the model's arrival, at constant speed.
- **A-2** (SPINPEAK, ≤ 1.80): the START's current peak ÷ the mean current of **60 ms of steady running**.
  - The reference is 31 samples (60 ms) starting 420 ms after the first AT_SPEED sample. That is where the model
    placed its own, to the 2 ms sample, and more than RAMP_TAU_MS past the ramp.
  - It counts only when every sample from the first AT_SPEED to the reference's end reads DCS_AT_SPEED. That is the
    driver's own report that its acceleration is 0. `jerkStep` writes AT_SPEED only on the arrival pass and on every
    later pass at the target, where it zeroes `drv_accel_now` in the same step. A held pass turns it to SPIN_UP, and
    a stop turns it to SPIN_DN.
  - Until SRC_REV 60 the reference was the 60 ms before the first AT_SPEED. Under the S-curve that is the ramp-out,
    still carrying up to 24 % of the speed-up acceleration, so a correct start could fail.
  - **The bound stays 1.80.** Its derivation was against steady running. The S-curve only lowers the peak's
    acceleration term: its limit, 33,958 a pass, is under the model's 40,220, and it eases in from 0.
  - **Negative:** the shipped servo's start spike, 1.94–3.04 (measured, design §5.5).
- **A-1** (SPINSTRT, ≤ 0.10): duty's largest fall from its running maximum over the **rise** only.
  - The window runs from duty leaving its floor to 126 samples before the first AT_SPEED: RAMP_TAU_MS, plus one
    sample.
  - The S-curve removes the acceleration over exactly RAMP_TAU_MS before arrival. There the torque demand falls by
    design, and duty may fall with nothing hunting. The model's acceleration never fell.
  - **The bound stays 0.10** (model 0.01–0.04 over a rise).
  - **Negative:** the shipped servo's hunting during the rise, 0.34–0.53 (measured, design §5.5).
- **Criterion tokens change with their meaning:** `RISE_DUTY_DROP_PM` (was `START_DUTY_DROP_PM`) and
  `START_I_OVER_STEADY_X100` (was `START_I_RATIO_X100`). The cell ids are unchanged. `BM-SPINSTART`'s `tail_x10` and
  `tail_n` are now the steady reference's.

## What each cell decides, and how each can fail

Every criterion is fixed in `src/test_bench_dual.spin2` before the run (the load cells' section is "the floor run's
load cells"). Each claim that needs a control has one, and its PASS counts only when the control's did. Each cell
prints NOMEAS when its precondition did not arise, and its record's `why` says which.

### The load cells (SRC_REV 58; timing re-derived at SRC_REV 60)

| Cell | Criterion | Fails if (the negative) | NOMEAS when |
|---|---|---|---|
| **R21-DUAL-POSTFLT-P** (per motor, PL-93) | after the fault and its recovery, the same spin's getCurrent() over its first second at speed ÷ the leg's own over the same second before the fault ≤ **1.50** | above; an absolute-current abort scores 99.99. **Negative, measured:** Visit 6a drew 3.8–4.2× and hit the 10 A abort on the drive-up (PL-93) | the fault did not latch, the recovery did not clear, too little turn left (under 80 ticks; about 38 are needed), he skipped it, or the "before" is under 0.05 A |
| **R21-DUAL-BLKSTOP-P** (LEFT, PL-106) | every trial whose wheel stayed blocked: both codes `ERR_PLATFORM_BLOCKED` within 4 s but not before 1 s (about 1.3 s expected), and the left reads `SR_BLOCKED` | a trial not latched in 4 s (a driver without the stop leaves a stalled wheel commanded: Visit 6a's wheel sat at duty_max reporting AT_SPEED), a latch before 1 s (a false fire, PL-116's class), or another stop reason | the chock did not hold (the wheel turned 3 ticks: `why NOT_BLOCKED`, and BLOCK ends) |
| **R21-DUAL-PROTCLR-P** (PL-111's precondition) | every latched trial: a drive is refused with `ERR_PLATFORM_BLOCKED`; `clearEmergency()` leaves it latched; `clearProtectiveStop()` returns NO_ERROR and both codes read NO_ERROR; the next drive is taken | any step otherwise. The in-run negative is the refused drive: the same call the last step makes, before the clear. `clearEmergency()` was the serial host's only release before the fix (`emerclear`), and it must not release | no trial latched |
| **R21-DUAL-BLKSHORT-P** (LEFT, the control) | the BRAKE trial's phase sum at rest after the stop **< 80 mV**: a short | at or above: the instrument cannot see a short on this wheel, and BLKCOAST's PASS does not count | the BRAKE trial did not latch |
| **R21-DUAL-BLKCOAST-P** (LEFT, PL-132) | the COAST trial's phase sum at rest after the stop **≥ 80 mV**: a coast | under 80: shorted. **Negative, measured:** before DRIVER_REV 20 the stop shorted under coast; a short at rest reads 11–25 mV and a coast 160–174 mV (`debug_260923-192848.log`, LEFT, X-2 against X-3) | the COAST trial did not latch |
| **R21-DUAL-HELDATSPD-P** (LEFT, PL-95) | over every BLOCK drive and every LOAD window, **no two samples in a row read AT_SPEED at \|err\| ≥ LAG_HOLD** | any such pair. **Negative, measured:** PL-93's trace read AT_SPEED at e −101 and duty_max for eight samples running | no sample was ever held (\|err\| ≥ LAG_SOFT) |
| **R21-DUAL-LDPATH-P** (PL-150, the path limiter) | in the judged drag window, \|left − right\| hall ticks ÷ the larger **≤ 100 thousandths**: both slowed together, the line kept | above. **Negative, by construction:** without the limiter the undragged wheel keeps its whole command while the judged window has the dragged one under 80 %: a mismatch of at least 200 thousandths | no drag trial was judged, or the window's travel was under 20 ticks |
| **R21-DUAL-LDHOLD-P** (LEFT, PL-150, the overload hold) | in the judged drag window, the dragged wheel's longest gap between hall ticks **≤ 1,000 ms**, and no fault | a fault (a driver with no lag limiter faults FC_LAG at \|err\| 125), or a longer gap with no protective stop (a hold whose field decayed to zero and stood still) | no drag trial was judged |

**When a drag trial is judged:** the left wheel read SHORT (its lag limiter held) in the window, *and* ran under
**80 %** of its command's predicted rate, *and* no protective stop latched. It is also judged if a wheel faulted.
Otherwise it was too light (`NOT_OVERLOADED`: the next READY asks for a harder pull) or it stalled (`STALLED`: the
next asks for a lighter one).

**Recorded, not judged:** `BM-LOAD`/`BM-LOADW` for every trial, the free trial included: each wheel's travel and %
of command, the mismatch, the least path scale, the SHORT polls and the path limiter's engages. `BM-BLOCK`/`BM-BLKCLR`
record the latch time, both codes and stop reasons, every API return, and both wheels' phase sums. Each BLOCK trial
and each drag trial is traced.

### The spin and incline cells

| Cell | Criterion | Fails if | Control |
|---|---|---|---|
| **R19-DUAL-SPINSTOP-P** | every leg ends within **±3 ticks** of the limit (±2 before DRIVER_REV 39: the plan may rest one tick short) | an overshoot, an undershoot, or the guard fires | — |
| **R19-DUAL-SPINOFF-P** | every driver applied the table's pair | a write that did not land | — |
| **R19-DUAL-SPINDIR-P** | no wheel ran against its commanded direction | any did | — |
| **R19-DUAL-SPINHUNT-P** (A-3) | slow and medium schedule legs: no window with duty_pk − duty > 400 or err_pk > 76 | any such window | the shipped servo read 800–1,650 / 75–89 wheels up |
| **R19-DUAL-SPINERR-P** (A-4) | \|mean err\| within 47–49 in every schedule window | outside | — |
| **R19-DUAL-SPINSTRT-P** (A-1, PL-160's feel) | worst duty drop over the START's rise (duty leaving its floor, to RAMP_TAU_MS + one sample before the first AT_SPEED) ≤ 100 per mille | above: the shipped servo's hunting read 340–530 | — |
| **R19-DUAL-SPINPEAK-P** (A-2, PL-160's feel) | worst START current peak ÷ 60 ms of steady running, 420 ms after the first AT_SPEED, every sample to its end AT_SPEED (a = 0) ≤ 1.80 | above: the shipped servo's start spike read 1.94–3.04 | NOMEAS when the reference was not all AT_SPEED (a held or stopping wheel) |
| **R19-DUAL-SPINFOL-P** (A-8) | the two following readings within 5 points | they differ more | — |
| **R19-DUAL-SPINSYM-P** | medium, schedule: larger direction's current ÷ smaller ≤ 1.25 | above | **SPINCTL** |
| **R19-DUAL-SPINCTL-P** (control) | legacy current ÷ schedule current ≥ 1.25 | below: the load masks the offsets' effect | — |
| **R19-DUAL-SPINLEAD-P** | schedule ÷ fixed at the quarter ≤ 1.05 (both now over 300 ms windows) | above | — |
| **R19-DUAL-SPINPLAT-P** (X-5 on the floor) | 2 s after one wheel's fault, the other runs at ≤ 10 % of its earlier rate | it keeps driving (PL-117) | — |
| **R19-DUAL-CRPCOAST-P** (control) | the coast rolls ≥ 3 ticks down the incline | it does not: CREEP/CRPHOLD go NOMEAS | — |
| **R19-DUAL-CRPLOW-P** (control) | creep ≥ 2 ticks at a 1 % ceiling | it does not: repeat steeper | — |
| **R19-DUAL-CREEP-P** | **0 ticks** of creep while HOLDING, at the 10 % ceiling | any creep | CRPCOAST, CRPLOW |
| **R19-DUAL-CRPHOLD-P** | still HOLDING when the 15 s window ends | LIMITED or SLIPPED | — |
| NOSTALL, DBGMASK, TRACES, RSTPROV, LAGBND (-P) | as every part | as every part | — |

**Recorded, not judged:** `BM-CREEPW` sizes `HOLD_CEILING_PCT` under load; `BM-SPINW` gives loaded current per wheel
and direction; `BM-SPINSTART` gives each quarter START's peak and its steady reference (A-2's two terms).

**Known confounds:**
- If his hand displaces a wheel by a tick before release on the incline, the hold ramps to its ceiling and hands off
  at about 10 s. It shows as LIMITED, with `disp` 1.
- In LOAD, a pull that stops the platform for a second latches the protective stop (`STALLED`): correct behaviour,
  but not the overload claim, so that trial is not judged and the next asks for less.

## What this visit cannot measure, named

- A phase short's current (PL-118).
- The 27 A derate: the rig cannot reach it.
- Speeds above power 23 on the floor.
- An overload the platform meets on its own, unassisted: LOAD's overload is his pull, set against a limit lowered to
  4 A. That is the claim's construction, stated.
- The feel of the ramp beyond what he reports: no cell measures jerk under load (t0-stopreason's R22 cells measure it
  wheels up, pass by pass).
- The serial `protclear` path (PL-111's own certification) and the demos: the release-candidate pass.

## After the visit

One analysis per set of logs, under `DOCs/procedures/BENCH-RUN-PROCESSING.md`, with his "PL-160 feel" line quoted.
Then close every punch-list item its cells certify (PL-93, PL-95, PL-106, PL-132, PL-150, PL-111's precondition, and
PL-160's feel), and re-count the burn-down.

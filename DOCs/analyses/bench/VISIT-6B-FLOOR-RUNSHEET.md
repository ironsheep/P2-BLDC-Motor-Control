# The floor run — run sheet (the last bench visit before 6.0)

**Task:** «#3576» runs it; «#3591» built it, and SRC_REV 58 added the load cells. **Tier:** `dual-spin` (part
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

It also carries the floor run's own claims, unchanged since «#3591»: the commutation offsets under load, R18.3's loaded
expectations, X-5 on the floor (PL-117), and the hold on an incline, which sizes `HOLD_CEILING_PCT`.

**Not in this visit:** the serial path and the demos, which wait for a release-candidate driver. The 27 A derate
cannot be reached on this rig. PL-160's jerk-limited ramp is not built yet.

---

## ⛔ First: push, then pull at the bench

`git log --oneline -1 -- src/` at the bench must show the commit that carries **test_bench_dual SRC_REV 58** and the
release-candidate driver.

## Check the banner before reading anything else

| Every `dual-*` log must read |
|---|
| `BM-BANNER,...,src_rev,58,fmt,37,part,SPIN` |
| `BM-BUILD ... drv_rev,37` or later: the driver under test. A lower number means an old tree. |
| `BM-BLKBUILD`, `BM-LDBUILD` and `BM-RDBUILD` present: the load cells' numbers were pre-registered |

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
| **Purpose** | **Certification** of the load claims above, on the release-candidate driver, plus the floor run's measurements: loaded current by direction and pair, and the hold's duty and current on the incline. |
| **Hardware risk** | **The highest this project has: wheels down, a person present.** SPIN turns the platform in place at up to about half a turn a second, at most one turn per leg; legs 11 and 12 fault one wheel on purpose. BLOCK drives only the chocked LEFT wheel, current-limited to 2 A (about 14 N at the tyre); if it turns 17 mm the harness stops it. LOAD drives the platform straight at a slow walk, current-limited to 4 A, at most 2 m, with an e-stop 35 mm past that; you walk behind it. On the incline the platform can roll up to about 17 mm (coast) or 35 mm (hold trials) before the harness brakes it. The 10 A abort and the fold-back limiter apply throughout. **Stand outside the swept circle while it spins. Panic: disconnect the battery.** |
| **Who observes / acts** | Stephen, on every screen: each says what is happening, the one next click, and what he should see. He chocks the wheel (BLOCK), pulls the strap (LOAD) and handles the platform on the incline (CREEP). |
| **Runs that carry state** | None. Every pair of legs, every BLOCK and LOAD trial and every creep trial runs in its own steering lifetime; a written offset pair is restored and read back (`BM-OFFREST`); the lowered current limits are restored before each lifetime stops. |
| **Run length** | About **14 minutes of run**: SPIN about 5.5 (12 legs and 2 re-drives), BLOCK about 1.5, LOAD about 4 (a free trial and 1 to 3 drag trials), CREEP about 2.5. About **40 minutes at the rig** with the setups. Cap 30 minutes of run. About 35 clicks. |
| **Repeatability** | Repeatable. Each segment's first screen has SKIP: to rerun only BLOCK, LOAD or the incline, SKIP leg 1 and each segment before the one you want. |
| **Variant matrix** | One binary, `-D BENCH_QUIET -D DUAL_PART_SPIN`, on the Visit 10 rig: Rev B, 6.5in hubs, 18.5 V pack, 270 MHz. DEBUG footprint 7,494 bytes (limit 12,404). |

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
| **BLOCKED-WHEEL TEST** | leaves the platform where it is. **Chocks the LEFT wheel front and back**, hard against the tyre. Hands clear, then clicks START. Two short trials follow: in each the left wheel pushes the chock and should stop itself within 4 s. Nothing else to click. |
| **LOADED-DRIVE TEST** | **removes both chocks**, aims the platform's front down the lane, tethers it slack along the lane, **ties the strap to the frame beside the LEFT wheel**, and stands behind holding its end slack. Clicks START. |
| LOAD READY, "NEXT: KEEP THE STRAP SLACK" | the free trial: clicks START and walks behind, strap slack |
| LOAD READY, "NEXT: YOU PULL WHEN TOLD" | clicks START and walks behind, strap slack |
| **PULL** | **pulls back on the strap, firmly and steadily, while walking, until the number (its speed, % of command) reads about 50**. Never to 0: a platform that stops for a second latches the protective stop, and the trial is not judged. Keeps pulling until LET GO. |
| LET GO | lets the strap go slack; the platform stops itself |
| BACK | pushes the platform back to the start of the lane (its wheels roll freely), clicks DONE. **After the last trial, unties the strap first.** |
| LOAD READY, "LAST TOO LIGHT: PULL HARDER" or "LAST STALLED: PULL LESS" | adjusts his pull, clicks START. There are up to three drag trials; the first judged one ends LOAD. |
| NOW THE INCLINE | carries the platform onto the ramp, wheels rolling straight down the slope, holds it, clicks START; then DONE when he lets go, DONE when he holds it again |

---

## SPIN: the legs

Odd legs spin right (clockwise from above), even legs spin left.

| Legs | Pair | Speed (power) | Pair each driver must apply |
|---|---|---|---|
| 1–2 | the shipped lead schedule | SLOW (7) | 17 / 336 |
| 3–4 | schedule | MEDIUM (13) | 15 / 337 |
| 5–6 | **legacy 43/317, the control** | MEDIUM | 43 / 317 |
| 7–8 | schedule, traced | BRISK (23) | 1 / 351 |
| 9–10 | fixed 14/338 | BRISK | 14 / 338 |
| 11–12 | schedule, **one wheel faulted, then the re-drive** | SLOW | 17 / 336 |

The travel limit is one revolution of the platform: π × 387 mm = 1,216 mm, 211 hall ticks. Each leg's limit is armed
before it moves, and the harness e-stops 6 ticks past it. A re-drive's limit is whatever is left of its leg's turn
(`BM-RDRIVE remain`), so the tether still winds at most one turn.

## What each cell decides, and how each can fail

Every criterion is fixed in `src/test_bench_dual.spin2` before the run (the load cells' section is "the floor run's
load cells"). Each claim that needs a control has one, and its PASS counts only when the control's did. Each cell
prints NOMEAS when its precondition did not arise, and its record's `why` says which.

### The load cells (SRC_REV 58)

| Cell | Criterion | Fails if (the negative) | NOMEAS when |
|---|---|---|---|
| **R21-DUAL-POSTFLT-P** (per motor, PL-93) | after the fault and its recovery, the same spin's getCurrent() over its first second at speed ÷ the leg's own over the same second before the fault ≤ **1.50** | above; an absolute-current abort scores 99.99. **Negative, measured:** Visit 6a drew 3.8–4.2× and hit the 10 A abort on the drive-up (PL-93) | the fault did not latch, the recovery did not clear, too little turn left, he skipped it, or the "before" is under 0.05 A |
| **R21-DUAL-BLKSTOP-P** (LEFT, PL-106) | every trial whose wheel stayed blocked: both codes `ERR_PLATFORM_BLOCKED` within 4 s but not before 1 s, and the left reads `SR_BLOCKED` | a trial not latched in 4 s (a driver without the stop leaves a stalled wheel commanded: Visit 6a's wheel sat at duty_max reporting AT_SPEED), a latch before 1 s (a false fire, PL-116's class), or another stop reason | the chock did not hold (the wheel turned 3 ticks: `why NOT_BLOCKED`, and BLOCK ends) |
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

### The spin and incline cells (unchanged)

| Cell | Criterion | Fails if | Control |
|---|---|---|---|
| **R19-DUAL-SPINSTOP-P** | every leg ends within ±2 ticks of the limit | an overshoot, an undershoot, or the guard fires | — |
| **R19-DUAL-SPINOFF-P** | every driver applied the table's pair | a write that did not land | — |
| **R19-DUAL-SPINDIR-P** | no wheel ran against its commanded direction | any did | — |
| **R19-DUAL-SPINHUNT-P** (A-3) | slow and medium schedule legs: no window with duty_pk − duty > 400 or err_pk > 76 | any such window | the shipped servo read 800–1,650 / 75–89 wheels up |
| **R19-DUAL-SPINERR-P** (A-4) | \|mean err\| within 47–49 in every schedule window | outside | — |
| **R19-DUAL-SPINSTRT-P** (A-1) | worst duty drop at start ≤ 100 per mille | above | shipped read 340–530 |
| **R19-DUAL-SPINPEAK-P** (A-2) | worst start-current ratio ≤ 1.80 | above | shipped read 1.94–3.04 |
| **R19-DUAL-SPINFOL-P** (A-8) | the two following readings within 5 points | they differ more | — |
| **R19-DUAL-SPINSYM-P** | medium, schedule: larger direction's current ÷ smaller ≤ 1.25 | above | **SPINCTL** |
| **R19-DUAL-SPINCTL-P** (control) | legacy current ÷ schedule current ≥ 1.25 | below: the load masks the offsets' effect | — |
| **R19-DUAL-SPINLEAD-P** | schedule ÷ fixed at the quarter ≤ 1.05 | above | — |
| **R19-DUAL-SPINPLAT-P** (X-5 on the floor) | 2 s after one wheel's fault, the other runs at ≤ 10 % of its earlier rate | it keeps driving (PL-117) | — |
| **R19-DUAL-CRPCOAST-P** (control) | the coast rolls ≥ 3 ticks down the incline | it does not: CREEP/CRPHOLD go NOMEAS | — |
| **R19-DUAL-CRPLOW-P** (control) | creep ≥ 2 ticks at a 1 % ceiling | it does not: repeat steeper | — |
| **R19-DUAL-CREEP-P** | **0 ticks** of creep while HOLDING, at the 10 % ceiling | any creep | CRPCOAST, CRPLOW |
| **R19-DUAL-CRPHOLD-P** | still HOLDING when the 15 s window ends | LIMITED or SLIPPED | — |
| NOSTALL, DBGMASK, TRACES, RSTPROV, LAGBND (-P) | as every part | as every part | — |

**Recorded, not judged:** `BM-CREEPW` sizes `HOLD_CEILING_PCT` under load; `BM-SPINW` gives loaded current per wheel
and direction.

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
- The serial `protclear` path (PL-111's own certification) and the demos: the release-candidate pass.

## After the visit

One analysis per set of logs, under `DOCs/procedures/BENCH-RUN-PROCESSING.md`. Then close every punch-list item its
cells certify (PL-93, PL-95, PL-106, PL-132, PL-150, and PL-111's precondition), and re-count the burn-down.

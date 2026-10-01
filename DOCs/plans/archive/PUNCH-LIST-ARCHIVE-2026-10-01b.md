
# Punch-list archive — 2026-10-01 (b)

Items swept out of [`DOCs/PUNCH-LIST.md`](../../PUNCH-LIST.md) by the punch-list study that opened 6.1.0 planning
(2026-10-01, after the 6.0.0 closeout sweep in [`PUNCH-LIST-ARCHIVE-2026-10-01.md`](PUNCH-LIST-ARCHIVE-2026-10-01.md),
which is never re-edited). Each entry is copied verbatim, and above it an **Archived** line says what closed it and
what was checked in the tree to establish that.
Swept: PL-19 (obsolete), PL-31 (delivered), PL-163 (certified; its residual is the new active PL-170), and the three
2026-09-20 driver notes (superseded).

**This file is never re-edited.** If an archived item must be reopened, it returns to the active
punch list as a *new* item that references this archive.

**"What is outstanding?" is answered from the active punch list only** — never re-derived from
this file.

---

### PL-19 -- `test_bench_char.spin2` drives the right wheel in motor frame, but captions it in robot frame

> **Archived 2026-10-01 — OBSOLETE.** The captions this entry was about no longer exist: the meter-free rework
> (`7595274`) removed the binary's PLOT panel, and with it every caption bitmap (PL-37). The other half of the fix is
> in the tree: `test_bench_char.spin2` documents that it runs in motor frame (`forwardIsReverse()` is never called,
> header :75) and every BC-HOLD record carries `robot_dir` (`:2452`). The data was always valid (below).

> **6.0 status (2026-09-26 audit):** ANCILLARY — not chased for 6.0 (Stephen, 2026-09-26: only work that makes a 6.0 feature operational is chased) (bench harness captions)

**Found 2026-09-12 in Bench Pass 1 step 4, by Stephen at the bench** -- the right wheel turned
opposite to the plan on all four RIGHT holds (his meter sheet marks them `REV???` / `FWD???`).

`test_bench_spin.spin2:77-79` calls `wheelR.forwardIsReverse()`, because the two motors face
opposite directions on the chassis. `test_bench_char.spin2` `ensureSide()` (:604-609) starts
`wheelR` without it, so "RIGHT WHEEL FORWARD" commands a positive increment, which on the
right motor is robot-reverse. The correction was made to the spin binary at 23:40 on
2026-09-11 and never searched into its sibling -- a doctrine-overlay P8 miss.

**The data is valid.** `BC-HOLD` logs the signed `cmd_incre`, so every hold is attributable,
and motor frame is the frame that exposed the forward/reverse current asymmetry
([evaluation](analyses/bench/2026-09-12/CHAR-RUN-EVALUATION.md)).

**Fix (my call, per P3):** keep characterisation in motor frame -- it is a per-motor
measurement -- and make the frame explicit: captions name both frames (e.g. *RIGHT MOTOR +
INCREMENT (robot reverse)*), and `BC-HOLD` gains a `robot_dir` field. The captions are bitmaps,
so regenerate with `tools/gen_bench_char_assets.py`. Check `test_bench_t0.spin2` and
`test_bench_detect.spin2` for the same class in the same change.

---

### PL-31 -- the offset scan finds the no-load minimum but not the fault cliff beside it

> **Archived 2026-10-01 — DELIVERED.** All three scan changes the entry asked for were built and measured: the cliff
> walk and the minimum-to-cliff margin (scan v2, run 4: both left cliffs located, 7.5° from each low), and the zero
> read before every point including after a restart (scan v3, measured in run 7; run 8 reproduced the quarter-speed
> minima within 0.1–1.6°). What the scan still lacks is a separate defect, carried by PL-46 (its geometry under the lag
> limiter) and PL-98 (two cells that cannot fail).

> **6.0 status (2026-09-26 audit):** ANCILLARY — not chased for 6.0 (Stephen, 2026-09-26: only work that makes a 6.0 feature operational is chased) (commutation scan instrument)

**Found 2026-09-12 in scan run 3** (DERIVED from MEASURED, evaluation §4, §5, §8). On the left
motor every minimum-current offset sits within 10° of an offset that faults, measured with the
wheels unloaded:
- positive ¼: minimum −21°, fault by −8°;
- positive ½: still falling at −11°, fault at −6°;
- negative ¼: still falling at +13°, fault at +3°, so the minimum is not bracketed.

A no-load minimum therefore cannot be shipped as the offset without a margin measured under
load.

**Scan changes:**
1. fine-walk (5°) into a fault edge before declaring `EDGE_FAULT`;
2. report the cliff location and the minimum-to-cliff margin per leg;
3. re-measure the zero at every reference point, because a ~13–16 mV sense-side bias appeared
   after some high-current or fault events (coarse points read higher than fine points at the
   same offset, with the same duty).

**Scan v2 (`5ea0510`) in run 4 (MEASURED, `analyses/bench/2026-09-13/SCAN-RUN-4-EVALUATION.md`):**
- Both left cliffs were located: negative edge 5.5°, positive −15.5°, each 7.5° from its lowest
  point.
- The bias is a zero shift: references of 89.3 and 100.4 mV sat on zeros of 7.7 and 18.9, giving
  identical net readings of 81.6 and 81.5. The 18.9 zero was read 1.5 s after an `ABORT_I` restart.
- Remaining defect: `evaluateBracket` never brackets a side whose walk stopped on faults, even
  when the cliff probe rises above the low. Both legs therefore reported NOT_BRACKETED, neither
  fitted, and both ½-speed legs were skipped.

Scan v3 fixes it by ending the sweep window at the last good point, and reads the zero before
every point, including after every restart.

---

### PL-163 -- on a Rev A board below about 2.7 A, the fold-back cut the drive on every driven frame

> **Archived 2026-10-01 — CERTIFIED.** The defect this entry names is ABSENT on both Rev A boards, MEASURED on two
> runs (2026-09-30: `fold_win` 407 / 341 of 220,000 unloaded on the RIGHT board; rerun 734 / 9,485 LEFT and 127 / 919
> RIGHT, where the unfixed compare folds every frame). The fix is DRIVER_REV 38's compare plus DRIVER_REV 40's
> `FOLD_MIN_MV`. What stayed open is a different item: `FOLD_MIN_MV`'s ±3 mV noise premise is false on Rev A (7 mV
> measured), the FOLDPOS cell cannot measure as built, and two `t0-reva` harness gaps. That is now **PL-170** on the
> active list.

> **6.0 status (2026-09-30, after both Rev A runs):** the every-frame defect is ABSENT on both Rev A boards (MEASURED,
> below); both cells NOMEAS by their own rules (the test limit sits at the sense chain's noise floor); the residual (FOLD_MIN_MV's noise premise, false on Rev A) is ANCILLARY -- TEST USE limits only,
> no user can reach it (overlay P5). Not chased for 6.0 unless Stephen asks.

**Found 2026-09-27** by the DRIVER_REV 37 desk review (PL-146's rest-offset work).
- **DERIVED:** the fold-back threshold at the duty floor is `max(duty_, duty_floor_) * i_limit_k_ >> 16`. Rev A's
  larger sense resistor gives a smaller mV-per-A, and below about 2.7 A the shift truncates the threshold to 0, so
  every driven frame read above it and folded — a Rev A user setting a low current limit got a drive that could not
  hold its duty.
- **Fix (DRIVER_REV 38):** the compare folds only when the whole-mV reading is above floor(t) (`wcz`, `if_nc_and_nz`),
  i.e. at or above ceil(t). Rounding the threshold instead would still fold every frame for t < 0.5 (1 A on Rev A).
- **Negative:** on Rev A with `testSetCurrentLimits(2, 2)`, a driven, unloaded wheel at the duty floor counts
  `foldback_frames` every frame; fixed, it counts none.

**Disposition (2026-09-30):** certifies on the Rev A platform, which carries two Rev A boards; boards are never moved
between platforms (STEPHEN 2026-09-30: *"Prepare it to run on the RevA platform that has two RevA boards"*). Tier
`t0-reva`, rebuilt by «#3629» with no window: the unloaded legs on each Rev A group are the negative (FOLD), and a grip
on the RIGHT wheel, held until the program stops it, is the positive (FOLDPOS). The cell's record states the effective
threshold, `FOLD_MIN_MV` (a fold needs a 5 mV net reading).

**2026-09-27, the residual, built (DRIVER_REV 40, uncommitted).**
- **DERIVED:** DRIVER_REV 38 folds on a net reading above floor(t). At a 2 A Rev A limit near the duty floor t is
  0.75 mV, so any 1 mV net reading folds, about 0.2 A of DC link. That decision sits below what the sense chain
  resolves. Each reading is one frame, floored to whole mV. The noise is ±3 mV (CURRENT-LIMIT-AND-STOP-DESIGN.md §3.4;
  PL-146's Rev B offset reached its threshold on noise). The netted zero is the truncated mean of floored readings,
  so it sits 0.5–1.5 mV low. Zero current can therefore read up to 4 mV net.
- **Built:** `FOLD_MIN_MV` = 4. `setFoldLimit()` writes `i_limit_k` and raises the fold's `duty_floor` to
  ceil(4 × 65536 / K), so t never falls below 4 mV and a fold needs a 5 mV net reading. The two longs are written in
  the order whose one-frame mix is the lower threshold. Above the raised floor, t is unchanged.
  - Rev B is never raised: t ≥ 11 mV at 1 A. Neither is Rev A at 11 A and up, so the shipped 40 A and 27 A limits
    are unchanged on both boards. Only a TEST-USE Rev A limit of 1–10 A changes. At 2 A the floor moves from
    m = 0.10 to 0.53.
  - The derate's estimate keeps m = 0.1 (`dutyFloorEst`).
  - Spin2 only: cog RAM and LUT unchanged.
- **Negative (desk model, 220,000 frames at duty 2,000, Rev A, 2 A, uniform ±3 mV noise):**

  | Case | pre-DRIVER_REV 38 | DRIVER_REV 38–39 | fixed |
  |---|---|---|---|
  | Unloaded (0.09 A DC link) | 220,000 | ~145,000 | **0** |
  | Overloaded (1.2 A DC link) | 220,000 | 220,000 | 165,000–201,000 (still folds) |

- **What still protects at a raised floor:**
  - the fold itself, on any net reading over 4 mV
  - `duty_min` (m ≈ 0.065), since the fold never cut below it
  - the lag gates and the blocked stop
  - the 1 s derate average
- **R22-T0-REVA-FOLD:** its PASS (a window rise of 0) still holds. Its record and notes still describe a threshold
  floored to 0 and a 1 mV fold. They need the effective threshold and a positive control before they carry
  certification (see the task report).

**2026-09-30, the Rev A platform run** (`t0-reva`, test_bench_t0 SRC_REV 29, DRIVER_REV 46;
`DOCs/analyses/bench/2026-09-30/reva/REVA-PLATFORM-EVALUATION.md`, log `debug_260930-155650.log`).
- **MEASURED, the defect is absent:** the RIGHT Rev A board's unloaded legs folded on `fold_win,407` and `341` of
  `frames_win,220_000`; the pre-DRIVER_REV 38 compare folds on every frame.
- **MEASURED, the residual's premise is false on Rev A:** `net_max_mv,7` on both unloaded legs (zero 13 mV, mean 13 mV,
  792,220 samples), against the ±3 mV that sized FOLD_MIN_MV = 4. So the fold acts on noise, about 75 frames a second,
  at a 2 A limit. Only `testSetCurrentLimits()` sets such a limit; at the shipped 40 A peak the Rev A threshold at the
  duty floor is about 15 mV. **Ancillary for 6.0.** If chased: FOLD_MIN_MV per board revision, sized from this reading.
- **Both cells NOMEAS** by their pre-registered rules (FOLD: PREMISE_NOISE; FOLDPOS: `measured,FALSE`).
- **FOLDPOS cannot measure as built (SRC_REV 29, harness).** A redesign needs all three: (1) the judged window opens at
  the speed-up, not after a 3 s lead, because a firm grip latches the protective stop about 1 s after it stalls the
  wheel (`state_end,7`, `fold_win,0`); (2) no duty gate, since the fold holds the duty below m = 0.2 under a grip
  (`duty_pk,1_600`); (3) a rate criterion against the unloaded legs' noise-fold rate, with the acceleration's folds
  separated from the grip's (`fold_ramp,758` mixes them).
- **Harness gaps, fix with the next Rev A build:** `t0vStart()` reports a refused start's board as `REV_Unknown`
  ("NONE"), so a start-check refusal reads as "not REV_A"; the hold record prints no stop reason.
- **The LEFT board did not start:** its start check failed the phase U lead after retries (`healthFailed = $0000_0004`,
  `error,-1_020`); V and W passed, and the RIGHT Rev A board passed all three. Asked of Stephen (lead open, or a false
  refusal); a false refusal would be a start-check finding of its own, not PL-163's.

**2026-09-30 21:09, the Rev A rerun** (`t0-reva`, test_bench_t0 SRC_REV 30, hands-off;
`DOCs/analyses/bench/2026-09-30/reva2/REVA-RERUN-EVALUATION.md`, log `debug_260930-210953.log`).
- **The LEFT board starts** after Stephen's lead check: `chk,$5F,fail,$0`, every lead probe ~800 mV. The first run's
  refusal was the lead; the start check's refuse and pass are both now seen on Rev A.
- **MEASURED, the defect stays absent on both boards:** unloaded `fold_win` 734 / 9,485 (LEFT, powers 10 / 5) and
  127 / 919 (RIGHT), of 220,000. The LEFT's power-5 leg folds 4.3 % on noise: its mean reads 1 mV above its netted zero.
- **The hands-off positive control's premise is false:** the hard speed-up (power 40 at 10,000 mm/s²) never raised the
  mean net reading to 3 mV (`net_mean_mv` 1 / 0), because the fold itself, at 4 mV (about 0.8 A of DC link), cut every
  frame that crossed it; the wheels were still spinning up at 1.5 s. FOLD and FOLDPOS NOMEAS on both boards.
- **Disposition:** at a 2 A limit every Rev A reading sits at the sense chain's noise floor (2 A is about 10 mV against a
  12-13 mV zero; noise peaks 6-8 mV), at a limit no user can set. No further Rev A runs for 6.0; the residual stays
  ancillary (overlay P5) unless Stephen asks.

---

### The three 2026-09-20 driver notes

> **Archived 2026-10-01 — SUPERSEDED.** All three were design notes for the R18 drive rework, and each ended "R18.4
> was built and measured unloaded; what remains is the loaded floor run". That work shipped in 6.0.0 and the loaded
> floor runs took place (2026-09-28 and the 2026-09-30 rerun): the drive reads whether it follows its command
> (`fol_pct`), how much field the limiter withheld (`lag_held`) and how much duty was capped (`duty_capped`); the blocked
> stop that the 25 A mechanism lacked is certified (PL-106, archived 2026-10-01); the speed-change kick is certified
> (PL-87, archived 2026-09-27); and the ladder now descends (`DESCEND`). What the floor runs found that is still open
> is PL-167 (speed under load), which carries it forward.

#### ⭐ THE OBSERVABLES THEMSELVES MUST BE RESPECIFIED -- a measure that tops out is not a measure

**STEPHEN 2026-09-20:** *"if we have measures that are topping out we need to respecify them so they do
not - as they are not useful once topped out"*. That is the general statement of why every instrument
built on this driver has been blind, and it applies to the driver's own control as much as to the bench.

| Observable | How it tops out | What it should be instead -- unbounded where it matters |
|---|---|---|
| `err` (position error) | **Twice over.** The lag limiter holds it near `LAG_HOLD` (100), and the stored field is bounded by its own +-127 representation -- the tree already notes a driver with no limiter simply prints 127. | **The limiting actually applied** -- the field advance the limiter withheld this pass. When the drive is keeping up it is zero; when it cannot, it grows without bound. That is the same information `err` was supposed to carry, in a form that does not stop. |
| `duty` | Saturates at `duty_max` (24_264) and pins there for the whole top half of the range. | **Duty DEMAND before the cap**, or the **deficit** (demand less cap). Once duty pins, the deficit is what says how far past capability the command is; duty itself says only "still pinned". |
| `tr_over` (the kick cell) | Derived from `err`, so it inherits both ceilings -- which is why it read 0 of 22 while the transition current rose seventy-five fold. | Transition **current**, already recorded as `tr_i_pk`. Not clamped. |
| `AT_SPEED` | A boolean meaning "my own increment reached its target" -- true by construction even when the motor never got there. | **Measured rate against commanded rate**, a ratio that keeps informing on both sides of the limit. |

⭐ **This is not only a telemetry fix. The respecified quantities are exactly what the drive needs as
feedback**: "how much am I withholding" and "how much duty did I want beyond what I have" are the two
numbers that say the command is unachievable, and a drive that has them does not need a separate droop
detector bolted on -- it can hold at the achievable rate by construction. The instrument and the control
want the same respecification, which is a sign it is the right one.

**Cog space is a constraint to respect, not a gate** (STEPHEN 2026-09-20: *"you are fretting too much
about cog space, the lut addition just doubled it. we have room we just have to be mindful"*).

**Fix direction (this is the 6.0.0 driver work, and everything else is downstream of it):** close the
loop the halls and the current are already giving us -- correct the field against hall edges rather than
free-running between them, bound the ramp by measured acceleration rather than a fixed increment step,
and use current as the signal for commutation quality rather than only as a fold-back trigger. **A
droop detector, which this list previously proposed, is a guard around this defect and not a fix for
it** (doctrine D1: fix the system, not the display).

#### What the user can actually command -- the space the drive has to be good across

**STEPHEN 2026-09-20:** *"if we also weigh-in what a user can command we are going to have to handle
small delta speed-up/slow-down requests as well as large, near max throttle... our drive mech. has to
handle this well"*. That is the acceptance space, and measuring against it exposes two gaps.

⛔ **CORRECTION to an earlier reading of mine: the kick does NOT scale with the size of the speed
change.** MEASURED, the SAME 20x10^6 step taken at six places in the range:

| step | 20->40 | 40->60 | 60->80 | **80->100** | 100->120 | 120->140 |
|---|---|---|---|---|---|---|
| transition current | 234 | 583 | 1_197 | **1_439** | 1_264 | 599 |

**Identical command, six-fold difference in what the motor does** -- peaking at the step that lands on
the saturation knee (rung 7). So the same user action, a modest throttle bump, behaves completely
differently depending on where in the range it is made. **Where the change happens dominates; how big it
is does not.** That is a property of the drive, not of the request, and it is exactly what "handle this
well" has to mean.

⛔ **AND EVERY TRANSITION WE HAVE EVER MEASURED IS A SPEED-UP.** MEASURED across the whole load: **44
speed-up steps recorded, ZERO speed-down steps.** The ladder only climbs, and the LIVE segment
(QTR -> HALF -> TOP) climbs too and emits no transition record at all. **A user slowing from 80% to 60%
is completely uncharacterised** -- and slowing is the direction where the field must fall BACK through
the rotor, which is the opposite sign of error and a different failure if it is wrong.

**The space, and what we hold for each cell:**

| | small delta | medium delta | large delta | near-max |
|---|---|---|---|---|
| **speed UP, low in range** | not measured | MEASURED (rungs 3-5) | not measured | n/a |
| **speed UP, at the knee** | not measured | **MEASURED, and it is the worst case** | not measured | n/a |
| **speed UP, high in range** | not measured | MEASURED (rungs 9-12, already saturated) | not measured | MEASURED, saturated |
| **speed DOWN, any** | **NOTHING** | **NOTHING** | **NOTHING** | **NOTHING** |

**So the acceptance test for the corrected drive is a ladder that also descends, that includes a small
delta and a large one at each of low / knee / high, and that records a transition for every step
including the LIVE-style ones.** The instrument change is small -- `BM-RUNGTR` already carries the right
fields and simply is not emitted for every segment -- and it must land with the drive fix, not after it,
or the fix is verified only on the quarter of the space we happen to have.

**Verification is already paid for on the part we do cover:** the ladder prints `duty_pk`, steady
current, `err_pk` and the transition current per rung, so the table above IS the acceptance test. A corrected drive flattens the
transition current, keeps duty off its ceiling until genuinely at the ceiling, and does not report
AT_SPEED while the field is parked.

**2026-09-26:** R18.4 was built and measured unloaded at Visits 8, 8b, 9 and 9b; what remains is the loaded floor run and the kick, PL-87.

#### ⛔ THE MECHANISM, read from the samples 2026-09-20 -- and it is a DRIVER defect, not a harness one

**MEASURED** (`debug_260919-173537.log`, tid 16, RIGHT wheel, eight consecutive samples k 64-71):

| | reading |
|---|---|
| `i` | **3_742 -> 3_772 mV**, i.e. about **25 A** at the harness's own 150 mV/A calibration |
| `d` | **23_891 -> 24_264**, and 24_264 **is `duty_max`** -- the servo wound to the ceiling and stayed |
| `e` | **pinned at -101**, just under the driver's `\|err\| >= 125` fault test, and right at `LAG_HOLD` (100) |
| `st` | **AT_SPEED** throughout |

**DERIVED, and every step is visible in the numbers above:** the lag limiter holds the field so `err`
sits at its hold threshold and **never reaches the fault test**; the duty servo, seeing an error it
cannot clear, **winds `duty_` to `duty_max`**; S-2's current fold-back computes its threshold as
`max(duty_, duty_floor_) * i_limit_k_ >> 16`, so **at `duty_max` that threshold is at its most
permissive** and no fold-back occurred (duty rose into the ceiling rather than backing off); the
protective stop did not fire either. The driver therefore sat at **maximum duty drawing ~25 A while
reporting AT_SPEED**, and the only thing that stopped it was the harness's external 10 A abort.

⛔ **A USER HAS NO SUCH ABORT.** This is the same shape as a stalled or blocked wheel -- "commanded rate
cannot be reached" -- so it is reachable outside a provoked fault. It is filed here because a fault
exposed it, but **the condition is general and it is the most consequential thing Visit 6a found.**

**Fix direction (driver, and it subsumes PL-86 and PL-46's instrument problem):** a **droop detector** --
compare commanded tick rate against measured tick rate, and when they diverge for N consecutive frames
act on it (fault, or the protective stop that already exists). One mechanism then serves three needs:
the driver gets the protection it is missing, the commutation scan gets the stop condition the limiter
took away (PL-46), and the fault provocation gets a reachable edge (PL-86). The current-limit threshold
scaling with duty should be re-read at the same time: it is most permissive exactly when duty is
highest, which is backwards for this failure.

**2026-09-26:** R18.4 was built and measured unloaded at Visits 8, 8b, 9 and 9b; what remains is the loaded floor run.

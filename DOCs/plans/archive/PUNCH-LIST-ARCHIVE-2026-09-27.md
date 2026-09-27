# Punch-list archive — 2026-09-27

Items swept out of [`DOCs/PUNCH-LIST.md`](../../PUNCH-LIST.md) after Visit 10 pass 7
(task «#3613»; evaluation
[`VISIT-10-PASS7-EVALUATION.md`](../../analyses/bench/2026-09-26/pass7/VISIT-10-PASS7-EVALUATION.md)).
Each entry is copied verbatim, and under it an **Archived** line says what closed it.

**This file is never re-edited.** If an archived item must be reopened, it returns to the active
punch list as a *new* item that references this archive.

**"What is outstanding?" is answered from the active punch list only** — never re-derived from
this file.

---

### PL-66 -- a faulted motor stays faulted when the caller sends the same power again

> **6.0 status (2026-09-26 audit):** AWAITS CERT — fix built, not yet run: FLTRETRY cannot certify until dual-b's provocation uses testForceFault (PL-119).

**Found 2026-09-15** while stating the fault-clearing rule for «#3547». DERIVED from source, not observed on
hardware.

**The mechanism (`src/isp_bldc_motor.spin2`, PASM driver):**
- The driver leaves `DCS_FAULTED` only through `.resetFault`, inside `.newRqst`.
- A stop always gets there: a zero request while not STOPPED jumps to `.newRqst`.
- A nonzero request gets there only if it differs from the last one. `.notRqStop` compares it with the saved
  request and, when they are equal, continues the current request (`.currRqst`).
- In `DCS_FAULTED`, `.currRqst` matches no state and falls through to `.justIncr`, which advances `angle_` with
  the drive off. The motor stays faulted.

**Who is affected:** a caller that retries after a fault by sending the power it was already running at, such as
`driveAtPower(50)` again, or a loop that re-sends its current command. The retry does nothing. Since «#3547»
`getStatus()` reports `DS_FAULTED`, so the state is visible, but nothing says the retry was ignored. The two-wheel
object and the serial protocol inherit it.

**Related:** PL-28 item 1 is the same mechanism on the test path. `testResetFault()` works around it by sending
zero first.

**Fix direction:** decide what a repeated command does while faulted.
- Treat it as a new request, so a retry restarts the motor. Correct by construction for a retry, but a fault at
  speed may mean a blocked wheel (PL-47 rule 5), and a retry would drive into it again.
- Or keep requiring a stop or a changed power first, and state that in `DRIVE-OBJECTS.md` and the method docs.

That is an API and safety decision for Stephen, taken when the fault path is next scheduled. «#3547» documents
today's rule: *the fault clears when a stop or a different power is commanded*.

**Fixed in tree 2026-09-16 («#3556»). Run-time proof STILL MISSING (aged-state sweep 2026-09-17):**
`R16-DUAL-FLTRETRY-B` was NOMEAS at Visits 4 and 5 because the fault provocation trips the harness's own
10 A abort first (PL-86). IN THIS RELEASE with fault handling. Decided by Stephen's
2026-09-16 API rule: a retry restarts the motor.

**Where the fix lives, and why.** The fault-clear edge is made in the front cog, not the driver.
`drvMotor` copies `tgt_incr` into `sv_tgt_incr` every pass, so its "same request" compare means "the
command is still standing". An edge taken there would clear a fault on the very next pass, and the
fault would never latch. The PASM is unchanged.

**What happens on a drive while FAULTED.** `frontClearFault()`, called from `frontDrive()`, runs
first. It writes a zero command, and waits a bounded `FRONT_SYNC_WAIT_PASSES` drive passes for
`drv_state` to leave `DCS_FAULTED`. A zero request reaches `.newRqst` -> `.resetFault` in one pass.
- On success, the requested command is written.
- On expiry, it returns `ERR_NO_RESPONSE` and the zero stays written.
- The wait is counted in `bDidWait` and in `requestWaits()`.

**Two wheels.** `frontDriveWheels()` clears both selected wheels before writing either. If either
fails, both are zeroed. Invariant: *a platform never drives one selected wheel while refusing the
other.*

**Archived 2026-09-27 (Visit 10 pass 7):** CERTIFIED — R16-DUAL-FLTRETRY-B PASS in dual-reg (at speed 1.4 s after the same-power retry).

### PL-78 -- the lag error clamps at 115-116 against a 110 bound, and commanded velocity is not rate-limited (the slam)

> **6.0 status (2026-09-26 audit):** RELEASE — the speed-change kick. Stephen ruled the slam not shippable (2026-09-17); R17-DUAL-TRKICK-A was still FAIL at Visit 8b (183/182 mV) and has not been judged on the current driver.

> **STATUS 2026-09-18 («#3573»):** the first half (`LAGBND`) is certified at Visit 5. The second half -- the slam --
> is judged at Visit 6 by `R17-DUAL-TRKICK-A` on the new `BM-RUNGTR` transition record (PL-87's box). A source
> re-read of the speed-change entry found no further construction defect for a same-sign speed-up: the
> `.doSpdChange` ramp reset is the only inherited state, and it is in the binary. If TRKICK fails, the failing
> transitions' `incre` pairs name which path to read next (speed-up, ramp-down, or direction change via
> `.slow2Chg`); the driver comment no longer cites the withdrawn Visit 4 `err_pk` table as evidence.

**Found 2026-09-17 in «#3561»**, Visit 4, all four dual parts. This entry carries both the failing cell and the
physical effect Stephen reported, because the open question is whether they are one finding or two.

**MEASURED -- `R16-DUAL-LAGBND` `MAX_ABS_ERR`, bound `lo 0 hi 110`, `sat 127` in every record:**

| Part | LEFT | RIGHT | samples (L / R) | Log |
| --- | --- | --- | --- | --- |
| A | **115** | **115** | 63 947 / 63 998 | `debug_260917-131445.log` L15301-15302 |
| B | **115** | **115** | 19 761 / 19 862 | `debug_260917-130012.log` L7574-7575 |
| C | **116** | **116** | 19 933 / 19 922 | `debug_260917-131237.log` L5621-5622 |
| D | **115** | 87 | 3 293 / 2 308 | `debug_260917-125859.log` L119-120 |

**«#3558»'s lag limiter is working:** the measurement never reaches `sat 127`, which is where the unfixed driver
pegs the stored `err` field.

**DERIVED -- the number is too repeatable to be a transient.** 115 / 115 / 115 / 115 / 116 / 116 / 115
across four parts with completely different motion profiles, sample counts from 2 308 to 63 998, and both
motors. A peak driven by motion would scatter. Part D's RIGHT reaching only 87 fits: it is the shortest run and
never demanded enough.

**SETTLED FROM THE SOURCE 2026-09-17, and it makes this an INSTRUMENT defect, not a driver defect.**
`src/isp_bldc_motor.spin2:3344-3346`:

```spin2
    ' C-5 (DOCs/plans/CURRENT-LIMIT-AND-STOP-DESIGN.md section 3.2): lag thresholds, err_ units (256 per hall cycle)
    LAG_SOFT                    = 80        ' 112.5 deg: the ramp waits for the rotor; the PL-55 duty ceiling lifts
    LAG_HOLD                    = 100       ' 140.6 deg: the field stops advancing (the fault test is at 125)
```

and `src/isp_bldc_motor.spin2:3803-3804`:

```spin2
.justIncr   ' just do our increment of angle and we're done!
                cmps    lag_s, #LAG_HOLD            wc  ' C-5: the field advances only while the rotor trails it by
    if_c        add     angle_, drv_incr                '  less than LAG_HOLD, so |err_| stays under the 125 fault test
```

**The clamp is at 100, not at 115.** The test is taken on `lag_s` sampled at the *top* of the pass
(`:3560`), and the field then advances by one whole `drv_incr` before the next test. So the largest `err_` any
sampler can observe is **`LAG_HOLD` plus one pass's field advance**, and at the ladder's top rung that quantum is
roughly 15-16 err units -- which is exactly the 115-116 measured, and exactly why it barely moves between parts.

⛔ **The 110 bound was therefore wrong, not the driver.** It was written as `LAG_HOLD + 10`, under-estimating
the one-pass quantum at `ladder_max 165_000_000`. The driver is doing precisely what C-5 designed it to do, and
the fault test at 125 is still never reached -- which is the property that actually matters.

**Fix direction:** set the bound from the design, not from a round number: `LAG_HOLD` plus the maximum per-pass
field advance at `ladder_max`, computed rather than guessed, with the 125 fault threshold as the hard ceiling the
cell really guards. **This is the one case where raising the bound is correct** -- not because it turns the cell
green, but because the old bound described a state the design never promised. Record the arithmetic in the cell
so the next reader can check it (doctrine D2: a criterion that cannot be met by a correct system has not passed,
it has misreported).

> ## ⛔ CORRECTED 2026-09-17, BEFORE THE FIX WAS BUILT: "LAG_HOLD + one pass ~= 15-16" DOES NOT COMPUTE.
>
> **The arithmetic is checkable and it fails.** `err_` is `(hall angle + offset) - angle_` shifted right
> by 24 bits (`src/isp_bldc_motor.spin2`, the `.noFault` block), so **256 units make one electrical
> cycle**, and the design document states the same conversion and works it out:
> *"At the 6.5in ceiling of 172,000,000 it advances `angle_` by 10.25 units per drive pass. At 75 %
> (110,250,000) it advances 6.57 units"* (`plans/CURRENT-LIMIT-AND-STOP-DESIGN.md`, Units). At the
> ladder's own top rung, 165,000,000, the advance is **9.8 units**, not 15-16.
>
> ⛔ **And the measurement refutes the model outright: part A (a ladder to 165,000,000) and part D (a
> steady power 50, where the advance is a fraction of that) BOTH read 115.** A bound generated from the
> per-pass advance would differ by several units between those two parts. It does not. **So the gap
> between `LAG_HOLD` 100 and the observed 115-116 is UNDETERMINED** -- that is a deliverable, not a gap
> (doctrine overlay P8), and it is recorded here rather than filled with a mechanism.
>
> The design's own invariant is written the same way and is equally not what is observed:
> *"`|err_|` cannot exceed `LAG_HOLD` plus one pass's increment (100 + 10.25 < 125)"* (section 3.2). The
> **conclusion** of that sentence holds -- `|err_|` stays under the 125 fault test, in every part, on both
> motors -- and its arithmetic does not generate the 115. Only the conclusion is used.
>
> ### FIXED IN TREE 2026-09-17 -- the bound is the driver's own fault test
>
> `LAG_MAX_HI` is now `LAG_FAULT_TEST - 1` = **124**, with `LAG_FAULT_TEST = 125` named and sourced to the
> driver's `cmp tmpY, #125 wc`. That is the only number here the design actually promises, it is what the
> lag limiter exists to guarantee, and **it has a real negative case**: a driver with no limiter pegs the
> stored field at its 127 saturation and fails it. `LAG_HOLD_REF = 100` is carried alongside, and
> `BM-LAG` now prints `hold` and `fault` beside `max_err` and `hi`, so the whole band is in the record and
> a reading between the gate and the criterion reads as the normal state rather than as a near-miss.
>
> **What is NOT claimed:** that 115 is now explained. It is bounded, and the bound is sourced. If a future
> visit reads a `max_err` that walks toward 124, the record now carries every number needed to see it.

**STEPHEN 2026-09-17, the physical effect:** *"On your dual A run, you're making a bunch of speed changes. One of
the things I noticed in the speed changes is that we are physically slamming the platform... I would think speed
changes should be really smooth, but they're not, so we need to understand what this effect is."*

**MEASURED -- the slam's signature**, `debug_260917-131445.log` L15170-15205, `BM-RUNG2` LEFT forward:

```
rung     0    1    2    3    4    5    6    7    8    9   10   11
err     34   48   48   48   49   48   48   55   63   65   68   73
err_pk  56   75   71   71   72   72   73   80   88   91   94   98
gap     22   27   23   23   23   24   25   25   25   26   26   25
```

**`err_pk` sits ~25 counts above the steady `err` at every rung change, independent of step size.**

**THE MECHANISM, SETTLED FROM THE SOURCE 2026-09-17. It is NOT a missing ramp.** The ramp is applied to every
change of target -- `.doSpdChange` (`src/isp_bldc_motor.spin2:3655`) routes a speed change to `.rampUp`,
`.rampDn` or `.slow2Chg` exactly as a start from rest does. **The defect is the ramp's starting RATE.**
`:3706-3707`, in `.rampUp`:

```spin2
                or      drv_incr, drv_incr          wz  ' -and- are we stopped, just about to spin up?
    if_z        mov     ramp_curr, ramp_min_            ' set initial ramp if starting from 0
```

and `:3715-3718`, the growth:

```spin2
                mov     curr_ramp, ramp_curr            ' current ramp
                add     ramp_curr, ramp_inc_            ' increase ramp for next time
                cmps    ramp_curr, ramp_max_        wc  ' too high?
    if_nc       mov     ramp_curr, ramp_max_            ' Y set to ramp_max
```

**`ramp_curr` is reset to `ramp_min_` only when `drv_incr` is zero -- i.e. only when starting from rest.** On a
speed change from a *running* speed, `drv_incr` is non-zero, so `ramp_curr` is **inherited from the previous
ramp** and keeps accumulating, while a start from rest begins gently at `ramp_min_` (1 500) and grows.

> **CORRECTED 2026-09-17, same day, before this entry was acted on.** A first draft of this entry said the
> inherited value is `ramp_max_`. **It is not, and finding C-2b in the companion study already established
> why:** `ramp_curr` grows by `ramp_inc` = 22 per drive pass from 1 500, and `ramp_max_` = 200 000 is
> unreachable in every shipped configuration. Growth also stops the moment the ramp completes
> (`.endRUpAtSpeed`), so it accumulates only across the *ramping* portion of each rung -- roughly 107 to 618
> passes at Visit 4's measured `steady_ms` of 56-323. Verified in source: `ramp_min := 1_500`,
> `ramp_max := 200_000`, `ramp_inc := 22` (`src/isp_bldc_motor.spin2:526-528`). **The defect and the fix are
> unchanged; the magnitude claim was wrong and is withdrawn.**

**What actually limits the jolt, and it is the cleaner explanation.** The ramp is gated by `LAG_SOFT` = 80
(`:3345`), tested at `:3712`: `cmps lag_s, #LAG_SOFT wc` / `if_nc jmp #.justIncr` -- *the ramp waits for the
rotor this pass*. So on a transition that starts with a large inherited `ramp_curr`, the ramp drives the lag
straight into the `LAG_SOFT` gate and is throttled there.

⭐ **The measurement lands exactly where that predicts, and rung 0 is the control.**

| | `err_pk` | vs `LAG_SOFT` = 80 |
| --- | --- | --- |
| **rung 0** -- the only transition starting from rest, `ramp_curr` = `ramp_min_` = 1 500 | **56** | **below** -- the limiter is never reached, the ramp is never throttled |
| rungs 1-11 -- every transition inheriting an accumulated `ramp_curr` | **71-98** | **at or above** -- the ramp hits the lag gate on every one |

The one rung that gets the soft start is the one that stays under the limiter, and it is the one that does not
slam. Rungs 1-11 each drive the rotor into the lag gate and are held there -- that repeated hit is what is felt
through the platform.

**Fix direction -- correct by construction (P10):** reset `ramp_curr` to `ramp_min_` at the start of **every**
new ramp, not only when `drv_incr` is zero. The soft start then applies to every speed change, acceleration is
continuous at each transition, and `err_pk` should fall toward `err` at rungs 1-11 while rung 0 is unchanged --
a directly measurable prediction for the next visit, with rung 0 as the built-in control.

**Note what this is NOT.** It is not a missing slew-rate limit (the ramp exists), and it is not the lag clamp
(see above -- that half is an instrument bound, and `LAG_HOLD` is doing its job). The two halves of this entry
are two different findings that happened to be found together; **only this half is a driver defect.**

**Status (aged-state sweep 2026-09-17):**
- **First half (the bound): CLOSED.** `LAGBND` PASS on every part at Visit 5 against the driver's own fault test
  (115-116 vs 124).
- **Second half (the slam): fix IN THE BINARY, effect UNMEASURED, and STILL OPEN.** `mov ramp_curr, ramp_min_` at
  `.doSpdChange` (`src/isp_bldc_motor.spin2:3668`) resets the ramp on every new request. STEPHEN at Visit 5:
  *"some are not kicking but many still are... so your remove kicking on ramp up is only partially working."* The
  table above was never a measurement of the slam -- `err`/`err_pk` are steady-window statistics and rung 0 reads
  the same gap as every other rung (PL-87). The transition instrument (PL-87) comes first; then whatever still
  kicks is a driver question with evidence behind it. IN THIS RELEASE.

**Archived 2026-09-27 (Visit 10 pass 7):** CERTIFIED — R21-DUAL-TRKICK-T 16 mV left / 13 mV right against 50 over the seven worst transitions (pre-fix 64–183); the arrival pass now advances the field (DRIVER_REV 34).

### PL-87 -- the ladder's err_pk is a STEADY-WINDOW statistic, so no cell can see a transition kick

> **6.0 status (2026-09-26 audit):** RELEASE — the speed-change kick. Stephen ruled the slam not shippable (2026-09-17); R17-DUAL-TRKICK-A was still FAIL at Visit 8b (183/182 mV) and has not been judged on the current driver.

> **Status 2026-09-22, Visit 8:** `R17-DUAL-TRKICK-A` is still FAIL at 233 / 222 mV on DRIVER_REV 3 (221 / 214
> before). The R18.4 drive change did not move the transition kick, although «#3583» was scoped to subsume it.
> It remains open (Visit 8 evaluation F-8).

> ## BOTH FIXES LANDED 2026-09-20 («#3580» R18.1, dual SRC_REV 21 / FMT 9); run-time proof owed to Visit 7
>
> The box below asked for exactly two things, and both are in the tree:
>
> 1. **`R17-DUAL-TRKICK-A` is re-judged on current.** The criterion is `tr_i_over` -- the transition
>    current peak less the rung's **own** steady `i_max`, a new `BM-RUNGTR` field -- above
>    `TRKICK_EXCESS_MV` (50 sense mV, about a third of an amp at the 150 mV/A the harness aborts on).
>    The from-rest control machinery is **deleted** rather than repointed: an instrument built on a
>    clamped observable is blind whatever control it is given.
>    **The number and its negative case are MEASURED**, from all four ladders of
>    `debug_260919-173751.log`, as `tr_i_pk - i_max` per rung:
>
>    | ladder | 0 | 1 | 2 | 3 | 4 | 5 | 6 | 7 | 8 | 9 | 10 | 11 |
>    |---|---|---|---|---|---|---|---|---|---|---|---|---|
>    | LEFT reverse | -2 | 0 | -2 | -10 | -38 | -66 | **+157** | **+646** | **+401** | **+81** | **+128** | **+128** |
>    | LEFT forward | +1 | +1 | -3 | -7 | -21 | -34 | -76 | **+506** | **+397** | **+91** | **+112** | **+192** |
>    | RIGHT reverse | 0 | 0 | -4 | -22 | -46 | -69 | **+186** | **+677** | **+403** | **+87** | **+110** | -52 |
>    | RIGHT forward | +2 | +1 | -2 | -2 | -10 | -47 | -137 | **+580** | **+412** | **+82** | **+113** | **+214** |
>
>    ⭐ **Below the knee a change of speed costs NOTHING above steady running** -- every reading is at
>    or below zero. At and above it the transition draws two to three times the steady peak. The two
>    populations are separated by a gap running from **-137 to +81 with nothing in it**, so the
>    criterion is not a judgement call. **Visit 6a would have FAILED this cell 11 times of 22 on the
>    LEFT motor and 10 of 22 on the RIGHT** -- against the 0 of 22 that `tr_over` reported.
> 2. **The short ramps are instrumented.** `LIVE` now emits `BM-RUNGTR` and the new `BM-RUNGHL` for
>    every rung. It does **not** fold `TRKICK`: its settle is `LIVE_SETTLE_MS` against the ladder's
>    `LADDER_SETTLE_MS`, so its transition window is a different length, and one verdict over two
>    populations can fail on the mixture rather than on the drive (doctrine D2).
>
> **Also landed with them**, because the same instrument is what Visit 7 reads: `BM-RUNGTR` gains
> `from_incre`, the speed the wheel was holding when the command arrived, so a transition's **delta and
> its direction** come off the record; and the ladder walk gains a **descent** and six **delta cells**
> (a small and a large change of speed at low, at the knee and at the ceiling, each taken up and down).
>
> **What is still owed:** a run. The criterion has never judged a live ladder, and the driver half of
> the kick is **PL-95**'s, fixed in R18.4.

> ## ⛔ THE REPLACEMENT INSTRUMENT IS ALSO BLIND -- and Visit 6a's own log already holds the reading
> that is not. Recorded 2026-09-20.
>
> **STEPHEN 2026-09-20, the observation the run sheet asked for in advance:** *"there we two fwd/rev
> ramps short/long for each motor. in the short ramps they kicked between 2 and 3. in the long ramps
> they kicked at each increment"*.
>
> **`R17-DUAL-TRKICK-A` PASSED with 0 kicks of 22 per wheel. It is a FALSE PASS.** His hand is the
> control, and doctrine D2 puts the suspicion on the measurement.
>
> **MEASURED, `debug_260919-173751.log`, the LEFT reverse ladder, twelve rungs in order** (every ramp
> in the load has the same shape):
>
> | rung | 1 | 2 | 3 | 4 | 5 | 6 | 7 | 8 | 9 | 10 | 11 | 12 |
> |---|---|---|---|---|---|---|---|---|---|---|---|---|
> | `tr_err_pk` | 98 | 76 | 73 | 75 | 75 | 75 | 78 | 85 | 95 | 97 | 102 | 105 |
> | `tr_over` **(what TRKICK judged)** | 36 | 3 | 2 | 4 | 3 | 3 | 1 | 0 | 0 | -1 | 0 | -1 |
> | `tr_i_pk` **(recorded, never judged)** | 19 | 25 | 55 | **234** | **583** | **1197** | **1439** | **1264** | 599 | 200 | 192 | 226 |
>
> ⭐ **The error says nothing and the current says everything.** Across the ramp `tr_err_pk` moves
> within a 73-106 band -- about +-15% -- while `tr_i_pk` rises **seventy-five fold** and peaks at rung 7.
> At the sense calibration the harness uses for its own abort (150 mV/A) rung 7 is **about 9.6 A**, and
> the RIGHT reverse ladder's rung 7 reads 1_522, **above the 1_500 abort threshold** -- it does not
> abort only because the abort wants four consecutive samples and this is a transient.
>
> **DERIVED, and it is the SAME root cause as PL-86, PL-46 and PL-93:** `tr_err_pk` sits in a narrow
> band around 100 because **the lag limiter holds it there** (`LAG_HOLD` = 100). Position error is a
> CLAMPED observable, so any instrument built on it is blind by construction -- which is why the Visit 5
> instrument could not see the kick, and why its replacement cannot either. **Current is not clamped,
> and it was being recorded beside the error the whole time.**
>
> **So the kick is MEASURED, on this visit's data, with no further bench time:** it is real, it is on
> every speed change of the long ramps, it grows with the size of the increment, and it peaks near 10 A.
> That matches his hand exactly, including "at each increment".
>
> **Two fixes, both free of a new run:**
> 1. **Re-judge `TRKICK` on `tr_i_pk`**, not `tr_over`. The criterion becomes a transition current
>    ceiling, or a rise over the from-rest rung, and its negative case is on file in this very table.
> 2. **The short ramps emit no `BM-RUNGTR` at all** -- only LADDER and CLOCK rungs do, so the LIVE
>    segment, where he felt a kick between rungs 2 and 3, has **no transition record**. Instrument it.
>
> ⭐ **AND «#3573»'S DRIVER HALF IS NEEDED.** The plan made it conditional on "if Visit 6a's TRKICK says
> the kick survives". TRKICK said no; the current and his hand both say yes. **The kick survives.**

> ## FIXED IN THE HARNESS 2026-09-18 («#3573», dual SRC_REV 16 / FMT 7); run-time proof owed to Visit 6
>
> - `rungMeasure()` now marks the ring at the drive command, and `transitionStats()` walks [command mark ..
>   window start] -- the ramp and the settle -- for peak |err| and peak |i|. Every LADDER and CLOCK rung prints
>   them in a new record, `BM-RUNGTR` (177 bytes worst case; `BM-RUNG2` had no room at 269), with `tr_over`: the
>   transition peak less the rung's own steady `err_pk`, so the servo ripple common to both cancels.
> - **The control is by state, not index:** `from_rest` is TRUE for the first rung of each motor and sign and for
>   the first rung after a recovered fault. A command whose ring sample was overwritten prints NA
>   (`WHY_RING_LOST_HEAD`), never a partial peak.
> - **New cell `R17-DUAL-TRKICK-A`** (per motor): counts the running-speed changes whose `tr_over` exceeds the
>   control's by more than `TRKICK_MARGIN` (10 err units, ~14 degrees electrical); PASS at 0. The margin is
>   DERIVED; the negative case is Stephen's Visit 5 observation that many transitions still kicked, which this
>   cell must then fail.
> - `BM-RUNG2`'s `err_pk` stays in the record as the steady statistic it is; its comment now says so.
> - **Limit, stated:** the instrument samples at 500 Hz, so a kick shorter than ~2 ms can fall between samples.
>   If the cell passes while a kick is still felt, that is the instrument's limit, not the driver's.

**Found 2026-09-17 at Visit 5**, checking Stephen's observation against the data. **Instrument defect,
mine (P3).** ⛔ **It invalidates the evidence PL-78's second half was built on.**

**STEPHEN 2026-09-17:** *"the ramps from dual-a some are not kicking but many still are... so your
remove kicking on ramp up is only partially working."*

**The driver fix IS in the binary** -- verified in source, `src/isp_bldc_motor.spin2:3668`,
`mov ramp_curr, ramp_min_` at `.doSpdChange`, reached once per request from `.newRqst`.

**MEASURED**, LEFT forward, Visit 5 (`debug_260917-173713.log` L15161-15196) against Visit 4's same
block:

| rung | 0 | 1 | 2 | 3 | 4 | 5 | 6 | 7 | 8 | 9 | 10 | 11 |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| `err` V5 | 33 | 48 | 48 | 48 | 48 | 48 | 48 | 55 | 63 | 66 | 69 | 74 |
| `err_pk` V5 | 57 | 77 | 71 | 72 | 72 | 72 | 72 | 81 | 88 | 91 | 94 | 100 |
| `err_pk` V4 | 56 | 75 | 71 | 71 | 72 | 72 | 73 | 80 | 88 | 91 | 94 | 98 |
| gap V5 | 24 | 29 | 23 | 24 | 24 | 24 | 24 | 26 | 25 | 25 | 25 | 26 |

**Unchanged within 1-2 counts at every rung. PL-78's prediction did not happen.**

⭐ **AND THE REASON IS THAT THIS TABLE WAS NEVER A MEASUREMENT OF THE SLAM.**

- `err` and `err_pk` come from `windowStats()`, over the window `rungWindow()` opens **after** AT_SPEED
  and after the settle. **The transition is over before the window opens.**
- **Rung 0 is the proof.** It is the only rung that starts from rest, so it always had the soft start and
  never had the defect -- and its gap is **24**, the same as every other rung's, at **both** visits. A
  statistic that reads the same on the control and on the suspects is not measuring the difference
  between them (doctrine D2).
- **DERIVED:** the ~25-count gap is the AT_SPEED duty-servo ripple. `CURRENT-LIMIT-AND-STOP-DESIGN.md`
  section 3.2 records the unloaded trace swinging -22 to -70 about a set point of 42 -- a peak about 25
  above the mean, which is exactly what `err_pk - err` reports.

⛔ **So PL-78's second half rests on window statistics read as transition statistics.** Whether the
driver change is right, wrong or partial, **this instrument cannot say, and could not have said at
Visit 4 either.** What Stephen felt with his hands is currently the only evidence about the slam, and it
says the fix helped some transitions and not others.

**Fix direction -- the measurement already exists and costs NO bench time.** `rungMeasure()` arms the
instrument at the command, so the ring **already holds every sample of the transition**; `windowStats()`
simply never reads them. Add a second statistics pass over [arm .. window start] -- the transition --
giving the peak |err| during the ramp, per rung, and print it in `BM-RUNG2` beside the steady pair.
**Rung 0 is the built-in control**, and the next ladder load then measures the slam directly instead of
inferring it.

**IN THIS RELEASE (aged-state sweep 2026-09-17)** -- it gates PL-78's second half, which is a behaviour Stephen
felt and ruled not shippable.

**Archived 2026-09-27 (Visit 10 pass 7):** CERTIFIED — R21-DUAL-TRKICK-T 16 mV left / 13 mV right against 50 over the seven worst transitions (pre-fix 64–183); the arrival pass now advances the field (DRIVER_REV 34).

### PL-143 -- the command timeout watches a drive whose own limit bounds it, so "arm a limit, then drive" is cut short

> **6.0 status (2026-09-26 audit):** RELEASE — Stephen's ruling on the command timeout versus an armed stopAfter* limit.

**Found 2026-09-26** while updating the RC demo («#3624»).
- **DERIVED from the source:** `REQ_DRIVE` marks every non-zero drive as open-ended for the command timeout
  (`isp_steering_2wheel.spin2` ~:2816, `frontWatchCommand()`). That includes a `driveDirection()` or `driveAtPower()`
  after `stopAfterTime()`, `stopAfterRotation()` or `stopAfterDistance()`. Only `driveForDistance()` is exempt, "a
  bounded move" (DRIVE-OBJECTS.md, `setCommandTimeout()`).
- So with `setCommandTimeout()` on, the library's own recommended pattern ("arm the limit BEFORE the drive") stops at
  the timeout unless the program re-sends the drive. Re-sending may itself disturb the armed limit; that is not checked.
- The RC demo's slow one-rotation drive is exactly that pattern. It would be cut after the timeout, so the demo does
  not turn the guard on yet.

**Disposition: question for Stephen** (the API contract is his, D10). Either a drive with an armed platform limit is
bounded and not watched, as `driveForDistance()` is; or it is watched, the doc says so, and a program re-sends it.
Once ruled, the RC demo gains `setCommandTimeout()` as its link-loss guard for wheels-down driving.

**RULED, STEPHEN 2026-09-26:** *"i wouldn't expect carveouts"*, and on my proposal to also change what refreshes the
timeout: *"are you asking me to reshape the mechanism vs, just apply it correctly?"*
- **The build:** the command timeout watches every drive, with no exemptions. `driveForDistance()`'s bounded-move
  exemption (`bCmdWatched := FALSE`, steering `REQ_DRIVE_DISTANCE`) goes, and a drive with a `stopAfter*()` limit
  armed is watched like any other. The refresh is unchanged: a drive command resets the clock.
- **Docs:** `setCommandTimeout()` in DRIVE-OBJECTS.md and DRIVE-OBJECTS-SERIAL.md, and the README line. With the guard
  on, a program running a long move re-sends its drive. Re-sending `driveAtPower()`/`driveDirection()` keeps an armed
  `stopAfter*()` limit (`REQ_DRIVE` disarms only the per-wheel limits `driveForDistance()` sets, steering ~:2822).
  Re-sending `driveForDistance()` restarts its distance.
- **Then the RC demo** enables the guard. It is built in the Pass A batch, and its cell is CMDTIMEOUT extended to a
  bounded move.

**Archived 2026-09-27 (Visit 10 pass 7):** CERTIFIED — CMDTIMEOUT PASS both forms, including a 20 m driveForDistance() left silent (DRIVER_REV 32).

### PL-147 -- the two "following" readings measured against different commands while the path limiter scaled

> **6.0 status (2026-09-26 audit):** AWAITS CERT — fix built, not yet run: pass 7 NOTFOL-D PASS.

**Found 2026-09-26** at Visit 10 pass 6 (evaluation §5).
- **MEASURED:** R18-DUAL-NOTFOL-D LEFT FAIL: `BM-HOLD,...,LEFT,...,short_permille,84,short_pct,105`.
- The limiter's fraction (`shortfallNow()`) is taken against `userCmdIncr`, the user's command.
- The rpm window's percentage (`updateFollowing()`, `testGetFollowing()`) was taken against `targetIncre`, which a
  path scale rewrites. So a wheel scaled to 8 % "followed" at 105 % of the scaled command, while the other reading
  said 84 ‰ of the user's.
- One value, two meanings (D7).
- The cell was right to fail. A-8 requires the two readings to agree.

**Disposition: ⛔ FIX, built** (DRIVER_REV 30, `isp_bldc_motor.spin2`). The percentage is now of `userCmdIncr`.
`targetIncre` still gates validity, so a stopped or e-stopped wheel (driver command zeroed, user command kept) is not
reported as not following. Test-use observable; no PASM or ABI change. Certifies at pass 7 (NOTFOL-D PASS on a
behind wheel).

**Archived 2026-09-27 (Visit 10 pass 7):** CERTIFIED — NOTFOL-D LEFT PASS, short_permille 77 / short_pct 9.

### PL-151 -- four 6.0 API behaviours were last certified on the pre-R18.4 driver, or never

> **6.0 status (2026-09-26 audit):** RELEASE — each is a README claim with stale or no evidence.

**Found 2026-09-26** by the release audit.
- `driveForDistance(left, right)` turns: R17-DUAL-TURNDIST-B PASS at Visit 6a, on the pre-R18.4 driver. Part B has not
  run since.
- `getFaultCause()`: R17-DUAL-FLTCAUSE-B NOMEAS at Visit 6a, and no later PASS. A cause is only seen in passing (`cause,LAG`).
- `getStatus()` reporting `DS_ESTOP`: no cell was found that reads it.
- `stopAfterRotation()`: no cell was found.

**Disposition: ⛔ release work.** One regression tier on the current driver covers all four:
- part B's TURNDIST;
- a FLTCAUSE cell provoked with `testForceFault()` (PL-119), which also lets PL-66's FLTRETRY certify;
- a `getStatus()` read after an e-stop;
- a `stopAfterRotation()` leg in T0.

It should be built in the pointed form that PL-152 describes.

**Archived 2026-09-27 (Visit 10 pass 7):** CERTIFIED — dual-reg TURNDIST (1 tick), FLTCAUSE (LAG / NONE), T0 ROTSTOP and ESTOPSTATUS.

### PL-152 -- every bench tier compiles twice, and carries every harness part ever written

> **6.0 status (2026-09-26 audit):** RELEASE (support) — makes every remaining pass cheaper; changes nothing measured.

**Found 2026-09-26** from Stephen's observation: *"The script is now compiling files twice... Your files are large
enough that they take a really long time to compile... our bench run tests should not be an accumulation of all the
tests we've ever run. They should be fairly pointed."*
- **MEASURED (dev container):** `tools/bench-run.sh` compiles each tier plain and then with `-d` to measure the DEBUG
  footprint from the size difference. A `test_bench_dual` compile takes about 13 s, so each dual tier spends about 26 s
  compiling. The commit gate already measures the same footprint for every tier, on the tree the bench pulls.
- **MEASURED:** the dual harness (22,062 lines, 15 parts) compiles all parts into every tier. Pass 6's START,
  swapneg and D images were all 152,139 B. The driver and steering objects alone compile in about 4 s, so the
  harness is about 70 % of the compile.

**Disposition: ⛔ FIX, after pass 7** (so the pass on the bench is not disturbed):
1. The bench compiles once, with `-d`. The footprint stays enforced by the commit gate.
2. Each `test_bench_dual` part goes behind its own compile flag, so a tier builds only its part and the shared plumbing.
   Every tier's banner and cells are re-checked, and the images are measured before and after.

**Archived 2026-09-27 (Visit 10 pass 7):** CERTIFIED — every dual tier ran from its own one-part image, one compile at the bench.

### PL-153 -- the odometer resets itself, and the distance limits count from the odometer instead of from where they were armed

> **6.0 status (2026-09-26 audit):** RELEASE — ruled by Stephen from the public-API audit (API-1, API-5).

**Found 2026-09-26** by the public-API usability audit («#3613» session; read-only survey, verified in source).
- **API-1 (VERIFIED):** the motor object's `driveForDistance()`, `stopAfterDistance()` and both objects'
  `stopAfterRotation()` compare the limit against `posTrkHallTicks`, the odometer since the last reset
  (`isp_bldc_motor.spin2` ~:3059), and arming does not reset it (motor `REQ_DRIVE_DISTANCE` ~:5157, `REQ_LIMIT_TICKS`;
  steering `stopAfterRotation` posts no reset ~:645). A second `driveForDistance(1, DDU_FT)` stops at once.
- **API-5:** the odometer is zeroed silently while a motor is FAULTED or e-stopped (`frontResetTracking` every pass,
  ~:2990) and by the steering object's distance moves (~:2830, :2863). `getDistance()` after an e-stop reads 0.

**STEPHEN 2026-09-26:** *"I would think odometer is distance traveled... if you backed up, you also moved distance...
it's total amount traveled."* So the odometer stays unsigned total travel and resets only on `resetTracking()`.
Each distance or rotation limit counts the travel from the point where it was armed.

**Disposition: ⛔ build.** Separate the odometer from the limit base. Remove the silent resets. Change the
`resetTracking()` docs ("use current position as home") to say it resets the odometer. A T0 cell: two back-to-back
`driveForDistance()` moves each travel their distance; an e-stop leaves `getDistance()` unchanged.

**Archived 2026-09-27 (Visit 10 pass 7):** CERTIFIED — R20-T0-ODOMETER (two 52-tick moves 53 and 53; odometer 106 unchanged across an e-stop).

### PL-155 -- settings a user makes are lost on start() without saying so, and several have no getter

> **6.0 status (2026-09-26 audit):** RELEASE — the same class as the acceleration finding (API-4).

**Found 2026-09-26** by the public-API audit. `init()` resets `setMaxSpeed` (~:3869), `setMaxSpeedForDistance`
(~:3870), `holdAtStop` (~:3844) and `forwardIsReverse` (~:3858) on every `start()`. Their docs do not say so, and they
return NO_ERROR before start. There is no `holdAtStop` getter, `forwardIsReverse` has no undo or getter, and neither
object has `getCommandTimeout()`.

**Disposition: ⛔ build.** It goes with the acceleration/deceleration persistence (the kick spec). User settings live
outside `init()`'s reset and are applied at every start. Each gets a getter, `forwardIsReverse` takes an enable, and
the steering and serial mirrors follow.

**Archived 2026-09-27 (Visit 10 pass 7):** CERTIFIED — R20-T0-PERSIST and R20-T0-API-PERSIST.

### PL-156 -- there is no "move finished" test, and the demos' wait loop hangs on a fault or e-stop

> **6.0 status (2026-09-26 audit):** RELEASE — users copy the demos (API-7).

**Found 2026-09-26** by the public-API audit. `isStopped()` is DCS_STOPPED only. The demos' `waitUntilMotorDone()`
(`demo_dual_motor.spin2` ~:297-315, `demo_single_motor.spin2` ~:285-296) loops unbounded on `isStarting()`, then on
`isStopped()`. It hangs when a fault or e-stop ends a move, or when a 2 ms poll misses SPIN_UP.

**Disposition: ⛔ build.** A predicate true once the motor is not moving under a command (stopped, faulted, e-stopped
or protectively stopped). The demos wait on it with a bound and report `getStopReason()`.

**Archived 2026-09-27 (Visit 10 pass 7):** CERTIFIED — R20-T0-MOVEDONE.

### PL-158 -- getStatus() says HOLDING after the hold has handed off, and rotation limits and counts truncate

> **6.0 status (2026-09-26 audit):** RELEASE — ruled in (API-11, API-12).

**Found 2026-09-26** by the public-API audit.
- **API-11:** `getStatus()` reports DS_HOLDING whenever the stop mode is brake and the motor is stopped (~:1634-1638).
  That includes a hold that has handed off to the short, and a post-fault brake.
- **API-12:** DRU_DEGREES limits truncate (90° becomes 88°, ~:740), and `getRotationCount(DRU_ROTATIONS)` is an
  integer divide (~:1190).

**Disposition: ⛔ build.** DS_HOLDING follows the hold's own state. Limits round to the nearest tick. The integer
resolution of each getter is documented.

**Archived 2026-09-27 (Visit 10 pass 7):** CERTIFIED — R20-T0-API families (status and rounding checks) 0 bad.

### PL-159 -- documentation the API audit found wrong or missing

> **6.0 status (2026-09-26 audit):** RELEASE — the doc-only items, ruled in.

**Found 2026-09-26** by the public-API audit.
- **API-14:** `calibrate()` is public and returns NO_ERROR while doing nothing.
- **API-15:** `getCurrent()` returns `fAmps`, an integer in 0.1 mA, named like a float.
- **API-6, STEPHEN 2026-09-26 "B":** `driveForDistance()` stays forward-only. The docs teach backing up as
  `driveAtPower(-power)` then `stopAfterDistance()`, and state that the two calls are not one atomic move.
- The serial doc gaps listed in PL-154.

**Disposition: ⛔ build (docs).** `calibrate()` states plainly that it does nothing and returns an error code (the API
is kept). The `fAmps` result is renamed in the doc and the source comment. The backing-up pattern goes in
DRIVE-OBJECTS.md and DEVELOP.md.

**Archived 2026-09-27 (Visit 10 pass 7):** CERTIFIED — R20-T0-API-CALIBRATE (-1_021 both objects); docs in place.

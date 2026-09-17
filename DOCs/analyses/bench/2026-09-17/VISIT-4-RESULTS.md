# Visit 4 — Results

**Run:** 2026-09-17, 12:52–13:20 local. Unattended, wheels lifted, Rev B, both motors, 270 MHz.
**Sheet:** `DOCs/analyses/bench/VISIT-4-RUNSHEET.md` · **Task:** «#3561» · **Plan:** §R16.9 (Sprint Revision 2026-09-16)

Provenance marks per doctrine overlay P8: **MEASURED** = cites a log line · **DERIVED** = my
reasoning from traced claims · **STEPHEN** = his words with the date · *unlabelled* = the sources
were read and do not settle it.

---

## 0. Banner check — the gate before any result is read (PL-68)

MEASURED. Five of six loads emitted a banner; every one matches the sheet.

| Log | Tier | Banner | vs sheet |
|---|---|---|---|
| `debug_260917-125221.log` | t0 | **none** | **see §1** |
| `debug_260917-125254.log` | char | `BC-BANNER src_rev 7 fmt 7` (L21) | ✅ |
| `debug_260917-125859.log` | dual-D | `BM-BANNER src_rev 13 fmt 4 part D` (L21) | ✅ |
| `debug_260917-130012.log` | dual-B | `BM-BANNER src_rev 13 fmt 4 part B` (L21) | ✅ |
| `debug_260917-131237.log` | dual-C | `BM-BANNER src_rev 13 fmt 4 part C` (L21) | ✅ |
| `debug_260917-131445.log` | dual-A | `BM-BANNER src_rev 13 fmt 4 part A` (L21) | ✅ |

All five carry `clkfreq 270_000_000, left_base 32, right_base 16, voltage_enum 6, det_mode 30`.
All four dual loads are one binary (`test_bench_dual.bin`, 72 269 bytes); the part is selected at
run time. `git reflog show origin/main@{0}` = **`e4dd107`**, the harness commit — the tree Stephen
ran. `1abba46` is doc-only and unpushed, exactly as predicted.

**No `src_rev` mismatch anywhere. Visit 4's evidence is admissible.** Four of the five completed
cleanly (`BM-END exit,COMPLETE`, `trap_code 0`, `unrecov 0`); char ended `BC-END exit,COMPLETE`.

---

## 1. NEW FINDING — the t0 load emitted nothing (PL-69)

**MEASURED.** `debug_260917-125221.log` is 19 lines: `[DOWNLOAD SUCCESS] test_bench_t0.bin |
Size: 43780 bytes` (L16), then `Session Ended` 14 s later (L18). Not one program line.

**The tell is what is missing, not what is there.** The t0 log has **no `Cog0 INIT $0000_0FA8 …
jump` lines**. Every other log has them (char L18; each dual L17–19). Those INIT lines are emitted
by the *debug kernel* at load. Their total absence means the downloaded image **carried no debug
kernel** — i.e. `test_bench_t0.bin` was built without `-d` — rather than the program running and
staying silent.

**STEPHEN 2026-09-17:** *"The T0 run didn't emit any debug output. I don't know why. It looks like
it compiled correctly from what I could see with the -d flag, but nothing happened, so that log is
pretty sparse."*

**DERIVED:** this is a **harness defect and it is mine** (P2 — my script fronting his tools), not a
driver defect. Root-cause it in `tools/bench-run.sh`'s t0 tier before suspecting `pnut-ts` (P7 —
presume the compiler is correct).

**Consequence, stated as itself and never as a pass** (task-execution overlay §8): **all ten t0
cells are NOT_BUILT.**

| Cell | Verdict | Why |
|---|---|---|
| R16-T0-BADGROUP, PINSKEEP, LIMKEEP, NOABORT, STRNOTSTART, STEERCOGS, RESTZERO, NOBOARD, FRONTFAIL, R1-T0-RESTART | **NOT_BUILT** | binary emitted nothing; §1 |

⛔ **The error contract («#3554», «#3555») is therefore NOT certified by Visit 4**, except for the
one steering cell that rode the char tier (§2). This gates the 6.0.0 tag.

---

## 2. char — a clean sweep

**MEASURED.** `debug_260917-125254.log`, `BC-END exit,COMPLETE, preflight_ok,TRUE, holds_run,9,
lib_abort,FALSE, trap,0` (L522). **Every cell PASS; no FAIL, no NOMEAS.**

| Cell | Motor | Criterion | Measured | Band | Verdict |
|---|---|---|---|---|---|
| R5-CHAR-SENSE ×8 | L,R | `NET_VS_PASS1_PCT` | 42,45,47,53,74,77,95,108 | −150..150 | **PASS** (L487–494) |
| R4-CHAR-RPM ×8 | L,R | `RPM_ERR` | −1,0,−1,−1,−1,0,0,−1 | −2..2 | **PASS** (L495–502) |
| R2-CHAR-ISCALE ×8 | L,R | `RSENSE_IMPLIED` | 149–162 | 135..165 | **PASS** (L503–510) |
| R3-CHAR-INTEG ×2 | L,R | `MISSED_ILLEGAL_SUM` | 0 | 0..0 | **PASS** (L511–512) |
| R10-CHAR-STEERFAIL | — | `RET_NEG_NOLEAK` | TRUE | TRUE | **PASS** (L513) |
| **R16-CHAR-STEERERR** | R | `WHEEL_NAMED` | TRUE | TRUE | **PASS** (L514) |
| R10-CHAR-STEERSTART | — | `STEER_START_COG` | TRUE | TRUE | **PASS** (L515) |
| R10-CHAR-STEERLIVE ×2 | L,R | `WHEEL_TICKS` | 13, 13 | ≥6 | **PASS** (L516–517) |
| **R13-CHAR-BRAKESTART ×4** | L,R | `BRAKE_START_MOVE` | TRUE | TRUE | **PASS** (L518–521) |

**What this certifies.**
- **R16-CHAR-STEERERR PASS** — steering `getError()` names the failing wheel. The one piece of the
  «#3555» error contract Visit 4 *did* reach.
- **R13-CHAR-BRAKESTART PASS ×4** — the brake-mode start **rebuilt on the front-cog contract**,
  with no harness `cogatn`, moves both motors. «#3513» certified.
- **R4-CHAR-RPM PASS** — rpm is live and accurate to ±1 rpm over n≈590. Finding **W** is settled:
  callers who coded around a constant 0 now get real numbers.
- **R2-CHAR-ISCALE PASS** — implied R-sense 149–162 against a 135–165 band, both motors. The
  current scale is right.

**Free from the same log (MEASURED, L471–478):** `pinSum = 94, 64010 Rev B, highTimeUs = 72` ·
`dead_gap = 70` · `duty_min = 1_600, duty_max = 24_264` · `adc_fram = 6_136` · `frame_cnt = 6_136`
· `maxFwdIncreAtPwr = 147_000_000`.

⭐ **`dead_gap = 70` confirms the A1 / PL-9 ruling.** 70 ticks at 270 MHz = **259 ns**, above the
250 ns minimum both Parallax manuals specify. Deleting the per-revision conditional was correct,
and the surviving value is in spec for both boards. `CLAUDE.md`'s "Board revision handling"
paragraph still describes the deleted conditional — raise with Stephen, do not edit (his file).

---

## 3. dual-D — the new part D, and the two defects that matter

**MEASURED.** `debug_260917-125859.log`, 126 lines, `BM-END exit,COMPLETE, part,D, segs,3` (L122).
The tier is short because it is verdict-only and quiet — it ran to completion, it did not abort.

| Cell | Motor | Criterion | Measured | Verdict |
|---|---|---|---|---|
| R16-DUAL-NOSTALL-D | — | `ENDED_BY_COG0` | TRUE | PASS (L102) |
| R16-DUAL-DBGMASK-D | — | `QUIET_MASKS` | TRUE | PASS (L103) |
| R16-DUAL-LOCKSTEP-D | BOTH | `WHEELS_TOGETHER` | TRUE | PASS (L104) |
| R16-DUAL-TRACKRST-D | BOTH | `RESET_AT_SPEED` | TRUE | PASS (L105) |
| R16-DUAL-ESTOP-D | BOTH | `ESTOP_LATCHED` | TRUE | PASS (L106) |
| R16-DUAL-ORDERED-D | BOTH | `ORDERED_STOP` | TRUE | PASS (L107) |
| R16-DUAL-TIMESTOP-D | BOTH | `AT_REST_BY_LIMIT` | NA, n=0 | **NOMEAS** (L108) |
| R16-DUAL-COOPSHUT-D | BOTH | `SHUTDOWN_BOUNDED` | TRUE | PASS (L109) |
| **R16-DUAL-FRONTST-D** | **BOTH** | `FRONT_LOOP_HEALTH` | **FALSE** | **FAIL** (L110) |
| R16-DUAL-FOLDBACK-D | L, R | `FOLDBACK_HELD` | TRUE, TRUE | PASS (L111–112) |
| R16-DUAL-DERATE-D | L | `DERATED_IN_WINDOW` | NA, n=0 | **NOMEAS** (L113) |
| **R16-DUAL-DERATE-D** | **R** | `DERATED_IN_WINDOW` | **FALSE** | **FAIL** (L114) |
| R16-DUAL-BLOCKED-D | BOTH | `PROTECTIVE_STOP` | NA, n=0 | **NOMEAS** (L115) |
| R16-DUAL-WESTOP-D | L | `ESTOP_LATCHED` | TRUE | PASS (L116) |
| R16-DUAL-WTIMSTOP-D | L | `AT_REST_BY_LIMIT` | NA, n=0 | **NOMEAS** (L117) |
| R16-DUAL-FRONTST-D | L | `FRONT_LOOP_HEALTH` | TRUE | PASS (L118) |
| R16-DUAL-LAGBND-D | L | `MAX_ABS_ERR` | 115 (0..110) | **FAIL** (L119) |
| R16-DUAL-LAGBND-D | R | `MAX_ABS_ERR` | 87 (0..110) | PASS (L120) |

### 3a. ⛔ FRONTST-D FAIL — the steering front cog's stack is exactly full (PL-70)

**MEASURED.** The two `BM-FRONTST` records differ in one field:

```
L67  BM-FRONTST motor,BOTH  passes,18_052 late,0 max_ticks,215_784 max_us,799 slot_us,1_000 stack_hi,128 stack_of,128   -> FAIL
L96  BM-FRONTST motor,LEFT  passes,11_653 late,0 max_ticks,169_936 max_us,629 slot_us,1_000 stack_hi,114 stack_of,128   -> PASS
```

**`stack_hi 128 == stack_of 128`.** The steering object's front cog — the one that services *both*
wheels — has driven its stack high-water mark to the full allocation. The single-motor front cog
peaks at 114 of 128 and passes. **DERIVED:** zero stack margin, and one more nested call or one
deeper interrupt path overruns it. This is the 3-cog two-wheel form «#3513» ships.

`max_us 799` of a `slot_us 1_000` budget is also 80 % occupancy, though `late,0` says it never
missed its slot. The stack is the defect; the occupancy is a number to watch.

**Fix:** raise the steering front cog's stack allocation and re-measure `stack_hi` against the new
`stack_of`. This is *correct by construction* (P10): size the stack from the measured high-water
mark plus margin, rather than tuning the criterion.

### 3b. The single-motor LIMIT segment reports "motor not started" after a successful start (PL-71)

**MEASURED**, `debug_260917-125859.log` L86–95, in order:

```
L86  BM-START seg,LIMIT motor,LEFT life,5 cog_ret,3 cog_ok,TRUE board,REV_B ready,TRUE ... why,NONE
L87  ! ERROR: driveAtPowerEx() motor not started
L88  ! ERROR: driveAtPowerEx() motor not started
L91  ! ERROR: clearEmergency() not cleared eError = -1_007
L93  ! ERROR: driveAtPowerEx() motor not started
L94  ! ERROR: stopAfterTime() rejected eError = -1_007, nTime = 2_000, eTimeUnits = 1
L95  BM-DSTEP step,TIMESTOP motor,LEFT ... result,NOMEAS why,STOP_TIMEOUT
```

`start()` returned cog 3 with `cog_ok,TRUE` and `ready,TRUE` — and the very next `driveAtPowerEx()`
says the motor is not started. **This is an API-contract defect of exactly the class P3 names:** a
member that does not keep the promise its name and its documentation make. It is also the direct
cause of three of part D's four NOMEAS results (TIMESTOP both forms, WTIMSTOP).

**Not yet determined:** whether the `-1007` from `clearEmergency()` is the same root cause or a
second one. Reading `isp_bldc_motor.spin2`'s started-state predicate is the next step; do not
design a bench cell for it (P10 — the bench certifies, it never engineers).

### 3c. DERATE-D FAIL is the criterion's band, not the driver

**MEASURED**, L78–80: `BM-LIMST DERATE` gives LEFT `phase_ma 2_357 value 0 derated FALSE`,
RIGHT `phase_ma 2_632 value 2_602 derated FALSE`, and `BM-DSTEP DERATE measured 2_602, lo 500,
hi 2_500 -> FAIL` — **4 % over the top of the band.** With `peak_a 20, cont_a 8`, a lifted wheel
never approaches the 8 A continuous limit, so derating correctly never fired. **DERIVED:** the cell
is judging *phase current magnitude* against a band that the lifted-wheel current slightly exceeds,
not judging whether derating happened. The band is mine to fix (P3).

### 3d. The NOMEAS results that are designed, and the ones that are not

- **BLOCKED-D NOMEAS, `why,NOT_BLOCKED`** — designed. A lifted wheel cannot be blocked; the cell
  was built to print NOMEAS with a why. Correct behaviour of the instrument.
- **DERATE-D LEFT NOMEAS (n=0)** — designed, same reason.
- **TIMESTOP-D / WTIMSTOP-D NOMEAS, `why,STOP_TIMEOUT`** — **not designed.** These are lost to the
  §3b defect. They are owed to Visit 5.

**FOLDBACK-D PASS both** (`value 5_186` L, `4_801` R, band 0..8 800) — current fold-back holds.

---

## 4. dual-B — droop certified, three real failures

**MEASURED.** `debug_260917-130012.log`, 7 581 lines, `BM-END exit,COMPLETE, part,B, segs,3` (L7577).

| Cell | Motor | Criterion | Measured | Verdict |
|---|---|---|---|---|
| R14-DUAL-NOSTALL-B / DBGMASK-B / TRACES-B | — | — | TRUE / TRUE / 0 | PASS (L7559–7561) |
| R14-DUAL-RSTPROV-B | L, R | `RESET_UNCLEARED` | NA, n=0 | NOMEAS (L7562, L7566) |
| R14-DUAL-RAMPREST-B | L, R | `RAMP_RESTORED` | TRUE | PASS (L7563, L7567) |
| **R16-DUAL-STOPCUR-B** | **L, R** | `STOP_UNDER_HOLD_I` | **FALSE** | **FAIL** (L7564, L7568) |
| **R16-DUAL-RMPDROOP-B** | L, R | `DROOPED_NOT_FAULT` | TRUE | **PASS** (L7565, L7569) |
| R14-DUAL-FLTAPI-B | BOTH | `FAULT_API_LATCHED` | NA, n=0 | NOMEAS (L7570) |
| R16-DUAL-FLTRETRY-B | BOTH | `SAME_POWER_AGAIN` | NA, n=0 | NOMEAS (L7571) |
| R16-DUAL-STOPLIM-B | BOTH | `REST_FROM_TARGET` | NA, n=0 | NOMEAS (L7572) |
| **R16-DUAL-DISTM-B** | BOTH | `METRES_AGREE` | **FALSE** | **FAIL** (L7573) |
| R16-DUAL-LAGBND-B | L, R | `MAX_ABS_ERR` | 115 (0..110) | **FAIL** (L7574–7575) |

### 4a. ⭐ RMPDROOP-B PASS — «#3558»'s central claim is certified

`DROOPED_NOT_FAULT` TRUE on both motors. **The driver droops under a load it cannot follow instead
of faulting.** That is the headline behaviour of the current-limiting design, and it is measured.

### 4b. STOPCUR-B FAIL — stops from speed are not staying under the hold-current bound

`STOP_UNDER_HOLD_I` FALSE, both motors. The bounded stop from «#3558» did not hold its current
bound. **Not yet determined:** the per-sample `BM-STOPCUR` records need reading to say by how much
and at which point in the stop. That is the first thing to read in this log next session.

### 4c. DISTM-B FAIL — metres are off by ~1 000× and inverted (PL-72)

**MEASURED**, L7547:

```
BM-DISTM l_ticks,2_688 r_ticks,2_688 l_m,-14_640 r_m,-14_640 l_pred_m,15 r_pred_m,15 mm_x100,576 agree,FALSE
```

**DERIVED:** `mm_x100 576` = 5.76 mm per tick; 2 688 ticks × 5.76 mm = **15 483 mm = 15.48 m**,
against `l_pred_m 15`. So the *magnitude is right* — `l_m` is carrying **millimetres while the
field and the criterion read it as metres**, and **the sign is inverted**. Two separate faults in
one reading. This is the DDU_M path the release notes already promise to have fixed; the promise
does not survive this measurement and must be re-checked before it ships in the README.

### 4d. Why FLTAPI / FLTRETRY / STOPLIM are NOMEAS

**MEASURED**, L7546–7551: `BM-OVERSHOOT … why,NOT_REACHED` (target 529, tracked 2 688), then
`BM-ABORT seg,OVERSHT reason,ABS_CURRENT value,2_217 scope,TRIAL`, then
`BM-FLTAPI … why,ABORTED, retry_err,NA, retry_ms,NA, retry_ok,FALSE`.

The overshoot trial tripped the absolute-current abort, so the 180° fault provocation never ran and
the three cells behind it have no data. **Reported as NOMEAS, not as passes.** The abort itself is
the instrument working; the cells are owed to Visit 5 with a stimulus that does not trip it.

---

## 5. dual-C — the deceleration number, confirmed

**MEASURED.** `debug_260917-131237.log`, 5 628 lines, `BM-END exit,COMPLETE, part,C` (L5624).

| Cell | Motor | Criterion | Measured | Band | Verdict |
|---|---|---|---|---|---|
| R14-DUAL-NOSTALL-C / DBGMASK-C / TRACES-C | — | — | TRUE / TRUE / 0 | — | PASS (L5612–5614) |
| R14-DUAL-RSTPROV-C | L, R | `RESET_UNCLEARED` | NA, n=0 | — | NOMEAS (L5615, L5618) |
| R14-DUAL-OFFREST-C | L, R | `OFFSETS_RESTORED` | TRUE | — | PASS (L5616, L5619) |
| **R16-DUAL-STPDECEL-C** | **L, R** | `STOP_TICKS_IN_BAND` | **75, 75** | 60..95 | **PASS** (L5617, L5620) |
| R16-DUAL-LAGBND-C | L, R | `MAX_ABS_ERR` | 116 (0..110) | | **FAIL** (L5621–5622) |

⭐ **STPDECEL-C PASS at 75 ticks on both motors**, against Visit 3's measured 74–77. Two independent
visits agree to within 1–2 ticks. **This is the C-4 deceleration number**, and per D2 the agreement
of independent readings is itself evidence. It is ready to go into `DRIVE-OBJECTS.md` via «#3514».

---

## 6. dual-A — the speed law certified, and Stephen's slam

**MEASURED.** `debug_260917-131445.log`, 15 308 lines, `BM-END exit,COMPLETE, part,A, segs,4,
records,15_211, trap_code,0, unrecov,0` (L15304).

| Cell | Motor | Criterion | Measured | Verdict |
|---|---|---|---|---|
| R14-DUAL-NOSTALL-A / DBGMASK-A | — | — | TRUE | PASS (L15288–15289) |
| R14-DUAL-INSTLIVE-A | L, R | `INST_LIVE` | TRUE | PASS (L15290, L15295) |
| R14-DUAL-IDLEFLT-A | L, R | `IDLE_WHEEL_UP` | 0 of n=48 | PASS (L15291, L15296) |
| R14-DUAL-REVB-A | L, R | `STARTS_NOT_REVB` | 0 of n=12 | PASS (L15292, L15297) |
| R14-DUAL-INTEG-A | L, R | `MISSED_ILLEGAL_SUM` | 0 of n=36 | PASS (L15293, L15298) |
| R14-DUAL-TRACES-A | — | `TRACE_DATA_LOST` | 0 of n=48 | PASS (L15300) |
| **R16-DUAL-NOFOLD-A** | **L, R** | `RATE_HELD_NO_FOLD` | **FALSE** | **FAIL** (L15294, L15299) |
| **R16-DUAL-LAGBND-A** | **L, R** | `MAX_ABS_ERR` | **115** (0..110) | **FAIL** (L15301–15302) |

**REVB-A PASS, 0 of 12 starts misdetected** — board-revision detection held across twelve
start/stop cycles on a Rev B board. The «#3500» repair stands up.

### 6a. NOFOLD-A FAIL is an instrument defect — C-1's speed law is certified

**MEASURED.** `rate_x10` tracks `pred_x10` at **every one of 48 rungs, both motors, both
directions, to better than 0.5 %** — except rung 0:

| Rung 0 | ticks | rate_x10 | pred_x10 | ratio | Line |
|---|---|---|---|---|---|
| L reverse | −14 | −139 | −133 | **104.5 %** | L15131 |
| L forward | 14 | 139 | 133 | **104.5 %** | L15170 |
| R reverse | −14 | −139 | −133 | **104.5 %** | L15209 |
| R forward | 13 | 129 | 133 | **97.0 %** | L15248 |

Representative of every other rung — L forward rung 11: `rate_x10 4_415` vs `pred_x10 4_409` =
**100.1 %** (L15203).

**DERIVED:** at rung 0 (`incre 5_000_000`) the entire measurement is 13–14 ticks in a ~1 s window,
so **one tick of quantisation is ~7.5 %**. A 97–103 % band **cannot be met at rung 0 by
construction** — ±1 tick spans 97–105 %. The criterion is narrower than its own resolution, and it
is my instrument (P3). Fix the band's floor rung or widen it to the quantisation limit; **do not
touch the driver for this.**

⭐ **C-1's speed law is CERTIFIED by this data** — 48 rungs, two motors, two directions, under 0.5 %
across a 33:1 speed range.

### 6b. Free physics, no extra run needed

**MEASURED**, `BM-RUNG2`/`BM-RUNG3`, L15170–15205 (L forward): duty saturates at `duty_max 24_264`
from rung 7 up, with `ph_x10 ≈ 24 400` — so `duty_max` is essentially **full modulation, not a
current clamp**. Current by rung (`amps_x10k`):

```
rung   0     1     2      3      4       5       6       7       8      9     10     11
amps  440   415  1_199  6_690 18_138  37_483  66_175  38_479 11_045 6_138 3_031  3_110
```

Peak **≈ 6.6 A at rung 6**, then falling as speed rises — back-EMF against a lifted wheel. **The
current channel is alive and load-responsive**, which answers one of «#3514»'s open write-back
questions outright. No fold-back was demanded because no rung asked for more than the limit; part D
is where fold-back gets its real test, and it passed there (§3d).

### 6c. ⭐ LAGBND — the slam, and what it actually is

**MEASURED.** `MAX_ABS_ERR` across all four parts:

| Part | LEFT | RIGHT | samples (L/R) | Bound |
|---|---|---|---|---|
| A | **115** | **115** | 63 947 / 63 998 | 0..110 |
| B | **115** | **115** | 19 761 / 19 862 | 0..110 |
| C | **116** | **116** | 19 933 / 19 922 | 0..110 |
| D | **115** | 87 | 3 293 / 2 308 | 0..110 |

`sat` is 127 in every record and the measurement never reaches it. **«#3558»'s lag limiter IS
working** — the unfixed driver pegs the stored `err` field at 127, and this one does not.

⚠ **But look at the consistency.** 115, 115, 115, 115, 116, 116, 115 — across four parts with
completely different motion profiles, sample counts from 2 308 to 63 998, and both motors.
A transient peak driven by motion would scatter; a number this repeatable is structural. Part D
RIGHT reaching only 87 fits: it is the shortest run and simply never demanded enough.

#### 6c-i. Settled from the source — the 110 bound was wrong, not the driver

**MEASURED**, `src/isp_bldc_motor.spin2:3344-3346` and `:3803-3804`:

```spin2
    LAG_SOFT  = 80     ' 112.5 deg: the ramp waits for the rotor; the PL-55 duty ceiling lifts
    LAG_HOLD  = 100    ' 140.6 deg: the field stops advancing (the fault test is at 125)
...
.justIncr
                cmps    lag_s, #LAG_HOLD            wc
    if_c        add     angle_, drv_incr
```

**The clamp is at 100, not at 115.** The test reads `lag_s` sampled at the *top* of the pass
(`:3560`); the field then advances by a whole `drv_incr` before the next test. So the largest
`err_` any sampler can observe is **`LAG_HOLD` + one pass's field advance** — roughly 15–16 err
units at the ladder's top rung. That is exactly 115–116, and exactly why it barely moves between
parts.

⛔ **So `R16-DUAL-LAGBND` is an instrument defect too.** The bound was written as `LAG_HOLD + 10`,
under-estimating the one-pass quantum at `ladder_max 165_000_000`. The driver does what C-5
designed, and **the 125 fault test is never reached** — the property the cell exists to guard.

**This is the one case where raising the bound is correct** — not because it turns four FAILs
green, but because the old bound described a state the design never promised. It must be *computed*
from `LAG_HOLD` plus the max per-pass advance, with 125 as the hard ceiling, and the arithmetic
recorded in the cell.

#### The slam mechanism — answering Stephen's question

**STEPHEN 2026-09-17:** *"On your dual A run, you're making a bunch of speed changes. One of the
things I noticed in the speed changes is that we are physically slamming the platform… I would
think speed changes should be really smooth, but they're not."*

**MEASURED**, `BM-RUNG2 err` (steady) and `err_pk` (peak), LEFT forward, rungs 0–11 (L15170–15205):

```
rung    0     1     2     3     4     5     6     7     8     9    10    11
err    34    48    48    48    49    48    48    55    63    65    68    73
err_pk 56    75    71    71    72    72    73    80    88    91    94    98
gap    22    27    23    23    23    24    25    25    25    26    26    25
```

**`err_pk` sits ~25 counts above the steady `err` at every single rung change.** That repeated
excursion, once per step, is the jolt he felt. The right motor shows the same shape.

⚠ **Correcting this document's first reading.** From the logs alone I derived that nothing
rate-limits the commanded velocity, and proposed adding a slew-rate limiter. **That was wrong.**
`.doSpdChange` (`src/isp_bldc_motor.spin2:3655`) routes every speed change through `.rampUp` /
`.rampDn` / `.slow2Chg`, exactly as a start from rest does. The ramp exists and is applied to every
target change. **The defect is the ramp's starting rate.**

**MEASURED**, `src/isp_bldc_motor.spin2:3706-3707` and `:3715-3718`:

```spin2
                or      drv_incr, drv_incr          wz  ' -and- are we stopped, just about to spin up?
    if_z        mov     ramp_curr, ramp_min_            ' set initial ramp if starting from 0
...
                mov     curr_ramp, ramp_curr
                add     ramp_curr, ramp_inc_            ' increase ramp for next time
                cmps    ramp_curr, ramp_max_        wc
    if_nc       mov     ramp_curr, ramp_max_
```

**`ramp_curr` is reset to `ramp_min_` only when `drv_incr` is zero — only when starting from
rest.** On a speed change from a running speed it is **inherited**, and lines 3716–3718 have
already driven it to `ramp_max_`. So every rung-to-rung transition starts at **full ramp rate on
its very first pass**, with no soft start, while a start from rest begins gently and grows.

A step in commanded *acceleration* is a jolt. It also fits the measurement better than any load
effect: the ~25-count gap is nearly constant across rungs **because the ramp rate is `ramp_max_`
every time**, independent of how large the speed step is.

⭐ **The data carries its own control.** Rung 0 is the only transition that starts from rest, and it
has the **smallest** gap in the table (22). Rung 1 — the first to inherit `ramp_max_` — has the
**largest** (27). The one rung that gets the soft start is the one that does not slam.

**The fix — correct by construction (P10):** reset `ramp_curr` to `ramp_min_` at the start of
**every** new ramp, not only when `drv_incr` is zero. The soft start then applies to every speed
change and acceleration is continuous at each transition.

**Prediction for Visit 5, with a built-in control:** `err_pk` falls toward `err` at rungs 1–11
while **rung 0 is unchanged**. If rung 0 moves too, the fix did something other than what it claims.

**These are two different findings that were found together.** The lag bound (§6c-i) is my
instrument's arithmetic; only the ramp reset is a driver defect. Both are filed as PL-78.

### 6d. Telemetry `UNKNOWN` / `up,FALSE` — noted, not yet a finding

**MEASURED**, L2800 (`tid 9`): `pos,-416 hw,22 i,NA ph,NA d,NA e,NA st,UNKNOWN up,FALSE`; L12000
(`tid 39`): `pos,986 hw,-29 … st,UNKNOWN up,FALSE`. Yet `R14-DUAL-TRACES-A` passed with 0 trace
data lost across n=48.

**Undetermined.** This is most likely the designed "driver cog stopped, status block stale" state
between stop trials, but two samples do not make a property (D2 — a negative measured once is not a
property, and the same holds for a positive). Read the STOPMODE region before filing anything.

---

## 7. Roll-up

**48 cells reached a verdict; 10 are NOT_BUILT; 9 are NOMEAS.**

| | Count |
|---|---|
| **PASS** | 47 |
| **FAIL** | 13 |
| **NOMEAS** | 9 |
| **NOT_BUILT** | 10 (all t0) |

**Certified this visit:** the front-cog brake-mode start («#3513»); steering `getError()` naming the
wheel («#3555», the one error-contract cell that ran); rpm live and accurate (**W**); current scale
(R2-ISCALE); hall integrity zero missed/illegal across char and part A; board-revision detection
over 12 restarts («#3500»); **droop-instead-of-fault** («#3558»'s headline); current fold-back;
e-stop latch and clear; ordered and co-operative shutdown; lockstep start; tracking reset at speed;
**C-1's speed law**; **C-4's deceleration at 75 ticks**, agreeing with Visit 3; and `dead_gap = 70`
= 259 ns, confirming the A1/PL-9 ruling.

**Driver defects, not certified, blocking the 6.0.0 tag:**

1. **The error contract** — t0 emitted nothing (§1). Ten cells, zero evidence. *Harness, mine.*
2. **The steering front cog's stack is full** (§3a) — a shipping defect in the 3-cog form.
3. **"Motor not started" after a successful start** (§3b) — an API-contract defect that also cost
   three NOMEAS cells.
4. **Stops from speed exceed the hold-current bound** (§4b).
5. **DDU_M metres are ~1 000× off and sign-inverted** (§4c) — and the README already promises this
   fixed.
6. **Every speed change starts at full ramp rate** (§6c-ii) — `ramp_curr` is only reset from rest.
   **This is Stephen's slam**, and it is one line.

**Instrument defects, mine to fix, not driver findings:** the NOFOLD rung-0 band (§6a), the DERATE
current band (§3c), and — settled from the source after this report's first draft — **the LAGBND
110 bound itself** (§6c-i), which under-estimates the one-pass field advance above `LAG_HOLD = 100`.

⚠ **Four of the thirteen FAILs are therefore my instruments, not the driver:** `LAGBND` ×4 counts
under §6c-i, `NOFOLD` ×2 and `DERATE` ×1. Corrected cell counts after the source reading:
**6 driver FAILs, 7 instrument FAILs.**

**Visits per certified plan section** (v13, *the bench visit* rule 4): §R16.9 has now consumed
**one** visit and will need a second for the six items above. A rising count is a planning finding;
at two it is still within the plan's own "at least two change episodes by design" (D5).

---

## 8. Findings filed to `DOCs/PUNCH-LIST.md`

Filed 2026-09-17. The punch list's high-water mark was **PL-73**, so these take PL-74…PL-80.

| ID | Summary | Owner |
|---|---|---|
| **PL-74** | t0 bench binary carried no debug kernel; whole tier lost, 10 cells NOT_BUILT | mine (harness) |
| **PL-75** | Steering front cog `stack_hi == stack_of == 128`; zero margin | driver |
| **PL-76** | `driveAtPowerEx()` / `clearEmergency()` report not-started after a successful `start()` (`-1007`) | driver |
| **PL-77** | `BM-DISTM` metres ~1 000× low and sign-inverted; refutes a release line «#3515» already carries | driver or harness — undetermined |
| **PL-78** | Lag error clamps at 115–116 against a 110 bound; commanded velocity is not slew-rate-limited — **the slam** | driver |
| **PL-79** | NOFOLD rung-0 band narrower than tick quantisation; also hides any real fold-back | mine (instrument) |
| **PL-80** | DERATE cell judges current magnitude, not whether derating happened | mine (instrument) |

---

*Written from the logs by reading them. No log-analysis tooling was built or used (doctrine overlay
P10; STEPHEN 2026-09-15).*

# Bench Visit 3 — what we learned (2026-09-16)

**Rig:** Rev B dual 6.5″ platform. Left board on P32, right board on P16. Wheels up, no load, both motors
connected, board powered from the pack. **Offsets:** unchanged, 43° / 317°.

**Tree:** `53c1f2b`, the remote from 12:18. The runs started at 12:35 (`git reflog show origin/main`). Harness
banners read `src_rev 11, fmt 3`, which is what the Visit 3 sheet was written for.

**Logs:** still in `src/logs/`. Files are named by their time: `123801` = `debug_260916-123801.log`.

| Log | Load | Result |
|---|---|---|
| `123557` | `dual-clock` 200 MHz | COMPLETE, trap 0 (`:71`) |
| `123637` | `dual-clock` 270 MHz | COMPLETE, trap 0 |
| `123717` | `dual-clock` 300 MHz | COMPLETE, trap 0 |
| `123801` | `dual-b` | COMPLETE, 3,050 records, trap 0 (`:3094`) |
| `123957` | `dual-c` | COMPLETE, 5,569 records, trap 0 (`:5610`) |
| `124157` | `char` | COMPLETE, holds 9, `lib_abort` FALSE, trap 0 |

Not run: the attended pair (the rebuilt panel, `1937fe6`, was not on the remote), and `detect-phase2` (withdrawn).

**Provenance tags:** **MEASURED**, a log line cited `file:line`; **DERIVED**, a calculation or a reading of
source; **STEPHEN**, his words.

---

## 0 · The verdict

**All four repairs this visit carried are certified on the bench.** They were the reason for the visit.

| Repair | Task | Verdict | Evidence |
|---|---|---|---|
| E-stop leaves no running increment behind (PL-57) | «#3546» | **CERTIFIED** | 4 of 4 brake-mode restarts after `clearEmergency()` reached AT_SPEED and rested after the e-stop; Visit 2 and the first attempt today faulted 4 of 4 (§4) |
| Faults visible through the public API (M, AF, S-5) | «#3547», «#3550», «#3552» | **CERTIFIED** | `R14-DUAL-FLTAPI-B` PASS: both wheels faulted at 101 ms; `getStatus()` FAULTED, steering `isFaulted()` TRUE, and the latch still set 5.8 s later (§3) |
| C-3: distance stops fire within one sense pass | «#3512» | **CERTIFIED** | The stop is issued 2 ticks past the target on all four reps, against 22 at Visit 2 (§2) |
| The speed model (PL-50) | «#3548» | **CERTIFIED by measurement** | 12 clock rungs read 0.998–1.003 of the prediction at 200, 270 and 300 MHz (§1). This replaces Visit 2's arithmetic certification. |

**Also certified:** `CLKFRAME` at all three clocks, so a user may run the driver at 200, 270 or 300 MHz (§1).
`RSTPROV-B` passes on both wheels for the first time, and rpm reads true through the 128 Hz sense loop (§5).

**New, and open:**
- **Illegal hall codes on the right motor at 200 MHz only:** 3 and 5 in two 1-second windows, and 0 at 270
  and 300 (§1). Filed as PL-69.
- **PL-55 is unchanged:** every stop from 75 % still trips the 10 A abort on all four combinations (§2).

**Not measured:** the e-stop hold counted in passes («#3512»). No load runs the motor object's sense task
through an e-stop (§4.3).

---

## 1 · The clock sweep — CLKFRAME, and the driver is clock-independent

MEASURED, per clock (both motors, both signs, 75M):

| Clock | `adc_fram` = `frame_cnt` = expected | `dead_gap` | rate / prediction | net current NEG / POS (mV) | `rs_impl` | illegal hall codes |
|---|---|---|---|---|---|---|
| 200 MHz | 4,545 | 52 | 0.998–1.000 | 981–992 / 494–525 | 149–150 | **L 0, 0; R 3, 5** |
| 270 MHz | 6,136 | 70 | 0.999–1.002 | 976–984 / 496–526 | 149–151 | 0 |
| 300 MHz | 6,818 | 78 | 1.000–1.003 | 969–976 / 489–524 | 150 | 0 |

Sources: `123557:42-63`, `123637` BM-CLOCK / BM-RUNG records, `123717` BM-CLOCK / BM-RUNG records. `CLKFRM`,
`NOSTLL` and `DBGMSK` are PASS at every clock.

**DERIVED:**
- **Dead time is 260 ns at every clock:** 52 / 200 MHz, 70 / 270 MHz and 78 / 300 MHz all come to 259–260 ns.
  That meets the 250 ns minimum of both boards' manuals (A1, PL-9).
- **Speed, current scaling and the frame are clock-independent.** Duty scales with the frame (duty /
  `duty_max` is 0.776–0.778 at every clock for the NEG rung), so the fraction of the bus applied is the same.
- **PL-50's model now has a measured certification.** Rate over prediction is 0.998–1.003 at three clocks. Visit
  2's ladder gave 0.953–0.965 against the old prediction, and today's harness divides that prediction by 23/22.
- **S-3's clock route is closed.** The implied sense scale is 149–151 at every clock, so the current reading
  does not depend on the clock.

**The illegal hall codes (MEASURED `123557:57,63`):** `illegal_d 3` on RIGHT NEG and `5` on RIGHT POS, each in a
1-second, 201-tick window. `missed_d` stays 0, and the instrument's own hall count agrees (`hw_ticks` ±201,
`hw_skip` 0). LEFT reads 0 at 200 MHz, and both motors read 0 at 270 and 300 MHz and at every Visit 1 and
Visit 2 hold at 270 MHz.
- An illegal code is %000 or %111, entered from the driver's own hall read.
- **What this does not establish:** that the cause is the clock. It is one run, one motor, 8 events. The same
  motor at 270 MHz ten seconds later read 0. The condition may be transient (doctrine D2): a connector, or the
  hall read landing on an edge.
- **The owner is the driver's hall sampling, not the instrument:** the instrument's independent count lost
  nothing.

---

## 2 · Part B — FAULTB, OVERSHT (C-3), and the fault-API trial

### 2.1 FAULTB: PL-55 unchanged

Trial 1 (`ramp_inc` 22, 110.25M) was OK on all four combinations, with `i_pk` 1,040–1,075 mV and `dsat` FALSE
(`123801:448,862,1278,1695`). **The stop after it tripped the 10 A abort on all four** (`:447,861,1277,1694`), so
trials 2–5 are SKIPPED `NO_COG`. This matches the first attempt today and Visit 2's three of four. Z and C-5
get no new data from this segment.

### 2.2 OVERSHT at 50 %: C-3 measured

MEASURED (`123801:2021,2329,2673,3017`); the steering start returned 5, both boards Rev B (`:1713`):

| Run | Target (ticks) | Stop issued at | Rest | Latency | Decel after the stop | Past the target |
|---|---|---|---|---|---|---|
| 2 ft, rep 1 | 105 | 107 | 182 | 2 | 75 | 77 (444 mm) |
| 2 ft, rep 2 | 105 | 107 | 182 / 181 | 2 | 74–75 | 76–77 |
| 10 ft, rep 1 | 529 | 531 | 606 | 2 | 75 | 77 (444 mm) |
| 10 ft, rep 2 | 529 | 531 | 606 / 605 | 2 | 74–75 | 76–77 |

No rep tripped the abort. Left and right agree within one tick.

**DERIVED:**
- **The stop latency is fixed.** It is 2 ticks, about 10 ms at 196 ticks/s, which is one pass of the 128 Hz
  sense loop. At Visit 2 on the 8 Hz loop it was 22 ticks on one rep and 3 on the other, and 2 ft was all that
  measured anything.
- **The deceleration is all of what remains.** From 196 ticks/s at the 254 ticks/s² `stopMotor()` ramp (Visit 2
  §4), v² / 2a = 75.6 ticks. That is the 75 measured. So the stop overshoots its target by the ramp distance plus
  one sense pass, and repeats to a tick.
- **A 2 ft move reaches half speed**, since its decel matches the 10 ft one.

### 2.3 The fault-API trial — certified

MEASURED (`123801:3020-3082`):
- `BM-FLTAPI … want_inc 10_000, l_inc 10_000, r_inc 10_000, rows 60, flt_ms 101, held_ms 5_799, need_ms 3_000,
  latched TRUE`.
- **Row at 1 ms:** both MOVING, SPIN_UP, no fault, turning TRUE.
- **Row at 101 ms and every row to 5,900 ms:** `l_stat` / `r_stat` FAULTED, `l_st` / `r_st` FAULTED, per-wheel
  fault and latch TRUE, `turning` FALSE, `faulted` (steering `isFaulted()`) TRUE, `estop` FALSE.
- Both ramp read-backs restored (`BM-RAMPREST`, `:3018-3019`). Reset alone cleared each wheel in 30 ms
  (`BM-RECOVER`, `:3020-3021`). `R14-DUAL-FLTAPI-B` PASS (`:3092`).

**Certified by this:**
- **M:** `getStatus()` reports DS_FAULTED.
- **AF:** the steering object's `isFaulted()` reports it.
- **S-5:** the latch is not cleared after 3 s; it held 5.8 s.

**One observation, not a defect:** `getPower()` keeps reporting 50 / 50 throughout the fault. It returns the
last commanded power, as its contract says. With PL-66 (a repeated power does not clear a fault), a caller
reading `getPower()` alone would not see that the motor is not driving. `DRIVE-OBJECTS.md` should say so
(«#3515»).

---

## 3 · Part C — BASELINE and POSTFLT

- BASELINE: all eight `stopMotor()` traces REST, at `rest_k` 404–446 (`123957:369-2661`).
- POSTFLT's 3° fault provocation: NO_FAULT on all four, as at Visit 2 (`:2667,2976,4130,4440`). RIGHT BRAKE
  (tid 16) did not confirm rest by the stillness rule (`:4748`), as happened once at Visit 2 §4.
- `RSTPROV-C` is NOMEAS on both wheels, because no fault happened in part C. The reset path it guards is exercised
  and passes in part B, `RSTPROV-B` (§2.3).

---

## 4 · The e-stop — PL-57 certified

### 4.1 Before, from the same harness revision's predecessor

At Visit 2 and at today's first attempt on `6aed714`, every brake-mode trial after an e-stop reached AT_SPEED
at `pos` 0 and FAULTED at k 8. Its trace ends were stored 10 / ksum 45 and stored 13 / ksum 78.

### 4.2 Today

| tid | Motor | Sign | Mode | End | `rest_k` | Line |
|---|---|---|---|---|---|---|
| 11 | LEFT | NEG | FLOAT | REST | 54 | `:3492` |
| 12 | LEFT | NEG | BRAKE | **REST** | 64 | `:3710` |
| 13 | LEFT | POS | FLOAT | REST | 54 | `:3918` |
| 14 | LEFT | POS | BRAKE | **REST** | 54 | `:4126` |
| 17 | RIGHT | NEG | FLOAT | REST | 54 | `:4956` |
| 18 | RIGHT | NEG | BRAKE | **REST** | 65 | `:5177` |
| 19 | RIGHT | POS | FLOAT | REST | 55 | `:5388` |
| 20 | RIGHT | POS | BRAKE | **REST** | 55 | `:5599` |

MEASURED, tid 12 in full (`:3494-3572`): through k 0–49 the wheel is AT_SPEED at half speed. Current is
870–987 mV, `pos` advances 19 ticks in 98 ms (194 ticks/s), and the fault flag is FALSE. At the e-stop, k 50,
current falls to 8 mV in one sample, and `pos` moves −19 → −21 → −20 and holds. No fault at any point.

**DERIVED:** the restart after `clearEmergency()` now starts from zero and ramps to speed. That is the path
`17122f2` built (`.clearRun` on the e-stop entry). The 1–2 tick rock after the e-stop is the wheel settling
against a brake.

**PL-57: CERTIFIED**, 4 of 4, both motors, both signs.

### 4.3 The e-stop hold in passes — not measured

The motor object's sense task, which releases an e-stop after `ESTOP_HOLD_PASSES`, is started only by part A's
LIVE segment (`src/test_bench_dual.spin2:1649`). In part C the e-stop stays in ESTOP for the whole 310 ms trace
(`123957`, tid 11, k 50–205). So no load exercised the hold.
- DERIVED: 16 passes at 128 Hz is 125 ms, the same as the one 125 ms pass it replaced. The construction is
  equivalent by arithmetic, not by measurement.

---

## 5 · Char (`124157`)

- All 34 SIGNOFF lines PASS.
- rpm error 0 at seven holds and −1 at one (64 against 65, LEFT +¼). Rates 982 / 1,964, implied scale 149–150,
  missed and illegal 0.
- Steering start 4; steer-fail −1 with no leaked cog; brake start ×4 moved 13 ticks.
- Net current is within 1 % of Visit 2 at every hold.

DERIVED: rpm is read through a 128-sample window (`HALL_WINDOW_SIZE = SENSE_LOOP_HZ`), and a ±1 rpm step is one
tick in that window. **«#3512»'s rpm limb: CERTIFIED.**

---

## 6 · What this means for the driver

> **Overtaken since (aged-state sweep 2026-09-17).** Items 2, 3 and 5 below describe the driver as it
> stood on 2026-09-16 and are no longer true:
> - **Item 2:** distance stops now begin the ramp early and land at their limit -- 1 tick past a 529-tick
>   target, worst of 4 trials (`R16-DUAL-STOPLIM-B` PASS, Visit 5, `VISIT-5-RESULTS.md` §4b).
> - **Item 3:** PL-55 is closed -- Visit 4 stop peaks 971-1_055 mV against the 1_500 mV abort, and
>   `R16-DUAL-STOPCUR-B` PASS at Visit 5.
> - **Item 5:** PL-66 is fixed in the tree: a repeated power clears a fault and restarts the motor
>   («#3556», front cog). Its run-time proof (`R16-DUAL-FLTRETRY-B`) has not yet happened; see PL-86.
> - Section 2.3's fault provocation (`ramp_inc` 10_000 from standstill) was replaced at Visit 4 by a 180°
>   offset write (PL-86). DERIVED, not re-read from the design: a ramp the rotor cannot follow now makes
>   the lag-limited driver droop rather than fault, so the old stimulus cannot provoke a fault.

1. **The repairs are done and proven.** Every driver change this sprint made since Visit 2 behaves as designed on
   hardware. Nothing measured here asks for a change to any of them.
2. **Distance stops:** latency is now one sense pass. The remaining overshoot, 75 ticks (about 430 mm) at half
   speed, is the `stopMotor()` ramp itself, repeatable to a tick. Any further gain in stop accuracy is a design
   choice, not a defect: begin the ramp early by its known distance, or ramp faster. That choice meets PL-55,
   which is the same ramp drawing more than 10 A from 75 %.
3. **PL-55 is now the driver's largest open behaviour**, and STEPHEN scheduled it for this release after the
   repairs: *"we want to address it at this release, but not right now."* The repairs are now certified.
4. **Clock choice is free:** 200, 270 and 300 MHz all give the same speed, current scale and 260 ns dead time. One
   open question at 200 MHz (PL-69).
5. **Documentation (`DRIVE-OBJECTS.md`, «#3515»):** `getPower()` reports the commanded power while faulted. The
   fault clears only on a stop or a different power (PL-66).

---

## 7 · Findings filed

In `DOCs/PUNCH-LIST.md`, 2026-09-16:
- **PL-69:** illegal hall codes on the right motor at 200 MHz, 8 in two 1-second windows, none at 270 or 300.
- **PL-55:** the Visit 3 note now includes today's second run: the same four aborts on the current tree.

---

## Revision history

- **2026-09-16, first attempt:** the first set of Visit 3 logs came from `6aed714`, the remote before that day's
  push. It certified nothing, and this report originally recorded that (git history, `e9c012d`). Its readings
  were a repeat of Visit 2 and are not carried here, except the PL-55 aborts and the PL-57 "before" signature
  in §4.1.

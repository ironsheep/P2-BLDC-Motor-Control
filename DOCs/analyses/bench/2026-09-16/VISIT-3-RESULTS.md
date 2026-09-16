# Bench Visit 3 — what we learned (2026-09-16)

**Rig:** Rev B dual 6.5″ platform. Left board on P32, right board on P16. Wheels up, no load, both motors
connected, board powered from the pack. **Offsets:** unchanged, 43° / 317°.

**Logs:** still in `src/logs/`, not yet copied into this folder. Files are named by their time: `120132` =
`debug_260916-120132.log`.

**Provenance tags:**
- **MEASURED** — a log line, cited `file:line`.
- **DERIVED** — a calculation, or a reading of source or git history.
- **STEPHEN** — his words.

---

## 0 · The verdict

- **Visit 3 certified nothing: these binaries were not built from the Visit 3 tree.** The run sheet was
  written for tree `9bdb9ea`, harness `SRC_REV 11 / FMT 3`. Both motion-harness logs print
  `src_rev 7, fmt 1` (`120132:21`, `120254:21`). §1 has the evidence.
- **So the four repairs are still uncertified:** PL-57 e-stop reset (`17122f2`), fault reporting M / AF / S-5
  (`4c6122a`), the PL-50 speed model (`65bda4b`), and C-3 stop latency (`021ad06`). So are the clock guard
  and every harness change made for this visit.
- **What ran is a re-run of Visit 2's parts B and C, plus char, on an older tree.** It repeats Visit 2
  closely (§3–§5). One reading is new: **all four motor/direction combinations now trip the 10 A abort
  when stopping from 75 %**, including LEFT POS, which never tripped at Visit 2 (§3; added to PL-55).
- **The `dual-clock` loads were lost again, for a new reason:** the clock was given as `200` and `270`, not
  `200000000` and `270000000` (§2). The Visit 3 runner refuses such a value with a message; the runner that
  ran accepted it.
- **Not run:** `dual-clock 300000000`, and `detect-phase2` on Rev A (withdrawn 2026-09-16; it certified
  nothing).

---

## 1 · Which tree ran

**MEASURED:**
- Part B banner: `BM-BANNER … src_rev,7,fmt,1,part,B` (`120132:21`). Part C: `src_rev,7,fmt,1,part,C`
  (`120254:21`).
- OVERSHT ran at **75 %** power (`120132:1715`, `l_pwr,75,r_pwr,75`) and its plan record reads
  `est_s,120,est_kb,400` (`120132:30`).
- There is no `BM-FLTAPI` record and no `R14-DUAL-FLTAPI-B` cell in the part B log.
- The `dual-clock` console banner lists the clocks as `200000000, 270000000, 300000000`, comma-separated,
  and the runner patched `CLK_FREQ to 200` without complaint (`dual-clock200.out:3,10`).
- The runner's `cd` shows the bench checkout at `…/IronSheepProductionsLLC/Projects P2/P2-BLDC-Motor-Control/
  P2-BLDC-Motor-Control` (`dual-clock200.out:8`).

**DERIVED, from `src/test_bench_dual.spin2`'s revision notes and git history:**
- `SRC_REV 7` is the panel fix `6aed714`. `SRC_REV 8` arrived with `65bda4b` (PL-50), and `SRC_REV 10`
  moved OVERSHT to 50 %.
- So the harness was built from a tree between `6aed714` and `4c6122a`. The Visit 3 harness (`SRC_REV 11`,
  `f218eab`…`7bf4aff`) was not in it.
- The comma-separated banner with no clock check is the runner as it stood before `13d5c46`.
- Visit 2's part C ran `src_rev 6` (`_OLD/debug_260915-135838.log`), so this is a later tree than Visit 2's
  unattended runs. It is consistent with the Visit 2 attended tree (`src_rev 7`).

**Which commit, settled by git (MEASURED):** `git reflog show origin/main` shows the remote at `6aed714` from
2026-09-15 14:17 until the push at 2026-09-16 12:18. STEPHEN, 2026-09-16: *"i just pushed, i'll pull before
running. I always do"*. So the bench pulled `6aed714`. The Visit 3 commits, `17122f2` through `24866c2`, had not
yet been pushed. That commit is harness `SRC_REV 7` and contains none of the four repairs, which matches every
banner above. §5.2 is therefore the unfixed driver, not a failed fix.

The logs alone could not name the commit, because the `SRC_REV 7` window also covers `17122f2`. Git answered it
(PL-68).

---

## 2 · `dual-clock` — lost again

MEASURED:
- `dual-clock200.out` and `dual-clock270.out` both stop at `pnut-ts: Compiling with DEBUG`, with no error
  line and no log (`:15`).
- Each shows `patching CLK_FREQ to 200` (and `270`) in `test_bench_dual.spin2` (`:10`).

DERIVED:
- A 200 Hz `CLK_FREQ` is not a buildable P2 clock. The compile stopped, and its error went to stderr, which
  the console capture does not keep.
- At Visit 2 the value had one digit too many (`2000000000`); here it has six too few.
- The Visit 3 runner (`13d5c46`) accepts only `200000000`, `270000000` or `300000000`, and prints the reason
  on the console when it refuses. Built from the current tree, both of these would have stopped with that
  message before compiling.
- **CLKFRAME is still never measured.**

---

## 3 · Part B — FAULTB and OVERSHT (`120132`)

**Result:** COMPLETE, 1,996 records, trap 0 (`:2037-2038`). NOSTALL, DBGMASK, TRACES and RAMPREST PASS on both
wheels. `RSTPROV-B` is NOMEAS on both (`:2030-2036`).

**FAULTB trial 1** (`ramp_inc` 22, 110.25M from standstill), OK on all four combinations:

| Combination | i_pk today (mV) | Visit 2 | Stop abort today (mV) | Line |
|---|---|---|---|---|
| LEFT NEG | 1,081 | 1,005 | 1,569 | `:445-446` |
| LEFT POS | 1,088 | 971 | **1,536** | `:861-862` |
| RIGHT NEG | 1,112 | 1,023 | 1,534 | `:1275-1276` |
| RIGHT POS | 1,099 | 1,032 | 1,638 | `:1694-1695` |

- **All four combinations aborted on the stop from 75 %.** At Visit 2, LEFT POS never tripped.
- So trials 2–5 are SKIPPED `NO_COG` everywhere. Z and C-5 got no data today.
- Trial-1 peak current ran 6.5–12 % above Visit 2 on every combination. While the wheels were driven, the char
  holds ran 1.5–2.0 % lower duty than Visit 2 at the same speed and current (§6). A fuller pack would do both.
  That is DERIVED and unverified: no pack voltage is logged in these runs.

**OVERSHT at 75 %** (the pre-`f218eab` harness):
- The steering start returned 5, both boards Rev B (`:1713`).
- 2 ft rep 1: the stop was issued at tick 127, as at Visit 2, then the **10 A abort fired at 1,571 mV**
  (`:1714`, `:2018`). No rest position was recorded.
- At Visit 2 the same rep completed with a peak of 1,570 mV, just below the threshold.
- The other three reps were `NO_COG` (`:2019-2027`).
- **C-3: NOMEAS**, as at Visit 2. The 50 % trial built for exactly this did not run.

---

## 4 · Part C — BASELINE (`120254`)

- COMPLETE, 4,769 records, trap 0 (`:4809-4810`). Every part C cell PASS (`:4802-4808`).
- All eight `stopMotor()` traces reached REST, at `rest_k` 402–462 (`:369-2656`).

---

## 5 · Part C — POSTFLT

### 5.1 The 3° fault provocation still does not fault at half speed

All four FAULT traces are `why,NO_FAULT` (`:2662`, `:2971`, `:3732`, `:4042`), as at Visit 2 §5.1. The Visit 3
harness no longer depends on this provocation: its fault trial uses `ramp_inc` 10,000 from standstill
(«#3552»). Nothing new here.

### 5.2 E-stop, FLOAT then BRAKE — identical to Visit 2

- **FLOAT:** every trace rests at `rest_k` 54–55 (`:3488`, `:3712`, `:4562`, `:4783`). At Visit 2 it was
  55–56.
- **BRAKE, the restart after `clearEmergency()`:** it **faulted 4 of 4** before moving, `end FAULT`,
  `NOT_REACHED`. Reset alone cleared each fault in 30 ms (`:3500-3501`, `:3727-3728`, `:4574-4575`, `:4798-4799`).
- **The trace ends match Visit 2 exactly:** stored 10 with ksum 45 (tid 12, 18), and stored 13 with ksum 78
  (tid 14, 20). Visit 2 printed the same four lines (`_OLD/debug_260915-135838.log`).

DERIVED: this is PL-57's defect, reproduced a second time on a tree without `17122f2` (§1). It says nothing about
the fix. **PL-57 stays uncertified**, and its negative limb is now measured twice with an identical signature. When the current tree runs, any change in these four
trace ends is the fix showing.

---

## 6 · Char (`120843`)

- **Result:** COMPLETE, holds 9, `lib_abort` FALSE, trap 0 (`:441`). All 34 SIGNOFF lines PASS (`:407-440`).
- **Binary:** `src_rev 6`, built from `6aed714` (§1), so the sense loop was still 8 Hz. This is not evidence for
  «#3512»'s 128 Hz loop.

| Hold | Motor | Incre | Net today (mV) | Visit 2 | Change | Duty today | Visit 2 | Change |
|---|---|---|---|---|---|---|---|---|
| 1 | L | +¼ | 83.2 | 84.0 | −1.0 % | 7,211 | 7,343 | −1.8 % |
| 2 | L | −¼ | 166.1 | 165.2 | +0.5 % | 8,178 | 8,319 | −1.7 % |
| 3 | R | +¼ | 91.0 | 90.1 | +1.0 % | 7,306 | 7,426 | −1.6 % |
| 4 | R | −¼ | 169.5 | 169.6 | −0.1 % | 8,179 | 8,324 | −1.7 % |
| 5 | L | +½ | 470.4 | 469.2 | +0.3 % | 15,838 | 16,130 | −1.8 % |
| 6 | L | −½ | 914.9 | 915.0 | 0.0 % | 18,397 | 18,780 | −2.0 % |
| 7 | R | +½ | 503.7 | 499.0 | +0.9 % | 15,981 | 16,230 | −1.5 % |
| 8 | R | −½ | 923.2 | 917.2 | +0.7 % | 18,293 | 18,576 | −1.5 % |

Source: `:93-241`.

- rpm 65 / 131 with error 0 and implied scale 149–150 at all eight holds. Missed and illegal hall counts are 0.
- Steering start returned 4. Steer-fail returned −1 and leaked no cog. The brake start passed ×4
  (`:346`, `:361-406`).
- The left zero still reads 7.1–8.5 mV: `getCurrent()` at rest is 494 `amps_x10k` (PL-45, `:72`).
- The debug stream corrupted again around the fast cog starts (`:242-246`, `:274-279`, `:301-305`). No verdict
  was lost (PL-41).

---

## 7 · Owed after this visit

Everything the Visit 3 sheet was for is still owed, unchanged:

| Load | Certifies |
|---|---|
| `dual-clock` 200000000 / 270000000 / 300000000 | «#3549» clock guard, CLKFRAME |
| `dual-b` | «#3512» C-3 at 50 %; «#3547» / «#3550» / «#3552» fault reporting |
| `dual-c` | «#3546» PL-57 e-stop reset; the e-stop hold in passes |
| `char` | rpm through the 128 Hz sense loop («#3512») |

Plus the attended pair after «#3553»: `dual-ui` and `dual-brake`.

---

## 8 · Findings filed

Filed in `DOCs/PUNCH-LIST.md` on 2026-09-16:
- **PL-55:** LEFT POS now trips too, so all four combinations abort on a stop from 75 %. OVERSHT 2 ft rep 1
  aborted at 1,571 mV, where Visit 2's completed at a 1,570 mV peak.
- **PL-68:** no bench log or console names the commit it was built from. The Visit 3 commits had not reached the
  remote when the bench pulled, and that was found only by reading banners and git's record.

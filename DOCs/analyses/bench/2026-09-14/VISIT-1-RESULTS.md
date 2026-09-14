# Bench Visit 1 — what we learned (2026-09-14)

**Rig:** Rev B dual 6.5″ platform. Left board on P32, right board on P16. Wheels up, no load,
motors connected, board powered from the pack. **Source:** `fa8819d`. **Offsets:** unchanged,
43° / 317°.

**Provenance tags:**
- **MEASURED** — a log line in this folder, cited `file:line` (files named by their time,
  e.g. `114703` = `debug_260914-114703.log`).
- **DERIVED** — a calculation or a reading of source.
- **STEPHEN** — his words.

**STEPHEN, 2026-09-14:** *"1st run locked up but may have a clue i think vibration affected the
power supply (just a hypothesis) so i hardened the p/s connections. then i reran all tests. the
t0-hand test was aborted because the UI didn't draw properly so i couldn't understand what was
being asked."* and *"after the hardening all tests ran to completion (except t0-hand)"*.

**Sign-off sheet:** [`VISIT-1-SIGNOFF.md`](VISIT-1-SIGNOFF.md), produced by
`tools/signoff-collate.py --visit 1 --date 2026-09-14 --update --static-tree` over the seven logs
that carry data.

---

## 0 · The verdict

- **The Batch 1 foundations hold on the real rig.** The following all measured as designed:
  - board detection, including after stop and restart;
  - the hall integrity counters;
  - the S-3 current scale;
  - live rpm;
  - start-time ADC calibration;
  - the scan watchdog;
  - the driver start code in cog lookup RAM;
  - the fault-reset path.

  Eleven of the thirteen sign-off rows signed off.
- **The two-wheel steering object's fixed start released both motors and drove them**, on the
  bench for the first time (§5).
- **That corrects a sprint premise.** The claim that 5.0.2's start "returned 0" and could not
  start its motors rested only on trapped captures, which always read 0.
  - The 2026-09-09 audit read 5.0.2's source: success returned cog id + 1, and the sync handshake
    was correct.
  - The field report's `demo_dual_motor` ran both motors through that same start.

  «#3499» was therefore a change to the documented contract, not a repair of a dead start (§5).
- **The three start-return FAILs and the brake-start NOMEAS come from the tests' capture, not
  from the library.** In every trapped call the library took the correct path and printed it,
  and every trapped capture read 0 (§6, §7). «#3499»'s return contract is therefore **not yet
  certified**. Its no-orphan limb did pass, but the collation could not see that verdict (§6).
- **The first scan run went silent under load, and the watchdog did not speak.** The watchdog
  was then proven working nine minutes later. After Stephen hardened the supply connections,
  every run completed, including a scan through the exact point where run 6 stopped. That
  supports his supply hypothesis. It does not prove it (§8).
- **T0-12, the only ground truth for 90 ticks per revolution, did not run.** Its panel draws
  nothing (§10).
- **Scan run 7: DO NOT APPLY — but not because the motors disagree.**
  - Both motors put each direction's quarter-speed minimum within about 1.5°: about +13.5°
    for negative increments and −21.6° for positive. That reproduces runs 4–6 within about 2°.
  - At those offsets the current is 86–97% below the defaults.
  - **The half-speed confirmation the rule requires was never actually measured.** The scan did
    not probe between the last clean point and the fault, and a sign-off cell that should have
    caught this passed (§3).
  - The candidate pair sits 6.5–8.5° from a fault edge at no load. What margin is enough is
    Stephen's decision.

## 1 · The runs

| Log | Binary | Started | Result |
|---|---|---|---|
| `113544` | scan | 11:35:44 | **Download failed:** "No Propeller v2 device found" after two handshake attempts (`113544:16-18`). No data. |
| `113610` | scan, run 6 | 11:36:10 | **Went silent** 36 s in. TRUNCATED. Stephen then hardened the supply connections (§8). |
| `114523` | scan, watchdog self-test build | 11:45:23 | COMPLETE. The watchdog fired and ended the session (§2). |
| `114608` | detection sweep, phase 2 | 11:46:08 | COMPLETE. |
| `114635` + `114636` | Tier 0 | 11:46:35 | COMPLETE. The terminal split the session across two files; `114635` holds only its header. |
| `114703` | scan, run 7 | 11:47:03 | COMPLETE (§3). |
| `115953` | characterisation + steering + brake start | 11:59:53 | COMPLETE. |
| `120126` | Tier 0, T0-12 hand rotation | 12:01:26 | TRUNCATED. Aborted at the bench (§10). |

Every banner gave `cfg_id BENCH` with left base 32 and right base 16, where the binary prints one
(`113610:21`, `114523:21`, `114608:20`, `114703:21`, `115953:21`). Tier 0 prints no banner; its
active config line reads base 16, voltage enum 6 (`114636:12`).

## 2 · What is now certified

| Row | Task | Feature | Verdict | Evidence |
|---|---|---|---|---|
| 2 | «#3500» | Board detection | **SIGNED OFF** | Rev B at every start in the scan, char and Tier 0. After-stop and dirtied-pin reads are Rev B. An empty group reads not-detected. The detection re-run differs from the 2026-09-11 baseline **only** where predicted: 14 predicted changes occurred, 0 unpredicted, 0 predicted-but-absent. The gate-input guard skipped exactly its 12 cells. |
| 3 | «#3501» | Hall integrity counters | **SIGNED OFF** | 0 missed and 0 illegal across 62 + 58 scan points and every char hold. Coverage only: nothing on this rig provoked a bad transition. |
| 4 | «#3502» | rpm and mm/tick | **SIGNED OFF** | rpm 65 at 98.2 ticks/s and 131 at 196.4, error 0 at all eight holds (`115953:493-500`). The 1 m tick conversion passes (`114636:54`). |
| 5 | «#3503» | S-3 ADC scale | **SIGNED OFF** | Implied sense scale 149–150 mV/A at all eight holds (`115953:501-508`). |
| 6 | «#3519» | Independent offset setter | **SIGNED OFF** | 64 + 60 read-backs exact. |
| 7 | «#3524» | Hall inputs not driven at start | **SIGNED OFF** | 0 illegal at 18 starts. |
| 8 | «#3529» | ADC calibration | **SIGNED OFF** | Cross-start zero spread over five starts: 0.7–1.8 mV per channel in the scan (`114703:1376-1400`), 1.0–2.2 mV in Tier 0 (`114636:184-187`). Run 5 moved up to 62 mV (current) and 85 mV (phase). **PL-30's 72 mV right-board offset is gone:** the right zero reads 0.3–0.5 mV at every char start (`115953:143,164,227,248`). |
| 9 | «#3530» | Scan v4 logic | **SIGNED OFF — but the cells prove less than their names** | The cells record that the new code ran: a cliff probe on every half-speed leg, every point netted on its own zero, the pair record on net ratio only. **R9-SCAN-HALFLEG passed while no half-speed minimum was resolved** (its criterion is met by the very defect it exists to catch, D1). R9-SCAN-OWNZERO and R9-SCAN-PAIR2 would pass on the unfixed path too (D6). See [`SCAN-RUN-7-EVALUATION.md`](SCAN-RUN-7-EVALUATION.md) §5. |
| 10 | «#3533» | PL-28 / PL-22 / PL-9 | **FAIL** — one cell, R10-CHAR-STEERFAIL, an instrument capture defect (§6). | Reset alone clears a fault, both motors (`114703:1387,1408`). `stop()` leaves a not-ready, not-stopped state (`114636:1003-1004`). The steering start returned a real cog id path and both wheels moved (§5). `gapInMS` is absent from source. |
| 11 | «#3534» | Scan watchdog | **SIGNED OFF** | Self-test armed a stall at 11:45:26.790 (`114523:74`). Watchdog declared at 4,000 ms (`:75`), stopped both wheels, stack intact (`:76-80`), and ended the session at 11:45:30.969 (`:81-82`). Run 7 ended by cog 0 (`114703:1410`). |
| 12 | «#3535» | Driver start in cog LUT | **SIGNED OFF** | Every start reached ready, tick rate in band. |
| 1 | «#3499» | `start()` returns the cog id or −1; no orphaned cog | **FAIL** — the capture, not the library (§6) | — |
| 13 | «#3535» | Brake-mode start path | **NOMEAS** — consequence of §6 (§7) | — |

Deferred, not owed to this visit: R2-DETECT-OVERLAP, which needs a session with the motors
unplugged.

## 3 · Scan run 7 — commutation offsets

Full evaluation: [`SCAN-RUN-7-EVALUATION.md`](SCAN-RUN-7-EVALUATION.md).

- **Complete, both motors, 106 points, 728 s, ended by cog 0** (`114703:1410-1411`).
  - Foundations all held. The right motor's zero reads 0.2–1.8 mV, where runs 3–5 read 71–76 mV.
  - 15 faults, every one during acceleration, all recovered in session.
- **Quarter speed — the motors agree** (MEASURED fits):

  | | Negative increment (`offset_fwd`) | Positive increment (`offset_rev`) |
  |---|---|---|
  | LEFT | +13.4° ± 0.5 | −20.9° ± 0.7 |
  | RIGHT | +13.7° ± 0.7 | −22.3° ± 0.4 |

  - These reproduce runs 4–6 within about 2°. The hall electrical zero is about −4° on both
    motors.
  - Near the minima the negative/positive current ratio is 0.93–1.29, against 1.84–2.03 at the
    defaults.
- **Half speed — no minimum demonstrated.**
  - In all four legs the lowest current is at the last clean point before a fault, and nothing
    between the two was measured.
  - R9-SCAN-HALFLEG passed anyway: its criterion can be met by the defect it should catch (D1).
  - Scan v4 carries eight instrument defects in all (D1–D8).
- **Disposition: DO NOT APPLY.**
  - **Candidate pair:** `offset_fwd` ≈ 14°, `offset_rev` ≈ 338°. At no load it would cut current
    86–97%.
  - **Margin:** the candidate sits 6.5–8.5° from a fault edge at no load. What margin is enough is
    Stephen's decision.
  - **Next:** scan v5 makes the half-speed confirmation measurable.
- **At the point where run 6 went silent** (left, negative increment, 53°), run 7 drew 392.8 mV
  net, ≈ 2.6 A, with no fault (`114703:224-226`).

## 4 · Characterisation regression against Pass 1

Offsets 43° / 317°. Sense is mV at 150 mV/A. **Net** = raw minus the zero read at that hold's own
driver start. **A** is `getCurrent()`, which divides the **raw** reading, zero included.

| Hold | Motor | Incre | Robot | Pass 1 meter A | Pass 1 sense | Today raw | Today zero | Today net | Net ÷ 150 | `getCurrent()` A | Duty (P1 → today) | Err | rpm |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 1 | L | +¼ | fwd | 0.536 | 90.7 | 91.6 | 7.2 | 84.4 | 0.563 | 0.611 | 7,323 → 7,280 | 48 | 65 |
| 2 | L | −¼ | rev | 1.054 | 169.5 | 173.8 | 8.1 | 165.7 | 1.105 | 1.159 | 8,272 → 8,247 | −49 | 65 |
| 3 | R | +¼ | rev | 0.570 | 91.6 | 91.5 | 0.5 | 91.0 | 0.607 | 0.610 | 7,337 → 7,365 | 48 | 65 |
| 4 | R | −¼ | fwd | 1.058 | 168.2 | 167.1 | 0.5 | 166.6 | 1.111 | 1.114 | 8,185 → 8,238 | −49 | 65 |
| 5 | L | +½ | fwd | 3.004 | 455.7 | 481.3 | 7.9 | 473.4 | 3.156 | 3.209 | 16,064 → 16,050 | 49 | 131 |
| 6 | L | −½ | rev | 5.564 | 839.3 | 931.9 | 8.2 | 923.7 | 6.158 | 6.214 | 18,246 → 18,791 | −48 | 131 |
| 7 | R | +½ | rev | 3.140 | 483.8 | 495.9 | 0.3 | 495.6 | 3.304 | 3.306 | 16,070 → 16,043 | 48 | 131 |
| 8 | R | −½ | fwd | 5.530 | 843.6 | 911.7 | 0.4 | 911.3 | 6.075 | 6.078 | 18,401 → 18,350 | −49 | 131 |

Pass 1 from [`../2026-09-12/CHAR-RUN-EVALUATION.md`](../2026-09-12/CHAR-RUN-EVALUATION.md); today
from `115953:101-249`.

**What it shows:**
- **The status block survived its growth from 14 to 16 longs.** Duty, error and tick rate match
  Pass 1 at every hold: duty within 1% except hold 6 (+3%), tick rate identical (MEASURED).
- **The asymmetry is unchanged on the default offsets, as predicted.** Negative/positive net
  current ratio: left ¼ 1.96, right ¼ 1.83, left ½ 1.95, right ½ 1.84. Pass 1 gave 1.97, 1.93,
  1.86, 1.76 (DERIVED).
- **Today reads 5–11% above Pass 1's meter**, net ÷ 150 against meter A. The quarter-speed holds
  and positive half-speed holds are about +5%. The negative half-speed holds are +11% (left) and
  +10% (right) (DERIVED). The cause cannot be told: no voltage or temperature was logged, because
  the meter is retired and the front end («#3506») is not built.
- **`getCurrent()` includes the sense zero.** The char run's `amps_x10k` and `watts_mW` are the
  library's `getCurrent()`, computed from the raw sense long with no zero subtracted
  (`src/isp_bldc_motor.spin2:752-767`; `src/test_bench_char.spin2:1398-1413`, DERIVED). On the left
  board that is about 0.05 A and 1 W at rest (`115953:80`). Watts use the nominal 18.5 V. Filed as
  PL-45.
- Board revision Rev B, `dead_gap` 70, and hall counters 0 at every hold (MEASURED).

## 5 · The steering object's synchronized start ran on the bench for the first time

- `isp_steering_2wheel.start()` started both motor cogs parked on attention. It released them with
  the mask built from real cog ids: `sendatn: ltcog = 2 rtcog = 3` (`115953:402`).
- Both wheels reached AT_SPEED at 13 % power, moved 13 ticks each, and stopped
  (`115953:404-420`).
- This certifies the fixed start path (PL-22, «#3499»).
- **A sprint premise falls with it.** PL-22 held that the shipped 5.0.2 start path was broken:
  `start()` "returned 0 on success", so the `1<<(ltcog-1)` mask selected no cog. **That premise is
  refuted** (DERIVED):
  - its only measurements were trapped captures (§6);
  - the 2026-09-09 audit, reading 5.0.2's source before any bench run, found success returned
    cog id + 1 (finding C), which makes the old mask `1<<cog`, and found the sync handshake
    correct (finding AH);
  - the field report's `demo_dual_motor` drove both motors through that start
    (`../user-report-2026-09-09-ANALYSIS.md`, observations 1 and 4). That is impossible if the
    mask selected no cog.
- **The real 5.0.2 defects were findings C and AD.** The return disagreed with its own doc, and a
  failed start went unchecked. Its failure value was 0 by the documented `coginit` contract, or
  `$8000_0010` given the `$8000_000F` the library printed under cog exhaustion; neither is −1.
- **So «#3499» changed the documented contract** (cog id or −1, STEPHEN's option B, 2026-09-12). For
  5.0.2 callers that is a user-visible change, not the repair of a dead start. PL-22 is rewritten,
  and every record carrying the premise was corrected in this change.

## 6 · The start-return FAILs are the tests' capture, not the library

**Every value read through an expression-context abort trap, `x := \method()`, came back 0.** That
held even where the library had just taken, and printed, a non-zero path:

| Where | Library printed | Captured |
|---|---|---|
| T0-15a, `startTrapped()` | `* Motor COG #1` (`114636:967`) | `start_return,0` (`:969`) → R1-T0-START **FAIL** |
| T0-15b, all 7 free cogs occupied | `!! ERROR filed to start Motor Control task` — the −1 path (`:1058`) | `start_return,0` (`:1059`) → R1-T0-EXHAUST **FAIL** |
| T0-15c, start then start again | driver cogs running (`:972-993`) | `start1,0` and `start2,0` (`:996-1002`) |
| char STEERFAIL, five spacer cogs | left `* Motor COG #7`, right `!! ERROR filed to start Motor Control task`, then `!! ERROR filed to start left/right drive cog(s)` — steering's −1 path (`115953:268-281`) | `steer_fail_return,0` (`:420`) → R10-CHAR-STEERFAIL **FAIL** |
| char brake start | `* Motor COG #2` (`:470`) | `start_return,0` (`:471`) |
| char `steerDriveTrapped()` | both wheels moved 13 ticks | `aborted,DRIVE`, because its `TRUE` came back 0 (`:420`) |

- **The library's own code is right** (`src/isp_bldc_motor.spin2:109-122`,
  `src/isp_steering_2wheel.spin2:119-170`). An untrapped call to the same method returned real
  ids: the steering object's `startEx()` calls produced `ltcog = 2 rtcog = 3`.
- **A search for a counterexample found none:** 12 logged instances at 6 source sites, every
  trapped value 0. The search covered every trap site in the T0, char, scan and detect binaries,
  and the 2026-09-11 logs (DERIVED from a full read of each file). Things it ruled out:
  - *caller and callee sharing a variable name:* T0-10 and T0-8 trap `\motor.start()` directly,
    with different names, and read 0;
  - *where in the callee the result is set:* both first and last read 0;
  - *an enclosing trap:* untrapped calls made inside `\runSession()` and `\runScan()` return
    correctly.

  Every "cog" field that matched the library came from an **untrapped** call (scan `BS-START`,
  char `BC-START` and `BC-PREFLIGHT`).
- **The P2 knowledge base says a trap returns the method's normal return value when no abort
  occurs** (`p2kbSpin2Abort`). The toolchain's behaviour here differs. That is a question for
  Stephen, whose compiler it is.
- **Not yet told apart:** every receiving variable was already 0, so the logs cannot separate
  "the trap yields 0" from "the trap assigns nothing". Filed as **PL-44**, with the fix direction:
  capture the result without depending on the trap's value, and self-check a known non-zero
  return.
- **It reaches back.** PL-22's MEASURED evidence that the pre-«#3499» `start()` "returned 0 on
  success" was T0-10's trapped capture on 2026-09-11, and the detect binary's `start_ret 0` on
  2026-09-12 was another. Both are void. Re-derived from the 2026-09-09 audit and the field report,
  5.0.2 returned cog id + 1 on success (§5).
- **The no-orphan limb actually passed.** T0-15c printed `R1-T0-RESTART ... verdict,PASS`, but on
  the tail of a corrupted line (`114636:1002`). The collation did not see it and reported NOMEAS
  (PL-40). Free cogs went baseline 7 → 6 → 6 → 7, so the second `start()` left no orphan.
- **A criterion was satisfied by the broken capture:** `claimsFreeCheck()` accepts any return
  from 0 to 7, and a stuck 0 is in range (`src/test_bench_char.spin2:1942,1945`) (DERIVED). The
  measured leak evidence stands on its own: free cogs after the failed start equalled the
  baseline, 6 = 6 (`115953:420`).

## 7 · Why the brake start measured nothing

`measureBrakeStart()` uses the trapped cog id only when the wheel's own `testGetMotorCog()` agrees
with it (`src/test_bench_char.spin2:2212-2213`). With a captured 0 against a real cog 2, the guard
refused, as designed, to signal a cog that might be the wrong one. No drive ran, and all four
instances printed NOMEAS (`115953:471,484,515-518`). This is §6's defect, not a brake-path
result. The brake-mode start remains uncertified.

## 8 · Scan run 6 went silent under load

**What the log shows (MEASURED):**
- Run 6 passed its left self-check (`113610:210`, ratio 1.986) and its reference point (`:216-218`).
- It stepped the offset to 53° (`:220`) and commanded −¼ speed at 11:36:46.755 (`:222`).
- Nothing more arrived from the P2. The session was closed at 11:39:07 (`:224`).
- **The watchdog printed nothing.** On a cog-0 stall it stops both wheels, then prints
  `BS-WATCHDOG`, a sign-off FAIL, `BS-END` and `DEBUG_END_SESSION`, within 4.0–4.5 s
  (`src/test_bench_scan.spin2:5453-5515`, DERIVED).
- The same watchdog fired correctly nine minutes later (`114523:74-82`).
- 26 s before run 6, the first download failed with "No Propeller v2 device found" (`113544:16-18`).
- In run 7 the same point drew ≈ 2.7 A (`114703:224-226`), the highest non-aborting current in
  that leg. So run 6 went silent within the first 16 ms of a step to about 2.7 A.

**What that rules in and out (DERIVED):**
- **Not a cog-0-only software stall.** The watchdog would have spoken. That was the assumption
  behind «#3534» and «#3536».
- **Still open, told apart by what the wheels did after 11:36:46:**

  | Explanation | The wheels would have… |
  |---|---|
  | P2 brown-out or reset (supply connection sagging under the load step) | stopped and gone free at once |
  | Debug channel jammed (every cog blocks at its next `debug()`) | finished the point, stopped and gone free about 4–5 s later |
  | Host or link loss (the P2 carried on unheard) | kept running the scan's points for up to 30 minutes |

- **For Stephen's hypothesis:** a download failure and a silence under a load step minutes apart,
  then no recurrence in six runs after the connections were hardened — including through the
  identical point.
- **Against treating it as settled:** one clean scan after a change is not a property. Run 5's
  silence came at a low-current point (8°, about 0.1 A). No rail voltage is logged, so a dip cannot
  be seen. The fix is proven only by visits that keep not recurring.

## 9 · The debug stream corrupts when cogs start and stop quickly

Nine corrupted stretches, all in phases that start or stop several cogs within milliseconds:
- Tier 0's restart and exhaustion tests (`114636:983,994-1002,1041,1059`).
- Char's cog-exhaustion start and brake-start phases (`115953:250-254,282-364,375-379,432-459`).
- The typical signature is a `CogN  IN` line cut short.

Records inside them are lost to the collation (§6). The mechanism is not established. The class
is filed as PL-41, the collation gap as PL-40.

## 10 · T0-12 did not run

The panel is declared and never drawn into; the operator prompt went only to the terminal text
(`src/test_bench_t0.spin2:1232-1233`). No key was received: about 230 key polls, no
`T0-12,started` (`120126:22-235`). **90 ticks per revolution is still unmeasured** (PL-39, PL-42).

## 11 · Owed, and not done this visit

- **T0-12 hand rotation:** blocked by PL-42.
- **Rev A detection re-run:** «#3505» step 4. Not run today.
- **R2-DETECT-OVERLAP:** needs the motors unplugged.
- **«#3499» return contract, R10-CHAR-STEERFAIL, R13 brake start:** re-measure once the capture is
  fixed (§6).
- **The lock-up's cause:** what the wheels did after 11:36:46 (§8).

## 12 · Findings filed

- **PL-38:** the 6.5″ 6.0 V / 7.4 V speed ceilings reuse the 11.1 V value.
- **PL-39:** `MOTOR_CHOICE.md`'s hall FWD/REV labels are opposite to the library's forward.
- **PL-40:** the collation misses a verdict printed inside a corrupted line.
- **PL-41:** debug-stream corruption around fast cog start and stop.
- **PL-42:** the T0-12 panel draws nothing.
- **PL-43:** scan run 6 went silent under a load step, and the watchdog did not speak.
- **PL-44:** every value captured through an abort trap in the bench binaries reads 0.
- **PL-45:** `getCurrent()` reads about 0.05 A at rest on the left board.

# Bench Visit 2 — what we learned (2026-09-15)

**Rig:** Rev B dual 6.5″ platform. Left board on P32, right board on P16. Wheels up, no load, both
motors connected, board powered from the pack. **Offsets:** unchanged, 43° / 317°.

**Binaries:**
- **Motion harness:** banner `src_rev 6`, built before the panel fix `6aed714` (SRC_REV 7).
- **Scan:** `src_rev 10`.
- **Char:** `src_rev 6`.

**Provenance tags:**
- **MEASURED** — a log line, cited `file:line`. Files are named by their time: `134805` =
  `debug_260915-134805.log`. The logs are still in `src/logs/` and have not yet been copied into this
  folder.
- **DERIVED** — a calculation, or a reading of source.
- **STEPHEN** — his words.

**STEPHEN, 2026-09-15:** *"note: dual-clock2m.out three tests couldnt be run - this is the console out
from 1 of them"*.

**Units used below:**
- Trace current `i` is in mV at the sense resistor. Every rung measured 143–153 mV per A, so 1,500 mV is
  about 10 A.
- 1 tick is 1/90 of a revolution, and 5.76 mm of wheel travel.
- Motor-frame sign: NEG and POS are the sign of the increment given to that motor.

---

## 0 · The verdict

- **Visit 1's owed return-contract items are now certified.**
  - `R1-T0-START`, `R1-T0-EXHAUST`, `R1-T0-RESTART`, `R10-CHAR-STEERFAIL` and all four
    `R13-CHAR-BRAKESTART` pass (§2).
  - So the PL-44 capture fix works, and the Visit 1 FAILs were the capture, as reported.
- **All three motion-harness parts ran to COMPLETE with trap code 0.** Every sign-off cell passed except
  `R14-DUAL-RSTPROV-B` RIGHT, which is NOMEAS because no right-wheel fault happened (§6).
- **Headline: stopping from 75 % speed or above draws more than 10 A on three of the four motor/sign
  combinations.** The harness's 10 A abort fired 8 times (§3). Only LEFT POS never tripped. This cost:
  - the FAULTB ramp sweep on three combinations;
  - the 10 ft overshoot measurement;
  - the right-wheel reset-provenance cell.

  The mechanism is measured at half speed: `stopMotor()` drives the wheel down a ramp, and current rises
  25–45 % above running current while it does.
- **`emergencyCutoff()` stops a half-speed wheel within one tick** (§5.2). Releasing the pins with `stop()`
  lets it coast 38–48 ticks.
  - The hall counter runs every pass in every state, so it is the wheel that stopped, not the count.
  - The source suggests the driver's "drive off" state holds all three low-side FETs on, which brakes
    the motor. That rests on one unverified hardware fact.
  - If it holds, **"float" is also that brake**, and so is every fault.
- **A library defect: after `emergencyCutoff()` then `clearEmergency()`, a restart at the same speed
  faults at once** (4 of 4, §5.3). The e-stop path never clears the driver's running increment, so the
  restart declares AT_SPEED against a stopped wheel.
- **`holdAtStop()` has no effect on a stop from speed** (§4).
  - `stopMotor()` ramps down at about 254 ticks/s² every time: 19–20 ticks from quarter speed and 74–76
    from half. That holds on both motors, both signs, float or brake.
  - Only `stop()`, which releases the pins, is different: it coasts to rest in 55–60 % of the distance.
- **The post-fault stop (S-9a) is NOMEAS.** The 3° offset meant to provoke a fault at half speed ran
  2 s without faulting on both motors (§5.1). That contradicts scan run 8, whose half-speed leg faulted
  at 4°.
- **Ladder:** all 48 rungs were OK, including the 155M and 165M probes (§9).
  - The unloaded ceiling is above 165M on both motors and both signs.
  - Speed is a constant 4.3 % below the formula from 10M to 165M. That is a gain error, not a departure.
  - Above 100M the duty is pinned at maximum and current falls twentyfold while speed still tracks.
- **The left board's `ph_x10` reading sags 2.4–2.8 % under load; the right board's moves 0.2–0.3 %** at
  the same currents (§9.4).
- **Scan run 8: DO NOT APPLY** (§11).
  - Quarter-speed minima reproduce run 7 within 0.1–1.6°.
  - The half-speed minimum is still not demonstrated.
  - `R9-SCAN-HALFLEG` now FAILs honestly: run 7's defect D1 is fixed.
- **Char matches Visit 1** within −1.0…+1.8 % net current and −0.1…+1.2 % duty at all eight holds (§12).
- **Not run:**
  - the three `dual-clock` loads — the one console shows a ten-digit clock value;
  - `t0-hand`, the `dual-ui` re-run, `dual-brake`, `dual-floor` and `detect-phase2` (§15).

---

## 1 · The runs

| Log | Binary | Started | Result |
|---|---|---|---|
| `134659` | `dual-ui` | 13:46:59 | No input reached the walkthrough. Fixed in `6aed714`; not re-run. |
| `134805` | dual part A: PREFLT, STOPMODE, LIVE, LADDER | 13:48:05 | COMPLETE, records 15,186, trap 0, 5 m 09 s (`134805:15251`). |
| `dual-clock2m.out` | `dual-clock` (console only) | — | Banner shows `clkfreq 2000000000`; output stops at "Compiling with DEBUG" with no error line. No log. |
| `135528` | dual part B: PREFLT, FAULTB, OVERSHT | 13:55:28 | COMPLETE, records 3,215, trap 0 (`135528:3257`). |
| `135838` | dual part C: PREFLT, BASELINE, POSTFLT | 13:58:38 | COMPLETE, records 4,773, trap 0 (`135838:4814`). |
| `140038` | Tier 0 | 14:00:38 | COMPLETE, all 14 SIGNOFF lines PASS, `T0-TRAP` 0 (`140038:1070`). |
| `140100` | characterisation + steering + brake start | 14:01:00 | COMPLETE, holds 9, `lib_abort` FALSE, trap 0 (`140100:449`). |
| `140255` | scan, run 8 | 14:02:55 | COMPLETE, 746 s, 109 points, 15 faults (all cleared), 4 current aborts, trap 0 (`140255:1433`). |

**`dual-clock`** — MEASURED: the one console shows `clkfreq 2000000000`. That is ten digits; the run
sheet's value is `200000000`.

DERIVED:
- The console capture holds only stdout, so the reason the build stopped is not in the file.
- The other two loads left nothing to read. I do not know why they failed.

---

## 2 · What is now certified

Verdicts are read from the SIGNOFF lines. The collation tool is withdrawn.

| Row | Task | Feature | Verdict | Evidence |
|---|---|---|---|---|
| 1 | «#3499» | `start()` returns the cog id or −1; no orphaned cog | **SIGNED OFF** | `R1-T0-START` PASS: return 1 with raw cog 2 (`140038:975-976`). `R1-T0-RESTART` PASS, again printed on the tail of a corrupted line (`:1011`). `R1-T0-EXHAUST` PASS: return −1, occupied 7 = 7 after (`:1068-1069`). |
| 10 | «#3533» | PL-28 / PL-22 / PL-9 | **SIGNED OFF** | `R10-CHAR-STEERFAIL` PASS: return −1, 6 free cogs before and after (`140100:354`). `STEERSTART` and `STEERLIVE` (L 13, R 13 ticks) PASS. `R10-T0-STOPREADY` PASS (`140038:1012-1013`). |
| 13 | «#3535» | Brake-mode start path | **SIGNED OFF** | `R13-CHAR-BRAKESTART` PASS ×4: start return 2, ready, ±13 ticks, no fault (`140100:369-414`). |
| 14 | «#3508» | Motion harness, parts A–C | **Partly signed off.** Every A, B and C cell PASS except `RSTPROV-B` RIGHT (NOMEAS, n 0). `CLKFRAME`, `BRAKEFLT` and `FLOORANS` are still owed because their loads did not run. | A: `134805:15239-15249`. B: `135528:3249-3255`. C: `135838:4806-4812`. |
| 15 | «#3507» | `R15-HOST-CHANLIVE` | Positive limb present | The char log carries library debug lines (`MOT:`, init values) outside its own `BC-` records. |
| 2–8 | — | Visit 1 rows, re-measured | Still PASS | Rev B at every start in all logs; missed/illegal 0 everywhere; rpm error 0 and implied scale 149–150 at all eight char holds (`140100:415-448`); scan ZXS and ZXSALL spread ≤ 1.9 mV (`140255:1410,1431`). |

**Still owed from «#3505»:** the Rev A detection re-run (step 4), `R2-DETECT-OVERLAP`, and T0-12 (§15).

---

## 3 · Stopping from speed draws more than 10 A

### 3.1 Every abort

The harness aborts a trial on 4 consecutive readings at or above 1,500 mV (`134805:22`,
`abs_abort_mV 1_500`).

| Where | Motor | Sign | Stopping from | Abort value (mV) | Line |
|---|---|---|---|---|---|
| FAULTB, after trial 1 | LEFT | NEG | 110.25M (75 %) | 1,506 | `135528:443` |
| FAULTB, after trial 1 | RIGHT | NEG | 110.25M | 1,552 | `135528:1831` |
| FAULTB, after trial 1 | RIGHT | POS | 110.25M | 1,519 | `135528:2245` |
| LIVE, after the 75 % rung | RIGHT | POS | 110.25M | 1,586 | `134805:15079` |
| LADDER, after the top rung | LEFT | NEG | 165M | 1,642 | `134805:15120` |
| LADDER, after the top rung | RIGHT | NEG | 165M | 1,513 | `134805:15197` |
| LADDER, after the top rung | RIGHT | POS | 165M | 1,557 | `134805:15236` |
| OVERSHT 10 ft, rep 1 | BOTH (the right wheel's current) | right runs NEG | steering 75 % | 1,646 | `135528:2973` |

**LEFT POS never tripped:**
- FAULTB trial 1 stop (`135528:857`);
- LIVE 75 % (`134805:15072`);
- LADDER 165M (`134805:15156`, followed by the right-side start with no abort).

MEASURED, 10 ft trace: during SPIN_DN the left current rose from 856 to 1,324 mV and the right from 775
to 1,646. The cog was gone by k 877 (`135528:3241`).

### 3.2 The mechanism, measured at half speed

In each STOPMODE and BASELINE trace, current rises while the wheel stops:

| Motor, sign | Running current before the stop (mV) | Peak during the stop (mV) | Rise |
|---|---|---|---|
| LEFT NEG half | 900–973 | 1,143–1,212 | +22–31 % |
| RIGHT NEG half | 905–992 | 1,156–1,218 | +21–32 % |
| LEFT POS half | 456–511 | 637–668 | +30–43 % |
| RIGHT POS half | 445–551 | 677–721 | +24–53 % |

MEASURED:
- Duty falls slowly through the stop, for example from 18,777 to 1,600 over about 370 ms
  (`135838:97-361`).
- Current peaks roughly 60–100 ms into SPIN_DN.

DERIVED, from source:
- A zero request enters `.rampDn`. `drv_incr` steps down by `ramp_down` every 500 µs while the wheel is
  driven (`isp_bldc_motor.spin2:2206-2211`, `:2303-2320`).
- Drive is turned off only on reaching zero (`:2327-2333`).
- The wheel is therefore *driven* down its ramp; it does not coast.
- Running current at 75 % is 969 mV (LEFT) and 1,034 mV (RIGHT) (`134805:15072,15078`). With the same
  25–50 % rise, the peak lands at 1,200–1,550 mV — the abort threshold.
- From 165M the ramp passes back through 100M, where running current is highest (§9.3). That is why a
  stop from the top rung trips even though the running current there is only about 500 mV.

### 3.3 What it cost

- **FAULTB trials 2–5** (`ramp_inc` 100, 500, 2,000, 10,000) are SKIPPED `NO_COG` on LEFT NEG, RIGHT NEG
  and RIGHT POS (`135528:445-456,1833-1844,2247-2258`). Z and C-5 have data on LEFT POS only.
- **C-3 at 10 ft** is NOMEAS: rep 1 was aborted and rep 2 had `NO_COG` (`135528:3243-3246`).
- **`R14-DUAL-RSTPROV-B` RIGHT** is NOMEAS: no right-wheel ramp trial ran far enough to fault.

**Disposition, STEPHEN 2026-09-15:** *"put this as an item we need to research after our driver is back
in shape. That sounds like a new feature request to me, and yes, we want to address it at this release,
but not right now."*

It is filed as PL-55. The harness keeps its 10 A abort, and trials that stop from 75 % stay NOMEAS
until the research is done.

---

## 4 · C-4 — stop data (part A STOPMODE, 2 reps)

**Setup:**
- Speeds are from LIVE: quarter 98.3 / 98.5 ticks/s (L/R), half 196.6 / 196.0 (`134805:15070-15077`).
- **Ticks to rest** are exact hall counts (`hw` from the mark to rest).
- **Time to rest** is `(rest_k − mark_k) × 2 ms`. It depends on the 300 ms stillness rule, so its spread
  is wider than the tick spread.
- **Deceleration** is `v² / (2 × ticks)`, assuming constant deceleration. The time-based figure,
  `v / t`, agrees within 10–20 %.
- **STOPCMD** = `stopMotor()`, with `holdAtStop(FALSE)` (FLOAT) or `holdAtStop(TRUE)` (BRAKE).
  **STOPCOG** = `stop()`: cogstop and pins cleared; position from `hw` only.

| Motor | Sign | Speed | Stop | Ticks rep 1 / 2 | Revs | Time to rest ms rep 1 / 2 | Decel ticks/s² |
|---|---|---|---|---|---|---|---|
| LEFT | NEG | ¼ | STOPCMD FLOAT | 19 / 20 | 0.21–0.22 | 304 / 374 | 248 |
| LEFT | NEG | ¼ | STOPCMD BRAKE | 19 / 19 | 0.21 | 340 / 342 | 254 |
| LEFT | NEG | ¼ | STOPCOG | 13 / 13 | 0.14 | 210 / 206 | 372 |
| LEFT | POS | ¼ | STOPCMD FLOAT | 20 / 19 | 0.21–0.22 | 382 / 534 | 248 |
| LEFT | POS | ¼ | STOPCMD BRAKE | 20 / 20 | 0.22 | 378 / 386 | 242 |
| LEFT | POS | ¼ | STOPCOG | 13 / 13 | 0.14 | 226 / 218 | 372 |
| LEFT | NEG | ½ | STOPCMD FLOAT | 76 / 76 | 0.84 | 732 / 738 | 254 |
| LEFT | NEG | ½ | STOPCMD BRAKE | 76 / 76 | 0.84 | 704 / 710 | 254 |
| LEFT | NEG | ½ | STOPCOG | 47 / 46 | 0.51–0.52 | 478 / 438 | 416 |
| LEFT | POS | ½ | STOPCMD FLOAT | 76 / 76 | 0.84 | 746 / 748 | 254 |
| LEFT | POS | ½ | STOPCMD BRAKE | 76 / 76 | 0.84 | 748 / 752 | 254 |
| LEFT | POS | ½ | STOPCOG | 47 / 48 | 0.52–0.53 | 460 / 484 | 407 |
| RIGHT | NEG | ¼ | STOPCMD FLOAT | 19 / 19 | 0.21 | rest not confirmed ×2 | 255 |
| RIGHT | NEG | ¼ | STOPCMD BRAKE | 19 / 19 | 0.21 | 346 / 340 | 255 |
| RIGHT | NEG | ¼ | STOPCOG | 10 / 9 | 0.10–0.11 | 158 / 214 | 511 |
| RIGHT | POS | ¼ | STOPCMD FLOAT | 20 / 20 | 0.22 | 384 / 382 | 243 |
| RIGHT | POS | ¼ | STOPCMD BRAKE | 20 / 20 | 0.22 | 382 / 378 | 243 |
| RIGHT | POS | ¼ | STOPCOG | 11 / 11 | 0.12 | 178 / 192 | 441 |
| RIGHT | NEG | ½ | STOPCMD FLOAT | 76 / 76 | 0.84 | 748 / 760 | 253 |
| RIGHT | NEG | ½ | STOPCMD BRAKE | 76 / 76 | 0.84 | 708 / 706 | 253 |
| RIGHT | NEG | ½ | STOPCOG | 38 / 41 | 0.42–0.46 | 434 / 382 | 486 |
| RIGHT | POS | ½ | STOPCMD FLOAT | 76 / 76 | 0.84 | 768 / 760 | 253 |
| RIGHT | POS | ½ | STOPCMD BRAKE | 76 / 74 | 0.82–0.84 | 754 / 752 | 256 |
| RIGHT | POS | ½ | STOPCOG | 40 / 39 | 0.43–0.44 | 440 / 384 | 486 |

**What the table shows (DERIVED):**
- **`stopMotor()` decelerates at 242–256 ticks/s² on both motors, both signs and both speeds.** In wheel
  terms that is 1.4–1.5 m/s². Distance scales with speed squared: 19.5 ticks at quarter speed × 4 ≈
  76 at half. It is the driver's fixed `ramp_down` rate, not the load.
- **Float and brake give the same stop.** Ticks are identical rep for rep. `.rampDn` never reads
  `stop_mode`; it is read only once the motor is STOPPED (`isp_bldc_motor.spin2:2156-2160`,
  `:2327-2333`). `stopMotor()`'s own doc line "AFFECTED BY: holdAtStop()" (`:666`) holds only at rest.
- **`stop()` coasts to rest in 55–60 % of `stopMotor()`'s distance** at 370–510 ticks/s². The unloaded
  wheel's own drag stops it faster than the driver's ramp.
- **These are unloaded wheels on blocks.** On the floor, robot mass lengthens the coast; the driven ramp
  should hold its rate until current limits intervene. C-4 publication is «#3514» / «#3515».
- **RIGHT NEG quarter FLOAT never confirmed rest, both reps** (`134805:7888,8787`, `why NOT_REACHED`).
  It still reached STOPPED after 19 ticks. The trace data are complete; the stillness rule did not fire.

---

## 5 · Post-fault and post-e-stop stops (part C)

### 5.1 S-9a fault: NOMEAS — the provoked fault did not happen

All four fault traces are `why,NO_FAULT` (`135838:2659,2969,3733,4043`).

MEASURED, LEFT FLOAT:
- The NEG offset was written to 3° at half speed.
- Current fell from about 945 mV (`:2660`) to 21–32 mV (`:2916-2922`).
- Speed held: 3 ticks per 16 ms, about 190 ticks/s.
- No fault came in 2 s.
- After the offset was restored, `stopMotor()` stopped the wheel in 74–75 ticks, the same as BASELINE's
  74–76.

The right wheel did the same.

DERIVED:
- POSTFLT's premise was that 3° faults. That was measured at quarter speed (design `:487-493`), and it
  does not hold at half speed.
- It also contradicts scan run 8. That scan's RIGHT NEG half-speed leg faulted at 4°, with 5° its last
  clean point (`140255`, §11), yet a single write of 3° at speed runs cleanly here.
- The half-speed fault edge is therefore not a fixed angle. How it is approached matters: the scan steps
  and settles, while POSTFLT writes once at speed.
- A fault-from-speed trial needs a provocation that actually faults.

### 5.2 E-stop, FLOAT: the wheel stops within one tick

MEASURED, four traces (LEFT and RIGHT, both signs):
- One sample after the mark, `i` falls to 8–12 mV (`135838:3296-3297`).
- `pos` and `hw` stop changing within one tick. Rest is confirmed at `rest_k` 55–56, 10–12 ms after the
  mark (`:3489,3713,4563,4787`).
- The duty status decays by 88 per sample for 400 ms. It is a stale value; drive is off.

Baselines from the same log:

| Stop | Ticks | Time |
|---|---|---|
| `stopMotor()` | 74–76 | 702–766 ms |
| `stop()` (part A, pins released) | 38–48 | — |
| `emergencyCutoff()` | 1 | — |

**DERIVED, why the count is real:**
- The hall count runs in the control loop on every pass, whatever the driver state
  (`isp_bldc_motor.spin2:2485-2495`). The e-stop only skips the request logic (`:2141-2146`).
- So the wheel stopped. Its average deceleration was at least 19,000 ticks/s², about 40 times the
  pins-released coast.

**DERIVED, the likely mechanism — one unverified fact:**
- `emergencyCutoff()` leads to `.driveoff`, which sets `driveoff := 1` (`:2144`, `:2572-2573`).
- The control loop then writes duty 0 to all six PWM pins (`:2468-2469`).
- The low-side pins are configured with inverted output (`pwmn`, `P_INVERT_OUTPUT`, `:2615`; comment
  `:2465`). Duty 0 on those pins is therefore a constant high.
- **UNVERIFIED:** that a high on the Rev B board's low-side input turns that FET on. If it does, all
  three phases are held to ground: a dynamic brake. Near-zero sense current fits braking current
  circulating in the bridge. That too is unverified; it depends on where the shunt sits.

**If the premise holds, three things follow:**
- `driveoff` is also the driver's *float* state at rest: `checkstop` sets it for `SM_FLOAT` (`:2580-2585`).
- It is also the fault state (`:2539`).
- So "float" does not freewheel, and a fault at speed brakes hard. On the floor with robot mass, that
  braking current is large, and the sense resistor may not show it.

**S-9a rule output:** the e-stop sits outside both baselines — far shorter than either. The rule's
"otherwise → BETWEEN" label does not describe that, so I report it as **OUTSIDE_BOTH**.

### 5.3 E-stop, BRAKE: every instance faulted before moving — a library defect

MEASURED, four traces (`135838:3490-3502`, `3714-3729`, `4564-4576`, `4788-4803`). Each follows an e-stop
FLOAT trial, then `clearEmergency()` → `holdAtStop(FALSE)` → zero → STOPPED (design `:494-495`):
- k 0–1 STOPPED;
- **k 2 AT_SPEED with `pos` 0** (`:3460`);
- duty rises from 1,600 to 2,734, `i` stays at 12–21 mV, and `e` goes from −19 to −111;
- **k 8 FAULTED, `e` 127** (`:3466`);
- header `why,FAULTED`, trace NOT_REACHED;
- reset alone cleared it in 30 ms (`:3502`).

DERIVED, from source:
1. The e-stop path jumps to `.endRqst` without clearing `drv_incr` (`:2141-2146`).
2. The clear path only sets `DCS_STOPPED` (`:2148-2149`).
3. A zero request while STOPPED exits without touching it (`:2156-2161`).

So the driver sits in STOPPED still holding its half-speed increment. On the next start:
- `.rampUp` finds `drv_incr` non-zero and skips both the ramp start and `.checkstopfloaton`
  (`:2270-2272`).
- It finds `drv_incr` equal to the target and declares AT_SPEED (`:2274-2275`, `:2295-2296`).
- `angle_` then advances at half speed against a stationary wheel, and the position-error check faults
  (`:2536-2541`).

**Why the BRAKE label is incidental:** these trials simply came second after an e-stop. The next e-stop
FLOAT trial started cleanly, because `.resetFault` zeroes `drv_incr` (`:2195-2200`). DERIVED, not
measured: a restart at a *different* speed would begin from the stale increment instead of from zero.

**S-9a:** e-stop BRAKE is **NOMEAS**.

---

## 6 · FAULTB and C-5

**Trial 1** (`ramp_inc` 22, 110.25M from standstill) was **OK on all four combinations**:

| Combination | t_ms | i_pk (mV) | dsat | Line |
|---|---|---|---|---|
| LEFT NEG | 1,625 | 1,005 | FALSE | `135528:444` |
| LEFT POS | 1,624 | 971 | FALSE | `:857` |
| RIGHT NEG | 1,624 | 1,023 | FALSE | `:1832` |
| RIGHT POS | 1,624 | 1,032 | FALSE | `:2246` |

MEASURED: every ramp-22 start spent about 200 ms at duty 1,600 with no motion before the wheel moved.

**Trials 2–5 ran on LEFT POS only** (§3.3):

| Trial | `ramp_inc` | Result | t_ms | i_pk (mV) | dsat | Recovery | Line |
|---|---|---|---|---|---|---|---|
| 2 | 100 | OK | 775 | 970 | FALSE | — | `:1199` |
| 3 | 500 | FAULT | 186 | 219 | FALSE | RESET, 31 ms | `:1302` |
| 4 | 2,000 | FAULT | 115 | 123 | FALSE | RESET, 32 ms | `:1370` |
| 5 | 10,000 | FAULT | 96 | 200 | FALSE | RESET, 32 ms | `:1428` |

MEASURED: in each fault `e` saturates at 127 after 1–2 ticks of motion, at low current.

- **C-5: GATE_CHANGES.** The faults arrive with `dsat` FALSE; they are position-error faults, not a duty
  or current limit. **Not URGENT:** `ramp_inc` 22 did not fault unloaded.
- **Z:** NOMEAS (attended load not run).
- **S-1:** NOMEAS, `NO_TEMP_SENSOR`.
- **Segment:** items 20, faults 3, unrecovered 0 (`:2259`).

---

## 7 · C-3 — overshoot (steering, 75 %)

The steering start returned 5, both boards Rev B (`135528:2264`).

| Run | tgt | Stop issued at | Rest | Latency part | Total overshoot | Line |
|---|---|---|---|---|---|---|
| 2 ft, rep 1 | 105 | 127 | 251 | 22 ticks (127 mm) | 146 ticks (841 mm) | `:2642` |
| 2 ft, rep 2 | 105 | 108 | 207 | 3 ticks (17 mm) | 102 ticks (588 mm) | `:2972` |
| 10 ft, rep 1 | 529 | 531 | — (aborted, §3) | 2 ticks | NOMEAS | `:3243` |
| 10 ft, rep 2 | — | — | — | — | NOMEAS, `NO_COG` | `:3244-3246` |

MEASURED: in 2 ft rep 1 the right wheel's current reached 1,570 mV during the stop, just short of the
abort.

DERIVED:
- **At 2 ft the wheels were still accelerating** when the distance stop fired. Using §4's 254 ticks/s²,
  the 124 and 99 decel ticks imply 251 and 224 ticks/s at the stop, against 295 at 75 %
  (`134805:15072`). The 1.2 m full-speed prediction does not apply to 2 ft.
- **C-3 verdict: NOMEAS** — the 10 ft runs are the prediction's test.
- **Cross-check, not a verdict:** from 295 ticks/s at 254 ticks/s², the decel distance is 171 ticks
  (0.99 m), plus a few ticks of latency. That is inside the 1.2 m ± 20 % band (0.96–1.44 m), but it is
  unloaded.

---

## 8 · W — live rpm (part A LIVE)

| Motor | Incre | rpm | `rate_x10 × 60 / 900` | Difference |
|---|---|---|---|---|
| LEFT | 36.75M | 65 | 65.5 | −0.5 |
| LEFT | 73.5M | 131 | 131.1 | −0.1 |
| LEFT | 110.25M | 196 | 196.6 | −0.6 |
| RIGHT | 36.75M | 65 | 65.7 | −0.7 |
| RIGHT | 73.5M | 131 | 130.7 | +0.3 |
| RIGHT | 110.25M | 196 | 196.3 | −0.3 |

Source: `134805:15070-15078`.

**W: PASS.** All six rows are within ±2 rpm, with `hb_ok` TRUE and `i_min ≠ i_max`.

---

## 9 · LADDER (part A)

### 9.1 C-1 — the speed law

`rate_x10 / pred_x10` per rung:

| Rung | LEFT NEG | LEFT POS | RIGHT NEG | RIGHT POS |
|---|---|---|---|---|
| 5M | 1.000 | 1.000 | 1.000 | 1.000 |
| 10M | 0.964 | 0.964 | 0.964 | 0.964 |
| 20M | 0.946 | 0.948 | 0.948 | 0.962 |
| 40M | 0.963 | 0.960 | 0.965 | 0.954 |
| 60M | 0.955 | 0.959 | 0.953 | 0.953 |
| 80M | 0.956 | 0.959 | 0.959 | 0.955 |
| 100M | 0.955 | 0.955 | 0.958 | 0.956 |
| 120M | 0.959 | 0.958 | 0.956 | 0.958 |
| 140M | 0.958 | 0.959 | 0.958 | 0.958 |
| 147M | 0.958 | 0.958 | 0.957 | 0.957 |
| 155M (probe) | 0.957 | 0.956 | 0.957 | 0.958 |
| 165M (probe) | 0.958 | 0.958 | 0.956 | 0.958 |

Source: `134805:15084-15233`.

- **The 5M rung is quantised:** 14 ticks in a 1 s window, so ±1 tick is ±7 %.
- **Rule literal:** the departure rung is 10M on all four — the first OK rung outside 2 %.
- **DERIVED:** the ratio does not drift with speed; it stays at 0.953–0.965 from 40M to 165M. That is a
  constant gain about 4.3 % below the formula, the known Q9 / PL-50 gap, not a departure of the speed law.

### 9.2 The real ceiling (PL-26)

- **All 48 rungs are OK, including both probes, on both motors and both signs.** No rung faulted.
- The highest OK rung is 165M, so **the unloaded ceiling is above 165M** — at least 12 % above the
  147M limit (`isp_bldc_motor.spin2:1413`).
- The run sheet expected the two probe rungs might fault; neither did.
- **Duty** reaches `duty_max` 24,264 by 120M on all four; at 100M it is 23,431–24,241.
- **Peak error** grows from 64–77 at low rungs to 101–107 at 165M.

### 9.3 Current linearity

**`inet_x10` peaks at 100M, then falls:**

| | LEFT NEG | LEFT POS | RIGHT NEG | RIGHT POS |
|---|---|---|---|---|
| 100M | 11,840 | 10,186 | 12,612 | 10,811 |
| 120M | 5,466 | 5,461 | 5,721 | 5,717 |
| 140M | 1,500 | 1,498 | 1,515 | 1,526 |
| 155M | 437 | 435 | 474 | 474 |
| 165M | 525 | 524 | 650 | 653 |

- **Non-decreasing rule: FAILS above 100M on all four.** The fall is twentyfold, far outside any rung's
  sample spread.
- **`rs_impl`** was 143–153 at every rung: in band.
- **EXTRAPOLATED** (above 8,400): LEFT NEG 80M and 100M; LEFT POS 100M; RIGHT NEG 80M and 100M;
  RIGHT POS 100M.
- **NEAR_RAIL:** none. The largest `i_max` is 1,397.
- **DERIVED:** once duty is pinned, speed still tracks the command at the same 0.957 ratio while current
  collapses and error grows. The mechanism is not established.

### 9.4 C-6 — bus ratio from load sag

`ph_x10` over OK rungs from 20M up. `I_max` is the largest `inet_x10` / 1,500. The bound is
`B = I_max × 20 mΩ / 18,500 mV`. The sag estimate is `I_max × 83 mΩ` as a fraction of the pack voltage.

| Motor, sign | `ph_x10` max / min / mean | d | I_max | B | Sag estimate | d − sag | Verdict |
|---|---|---|---|---|---|---|---|
| LEFT NEG | 24,332 / 23,653 / 24,111 | 2.82 % | 7.89 A | 0.85 % | 3.54 % | −0.72 % | CONSISTENT |
| LEFT POS | 24,335 / 23,754 / 24,163 | 2.40 % | 6.79 A | 0.73 % | 3.05 % | −0.65 % | CONSISTENT |
| RIGHT NEG | 23,988 / 23,921 / 23,953 | 0.28 % | 8.41 A | 0.91 % | — | — | INCONCLUSIVE |
| RIGHT POS | 23,987 / 23,945 / 23,968 | 0.18 % | 7.21 A | 0.78 % | — | — | INCONCLUSIVE |

- **INCONCLUSIVE (RIGHT):** the missing measurement is one DMM reading across the right board's own
  supply terminals at a high rung.
- **CONSISTENT (LEFT):** the pack-sag estimate comes from a different pack state (rule text).

**DERIVED:**
- **The two boards disagree.** Same pack, similar currents: the left `ph_x10` dips 2.4–2.8 %, with its
  minimum at the highest-current rung, while the right moves 0.2–0.3 %.
- A single pack sag cannot produce both. Which board is right needs the same DMM reading on **both**
  boards.
- The left board also carries the 7.6–8.0 mV current zero (PL-45; `zero_x10` 76–80 against 1–8 on the
  right).

---

## 10 · S-3 by the clock route

**NOMEAS.** No `dual-clock` load produced a log (§1). The `CLKFRAME` cell remains owed.

---

## 11 · Scan run 8 — commutation offsets

Source: `140255`. 746 s, 109 points, 15 faults (all cleared, by RESET or reset alone), 4 current aborts
at the ±63° sweep points, `lib_abort` FALSE, trap 0 (`:1433`).

**Self-check ratios:** LEFT 1.959, RIGHT 1.862 — both PASS (`:210`, `:785`).

**Quarter speed:**

| Leg | Result | Minimum | Fault edge | Margin | Current at minimum vs default | Run 7 |
|---|---|---|---|---|---|---|
| LEFT NEG | NOT_BRACKETED | Floor 14.0–15.1 mV from 7° to 13°; faults at 5°, 3°, −7° | 6.0° | 7.0° | — | +13.4° |
| LEFT POS | OK, n 7 | −20.8° ± 0.7 | −12.0° | 8.8° | 11.0 vs 82.8 mV (−86.7 %) | −20.9° |
| RIGHT POS | OK, n 7 | −20.7° ± 0.6 | −12.0° | 8.7° | 12.5 vs 91.1 mV (−86.2 %) | −22.3° |
| RIGHT NEG | OK, n 6 | +13.8° ± 0.6 (flat floor 15.8–17.3 mV from 7° to 18°) | 6.0° | 7.8° | 15.8 vs 169.9 mV (−90.7 %) | +13.7° |

Sources: `:344-356`, `:531-534`, `:653-658`, `:1386-1391`.

**Half speed** — every leg POOR and pinned. Current was still falling at the last clean point before the
fault:

| Leg | Fit minimum | Last clean | First fault | Edge | Margin from fit |
|---|---|---|---|---|---|
| LEFT NEG | skipped (quarter leg not bracketed) | — | — | — | — |
| LEFT POS | −15.9° | −12° (16.6 mV) | −11° | −11.5° | 4.4° |
| RIGHT POS | −15.8° | −12° (19.3 mV) | −11° | −11.5° | 4.3° |
| RIGHT NEG | +8.5° | 5° (20.6 mV) | 4° | 4.5° | 4.0° |

**Pair and cells:**
- RIGHT pair complete: mid −3.5°, lead 17.3°, `ratio_net` 1.264, imbalance TRUE.
- `R9-SCAN-HALFLEG`: LEFT NEG NOMEAS; LEFT POS, RIGHT NEG and RIGHT POS **FAIL**. Run 7's D1 is fixed —
  the cell now tells the truth.
- Every other scan cell PASS: COGOK, REVB, INTEG, SELF, OFFSETS, STARTILL, ALIVE, RATE, ZXS, OWNZERO,
  RSTALONE, and PAIR2 on RIGHT. PAIR2 LEFT is NOMEAS (`:1392-1432`).

**Disposition: DO NOT APPLY.**
- Quarter-speed minima reproduce run 7 within 0.1–1.6°.
- The half-speed minimum is still not demonstrated; the fault edge arrives first.
- «#3523» stays blocked, and the margin decision is still Stephen's.

---

## 12 · Characterisation regression against Visit 1

Net current in mV, and duty. All holds ran at rpm error 0; rates were 982 / 1,964; implied scale was
149–150 (`140100:415-448`).

| Hold | Motor | Incre | Visit 1 net | Today net | Change | Visit 1 duty | Today duty | Change |
|---|---|---|---|---|---|---|---|---|
| 1 | L | +¼ | 84.4 | 84.0 | −0.5 % | 7,280 | 7,343 | +0.9 % |
| 2 | L | −¼ | 165.7 | 165.2 | −0.3 % | 8,247 | 8,319 | +0.9 % |
| 3 | R | +¼ | 91.0 | 90.1 | −1.0 % | 7,365 | 7,426 | +0.8 % |
| 4 | R | −¼ | 166.6 | 169.6 | +1.8 % | 8,238 | 8,324 | +1.0 % |
| 5 | L | +½ | 473.4 | 469.2 | −0.9 % | 16,050 | 16,130 | +0.5 % |
| 6 | L | −½ | 923.7 | 915.0 | −0.9 % | 18,791 | 18,780 | −0.1 % |
| 7 | R | +½ | 495.6 | 499.0 | +0.7 % | 16,043 | 16,230 | +1.2 % |
| 8 | R | −½ | 911.3 | 917.2 | +0.6 % | 18,350 | 18,576 | +1.2 % |

**Negative-to-positive current ratios:** Lq 1.967, Rq 1.882, Lh 1.950, Rh 1.838.

**Zeros:**
- Left 7.6–8.4 mV.
- Right −0.1 to 0.7 mV.
- `getCurrent()` at rest still includes the left zero: 525 in `amps_x10k` units (PL-45).

**Steering start in char:** `sendatn` left cog 2, right cog 3; start return 4 (`140100:336`).

---

## 13 · Tier 0

**All 14 SIGNOFF lines PASS** (`140038`): 1M-TICKS, ZXS, STOPPED, REPEAT ×2, DIRTY ×2, EMPTY, START,
RESTART, STOPREADY, EXHAUST.

| Line | What |
|---|---|
| `:1-319` | T0-1 Rev B (22) with dead gap 70; T0-2 forced Rev A read as `USER FORCED` |
| `:530` | REPEAT PASS, base 16 |
| `:852-853` | REPEAT PASS, base 32 |
| `:901` | DIRTY PASS, base 16 |
| `:948` | DIRTY PASS, base 32 |
| `:960-961` | EMPTY PASS |
| `:1027` | T0-10 capture now real: start return 1, raw cog 2 |
| `:1070` | `T0-TRAP` code 0 |

The ZXS cell (RIGHT) read I 12, U 11, V 6, W 15, within its 0–50 band.

---

## 14 · The debug stream still corrupts around fast cog start and stop (PL-41)

The same class as Visit 1, in the same phases:
- **Tier 0:** `140038:978,989-994,1004-1011,1050,1068`.
- **Char:** `140100:250-254,282-287,309-313`.

No verdict was lost this time. `R1-T0-RESTART` again printed on the tail of a corrupted line (`:1011`).

---

## 15 · Owed, and not done this visit

| Owed item | Why | What it holds up |
|---|---|---|
| `dual-clock` ×3 (run sheet steps 2–4) | Builds did not run (§1) | S-3 clock route, `CLKFRAME` |
| `t0-hand` (step 10) | Not run | T0-12. **90 ticks per revolution is still unmeasured.** |
| `dual-ui` re-run on SRC_REV 7 (step 11) | Not run | It gates steps 12 and 13 |
| `dual-brake` (step 12) | Not run | M, Z, S-5, AF context, `BRAKEFLT` |
| `dual-floor` (step 13) | Not run | AC, `FLOORANS` |
| `detect-phase2` on Rev A (step 14) | Not run | «#3505» step 4; `R2-DETECT-OVERLAP` needs the motors unplugged |
| FAULTB trials 2–5 on L NEG, R NEG, R POS; C-3 at 10 ft; `RSTPROV-B` RIGHT | Blocked by §3 | — |
| S-9a fault stop | Blocked by §5.1 | — |
| S-9a e-stop brake | Blocked by §5.3 | — |

There are no logs for steps 10–14, and I have no note of why they did not run.

---

## 16 · Findings filed

Filed in `DOCs/PUNCH-LIST.md` on 2026-09-15:
- items 1–7 as **PL-55 … PL-61**;
- item 8 as **PL-62**;
- item 9 as **PL-63**.

Visit 2 notes were also added to PL-26, PL-36, PL-41, PL-44, PL-46 and PL-50.

1. **Stopping from 75 % or above draws more than 10 A** on LEFT NEG, RIGHT NEG and RIGHT POS (8 aborts,
   §3). `stopMotor()` drives the wheel down its ramp with current 25–50 % above running current.
   STEPHEN: research it after the driver repairs, in this release (PL-55).
2. **`emergencyCutoff()` stops a half-speed wheel within one tick** (§5.2). The source reading says
   `driveoff` holds the low-side FETs on. **UNVERIFIED:** the board's low-side input polarity. If true,
   "float" at rest and every fault at speed are the same dynamic brake, and the braking current may be
   invisible to the sense resistor.
3. **After `emergencyCutoff()` then `clearEmergency()`, `drv_incr` keeps its old value.** A restart at
   the same speed declares AT_SPEED and faults in 16 ms (4/4, §5.3). A restart at another speed would
   skip the ramp from zero. This is a library defect.
4. **`holdAtStop()` does not change a stop from speed** (§4). `stopMotor()`'s doc line "AFFECTED BY:
   holdAtStop()" is true only at rest. Documentation impact: `DRIVE-OBJECTS.md`, with «#3514» / «#3515».
5. **POSTFLT's 3° provocation does not fault at half speed** on either motor (§5.1). It conflicts with scan
   run 8's 4° half-speed fault edge. The harness needs a fault-from-speed provocation that faults.
6. **The left board's `ph_x10` sags 2.4–2.8 % with load; the right's moves 0.2–0.3 %** at the same
   current (§9.4). It needs a DMM at each board's supply terminals.
7. **Above 100M, current falls twentyfold with duty pinned while speed still tracks.** The unloaded
   ceiling is above 165M on both motors (§9.2–9.3). This is input to PL-26.
8. **`dual-clock`:** the only console shows `clkfreq 2000000000` (ten digits), and the console capture
   does not show why the build stopped. `tools/bench-run.sh:221` checks only that the value is digits.
   The tier should refuse any value other than the three run-sheet values, and say so on the console.
9. **RIGHT NEG quarter-speed float stop never confirmed rest** in either rep, although it stopped in 19
   ticks (§4).

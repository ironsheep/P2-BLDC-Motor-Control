# Visit 7c pass 2 — Z SETTLED COLD at −3.3°, the ALIGN instrument CERTIFIED, the start seed FALSIFIED

**Task:** «#3594» (Visit 7c), with «#3600» (the start seed) certified or not by load 2.
**Run sheet:** [`../VISIT-7C-RUNSHEET.md`](../VISIT-7C-RUNSHEET.md), pass 2.
**Procedure:** `DOCs/procedures/BENCH-RUN-PROCESSING.md`.

| Log | Load | Binary | Size | Rebuilt (UTC) | Source |
|---|---|---|---|---|---|
| `debug_260922-122515.log` | `dual-align`, run 1 | `test_bench_dual.bin` part ALIGN | 84,546 | 18:25:13 | `12413b1` |
| `debug_260922-122644.log` | `dual-align`, run 2 | same | 84,546 | 18:26:43 | `12413b1` |
| `debug_260922-122752.log` | `dual-a` | `test_bench_dual.bin` part A | 84,546 | 18:27:51 | `12413b1` |

MEASURED: both parts rebuild to exactly 84,546 bytes from this tree. HEAD at run time was `12413b1`; the
only source change since then (`93f74da`) is comment text.

**Outcome.** All three `BM-END … exit,COMPLETE … trap_code,0`.

**Banner check, verified first.** Every `BM-BANNER` reads `src_rev,25,fmt,13`, part `ALIGN` / `ALIGN` / `A`;
every `BM-BUILD` reads `servo_engage,57`. The sheet asked for exactly that.

Stephen ran the hand-turned tier twice on purpose: *"by hand can be somewhat inconsistent so if a set of
turns looks erratic having a 2nd set might normalize the findings."*

---

## §1 · Headline

| Learning | The number that carries it |
|---|---|
| **Z, the hall zero, is −3.3° measured cold** — two independent methods now agree | LEFT **−3.31°**, RIGHT **−3.25°** (8 legs each); driven scan **−3.6 ± 0.4°** |
| **Z does not move with speed** — the instrument's own negative case holds | slow vs brisk: LEFT −3.34 / −3.29, RIGHT −3.22 / −3.28 |
| **Two hand runs reproduce each other**; no leg was erratic | per wheel, run 1 vs run 2 within **0.1°** |
| **The crossing detector (PL-99) is certified on hardware** | **266–269** crossings per leg against 270 physical, `dropped,0` on all 16 legs (shakedown: ~1,487, overflowed) |
| **The six hall sectors are unequal, by about ±1°** — real, and too small to matter | LEFT sectors 58.6–61.5°, the same pattern on every leg; RIGHT within ±0.6° |
| **Hall lag is an ANGLE, ±1.0° per direction**, not a time delay | the same at 43 and 117 edges/s |
| **Back-EMF is readable on the phase channels** — coasting, from 43 edges/s up | 2–5° scatter per crossing; floor not reached |
| ⛔ **The start seed («#3600») does not remove the start surge — falsified, and reverted** | duty back at its floor until k≈243 (pass 1: k≈248); peak current 57–88 (pass 1: 64–100) |
| ⛔ **Pass 1's "start mechanism settled" was wrong** — the surge is the servo HUNTING as the ramp accelerates | `e` −35 ↔ −84, duty 3,600 ↔ 6,200, ~150 ms cycle, in both runs |
| The CLIP cell's FAIL is a false alarm from how the band is sized | failing legs: `bias_tries` 4–22, hysteresis 17–58 mV; their Z matches clean legs within 0.3° |

---

## §2 · Root cause

No run aborted.

---

## §3 · Load 1 — the ALIGN tier, both runs

### 3.1 The cells

| Cell | Run 1 | Run 2 | Verdict |
|---|---|---|---|
| `R18-DUAL-ALIGN-ND` | `measured,15` [0..150] | `measured,14` | PASS — the bridge never drove |
| `R18-DUAL-ALIGN-CLIP` | `measured,2` [0..0] | `measured,3` | **FAIL — a false alarm, §3.4** |
| `R18-DUAL-ALIGN-COVER` | `measured,268` [20..] | `measured,268` | PASS |
| `R18-DUAL-ALIGN-RES` | `measured,103` [4..] | `measured,104` | PASS |
| `R18-DUAL-ALIGN-MTRX` | `TRUE` | `TRUE` | PASS — all four wheel × direction combinations returned a clean leg |

`R18-DUAL-NOSTALL-Z` and `-DBGMASK-Z` PASS in both.

### 3.2 PL-99 — the crossing detector, judged against the sheet's falsifier

The sheet: *"`cross` near 270 per leg and `dropped,0` … `cross` far above 270, or any `dropped` > 0, means
the hysteresis did not take."* Every `BM-ALEG` in both logs carries `cross` 266–269, `dropped,0` and
`unusable` 0 or 1 — for example run 1 leg 0: `cross,269,unusable,0,dropped,0`. **PL-99 is certified.**

`hyst_*_mV` read **9–10 mV** on every leg whose bias landed first try — resting noise about 5 mV plus the
4 mV margin, as sized.

### 3.3 Z — how it is computed, and the result

**The method, since nothing fixed it in advance.** «#3590» specified only "interpolate `t_us/dur_us` to
60°". A number in the driver's frame needs a mapping from crossing to rotor angle, derived here and then
tested against the data before any Z is read. Scratch arithmetic, not committed (doctrine P10).

1. **Hall frame.** Each crossing's position is `phi = 60·T1(h) + 60·f` on a positive leg, and
   `60·T1(h) + 60 − 60·f` on a negative one. Here `T1` is the driver's forward table (`hltbAngles`) and
   `f = t_us/dur_us`, with negative `t_us` meaning the previous sector.
2. **Rotor frame.** The drive writes phase levels `sin(angle_ + n·120°)` (`isp_bldc_motor.spin2:4467-4474`,
   `getqy`). That forms a stator vector at `angle_ − 90°` on phase axes 0°, −120°, +120°, so the rotor
   angle θ gives a back-EMF on phase x of `−ω·sin(θ − α_x)`.
3. **The frame is tested, not assumed.** In it, the three phases' positive peaks must fall 120° apart in
   the order U → W → V for positive ticks. MEASURED run 1 leg 0: U 64.2°, W 184.4°, V 305.1° — 120.2° and
   120.7° apart, in that order. The other orientation predicts U → V → W and is excluded.
4. **Level-shift immunity.** Rising and falling crossings sit ~165° apart, not 180°, because clipping the
   negative half-waves shifts the effective zero level. Each phase's **peak** — the midpoint of its two
   crossings — is immune to that shift, so the peak is what is used.
5. **From the hall-frame offset `c` (`phi = θ + c`) to Z.** The driver has no interpolation, so it holds
   the table angle for the whole sector (`T2(h) = T1(h) − 60°`). Averaging field and rotor over a sector
   in each direction, and requiring the two directions' optimal offsets to be symmetric, gives
   **`Z = 150° − c`**. The same algebra gives `L = setpoint − δ − 60°`, where δ is the torque angle
   beyond 90° (§9).

**Result.** Per leg, `c` agrees across its three phases within **0.02–0.60°**.

| | Z forward | Z reverse | **Z (mean — cancels hall lag)** | lag, each way |
|---|---:|---:|---:|---:|
| LEFT, slow (4 legs) | −4.39 | −2.28 | **−3.34** | ±1.05 |
| LEFT, brisk (4 legs) | −4.33 | −2.24 | **−3.29** | ±1.04 |
| RIGHT, slow (4 legs) | −4.03 | −2.40 | **−3.22** | ±0.82 |
| RIGHT, brisk (4 legs) | −4.45 | −2.11 | **−3.28** | ±1.17 |
| **LEFT, all 8** | | | **−3.31** | |
| **RIGHT, all 8** | | | **−3.25** | |

Run 1 against run 2, per wheel: LEFT −3.29 / −3.34, RIGHT −3.19 / −3.30.

- **The instrument's negative case holds.** The sheet: *"slow and brisk legs disagreeing on Z by more than
  their spread falsifies the instrument."* They agree within 0.12° on both wheels.
- **Against the driven value.** The sheet: *"a cold Z inside about ±2° of it confirms both."* Cold
  −3.3° against driven −3.6 ± 0.4°: inside by a wide margin. **Two methods sharing no instrument, no
  current and no drive agree within 0.35°**, and the frame derivation in step 3 is confirmed with them.
- **The hall lag is an angle.** Forward reads more negative than reverse by about 2°, equally at 43 and
  117 edges/s. A time delay would grow with speed; this does not. It is hall hysteresis, ±1° each way.

**On Stephen's second run.** No leg was erratic: the three phases agree within 0.6° on every leg, and the
two runs agree within 0.1° per wheel. The second run still earned its place: each leg flagged `CLIPPED`
in one run has a clean twin in the other (run 1 leg 7; run 2 legs 5 and 6), so every combination has a
clean leg.

### 3.4 The CLIP cell's FAIL is a false alarm — PL-103

Five legs flagged `band_railed`. In every one, the bias read landed only after re-takes, and the band
came out wide:

| Run / leg | `bias_tries` | `hyst_u/v/w_mV` | `band_railed` |
|---|---:|---|---:|
| 1 / 5 | 6 | 27 / 17 / 20 | 0 |
| 1 / 6 | 14 | 19 / 23 / 17 | 0 |
| 1 / 7 | 22 | **58** / 27 / 37 | **2** |
| 2 / 1 | 2 | 17 / 22 / 15 | 0 |
| 2 / 5 | 4 | 34 / **48** / 29 | **1** |
| 2 / 6 | 5 | 33 / 30 / **57** | **2** |

Every first-try bias gave 9–10 mV. The read counts as "still" when the hall code does not change, but a
wheel still coasting **inside one sector** passes that test while its back-EMF inflates the stray the band
is sized from. The band then reaches the rail. Yet those legs' Z — run 1 leg 7 −4.40, run 2 leg 5 −4.15,
run 2 leg 6 −2.15 — match their clean twins within 0.3°. **The cell refused good data for a reason that
is not in the data.** It is not the failure it exists to catch, and it is filed rather than fixed now
(§7).

### 3.5 H-3 — are the six hall sectors equal?

Each sector's share of the six sectors around it, from `dur_us`, as electrical degrees. No frame
assumption is involved.

| Hall code | LEFT, 8 legs (typical ±0.3 s.e.) | RIGHT, clean legs |
|---|---:|---:|
| `001` | 58.6–59.5 | 58.6–59.5 |
| `010` | 60.0–61.0 | 58.8–59.6 |
| `011` | 59.2–60.3 | 59.8–60.6 |
| `100` | 58.8–60.1 | 59.6–60.7 |
| `101` | **60.8–61.5** | 59.8–60.0 |
| `110` | 59.2–59.7 | 59.4–60.4 |

**Unequal, by about ±1°.** Averaged over legs: LEFT 59.2 / 60.7 / 59.6 / 59.3 / 61.0 / 59.5 (±0.9° about
60); RIGHT 59.3 / 59.2 / 60.3 / 60.1 / 59.9 / 60.0 (±0.55°). LEFT is the larger case: `101` wide and `001` narrow on every leg, both
directions, both speeds and both runs. Hall lag shifts every edge the same way, so it cannot produce a
width pattern; this is the sensors' placement.

**What it decides:**
- For a 60°-sector commutator, ±1° is noise.
- For any future sub-sector interpolation, it is the ~1° floor of the error.
- **It does not explain the RIGHT motor's residual asymmetry** (manual §7.3): RIGHT has the *smaller*
  spread.

### 3.6 Back-EMF as a position source

- **Clean down to the slowest leg:** 43 edges/s (run 1 leg 0), crossing scatter 2–5° per type. The floor
  was not reached.
- **Peak railing** runs 71–196 per thousand readings (`rail_pm`). The negative half-waves clip, as the
  sheet expected, and clipping does not move a crossing.

---

## §4 · Load 2 — `dual-a`, and the START trace

### 4.1 Nothing else in part A changed

All 24 `SIGNOFF` verdicts equal pass 1's (`debug_260921-224820.log`), cell for cell.

`R17-DUAL-TRKICK-A` FAILs exactly as before: `measured,221` / `214` against [0..50], where pass 1 read
225 / 223. It is the transition kick at a **speed change**, a path the seed did not touch.

`R16-DUAL-LAGBND-A` reads `measured,113` [0..124] on both motors, as in pass 1. The sheet's falsifier —
*"a new failure anywhere in part A is a finding against this change"* — did not fire.

### 4.2 The start seed — judged against the prediction fixed before the run

| Reading | Pass 1 (seed 0) | Pass 2 predicted | **Pass 2 measured** |
|---|---|---|---|
| `e` at k=1–3 | ~0 (−1, 0) | ~57 | **−58, +57, −58, +57** ✓ |
| duty first moves | k=232 | within the first samples | **k=1–3** ✓ |
| duty last at its 1,600 floor | k=232–249 | — | **k=242–244** ✗ |
| peak current (tids 1, 8, 27, 34) | 87, 100, 82, 64 | **lower** | **88, 72, 57, 72** ✗ |

⛔ **The falsifier fires.** The sheet: *"duty still pinned for hundreds of ms, or peak current unchanged or
higher."* Duty is back at its floor for ~390 ms, and the peaks are unchanged within their spread.
**«#3600» is not certified.**

### 4.3 What actually happens at a start — and why pass 1's conclusion was wrong

The same trace in both runs, tid 1 (LEFT, −36,750,000):

```
pass 1  k=100 pos=0  d=1_600 e=-18 | k=225 pos=-3 d=1_600 e=-42 | k=350 pos=-12 d=5_837 e=-82 | k=375 pos=-16 i=72 d=4_829 e=-35 | k=425 pos=-22 i=50 d=6_194 e=-84
pass 2  k=25  pos=-1 d=1_946 e=-15 | k=100 pos=-2 d=1_600 e=9  | k=350 pos=-14 d=5_447 e=-59 | k=375 pos=-18 i=85 d=5_263 e=-15 | k=425 pos=-24 i=53 d=5_715 e=-66
```

1. **During the "pinned" wait the rotor is not waiting — it is moving.** `pos` walks 0 → −3 by k=225 in
   pass 1, with duty at 1,600 throughout. Early in the ramp the field advances slowly enough for minimum
   duty to drag the rotor with it. Duty has no reason to rise until the ramp outruns that.
2. **The seed changes only the first moment.** Duty jumps, the rotor snaps about a tick onto the field
   and past it (`e` flips to **+19** and **+9** — the rotor *ahead*), and duty falls back to its floor
   for the same stretch.
3. **The current peaks come from the servo HUNTING.** Once the ramp outruns minimum duty, `e` and duty
   swing together: −82 → −35 → −84 and 5,837 → 4,829 → 6,194 on a ~150 ms cycle, in both runs. Each
   swing's high point is a current peak (i 72, 50, 63; then 85, 53, 49).

**Why pass 1 read it wrongly.** Its falsifier was *"if duty moves before |err| crosses 60°, the deadband
story is wrong."* Duty did not move early, so the story "held" — but **the rotor-follows-the-slow-ramp
explanation predicts exactly the same thing**. The falsifier could not tell the two apart, and the
conclusion was stronger than the test (a planning gap, recorded).

**The prime suspects, for «#3589»:**
- **PL-101** — the servo holds a 21° band, not a point.
- **Asymmetric gains** — 18 above the setpoint, 4 below (`isp_bldc_motor.spin2:2264-2265`).

Together those are the classic shape of a limit cycle: fast up, slow down, and no restoring force inside
the band.

### 4.4 Low-speed starts — changed, not judged

`BM-LOW`'s `edges` and gap statistics are unchanged at every rung. `first_ms` moved: 1×10⁶ went from
239–301 ms to 27–43 ms, while 2–3×10⁶ went up. That is the seed's snap interacting with where each
lifetime left the rotor. No cell judges it, and the revert removes it.

---

## §5 · What this means for the driver

### 5a · What it now DOES

- **Reverted: the start seed.** It removed no wait and added a one-tick snap at every start. Removed in
  this session (D5: a control that does not earn its keep is removed, not kept). Cog RAM is back to
  **471 of 496, 25 free**, recounted from the compiler.
- **Confirmed, and no change:** the shipped hall zero. `HUB_HALL_ZERO_DEGR = −4` against a cold −3.3 and a
  driven −3.6: right to within 0.7°, inside the constant's own 1° resolution.
- **Confirmed, and no change:** hall lag. ±1° each way is already absorbed in the measured `L`.
- ⚠ **What this does NOT license:**
  - Any start-surge fix. Its mechanism is now a *hypothesis* (servo hunting) with no discriminating test
    yet. The fix is «#3589»'s design, and it will be certified by the START trace.
  - Treating Z = −3.3 as a reason to change the constant.
  - Treating the equal-enough sectors as licensing sub-sector interpolation. That still needs back-EMF
    *while driving*, which is unmeasured.

### 5b · What it now KNOWS

- **Front 3 did not advance.** The drive reads the phase channels but acts on none of them; the
  back-EMF-as-position capability is proven only on the bench, coasting. No sensor was integrated.
- **What it established for front 3:** back-EMF is a usable angle source at coasting speeds ≥ 43
  edges/s, within 2–5°, and agrees with the halls to 0.35° on Z. That is the first row of evidence a
  back-EMF integration would stand on.

---

## §6 · What this changes about the next run

- **Carry: the START trace**, re-used as-is, to certify «#3589»'s servo change when it lands. **Its
  falsifier must now discriminate.** A prediction about duty timing alone cannot, since both stories
  predict it. The next sheet judges the **hunting**: the amplitude of the `e` and duty swings during
  acceleration, and whether current peaks coincide with duty swing peaks.
- **Carry: Rev A Z** — the other two units, hand-turned — once PL-103 is fixed and the phase-scale
  question (manual §9.1) is answered. The instrument is certified; that is what was missing.
- **Carry: back-EMF while driving**, if «#3589» chooses to integrate it. Nothing measures it yet, and it
  gates that choice.
- **Drop: the ALIGN tier for these two units.** Z and H-3 are answered, reproduced and cross-checked.
  Re-running it would re-measure known values (P10).
- **Carry, unchanged: the loaded floor run («#3591»)**, still behind the PLOT work.

---

## §7 · Findings register

| Id | Finding | Disposition |
|---|---|---|
| **P2-1** | PL-99 certified: 266–269 of 270 crossings, `dropped,0`, 16 legs | **Closed** — PL-99 marked certified |
| **P2-2** | Z = −3.3° cold (L −3.31, R −3.25), speed-invariant to 0.12°, agreeing with the driven −3.6 ± 0.4 | **Closed** — into «#3599» for the manual |
| **P2-3** | Hall sectors unequal by ±1°, a fixed per-motor pattern; not the RIGHT asymmetry's cause | **Closed** (H-3) — into «#3599» |
| **P2-4** | Hall lag is ±1.0° of angle, speed-independent | **Closed** |
| **P2-5** | Back-EMF readable coasting from 43 edges/s; floor not reached; unmeasured while driving | **Watch** — «#3589»'s sensor row; the next discriminating measurement is back-EMF while driving |
| **P2-6** | CLIP false alarm: the band is sized from a bias read taken while the wheel still coasts inside a sector | ⛔ **Punch list — PL-103** |
| **P2-7** | The start seed does not remove the surge; falsifier fired | ⛔ **FIX — reverted this session**; «#3600» closed with this result |
| **P2-8** | Pass 1's "start mechanism settled" was wrong; the surge is servo hunting during ramp acceleration | ⛔ **FIX — the record corrected this session** (pass-1 evaluation, manual §6.4, design doc, «#3589», PL-101) |
| **P2-9** | Pass 1's falsifier could not distinguish its two explanations | **Planning gap** — recorded in the candidates buffer |
| **P2-10** | `L = setpoint − δ − 60°`; with the setpoint really a 21° band, L's speed dependence may be the servo's position in that band | **Watch** — a hypothesis for «#3589», not a claim |
| **P2-11** | `R17-DUAL-TRKICK-A` still FAILs (221 / 214) | **Watch** — unchanged; «#3583»'s |
| **P2-12** | With the seed removed, `servo_engage` no longer marks a driver change — the banner had no driver identity again | ⛔ **FIX — done this session**: the driver gains a hand-bumped `DRIVER_REV`, and `BM-BUILD` prints `drv_rev` (harness SRC_REV 26, FMT 14) |

---

## §8 · What is NOT established

- **Back-EMF while the bridge drives.** Everything in §3.6 is coasting.
- **Back-EMF's low-speed floor.** The slowest leg (43 edges/s) was still clean; the drive's slowest
  command is 2.7 edges/s.
- **Back-EMF's amplitude in volts**, and so the phase-sense scale needed for Rev A.
- **The start surge's mechanism.** Servo hunting is what the traces show; *why* it hunts is not tested.
  PL-101's band and the 18 / 4 gain asymmetry are suspects, not causes.
- **Anything about the Rev A pair.**
- **The start surge under load.**

---

## §9 · Questions left open

| Question | What would settle it | Owner |
|---|---|---|
| Why does the servo hunt during acceleration — the band, the gain asymmetry, or the ramp rate? | A desk model of the servo against the measured traces first, then the START trace judging amplitude on the changed drive | «#3589» |
| Is L's speed dependence the servo's position within its band? | Log `e` at steady speed per rung: if the mean \|e\| moves through 42–56 as L moves, the band carries it | «#3589» |
| Can back-EMF carry angle while driving, and below 43 edges/s? | Per-phase samples during driven low-speed rungs (the harness sums them today) | «#3589», if it chooses integration |
| Do the Rev A boards present phase voltage at the same scale? | Manual §9.1's check, before any Rev A reading | «#3599» |

---

## §10 · FRONTS, after

```
FRONTS  (after this run)
  completion   driver last changed 0 commits ago (the seed revert, this session)
  information  0 loads ready and unrun -- dual-align answered; dual-a ran; the next loads wait on «#3589»
  robustness   sensors the DRIVER acts on: halls y  current y  back-EMF n  follow n
```

- **Completion — advanced, by removal.** The driver lost a change that did not work (D5).
- **Information — advanced:** Z cold and cross-checked, H-3 answered, hall lag characterised, back-EMF
  proven readable coasting, and the start surge's real shape found.
- **Robustness — not advanced.** No sensor was integrated; back-EMF's case for integration is stronger
  and still unmeasured while driving.

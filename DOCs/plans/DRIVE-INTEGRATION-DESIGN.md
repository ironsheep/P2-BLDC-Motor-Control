# Drive integration design — R18.3

**Plan section:** R18.3 of [`BENCH-READINESS-SPRINT-PLAN.md`](BENCH-READINESS-SPRINT-PLAN.md), which
split it by gate on 2026-09-22. This document is the design both halves write into:

- **«#3596», the desk half — sections 1 to 4.** What the drive can sense, the user-visible contract,
  what it means for two wheels, and the space and time the change has to fit in. None of it waits on
  a bench answer.
- **«#3589», the bench-gated half — section 5 names what it owns.** It adds the drive change and its
  acceptance numbers, taking sections 1 to 4 as given or arguing any change.

Provenance marks follow doctrine overlay P8: **MEASURED** cites a log, a record or `file:line`;
**DERIVED** is reasoning from named traced claims; **STEPHEN** is his words; unlabelled means the
sources were read and do not settle it.

---

## 1. What the drive can sense

Four channels reach the driver. Two are fully characterised; two are open.

### 1.1 Halls — position, direction, speed; not angle inside a sector

| Claim | Provenance |
|---|---|
| Three hall lines, **6 ticks per electrical cycle**, 15 pole pairs, so **90 ticks per wheel revolution** — each tick is 60° electrical, **4° of wheel**. | MEASURED: T0-12 hand pass, 270 ticks over 3 revolutions (Visit 2); `isp_bldc_motor.spin2` `HALL_TICKS_PER_CYCLE = 6` |
| All three lines are read **at one instant**, one `INA`/`INB` read per sample. | `initAngleFmHall` and the control loop, PL-90 |
| **Zero missed and zero illegal transitions at every rung of the ladder, including the two above the nominal ceiling.** | MEASURED: `BENCH-LOG-STUDY-2026-09-21.md` §6.4 |
| **Speed tracks the command to 0.1–0.3 %** at every rung unloaded, and **to 4 % at the very bottom** (1×10⁶, 2.7 edges/s). | MEASURED: same study §6.1, §6.3 |
| About **4.3 drive passes per hall edge at the top rung** (1,913 passes/s). | DERIVED at «#3581», corroborated: 44,165 frames/s measured against 44,000 nominal (§6.4) |
| The hall zero sits at **Z = −3.6 ± 0.4°** driven, **−3.3°** cold from back-EMF, and does not move with speed. | MEASURED: four scan self-locations, and the ALIGN tier — `MOTOR-6.5IN-TECHNICAL-MANUAL.md` §4 |

**What the halls cannot tell:**
- **Where the rotor is inside a 60° sector.** The field free-runs between edges (PL-95).
- **Anything fast at low speed.** At 1×10⁶ an edge arrives every 278–448 ms, and the rotor's
  instantaneous speed swings about ±30 % between edges from cogging. MEASURED: study §6.3, F12.
- **Where the rotor is inside a sector, to better than about 1°, even by interpolation.** The six
  sectors are unequal by ±1° (MEASURED, Visit 7c pass 2 §3.5; manual H-3 FILLED), which is the error
  floor of any within-sector interpolation.

**What the drive already does with them.**
- **Position:** `pos`, tracking, and the distance, rotation and time stops.
- **The duty servo's error:** `err_` at `:4569-4574`.
- **The blocked-motor protective stop:** no tick for `BLOCKED_PASSES` (1,000 front passes, ~1 s) while
  held at the lag limit, `:1790-1795`.
- **The measured rate**, over a 1 s window of 125 slots, which feeds `testGetFollowing()` (`:1468`).
  ⚠ Its commanded side was corrected at Visit 7c (C-1, `SIGNX 30`, `:3670`) and has not yet been
  re-judged on a run. H-10 stays open until it is.

### 1.2 Current sense — one DC-link shunt, fast, one-signed

| Claim | Provenance |
|---|---|
| **One** low-side shunt measures **total MOSFET load current**, the DC link. There is **no per-phase current** on this board. | Parallax 64010 manual, quoted in `BOARD-REVISION-FACTS.md` §Rev A, §Rev B 8 |
| Rev B: 3 mΩ with an INA180B2, calibrated to **150 mV/A**. Rev A: 5 mΩ with no amplifier, about **30× coarser**. | same; `CURRENT-LIMIT-AND-STOP-DESIGN.md` |
| Sampled **every PWM frame**, and the fold-back limiter reads it **in the same 43.9 kHz loop** — so it is at most one frame (22.8 µs) old when acted on. | `:4438` (loop rate comment); the limiter at `:4583-4590` sits in that loop |
| Phase current is only a **lower-bound estimate**: I_phase ≥ I_dc / (0.75 m). | `CURRENT-LIMIT-AND-STOP-DESIGN.md` §3.4; implemented at `:4583-4585` and `:1778-1780` |
| A rest zero is captured at start with the bridge floated and subtracted from every reading. | PL-45; `captureRestZero()` |
| Worst reading in the last scan: **1,036 mV (~6.9 A)**, far under the fold-back. | MEASURED: `2026-09-22/SHAKEDOWN-EVALUATION.md` |

**What it cannot tell:**
- **Regeneration.** A low-side shunt drives its node below ground when current flows back. Rev A almost
  certainly cannot see it; Rev B depends on the INA180B2's reference pin. Hole H-7.
- **Which phase carries the current.**

**What the drive already does with it.** The per-frame fold-back to `I_PEAK_A`, and the front cog's
thermal derate to `I_CONT_A` over a ~1 s average (`:1777-1787`). On Rev A the same code runs at 30× less
resolution, and whether it protects Rev A is a question the Rev A pair answers after «#3583»
(manual §9.1).

### 1.3 Phase voltages as a rotor-angle source — proven coasting, open while driving

The three phase-sense channels are read and scaled every frame and reach nothing but the status
block.

| Claim | Provenance |
|---|---|
| With the bridge **coasting**, they carry the motor's back-EMF: clean zero crossings, 2–5° scatter per crossing type, about 45 per type per 3-turn leg. | MEASURED: `2026-09-22/VISIT-7C-PASS2-EVALUATION.md` §3.3, §3.6 |
| That holds from the slowest leg measured, **43 hall edges/s**, upward. The floor was not reached. | same |
| Z derived from them agrees with the driven scan within **0.35°**, and the phases fall in the order the drive's `sin(angle_ + n·120°)` convention predicts. | same, §3.3 |
| The negative half-waves **clip** at the ADC floor (the resting level sits ~55 mV above it), so amplitude is unusable as it stands; crossings are unaffected. | same, `rail_pm` 71–196 ‰ |

**Open, and «#3589» owns it:**
- **Readability while the bridge drives.** The pins then carry PWM; nothing has measured it.
- **Readability below 43 edges/s.** The drive's slowest command is 2.7 edges/s, and that low regime
  is where the halls stop informing and an angle source would be wanted.

### 1.4 The phase-voltage SUM as a bus-voltage reading — a candidate, unverified

Found while writing this section. The harness's `ph_x10` is the mean of `u+v+w` in mV ×10
(`test_bench_dual.spin2:8423`), and on the 2026-09-20 ladder it read **23,799–23,831** — about 2.38 V
at the pins — at rungs whose duty ran from 7 % to 100 % and whose current ran from 58 to 10,839 mV.
MEASURED: study §6.5. Coasting at rest the three pins sit near 55 mV each.

DERIVED: a sum that stays constant across duty is what a driven bridge produces when each phase
averages half the bus through a fixed divider. At a nominal 18.5 V that implies a divider near
**1/11.7**. If it holds, **bus voltage (hole H-8) needs no new hardware** — only one reading at a known
pack voltage to set the ratio.

**Unverified, and there is a reason for doubt.** The 0.13 % spread across a 0–7 A load says either the
pack barely sagged or the sum is not tracking the bus. The divider ratio is not in any document we
hold; `BOARD-REVISION-FACTS.md` does not cover phase sensing. Not designed on until verified.

---

## 2. The user-visible contract

Each decision below says what the member will do, what the other choice would have been and why it
was not taken, and the release-note line «#3515» owes. The rule behind all of them (doctrine overlay
P3): **the API keeps the promise its name and documentation make.** Where the answer is a *new*
promise, it is **Stephen's ruling**, quoted.

The fact that shapes all of them. MEASURED, study §6.1a: **unloaded, the rotor tracks the command to
0.2 % at every rung up to the top, even with duty pinned from rung 6.** What is lost above the knee is
torque margin, not speed. A command the drive cannot follow has been seen only at the scan's torque
and current walls (44–47 % following) and, by the physics of the knee, will appear **under load** —
which has not been measured (H-6, the floor run «#3591»).

### C-1 · `DCS_AT_SPEED` keeps meaning "the field reached its commanded rate"

- **Decided.** It stays a **ramp-completion state**, set where the field's increment reaches its
  target (`:4302`, `:4335`).
- **The other way:** make it a measured claim, set only when the rotor follows.
- **Why not.** The PASM driver **accepts a new command only in `STOPPED`, `AT_SPEED` or `FAULTED`**
  (`:4158-4162`), and throws the request away otherwise. A motor that could not follow would never
  reach a measured `AT_SPEED`, so it would discard every new speed command: a user easing off a
  struggling motor would be ignored. One value, one meaning (D7). The measured claim is a separate
  observable, C-6.
  - *Amended by «#3589»:* §5.3 D-4 makes every state accept a command, so the discard argument no
    longer applies. The decision stands on *one value, one meaning* alone. Under D-5 an overloaded
    motor's field genuinely runs below its command, so `AT_SPEED` clearing then is this meaning
    kept, not changed.
- **Release note:** none — `getDriverState()` is not in the user documents, and nothing changes.

### C-2 · `getPower()` keeps returning the commanded power

- **Decided.** It returns the last commanded power, 0 once stopped, exactly as documented (`:826`).
- **The other way:** report an *achieved* power, the measured rate as a fraction of the power table.
- **Why not.** It would move with load and would stop meaning "what I asked for". A caller could no
  longer read back what it set, and 0 would no longer mean stopped. Achieved speed is a different
  quantity with its own member (C-6).
- **Release note:** a clarification only — *"getPower() returns what you commanded, not what the motor
  achieved."*

### C-3 · `isTurning()` keeps its state meaning, with its one gap bounded

- **Decided.** TRUE while the motor is commanded to move and is neither stopped, faulted nor
  emergency-stopped (`:1138-1143`).
- **Where the name would lie, and the bound on it.** A motor that is **stalled** is not turning. The
  lie lasts until the blocked-motor protection stops it: at most `BLOCKED_PASSES`, ~1 s (`:1790-1795`,
  `:3896`). A motor running slower than commanded **is** turning, so a droop is not a lie.
- **The other way:** measure it — TRUE only while hall ticks arrive.
- **Why not.** At the bottom of the range an edge arrives every 278–448 ms (MEASURED, §1.1), so a
  tick-based test either flickers or carries about half a second of latency. The bound the protection
  already enforces is tighter than the measured test could offer at low speed.
- **Release note:** a documentation line — *"isTurning() is TRUE while the motor is commanded to move; a
  motor that stalls is stopped by the blocked-motor protection within about a second."*

### C-4 · `setMaxSpeed()` stays a cap on what is commanded

- **Decided.** It caps commanded power in both directions and refuses nothing. When the drive cannot
  reach a command, it runs at the fastest rate it can sustain — R18.4's correction 2, *hold at the
  achievable rate rather than winding the field ahead*. The call still returns `NO_ERROR`.
- **The other way:** refuse or clamp a cap above a measured ceiling.
- **Why not.** Achievability depends on load and on the pack, and the call knows neither. The only
  ceiling table is invalidated by this very change (PL-26, PL-38). No per-direction ceiling has ever
  been measured (H-9).
- **Release note:** *"setMaxSpeed() caps what you command. Under load a motor may run slower than a
  capped command; it then holds the fastest speed it can sustain."*

### C-5 · `setMaxSpeedForDistance()` likewise; a distance move still stops at its distance

- **Decided.** The same as C-4. Distance stops are **position-based** (the front cog counts ticks), so
  a move that runs slower than commanded still stops at its distance and only takes longer.
- **The two-wheel exception** is a path question, section 3.
- **Release note:** covered by C-4's line.

### C-6 · The measured claim stays inside the drive — **ruled: TEST-USE only for 6.0.0**

- **STEPHEN 2026-09-22:** *"let's keep in test only for now, and punch-list the possible need thru API."*
- **So.** `testGetFollowing()` stays TEST-USE. The drive and the steering object **use** the reading
  internally — for correction 2's hold at the achievable rate, and for section 3's path-preserving
  speed limiting — and no public member reports it. The possible public query (`isFollowing() :
  bFollowing, bMeasured`, "following" at ≥ 90 % of commanded) is **PL-102**.
- **Consequence for the other release notes:** none of C-2, C-4 or C-7 may point a user at a member
  that does not exist, so their lines say what the drive does and stop there.
- **Release note:** none.

### C-7 · The documented speed range

- **Status after this change.** `power` [−100..100] is a **commanded speed**, mapped linearly onto a
  per-voltage increment table (`incrementForPower()`, `:2438`).
- **What it guarantees:** unloaded, the rotor meets it to 0.2 % across the whole range at 18.5 V.
- **What it does not guarantee:** the top ~45 % of the range (rung 6 of 11 up) runs with **no torque
  margin**, so under load it will not be met. The published speeds are ~4 % high (MEASURED 1,913
  passes/s against the 2,000 they assume — manual §6.1).
- **Release note:** *"The power range is a commanded speed. Unloaded it is met across the range; the
  upper part runs with little torque in reserve, so under load a motor may fall short."* The ~4 %
  correction is already «#3515»'s.

---

## 3. Two wheels

**What the steering object does today.** It has **no wheel-to-wheel matching**. It commands both
wheels open-loop — the same power scaled by direction — releases them together with one `ATN`, and
tracks each wheel's distance for its stops (`isp_steering_2wheel.spin2`, `frontDriveWheels()` `:2079`;
78 public methods). So a platform keeps its commanded path only while **both** motors follow.

**The consequence of C-4.** A wheel holding "the fastest rate it can sustain" while its partner follows
**changes the platform's path**: a turn tightens or opens, and a straight line curves. Nothing reports it
today.

**Ruled: path over speed.** STEPHEN 2026-09-22: *"yes path over speed"*. Chosen over *speed over path*,
where each wheel does its best independently: cheaper, but the platform then goes somewhere nobody
commanded, and with C-6 test-only nothing would report it.

**Path-preserving speed limiting.** When either wheel cannot follow its command, the steering object
scales **both** wheels' commands by the slower wheel's achievable fraction. The platform keeps its
direction and loses speed. `driveDirection()`, `driveAtPower()` and `driveForDistance(left, right)`
all promise a path by their names, and this is what keeps that promise.

- **What to call it, and what not to.** It is **wheel-speed desaturation** in robotics terms: scale
  every wheel by one factor so the ratio survives. It is **not traction control**. The halls measure
  wheel rotation, not ground motion, so a wheel that slips spins freely, meets its command and looks
  healthy. Traction control needs a ground-speed reference this platform does not have. Nor is it
  *adaptive* drive, which retunes a controller; this limits one. The user documents call it
  **path-preserving speed limiting**.
- ⚠ **Its cost — «#3589» designs against it, «#3583» builds it:**
  - It closes a loop on the following reading, which lags by up to its 1 s window. At that lag the
    platform can veer for up to a second before the correction takes hold. A shorter or partial window
    is the fix, and it is the same change as «#3597»'s option (a) — design them together.
  - It runs in the **steering front cog**, the tightest budget in the design (section 4.2). Measure
    that cog's pass time today, with `updateFollowing()` in it, before designing the loop.
  - It must release the scaling when the slow wheel recovers, without hunting between the two.
- **Release note:** *"When one wheel cannot keep up — one side loaded, say — the platform now slows both
  wheels together, so it keeps the path you commanded instead of curving off it."*

**The re-export rule.** Neither ruling adds a public enum. Any `DS_*` or `ERR_*` that «#3589»
introduces must be mirrored as a `CON` alias in `isp_steering_2wheel.spin2`, or callers cannot name it.

---

## 4. Space and time the change has to fit in

### 4.1 Driver cog RAM — 25 longs free

MEASURED 2026-09-22, and the method is the point.

- **The method.** `pnut-ts -l isp_bldc_motor.spin2`. The symbol table gives each DAT label's cog address
  in the **top 12 bits** of its VALUE.
- **Cog RAM:** `DRIVER` is at `$000`; the last cog-resident long, `DUTY_CAPPED_`, is at `$1D6`.
  **471 of the 496 `fit` allows are used — 25 free.** («#3600»'s start seed took 8 of them and was
  removed after Visit 7c pass 2 showed it did not remove the surge.)
- **LUT:** `LUTCODESTART` `$200` to `LUTCODEEND` `$27B` — **123 of 512 used, 389 free.**
- **The old `fit` comment claimed "~400 used", hand-counted from source** — about 80 short. That is
  why the count is now read from the compiler, and the comment says so.

**What that means for «#3583».**
- **Cog RAM is spent only on the 43.9 kHz loop's hot path.** Everything that runs per start, per
  command or per drive pass (~1,913/s) belongs in the LUT block, which the start sequence,
  `gettgtincr` and `driveinit` already use.
- **Count again before adding,** by the method above.

### 4.2 Front cogs — one has room, one does not

MEASURED at `2026-09-19/debug_260919-172627.log`, `BM-FRONTST` (src_rev 20, part D):

| Front cog | Worst pass | Slot | Headroom | Late passes |
|---|---:|---:|---:|---:|
| Single wheel (`isp_bldc_motor`) | 299 µs | 1,000 µs | **70 %** | 0 of 17,700 |
| Steering, both wheels (`isp_steering_2wheel`) | 914 µs | 1,000 µs | **8.6 %** | 1 of 33,195 |

⚠ **Both predate `updateFollowing()`** (`31c8b91`, 2026-09-22): one `muldiv64` per wheel at the 125 Hz
slot rate. **The steering cog's figure today is unmeasured.** The next part-D run re-measures it, and
until then 8.6 % is an upper bound on what is left.

**What that means.** Anything section 3's "path over speed" adds to the steering front cog has to fit
in under 86 µs of worst-case pass, less whatever `updateFollowing()` now costs. That is the tightest
budget in the design, and it is measured before building, not after.

---

## 5. The drive change — written by «#3589»

Sections 1 to 4 are carried in. Two are amended, with the reason given where each changes: §1.1's
H-3 line (answered) and C-1's second reason (§5.3 D-4 removes the discard it cited; the decision
stands).

**The evidence base.** Two sources:
- **The logs, read directly:** the eight START traces (pass 1 `debug_260921-224820.log`, pass 2
  `debug_260922-122752.log`) and the pass 2 ladder in the same log.
- **A desk model of the shipped drive**, kept with this plan in [`servo-model/`](servo-model/). It
  runs the servo exactly as the PASM does, frame by frame at 44 kHz. The ramp and the lag limiter
  run per drive pass. The hall angle is held per sector, as the driver holds it. The motor is an
  R-only voltage-mode dq model with one inertia and coulomb plus viscous loss.
  - Its back-EMF constant comes from the ladder.
  - **One parameter is fitted:** the physical angle at which the servo's mean error sits.
  - Inertia and winding resistance are estimates, and **§5.2 shows that the conclusions hold
    with each halved and doubled.**
  - Everything the model says is **DERIVED**. The bench certifies it (§5.6).

### 5.1 What the servo actually is — MEASURED, from the source and the traces

1. **It runs every PWM frame, 44,000 times a second,** not once per drive pass (`:4596-4600`, inside
   `.ctlMotor`).
2. **It is a relay, not an 18 : 4 proportional gain.**
   - Below the setpoint, `((|e| − 42) × 4) SAR 8` is **exactly −1 for every |e| from 0 to 41**,
     whatever the error. `duty_dn = 4` has no effect beyond that −1.
   - Above the band, `duty_up = 18` gives +1 at |e| 57–70, +2 at 71–84, and so on.
   - The traces show it: duty moves ±88 per 2 ms sample, which is **±1 per frame** (pass 2 tid 1,
     k = 2…14 at |e| 58, then k = 16…30 at |e| 15).
3. **Its input is a 43-count sawtooth.** The hall angle is held for the whole sector, so the error
   climbs by one sector (256/6 = 42.7 counts) and drops back at every edge. The band is 15 counts
   wide, so the error sweeps straight through it every sector.
4. **At running speed that sawtooth dithers the band into a point.** Mean |e| is **48 counts (67.5°)**
   at every ladder rung from 40 to 120 × 10⁶, both motors, both directions. It is **45** at 20 × 10⁶.
   So PL-101's band is real for a slowly changing error, and at running speed it averages away.
5. **Steady duty is proportional to speed.** It runs **167–174 duty counts per 10⁶ of increment** at
   rungs 3–7 on both motors. That is the back-EMF line. It also equals `duty_max` divided by the
   18.5 V ceiling increment: 24,264 / 147 × 10⁶ = **165 per 10⁶**.

### 5.2 Why it hunts — the mechanism, and the rival it beats

**The mechanism (DERIVED).** The rotor's torque is `Va·sin δ − E` over the winding resistance, where
δ is the voltage's angle from the magnets.
- Its **stiffness** is the rise in torque per degree of lag, `Va·cos δ`. That is small near
  δ = 90° and proportional to duty.
- The servo is **integral-only** on the lag.
- An integral loop around a damped inertia with a spring, `J s³ + D s² + k s + K`, is stable only
  when `D·k > J·K`. **At low duty the stiffness k is too small for the servo's gain, so the loop
  limit-cycles.**

A start ramps straight through that low-speed region, so the start surge is that limit cycle.

**The model reproduces the whole picture from its one fitted parameter.** The fit puts δ at about
79° at the servo's mean error (bracket 76°–84°, e90 = 52–60).

| | Measured (shipped drive) | Model (shipped servo) |
|---|---|---|
| Steady 10 × 10⁶: duty, peak | 2,020, 2,840–3,310 | 2,011, 2,697 |
| Steady 20 × 10⁶: duty, peak, err_pk | 3,850, 5,300–5,580, 87–89 | 3,864, 4,911, 81 |
| Steady 40 × 10⁶ and up | calm, err_pk 71–75 | calm, err_pk 71–72 |
| Mean error at 40–120 × 10⁶ | 48 | 48.7 |
| First rotor ticks, QTR start (samples) | 115, 175, 211, 236 | 145, 190, 220, 244 |
| Duty leaves its floor for good | k ≈ 232–250 | k ≈ 240 |
| Hunting during acceleration | 3,600 ↔ 6,200–7,000, ~150 ms | 3,000 ↔ 7,700, 120–180 ms |

**The rival, and the reading that separates them.** Pass 2 named two suspects: PL-101's band and the
18 / 4 asymmetry. The model removes both — a symmetric integral with no truncation, about the same
point — and **it still hunts at the shipped servo's effective gain** (0.05 duty per count per frame:
20 × 10⁶ peaks at 4,447 against a mean of 3,785). It stops hunting only when the gain falls below
what the stiffness supports (0.02). **The band and the asymmetry are not needed to produce the
surge; the gain against the stiffness is.**

The bench already carries the reading that tells the mechanism from the other rival pass 1
entertained: *"the servo lags the ramp's rising voltage demand"*. That story needs a ramp. **The
ladder's steady rungs 1–2 hunt with no ramp at all** — duty peaks 40–60 % above the mean at constant
speed. MEASURED. A ramp-lag mechanism cannot produce that. A stiffness-limited loop does.

**What the model does not settle.** Its current is a proxy (DC-link power over the bus), so current
predictions are ratios, never counts. Its δ is fitted, not measured.

### 5.3 The change

**D-1 · Feedforward duty.** Each drive pass, `duty_ff = |drv_incr| × duty_max / ceiling_incr`.
- The ramp's rising voltage demand then no longer has to be integrated up by the servo.
- The ceiling increment is the one the power table already carries for this motor and voltage, so
  **no new per-motor constant is introduced**. Across the 11.1–22.2 V rows it matches the measured
  18.5 V line, scaled by voltage, within 2.5 %.
- It is computed once at `init()`, before the cog starts, and patched into the driver image as the
  hall tables are. It is not a new params-block long, so the ABI is unchanged.
- For the Doco motor it is derived the same way and **not certified**; that motor is not on the
  bench.

**D-2 · The trim servo — symmetric, untruncated, gain scheduled on duty, one anti-windup for every
limiter.** Each frame:
- `acc += (|e| − SETPOINT) × duty`, a 32-bit accumulator;
- `duty = duty_ff + acc SAR 18`;
- then the existing current fold-back, `duty_cap_` and `duty_min_` clamps, **unchanged**;
- then, **if any of them changed duty**, `acc` is re-derived from the applied duty, so the trim never
  holds what a limiter refused.
- The multiply by duty makes the gain proportional to the stiffness the rotor has. `SAR 18` is
  1/32 per count per frame at duty 8,192.
- **This removes PL-101's band and the relay by construction.** One value, one meaning: the
  setpoint is a point.

| Model, every variant (J and R halved and doubled, δ fit ±4, three times the friction) | Shipped | D-1 + D-2 |
|---|---|---|
| Steady duty swing (peak − mean), 10 × 10⁶ | 409–1,624 | **46–153** |
| Steady duty swing, 20 × 10⁶ | 212–2,271 | **40–88** |
| START: largest duty drop from its running maximum during acceleration | 0.21–0.44 | **0.01–0.04** |
| START: current peak ÷ settled current | 1.84–14.6 | **1.13–2.57** |

Feedforward with the shipped servo kept as the trim was also run. It halves the start peak, but it
leaves steady rungs 1–2 hunting exactly as today. **D-1 is not enough without D-2.**

**D-3 · Which knob carries the lead — decision (a).** **The commutation offset carries it:**
`L = 18`, `Z = −4`, the shipped 14 / 338 pair, **unchanged**.
- `SETPOINT = 48` counts (67.5°). That is **the mean the shipped servo already settles at**, at every
  rung where L was measured and tuned (the quarter is rung 3's neighbour; both read 48).
- **So total steady field placement at the quarter is unchanged, and nothing is corrected twice.**
  The setpoint does **not** move toward the designer's 90°. The scan's offset correction already
  made that correction (manual §3.3), and making it again would add ~55° into the steep basin.
- The one placement change is at low speed. The shipped servo averaged 45 there; the new one holds
  48 everywhere, **+3 counts (4.2°) more lead at about an eighth**. D-7 carries the consequence.

**D-4 · Every command is accepted in every state — PL-104.** The driver now throws a new speed away
unless it is `STOPPED`, `AT_SPEED` or `FAULTED` (`:4160-4167`).
- A wheel whose ramp is waiting on its rotor stays in `SPIN_UP`, and **cannot be commanded slower**
  (only stop gets through). That breaks the API's promise (doctrine P3), and it would silently
  defeat D-5 and D-6.
- `.newRqst`'s own branches already handle a change from any running speed and either sign
  (`.doSpdChange`, `.notSame`). So the fix **removes** the busy test and adds nothing.
- PL-78's re-arm of `ramp_curr` still happens once per request. A stream of scale-downs uses the
  ramp-down rate (fast); a release uses the gentle ramp-up (slow). That is the asymmetry D-6 wants.
- **C-1 stands**: `AT_SPEED` keeps its ramp-completion meaning. Its second reason ("a measured
  AT_SPEED would discard every command") is now moot, not wrong. The first reason — one value, one
  meaning — carries it alone.

**D-5 · Correction 2: hold at the achievable rate.** Today the lag limiter already stops the field
advancing at `LAG_HOLD`, so the field's rate matches the rotor's. But `drv_incr` keeps the commanded
value. When the load releases, the field resumes at full rate in one pass, which is a kick.
- **The change:** on every held pass in `SPIN_UP` or `AT_SPEED`, `drv_incr −= drv_incr SAR 6` (a
  33 ms time constant at 1,913 passes/s), and the state becomes `SPIN_UP`.
- A ramp-down or a direction change is never re-labelled. A stop in progress stays a stop.
- The field's rate then settles at the rotor's achievable rate. Recovery is the ordinary ramp back
  up, never a step.
- `lag_held` keeps counting, so the observable is unchanged.

**D-6 · Path-preserving speed limiting, in the steering front cog.** Each 8 ms slot:
- **A wheel is short** when its `lag_held` advanced in the last 4 slots.
- **Its achieved fraction** is then `|drv_incr_now| ÷ |commanded|`. Both are already in the status
  block, and after D-5 the fraction is exact and immediate.
- While either wheel is short, both wheels are commanded at the lower wheel's fraction. The scale
  releases by 2 % per slot, about 0.4 s to full, only after 4 clean slots. Down fast, up slow, so
  it cannot hunt between the two.
- **This does not need a shorter hall window.** The 1 s window lag named in §3 as this loop's cost
  is gone, because the drive's own hold counter reports the shortfall at slot rate. So «#3597»'s
  option (a) is no longer needed for the limiter; «#3597» is free to choose (b) or (c) on its own
  merits.
- `testGetFollowing()` stays as the independent reading and the TEST-USE observable (C-6).
- **Budget:** the limiter runs once per slot and costs two status reads, two compares and, only
  while active, one `muldiv64` per wheel. It is measured, not assumed (§5.4).

**D-7 · The speed law for L — a CANDIDATE, not designed in; Stephen decides, from §7's benefit
measure.** As designed, L stays the compile-time quarter tune.
- **Pass 2's band hypothesis (P2-10) is answered, and it is not the law.** The ladder's mean error
  moves 45 → 48 between about the eighth and the quarter. That is 4.2° in the direction that lowers
  L as speed rises: **about a third of L's measured 12.2°, of the right sign**. D-2 now holds 48 at
  every speed, so that third is removed by construction and the rest stays H-2.
- **What building it would face:**
  - The half rung has not been bracketed (H-5).
  - A two-point schedule would be tuned against the shipped servo's low-speed placement, which D-3
    changes by 4.2°.
- **What it would buy** is §7's row C-A.

**D-8 · Back-EMF as a position source — a CANDIDATE, not designed in; Stephen decides, from §7.**
- **What it would give:** a finer angle, either to interpolate within a sector for a proportional
  term or to hold the field at the torque peak.
- **Nothing here needs it.** D-1 and D-2 remove the hunting with the sector-resolution angle.
- **Interpolation is not free where it would be wanted.** Hall-timing interpolation plus a P term
  tightens the error from 27–70 to 46–50 in the model, but hunts again at 10 × 10⁶ at higher gain.
  The model has no cogging, which swings speed ±30 % between edges at the bottom of the range
  (§1.1). A back-EMF angle is unmeasured below 43 edges/s and **unmeasured while the bridge drives
  at all**.
- **The next discriminating measurement, if it is reopened:** per-phase samples during driven
  rungs 0–2. The harness sums them today.
- **The robustness front this release advances instead:** the drive acts on its own shortfall (D-5)
  and the steering object on both wheels' (D-6).

**D-9 · What does not change, and why:**
- **The ramp shape** (`ramp_min`, `ramp_inc`, `ramp_max`).
- **The PL-55 ramp-down duty ceiling.** With D-1 it may never bind. Visit 8's speed-down cells read
  `duty_capped` over each ramp-down, and if it never counts, the ceiling is removed then (D5), not
  now.
- **`LAG_SOFT` and `LAG_HOLD`.** In the fitted frame they sit at δ ≈ 124° and ≈ 152°, well past the
  torque peak, so an overloaded motor is held at about half the torque it could make. But the
  sawtooth rides ±21 counts on the error, and the shipped servo's steady `err_pk` is already 71–75.
  **A threshold near the peak would trip in normal running.** Only a sub-sector angle could place it
  there. **PL-105** records it, and the loaded floor run measures what it costs.

### 5.4 Space and time

| Part | Where | Longs, estimated from the instruction sketch |
|---|---|---|
| D-1 `duty_ff` per pass (`abs`, `sca`, store) + its constant | LUT | +4 of 389 free |
| D-2 accumulator, scheduled multiply, anti-windup re-derive | cog, hot path | +7 of 25 free |
| D-4 busy test removed | cog | −5 |
| D-5 decay and state on a held pass | cog, `.justIncr` | +4 |
| **Net cog RAM** | | **about +6, leaving ~19** |

- **«#3583» counts from the compiler** (§4.1's method), before and after. An estimate is not a count.
- **The per-frame cost is two instructions over today's servo**: one multiply and the anti-windup
  test. It sits inside the 22.7 µs frame, and «#3583» confirms `loop_dtcks` does not move beyond
  noise.
- **The steering front cog** is the budget that could fail. Its headroom was 8.6 % before
  `updateFollowing()`. «#3583»'s first part-D run reads `BM-FRONTST` with D-6 in place, and §5.5
  A-10 judges it.

### 5.5 Acceptance numbers

Every number is **unloaded, wheels up**, with the loaded expectation beside it. Every criterion
fails on today's drive: the "shipped" column is **MEASURED** from the logs named in §5 unless marked.

| Id | Criterion (new drive, Visit 8) | Shipped | New, predicted | Loaded expectation |
|---|---|---|---|---|
| **A-1** | START (QTR, ±36.75 × 10⁶, both motors, 4 traces): the largest fall of duty from its running maximum, between duty leaving its floor and `AT_SPEED`, **≤ 0.10** | **0.34–0.53** (8 traces) | 0.01–0.04 | ≤ 0.10 (model with 3× friction: 0.02) |
| **A-2** | START current peak ÷ mean current over the trace's last 60 ms, **≤ 1.8** | **1.94–3.04** | 1.13–1.80 (2.57 at the δ bracket's edge) | ≤ 1.8 |
| **A-3** | Steady rungs 1–2 (10 and 20 × 10⁶): `duty_pk − duty` **≤ 400** and `err_pk` **≤ 76** | 800–1,650 and 75–89 | 40–153 and 69–72 | same |
| **A-4** | Mean `err` at every rung 1–8 is **47–49** — a point, not a band | 45 at rung 2 | 48 | same |
| **A-5** | Rungs 3–8 do not regress: steady `duty` and `inet_x10` within **±5 %** of pass 2, `rate_x10` within **0.5 %** of `pred_x10` | the pass 2 ladder | unchanged | n/a |
| **A-6** | A speed-DOWN issued during `SPIN_UP` (quarter, then an eighth at 0.3 s) takes effect: `drv_incr` starts falling **within one drive pass** of the command | **discarded** (read from `:4160-4167`; the cell fails on today's binary) | accepted | same |
| **A-7** | Held at a driven-off offset where the drive cannot follow — the scan's current-wall offset, where it measured 44–47 % following — **`drv_incr_now` settles within 0.2 s** at a rate within 10 % of the measured tick rate, and recovery after the offset is restored meets A-2 | holds `drv_incr` at the command | settles | the floor run's one-sided load |
| **A-8** | The two following readings agree: D-6's fraction against `testGetFollowing()` within **5 points**, once both are valid, on both a following and a not-following case | n/a — D-6 is new | agree | same |
| **A-9** | Driver cog RAM free after «#3583» **≥ 10 longs**, counted from the compiler | 25 | ~19 | n/a |
| **A-10** | Steering front cog worst pass **≤ 950 µs**, `late` 0 over the run | 914 µs (before `updateFollowing()`) | unknown — measured | n/a |

**Why swing amplitude, and not duty timing.** Pass 1 judged duty timing, which both explanations
predicted. A-1 and A-3 judge **amplitude**, which the stiffness-limited loop produces and a correctly
fed, correctly gained servo does not.

**Honesty about A-2.** The model's current is a proxy. A-1 is the primary judgement of the START, and
A-2 corroborates it.

### 5.6 The two certifications

1. **Visit 8 («#3584») — wheels up, A-1 to A-10.**
   - It carries the START trace and the ladder as they stand, plus three new cells: A-6's mid-ramp
     command, A-7's forced shortfall, and A-8's agreement.
   - **A-6 and A-7 each have a built-in negative case:** the shipped binary fails both by
     construction, and the run sheet shows that before the visit.
2. **The loaded floor run («#3591», at «#3576»).** It judges:
   - A-1 and A-2 under load;
   - whether rungs 1–2 hunt loaded (A-3);
   - what a hold at `LAG_HOLD` costs in current (PL-105);
   - D-7's low-speed current in amperes;
   - D-6 on a platform, the one place a wheel can genuinely fall short with its partner following.

## 6. What «#3589» decided, in one table

| Decision | Decided | Where |
|---|---|---|
| (a) Which knob carries the lead; point or band | The offset carries L (unchanged). The servo holds a **point**, 48, by construction. | §5.3 D-2, D-3 |
| (b) The start surge | **Mechanism:** an integral-only servo whose gain exceeds what the rotor's low-duty stiffness supports. **Fix:** feedforward plus a duty-scheduled, untruncated trim. **Separating reading:** steady rungs 1–2 hunt with no ramp; START amplitude A-1. | §5.2, D-1, D-2, A-1, A-3 |
| (c) The speed law for L | The band explains a third of it, and D-2 removes that third. A schedule for the rest is **a candidate for Stephen**, priced in §7. | §5.3 D-7, §7 C-A |
| (d) Back-EMF | Not needed by D-1 to D-6. Integrating it is **a candidate for Stephen**, priced in §7. | §5.3 D-8, §7 C-B |
| Path over speed, and its lag | Limited from the drive's own hold counter at slot rate, with no 1 s window. | §5.3 D-5, D-6 |
| Whether §1.4's bus reading is real | Unchanged: unverified, not designed on. | §1.4 |

## 7. Every driver function on the table, and what it buys — for Stephen's release decision

**What goes into the outgoing release is Stephen's decision** (doctrine overlay P5). This section prices
every function: the ones §5 designs in, and the candidates it does not.
- **Benefit** is stated in what a user would feel: current, torque, the size of a surge.
- **Sureness** is stated the same way throughout: **measured** (a log says so), **modelled** (the desk model
  says so, fitted on one parameter), or **unknown**.
- **What would firm it up** names the cheapest measurement that turns a modelled or unknown benefit into a
  measured one.

**One fact frames the whole table.** Unloaded, the drive never runs short. Zero held passes at every rung
and every transition of the pass 2 ladder: `BM-RUNGHL` `tr_lag,0` and `win_lag,0` on all 178 records.
MEASURED. **So every function aimed at overload shows no benefit wheels-up**, and its benefit is
whatever the loaded floor run finds.

### 7.1 Designed in by §5

| Id | Function | Benefit | Sureness | Cost | What would firm it up |
|---|---|---|---|---|---|
| **D-1 + D-2** | Feedforward duty and a stiffness-scaled trim | **The start surge and the low-speed hunting go.** Duty's fall during acceleration drops from 34–53 % to 1–4 %. Start current peak drops from 1.9–3.0× settled to 1.1–1.8×. At 10–20 × 10⁶ steady, duty swings of 40–60 % above the mean become under 5 %. This is the surge the manual says you can feel through the frame. | Today's numbers **measured**; the new ones **modelled** | ~+5 cog longs, +4 LUT | Visit 8, A-1 to A-4 |
| **D-4** | Accept every command in every state | Easing off a motor that is still spinning up works. **Today the command is silently ignored.** | Defect **read from the source**; the shipped binary fails A-6 | −5 cog longs | Visit 8, A-6 |
| **D-5** | Hold at the achievable rate | No lurch when an overload releases: the field ramps back instead of stepping to full speed. **None unloaded.** | Mechanism **read from the source**; size under load **unknown** | +4 cog longs | Visit 8 A-7 (forced), then the floor run |
| **D-6** | Path-preserving speed limiting | When one wheel falls short, the platform slows instead of curving off its path. **None unloaded.** How often it matters in real use is **unknown**. | **Unknown** until loaded | Steering front-cog time, not yet measured (A-10) | The floor run, and a one-sided load |

### 7.2 Candidates — not designed in

| Id | Function | Benefit | Sureness | Cost | What would firm it up |
|---|---|---|---|---|---|
| **C-A** | **Speed-dependent lead angle** (L scheduled on speed, set from the front cog; no PASM change) | **Below the quarter:** at an eighth, net current 14–17 mV at the shipped pair against 8.7–10.6 mV at the best offset (`debug_260921-223111.log`, both motors, both signs), 1.7× on paper, **about 0.04 A**. **At the quarter:** none, because the shipped pair is the quarter's optimum. **Above the quarter, where the current is:** unknown. Net current at the shipped pair climbs 25 → 45 → 73 → 112 mV (0.17 → 0.75 A) across 60–120 × 10⁶. If L keeps falling as it does below the quarter, the shipped 18° over-leads there by ~10–15°. At the quarter, 10° of over-lead costs 1.8–2.7× and 15° costs 3.0–4.6× (the same scan, both signs). So it **could** be several tenths of an ampere at cruise. That is an extrapolation, not a reading. | Below the quarter **measured**; above it **unknown** | Small, and no PASM change. **Built as:** a table of L against speed from measurement, interpolated linearly in log-speed between measured points (the measured law is ~12.2° per doubling) and held flat outside them, never extrapolated. It is keyed on `drv_incr_now`, so it follows ramps. The front cog writes `offset_fwd = Z + L` and `offset_rev = Z − L` every 8 ms slot; the driver re-reads its params block every frame. That is under 1° per update at the steepest ramp. **Only L moves; the servo setpoint never does** (§3.3's trap). It costs one lookup per wheel per slot, which counts against the steering cog's headroom (A-10). | **One run both prices it and fills the table**, taken after D-1/D-2 land (the shipped servo sits 4.2° differently at low speed): hold each rung at steady speed and **step L live** (18, 13, 8, lower while current still falls), reading net current per step. Do not restart at each value. The scan's half-rung torque bound (swept 23) conflicts with today's ladder running swept 14 at 60–80 × 10⁶, and the scan's per-point start is a suspect for that (a hypothesis). |
| **C-B** | **Back-EMF as a position source** | (1) Enables C-D. (2) **A second set of position marks, not a continuous angle.** Each phase's zero crossings give 6 marks per electrical cycle, about 34° into each hall sector (the pass 2 frame: peaks at 64.2°/184.4°/305.1°, crossings ±90° from them). Together with the hall edges, that is a mark roughly every 30° instead of every 60°. Each mark is timed to **2–5° electrical** (0.13–0.33° of wheel), measured coasting. Between marks the angle is still interpolated by timing. A continuous angle would need the waveform's amplitude, which the clipped negative half-waves make unusable as the channels stand. (3) A fallback if a hall fails, **but the halls have never missed or given an illegal code on any run**, so that benefit is nil on the evidence. | **Unknown**: back-EMF has never been read while the bridge drives, nor below 43 edges/s | **High, and structural.** **While driving, the drive senses back-EMF 0 % of the time.** All three phases are PWM-driven every frame, and each ADC reading counts over a whole frame (`P_COUNT_HIGHS`, p2kb `p2kbArchSmartPin01111CountHighsOptionalDec`), so it reads the applied average: the constant ~2.38 V phase sum of §1.4. Sensing while driving needs one of two things. **(i) Release windows:** all six FETs off, winding current drained through the body diodes, then one whole 22.7 µs frame read. That is ~45–70 µs per look (inductance unmeasured), near each of 6 crossings per electrical cycle: ~100/s at the quarter (0.5–0.7 % of the time released) and ~400/s at the top (2–3 %). Each window costs torque and a regen pulse, and likely an audible tick. **(ii) Six-step drive,** which floats one phase a third of the time, giving up sinusoidal drive. The signal also scales with speed: ~1 V peak at 43 edges/s and ~65 mV at the slowest command (DERIVED from the ladder's back-EMF line), against ~5 mV of noise. | **First, whether a clean window exists: a release-window capture.** Release the bridge for ~10 frames at a few speeds, wheels up, and capture the phase pins through the release in `P_ADC_SCOPE` mode (a filtered sample every clock, ~5–6 effective bits, p2kb `p2kbArchSmartPin11010AdcScopeTrigger`). The diode-clamped decay shows as a rail reading and then its departure from the rail. The capture yields decay time, settle time and the clean window against current, none of which is known: winding inductance has never been measured, and the board's phase-sense filtering is not in any document we hold. Then per-phase samples during driven rungs 0–2. Both need harness code and a run. |
| **C-C** | **Hall-timing interpolation** (the angle inside a sector, from the last edge's timing) | Enables C-D above the lowest speeds. In the model, the servo's error band tightens from 27–70 to 46–50. Its benefit to a user, beyond C-D, is not quantified. **At the bottom of the range it misleads:** cogging swings speed ±30 % between edges (MEASURED). | Tightening **modelled**; low-speed limit **measured** | Moderate: ~8–10 cog longs | Only worth measuring if C-D is wanted |
| **C-D** | **Hold an overloaded motor at the torque peak** (PL-105) | **About 1.8–2.7× today's pull when a wheel is overloaded**, as when climbing or pushing against an obstacle. Today the hold sits at δ ≈ 146–158°, where sin δ is 0.37–0.56 of the peak. It also means less current wasted while held. | **Modelled** on the fitted frame; the δ bracket is the fit's own spread | Needs C-B or C-C first | **The floor run:** how often and how long a wheel sits at the hold in normal use. If never, the benefit is theoretical. |

### 7.3 Stephen's decision, 2026-09-22

- **C-A, dynamic lead: IN.** «#3583» builds the mechanism with the table flat at L = 18, plus the live
  L-step tier. Visit 8 («#3584») measures the table, and «#3601» fills it and makes the final
  adjustments.
- **C-B, back-EMF: DEFERRED** to a delta release after 6.0.0 («#3602»). C-D and C-C go with it.
- STEPHEN: *"My current thinking is to defer back EMF. Let's go with dynamic lead. Let's build the driver
  as you need to now so we can do the testing to calculate dynamic lead, and then we'll make final
  adjustments once we understand the results from the testing."*

**Sequencing note for the decision, not a recommendation of scope.**
- C-A's firming run needs no driver change, so its benefit can be measured before anything is built.
- C-D's value hinges on one number the floor run produces.
- C-B's feasibility hinges on a measurement no run has attempted yet.

---

## Revision history

- **2026-09-22** — sections 1 to 4 written by «#3596». Section 5 names «#3589»'s scope.
- **2026-09-22** — Stephen's two rulings: C-6 stays TEST-USE (PL-102 records the possible API), and
  section 3 is path over speed, named path-preserving speed limiting.
- **2026-09-22** — after Visit 7c pass 2: §1.3 now carries the back-EMF measurement; §4.1 recounted
  after the start seed was removed (25 free); §5's start-transient row now reads the servo hunting,
  and back-EMF's row is answered for coasting.
- **2026-09-22** — «#3589»: §5 replaced by the drive change (D-1 to D-9), its acceptance numbers
  (A-1 to A-10) and the two certifications; §6 summarises the four decisions. §1.1's H-3 line
  answered and the Z row given both values. C-1's second reason is moot under D-4, while the
  decision stands on its first. The desk model is kept in `servo-model/`.
- **2026-09-22** — Stephen: release scope is his, and every candidate function comes with a measure of
  benefit. D-7 and D-8 are re-worded as candidates, and §7 prices every function, designed-in and
  candidate, for his decision.

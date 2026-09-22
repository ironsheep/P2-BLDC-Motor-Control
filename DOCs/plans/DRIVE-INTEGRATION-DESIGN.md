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
| The hall zero sits at **Z = −3.6 ± 0.4°** and does not move with speed. | MEASURED: four scan self-locations — `MOTOR-6.5IN-TECHNICAL-MANUAL.md` §3 |

**What the halls cannot tell:**
- **Where the rotor is inside a 60° sector.** The field free-runs between edges (PL-95).
- **Anything fast at low speed.** At 1×10⁶ an edge arrives every 278–448 ms, and the rotor's
  instantaneous speed swings about ±30 % between edges from cogging. MEASURED: study §6.3, F12.
- **Whether the six sectors are equal.** Hole H-3; the ALIGN tier measures it at Visit 7c pass 2.

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

### 1.3 Phase voltages as a rotor-angle source — OPEN

The three phase-sense channels are read and scaled every frame and reach nothing but the status
block. Whether they carry usable rotor angle between hall edges, and down to what speed, is the
question the ALIGN tier gives its first real reading on (hand-turned back-EMF). **Left open here by
design** — «#3589» settles its row from that tier.

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

### 4.1 Driver cog RAM — 17 longs free

MEASURED 2026-09-22, and the method is the point.

- **The method.** `pnut-ts -l isp_bldc_motor.spin2`. The symbol table gives each DAT label's cog address
  in the **top 12 bits** of its VALUE.
- **Cog RAM:** `DRIVER` is at `$000`; the last cog-resident long, `DUTY_CAPPED_`, is at `$1DE`.
  **479 of the 496 `fit` allows are used — 17 free.**
- **LUT:** `LUTCODESTART` `$200` to `LUTCODEEND` `$27B` — **123 of 512 used, 389 free.**
- **Before «#3600»** `DUTY_CAPPED_` was at `$1D6`: 25 free. The start seed cost 8.
- **The old `fit` comment claimed "~400 used", hand-counted from source** — about 80 short. That is
  why the count is now read from the compiler, and the comment says so.

**What that means for «#3583».**
- **Cog RAM is spent only on the 43.9 kHz loop's hot path.** Everything that runs per start, per
  command or per drive pass (~1,913/s) belongs in the LUT block, which the start sequence,
  `gettgtincr` and `driveinit` already use.
- **8 longs are recoverable now:** `.startFromRest` runs once per start, so it can move to the LUT.
  `.checkstopfloaton` would then need a global label.
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

## 5. What «#3589» decides — named here, not settled

| Decision | Waits on | State 2026-09-22 |
|---|---|---|
| **Which knob carries the lead** | ~~the setpoint A/B~~ | The A/B is **retired**: the field sits at the commanded angle and the servo integrates to its setpoint, so setpoint and lead combine **by construction** (`:4467-4474`, `:4591`). What is left is PL-101: the servo holds a **21° band** (|err| 42–56), not a point, because its gain truncates. Whether the drive should hold a point is «#3589»'s call. |
| **The start transient** | the START trace | **Mechanism answered** (Visit 7c, 4 of 4). The fix is built («#3600», `4014b92`) and is certified by Visit 7c pass 2 load 2. Its size **under load** waits on the floor run. |
| **The speed law for `L`** | `L` at a half (H-5) | Never obtained in five attempts; a candidate to close as unanswerable on this rig. |
| **Back-EMF's usable range** (§1.3) | the ALIGN tier | Pass 2 load 1. |
| **Whether §1.4's bus reading is real** | one known-voltage reading | Found 2026-09-22, unverified. |

---

## Revision history

- **2026-09-22** — sections 1 to 4 written by «#3596». Section 5 names «#3589»'s scope.
- **2026-09-22** — Stephen's two rulings: C-6 stays TEST-USE (PL-102 records the possible API), and
  section 3 is path over speed, named path-preserving speed limiting.

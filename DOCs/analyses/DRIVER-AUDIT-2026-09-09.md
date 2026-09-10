# BLDC Driver Code Audit — 2026-09-09

**Type:** study. Findings are reported, not fixed — fixes are a separate sprint
(Stephen, 2026-09-09). Charter: [`DRIVER-AUDIT-CHARTER.md`](DRIVER-AUDIT-CHARTER.md).
Companion reference: [`DRIVER-THEORY-OF-OPERATIONS.md`](../../DRIVER-THEORY-OF-OPERATIONS.md).

**Scope read in full:** `isp_bldc_motor.spin2` (2392 lines today; 2359 when this audit was written -- the TEST-USE ONLY pass-throughs were added 2026-09-10 — Spin2 API, `taskPostionSense`,
the PASM2 driver), `isp_steering_2wheel.spin2` (909), `isp_bldc_motor_userconfig.spin2`,
`isp_dist_utils.spin2`, `isp_steering_serial.spin2`.

**Method note:** every claim about PASM2 or Spin2 semantics was verified against `p2kb-mcp`
before being written, per the project's `DOMAIN_AUTHORITY`. That discipline killed one
finding before it reached this page — see [Ruled out](#ruled-out).

**Field corroboration, 2026-09-09:** a user report of dual-motor faults arrived after this
audit was written and independently exercises four of its findings — see
[`user-report-2026-09-09-ANALYSIS.md`](user-report-2026-09-09-ANALYSIS.md). It raised three
further findings (AI, AJ, AK), folded in below.

**Entry baseline:** build clean, 0 warnings; `tools/build-check.sh` PASS, 39/39 files,
both release demos certified. No code was modified by this audit.

---

## Summary

**24 findings.** Six are defects a user can hit today without doing anything unusual. Three (AI, AJ, AK) were raised by a field report received after the audit was written.

| # | Severity | Finding |
|---|---|---|
| [M](#m) / [AF](#af) | **Defect** | A faulted motor reports `DS_MOVING` — end to end, including over serial |
| [W](#w) | **Defect** | All speed/RPM telemetry reads zero-or-negative (wrong variable in one line) |
| [AB](#ab) | **Defect** | `driveForDistance()` cannot turn; the documented feature is absent |
| [A1](#a1) | **Defect + HW hazard** | Dead-gap comparison uses the wrong enum. **REVISED 2026-09-10:** *both* boards specify a 250 ns minimum, so the per-revision distinction does not exist — the fix is to **delete the branch**, not repair the comparison (repairing it alone puts Rev B ~5× under spec) |
| [A2](#a2) / [A3](#a3) | **Defect** | User board-revision override is silently ignored; status string then lies |
| [N](#n) | **Defect** | DocoEng low-power floor computed from an unassigned sentinel |
| [F](#f) | **Defect** | `stopAfterDistance(_, DDU_M)` is 10× short |
| [O](#o) | **Defect** | `PWR_25p9V` passes validation, then aborts at init |
| [AD](#ad) | **Defect** | Motor cog start failure is never checked |
| [AE](#ae) | **Defect** | No validation that the two motors' pin groups don't overlap |
| [AC](#ac) | **Defect?** | Steering direction contradicts its own comment — needs hardware confirmation |
| [Y](#y) | Defect | `maxNeg` is neither max-negative nor the documented `1` |
| [Z](#z) | Feature-gap | Fault is a hard latch with no fallback strategy |
| [G](#g) | Defect | `setAcceleration()` is advertised as non-working but silently corrupts ramping |
| [C](#c) | Defect | `start()` return contract is wrong |
| [K](#k) | Feature-gap | Distance units you can read but cannot command |
| [P](#p) | Risk | Undocumented 2³⁰ ceiling on the drive increment |
| [H](#h) | Risk | `resetTracking()` blocks the calling cog ~200 ms (~400 ms via steering) |
| [I](#i) / [T](#t) | Risk | `abort()` used for parameter validation, including inside getters |
| [J](#j) | Latent | `stopAfterTime` wraps at ~49.7 days |
| [Q](#q) | Risk | `SyncStatus()` busy-waits with no timeout |
| [AI](#ai) | Feature-gap | Reverse commutation offset is derived, never characterized — one wheel of every 2-wheel platform runs on it |
| [AJ](#aj) | Feature-gap | The 6.5″ motor's offset ignores supply voltage *and* board revision; the DocoEng motor's does not. **REFRAMED 2026-09-10** — the hall path is identical across revisions, so the DocoEng table's per-revision split may be an S-3 instrumentation artifact |
| [AK](#ak) | Feature-gap | No voltage feedback — the power table is fixed at the *declared* nominal |

**Two long-standing README known-issues are now diagnosed**, not merely restated:
*"drive status reporting is not working in the base objects"* is [M](#m)+[AF](#af), and
*"motor can fault at higher load conditions"* is [Z](#z).

**Three root causes account for nine of the findings**, which is good news for the fix
sprint — they are cheaper to fix together than the count suggests:

- **Two parallel enum families for board revision** → A1, A2, A3
- **Near-identical names differing by one prefix letter** → W (`hallCntsIn8thSec` vs
  `nHallCntsIn8thSec`), and the same hazard class as N
- **A status vocabulary that cannot express failure** → M, AF, and half of Z's impact

---

## Defects

<a id="m"></a>
### M — `getStatus()` reports `DS_MOVING` while faulted or emergency-stopped
`isp_bldc_motor.spin2:568-578` · **Defect** · *README known issue, diagnosed*

```spin2
eStatus := DS_Unknown
if isStopped()                    ' drv_state == DCS_STOPPED only
    ... DS_HOLDING / DS_OFF
elseif isReady()                  ' drv_state <> DCS_Unknown — true for EVERYTHING else
    eStatus := DS_MOVING
```

`drv_state` can be `DCS_FAULTED` or `DCS_ESTOP`. Neither is `DCS_STOPPED`, and both make
`isReady()` true, so both fall into the `DS_MOVING` arm.

Two layers to this:

1. `getStatus()` ignores `isFaulted()` and `isEmergency()` — which exist at `:648` and
   `:663` and are correct.
2. The `DS_*` enum itself (`:51`) is `DS_Unknown, DS_MOVING, DS_HOLDING, DS_OFF`. **It has
   no value for faulted or e-stopped**, so even correct logic could not report them.

`isTurning()` (`:659`) *does* test all four conditions. The author knew the pattern;
`getStatus()` was never updated to match.

**Failure scenario:** a robot's motor stalls against an obstacle and faults. PWM is off,
the wheel is dead. The application polls `getStatus()`, sees `DS_MOVING`, and keeps
driving the other wheel. The platform pivots into the obstacle indefinitely.

<a id="af"></a>
### AF — a two-wheel application has no public way to detect a fault
`isp_steering_2wheel.spin2:403-448, 506-521` · **Defect (API gap)**

The steering object's public predicates are only `isReady`, `isStopped`, `isStarting`,
`isTurning`. There is **no `isFaulted()` and no `isEmergency()`**.

The two helpers that do know are both `PRI` and therefore unreachable from an application:
`getDriverState()` (`:408`) and `getFaultStatus()` (`:418`). They *are* used internally
(`:608-611, :664, :674, :684, :704`) — this is an access-modifier gap, not dead code.

The full chain:

```
isp_bldc_motor.getStatus()        reports DS_MOVING while faulted   (finding M)
  └─▶ isp_steering_2wheel.getStatus()   forwards it verbatim  (:403)
        └─▶ isp_steering_serial.spin2:432  wheels.getStatus() → host
```

That is precisely README's *"…so is also reported badly over serial I/F"*, traced end to
end. The only indirect signal an application has is `isTurning()` returning false.

**Highest-value fix target in this audit.** Fixing M without also widening the `DS_*` enum
and exposing a steering-level fault query leaves the serial consumer no better off.

<a id="w"></a>
### W — the rate window adds a variable that is always zero
`isp_bldc_motor.spin2:1297-1310` · **Defect**

```spin2
nHallCntsIn8thSec := absDistanceInTics(pos, prioro8thSecPos)   ' local — correct new reading
...
hallWindowSum -= LONG[@hallCountsWindow][hallWinIndex]         ' remove oldest      :1268
long [@hallCountsWindow][hallWinIndex] := nHallCntsIn8thSec    ' store new reading  :1269
hallWindowSum += hallCntsIn8thSec                              ' ← WRONG VARIABLE   :1270
```

`hallCntsIn8thSec` is the VAR at `:1161`. It is assigned in **exactly one place** — `:1259`,
to `0`, inside `resetWindowAccumulators()` — and never again anywhere in the file. So
`:1270` always adds zero while `:1268` keeps subtracting real entries.

`hallWindowSum` therefore starts at 0 and, once the 8-entry window fills, only ever
decreases. The intended line is obviously `+= nHallCntsIn8thSec`.

**Blast radius** — everything downstream of `cntsInSec := hallWindowSum` (`:1343`):
`tvRpm_x10`, `rpm`, `maxRpm`, `tvMaxRpmIn10ths`, `tvMaxCntsInSec` (`:1344-1349`), and
`mmPerSec_x10`, `ftPerSec_x10`, `kmh_x10`, `mph_x10` plus their max trackers
(`:1362-1369`). The `max()` trackers pin at 0 because they start at 0 and never see a
positive sample. These are exactly the values published to the HDMI debug display
(`:1067`).

**Not affected:** `posTrkHallTicks` (`:1275`) uses the correct local, so `getDistance()`
and `getRotationCount()` are sound. The defect is confined to rate reporting.

This plausibly explains why `util_char_motor.spin2` and `test_motor_char*.spin2` exist as
separate programs computing their own rate numbers.

<a id="ab"></a>
### AB — `driveForDistance()` cannot turn
`isp_steering_2wheel.spin2:190-200` · **Defect / feature absent**

```spin2
shorterDistance := leftDistance < rightDistance ? leftDistance : rightDistance
stopAfterDistance(shorterDistance, eDistanceUnits)
maxLtSpeed := ltWheel.getMaxSpeedForDistance()
maxRtSpeed := rtWheel.getMaxSpeedForDistance()
driveAtPower(maxLtSpeed, maxRtSpeed)
```

Its own doc comment, and `DRIVE-OBJECTS.md`, both claim: *"Control the forward direction
**or rate of turn** of your robot using the {leftDistance} and {rightDistance} inputs."*

The two distances are collapsed to their **minimum**, and that single value becomes one
stop-distance for both wheels. Both wheels are then driven at
`getMaxSpeedForDistance()` — the same per-wheel default (75). **The distance ratio is
discarded entirely.**

**Failure scenario:** `driveForDistance(100, 50, DDU_CM)` is documented as an arc. It
drives straight for 50 cm.

A real turn needs per-wheel powers proportional to the distance ratio and per-wheel stop
distances. Neither exists.

<a id="a1"></a>
### A1 — Rev B never receives its shorter dead gap
`isp_bldc_motor.spin2:198` · **Defect** · *root cause A*

```spin2
if eDetectedBoard == BRD_REV_B      ' eDetectedBoard holds REV_* (21/22); BRD_REV_B is 32
    gapInMS := 52
else
    gapInMS := 260
```

Two enum families describe one concept:

| Declaration | Values |
|---|---|
| `:36` `#20, REV_Unknown, REV_A, REV_B` | 20, 21, 22 |
| `:39` `#30, BRD_AUTO_DET, BRD_REV_A, BRD_REV_B` | 30, 31, 32 |

`getBoardType()` returns `REV_*` (its own comment at `:602` says so). The comparison
against `BRD_REV_B` can therefore **never be true**, and `gapInMS` is always 260.

The same method compares the same variable **correctly** at `:261`/`:263` (`REV_A`/`REV_B`)
to select the current-sense resistor — which proves the intent.

`dead_gap` feeds `pwm_limit` and `duty_min`, so a Rev B board runs the longer dead gap and
loses some PWM headroom. This silently defeats commit `2269894`, *"adjust gap based on board
type… REV_B needs shorter to reduce jerk"* — a **v5.0.2 feature that does not work**.

> ## REVISED 2026-09-10 — the verdict inverts. Do NOT apply the obvious fix.
>
> Stephen surfaced the Parallax board documentation — **for both revisions.** Each manual
> carries the same warning and the same number:
>
> > *"…it is possible, for fractions of a second during fast switching, that both high and
> > low MOSFETs might be partially on and causing momentary overcurrent. Therefore, the
> > **recommended minimum pause (deadtime) is 250 ns** after switching off one MOSFET and
> > before switching on the other MOSFET in the same channel."*
>
> ### The decisive detail: the two boards ship different drivers and the same requirement
>
> | | MOSFET driver | propagation | rise / fall | **vendor minimum deadtime** |
> |---|---|---|---|---|
> | **Rev A** | MIC4604 | 39 ns | ~20 ns / ~20 ns | **250 ns** |
> | **Rev B** | UCC27211D | ~20 ns | 7.2 ns / 5.5 ns | **250 ns** |
>
> Rev B's drivers are roughly **twice as fast** as Rev A's on every figure — and Parallax
> still specifies **the same 250 ns**. That is the whole argument in one line: **deadtime
> here is set by the MOSFETs' response, not by the drivers' switching speed.** Both manuals
> say so explicitly ("*the MOSFETs require some time to respond to the control signal from
> the MOSFET Drivers*").
>
> **Therefore there is no board-revision-dependent deadtime requirement at all.** The
> conditional at `:198` is not merely miscoded — **the distinction it encodes does not
> exist.**
>
> **The enum defect above is real and unchanged.** What changes is which behaviour is
> correct.
>
> | | value | vs. the 250 ns minimum (**both** revisions) |
> |---|---|---|
> | What the code **actually does** today (every board) | **260 ns** | **compliant** ✅ |
> | What the code **intends** for Rev B | **52 ns** | **~5× below minimum** ❌ |
>
> Measured across the three clocks the suite uses, the `(ticks1us * gap) / 1_000` integer
> arithmetic holds both values steady: 260 ns → 70/52/78 clocks at 270/200/300 MHz
> (259.3 / 260.0 / 260.0 ns); 52 ns → 14/10/15 clocks (51.9 / 50.0 / 50.0 ns).
>
> **So the bug is currently protecting the hardware.** Repairing the comparison *alone* —
> the one-word change this finding appears to call for — would drop every Rev B board to
> ~52 ns and produce exactly the shoot-through overcurrent the vendor note warns about:
> higher current surge demanded of the pack, hotter FETs, reduced efficiency, and a
> plausible path to destroying a half-bridge.
>
> **Reclassified: `Defect (latent)` → `Defect (do-not-fix-naively) + hardware hazard`.**
>
> ### What the fix actually is: **delete the conditional**
>
> Since both revisions specify the same 250 ns minimum, the correct code has **no branch**:
>
> ```spin2
> ' both revisions: Parallax specifies a 250 ns minimum deadtime.
> ' Set by MOSFET response time, NOT by driver speed - Rev B's UCC27211D is ~2x
> ' faster than Rev A's MIC4604 and carries the identical requirement.
> gapInNs := 260                      ' >= 250 ns vendor minimum, both boards
> ```
>
> This is strictly better than repairing the comparison:
>
> - it is the behaviour the boards are **already getting**, so it changes nothing on
>   hardware and cannot regress a working system;
> - it **removes** one of root cause **A**'s three sites outright — with no comparison,
>   there is no wrong-enum comparison to get wrong;
> - it deletes a distinction the vendor documentation says does not exist.
>
> Then recheck `pwm_limit` and `duty_min`, both derived from `dead_gap` (unchanged in
> practice, since the value does not move).
>
> **Rename `gapInMS` while there** — it holds nanoseconds and has always said
> milliseconds.
>
> ### Before chasing a better number: what is the prize? **0.9 % of duty range.**
>
> `pwm_limit = frame_cnt/2 − dead_gap/2`, so the dead gap's entire cost is `dead_gap/2` out
> of `frame_cnt/2`. Computed from the actual source arithmetic at all three suite clocks:
>
> | dead gap | cost in duty range, 200 / 270 / 300 MHz |
> |---|---|
> | 260 ns (today, both boards) | **1.14 % / 1.14 % / 1.14 %** |
> | 250 ns (vendor minimum) | 1.10 % / 1.08 % / 1.09 % |
> | 52 ns (intended for Rev B) | 0.22 % / 0.23 % / 0.21 % |
>
> **The whole prize for going from 260 ns to 52 ns is ~0.9 % of duty range.** That is far too
> small to be worth operating outside the vendor's specification, and far too small to
> explain a perceptible change in jerk — which independently undermines commit `2269894`'s
> premise on measurement grounds, not just documentary ones.
>
> ### And keep 260, not 250 — integer truncation
>
> `dead_gap := (ticks1us * gapInNs) / 1_000` truncates. A literal **250** yields **67 clocks
> = 248.1 ns at 270 MHz — under the vendor minimum.** 260 ns clears 250 ns at every clock the
> suite uses (259.3 / 260.0 / 260.0 ns at 270 / 200 / 300 MHz). **260 is the correct constant
> precisely because it carries margin for the truncation.** Do not "tighten" it to 250.
>
> ### The consequence for the v5.0.2 jerk fix
>
> The premise of commit `2269894` — *"REV_B needs shorter to reduce jerk"* — is not merely
> unachievable, it is **contradicted by the vendor documentation for both boards.** There is
> no Rev-B-specific shorter deadtime to be had. And it never took effect anyway, because the
> comparison never matched. **Reducing jerk needs a different mechanism** — most plausibly
> the lag-limited ramp in **C-5**, already the top recommendation of the second study.
>
> ### Where the 52 ns probably came from — and why the trap is well-set
>
> Both manuals pre-empt exactly this inference: *"Even though the MOSFET Drivers feature a
> fast … propagation delay and typically … rise/fall time, **the MOSFETs require some time
> to respond**…"* Rev B's UCC27211D numbers (20 ns propagation, 7.2/5.5 ns transitions) are
> genuinely fast, and sizing deadtime from them lands near 50 ns — which is roughly the 52 ns
> in the source. The faster driver is precisely what makes the wrong answer look reasonable.
> A plausible origin, not a documented one.
>
> **Related:** the same 250 ns minimum is the number the **T1-13** harness must implement if
> it PWMs the fourth channel itself — see the shoot-through hazard in the bench plan.

<a id="a2"></a>
### A2 — the user's board-revision override is silently ignored
`isp_bldc_motor.spin2:606-611` · **Defect** · *root cause A*

`getInternalDetectMode()` (`:872`) returns `BRD_AUTO_DET` / `BRD_REV_A` / `BRD_REV_B`
(30/31/32), stored in `eUserDetectionMode`. `getBoardType()` then does:

```spin2
case eUserDetectionMode
    REV_A:      ' 21 — cannot match 31
        eBoardRev := REV_A
    REV_B:      ' 22 — cannot match 32
        eBoardRev := REV_B
    other:
        ...auto-detect...
```

Verified against `p2kb-mcp` (`p2kbSpin2Case`): Spin2 `CASE` is plain equality dispatch —
the documentation's own PASM equivalent is `CMP`/`IF_Z JMP` — with no fall-through and
`OTHER` catching unmatched values. A value of 31 or 32 cannot match arms of 21 or 22, so
control always reaches `other:` and auto-detects.

**Failure scenario:** a board that auto-detection misreads is exactly the case the override
exists for, and the override does nothing.

<a id="a3"></a>
### A3 — the status string claims an override that wasn't honoured
`isp_bldc_motor.spin2:591-596` · **Defect** · *root cause A*

`getInternalDetectMode()` still sets `bUserForced := TRUE` even though A2 means the
override was discarded. `boardIdString()` then reports `"64010 Rev A -USER FORCED"` for a
value that actually came from auto-detection.

<a id="n"></a>
### N — DocoEng low-power floor is computed from an unassigned sentinel
`isp_bldc_motor.spin2:981` · **Defect**

```spin2
minFwdIncreAtPwr := VALUE_NOT_SET            ' = -1   (preset at :901)
...
if user.MOTOR_TYPE == MOTR_DOCO_4KRPM
    minFwdIncreAtPwr := 0 - minFwdIncreAtPwr ' 0 - (-1) = 1   ← reads the preset
    minRevIncreAtPwr := 544_628
else
    minFwdIncreAtPwr := 544_628              ' assigns first…
    minRevIncreAtPwr := 0 - minFwdIncreAtPwr ' …then negates the ASSIGNED value  ✓
```

The `else` arm shows the correct pattern. The DocoEng arm negates the sentinel instead of a
real floor, so `minFwdIncreAtPwr` becomes `+1` rather than the intended `-544_628` — the
"anything below yields NO rotation" threshold, sign-flipped for the DocoEng motor's
inverted convention.

**Effect:** at `power = 1` the DocoEng motor is handed increment `+1` — wrong sign and
essentially zero magnitude. The intended minimum-rotation floor is never applied, so the
mapping jumps from `+1` to `-3_888_887` between power 1 and 2.

<a id="f"></a>
### F — `stopAfterDistance(_, DDU_M)` is 10× short
`isp_bldc_motor.spin2:441` · **Defect**

`tickInMM_x10` is (mm per tick) × 10, so `ticks = distance_mm × 10 / tickInMM_x10`.

| Unit | Code | Correct? |
|---|---|---|
| `DDU_MM` | `(nDistance * 10) / tickInMM_x10` | ✓ |
| `DDU_CM` | `(nDistance * 10 * 10) / tickInMM_x10` | ✓ |
| `DDU_M` | `(nDistance * 100 * 10) / tickInMM_x10` | ✗ gives `n × 1000`, needs `n × 10000` |
| `DDU_IN`, `DDU_FT` | via `fIn2mm(...) *. 10.0` | ✓ |

**Failure scenario:** `stopAfterDistance(1, DDU_M)` stops after 0.1 m.

Independently corroborated by finding [S](#s): `getDistance()` computes `DDU_M` correctly
(`/. 1000.0`), so the two APIs disagree by exactly 10× on the same unit.

<a id="o"></a>
### O — `PWR_25p9V` passes validation, then aborts at init
`isp_bldc_motor.spin2:685` vs `:925` · **Defect**

`validVoltageForChoice()` accepts `PWR_6p0V..PWR_25p9V` for the 6.5″ motor, so
`PWR_25p9V` (9) is reported **legal**. `confgurePowerLimits()` then looks up
`PWR_6p0V..PWR_11p1V, PWR_12p0V, PWR_14p8V, PWR_18p5V, PWR_22p2V..PWR_24p0V` — which tops
out at `PWR_24p0V` (8) — misses, and hits `abort` with *"SHOULD NEVER get here!"*.

**Failure scenario:** a 7s LiPo configuration validates cleanly in the user's own
pre-flight check and then aborts during `start()`.

<a id="ad"></a>
### AD — motor cog start failure is never checked
`isp_steering_2wheel.spin2:106-115` · **Defect**

```spin2
ltcog := ltWheel.startEx(...)      ' cogid+1, or 0 on failure (finding C)
rtcog := rtWheel.startEx(...)
cogmask := (1<<(ltcog-1))|(1<<(rtcog-1))
```

Neither return is tested. On failure the value is `0`, making the shift count `-1` and the
mask garbage. Both wheels were started with `sync = true`, so each is parked in `waitatn`;
a wrong mask means the surviving motor is **never released** and the drive system hangs
with no diagnostic. `start()` returns only the *sense* cog id, so the caller cannot detect
it either.

<a id="ae"></a>
### AE — no validation that the two pin groups don't overlap
`isp_steering_2wheel.spin2:97` · **Defect (config trap)**

`start(leftBasePin, rightBasePin, …)` passes each straight through; each wheel's
`validatePinBase()` only checks its own value is one of the legal bases.

The enum is `#0[8], PINS_P0_P15, PINS_P8_P23, PINS_P16_P31, …` — stride 8, so
`PINS_P0_P15` (0) and `PINS_P8_P23` (8) **overlap on pins 8–15**. Configuring left and
right to that pair gives two driver cogs writing the same eight smart pins. Nothing
detects it; it would present as erratic motor behaviour.

<a id="ac"></a>
### AC — steering direction contradicts its own comment
`isp_steering_2wheel.spin2:670-682` · **Defect? — needs hardware confirmation**

```spin2
ltPower := ((limitDir <= 0)) ? limitPwr : reducedPower
rtPower := ((limitDir >= 0)) ? limitPwr : reducedPower
```

The comment block immediately above says: *"if turning towards right, left motor stays at
power, right motor is reduced."* The code does the opposite — for `limitDir > 0` the
**left** motor is reduced and the right stays at full.

Three sources disagree:

| Source | Claim |
|---|---|
| The code | `direction > 0` reduces **left** → pivots left |
| The code's own comment | `direction > 0` should reduce **right** |
| `DRIVE-OBJECTS.md` | `direction > 0` = "turn to the right" |
| `README.md` FlySky table | "turn to right (slow down left motor)" — matches the code, contradicts the physics |

On a differential drive, slowing the left wheel pivots left. **I could not resolve which
convention is intended without running the platform**, and I did not run it. What is
objectively a defect regardless of intent: the code contradicts the comment directly above
it, and the two user-facing documents disagree with each other.

**Recommended verification:** command `driveDirection(50, +50)` on the bench and observe
which way it turns.

<a id="y"></a>
### Y — `maxNeg` is neither max-negative nor `1`
`isp_bldc_motor.spin2:2196` · **Defect (documentation/naming)**

```pasm2
maxNeg  LONG  $FFFF_FFFF   ' comment: "32-bits of one (max negative signed value)"
```

`$FFFF_FFFF` is `-1`. The max negative signed value is `$8000_0000`. Name and comment are
both wrong; the value is really an all-ones sentinel.

Compounding: the Spin2 VAR comment at `:1511` says `fault` is *"written to 1 on fault"*,
but `:2075` writes `$FFFF_FFFF`. Code testing `fault == 1` would never fire.
`isFaultSignal()` tests `fault <> false`, so it works today — this is a trap for the next
reader, not a live failure.

---

## Feature gaps

<a id="z"></a>
### Z — fault is a hard latch with no fallback
`isp_bldc_motor.spin2:2102-2108` · *README known issue, diagnosed*

When the rotor lags the commanded angle by ≥ 125/256 of a turn (~176°) and the drive is not
already off, the driver calls `.driveoff`, latches `drv_state_ := DCS_FAULTED`, and signals
`fault`. There is no retry, no torque back-off, no re-sync attempt. Recovery happens only
when a new drive request arrives (`.resetFault`, `:1755`).

This is README's *"motor can fault at higher load conditions (we need to add a fallback
algorithm so the motor doesn't 'give up' under load)"*.

**Its severity is set by [M](#m):** the motor stops dead and stays dead, while the API
reports `DS_MOVING`. On a drive platform that is a silent failure with physical
consequences. Fixing M does not fix Z, but it converts Z from *silent* to *reported* — which
is why M is the higher-value fix.

<a id="g"></a>
### G — `setAcceleration()` silently corrupts ramping
`isp_bldc_motor.spin2:308`

```spin2
PUB setAcceleration(rate)
'' Limit Acceleration to {rate} where {rate} is [??? - ???] mm/s squared
  ' need to convert from units to ramp increment     ← never written
    setRampingValues(ramp_min, ramp_max, rate, ramp_down)
```

A value documented as mm/s² is passed straight into `ramp_inc`, an angle increment applied
every 500 µs whose default is **22**. `setAcceleration(1000)` sets it to 1000 — roughly 45×
the default.

`DRIVE-OBJECTS.md` advertises this as **"NOT WORKING, YET"**, but it is not inert — it
writes. A method that is documented as non-functional and silently changes drive behaviour
is worse than one that does nothing. The doc comment still carries literal `???`
placeholders.

<a id="c"></a>
### C — `start()`'s documented return contract is wrong
`isp_bldc_motor.spin2:76-84, :103`

The doc says *"@returns ok - The COG ID of the motor driver task or (-1) if failed to
start"*. The code is `ok := motorCog := coginit(NEWCOG, @driver, @pinbase) + 1`.

`coginit` returns −1 on failure, so `+1` yields **0**; on success it yields **cogid + 1**,
not the cog id. A caller testing `== -1` for failure never sees it — which is exactly what
[AD](#ad) does wrong downstream.

<a id="k"></a>
### K — distance units you can read but cannot command

`getDistance()` documents and handles `DDU_KM` and `DDU_MI`. `stopAfterDistance()` supports
only `MM/CM/IN/FT/M` and aborts on anything else.

<a id="ai"></a>
### AI — the reverse commutation offset is derived, never characterized
`isp_bldc_motor.spin2:884-886` · **Feature-gap / Risk** · *raised by the 2026-09-09 field report*

```spin2
' 4 degrees per tic, offset was actually 5 tics! or 20 degrees
' from characterization at 18v5:
fwdDegrees := ofsDegr := 43
revDegrees := 360 - fwdDegrees          ' = 317 — arithmetic, not measured
```

The forward offset carries a comment recording where it came from — bench characterization
at 18.5 V. The reverse offset is its arithmetic mirror. The author's own open question
appears in the DocoEng branch of the same method: `revDegrees := 360 - ofsDegr  ' vs. using 360?`

Because `isp_steering_2wheel` calls `rtWheel.forwardIsReverse()` (`:110`), the right motor
of **every** two-wheel platform takes the reverse path through `incrementForPower()` and
therefore runs permanently on this uncharacterized offset. Commutation offset sets torque
produced per amp, so if 317° is not the true optimum the right wheel has less margin than
the left against the ~176° fault threshold.

**Failure scenario:** exactly the field report — the right motor faults repeatedly under a
load the left motor handles, on hardware that tests clean one motor at a time.

<a id="aj"></a>
### AJ — the 6.5″ motor's offset ignores voltage and board revision
`isp_bldc_motor.spin2:884-886` vs `:843-848` · **Feature-gap** · *raised by the field report*

| Motor | Offset selection |
| --- | --- |
| `MOTR_DOCO_4KRPM` | lookup over **7 voltages × 2 board revisions**, with per-voltage bench notes |
| `MOTR_6_5_INCH` | a single hardcoded `43`, used at every voltage from 6 V to 25.9 V and on both revisions |

The 6.5″ hub motor is the one the product page leads with and the one in most built
platforms, and it has markedly the less mature characterization of the two supported
motors.

> ### REFRAMED 2026-09-10 — the question may be backwards
>
> Vendor documentation for both revisions
> ([`BOARD-REVISION-FACTS.md`](BOARD-REVISION-FACTS.md) §1.1) shows the **hall input path is
> character-for-character identical** between Rev A and Rev B: same 3.9 kΩ pull-ups to 3.3 V,
> same 3.9 kΩ series resistors, same header, same 5 V rail.
>
> Yet the DocoEng table shifts by **~15–20°** between revisions. Nothing electrical accounts
> for it. Commutation offset compensates loop delay, and the only delays that differ are
> gate-driver propagation (39 ns vs ~20 ns) and the dead gap (260 ns, identical in practice
> per **A1**). In electrical degrees on a 15-cycle/rev motor at ~274 RPM, **18° is 730 µs** —
> three orders of magnitude larger than a 19 ns or 260 ns difference.
>
> **Leading hypothesis: the table is measuring the instrument, not the motor.** The offsets
> were picked empirically by minimum current draw and fault behaviour — the bench notes in
> the source say so (*"51-54 best, 55 fault?!"*). Rev A and Rev B present current to the P2 at
> scales **30× apart** (5 mV/A vs 150 mV/A, §2.2), and `sense_i_mV` is separately wrong by
> `adc_fram` (**S-3**). A criterion resting on current readings and fault thresholds would
> return different answers per board for reasons of measurement.
>
> **So the better question is not "why doesn't the 6.5″ motor vary by revision?" but "why
> does the DocoEng one?"** — and whether that table should be one table rather than two.
> **T1-10** / **T1-11** can settle it; run T1-10 on Rev B and compare against the Rev A
> column. Full working: `BOARD-REVISION-FACTS.md` §2.7.

<a id="ak"></a>
### AK — no voltage feedback; the power table is fixed at the declared nominal
`isp_bldc_motor.spin2:926-990` · **Feature-gap** · *raised by the field report*

`confgurePowerLimits()` runs once, at `start()`, and picks an increment ceiling from the
voltage the user **declared** in `isp_bldc_motor_userconfig.spin2`. Nothing measures actual
supply voltage — not at start-up, not ever — and nothing adapts as the pack drains.

The driver *does* sample phase current into `sense_i_mV`, but purely as telemetry; no
control loop consumes it. There is no current limiting and no torque back-off.

Combined with [Z](#z) and with a table characterized about 2 % below the measured fault
point (the code's own note: *"147_000_000 anything above yields RPM 272.0 … until fault at
277.3"*), battery state becomes a direct determinant of whether a run completes.

**Failure scenario:** the field report's observation 3 — first run on a charged pack
succeeds, subsequent runs fault, with no code or configuration change in between.

---

## Risks and latent issues

<a id="p"></a>
### P — undocumented 2³⁰ ceiling on the drive increment
`isp_bldc_motor.spin2:991` / `:2097-2105` · **Risk**

`targetIncre` carries the sync flag in bit 31 and a **31-bit signed** increment in bits
30..0. Spin2 does `ZEROX= 30` (verified via `p2kb`: zeroes *all* bits above bit 30,
destroying the sign) then ORs in the sync flag; the PASM restores the sign with
`signx tgt_incr, #30`.

The design is correct — I verified the whole handshake, including that `POLLATN`'s flags
are set to the ATN flag *state* (`p2kbPasm2Pollatn`), so `if_c_and_z` really does mean
"attention received".

The risk is the unstated invariant: **|increment| must stay below 2³⁰ = 1 073 741 823.** The
largest table value today is 545 000 000 — about 2× headroom. A new motor or a higher supply
voltage would breach it, and the symptom would be a motor running the wrong direction, with
nothing checking and nothing documenting the limit. Now stated in the Theory of Operations,
Invariant 4.

<a id="h"></a>
### H — `resetTracking()` blocks the calling cog
`isp_bldc_motor.spin2:351` · **Risk**

```spin2
posTrkHallTicks := 0
waitms(200)   ' values will clear in 125ms
```

The sleep stands in for a handshake with the sense cog that concurrently accumulates
`posTrkHallTicks`; a tick landing between the write and the cog's next accumulate is
silently kept.

The chain `resetWindowAccumulators()` (`:1255`) → `resetTracking()` (`:1262`) → `waitms(200)`
has two consequences:

1. It is called **inside** the 125 ms sense loop (`:1293`) on fault/e-stop, so that
   iteration takes ~200 ms and overruns the loop's own period.
2. `resetWindowAccumulators()` is **public** and the steering object calls it from a
   *different* cog for both wheels (`:178-179`, `:600-612`) — blocking that cog ~400 ms. A
   caller has no way to know a "reset counters" call sleeps.

<a id="i"></a><a id="t"></a>
### I / T — `abort()` used for parameter validation, including inside getters

`stopAfterRotation` (`:397, :415`), `stopAfterDistance` (`:424, :429, :444`),
`stopAfterTime` (`:453, :461`), `getDistance` (`:525`), `getRotationCount` (`:542`),
`motorVoltage` (`:975`), `confgurePowerLimits` (`:899, :938, :953`).

Two consequences: an uncaught `abort` unwinds the caller's entire stack, and aborting
*after* a prior `driveAtPower()` leaves the motor running while the stack unwinds. An
`abort` from a **query** — `getDistance()` with a bad units enum — is the sharpest case.

Each stop-method site also carries an unresolved `FIXME: UNDONE should be more than ticks
needed for spin-up/down ramps!!!`.

Contrary to the guide (§5.4, API methods return error codes), but noted here as a *risk*
rather than a conformance nit because of the runtime consequence.

<a id="j"></a>
### J — `stopAfterTime` wraps at ~49.7 days
`isp_bldc_motor.spin2:465-476` · **Latent**

`motorStopMSecs := getms() + n`, and `getms()` is a 32-bit millisecond counter. The
`if motorStopMSecs == 0 → 1` guard shows 0 is the not-set sentinel, but a wrapped deadline
compares wrong in the sense loop. Long-uptime installations only.

<a id="q"></a>
### Q — `SyncStatus()` busy-waits with no timeout
`isp_bldc_motor.spin2:999` · **Risk**

```spin2
repeat while targetIncre & $8000_0000
```

If the peer motor never clears the sync bit — failed `coginit`, stopped cog — this spins
forever. Reached from `driveAtPower()` in the steering layer, so [AD](#ad) makes it
reachable in practice.

<a id="s"></a>
### S — two conversion paths for one physical relationship

`getDistance()` (`:497`) uses a float `fMMpTick` recomputed per call; `stopAfterDistance()`
(`:417`) uses the integer `tickInMM_x10`. Same relationship, two implementations that can
disagree by rounding — and that **do** disagree by 10× on `DDU_M`, which is how [F](#f) was
corroborated.

### Other notes

| Ref | Note |
|---|---|
| D | Unused locals `legalBase` at `:86` and `:125` |
| E | `gapInMS` holds **nanoseconds**, not milliseconds (`:198-203`) |
| L | `stopAfterTime`'s two branches are identical but for one multiplier; validation `case` has empty arms then re-tests with `if` |
| U | Dead/commented-out code: `isStarting()` (`:652`) carries a previous implementation; `getRotationCount` presets an unreachable `-1` |
| V | HDMI block: `pTitlesAr` comment doesn't match usage; `nVarsInGroup := 7` duplicates `DBG_MAX_VARS_IN_GROUP` |
| AA | `.noFault` (`:2077`) is a label nothing jumps to; `setq` comment says "13" for a 14-long transfer; `sync_required` is a DAT long writable only before `coginit` |
| AG | Steering keeps two parallel records of "what was requested" (`rqstPower`/`rqstDirection` vs `rqstLtPower`/`rqstRtPower`) |
| AH | `waitms(100)` before `cogatn` (`:113`) is unnecessary — the ATN flag latches (`p2kbPasm2Pollatn`). Harmless, but reads as a race fix that fixes nothing |

---

## What is verifiably correct

Worth recording, because an audit that lists only problems misrepresents the code.

- **The Spin2↔PASM2 ABI is internally consistent.** All three regions were checked
  end-to-end: the `ptra` walk, the 14-long status block (Spin2 VAR order = PASM `res` order
  = count constant), the fault long at index 14, and the 14-long parameter block. No
  mismatch. The fragility is that nothing *enforces* it — now written up as Invariants 1–3
  in the Theory of Operations.
- **The two-motor sync handshake is correct**, including the `POLLATN` flag polarity and
  the sign-restore, both verified against `p2kb-mcp`.
- **Distance and rotation tracking are sound** — `posTrkHallTicks` uses the correct
  variable, so [W](#w) does not touch `getDistance()` or `getRotationCount()`.
- **The commutation tables and the `(old << 3) | new` delta scheme** are consistent between
  both supported motors.

---

## Conformance — `central:spin2-authoring-guide` (PL-2)

Reported separately so style findings do not bury correctness findings. Machine-checkable
rules were run as checks; the rest were noted during the read.

**Passing — no violations in any in-scope file:**

| Rule | Result |
|---|---|
| §1.1 ASCII only | 0 non-ASCII codepoints |
| §1.2 no `=>` as comparison | 0 |
| §1.8 no `@""` empty literal | 0 |
| §2.2 no generic container names | 0 live occurrences |

**Failing:**

| Rule | Result |
|---|---|
| §4.3 PUB `@param` tags | **49 of 53** param-taking PUBs carry none — `isp_bldc_motor` 22/25, `isp_steering_2wheel` 16/17, `isp_dist_utils` 11/11 |
| §4.4 PRI documentation | **29 of 56** PRIs have no leading comment — `isp_bldc_motor` 11/23, `isp_steering_2wheel` 15/27, `isp_steering_serial` 3/6 |
| §3.2 PUB before PRI | Structurally violated: `isp_bldc_motor` first PRI at `:137` then 56 PUBs after; `isp_steering_2wheel` first PRI at `:348` then 18 after |
| §5.7 no magic numbers | Several — `$ffffffff` sentinel (`:356`), `nVarsInGroup := 7` (`:1032`), fault threshold `#125` (`:2071`) |
| §5.4 API returns error codes | Violated by design — see [I/T](#i) |
| §5.0 no unused locals | Finding D |

**The distinction that matters for planning:** the conformance picture is dominated by
**documentation debt**, not language misuse. The language-rule half of the guide is
essentially clean. The risky-to-change rules pass; what fails is additive and safe to fix
incrementally.

`start()` and `startEx()` are the two methods that *do* carry full `@param` documentation —
they show the intended house style, so the fix has a template in-tree.

**On PL-2's owed gate:** the four passing checks above are exactly the mechanical ones
uSD's `tools/check_style.sh` already implements. §4.3, §4.4 and §3.2 are equally mechanical
and worth adding when `STYLE_GATE_COMMAND` is built.

---

## Ruled out

Recorded deliberately, because it is the obvious wrong conclusion and a later reader would
otherwise re-derive it.

**Suspected:** that the 200 ms overrun in [H](#h) makes
`waitct(senseStartTicks + ticks125ms)` (`:1330`) wait a full 32-bit counter wrap — ~15.9 s at
270 MHz — because the target is already ~75 ms in the past. That would have been a severe
finding: the sense loop dead for 16 seconds after every fault.

**It does not happen.** Verified against `p2kb-mcp` (`p2kbPasm2Waitct1`): the CT event flag
is set whenever the System Counter **passes** the trigger value — *"MSB of CT − CT1 is 0"* —
a signed has-passed test, not an equality match. A target up to ~2³¹ ticks (~7.95 s) in the
past satisfies immediately. The loop runs one long iteration and, because `senseStartTicks`
is re-read at the top of each pass, self-corrects on the next.

---

## Suggested fix ordering

Not a plan — the fix sprint is separate. Offered because the dependencies are real.

1. **[M](#m) + [AF](#af) together**, plus widening `DS_*`. Fixing `getStatus()` alone is
   not enough; the enum cannot express failure and the steering layer exposes no fault
   query. This is the one that makes [Z](#z) visible instead of silent.
2. **[W](#w)** — a one-word change (`hallCntsIn8thSec` → `nHallCntsIn8thSec`) that restores
   all speed/RPM telemetry. Highest value per byte in the audit.
3. **Root cause A ([A1](#a1), [A2](#a2), [A3](#a3))** — collapse the two board-revision enum
   families into one, or convert explicitly at the two boundaries. Fixing the three
   symptoms separately invites the fourth.
4. **[F](#f), [N](#n), [O](#o)** — independent, small, each self-contained.
5. **[AD](#ad) + [C](#c)** together — the return contract and the caller that trusts it.
6. **[AB](#ab)** — genuinely new work, not a repair; scope it deliberately.
7. **[AC](#ac)** — needs a bench observation before any code change.
8. **[AI](#ai) / [AJ](#aj)** — bench characterization work, not coding: measure the true
   reverse offset for the 6.5″ motor, and decide whether it needs a per-voltage table like
   the DocoEng motor already has. This is the most likely route to the field report's
   right-motor asymmetry.
9. **[AK](#ak)** — design work. Even reading pack voltage once at `start()` and refusing to
   select a table above what the pack can support would be a meaningful improvement over
   trusting a declared constant.

**Trivially safe, if you want them green-lit outside a sprint:** the one-word fix for
[W](#w), and the `DDU_M` multiplier in [F](#f). Both are single-token changes with no
structural consequence. Everything else deserves the sprint.

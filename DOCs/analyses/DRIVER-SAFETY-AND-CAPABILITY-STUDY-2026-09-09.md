# Driver Study II — Protection and Capability

**Date:** 2026-09-09
**Scope:** `src/isp_bldc_motor.spin2` (Spin2 API, sense task, PASM2 driver),
`src/isp_steering_2wheel.spin2`, `src/isp_steering_serial.spin2`,
`src/isp_flysky_rx.spin2`, `src/jm_sbus_rx.spin2`, the RC demos, and
`BLDC_Motor_Driver_ChipNew.spin2` (Chip Gracey's reference, repo root, read-only).
**Posture:** STUDY. No source was modified. Findings only.
**Companion:** [`DRIVER-AUDIT-2026-09-09.md`](DRIVER-AUDIT-2026-09-09.md) — the
defect audit. This study does not repeat its findings; where the two touch, this
document cross-references by the audit's letter ID and goes to the mechanism
underneath.

---

## Why two heads

Stephen asked two questions in one breath, and they turn out to be the same
question seen from opposite ends:

1. **How does this code detect trouble, and how would we better protect the
   hardware attached to it?**
2. **What would most benefit a user — how do we fix ramps, acceleration,
   deceleration and braking so this feels like a real motor driver?**

They converge because the driver's *only* trouble detector is the same signal
that would make its ramps intelligent. The rotor's angular lag behind the
commanded field is measured 44,000 times a second, and it is used for exactly
one thing: to give up. Nothing throttles on it, nothing reports it, nothing
learns from it. Fix that one omission and both heads move at once.

Finding IDs in this document are `S-n` (protection) and `C-n` (capability), to
keep them distinct from the audit's letters.

---

# PART I — PROTECTION

## I.1 The complete map of what exists today

Every mechanism in the codebase that can stop a motor, in full:

| # | Mechanism | Where | Trigger | Latency |
| --- | --- | --- | --- | --- |
| 1 | Angle-lag fault | `isp_bldc_motor.spin2:2103-2108` | rotor lags commanded field by ≥125/256 turn (~176° electrical) — drive off, **ignoring `stop_mode`** (**S-9a**) | 22.7 µs |
| 2 | `stopMotor()` | `isp_bldc_motor.spin2:476` | user call | next 500 µs pass |
| 3 | `emergencyCutoff()` | `isp_bldc_motor.spin2:481` | user call | next 500 µs pass |
| 4 | time limit | `isp_bldc_motor.spin2:1338-1342` | `stopAfterTime()` elapsed | up to 125 ms |
| 5 | distance limit | `isp_bldc_motor.spin2:1343-1347` | `stopAfterDistance()` reached | up to 125 ms |
| 6 | `stop()` | `isp_bldc_motor.spin2:109` | user call — `cogstop` + `pinclear` | immediate, ungraceful |
| 7 | `abort` on bad parameter | 10 call sites | invalid argument | caller's `\` handler |

That is the entire list. Note what is **not** on it:

- no over-current trip
- no over-temperature anything (there is no temperature sensor, and no proxy)
- no under-voltage / battery-exhaustion trip
- no stall detector distinct from #1
- no hall-sensor plausibility check
- no command watchdog or link-loss failsafe
- no rate limit on direction reversal
- no cross-check that the two wheels of a two-wheel platform agree

**S-1 — the system has exactly one automatic protection, and it is a
last-resort detector, not a protective one.**

Mechanism #1 fires when the rotor has fallen 176° of electrical rotation behind
the field. At that angle the torque available from the commanded field is
`sin(176°) ≈ 0.07` of peak — essentially zero — while the duty regulator (see
I.2) has already wound the modulation depth to its ceiling trying to catch up.
So by construction the trip fires **only after the motor has spent some
milliseconds in the worst electrical condition it can be in**: maximum
modulation into a rotor that is not turning with the field. It is the point
past which commutation would run backwards, not a point chosen to protect
anything. For the 6.5″ motor (15 electrical cycles per wheel revolution) 176°
electrical is 11.7° of wheel rotation — the wheel barely moves while the
current goes wherever the battery and the winding resistance decide.

## I.2 The driver is smarter than its fault handling — and that is the opportunity

It is worth being precise about the control structure, because the usual
shorthand ("it's open-loop") is wrong and the wrong shorthand leads to the
wrong fixes.

`isp_bldc_motor.spin2:2110-2117`:

```
.noFault        sub     tmpY, #256/6                wc  ' target lag = 42/256 turn = 59°
    if_nc       muls    tmpY, duty_up_                  ' lagging more than 59° -> raise duty (gain 18)
    if_c        muls    tmpY, duty_dn_                  ' lagging less than 59° -> lower duty (gain 4)
                sar     tmpY, #8
                add     duty_, tmpY
                fles    duty_, duty_max_
                fges    duty_, duty_min_
```

This is a real closed loop: an asymmetric proportional regulator that drives the
**load angle** to 59° electrical by modulating duty. Rise gain 18, fall gain 4 —
deliberately quick to add torque, slow to give it back. It runs at 44 kHz. It
works, and it is the reason the thing drives at all.

What is open-loop is the **speed reference**. `angle_` is advanced by `drv_incr`
every 500 µs (`isp_bldc_motor.spin2:1950`) with no reference whatsoever to
whether the rotor is following. So the architecture is:

```
   speed reference  ──(open loop, ramps blindly)──▶  angle_
                                                       │
   rotor position ──▶ load angle error ──▶ duty regulator (closed, 44 kHz)
                                │
                                └──▶ if error > 176°: give up
```

The duty regulator saturates at `duty_max_` and then has nothing left. The speed
reference keeps advancing anyway. The lag grows. The fault fires.

**S-2 — every quantity needed for graceful degradation is already in the cog
and already computed; none of it is used for anything but the give-up test.**

> **UNBLOCKED 2026-09-10.** Whether a current limit could be built on `sense_i_` at all
> depended on what that channel actually measures — a question this study left to **T1-5** to
> answer on the bench. **Vendor documentation settles it on paper:** both revisions sense
> *"Total MOSFET load current"* with a shunt *"between common MOSFET GND and common system
> GND"* — a **DC-link shunt** carrying the whole bridge's return current
> ([`BOARD-REVISION-FACTS.md`](BOARD-REVISION-FACTS.md) §2.3), at **5 mV/A** (Rev A) and
> **150 mV/A** (Rev B, 3 mΩ × INA180B2 at 50 V/V).
>
> So S-2 is a **design** question now, not a feasibility one. Two carry-forwards: the reading
> must be corrected for **S-3** before any threshold is set against it, and it is not yet
> known whether the channel can see *reverse* (regenerative) current — see §2.8 of the facts
> file.

At the instant of the fault the driver knows, in cog registers:

| Register | Meaning | Used for protection? |
| --- | --- | --- |
| `err_` | load angle, signed, 1/256 turn units | only the ≥125 test |
| `duty_` | modulation depth, clamped at `duty_max_` | no |
| `sense_i_` | current-sense ADC, updated at 44 kHz | **no — never compared to anything** |
| `sense_u_/v_/w_` | phase voltages, 44 kHz | no |
| `pos_` | hall tick accumulator | no |
| `hall_` | raw 3-bit hall code | no |

`sense_i_` deserves its own line. Search the entire PASM driver: it appears at
`isp_bldc_motor.spin2:2002` (read), `1980-1981` (scaled), and in the block
`wrlong` at `2089`. It is never the subject of a `cmp`. **The board has a
current-sense amplifier, the driver samples it every 22.7 µs, and the value is
pure telemetry.** There is no current limit anywhere in this codebase.

That is the single largest protection gap. A BLDC driver without a current limit
is protected only by whatever the FETs and the battery can survive.

## I.3 The current reading is wrong, and wrong by a clock-dependent factor

**S-3.** This one is provable from the reference implementation.

Chip's original, `BLDC_Motor_Driver_ChipNew.spin2:178-192`:

```
                sub     sense_u_, gio_levels+0     'compute (quotient * (pin_level - gio_level)) >> 11
                muls    sense_u_, scl_levels+0
                sar     sense_u_, #11              <-- normalization
                ...
                sub     sense_i_, gio_levels+3
                muls    sense_i_, scl_levels+3
                sar     sense_i_, #11              <-- normalization
```

with `numerator LONG 3300 << 11`. The `<< 11` is a fixed-point scale that keeps
precision through the integer `qdiv` at line 165; the `sar #11` takes it back
out. Result: millivolts.

Ours, `isp_bldc_motor.spin2:2004-2014`:

```
                sub     sense_u_, gio_levels+0     ' compute (numerator * (pin_level - gio_level))
                muls    sense_u_, scl_levels+0
                sub     sense_v_, gio_levels+1
                muls    sense_v_, scl_levels+1
                sub     sense_w_, gio_levels+2
                muls    sense_w_, scl_levels+2
                sub     sense_i_, gio_levels+3
                muls    sense_i_, scl_levels+3
```

**All four `sar` instructions are gone.** In their place, `init()` changed the
numerator (`isp_bldc_motor.spin2:195`):

```
    numerator   :=    3300 * adc_fram    ' calculate the adc scaling based off the adc_fram count
```

and `getCurrent()` records the belief that this handled it
(`isp_bldc_motor.spin2:556`): *"this is handled by updating numerator in init()
to include period (adc_fram)"*.

It does not handle it. Multiplying the numerator makes the result **larger**;
the normalization that made it millivolts was a right shift, and that step was
removed. The net effect is that `sense_u_mV`, `sense_v_mV`, `sense_w_mV` and
`sense_i_mV` are all `adc_fram` times larger than millivolts.

`adc_fram` is not a constant. From `isp_bldc_motor.spin2:188`:

```
    frame_cnt := (ticks1us * (1_000_000_000 / PWM_RATE_IN_HZ)) / 1_000
```

| System clock | `adc_fram` | scale error in `sense_*_mV` |
| --- | --- | --- |
| 200 MHz | 4545 | ×4545 |
| 270 MHz (both flagship demos) | 6136 | ×6136 |
| 300 MHz | 6818 | ×6818 |

So `getCurrent()` (`isp_bldc_motor.spin2:548-559`) returns
`sense_i_mV / rSenseForBoard`, which is not amps, not tenths of a milliamp, and
not a fixed multiple of either — **it is amps × `adc_fram`, and it changes if
the user changes `_clkfreq`.** The same defect flows into `fWatts`, into
`tv_mA` / `tv_mW` on the HDMI display (`isp_bldc_motor.spin2:1386-1387`), and
into `getCurrent()` on the steering object (`isp_steering_2wheel.spin2:398`).

By coincidence 6136 is within 1.6× of the 10,000 that "multiples of 0.1 mA"
would imply, which is very likely why the numbers looked plausible enough for
`README.md` to declare the long-standing *"Calculation of current and power not
yet correct"* known issue **fixed in v5.0.0**. It is not fixed. The reading is
approximately 1.63× low at 270 MHz and 2.2× low at 200 MHz, in units of amps.

Shape of the correction (for the fix sprint, not applied here): keep a
power-of-two fixed-point scale independent of the ADC window — e.g.
`numerator := 3300 << 16` with `sar sense_x_, #16` restored on all four
channels. Tying the scale to `adc_fram` is what forced the problem, since
`adc_fram` is not a power of two and so cannot be shifted back out.

**This finding must be settled before any current-based protection is designed**,
because a current limit built on this reading would trip at a threshold that
moves with the system clock.

## I.4 Emergency stop is a 250 ms pulse, not a latch

**S-4.** `emergencyCutoff()` sets `e_stop := TRUE`
(`isp_bldc_motor.spin2:481-485`), and the driver honours it immediately and
correctly — `isp_bldc_motor.spin2:1732-1739` floats the drive and parks in
`DCS_ESTOP`, ignoring everything else while `e_stop` is set. Good.

Then the position-sense task cancels it. `isp_bldc_motor.spin2:1352-1356`:

```
        if isEmergency()
            if eStopState == true
                clearEmergency()
            !!= eStopState                                                      ' toggle stop flag
```

`eStopState` starts `false` and toggles every pass, so on the second 125 ms pass
after the e-stop takes effect, the supervisor calls `clearEmergency()` — which
sets `e_stop := FALSE` (`isp_bldc_motor.spin2:487-490`). The identical pattern
is in the steering object at `isp_steering_2wheel.spin2:818-822`, where it also
resets `userCutoff := FALSE` behind the caller's back.

So: **an emergency stop asserted by the application is unilaterally released by
the library within 250 ms.** The motor does not restart on its own — the target
increment was zeroed on the way in — but `isEmergency()` now reports `false`,
`userCutoff` is `false`, and the very next `driveAtPower()` from any source will
be obeyed as though nothing happened.

The RC demos survive this only because the *application* re-reads the switch
every pass and gates on it — `demo_dual_motor_rc.spin2:234` (`if not
bEmerCutoff`) and again at `demo_dual_motor_rc_hdmi.spin2`. The interlock lives
in the demo, not in the library. A user who follows the natural reading of the
API — call `emergencyCutoff()` from an event handler, trust it to hold — gets a
quarter-second of protection.

Worth stating plainly: `userCutoff` (`isp_steering_2wheel.spin2:735`) is written
in three places and read in exactly one — as a value pushed to the HDMI debug
display (`isp_steering_2wheel.spin2:1034`). It gates nothing.

## I.5 The fault latch is erased on a timer by a debug routine

**S-5.** `fault` is written by the driver at the moment of the trip
(`isp_bldc_motor.spin2:2108`) and is the only *sticky* evidence a fault ever
happened — `drv_state` clears itself as soon as anything re-commands the motor.

In the two-wheel object, the code that reads it also destroys it.
`isp_steering_2wheel.spin2:418-447`:

```
    ' if fault appears then let it stay for 3*1000 mSec
    ' . after that, clear it
    ...
    elseif bLeftSignal == TRUE and ltFaultSeenMS <> 0 and getms() > ltFaultSeenMS
        debug(" -------------- LtMotr Cleared FAULT --------------")
        ltWheel.clearFaultSignal()
        ltFaultSeenMS := 0
```

Three seconds after a fault appears, the latch is cleared. And `getFaultStatus()`
is **`PRI`** — its only two callers are `reportFaultStatus()` and
`reportMotorFaultOnChange()` (`isp_steering_2wheel.spin2:855, 704`), both of
which do nothing but emit `debug()` output. Since `debug()` compiles to nothing
without `-d`, in a **release build the clearing still happens** (it is in the
same `PRI`, reached from `showDriveStatesOnChange()` in the sense task at
`isp_steering_2wheel.spin2:795`) while the reporting does not.

So on a two-wheel platform the sequence is: fault occurs → latch set → no public
API can see it → latch auto-cleared three seconds later → no trace remains.

This compounds audit findings **M** (a faulted motor reports `DS_MOVING`) and
**AF** (no public fault query on the steering object) into something worse than
either: the two-wheel layer does not merely fail to expose the fault, it
actively erases the evidence on a timer.

## I.6 The serial host is told the robot is fine

**S-6.** The serial protocol's only status command,
`isp_steering_serial.spin2:432`, returns `wheels.getStatus()` — the
`DS_MOVING` / `DS_HOLDING` / `DS_OFF` triple. Per audit finding **M**, a faulted
motor satisfies `isReady()` and fails `isStopped()`, so `getStatus()` returns
`DS_MOVING`.

An RPi or Arduino driving this platform over serial therefore receives
`DS_MOVING` from a wheel that is dead. There is no serial command that can
report a fault, and no serial command that can report current, voltage, or any
health signal at all. This is the exact failure the user's 2026-09-09 mail
describes from the field
([`user-report-2026-09-09-ANALYSIS.md`](user-report-2026-09-09-ANALYSIS.md)).

## I.7 Free diagnostics are computed and thrown away

**S-7.** The hall decoder at `isp_bldc_motor.spin2:2074-2084` reads the three
sensors into `hall_` and indexes `deltas[old<<3 | new]`. The table
(`isp_bldc_motor.spin2:2223-2230`) has all-zero entries for `old = %000`,
`old = %111`, `new = %000` and `new = %111` — because those codes cannot occur
on a healthy 3-sensor hall set. The `hall_angles` table repeats the point in a
comment: `'-%000- can't happen`, `'-%111- can't happen`.

A hall code of `%000` or `%111` is the classic, unambiguous signature of a
**disconnected or dead hall sensor** — precisely the failure the user in the
field may be chasing. The driver detects the impossible code implicitly (delta
zero, angle from `hall_angles[0]` = 0), silently absorbs it, drives on with a
frozen position, and eventually trips the generic 176° fault with no indication
of cause.

Three instructions would turn that into a distinct, actionable diagnostic. The
information is already in a register.

The same applies to the distinction the driver could make but doesn't:

| Condition | Distinguishable from existing registers? | Reported today |
| --- | --- | --- |
| rotor stalled against an obstacle | `err_` large, `pos_` not advancing | generic fault |
| hall sensor failed/disconnected | `hall_` = %000 or %111 | generic fault |
| commanded past the motor's speed ceiling | `duty_` saturated, `err_` growing, `pos_` advancing | generic fault |
| motor unplugged | `err_` large, `sense_i_` ~0 | generic fault |
| phase short | `sense_i_` high | *nothing* |

Five distinct physical situations, one undifferentiated `DCS_FAULTED`.

## I.8 Nothing watches the command source

**S-8.** There is no watchdog on the command path. A motor commanded to 75%
stays at 75% forever unless something calls again. If the application cog hangs,
crashes, or blocks on a `repeat` that never exits, the drive cog holds the last
commanded speed indefinitely — the two cogs are decoupled by design
(`CLAUDE.md`: *"the drive subsystem is conceptually always running"*), which is
the right architecture and exactly why it needs a heartbeat.

Concretely, for the two supported control front-ends:

**Serial.** `isp_steering_serial.spin2` and `isp_queue_serial.spin2` contain no
timeout, no heartbeat, no last-command-age check (grepped: `timeout`,
`watchdog`, `heartbeat`, `deadman` — zero hits). Unplug the USB cable from the
RPi mid-drive and the robot keeps driving.

**RC.** `jm_sbus_rx.spin2` decodes the S.BUS frame-lost and failsafe flags
correctly and exposes them as `has_signal()` (`jm_sbus_rx.spin2:158`) and
`in_failsafe()` (`jm_sbus_rx.spin2:165`). `isp_flysky_rx.spin2` consumes them in
exactly one place — `showSbus()` at `isp_flysky_rx.spin2:169-181` — which prints
a debug line and returns nothing. `isp_flysky_rx` publishes **no** link-health
method, and neither RC demo checks. On frame loss the S.BUS driver leaves the
channel values untouched (`jm_sbus_rx.spin2:297` sets only the flag), so
`readChannel()` keeps returning the last joystick position.

**Turn the transmitter off while driving and the platform continues at the last
commanded speed and heading.** The receiver told us. We printed it to a debug
terminal nobody is watching and drove on.

## I.9 One "off" for three meanings — and a fault ignores your stop mode

**S-9 — WITHDRAWN 2026-09-10.** An earlier revision of this study argued from the
smart-pin configuration that `SM_FLOAT` could not actually float — that `wypin #0`
on the `P_INVERT_OUTPUT` low-side pins would drive them constantly high and short
the windings. **Stephen's prior bench testing shows freewheel/float works and full
braking works.** The hardware settles it; the inference was wrong. No further test
is needed to establish that both stop modes behave as named.

**S-9a — what survives, and it is sharper than what it replaces.**

> ### PR #17 EXAMINED 2026-09-10 — and a claim made earlier the same day is WITHDRAWN
>
> **WITHDRAWN: "S-9a is a regression introduced by PR #17."** That was written earlier on
> 2026-09-10 from the PR's diff hunks without checking the pre-PR-17 fault path itself. It is
> wrong. **Ignoring `stop_mode_` at fault predates PR #17.** The pre-PR-17 code:
>
> ```
>                 dirl    drive_pins      ' at FAULT: float all control pins (make them inputs)
>                 wypin   #0, drive_pins  ' reset all pwm values to OFF (better restart after fault)
>                 mov     drv_state_,#DCS_FAULTED
> ```
>
> — unconditional, no `stop_mode_` test, exactly as today. **S-9a stands as a defect; it has
> no PR #17 provenance.** It has been there all along.
>
> ### What PR #17 *did* change: the mechanism, not the policy
>
> | | pre-PR-17 | today |
> |---|---|---|
> | at fault | `dirl drive_pins` — **pins physically floated (high-Z)**, plus `wypin #0` | `call #.driveoff` — sets a **software flag**; `.driveinit`'s comment says the PWM smart pins *"are never disabled after this"* |
> | flag's effect | — | at `:2057-2058`, `driveoff=1` causes `wypin #0, drive_pins` — **duty 0 with the pins still enabled as outputs** |
>
> **This is a real difference, and it sharpens T1-1 considerably.** Pre-PR-17 a fault left the
> half-bridge high-Z, unambiguously a freewheel. Today a fault leaves the smart pins enabled
> and commands duty 0. Whether duty 0 on complementary `pwmt`/`pwmn` pairs leaves the phases
> floating or **shorted together** — which would be a brake, the opposite of S-9a's
> assumption — depends on smart-pin output polarity at zero duty, and **must be measured
> rather than reasoned about.**
>
> > **T1-1's post-fault stop mode is therefore not a confirmation of S-9a — it is an open
> > question with two opposite plausible answers.** Measure the post-fault coast-down against
> > the float and brake baselines from the same test. If it matches brake, S-9a's *impact*
> > claim inverts even though the missing `stop_mode_` test is real.
>
> ### PR #17 also made two things better — do not revert it
>
> - It **added fault suppression while drive is off**: `testb driveoff, #0 orc` at `:2105`,
>   so manually spinning a floated wheel no longer trips a fault. No pre-PR-17 equivalent.
> - It **consolidated the anti-jerk work rather than dropping it.** A first reading of the
>   diff suggested PR #17 removed the `.initAngleFmHall` calls whose comments say *"so motor
>   doesn't jerk"*. It did not: they were folded into a `SKIP`-based family —
>   `.checkstop` / `.checkstopfloatoff` / `.checkstopfloaton` at `:2150-2161` — where
>   `.checkstop` still calls `.initAngleFmHall` and still resets `duty_`, *"reduces jerk if
>   not fully aligned"*. **The jerk handling survives PR #17 intact.**
>
> ### The branch itself
>
> | | |
> |---|---|
> | `7f526a8` | 2023-09-10 — *"change how pwm enable/disable works"*, **Tim Moore** |
> | `f1c7402` | 2023-09-14 — **PR #17 merged to `main`**, shipping since |
> | `86a3e7b` | 2023-09-14 — *Revert "…"*, branch `revert-17-pwm-enable-disable`, **never merged** |
>
> A revert was opened the same day the PR merged, then abandoned. Given the above, abandoning
> it looks correct: PR #17 is a net improvement. **Do not resurrect the branch** — it would
> undo the SKIP consolidation and the fault suppression, it is 24 commits behind, and it
> conflicts with `2269894` in the same region. Keep it as evidence of the pre-PR-17
> hardware-float behaviour, which is the one thing today's code cannot show you.

Three semantically different events reach the same code:

```
.driveoff                                               ' disable pwm always
    _ret_       mov     driveoff, #1
```
(`isp_bldc_motor.spin2:2147-2148`), consumed in the 44 kHz loop at
`isp_bldc_motor.spin2:2057-2058`.

The fault path calls it **unconditionally**, without consulting `stop_mode_`
(`isp_bldc_motor.spin2:2103-2108`):

```
    if_nc       call    #.driveoff                      ' at FAULT: disable pwm output
    if_nc       mov     drv_state_, #DCS_FAULTED
```

`stop_mode_` is honoured only by `.checkstop` and its two `skip`-patterned
variants, and after a fault `.checkstop` does not run again until a **new drive
request** arrives (`.resetFault`, `isp_bldc_motor.spin2:1785-1799`).

So, given that float genuinely floats:

> **A user who called `holdAtStop(true)` — asking for the wheel to hold position —
> gets a freewheel instead the moment the motor faults, and keeps it until they
> issue a new drive command.**

A robot that faults on a slope coasts away, in the exact configuration chosen to
prevent that. The same applies to `emergencyCutoff()`, which also routes through
`.driveoff` and so also ignores the requested stop mode.

This is now a *measurement*, not an inference — see **T1-1** in the bench plan,
which characterises coast-down under float, brake, pins-cleared, and post-fault,
and reports the deceleration of each. Those four numbers are also what **C-4**
needs and what `DRIVE-OBJECTS.md` does not say.

## I.10 The unevenness, mapped

Stephen's own framing — *"our approach is pretty weak and it's unevenly spread"*
— is measurable. Every public entry point, scored on what it does when something
is wrong:

| Layer | Validates input | Reports failure how | Fault visible | Latched |
| --- | --- | --- | --- | --- |
| `driveAtPower()` | clamps silently to ±100, then to ±`maxSpeed` | `debug()` only | — | — |
| `setMaxSpeed()` | clamps silently | `debug()` only | — | — |
| `setAcceleration()` | **none** | none | — | — |
| `setRampingValues()` | **none** | none | — | — |
| `stopAfterDistance()` | `abort` | unwinds caller | — | — |
| `stopAfterRotation()` | `abort` | unwinds caller | — | — |
| `stopAfterTime()` | `abort` | unwinds caller | — | — |
| `getDistance()` | `abort` **from a getter** | unwinds caller | — | — |
| `getRotationCount()` | `abort` **from a getter** | unwinds caller | — | — |
| `start()` | returns cog+1; failure never checked (audit **AD**) | `debug()` only | — | — |
| `confgurePowerLimits()` | `abort` from inside `init()` | unwinds caller | — | — |
| motor `isFaulted()` | — | — | yes | no |
| motor `isFaultSignal()` | — | — | yes | **yes, until someone clears it** |
| steering — *any* | — | — | **no public method** | erased after 3 s |
| serial — *any* | — | — | **no command exists** | — |

Four different error conventions coexist: silent clamping, `debug()`-only
warning, `abort`, and a return value nobody checks. `abort` is used both for
programmer error (bad enum) and for state error (`incrementForPower()` aborts
when the voltage was never configured, `isp_bldc_motor.spin2:847`) — and it is
used inside *getters*, so `getDistance(DDU_KM)` can unwind a caller that was
merely asking a question (audit **I/T**).

And the visibility column collapses to nothing at exactly the layer most users
actually program against. A single-motor user has `isFaulted()`. A two-wheel
user — the flagship configuration, the one both release demos ship — has
nothing.

## I.11 What a protection layer would look like

Not a design; a statement of the shape, so the fix sprint has a target.

**Tier 0 — in the 44 kHz driver loop, from registers already present:**

1. **Current limit.** `cmp sense_i_, i_limit_` → on exceed, subtract from `duty_`
   instead of adding. Fold-back, not trip. Costs ~4 instructions in a loop that
   has headroom (`fit 496` currently reports 443 used). *Blocked on S-3 —
   the reading must mean something first.*
2. **Soft lag limit.** When `|err_| > soft_threshold` (say 90° rather than 176°)
   **and** `duty_` is saturated at `duty_max_`, stop advancing `angle_` — or back
   `drv_incr` down. The motor then settles at whatever speed the load allows
   instead of accelerating into a fault. This is the "fallback algorithm so the
   motor doesn't give up under load" that `README.md` has listed as a known issue
   since v2.0.0. See **C-5**.
3. **Hall plausibility.** `hall_ == %000 or %111` → distinct fault code.

**Tier 1 — fault taxonomy instead of one bit:** replace the single `fault` long
with a bitfield (`FLT_LAG`, `FLT_OVERCURRENT`, `FLT_HALL`, `FLT_STALL`,
`FLT_UNDERVOLT`) written by the driver, latched until *explicitly* cleared by
the application. Never auto-cleared on a timer. The 15th long is already
reserved in the ABI (`isp_bldc_motor.spin2:1544`) — this is a change of meaning,
not of layout.

**Tier 2 — make it visible at every layer.** `isFaulted()` / `faultFlags()` /
`clearFault()` mirrored on `isp_steering_2wheel` (per `CLAUDE.md`'s rule that
new public enums must be mirrored) and a `getfaults` serial command. Delete the
3-second auto-clear. Delete the e-stop auto-clear.

**Tier 3 — watchdog.** An optional `setCommandTimeout(ms)`; if no drive command
arrives within the window, ramp to zero. Publish `linkIsHealthy()` from
`isp_flysky_rx` (the data is already decoded) and wire the RC demos to it. This
is the difference between a demo and something you let run in a parking lot.

Ordered by lives-and-hardware saved per line of code changed: **1, 2, Tier 2,
3.**

---

# PART II — CAPABILITY

## II.1 The mental model that makes everything else obvious

The single most useful thing to write down, because it is nowhere in the docs:

> **`drv_incr` is the rate at which the commanded magnetic field rotates, in
> units of 2³² per full electrical revolution, applied every 500 µs.**

From that, everything is computable:

```
  mechanical RPM = drv_incr × 2000 × 60 / (2³² × electricalCyclesPerRev)
```

with `electricalCyclesPerRev` = 15 for the 6.5″ hub motor (30 poles) and 4 for
the DocoEng 4k motor (8 poles) — both stated in the comments at
`isp_bldc_motor.spin2:2233-2250`.

**C-1 — check it against the code's own characterization notes.** At 18.5 V the
6.5″ table entry is `147_000_000` (`isp_bldc_motor.spin2:973`) and the comment
beside it reads *"anything above yields RPM 272.0"*. The formula gives:

```
  147e6 × 2000 × 60 / (4.295e9 × 15) = 273.8 RPM
```

The model is exact. Which means the entire per-voltage lookup table — eight
magic numbers per motor per board revision, the thing `ADDING_MOTOR.md` exists
to explain how to produce — is **not a calibration**. Each number is one fact:
*the highest speed this motor can be commanded to at this voltage before the
back-EMF makes it impossible to follow.* It is a back-EMF ceiling, hand-measured
by driving the motor until it faults and writing down the number just below.

That reframing is the key to Part II. It says:

- The `power → speed` map is already perfectly linear and physically meaningful
  (`incrementForPower()` → `map()`, `isp_bldc_motor.spin2:845-858, 789-810`).
  `driveAtPower(50)` really is half of top speed. That part is *good* and should
  be kept and documented — it is better than most hobby motor APIs.
- The ceiling exists only because the driver has no way to notice it is being
  asked for the impossible. Give it that ability (**C-5**) and the tables become
  unnecessary — the motor finds its own ceiling every time, at the actual battery
  voltage, under the actual load, on the actual board.
- The unit users would actually want — RPM, or mm/s — is one multiply away and
  is not offered.

## II.2 Ramps: what they actually do

`init()` sets four values (`isp_bldc_motor.spin2:229-233`):

```
    ramp_max := 200_000     ' ceiling on the per-500µs increment step
    ramp_min := 1_500       ' first step
    ramp_inc := 22          ' step growth per 500 µs
    ramp_down := 50_000     ' fixed decrement step
```

**Spin-up** (`isp_bldc_motor.spin2:1860-1887`) adds `ramp_curr` to `drv_incr`
every 500 µs, and `ramp_curr` itself grows by `ramp_inc` each pass until it hits
`ramp_max`. That is **constant jerk**: acceleration ramps linearly, speed grows
quadratically.

**Spin-down** (`isp_bldc_motor.spin2:1896-1913`) uses `ramp_down` flat. That is
**constant deceleration**.

Concretely, for the shipped dual-motor configuration (6.5″ motor, 18.5 V,
`maxSpeed = 75`, target increment ≈ 110,000,000):

| | value |
| --- | --- |
| time to reach commanded speed | ~1.55 s |
| acceleration step at the moment of arrival | 69,480 per 500 µs |
| acceleration step one pass later | **0** |
| time to stop from that speed | 1.10 s |
| deceleration step throughout | 50,000 per 500 µs |
| deceleration step at the moment of arrival | 50,000 → **0** |

**C-2 — both ramps end in a step discontinuity in acceleration.** The profile
climbs smoothly and then, on a single 500 µs boundary, acceleration goes from
1.4× the braking rate to nothing. That is a jerk impulse, and it is felt as the
lurch at the top of every spin-up and the snap at the end of every stop. This is
the mechanical definition of "doesn't feel natural." No S-curve, no rounding, no
taper.

**C-2b — `ramp_max` is dead code in every shipped configuration.** `ramp_curr`
starting at 1,500 and growing by 22 per pass needs 9,022 passes — 4.5 seconds —
to reach 200,000. The fastest shipped configuration (DocoEng at 24 V on Rev B,
increment 460,000,000) arrives at its target after ~3.2 s with `ramp_curr` at
143,752. The clamp never engages for any motor, voltage, or board revision this
library supports.

**C-2c — the ramps are in units of nothing.** `setAcceleration(rate)`
(`isp_bldc_motor.spin2:308-311`) passes `rate` straight into `ramp_inc`. Its
doc-comment reads *"where {rate} is [??? - ???] mm/s squared (default is ???
mm/s squared)"* — the author's own question marks, still in the shipped source.
`demo_dual_motor_rc.spin2:194` feeds it `readchannel(CTL_VRA)/10`, a raw RC
potentiometer value. There is no validation (`setRampingValues()` has none
either), and audit finding **G** records that a bad value silently corrupts
ramping. A user cannot ask for "0.5 m/s²" because nothing in the system knows
what a metre is at that layer.

The correct unit is derivable and simple. `ramp_inc` is jerk; `ramp_curr` is
acceleration in increment-units per 500 µs, and by **C-1** increment converts to
RPM by a fixed constant, and RPM converts to mm/s via the wheel circumference
the object already computes (`circInMM_x10`, `isp_bldc_motor.spin2:254-256`).
The whole chain exists. Nobody joined it up.

**C-2d — prior art is in the tree, unadopted.** `src/test_new_ramps.spin2`
prototypes a two-rate ramp: `ramp_slo_ = 12_000` below a 50,000 threshold, then
`ramp_fast_ = 50_000` above it (`test_new_ramps.spin2:153-155`), with the
comment *"slower initial ramp so we don't fault."* It was never merged. It is a
better shape than the shipped quadratic for the specific problem of faulting on
start, but it is still open-loop guessing, and **C-5** supersedes it.

## II.3 Deceleration: `driveForDistance()` overshoots by about 1.2 metres

**C-3.** This is the most user-visible capability defect in the library, and it
falls out of two facts that are individually reasonable and jointly disastrous.

*Fact one:* the distance check runs in the 8 Hz position-sense task
(`isp_bldc_motor.spin2:1343-1347`; steering equivalent at
`isp_steering_2wheel.spin2:807-811`). Granularity: 125 ms.

*Fact two:* when the target is reached, the code calls `setTargetAccel(0)` —
which begins a *normal* ramp-down. There is no lookahead, no braking-distance
calculation, nothing that starts slowing before the target.

For the shipped dual-motor configuration (6.5″ wheels, 518.8 mm circumference,
`maxSpeed4dist = 75` → ~205 RPM → **1.77 m/s**):

| phase | time | distance |
| --- | --- | --- |
| target passed, waiting for next 8 Hz check | up to 125 ms | up to **221 mm** |
| ramp-down at `ramp_down` = 50,000/500 µs | 1.10 s | ~**974 mm** |
| **total overshoot** | | **≈ 1.2 m** |

`driveForDistance(2, DDU_FT)` — 610 mm — travels roughly **1.8 m**, three times
the request. The method is only meaningful for distances much larger than the
stopping distance, and nothing in `DRIVE-OBJECTS.md` says so.

Note also that `ramp_down` is an *absolute* step, so stopping distance scales
with speed **and** with the configured voltage: the same call stops in ~0.6 m at
6 V and ~1.4 m at 24 V. The feel of the API changes when the user changes their
battery.

The fix is standard motion control and the driver is the right place for it:
give the PASM loop the stop target in hall ticks, let it compute
`stoppingDistance = drv_incr² / (2 × ramp_down)` each pass, and begin the
ramp-down when the remaining distance drops below it. That is a trapezoidal
profile, checked at 2 kHz instead of 8 Hz, and it lands within a hall tick or
two. The driver already owns `pos_`.

## II.4 Braking: three behaviours, none of them named that

**C-4.** The API's vocabulary for stopping is `holdAtStop(bEnable)` — one
boolean — plus `stopMotor()` and `emergencyCutoff()`. What a user of a motor
driver expects to be able to ask for:

| Want | Available today |
| --- | --- |
| coast to a stop (no braking) | `holdAtStop(false)` — works; **but a fault silently downgrades brake to coast**, see **S-9a** |
| ramp down at a chosen rate | `setRampingValues()`'s 4th argument, undocumented, unvalidated, no units |
| stop as fast as the motor can without faulting | **not available** |
| hold position against a load once stopped | `holdAtStop(true)` — this one works |
| brake now, hard, and stay stopped | **not available** — `emergencyCutoff()` is the closest, and it self-clears (S-4) |
| reverse-plug braking | **not available** |

There is also no rate limit on direction reversal. `driveAtPower(+75)` followed
immediately by `driveAtPower(-75)` enters `DCS_SLOW_TO_CHG`
(`isp_bldc_motor.spin2:1933-1947`), which ramps down at `ramp_down`, then
spins up the other way. That is the correct structure — but the ramp-down rate
is the same fixed 50,000 whether the platform is a 2 kg bench rig or a 30 kg
robot, and nothing checks whether the motor actually followed.

## II.5 The one change that fixes the most: lag-limited ramping

**C-5.** This is the recommendation the rest of Part II is building toward, and
it closes `README.md`'s oldest open known issue.

The driver knows, every 22.7 µs, both of these:

- `err_` — how far the rotor is behind the commanded field
- `duty_` — whether the torque regulator still has anything left

Today it uses them to decide when to give up. The proposal is to use them to
decide **how fast to accelerate**:

```
  each 500 µs pass, before advancing drv_incr:
      if |err_| > lag_soft  and  duty_ >= duty_max_:
          the motor cannot follow -> do not increase drv_incr
          (and if |err_| > lag_hard: decrease it)
      else:
          ramp normally
```

Consequences, in order of value:

1. **Faults become rare.** The condition the 176° trip detects can now only be
   reached by a genuine mechanical event — a stall, a jam, a lost hall sensor —
   because the driver stops digging as soon as the rotor starts falling behind.
   This *is* the "fallback algorithm so the motor doesn't give up under load"
   that has been a known issue since v2.0.0.
2. **The ramp becomes load-adaptive for free.** Uphill, on gravel, with a heavy
   payload, the acceleration self-limits to what the motor can deliver. The
   comment history in `init()` (`isp_bldc_motor.spin2:223-225`) is a record of
   Stephen hand-tuning `ramp_inc` against gravel surfaces at three different
   voltages — that tuning exercise disappears.
3. **The per-voltage tables stop being load-bearing.** Command 100% at any
   voltage; the lag limiter holds the motor at whatever it can actually do. The
   tables can stay as a starting hint but a wrong entry stops being a fault
   generator. `ADDING_MOTOR.md` gets substantially shorter.
4. **It makes the ramp shape almost irrelevant.** A limiter that refuses to
   outrun the rotor produces a naturally-tapering approach to top speed — the
   S-curve appears on its own, because the achievable acceleration falls as
   back-EMF rises.

Cost: roughly a dozen PASM2 instructions in a loop with 53 longs of cog space
free (`fit 496`, currently 443). No ABI change — `lag_soft` / `lag_hard` are new
parameters in the 14-long params block, which means bumping
`DRVR_PARAMS_LONGS_COUNT` and the matching `DAT` in lockstep, per `CLAUDE.md`.

This is the highest-value change identified in either study.

## II.6 Voltage: told, not sensed — and it does not have to be

**C-6.** Today the user declares `DRIVE_VOLTAGE` in
`isp_bldc_motor_userconfig.spin2` and the library trusts it completely: it
selects the speed ceiling (`confgurePowerLimits()`), the commutation offsets for
the DocoEng motor (`offsetsForMotor()`), and the wattage arithmetic
(`motorVoltage()`). Audit finding **AK** records the consequence — as a LiPo
sags from 18.5 V to 15 V under load, every one of those choices silently becomes
wrong, and the ceiling that was safe at full charge is now above what the motor
can follow. The robot's fault rate goes up as the battery goes down, which is
precisely the field report we have.

**The hardware may already be able to measure it.** The board presents five ADC
channels; the driver configures four (`isp_bldc_motor.spin2:1644-1689`) and
uses three phase voltages plus the current sense. `pin_adc_x_i` (base+3) is
declared and never used — comparison with Chip's reference
(`BLDC_Motor_Driver_ChipNew.spin2:360-375`, which also declares `pwm_x_l/h`)
shows it belongs to the board's **fourth half-bridge**, not to a bus divider.
So there is no dedicated Vbus channel.

But there is an inference path. The three phase drives are centred: the code
subtracts the midpoint of the three and adds `bias = frame_cnt/4`
(`isp_bldc_motor.spin2:2038-2052`), and the PWM compare window is
`frame_cnt/2`. So the *average of the three phase duties is 50% by
construction*, independent of angle and of commanded duty. The ADCs integrate
over a full frame. Therefore:

```
  (sense_u + sense_v + sense_w) / 3  ≈  Vbus / 2 × (board divider ratio)
```

If that holds, the bus voltage is available whenever the drive is energized, at
44 kHz, from hardware already installed and already sampled — for the cost of
one add and one shift.

**This is a hypothesis with a cheap test.** Drive a motor at a fixed power and
log `(sense_u_mV + sense_v_mV + sense_w_mV)/3` against a DMM on the battery, at
two supply voltages (say 12 V and 18.5 V), on both board revisions. If the ratio
is constant, the divider constant falls out of the two readings and voltage
sensing exists. *This test is only meaningful after S-3 is fixed* — the sense
values are currently scaled by `adc_fram`, which will cancel in the ratio but
not in the absolute constant.

What it would buy:

- speed ceilings that track the actual battery instead of a declared nominal
- a genuine low-battery warning and cutoff — LiPo packs are damaged by
  over-discharge, and this library will happily drive one flat
- correct wattage numbers
- `DRIVE_VOLTAGE` demoted from a load-bearing constant to a sanity check

Even if the inference fails, saying so in the docs is worth more than the
current silence.

### C-6b — a direct Vbus read the board may already support, at zero cost

**C-6's averaging inference is not the only route, and probably not the best one.**

> ### CORRECTED 2026-09-10 — read this before the table below
>
> **Stephen confirmed all four channels are populated: U, V, W and X.** The
> question this section was gated on is answered — the fourth half-bridge is real
> hardware.
>
> **Two claims below were wrong, and the correction improves the position:**
>
> 1. **`pin_adc_x_i` (base+3) IS configured — it is a live, running ADC.** The
>    table said "never `wrpin`'d". In fact `adc_pins` is `(4 << 6) + 0`, i.e.
>    *base+0 addpins 4* = **five** pins, base+0 through base+4 — which includes
>    base+3. Every `wrpin adc_modes+0/+1/+2` and every `dirh adc_pins` in the
>    setup applies to X along with the rest, so X is sampling in the same
>    `P_ADC_1X | P_COUNT_HIGHS` mode, phase-locked to the same PWM frame. The
>    trailing comment *"adc_x not used"* means **never read**, not never
>    configured: the calibration reads (`rdpin gio_levels+0..3`,
>    `rdpin vio_levels+0..3`) cover only U, V, W and CUR, and no `scl_levels`
>    entry exists for X. **So a harness needs no setup at all to read X** — but it
>    must supply X's own GIO/VIO calibration to convert counts to mV, since the
>    driver never collected it. For C-6b's *ratio*, that does not matter.
> 2. **`pwm_x_l` / `pwm_x_h` are NOT declared in this driver.** The pin list ends
>    at `pin_pwm_w_h` (base+13); there is no `pwm_x_*` symbol anywhere in
>    `isp_bldc_motor.spin2`. Chip's reference declares them; ours never did. The
>    board's fourth-channel gate pins are base+14/15 by position, and they are
>    free within the 16-pin group — but nothing in our source names them.
>
> **And one hazard that only exists now that the FETs are known to be populated:**
> driving base+14 and base+15 both active at once is a **shoot-through** that
> destroys the half-bridge and possibly the board. See the rewritten **T1-13** in
> the bench plan before anyone PWMs that channel.

Our driver names 14 of the 16 pins in a group. The fourth channel's three pins
are the exception:

| Pin | Name | Status |
| --- | --- | --- |
| base+3 | `pin_adc_x_i` | declared (`isp_bldc_motor.spin2:2309`) and **configured and running as an ADC** (it falls inside `adc_pins`), but **never read** |
| base+14 | (`pwm_x_l` on the board) | **not declared in this driver at all** — outside `all_pins`, *"skip last 2 pwm pins, not used"* |
| base+15 | (`pwm_x_h` on the board) | likewise |

These are the board's **fourth half-bridge** — the 64010 is a *Universal* Motor
Driver, and Chip's reference declares all three
(`BLDC_Motor_Driver_ChipNew.spin2:363, 374-375`). This library drives a 3-phase
BLDC and so never uses the fourth channel. **Confirmed populated, 2026-09-10.**

**Vbus can therefore be read directly.** Switch the fourth channel's half-bridge —
with nothing connected to that phase, no load current flows — and its phase node
follows Vbus. `pin_adc_x_i` is that node, brought back to the P2 through whatever
divider the board already uses for the other three phase senses, and it is
*already sampling*. The read costs nothing; only the switching needs care.

Why this is better than **C-6**:

- it is a **direct measurement**, not an inference resting on the drive being
  centred at 50 %
- it works with **the motor stopped**, so voltage is known *before* choosing a
  speed ceiling — which is exactly when you need it
- it needs **no external hardware at all** and no change to the driver: the
  harness can configure base+3 and base+14/15 from a spare cog, because the
  driver never touches them

Two things to settle, both cheap:

1. **Are the fourth channel's FETs actually populated on the 64010?** This needs
   the schematic, not the source. *(Open question for Stephen.)*
2. **Bootstrap gate drivers cannot hold a high side on indefinitely** — the
   bootstrap capacitor charges only while the low side conducts. Workaround: PWM
   the fourth channel at a known duty and read the average, then
   `Vbus = reading / duty`. Bootstrap-friendly and just as accurate.

Even if the FETs are absent, `pin_adc_x_i` may still sit on the divider network
and read something useful passively — worth one line of test code to find out.

**A third route, also free:** at any instant a phase's high side is on, that
phase node *is* Vbus, and the driver already knows the duty it commanded
(`drive_u_`). So `Vbus ≈ sense_u_mV / (drive_u_ / frame)`. Unlike **C-6** this
makes no assumption about centring, so it serves as an independent cross-check
of whichever method is adopted.

### C-6c — "which size battery" is the wrong question

The natural next thought is to auto-detect the pack — 4S, 5S, 6S — so the user
need not declare `DRIVE_VOLTAGE`. **Open-circuit voltage cannot do this
reliably**, and it is worth being explicit about why:

| Pack | Empty (3.0 V/cell) | Full (4.2 V/cell) |
| --- | --- | --- |
| 3S | 9.0 | 12.6 |
| 4S | 12.0 | 16.8 |
| 5S | 15.0 | 21.0 |
| 6S | 18.0 | 25.2 |
| 7S | 21.0 | 25.2 → 29.4 |

**Every adjacent pair overlaps.** A reading of 18.5 V is a half-charged 5S or a
nearly-flat 6S, and nothing in the voltage alone separates them. Worse, the
existing enum spans chemistries — `PWR_6p0V`, `PWR_12p0V` and `PWR_24p0V` are
lead-acid nominals, not LiPo — so per-cell inference would have to know the
chemistry before it could count cells.

**But the library does not actually need the cell count.** `DRIVE_VOLTAGE` feeds
exactly three things: the speed ceiling, the DocoEng commutation offsets, and the
wattage arithmetic. **All three want volts, not a pack description.** A 4S at
full charge and a 5S at half charge both sit near 15 V and both *should* be
driven identically — that is physically correct, and the current enum actively
prevents it.

So the fix is not detection. It is:

1. **Interpolate the existing tables on measured volts** instead of indexing them
   by a declared nominal. That alone closes **AK**, and it is a better change
   than any detection scheme because it tracks sag continuously as the pack
   drains under load.
2. **And note that C-5 subsumes most of this.** With a lag-limited ramp the
   driver discovers its own ceiling every time, at the actual voltage, under the
   actual load. **You do not need to know the battery voltage to pick a safe
   speed ceiling if the motor is allowed to tell you.** That materially lowers
   the value of voltage sensing for its single largest use case.

### Where a genuine product-side need remains

Everything above is satisfied by bench fixtures plus a software change. **One
thing is not, and it is a real product gap:** there is no low-voltage cutoff.
This library will drive a LiPo flat and damage it, and nothing warns the user.

That is the one place cell count genuinely matters, because the safe threshold is
per-cell (≈3.3–3.5 V/cell under load) and only the cell count converts it to a
pack threshold. Two ways to get it, neither needing new hardware:

- **Ask for it, and ask better.** Replace `DRIVE_VOLTAGE = PWR_18p5V` with
  `BATTERY_CELLS = 5` (plus chemistry where it matters). This is a *simpler*
  question than the one users are asked today — they know their pack is "5S";
  they may not know 5S means 18.5 V, and the current enum forces them to make
  that translation and get it right. Config gets easier **and** more accurate.
- **Learn it, self-calibrating.** A pack straight off the charger is
  4.15–4.2 V/cell, and at full charge the pack voltages are unambiguous (8.4,
  12.6, 16.8, 21.0, 25.2, 29.4 — cleanly separated). Record the highest voltage
  ever seen in non-volatile storage; `cells = round(maxV / 4.2)` converges to the
  right answer the first time the user runs on a fresh charge.

**Recommended: the config change.** It costs nothing, it cannot be wrong in a
way the user cannot see, and it makes the existing configuration question better
rather than adding a mechanism. Voltage measurement then supplies the runtime
value, and the cutoff has what it needs.

**Priority, stated honestly:** this sits below **C-5**, below the fault-visibility
work, and below fixing **S-3**. It is a real gap — a damaged LiPo is a real cost
to a real user — but it is not what is breaking robots in the field today.

## II.7 What "general purpose" would actually require

**C-7.** Stephen's phrasing was *a stronger, more general-purpose motor driver
that would feel more natural.* Ranked by what a user hits first:

| # | Capability | Present? | Notes |
| --- | --- | --- | --- |
| 1 | doesn't fault under normal load | no | **C-5** |
| 2 | stops where you asked it to | no | **C-3**, ~1.2 m over |
| 3 | smooth start and stop | partly | **C-2**, jerk step at both ends |
| 4 | acceleration in real units | no | **C-2c**, `??? mm/s²` |
| 5 | speed in real units (RPM / mm/s) | no | one multiply away, **C-1** |
| 6 | tells you when it's unhappy | no | **S-5**, **S-6** |
| 7 | current limit | no | **S-2** |
| 8 | believable current reading | no | **S-3** |
| 9 | knows its battery | no | **C-6** |
| 10 | works on a new motor without characterization | no | **C-1** reframing + **C-5** |
| 11 | closed-loop speed hold on a grade | no | see below |
| 12 | position hold / go-to-angle | partial | `moveShaftToAngle()` is test-only, single-shot |

On #11 — true speed regulation. Today `driveAtPower(50)` commands a field speed;
on a downhill the rotor is dragged *ahead* of the field and the duty regulator
backs off, but there is no mechanism to command "hold 200 RPM regardless." The
ingredients are present (`pos_` at 44 kHz, hall ticks per rotation known) but the
telemetry that would feed it is broken — audit finding **W**, one wrong variable
name at `isp_bldc_motor.spin2:1303`
(`hallWindowSum += hallCntsIn8thSec` should be `+= nHallCntsIn8thSec`), zeroes
every RPM and speed reading the library produces. Fixing **W** is a one-word
change and is a prerequisite for anything speed-based, including a user-facing
`getSpeed()`.

On #12 — the test-only `moveShaftToAngle()` (`isp_bldc_motor.spin2:356-362`)
plus the existing `hold` mode is 80% of a position-control API. Users building
arms, turrets and lifts want it; it is closer to shipping than it looks.

---

# PART III — SYNTHESIS

## What most benefits a user

Merging both heads, ordered by *user benefit per unit of risk and effort*. The
first four are, in my judgement, the whole answer to Stephen's question.

| Rank | Change | Head | Why here |
| --- | --- | --- | --- |
| 1 | **Lag-limited ramp** (**C-5**) | both | Closes the oldest known issue. Turns faults into speed droop. Makes ramps load-adaptive. Makes the voltage tables non-critical. ~12 PASM instructions. |
| 2 | **Fault taxonomy, latched, visible at every layer** (**S-5/S-6/S-7**, audit **M/AF**) | protection | Users currently cannot see the one thing that goes wrong. Includes deleting both auto-clears. |
| 3 | **Fix the current scaling** (**S-3**), then **add a current limit** (**S-2**) | protection | The only real hardware protection available, and it is one restored `sar` away from being measurable. |
| 4 | **Trapezoidal distance stops** (**C-3**) | capability | `driveForDistance()` is a headline API that misses by a metre. Move the stop decision into the 2 kHz loop. |
| 5 | **Fix finding W** (one word) | capability | Unblocks all speed telemetry and any future speed regulation. |
| 6 | **Real units for acceleration and speed** (**C-2c**, **C-1**) | capability | Removes `???` from the shipped doc-comments; makes the API describable. |
| 7 | **Command watchdog + RC link-health** (**S-8**) | protection | The receiver already tells us. |
| 8 | **Latch the e-stop** (**S-4**) | protection | Small, but the current behaviour is indefensible if anyone reads the method name and believes it. |
| 9 | **Make the fault path honour `stop_mode`** (**S-9a**), and give fault / e-stop / float distinct behaviours | protection | A faulted robot currently freewheels even when configured to brake. Quantified by bench **T1-1**. |
| 10 | **Bus voltage** — prefer the direct 4th-channel read (**C-6b**), fall back to inference (**C-6**); drive the tables from measured volts (**C-6c**) | both | Closes **AK**. Largely subsumed by **C-5** for the speed-ceiling case, so its real value is the missing low-voltage cutoff. |
| 11 | S-curve ramp shaping (**C-2**) | capability | Deliberately last — **C-5** delivers most of the smoothness for free. Do it after, if it is still wanted. |

## Bench measurements this study could not make

**Superseded — these are now a written run sheet:**
[`BENCH-TEST-PLAN-2026-09-10.md`](BENCH-TEST-PLAN-2026-09-10.md).

That plan turns every open question from both studies into an ordered, largely
automated suite: three tiers, one physical rig, one evening. In summary:

| Tier | Needs | Closes |
| --- | --- | --- |
| **0** — dry, no motor, no risk | P2 + Rev B board, motor rail off | **A1**, **A2**, **A3**, **F**, **O**, **G**, **I/T**, **K**, **AE**, **AD**, and a first look at **C-6b** |
| **1** — wheels up | dual platform on blocks, Rev B, 18.5 V | **S-9a**, **W**, **C-1**, **S-3**, **C-6**, **C-6b**, **C-5**'s gate, **C-3**, **M**, **AF**, **Z**, **AI**, and the user's field discriminator |
| **2** — wheels down | same rig, lowered | **AC** |

Two things worth carrying back into this document:

- **The plan needs no external instruments.** A ≈$15 front end (§2A of the plan)
  puts bus voltage, bus current and board temperature on three spare P2 pins,
  sampled by the P2's own ADC. That makes the electrical references automatic and
  — more importantly — makes them work during *transients*, which no panel meter
  can do. It is bench equipment only, not proposed product hardware.
- **The single most consequential test is `T1-7`.** It asks whether `duty_`
  saturates before the lag runs away. If it does, **C-5** is buildable exactly as
  specified. If it does not, the highest-value recommendation in this study needs
  redesigning — and that is worth knowing before any PASM is written.

**ANSWERED 2026-09-10 — all four channels are populated (U, V, W, X), per
Stephen.** The question as originally posed: are the 64010's fourth-channel
FETs populated? It decided whether **C-6b** — the direct bus-voltage read — is
available. **It is available.** What remains is not a schematic question but a
switching one: see the shoot-through hazard in the bench plan's **T1-13**.

## Relationship to the first study

The audit found 24 things wrong. This study asks *why* the same class of thing
keeps being wrong, and lands on two root causes:

- **Protection was never designed as a layer.** It accreted: one detector in the
  PASM driver, one boolean at the Spin2 boundary, four different error
  conventions above that, and nothing at all at the two-wheel and serial layers
  where most users live. The auto-clears in the sense tasks are the tell — they
  are there so the *debug display* wouldn't stay stuck, and they cost the system
  its only latched evidence.
- **The speed reference was never closed.** Every hand-tuned constant in this
  driver — the eight-entry voltage tables, `ramp_inc`, `ramp_min`,
  `ramp_down`, the gravel-surface comment history, the whole of
  `ADDING_MOTOR.md` — exists to compensate for a control loop that does not
  watch whether the motor is following. Close it and most of that apparatus
  becomes optional.

---

*Study conducted 2026-09-09. No source modified. Findings only — the fix sprint
is still unplanned, per Stephen's standing instruction that studies stop at the
findings.*

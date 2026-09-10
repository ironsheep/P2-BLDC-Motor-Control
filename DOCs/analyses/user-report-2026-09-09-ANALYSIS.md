# Analysis — user report of dual-motor faults, 2026-09-09

Report: [`user-report-2026-09-09-dual-motor-fault.md`](user-report-2026-09-09-dual-motor-fault.md)
Audit: [`DRIVER-AUDIT-2026-09-09.md`](DRIVER-AUDIT-2026-09-09.md)

**Short answer to the reporter's question — "is there a known reason for this fault
problem?" — yes.** Four of their five observations map onto defects and gaps this audit
found independently, two days of code reading before the mail arrived. One observation
(the demo carrying on with a dead wheel) is an exact field demonstration of the audit's
highest-value finding.

Their hardware is almost certainly fine. Their diagnosis that "the boards are operating
properly" is supported by the code.

---

## Observation → finding map

| # | Their observation | Maps to | Confidence |
| --- | --- | --- | --- |
| 4 | Demo carries on driving only the left motor after the right faults | **AF + M** — no public fault query, and `getStatus()` reports a faulted motor as `DS_MOVING` | **Confirmed** — mechanism traced through their exact demo |
| 2 | Right motor faults more than left | **AI (new)** — the reversed motor runs a commutation offset that was never characterized, only derived | **High** |
| 1 | Dual faults, single does not | **Z** — fault is a hard latch with no fallback, and two motors ramp simultaneously off one pack | **High** |
| 3 | First run fine, later runs fault | **AK (new)** — no voltage feedback; the power table is fixed at the *declared* nominal | **High** |
| 5 | Hello World and single-motor demos pass | Consistent with all of the above | — |

---

## Observation 4 — the demo keeps going with a dead wheel

**This is finding [AF](DRIVER-AUDIT-2026-09-09.md#af) demonstrated in the field**, and it
is the part of their report that is purely a software defect.

Their demo calls `waitUntilMotorDone()` between moves
(`demo_dual_motor.spin2`), which polls:

```spin2
if wheels.isStarting() == false ...     ' lt.isStarting() OR rt.isStarting()
if wheels.isStopped()  == false ...     ' lt.isStopped() AND rt.isStopped()
```

Neither predicate can see a fault. `isStopped()` tests `drv_state == DCS_STOPPED`, and a
faulted motor is in `DCS_FAULTED` — a different state. So the demo has exactly three ways
to ask about the right motor, and **all three are blind to the fault**:

- `wheels.getStatus()` → reports `DS_MOVING` for a faulted motor (finding **M**), and the
  `DS_*` enum has no value for "faulted" even if the logic were fixed
- `wheels.isFaulted()` → **does not exist** on the steering object
- `wheels.getDriverState()` → exists but is `PRI`, unreachable from the demo

The steering object *does* know — `getFaultStatus()` and `getDriverState()` are used
internally — but both are private. So the demo drives on, one wheel dead, and the only
reason the reporter knows anything is wrong is that the *driver's own* `debug()` output
prints it.

**They are not missing an API call. There isn't one.**

---

## Observation 2 — why the right motor, specifically

The right motor is the one the steering object reverses:

```spin2
rtWheel.forwardIsReverse()        ' isp_steering_2wheel.spin2:110
```

That makes every right-motor command take the **reverse** path through
`incrementForPower()`, which uses `offset_rev` rather than `offset_fwd`. And for the 6.5″
hub motor, `offsetsForMotor()` (`isp_bldc_motor.spin2:884-886`) is:

```spin2
' 4 degrees per tic, offset was actually 5 tics! or 20 degrees
' from characterization at 18v5:
fwdDegrees := ofsDegr := 43
revDegrees := 360 - fwdDegrees          ' = 317 — DERIVED, not measured
```

**The reverse offset is assumed to be the mirror of the forward offset.** It was never
independently characterized. The forward value (43°) carries a comment saying it came from
bench characterization; the reverse value is arithmetic.

The author was aware this is an assumption — the DocoEng branch of the same method carries
the note `revDegrees := 360 - ofsDegr    ' vs. using 360?`, an open question left in the
code.

Commutation offset is exactly the parameter that sets how efficiently torque is produced.
If the true optimal reverse offset for these motors is not 317°, the right motor produces
less torque per amp than the left, lags further under identical load, and reaches the
~176° error threshold first. **That is a direct, specific mechanism for a left/right
asymmetry**, and it predicts precisely what they observe: right usually, left sometimes.

Recorded as new finding **AI**.

---

## Observation 1 — dual faults where single does not

Nothing in the two-motor path makes an *individual* motor weaker. What changes is the
load on the shared supply and the absence of any coordination:

- Both motors ramp **simultaneously and identically** — `ramp_min` 1 500, `ramp_inc` 22
  every 500 µs, up to `ramp_max` 200 000. Peak inrush for the two wheels coincides exactly.
- There is **no current limiting** anywhere in the driver. The ADC reads phase current
  into `sense_i_mV`, but nothing closes a loop on it — it is telemetry only.
- There is **no stagger, no soft-start offset** between the two wheels.
- When a motor cannot keep up, finding [Z](DRIVER-AUDIT-2026-09-09.md#z) applies: the
  driver's entire response is *stop* — PWM off, `DCS_FAULTED` latched, no torque back-off
  and no retry. This is README's own known issue: *"we need to add a fallback algorithm so
  the motor doesn't 'give up' under load."*

The single-motor demo halves the peak current draw and removes the coincident inrush. That
their single-motor runs pass on both motors is consistent with the motors and boards being
healthy, and with the margin simply being too thin for two at once.

**How thin the margin is, in the code's own words.** The 18.5 V entry for the 6.5″ motor is
`147_000_000`, and the comment beside it reads:

```
' 147_000_000 anything above yields RPM 272.0, cts/Sec 408 (until fault at 277.3 416)
```

Full commanded power sits about **2 % below the measured fault point**. That is a
characterization tuned to the edge of what the motor could do on the bench, with no
allowance for a loaded robot, an incline, carpet, a warm motor, or a sagging pack.

---

## Observation 3 — why later runs fail when the first succeeds

**The driver never measures the supply voltage.** `confgurePowerLimits()` runs once, at
`start()`, and selects a fixed increment table from the voltage the *user declared* in
`isp_bldc_motor_userconfig.spin2` — not from anything measured. Nothing re-reads it, and
nothing adapts as the pack drains.

So the commanded increment stays at the 18.5 V value while the actual pack voltage falls
through the run. Less available torque against an unchanged demand means growing angular
error, and the fault threshold is only ~2 % away to begin with. Add motor and FET heating
across a ~35-second demo (1 ft + 15 s + 15 s) and the second run starts with less margin
than the first.

Recorded as new finding **AK**.

**One thing worth checking on their side:** a 5S LiPo at full charge is **21.0 V**
(4.2 V × 5). 18.5 V is the *nominal* rating — 3.7 V per cell, which is roughly mid-
discharge. If their meter reads 18.5 V on a pack they consider fully charged, the pack may
be tired, partially charged, or being read under load. That alone would explain a
first-run/later-run difference.

---

## What I would *not* blame

Being explicit, because these are the plausible-looking wrong answers.

**The Rev B dead-gap defect (finding [A1](DRIVER-AUDIT-2026-09-09.md#a1)) is a real bug but
is not the cause here.** It does reduce PWM headroom, but the arithmetic bounds it: at
270 MHz, `frame_cnt` = 6136, and `dead_gap` is 70 ticks with the wrong (260 ns) value
versus 14 with the correct 52 ns. `pwm_limit` is therefore 3033 instead of 3061 — about
**0.9 % less duty**. That is a marginal contributor at most, not a fault mechanism. Its real
cost is the start-up jerk the v5.0.2 commit was written to fix.

**Their P2-EC Rev D module is not implicated.** The `getBoardType()` detection concerns the
64010 motor driver board revision, not the edge module.

---

## What to ask for next

The reporter's debug output was attached to the mail but is not available here. Three
things in it would confirm or refute the above quickly:

1. **The board-ID line for each motor on each run.** The driver prints
   `64010 Rev A` / `64010 Rev B` / `No Board Connected` at start-up. *Does it report the
   same revision on a good run and a faulting run?* Detection charges a 0.1 µF capacitor
   and counts 500 samples; a borderline count could land differently between runs, and if
   it ever reports "No Board Connected" that is finding
   [B](DRIVER-AUDIT-2026-09-09.md#defects) — `rSenseForBoard` is left at −1 and current
   readings become garbage.
2. **Which move faults.** The demo does `driveForDistance(1, 1, DDU_FT)`, then
   `driveDirection(80, -25)`, then `driveDirection(80, +25)`. Note the second and third
   are *turns*: `calcPowerForDirection` reduces one wheel to 60 while the other is clamped
   to 75 by the default `maxSpeed`. If faults cluster on one of the two turn directions,
   that points at finding [AC](DRIVER-AUDIT-2026-09-09.md#ac) (the steering side/direction
   inversion) as well.
3. **Pack voltage measured under load**, not at rest.

---

## What they can try now

Offered as mitigations, not fixes — the fixes are a separate sprint.

1. **Reduce commanded power.** Uncomment the line already present in their demo:
   ```spin2
   wheels.setMaxSpeed(60)      ' the demo ships with setMaxSpeed(100) commented out
   ```
   The demo asks for 80, which the default `maxSpeed` of 75 already clamps. Dropping to 60
   buys real margin against the ~2 % headroom described above. This is the single highest-
   value thing they can change.

2. **Declare a lower supply voltage than they are actually running.** Setting
   `DRIVE_VOLTAGE = PWR_14p8V` in `isp_bldc_motor_userconfig.spin2` while still running the
   18.5 V pack selects the 120 000 000 increment ceiling instead of 147 000 000 — about
   **18 % less aggressive commanding** for the same hardware. It is a deliberate
   mis-declaration and should be described as such, but it is effective and requires no
   code change.

3. **Confirm the pack.** Charge to 21.0 V and measure under load.

4. **Expect no fault report from the demo.** Until finding AF is fixed, the demo cannot
   tell them a wheel has faulted; only the driver's own `debug()` output will.

---

## New findings raised by this report

Both added to the audit document.

### AI — the reverse commutation offset is derived, never characterized
`isp_bldc_motor.spin2:884-886` · **Feature-gap / Risk**

For the 6.5″ motor, `fwdDegrees := 43` is documented as coming from bench
characterization "at 18v5"; `revDegrees := 360 - fwdDegrees` is arithmetic. Because the
two-wheel steering object reverses one motor, **one wheel of every two-wheel platform runs
permanently on an uncharacterized offset.** The DocoEng branch of the same method carries
the author's own open question about this (`' vs. using 360?`).

### AJ — the 6.5″ motor's offset ignores supply voltage and board revision
`isp_bldc_motor.spin2:884-886` vs `:843-848` · **Feature-gap**

The DocoEng motor gets a per-voltage **and** per-board-revision offset lookup (seven
voltages × two revisions). The 6.5″ hub motor — the motor in this user's robot and the one
the product page leads with — gets a single hardcoded `43`, applied at every supported
voltage from 6 V to 25.9 V and on both board revisions. The characterization maturity of
the two supported motors is markedly different, and the less mature one is the flagship.

### AK — no voltage feedback; the power table is fixed at the declared nominal
`isp_bldc_motor.spin2:926-990` · **Feature-gap**

`confgurePowerLimits()` runs once at `start()` and selects an increment ceiling from the
voltage the user *declared*. Nothing measures actual pack voltage, at start-up or ever, and
nothing adapts as it sags. Combined with a table characterized ~2 % below the fault
threshold ([Z](DRIVER-AUDIT-2026-09-09.md#z)), this makes battery state a direct
determinant of whether a run completes — which is exactly the reporter's observation 3.

Note this is *related to but distinct from* the current-sense path: the driver does sample
phase current into `sense_i_mV`, but only as telemetry. No control loop consumes it.

---

## Would fixing the audited findings resolve his situation?

Asked directly, 2026-09-09. **Partially — and not the part he asked about.**

One of his four observations is fully addressed by code. The core complaint — *"cannot get
consistent and repeatable runs"* — is not.

| His observation | Addressed by fixing the audit findings? |
| --- | --- |
| 4. Demo silently runs on one wheel after a fault | **Yes, completely.** M + AF are pure software defects: fix `getStatus()`, widen `DS_*` to express faulted/e-stopped, make `isFaulted()`/`getDriverState()` public. |
| 2. Right motor faults more than left | **No.** AI requires bench *characterization* — measuring the true reverse offset on real motors. Whether 317° is wrong, and by how much, is currently unknown. |
| 1. Dual faults where single does not | **No.** Z is a feature gap: torque back-off / retry / re-sync is new engineering, not a repair. |
| 3. First run works, later runs fault | **No.** AK requires new design — measuring pack voltage and adapting demand to it. |

**That split is not an artifact of how this audit was written.** The findings touching his
fault are classified *feature-gap* rather than *defect* precisely because they require work
that does not exist yet, rather than correcting something that is wrong.

### What the fixes would actually change for him

His robot would still fault. It would **stop and say so**, instead of limping on the left
wheel while reporting `DS_MOVING`.

That is a real improvement, and it compounds with fixing [W](DRIVER-AUDIT-2026-09-09.md#w):
today his RPM and speed telemetry read zero-or-negative, so any rate numbers in his debug
output are untrustworthy. Fixing M/AF/W together would make his next debugging session far
cheaper. But it solves diagnosability, not reliability.

### Caveat on A1 that should not be overstated

Fixing the Rev B dead gap gains ~0.9 % duty — marginal, as established. There is a possible
second-order effect that is **unquantified**: the v5.0.2 commit author observed *jerk* on
Rev B with the long gap, and jerk means current transients at start-up, which is exactly
when his motors are most likely to trip. A1 may therefore help start-up more than the duty
figure suggests. This is unmeasured and should not be promised to him.

### What would actually make his runs repeatable

In leverage order. Only the first is available today.

1. **Reduce commanded power** — `setMaxSpeed(60)`, or declare `PWR_14p8V` while running the
   18.5 V pack. No code change.
2. **Characterize the reverse offset** ([AI](DRIVER-AUDIT-2026-09-09.md#ai)) — bench work.
   Highest-leverage engineering item for his specific right-wheel asymmetry.
3. **Fallback algorithm** ([Z](DRIVER-AUDIT-2026-09-09.md#z)) — graceful degradation instead
   of a hard stop. Already requested in README's own "Future directions".
4. **Voltage feedback** ([AK](DRIVER-AUDIT-2026-09-09.md#ak)) — removes the
   first-run/later-run inconsistency directly.

### What this audit cannot exclude

His evidence that the boards are sound is good but not conclusive. **The single-motor demo
draws roughly half the current and removes the coincident inrush.** A marginal physical
connection would appear only under dual load — connector resistance, a partially-seated
phase or hall wire on the right motor, or a pack with high internal resistance. That would
produce his exact symptom pattern and would survive every code fix in this audit.

**Discriminating test, five minutes, no code:** swap the left and right motor cables at the
board end and re-run.

- Fault **follows the cable/motor** → physical, and no driver fix will help.
- Fault **stays on the right channel** → the reverse-offset path (AI), since that is what
  the steering object's `forwardIsReverse()` makes unique to that side.

This test should precede any code change, because it separates the two leading explanations
and one of them is not a software problem at all.

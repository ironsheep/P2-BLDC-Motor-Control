# Fault strata study — every path that ends a drive, and what still works when it does

**Task:** «#3609» phase 1 (desk). **Date:** 2026-09-23. **Status:** report only, nothing in the driver changed.
Phases 2 (wheels-up experiments) and 3 (the graded-response design) are open; §7 carries their inputs.

## 1. Scope

**Question.** When the drive ends or refuses, what raised it, what can the driver still read at that moment,
and which bridge state does it take today? Which physically different failures share one response?

**Surface.** `src/isp_bldc_motor.spin2`: the PASM driver loop, the front cog and the public API.
`src/isp_steering_2wheel.spin2`: its front loop and fault getters. Board facts come from
`DOCs/analyses/BOARD-REVISION-FACTS.md`, the sense channels' meaning from `DOCs/MOTOR-6.5IN-TECHNICAL-MANUAL.md`,
and the related entries from `DOCs/PUNCH-LIST.md`.

**Excluded.** The bench harness (`src/test_*.spin2`), because it shapes no production response; that is the
startup study's surface. The serial top level (`isp_steering_serial.spin2`), which only relays errors.

**Severity scale:** *breaks users · wrong but contained · latent · hygiene.* **Marks:** MEASURED / DERIVED /
STEPHEN / unlabelled = undetermined (doctrine overlay P8).

**Method.** A read-only survey agent traced the paths. I then re-opened every line the findings below rest on:
`isp_bldc_motor.spin2` :1840-1947, :3400-3445, :3650-3670, :3800-3826, :4100-4115, :4420-4500,
:4672-4990, and `isp_steering_2wheel.spin2` :1725-1825.

## 2. Read order (ticked)

- [x] Bridge-state definitions and the stop-mode contract (`:4104-4112`)
- [x] PASM per-pass loop: e-stop entry, request handling, `.ctlMotor`, hall decode, fault test, status block-copy (`:4411-4925`)
- [x] PASM subroutines `.shortBridge`, `.faultBridge`, `.clearRun`, `checkstop` (`:4940-4970`)
- [x] Front cog: `frontLoop` pass order, `bFrontProtect`, `frontProtectiveStop`, `frontEStop`, command timeout, `frontNoteFault`, `frontTrack` (`:1840-2006`, `:3400-3445`, `:3650-3670`, `:3800-3826`)
- [x] Start-time refusals (`setupForStart`, `launchDriver`, `launchFront`: `:2174-2289`)
- [x] The error enum (`:113-133`) and `getError()` precedence (`:710-734`)
- [x] Steering: `frontLoop` (`:1694-1781`), `frontLimitPath` (`:1782-1825`), fault getters
- [ ] `postRequest()` past `:3739` (the caller side of `ERR_NO_RESPONSE`), not fully read; see U-2

## 3. The stratified fault table

Bridge states (`:4104-4112`): **BR_DRIVE** means PWM switching; **BR_SHORT** means all low sides on and the
phases shorted, a dynamic brake; **BR_COAST** means all six FETs off, a freewheel.

**What still runs after any stop (MEASURED from source).** Every pass of `.ctlMotor` reads the four sense
channels (`:4738-4758`), decodes the halls into `pos_` and counts illegal codes (`:4826-4849`), and block-copies
the status run to hub (`:4922-4923`). It does this **whatever the bridge state or `drv_state`**. The position
fault test is armed only while `bridge == BR_DRIVE` (`:4874`, `tjnz bridge,#.noFault`), so a stopped bridge
never re-faults. **The driver therefore keeps its whole sensing picture live through every fault and e-stop.**
That is the precondition for a graceful response, and it already holds.

**The sense channels (corrects an earlier record).** `sense_i` is the **DC-link current** shunt
(BOARD-REVISION-FACTS §2.3). `sense_u/v/w` are the three **phase voltages**
(DRIVER-SAFETY-AND-CAPABILITY-STUDY-2026-09-09 §fault table; the hall-zero method in MOTOR-6.5IN-TECHNICAL-MANUAL §9.1
reads back-EMF through them with the bridge coasting). There is no dedicated supply-voltage channel. See F-9.

| id | Path | Raised (file:line) | Trigger | Cog | Bridge today | Latch / clear | Still readable at that moment | Report |
|---|---|---|---|---|---|---|---|---|
| P-1 | Position fault → `DCS_FAULTED` | `:4872-4877` | \|err\| ≥ 125 (~176° electrical) while BR_DRIVE | PASM | `.faultBridge` `:4943-4947`: SM_FLOAT→COAST, SM_BRAKE→SHORT | latched; cleared only by a new request via `.newRqst`→`.resetFault` `:4478-4488` | halls, `pos`, DC-link current, phase voltages: all live (see above) | `isFaulted()`, `getFaultCause()` |
| P-1a | …classified **FC_LAG** | `:3816-3823` | at first FAULTED pass: hall code legal, no new illegal entry | front | (already set by P-1) | cause kept until next fault or `start()` | as P-1, halls legal | `getFaultCause()` |
| P-1b | …classified **FC_HALL** | `:3819-3821` | hall code %000/%111, or a new illegal entry since last pass | front | (already set by P-1) | as P-1a | as P-1, halls **not** trustworthy; current and phase voltages live | `getFaultCause()`, `getHallIllegalCodes()` |
| P-2 | Blocked motor → `ERR_PLATFORM_BLOCKED` (-2_001) | `bFrontProtect` `:1897-1902`, call `:3436-3437` | commanded, \|err\| ≥ LAG_SOFT, `pos` unchanged for BLOCKED_PASSES, state SPIN_UP/AT_SPEED/SPIN_DN | front | `frontEStop(TRUE)` → PASM `.shortBridge` `:4431`: **SHORT whatever the stop mode** | protective code latched, first cause sticks `:1913-1914`; `clearProtectiveStop()` then `clearEmergency()` | all live; by construction the halls are legal and the rotor is not moving | `getProtectiveStop()`, `getError()` |
| P-3 | Other `-2_0xx` causes | `frontProtectiveStop` `:1905-1915` | any code in the reserved range | front | as P-2 | as P-2 | — | as P-2 |
| P-4 | E-stop (`emergencyCutoff()`) | `frontEStop` `:1936-1946`, PASM `:4426-4434` | user call, or a protective stop | front writes, PASM acts | `.shortBridge`: **SHORT whatever the stop mode**, plus `.clearRun` | `DCS_ESTOP` latched; `clearEmergency()` | all live | `isEmergency()`, `ERR_EMERGENCY_STOPPED` on refused commands |
| P-5 | Command timeout `ERR_COMMAND_TIMEOUT` (-1_019) | `bFrontCommandTimedOut` `:3658-3668`, call `:3434-3435` | timeout on (off by default), open-ended drive, no command within it | front | `frontZeroPower()`: a ramped stop, then the **user's stop mode** at rest | not latched; counted, reported once | all live, healthy | `getError()` once |
| P-6 | Distance/rotation/time limit | `:3432-3433` | a stop limit crossed | front | as P-5 | not an error | all live | — |
| P-7 | Sync timeout `ERR_SYNC_TIMEOUT` (-1_013), steering | `isp_steering_2wheel.spin2:2240-2242` | a synchronized command not taken in time | caller | both motors stopped (`:414` doc) | not latched | all live | the method's return |
| P-8 | Current fold-back and thermal derate (**not a stop**) | PASM `:4879-4886`; front `:1885-1895` | DC-link current at or over `threshold(i_limit_k, duty)`; ~1 s average over the continuous limit | PASM + front | stays BR_DRIVE; duty folds back ~1.6 % per frame | running flag `bDerated`, not an error | all live | TEST-USE limits getter only |
| P-9 | Start refusals (`ERR_BOARD_NOT_DETECTED`, `ERR_BAD_PIN_GROUP`, `ERR_PIN_GROUP_IN_USE`, `ERR_BAD_VOLTAGE`, `ERR_BAD_DETECT_MODE`, `ERR_ABI_MISMATCH`, `ERR_NO_FREE_COG`) | `:2184-2200`, `:2222-2228`, `:2239`, `:2273` | validation or detection fails | caller | none (no driver runs) | one-shot | nothing (no driver cog) | `start()` return, `getError()` |
| P-10 | `ERR_NO_RESPONSE` (-1_017) | `:2285`, `:859`, `:1764`, `:3700` | a bounded wait on the front cog or driver expires | caller | unchanged; whatever the underlying latch set | not its own latch | undetermined (U-2) | the method's return |

## 4. Strata: grouped by what still works

| Stratum | What still works | Rows | Response today |
|---|---|---|---|
| **S0 · healthy, power-limited** | everything | P-8 | keeps driving at reduced duty; correct |
| **S1 · healthy, drive ended by policy** | everything | P-5, P-6, P-7 | ramped stop, then the user's stop mode; correct |
| **S2 · healthy sensors, motion obstructed** | halls, current, phase voltages; rotor stationary | P-2 | **hard short** regardless of stop mode |
| **S3 · control lost, halls intact** | halls, current, phase voltages; the rotor is not following the field | P-1a | COAST or SHORT by stop mode, at whatever speed |
| **S4 · halls lost** | current and phase voltages (back-EMF visible only while coasting) | P-1b | COAST or SHORT by stop mode, at whatever speed |
| **S5 · deliberate emergency** | everything | P-4 | hard short, by stated intent (STEPHEN 2026-09-23, doc comment `:666-669`) |
| **S6 · nothing running** | nothing | P-9 | refused before a cog starts |
| **S7 · inter-cog communication lost** | undetermined | P-10 | undetermined |

## 5. Findings register

| # | Severity | Finding | Evidence | Mark | Root cause | Trivially safe? |
|---|---|---|---|---|---|---|
| F-1 | breaks users | **On a two-wheel platform, a position fault on one wheel does not stop the other.** Steering's front loop secures both wheels only for a *blocked* wheel (`:1755-1759`). Nothing in the loop reacts to one wheel reading `DCS_FAULTED`, so the healthy wheel keeps its command and the platform pivots about the faulted wheel. Whether the path limiter scales the healthy wheel down is undetermined: it depends on the faulted wheel's `holdSlotsAgo`/`drv_incr_now` after a fault, which the source does not settle. | `isp_steering_2wheel.spin2:1725-1760`; search `isFaulted` in that file finds only getters (`:881`, `:1295`, `:1467`); control search `bFrontProtect` finds `:1755` | DERIVED from a traced absence | R-2 | no |
| F-2 | breaks users | **The fault bridge ignores the fault's cause.** `.faultBridge` branches on the stop mode alone. FC_LAG (halls fine, S3) and FC_HALL (halls gone, S4) take the same response. The cause is computed later, on another cog, with no path back to the bridge. | `:4943-4947`; `:3806-3823` | MEASURED (source) | R-1 | no |
| F-3 | breaks users | **Every S3/S4 fault stops at full speed in one frame.** COAST (the wheel rolls free, and on an incline it runs away) or SHORT (a braking torque set by speed ÷ winding resistance, the tip-over case in the task's WHY). Nothing slows under control first, although the halls and a re-sync primitive are both there (F-6). | `:4872-4877`, `:4943-4947` | MEASURED (source); the torque figure is modelled (task WHY), not measured | R-1 | no |
| F-4 | wrong but contained | **FC_LAG covers many physical causes.** The fault test is angle error alone. Overload or stall, a wrong commutation offset, supply sag, an open phase, a dead FET and a missing motor all appear as "rotor not following" with legal halls. The last three are hardware failures, not load. | `:4860-4877`; classifier `:3816-3823` | DERIVED (the open-phase, dead-FET and missing-motor cases are inferred from the physics, not measured) | R-1 | no |
| F-5 | latent | **The blocked stop and a real emergency share one response.** The blocked stop escalates to e-stop and therefore to SHORT whatever the user's stop mode. The wheel is stationary by construction, so a short produces no braking torque and no current surge. On an incline, though, a short at rest creeps («#3608» physics), and SM_FLOAT users get a short they did not choose. PL-116 (a lifted wheel latched a blocked stop right after an e-stop was cleared) and PL-106 (the blocked stop cannot be provoked on a lifted rig) are the related open entries. | `:1905-1915`, `:4431` | MEASURED (source); DERIVED consequence | R-1 | no |
| F-6 | latent | **The primitives for "re-sync from halls and ramp down" already exist.** `initAngleFmHall` (called by `checkstop`), `.rampUp`'s re-seed of the angle from the halls when `drv_incr == 0` (`.clearRun` comment `:4957`), and the ramp-down with its duty ceiling (`:4672-4700`). A fault does **not** run `.clearRun` until `.resetFault`, so the running state is intact at the moment of the fault. | `:4481-4488`, `:4953-4957`, `:4963-4971` | DERIVED | — (a capability, for phase 3) | — |
| F-7 | latent | **SHORT removes the back-EMF signal and COAST keeps it.** In a short the phases are tied together, so the phase voltages read about zero. In a coast they carry back-EMF, which is how the hall-zero method reads the rotor. Whenever halls are lost (S4), the only other position source («#3602», deferred) needs the bridge to coast, so a SHORT response to S4 destroys the one remaining sensor. | bridge semantics `:4104-4112`; technical manual §9.1 | DERIVED | R-1 | no |
| F-8 | hygiene | `frontProtectiveStop`'s comment says *"the driver floats the drive"*, but the e-stop it calls **shorts** (`:4431`). | `:1910` vs `:4431` | MEASURED (source) | — | **yes**: comment-only |
| F-9 | wrong but contained | **The "established decision" handed to both surveys was wrong about the sense channels.** It said "I/U/V/W are phase CURRENT shunts". In fact `sense_i` is the DC-link current and `sense_u/v/w` are phase voltages. Separately, the mean of the three phase voltages while switching is a candidate **bus-voltage proxy** (C-6). PL-60 found it CONSISTENT on the left board and INCONCLUSIVE on the right, so it is unconfirmed. It works only while the bridge switches, so it does not replace Stephen's 5S sensor («#3611»). The same wrong sentence sits in «#3611»'s task body. | BOARD-REVISION-FACTS §2.3; DRIVER-SAFETY-AND-CAPABILITY-STUDY-2026-09-09 fault table; PUNCH-LIST PL-60 | MEASURED (records) | — (aged state) | **yes**: record-only, corrected in the task records with this study |
| F-10 | latent | **One protective cause exists in code.** The `-2_0xx` range is general, but `ERR_PLATFORM_BLOCKED` is its only producer. | `frontProtectiveStop(` has two call sites, motor `:3437` and steering `:1758-1759` | MEASURED (search) | — | — |

**Root-cause groups.**

- **R-1 · One response per stop mode, not per stratum** (F-2, F-3, F-4, F-5, F-7). The bridge decision is made
  in PASM from `stop_mode_` alone, at the instant of detection, before anything knows *which* failure it is.
  This is the collapse Stephen suspected.
- **R-2 · No platform-level fault policy** (F-1). Each wheel's fault is that wheel's business. A platform
  "never drives one wheel" (steering's own comment, `:1754`), but only the blocked path honours that.

## 6. Undetermined, as questions for phase 2 or 3

- **U-1** After one wheel faults, does steering's path limiter pull the healthy wheel down, and how far? It
  depends on the faulted wheel's `drv_incr_now` and `holdSlotsAgo` after `DCS_FAULTED`. A wheels-up cell
  answers it (§7, cell X-5).
- **U-2** `ERR_NO_RESPONSE` with a *dead* front cog versus a dead driver cog: the caller cannot tell them
  apart from the code read. `postRequest()` past `:3739` was not fully read.
- **U-3** Winding resistance, which sets the short-circuit current and torque of every SHORT response. It
  is unmeasured (task WHY; «#3610» stage 1 would yield it).

## 7. Inputs to phase 2: candidate cells, each able to FAIL

All wheels up except X-1. Pre-registered readings are stated in advance.

- **X-1 · Winding resistance** (meter, bench power off). *Expect* 0.3–0.6 Ω phase to phase (task WHY). A reading
  outside that range revises the short-circuit model.
- **X-2 · Today's SHORT from speed.** Provoke P-1 at 3 speeds under SM_BRAKE and log `sense_i`, the phase
  voltages and hall ticks to rest. *Expect* peak DC-link current to scale with speed, and a stop in fewer ticks
  than X-3's coast. **Fails** if current does not scale with speed.
- **X-3 · Today's COAST from speed** (SM_FLOAT, same provocation). *Expect* phase voltages to carry a back-EMF
  sinusoid at the hall rate (F-7). **Fails** if the phase voltages stay flat while the halls tick.
- **X-4 · Re-sync and ramp after a provoked fault.** A test build seeds the angle from the halls after
  P-1 and ramps down at the user's deceleration. *Expect* the hall rate to fall along the ramp with no second
  fault. **Fails** on a second fault, or on a hall rate that does not follow the ramp.
- **X-5 · One wheel faults, platform** (steering, wheels up). *Expect today* (F-1) that the healthy wheel keeps
  turning. Log both wheels' ticks. This cell **fails the F-1 finding** if the healthy wheel stops or slows to the
  faulted wheel's rate.
- **X-6 · Graded short.** First a p2kb check that the low-side smart-pin PWM can run a duty-limited short
  (P7), then measure deceleration against duty. Pre-registered reading: deceleration rises monotonically with
  duty.

## 8. Not read

`postRequest()` past `:3739` (U-2); the bench harness (out of scope); `isp_steering_serial.spin2` (relays only).

## 9. Hand-off

Phase 3 designs one response per stratum. The inputs are R-1 and R-2, the capability in F-6, and the X-cells'
results. The task body sets the candidate shape; nothing here licenses a response before the cells run (D2).
F-8 is comment-only and F-9 is record-only: both are trivially safe.

# Findings audit — what was recorded and not acted on

**Opened 2026-09-17** at Stephen's direction, after the commutation discussion showed that a week-old
evaluation already answered the question being asked. **Completed the same evening.**

**STEPHEN 2026-09-17:** *"It seems like you've got enough test results, and now you've demonstrated that
you've ignored some of the findings. Maybe we should treat this as a class issue and audit all of your
test result findings, and see which ones we haven't paid attention to and which ones are beneficial."*

**Every finding gets two questions, and the second one had never been asked before:**

1. Was it acted on?
2. ⭐ **Does what has landed since make it actionable, or make its data worth more than when it was
   written?** A disposition of *do not apply* or *deferred* carries the conditions it was written under,
   and later work removes those conditions.

Doctrine overlay **P11** was written from this: *a finding's value changes when the system changes; the
sweep is owed before a criterion, a run or a recommendation.*

**This audit schedules nothing** (doctrine overlay P5). §2 ranks by what an item would buy; what goes into
the release is Stephen's decision.

---

## 0 · Coverage

**All 22 documents and the whole punch list were read.** Each row says who read it. A reader agent's
report is a report, not a verification (doctrine D2), so every item in §2 that changes a recommendation
was checked against a primary: the source, `VISIT-5-RESULTS.md`, or the punch-list entry itself.

| Document | Read by | Represented |
|---|---|---|
| `bench/2026-09-12/CHAR-RUN-EVALUATION.md` | reader agent, full | §2, §5 |
| `bench/2026-09-12/DETECT-A-EVALUATION.md` | reader agent, full | §5 |
| `bench/2026-09-12/SCAN-ABORT-EVALUATION.md` | reader agent, full | §2.6, §5 |
| `bench/2026-09-12/SCAN-RUN-3-EVALUATION.md` | reader agent, full | §2.2 |
| `bench/2026-09-13/SCAN-RUN-4-EVALUATION.md` | arbiter, full (earlier today) | §2.2 |
| `bench/2026-09-13/SCAN-RUN-5-EVALUATION.md` | reader agent, full | §2.2 |
| `bench/2026-09-14/SCAN-RUN-7-EVALUATION.md` | arbiter, full (earlier today) | §2.2 |
| `bench/2026-09-14/VISIT-1-RESULTS.md` | reader agent, full | §2, §5 |
| `bench/2026-09-14/VISIT-1-SIGNOFF.md` | reader agent, full | §5 |
| `bench/2026-09-15/VISIT-2-RESULTS.md` | arbiter §0–2, reader agent §3–16 | §2, §3 |
| `bench/2026-09-15/VISIT-2-ATTENDED-RESULTS.md` | reader agent, full | §2.9, §5 |
| `bench/2026-09-16/VISIT-3-RESULTS.md` | arbiter, full (earlier today) | §2, §3 |
| `bench/2026-09-17/VISIT-4-RESULTS.md` | arbiter, substantial (earlier today) | §2 |
| `bench/2026-09-17/VISIT-5-RESULTS.md` | **arbiter, full, this session** | throughout |
| `DRIVER-AUDIT-2026-09-09.md` | reader agent, full | §2, §4 |
| `DRIVER-SAFETY-AND-CAPABILITY-STUDY-2026-09-09.md` | reader agent, full | §2, §4 |
| `BLDC-COMMUTATION-PRINCIPLES.md` | reader agent, full | §2.2 |
| `BOARD-REVISION-FACTS.md` | **arbiter, full, this session** | §2.1, §2.5 |
| `PL-44-ROOT-CAUSE-STUDY.md` | reader agent, full | §2.10 |
| `user-report-2026-09-09-ANALYSIS.md` | reader agent, full | §2.11, §3 |
| `ATTENDED-UI-AUDIT-2026-09-15.md` | reader agent, full | §5 |
| `BENCH-TEST-PLAN-2026-09-10.md` | reader agent, full | §2, §4 |
| `DOCs/PUNCH-LIST.md` PL-1 … PL-90 | two reader agents (split at line 2100); PL-56, PL-69, PL-89, PL-90 by the arbiter | §2, §3 |
| **Current source**, for 17 findings from the 2026-09-09 studies | reader agent; `holdAtStop()` / `checkstop` / the hall read by the arbiter | §4 |

⚠ **Tool note for Stephen:** the source-verification agent made one accidental shell call (`true`, a
no-op) before it re-read its no-shell brief. It changed nothing. Every other reader used the Read tool
only.

---

## 1 · The class defect

**Findings are filed and then never re-read.** The punch list and the evaluations are a filing system,
and nothing sweeps them when something changes. **Four failure shapes**, all present in quantity:

| Shape | What it looks like | Count found | Worst instance |
|---|---|---|---|
| **A. The blocker is removed and nobody returns** | A finding parked on a condition; later work removes the condition; the finding stays parked | 5 | The commutation scan (§2.2) |
| **B. The finding is fixed and the record never says so** | "Run-time proof owed to Visit N", with Visit N long past | **16** | PL-55, still described as the largest open behaviour (§3) |
| **C. The data outlives the question and nobody asks the new question** | Measurements taken for one cell answer a later question | 3 | Scan runs 7 and 8 already answer the commutation question |
| **D. A new finding contradicts a settled one without citing it** | A later entry reasserts what an earlier entry withdrew | 2 | PL-89 against PL-56 (§2.1); PL-90 against the hall network already recorded (§2.5) |

**Shape D is new, and it is the most dangerous of the four.** Shape B leaves a stale record. Shape D
builds on one: PL-89 was written today without reading PL-56, which had already settled one of its two
premises, and its conclusion contradicts a bench fact of Stephen's that PL-56 records.

---

## 2 · Ranked by what each item would buy

### 2.1 ⭐ Is "float" a short? PL-89 had its table backwards, and it collides with Stephen's bench fact

**What PL-89 claims** (filed today): `holdAtStop(FALSE)` gives a powered hold, `holdAtStop(TRUE)`
shorts the phases, and every fault and e-stop shorts them.

**What the source actually says**, read this session:

- `holdAtStop(bEnable)` sets `stop_mode := (bEnable) ? SM_BRAKE : SM_FLOAT`
  (`src/isp_bldc_motor.spin2:713`).
- `checkstop` (`:4078-4085`) runs `cmp stop_mode_, #SM_FLOAT wz` and then `modz _nz wz`, so Z is set when
  the mode is **not** FLOAT. The result is:
  - **SM_BRAKE**: `driveoff := 0`. PWM stays on at `duty_min`, at an angle taken from the halls. That is a
    **powered position hold**, which is what `holdAtStop(TRUE)`'s doc promises.
  - **SM_FLOAT**: `driveoff := 1`. The control loop then runs `wypin #0, drive_pins` (`:3949`).

**So PL-89's first two table rows are swapped.** If `wypin #0` shorts the phases, **the short belongs to
FLOAT**, the setting documented as coast, and not to BRAKE.

**The polarity link PL-89 calls "not established" was established on 2026-09-15, in PL-56.** Normal
drive writes each low-side pin the high side's duty plus `dead_gap`, on an inverted output. That gives
complementary drive with deadtime **only if a high on the low-side input turns the low FET on**. With the
opposite polarity, both FETs of a phase would be on together every PWM period, and hours of running on
this rig have never shown that. So `wypin #0` on the inverted low sides holds all three low FETs on.

**That derivation now says FLOAT at rest shorts the windings. Stephen's recorded bench fact says float
freewheels.** PL-56 records it: *"Stephen's prior bench testing shows freewheel/float works and full
braking works"* (the safety study, pre-sprint), and STEPHEN 2026-09-15: *"we came into this work with
float working as desired"*.

⛔ **Doctrine overlay P8: his recorded bench fact outranks my derivation, so the derivation is the
suspect.** Something in the chain from `driveoff = 1` to the FET gates is not what the source reading
says. Candidates, none checked: what an inverted triangle-PWM smart pin actually outputs with Y = 0; the
board's added logic buffer; or whether the state he tested differs from the at-rest FLOAT path.

**His hand test decides it**, and the predictions in PL-89 must be swapped before it runs:

- `holdAtStop(TRUE)`: held, with cogging.
- `holdAtStop(FALSE)`: freewheels if his fact holds; resists harder the faster it turns if the derivation
  holds.
- `stop()`: freewheels in either case.

**What it buys:** whether a documented public contract, coast, is true. It also settles whether every
fault and e-stop brakes (Visit 2 measured `emergencyCutoff()` stopping a half-speed wheel within one
tick), which is exactly what a user's platform does on a fault.

> **Disposition, STEPHEN 2026-09-17 (later the same night):** *"isn't there a set*() which specifies motor stop
> condition? so user would select it for their application"*. `holdAtStop()` is the user's selection, so this is
> not a behaviour question: **every stop path must deliver the selection** — at rest, on a fault, and on an
> e-stop as its documentation promises. An API-contract fix, in this release; the hand test certifies it.
> A supporting reading surfaced by §6: the char tier's quiescent hold under `SM_FLOAT` shows `duty_` wound to
> `duty_max` with near-zero current, so FLOAT at rest **is** the `driveoff` path (whether that path shorts the
> windings, a still wheel cannot show).

**Correction owed:** PL-89's table, its headline, and its predictions. The subject line of commit
`578f3ef` ("Float is a powered hold") is wrong and stays wrong in history; the entry carries the
correction.

### 2.2 ⭐ The commutation scan: three of its four blockers are gone

**The data** (`SCAN-RUN-5`, `SCAN-RUN-7`, `VISIT-2-RESULTS.md` §11 run 8), both motors, reproduced:

| | LEFT | RIGHT |
|---|---|---|
| negative-increment minimum, ¼ speed | +13.4° ± 0.5 | +13.7° ± 0.7 |
| positive-increment minimum, ¼ speed | −20.9° ± 0.7 | −22.3° ± 0.4 |
| hall electrical zero | −3.8° ± 0.4 | −4.3° ± 0.4 |
| current saved at the minimum, ¼ speed, no load | 86.7 % (pos) | 86.2 % (pos), 90.7 % (neg) |
| **margin to the fault edge, ½ speed** | **4.4°** (pos) | **4.3°** (pos), **4.0°** (neg) |

At the minima the 2:1 direction asymmetry collapses to 1.16 (left) and 1.08 (right). The candidate pair
is 14° / 338°.

**Its "do not apply" rested on four conditions** (`SCAN-RUN-3` §7, restated in `SCAN-RUN-5` §9):

| Condition | Status now |
|---|---|
| (a) the negative minimum was not bracketed | **gone.** Bracketed on the right motor in run 8; left still NOT_BRACKETED at a flat floor of 14.0–15.1 mV |
| (b) the right motor produced no data | **gone.** Runs 5, 7 and 8 have it |
| (c) the half-speed legs ended on **faults** before a minimum | **gone.** The lag limiter («#3558», the ramp that waits for the rotor) makes the driver droop instead of faulting; `RMPDROOP` passed on both motors at Visits 4 and 5 |
| (d) every minimum sits within ~10° of a fault edge **at no load**, and nobody has measured the margin **under load** | **stands.** Nothing since touches it |

**Two more things stand between the data and a re-run**, and neither is in the landed list:

- **The scan's own instrument defects.** `VISIT-1-RESULTS.md` records that scan v4's cells "prove less
  than their names": `R9-SCAN-HALFLEG` passed on the very defect it exists to catch. Run 8 fixed D1 and
  failed three legs honestly. The rest of D1–D8 must be read against the scan binary before it runs
  again.
- **The cog-0 lockup of run 5** («#3534»), later traced to an unsound power connection (PL-43, repaired by
  Stephen). PL-43 was reopened by a silent P2 at Visit 2 (§2.9).

⛔ **A scope question that is Stephen's, not mine (P5).** On 2026-09-15 he ruled that the scan offsets are
not in 6.0.0 and that the default 43° / 317° pair ships. On 2026-09-17 he ruled 6.0.0 *"not shippable as
is. we need better behavior"*. **The earlier exclusion was written before the later ruling, and before the
lag limiter removed condition (c).** Whether it still stands is his call; this audit does not reopen it.

**What it buys:** 86–97 % of the no-load current, the 2:1 direction asymmetry that PL-88 shows is not
cancelled on the platform, and every downstream effect of wasted current (heat, battery, loaded top
speed).

**The acceptance criterion already exists** (`BLDC-COMMUTATION-PRINCIPLES.md`): Visit 4's reverse/forward
current ratio at rungs 2–5 is LEFT 2.16 / 2.00 / 2.02 / 1.97 and RIGHT 1.88 / 1.86; the target is 1.0.
Visit 4 reproduced the 2026-09-12 Bench Pass 1 asymmetry (1.76–1.97), so two independent measurements
agree.

### 2.3 The fault limb: one stimulus unblocks six findings

> ⛔ **CORRECTED the same night: the next sentence was wrong.** Visit 3 DID fault the driver on purpose and read
> the result: `R14-DUAL-FLTAPI-B` PASS, both wheels FAULTED at 101 ms, `getStatus()` FAULTED, steering
> `isFaulted()` TRUE, the latch held 5.8 s — certifying **M**, **AF** and **S-5**, and `RSTPROV-B` passed
> (`bench/2026-09-16/VISIT-3-RESULTS.md` §2.3). That stimulus (a `ramp_inc` of 10 000 from standstill) predates
> the lag limiter, which now makes such a ramp droop instead of fault. **What is genuinely missing is a fault
> provocation on today's lag-limited driver**, and the six findings below are the ones it gates. The audit
> read the Visit 4/5 NOMEAS rows and did not reach back to Visit 3 — the asserted-absence failure (overlay P8)
> inside the audit that exists to catch it.

~~Nothing has ever made the driver fault on purpose and survived to read the result.~~ **Six findings wait on
that one stimulus:**

| Finding | What it needs |
|---|---|
| **S-7** | A hall `%000`/`%111` is counted (`hall_illegal_`) but never reported as a distinct fault reason; the fault test is the angle error alone (`:4016-4021`). **Still present in source** |
| **S-9a / PL-89** | What a fault actually does to the bridge |
| **Z, recovery half** | Recovery after a fault |
| **PL-66** | A same-power retry after a fault restarts the motor. Fixed in the tree; **run-time proof has never happened**, because `R16-DUAL-FLTRETRY-B` was NOMEAS at Visits 4 and 5 |
| **«#3547», the fault API** | `R14-DUAL-FLTAPI-B`, NOMEAS twice |
| **PL-59** | A 3° offset at half speed does not fault in 2 s |

**Why it keeps failing** (PL-86, `VISIT-5-RESULTS.md` §4c): the provocation writes an offset 180° from
the running pair. Current reaches 2 445 mV (≈ 16 A) within about 100 ms and trips the harness's own 10 A
abort before the driver's fault test is reached. **The fix is arithmetic, not a run:** the fault test
fires at |err| ≥ 125 (≈ 176°), so the provocation only has to exceed that, not jump to 180° at speed.

**What it buys:** certification of the fault path on today's driver. M, AF and S-5 are fixed in source
(§4) and were certified at Visit 3, so what remains is the retry, the fault's bridge state, the hall-fault
reason and the recovery on the current driver.

### 2.4 The slam has no instrument (PL-87), and the fix costs no bench time

`err` and `err_pk` are statistics over the **steady** window; `rungMeasure()` opens the window after
AT_SPEED and settle. **Rung 0, the only transition from rest, shows the same ~25-count gap as every other
rung at both visits**, so the statistic cannot see a transition. PL-78's driver fix **is** in the binary
(`src/isp_bldc_motor.spin2:3668`, verified in source this session), and **its effect is unmeasured**.
Stephen's observation — *"some are not kicking but many still are"* — is the only evidence.

The ring already holds every transition sample; `windowStats()` never reads them. A second pass over
[arm … window start] gives the transition peak per rung, with rung 0 as the built-in control.

⚠ **The safety study's own text is stale here:** it says the PL-78 one-liner is "identified but not yet
applied". It was applied before Visit 5.

### 2.5 The hall read: PL-69, PL-90, and the hall network already on file

- **PL-69** (MEASURED, Visit 3): `illegal_d` 3 and 5 on the RIGHT motor at 200 MHz only; zero at 270 and
  300 MHz, zero on the LEFT motor, zero at every other hold.
- **PL-90** (filed today) proposed a torn three-`TESTP` read as the candidate cause, and asked in its Q1
  whether the hall lines need a pull-up. **The answer to Q1 had been in `BOARD-REVISION-FACTS.md` §1.1 since
  2026-09-10:** each of U, V and W has a 3.9 kΩ pull-up to 3.3 V and a 3.9 kΩ series resistor to the P2,
  word for word identical on Rev A and Rev B. STEPHEN confirmed it tonight (*"REV A/B hall signals are
  conditioned identically"*). **This is shape D:** a question filed while its answer sat in our own file.
- **SCAN-ABORT** (2026-09-12) is earlier hall history: an `illegal 1` at every start, caused by the start
  sequence raising DIR on the hall pins. Fixed by «#3524» and confirmed at run 3.

**The hall read's mechanism is the next discussion with Stephen and is not settled here.** The audit
records two things that bear on it:

- **The driver's own `deltas` table changes exactly one hall line per legal step.** That bears directly on
  whether a torn read can produce `%000` / `%111` at all.
- **The P2's "pull-up" is a weak drive**, live only with DIR high (p2kb `p2kbArchPinDriveConfiguration`).
  On these pins it would push against the board's 3.9 kΩ series network.

### 2.6 Straight-line driving puts one wheel in the 2× direction (PL-88)

The motors are mirror-mounted, so platform-forward is a positive increment on one wheel and a negative
increment on the other. The asymmetry is **not** cancelled on the platform, which means uneven heat and
battery drain, and different derate points: a veer under load. **§2.2 is its fix**; no separate work is
owed.

### 2.7 API-contract defects still present in source (doctrine overlay P3: mine to fix, not his to decide)

Verified in the current tree this session (§4):

| id | Defect | Where |
|---|---|---|
| **AB** | `driveForDistance(left, right)` drives both wheels to the **shorter** of the two, so it cannot turn, although the API takes two distances | `src/isp_steering_2wheel.spin2:337, 359-369` |
| **G** | `setAcceleration()` / `setRampingValues()` write all four ramp values with no validation, and the doc still reads `[??? - ???] mm/s squared`. **C-1's speed law is now certified to <0.5 %**, so real units can be derived | `src/isp_bldc_motor.spin2:631-653` |
| **K** | `DDU_KM` and `DDU_MI` can be read by `getDistance()` but not commanded: `ticksForDistance()` has no case for them in either object | `isp_bldc_motor.spin2:1826-1841`; `isp_steering_2wheel.spin2:509-526` |
| **AC** | The comment beside the turn code says a turn to the right reduces the right wheel; the code reduces the **left** for `limitDir > 0`, so the platform turns left. Visit 2's attended video confirmed a left turn; the comment is wrong and the DRIVE-OBJECTS / README cross-check is still owed | `isp_steering_2wheel.spin2:1370-1385` |

**They are recorded here because the audit found them; fixing them is scope for the plan that follows.**

### 2.8 Safety and capability gaps that are Stephen's scope

| id | Gap | Why it is his |
|---|---|---|
| **PL-73** | A board that fails detection drives **with no current limit** | Refuse to start, or run under a conservative limit: an API and safety decision |
| **S-8** | No command watchdog or link-loss failsafe on the serial or RC path. Turn the transmitter off and the platform keeps driving | A new public mechanism |
| **S-6** | The serial `getstatus` now carries `DS_FAULTED` and `DS_ESTOP` (fixed through M and AF), but there is no health or fault command | A protocol addition |
| **AK / C-6 / C-6b** | No bus-voltage feedback. The power table is fixed at the declared voltage. This is the user report's symptom 3 (*first run fine, later runs fault*). C-6b's route, the unused fourth half-bridge's ADC, costs no hardware but has a documented shoot-through hazard if that channel is ever driven | New capability |

### 2.9 PL-43: the silent P2 at Visit 2 has no root cause

`dual-brake` went silent about 3 s after its prompt (`debug_260915-142454.log:122`), which is PL-43's
signature a second time. The attended rebuild added a heartbeat, so a silence is now *visible*, but
nothing explains it. It is safety-relevant: a platform whose controller stops mid-command.

### 2.10 Smaller open items with a named fix

- **PL-44 study §4**: the char harness's PL-36 claims check is masked (char:1887-1892), the t0 guards accept
  a stuck 0 (t0:942, :621, :685), and `steerDriveTrapped` reports a wrong value as an abort. All were
  recorded for «#3539» (design the trap-capture pattern out); **whether «#3539» carried them was not
  verified.**
- **PL-53**: its deferral reason, "Visit 2 runs these binaries again", has expired.
- **PL-68**: a bench log still cannot name the commit it was built from.
- **PL-41 / PL-85**: cog bursts truncate DEBUG on the wire; «#3543» (design the cog-lifecycle antipatterns
  out) is the named fix.
- **PL-60**: the left board's phase-sense sag of 2.4–2.8 % against the right board's 0.2–0.3 %.
- **PL-62, PL-63, PL-67, PL-71 / N** (the Doco floor, still present in source): minor, or outside 6.0.0.

### 2.11 The field user's report, 2026-09-09 — where each symptom stands

| Symptom | Then | Now |
|---|---|---|
| 1. Two motors fault where one does not | NO fix (Z: hard latch, no back-off) | **Addressed**: the lag limiter droops instead of faulting, the current limit and the bounded stop are certified |
| 2. The right motor faults more | NO (AI: reverse offset never characterised) | **Open**: the scan (§2.2) is the fix, and it is outside 6.0.0 by ruling |
| 3. First run fine, later runs fault | NO (AK: no voltage feedback) | **Open** (§2.8) |
| 4. The demo keeps driving after a fault and reports MOVING | YES by code fix (M, AF) | **Fixed in source** (§4); the run-time fault limb waits on §2.3 |
| 5. Hello World and single-motor pass | — | — |

The report's alternative, a connector or harness fault that would survive every code fix, proposed a
cable-swap test. That test is **not possible on this rig** (BENCH-TEST-PLAN T1-12, withdrawn 2026-09-14),
and Visit 1 showed the two motors equivalent hold for hold.

---

## 3 · Records that are now wrong — the correction batch

**Shape B, 16 entries.** Each still says a proof is owed, or that something is open, when a later visit
settled it. **Correcting a status line is filing, and filing is mine (P5).**

> ✅ **APPLIED 2026-09-17 night («#3567», the aged-state sweep)** — and widened: every PL entry was re-read, not
> only these, and roughly 40 status lines were corrected, including PL-8, PL-10, PL-11, PL-33, PL-35, PL-41,
> PL-48, PL-49, PL-57, PL-59, PL-62, PL-73, PL-75, PL-78, PL-85, PL-86, PL-87, PL-88, PL-90. The two 2026-09-09
> studies, the user-report analysis and Visit 3's §6 gained dated status blocks. The table below is kept as
> the record of what was found:

| Record | Says | Settled by |
|---|---|---|
| PL-25 | proof owed to Visit 4 | `R16-T0-NOBOARD` PASS, Visit 5 L184 |
| PL-28 | proof owed to Visit 1 | Visits 1–5 ran; verify the cell |
| PL-30 | "still open: right board +64 mV" | the sense-zero calibration: 71–76 mV → 0.1–1.8 mV |
| PL-32 | proof owed to Visits 1 and 2 | per-start zero certified (Visit 5 t0: 0.0–1.6 mV across five starts) |
| PL-45 | proof owed to Visit 4 | `R16-T0-RESTZERO` PASS L177/181, Visit 5 |
| PL-46 | scan "stays blocked" | condition (c) removed, §2.2 |
| PL-47 | "deferred, not in the driver path" | the error contract, certified at Visit 5; **zero `abort` uses remain in either library object** |
| PL-52 | proof owed to Visit 4 | Visit 5 t0, error contract certified |
| PL-53 | deferred until Visit 2 re-runs the binaries | Visits 2–5 ran |
| **PL-55** | proof owed to Visit 4; **`VISIT-3-RESULTS.md` §6 calls it the largest open behaviour** | stop peaks 971–1 055 mV against a 1 500 mV abort (Visit 4); `STOPCUR` PASS (Visit 5) |
| PL-61 | "mechanism not established" | duty saturates at `duty_max` from rung 7 while back-EMF rises against a fixed applied voltage (`VISIT-5-RESULTS.md` §5b). DERIVED; worth one line in the entry |
| PL-64, PL-65 | open | fixed in the attended rebuild, SRC_REV 12 (`ATTENDED-UI-AUDIT` §7) |
| PL-70, PL-72 | open / construct to be removed | the front cog («#3513») replaced the loop; verify PL-70's divide is gone |
| PL-74 | "the next run discriminates" | Visit 5 t0 emitted: closed (`VISIT-5-RESULTS.md` §2a) |
| PL-84 | "Visit 5 settles it" | `str_mm_x100` 576, `agree TRUE` (Visit 5 L7652) |
| **PL-89** | the swapped table, and the premise PL-56 had settled | §2.1 |

**The two 2026-09-09 studies self-audit only to Visit 4.** Visit 5 closed three items they still list as
open:

- **F**: `stopAfterDistance(DDU_M)` — `R16-DUAL-DISTM-B` PASS.
- **C-3**: the distance overshoot — `STOPLIM` PASS, worst case 1 tick.
- **AD**: the start-failure path — `R16-T0-FRONTFAIL` PASS.

`user-report-2026-09-09-ANALYSIS.md`'s resolution table still reads NO for symptom 1.

---

## 4 · The 2026-09-09 study findings against today's source

Verified by reading the current tree; the line numbers are current.

| id | Verdict | Evidence |
|---|---|---|
| M | **FIXED** | `getStatus()` returns `DS_FAULTED` / `DS_ESTOP` before the ready test, `isp_bldc_motor.spin2:1200-1216` |
| AF | **FIXED** | the steering object's `getStatus()` forwards both wheels, `isp_steering_2wheel.spin2:821-826` |
| S-5 | **FIXED** | no timed auto-clear; `clearFaultSignal()` is the only writer (`:1400-1409`) |
| A2 / A3 | **FIXED** | `getBoardType()` switches on the BRD_* override (`:1305-1314`) |
| AE | **FIXED** | `claimPinBase()` rejects an overlapping group with `ERR_PIN_GROUP_IN_USE` (`:284-322`) |
| O | **FIXED** | `PWR_25p9V` is outside both lookdown ranges, so it is rejected up front (`:1925-1936`) |
| I / T | **FIXED** | zero `abort` uses in either library object |
| H | **FIXED** | `resetTracking()` goes through the bounded request (20 ms) |
| Q | **FIXED** | `SyncStatus()` is bounded by `SYNC_TIMEOUT_MS` (`:2014-2031`) |
| W | **FIXED** | Visit 4 `RPM_ERR` within ±2 |
| A1 | **FIXED** | the conditional was deleted; 259–260 ns measured at all three clocks |
| F, C-3, AD | **FIXED** | Visit 5 (§3) |
| AB, G, K, AC | **STILL PRESENT** | §2.7 |
| S-7, S-8, N | **STILL PRESENT** | §2.3, §2.8, §2.10 |
| S-6 | **CHANGED** | status now correct; no health command |

---

## 5 · Closed, and correctly recorded as closed

Detection: pinclear-before-read («#3500»), 0/12 misdetections at Visits 4 and 5, `R2-HOST-DETDIFF` 14/0/0.
The start-return contract (PL-22, PL-24, PL-44 via PL-53). S-2 (the current limit), S-3 (the scale,
6138 against the predicted 6136), S-4 (the e-stop latch). C-1 (the speed law, <0.5 % over 48 rungs). C-5
(the lag limiter). PL-36, PL-40, PL-42 (90 ticks/rev, 270 transitions over 3 revolutions), PL-50. The
hall `illegal 1` at start («#3524»). The attended UI rebuild (B-1 … U-4).

---

## 6 · What the tests measure that nothing needs, and what they taught beyond the question

Asked by STEPHEN, 2026-09-17: *"are there any tests that provide values which are not attributable to findings
we need? have we learned more than we asked and is any of it useful?"*

**Method.** Five read-only agents inventoried every record each bench binary emits (`test_bench_t0`, `_spin`,
`_detect`, `_char`, `_scan`, `_dual`) and mapped each field to the sign-off cell or finding that consumes it,
then read the newest real log for its tier. Logs read: t0 (Visit 5) in full; char (Visit 4), dual-a and dual-b
(Visit 5), detect-phase2 (Visit 2) in part. **Not read:** spin, dual-c, dual-clock, dual-d, and the scan's run-8
log (its numbers come from the Visit 2 report). The scan's own emission table was not completed; its
self-checks were read against the current driver instead (§6.3).

### 6.1 Values that feed nothing

| Where | What | Disposition |
|---|---|---|
| t0 T0-1, T0-2, T0-4, T0-10 (`start_return`) | print values for findings now fixed in source (A1, A2/A3, O, AD+); **no sign-off cell** | retire, or convert to regression cells |
| t0 T0-8 | cog count under exhaustion, printed, never judged | setup for `R1-T0-EXHAUST`; its cog churn is what «#3543» removes |
| detect `BD-RUN.run_ts` | always the literal token `HOSTLOG` | drop -- it measures nothing |
| detect `bnc` / `bnc_max` | bounce counts, never compared to anything | attribute or drop |
| char `BC-SENSE` min/max/watts | ripple bounds and derived power | cheap; drop or attribute |
| dual `BM-RUNG2` `err` / `err_pk` | **unjudged, and misread as the slam** | replace with the transition statistic (PL-87) |
| dual `BM-CLOCK` `dead_gap` | A1 is closed | keep as a free regression print |

Most other unattributed fields are cheap context on lines that must print anyway.

### 6.2 The opposite gap — recorded but never judged

- **The idle wheel during another wheel's fault or overshoot trial** (`BM-TS o_pos/o_hw/o_i/o_up`): nothing fails
  if it moves or faults.
- **Part B's offset restore after the 180° fault-API trial** (`BM-OFFREST`): its cell is part C's, so a failed
  restore in part B lets the run continue on a wrong offset.
- **char `BC-HOLD steady_src`**: a hold that reached "steady" by TIMEOUT silently weakens that hold's window.

### 6.3 Learned beyond the question — and useful

1. **FLOAT at rest takes the `driveoff` path** (char quiescent hold: `duty_` wound to `duty_max` 24_264, current
   near zero, `debug_260917-125254.log:91-93`). Bears on PL-89; the duty telemetry at rest reports a duty that
   is not applied.
2. **The scan's geometry is invalid on today's driver.** It finds each window edge by walking until the motor
   FAULTS; the lag limiter makes it droop instead. The stop condition must become a droop detector — its own
   `R12-SCAN-RATE` tick-rate check is ready — and the fold-back limit must be checked against the worst swept
   current. Scan defects D1-D5 and D7 are fixed; D6 and D8 are unconfirmed.
3. **PL-61 is explained, and unloaded top speed is set by bus voltage:** current peaks ~6.7 A at rung 6 and
   collapses once duty saturates while back-EMF keeps rising.
4. **detect's raw `IN` snapshots carry the hall bits** — a free instrument for the hall lines at rest, and they
   caught motors plugged in when the run sheet said unplugged.
5. **Smaller:**
   - lag rises monotonically with commanded speed (`err_pk` 107 at rung 11);
   - the implied sense scale holds at 148-152 across the whole ladder, both motors;
   - rest current is 3.5 mA and 6.5 mA on the two boards (PL-45's closure, quantified);
   - `BM-FBTRIAL` already records peak current and duty at a fault — data for the fault-handling design;
   - the fourth ADC channel reads live (1_134 counts) — the route to battery voltage.

---

## 7 · Rulings taken the same night (STEPHEN, 2026-09-17)

- *"clean up all state that is aged. it always misguides to keep it clean is priority!"* — done first («#3567»);
  doctrine overlay P11 now says aged state is priority work.
- **Order of work:** API promises → hall fix and characterisation → fault handling → code/comment sync always →
  the style gate → every outstanding task → the commutation scan and offset confirmation.
- *"yes the spin2 style guide is a gate for this project - we deliver code, it MUST match our style guide (all
  .spin2 files in repo that we produced in project - not those copied from other developers)"* — PL-2, PL-10,
  PL-11 in this release.
- *"your outstanding tasks must be completed before this release"*, and *"no those three are not in"* — the
  measurement front end, the vibration study and the N-motor roster stay out.
- *"we need confirmation of motor phase offsets before release - finish the commutation scan"*; then *"yes spin in
  place but max revolutions limit so we don't stress cable"* — lifted scan, then an attended spin-in-place floor run.
- Stop behaviour is the user's `holdAtStop()` selection; every path honours it (§2.1).
- *"yes to all"*: PL-73 in (refuse an undetected board unless a revision is forced); S-8 in (opt-in link-loss
  timeout); S-6 out (document the status values); AK measured feedback out (Known Issue) — and *"we should be able
  to report battery size/voltage compiled in"*: a getter for the compiled-in voltage is in.

---

## Revision history

- **2026-09-17, afternoon** — opened. Partial: 8 of 22 documents read. It surfaced the scan stall, PL-69,
  PL-55's status, the float/brake question, the e-stop hold and the board phase-sense difference.
- **2026-09-17, evening** — completed. The remaining 14 documents and the whole punch list were read by
  nine read-only agents, and a tenth checked 17 of the 2026-09-09 findings against current source. The
  arbiter read Visit 5, `BOARD-REVISION-FACTS`, PL-56, PL-69, PL-89, PL-90, `holdAtStop()`, `checkstop`
  and the hall read directly. New this pass:
  - PL-89's table is backwards against `checkstop`, and it contradicts Stephen's recorded bench fact
    (§2.1);
  - the hall-network answer had been on file since 2026-09-10 (§2.5);
  - three of the scan's four blockers are gone (§2.2);
  - six findings wait on one fault stimulus (§2.3);
  - 16 stale records (§3);
  - 11 study findings fixed in source, and 7 still present (§4).
  - Shape D is added to §1.
- **2026-09-17, night** — §2.1 gains Stephen's disposition (honour `holdAtStop()`); §2.3 corrected: Visit 3
  had certified M, AF and S-5 with a fault provoked on purpose, which this audit missed; §3 marked applied;
  §6 (the emission inventory) and §7 (the night's rulings) added.

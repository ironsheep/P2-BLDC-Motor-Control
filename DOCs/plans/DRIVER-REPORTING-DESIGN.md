# Driver Reporting — design for R20.1 («#3621», phase 1)

**Status:** reviewed and ruled, 2026-09-25 (§10). Ready to build.
**Scope:** Stephen's five API rulings of 2026-09-25 (plan R20, `BENCH-READINESS-SPRINT-PLAN.md` §R20), in
`isp_bldc_motor`, `isp_steering_2wheel` and `isp_steering_serial`.
**Provenance marks:** MEASURED (log or file:line), DERIVED (my reasoning, from the lines cited), STEPHEN (his words).
Unless a section says otherwise, line numbers are in `src/isp_bldc_motor.spin2` (**M**) and `src/isp_steering_2wheel.spin2` (**S**) at `ebea690`.

---

## 0. The shape in one paragraph

Every new mechanism lives in Spin2 on the **front cog**. The front cog already owns every stop, so it also
writes each stop's reason (`getStopReason()`) and queues each soft condition it handles (`getEvent()`). A stop
path writes its command first and its record second, so no record delays a stop (D6). The PASM driver, its two
shared-memory runs and its LUT are unchanged (§7). `start()` gains bounded re-checks and a refusal. The fault
and hold setters become public. `FR_GRADED` becomes the default in a separate one-line change, gated on pass 5.

---

## 1. Stop reasons — `getStopReason()`

### 1.1 The contract

| Rule | Decision |
|---|---|
| Values | `#40, SR_NONE, SR_COMMANDED, SR_AT_LIMIT, SR_FAULT_CONTROLLED, SR_FAULT_LOST, SR_BLOCKED, SR_LINK_LOST, SR_EMERGENCY, SR_PARTNER` (40–48) |
| Why base 40 | The serial link carries these as numbers. The other enums on the wire are DS\_\* 10–15 (M:73), REV\_\* 20–22 (M:55) and BRD\_\* 30–32 (userconfig:38). ERR\_\* are all below −1_000 (M:117–119). So no stop reason can be read as a status, a board, or an error (P3/D7). |
| Meaning | **Why the last drive ended.** `SR_NONE` means no drive has ended since the last drive command, or since `start()`. |
| Opened by | A drive command the front cog *accepts*: a non-zero power, `driveForDistance()`, or a non-zero TEST-USE increment. It sets `stopReason := SR_NONE` and `bDriveOpen := TRUE`. A refused command opens nothing. |
| Written by | `frontRecordStop(eReason)` (new, **M**, FRONT COG ONLY), and nothing else. If `bDriveOpen` is set, it writes the reason, clears `bDriveOpen` and queues `EV_STOP` with that reason (§2). Otherwise it writes nothing. |
| First cause wins | The first stop after a drive is the reason. A later stop of that motor, such as an e-stop at rest after a limit, changes nothing here. It appears only in the event stream when it is a fault. **One exception:** `SR_FAULT_CONTROLLED` escalates to `SR_FAULT_LOST` when a latched fault begins on the re-synced stop. That second fault changes what the wheel did: control was lost. |
| Sticky until | The next accepted drive command. `start()` (through `init()`) sets `SR_NONE`. `stop()` leaves the value readable. |
| Single writer | The front cog only: the object's own front cog, or the steering front cog through the **M** routines. `init()` writes the value before any front cog exists. |
| Not | Not a `getError()` code, and `getStatus()` is unchanged (STEPHEN: *"getStatus unchanged … not a getError code"*). |

**Why "first wins" (DERIVED).** Stephen's words are *"the user needs to know how the stop was commanded when not
expected"*. That asks for the cause, not the last thing to happen. Take a user `stopMotor()` followed by a fault
on the ramp down. The stop was still commanded; the fault is reported by `EV_FAULT` and `getFaultCause()`.
§10 Q2 asks Stephen to confirm this.

**The walk needs no special case (DERIVED).** `REQ_WALK` (M:4385–4396, S:2454–2470) is not a drive command, so
it opens nothing. Every stop inside `checkWiring()` then finds `bDriveOpen` FALSE and writes nothing: the leg's
limit, the guard's short (M:2444), and `bWalkLeg()`'s timeout stop (M:2736, S:1684). If a drive was open when
`checkWiring()` was called, the walk's first command ends it with `SR_COMMANDED`: a call the program made ended
that drive. The walk's verdict stays with `HLT_WIRING`, and a guard trip is reported by `EV_WALK_GUARD`.

### 1.2 Every stop path

"Where the record is written" is the line that calls `frontRecordStop()`, always **after** the command write on
that path.

| # | Stop path (what ends the drive) | Single motor (**M**) | Steering (**S**) | SR recorded |
|---|---|---|---|---|
| 1 | `stopMotor()` / `stopMotors()`: REQ_STOP | apply M:4353–4355 (`frontStopCommanded` M:2247) | apply S:2390–2396 (each selected wheel) | SR_COMMANDED |
| 2 | A zero power: `driveAtPower(0)`, or a zero wheel in `driveAtPower(l, r)` / `driveDirection(p, ±100)` | REQ_DRIVE M:4375–4377 with nArg1 = 0 | REQ_DRIVE S:2437–2440, per wheel with 0 | SR_COMMANDED |
| 3 | A synchronized drive the driver did not take, which zeroes the motor | M:4446–4449 | S:2630–2637; plus the refused-clear and write-race zeroing at S:2607, S:2642 | SR_COMMANDED (the program's call ended it and returned the error) |
| 4 | TEST-USE zero increment | REQ_TEST_INCREMENT M:4405–4409 | S:2485–2493 | SR_COMMANDED |
| 5 | Distance, rotation or time limit | M:4176–4177 (`bFrontLimitsDue` M:2559) | platform S:2096–2099 (both wheels); per-wheel `driveForDistance` S:2101–2104 (that wheel) | SR_AT_LIMIT |
| 6 | Command timeout (S-8) | M:4178–4179 (M:4419–4432) | S:2105–2107 (both) | SR_LINK_LOST |
| 7 | Blocked wheel, protective stop | M:4180–4181 (`frontProtectiveStop` M:2305) | S:2109–2113 | SR_BLOCKED; in steering the **unblocked** wheel gets SR_PARTNER (both get SR_BLOCKED if both were blocked on that pass) |
| 8 | Fault answered by re-sync (FR_GRADED, halls legal) | inside `frontNoteFault` M:4591–4600, called by `frontTrack` | the same routine, from S:2088–2089 | SR_FAULT_CONTROLLED |
| 9 | Fault latched, DCS_FAULTED (PASM `.blunt` M:6486–6494: full short, graded short, or a coast under SM_FLOAT) | inside `frontNoteFault` M:4603–4611 | the same, from S:2088–2089 | SR_FAULT_LOST; escalates an SR_FAULT_CONTROLLED still standing |
| 10 | Partner fault (R19.2, PL-117) | — | `frontPlatformFaultStop` S:2713–2735 (called S:2092, after both `frontTrack`s) | SR_PARTNER on the wheel that did not fault; the faulted wheel already holds its own reason from row 8 or 9 |
| 11 | `emergencyCutoff()`: REQ_ESTOP | apply M:4350–4352 | apply S:2383–2389 | SR_EMERGENCY. Recorded at the **apply site**, not in `frontEStop()` (M:2455), because the walk guard also calls `frontEStop(TRUE)` (M:2444) |
| 12 | Walk leg: its limit, the guard (M:2441–2446), or its timeout stop (M:2736, S:1684) | — | — | none (the gate; see §1.1) |
| 13 | Hold hand-off to the short (M:2406–2419) | at rest, no drive open | same | none; `EV_HOLD_*` |
| 14 | `clearEmergency` / `clearProtectiveStop` zero writes (M:4356–4363, S:2397–2413); the zero written by `frontClearFault` (M:2141–2151) | motor already stopped, drive closed | same | none |
| 15 | No-answer fallback: `frontSecure()` from `stopMotor` / `emergencyCutoff` (M:698–702, M:718–722, S:1724–1730) | caller's cog | caller's cog | **none**: this cog is not the writer (see the limit below) |
| 16 | `stop()` (M:265, S:286) | cogs stopped | same | none; the last reason stays readable |

**Paths that cannot be told apart today, and what each needs:**
- **The walk guard against a user e-stop.** Both call `frontEStop(TRUE)`. *Needs:* the record written at the
  REQ_ESTOP apply site (row 11), and none in `frontEStop()`.
- **Which wheel was blocked.** Both wheels latch the same `ERR_PLATFORM_BLOCKED` (S:2112–2113), so
  `getProtectiveStop()` cannot say which one was blocked. *Needs:* the reason chosen from `bLeftBlocked` /
  `bRightBlocked` (S:2109–2110). The stop reason then carries the one thing the protective code cannot. §10 Q5
  asks Stephen to confirm SR_PARTNER here.
- **Re-sync against latched fault.** `faultResponse` writes the `fault` long for **every** fault (M:6473), so
  `isFaultSignal()` (M:1537) reads TRUE after a re-sync too, and cannot tell them apart. They are already told
  apart by two edges: `fault_resyncs` changing (M:4591) and DCS_FAULTED beginning (M:4603). Rows 8 and 9 key on
  those edges, so nothing new is needed. This also answers R19's question 3 ("should `getError()` report a
  re-sync?"): SR_FAULT_CONTROLLED reports it, and it is not an error.
- **Known limit, row 15.** When a running front cog fails to answer within `REQ_ACK_TIMEOUT_MS`, the caller's
  cog secures the motor directly. A write there would give `stopReason` a second writer, so nothing is recorded,
  and a drive left open reads SR_NONE while the motor is stopped. This path exists only when the front cog has
  failed, and it already prints `! ERROR … front cog did not answer`. The DRIVE-OBJECTS.md line for
  `getStopReason()` states it.

---

## 2. The soft-event log — `getEvent()`

### 2.1 Kinds

`#60, EV_NONE, EV_LOST, EV_STOP, EV_FAULT_RESYNC, EV_FAULT, EV_HOLD_SLIP, EV_HOLD_LIMIT, EV_CURRENT_LIMIT,
EV_PATH_LIMIT, EV_HALL_MISSED, EV_HALL_ILLEGAL, EV_WALK_GUARD, EV_LATE_PASS, EV_PACK, EV_CHECK_RETRY, EV_FOLDBACK`
(60–75, disjoint from every other enum on the wire). Wheel identities for the steering object:
`#50, EVW_LEFT, EVW_RIGHT, EVW_PLATFORM`.

| Kind | Condition | Where the front cog sees it today | `value` | Trigger |
|---|---|---|---|---|
| EV_NONE | nothing unread | — | 0 | returned only when this cog has nothing unread and lost nothing |
| EV_LOST | this cog fell more than EV_QUEUE_DEPTH behind | reader side (§2.2) | events lost | synthesised for one reader; it always comes **before** that reader's retained events and before any EV_NONE (D2) |
| EV_STOP | a stop reason was written | `frontRecordStop()` (§1.2) | the SR\_\* written | once per recorded stop, plus the one escalation |
| EV_FAULT_RESYNC | a fault answered by re-sync | M:4591 (`fault_resyncs` changed) | FC_LAG | edge |
| EV_FAULT | DCS_FAULTED began | M:4603–4611 | FC_LAG or FC_HALL | edge |
| EV_HOLD_SLIP | hold handed to the short on a slip | M:2406–2409 | `holdDisp`, ticks | edge (once per rest, by the HS\_ state machine) |
| EV_HOLD_LIMIT | hold handed to the short at its time limit | M:2416–2419 | `hold_duty` at the ceiling | edge (once per rest) |
| EV_CURRENT_LIMIT | the thermal derate engaged or released | M:2290–2295 | the limit now in force, A (`limitContA` or `limitPeakA`) | edge (each transition) |
| EV_PATH_LIMIT | steering path limiter engaged, or fully released | S:2172–2175 (the drop from 1000 only), S:2176–2181 (back to 1000 only) | the scale, ‰ | edge: engage and release only, never each deepening step. Logged on the short wheel; the lower one if both are short |
| EV_HALL_MISSED | `hall_missed` grew | not read per pass today (only M:1161). One read is added | the growth since the last EV_HALL_MISSED | rate-limited: at most one per EV_RATE_GAP_MS, so the counts are carried, never dropped |
| EV_HALL_ILLEGAL | `hall_illegal` grew | M:4602 (already read every pass) | the growth, both words summed | rate-limited, as above |
| EV_WALK_GUARD | the walk guard shorted a leg | M:2443–2446 | the net mV that tripped it | edge (once per leg) |
| EV_LATE_PASS | a front pass overran its slot | M:4190–4195, S:2124–2129 | late passes since the last EV_LATE_PASS | rate-limited; steering reports it as EVW_PLATFORM |
| EV_PACK | pack sensor status changed | `frontSamplePack` M:1226–1232 (the status test of M:1244) | the new PACK\_\* status | edge, and at most one per EV_RATE_GAP_MS |
| EV_CHECK_RETRY | a start check failed, then passed on retry | §3; queued by the front cog through `frontNoteStartChecks()` | the recovered HLT\_\* mask \| (attempts used << 8) | once per start |

**EV_FOLDBACK: a driver counter.** STEPHEN 2026-09-25, *"yes A"*.
- The driver's per-frame current fold-back (M:5828–5832) gets a counter register, `foldback_cnt_`.
- One `if_nc add foldback_cnt_, #1` runs on the fold-back branch only, so a normal frame costs nothing.
- The count is published as a new status long, `foldback_frames`.
- The front cog queues EV_FOLDBACK on the edge where the count starts to grow (value 0), and again when it has been
  still for EV_RATE_GAP_MS (value = frames limited since the engage). A sustained push is therefore two events,
  never a flood.
- `duty_capped` (M:5852) counts the PL-55 duty cap, which is a different limiter.
- The thermal derate, which the front cog already sees, is EV_CURRENT_LIMIT.
- **ABI change, §7.**
- **Cell:** R20-DUAL-EV-FOLDBACK, in dual-d's low-limit LIMIT segment. EV_FOLDBACK must appear in the limited
  segment and must not appear in any default-limit run segment.

**Not separate kinds (DERIVED, one value one meaning).** Command timeout, blocked, e-stop and partner stops all
end a drive, so each is EV_STOP with its SR\_\*. Sync timeout is not an event: the call that caused it returns
it.

### 2.2 The queue: layout, ownership and readers

Per motor object instance (**M**), all Spin2-only VAR, appended to the front-cog block after `cmdTimeoutSeen`
(M:5300):

| Long(s) | Writer | Purpose |
|---|---|---|
| `evKind[17]`, `evMs[17]`, `evVal[17]` | front cog | a ring of `EV_QUEUE_DEPTH + 1` = 17 slots; index = sequence +// 17 |
| `evHead` | front cog | events queued this lifetime; written **last** in each write (publish) |
| `evEpoch` | `start()`, before any front cog (by `init()`) | lifetime number, so a reader discards a cursor left from an earlier lifetime |
| `evTotal[EV_KINDS_COUNTED]` | front cog (`init()` zeroes it before launch) | per-kind totals since start. They are never lost |
| `evCursor[8]`, `evCursorEpoch[8]` | **each reader cog, its own long only**, indexed by COGID() | where this cog has read to |
| rate/edge state (`evLastMissed`, `evLastIllegal`, `evLastLate`, `evLastPack`, three last-ms longs) | front cog | the rate limits of §2.1 |

**Several user cogs are correct by construction, with no lock (DERIVED).** Each cog has its own cursor, and only
that cog writes it. This is the pattern `getError()` already uses for `cmdTimeoutSeen` (M:762–767), where every
cog hears of every timeout once and no long has two writers. So **every reader cog sees the whole stream**, and
no cog can steal another's event. The front cog never waits on a reader: a reader that falls behind loses its own
oldest events, and learns it as EV_LOST.

- **Write** (front cog, `frontQueueEvent(eKind, nValue)`): slot `evHead +// 17` ← kind, `getms()`, value; then
  `evTotal[kind]++`; then `evHead++`, last.
- **Read** (caller cog c, `getEvent()`):
  1. If `evCursorEpoch[c] <> evEpoch`, set the cursor to 0 and adopt the epoch.
  2. `lag := evHead − cursor`. If lag is 0, return EV_NONE.
  3. If lag > 16, return **EV_LOST** with value `lag − 16`, and set the cursor to `evHead − 16`.
  4. Otherwise copy the slot, then read `evHead` again. If the lag is now > 16, the front cog may have been
     rewriting this slot during the copy: discard the copy and take step 3. Otherwise advance the cursor and
     return the copy.
  The seventeenth slot is what makes this sound. The front cog writes slot `evHead +// 17` before it publishes,
  and that slot is never one a reader with lag ≤ 16 can be reading. So a torn copy is always detected.
- **Signatures.**
  - **M:** `getEvent() : eKind, nMs, nValue`. There is no motor field, because this object is one motor
    (DEVIATION, §9).
  - **S:** `getEvent() : eKind, nMs, eWheel, nValue`. It first reports a loss on either wheel's ring (left
    first). Then it returns the older of the two rings' next events by `nMs` (signed difference; a tie goes
    left). EV_LATE_PASS is reported as EVW_PLATFORM.
  - Totals: **M** `getEventTotal(eKind) : nCount`; **S** `getEventTotal(eKind) : nLeft, nRight, nPlatform`.
    EV_NONE and EV_LOST have no total: they read 0 and record ERR_BAD_COUNT, as any other out-of-range enum does.
- **Steering platform events** go in the left wheel's ring, flagged by their kind. The steering front cog is
  still that ring's only writer. This avoids a third ring (lean).
- **`start()` empties the log**: `init()` advances `evEpoch` and zeroes `evHead` and the totals before the front
  cog exists. A `getEvent()` running on another cog *during* `start()` is as undefined as any getter there.

**Depth.** `EV_QUEUE_DEPTH = 16` per motor, provisional (Stephen's starting value). With every kind
edge-triggered or rate-limited, the worst sustained rate is set by the three rate-limited kinds at one per second
each, plus a burst of about four on a fault pass. A reader that polls at least once a second on a quiet robot
does not lose events. Bursts are sized by §6's EV_LOST cell. DERIVED.

### 2.3 Cost per pass, and the steering front cog's budget

**Budget.**
- MEASURED: the steering front cog's worst pass was 847 µs against the A-10 gate of ≤ 950 µs, with 0 late passes
  and stack 135 of 256 (`2026-09-22/VISIT-8-EVALUATION.md:104,118`, after `updateFollowing()`).
- The earlier 914 µs (`DRIVE-INTEGRATION-DESIGN.md:276`) predates `updateFollowing()`.
- **Unmeasured since:** R19 added `frontHold` ×2, `frontWalkGuard` ×2, `frontPlatformFaultStop` and
  `frontSamplePack` to the steering loop (S:2090–2116). So the headroom today is unknown and could be under
  103 µs.

**Where the new work goes (DERIVED).**
- **No pass without an event does new work on the slot pass.** The slot pass (`passCount +// WINDOW_PASSES ==
  0`) carries the two `updateWindowAccumulators()` calls and `frontLimitPath()`, and it is the likely worst pass.
  The only per-pass checks, for the hall and pack rate limits, run in `frontEventChecks()` on the **opposite
  phase**, `passCount +// WINDOW_PASSES == WINDOW_PASSES / 2`: two compares per wheel.
  - The late-pass check runs only on a pass that is already late.
  - The edge kinds sit inside branches that already exist (M:2290, 2406, 2416, 2443, 4591, 4603).
- **A queued event** costs one `frontQueueEvent()`: about eight hub reads or writes and one `getms()`. DERIVED
  estimate: 5–10 µs per event at 270 MHz. Unmeasured.
- **The worst event burst on one pass** is a steering fault pass: EV_FAULT, then EV_STOP on the faulted wheel,
  then EV_STOP(SR_PARTNER) on the other. Three events, about 15–30 µs, and that pass can coincide with a slot
  pass.

**Measured before this can ship.** The new cell R20-DUAL-FRONTST-EV (§6) reads `testGetFrontStats()` after FLTPLAT,
which is the run that produces that burst. It is gated at A-10's ≤ 950 µs with late 0.

**Contingency, not built unless the cell fails.** A fault pass would set a per-wheel pending mask, and
`frontEventChecks()` would queue it on the next opposite-phase pass. That moves at most 1 ms of latency onto the
*record*, never onto the stop.

**D6.** Every `frontRecordStop()` / `frontQueueEvent()` call is placed after the command write on its path, so no
record delays a stop. The PASM driver loop is not touched (§7).

---

## 3. `start()` refusal, retries, and `getHealth()`'s third result

| Item | Decision |
|---|---|
| Checks that can refuse | `START_CHECKS_REFUSE = HLT_HALLS \| HLT_SENSE_ZERO \| HLT_PHASE_U \| HLT_PHASE_V \| HLT_PHASE_W` (= HLT_ALL_CHECKS, M:101) |
| Not refusing | HLT_WIRING (the walk: opt-in, and it moves the wheel). HLT_PACK: the pack sensor measures the pack, not the drive, so an unplugged sensor must not stop a robot (DERIVED; §10 Q4) |
| What a retry re-runs | **Only the refusing checks that failed, in the same driver lifetime.** Phase: all three probes again, about 40 ms, re-judging the three phase bits. Halls: the code must be legal now, and `hall_illegal` must not grow during the retry gap (not "since driver start", which a boot transient would fail for ever). Sense zero: this wheel's rest zero re-captured (`captureRestZero()`, about 1 s) and re-judged |
| Not re-run: the driver launch | DERIVED from PL-120, MEASURED. The failing state survived 8 fresh driver lifetimes in one program (`PUNCH-LIST.md` PL-120, 2026-09-24 21:21), and pass 1's all-phase failure held across all 10 starts. So no measured case exists that a relaunch clears and a re-check does not. A relaunch in steering would also need both drivers re-parked for a new lockstep release (S:219–225) |
| Count | `START_CHECK_RETRIES = 3` (PROVISIONAL, STEPHEN "provisional 3"), meaning up to 4 attempts. `START_CHECK_RETRY_MS = 250` (PROVISIONAL) is the gap before each retry, so a transient can pass. Both are sized by the bench (§6 R20-DUAL-RETRY) |
| Worst added time | Only on a failure. Phase only: 3 × (250 + 40) ≈ 0.9 s. With sense zero: 3 × (250 + 1_000 + 40) ≈ 3.9 s per wheel, and steering checks its wheels in turn |
| Retries with opt-out | They run in both modes, so the verdict and the third result mean the same thing either way. The opt-out removes only the refusal |
| `runStartChecks()` | Returns the refusing bits still failed after the retries. It sets `healthRecovered`: the refusing bits that failed in some attempt and pass in the final one |
| Refusal (single motor) | `startEx()` (M:241–247): after the checks, if the refusing bits are non-zero and the refusal is on, it calls `stop()`, records `ERR_START_CHECK_FAILED` (= −1_020, the next free code after M:161) and returns −1. `startPackSense()` does not run |
| Refusal (steering) | `start()` (S:240–242): both wheels' checks, with their retries, run after the lockstep release and before the front cog exists. If either wheel fails and the refusal is on: `ltWheel.stop()`, `rtWheel.stop()`, no front cog, return −1. `recordError(ERR_START_CHECK_FAILED)` goes in the platform slot and `recordCallerError()` in each failing wheel's slot, so `getError()` says which wheel |
| `setStartChecks(bRefuse)` | Both objects. Call before `start()`. Stored as `bStartChecksOptOut`, which is **not** reset by `init()`. A VAR is zero at load, so the default (refuse) is correct by construction. Returns NO_ERROR, and takes effect at the next `start()`. Steering keeps its own copy; its wheels' copies are unused under `startOwned()` |
| `getHealth()` after a refusal | Readable. `healthChecked`, `healthFailed` and `healthRecovered` are written by `runStartChecks()`, cleared only by `init()` at the next start (M:3193–3194), and never touched by `stop()` (M:265–315). Steering's `getHealth()` reads its wheels' longs directly, with no front cog needed |
| Third result | **M** `getHealth() : nChecked, nFailed, nRecovered`; **S** `getHealth() : nLeftChecked, nLeftFailed, nLeftRecovered, nRightChecked, nRightFailed, nRightRecovered`. *nRecovered*: refusing checks that failed at least once and then passed. They are not in *nFailed* |
| Event | `EV_CHECK_RETRY`, queued by the front cog. **M**: the start's cog posts the new `REQ_NOTE_START` once `start()` succeeds, and its apply calls `frontNoteStartChecks()`; the front cog runs during the checks, so the caller's cog must not write the ring. **S**: `frontLoop()`'s entry (S:2059–2071) calls it for each wheel, because the checks finished before that cog existed. No per-pass cost |
| Pack sensor | `startPackSense()` runs only on a start that is not refused. HLT_PACK is judged as today |

**Test hooks the negatives need (TEST-USE, before `start()`).**
- `testSetProbeWithhold(ePhase)` keeps its meaning, "that one start". It now covers **every attempt** of that
  start, and is cleared at the end of `start()` rather than inside the check. That is the refusal negative.
- New `testSetProbeWithholdFirst(ePhase)`: the withheld phase applies to the **first attempt only**. That is the
  retry-reporting positive.
- Steering mirrors: `testLeftSetProbeWithholdFirst()` / `testRightSetProbeWithholdFirst()`.

**What the harness must now call.**
- `dual-start-phaseneg`: the lifetimes rotate three ways:
  - **opt-out**, `setStartChecks(FALSE)`, which keeps R19-DUAL-PHNEG-X and WINDNEG-X exactly as today;
  - **refusal**, the default;
  - **withhold-first**.
- `dual-start-nowalk` (B-1) opts out, because its floated window needs running drivers.
- Positive tiers keep the default.
- `bSteerStart()` (test_bench_dual:16550) and `bWheelStart()` (:16053) print the −1 cause, `getError()`, and
  all three health masks on a refused start.
- The harness's 4 s start stall watchdog (named at M:5042–5043) must cover the worst retry time above.

---

## 4. Public setters and getters

| Motor object (**M**) | Range / validation | Errors |
|---|---|---|
| `setFaultResponse(eMode, brakePct)`; **replaces** `testSetFaultResponse` (M:811) | eMode ∈ {FR_SHIPPED, FR_GRADED}; brakePct 0..100 | ERR_BAD_COUNT (nothing changed); ERR_NOT_STARTED / ERR_NO_RESPONSE (it is posted to the front cog, the only writer) |
| `getFaultResponse() : eMode, brakePct` | returns the % as set. A new `faultBrakePct` long is needed because `brake_on` holds frames (M:2357) | — |
| `setHoldLimits(ceilingPct, riseMs, limitMs)`; **replaces** `testSetHoldLimits` (M:798) | 1..100; 1..HOLD_RISE_MS_MAX; 1..HOLD_LIMIT_MS_MAX (M:5024–5025, now public) | as above |
| `getHoldLimits() : ceilingPct, riseMs, limitMs` | the values as set; three new longs, since M:2346–2348 stores derived passes | — |
| `setStartChecks(bRefuse)` | any value; non-zero means refuse | NO_ERROR |
| `getStopReason() : eReason` | — | — |
| `getEvent()`, `getEventTotal(eKind)` | §2.2 | ERR_BAD_COUNT for a kind outside the counted kinds |

- Both setters say in their doc that `start()` restores the defaults, as `setCommandTimeout()` does (M:483).
- The hold defaults are documented as **sized unloaded** (STEPHEN, ruling 2). The floor run (R19.8) sizes them
  loaded.
- `testGetFaultResponse` / `testGetHold` stay TEST-USE: they return internals, including counters.
- `test_bench_dual` and `test_bench_t0` call sites move to the new names.

**Steering mirrors (S).**
- `setFaultResponse`, `getFaultResponse`: both wheels are always set together, so the getter returns the left
  wheel's values, and the doc says both wheels carry them.
- `setHoldLimits`, `getHoldLimits`, `setStartChecks`.
- `getStopReason() : eLeftReason, eRightReason`, `getEvent()`, `getEventTotal()`, and `getHealth()` with six
  results.
- These replace S:681–716.

**Re-exports added to S:13–146 (CLAUDE.md rule).** For each constant below, **M** moves it into the public CON
block (M:14–175) where it is internal today, and **S** re-exports it:
- `FR_SHIPPED`, `FR_GRADED`: values unchanged, because the PASM compares `#FR_GRADED` (M:6474, 6489);
- `SR_*` (9);
- `EV_*` (15);
- `EVW_*` (3; S only);
- `ERR_START_CHECK_FAILED`;
- `HOLD_RISE_MS_MAX`, `HOLD_LIMIT_MS_MAX`;
- `EV_QUEUE_DEPTH`.

**Serial protocol exposure (`isp_steering_serial`, DRIVE-OBJECTS-SERIAL.md).** The design only; build with the
rest.

| Command | Reply |
|---|---|
| `getstopreason` | `stopreason {lt} {rt}` (40–48) |
| `gethealth` | `health {ltChk} {ltFail} {ltRecov} {rtChk} {rtFail} {rtRecov}` |
| `getevent` | `event {kind} {ms} {wheel} {value}`: one event per request, `kind` 60 when empty. The serial loop is one cog, so it is one reader with its own cursor |
| `getevtotal {kind}` | `evtotal {lt} {rt} {plat}` |
| `setfaultresp {mode} {pct}` / `getfaultresp` | OK \| ERROR / `faultresp {mode} {pct}` |
| `setholdlimits {pct} {rise} {limit}` / `getholdlimits` | OK \| ERROR / `holdlimits {pct} {rise} {limit}` |

- `errorName()` gains `ERR_START_CHECK_FAILED`.
- The "Values sent as numbers" table gains rows for SR, EV and EVW.
- **Gap:** on a refused start the serial top level never starts its host link (`isp_steering_serial.spin2:170–174`), so the host
  cannot ask why (§10 Q6).

---

## 5. FR_GRADED as the default

- **The change:** one constant, `FAULT_RESPONSE_DEFAULT = FR_GRADED` (M:4932), with its comment. It takes effect
  through `init()` (M:3179) → `frontSetFaultResponse()`, and writes the `fault_mode` parameter at run time, so the
  driver image is unchanged.
- It bumps `DRIVER_REV` (M:4973), as every behaviour change does.
- **It lands only after pass 5 (R20.6) certifies the right wheel's fault cells** (STEPHEN ruling 1, *"yes A"*,
  conditional). Those cells are owed under PL-120.
- It lands as its own commit after that certification, separate from the rest of R20.1. So the API work can land
  and be certified without it.
- With it, SR_FAULT_CONTROLLED becomes the usual fault reason, and SR_FAULT_LOST means that control was lost.

---

## 6. Bench cells

Every cell prints SIGNOFF-DECL / SIGNOFF as the harnesses already do, and states the reading before the run. PASS
needs the positive **and** the negative. Tier names follow `tools/bench-run.sh`.

| Cell | Tier | Pre-registered reading (positive) | Negative that makes it able to FAIL |
|---|---|---|---|
| R20-T0-SR-COMMANDED | t0-stopreason (see ‡) | `driveAtPower(15)`, 300 ms, `stopMotor()` → SR_COMMANDED; still COMMANDED 500 ms later (sticky) | After `driveAtPower(15)`, before any stop, it must read **SR_NONE**. A reason that is never cleared fails |
| R20-T0-SR-ATLIMIT | t0-stopreason | `stopAfterTime(300, DTU_MILLISEC)` + drive → SR_AT_LIMIT | `stopMotor()` at 100 ms under the same armed limit → SR_COMMANDED, not AT_LIMIT |
| R20-T0-SR-ESTOP | t0-stopreason | drive, `emergencyCutoff()` → SR_EMERGENCY (then `clearEmergency()`) | `emergencyCutoff()` **at rest after a COMMANDED stop** → still SR_COMMANDED (first wins, and no drive is open) |
| R20-T0-SR-LINKLOST | t0-stopreason | `setCommandTimeout(100)`, drive, no command for 400 ms → SR_LINK_LOST | the same with the command re-sent every 30 ms for 400 ms, then `stopMotor()` → SR_COMMANDED |
| R20-T0-EV-STOP | t0-stopreason | draining after the four cells above (each leg run in the order listed) gives exactly seven EV_STOP: 41 (COMMANDED), 42, 41 (the ATLIMIT negative), 47, 41 (the ESTOP negative's stop; the e-stop at rest records nothing), 46, 41 (the LINKLOST negative), with rising `ms` | a missing, extra or reordered EV_STOP fails. The e-stop at rest adding an eighth also fails |
| R20-T0-EV-LOST | t0-stopreason | 20 drive/stop cycles **without draining**, then drain → EV_LOST value 4, then 16 EV_STOP, then EV_NONE | **This is the negative itself:** EV_NONE before EV_LOST, a count ≠ 4, or fewer than 16 retained fails (D2: a dropped event never reads as none) |
| R20-T0-EV-TOTAL | t0-stopreason | after EV-LOST, `getEventTotal(EV_STOP)` = 27 (7 + 20) | a total that counts only the drained events (7 + 16 = 23) fails |
| R20-T0-EV-2COG | t0-stopreason | a helper cog and the main cog each drain the same 4 stops and each read all 4 | either cog reading fewer than 4 (a shared cursor) fails |
| R20-DUAL-SR-FAULT | dual-fault (FLTRESP X-4) | FR_GRADED, one forced fault at speed → SR_FAULT_CONTROLLED; EV_FAULT_RESYNC value FC_LAG | X-2 (FR_SHIPPED) must **not** read SR_FAULT_CONTROLLED, and the rest-hook trial (`frHookRestTrial`, test_bench_dual:10657) must read SR_NONE |
| R20-DUAL-SR-FLOST | dual-fault (X-2, X-3, X-6) | X-2 / X-3 → SR_FAULT_LOST with EV_FAULT; X-6 (a second fault on the re-synced ramp) → escalated SR_FAULT_LOST, with EV_STOP 43 then 44 | X-4 must **not** read SR_FAULT_LOST |
| R20-DUAL-EV-FOLDBACK | dual-d (LIMIT, low `testSetCurrentLimits`) | EV_FOLDBACK engage (value 0), then its release with value > 0 frames | 0 EV_FOLDBACK in the default-limit run segments |
| R20-DUAL-SR-PARTNER | dual-fault (FLTPLAT, `segFaultPlat` :8885) | the faulted wheel reads SR_FAULT_LOST (LEFT, FR_SHIPPED) or SR_FAULT_CONTROLLED (RIGHT, FR_GRADED); the other reads **SR_PARTNER** | the faulted wheel reading PARTNER, or the other reading any fault reason, fails. **Owed:** the RIGHT trial needs the right wheel driving (PL-120) |
| R20-DUAL-FRONTST-EV | dual-fault, after FLTPLAT | steering worst pass ≤ 950 µs, late 0, stack < 256 | its own threshold. This is the budget in §2.3 |
| R20-DUAL-REFUSE | dual-start-phaseneg (refusal lifetimes) | `start()` = −1; `getError()` = ERR_START_CHECK_FAILED (platform and LEFT); `getHealth()` after the refusal reads LEFT failed = exactly the withheld bit | the opt-out lifetimes (next row) |
| R20-DUAL-OPTOUT | dual-start-phaseneg (opt-out lifetimes) | `start()` ≥ 0 with the same withheld bit failed | a refusal here fails. Paired with REFUSE, each is the other's control |
| R20-DUAL-RETRY | dual-start-phaseneg (withhold-first lifetimes) | `start()` ≥ 0; LEFT failed 0, recovered = the withheld bit; EV_CHECK_RETRY value = bit \| (2 << 8) | positive `dual-start`: every lifetime recovered 0 and no EV_CHECK_RETRY (a spurious retry fails) |
| R20-DUAL-NOREFUSE | dual-start (positive) | 10 of 10 starts ≥ 0 | a refused healthy start fails |
| R20-DUAL-EV-WALKGUARD | dual-start-swapneg | each swapped LEFT walk that the guard ends → EV_WALK_GUARD, value ≥ WALK_I_LIMIT_MV | positive dual-start walks: 0 EV_WALK_GUARD |
| R20-DUAL-EV-HALLMISSED | dual-start-swapneg | EV_HALL_MISSED on LEFT; the sum of its values = the growth in `getHallIntegrityCounts()` | positive dual-start: 0 hall events on either wheel |
| R20-DUAL-EV-HALLILL | dual-start-nowalk (B-1, attended, opt-out) | RIGHT: EV_HALL_ILLEGAL; the sum of its values = its illegal count | LEFT (connected): none |
| R20-DUAL-EV-PATH | dual-d (the A-7 load) | EV_PATH_LIMIT engage (value < 1000) on the short wheel, then release (1000) | a steering segment with no wheel short: none |
| R20-DUAL-EV-CLIMIT | dual-d (LIMIT, low `testSetCurrentLimits`) | EV_CURRENT_LIMIT value = contA, then peakA | 0 events in the run segments at default limits. **NOT CHECKED** whether wheels-up reaches the derate; if not, it moves to the floor |
| R20-T0-EV-HOLD | t0-stopmode (T0-24 rows 1–3, attended) | the slip row → EV_HOLD_SLIP, value \|disp\| ≥ 2; the limit row (short `setHoldLimits`) → EV_HOLD_LIMIT | the hold row that must not slip: none |
| R20-T0-EV-LATE | every tier that prints FRONTST | EV_LATE_PASS total > 0 **iff** late > 0 | the consistency check itself fails either way. The positive side is NOMEAS while late stays 0 (MEASURED 0 at Visit 8) |
| R20-PACK-EV | R20.4's pack run (attended) | unplugging the sensor → EV_PACK value PACK_ABSENT; replugging → PACK_PRESENT | a pack held steady for 60 s: no EV_PACK |
| R20-FLOOR-SR-BLOCKED | dual-spin / floor («#3576») | the blocked wheel reads SR_BLOCKED, the other SR_PARTNER; EV_STOP for each | **SR_BLOCKED cannot be provoked wheels-up** (PL-106; MEASURED NOMEAS in every part-D run, `VISIT-8-EVALUATION.md:108–111`). A wheel that did not block reading BLOCKED fails |

‡ **Tier.** The brief puts the COMMANDED, AT_LIMIT, EMERGENCY and LINK_LOST cells in `t0`. `t0` promises no
motion (bench-run.sh:111), and each of these cells has to drive the wheel. So the design puts them in the t0
binary behind `-D T0_STOPREASON`, as a new tier `t0-stopreason` [MOTORS CONNECTED, WHEELS UP, UNATTENDED], on
the `t0-stopmode` precedent (DEVIATION, §9).

---

## 7. Cog RAM, LUT, parameter ABI and hub cost

- **PASM: one change, the fold-back counter (EV_FOLDBACK, STEPHEN "yes A").**
  - One register, `foldback_cnt_`, zeroed at driver start with `fault_resyncs_`.
  - One instruction on the fold-back branch.
  - Cog RAM goes 491 → 493 of 496, per the compiler at `fit 496`, M:6163; recount at build.
  - The register joins the status run that the driver block-copies out, so `DRVR_STATUS_LONGS_COUNT` goes 20 → 21.
  - The hub `foldback_frames` long is inserted as the run's last long, **before** `fault`, which must stay
    immediately after the run (CLAUDE.md ABI rule).
  - The count constant, the VAR, the PASM register order and `isAbiLayoutValid()` all change together.
  - DRIVER_REV bumps.

  Everything else is Spin2 on a front cog or a caller's cog:
  - stop reasons and events: §1 and §2, front cog;
  - retries: §3, caller's cog, reusing the existing probe path `probe_phase` (M:1112);
  - setters: the existing `REQ_SET_FAULT` / `REQ_SET_HOLD` (M:4366–4369);
  - FR_GRADED: a run-time parameter write (§5).
- `DRVR_LAUNCH/PARAMS_LONGS_COUNT` are unchanged at 4 and 25. STATUS goes 20 → 21 (above). The LUT stays at 229 of
  512 (M:6505).
- **New VAR** is Spin2-only, appended after `cmdTimeoutSeen` (M:5300) inside the block `isAbiLayoutValid()`
  already fences (M:3760). The only edit there is that range's last long moving to the new last long.
- **Hub per motor instance (DERIVED):**

  | Item | Longs |
  |---|---:|
  | ring (51) + head (1) + epoch (1) | 53 |
  | cursors and their epochs | 16 |
  | totals | 15 |
  | rate and edge state | 7 |
  | `stopReason`, `bDriveOpen` | 2 |
  | `healthRecovered`, `bStartChecksOptOut`, `testProbeWithholdFirst` | 3 |
  | the as-set fault and hold values | 4 |
  | **Total** | **≈ 100 (≈ 400 bytes)** |

  - The steering object carries about 800 bytes in its wheels, plus a few longs of its own.
  - `test_bench_t0` holds 6 motor instances and 1 steering object, so about 3.2 KB of VAR.
  - Code is per object, not per instance. Its size is **NOT CHECKED** until the build's `.lst`.
- **Front stack:** two call levels are added under `frontTrack` (`frontNoteFault` → `frontRecordStop` →
  `frontQueueEvent`). MEASURED high-water marks: 115 of 192 (motor) and 135 of 256 (steering)
  (`VISIT-8-EVALUATION.md:118`). The next FRONTST reading re-measures them.

---

## 8. User-document lines to draft (R20.5 writes the prose)

- **DRIVE-OBJECTS.md, both interface tables:**
  - `getStopReason()`, with the SR\_\* list, "first stop after a drive", and the no-answer limit;
  - `getEvent()` and `getEventTotal()`, with per-cog reading, EV_LOST, and "no peak fold-back in the log";
  - `setFaultResponse` / `getFaultResponse`;
  - `setHoldLimits` / `getHoldLimits`, "sized unloaded";
  - `setStartChecks`;
  - `getHealth()`'s third result, replacing "a wheel that fails one still starts" (S:1019–1020, M:1255);
  - `start()`'s −1 on ERR_START_CHECK_FAILED.
- **DRIVE-OBJECTS.md "Errors":** ERR_START_CHECK_FAILED (−1020).
- **DRIVE-OBJECTS.md "Protection and limits":** the faults bullet names SR_FAULT_CONTROLLED and SR_FAULT_LOST, and after
  §5 the graded default.
- **DRIVE-OBJECTS-SERIAL.md:** the §4 commands, and the numbers-table rows for SR, EV and EVW.
- **README "Latest Changes":** stop reasons; the event log; start refuses a failed check after retries (with the
  opt-out); public fault and hold setters; later, the graded fault response as the default.

---

## 9. Deviations from the rulings and the brief

1. **EV_FOLDBACK needs a PASM counter and a status long** (§2.1, §7). STEPHEN chose it over a sampled detector and
   over leaving it out.
2. **The single-motor `getEvent()` has no motor field.** The object is one motor. Steering returns `eWheel`, which
   is Stephen's "motor".
3. **SR_PARTNER also covers the unblocked wheel of a blocked pair**, not only a fault partner. Its one meaning is
   "the other wheel's condition stopped this one; read that wheel's reason" (Q5).
4. **The four t0 SR cells go to a wheels-up t0 sub-tier**, since plain t0 promises no motion (§6 ‡).
5. **A retry does not relaunch the driver** (§3, from PL-120 MEASURED).
6. **`getHealth()` gains a result**, as ruled. DERIVED from the `_` placeholders at M:2647 and S:246, a caller's
   result count must match the method's. So every caller changes: S:1027–1028, test_bench_dual:11087 and :11250,
   and user code in the 6.0.0 notes.
7. **`testSetFaultResponse` / `testSetHoldLimits` are removed**, not kept beside the public names (one name, one
   meaning). The harness call sites move.

---

## 10. Open questions

**Ruled by Stephen, 2026-09-25:**
- **Q1, the names: `SR_FAULT_CONTROLLED` and `SR_FAULT_LOST`** (*"yes A"*). The first draft's `SR_FAULT_BRAKED`
  described a brake that coasts under SM_FLOAT.
- **Q3, fold-back: a driver counter** (*"yes A"*), as in §2.1 and §7.

The question list as first drafted:
- **Q1.** The name for "fault, control lost".
- **Q2.** First cause wins (with the fault escalation), or the latest stop wins?
- **Q3.** Fold-back reporting: a PASM counter (+1 status long, DRIVER_REV), a sampled front-cog detector
  (misses short fold-backs), or none for 6.0.0?
- **Q4.** Should HLT_PACK stay out of the refusal? (Recommended: yes.)
- **Q5.** SR_PARTNER for the unblocked wheel, or SR_BLOCKED on both, matching `getProtectiveStop()`?
- **Q6.** On a refused start, should the serial top level still open its host link, answering only
  `gethealth` / `geterror`, so an RPi can learn why?

**Review, 2026-09-25 (arbiter).** Two load-bearing claims were checked against the source:
- the fold-back branch (M:5828–5832) counts nothing;
- the health longs are cleared only at M:3193–3194 and rewritten at M:1100.

Four of the six questions are settled here, because each has one reading that keeps the API's promise (overlay P3).
They are reported to Stephen, not put to him:
- **Q2: first cause wins.** His words ask *"how the stop was commanded when not expected"*, which is the cause. A
  later fault on a commanded stop is still reported, by EV_FAULT and `getFaultCause()`.
- **Q4: HLT_PACK stays out of the refusal.** The sensor is optional hardware. Refusing a robot for a sensor it may
  not have fitted breaks `start()`'s promise to start a drivable motor.
- **Q5: SR_PARTNER for the unblocked wheel.** It carries the one fact `getProtectiveStop()` cannot, which is which
  wheel was blocked. Its meaning stays single: *the other wheel's condition stopped this one.*
- **Q6: yes.** On a refused start the serial top level opens its host link answering `gethealth` and `geterror`
  only. A refusal the host cannot ask about fails ruling 4's purpose.

Two go to Stephen, one at a time:
- Q1, the name. Naming is his.
- Q3, fold-back reporting. It adds a status long, so it is a priced driver change (P5).

`getHealth()`'s extra result costs users nothing: the method is new in 6.0.0, so no released code calls it.

**Mine (settled at build, reported back):**
- the 17-slot ring;
- `EV_RATE_GAP_MS = 1_000`, `START_CHECK_RETRY_MS = 250` (provisional; the bench sizes them);
- the per-event cost (the FRONTST cell measures it);
- the `t0-stopreason` tier name;
- whether `REQ_NOTE_START` is appended after `REQ_EXIT` (the codes are internal, not on the wire).

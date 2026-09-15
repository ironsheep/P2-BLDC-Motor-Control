# Motion Harness -- Design (task «#3508», phase 1)

**Status:** DESIGN, for arbiter review. Phase 2 implements it. No source, tool or manifest file is
changed by this document.

**Governs:** `src/test_bench_dual.spin2` (new), `src/isp_bench_log.spin2` (new, PL-17), and the
bench-config, runner, collation and manifest changes listed in section 9.

**Scope ruling carried in (STEPHEN 2026-09-14):** *"we are not doing any external measurement"*.
Every reading comes from the driver's own status block, its calibrated sense channel (150 mV/A,
Rev B) and the hall inputs. Regen current into the pack and FET temperature are **not measured**
and are reported as such (reason tokens `NO_EXTERNAL_I`, `NO_TEMP_SENSOR`), never as tested.

**Provenance tags:** MEASURED (a log line or a bench evaluation, cited) · DERIVED (a reading of
source or arithmetic, cited `file:line`) · STEPHEN (his words) · UNVERIFIED (a P2/Spin2 semantic
not citable from a file in the tree; collected in section 11).

**Findings this harness serves** (definitions: `DOCs/analyses/DRIVER-SAFETY-AND-CAPABILITY-STUDY-2026-09-09.md`
C-1 `:587`, C-3 `:685`, C-4 `:723`, C-5 `:745`, C-6 `:795`, S-1 `:64`, S-3 `:155`, S-5 `:278`,
S-9a `:395`; `DOCs/analyses/DRIVER-AUDIT-2026-09-09.md` M `:73`, AF `:102`, Z `:493`, AC `:443`;
bench method
`DOCs/analyses/BENCH-TEST-PLAN-2026-09-10.md` T1-1 `:638`, T1-2 `:716`, T1-3 `:737`, T1-4 `:775`,
T1-6 `:849`, T1-7 `:882`, T1-8 `:946`, T1-9 `:971`, T2-1 `:1205`).

---

## 1 · Invariants -- the construction, and the failure it makes impossible

Each row names a construction the implementation must keep, the failure it removes, and the
sign-off cell (section 5) that certifies it on the rig.

| # | Construction | Failure made impossible | Cell |
|---|---|---|---|
| I1 | **All timed sampling happens in one instrument cog whose call graph contains no `debug()` statement.** Its only library calls are `testGetMotorCog()`, `testGetTelemetry()`, `getRawHallTicks()`, `getHallIntegrityCounts()` (motor) and the steering pass-throughs `testGetDriverState()`, `testLeftGetTelemetry()`, `testRightGetTelemetry()`, `testGetRawHallTicks()`, `getHallIntegrityCounts()`; none contains a `debug()` (DERIVED: `isp_bldc_motor.spin2:798-811`, `:1164-1186`, `:1234-1242`; `isp_steering_2wheel.spin2:491-500`, `:615-676`). | A `debug()` inside a timed window dominating the timing it measures (plan hazard 1, `BENCH-TEST-PLAN-2026-09-10.md:1316-1321`). The instrument never contends for the DEBUG lock, so no other cog's output can delay a sample, and no emitter on cog 0 can be inside a timed loop because cog 0 has no timed loop. | R14-DUAL-INSTLIVE-A |
| I2 | **Every accumulator is bounded by construction:** statistics are computed only at drain, over at most `INST_RING_SAMPLES` (4096) samples whose fields were clamped when stored (i to +/-32767 mV, phase sum to +/-32767 mV, duty to 0..65535, err to -128..127). Worst sums: duty 65535 x 4096 = 268_431_360; phase 32767 x 4096 = 134_213_632; both < POSX (2_147_483_647). The only run-long counters (samples, late, dropped, seq) saturate at `LIM_BIG` before incrementing. | PL-20's wrapped mean (`DOCs/PUNCH-LIST.md:522-534`): no sum can exceed a long, however long a segment runs. | coverage (no unfixed path exists in a new binary) |
| I3 | **Telemetry is read only from a running driver**, gated per sample and per motor: WHEEL source `up := testGetMotorCog() <> 0` (`isp_bldc_motor.spin2:1234-1242`); STEER source `up := state <> DCS_Unknown`, valid because `stop()` writes `DCS_Unknown` after its `cogstop` (`isp_bldc_motor.spin2:132-138`). A sample with `up` FALSE stores the flag and prints driver fields as `NA` with reason `NO_COG`. | PL-21's frozen status block read as a measurement (`DOCs/PUNCH-LIST.md:536-551`, MEASURED `debug_260912-153807.log:460`). | R14-DUAL-INSTLIVE-A (frozen i fails it) |
| I4 | **Instrument cog lifecycle is owned by cog 0 and cooperative.** Started once at run start, stopped once at run end (no thrash, decision 22). Stop = command `INST_CMD_EXIT`, bounded wait for the acknowledged state `INST_EXITED`, then `cogstop`. It allocates and holds no lock. Because of I1 it can never be mid-DEBUG when stopped. Every shared long has exactly one writer (table in section 2.4). | A stopped cog leaking a lock or cutting a DEBUG message (PL-41, STEPHEN 2026-09-14 *"cogstop clears the locks but if the stopped cog didn't rlease them first they are leaked"*); two cogs writing one value. | R14-DUAL-NOSTALL-* (BM-INST STOP with ack) |
| I5 | **Every other cog that can be stopped by a library `stop()` is also DEBUG-free in this build.** The quiet build sets `MOTOR_DBG_MASK` and `STEER_DBG_MASK` to ERROR + WARNING only. That compiles out every `debug()` reachable from the steering sense task and the motor sense task: steering FAULT `:530-547` (`getFaultStatus()`), `:1011`, SENSE `:1121`, `:1136`; motor FAULT `:684` (`clearEmergency()`, called from the sense task), `:978` (`clearFaultSignal()`, called from `getFaultStatus()`), SENSE `:1790`, `:1795` (DERIVED from the channel map, `DOCs/plans/DEBUG-CHANNELS-DESIGN.md:123-151`). The ERROR/WARNING statements left are reachable only from calls cog 0 makes. | `steering.stop()` or `wheel.stop()` cutting a sense cog mid-message (PL-41 instances, `DOCs/PUNCH-LIST.md:1183-1191`). | R14-DUAL-DBGMASK-* |
| I6 | **The idle wheel is floated by never being started.** A motor-frame segment `stop()`s both wheels, then starts only the wheel under test (the char pattern, `src/test_bench_char.spin2:54-56`). `holdAtStop(TRUE)` is issued only to the wheel under test, only inside a trial that requests BRAKE, and every exit path of that trial issues `holdAtStop(FALSE)` before the next statement that commands anything. Steering segments drive both wheels and set `holdAtStop(FALSE)` at start. | Holding current on the idle wheel (plan `:527-531`), and a brake request leaking from one trial into the next. | R14-DUAL-IDLEFLT-A |
| I7 | **No post-fault stop outcome is labelled in advance.** A trace header names only what was *requested* (`req_mode` FLOAT/BRAKE) and what was *done* (`cause` FAULT/ESTOP/STOPCMD/STOPCOG); no field, token or on-board verdict names what the wheel did afterwards. Every post-fault and post-e-stop trace is preceded **in the same program load** by FLOAT and BRAKE baseline traces on the same motor, sign and speed, so the analyser compares like with like. | Pre-deciding S-9a's open question, whose two plausible answers are opposite (study `:419-430`). | coverage; analyser S-9a (section 5.3) |
| I8 | **A truncated log is detectable record by record.** Every `BM-` record carries a run-wide `seq` (1, 2, 3 ...); every trace carries `BM-TRACE-END` with its emitted-line count and a checksum over emitted `k`; the run ends with `BM-END records,<last seq>` then `DEBUG_END_SESSION`. A gap in `seq`, a trace whose end record is missing or disagrees, or a missing `BM-END` names the last good record. | An analyser verdict from a log that stopped early or dropped lines (plan `:891-893`; collation's COMPLETE rule `tools/signoff-collate.py:708-711` covers only the end marker). | host rule (#3509) |
| I9 | **One top-level trap, printed every run.** `main()` makes exactly one trapped call, `trapCode := \runPart()`, and emits `BM-TRAP` on every path. No other `\` exists in the file, there is no `abort` statement in the file, and no normal return is ever captured through a trap. | PL-44's zero-reading captures and nested traps (`DOCs/PUNCH-LIST.md:1337-1449`); decision 21. | R14-DUAL-NOSTALL-* (trap field) |
| I10 | **Cog 0 never touches a wheel while the instrument is reading it.** Any `start()`, `stop()`, source switch or ring drain is legal only while the instrument has acknowledged `IDLE` or `FROZEN`; the wrappers check the acknowledged state first and refuse (count + `BM-SEG why,INST_BUSY`) otherwise. | A sample straddling `init()` writing the VARs the instrument reads; a drain racing the writer. | coverage |
| I11 | **Every side effect a trial creates is undone on every exit path of that trial, before the next check reads anything.** Ramping values are read back to the defaults, offsets to the pair read at that lifetime's start, stop mode to FLOAT, e-stop cleared. Each restore is read back and printed. | A trial's ramp or offset silently governing the next trial (decision 20, *"no cleanup before its check"*). | R14-DUAL-RAMPREST-B, R14-DUAL-OFFREST-C |
| I12 | **Board detection is never forced;** `BRD_AUTO_DET` at every start, and the detected revision is logged at every wheel-object start. | Hiding a detection regression (plan `:320-321`). | R14-DUAL-REVB-A |

---

## 2 · The instrument cog

### 2.1 What it samples, per sample, for both motors

`cogspin(NEWCOG, instrument(), @instStack)` in the top file. A cogspin'd method of the top file calling
child-object methods is the scan watchdog's proven pattern (MEASURED: its `wheelL.stop()` /
`testGetTelemetry()` calls ran in `DOCs/analyses/bench/2026-09-14/debug_260914-114523.log:74-82`).

Per sample the instrument reads, for LEFT then RIGHT:

| Source `instSrc` | `up` | status longs | position | integrity |
|---|---|---|---|---|
| `INST_SRC_WHEELS` (wheelL/wheelR) | `testGetMotorCog() <> 0` | `testGetTelemetry()`: duty, err, sense_i, sense_u, sense_v, sense_w, state, fault | `getRawHallTicks()` (driver `pos`) | `getHallIntegrityCounts()` |
| `INST_SRC_STEER` (steering object) | `state <> DCS_Unknown` from `testGetDriverState()` | `testLeftGetTelemetry()` / `testRightGetTelemetry()` | `testGetRawHallTicks()` | `steering.getHallIntegrityCounts()` |
| `INST_SRC_NONE` | FALSE | not read | not read | not read |

Plus, **independent of the driver**, for each motor: the three hall inputs at base+5..base+7,
read with `pinread(base + 5 addpins 2)` and decoded with a local copy of `deltas65` into `hwPos`
(the T0-12 method, `src/test_bench_t0.spin2:214-232`, `:1270-1276`). The hall inputs are plain
inputs, never smart pins (`src/test_bench_t0.spin2:1214-1218`), so no `RDPIN`/`RQPIN` is involved.
`hwPos` is the only position that keeps counting after `stop()` freezes `pos` (T1-1 condition c),
and it cross-checks `pos` everywhere else. A code change with a zero table delta that is not an
illegal code increments `hwSkip` (a transition the 2 ms poll could not resolve: counted, never
silent). DERIVED ceiling: one transition per poll at 500 Hz is 500 ticks/s; the ladder's top probe
(165_000_000) predicts 461 ticks/s, so `hwSkip` may become non-zero only at the top two rungs.

The instrument never commands a motor and never calls a library method with a side effect.

### 2.2 Period, from CLK_FREQ

```
INST_RATE_HZ       = 500                               ' 2 ms, plan T1-1's poll period (BENCH-TEST-PLAN :688-691)
INST_PERIOD_TICKS  = CLK_FREQ / INST_RATE_HZ           ' 400_000 @200 MHz, 540_000 @270, 600_000 @300
INST_LATE_TICKS    = INST_PERIOD_TICKS / 4             ' a sample later than this past its due time is "late"
```

Schedule is absolute: `dueCt += INST_PERIOD_TICKS` each sample. Before waiting, the loop computes
`slack := dueCt - getct()` (signed). If `slack > 0` it `waitct(dueCt)`; if `slack <= 0` it does **not**
call `waitct` (UNVERIFIED 11.1: a `waitct` target already passed waits for the counter to wrap,
~15.9 s at 270 MHz) and instead: `late += 1`, `maxLateTicks #>= -slack`, and, if `-slack >=
INST_PERIOD_TICKS`, re-bases `dueCt := getct() + INST_PERIOD_TICKS` and adds the whole periods skipped
to `skipped`. Each stored sample carries its own `getct()` (field `t`), so an analyser never assumes
the nominal period. The Spin2 cost of one two-motor sample is not known (UNVERIFIED 11.4); `late`,
`skipped` and `maxLateTicks` make an overrun visible and counted.

`instDecimate` (1..`INST_DECIM_MAX` 20) stores one sample in N; only the wheels-down segment uses
it (N = 10, 20 ms).

### 2.3 Ring buffer layout and RAM

One sample = 9 longs, written in this order at `ring[w * INST_SAMPLE_LONGS]`:

| Offset | Content |
|---|---|
| +0 | `t` -- `getct()` at the start of the sample |
| +1 | LEFT `pos` (driver) |
| +2 | LEFT `sense` = `(i clamped to i16) << 16` OR `((u+v+w) clamped to i16) & $FFFF` |
| +3 | LEFT `flags` = `duty` (0..65535) << 16 OR `(err & $FF)` << 8 OR `state` (0..7) << 5 OR `fault` << 4 OR `up` << 3 OR `integDelta` (0..7, saturating) |
| +4 | LEFT `hwPos` |
| +5..+8 | RIGHT, same four |

`integDelta` = (missed + illegal now) - (missed + illegal at the previous stored sample), saturating
at 7; a saturation increments `integSat`. Each clamp of i, phase sum, duty or err increments `clamps`.

```
INST_SAMPLE_LONGS = 9
INST_RING_SAMPLES = 4096                               ' 8.19 s at 500 Hz, 81.9 s at decimate 10
ring bytes        = 4096 x 9 x 4 = 147_456 (144 KB)
INST_STACK_LONGS  = 128                                ' P2AN006 start value, as the scan watchdog (test_bench_scan.spin2:718-746)
```

DERIVED sizing: the longest undecimated capture is the stop-mode coast (spin-up excluded; capture
starts `TRACE_PRE_SAMPLES` = 50 samples before the stop mark and ends at rest or at
`TRACE_MAX_SAMPLES` = 4000, 8.0 s). The field widths are DERIVED from source: duty_max = 24_264 at
270 MHz and 26_960 at 300 MHz (`isp_bldc_motor.spin2:336`, MEASURED 24_264 at `debug_260912-153807.log:25`);
`err` is `sar #24` of a long, -128..127 (`isp_bldc_motor.spin2:2534`); DCS_* is 0..7 (`:1951`). Phase 2
must report the compiled image size and confirm the ring fits the hub with DEBUG enabled
(UNVERIFIED 11.10).

### 2.4 Ownership: one writer per value

| Value | Writer | Readers |
|---|---|---|
| `instCmd`, `instArg0..2`, `instCmdSeq`, `instSrc`, `instDecimate`, `instMarkCt`, `instMarkSeq` | cog 0 | instrument |
| `instAckSeq`, `instState`, `instHeartbeat`, `ring[]`, `instW`, `instTotal`, `instLate`, `instSkipped`, `instMaxLateTicks`, `instClamps`, `instIntegSat`, `instHwSkip[2]`, `instLast*[2]` (last sample mirror: i, state, fault, up, pos, hwPos) | instrument | cog 0, watchdog (heartbeat only) |
| `wdHeartbeat`, `wdCheckpoint` | cog 0 (`beat()`) | watchdog |
| `wdDeclaring` | watchdog | cog 0 |

Command handshake: cog 0 writes the arguments, then `instCmd`, then increments `instCmdSeq`. The
instrument, once per loop, sees `instCmdSeq <> instAckSeq`, executes the command, then writes
`instState` and finally `instAckSeq := instCmdSeq`. Cog 0 waits for `instAckSeq == instCmdSeq`, bounded
by `INST_ACK_TIMEOUT_MS` = 100 (50 periods), beating `CP_INST_ACK` every `SAMPLE_MS` (5 ms). A timeout
emits `BM-INST event,NOACK` and the segment is skipped with `why,INST_NOACK`.

### 2.5 States and commands

| Command | Legal from | Effect | Acked state |
|---|---|---|---|
| `INST_CMD_ARM` (arg0 source, arg1 decimate) | IDLE, FROZEN | clears `instW`, `instTotal`, per-capture counters; starts storing | RUN |
| `INST_CMD_FREEZE` (arg0 post-samples) | RUN | stores arg0 more samples, then stops storing; keeps its heartbeat and `instLast*` mirror current | FROZEN (acked only after the post samples) |
| `INST_CMD_IDLE` | FROZEN, RUN | stops storing and stops reading any wheel | IDLE |
| `INST_CMD_EXIT` | any | stops reading; loops `waitms(INST_EXIT_POLL_MS)` forever | EXITED |

The ring is circular while RUN: when `instTotal > INST_RING_SAMPLES` the oldest samples are
overwritten and the excess is reported as `lost_head` in `BM-TRACE-END` (a pre-trigger history that
outlived the ring; counted and printed, never silent). Every capture this design commands is bounded
to fit, except the hand-brake wait, where `lost_head` is expected and harmless because the freeze
follows the fault.

`instMarkCt`/`instMarkSeq`: cog 0 writes `getct()` into `instMarkCt` immediately before the library
call that starts the event (the stop command, the fault-provoking offset write, `emergencyCutoff()`,
`stop()`). At drain, the mark index is the first stored sample whose `t` is at or after the mark, found
on the single `getct()` timebase (UNVERIFIED 11.6).

### 2.6 Drain and emission

- Drain happens only in FROZEN or IDLE (I10); the instrument is not writing the ring, so cog 0 reads
  it without a race.
- Cog 0 computes rung statistics from the drained samples (I2) and emits trace lines under the
  decimation rule in section 3.5. Every emitted record goes through one helper, `emitRecord()`, which
  beats `CP_EMIT` before and after its single `debug(zstr_(log.pLine()))`.
- Emission never happens in RUN except the cog-0 safety records `BM-ABORT` (emitted after the wheel it
  stops has been stopped), so no command timing depends on the serial link.

### 2.7 Overrun and drop -- counted, emitted, judged

| Counter | Meaning | Printed in | Judged |
|---|---|---|---|
| `late` | a sample started more than `INST_LATE_TICKS` after its due time | `BM-RUNG3`, `BM-TRACE-END`, `BM-INST` | analyser flags a rung or trace whose late fraction exceeds 10 % as `DEGRADED` |
| `skipped` | whole periods with no sample | same | same |
| `lost_head` | samples overwritten before the freeze | `BM-TRACE-END` | trace marked `HEAD_LOST`; never a verdict input before `k = 0` |
| `dropped` | a stored sample index beyond the capture (a capture longer than `TRACE_MAX_SAMPLES`) | `BM-TRACE-END`, `BM-INST` | cell R14-DUAL-RING-A (0..0) |
| `clamps`, `integSat`, `hwSkip` | field clamp, integrity delta saturation, unresolved hall transition | `BM-RUNG3`, `BM-TRACE-END` | analyser annotates |

### 2.8 Cog 0 safety monitor

Cog 0 never calls a library getter inside a timed wait. It reads the instrument's `instLast*` mirror
every `SAMPLE_MS` (5 ms) and acts: `i >= ABS_ABORT_MV` (1_500 mV = 10 A, the scan's limit,
`src/test_bench_scan.spin2:482-483`) on `ABS_ABORT_SAMPLES` (4) consecutive reads stops that wheel
first, then records `BM-ABORT`; a fault flag ends the wait; the instrument heartbeat not advancing
for `INST_STALL_MS` (100 ms) ends the segment with `why,INST_STALLED`. Cog 0 also detects AT_SPEED and
STOPPED from the mirror, so one timebase governs both command decisions and samples.

---

## 3 · Record format

### 3.1 Rules (every `BM-` record)

- **Tag first**, prefix `BM-` (bench motion), then comma-separated `name,value` pairs, every field
  always present, in the order tabled below. One record = one `debug(zstr_(...))` line from the
  shared builder (section 7). Worst case of every record is under 280 bytes, the longest record
  measured intact (`src/test_bench_scan.spin2:153-154`).
- **Second field is always `seq`** (run-wide, from 1, `LIM_MID`), I8.
- **Clamps:** every numeric field is clamped to one width: `LIM_TINY` 999 (4 bytes), `LIM_SMALL`
  99_999 (7), `LIM_MID` 9_999_999 (10), `LIM_BIG` 999_999_999 (12) (`src/test_bench_scan.spin2:497-500`).
  Numbers carry `_` grouping (the builder's `lineAddNum`, `:5491-5517`). A token longer than its
  maximum prints `?`.
- **Booleans** print `TRUE`/`FALSE` (decision 13). **Absence** prints `NA`.
- **`why` is the last field of every measurement record** (token, max 18). It is `NONE` when no
  field is `NA`; otherwise it names the cause of every `NA` in that record. By construction every
  `NA` in one record comes from one first cause; a record in which two independent absences could
  co-occur is split into two records instead (this is why steering traces have their own header).
- **Attribution (PL-19):** every record names the motor (`LEFT`, `RIGHT`, or `BOTH` for steering)
  and the command (`incre` for a wheel, `l_pwr`/`r_pwr`/`power` for steering), either directly or
  through an id whose header carries them: `rid` -> `BM-RUNG`, `tid` -> `BM-TRACE`/`BM-STRACE`,
  `sid` -> `BM-SSTART`. A child whose parent header is absent is unattributable, and the analyser
  treats it as truncation (I8).
- **Applied offsets:** every wheel measurement header carries `off_neg`/`off_pos` read back with
  `testGetFwdRevIndep()` (`isp_bldc_motor.spin2:1100-1111`) immediately before that measurement.
  Steering segments never change offsets, so `BM-SSTART` carries the pair for its whole lifetime.
- **Integrity beside every measurement:** `BM-RUNG3` carries `missed_d`/`illegal_d`; every trace end
  carries `ig_sum`/`o_ig_sum`; every `BM-TS` carries `ig`.

**`why` tokens:** `NONE`, `NO_COG`, `NOT_REACHED`, `FAULTED`, `STEADY_TIMEOUT`, `WINDOW_TIMEOUT`,
`STOP_TIMEOUT`, `NO_SAMPLES`, `NO_FAULT`, `ABORTED`, `INST_NOACK`, `INST_STALLED`, `INST_BUSY`,
`RING_LOST_HEAD`, `MOTOR_RETIRED`, `OPERATOR_SKIP`, `OPERATOR_TIMEOUT`, `NO_PASSTHROUGH`,
`UNSWEPT_CLOCK`, `LADDER_STOPPED`, `SYNC_PRECOND`, `NO_EXTERNAL_V`, `NO_EXTERNAL_I`, `NO_TEMP_SENSOR`,
`PART_NOT_BUILT`.

Byte counts below: each field is `2 + len(name) + width`; the total includes the tag.

### 3.2 Header records (emitted before anything moves)

| Tag | Fields in order (width) | Worst case |
|---|---|---|
| `BM-BANNER` | seq(MID), src_rev(SMALL), fmt(SMALL), part(tok 5: `NONE` `A` `B` `C` `CLOCK` `BRAKE` `FLOOR`), cfg_id(tok 5), frame(tok 5 `MOTOR`), clkfreq(BIG), left_base(SMALL), right_base(SMALL), voltage_enum(SMALL), det_mode(SMALL), motor_type(SMALL), quiet(BOOL), mdbg(SMALL, compiled `user.MOTOR_DBG_MASK`), sdbg(SMALL) | 241 |
| `BM-BUILD` | seq, sf(TINY), inst_hz(SMALL), inst_ticks(BIG), ring(SMALL), slongs(TINY), waitms_max(SMALL), wd_stall_ms(SMALL), abs_abort_mV(SMALL), ladder_max(BIG), rwire_mohm(SMALL), pack_mV(SMALL), fault_cool_ms(SMALL) | 237 |
| `SIGNOFF-DECL` | as `DOCs/plans/VISIT-SIGNOFF-DESIGN.md:480`, `bin,DUAL` | 65 |
| `BM-WDSTART` | seq, started(BOOL), cog(TINY) | 48 |
| `BM-INST` | seq, event(tok 7 `START` `STOP` `NOSTART` `NOACK`), cog(TINY), state(tok 7), ack_ms(SMALL), samples(BIG), late(BIG), skipped(BIG), max_late_us(MID), clamps(MID), why | 198 |
| `BM-PLAN` | seq, seg(tok 8), order(TINY), attended(BOOL), part(tok 5), finds(tok 24, `_`-joined finding ids), est_s(SMALL) | 117 |
| `BM-LADDER` | seq, rung(TINY), incre(BIG), pred_x10(MID), probe(BOOL) | 85 |

`part` comes from its own `#ifdef` chain, never a runtime test, so a mistyped `-D`
lands on the honest `NONE` (the scan's `cfg_id` pattern, `src/test_bench_scan.spin2:3829-3841`).
`quiet`, `mdbg` and `sdbg` print what was compiled, so the debug-mask build is proven in the log.
`rwire_mohm` (20) and `pack_mV` (18_500) are the constants the C-6 wiring-drop bound needs (section 5.3).
A line `* PANIC PROCEDURE IS PHYSICAL BATTERY DISCONNECT ONLY -- emergencyCutoff() self-cancels in about 250 ms (finding S-4)`
follows the header, as the scan does (`:3827`).

`pred_x10` = predicted hall ticks per second x10 from C-1: `incre x 12_000 x 10 / 2^32`, computed in
two steps to stay inside a long: `(incre / 1_000) x 120 / 4_295` for positive magnitude (DERIVED from
study `:580`, 90 ticks per revolution, 15 electrical cycles; rounding error < 0.1 %). The harness
prints it; it never judges C-1.

### 3.3 Lifetime and rung records

| Tag | Fields in order | Worst case |
|---|---|---|
| `BM-START` (wheel object start) | seq, seg, motor, life(SMALL), cog_ret(TINY), cog_ok(BOOL: 0..7 AND == `testGetMotorCog()`-1), board(tok 7 `REV_A` `REV_B` `UNKNOWN`), board_enum(TINY), ready(BOOL), ready_ms(SMALL), off_neg(TINY), off_pos(TINY), missed(SMALL), illegal(SMALL), zero_x10(MID, floated zero-command sense_i mean, 200 x 5 ms, same lifetime), ph_x10(MID, floated u+v+w mean), why | 264 |
| `BM-SSTART` (steering start) | seq, seg, life, motor(`BOTH`), ret(TINY), ret_ok(BOOL: 0..7), l_st(tok 10), r_st(tok 10), ready_ms, l_neg, l_pos, r_neg, r_pos(TINY), l_ig(SMALL), r_ig(SMALL), board(`NA`), why(`NO_PASSTHROUGH`) | 240 |
| `BM-RUNG` | seq, seg, life, rid(SMALL), rung(TINY), motor, incre(BIG), result(tok 14 `OK` `FAULT` `STEADY_TIMEOUT` `WINDOW_TIMEOUT` `NO_COG` `ABORT_I` `SKIPPED`), off_neg, off_pos, steady_ms(SMALL), win_ms(SMALL), ticks(MID), rate_x10(MID), pred_x10(MID), why | 262 |
| `BM-RUNG2` | seq, rid, motor, incre, zero_x10(MID), i_x10(MID), inet_x10(MID), i_min(SMALL), i_max(SMALL), ph_x10(MID), duty(SMALL), duty_pk(SMALL), duty_max(SMALL), err(TINY), err_pk(TINY), n(SMALL), why | 269 |
| `BM-RUNG3` | seq, rid, motor, incre, missed_d(SMALL), illegal_d(SMALL), hw_ticks(MID), hw_skip(SMALL), amps_x10k(MID, mean `getCurrent()` over the window), rs_impl(SMALL, `i_x10 x 1_000 / amps_x10k`), late(SMALL), skipped(SMALL), clamps(SMALL), idle_up(BOOL, any sample of the idle wheel `up`), idle_i(SMALL), why | 270 |
| `BM-LIVE` | seq, rid, motor, incre, up_all(BOOL), ticks(MID), i_min, i_max, frozen(BOOL i_min == i_max), rpm(SMALL, `testGetRpm()`), rate_x10(MID), hb_ok(BOOL instrument heartbeat advanced), why | 203 |
| `BM-CLOCK` | seq, motor, clkfreq(BIG), adc_fram(SMALL), frame_cnt(SMALL), dead_gap(TINY), exp_fram(SMALL), fram_ok(BOOL), why(`UNSWEPT_CLOCK` when CLK_FREQ is not 200/270/300 MHz) | 159 |

`zero_x10`, `inet_x10 = i_x10 - zero_x10` use the zero read in the same driver lifetime (PL-32,
`DOCs/PUNCH-LIST.md:847-907`). `exp_fram` is the frame count DERIVED from `isp_bldc_motor.spin2:310`
at the compiled clock: 4_545 / 6_136 / 6_818 (study `:208-212`; MEASURED 6_136 at
`debug_260912-153807.log:25`).

### 3.4 Trace records

| Tag | Fields in order | Worst case |
|---|---|---|
| `BM-TRACE` (wheel) | seq, tid, seg, life, motor, cause(tok 9 `STOPCMD` `STOPCOG` `FAULT` `ESTOP` `RAMP`), incre, off_neg, off_pos, req_mode(tok 5 `FLOAT`/`BRAKE`, what was requested), ramp_inc(MID, read back), period_us(SMALL), decim(TINY), pre(SMALL), why | 233 |
| `BM-STRACE` (steering; primary motor is LEFT, `o_` fields are RIGHT) | seq, tid, seg, life, motor(`BOTH`), cause(tok 9 `DISTANCE` `BRAKEHAND` `FLOOR`), l_pwr(TINY), r_pwr(TINY), dir(TINY), req_mode, period_us, decim, pre, why | 200 |
| `BM-TS` (one stored sample) | seq, tid, k(SMALL, stored-sample index), lt(BOOL late), pos(MID, relative to k=0), hw(MID, relative), i(SMALL mV), ph(SMALL mV sum), d(SMALL duty), e(TINY err), st(tok 10), flt(BOOL), up(BOOL), ig(SMALL, integrity events since k=0), o_pos(MID), o_hw(MID), o_i(SMALL), o_up(BOOL), why(`NO_COG` when `up` or `o_up` is FALSE; the flags say which) | 241 |
| `BM-TRACE-END` | seq, tid, stored(SMALL), emitted(SMALL), ksum(MID, sum of emitted k, clamped), mark_k(SMALL), late, skipped(SMALL), lost_head(SMALL), dropped(SMALL), end(tok 10 `REST` `TIMEOUT` `FAULT` `ABORT` `FROZEN`), rest_k(SMALL), ig_sum(SMALL), o_ig_sum(SMALL), hw_skip(SMALL), why | 265 |

### 3.5 Trace emission rule (volume)

Sample `k` is emitted when any holds: `k < mark_k + TRACE_DENSE_SAMPLES` (250 = 0.5 s after the
mark); `pos` or `hw` differs from the last emitted line; `st`, `flt` or `up` differs from the last
emitted line; `k` mod `TRACE_SPARSE_EVERY` (25 = 50 ms) is 0; or `k` is the first or last stored
sample. `k` is always printed, so time is recovered from `k x period_us` and the late flags.
`emitted` and `ksum` in `BM-TRACE-END` let the analyser prove no emitted line was lost (I8).
DERIVED volume: a 4 s coast at 200 ticks/s is at most 250 + 800 + 80 lines x 241 bytes, about 272 KB,
well under two seconds at 2 Mbaud.

### 3.6 Segment records

| Tag | Fields in order | Worst case |
|---|---|---|
| `BM-FBTRIAL` | seq, tid, motor, trial(TINY), ramp_inc(MID), incre, off_neg, off_pos, result(tok 14), t_ms(SMALL, to AT_SPEED or fault), i_pk(SMALL), duty_pk(SMALL), duty_max(SMALL), dsat(BOOL, `d >= duty_max` at the first `flt` sample), rst(tok 9 `NONE` `RESET` `RESTART` `FAILED`), rst_ms(SMALL), why | 269 |
| `BM-RAMPREST` | seq, motor, min(MID), max(MID), inc(MID), down(MID), ok(BOOL, equals 1_500/200_000/22/50_000 read back), why | 131 |
| `BM-OFFREST` | seq, motor, want_neg(TINY), want_pos(TINY), off_neg, off_pos, ok(BOOL), why | 123 |
| `BM-RECOVER` | seq, seg, tid, motor, incre, off_neg, off_pos, step(tok 8 `RESET` `RESTART`), cleared(BOOL stopped AND not faulted), ms(SMALL), st(tok 10), flt(BOOL), why | 193 |
| `BM-UNRECOV` | seq, seg, tid, motor, incre, off_neg, off_pos, st, flt, up, action(tok 13 `MOTOR_RETIRED`), why | 184 |
| `BM-ABORT` | seq, seg, tid, motor, incre, reason(tok 12 `ABS_CURRENT` `INST_STALLED` `TIME_CAP` `SYNC_PRECOND`), value(BIG), scope(tok 5 `TRIAL` `SEG` `RUN`), why | 153 |
| `BM-OVERSHOOT` | seq, tid, sid, motor(`BOTH`), power(TINY), dist_ft(TINY), tgt(MID, DERIVED target ticks), l_stop(MID, left `pos` delta at the first `SPIN_DN` sample), r_stop(MID), l_rest(MID), r_rest(MID), l_trk(MID, steering `getRotationCount(DRU_HALL_TICKS)` left), r_trk(MID), t_stop(SMALL ms from command to first `SPIN_DN`), l_ig(SMALL), r_ig(SMALL), why | 271 |
| `BM-OUT` (one 100 ms poll of the public API) | seq, tid, sid, motor(`BOTH`), t_ms(SMALL), l_stat(tok 7 `MOVING` `HOLDING` `OFF` `UNKNOWN`), r_stat, l_st(tok 10), r_st, l_flt(BOOL), l_sig(BOOL), r_flt, r_sig, turning(BOOL), l_pwr(TINY), r_pwr(TINY), why | 239 |
| `BM-FLOOR` | seq, tid, sid, motor(`BOTH`), power(TINY), dir(TINY), run_ms(SMALL), answer(tok 8 `LEFT` `RIGHT` `STRAIGHT` `NOMOVE` `NONE`), input(tok 5 `KEY` `MOUSE` `NONE`), l_rate_x10(MID), r_rate_x10(MID), slower(tok 5 `LEFT` `RIGHT` `EQUAL`), stop_by(tok 8 `TIMER` `OPERATOR` `ABORT`), why | 219 |
| `BM-OPER` | seq, prompt(tok 10 `BRAKE_L` `FLOOR`), event(tok 8 `SHOWN` `START` `SKIP` `TIMEOUT` `ANSWER` `DONE`), answer(tok 8), input(tok 5), wait_ms(MID), why | 125 |
| `BM-SEG` | seq, seg, event(tok 5 `BEGIN` `END` `SKIP`), attended(BOOL), items(SMALL), faults(SMALL), unrecov(TINY), ms(MID), why | 140 |

Segment tokens (`seg`, max 8): `PREFLT`, `STOPMODE`, `LIVE`, `LADDER`, `CLOCK`, `FAULTB`,
`OVERSHT`, `OUTSIDE`, `BASELINE`, `POSTFLT`, `FLOOR`.

`BM-OUT`'s `l_stat`/`r_stat` are `steering.getStatus()` (M, `isp_steering_2wheel.spin2:502-507`);
`l_flt`/`l_sig`/`r_flt`/`r_sig` are `testGetFaultStatus()`, which has no side effect
(`:624-639`); `turning` is `isTurning()` (`:870-874`); `l_st`/`r_st` are `testGetDriverState()`
(`:615-622`). All are read by cog 0 into a `OUT_POLLS` (80) x 12-long buffer and emitted after the
window (I1 needs no instrument for a 100 ms poll).

### 3.7 End-of-run records

| Tag | Fields in order | Worst case |
|---|---|---|
| `BM-WATCHDOG` (watchdog cog, on a stall) | seq, ms(SMALL), checkpoint(TINY), cp_tok(tok 10), l_cog(TINY), r_cog(TINY), steer_up(BOOL), inst_state(tok 7), stack_ok(BOOL) | 142 |
| `BM-WATCHDOG2` | seq, then per motor l_st, l_flt, l_duty(SMALL), l_err(TINY), l_i(SMALL), l_pos(MID), and the same six for r_ | 193 |
| `SIGNOFF` | as `DOCs/plans/VISIT-SIGNOFF-DESIGN.md:486`, `bin,DUAL`; builder emitters as `src/test_bench_scan.spin2:4987-5132` | 196 |
| `BM-TRAP` | seq, code(BIG, the top-level trap value), returned(BOOL, `runPart()` reached its end) | 55 |
| `BM-END` | seq, exit(tok 8 `COMPLETE` `ABORTED` `WATCHDOG`), part(tok 5), segs(TINY), last_seg(tok 8), records(MID, the `seq` this record carries), trap_code(BIG), unrecov(TINY), why | 152 |
| (marker) | `debug("DEBUG_END_SESSION")`, quoted, alone (`src/test_bench_scan.spin2:1258-1259`) | -- |

The watchdog cog uses its own builder instance (section 7), so it never touches cog 0's buffer; its
`seq` continues from `logSeq` read once at declaration and marks `BM-WATCHDOG` with that value +1 (the
host tolerates one seq discontinuity only when `BM-WATCHDOG` is present).

---

## 4 · Run sequence

### 4.1 Program loads, in the Visit 2 order (non-negotiable, arbiter context B)

One source file, one segment set per build. The part is chosen at compile time by `bench-run.sh`,
so an unattended load physically contains no operator step and an attended load contains no
unattended motion segment. With no part flag the build prints `part,NONE`, runs no segment, and ends
(the honest fallback for a mistyped `-D`; `pnut-ts` ignores an unknown `-D`, `tools/bench-run.sh:98-104`).

| # | Command | Part flag | Segments | Rig state | Hands |
|---|---|---|---|---|---|
| 1 | `tools/bench-run.sh dual-a` | `DUAL_PART_A` | PREFLT, STOPMODE, LIVE, LADDER | wheels up | none |
| 2 | `tools/bench-run.sh dual-clock 200000000` | `DUAL_PART_CLOCK` | PREFLT, CLOCK | wheels up | none |
| 3 | `tools/bench-run.sh dual-clock 270000000` | same | same | wheels up | none |
| 4 | `tools/bench-run.sh dual-clock 300000000` | same | same | wheels up | none |
| 5 | `tools/bench-run.sh dual-b` | `DUAL_PART_B` | PREFLT, FAULTB, OVERSHT | wheels up | none |
| 6 | `tools/bench-run.sh dual-brake` | `DUAL_PART_BRAKE` | OUTSIDE | wheels up | **Stephen: one hand-brake** |
| 7 | `tools/bench-run.sh dual-c` | `DUAL_PART_C` | PREFLT, BASELINE, POSTFLT | wheels up | none |
| 8 | `tools/bench-run.sh dual-floor` | `DUAL_PART_FLOOR` | FLOOR | **wheels down** | **Stephen: brief (about 2 s) wheels-down observation** |

Every load also carries `-D BENCH_CFG -D BENCH_QUIET` (section 6). The three clock builds are
produced by `bench-run.sh`'s existing `CLK_FREQ` patch-and-restore (`tools/bench-run.sh:172-202`);
the file must therefore contain exactly one line matching `CLK_FREQ = <digits>`. The `dual-clock` tier
refuses to run without a `clkfreq` argument (section 9). Each load is its own log; each ends with
`BM-END` and `DEBUG_END_SESSION`.

**Every load starts the same way:** watchdog cog (`BM-WDSTART`), header records, instrument cog
(`BM-INST event,START`), then the part's segments, then shutdown (both wheels and the steering object
`stop()`ped), `INST_CMD_EXIT` + ack + `cogstop` (`BM-INST event,STOP`), watchdog `cogstop` (only when
`wdDeclaring` is FALSE, `src/test_bench_scan.spin2:1243-1265`), SIGNOFF records, `BM-TRAP`, `BM-END`,
marker.

### 4.2 Recovery policy (all segments)

1. A fault seen by the instrument ends that trial's wait. The capture is frozen and every side effect of
   the trial is restored and read back (I11) **before** any check.
2. `testResetFault()` alone (it issues the zero command itself, `isp_bldc_motor.spin2:1129-1155`,
   PL-28 fix). Cleared = `isStopped()` AND NOT `isFaultSignal()`. `BM-RECOVER step,RESET`.
3. If not cleared: `stop()`, rest `RESTART_REST_MS` (500), `start()`, wait ready. `BM-RECOVER step,RESTART`.
4. If still not cleared: `BM-UNRECOV action,MOTOR_RETIRED`; that motor's remaining trials in this load
   are emitted as `SKIPPED`/`NOMEAS why,MOTOR_RETIRED`; the other motor and later segments continue.
   Never ends the session.
5. After any fault, `FAULT_COOL_MS` beat-polled: 5_000 (scan, `src/test_bench_scan.spin2:374`), except
   FAULTB, which uses `FAULT_TRIAL_COOL_MS` = 10_000 (open question Q3).
6. Run caps per load: `RUN_TIME_CAP_S` (part A 1_500, clock 300, B 1_200, C 900, attended 600),
   `RUN_FAULT_CAP` 40, and the absolute current abort (section 2.8).

### 4.3 Watchdog beat contract

`beat(CP_*)` exactly as the scan (`src/test_bench_scan.spin2:5551-5572`), including the park once the
watchdog declares. Checkpoints:

`CP_INIT, CP_INST_ACK, CP_LOOP_READY, CP_LOOP_ZERO, CP_LOOP_ATSPEED, CP_LOOP_SETTLE, CP_LOOP_WINDOW,
CP_LOOP_CAPTURE, CP_LOOP_REST, CP_LOOP_STOPPED, CP_LOOP_COOL, CP_LOOP_DRAIN, CP_LOOP_OPER,
CP_LOOP_POLL, CP_LIB_START, CP_LIB_STOP, CP_LIB_COMMAND, CP_LIB_QUERY, CP_LIB_OFFSETS, CP_LIB_RAMP,
CP_LIB_HOLD, CP_LIB_ESTOP, CP_LIB_RESETFAULT, CP_LIB_STEER_START, CP_LIB_STEER_DRIVE,
CP_LIB_STEER_STOP, CP_LIB_STEER_QUERY, CP_EMIT, CP_PANEL`

- Every loop beats once per pass; every pass waits `SAMPLE_MS` (5 ms) or, in operator loops,
  `OPER_POLL_MS` (50 ms, under PC_KEY's ~100 ms latch, `DISPLAY-PATTERNS-builders-guide.md:206`).
- Every library call is bracketed by the same `CP_LIB_*` before and after.
- Longest legitimate un-beaten gaps (DERIVED): `testResetFault()` <= 2_030 ms
  (`src/test_bench_scan.spin2:701-702`); `steering.driveForDistance()` about 400 ms, two
  `resetTracking()` `waitms(200)` (`isp_steering_2wheel.spin2:229-230`, `:320`; `isp_bldc_motor.spin2:522`);
  `steering.start()` `waitms(100)` (`isp_steering_2wheel.spin2:141`). All under `WD_STALL_MS` = 4_000.
- `steering.driveAtPower()` ends in `SyncStatus()`, an unbounded busy wait
  (`isp_bldc_motor.spin2:1442-1446`; PL-49 F-6), which never returns while a driver sits in
  `DCS_ESTOP` because that path exits before reading the command (`isp_bldc_motor.spin2:2139-2146`).
  Construction: every steering drive call is preceded by a check that both wheels are `up` and neither
  is `DCS_ESTOP`; a failed check emits `BM-ABORT reason,SYNC_PRECOND` instead of calling. The watchdog
  is the backstop.
- Every `waitms()` argument is a CON at or under `WAITMS_MAX_MS = $8000_0000 +/ (CLK_FREQ / 1000)`
  (7_158 ms at 300 MHz, 7_953 at 270, 10_737 at 200): `SAMPLE_MS` 5, `OPER_POLL_MS` 50,
  `INST_EXIT_POLL_MS` 50, `WD_POLL_MS` 250, `WD_IDLE_MS` 1_000. Every longer wait is a beat-polled loop.
- On a stall the watchdog stops `wheelL`, `wheelR` and `steering` (never through a `beat()` wrapper),
  then emits `BM-WATCHDOG`, `BM-WATCHDOG2`, the part's `R14-DUAL-NOSTALL-*` as FAIL, `BM-END exit,WATCHDOG`
  and the marker. It never commands the instrument (not its value to write, 2.4).

### 4.4 Segments

**PREFLT** -- every motion load. *Finding:* none (proves the rig). *Commands:* per wheel, the scan's
preflight: start, `PREFLIGHT_INCRE` (18_375_000) for 700 ms, zero, wait stopped, stop
(`src/test_bench_scan.spin2:1448-1477`), with the instrument armed on that wheel. *Measures:* tick and
`hwPos` deltas; `BM-START`, and `BM-PREFLT` (seq, motor, incre, ticks(SMALL), hw_ticks(MID), moved(BOOL),
why; worst case 124 bytes). *Fail:* either wheel moves 0 ticks -> run abort (`BM-ABORT scope,RUN`), no
segment runs. ~5 s.

**STOPMODE** -- part A, first (T1-1). *Findings:* C-4 (published decel data), S-9a baselines (float,
brake, pins-cleared). *Commands:* per motor (LEFT, RIGHT) x speed (QTR 36_750_000, HALF 73_500_000) x
sign (NEG, POS) x rep (`STOPMODE_REPS` = 2): one driver lifetime, zero read, then three traces in this
order, each spin-up -> `DCS_AT_SPEED` (<= 4 s) -> settle 1_000 ms -> mark -> event -> capture until rest
(`pos` and `hwPos` unchanged for `REST_CONFIRM_MS` 300) or `TRACE_MAX_SAMPLES` (8.0 s):
(1) `cause STOPCMD, req_mode FLOAT`: `holdAtStop(FALSE)`, `stopMotor()`;
(2) `cause STOPCMD, req_mode BRAKE`: `holdAtStop(TRUE)` issued **before** spin-up, `stopMotor()`, then
`holdAtStop(FALSE)` once frozen;
(3) `cause STOPCOG, req_mode FLOAT`: `stop()` (cogstop + pinclear, `isp_bldc_motor.spin2:128-162`); the
coast is measured by `hwPos` only, since `pos` freezes. That ends the lifetime.
*Measures:* `BM-TRACE`, `BM-TS`, `BM-TRACE-END` per trace. 48 traces, one start per lifetime (16 starts,
never closer than 500 ms apart). *Unattended.* ~9 min.

**LIVE** -- part A (T1-2, W). *Commands:* per motor one lifetime with `startSenseCog()` (its debug is
compiled out, I5); positive sign rungs QTR, HALF, 110_250_000; each AT_SPEED -> settle 1_500 ms (the
~1 s rpm window fills, `isp_bldc_motor.spin2:1221-1232`) -> 1_000 ms instrument window -> `testGetRpm()`.
*Measures:* `BM-LIVE`. *Unattended.* ~1 min.

**LADDER** -- part A (T1-3; C-1, C-5's duty question, S-3 linearity, C-6 data; T1-11 matched motors).
*Commands:* per motor x sign (NEG then POS), one lifetime, zero read, then ascending rungs from the
`LADDER` DAT table, printed first as `BM-LADDER`: 5, 10, 20, 40, 60, 80, 100, 120, 140, 147 x 10^6, plus
probe rungs 155 and 165 x 10^6 (`probe,TRUE`, open question Q2; `LADDER_PROBES` = 0 removes them).
Each rung: command -> AT_SPEED (<= 6_000 ms) -> settle 500 ms -> 1_000 ms window, during which cog 0
also reads `getCurrent()` every 20 ms (the only library call in any window; bracketed; it has no debug,
`isp_bldc_motor.spin2:750-765`) -> freeze -> drain -> emit `BM-RUNG`, `BM-RUNG2`, `BM-RUNG3`. Two
consecutive faulted rungs end that sign's ladder (`LADDER_FAULT_STOP` = 2); the rest print
`result,SKIPPED why,LADDER_STOPPED`. Faults recover per 4.2. *Unattended.* ~4 min.

**CLOCK** -- the three clock loads (T1-4, S-3 by an independent route). *Commands:* per motor x sign,
one lifetime: `testGetDriveConstants()` -> `BM-CLOCK`; zero; one rung at 75_000_000 (plan `:790`) ->
`BM-RUNG/2/3`. *Measures:* `adc_fram` against 4_545/6_136/6_818 and `sense_i` net at a physically
identical speed. *Unattended.* ~1 min per load.

**FAULTB** -- part B (T1-7; C-5, Z, S-1). *Commands:* per motor x sign, one lifetime; five trials
`ramp_inc` in {22, 100, 500, 2_000, 10_000} ascending (plan `:917-918`). Trial: wheel stopped ->
`setRampingValues(1_500, 200_000, inc, 50_000)` read back -> arm -> mark -> command 110_250_000 (75 %)
from standstill -> capture until AT_SPEED + 500 ms, fault, or `FB_TIMEOUT_MS` 6_000 -> freeze -> restore
`setRampingValues(1_500, 200_000, 22, 50_000)` and read back (`BM-RAMPREST`, I11; defaults DERIVED
`isp_bldc_motor.spin2:355-358`) -> recovery 4.2 if faulted -> zero, wait stopped -> cool 10_000 ms.
*Measures:* `BM-TRACE cause,RAMP`, `BM-TS`, `BM-TRACE-END`, `BM-FBTRIAL`; S-1 is not measured
(`NO_TEMP_SENSOR`). Current at fault comes from the trace's `i` (plan `:922`). *Unattended.* ~7 min.

**OVERSHT** -- part B (T1-8; C-3). *Commands:* `wheelL.stop()`, `wheelR.stop()` first (shared pin claims,
PL-18); `steering.start(LEFT_TEST_BASE, RIGHT_TEST_BASE, PWR_18p5V, BRD_AUTO_DET, BRD_AUTO_DET)` ->
`BM-SSTART`; `holdAtStop(FALSE)`; instrument source STEER; for distance 2 ft and 10 ft x 2 reps:
precondition (4.3) -> mark -> `driveForDistance(d, d, DDU_FT)` -> wait both STOPPED + 500 ms or 12_000 ms
-> freeze -> `BM-STRACE`, `BM-TS`, `BM-TRACE-END`, `BM-OVERSHOOT`. `tgt` is DERIVED with the steering
object's own arithmetic: `circInMM_x10` 5_187, `tickInMM_x100` = (51_870 + 45) / 90 = 576
(`isp_steering_2wheel.spin2:149-153`), 2 ft -> 60_960 / 576 = 105 ticks, 10 ft -> 304_800 / 576 = 529
(`:340-342`). `steering.stop()` at the end. *Unattended.* ~2 min.

**OUTSIDE** -- attended load 6 (T1-9; M, AF, S-5, Z). *Precondition act:* Stephen at the rig, platform on
blocks. *Commands:* panel prompt `BRAKE_L` (section 8) and wait for START (<= 120 s, else
`BM-OPER event,TIMEOUT`, segment NOMEAS, no motion). Then steering start, `holdAtStop(FALSE)`, arm
instrument (decimate 10, 20 ms), precondition, `driveAtPower(50, 50)`, both AT_SPEED (<= 6 s), settle
1 s, panel `BRAKE NOW`; wait for the LEFT fault flag (<= 30 s; SKIP honoured). On the fault: mark, panel
`RELEASE`, then cog 0 polls the public API every 100 ms into the `BM-OUT` buffer: 5_000 ms untouched
(S-5's 3 s latch clear, `isp_steering_2wheel.spin2:527-548`, runs from the sense task at
`:970`, `:1061-1069`); then Z step 1, `driveAtPower(50, 50)` again, same power, 2_000 ms; then Z step 2,
`stopMotors()`, both STOPPED (<= 3 s), `driveAtPower(50, 50)`, 2_000 ms; then `stopMotors()`, stopped,
freeze, `steering.stop()`. *Measures:* `BM-STRACE cause,BRAKEHAND`, `BM-TS`, `BM-TRACE-END`, up to 100
`BM-OUT`, `BM-OPER`. *Hand-brake is the only physical act.* ~2 min.

**BASELINE** -- part C, before POSTFLT, same load (I7). *Commands:* per motor x sign, HALF, one lifetime:
STOPMODE conditions (1) and (2) only. 8 traces. ~2 min.

**POSTFLT** -- part C (T1-1 d and e; S-9a). *Commands, per motor:*
- *Fault:* NEG sign, HALF, `req_mode` FLOAT then BRAKE (`holdAtStop` before spin-up): AT_SPEED -> settle
  1 s -> read offsets `want_neg/want_pos` -> arm -> mark -> `testSetFwdRevIndep(FAULT_PROVOKE_NEG_DEG, want_pos)`
  with `FAULT_PROVOKE_NEG_DEG` = 3 (MEASURED to fault on both motors' negative legs at quarter speed,
  `DOCs/plans/VISIT-SIGNOFF-DESIGN.md:1225-1226`; at half speed the usable window is narrower,
  sprint plan `:350-351`) -> capture until rest or 8 s -> freeze -> restore offsets and read back
  (`BM-OFFREST`) -> `holdAtStop(FALSE)` -> recovery 4.2. No fault within 2_000 ms: restore, `stopMotor()`,
  trace `why,NO_FAULT`.
- *E-stop:* both signs, HALF, `req_mode` FLOAT then BRAKE: AT_SPEED -> settle -> arm -> mark ->
  `emergencyCutoff()` -> capture until rest or 8 s -> freeze -> `clearEmergency()` -> `holdAtStop(FALSE)`
  -> zero, wait STOPPED. No sense cog runs on these instances, so S-4's self-cancel cannot intervene
  (`isp_bldc_motor.spin2:1799-1805` runs only in the sense task).

*Measures:* `BM-TRACE cause,FAULT` / `cause,ESTOP`, `BM-TS`, `BM-TRACE-END`, `BM-OFFREST`, `BM-RECOVER`.
12 traces. *Unattended.* ~3 min.

**FLOOR** -- attended load 9 (T2-1; AC). *Precondition act:* platform lowered to the floor, space clear.
*Commands:* panel prompt `FLOOR`, START (<= 120 s); steering start; `holdAtStop(FALSE)`; arm (decimate 10);
precondition; `driveDirection(50, 50)`; poll every 50 ms for `FLOOR_RUN_MS` 2_000 or STOP (click or
space); `stopMotors()`; wait stopped; freeze; panel asks LEFT / RIGHT / STRAIGHT / DID NOT MOVE
(<= 120 s); `steering.stop()`. *Measures:* `BM-STRACE cause,FLOOR`, `BM-TS`, `BM-TRACE-END`, `BM-FLOOR`,
`BM-OPER`. *The observation is the only physical act.* ~2 min.

---

## 5 · Verdicts

### 5.1 Who judges what

- **The P2 emits SIGNOFF verdicts** only for properties of this harness and of the library paths it
  exercises (the construction invariants of section 1, plus fault recovery and detection). They follow
  `DOCs/plans/VISIT-SIGNOFF-DESIGN.md` §B exactly, `bin,DUAL`, and are emitted once, on cog 0's end path
  after both wheels, the steering object and the instrument are stopped.
- **The analyser «#3509» judges the findings** (C-1, C-3, C-4, C-5, C-6, S-3, S-5, S-9a, M, Z, AC, the
  field question). It never prints a `SIGNOFF` (`VISIT-SIGNOFF-DESIGN.md:838-851`). Its inputs are the
  measurement records of section 3; its thresholds and their sources are fixed in 5.3 before the visit.
- **Cell ids carry the part** (`-A`, `-K`, `-B`, `-H`, `-C`, `-F`). Reason: the collation lets only
  the latest build declaring a cell speak (`tools/signoff-collate.py:950-956`), and the part builds are
  different images, so a shared cell id would let part C's log supersede a part A FAIL. The three clock
  builds share `-K` deliberately: every one of their logs speaks, and any FAIL fails the cell.

### 5.2 SIGNOFF cells -- manifest row 14, task 3508, visit_owed 2, status OWED

A cell prints PASS only when measured and in `lo..hi` (or TRUE), FAIL when measured otherwise, NOMEAS
with `measured,NA` and `n,0` when not measured. NOT_BUILT is what the host reports for a cell no log
declares (a part not run).

| Cell | Part | crit | units | lo | hi | min_inst | Measured as | NOMEAS when | FAIL fires on (decision 19) |
|---|---|---|---|---|---|---|---|---|---|
| `R14-DUAL-NOSTALL-A` `-K` `-B` `-H` `-C` `-F` | each | `ENDED_BY_COG0` | BOOL | TRUE | TRUE | 1 | cog 0 reached its end path; the watchdog's stall path prints FALSE (scan pattern, `VISIT-SIGNOFF-DESIGN.md:1128-1130`) | never | a cog-0 stall: scan run 5/6's silent stop (MEASURED, `VISIT-1-RESULTS.md:255-273`) |
| `R14-DUAL-DBGMASK-A` `-K` `-B` `-H` `-C` `-F` | each | `QUIET_MASKS` | BOOL | TRUE | TRUE | 1 | compiled `user.MOTOR_DBG_MASK == DECOD DBGCH_ERROR \| DECOD DBGCH_WARNING` AND the same for `STEER_DBG_MASK` | never | a load built without `-D BENCH_QUIET`, or with it mistyped: the bench masks then include LIFECYCLE..TEST (`src/isp_bldc_motor_userconfig_bench.spin2:78-79`), I5 no longer holds, and the cell prints FALSE |
| `R14-DUAL-INSTLIVE-A` | A (LIVE) | `INST_LIVE` | BOOL | TRUE | TRUE | 2 (per motor) | at the QTR rung: every sample `up`, driver ticks >= `LIVE_MIN_TICKS` (49, half the MEASURED 98.2 ticks/s, `VISIT-1-RESULTS.md:90`), `i_min <> i_max`, instrument heartbeat advanced, and `|ticks - hw_ticks| <= 2` | the rung did not reach AT_SPEED | the instrument reading a stopped instance (frozen block: i min = max, MEASURED `debug_260912-153807.log:460`, PL-21), reading the wrong source, or a stalled instrument |
| `R14-DUAL-IDLEFLT-A` | A | `IDLE_WHEEL_UP` | COUNT | 0 | 0 | 2 | motor-frame captures (STOPMODE, LADDER) in which any sample shows the idle wheel `up` | no capture ran on that motor | a restart that omits stopping the other side (what `restartSide()` exists to prevent, `src/test_bench_scan.spin2:1522-1532`) |
| `R14-DUAL-REVB-A` | A | `STARTS_NOT_REVB` | COUNT | 0 | 0 | 2 | wheel starts whose `getBoardType()` is not `REV_B` | no start on that motor | detection misreading after a restart: 4 of 4 Rev A before «#3500» (MEASURED, `CHAR-RUN-EVALUATION.md:115-121`) |
| `R14-DUAL-INTEG-A` | A | `MISSED_ILLEGAL_SUM` | COUNT | 0 | 0 | 2 | missed + illegal over every start and rung | no start | COVERAGE: counters that never count cannot fail it (as R3-SCAN-INTEG) |
| `R14-DUAL-TRACES-A` `-B` `-C` | A, B, C | `TRACE_DATA_LOST` | COUNT | 0 | 0 | 1 | traces whose `lost_head` reaches `mark_k`, or with `dropped > 0` | the part ran no trace | a capture that outlives the ring or a freeze issued late: a construction defect in the harness, not in the library |
| `R14-DUAL-CLKFRAME-K` | CLOCK | `FRAME_AT_CLOCK` | BOOL | TRUE | TRUE | 2 (per motor) | `adc_fram == exp_fram` for the compiled `CLK_FREQ` | `CLK_FREQ` is not 200/270/300 MHz (`UNSWEPT_CLOCK`) | COVERAGE: `adc_fram` and `exp_fram` derive from the same clock; the cross-clock proof is the analyser's (5.3) |
| `R14-DUAL-RSTPROV-B` `-C` | B, C | `RESET_UNCLEARED` | COUNT | 0 | 0 | 2 (per motor) | faults in the part not cleared by `testResetFault()` alone; `n` = faults | no fault on that motor | the pre-67d11f6 `testResetFault()`, which sent no zero command and stayed FAULTED for 2_030 ms with a non-zero command set (`VISIT-SIGNOFF-DESIGN.md:281`, PL-28) |
| `R14-DUAL-RAMPREST-B` | B | `RAMP_RESTORED` | BOOL | TRUE | TRUE | 2 (per motor) | after the last trial, `getRampingValues()` reads 1_500 / 200_000 / 22 / 50_000 | FAULTB did not run on that motor | a trial exit path (fault, timeout, abort) that skips the restore (I11) |
| `R14-DUAL-OFFREST-C` | C | `OFFSETS_RESTORED` | BOOL | TRUE | TRUE | 2 (per motor) | after every provoked-fault trial, `testGetFwdRevIndep()` equals the pair read before it | no fault trial ran on that motor | a trial exit path that skips the offset restore (I11) |
| `R14-DUAL-BRAKEFLT-H` | BRAKE | `BRAKE_FAULT_SEEN` | BOOL | TRUE | TRUE | 1 | the instrument saw the LEFT fault flag after `BRAKE NOW` | START or brake timed out, or SKIP | COVERAGE: proves the attended path ran |
| `R14-DUAL-FLOORANS-F` | FLOOR | `OPERATOR_ANSWERED` | BOOL | TRUE | TRUE | 1 | an answer was recorded after the run | START or answer timed out | COVERAGE: proves the attended path ran |

`R14-DUAL-DBGMASK-*` is a harness cell. It shows the quiet build was compiled; it is not «#3507»'s own
certification, which this design does not take on (Q12).

### 5.3 Analyser verdicts («#3509») -- data, rule, threshold source

Every verdict is refused, naming the last good `seq`, when the log fails I8: a `seq` gap other than the
one allowed before `BM-WATCHDOG`, a trace without a consistent `BM-TRACE-END` (`emitted` and `ksum`
recomputed), a child record without its parent header, or no `BM-END`. The collation's
COMPLETE/TRUNCATED reader is imported, not copied (`VISIT-SIGNOFF-DESIGN.md:848-850`). A rung or trace
with more than 10 % late samples is `DEGRADED` and cannot confirm or withdraw anything.

| Finding | Data | Rule | Threshold source |
|---|---|---|---|
| **S-9a** (post-fault / post-e-stop stop) | part C: `BM-TRACE cause,FAULT` and `cause,ESTOP` against `cause,STOPCMD req_mode,FLOAT` and `req_mode,BRAKE` for the same motor, sign and speed in the same log | per trace: time to rest (`(rest_k - mark_k) x period_us`), revolutions to rest (`hw` delta / 90), and a deceleration fit over the first 500 ms after `mark_k`. `MATCHES_FLOAT` / `MATCHES_BRAKE` when within 2x the rep-to-rep spread of that baseline and outside the other's; `BETWEEN` otherwise; `NOMEAS` on `why,NO_FAULT` | the run's own baselines (I7); no fixed number |
| **C-4** (published decel data) | part A STOPMODE, 2 reps | table per motor x sign x speed x mode: deceleration (ticks/s^2), time to rest (ms), revolutions to rest, from the stated `pred_x10` speed; rep spread printed beside each | measured; publication in `DRIVE-OBJECTS.md` is «#3514»/«#3515» |
| **W** (telemetry liveness) | `BM-LIVE` | `rpm - rate_x10 x 60 / 900` within +/-2 rpm | `VISIT-SIGNOFF-DESIGN.md:334-340` (A.5-c) |
| **C-1** (speed law) | `BM-RUNG` non-probe rungs, result OK | ratio `rate_x10 / pred_x10` per rung, both signs, both motors; departure rung = first OK rung outside the tolerance, or first faulted rung | plan T1-3 `:758-759` gives 2 %; **Q9**: existing evidence already sits 4-5 % below the formula at quarter and half speed |
| **real ceiling** (PL-26) | `BM-RUNG` incl. probe rungs | per motor x sign: highest OK rung and first fault rung, against 147_000_000 | `isp_bldc_motor.spin2:1413` |
| **C-5 gate** | `BM-RUNG2` at the departure rung; `BM-FBTRIAL`; `BM-TS` `d`, `e` over the last 100 ms before the first `flt` | `GATE_VALID` when `dsat` TRUE and `abs(e)` rising over that span; `GATE_CHANGES` when a fault arrives with `dsat` FALSE; `URGENT` when ramp_inc 22 faults unloaded | plan T1-7 `:925-934` |
| **Z** | `BM-OUT` after Z step 1 and step 2 | CONFIRMED when the braked wheel is still FAULTED after the same-power re-command and runs only after the stop + re-command | audit Z `:493-507` |
| **M** | `BM-OUT` | CONFIRMED when any poll shows `l_stat MOVING` with `l_st FAULTED` | audit M `:73-99` |
| **S-5** | `BM-OUT` `l_sig` | CONFIRMED when `l_sig` goes TRUE -> FALSE between 2_875 and 3_250 ms after the fault mark with no clearing call made by the harness (none exists in that window) | 3_000 ms, `isp_steering_2wheel.spin2:531`; +/-125 ms sense period, `:1003` |
| **AF** | none on the bench | reported as a source property, not a bench verdict | audit AF `:102-124` |
| **S-3** (clock route) | three `dual-clock` logs: `BM-CLOCK`, and `BM-RUNG2 inet_x10` at 75_000_000 per motor x sign | `adc_fram` ratios 270/200 = 1.350 and 300/270 = 1.111 (arbiter-fixed); `inet_x10` ratios across clocks within +/-15 % of 1.000 -> `FIX_CONFIRMED`; tracking 1.350/1.111 -> `DEFECT_PRESENT` | 1.350/1.111 arbiter context C; +/-15 % `VISIT-SIGNOFF-DESIGN.md:346-364` |
| **Current linearity** | `BM-RUNG2`, `BM-RUNG3` along the ladder | per motor x sign: `inet_x10` non-decreasing over OK rungs (a dip within the rung's own sample spread allowed); `rs_impl` in 135..165 at every rung; rungs above 8_400 mV x10 (5.6 A x 150) labelled `EXTRAPOLATED`; any `i_max >= 3_250` labelled `NEAR_RAIL` | 135..165 `SIGNOFF-MANIFEST.tsv` R2-CHAR-ISCALE; 5.6 A the Pass 1 anchor, `CHAR-RUN-EVALUATION.md:104-111` |
| **C-6** (bus ratio from load sag) | `BM-RUNG2 ph_x10`, `inet_x10`, `duty` over OK rungs >= 20_000_000; `BM-BUILD rwire_mohm`, `pack_mV` | drift `d = (max - min) / mean` of `ph_x10`; wiring-drop bound `B = I_max x rwire_mohm / pack_mV` with `I_max = max inet_x10 / 1_500` amps. `d <= B` -> **INCONCLUSIVE, naming the missing measurement: one DMM reading across the board's own supply terminals at a high rung**. `d > B`: remove the pack-sag estimate `I x R_pack` (R_pack about 83 mOhm, DERIVED from MEASURED 20.43 V at rest and 19.97 V at 5.56 A, `CHAR-RUN-EVALUATION.md:32-40`, a different pack state, so an estimate) and report `CONSISTENT` if the residual is within `B`, else `DEPARTS`. Never `WITHDRAWN` without a board-side voltage reading (`NO_EXTERNAL_V`) | bound: plan `:878-887`; 20 mOhm plan `:881` |
| **C-3** | `BM-OVERSHOOT` | overshoot `l_rest - tgt` ticks x 5.76 mm (576 / 100); latency part `l_stop - tgt`; CONFIRMED when total is within +/-20 % of the prediction | about 1.2 m at 75 %, study `:696-703`; +/-20 % plan `:962-964` |
| **AC** | `BM-FLOOR` | three sources compared: the observed `answer`; the telemetry (`slower` wheel is the side it turns to); the code's expectation, direction > 0 reduces the LEFT motor (`isp_steering_2wheel.spin2:848-849`) -> turns left. Reports which of code comment, `DRIVE-OBJECTS.md` and `README.md` is wrong | audit AC `:443-470` |
| **S-1** | none | `NOMEAS NO_TEMP_SENSOR` | scope ruling |
| **Regen into the pack** | none | `NOMEAS NO_EXTERNAL_I` | scope ruling |

---

## 6 · Debug budget

### 6.1 Bench masks

The quiet set is **ERROR + WARNING** for both objects, selected by `-D BENCH_QUIET` inside the bench
config's `CON { DEBUG output }` block (`src/isp_bldc_motor_userconfig_bench.spin2:73-79`):

```spin2
CON { DEBUG output }

#ifdef BENCH_QUIET
    ' motion harness (task 3508): no debug() reachable from any cog a library stop() can end
    MOTOR_DBG_MASK = DECOD DBGCH_ERROR | DECOD DBGCH_WARNING
    STEER_DBG_MASK = DECOD DBGCH_ERROR | DECOD DBGCH_WARNING
    BENCH_QUIET_BUILD = TRUE
#else
    MOTOR_DBG_MASK = <unchanged line 78>
    STEER_DBG_MASK = <unchanged line 79>
    BENCH_QUIET_BUILD = FALSE
#endif
```

- **Why a flag, not a change to the existing masks:** the scan, char, Tier 0 and detection binaries
  read the same bench config, and their logs are compared against earlier runs (the detection diff,
  `VISIT-SIGNOFF-DESIGN.md:636-684`). The `#else` branch keeps their output byte-for-byte.
- **Why ERROR + WARNING and not FAULT too:** FAULT is exactly the channel the sense tasks print on
  (I5). Every fault this harness cares about is recorded by the instrument instead.
- **Proof in the log:** `BM-BANNER quiet,mdbg,sdbg` and `R14-DUAL-DBGMASK-*`. A `pnut-ts` that ignores
  the flag produces `quiet,FALSE` and a FAIL, never a quietly noisy run.

### 6.2 Record count against the ceiling

**Ceiling:** 255 DEBUG records per compiled program (sprint plan `:709-711`; restated
`DOCs/plans/DEBUG-CHANNELS-DESIGN.md:178`; "the per-top total ... «#3508» measures it for its own
binary", `:192`).

**Library contribution under the quiet masks (DERIVED from the channel map):** motor ERROR 17 +
WARNING 3 = 20 (`DEBUG-CHANNELS-DESIGN.md:125-126`); steering ERROR 10, WARNING 0 (`:146`). Total 30
if each object image is counted once; 90 if each of the four motor instances (`wheelL`, `wheelR`, the
steering object's two) were counted separately (UNVERIFIED 11.9). Either way far under the ceiling.

**Harness contribution (a bound phase 2 replaces with the real count):** one cog-0 emit statement
(`emitRecord()`), one watchdog emit statement, two `DEBUG_END_SESSION` statements, one panic line, and
the panel's statements (one `PLOT`, five `LAYER`, one `CROP 1`, one `UPDATE`, at most 12 parameterised
`CROP`s, one `PC_KEY`, one `PC_MOUSE`): at most 27. Worst case 90 + 27 = 117 of 255.

**Counting method, phase 2:** count every `debug(` and `debug[` statement in `src/test_bench_dual.spin2`
and `src/isp_bench_log.spin2` (the latter must have none) by reading the file; add the library's enabled
statements from the channel map for the quiet masks; record the table in the file header beside the
number the compiler accepted. A build that exceeds the ceiling does not compile, so `tools/build-check.sh`
green is the confirmation, not the estimate.

---

## 7 · Shared code

### 7.1 `src/isp_bench_log.spin2` -- the PL-17 extraction

A constants-free object (no `OBJ user`, so it compiles under every config block, the build gate's
library rule), with no `debug()` statement and all state in `VAR`, so each instance owns its own buffer.
Two instances in the harness: `log` (cog 0) and `wdLog` (watchdog cog). That removes the watchdog mirror
copies the scan needed (`src/test_bench_scan.spin2:728-739`, `:779-783`).

| Method | Signature | Body transcribed from |
|---|---|---|
| begin | `PUB begin(pTag)` | `lineReset()` + `lineAddText(pTag)` (`test_bench_scan.spin2:5460-5489`) |
| numField | `PUB numField(pName, numValue, limitAbs)` | `boundedField()` (`:5134-5141`) |
| naNumField | `PUB naNumField(pName, numValue, limitAbs, bValid)` | `naOrBoundedField()` (`:5143-5154`) |
| boolField | `PUB boolField(pName, bFlag)` | `boolField()` (`:5156-5162`) |
| tokenField | `PUB tokenField(pName, pToken, maxLen)` | `tokenField()` + `tokenFits()` (`:5164-5189`) |
| textField | `PUB textField(pName, pText)` | `lineTextField()` (`:5530-5539`) |
| pLine | `PUB pLine() : pText` | returns `@lineBuf` (zero-terminated) |
| lineLength | `PUB lineLength() : nBytes` | returns `lineLen` |

`lineAddChar`, `lineAddNum` (`:5466-5517`) stay `PRI`. `NA`, `TRUE`, `FALSE`, `?` are the object's own
`DAT` tokens. Emission stays in the caller (`debug(zstr_(log.pLine()))`), so the object never takes the
DEBUG lock and the caller keeps its `beat()` bracket. The digit grouping is therefore byte-identical to
every existing `BS-`/`BC-`/`BD-` record by construction.

### 7.2 Adoption

- **In this task:** the object is created, and `test_bench_dual.spin2` is its only consumer.
- **Not in this task (recommended as a new punch-list item):** converting `test_bench_scan.spin2`,
  `test_bench_char.spin2` and `test_bench_detect.spin2`. Each is a certified binary queued to run again at
  Visit 2 (scan run 8, the char certification, the detection re-run), and the detection log is diffed
  against a baseline. Converting them now changes three binaries the visit certifies, for no change in
  what they measure. This is Q5.

### 7.3 `src/test_dual_motor.spin2`

Left untouched. It is not a bench binary (it reads the user config, has no records, watchdog or
sign-off), none of its code is reused, and the plan's "extension" wording (`BENCH-READINESS-SPRINT-PLAN.md:760-764`)
predates the three-binary split. Two defects noticed: its header names itself `demo_dual_motor.spin2`
(`src/test_dual_motor.spin2:3`), and everything after the `repeat` at `:78` is unreachable. Listed in
DEVIATIONS as out of scope.

---

## 8 · Operator steps

### 8.1 Precedent followed

| What | Where it is proven or specified |
|---|---|
| Window, layers, crop-and-overlay, one `UPDATE` per frame | `DOCs/REF-NO-COMMIT/dbg-display-theory/DISPLAY-PATTERNS-builders-guide.md:30-82`; `HOWTO-build-debug-displays-with-claude.md:101-111` |
| A panel that drew and read input **on this rig**: `PLOT` + `LAYER 1..5` + `CROP 1` + `UPDATE`, then `PC_KEY` and `PC_MOUSE` polls with `CROP` blits | MEASURED `DOCs/analyses/bench/2026-09-12/debug_260912-153807.log:19`, `:54-59` |
| Generator as single source of layout: Pillow, 24-bit BMP, prints the `CON` block | `tools/gen_t0hand_assets.py:1-26`, `:32-61`, `:165-198`; HOWTO `:70-97` |
| In-tree panel code: setup `t0hSetupPanel()`, compose `t0hDrawPanel()`, keypress with arming | `src/test_bench_t0.spin2:1292-1346`, `:1251-1257`, `:1278-1283` |
| `PC_KEY` / `PC_MOUSE`: each last in its own statement, window focus, ~100 ms latch, 7 consecutive longs, buttons read -1 | DISPLAY-PATTERNS `:201-227`, `:288-297` |
| Opaque cells, restore to erase, fixed cell pitch | DISPLAY-PATTERNS `:153-192` |
| Gotchas: `>=`/`<=`, bare BMP names resolve from `src/` | HOWTO `:115-129` |
| The batch runner is headed, so PLOT windows work | `DOCs/PUNCH-LIST.md:369-379` |
| The failure mode to design against: a panel that drew nothing, operator could not tell what was asked | `VISIT-1-RESULTS.md:293-297`; PL-42 `DOCs/PUNCH-LIST.md:1249-1283` |

### 8.2 The panel

- Window `bmpanel`, `SIZE 480 260`, `POS 60 80`, `HIDEXY UPDATE`. Layers: 1 `bm_bg.bmp` (header, prompt
  well, button frames, footer "CLICK THIS WINDOW FIRST -- PANIC: DISCONNECT THE BATTERY"); 2
  `bm_prompt.bmp` (prompt text cells stacked by row: `BRAKE_L` two lines, `FLOOR` two
  lines); 3 `bm_state.bmp` (state words stacked: WAITING FOR START, STARTING, BRAKE THE LEFT WHEEL NOW,
  RELEASE THE WHEEL, OBSERVING, WHICH WAY DID IT TURN?, DONE, SKIPPED, TIMED OUT); 4 `bm_buttons.bmp`
  (cells START, SKIP, STOP, LEFT, RIGHT, STRAIGHT, DID NOT MOVE, each normal and highlighted); 5
  `bm_digits.bmp` (0-9 plus blank, a 3-digit countdown).
- Assets and a `BM_*` geometry `CON` block from `tools/gen_dual_assets.py`, same structure as
  `gen_t0hand_assets.py`.
- Input: `debug(\`bmpanel \`pc_key(@keyCode))` and `debug(\`bmpanel \`pc_mouse(@mouseX))` as two
  statements every `OPER_POLL_MS` (50 ms). `VAR LONG mouseX, mouseY, mouseWheel, mouseL, mouseM, mouseR,
  mousePixel` adjacent. A click acts on the press after a released reading (the T0-12 arming,
  `test_bench_t0.spin2:1251-1257`); hit-test by bounding box per button from the `BM_*` constants.
  Keys: `S` START, `K` SKIP, space STOP, `L` `R` `T` `N` answers.
- Redraw only on a state change or once a second for the countdown (dirty flag, DISPLAY-PATTERNS `:255-268`).
- Every prompt, click, key, timeout and answer is also a `BM-OPER` record, so the log tells the analyser
  what the operator saw and did; the terminal is never the only channel.

### 8.3 Correct by construction for attended steps

- **No motion before START.** The panel is drawn and waits for START before any wheel is started. A
  panel that fails to draw costs a 120 s timeout and a NOMEAS; it can never be followed by motion the
  operator did not ask for.
- **The operator never types a value** (decision 14): the hand-brake needs no input at all (the fault is
  detected by the instrument); the floor answer is a choice of four buttons.
- **STOP is always live** in the floor segment, polled every 50 ms; the absolute current monitor
  (2.8) is live in both. PANIC remains physical battery disconnect only (arbiter context D).
- **Hand-brake prompt text:** "HANDS CLEAR. CLICK START: BOTH WHEELS RUN AT HALF POWER." then "BRAKE THE
  LEFT WHEEL NOW -- HOLD IT UNTIL THE PANEL SAYS RELEASE." then "RELEASE THE WHEEL."
- **Floor prompt text:** "PLATFORM ON THE FLOOR, SPACE CLEAR. CLICK START: IT DRIVES ABOUT 2 SECONDS,
  POWER 50, DIRECTION +50. CLICK STOP OR PRESS SPACE ANY TIME." then "WHICH WAY DID IT TURN?"

---

## 9 · Changes outside the new binary

| File | Change | Owner |
|---|---|---|
| `src/isp_bldc_motor_userconfig_bench.spin2` | `#ifdef BENCH_QUIET` branch setting the two quiet masks (6.1; no `BENCH_QUIET_BUILD` constant, 12.6); the `#else` branch keeps today's two mask lines unchanged | phase 2 |
| `src/isp_steering_2wheel.spin2` | TEST-USE ONLY `testGetBoardTypes()` (12.1 Q8) | phase 2 |
| `src/isp_bench_log.spin2` | new (7.1) | phase 2 |
| `tools/gen_dual_assets.py`, `src/bm_bg.bmp`, `src/bm_prompt.bmp`, `src/bm_state.bmp`, `src/bm_buttons.bmp`, `src/bm_digits.bmp` | new; the BMPs exist only after the generator runs (Q6) | phase 2 + Q6 |
| `tools/bench-run.sh` | tiers `dual-a`, `dual-clock`, `dual-b`, `dual-brake`, `dual-c`, `dual-floor`, each `BENCH_FILE="test_bench_dual.spin2"`, `EXTRA_DEFS=(-D BENCH_QUIET -D DUAL_PART_<X>)`, a `PRECONDITION` naming the rig state and hands from 4.1; `dual-clock` exits 2 with a usage message when no `clkfreq` is given; usage lines; the header list of binaries that print the end marker (`:28-33`) | phase 2 |
| `tools/signoff-collate.py` | `BINS` gains `DUAL` (`:118`); `BIN_SOURCES` gains `"DUAL": "src/test_bench_dual.spin2"` (`:120-125`); `BANNER_TAGS` gains `BM-BANNER` (`:144`); `HEADER_TAGS` gains `BM-BUILD` (`:146`); the harness's declaration emitter must be named to match `DECL_CALL_RE` (`:149`, `...signoffdecl...(`); a `--selftest` fixture with one `BM-` log | phase 2 |
| `DOCs/analyses/bench/SIGNOFF-MANIFEST.tsv` | 26 new lines, row 14, task 3508, bin `DUAL`, `visit_owed` 2, status `OWED`, from 5.2 (NOSTALL x6, DBGMASK x6, INSTLIVE, IDLEFLT, REVB, INTEG, TRACES x3, CLKFRAME, RSTPROV x2, RAMPREST, OFFREST, BRAKEFLT, FLOORANS) | phase 2 (Q7) |
| `DOCs/analyses/bench/SIGNOFF-MANIFEST.md` | regenerated by the collation, never by hand (`VISIT-SIGNOFF-DESIGN.md:143-158`) | Q7 |
| `DOCs/PUNCH-LIST.md` | PL-17 progress; a new item for adopting the object in scan/char/detect; `test_dual_motor.spin2` defects | Q7 |
| `DRIVE-OBJECTS.md` | **none in this task.** The C-4 table is produced by the analyser and published by «#3514»/«#3515» (sprint plan `:981-982`) | -- |
| `src/isp_bldc_motor.spin2`, `src/isp_steering_2wheel.spin2`, `src/isp_bldc_motor_userconfig.spin2` | **none.** Every method this design calls exists today (section 2.1, 3, 4.4 citations). The PASM-addressed VAR runs (`isp_bldc_motor.spin2:1976-2009`, `:2045-2064`) are not touched; phase 2 confirms both library files are absent from `git diff` | -- |

Gates for phase 2: `tools/build-check.sh` green with both release demos certified (the new top must
compile under at least one block; with no part flag it compiles everywhere, using library `PINS_*`
constants as the scan does, `src/test_bench_scan.spin2:245-254`); `tools/check_style.sh` exit 0 on both
new `.spin2` files; `tools/signoff-collate.py --selftest` and `--check-ready 2`.

---

## 10 · Open questions

Stephen's calls, or facts about the rig this design cannot determine. Nothing above guesses them: each
names the default the design carries until answered.

- **Q1.** Answered/retired -- see section 12.1.
- **Q2 (Stephen) -- ladder rungs above the 147_000_000 ceiling.** T1-3 lists 155 and 165 x 10^6 to find the
  real ceiling (plan `:747-749`); they fault on purpose at the highest speeds the rig runs (~461 ticks/s
  predicted), guarded by the 10 A abort. Keep them? *Default: built in, `LADDER_PROBES` = 2.*
- **Q3.** Answered/retired -- see section 12.1.
- **Q4 (fact) -- whether the harness's `pinread()` of the hall inputs is invisible to a running driver**
  that reads them with `testp`. The pins are plain inputs (T0-12 precedent, run with no driver cog).
  UNVERIFIED 11.3; if false, `hwPos` must be dropped and STOPMODE condition (3) loses its only position.
- **Q5 (arbiter / Stephen) -- PL-17 adoption.** The extraction is in this task; converting the scan, char
  and detection binaries to it changes three binaries Visit 2 certifies. *Default: a separate punch-list
  item after Visit 2 (7.2).*
- **Q6 (arbiter) -- who runs `tools/gen_dual_assets.py`.** The dispatch rules allow no shell beyond the
  gates, the compiler and git, so phase 2 cannot produce the BMPs, exactly the gap «#3542» left
  (`tools/gen_t0hand_assets.py:23-25`). The attended loads cannot draw without them.
- **Q7 (arbiter) -- DOCs edits in phase 2.** Decision 10 forbids `DOCs/` edits a task does not name.
  Phase 2 needs `DOCs/analyses/bench/SIGNOFF-MANIFEST.tsv` (and its generated `.md`), and should record
  PL-17 progress and two new punch-list items in `DOCs/PUNCH-LIST.md`.
- **Q8 (arbiter / Stephen) -- board revision at steering starts.** The steering object has no per-wheel
  `getBoardType()` pass-through, so "log the detected revision at every start" is met only for wheel-object
  starts; steering starts print `board,NA why,NO_PASSTHROUGH`. Adding the pass-through is a library change
  outside this task. *Default: NA.*
- **Q9 (arbiter, for «#3509») -- C-1's tolerance against existing evidence.** The speed-law formula
  (study `:580`) predicts 102.7 ticks/s at 36_750_000 and 205.4 at 73_500_000. MEASURED: 98.2 and 196.4
  (`VISIT-1-RESULTS.md:90`), 4.4 % below at both; the code's own 147_000_000 note (272.0 rpm against
  273.8, `isp_bldc_motor.spin2:1413`) is 0.7 % below. T1-3's 2 % criterion would therefore report C-1
  departing at the first rung on today's evidence. The scan's own "expected 99" (`test_bench_scan.spin2:396`)
  is labelled DERIVED without its derivation. Which prediction and tolerance does the analyser judge
  against? The harness records both measured and formula rates either way.
- **Q10.** Answered/retired -- see section 12.1.
- **Q11 (fact) -- a fault provoked by an offset change at half speed.** POSTFLT writes offset 3 deg while
  the wheel runs at `DCS_AT_SPEED`. Faults at 3 deg are MEASURED only from a standing start at quarter
  speed. The current transient between the write and the driver's fault trip is not measured.
  *Default: built, with the 10 A abort live and `NO_FAULT` handled.*
- **Q12 (arbiter) -- «#3507»'s own certification cells.** The plan certifies DEBUG channels at Visit 2;
  this design proves only that the quiet build was compiled (R14-DUAL-DBGMASK-*). A cell that proves a
  masked channel prints nothing at run time needs a source-side check and belongs to «#3507».

---

## 11 · UNVERIFIED P2 / Spin2 facts the design relies on

Each is to be resolved against p2kb before phase 2 depends on it.

1. **`waitct()` with a target already in the past** waits for the 32-bit counter to wrap (about 15.9 s at
   270 MHz). The instrument never calls it without positive slack (2.2).
2. **Signed `getct()` differences** are valid across wrap for spans under 2^31 ticks (7.95 s at 270 MHz,
   10.7 s at 200 MHz); every span the instrument subtracts is one period or less.
3. **`pinread()` on base+5..base+7 while the driver `testp`s the same pins** does not disturb the driver
   (not a smart pin, so no acknowledge) (Q4).
4. **One two-motor instrument sample (about 8 method calls, 2 `pinread`s, packing) completes in well under
   2 ms** of Spin2 interpretation at 200 MHz. Counted by `late`/`skipped` regardless.
5. **A single `LONG` read by one cog while another cog writes it** returns either the old or the new value
   (the handshake in 2.4 relies on it).
6. **`getct()` is one system counter shared by every cog**, so the instrument's `t` and cog 0's
   `instMarkCt` are on one timebase.
7. **`cogstop()` of a cog parked in `waitms()` holding no lock and emitting no DEBUG** has no side effect
   beyond ending the cog (STEPHEN 2026-09-14 on locks, `DOCs/PUNCH-LIST.md:1215-1220`; the no-debug,
   no-lock precondition is the design's).
8. **`PC_MOUSE` fills seven consecutive longs and reports buttons as -1 while down**, and **`PC_KEY` /
   `PC_MOUSE` work with `{Spin2_v50}` absent**: the REF guide calls the directive mandatory for LAYER/CROP
   (`DISPLAY-PATTERNS-builders-guide.md:7`), yet `src/test_bench_t0.spin2` uses them without it.
9. **The 255-record DEBUG ceiling counts each distinct statement once per de-duplicated object image**
   (PL-18's image de-duplication, `DOCs/PUNCH-LIST.md:461-473`), not once per instance. The budget holds
   under either reading (6.2).
10. **Hub RAM left for a 147_456-byte ring** with DEBUG compiled in (the debugger's own hub reservation).
    Phase 2 reports the image size.
11. **`gettgtincr` handles the sync bit while the driver is `DCS_FAULTED`**, so `steering.driveAtPower()`'s
    `SyncStatus()` returns when one wheel is faulted (OUTSIDE, Z step 1). Its body sits in the LUT block and
    was not read. The watchdog backstops a hang.
12. **A parameter write through `testSetFwdRevIndep()` takes effect on the driver's next control pass**
    (DERIVED from the per-pass `setq`/`rdlong` of the parameter table, `isp_bldc_motor.spin2:2519-2520`;
    listed because POSTFLT's timing rests on it).
13. **`#ifdef` inside a `CON` block of an included constants object** sees a command-line `-D`. The `OBJ`
    and `DAT` forms are proven in the tree (`isp_bldc_motor.spin2:61-65`, `test_bench_scan.spin2:917-921`);
    decision 16 covers the construct.

---

## 12 · Arbiter review rulings (2026-09-14)

The design was reviewed against its cited sources and p2kb. The rulings below **bind phase 2** and
override any earlier section they contradict. Rulings marked **STEPHEN** are open until he answers.
Until then, phase 2 builds the default stated in section 10.

### 12.1 Open questions

| Q | Ruling | Owner and basis |
|---|---|---|
| Q1 | **Answered: not possible.** STEPHEN 2026-09-14: *"the is no ability to swap motor cables"*. Consequences: <br>- Load 7 (`DUAL_PART_SWAP`, `CABLES_SWAPPED`, the SWAP segment, the `dual-swap` tier and the `-S` cells) is **removed**: a load that can never run on this rig earns no place in the binary (D5). <br>- **The field question is settled on this rig, so there is no verdict to build, not even a partial one** (§5.3's "Field question" row is withdrawn). STEPHEN 2026-09-14: *"what bad behavior i thought we settled that they were performing the same now"*. MEASURED at Visit 1: <br>- the two motors match hold for hold (`bench/2026-09-14/VISIT-1-RESULTS.md` §4); <br>- the negative/positive current ratio is identical in kind on both (left 1.96/1.95, right 1.83/1.84); <br>- the scan's per-sign minima agree across the motors within about 1.5° (§3). <br>Nothing follows a motor or a channel. The one asymmetry follows the increment sign on both motors, which is the offset path the scan and «#3523» address. The discriminator was written for the field user's rig (`user-report-2026-09-09-ANALYSIS.md:301-317`). | STEPHEN |
| Q3 | **Retired, keep 10_000 ms.** Scan run 7 provoked 15 faults on this rig, every one recovered, with a 5_000 ms cool-down (`VISIT-1-RESULTS.md` §3; `test_bench_scan.spin2:374`, MEASURED). FAULTB's up to 20 faults at twice that cool-down sits inside proven precedent, so this is not a question for Stephen. | arbiter (precedent) |
| Q2 | **Keep the probe rungs** (`LADDER_PROBES` = 2). Plan T1-3 lists them to find the real ceiling, so they are planned work. The driver fault latch and the 10 A abort bound each probe. | arbiter (D4: work the plan) |
| Q3 | **Asked of Stephen.** Default 10_000 ms. | STEPHEN (thermal margin of his FETs, with no sensor) |
| Q4 | **Resolved; `hwPos` stays.** `PINREAD` reads the IN register and does not affect pin configuration (p2kbSpin2Pinread). The hall pins are plain inputs the driver reads with `testp`. Section 11 fact 3 is closed. | p2kb |
| Q5 | **Adoption by scan, char and detect is a punch-list item after Visit 2**, filed by phase 2. Visit 2 certifies those three binaries as they are. | arbiter (overlay P10: construction never grows the plan) |
| Q6 | **The arbiter runs `python3 tools/gen_dual_assets.py`** once, after phase 2 returns, then compiles. The BMPs are committed beside `src/t0h_*.bmp`. | arbiter |
| Q7 | **Yes.** Phase 2 adds the manifest cells to `DOCs/analyses/bench/SIGNOFF-MANIFEST.tsv` as `OWED` for visit 2 (task-execution overlay: *the commit that lands a feature adds its manifest cells*). It files punch-list items in `DOCs/PUNCH-LIST.md` (overlay P5: findings are ours to file). The arbiter regenerates `SIGNOFF-MANIFEST.md` with the collation. | arbiter |
| Q8 | **Add the pass-through.** The task requires the detected revision at every start, and `NA` at a steering start would leave that unmet. Add a TEST-USE ONLY `PUB testGetBoardTypes() : eLeftBoard, eRightBoard` to `isp_steering_2wheel.spin2`, returning `ltWheel.getBoardType()` and `rtWheel.getBoardType()`, beside the existing pass-throughs (`:615-831`). `BM-SSTART` then carries `l_board`/`r_board` (tok 7) and `why` becomes `NONE`; recompute its worst case. It adds no enum and does not touch the ABI. | arbiter (the task text) |
| Q9 | **The harness is unchanged**, since it records both rates. The analyser rule belongs to «#3509»: C-1 is judged as **linearity**. At every OK rung, `rate_x10 / pred_x10` must lie within 2 % (T1-3) of the same motor and sign's lowest OK rung. The absolute gap to the 500 µs model is reported beside it as its own reading, never as a C-1 departure. The gap itself (MEASURED 4.4 % at both speeds, `VISIT-1-RESULTS.md:90`) is filed as **PL-50**. | arbiter (instrument design, overlay P3) |
| Q10 | **Retired, `FLOOR_RUN_MS` = 2_000 with STOP live.** The "30 seconds" was never a drive duration. Bench plan T2-1 (`BENCH-TEST-PLAN-2026-09-10.md:1215`) says *"Thirty seconds, and it settles a documentation contradiction"*, which is its estimate of the effort. «#3511»'s body turned that into "one 30-second observation", and §4.4 into a 30 s drive of about 25 m. Finding AC (`DRIVER-AUDIT-2026-09-09.md:443-470`) needs only to see which way the platform turns, and 2 s at power 50 shows that. No floor-space question remains. | arbiter (research) |
| Q11 | **Keep, with the 10 A abort.** A fault from speed is the POSTFLT trial's purpose (S-9a), the fault latch and abort bound the transient, and the trace's `i` records it. | arbiter (overlay P3) |
| Q12 | **Add «#3507»'s run-time cells here**, since this binary is the first quiet build. See 12.3. Without them, «#3507» landed with no certification cell, and that gap blocks Visit 2. | arbiter (task-execution overlay §8) |

### 12.2 Section 11 facts

- **Resolved by p2kb:**
  - fact 2 and fact 6: all cogs see one counter, and a `GETCT` difference is wrap-safe (p2kbSpin2Getct);
  - fact 3: see Q4;
  - fact 8: `PC_MOUSE` fills seven longs with buttons at -1 while pressed, `PC_KEY` latches 100 ms, and each must be the last command of its statement with its own backtick (p2kbSpin2DbgPcMouse, p2kbSpin2DbgPcKey). For the `{Spin2_v50}` question, the panel source follows `src/test_bench_t0.spin2`'s form exactly, and Visit 2 certifies both panels;
  - fact 13: `-D` defines the symbol in every file of the compilation, OBJ children included (p2kbSpin2ExternalSymbols).
- **No dependency remains:**
  - fact 1: the instrument never calls `waitct` without positive slack;
  - fact 7: the instrument holds no lock (p2kbSpin2Cogstop: locks are not released by `cogstop`, so none may be held);
  - fact 11: the `SYNC_PRECOND` check plus the watchdog backstop cover it.
- **Precedent:** fact 5, single-writer longs shared without locks, is the library's own driver/status-block pattern.
- **Measured by the harness itself:** facts 4 (`late`, `skipped`), 9 (phase 2 counts statements; build-check is the confirmation), 10 (phase 2 reports image size) and 12 (the POSTFLT trace).

### 12.3 Added sign-off cells: row 15, task 3507, visit_owed 2, OWED

These are host cells computed by `tools/signoff-collate.py`. They use its existing line classifier, not a new one.

| Cell | Crit | lo..hi | Measured as | FAIL fires on |
|---|---|---|---|---|
| `R15-HOST-QUIETLOG` | `LIB_LINES_IN_QUIET_LOG` | 0..0 (COUNT) | In every DUAL log, the P2 debug lines that the harness did not emit. The harness's own set is `BM-*`, `SIGNOFF-DECL`, `SIGNOFF`, the panel's display lines, the panic line and `DEBUG_END_SESSION`. | A build whose masks are not honoured, such as `-D BENCH_QUIET` absent or mistyped: library LIFECYCLE and COMMAND lines then print at every start. |
| `R15-HOST-CHANLIVE` | `LIB_LINES_ENABLED` | 1..NA (COUNT) | In the same visit's char log (default bench masks), the P2 debug lines outside that binary's own record set. | The positive limb: a mask change that silences every channel, including the enabled ones. |

`R14-DUAL-DBGMASK-*` stays as designed: it proves what was compiled, and R15 proves what printed.

### 12.4 Emission volume (added by review)

- **Per-trace cap `TRACE_EMIT_MAX` = 400 lines.** At drain, keep the dense window. Above the cap, first shrink the dense window to 100 samples, then raise the stride of the sparse and change-driven lines through 1, 2, 4 and 8 until the count fits.
  - `BM-TRACE-END` gains `stride` (TINY). Recompute its worst case, which must stay under 280.
  - The analyser recomputes `emitted` and `ksum` from the lines as emitted.
- **Reason (DERIVED):** uncapped, one part A load emits up to about 48 traces × about 1,130 lines. That is roughly 13 MB, more than 30 times any Visit 1 log. The cap bounds exposure. It is not a claim that volume causes lost logging.
- **`BM-PLAN` gains `est_kb`** (SMALL): the worst-case bytes of its segment, so a log that is far larger than planned is visible.

### 12.5 Phase 2 shape

- **Three sequential dispatches**, with no agent shell:
  - (a) `isp_bench_log.spin2`, the `BENCH_QUIET` bench-config branch, and the steering pass-through;
  - (b) `test_bench_dual.spin2` and `tools/gen_dual_assets.py`;
  - (c) the `bench-run.sh` tiers, the collation changes (`DUAL` plus the R15 host cells, with a selftest fixture), the manifest rows, and the punch-list items.
- The arbiter compiles after each dispatch and returns any errors to that agent.

### 12.6 No `BENCH_QUIET_BUILD` constant (added after part a)

- **The constant is removed.** §6.1's `BENCH_QUIET_BUILD` existed only in the bench config, but
  `tools/build-check.sh` compiles `test_bench_dual.spin2` under the end-user config too, where no such
  constant exists.
- **`BM-BANNER quiet` and `R14-DUAL-DBGMASK-*` are computed from the compiled masks:**
  `user.MOTOR_DBG_MASK == DECOD user.DBGCH_ERROR | DECOD user.DBGCH_WARNING`, and the same for
  `STEER_DBG_MASK`.
  - Both configs define those symbols.
  - The property printed is the property that matters: one value, one meaning.
- **MEASURED 2026-09-14:** the masks take effect. `isp_steering_2wheel.spin2 -d -D BENCH_CFG` compiles to
  21_768 bytes with `-D BENCH_QUIET` and 24_501 bytes without it.

### 12.7 The event mark is located by ring index, never by time (added in b1 review)

**Defect found in b1 (DERIVED).** `drainFindMark()` finds the mark by testing whether `t - instMarkCt` is
non-negative.
- A `GETCT` difference is wrap-safe only for spans under 2^31 ticks: 10.7 s at 200 MHz, 7.95 s at
  270 MHz and 7.16 s at 300 MHz.
- A trace may run to `TRACE_MAX_SAMPLES` = 8.0 s after its pre-samples.
- So on a long capture at 270 or 300 MHz, the newest samples read as *before* the mark. The search then
  stops at once and the trace is emitted as `NOT_REACHED`.
- §11 fact 2 was resolved true, but §2.5 applied it past its range.

**Construction:**
- Cog 0 still writes `instMarkCt` and increments `instMarkSeq` immediately before the event's library
  call.
- The instrument, on the first pass that sees a new `instMarkSeq`, records `instMarkTotal := instTotal`
  (single writer: the instrument) **before** storing that pass's sample. That sample is the first one
  taken at or after the mark.
- At drain, the mark's logical index is `instMarkTotal - drLostHead`, valid when it is `>= 0` and
  `< drStored`. When the index is below 0, the mark sample was overwritten, and `lost_head` reaches the
  mark exactly as the TRACES cell defines.
- `instMarkCt` stays for `t`-relative timing within one period, and is never used to find the mark.
- **The invariant:** the mark's position depends only on sample order, so no capture length at any clock
  can misplace it.
- **The same construction delimits measurement windows.** `windowStats()` today selects samples whose
  `t` lies between two `getct()` bounds.
  - Worked through, a one-second window cannot admit a wrapped sample, because that would need both
    bounds to wrap in opposite directions.
  - It still rests on the same range argument. So each window start and end is a mark recorded by the
    instrument as `instTotal`, and samples are selected by logical index.
  - `rsWinMs` still comes from the `t` difference between the first and last in-window samples, which
    are about one second apart and wrap-safe.

`BM-TRACE-END` and its worst case are unchanged.

### 12.8 Driver command facts and the OVERSHT power field (added in b2 review)

**Driver facts** (read from source by a survey and spot-checked by the arbiter):
- A new non-zero increment is accepted only from `DCS_STOPPED`, `DCS_AT_SPEED` or `DCS_FAULTED`
  (`isp_bldc_motor.spin2:2163-2170`).
  - In any other state it is **discarded**, not queued.
  - It leaves `AT_SPEED` on the pass it is accepted: `SPIN_UP` or `SPIN_DN` for the same sign,
    `SLOW_TO_CHG` for a sign change (`:2242-2254`).
  - Every segment therefore commands only after `AT_SPEED`, `STOPPED` or a fault. LADDER's 20 ms
    command-seen wait covers one driver pass, one instrument sample and one cog-0 poll.
- A zero request is always processed (`:2153-2161`). A request equal to the last one is not a new
  request (`:2163-2164`); Z step 1 depends on this.
- A distance-limited stop is set by the sense task (`:1788-1797`). The driver then passes through
  `SPIN_DN` before `STOPPED` (`:2209-2211`, `:2300-2334`), so BM-OVERSHOOT's `SPIN_DN` stop fields are
  reachable.
- `emergencyCutoff()` forces `DCS_ESTOP` on the next pass. After `clearEmergency()` the next pass sets
  `DCS_STOPPED` (`:2139-2149`).
- `testGetMotorCog()` is 0 when no driver runs and cog id + 1 otherwise (`:113-134`, `:1234-1242`).
- The sign of `pos` for a positive increment depends on hall wiring and is not settled by source. LIVE
  therefore judges `|ticks|`.

**OVERSHT power:**
- b2 read `power` through the steering object's `getMaxSpeedForDistance()`, which returns the max
  *speed* (PL-51). The value was right only because both default to 75.
- **Construction:** OVERSHT calls `steering.setMaxSpeedForDistance(OVERSHT_POWER)` once after its
  steering start. It prints `OVERSHT_POWER` as `power`, and never reads the getter.
- The C-3 prediction (about 1.2 m at 75 %) is stated against that same constant.

### 12.9 Part b3 review rulings

- **`FMT_VERSION` stays 1.** b3 added the `BM-OPER` event token `STOP` and changed the sizes of
  `OUT_POLLS` (130, from the Z steps' worst case) and `BM-OUT`. No log in this format has been captured
  or consumed yet, so there is nothing to version against. The analyser «#3509» is generated against
  the format as landed in this task.
- **The power fields mean "last specified power".** BM-OUT `l_pwr`/`r_pwr` and BM-FLOOR's power
  read-back come from `getPower()`, which returns the last specified power and is not zeroed on a stop
  (PL-52, DERIVED). The analyser reads them that way and never infers "stopped" from a zero power;
  BM-OUT's `l_st`/`r_st` are the stop evidence.
- **Operator records are queued while the instrument stores** and emitted in order after the freeze, so
  no `BM-` emission falls inside a capture. The panel's own display statements still go out during
  capture. That is permitted: they come from cog 0, and the instrument never contends for the DEBUG
  lock (I1).
- **The panel's geometry block is generated.** `tools/gen_dual_assets.py` was run on 2026-09-14. Its
  printed block matched `src/test_bench_dual.spin2` exactly when read side by side, and it wrote
  `src/bm_bg.bmp`, `bm_prompt.bmp`, `bm_state.bmp`, `bm_buttons.bmp` and `bm_digits.bmp`. Whether the
  panel draws and takes input on the rig is owed to Visit 2.
  - The generator was re-run after its FLOOR prompt changed to "about 2 seconds" (§12.1 Q10).
  - The CON block it printed was unchanged.
- **`{Spin2_v50}` is line 1 of both files that build a panel:** `src/test_bench_dual.spin2`, and
  `src/test_bench_t0.spin2` for T0-12.
  - **Stephen's display technique requires it.** `DOCs/REF-NO-COMMIT/dbg-display-theory/DISPLAY-PATTERNS-builders-guide.md:7`
    says *"The source file must start with `{Spin2_v50}` (or later)"* for LAYER/CROP, and `:290` repeats
    it. That meets `central:spin2-authoring-guide` §3.1.1 rule 1; p2kb carries no version entry for
    LAYER/CROP.
  - **The only panel proven on this rig carried it.** `src/test_bench_char.spin2` had the directive from
    441c9d9 (2026-09-11 18:22) to 7595274 (2026-09-13 21:21), and its panel drew on 2026-09-12 at 15:38
    (MEASURED, `git log -S Spin2_v50`).
  - The T0-12 panel («#3542») was built without it. Adding it there is the one correct remedy for a step
    that Visit 2 runs.
- **The default PLOT mouse y-axis runs top-down,** taken from Stephen's guide.
  - `DISPLAY-PATTERNS-builders-guide.md:86-90`: default mode is top-left origin, y down; `cartesian` is
    bottom-left, y up. The harness uses default mode, and its hit-test and CROP destinations are top-down.
  - `p2kbSpin2Plot` states the opposite for a new window: bottom-left, y up, "hardware-verified EF-020".
    Stephen's guide describes the technique his panels proved on hardware, so it governs here (overlay
    P7). The disagreement is reported to him for the P2KB project, not resolved in this one.
  - **The stakes are bounded:** the buttons lie only in the lower half of the panel, so a flipped axis
    would hit no button rather than the wrong one, and every button also has a key.

### 12.10 Part c review rulings (sign-off cells)

- **Each clock build owns its cells.** `tools/signoff-collate.py:954-968` lets only the latest build
  declaring a cell speak, and supersedes earlier builds; a shared `-K` would let the 300 MHz log hide a
  200 MHz FAIL. So `R14-DUAL-NOSTALL`, `R14-DUAL-DBGMASK` and `R14-DUAL-CLKFRAME` carry the compiled
  clock: `-K200`, `-K270`, `-K300`, selected from `CLK_FREQ` at compile time. A CLOCK build at any
  other clock declares and emits no sign-off cells (as `PART_NONE` does). Its BM-CLOCK record still
  prints `UNSWEPT_CLOCK`. A declared CLKFRAME cell is therefore always at a swept clock, which removes
  the FAIL-versus-NOMEAS contradiction. Row 14 becomes 32 cells: 26 - 3 shared + 9 per-clock.
  - **As built, the ids abbreviate their family word:** `R14-DUAL-NOSTLL-K200/-K270/-K300`,
    `R14-DUAL-DBGMSK-K200/...` and `R14-DUAL-CLKFRM-K200/...`. The full words would exceed the 20-character
    cell-id limit that both the manifest validator and the harness's `TOKMAX_CELL` enforce. The clock stays
    readable in the id, which `-K2`/`-K27`/`-K3` would not.
  - The harness derives the clock slot and a single `SF_JUDGES_CELLS` constant from `CLK_FREQ` at
    compile time. Every declaration and emission site is guarded by that one constant.
- **Row-15 host cells** (§12.3, amended):
  - **Criterion names:** `R15-HOST-QUIETLOG` is `LIB_LINES_QUIET`. The manifest validator limits a crit to
    18 characters, the binaries' `TOKMAX_CRIT`, and that limit stands.
  - **A missing input log gives `NOT_BUILT`**, as every HOST cell and the collation's rule 1 do.
  - **Library `ERROR`/`WARNING` lines are not counted by QUIETLOG.** Those channels are enabled by
    design under the quiet masks, so counting them would give one FAIL two meanings. The collation
    derives their message prefixes mechanically from the leading string literal of every
    `debug[user.DBGCH_ERROR]` / `debug[user.DBGCH_WARNING]` statement in `src/isp_bldc_motor.spin2`
    and `src/isp_steering_2wheel.spin2`, and a matching line is not counted. The derivation is never
    hand-maintained. The proving lines still list any such line, so an ERROR during a DUAL load is seen.
  - **Each binary's own output is derived as well, never hand-maintained** (the task-handoff quality
    pass). The own sets are the record-family prefixes (`BM-`/`BC-`, `SIGNOFF-DECL`, `SIGNOFF`, which
    are the record contract) plus texts derived from the binary's source: the leading literal of every
    plain `debug("...")` statement, and the DAT string behind every `debug(zstr_(@label))`.
    - A derived text is refused if it is shorter than a minimum, if its label is unresolved, or if it
      begins any library debug literal, so it can never exempt a library line.
    - A missing binary source gives NOMEAS.
    - The hand-copied note strings are removed. Otherwise a changed char note would count as a library
      line, and CHANLIVE would pass with every channel silenced.
- **Accepted as built:**
  - `R14-DUAL-BRAKEFLT-H` counts a 10 A abort during the brake wait as measured. That is a real signal:
    the braked wheel drew over 10 A without the driver faulting.
  - `RAMPREST-B` and `OFFREST-C` are coverage of the restore path. Their falsifier is the I11
    construction, and the manifest basis says so.
  - `FLOORANS-F` is coverage.


# Visit 10 — run sheet, the release-candidate pass (wheels up): certify everything built, so only the floor run remains

**Task:** «#3613» runs it. **Burn-down:** `DOCs/PUNCH-LIST.md`, "Release burn-down".
**Last record:** `DOCs/analyses/bench/2026-09-26/pass7/VISIT-10-PASS7-EVALUATION.md` (DRIVER_REV 35). Pass 8's sheet was
never run. Its loads are folded in here, on DRIVER_REV 39.
**Stephen's ruling, 2026-09-26:** serial and demo testing come after a release-candidate driver. This is that pass, so
both are in it.

---

## Bench visits remaining to 6.0

| # | Visit | Closes | Run length |
|---|---|---|---|
| 1 | **This pass**: release candidate, wheels up | PL-14, 51, 52, 144, 145, 146, 161, 162 (pass 8's items). PL-160's wheels-up half: the generator's R22 cells and every stop re-derived for it. PL-149 (the demos). PL-148, 154, 157 (serial), **once desk items 1 and 2 below are built** | about 21 min of run, about 24 with compiles, plus the serial wiring |
| 2 | **The floor run** (last): `VISIT-6B-FLOOR-RUNSHEET.md`, tier `dual-spin` | PL-93, 95, 106, 132, 150, PL-111's API precondition, and PL-160's feel under load (SPINSTRT and SPINPEAK are start measures, so the new ramp is under them) | about 14 min of run, about 40 at the rig |

**Still open after both visits:**
- **PL-120**: a watch item, not a release item.
- **PL-163**: the Rev A fold-back fix. It stays open unless the optional Rev A block at the end runs, and that block first
  needs a cell that has not been built.
- **PL-111's serial half.** `protclear` releasing a latched stop is NOMEAS by design in `serial_certify.py`. A lifted rig
  cannot latch a protective stop. The floor run can, but it runs `test_bench_dual`, not the serial top level, so neither
  visit reaches this half as built. **It needs a ruling:** either the API half (floor) plus the unlatched serial checks
  (this pass) close it, or a way to latch the stop under the serial top level has to be built.
- **PL-160's owner questions Q2–Q5.** These are rulings, not bench work.
- The ancillary list.

**Before the floor sheet goes out:** its banner still reads `src_rev,58,fmt,37` / `drv_rev,37`. It also still says
"PL-160's jerk-limited ramp is not built yet". Both need re-cutting to SRC_REV 59 / FMT 38 / DRIVER_REV 39.

---

## ⛔ Before this sheet goes out: three desk items (P10, "no sheet goes out while a known, fixable item is unbuilt")

1. **The serial top level cannot be built for this rig. VERIFIED.**
   - The command `pnut-ts -D BENCH_CFG src/isp_steering_serial.spin2` gives
     `isp_steering_serial.spin2:236:error:Expected an object constant, structure, or method`.
   - The cause: its `user` object is always `isp_bldc_motor_userconfig`, whose active block is single-motor
     (`ONLY_MOTOR_BASE`, Doco, 12 V), and it reads `user.LEFT_MOTOR_BASE`.
   - No block in the user config matches the rig. The rig is left P32 and right P16; the user config's dual blocks are
     P0/P16 and P16/P32. So editing the user config at the bench is not a workaround.
   - **Fix:** the demos' own pattern (`demo_dual_motor.spin2` :47–51): `#ifdef BENCH_CFG` selects
     `isp_bldc_motor_userconfig_bench` for `user`.
2. **`serial_certify.py`'s R20-SER-RAMP would FAIL a correct driver.**
   - `DEFAULT_ACCEL_NO_SINGLE_RATE` expects `getaccel` to read **0** after a fresh start. The script's docstring
     says the same.
   - Since DRIVER_REV 38, `getaccel` returns `wheels.getAcceleration()`, which reads the built-in **1_000** until set.
     See `isp_steering_serial.spin2` :506–507 and `DRIVE-OBJECTS-SERIAL.md` :157.
   - **Fix:** expect 1_000 (the library's ACCEL_BUILTIN_MM_S2), and correct the docstring.
3. **Desk question: the wiring walk's pass band.** `checkWiring()` judges each leg at WALK_TICKS (6) up to 6 + 3 ticks.
   - That band was set on the stepped ramp and plan. No commit in DRIVER_REV 36–39 re-derives it.
   - Under the stepped plan (pass 7, `debug_260926-174359.log`, `BM-SKWLEG`), each leg's limit fired at 5
     (`lim,5`) and the wheel rested at 7–8.
   - DRIVER_REV 39's plan is built to land on the limit, and may rest up to one tick **short**
     (STOP_PLAN_EARLY_TICKS, which the harness added to its own stop cells).
   - If a leg can rest at 5, HLT_WIRING fails. That would fail R19-DUAL-WALK-X, both demos' `* wiring:` lines and the
     serial checkwiring.
   - Derive it at the desk before the run. Do not wait to see what WALK-X reads.

---

## ⛔ First: PUSH, then pull at the bench

`git log --oneline -1 -- src/` at the bench must show **c30076b** or later: DRIVER_REV 39, test_bench_t0 SRC_REV 25,
test_bench_dual SRC_REV 59 / FMT 38. The serial block needs the later commit that carries desk items 1 and 2.

**What this invalidated since pass 7's binaries (cd6f1b7, DRIVER_REV 35):**
- DRIVER_REV 36: the fold-back acts only on a driven bridge; the pack is sampled once per slot.
- DRIVER_REV 37: requests are answered on a later pass instead of waited on; the rest offset is netted out of the
  fold-back.
- DRIVER_REV 38: the jerk-limited generator shapes every ramp and stop.
- DRIVER_REV 39: the driver plans and publishes its own stop; the status run grows from 22 to 24.

Every cell in every tier below runs against these.

## ⭐ Before anything: note the time you connect the pack

**Write down the clock time you connect the battery**, or that it was already connected. A `pack-connect*.txt` file's
creation time does this. PL-120 watch.

## Check the banner before reading anything else

| Load | Every banner / build record must read |
|---|---|
| `t0-stopreason`, `t0-api` | `* test_bench_t0 -- ... -- src_rev 25`; `t0-api` also `T0-26,begin,wheel,RIGHT_P16,driver_rev,39` |
| every `dual-*` | `BM-BANNER,...,src_rev,59,fmt,38,part,<START / D / REG / KICK / FRESP / PACK>` and `BM-BUILD,...,drv_rev,39,...` |
| `dual-pack` | `BM-PKBUILD,...,fitted,TRUE,pin,0,cal_pm,1_012,calibrated,TRUE` |
| `demo-single`, `demo-dual` | no demo prints a revision, so the SHA check above is their identity. `demo-dual` opens with `* dual motor demo`; `demo-single` has no opening line of its own; its first demo line is `* start checks: checked ...` |
| serial | P2 terminal: `* Serial I/F to dual motor platform`, then `* command loop *`; host: `SER-BANNER,script,serial_certify.py,...,baud,624000,drive_voltage,PWR_18p5V,dry_run,FALSE` |

---

## Tier selection: every tier answers a question of its own about DRIVER_REV 36–39 (P10), or it is out

| Tier | | The question no other included tier answers, or why it is out |
|---|---|---|
| `t0-stopreason` | **IN** | Does the generator shape each ramp as specified? That means each pass jerk- and limit-bound, no overshoot, a reversal through zero without DCS_STOPPED, and a stop read mid speed-up unwound within RAMP_TAU_MS. Do the driver's published plans put single-motor distance, rotation and time limits at rest inside their bounds, at cruise and mid-ramp? This is the only tier that samples `drv_accel_now` pass by pass. Also PL-52 |
| `t0-api` | **IN** | Do the four ramp longs' new meanings read back as derived (RAMPDEF, ACCEL, PERSIST)? Is start()'s voltage honoured (PL-14)? Does the steering distance speed read back (PL-51)? Does every setter and refusal keep its contract through DRIVER_REV 37's in-flight request service? This is the only tier that makes every API call |
| `dual-start` | **IN** | The planner overlay now loads over the start sequence (39), and the sync take is answered in flight (37). Do ten steering starts still pass their checks and walk inside their band under the new ramp and plan? Does the pack read against the config (PL-162 PACK-X)? And do the front cog's per-lifetime worst passes no longer spread by one drive pass (PL-161's negative)? |
| `dual-d` | **IN** | PL-161 FRONTST-D, PL-145 TIMESTOP, PL-146 EV-FOLDBACK, PL-144 PATH-HUNT. Also the e-stop release in flight (37), and the lag gate holding a stall under the generator (HOLDSET, NOTFOL) |
| `dual-reg` | **IN** | Does a steering turn by distance stop each wheel at its own limit on the driver's plan (TURNDIST, now 3 ticks)? Its 2-ft wheel fires while still accelerating. Does a drive of a FAULTED wheel pass through 37's two-stage in-flight fault clear (FLTRETRY)? No other tier judges either |
| `dual-kick` | **IN** | Every speed change is now a jerk-limited ramp. Does the speed-change kick stay at or under 50 mV? PL-160 names a kick back above pass 7's 16/13 mV as its negative, and pass 7's evaluation said this tier returns "if a later change touches the ramp" |
| `dual-fault` | **IN** | The shipped default response re-syncs and stops along the ramp, which is now the generator. Does it reach rest within 50–150 % of the S-curve's prediction (RESYNC-X)? Does the partner stop (PLATSTOP-X)? Does the steering front cog's fault pass stay under 950 µs after 37/39 (FRONTST-EV)? It is the only tier that forces a fault at speed, and the only 950 µs cell |
| `dual-pack` | **IN** | PL-162 PACK-ABSENT on the steady reference, and DRIVER_REV 36's per-slot raw-count sampler against the meter (CAL_POINT) |
| `demo-single` | **IN** | PL-149: does the shipped single-motor demo run end to end on the release candidate? |
| `demo-dual` | **IN** | PL-149: the same for the two-wheel demo |
| serial (not a bench-run tier) | **IN** | PL-148 / 154 / 157: does a real host get the documented replies from the 6.0 serial top level? |
| `t0` | OUT | Its no-motion cells judge objects 36–39 did not change. The exception is R17-T0-ACCEL, whose question (a rate becomes accel_up and its jerk, anchored on 33_958) is asked by `t0-api`'s API-ACCEL and RAMPDEF on the same conversion. Every start in every tier checks the ABI |
| `t0-hand` | OUT | The hall count is unchanged; the answer is on disk |
| `t0-stopmode`, `-fltfirst` | OUT | Attended. The stop states are unchanged PASM bridge modes. The hold-decay floor (DRV_INCR_FLOOR 1_500) equals the old ramp_min default. The held wheel's netted fold-back (37) is judged by `dual-d`'s EV-FOLDBACK pair: an over-netted fold-back fails its engage |
| `dual-a`, `dual-a-legacy` | OUT | LADDER, RATELAW and OFFSETS are characterisation already on disk. TAKE-A (re-derived) asks what R22-T0-RAMP-UNWIND asks, on the same `jerkStep` branch (a target against the acceleration's sign). TRKICK-A is `dual-kick`'s TRKICK-T |
| `dual-b` | OUT | STOPLIM-B asks TURNDIST-B's question (`dual-reg`) on the same REQ_DRIVE_DISTANCE path, with the same 3-tick bound. FAULTB/RMPDROOP is the C-5 fault-boundary sweep (characterisation). The lag gate under the generator is judged by `dual-d`'s HOLDSET/NOTFOL. RAMPREST judges the instrument |
| `dual-c` | OUT | STPDECEL-C (80..126 ticks from half speed) is a no-regression guard whose question R22-T0-STOPPLAN-C/-M ask directly (the stop against its derived plan). BASELINE's faults and e-stops are unchanged bridge modes; the e-stop release is `dual-d`'s |
| `dual-limits`, `-top` | OUT | Characterisation (limits reset E1–E4). LIMRAMP's traces are recorded and no cell judges them. The ramp shape is t0's R22 |
| `dual-clock-200/270/300` | OUT | CLKFRM judges a frame-count constant 36–39 did not touch. README names 270 MHz as the tested clock. (No cell judges the planner's frame slack: see "Not covered") |
| `dual-start-nowalk`, `-phaseneg`, `-swapneg` | OUT | The start checks are unchanged. The probe and hall checks run through `restBridge`, which lies after `gettgtincr`, outside the overlay ($200–$27E) (VERIFIED in `isp_bldc_motor.spin2` :8157, :8376–8402). Retries run from Spin2 in the same lifetime. `dual-start`'s ten starts exercise the overlay load |
| `dual-fault-rightfirst` | OUT | PL-120's order test, settled at pass 4 |
| `dual-lead`, `dual-align`, `dual-brake`, `dual-ui`, `panel` | OUT | Characterisation or attended UI; nothing under them changed |
| `dual-spin`, `dual-floor` | OUT | The floor run (visit 2) |
| `spin*`, `detect*`, `char`, `scan*` | OUT | Instrument or characterisation tiers; no 36–39 question |

---

## The visit, declared

| | |
|---|---|
| **Purpose** | **Certification** of the release-candidate driver (DRIVER_REV 39) wheels up, the release demos and the serial path |
| **Hardware risk** | • `t0-stopreason`: the right wheel at power 15, one **abrupt e-stop**, then spun to power 50 (about 145 rpm), reversed through zero, and stopped by limits mid-ramp.<br>• `t0-api`: nothing moves.<br>• `dual-start`: each start twitches the wheels; each wiring walk turns them 3.5 cm each way.<br>• `dual-d`: **wheels stop dead**, an e-stop is held, the current limit is lowered until a wheel stalls, and twice the platform is switched off while spinning.<br>• `dual-reg`: half-power turns; **one wheel faulted on purpose**, twice.<br>• `dual-kick`: one wheel at a time up to about 300 rpm commanded.<br>• `dual-fault`: **faults forced at speed** (up to about 220 rpm commanded), including a phase short that **stops a wheel dead**.<br>• demos: **full power, 15 s at a time**.<br>• serial: power 30, and checkwiring.<br>**Wheels up throughout. Panic: physical battery disconnect.** |
| **Who acts** | Every tier is hands-off except two. `dual-pack`: unplug and replug the sensor Powerpole twice, when told. Serial: wire three leads to the host and run one host command |
| **Runs that carry state** | None across runs. If PL-120 strikes, `t0-stopreason` waits up to 3 min for the right wheel; `dual-fault` pauses up to about 2 min, up to twice. The serial P2 keeps the speed-up rate it set until reset; it runs last |
| **Run length** | See the table below: **about 21 minutes of run, about 24 with one compile per load**, plus the serial wiring. Add up to about 3 min (`t0-stopreason`) and 2.5–4.5 min (`dual-fault`) if PL-120 strikes |
| **Repeatability** | All repeatable and idempotent |
| **Variant matrix** | Rev B ×2, the paired 6.5in hubs, 18.5 V pack (sensor on P0), 270 MHz. `test_bench_t0` T0-25 and T0-26. `test_bench_dual` parts START, D, REG, KICK, FRESP, PACK (`-D BENCH_QUIET`). Demos under `-D BENCH_CFG`, with the library's full debug channels, as a user's `-d` build has. Serial top level `-d -D BENCH_CFG` with `pythonSrc/serial_certify.py` |

**Run lengths.** The "text" column is each tier's own run-length text. Where that gives only a cap or an upper bound
(`dual-d`, `dual-pack`), pass 7's log-to-log time is used instead.

| Load | Its text | Pass 7, log to log (includes the next compile) | Used |
|---|---|---|---|
| `t0-stopreason` | "About 2 minutes, or up to about 5 if the right is refused" | 0:53, before the ramp legs were added | 2 |
| `t0-api` | "About 20 seconds" | 0:33 | 0.3 |
| `dual-start` | "expected about 1" | 1:18 | 1 |
| `dual-d` | cap 15 minutes only | 1:54 | 2 |
| `dual-reg` | "expected under 1" | 1:47 | 1 |
| `dual-kick` | "expected under 2" | 1:54 | 2 |
| `dual-fault` | "expected about 6 (about 8.5 with one pause, at most about 10.5 with both)" | not run | 6 |
| `dual-pack` | "Under 5 minutes" | about 2 | 2 |
| `demo-single` | "About 1 minute" | not run | 1 |
| `demo-dual` | "About 1.5 minutes, at most about 2" | not run | 1.5 |
| serial | "About 2 minutes" (the script's HOW LONG) | not run | 2 |
| **Total** | | | **about 21** |

---

## The commands — in this order

```bash
tools/bench-run.sh t0-stopreason   # 1: the right wheel: stop reasons, then the ramp tests at powers 50 and 25; one abrupt e-stop
tools/bench-run.sh t0-api          # 2: NOTHING MOVES. Every API setting with good and bad values; about 20 s
tools/bench-run.sh dual-start      # 3: 10 starts; at every start both wheels turn a little one way and back
tools/bench-run.sh dual-d          # 4: stops dead, holds an e-stop, lowers the current limit; twice switches the platform off while spinning
tools/bench-run.sh dual-reg        # 5: two turns by distance, then one wheel faulted on purpose and the same power sent again, twice
tools/bench-run.sh dual-kick       # 6: one wheel at a time, up through four speed steps to about 300 rpm and back down
tools/bench-run.sh dual-fault      # 7: FAULTS FORCED AT SPEED, one wheel at a time; one may STOP DEAD; about 6 min
tools/bench-run.sh dual-pack       # 8: NOTHING MOVES. Hands off 60 s, then unplug/replug the sensor Powerpole AT THE PACK twice, when told
tools/bench-run.sh demo-single     # 9: the single-motor demo on the RIGHT wheel: wiring walk, 15 s forward and 15 s reverse at full power
tools/bench-run.sh demo-dual       # 10: the two-wheel demo: wiring walk, 1 ft, two 15 s steered drives, each wheel alone 15 s at full power
# 11: the serial path, below -- after desk items 1 and 2 have landed
```

**No run depends on another run's result. Nothing is rewired until step 11.**

### Step 11: the serial path (PL-148, PL-154, PL-157), host-driven, wheels up

**How it is wired and run.** Sources: `SERIAL-CONTROL.md`, "Wiring the Serial Connection";
`src/isp_steering_serial.spin2` (GW_RX2 57, GW_TX2 56, GW_BAUDRATE 624_000); the `serial_certify.py` docstring.
- The P2 loads over the PropPlug as usual.
- The host (an RPi or a PC) talks to P56/P57 at 624,000 baud.
- The script runs nine cells and writes its own log on the host.

**Once, before the visit, at the host:**
- **Serial port.** An RPi on `/dev/serial0`, the documented host, with its UART set up per `SERIAL-CONTROL.md`,
  "Configuring your RPi". Or a PC with a 3.3 V TTL USB-serial adapter.
- **pyserial.** `python3 -m serial.tools.list_ports` must run. pyserial is not in `pythonSrc/requirements.txt`. On
  Raspberry Pi OS install it with `sudo apt-get install python3-serial`; elsewhere with `pip3 install pyserial`.
- **The script.** Copy `pythonSrc/serial_certify.py` from the pulled tree to the host and `chmod +x` it.
  `./serial_certify.py --dry-run` prints the plan and opens no port.

**At the bench:**
1. **Wire three leads, ground first.**
   - Host GND to the P2 GND near P56/P57. On an RPi that is header pin 6.
   - Host Tx to P2 **P57**. On an RPi that is pin 8, GPIO 14.
   - Host Rx from P2 **P56**. On an RPi that is pin 10, GPIO 15.
2. **Load the P2**, on the Mac, from `src/`:
   ```bash
   pnut-ts -l -d -D BENCH_CFG isp_steering_serial.spin2
   pnut-term-ts -u -r isp_steering_serial.bin
   ```
   - Leave the terminal open.
   - It must print `* Serial I/F to dual motor platform`, then `* command loop *`. The P2 now waits for the host's
     ident answer.
   - If it prints `* ERROR motors did not start: a start check failed` (PL-120), close the terminal and load once more.
3. **Run the script on the host:**
   - On an RPi: `./serial_certify.py --drive-voltage PWR_18p5V`.
   - On a PC: `./serial_certify.py --port <the adapter's port> --drive-voltage PWR_18p5V`.
   - It answers the waiting ident and reads that as a fresh start.
   - **Hands off.** Both wheels turn at power 30 through three timed cases, 45 s in all, and checkwiring turns them a
     little. About 2 minutes.
   - It ends with `SER-SUMMARY,pass,..,fail,..,nomeas,..,abort,NONE`.
4. **Close the pnut-term-ts session.** Bring back `serial-certify_<YYMMDD-HHMMSS>.log` from beside the script on the
   host, with the P2's log from `src/logs/`.

**Panic:** battery disconnect. Ctrl-C makes the script send `stopmotors` and `settimeout 0`, but do not rely on it.

---

## What each load decides

Every criterion below is the one in source, quoted as `CELL` / crit / bound (D2). The cells print their own verdicts.

| Tier | Decides it |
|---|---|
| `t0-stopreason` | **T0-25, as at pass 7:** SR-COMMANDED, SR-ATLIMIT, SR-ESTOP, SR-LINKLOST, EV-STOP, EV-LOST, EV-TOTAL, EV-2COG, ESTOPSTATUS, MOVEDONE, PERSIST.<br>**PL-52:** R20-T0-SR-COMMANDED / `NONE_OPEN_CMD_STOP` now also needs `getPower()` 15 while driving and 0 just after `stopMotor()` (record `T0-25,power`).<br>**Re-derived for the plan:** R20-T0-ROTSTOP / `RESTS_AT_LIMIT_NOT_UNARMED` and R20-T0-ODOMETER / `EACH_MOVE_OWN_DIST_ESTOP_KEEPS` at −4..+3 ticks (were ±3).<br>**PL-160, new:**<br>• R22-T0-RAMP-SHAPE / `JERK_LIMIT_ARRIVE_NO_CROSS`: each judged pass's acceleration within max(jerk_up, jerk_dn) of the last and inside its limit; a = 0 from the pass after arrival; no overshoot; the stop never through zero.<br>• R22-T0-RAMP-REVERSE / `CROSSES_ZERO_NEVER_STOPPED`.<br>• R22-T0-RAMP-UNWIND / `UNWINDS_AT_JERK_IN_TAU`: to 0 in ceil(a / Jx) passes (one more if read a pass late), within RAMP_TAU_MS.<br>• R22-T0-STOPPLAN-C / `CRUISE_STOP_RESTS_AT_LIMIT`: −5..+4 ticks, −6..+4 ms.<br>• R22-T0-STOPPLAN-M / `MIDRAMP_STOP_RESTS_AT_LIMIT`: −4..+3 ticks, −6..+4 ms |
| `t0-api` | Every family at `BAD_CALLS_ZERO` = 0.<br>**PL-14:** R20-T0-API-PERSIST includes a start at 14.8 V read back through `getDriveVoltage()`, then a restart at DRIVE_VOLTAGE.<br>**PL-51:** R20-T0-API-STEER includes the distance-speed set and read-back rows.<br>**PL-160:** R22-T0-API-RAMPDEF reads `getAcceleration()` 1_000, `getDeceleration()` 1_470 and `getRampingValues()` 71 / 33_958 / 104 / 49_918 on the bench wheel. R20-T0-API-ACCEL and PERSIST judge the four longs as the two limits and their jerks |
| `dual-start` | **PL-162:** R19-DUAL-PACK-X / `PACK_AS_CONFIGURED`, 0 bad.<br>**Under the generator and the overlay:** R19-DUAL-WALK-X / `WALKS_FAILED`, 0 (desk item 3 is about this cell).<br>HEALTH-X, PROBE-X, RZSPREAD-X, NOREFUSE, RETRY, EV-WALKGUARD, EV-HALLMISSED and R20-T0-EV-LATE: 0 bad, as before.<br>**PL-161, read not judged:** each lifetime's `BM-FRONTST` (late passes, `max_us`). PL-161's negative is "the dual-start lifetimes' max still one drive pass (~520 µs) above their min" |
| `dual-d` | **PL-161:** R16-DUAL-FRONTST-D / `FRONT_LOOP_HEALTH`, both forms: late ≤ 0, the longest pass under one ms (D_FRONT_PASS_TICKS_HI = TICKS_PER_MS), and the stack high-water under its object's allocation. **Note:** PL-161's "under 950 µs" is not this cell's bound. 950 µs is FRONTST-EV's, in `dual-fault`.<br>**PL-145:** R16-DUAL-TIMESTOP-D and WTIMSTOP-D / `FIELD_ZERO_BY_LIM`, every driver reading DCS_STOPPED within **−6..+6 ms** of the deadline (was −4..+7). `BM-TIMESTOP`'s `zero_ms` is judged; `rest_ms` is printed only; `late_pass` tells an overrun apart.<br>**PL-146:** R20-DUAL-EV-FOLDBACK / `FOLD_EV_PAIRED`, 0 bad; FOLDBACK-D L/R / `FOLDBACK_HELD`.<br>**PL-144:** R20-DUAL-PATH-HUNT / `PAIRS_IN_ONE_LOG`, exactly 1.<br>**As before:** ESTOP-D / `ESTOP_LATCHED`, LOCKSTEP-D / `WHEELS_TOGETHER`, HOLDSET-D / `FIELD_SETTLES_HELD`, NOTFOL-D / `NOT_FOLLOWING`, CMDTMO-D and WCMDTMO-D / `TIMEOUT_STOPPED`, R20-DUAL-RESTCOAST / `KEPT_PCT_OF_COAST` ≥ 80 |
| `dual-reg` | R17-DUAL-TURNDIST-B / `EACH_AT_OWN_LIMIT`, **0..3 ticks** (was 0..2: the plan's early tick).<br>R16-DUAL-FLTRETRY-B / `SAME_POWER_AGAIN`.<br>R17-DUAL-FLTCAUSE-B / `CAUSE_IS_LAG` |
| `dual-kick` | R21-DUAL-TRKICK-T / `KICK_PEAK_EXCESS`, 0..50 mV per wheel. The stimulus is unchanged; only the ramp between rungs is new. Pass 7 read 16 / 13 |
| `dual-fault` | R19-DUAL-RESYNC-X / `RESYNC_STOPPED`: exactly one re-sync; FC_LAG; no DCS_FAULTED; SPIN_DN then STOPPED; the hall rate falling; rest within FR_RAMP_LO_PCT..FR_RAMP_HI_PCT (50..150 %) of `frRampPredMs()`, which is 1_088 ms at 80 × 10⁶.<br>R20-DUAL-SR-FAULT / `RESYNC_SR_AND_EV`, 0 bad.<br>R19-DUAL-PLATSTOP-X / `OTHER_WHEEL_PCT`, 0..10 %.<br>R20-DUAL-FRONTST-EV / `BURST_PASS_950US`.<br>The other X cells, as before |
| `dual-pack` | **PL-162:** R20-PACK-ABSENT / `UNPLUG_NOT_ABSENT`, 0 bad of 2 cycles.<br>R20-PACK-METER / `CAL_POINT_MV`, 0..100 mV (PK_AGREE_MV); SECOND_POINT stays NOMEAS.<br>R20-PACK-EV / `PACK_STEADY_NO_EV` and `PACK_UNPLUG_EV`, 0 bad |
| `demo-single` | No sign-off cells. The demo states its own expectations: `* start checks` with no FAILED line; `* wiring: ok`; each drive's `* stopped:` reads **SR_AT_LIMIT** ("5. expect SR_AT_LIMIT: the time limit was reached"); no `* ERROR ... refused`; no `* TIMEOUT`; then `* DONE` |
| `demo-dual` | As `demo-single`, for both wheels: `* wiring: LEFT ok, RIGHT ok`, and every `* stopped: LEFT SR_AT_LIMIT, RIGHT SR_AT_LIMIT` ("expect SR_AT_LIMIT: the distance was reached") |
| serial | **PL-154:**<br>• R20-SER-LATENCY: `REPLIES_WELL_FORMED` 20 of 20; `MAX_ROUND_TRIP` 0..the bound (1 ms idle poll + wire time + 50 ms read poll, about 52 ms at 624,000; printed in `SER-LATENCY-PLAN`).<br>• R20-SER-NUMPARSE: `NON_NUMBERS_REFUSED` 0 of 7; `REFUSED_CHANGED_NOTHING`, `NAMES_POSITION` and `VALID_STILL_WORK` TRUE.<br>**PL-148:**<br>• R20-SER-ERRREPLY: `RANGE_NAMES_VALUE`; `REFUSAL_CODE` −1016; `REFUSAL_NAMES_CMD_AND_ERR`; `VALID_NOT_OK` 0.<br>• R20-SER-TIMEOUT: `*_RUNNING_BEFORE_MS`; `*_AT_REST_BY_BOUND` (5_000 + 2_500 ms); `*_REASON_LINK_LOST` (46 46); `*_ERR_TIMEOUT` −1019, for drivepwr and drivedist. Its negative: `RESEND_MAX_GAP` 0..4_999 ms, `RESEND_KEPT_RUNNING`, `RESEND_NO_TIMEOUT_ERR` 0.<br>• R20-SER-VOLT: `ENUM_IS_CONFIGURED` 6, `MV_IS_NOMINAL` 18_500.<br>• R20-SER-FAULTRESP: `DEFAULT_MODE_GRADED` 1 and `DEFAULT_BRAKE_PCT` 10 on a fresh start; `SET_GET_MISMATCHES` 0; `REFUSED_CHANGED_NOTHING` 0; `DEFAULT_RESTORED`.<br>• R20-SER-PROTCLEAR: `GETPROT_NONE`, `PROTCLEAR_HARMLESS`, `PROTCLEAR_KEEPS_ESTOP`; `LATCHED_STOP_RELEASED` NOMEAS by design.<br>**PL-157:**<br>• R20-SER-GETTERS: `GETTERS_MALFORMED` 0; `GETTERS_OUT_OF_RANGE` 0; `GETTERS_COUNT_ENFORCED` 6 of 6; `CHECKWIRING_VERDICT_READ`; `STARTCHECKS_REFUSED_RUNNING`; `STARTCHECKS_OPT_OUT_STARTS` NOMEAS by design.<br>• R20-SER-RAMP: `DEFAULT_DECEL_POSITIVE` 1..10_000; `SET_GET_MISMATCHES` 0; `REFUSED_CHANGED_NOTHING` 0; `GETTERS_COUNT_ENFORCED` 2 of 2. `DEFAULT_ACCEL_NO_SINGLE_RATE` is **0 in the script today and must become 1_000** (desk item 2) |

**Not covered by any cell on this sheet, named:**
- **PL-161's DRIVER_REV 39 negative, "a PWM frame overrun or ADC sample loss in the nine frames after a drive pass
  (loop_dtcks)".** No cell judges the planner's frame slack. The evidence the run gives for free is the EV-HALLMISSED
  counts and `loop_ticks` in the `BM-ABIS2` dumps.
- **The same at 160 MHz.** No tier runs below 200 MHz; the README names 270 MHz as the tested clock.

## After the visit

1. Write one analysis per set of logs, following `DOCs/procedures/BENCH-RUN-PROCESSING.md`. That includes
   `serial-certify_*.log`.
2. Close every punch-list item its cells certify, and re-count the burn-down.
3. Re-cut the floor sheet to SRC_REV 59 / FMT 38 / DRIVER_REV 39. The floor run is then the last visit.

---

## Optional, Stephen's call: a Rev A block for PL-163

| | |
|---|---|
| **What it would certify** | PL-163's negative: with `testSetCurrentLimits(2, 2)`, a driven, unloaded wheel at the duty floor on Rev A must count **no** `foldback_frames`. The pre-fix driver counted every frame below about 2.7 A |
| **Which tier** | **None as built.** No tier sets a 2 A limit on a free wheel and reads `foldback_frames`. `dual-d`'s limit steps are 8 A (FOLDBACK), 20/8 A (DERATE) and 1 A (BLOCKED, a stall on purpose), and t0 drives at the default limits. A pointed cell has to be built first, on the arbiter's order |
| **Board swap** | Battery off. Swap one Rev B board for a Rev A on the same headers. The bench config notes that both revisions use the same pin mapping, and it reads both boards as BRD_AUTO_DET, so there is no config edit. Battery on, run, then swap back before anything else (the floor run is Rev B). Swapping the P16 board also moves PL-120's suspect board, so note which board went back |
| **Minutes** | About 1 to run a single-wheel leg, plus two swaps at his pace (not measured on this rig) |
| **If not done** | PL-163 stays open past 6.0: fix built, not certified on hardware |

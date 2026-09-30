# Visit 10 — run sheet, the release-candidate pass (wheels up): certify everything built, so only the floor run remains

**Task:** «#3613» runs it. **Burn-down:** `DOCs/PUNCH-LIST.md`, "Release burn-down".
**Last record:** `DOCs/analyses/bench/2026-09-26/pass7/VISIT-10-PASS7-EVALUATION.md` (DRIVER_REV 35). Pass 8's sheet was
withdrawn before it ran; its loads are folded in here.
**Stephen's ruling, 2026-09-26:** serial and demo testing come after a release-candidate driver. This is that pass, so
both are in it.

---

## Bench visits remaining to 6.0

| # | Visit | Closes | Run length |
|---|---|---|---|
| 1 | **This pass**: release candidate, wheels up | PL-14, 51, 52, 144, 145, 146, 161, 162 (pass 8's items). PL-160's wheels-up half (the generator's R22 cells and every stop re-derived for it). PL-149 (the demos). PL-148, 154, 157 (serial). PL-163 if the optional Rev A block runs | about 25 min of run, plus the serial wiring |
| 2 | **The floor run** (last): `VISIT-6B-FLOOR-RUNSHEET.md`, tier `dual-spin` | PL-93, 95, 106, 132, 150, PL-111's API half, and PL-160's feel under load | about 14 min of run, about 40 at the rig |

**Still open after both visits:** PL-120 (a watch item, not a release item); PL-163 if the Rev A block is skipped; PL-111's
serial half (a latched protective stop cleared over serial: no visit latches one under the serial top level); PL-160's
owner questions Q4 and Q5; the ancillary list.

---

## ⛔ First: PUSH, then pull at the bench

`git log --oneline -1 -- src/` at the bench must show **b3df833** or later: DRIVER_REV 46, test_bench_t0 SRC_REV 27,
test_bench_dual SRC_REV 61 / FMT 38.

**What changed under every tier since pass 7's binaries (cd6f1b7, DRIVER_REV 35):**
- 36: fold-back only on a driven bridge; the pack sampled once per slot.
- 37: driver-dependent requests answered on a later pass; fold-back net of the rest offset.
- 38: the jerk-limited ramp generator shapes every ramp, stop and reversal.
- 39: the driver plans and publishes its own stop (status run 22 → 24).
- 40: walk band 3..11 and the walk on the built-in ramp; per-board walk guard; FOLD_MIN_MV; unbiased current and
  rest zero; derived REST_ZERO bands; serial builds for the rig and ends each reply in one LF.
- 41–45: memory reduction WP1–WP5, each proved equivalent to DRIVER_REV 40 by `tools/pasm_equiv`; the first-pass
  err_ fix; ERR_BAD_MOTOR_TABLE (−1022) at start.
- 46: setRampingValues() / getRampingValues() removed; the steering ramp setters change neither wheel on a refusal.

Every cell in every tier below runs against these.

## ⭐ Before anything: note the time you connect the pack

**Write down the clock time you connect the battery**, or that it was already connected (a `pack-connect*.txt` file's
creation time does this). PL-120 watch.

## Check the banner before reading anything else

| Load | Every banner / build record must read |
|---|---|
| `t0`, `t0-stopreason`, `t0-api` (and `t0-reva`) | `* test_bench_t0 -- ... -- src_rev 27`; `t0-api` also `T0-26,begin,wheel,RIGHT_P16,driver_rev,46` |
| every `dual-*` | `BM-BANNER,...,src_rev,61,fmt,38,part,<START / D / REG / KICK / FRESP / PACK>` and `BM-BUILD,...,drv_rev,46,...` |
| `dual-pack` | `BM-PKBUILD,...,fitted,TRUE,pin,0,cal_pm,1_012,calibrated,TRUE` |
| `demo-single`, `demo-dual` | no demo prints a revision, so the SHA check above is their identity. `demo-dual` opens with `* dual motor demo`; `demo-single`'s first line is `* start checks: checked ...` |
| serial | P2 terminal: `* Serial I/F to dual motor platform`, then `* command loop *`; host: `SER-BANNER,script,serial_certify.py,...,baud,624000,drive_voltage,PWR_18p5V,dry_run,FALSE` |

---

## Tier selection: every tier answers a question of its own about DRIVER_REV 36–46 (P10), or it is out

| Tier | | The question no other included tier answers, or why it is out |
|---|---|---|
| `t0` | **IN** | DRIVER_REV 40's unbiased rest zero (R16-T0-RESTZERO, ±10 mA on Rev B), and 46's ramp restore through the mm/s² setters (R17-T0-ACCEL now also judges the restored limits). Nothing moves |
| `t0-stopreason` | **IN** | The generator's shape pass by pass (the only tier that samples `drv_accel_now`), a reversal through zero, the unwind, the stop plan at cruise and mid-ramp; PL-52; and **R22-T0-FRAMESLACK**: no PWM frame overruns while the driver plans its stop (PL-161's DRIVER_REV 39 negative) |
| `t0-api` | **IN** | Every API contract through DRIVER_REV 37's in-flight request service and 46's API; the built-in ramp (RAMPDEF); PL-14 (start voltage); PL-51 (steering distance speed) |
| `dual-start` | **IN** | Ten starts with the run image loading over the start image (42), the re-derived walk band (40) and per-board guard; the table check at every start (44); PL-162 PACK-X; each lifetime's front-cog worst pass |
| `dual-d` | **IN** | PL-161 FRONTST-D, PL-145 TIMESTOP, PL-146 EV-FOLDBACK, PL-144 PATH-HUNT; the e-stop release in flight (37); the stall hold under the generator |
| `dual-reg` | **IN** | Turn by distance on the driver's plan (TURNDIST, 3 ticks); a FAULTED wheel's two-stage in-flight clear (FLTRETRY) |
| `dual-kick` | **IN** | The speed-change kick with every change now a jerk-limited ramp (PL-160's named negative) |
| `dual-fault` | **IN** | The default fault response ramping to rest on the generator (RESYNC-X); the partner stop; the only 950 µs cell, FRONTST-EV |
| `dual-pack` | **IN** | PL-162 PACK-ABSENT on the steady reference; the per-slot sampler against the meter |
| `demo-single`, `demo-dual` | **IN** | PL-149: the shipped demos end to end on the release candidate |
| serial (not a bench-run tier) | **IN** | PL-148 / 154 / 157, and the reply framing fixed at DRIVER_REV 40 |
| `t0-reva` | **OPTIONAL** | PL-163, Stephen's call (the block at the end) |
| `t0-hand`, `t0-stopmode` | OUT | Hall counting and stop states unchanged; answers on disk |
| `dual-a`, `dual-b`, `dual-c`, `dual-limits` | OUT | Characterisation, or a question an IN tier asks on the same path (TAKE-A → RAMP-UNWIND; STOPLIM-B → TURNDIST-B; STPDECEL-C → STOPPLAN-C/-M). FAULTB and LIMRAMP now set their ramps in mm/s² (SRC_REV 61): an instrument change, not a driver question |
| `dual-clock-*`, `dual-start-nowalk/-phaseneg/-swapneg`, `dual-fault-rightfirst`, `dual-lead/-align/-brake/-ui`, `panel`, `spin*`, `detect*`, `char`, `scan*` | OUT | Nothing under them changed, or characterisation / attended UI |
| `dual-spin`, `dual-floor` | OUT | The floor run (visit 2) |

---

## The visit, declared

| | |
|---|---|
| **Purpose** | **Certification** of the release-candidate driver (DRIVER_REV 46) wheels up, the release demos and the serial path |
| **Hardware risk** | • `t0`: nothing is driven; motors are started.<br>• `t0-stopreason`: the right wheel at power 15, one **abrupt e-stop**, then spun to power 50, reversed through zero, stopped by limits mid-ramp.<br>• `t0-api`: nothing moves.<br>• `dual-start`: each start twitches the wheels; each wiring walk turns them 3.5 cm each way.<br>• `dual-d`: **wheels stop dead**, an e-stop is held, a wheel is stalled on a lowered limit, and twice the platform is switched off while spinning.<br>• `dual-reg`: half-power turns; **one wheel faulted on purpose**, twice.<br>• `dual-kick`: one wheel at a time to about 300 rpm commanded.<br>• `dual-fault`: **faults forced at speed**, including a phase short that **stops a wheel dead**.<br>• demos: **full power, 15 s at a time**.<br>• serial: power 30, and checkwiring.<br>**Wheels up throughout. Panic: physical battery disconnect.** |
| **Who acts** | Hands-off except: `dual-pack` (unplug and replug the sensor Powerpole twice, when told); serial (wire three leads, run one host command). `t0-reva` is superseded (see the end) |
| **Runs that carry state** | None across runs. If PL-120 strikes, `t0-stopreason` waits up to 3 min for the right wheel; `dual-fault` pauses up to about 2 min, up to twice. The serial run is last |
| **Run length** | About 25 minutes of run (table below), plus the serial wiring. Add up to 3 min (`t0-stopreason`) and 2.5–4.5 min (`dual-fault`) if PL-120 strikes |
| **Repeatability** | All repeatable and idempotent |
| **Variant matrix** | Rev B ×2, the paired 6.5in hubs, 18.5 V pack (sensor on P0), 270 MHz. `test_bench_t0` T0 / T0-25 / T0-26; `test_bench_dual` parts START, D, REG, KICK, FRESP, PACK. Demos under `-D BENCH_CFG`. Serial top level `-d -D BENCH_CFG` with `pythonSrc/serial_certify.py` |

| Load | Minutes (the tier's own text; pass 7's log-to-log time where the text gives only a cap) |
|---|---|
| `t0` | about 1 (estimate: the tier states none) |
| `t0-stopreason` | 2 |
| `t0-api` | 0.5 |
| `dual-start` | 1 |
| `dual-d` | 2 |
| `dual-reg` | 1 |
| `dual-kick` | 2 |
| `dual-fault` | 6 |
| `dual-pack` | 2 |
| `demo-single` | 1 |
| `demo-dual` | 1.5 |
| serial | 2 |
| **Total** | **about 22 of run; about 25 with one compile per load** |

---

## The commands — in this order

```bash
tools/bench-run.sh t0              # 1: NOTHING DRIVEN. Tier 0: API, board detection, the rest zero
tools/bench-run.sh t0-stopreason   # 2: the right wheel: stop reasons, then the ramp tests at powers 50 and 25; one abrupt e-stop
tools/bench-run.sh t0-api          # 3: NOTHING MOVES. Every API setting with good and bad values; about 20 s
tools/bench-run.sh dual-start      # 4: 10 starts; at every start both wheels turn a little one way and back
tools/bench-run.sh dual-d          # 5: stops dead, holds an e-stop, stalls a wheel on a lowered limit; twice switches the platform off while spinning
tools/bench-run.sh dual-reg        # 6: two turns by distance, then one wheel faulted on purpose and the same power sent again, twice
tools/bench-run.sh dual-kick       # 7: one wheel at a time, up through four speed steps to about 300 rpm and back down
tools/bench-run.sh dual-fault      # 8: FAULTS FORCED AT SPEED, one wheel at a time; one may STOP DEAD; about 6 min
tools/bench-run.sh dual-pack       # 9: NOTHING MOVES. Hands off 60 s, then unplug/replug the sensor Powerpole AT THE PACK twice, when told
tools/bench-run.sh demo-single     # 10: the single-motor demo on the RIGHT wheel: wiring walk, 15 s forward and 15 s reverse at full power
tools/bench-run.sh demo-dual       # 11: the two-wheel demo: wiring walk, 1 ft, two 15 s steered drives, each wheel alone 15 s at full power
# 12: the serial path, below
# 13: SUPERSEDED 2026-09-30 -- t0-reva runs on the Rev A platform instead; see the end
```

**No run depends on another run's result. Nothing is rewired until step 12.**

### Step 12: the serial path (PL-148, PL-154, PL-157), host-driven, wheels up

Sources: `SERIAL-CONTROL.md` ("Wiring the Serial Connection"); `src/isp_steering_serial.spin2` (GW_RX2 57, GW_TX2 56,
GW_BAUDRATE 624_000); the `serial_certify.py` docstring.

**Once, before the visit, at the host:**
- **Serial port.** An RPi on `/dev/serial0` with its UART set up per `SERIAL-CONTROL.md`, "Configuring your RPi"; or a PC
  with a 3.3 V TTL USB-serial adapter.
- **pyserial.** `python3 -m serial.tools.list_ports` must run (Raspberry Pi OS: `sudo apt-get install python3-serial`;
  elsewhere `pip3 install pyserial`).
- **The scripts.** Copy **both** `pythonSrc/serial_certify.py` and `pythonSrc/P2-BLDC-Motor-Control-Demo.py` from the
  pulled tree into one directory on the host (the demo file beside the script, or R20-SER-DEMOWRAP is NOMEAS), and
  `chmod +x serial_certify.py`. `./serial_certify.py --dry-run` prints the plan and opens no port.

**At the bench:**
1. **Wire three leads, ground first:** host GND to the P2 GND near P56/P57 (RPi pin 6); host Tx to P2 **P57** (RPi pin 8,
   GPIO 14); host Rx from P2 **P56** (RPi pin 10, GPIO 15).
2. **Load the P2**, on the Mac, from `src/`:
   ```bash
   pnut-ts -l -d -D BENCH_CFG isp_steering_serial.spin2
   pnut-term-ts -u -r isp_steering_serial.bin
   ```
   Leave the terminal open. It must print `* Serial I/F to dual motor platform`, then `* command loop *`. If it prints
   `* ERROR motors did not start: a start check failed` (PL-120), close the terminal and load once more.
3. **Run the script on the host:** RPi `./serial_certify.py --drive-voltage PWR_18p5V`; PC `./serial_certify.py --port
   <port> --drive-voltage PWR_18p5V`. **Hands off.** Both wheels turn at power 30 through three timed cases, and
   checkwiring turns them a little. About 2 minutes. It ends with `SER-SUMMARY,pass,..,fail,..,nomeas,..,abort,NONE`.
4. **Close the pnut-term-ts session.** Bring back `serial-certify_<YYMMDD-HHMMSS>.log` from the host, with the P2's log
   from `src/logs/`.

**Panic:** battery disconnect. Ctrl-C makes the script send `stopmotors` and `settimeout 0`, but do not rely on it.

---

## What each load decides

The cells print their own verdicts, against the criteria in source (D2).

| Tier | Decides it |
|---|---|
| `t0` | Its cells as before, with: **R16-T0-RESTZERO** ±10 mA on Rev B (NOMEAS on any other board); **R17-T0-ACCEL**, which now also needs the limits restored exactly through `setAcceleration()` |
| `t0-stopreason` | T0-25 as at pass 7; **PL-52** in R20-T0-SR-COMMANDED (`getPower()` 15 while driving, 0 after `stopMotor()`); ROTSTOP and ODOMETER at −4..+3 ticks; **PL-160:** R22-T0-RAMP-SHAPE, -REVERSE, -UNWIND, -STOPPLAN-C (−5..+4 ticks, −6..+4 ms), -STOPPLAN-M (−4..+3 ticks, −6..+4 ms); **PL-161:** R22-T0-FRAMESLACK (the smallest `loop_ticks` above 699 clocks: every frame still waited for its ADC sample) |
| `t0-api` | Every family at 0 bad calls. **PL-14** (PERSIST: a start at 14.8 V read back); **PL-51** (STEER: distance-speed read-back); **RAMPDEF**: `getAcceleration()` 1_000, `getDeceleration()` 1_470, the four limits 71 / 33_958 / 104 / 49_918 on the bench wheel. The raw-setter rows are gone with the call |
| `dual-start` | **PL-162** R19-DUAL-PACK-X, 0 bad; R19-DUAL-WALK-X 0 (band 3..11 ticks from the library); HEALTH-X, PROBE-X, RZSPREAD-X (band −17..+36 mV, derived), NOREFUSE, RETRY, EV-WALKGUARD (the driver's per-board guard), EV-HALLMISSED, EV-LATE: 0 bad. Each lifetime's `BM-FRONTST` read, not judged |
| `dual-d` | **PL-161** R16-DUAL-FRONTST-D (late 0, longest pass under 1 ms, stack high-water in bounds); **PL-145** TIMESTOP-D / WTIMSTOP-D, DCS_STOPPED within −6..+6 ms of the deadline; **PL-146** R20-DUAL-EV-FOLDBACK 0 bad and FOLDBACK-D L/R; **PL-144** R20-DUAL-PATH-HUNT exactly 1; ESTOP, LOCKSTEP, HOLDSET, NOTFOL, CMDTMO, WCMDTMO, RESTCOAST ≥ 80 % as before |
| `dual-reg` | R17-DUAL-TURNDIST-B 0..3 ticks; R16-DUAL-FLTRETRY-B; R17-DUAL-FLTCAUSE-B |
| `dual-kick` | R21-DUAL-TRKICK-T 0..50 mV per wheel (pass 7 read 16 / 13) |
| `dual-fault` | R19-DUAL-RESYNC-X (rest within 50..150 % of the S-curve's prediction); R20-DUAL-SR-FAULT 0 bad; R19-DUAL-PLATSTOP-X 0..10 %; **R20-DUAL-FRONTST-EV** at most 950 µs, no late pass |
| `dual-pack` | **PL-162** R20-PACK-ABSENT 0 bad of 2; R20-PACK-METER CAL_POINT 0..100 mV; R20-PACK-EV 0 bad |
| `demo-single` | `* start checks` with no FAILED line; `* wiring: ok`; each `* stopped:` reads SR_AT_LIMIT; no `* ERROR ... refused`; no `* TIMEOUT`; then `* DONE` |
| `demo-dual` | As `demo-single` for both wheels: `* wiring: LEFT ok, RIGHT ok`; every `* stopped: LEFT SR_AT_LIMIT, RIGHT SR_AT_LIMIT` |
| serial | **PL-154:** R20-SER-LATENCY, R20-SER-NUMPARSE; any reply not ending in one LF aborts the run (`REPLY_NOT_LF_TERMINATED`). **PL-148:** R20-SER-ERRREPLY, -TIMEOUT, -VOLT, -FAULTRESP, -PROTCLEAR (now also `PROTCLEAR_COUNT_ENFORCED` and `NOOP_WHILE_DRIVING`; `LATCHED_STOP_RELEASED` NOMEAS by design), and **R20-SER-DEMOWRAP**: the Python demo's own wrapper class sends every documented command and returns what the P2 sent. **PL-157:** R20-SER-GETTERS; R20-SER-RAMP with `DEFAULT_ACCEL_BUILTIN` 1_000 and `DEFAULT_DECEL_BUILTIN` 1_470 |

**Not covered by any cell on this sheet, named:** the planner's frame slack at 160 MHz (no tier runs below 200 MHz; the
README names 270 MHz as the tested clock).

## After the visit

1. One analysis per set of logs, following `DOCs/procedures/BENCH-RUN-PROCESSING.md`, including `serial-certify_*.log`.
2. Close every punch-list item its cells certify, and re-count the burn-down.
3. The floor run is then the last visit (`VISIT-6B-FLOOR-RUNSHEET.md`).

---

## SUPERSEDED 2026-09-30: the Rev A block for PL-163 (`t0-reva`)

This block was never run, and it is not to be run as written: it asked for a board to be moved between platforms, and
boards are never moved (STEPHEN 2026-09-30: *"we would never swap the rev A and B boards"*). PL-163 now certifies on
the Rev A platform, which carries two Rev A boards, wheels up, with no window (`DOCs/plans/WINDOW-FREE-BENCH-SPRINT-PLAN.md`
§3, «#3629»). The instructions for that run are in `DOCs/analyses/bench/VISIT-6B-FLOOR-RUNSHEET.md`.

| | |
|---|---|
| **What it certifies** | R22-T0-REVA-FOLD: at a 2 A limit, a driven, unloaded Rev A wheel at the duty floor folds back on **no** frame (the pre-fix driver folded every frame). R22-T0-REVA-FOLDPOS: gripped by hand at the same limit, it **must** fold (the positive control). Both carry over to the Rev A platform run |

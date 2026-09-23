# Panel certification -- 2026-09-22 23:37-23:42: BOTH PANELS DRAW, t0 REPORTS 24 OF 24; T0-24 exposes two new defects

Three tiers run by Stephen through `tools/bench-run.sh`, the first pass with `-u` on every run (`8b94f60`)
and the first on the PL-114 fix (`f34e6fd`). Evaluated under `DOCs/procedures/BENCH-RUN-PROCESSING.md`.
Task «#3585».

| Tier | Log / USB capture | Binary, bytes | Rebuilt (UTC) | Source |
|---|---|---|---|---|
| `t0-hand` | `debug_260922-233736.log` / `usb-traffic_260922-233735.log` | `test_bench_t0.bin`, 34,276 | 2026-09-23 05:37:35 | `4d5772b` |
| `t0-stopmode` | `debug_260922-233857.log` / `usb-traffic_260922-233856.log` | `test_bench_t0.bin`, 37,065 | 2026-09-23 05:38:56 | `4d5772b` |
| `t0` | `debug_260922-234144.log` / `usb-traffic_260922-234143.log` | `test_bench_t0.bin`, 42,371 | 2026-09-23 05:41:43 | `4d5772b` |

Each size equals a fresh `-d -D BENCH_CFG -D BENCH_QUIET [-D T0_HAND | -D T0_STOPMODE]` build of `4d5772b`,
byte for byte. The three failing 2026-09-22 runs that PL-114 cites (21:58-22:00) are parked here too.

**Outcome.** All three sessions ended on `DEBUG_END_SESSION`: 23:38:14, 23:40:49 and 23:42:16. `t0` printed
`T0-TRAP,code,0`.

**Banner check, first.** All three print `src_rev 11`. The config line reads `motor_type_enum=0 base=16
voltage_enum=6 wheel_dia_x10=65`, which is the bench config, so `-D BENCH_CFG` reached the compiler. The tier
banners are `Tier 0: no motion` (`t0`, `t0-hand`) and `T0-24 stop-state hand test: ATTENDED` (`t0-stopmode`).

**No run sheet was written for this pass.** The acceptance conditions were stated in the hand-back that asked
for it (F6).

---

## 1 · Headline

| Learning | Carried by |
|---|---|
| **PL-114's fix works: both attended panels draw** | `t0-hand` wire: 1 `PLOT`, 3 `LAYER`, 249 `crop`, 32 `update`. `t0-stopmode` wire: 1 `PLOT`, 4 `LAYER`, 1,996 `crop`, 134 `update`. Both creates byte-identical to source |
| **`t0` reports every declared cell for the first time since PL-94** | 24 declared, 24 reporting, 30 `SIGNOFF` lines, all `PASS`, including `R17-T0-NOBOARDSTART` and `R1-T0-EXHAUST` |
| **The DBG-2 rewrite changed no record** | Every `SIGNOFF` shape identical to `debug_260919-172524.log`; the only difference is the two cells that arrive now |
| **T0-24's coast reading is blind by design** | The wheel had rested 1.3-2.4 s before the release registered on every row, so `after_ticks,0` throughout |
| **After the e-stop row, a lifted wheel did not turn under power 50** | Rows 4 and 5: `why,NOT_AT_SPEED` and `protective,-2_001` (`ERR_PLATFORM_BLOCKED`) |

---

## 3 · The measurement

### 3.1 The panels (the question this pass existed for)

**`t0-hand`.** The create arrived whole (`debug_260922-233736.log:22`):

```
`PLOT bench TITLE 'T0-12 hand-rotation anchor' SIZE 420 240 POS 60 80 HIDEXY UPDATE<CR><LF>`bench LAYER 1 't0h_bg.bmp'<CR><LF>...
```

It then took 467 key polls. Readings: `T0-12,started,hall_pin,21,hall_code,3`, and at the end
`T0-12,end,transitions,956,illegal,0,pos,-946,final_hall_code,3`.

**`t0-stopmode`.** The create `` `PLOT t0stop TITLE 'T0-24 stop-state hand test' SIZE 480 300 POS 60 80 HIDEXY
UPDATE`` arrived, followed by 1,159 key polls. The panel's action cards were read back from the crop stream:
each row's `arm`, then `POWERED` or the hand action, then `ROWDONE`.

The USB captures carry the same counts as the logs, so what was logged is what was sent.

### 3.2 `t0` -- every declared cell

```
T0-23,begin,no_board_start
T0-23,end,start_return,-1,error,-1_018,raw_motor_cog,0,baseline,7,free_after,7,claim_status,0
SIGNOFF,sf,1,bin,T0,cell,R17-T0-NOBOARDSTART,task,3570,motor,NONE,crit,REFUSED_NO_LEAK,measured,TRUE,...,verdict,PASS
SIGNOFF,sf,1,bin,T0,cell,R1-T0-EXHAUST,task,3499,motor,NONE,crit,RET_NEG_NOLEAK,measured,TRUE,...,verdict,PASS
```

| Cells | Lines | Verdicts |
|---|---|---|
| 24 declared | 30 (ZXS x4, REPEAT/DIRTY/RESTZERO x2 per board) | 30 `PASS`, 0 `FAIL`, 0 `NOMEAS` |

No line in any of the three logs carries two `CogN` prefixes. `t0-stopmode` had 4 `INIT` lines and `t0-hand` 2.

### 3.3 `t0-stopmode` -- the eight cells

```
R17-T0-HOLDPWR    TURN_RECORDS_FAULT          measured,TRUE        PASS
R17-T0-RESTCOAST  COAST_HALF_MS               measured,0  lo,150   FAIL
R17-T0-RESTSHORT  SHORT_HALF_MS               measured,0  hi,60    PASS
R17-T0-STOPGAP    COAST_LESS_SHORT_MS         measured,0  lo,100   FAIL
R17-T0-FLTCOAST   FLT_COAST_HALF_AND_FAULTED  NA                   NOMEAS
R17-T0-FLTSHORT   FLT_SHORT_HALF_AND_FAULTED  NA                   NOMEAS
R17-T0-FLTGAP     FLTCOAST_LESS_FLTHOLD_MS    NA                   NOMEAS
R17-T0-FREEREF    FREE_HALF_MS                measured,0  lo,150   FAIL
```

**Why every coast reading is 0: the instrument, not the drive.** The probe (`t0sProbe()`) starts the coast
phase at the SPACE press and ends it after 400 ms with no hall change (`T0_24_REST_QUIET_MS`). Each `coast`
record came about 380 ms after its `released` record, so the loop saw no transition at all. The panel's own
hand-tick readout, decoded from its digit crops, shows when the wheel actually stopped:

| Row | Last change of the hand count | Release registered | Wheel at rest for |
|---|---|---|---|
| 1 (hold, turned slowly) | 44 at 23:39:36.01 | 23:39:37.32 | >= 1.3 s |
| 2 (coast at rest) | 262 at 23:39:50.50 | 23:39:52.49 | >= 2.0 s |
| 3 (e-stop at rest) | 114 at or before 23:40:08.38 | 23:40:10.82 | >= 2.4 s |
| 6 (driver cog stopped, free) | 584 at 23:40:47.47 | 23:40:49.12 | >= 1.6 s |

Row 6 is the free yardstick. Its pins are released, and a brisk spin (six ticks in 106 ms at the release rate)
had stopped before the key registered. **So `after_ticks,0` is a true reading of a stationary wheel, taken
after the coast it was built to time had already happened.** Key checks ran every 112 ms (median; 81-135 ms)
against PC_KEY's ~100 ms latch. That cadence can miss a tap, but the logs cannot show whether it did (F3).

**Why rows 4 and 5 never set up:**

```
T0-24,provoke,hold_mode,FLOAT,why,NOT_AT_SPEED,note,no_offset_was_written
T0-24,row,3,set_up,FALSE,...,protective,-2_001,measured,FALSE
T0-24,provoke,hold_mode,BRAKE,why,NOT_AT_SPEED,note,no_offset_was_written
T0-24,row,4,set_up,FALSE,...,protective,-2_001,measured,FALSE
```

`-2_001` is `ERR_PLATFORM_BLOCKED` (`isp_bldc_motor.spin2:133`). The driver's blocked test (`:1895`) fires when
a commanded motor at `LAG_SOFT` or beyond shows no position change for `BLOCKED_PASSES` passes. So the driver
saw a lifted wheel that did not turn under `driveAtPower(50)`, and latched the stop inside the 4 s AT_SPEED
bound. Both powered rows, not just one, came right after the e-stop row's `emergencyCutoff()` and its teardown
`clearEmergency()`. The panel showed the `POWERED` card (hands off) on both (F4).

---

## 4 · What this means for the driver

**2a -- what it now DOES.** Nothing new. This pass certified harness and tooling only: the panels, the cell
census, and the footprint fix and gate. It licenses no driver change. **F4 may be one** -- the drive not
resuming after an e-stop is cleared would be a driver defect -- but one pass with the e-stop row always first
cannot separate that from a false-firing blocked test.

⚠ **What this does NOT license.**
- No change to `clearEmergency()` or to the blocked-motor test on F4 alone. The discriminator (section 5) comes
  first.
- No claim about the stop states. `RESTCOAST`, `STOPGAP` and `FREEREF` FAIL on the instrument, `RESTSHORT`'s
  PASS could not have failed, and the fault rows are `NOMEAS`. The driver's named bridge state per stop path
  («#3568») remains **uncertified at the wheel**.
- F4 does not answer PL-106. A blocked stop fired on a lifted rig, but possibly for the wrong reason, so it
  does not show the test working as designed.

**2b -- what it now KNOWS.** Nothing new. No sensor was integrated. The blocked test the driver already owns is
what reported F4, which is the driver knowing *something*. Whether it knew the right thing is F4's question.

---

## 5 · What this changes about the next run

Draft loads for the next attended pass. The next sheet inherits these, and must say why if it drops one.

1. **T0-24 rebuilt with the coast measured from the wheel, not the key (PL-115)**, then re-run: all six rows.
   It must show `FREEREF` coasting for more than 150 ms before any other cell is read.
2. **The F4 discriminator (PL-116).** The same binary with the powered rows before the e-stop row, one build
   flag. If they reach AT_SPEED and fault as designed, the e-stop clear path is implicated. If they are
   blocked again, the blocked test or the power-50 start is. Either way it is also the first chance at PL-106's
   provocation.
3. **The attended tiers not run since their panels were added:** `dual-ui`, `dual-brake`, `dual-floor`
   (PL-92's blast radius). The path is now proven, and the footprint gate passes them at 6,861 bytes.
   `dual-ui` certifies the PL-64 rebuild for Visit 6b.

---

## 6 · Findings register

| Id | Finding | Disposition |
|---|---|---|
| F1 | PL-114 fix certified: both panels draw; `t0` 24 of 24 | **Closed** -- PL-85 (lost verdict), PL-92, PL-94, PL-114 marked certified |
| F2 | DBG-2 rewrite left every record shape unchanged, on the wire | **Closed** |
| F3 | T0-24 times the coast from the SPACE press; the wheel is already at rest | **Punch list -- PL-115** (instrument; override rule: not fixed ahead of front-2 work) |
| F4 | After the e-stop row, a lifted wheel did not turn under power 50, and the blocked stop latched | **Punch list -- PL-116**, and next-run load 2 |
| F5 | T0-12 read 956 / -946, not a three-turn anchor | **Watch** -- no sheet asked for three turns; the 2026-09-15 anchor (270 / -270) stands. Actionable only when a sheet asks for it |
| F6 | The pass ran without a run sheet; seven attributes undeclared | **Closed as a process note** -- the next attended pass (section 5) gets a sheet |

---

## 7 · What is NOT established

- **Every T0-24 stop-state cell.** `HOLDPWR`'s PASS is a real reading: a turned wheel recorded a fault under a
  powered hold. The coast cells are instrument results (F3), and the three fault cells are `NOMEAS`.
- **Whether drive resumes after `clearEmergency()`** (F4). No certified run has driven a wheel after one:
  dual-d's `DST_ESTOP_CLEAR` checks only that the platform stays at rest.
- **Whether PC_KEY taps are missed at a 112 ms check cadence.** Plausible, not observed.
- **T0-12's count against a known number of turns** on this binary. It was not asked for.

## 8 · Questions left open

| Question | What settles it | Owner |
|---|---|---|
| Does drive resume after an e-stop is cleared, or does the blocked test false-fire? | Load 2 in section 5 | PL-116, «#3607» |
| Does each stop path put the wheel in its named bridge state? | T0-24 with PL-115 fixed | PL-115, «#3607» |

## 9 · FRONTS ledger, after

```
FRONTS  (after this run)
  completion   driver last changed 5 commits ago (03509db); this pass changed and licensed nothing in it
  information  3 loads ready and unrun since their panels were added: dual-ui, dual-brake, dual-floor
               (plus the two T0-24 loads of section 5, once PL-115 and the reorder flag are built)
  robustness   sensors the DRIVER acts on: halls y  current y  back-EMF n (deferred)  follow y (the
               blocked test, isp_bldc_motor.spin2:1895, blockedPasses at :4340) -- unchanged by this pass
```

*Front by front: **completion** did not advance; this pass certified tooling. **Information** advanced: the
panel path is proven, which makes three attended tiers runnable. **Robustness** did not advance: nothing
integrated, though F4 is the first time the driver's blocked test has fired on this rig.*

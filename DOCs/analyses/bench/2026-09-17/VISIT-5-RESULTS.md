# Visit 5 — Results

**Run:** 2026-09-17, 17:29–17:44 local. Unattended, wheels lifted, Rev B, both motors, 270 MHz.
**Sheet:** `DOCs/analyses/bench/VISIT-5-RUNSHEET.md` · **Task:** «#3565» · **Tree:** `a4a5aa4`
**Pack:** 20.57 V at start, 20.36 V at end (18.5 V nominal 5S, STEPHEN 2026-09-17). 0.21 V sag across
the whole session.

Provenance marks per doctrine overlay P8: **MEASURED** = cites a log line · **DERIVED** = my reasoning
from traced claims · **STEPHEN** = his words with the date · *unlabelled* = the sources were read and do
not settle it.

---

## 0. The headline

**ZERO FAILED CELLS AND ZERO NOT_BUILT CELLS, across four loads and 66 cell instances.** Visit 4 ended
with 13 FAILs and 10 NOT_BUILT; every one of them is now PASS or a designed NOMEAS.

| Load | Log | Cells | PASS | FAIL | NOMEAS | NOT_BUILT |
|---|---|---|---|---|---|---|
| `t0` | `debug_260917-172913.log` | 19 | **19** | 0 | 0 | 0 |
| `dual-d` | `debug_260917-173018.log` | 15 | 13 | 0 | 2 (designed) | 0 |
| `dual-b` | `debug_260917-173141.log` | 16 | 12 | 0 | 4 | 0 |
| `dual-a` | `debug_260917-173713.log` | 16 | **16** | 0 | 0 | 0 |

Every load ended `BM-END exit,COMPLETE, trap_code,0, unrecov,0`.

**Three things remain open, and none of them is a driver defect:** the slam has no instrument (§5), the
fault-API provocation still trips the harness's own current abort (§4c), and t0's shape corrupts its own
log (§2).

---

## 1. Banner check

MEASURED. All four loads emitted and matched the sheet.

| Log | Tier | Banner |
|---|---|---|
| `debug_260917-172913.log` | t0 | `src_rev 3` (L19) ✅ |
| `debug_260917-173018.log` | dual-D | `src_rev 14, fmt 5, part D` ✅ |
| `debug_260917-173141.log` | dual-B | `src_rev 14, fmt 5, part B` ✅ |
| `debug_260917-173713.log` | dual-A | `src_rev 14, fmt 5, part A` ✅ |

---

## 2. t0 — the tier came back, and its own shape damaged its log

### 2a. PL-74 is closed: the quiet build emits

**MEASURED**, `debug_260917-172913.log` L14–19: 40 918 bytes downloaded, `Cog0 INIT $0000_0000 load`,
`Cog0 INIT $0000_0FA8 jump`, then `* test_bench_t0 -- Tier 0: no motion -- src_rev 3`.

**All ten previously NOT_BUILT cells PASS**, and with them the whole t0 set:

| Cell | Verdict | Line |
|---|---|---|
| R4-T0-1M-TICKS | PASS | 54 |
| R16-T0-LIMKEEP | PASS | 59 |
| R16-T0-NOABORT | PASS | 86 |
| R16-T0-STRNOTSTART | PASS | 91 |
| R8-T0-ZXS ×4 (I/U/V/W) | PASS | 109–112 |
| R3-T0-STOPPED | PASS | 117 |
| R2-T0-REPEAT (L, R) | PASS | 120, 122 |
| R2-T0-DIRTY (L, R) | PASS | 130, 137 |
| R2-T0-EMPTY | PASS | 140 |
| R1-T0-START | PASS | 145 |
| R1-T0-RESTART | PASS | 152 |
| R10-T0-STOPREADY | PASS | 154 |
| R16-T0-BADGROUP | PASS | 158 |
| R16-T0-PINSKEEP | PASS | 163 |
| R16-T0-STEERCOGS | PASS | 173 |
| R16-T0-RESTZERO (L, R) | PASS | 177, 181 |
| R16-T0-NOBOARD | PASS | 184 |
| R16-T0-FRONTFAIL | PASS | 195 |
| R1-T0-EXHAUST | **PASS, recovered — see §2c** | 221 |

⭐ **The 6.0.0 error contract («#3554», «#3555») is certified**, and so are the front cog's cog
accounting («#3513»: `R16-T0-STEERCOGS`, `R16-T0-FRONTFAIL`) and the API contract fixes («#3556»:
`R16-T0-RESTZERO`, `R16-T0-NOBOARD`). **This was the last thing gating the 6.0.0 tag.**

⛔ **What is NOT established: why `SRC_REV 2` was silent.** The quiet build removes 2 866 bytes of
library debug data and the tier emits; that is a correlation and a cure, not a mechanism. See PL-74.

### 2b. STEPHEN's observation — the log is damaged by the test's own shape

**STEPHEN 2026-09-17:** *"t0 is constructed so that debug messages from cogs are overlapping causing
logging problems. … this is a test shape problem!"*

**MEASURED. Confirmed, and it is worse than "overlapping":**

```
L147  Cog1Cog1  INIT $0000_426A …
L149  CogCog1   INIT $0000_426A …
L151  CogCog1Cog0  T0-15c,baseline,7,free1,5,…
L168  [BINARY DATA: 80 bytes - displaying as hex]
L169    0000: 43 6F FF 43 6F 67 31 43 6F 67 30 … |Co.Cog1Cog0|
L221  SIGNOFF,…,R1-T0-EXHAUST,…,measured,TRUE,        <- record ends here
```

**Every damaged line is adjacent to a `CogN INIT` burst.** The bursts come from T0-8, T0-15b and T0-22,
each of which starts and stops **seven spacer cogs**, and from T0-15's restart and T0-19's three-cog
steering start.

⭐ **IT IS NOT THE TERMINAL. The truncation is on the wire.** MEASURED, `usb-traffic_260917-174323.log`
L1266, which is the raw USB byte stream:

```
0020: $2C $6D $65 $61 $73 $75 $72 $65  $64 $2C $54 $52 $55 $45 $2C $0D   ,measured,TRUE,.
0030: $0A $43 $6F $67 $30 $20 $20 $54  $30 $2D $54 $52 $41 $50           .Cog0  T0-TRAP
```

The P2 emitted `…,measured,TRUE,` followed by **CR LF** and then the next record. `lo,TRUE,hi,TRUE,
units,BOOL,n,1,verdict,PASS` **was never transmitted.** The run-together prefixes are on the wire too
(USB L1217–1218 `Cog1Co`/`g1  INIT`, L1248–1249 `Cog1C`/`og0  T0-15b`).

**DERIVED:** this is PL-41's mechanism seen at wire level for the first time. DEBUG output is serialised
by LOCK[15]; a cog stopped mid-message leaves the message unterminated and the next cog's prefix is
emitted behind it. **Stephen's reading is confirmed: the cause is the test's shape**, not the driver and
not the terminal.

### 2c. The lost verdict, recovered

`R1-T0-EXHAUST` lost everything after `measured,TRUE,`. It is recoverable **by construction**:
`emitSignoffBool()` prints the `measured` field *as* the criterion result, and computes
`verdict := PASS` exactly when the instance was measured and the criterion held. `measured,TRUE`
therefore **is** PASS.

The substance is intact in the record before it (L220, and USB L1249–1255):
`T0-15b,cogs_occupied,7,start_return,-1,raw_motor_cog,0,baseline,7,free_after,7` — under cog
exhaustion `start()` returned −1 and leaked no cog (baseline 7, free after 7). **R1-T0-EXHAUST = PASS.**

⚠ **This is a recovery, not a reading, and it only worked because Stephen captured the USB stream.** The
next occurrence in a record whose `measured` field is not the verdict is unrecoverable. Filed as
**PL-85**.

---

## 3. dual-d — every Visit 4 repair confirmed

**MEASURED.** `debug_260917-173018.log`, 120 lines, `BM-END exit,COMPLETE, part,D, segs,3`.

| Cell | Visit 4 | Visit 5 | What changed |
|---|---|---|---|
| R16-DUAL-TIMESTOP-D | NOMEAS `STOP_TIMEOUT` | **PASS** | PL-83: the rest wait was as long as the limit it waited past |
| R16-DUAL-WTIMSTOP-D | NOMEAS `STOP_TIMEOUT` | **PASS** | PL-83, same fix, wheel form |
| R16-DUAL-FRONTST-D BOTH | **FAIL** (`stack_hi 128 == stack_of 128`) | **PASS** | PL-75: the steering object's own 256-long stack |
| R16-DUAL-DERATE-D RIGHT | **FAIL** (2 602 ms vs 500–2 500) | **PASS** | PL-80: judge derated-and-restored, not an underivable window |
| R16-DUAL-LAGBND-D LEFT | **FAIL** (115 vs 110) | **PASS** (116 vs 124) | PL-78: the bound is the driver's own fault test |
| R16-DUAL-DERATE-D LEFT | NOMEAS | NOMEAS | designed — a lifted wheel need not reach the limit |
| R16-DUAL-BLOCKED-D | NOMEAS `NOT_BLOCKED` | NOMEAS | designed — a lifted wheel cannot be blocked |
| all others | PASS | PASS | — |

⭐ **PL-76 is closed by absence, and the absence is the measurement.** The Visit 4 log carried five
`driveAtPowerEx() motor not started` / `clearEmergency() -1_007` lines in the LIMIT segment's
single-wheel half. **This log contains none.** The ternary sweep removed them, exactly as predicted, and
the steering half — which never had them — is the unchanged control.

⭐ `BM-LAG` now prints `hold,100 fault,125` beside `max_err` and `hi` (L95–96), so the whole band is in
the record.

---

## 4. dual-b — the OVERSHT segment came back, and C-3 is measured

**MEASURED.** `debug_260917-173141.log`, 7 684 lines, `BM-END exit,COMPLETE, part,B, segs,3`.

### 4a. ⭐ PL-84 answered: `str_mm_x100` reads 576

**MEASURED**, L7652:

```
BM-DISTM tid,24 l_ticks,530 r_ticks,531 l_m,3 r_m,3 l_pred_m,3 r_pred_m,3
         mm_x100,576 str_mm_x100,576 agree,TRUE
```

The steering object's own travel-per-tick and the motor object's **agree**. At Visit 4 that copy held
about −544 643, which refused every `driveForDistance()` in the segment with `ERR_LIMIT_UNRESOLVABLE`
and made `getDistance(DDU_M)` return −14 640.

**DERIVED, and this is the strongest evidence PL-75 and PL-84 share one root cause:** the only change
between the two visits that touches that variable is the steering object's own 256-long stack.
`tickInMM_x100` is the second long past `taskStack` in VAR declaration order; with the enlarged stack
the value is correct and the segment runs. **Still not proof** — nothing shows an overrun wrote that
value — but the prediction was made before the run and the run met it.

### 4b. ⭐ C-3 is measured for the first time, and stops land AT their limit

**MEASURED**, L7651:

```
BM-OVERSHOOT tid,24 dist_ft,10 tgt,529 l_stop,455 r_stop,-455
             l_rest,530 r_rest,-529 l_trk,530 r_trk,531 t_stop,3_200 why,NONE
```

The platform drove 10 ft and came to rest at **530 ticks against a 529-tick target — one tick past.**

**MEASURED**, L7676: `R16-DUAL-STOPLIM-B measured,1 lo,0 hi,2 n,4 verdict,PASS` — worst case **1 tick**
over four trials.

⭐ **This certifies «#3559»'s central claim.** Before it, a distance stop overshot by about 77 ticks
(≈ 440 mm at half speed). It now stops at the limit. **This is a headline user-visible change for
6.0.0**, and it is the finding the OVERSHT segment exists for.

### 4c. What is still NOMEAS, and it is a harness stimulus problem

**MEASURED**, L7653: `BM-ABORT seg,OVERSHT tid,25 reason,ABS_CURRENT value,2_445 scope,TRIAL`, then
`BM-FLTAPI … rows,2 … why,ABORTED`.

The fault-API trial provokes a fault by writing a commutation offset **180° from the running pair on
both wheels**. That holds the field where the rotor cannot follow, and the current reaches **2 445 mV
(≈ 16 A)** within about 100 ms — past the harness's own 10 A absolute-current abort, which stops the
trial before the driver's fault test is reached.

**DERIVED: the driver is doing what a 180° offset demands.** This is not a driver defect and not a
criterion defect; it is a **provocation that is too strong for the instrument watching it**. Visit 4 had
the same abort at 2 217 mV. `R14-DUAL-FLTAPI-B` and `R16-DUAL-FLTRETRY-B` are NOMEAS for the second
visit running. Filed as **PL-86**.

`R14-DUAL-RSTPROV-B` NOMEAS (n=0) both motors is **designed**: no fault occurred, so there was no reset
to prove.

### 4d. The rest of part B

| Cell | Motor | Visit 4 | Visit 5 |
|---|---|---|---|
| R16-DUAL-STOPCUR-B | L, R | **FAIL** | **PASS** (PL-82: fixed bound, not a warming reference) |
| R16-DUAL-DISTM-B | BOTH | **FAIL** | **PASS** (PL-77 + PL-84) |
| R16-DUAL-RMPDROOP-B | L, R | PASS | PASS |
| R16-DUAL-LAGBND-B | L, R | **FAIL** (115) | **PASS** (115, 101 vs 124) |
| R14-DUAL-RAMPREST-B | L, R | PASS | PASS |
| R14-DUAL-TRACES-B | — | PASS | PASS (0 lost of 24) |

---

## 5. dual-a — every cell passes, and the slam is still there

**MEASURED.** `debug_260917-173713.log`, 15 300 lines, `BM-END exit,COMPLETE, part,A, segs,4`.
**All 16 cell instances PASS**, including the two that failed at Visit 4:

| Cell | Motor | Visit 4 | Visit 5 |
|---|---|---|---|
| R16-DUAL-NOFOLD-A | L, R | **FAIL** (compound) | **PASS** (PL-79: the fold half, judged alone) |
| R16-DUAL-RATELAW-A | L, R | *did not exist* | **PASS** (PL-79: band carries tick quantisation) |
| R16-DUAL-LAGBND-A | L, R | **FAIL** (115 vs 110) | **PASS** (115 vs 124) |
| INSTLIVE / IDLEFLT / REVB / INTEG / TRACES | — | PASS | PASS |

### 5a. ⛔ STEPHEN's observation — and the instrument cannot see what he felt

**STEPHEN 2026-09-17:** *"the ramps from dual-a some are not kicking but many still are… so your remove
kicking on ramp up is only partially working."*

**The driver fix IS in the binary.** Verified in source: `src/isp_bldc_motor.spin2:3668`,
`mov ramp_curr, ramp_min_` at `.doSpdChange`, reached from `.newRqst` once per request.

**MEASURED**, LEFT motor forward (life 22, L15161–15196), against Visit 4's same block:

| rung | 0 | 1 | 2 | 3 | 4 | 5 | 6 | 7 | 8 | 9 | 10 | 11 |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| `err` V5 | 33 | 48 | 48 | 48 | 48 | 48 | 48 | 55 | 63 | 66 | 69 | 74 |
| `err_pk` V5 | 57 | 77 | 71 | 72 | 72 | 72 | 72 | 81 | 88 | 91 | 94 | 100 |
| `err_pk` V4 | 56 | 75 | 71 | 71 | 72 | 72 | 73 | 80 | 88 | 91 | 94 | 98 |
| gap V5 | 24 | 29 | 23 | 24 | 24 | 24 | 24 | 26 | 25 | 25 | 25 | 26 |

⛔ **Unchanged, within 1–2 counts at every rung. The prediction in PL-78 — that `err_pk` would fall
toward `err` at rungs 1–11 while rung 0 stayed put — did not happen.**

⭐ **And the reason is that this table was NEVER a measurement of the slam.**

- `err` and `err_pk` are **window statistics**. `rungMeasure()` opens its window **after** AT_SPEED and
  after the settle, so the window covers steady running only. **The transition — where a kick happens —
  is over before the window opens.**
- **Rung 0 is the proof.** It is the only rung that starts from rest, so it always had the soft start and
  never had the defect. Its gap is **24**, the same as every other rung's, in **both** visits. A statistic
  that reads the same on the control and on the suspects is not measuring the difference between them.
- **DERIVED:** the ~25-count gap is the AT_SPEED duty-servo ripple. The design's own note records the
  unloaded trace swinging −22 to −70 about a set point of 42 — a peak about 25 above the mean, which is
  what `err_pk − err` reports.

**So Visit 4's "slam signature" table was window statistics read as transition statistics, and PL-78's
second half rests on it.** The driver change may be right, wrong or partial; **this instrument cannot
say**, and it could not have said at Visit 4 either.

**What Stephen felt is the evidence we have**, and it says the fix helped some transitions and not
others — which no cell in this load records.

⭐ **The measurement exists already and costs no bench time.** `rungMeasure()` arms the instrument at the
command, so the ring **already holds every sample of the transition**; `windowStats()` simply never reads
them. A `transitionStats()` over [arm … window start] gives the peak |err| during the ramp, per rung,
with rung 0 as a built-in control. Filed as **PL-87**.

### 5b. Free from the same data

**MEASURED**, `BM-RUNG3` L15163–15196 (LEFT forward), `amps_x10k` by rung:

```
rung   0     1     2     3      4      5      6      7      8      9     10     11
amps  319   437 1_246 6_692 18_302 38_051 67_289 36_412 10_023  5_333  2_794  3_381
```

Peak ≈ **6.7 A at rung 6**, falling as speed rises — back-EMF against a lifted wheel, and the same shape
Visit 4 measured. `duty` saturates at `duty_max 24_264` from rung 7 up.

`R14-DUAL-REVB-A` PASS, **0 of 12 starts misdetected** on both motors — «#3500» holds across another
twelve start/stop cycles.

---

## 6. What this visit changes

1. **The 6.0.0 tag is unblocked.** The error contract has run-time evidence; nothing else was gating it.
2. **«#3559» is certified**: a distance stop lands one tick from its limit, where it used to overshoot
   by about 77.
3. **PL-75 and PL-84 are one finding in practice.** The stack fix removed the corrupted value.
4. **Every criterion repaired in `bcc8139` reports correctly**, and the two that were repaired *and*
   could have failed — DERATE and LAGBND — passed on their merits rather than by widening.
5. **Three things stay open, none a driver defect:** the slam has no instrument (PL-87), the fault-API
   provocation is too strong for the abort watching it (PL-86), and t0's shape corrupts its own log
   (PL-85, PL-41).

---

## 7. New findings filed

| id | Summary |
|---|---|
| **PL-85** | t0's cog-start/stop bursts truncate DEBUG records on the wire; one verdict was lost and recovered only because a USB capture existed |
| **PL-86** | The fault-API trial's 180° provocation trips the harness's own 10 A abort before the driver faults; two cells NOMEAS for a second visit |
| **PL-87** | The ladder measures `err_pk` over the steady window, so no cell can see a transition kick; rung 0 reads the same as every other rung in both visits |

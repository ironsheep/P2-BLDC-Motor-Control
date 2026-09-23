# Visit 10 — run sheet (the drive ends well: the hold, the fault responses, the platform policy, startup checks)

**Task:** «#3613» runs it. **Built by:** «#3608» (hold, `524de4a`), «#3612» (platform policy, `d4c03a2`), «#3609»
(fault response, `d33b691` and `39ffc1a`), «#3610» (start checks, `340ff62`), «#3607» (T0-24, `6f2ed6f`), and the
harness parts in `6f2ed6f`. **Plan:** `BENCH-READINESS-SPRINT-PLAN.md`, the R19 section.

**Why this visit:** every R19 mechanism is built with each gate value as a settable parameter at a provisional value.
This visit **sizes those values** and certifies the mechanisms (Stephen, 2026-09-23: *"bench runs to determine gate
values is better than waiting to design algorithm"*). The new responses then go to Stephen, each with its measured
benefit, before any becomes the default.

---

## Check the banner before reading anything else

| Load | Every banner / build record must read |
|---|---|
| `dual-*` tiers | `BM-BUILD ... drv_rev,12` (the driver as built for this visit). Anything lower means an old tree was built: stop and report. The T0 harness prints no driver revision, so for the T0 tiers the check is the row layout below |
| `dual-fault` | part `FAULTRESP`; a `BM-FRBUILD` record; `BM-NOTBUILT` for `B4PULSE` only |
| `dual-start` | part `START`, segment `SKCHECK`, a `BM-SKBUILD` record; `dual-start-nowalk` also prints `BM-NOTBUILT` for the walk |
| `t0-stopmode` | `T0-24,row,...` records numbered 1 to 8, the first `hold_watch` (the hold rows exist only in this build), rows 6 and 7 powered; `-fltfirst` has rows 5 and 6 powered |

---

## The visit, declared

| | |
|---|---|
| **Purpose** | **Measurement and certification.** Measurement sizes the hold's ceiling in amps, the graded short's duty (deceleration against brake %), the rest-zero band, the lead-check thresholds and the wiring walk's power. Certification covers the hold's rise, slip and limit hand-offs, the re-synced stop, the fallback to the graded short, the platform stopping when one wheel faults, the forced-fault hook's negative control, and the stop-state coasts (PL-115). The PL-116 discriminator runs as a separate tier. |
| **Hardware risk** | `dual-fault` **faults the wheels on purpose at up to about 220 rpm commanded**. Each fault ends in the response under test: a phase short that stops the wheel dead, a free coast, a controlled ramp down, or the graded short. **The graded short regenerates into the supply, so it needs a pack, not a bench supply that cannot sink current.** Faults are forced by the driver's own test hook, not by the old offset shift that plugged the motor (PL-119). A forced fault that does not latch in 8 ms stops the wheel. The 10 A abort and the fold-back limiter apply throughout. The board cannot measure a short's own current (PL-118). `t0-stopmode` spins one wheel under power in two rows. **Wheels up throughout. Hands off in every unattended tier. Panic: physical battery disconnect.** |
| **Who can observe** | `t0-stopmode` is attended: Stephen pushes and spins the wheel as each row's panel asks, and each panel says what he should feel. The unattended tiers need nobody. **One observation is worth having near `dual-fault`:** does a 100 % graded stop sound or look like the full short? That is an observation, not a verdict. |
| **Runs that carry state** | None. Every `dual-fault` trial runs in its own driver lifetime and restores the fault response. The hold limits are TEST-USE and reset on every start. |
| **Run length** | `dual-fault` about 6 min (cap 15). `t0-stopmode`: 8 attended rows, roughly 10 min. `dual-start` under 1 min; its three attended negatives about 15 min including the rewiring. `t0-stopmode-fltfirst`: another ~10 min, only if its question is still open after `t0-stopmode`. |
| **Repeatability** | All repeatable and idempotent. |
| **Variant matrix** | Rev B, the paired 6.5in hubs, 18.5 V pack, 270 MHz, the same rig as Visit 9b. `test_bench_dual.spin2` parts FAULTRESP and START; `test_bench_t0.spin2` T0-24, with and without `-D T0_24_FLT_FIRST`. |

**New information, and what is carried.** Every load is new: none of these mechanisms has run on hardware. T0-24 has
run once (2026-09-22), and its instrument defect (PL-115) is what this rebuild fixes.

---

## The commands

```bash
tools/bench-run.sh dual-fault             # 1: the fault responses, the platform policy, the hook's negative control
tools/bench-run.sh dual-start-nowalk      # 2: ATTENDED WIRING -- B-1 (right hall connector unplugged)
tools/bench-run.sh dual-start-nowalk      # 3: ATTENDED WIRING -- B-3's negative (one right motor lead unplugged)
tools/bench-run.sh dual-start             # 4: ATTENDED WIRING -- B-5's negative (two right hall wires swapped)
tools/bench-run.sh dual-start             # 5: wiring restored -- the start checks sized over 10 starts, and the wiring walk
tools/bench-run.sh t0-stopmode            # 6: ATTENDED -- the hold rows and the stop states at the wheel
tools/bench-run.sh t0-stopmode-fltfirst   # 7: ATTENDED, only if run 6's rows 6-7 blocked again (PL-116)
```

Runs 2–4 each change one piece of wiring, battery disconnected: the procedures are under *Attended negative controls*.

---

## What each load decides, and how each can fail

Every criterion is fixed here, before the run (D2). Cells print their own verdict. The rest are judged in the report
from the named records.

### `dual-fault` — the fault responses (fault study §7)

Every fault is forced through `testForceFault()`, each trial in its own driver lifetime. Speeds are 40, 80 and
120 × 10⁶, all negative.

| Cell | Judged by | Criterion | Fails if | Control |
|---|---|---|---|---|
| **R19-DUAL-HOOKREST-X** | `BM-FRHOOK`, per motor, **first** | a forced fault at rest (hold off, bridge coasting) latches nothing; the state stays STOPPED for 500 ms | the hook faults an undriven motor | **This is the hook's own negative control.** Everything below rests on it |
| **R19-DUAL-FORCED-X** | `BM-FRTRIAL outcome`, `BM-ABORT NO_FAULT` | every requested first fault latches within 8 ms (count of misses 0) | the hook failed to fault a driven motor | HOOKREST |
| **R19-DUAL-RESTFLAT-X** | `BM-FRPHASE PRE/REST` | every phase under 50 mV p-p at rest | a channel swings with nothing turning | COASTEMF's control, measured first |
| **R19-DUAL-COASTEMF-X** | `BM-FRPHASE MOVE`, FR_SHIPPED, FLOAT, 3 speeds | every phase ≥ 50 mV p-p, crossing at the hall rate, while coasting | the phase voltages stay flat while the halls tick | RESTFLAT. This is the back-EMF a coast keeps and a short destroys (fault study F-7) |
| **R19-DUAL-SHORTTK-X** | `BM-FRSTAT`, FR_SHIPPED BRAKE against FLOAT at each speed | the short stops in fewer ticks than the coast | short ticks ≥ coast ticks at any speed | paired speeds |
| **R19-DUAL-SHORTI-X** | `BM-FRCUR`, `BM-FRWIND` | peak current rises with speed | no rise | **Expected NOMEAS** below 1 A over zero: the shunt cannot see a short (PL-118). The winding resistance is then NA |
| **R19-DUAL-RESYNC-X** | FR_GRADED 25 %, FLOAT, 80 × 10⁶ | exactly one re-sync, cause FC_LAG, never FAULTED, SPIN_DN then STOPPED, rate falling, rest within 50–150 % of the ramp's predicted time | any of those | the re-sync count read just before the fault |
| **R19-DUAL-BLUNT-X** | the second forced fault on a re-synced ramp | reads DCS_FAULTED (the fallback taken) | the fallback is not taken | — (DRIVER_REV 12's fix is what this certifies) |
| **R19-DUAL-GRADED-X** | `BM-FRSTAT f2_k`: coast, then 10, 25, 50, 100 %, hold TRUE | ticks and time to rest never rise as brake % rises, and 100 % is below the coast | a rise, or no overall fall | the coast bound (X6C) and the full-short bound (GRD100). **Sizes BRAKE_PCT_DEFAULT (25, provisional)** |
| **R19-DUAL-GRD100-X** | 100 % graded against X-2's full short at 80 × 10⁶ | within 2 ticks | differs by more | — |
| **R19-DUAL-PLATSTOP-X** | `BM-FRPLAT`, steering, power 50: LEFT faulted under FR_SHIPPED, then RIGHT under FR_GRADED | the watched wheel falls to ≤ 10 % of its earlier rate within 2 s of the other's fault | it keeps driving (PL-117's defect) | NOMEAS unless it turned ≥ 10 ticks before the fault |
| **R19-DUAL-FRREST-X** | `BM-FRREST` after each trial | FR_SHIPPED, the lifetime's brake_y, HS_OFF | a restore did not take | — |
| R19-DUAL-B4PULSE-X | — | NOT_BUILT (REPLACED_BY_X2; PL-118) | — | — |
| R14-DUAL-RSTPROV-X, -TRACES-X, R19-DUAL-NOSTALL-X, -DBGMASK-X | standard | as in every part | as in every part | as in every part |

### `t0-stopmode` — the hold rows and the stop states at the wheel (ATTENDED, right wheel)

Every action is a titled button (START ROW, DONE, ABORT); keys S, D and SPACE duplicate them. The rows are numbered
1–8 on the panel, in the log and here. **FREEREF is emitted first:** if it fails, the instrument has not shown it can
report a coast (INS-14), and every coast cell below is read with that in mind.

| Row | He clicks, then | He should feel | Cell | Pre-registered reading | Fails if |
|---|---|---|---|---|---|
| 1 HOLD-RISE | START ROW, pushes the wheel off where it stopped and holds it, DONE | the resistance **grow** over about ¼ s | R17-T0-HOLDRISE | HS_HOLDING throughout; duty rises from duty_min to the ceiling within 400 ms of the first displacement. **Records sense_i at the ceiling, sizing HOLD_CEILING_PCT in amps** | the duty never reaches the ceiling in time, or SLIPPED, LIMITED or FAULTED is seen |
| 2 HOLD-SLIP | START ROW, pushes past a 2 % ceiling, DONE | it **give way**, then a drag that grows with speed | R17-T0-HOLDSLIP | HS_SLIPPED before any DCS_FAULTED; the slip count advances | the hold persists past 2 ticks, or FAULTED comes first (recorded either way) |
| 3 HOLD-LIMIT | START ROW, a steady push at the ceiling for about 2 s | it hold, then **let go** after about 2 s | R17-T0-HOLDLIMIT | HS_LIMITED within 7 s; the limit count advances | it never hands off |
| 4 COAST AT REST | START ROW, spins briskly, lets go | it spin freely and coast | R17-T0-RESTCOAST | half-rate time ≥ 150 ms (from the rate peak) | < 150 ms |
| 5 E-STOP AT REST | START ROW, spins briskly, lets go | it resist harder the faster it turns, then stop quickly | R17-T0-RESTSHORT | half-rate time ≤ 60 ms | > 60 ms |
| (4 − 5) | — | — | R17-T0-STOPGAP | ≥ 100 ms apart | < 100 ms |
| 6 FAULT, COAST MODE | START ROW; **hands off**, it drives and faults itself; ABORT if needed | the wheel coasts after the fault | R17-T0-FLTCOAST | half-rate ≥ 150 ms and still FAULTED | either false, or it never reached AT_SPEED (**PL-116's symptom**) |
| 7 FAULT, HOLD MODE | as row 6 | the wheel brakes hard after the fault | R17-T0-FLTSHORT | half-rate ≤ 60 ms and still FAULTED | either false, or it never reached AT_SPEED |
| (6 − 7) | — | — | R17-T0-FLTGAP | ≥ 100 ms apart | < 100 ms |
| 8 DRIVER COG STOPPED | START ROW, spins briskly, lets go | it coast exactly as row 4 did | **R17-T0-FREEREF** | half-rate ≥ 150 ms | < 150 ms: the instrument itself cannot report a coast |

**Run 4 (`t0-stopmode-fltfirst`), only if rows 6–7 blocked in run 3:** the same rows, with the powered rows run
*before* the e-stop row. If they reach AT_SPEED and fault as designed, the e-stop clear path is implicated (a driver
defect and a new task). If they block again, the blocked test is (PL-106).

### `dual-start` — the start checks and the wiring walk (startup study §6)

Ten steering lifetimes. Each start records `BM-SSTART`, `BM-SKHEALTH` (both wheels) and one `BM-SKPROBE` per wheel;
the last three also record `BM-SKWALK`; the segment ends with one `BM-SKSUM` per wheel. The header's `BM-SKBUILD`
prints every band and threshold the cells judge against. There is no PREFLT, because the attended negatives load this
part with a wheel mis-wired.

| Cell | Criterion | Fails if | Control | Sizes |
|---|---|---|---|---|
| **R19-DUAL-HEALTH-X**, per wheel | 0 of 10 starts with any failed bit | any bit in `l_fail`/`r_fail` | B-1 and B-3's negatives (below) | — (certifies the health word) |
| **R19-DUAL-RZSPREAD-X**, per wheel | 0 rest zeros outside −100…+200 mV | one outside the band | none at driver level (the band is compiled in) | **REST_ZERO_MIN_MV/MAX_MV**, from `BM-SKSUM rz_min/max/spr/mean_x10`. The gap between the two boards' means answers the study's question of whether one band can serve both |
| **R19-DUAL-PRBFLR-X**, per wheel, **judged first** | the largest coasting-floor phase reading ≤ 99 mV | the floor reaches 100 mV | this *is* the probe's able-to-report control | the floor the follow threshold must stay above |
| **R19-DUAL-PROBE-X**, per wheel | 0 of 30 probes whose driven phase reads under 200 mV, or any follower under 50 % of it (stricter than the driver, which needs only one follow) | any bad probe | PRBFLR; B-3's negative | **CONT_MIN_DRIVEN_MV** (`drv_min_mV`), **CONT_FOLLOW_PCT** (`fol_min_pct`) |
| **R19-DUAL-WALK-X**, per wheel | 0 of 3 walks failing: HLT_WIRING passes, both legs 6–9 ticks in opposite directions, no hall events | `l_ok`/`r_ok` FALSE in `BM-SKWALK` | B-5's negative | **WALK_POWER** (10, provisional) from the legs, `walk_ms` and peak current; the overshoot allowance |
| **R19-DUAL-PACK-X** | every start reads PACK_NOT_FITTED, 0 mV, and no HLT_PACK | any other reading | — | none: the sensor is not fitted, so its calibration cannot be sized |
| R19-DUAL-NOSTALL-S, -DBGMASK-S | standard | as in every part | — | — |

The probe's pulse width and duty are fixed by the build, not swept, so they get no sized value.

### Attended negative controls — run these FIRST (D2), then `dual-start` itself

**Disconnect the battery before every wiring change and before every restore.** Mis-wire the **RIGHT** wheel, so
that the left wheel is the in-run control. Running the positive `dual-start` last also proves the wiring was restored.

1. **B-1 — the hall connector unplugged at start.** Unplug the RIGHT hall connector, then run
   `tools/bench-run.sh dual-start-nowalk`. No wheel is ever driven.
   - **Must read:** every start still succeeds (`BM-SSTART ret_ok,TRUE`); `r_fail` has HLT_HALLS ($0001) set, and
     `r_ill_lo + r_ill_hi > 0`.
   - **Verdicts:** HEALTH-X RIGHT FAIL 10/10, LEFT PASS; PROBE, RZSPREAD and PRBFLR PASS on both; WALK NOT_BUILT.
   - **Restore:** replug the connector.
2. **B-3's negative — one motor lead unplugged.** Unplug ONE RIGHT phase lead, then run `dual-start-nowalk`.
   - **Must read:** `r_fail` has exactly one of HLT_PHASE_U/V/W ($0004/$0008/$0010) at every start. The open phase
     reads at the floor (under 100 mV) as a follower and under the other two probes.
   - **Verdicts:** PROBE-X RIGHT FAIL, HEALTH-X RIGHT FAIL, PRBFLR PASS, the left wheel all PASS.
   - **Restore:** replug the lead.
3. **B-5's negative — two hall wires swapped.** Swap two RIGHT hall signal wires, then run `dual-start` (with the
   walk). **Watch the last three lifetimes:** the right wheel may jerk or buzz for up to 2 s per leg at power 10.
   Panic is the battery disconnect.
   - **Verdicts:** HEALTH and PROBE PASS on both wheels, since start's checks cannot see a swap. WALK-X RIGHT FAIL
     3/3 (`r_hlt,FALSE`, and `r_ig > 0` and/or legs out of band).
   - **The left wheel is judged on its own legs** (fixed before this visit: `checkWiring()` first shared one leg
     result between the wheels). But if the right wheel faults, the platform policy stops the left too. The left's
     leg may then come up short and fail its band, so the **left verdict is recorded, not pre-registered**, in this
     load.
   - **Restore:** the wires. A faulted wheel is recovered in-run with a 5 s cool-down.

Each attended load takes under a minute. With the rewiring, allow about 15 minutes for all three and the positive run.

---

## What this visit cannot measure, named

- **Any loaded value.** The hold's creep on a slope and its ceiling under load belong to the floor run («#3591»,
  «#3576»).
- **A phase short's current** (PL-118). The graded short's braking is judged by deceleration, not current.
- **The pack voltage.** The sensor is not fitted on this rig («#3611» waits on Stephen's unit).

---

## After the visit

One analysis per set of logs, under `DOCs/procedures/BENCH-RUN-PROCESSING.md`, reading the logs themselves. Then each
parameter the plan's R19 table names gets a sized value or a stated reason it has none. The P5 questions in plan "R19
as built" go to Stephen, each with its measured benefit:

- Should FR_GRADED become the default?
- Should the hold limits and the fault response become public setters?
- Should a re-synced fault be reported through getError()?
- What should start() do when a check fails?

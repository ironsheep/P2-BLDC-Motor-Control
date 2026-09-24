# Visit 10 — run sheet, pass 3 (the fallback, the walk guard, and T0-24 rebuilt)

**Task:** «#3613» runs it. **Built by:** «#3616» (the fault latch), «#3618» (the walk's current guard), PL-124 (the
REST window), «#3617» (T0-24's instrument). **Plan:** `BENCH-READINESS-SPRINT-PLAN.md`, R19.

**Passes 1 and 2 (2026-09-23):** the start checks and their negatives certified; the right board drives again. The
fallback to the graded short never showed, the walk drew about 26 A on crossed halls, and T0-24's instrument could not
read a coast. [Pass 2 evaluation](2026-09-23/VISIT-10-PASS2-EVALUATION.md). Pass 3 re-runs only what changed under it.

---

## Check the banner before reading anything else

| Load | Every banner / build record must read |
|---|---|
| `dual-*` tiers | `BM-BANNER,...,src_rev,40,fmt,25` and `BM-BUILD ... drv_rev,16`. Anything lower means an old tree was built: stop and report |
| `dual-start` | part `START`, `BM-SKBUILD ... no_walk,FALSE`, negative `NONE` |
| `dual-start-swapneg` | part `START`, `BM-SKBUILD` negative `SWAP`, a `BM-SKNEG` record before each of the last 3 `BM-SSTART` |
| `dual-fault` | part `FRESP`; a `BM-FRBUILD` record; `BM-NOTBUILT` for `B4PULSE` only |
| `t0-stopmode` | `src_rev 13`; `T0-24,row,...` records numbered 1 to 8 |

---

## The visit, declared

| | |
|---|---|
| **Purpose** | **Certification, and sizing the graded short.** It certifies that a second fault during a re-synced stop now takes the fallback and holds it (BLUNT). It sizes BRAKE_PCT_DEFAULT (GRADED, GRD100). It certifies the walk's current guard against the crossed-hall walk, the Rev B rest-zero band (−20…+40 mV), the REST window's fix, and T0-24's rebuilt instrument, each against its negative. |
| **Hardware risk** | `dual-fault` **faults the wheels on purpose at up to about 220 rpm commanded**. Each fault ends in a phase short, a free coast, a controlled ramp down, or the graded short. The graded short now actually runs, and **it regenerates into the supply, so it needs the pack, not a bench supply.** `dual-start-swapneg` drives the left wheel as if two hall wires were crossed; the new guard shorts a leg as soon as it draws more than 1 A. `t0-stopmode` spins the right wheel under power in rows 6 and 7, and in row 5 the program shorts the wheel while you watch it coast. **Wheels up throughout. Hands off in every unattended tier. Panic: physical battery disconnect.** |
| **Who can observe** | `t0-stopmode` is attended; each row says on its panel what to do and what you should feel. The unattended tiers need nobody, and **nobody should touch the wheels during `dual-fault`**: pass 2's right-wheel trials 14–17 were disturbed by a hand, and they are re-run here. |
| **Runs that carry state** | None. The swap negative applies to one start each. |
| **Run length** | About 15 minutes unattended, then about 10 minutes attended for run 4. |
| **Repeatability** | All repeatable and idempotent. |
| **Variant matrix** | Rev B, the paired 6.5in hubs, 18.5 V pack, 270 MHz. `test_bench_dual.spin2` parts START (two builds) and FAULTRESP; `test_bench_t0.spin2` T0-24. |

**Not re-run, and why:** `dual-start-phaseneg` and `dual-start-nowalk` certified in pass 2, and nothing under them has
changed since. The lead probe and the hall check are untouched; the only start-check change is the rest-zero band, which
run 1 judges.

---

## The commands — run every one, in this order

```bash
tools/bench-run.sh dual-start             # 1: Hands off. Startup checks with normal wiring; both wheels nudge a little near the end
tools/bench-run.sh dual-start-swapneg     # 2: Hands off. The program fakes crossed sensor wires on the LEFT wheel; it may twitch, then stops itself
tools/bench-run.sh dual-fault             # 3: Hands off, and keep hands away. Each wheel spins up and is stopped on purpose, about 6 minutes
tools/bench-run.sh t0-stopmode            # 4: YOU, at the RIGHT wheel: follow each panel; every row waits for you
```

**No run depends on another run's result, and nothing needs rewiring.**

---

## What each load decides, and how each can fail

Every criterion is fixed here, before the run (D2). Cells print their own verdict; the rest are judged in the report
from the named records.

### `dual-start` — the rest-zero band, and the guard's positive control

| Cell | Criterion | Fails if | Control | Sizes |
|---|---|---|---|---|
| **R19-DUAL-RZSPREAD-X**, per wheel | 0 rest zeros outside **−20…+40 mV** (`BM-SKSUM rz_lo,-20,rz_hi,40`) | one outside the band | pass 2's 40 starts per wheel: left 6.7–9.0, right −0.3–3.1 | certifies the sized band |
| **R19-DUAL-WALK-X**, per wheel | 0 of 3 walks failing | `l_ok`/`r_ok` FALSE | run 2 | **the guard's positive control**: a healthy walk must never trip it |
| R19-DUAL-HEALTH-X, PROBE-X, PRBFLR-X, PACK-X | as pass 2 | as pass 2 | — | — |

**Pre-registered:** every healthy `BM-SKWALK l_pk_i` stays near pass 2's 12–21 mV, far under the guard's 150 mV net.

### `dual-start-swapneg` — the guard's negative, and B-5's

| Cell | Criterion | Fails if |
|---|---|---|
| **R19-DUAL-SWNEG-X**, LEFT | 0 of 3 walks in which the left's HLT_WIRING was not judged failed | the swap went undetected in any walk |
| **The guard (judged in the report)** | every crossed walk's `BM-SKWALK l_pk_i` stays **under 577 mV**, the least pass 2 read unguarded | any walk at or above 577 mV: the guard did not bound it |

Pass 2 read 577, 3,858 and 594 mV on these walks. The guard shorts the leg within one front pass and one drive pass
(about 1.5 ms) of 150 mV net, so the instrument should see a small fraction of that. A walk that never reaches the bound
(the rotor happens to follow) is not a failure, provided HLT_WIRING still fails it.

### `dual-fault` — the fallback and the graded short (fault study §7)

The cells and their controls are pass 2's (see its sheet in the evaluation), with the changes below. Every fault is
forced through `testForceFault()`, each trial in its own driver lifetime, at 40, 80 and 120 × 10⁶.

| Cell | Criterion | Fails if | What changed |
|---|---|---|---|
| **R19-DUAL-BLUNT-X** | every X-6 / X6C second fault reads DCS_FAULTED, and it **stays** FAULTED until the trial's recovery | the fallback is not taken, or drops back to STOPPED on its own | DRIVER_REV 14: the fault is a latch. Pass 2 read `second,NO_FAULT` 10/10 because the fault was wiped in about 0.5 ms |
| **R19-DUAL-GRADED-X** | `BM-FRSTAT f2_k`: coast, then 10, 25, 50, 100 %: ticks and time to rest never rise as brake % rises; 100 % below the coast | a rise, or no overall fall | first run; **sizes BRAKE_PCT_DEFAULT** (25 provisional) |
| **R19-DUAL-GRD100-X** | 100 % graded against the full short at 80 × 10⁶, within 2 ticks | differs by more | first run |
| **R19-DUAL-RESTFLAT-X** | every phase under 50 mV p-p at rest, the REST window opening once the driver reads settled | a channel swings with nothing turning | PL-124: pass 2's X-4 failures (≈790 mV) were the ramp's last step, read too early |
| R19-DUAL-SHORTTK-X, COASTEMF-X, RIGHT at 80 and 120 | as pass 2 | as pass 2 | re-run: pass 2's right trials 14–17 were hand-disturbed |
| every other cell | as pass 2 | as pass 2 | unchanged |

**Pre-registered for X-6 in hold mode:** with the fallback held, the wheel now stops on the graded short, not on the
hold. The stop takes longer than pass 2's 27–59 ms at low brake %, and approaches the full short's at 100 %.

### `t0-stopmode` — the stop states at the wheel (ATTENDED, right wheel)

**The panel names the RIGHT wheel on every screen.** Every row waits for you. **FREEREF is emitted first:** if it fails,
the instrument has not shown it can report a coast, and every coast cell is read with that in mind.

**The reading is `band_ticks`:** the hall ticks the wheel turns from 120 ticks/s down to rest. It is the same measure on
every row, whatever speed the spin reached. **A spin row needs a hard spin that passes 120 ticks/s.** If yours does not,
the panel says TOO SLOW and asks you to spin again, up to 3 tries; only then is the row not measured, and the panel
says so.

| Row | You click, then | You should feel or see | Cell | Pre-registered reading | Fails if |
|---|---|---|---|---|---|
| 1 HOLD-RISE | START ROW, push the wheel off where it stopped and hold it, DONE | the resistance **grow** over about ¼ s | R17-T0-HOLDRISE | HS_HOLDING throughout; the ceiling within 400 ms of the first push | not in time, or SLIPPED, LIMITED or FAULTED |
| 2 HOLD-SLIP | START ROW, push past a low ceiling, DONE | it **give way**, then drag | R17-T0-HOLDSLIP | starts HS_HOLDING at 0 (else NOMEAS), then HS_SLIPPED before any FAULTED | the hold persists, or FAULTED first |
| 3 HOLD-LIMIT | START ROW, a steady push at the ceiling for about 2 s | it hold, then **let go** | R17-T0-HOLDLIMIT | starts HS_HOLDING at 0 (else NOMEAS), then HS_LIMITED within 7 s | it never hands off |
| 4 COAST AT REST | START ROW, spin it hard, let go | it spin freely and coast | R17-T0-RESTCOAST | band_ticks ≥ 7 | ≤ 6 |
| 5 E-STOP AS IT COASTS | START ROW, spin it hard, let go | it coast, then **stop abruptly**: the program shorts it as it slows | R17-T0-RESTSHORT | band_ticks ≤ 4, the e-stop latched at the band entry | ≥ 5, or the short was not applied |
| (4 − 5) | — | — | R17-T0-STOPGAP | ≥ 3 ticks apart | < 3 |
| 6 FAULT, COAST MODE | START ROW; **hands off**, it drives and is faulted on purpose; ABORT if needed | the wheel coasts after the fault | R17-T0-FLTCOAST | band_ticks ≥ 7 and still FAULTED | either false, or it never reached AT_SPEED |
| 7 FAULT, BRAKE MODE | as row 6 | the wheel brakes hard after the fault | R17-T0-FLTSHORT | band_ticks ≤ 4 and still FAULTED | either false, or it never reached AT_SPEED |
| (6 − 7) | — | — | R17-T0-FLTGAP | ≥ 3 ticks apart | < 3 |
| 8 DRIVER COG STOPPED | START ROW, spin it hard, let go | it coast exactly as row 4 did | **R17-T0-FREEREF** | band_ticks ≥ 7 | ≤ 6 |

The thresholds come from every coast and short on record (`test_bench_t0.spin2`, `CON { T0-24 sign-off limits }`,
each with its log): a coast predicts 9–36 band ticks and a short 1–3. Ticks 5 and 6 are a dead band that passes neither.

---

## What this visit cannot measure, named

- **Any loaded value**: the hold's creep on a slope and its ceiling under load belong to the floor run («#3576»).
- **A phase short's current** (PL-118).
- **The pack voltage**: no sensor is fitted («#3611»).
- **An open motor winding, or a hall pair actually crossed at the connector**: the rig cannot make either.
- **A Rev A rest zero**: no Rev A board is on the rig, so Rev A keeps its wide provisional band.

---

## After the visit

One analysis per set of logs, under `DOCs/procedures/BENCH-RUN-PROCESSING.md`. Then BRAKE_PCT_DEFAULT gets a sized value
or a stated reason it has none. The P5 questions go to Stephen, each with its measured benefit:

- Should FR_GRADED become the default?
- Should the hold limits and the fault response become public setters?
- Should a re-synced fault be reported through getError()?
- What should start() do when a check fails?

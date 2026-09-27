# Visit 10 — run sheet, pass 8 (close what pass 7 left open)

**Task:** «#3613» runs it. **Burn-down:** `DOCs/PUNCH-LIST.md`, "Release burn-down".
**Pass 7's record:** `DOCs/analyses/bench/2026-09-26/pass7/VISIT-10-PASS7-EVALUATION.md`. It certified 12 items.

**What this pass can close** (all built and gated; none has run on hardware):

| Closes | What it proves | Tier |
|---|---|---|
| PL-161 | the steering front cog keeps its 1 ms slot (pack work and the state report off the slot passes; no driver wait on a slot-work pass) | `dual-start`, `dual-d` |
| PL-146 | the fold-back acts only on a driven bridge, so the left's events drain | `dual-d` |
| PL-145 | the time stop fires on its deadline (the cell now times the stop, not the coast after it) | `dual-d` |
| PL-144 | the path limiter no longer hunts (precondition fixed) | `dual-d` |
| PL-162 | the pack cells judge with the right instrument (steady reference; PACK-X against the config) | `dual-pack`, `dual-start` |
| PL-14 | `start()` honours its voltage argument | `t0-api` |
| PL-51 | the steering distance-speed getter reads back what was set | `t0-api` |
| PL-52 | `getPower()` reads 0 after a stop | `t0-stopreason` |

**Not in this pass:** serial and demo testing wait for a release-candidate driver (Stephen, 2026-09-26). The floor
run's load items wait for the floor run. `dual-reg` and `dual-kick` certified at pass 7 and are not re-run: DRIVER_REV
36 changes neither the driven PASM path (the new instruction acts only on an undriven bridge) nor anything those
cells judge that `dual-start` and `dual-d` do not also exercise.

---

## ⛔ First: PUSH, then pull at the bench

`git log --oneline -1 -- src/` at the bench must show **ce8dd9d** or later (DRIVER_REV 36, test_bench_dual SRC_REV 57, test_bench_t0 SRC_REV 24).

**What this invalidated:** DRIVER_REV 35→36 (fold-back on an undriven bridge; the front cog's slot schedule). Every
cell in this pass's tiers runs against it.

## ⭐ Before anything: note the time you connect the pack

**Write down the clock time you connect the battery**, or that it was already connected (a `pack-connect*.txt` file's
creation time does this). PL-120 watch.

## Check the banner before reading anything else

| Load | Every banner / build record must read |
|---|---|
| `t0-stopreason`, `t0-api` | the t0 banner at `src_rev 24` |
| every `dual-*` tier | `BM-BANNER,...,src_rev,57,fmt,36` and `BM-BUILD ... drv_rev,36` |
| `dual-pack` | `BM-PKBUILD,...,fitted,TRUE,pin,0,cal_pm,1_012,calibrated,TRUE` |

---

## The visit, declared

| | |
|---|---|
| **Purpose** | **Certification** of DRIVER_REV 36 and three instrument fixes, plus the last three API checks. |
| **Hardware risk** | • `t0-stopreason`: one wheel driven slowly, **one abrupt e-stop**.<br>• `t0-api`: nothing moves; the motor is started five times, once at 14.8 V (nothing driven).<br>• `dual-d`: **the wheels stop dead**, an e-stop is latched, the current limit is lowered until a wheel cannot keep up, and twice the platform is switched off while the wheels spin.<br>**Wheels up throughout. Panic: physical battery disconnect.** |
| **Who can observe** | Every tier is hands-off except `dual-pack`: you unplug and replug the sensor Powerpole twice, when told. |
| **Runs that carry state** | None across runs. If PL-120 strikes, `t0-stopreason` waits for the right wheel to come back, up to 3 minutes. |
| **Run length** | `t0-stopreason` about 1.5 min. `t0-api` about 20 s. `dual-start` about 1. `dual-d` about 2.5. `dual-pack` under 3. **Total about 8 minutes.** |
| **Repeatability** | All repeatable and idempotent. |
| **Variant matrix** | Rev B, the paired 6.5in hubs, 18.5 V pack (sensor on P0), 270 MHz. `test_bench_t0` T0-25 and T0-26; `test_bench_dual` parts START, D, PACK. |

---

## The commands — five, in this order

```bash
tools/bench-run.sh t0-stopreason   # 1: FIRST. One wheel driven slowly and stopped every way; one abrupt e-stop; two short distance moves
tools/bench-run.sh t0-api          # 2: NOTHING MOVES. Every API setting with good and bad values; about 20 s
tools/bench-run.sh dual-start      # 3: 10 starts; at every start both wheels turn a little one way and back
tools/bench-run.sh dual-d          # 4: stops dead, holds an e-stop, lowers the current limit; twice switches the platform off while spinning
tools/bench-run.sh dual-pack       # 5: NOTHING MOVES. Hands off 60 s, then unplug/replug the sensor Powerpole AT THE PACK twice, when told
```

**No run depends on another run's result, and nothing needs rewiring.**

---

## What each load decides

Every criterion is fixed here, before the run (D2). The cells print their own verdicts.

| Tier | Decides it |
|---|---|
| `t0-stopreason` | T0-25's cells as at pass 7; **R20-T0-SR-COMMANDED now also requires `getPower()` 15 while driving and 0 after `stopMotor()`** (record `T0-25,power`) — PL-52 |
| `t0-api` | every R20-T0-API-* family at 0 bad calls; **PERSIST** now includes a start at 14.8 V read back through `getDriveVoltage()` (PL-14); **STEER** now includes the distance-speed set/read-back rows (PL-51) |
| `dual-start` | **R16-DUAL-FRONTST: every lifetime `late,0`, `max_us` under 950, no LATE_PASS event** (PL-161); **R19-DUAL-PACK-X judged against the config** (PL-162); WALK and the other START cells as before |
| `dual-d` | **R16-DUAL-FRONTST-D `late,0`, `max_us` under 950** (PL-161); **R20-DUAL-EV-FOLDBACK 0 bad** (PL-146), FOLDBACK-D L/R still PASS; **R16-DUAL-TIMESTOP-D and WTIMSTOP-D, criterion FIELD_ZERO_BY_LIM: every driver reads DCS_STOPPED within −4..+7 ms of the deadline** (PL-145; record `BM-TIMESTOP` `zero_ms` judged, `rest_ms` printed only, `late_pass` to tell an overrun apart); **R20-DUAL-PATH-HUNT exactly 1** (PL-144); CMDTIMEOUT, NOTFOL, RESTCOAST as before |
| `dual-pack` | **R20-PACK-ABSENT 2 of 2 against the steady reference** (PL-162); METER CAL_POINT (expected to move about +3 mV from −7, the raw-count average removes a −4 mV rounding bias); PKSTEADY spread near 94 mV; PACK-EV PASS |

**What a FRONTST failure would mean:** if `dual-start`'s worst passes still spread by about 520 µs across lifetimes,
the spread is the synchronized-take wait itself (PL-161), and its fix is answering on a later pass instead of waiting.

## After the visit

One analysis per set of logs, under `DOCs/procedures/BENCH-RUN-PROCESSING.md`. Then close every punch-list item its
cells certify, and re-count the burn-down.

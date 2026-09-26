# Visit 10 — run sheet, pass 7 (the burn-down pass: close every wheels-up item that has landed)

**Task:** «#3613» runs it. **Burn-down:** `DOCs/PUNCH-LIST.md`, "Release burn-down".

**What this pass can close** (all built and gated; none has run on hardware):

| Closes | What it proves | Tier |
|---|---|---|
| PL-78 / PL-87 / PL-95 | **the speed-change kick is gone** (the arrival pass now advances the field) | `dual-kick` |
| PL-144 | the path limiter no longer hunts | `dual-d` |
| PL-147 | the two "following" readings agree | `dual-d` |
| PL-146 | the fold-back events drain after the fields stop | `dual-d` |
| PL-143 | the command timeout watches every drive, `driveForDistance()` included | `dual-d` |
| PL-141 (positive half) | the path limiter engages for a wheel behind its partner | `dual-d` |
| PL-151 | turning by distance, fault cause, fault retry | `dual-reg`, `t0-stopreason` |
| PL-153 | the odometer is total travel; each limit counts from where it was armed | `t0-stopreason` |
| PL-155, PL-158, PL-159, PL-160 (API half) | every API setting accepts its range, refuses outside it, reads back, and survives `start()` | `t0-api`, `t0-stopreason` |
| PL-156 | `isMoveDone()` | `t0-stopreason` |
| PL-152 | the pointed tiers themselves (one compile, one part) | every dual tier |
| «#3611» pair 1 | the pack calibration applied (1012) | `dual-pack` |
| PL-120 | read against the header reseat; any refusal times its recovery | `t0-stopreason` |

**Not in this pass** (Stephen, 2026-09-26): serial and demo testing wait for a release-candidate driver. The floor
run's load items (the hold on an incline, the loaded path limiter and overload hold, a chocked wheel) wait for the
floor run.

---

## ⛔ First: PUSH, then pull at the bench

`git log --oneline -1 -- src/` at the bench must show **cd6f1b7** or later (DRIVER_REV 35).

**What this invalidated:** the driver changed (DRIVER_REV 30→35), so every cell that drives certifies again, and that
is the purpose of this pass.

## ⭐ Before anything: note the time you connect the pack

**Write down the clock time you connect the battery**, and whether it was already connected. PL-120 has struck on the
first load of the day twice.

## Check the banner before reading anything else

| Load | Every banner / build record must read |
|---|---|
| `t0-stopreason`, `t0-api` | the t0 banner at `src_rev 23` |
| every `dual-*` tier | `BM-BANNER,...,src_rev,55,fmt,35` and `BM-BUILD ... drv_rev,35` |
| `dual-pack` | `BM-PKBUILD,...,fitted,TRUE,pin,0,cal_pm,1_012,calibrated,TRUE` |

---

## The visit, declared

| | |
|---|---|
| **Purpose** | **Certification** of DRIVER_REV 30–35 and the API contract, plus one pack-calibration confirmation. |
| **Hardware risk** | • `t0-stopreason`: one wheel driven slowly, **one abrupt e-stop**.<br>• `dual-d`: **the wheels stop dead**, an e-stop is latched, the current limit is lowered until a wheel cannot keep up, and twice the platform is switched off while the wheels spin.<br>• `dual-reg`: **one wheel is faulted on purpose**, twice.<br>• `dual-kick`: each wheel in turn runs up to **top speed** (about 300 rpm).<br>**Wheels up throughout. Panic: physical battery disconnect.** |
| **Who can observe** | Every tier is hands-off except `dual-pack`: you unplug and replug the sensor Powerpole twice, when told. Also note the pack's power-on time (above). |
| **Runs that carry state** | None across runs. If PL-120 strikes, `t0-stopreason` waits for the right wheel to come back, up to 3 minutes. |
| **Run length** | `t0-stopreason` about 1.5 min (up to about 4.5 if the right is refused). `t0-api` about 15 s. `dual-start` about 1. `dual-d` about 2.5. `dual-reg` under 1. `dual-kick` under 2. `dual-pack` under 3. **Total about 12 minutes.** |
| **Repeatability** | All repeatable and idempotent. |
| **Variant matrix** | Rev B, the paired 6.5in hubs, 18.5 V pack (sensor on P0), 270 MHz. `test_bench_t0` T0-25 and T0-26; `test_bench_dual` parts START, D, REG, KICK, PACK. |

---

## The commands — seven, in this order

```bash
tools/bench-run.sh t0-stopreason   # 1: FIRST. One wheel driven slowly and stopped every way; one abrupt e-stop; two short distance moves; the left instead if the right won't start
tools/bench-run.sh t0-api          # 2: NOTHING MOVES. Every API setting with good and bad values; about 15 s
tools/bench-run.sh dual-start      # 3: 10 starts; at every start both wheels turn a little one way and back
tools/bench-run.sh dual-d          # 4: stops dead, holds an e-stop, lowers the current limit; twice switches the platform off while spinning
tools/bench-run.sh dual-reg        # 5: two turns by distance; then each wheel is faulted on purpose and restarted
tools/bench-run.sh dual-kick       # 6: one wheel at a time steps up to top speed and back down
tools/bench-run.sh dual-pack       # 7: NOTHING MOVES. Hands off 60 s, then unplug/replug the sensor Powerpole AT THE PACK twice, when told. No meter reading needed
```

**No run depends on another run's result, and nothing needs rewiring.**

---

## What each load decides

Every criterion is fixed here, before the run (D2). The cells print their own verdicts.

| Tier | Decides it |
|---|---|
| `t0-stopreason` | T0-25's eight cells, as before; R20-T0-ROTSTOP (one turn to within 3 ticks); R20-T0-ESTOPSTATUS; **R20-T0-ODOMETER** (two back-to-back moves each travel their distance; e-stop leaves the odometer unchanged); **R20-T0-MOVEDONE**; **R20-T0-PERSIST** |
| `t0-api` | every R20-T0-API-* family at 0 bad calls (ACCEL including setDeceleration, MAXSPEED, HOLD, FAULTRESP, HOLDLIMITS, TIMEOUT, LIMITS, PERSIST, CALIBRATE, STEER) |
| `dual-start` | WALK 0/10 per wheel, no leg ending OTHER, no PATH_LIMIT at a start; the other START cells as before |
| `dual-d` | **R20-DUAL-PATH-HUNT exactly 1** (pre-fix: 5); **R18-DUAL-NOTFOL-D PASS**; **R20-DUAL-EV-FOLDBACK 0 bad**; R20-DUAL-EV-PATH positive; **CMDTIMEOUT including the bounded limb** (a 20 m `driveForDistance()` left silent stops at the timeout); RESTCOAST and the STEERSEG steps as before. WTIMSTOP is read against PL-145 (its slack sits inside its own spread) |
| `dual-reg` | R17-DUAL-TURNDIST-B (each wheel within 0–2 ticks of its own target); R17-DUAL-FLTCAUSE-B (FC_LAG on the faulted wheel, FC_NONE after healthy drives); R16-DUAL-FLTRETRY-B (the same power clears the fault and drives) |
| `dual-kick` | **R21-DUAL-TRKICK-T ≤ 50 mV per motor** over the seven worst transitions (the pre-fix logs read 64–183) |
| `dual-pack` | R20-PACK-METER CAL_POINT (the applied calibration against your DMM's 20.74 V pair); ABSENT and EV as before |

## After the visit

One analysis per set of logs, under `DOCs/procedures/BENCH-RUN-PROCESSING.md`. Then close every punch-list item its
cells certify, and re-count the burn-down.

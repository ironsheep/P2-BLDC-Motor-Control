# Visit 10 — run sheet, pass 4 (the right wheel's failure caught in the act, the winding check, and the panel's own tests)

**Task:** «#3613» runs it. **Built by:** «#3609» (the protective stop in the stop mode, PL-132; the re-sync direction),
«#3610» (the winding check, PL-133), «#3613» (the PL-120 diagnostics, the required panel tests PL-135, BRAKE_PCT 10).
**Plan:** `BENCH-READINESS-SPRINT-PLAN.md`, R19.

**Done so far (pass 3):**
- 16:14 [evaluation](2026-09-24/VISIT-10-PASS3-RERUN-EVALUATION.md): fault fallback latch, walk guard's negative, REST
  window and Rev B rest-zero band certified.
- 17:19 [evaluation](2026-09-24/VISIT-10-PASS3-T0-DUALSTART-EVALUATION.md): start checks certified (13/13); the hold's
  rise was found 16 % slow and fixed.
- 21:21 [evaluation](2026-09-25/VISIT-10-DUALFAULT-T0-EVALUATION.md): the graded short and the hold's rise certified;
  BRAKE_PCT sized to 10. The right wheel's bridge died mid-run and was back on the next program load (PL-120), so every
  right-wheel fault cell is still owed.

---

## Check the banner before reading anything else

| Load | Every banner / build record must read |
|---|---|
| `dual-*` tiers | `BM-BANNER,...,src_rev,44,fmt,28` and `BM-BUILD ... drv_rev,22`. Anything lower means an old tree was built: stop and report |
| `dual-fault`, `dual-fault-rightfirst` | part `FRESP`; `BM-FRBUILD`, then `BM-FRDIAG ... right_first,FALSE` (or `TRUE`); `BM-FRRECSUM` before `BM-END` |
| `dual-start` | part `START`, `BM-SKBUILD ... neg,NONE`; a `BM-SKWIND` pair per wheel in lifetimes 1 and 2 |
| `dual-start-phaseneg` | part `START`, `BM-SKBUILD` negative `PHASE`; a `BM-SKNEG` and a `BM-SKWIND` per wheel in every lifetime |
| `t0-stopmode` | `src_rev 17`; the first row 1 screen record reads `panel_test,TRUE` |

---

## The visit, declared

| | |
|---|---|
| **Purpose** | **Diagnosis, certification and sizing.** It catches PL-120 while it happens: a dump 150 ms into a drive that is not moving, a same-run recovery probe, and the right wheel's trials run first. That decides whether time or a reload clears it, and whether the left's trials are a precondition. It re-runs every right-wheel fault cell and the platform stop policy. It measures the winding resistance for the first time (PL-133) against its negative. It certifies the panel's own tests (PL-135). |
| **Hardware risk** | Both `dual-fault` tiers **fault the wheels on purpose at up to about 220 rpm commanded**; each fault ends in a phase short, a coast, a controlled ramp or the graded short. **Run them on the pack.** The winding check in both `dual-start` tiers drives each pair of motor leads for up to 0.3 s: **each wheel twitches a little, three times, at each measured start.** `t0-stopmode` spins the right wheel under power in rows 6 and 7. **Wheels up throughout. Hands off in every unattended tier. Panic: physical battery disconnect.** |
| **Who can observe** | `t0-stopmode` is attended; every other tier needs nobody, and **nobody touches the wheels during the `dual-fault` tiers.** |
| **Runs that carry state** | None across runs. Within a `dual-fault` run, the recovery probe follows the first wheel that fails to move. |
| **Run length** | About 6 minutes for each `dual-fault` tier, plus at most 2 minutes if the recovery probe runs; about 1 minute for `dual-start`; about 2 for `dual-start-phaseneg`; about 10 attended for `t0-stopmode`. |
| **Repeatability** | All repeatable and idempotent. |
| **Variant matrix** | Rev B, the paired 6.5in hubs, 18.5 V pack, 270 MHz. `test_bench_dual.spin2` parts FAULTRESP (two orders) and START (two builds); `test_bench_t0.spin2` T0-24. |

---

## ⛔ First: push, then pull — the tree to run

**Push from the authoring tree first**, then pull at the bench. The source to run is named in the hand-back, and
`git log --oneline -1 -- src/` at the bench must show it. The banners are the check (table above).

## The commands — all five are ready

```bash
tools/bench-run.sh dual-fault-rightfirst  # 1: Hands off, on the pack. The RIGHT wheel's fault trials first, then the left's
tools/bench-run.sh dual-fault             # 2: Hands off, on the pack. The same trials, left first, as last time
tools/bench-run.sh dual-start             # 3: Hands off. Startup checks; the wheels twitch at the first two starts, then nudge near the end
tools/bench-run.sh dual-start-phaseneg    # 4: Hands off. A faked dead motor wire on the LEFT; the wheels twitch at every start
tools/bench-run.sh t0-stopmode            # 5: YOU, at the RIGHT wheel. Do what each screen asks, including its three panel tests
```

**No run depends on another run's result, and nothing needs rewiring.**

---

## What each load decides, and how each can fail

Every criterion is fixed here, before the run (D2). Cells print their own verdict; the rest are judged in the report
from the named records.

### `dual-fault-rightfirst` and `dual-fault` — PL-120, then every fault cell

| What | Criterion | Reading that decides it |
|---|---|---|
| **The right's fault cells** (BLUNT, GRADED, GRD100, RESYNC, RESTFLAT, SHORTTK, COASTEMF) | as pass 3 | owed since pass 2; the left's pass 3 values are the comparison |
| **PLATSTOP** (one wheel faults, the other stops) | as pass 3 | never measured |
| **PL-120, ordering** | — | the right dies in `dual-fault-rightfirst` before any left trial → the left's trials are **not** a precondition; it drives through all its trials there but dies in `dual-fault` → they are |
| **PL-120, recovery** | — | `BM-FRRECSUM ... recovered,TRUE` within the 2 minutes → time clears it; `recovered,FALSE` → it survives in the program until a reload |
| **PL-120, the failing moment** | — | `BM-ABI* where,NOMOTION`: the driver's runs 150 ms into a drive that is not moving, before the protective stop overwrites them. Compared against the same wheel's PREFLT dump |

**Pre-registered:** the left reproduces pass 3's graded chain within hall quantisation, now with BRAKE_PCT's restore at 10.
A NOMOTION dump on a wheel that then drives is read as early, not as a failure.

### `dual-start` — the winding check (PL-133), and the start checks as certified

| Cell | Criterion | Fails if |
|---|---|---|
| **R19-DUAL-WINDR-X**, per wheel | every pair in lifetimes 1–2 reads WND_MEASURED within 100–1_500 mΩ (PROVISIONAL plausibility band) | a pair not MEASURED (NOT_VISIBLE, TRIPPED, UNSETTLED) or outside the band |
| **R19-DUAL-WINDSPR-X**, per wheel | each lifetime's three pairs within 20 % of their mean | a pair further out: an unbalanced winding or a weak switch |
| HEALTH, RZSPREAD, PROBE, PRBFLR, WALK, PACK | as pass 3 | as pass 3 |

**Pre-registered (report):** each pair 300–600 mΩ; the two wheels within 20 % of each other.

### `dual-start-phaseneg` — the winding check's negative

| Cell | Criterion | Fails if |
|---|---|---|
| **R19-DUAL-WINDNEG-X**, LEFT | in every lifetime exactly the two pairs through the withheld phase read WND_NOT_VISIBLE and the third WND_MEASURED | the hook did not take (three MEASURED) or the wrong pair went dark |
| R19-DUAL-PHNEG-X, LEFT | as pass 2 | as pass 2 |

**In-run control (report):** the RIGHT's three pairs all MEASURED in every lifetime.

### `t0-stopmode` — the stop states, and the panel's own tests (PL-135)

The rows and their cells are pass 3's (the 21:29 evaluation, §5), and HOLD-RISE's estimator stops at a slip (PL-134).
Three screens now ask for one act each, and draw only the control that performs it:

| Check | Passes when | Fails if |
|---|---|---|
| **UI-MISS** | row 1's first screen ends on a `T0-24,input ... via,1 ... hit,MISS` click inside the grey box | no such click, or it reads a button |
| **UI-REDO** | row 4 shows `run,2`, with its own result | no second run |
| **UI-ABORT** | row 6 run 1 ends `why,ABORTED`, its RESULT `screen` record within 100 ms of the ABORT `input` record, and run 2 measures | more than 100 ms, or no run 2 |
| UI-CLICK, UI-WAIT | as pass 3 | as pass 3 |

---

## What this visit cannot measure, named

- **Any loaded value**: the hold's creep and ceiling under load, and the blocked-wheel stop in the stop mode (PL-132),
  belong to the floor run («#3576»); a lifted wheel cannot be blocked (PL-106).
- **A phase short's current** (PL-118).
- **The pack voltage**: no sensor is fitted («#3611»); the winding check uses the nominal 18.5 V.
- **An open motor winding, or a hall pair crossed at the connector**: the rig cannot make either.
- **A Rev A winding reading**: Rev A's sense scale cannot resolve it, so no pair is driven there.

---

## After the visit

One analysis per set of logs, under `DOCs/procedures/BENCH-RUN-PROCESSING.md`. Then the P5 questions go to Stephen, each
with its measured benefit:

- Should FR_GRADED become the default? (Benefit measured at pass 3: about 28× gentler than the full short in brake mode,
  for about 21 ticks more travel, at 80 × 10⁶, left wheel.)
- Should the hold limits and the fault response become public setters?
- Should a re-synced fault be reported through getError()?
- What should start() do when a check fails?

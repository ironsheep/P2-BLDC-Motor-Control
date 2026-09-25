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
| `dual-*` tiers | `BM-BANNER,...,src_rev,42,fmt,26` and `BM-BUILD ... drv_rev,19`. Anything lower means an old tree was built: stop and report |
| `dual-fault` | part `FRESP`; a `BM-FRBUILD` record; `BM-NOTBUILT` for `B4PULSE` only |
| `t0-stopmode` | `src_rev 16`; a `hold_start` record carries `rise_ms`; the `PLOT t0stop` create ends `SIZE 560 470 POS 60 60 HIDEXY UPDATE` (PL-128); a `T0-24,cogs` record with `measure_cog` 0–7; `T0-24,row,...` records numbered 1 to 8 |

---

## The visit, declared

| | |
|---|---|
| **Purpose** | **Certification, and sizing the graded short.** It certifies that a second fault during a re-synced stop now takes the fallback and holds it (BLUNT). It sizes BRAKE_PCT_DEFAULT (GRADED, GRD100). It certifies the walk's current guard against the crossed-hall walk, the Rev B rest-zero band (−20…+40 mV), the REST window's fix, and T0-24's rebuilt instrument, each against its negative. |
| **Hardware risk** | `dual-fault` **faults the wheels on purpose at up to about 220 rpm commanded**. Each fault ends in a phase short, a free coast, a controlled ramp down, or the graded short. The graded short is the full short switched on and off every 10 ms, so each short slice draws the full short's current, and each switch to coast returns a little current to the supply: **run it on the pack, not a bench supply.** `t0-stopmode` spins the right wheel under power in rows 6 and 7, and in row 5 the program shorts the wheel while you watch it coast. **Wheels up throughout. Hands off in every unattended tier. Panic: physical battery disconnect.** |
| **Who can observe** | `t0-stopmode` is attended; each row says on its panel what to do and what you should feel. The unattended tiers need nobody, and **nobody should touch the wheels during `dual-fault`**: pass 2's right-wheel trials 14–17 were disturbed by a hand, and they are re-run here. |
| **Runs that carry state** | None. |
| **Run length** | About 10 minutes unattended for run 1, then about 15 minutes attended for run 2, at your pace. |
| **Repeatability** | All repeatable and idempotent. |
| **Variant matrix** | Rev B, the paired 6.5in hubs, 18.5 V pack, 270 MHz. `test_bench_dual.spin2` parts START (two builds) and FAULTRESP; `test_bench_t0.spin2` T0-24. |

**Not re-run, and why:** every `dual-start*` tier is certified (pass 2 and today), and driver 18 changes only the hold
at rest, which no start check enters.

---

## ⛔ First: push, then pull — the tree to run

**Done so far:**
- 16:14–16:33 ([evaluation](2026-09-24/VISIT-10-PASS3-RERUN-EVALUATION.md)): BLUNT (left), the walk guard's negative,
  the REST window and the rest-zero band certified.
- 17:19–17:26 ([evaluation](2026-09-24/VISIT-10-PASS3-T0-DUALSTART-EVALUATION.md)): `dual-start` all PASS, and it
  drops. `t0-stopmode` 9 of 10: the hold rose 16 % slow (PL-130, fixed in driver 18). Its three deliberate acts are now
  asked on the panel (PL-131).

- **Push from the authoring tree first**, then pull at the bench. The source to run is named in the hand-back, and
  `git log --oneline -1 -- src/` at the bench must show it. The banners are the check (table above).

## The commands — both are ready

```bash
tools/bench-run.sh dual-fault             # 1: Hands off, nobody touches the wheels. Faults both wheels on purpose; the graded short now brakes
tools/bench-run.sh t0-stopmode            # 2: YOU, at the RIGHT wheel. Do what each row's panel says, including the three extra clicks it asks for
```

**No run depends on another run's result, and nothing needs rewiring.**

---

## What each load decides, and how each can fail

Every criterion is fixed here, before the run (D2). Cells print their own verdict; the rest are judged in the report
from the named records.

- **`dual-start`: done** 17:25, all 13 PASS: rest zeros in band on both wheels, healthy walks at 13–21 mV against the
  guard's 150 mV ([evaluation](2026-09-24/VISIT-10-PASS3-T0-DUALSTART-EVALUATION.md) §2).
- **`dual-start-swapneg`: done** 16:14. The guard bounded every crossed walk and HLT_WIRING failed each one
  ([evaluation](2026-09-24/VISIT-10-PASS3-RERUN-EVALUATION.md) §2).

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

### `t0-stopmode` — the stop states at the wheel (ATTENDED, right wheel) — the panel rebuilt (PL-127, «#3619»)

**How it works now.** Every row first shows its whole plan: what it tests, what you will do, and what you should feel.
**Nothing happens until you click START ROW.** A green **YOUR TURN** banner means it is waiting for you, and **only
DONE ends your turn**. The line under **SEEN NOW** tells you when the program has what it needs ("GOT IT, CLICK DONE").
A red banner means the program is driving the wheel: hands off, and **ABORT stops it at once**. Every row ends on a
**RESULT** screen that stays until you click **NEXT ROW** or **REDO ROW**. The forward button is always on the right,
ABORT and REDO always on the left, and only buttons that work are drawn. Enter and Esc work as the right and left
buttons.

**The reading is `band_ticks`:** the hall ticks the wheel turns from 120 ticks/s down to rest, the same on every row.
A spin row needs a hard spin. If it is too slow, the panel says so, and you just spin again.

**Three extra clicks, each asked on its row's panel** (each makes one of the interaction's checks able to fail): row 1's
first screen asks for a click on the empty panel, row 4's result asks for one REDO ROW, and row 6 asks for ABORT on its
first run, then REDO ROW.

| Row | You click, then | You should feel or see | Cell | Pre-registered reading | Fails if |
|---|---|---|---|---|---|
| 1 HOLD-RISE | START ROW; push the wheel firmly and keep pushing; DONE | the resistance **grow** while you hold it off its place | R17-T0-HOLDRISE | `rise_ms` 220–280 (driver 18; driver 17 read 289–291), and no slip, limit or fault before the ceiling | outside the band, or an event before the ceiling |
| 2 HOLD-SLIP | START ROW; turn it firmly; DONE | it **give way**, then drag | R17-T0-HOLDSLIP | starts HS_HOLDING at 0 (else NOMEAS), then HS_SLIPPED before any FAULTED | the hold persists, or FAULTED first |
| 3 HOLD-LIMIT | START ROW; a steady push for about 3 s; DONE | it hold, then **let go** | R17-T0-HOLDLIMIT | starts HS_HOLDING at 0 (else NOMEAS), then HS_LIMITED | it never hands off |
| 4 COAST AT REST | START ROW; spin it hard, let go; DONE when stopped | it spin freely and coast | R17-T0-RESTCOAST | band_ticks ≥ 7 | ≤ 6 |
| 5 E-STOP AS IT COASTS | START ROW; spin it hard, let go; DONE | it coast, then **stop abruptly** | R17-T0-RESTSHORT | band_ticks ≤ 4, the e-stop latched at the band entry | ≥ 5, or the short was not applied |
| (4 − 5) | — | — | R17-T0-STOPGAP | ≥ 3 ticks apart | < 3 |
| 6 FAULT, COAST MODE | START ROW; **hands off**; first run: ABORT as it spins up, then REDO ROW; the rerun ends by itself | the wheel coasts after the fault | R17-T0-FLTCOAST | band_ticks ≥ 7 and still FAULTED | either false, or it never reached AT_SPEED |
| 7 FAULT, BRAKE MODE | as row 6 | the wheel brakes hard after the fault | R17-T0-FLTSHORT | band_ticks ≤ 4 and still FAULTED | either false, or it never reached AT_SPEED |
| (6 − 7) | — | — | R17-T0-FLTGAP | ≥ 3 ticks apart | < 3 |
| 8 DRIVER COG STOPPED | START ROW; spin it hard, let go; DONE, then FINISH | it coast exactly as row 4 did | **R17-T0-FREEREF** | band_ticks ≥ 7 | ≤ 6 |

**The interaction's own checks, judged in the report from the log** (`T0-24,input` / `screen` / `status` records):

| Check | Passes when | Fails if |
|---|---|---|
| **UI-CLICK** — clicks arrive | every button click is a `T0-24,input` record naming that button | a click he made has no record, or a live button reads `MISS` |
| **UI-MISS** — the negative for UI-CLICK | the deliberate click in act 1 reads `hit,MISS` | it reads a button, or does not appear |
| **UI-WAIT** — no hand row moves on without him | every hand row's ACT → RESULT change follows a `DONE` or `ABORT` input record | an ACT screen of rows 1–5 or 8 ends with no such record |
| **UI-REDO** — the restart | act 2's row 4 shows `run,2`, with its own tries and result | no second run |
| **UI-ABORT** — ABORT on a powered row | act 3's row 6 run 1 ends `why,ABORTED`, its RESULT `screen` record within 100 ms of the ABORT `input` record, and run 2 measures | more than 100 ms, or no run 2 |

FREEREF is emitted first: if it fails, the instrument has not shown it can report a coast, and every coast cell is read
with that in mind.

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

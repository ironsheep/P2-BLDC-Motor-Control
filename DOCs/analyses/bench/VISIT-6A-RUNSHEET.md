# Visit 6a — run sheet (eight unattended loads, then one attended)

Run each command from the project root, in order. I read every log.

**Panic: PHYSICAL BATTERY DISCONNECT.** Nothing on the rig reaches the harness while it drives.

**Pull first.** Then check each banner before anything else — a load whose banner reads an older revision
certifies nothing, and Visit 3's first attempt was lost exactly that way (PL-68):

| Load | Banner must read |
|---|---|
| `t0` | `src_rev 10` |
| `t0-stopmode` | `src_rev 10`, and the banner says **ATTENDED, THE WHEEL SPINS ON TWO ROWS** |
| every `dual-*` | `src_rev 20`, `fmt 8` |

**Every run is wheels-lifted.** Rev B platform, on blocks, both wheels up and free, both motors connected,
pack charged. Nothing on this sheet needs the platform to move across a surface.

⛔ **I will not touch the tree while a load is in flight.** That matters more on this sheet than on any
before it: `dual-clock-200/-270/-300` are the one tier that writes to a source file (`CLK_FREQ` in
`test_bench_dual.spin2`), and an edit landing mid-run would compile into the next load.

## The visit, declared

Seven attributes, per *Shared vocabulary — the bench visit* (`~/.claude/skills-docs/SKILLS-AUTHORING.md`).

| | |
|---|---|
| **Purpose** | **Certification.** Visit 5 ended with zero failed cells and named three open things, all three now repaired in the tree; and **twenty-seven cells on this sheet have never run at all.** This visit says whether the R17 work does what it claims. |
| **Hardware risk** | Same kind as Visit 5 for the eight unattended loads — half speed, stopped dead, an e-stop latched and held, faults provoked on purpose, and the current limits lowered until the motor cannot turn, all wheels-up with no hands on the platform. **`t0-stopmode` is different in kind: your hands are on a wheel.** Four of its six rows are at rest with the wheel unpowered; **two of them spin the wheel under power and fault it on purpose, hands off, with SPACE live as an abort.** The panel names which is which before each row. Panic throughout: physical battery disconnect. |
| **Who can observe** | **Nobody, for the eight unattended loads** — every verdict is printed. **One observation is asked for in advance** (below, and it is the only one): on `dual-a`, **which ladder rungs you feel kick.** On `t0-stopmode` you are the instrument's hand: the panel names each action before its row, and **no key you press is read as a verdict** — every cell there is a hall-counter reading. |
| **Runs that carry state** | **None across loads.** Within a load, as before: `dual-b` and `dual-c` write the commutation offsets and restore them with a read-back, `dual-d` lowers the current limits and arms a command timeout and restores both. **New this visit:** the three `dual-clock-*` tiers each rewrite `CLK_FREQ` in `test_bench_dual.spin2` and put it back. A load that ends early leaves its restore undone, so **if one stops short, say so and leave the next until I have read that log.** |
| **Run length** | **~25 minutes of unattended running, then ~15 minutes of attended.** MEASURED at Visit 5: `dual-a` 5 min 39 s, `dual-b` 5 min 18 s, `dual-d` 54 s. MEASURED at Visit 3 from the log timestamps: each `dual-clock` load about 40 s, `dual-c` about 2 min. DERIVED: `dual-b` and `dual-d` each gain new steps, so allow a minute more apiece; `t0` about 2–3 min; `t0-stopmode` is paced by you — six rows, each an arm, a turn and a coast-down. |
| **Repeatability** | Every tier is repeatable and idempotent — a re-run costs only time. Faults are provoked and recovered inside the run; nothing needs a power cycle between loads. `t0-stopmode` may be re-run row for row if a row is spoiled. |
| **Variant matrix** | Nine loads: `t0` and `t0-stopmode` (one binary, two `-D` builds) × five `dual` parts at 270 MHz × three clock loads at 200 / 270 / 300 MHz × one rig (Rev B, paired 6.5in, 18.5 V). |

---

## What each load can decide that Visit 5 could not

Every load is here because something changed underneath it. The right-hand column is read from the diff,
not from the commit subject.

| # | Command | Last ran | What changed under it since — and so what the run decides |
|---|---|---|---|
| 1 | `tools/bench-run.sh t0` | Visit 5, `src_rev 3` | **Five new cells, and the fix for the damage Visit 5 found in this very tier.** `R17-T0-NOBOARDSTART` (PL-73), `R17-T0-ACCEL` / `-KMMI` / `-VOLTGET` (the API promises), `R17-T0-DEADGAP` (A1). `cc491bd` puts every cog start and stop in a quiet window — the PL-85 repair. The library under it changed too: the stop states, the API-promise fixes, the board refusal, the command timeout, the atomic hall read and the fault cause. |
| 2 | `tools/bench-run.sh dual-d` | Visit 5, `src_rev 14 fmt 5` | **The command timeout and the direction sign.** New steps CMDTIMEOUT and DIRSIGN with cells `R17-DUAL-CMDTMO-D`, `-WCMDTMO-D`, `-DIRSIGN-D`. Everything else in part D re-runs on a library that has since changed under it. |
| 3 | `tools/bench-run.sh dual-b` | Visit 5 | **PL-86's repair.** The fault provocation is now computed at speed per wheel instead of a fixed 180°, which is what tripped the 10 A abort at Visits 4 and 5 and left two cells NOMEAS twice. New: `R17-DUAL-FLTCAUSE-B`, `-OFFREST-B`, `-IDLEMOVE-B`, `-TURNDIST-B`, and STOPLIM now judged in the platform frame. |
| 4 | `tools/bench-run.sh dual-c` | **Visit 3**, `src_rev 11 fmt 3` | **The stop-state work's unattended half.** `R17-DUAL-FLTSTOP-C` says whether a fault delivers your `holdAtStop()` choice — FLOAT must coast further to rest than BRAKE. Also `-IDLEMOVE-C`, the computed provocation, and everything the library gained in the nine revisions since Visit 3. |
| 5 | `tools/bench-run.sh dual-a` | Visit 5 | **PL-87's repair — the instrument Visit 5 did not have.** Every ladder and clock rung now prints BM-RUNGTR, the transition from the command to the window start, and `R17-DUAL-TRKICK-A` judges it. Visit 5's table could not see a kick at all: rung 0, the control, read the same as every suspect. Also `-IDLEMOVE-A`. |
| 6 | `tools/bench-run.sh dual-clock-200` | **Visit 3**, as one `dual-clock` tier | **PL-69's cell.** Each clock lifetime now prints BM-HALLINT and folds `R17-DUAL-HALL-K200`: no illegal hall code. Visit 3's 200 MHz load read 3 and 5 illegal codes on the RIGHT motor, and nothing judged it. The hall read is now atomic (PL-90). |
| 7 | `tools/bench-run.sh dual-clock-270` | Visit 3 | `R17-DUAL-HALL-K270`, as above. |
| 8 | `tools/bench-run.sh dual-clock-300` | Visit 3 | `R17-DUAL-HALL-K300`, as above — and 300 MHz is where an illegal code is likeliest. |
| 9 | `tools/bench-run.sh t0-stopmode` | **never** | **The stop-state work's attended half**, and the only way to certify it. Eight new cells. **This tier's panel has never drawn on the rig**, so this load also certifies the panel; it is last for that reason. |

---

## Before the run: every new cell can fail

Doctrine D2 — a claim is not verified until its negative case is measured, and a cell that cannot exhibit
the difference proves nothing. Twenty-seven cells are new. Each one's negative case, and where that
negative case comes from:

### `t0` — five cells

| Cell | PASSES when | FAILS when — and where that comes from |
|---|---|---|
| `R17-T0-DEADGAP` | the compiled dead gap is at or above 250 ns in ticks at this clock | it is below it. **On file:** the deleted per-revision conditional asked for 52 ns on Rev B, out of spec on both boards' manuals (A1, PL-9). |
| `R17-T0-NOBOARDSTART` | `start()` on the empty group returns −1, records `ERR_BOARD_NOT_DETECTED`, starts no cog and leaks none | it returns a cog id or leaks one. **On file:** that is what the library did before PL-73. |
| `R17-T0-ACCEL` | three out-of-range rates are refused and change nothing, the 44 mm/s² anchor lands within 1% of the default `ramp_min`, and the top rate is above it | any factor in the mm/s² conversion is wrong — 1% of `ramp_min` is far tighter than any plausible factor error. |
| `R17-T0-KMMI` | 1 km converts to exactly 1000 m of ticks, 1 mi to exactly 5280 ft, and both are commandable | the conversion is inexact, or the unit is refused as a command. **On file:** `DDU_KM` / `DDU_MI` were read-only before this release. |
| `R17-T0-VOLTGET` | the motor and the running steering object both report the configured 18.5 V, and a not-yet-started steering object reports `PWR_Unknown` / 0 mV | a getter answers before a start (a value invented rather than measured), or reports a pack that is not the compiled one. |

### `dual-d` — three cells

| Cell | PASSES when | FAILS when — and where that comes from |
|---|---|---|
| `R17-DUAL-CMDTMO-D`, `-WCMDTMO-D` | **both limbs hold**: with a 500 ms timeout armed, a drive refreshed every 200 ms for 1.5 s keeps running, and one left silent then stops, no sooner than the timeout, inside the rest bound, reporting `ERR_COMMAND_TIMEOUT` | either limb fails, and **each is the other's negative case**: a timeout firing on a live link would stop the platform in the refreshed limb; a library with no timeout drives on through the silent limb's bound. Written into the step itself. |
| `R17-DUAL-DIRSIGN-D` | a positive `driveDirection()` slows the RIGHT wheel, leaving the LEFT ahead by the gap, and a negative one the reverse | either limb fails. **On file and measured:** before this release the sign was inverted — a positive direction slowed the LEFT wheel, and Visit 2's attended video saw the platform turn left (finding AC). That code fails both limbs; a harness that could not tell the wheels apart could not pass both. |

### `dual-b` — four cells

| Cell | PASSES when | FAILS when — and where that comes from |
|---|---|---|
| `R17-DUAL-FLTCAUSE-B` | both wheels latch `FC_LAG` as the provoked fault's cause | the cause is `FC_NONE` or the wrong one. Before S-7 there was **no cause recorded at all**, which fails it. |
| `R17-DUAL-OFFREST-B` | both wheels' offsets read back as written after the provocation | a restore did not take. Part C has carried this check; **part B wrote offsets with nothing checking the restore.** |
| `R17-DUAL-IDLEMOVE-B` | the stopped, uncommanded wheel drifts 2 ticks or less | a command reaches the wrong wheel and drives it tens of ticks. **On file:** PL-76's wrong-wheel ternary did exactly that, five times at Visit 4. |
| `R17-DUAL-TURNDIST-B` | each wheel of an unequal `driveForDistance(10, 2)` comes to rest within 2 ticks of **its own** limit | both wheels stop at one distance, or one overshoots. |

### `dual-c` — two cells

| Cell | PASSES when | FAILS when — and where that comes from |
|---|---|---|
| `R17-DUAL-FLTSTOP-C` | a fault under FLOAT travels at least 10 ticks further to rest than one under BRAKE | they read the same. **On file and measured:** the old driver shorted the windings on **every** fault, so both modes stopped identically — a short stops within one tick where an open bridge coasts 38–48 (Visit 2). |
| `R17-DUAL-IDLEMOVE-C` | as `-IDLEMOVE-B` | as `-IDLEMOVE-B`. |

### `dual-a` — two cells

| Cell | PASSES when | FAILS when — and where that comes from |
|---|---|---|
| `R17-DUAL-TRKICK-A` | a speed change from a running speed overshoots by no more than 10 err units above what the start from rest overshoots | it exceeds that. **The negative case is what you felt at Visit 5** — *"some are not kicking but many still are"* — which this must now fail if it is still true. The margin is DERIVED, not yet measured; **the first load reads the control's own spread**, so a surprising number here is information about the margin, not necessarily about the driver. |
| `R17-DUAL-IDLEMOVE-A` | as `-IDLEMOVE-B` | as `-IDLEMOVE-B`. |

### `dual-clock-200` / `-270` / `-300` — three cells

| Cell | PASSES when | FAILS when — and where that comes from |
|---|---|---|
| `R17-DUAL-HALL-K200` / `-K270` / `-K300` | no illegal hall code (`%000` or `%111`) over the clock's lifetimes | any is read. **On file and measured:** Visit 3's 200 MHz load read 3 and 5 on the RIGHT motor (PL-69) with nothing judging it. |

### `t0-stopmode` — eight cells

Each row's criterion is **the time the wheel takes to fall to half the rate it had when you let go** —
not how far it carries on, which would scale with how hard you pushed. A shorted winding brakes with a
torque proportional to speed; a free one does not. Free is at or above 150 ms, braked at or below 60 ms,
with a 90 ms dead band between them, both DERIVED from Visit 2's measurement of an e-stop stopping a
half-speed wheel within one tick where a released bridge coasted 38–48.

| Cell | PASSES when | FAILS when |
|---|---|---|
| `R17-T0-HOLDPWR` | turning the held wheel by hand makes the driver **record a fault** | it does not — and it cannot, unless the bridge is being driven, because the driver skips its fault test whenever the bridge is not DRIVE. This is the cell that says the hold is powered. |
| `R17-T0-RESTCOAST` | `holdAtStop(FALSE)` at rest halves in ≥150 ms — it coasts | it brakes. **This is the discriminating row of PL-89**: the old build's float shorted the windings. |
| `R17-T0-RESTSHORT` | the e-stop halves in ≤60 ms — it brakes | it coasts, which would contradict the e-stop's own documented *"immediately stop"*. |
| `R17-T0-STOPGAP` | coast and e-stop differ by ≥100 ms | they do not, which would say the two states are one — exactly the old build's behaviour. |
| `R17-T0-FLTCOAST` | a fault under FLOAT coasts **and** the driver is still FAULTED when the row ends | it brakes, or the fault did not survive to be measured. |
| `R17-T0-FLTSHORT` | a fault under BRAKE brakes **and** is still FAULTED | it coasts, or the fault did not survive. |
| `R17-T0-FLTGAP` | the two fault rows differ by ≥100 ms | they do not — the old driver's fault shorted whatever you had selected. |
| `R17-T0-FREEREF` | `stop()`, with the pins released, coasts | it does not — **and this is the control on the whole measurement.** If the released pins do not read as free, no other "free" verdict on this sheet can be trusted, whatever it says. |

---

## The one observation asked for, and it is asked for now

**On `dual-a`, note which ladder rungs you feel kick.** The ladder climbs twelve rungs per direction per
wheel; the rung number is printed as each one runs. A rung number, or "the first few", or "none" — all
three are useful.

**Why it is asked before the run and not after:** `R17-DUAL-TRKICK-A` is new, its margin is derived
rather than measured, and your hand at Visit 5 was the only instrument that ever detected the kick. If
the cell passes every rung and you still feel one, that is a finding about the instrument, and it can
only be made if both readings exist from the same run. It is the only observation this sheet asks for.

---

## Two things this sheet states, so no one has to infer them

**1. The fault provocations now fault by construction, under the same 10 A abort that stopped them
twice.** `dual-b`'s fault-API trial and `dual-c`'s POSTFLT no longer write a fixed 180° offset. Each
drives to speed, reads that wheel's own position error, and shifts both of its offsets by exactly what
lands the error on the driver's fault test, which fires in the next control frame — before current can
build. The 10 A abort is unchanged and still live; what changed is that the fault now arrives first. If
a trial still prints `NO_FAULT`, that is the third time and it is a finding, not a retry.

**2. `cc491bd`'s claim is proved by the absence of two things in the logs, and I check every log for
both.** Every bench cog start and stop now sits in a quiet window — 2 ms before, 10 ms after. The proof
is that **no record carries a run-together `CogN` prefix and no record is truncated.** At Visit 5 one
`t0` verdict was destroyed on the wire and recovered only because a USB capture happened to exist
(PL-85). **If you take a USB capture again, I will compare it line for line against the debug log; if
you do not, the debug log alone still carries the proof.**

---

## Stop and tell me if

- a load ends with an `ERROR:` line from `bench-run.sh` — that load certified nothing (it means the image
  emitted nothing, the PL-74 failure); power-cycle the P2 and re-run **that** tier before going on;
- a load ends early or you stop one — its within-load restore did not run, so the next load starts from
  an unknown state;
- `t0-stopmode`'s panel does not draw, or draws wrong — the rest of that tier is worthless without it,
  and everything before it is already banked;
- anything moves that this sheet did not say would move.

---

## Not on this sheet, and why

| Not run | Why |
|---|---|
| `char`, `detect`, `detect-lib`, `detect-phase2` | **No cell in them certifies anything this release needs.** `char`'s cells are sensing and steering start, and `dual` covers the hall read; nothing in the detect family changed beyond the board refusal, which `t0` certifies. They are not unchanged — both moved onto the shared record builder and both deliberately dropped fields that fed no decision — but that retirement is confirmed by whatever run they next have, and it decides nothing here. |
| `dual-brake` | Its panel is part of the `dual-ui` rebuild that has never run. It belongs after `dual-ui`, at Visit 6b. |
| `scan`, `scan-wdtest` | The scan is being redesigned for the lag-limited driver («#3575»); running today's would measure the droop it was never built to stop on. Visit 6b. |
| `dual-ui`, the spin-in-place floor tier | Visit 6b, in that order — `dual-ui` certifies the panel the floor run depends on. |

---

*Written for «#3579». The report is one analysis per set of logs, read from the logs themselves.*

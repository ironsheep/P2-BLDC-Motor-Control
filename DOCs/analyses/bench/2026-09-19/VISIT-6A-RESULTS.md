# Visit 6a — Results

**Run:** 2026-09-19, 17:25–17:49 local. Wheels lifted, Rev B, both motors, 270 MHz except the clock sweep.
**Sheet:** [`VISIT-6A-RUNSHEET.md`](../VISIT-6A-RUNSHEET.md) · **Task:** «#3579» · **Tree:** `912f950`
**Pack:** 20.40 V at start, 20.09 V at end (18.5 V nominal 5S). 0.31 V sag across the session.

Provenance marks per doctrine overlay P8: **MEASURED** = cites a log line · **DERIVED** = my reasoning
from traced claims · **STEPHEN** = his words with the date · *unlabelled* = the sources were read and do
not settle it.

---

## 0. The headline

**Eight of nine loads ran. 127 cell instances: 116 PASS, 2 FAIL, 9 NOMEAS — and 10 that were declared
and never emitted a verdict.** Every one of the three repairs this visit existed to certify was
exercised, and two of the three are confirmed.

| Load | Log | Instances | PASS | FAIL | NOMEAS | Declared, never emitted |
|---|---|---|---|---|---|---|
| `t0` | `172524` | 28 | **28** | 0 | 0 | **2** |
| `dual-d` | `172627` | 22 | 18 | **2** | 2 | 0 |
| `dual-b` | `172908` | 23 | 18 | 0 | 5 | 0 |
| `dual-c` | `173537` | 15 | 13 | 0 | 2 | 0 |
| `dual-a` | `173751` | 21 | **21** | 0 | 0 | 0 |
| `dual-clock-200/-270/-300` | `174430/174528/174623` | 18 | **18** | 0 | 0 | 0 |
| `t0-stopmode` | `174735` | **0** | — | — | — | **8** |

**The three things this visit came to settle:**

1. ⭐ **PL-69 is closed** — zero illegal hall codes at 200, 270 and 300 MHz (§7).
2. ⭐ **PL-87's instrument works, and reads zero kicks** (§6) — but Stephen's own reading was not
   recorded this time, and it is the half that matters (§10).
3. ⛔ **PL-86 failed a third time, and the cause is now identified** (§5). It is not the provocation.

**And two things went wrong that were not on the sheet's list of risks:**

- ⛔ **The attended tier never drew its panel, so none of its eight cells ran** (§2). **That one is
  mine.** My first cause for it was wrong — Stephen caught it — and §2 now carries the correction, a
  clean code audit, and the one A/B that will settle it.
- ⛔ **PL-85 is NOT closed.** The dual harness is clean across 27,000 records, but `t0` still lost two
  verdicts and truncated a third record at a cog start (§3). My first reading of this said it *was*
  closed; that reading was wrong and is corrected below.

---

## 1. Banner check

MEASURED. Every load that emitted matched the sheet.

| Log | Tier | Banner |
|---|---|---|
| `172524` | t0 | `src_rev 10` (L19) ✅ |
| `172627` | dual-D | `src_rev 20, fmt 8, part D` ✅ |
| `172908` | dual-B | `src_rev 20, fmt 8, part B` ✅ |
| `173537` | dual-C | `src_rev 20, fmt 8, part C` ✅ |
| `173751` | dual-A | `src_rev 20, fmt 8, part A` ✅ |
| `174430/174528/174623` | dual-CLOCK | `src_rev 20, fmt 8, part CLOCK`, clkfreq 200/270/300 M ✅ |
| `174735` | t0-stopmode | `src_rev 10`, and the ATTENDED banner ✅ |

`174429` is an 8-line log with a download start and nothing else — a load that was begun and replaced a
second later by `174430`. It certified nothing and cost nothing.

---

## 2. ⛔ The attended tier never drew its panel — and the cause is still open

**STEPHEN 2026-09-19:** *"your t0-stopmode put up no ui so couldn't tell what to do."*

**What the log shows (MEASURED, `174735`):** the binary downloaded and ran. The banner printed, all eight
`SIGNOFF-DECL` lines printed, `T0-24,begin` printed, and the driver's two cogs started (`Cog1`/`Cog2
INIT`, L20–21). Row 0 announced itself at 17:47:37.823 with its prediction and the action it was asking
for. **Then nothing for 95 seconds**, until `[TX] s<cr>` at 17:49:12 — Stephen typing `s` into the
terminal — and the session ended.

**The discriminating measurement:** the log contains **zero backtick display commands and zero
`PC_KEY`**, over roughly 1,900 key-poll iterations. The 2026-09-15 `t0-hand` log, whose panel did draw
on this rig, carries **718 backtick commands and 487 `PC_KEY` reads**.

**It is not the tier's code.** MEASURED by scanning the compiled image: `` `PLOT t0stop TITLE … SIZE 480
300 POS 60 80 HIDEXY UPDATE `` and its four `LAYER` commands are in the binary, byte for byte, in the
same shape as `t0-hand`'s working set. The assets are committed and present. The code ran — the records
either side of it printed.

> ⛔ **CORRECTED 2026-09-20. The cause below is WRONG and the finding has no confirmed cause.** STEPHEN:
> *"we have run plot windows before and i'm not sure the --console-mode prevents them i'm suspecting a
> code problem."* `pnut-term-ts --help` says `--console-mode` *"adds delay before close"*, `--headless`
> is the flag that suppresses windows (never passed here), and `--exit-on-end-session` is documented as
> **headed** batch mode that renders windows. The tree also held the counter-example I never looked for:
> `BENCH-PASS-1-RUNSHEET.md` has operators running `tools/bench-run.sh char`, and the 2026-09-12 `char`
> log carries a PLOT window and 18,738 display commands -- a panel drawn **through this runner** with
> `--console-mode` already in it. My argument rested on a correlation (every display-command log is
> dated 11-15 September) reported as a cause. **The code audit he then asked for comes back clean**, and
> the remaining step is one A/B at the rig: run `t0-hand`, whose panel is known to have drawn here, then
> `t0-stopmode`. Both the audit and the A/B are in PL-92.

**Where the commands went (this reading is SUPERSEDED -- kept because the measurements in it stand):**

- MEASURED: `tools/bench-run.sh` has run the terminal as `pnut-term-ts -r <binary> --console-mode
  --exit-on-end-session` since 2026-09-10 (`07f2509`). The script's own comment chose `--console-mode`
  over `--ide` deliberately, for a batch run.
- RECORDED: the 2026-09-15 session whose panel drew built and ran Tier 0 **"as built at the bench"**
  (`VISIT-2-ATTENDED-RESULTS.md`), i.e. not through the runner.
- MEASURED: **every log in the tree that ever carried a display command is dated 2026-09-11 to
  2026-09-15.** Thirteen logs; none later. No panel has drawn since the runner became the only path.
- DERIVED: the P2 emits the same bytes whatever the host does, so the loss is on the host side — a
  console-mode session opens no window, and does not write display commands to the log. With no window
  there is no `PC_KEY`, so the tier could wait forever; the `s` Stephen typed went out over the serial
  line as terminal input, which the harness never reads.

**What is actually known about the blast radius:** `t0-hand`, `dual-brake`, `dual-floor`, `dual-ui`
and `t0-stopmode` have all gone unrun through this path since their panels were added, so **it is not
known whether any of them draws**. `dual-ui` and the floor tier are Visit 6b's first two loads, which is
what makes the one-minute `t0-hand` A/B worth doing before that visit rather than during it.

**What I got wrong, and it is a doctrine miss, not a coding slip.** The sheet said this tier's panel had
never drawn on the rig and put it last for that reason — but I checked that the *panel technique* was
proven and never checked that the *path that would run it* had ever carried a panel. Overlay P7 is about
the whole step a person uses at the bench, and the runner is part of that step.

**Filed as PL-92**, which carries the full code audit (a `PLOT` create call present and first, four
`LAYER`s, `crop`+`update` at setup and per frame, call sites reached, assets verified 24-bit and
uncompressed, budgets at 164/255 records, and the compiled encoding identical to the proven panel) and
the A/B that decides between "the tier" and "the path".

---

## 3. `t0` — every cell that reported passed, and two verdicts were lost on the wire

**MEASURED:** 28 SIGNOFF instances, **28 PASS, 0 FAIL**. The five cells new since Visit 5 all passed:

| Cell | Result | What it settles |
|---|---|---|
| `R17-T0-DEADGAP` | PASS, n=1 | The compiled dead gap meets both manuals' 250 ns minimum (A1, PL-9). |
| `R17-T0-ACCEL` | PASS, n=5 | `setAcceleration()` refuses three out-of-range rates, and the 44 mm/s² anchor lands within 1% of the library's own default ramp (G). |
| `R17-T0-KMMI` | PASS, n=3 | Kilometres and miles convert exactly and can now be commanded (K). |
| `R17-T0-VOLTGET` | PASS, n=3 | The drive-voltage getter answers on both objects and reports nothing before a start (AK). |
| `R17-T0-NOBOARDSTART` | **LOST** | — see below. |

### 3a. ⛔ PL-85 is not closed, and my first reading of this was wrong

**MEASURED:** the `t0` log declares 24 cells and emits 22. Two are declared and never reported:
**`R17-T0-NOBOARDSTART`** and **`R1-T0-EXHAUST`**.

**MEASURED, the visible damage.** The source emits `T0-23,begin,no_board_start`
(`test_bench_t0.spin2:1812`). The log carries `T0-23,begin,no_bo` (`172524:180`) — **cut off mid-word**,
immediately before the library's refusal line and a `Cog1`/`Cog2` start burst. `T0-23`'s `end` record and
its SIGNOFF never appear at all. `R1-T0-EXHAUST`'s verdict goes missing inside the seven-cog exhaustion
burst the same way.

**So three records were damaged or destroyed, two of them verdicts** — the same failure mode, in the same
tier, that cost a verdict at Visit 5 (PL-85).

⚠ **Correcting myself:** my first pass over these logs checked only the dual harness's `BM-*` record
shape, found zero run-together prefixes and zero truncation in 27,000 records, and concluded PL-85 was
closed. That check never looked at the `t0` dialect, where the losses are. The corrected reading:

- **The quiet windows work where they were measured.** MEASURED: across all ten logs, **zero** log lines
  carry more than one `CogN` prefix, and no `BM-*` record is truncated.
- **They are not sufficient in `t0`.** That tier starts and stops far more cogs than any other, and it is
  still losing records at those bursts.

**Consequence:** PL-73's certification (`start()` refuses an undetected board) is **still owed** — the
cell ran, the driver behaved (the refusal line is in the log), but the verdict did not survive the wire.

---

## 4. `dual-d` — the new cells pass, and two long-standing cells fail by a hair

**MEASURED:** 18 PASS, 2 FAIL, 2 NOMEAS. **All three cells new since Visit 5 passed:**

- `R17-DUAL-CMDTMO-D` and `R17-DUAL-WCMDTMO-D` (PASS, both forms) — the opt-in command timeout (S-8)
  works: a refreshed drive keeps running and a silent one stops, no sooner than the timeout, reporting
  `ERR_COMMAND_TIMEOUT`. **Both limbs held**, which is what makes the cell mean anything.
- `R17-DUAL-DIRSIGN-D` (PASS) — a positive `driveDirection()` now slows the RIGHT wheel. Finding **AC**
  is confirmed fixed in `57e5785`; the platform turns the way the documentation says.

### The two failures, and both are marginal

| Cell | Measured | Band | Reading |
|---|---|---|---|
| `R16-DUAL-TIMESTOP-D` (BOTH) | **321 ms** | −2000 … **320** | **One millisecond over.** The single-wheel form of the same mechanism read 254 ms and passed. |
| `R16-DUAL-FRONTST-D` (BOTH) | `late,1` of 33,195 passes | 0 late | **One late pass in 33,195.** `max_us 914` against a `slot_us 1000`. The single-wheel form read `late,0`, `max_us 299`. |

**DERIVED, and worth more than the two FAILs:** the steering front cog is running at **91 % of its
1 ms slot** (914 µs peak) where the single-wheel front cog uses 30 % (299 µs). One late pass in 33,195 is
what a loop that close to its budget looks like. That is a headroom finding, not a defect — but it is
the number to watch if anything else is ever added to the front cog's pass.

The two NOMEAS (`DERATE-D` LEFT, `BLOCKED-D`) are the designed ones carried from Visit 5.

---

## 5. ⛔ `dual-b` and `dual-c` — PL-86 a third time, and the cause is the lag limiter

Seven cells are NOMEAS across the two parts, and every one of them is downstream of the same event.

### 5a. What happened

**MEASURED, `dual-b` (`172908`):** the fault-API trial computed its shifts, wrote them, and never
faulted —
`BM-FLTAPI … l_shift,240, r_shift,108, l_off,283, r_off,151, latched,FALSE, l_cause,NONE, r_cause,NONE,
why,ABORTED`, with `BM-ABORT … reason,ABS_CURRENT, value,2_655, scope,TRIAL`.

**MEASURED, `dual-c` (`173537`):** two aborts, one per wheel —
`BM-ABORT … motor,LEFT … ABS_CURRENT, value,3_435` and `… motor,RIGHT … value,3_771`.

The threshold is `ABS_ABORT_MV = 1_500` (10 A at 150 mV/A). Half-speed running current is about
**900 mV** (MEASURED at Visit 3, `debug_260916-123957.log` tid 11). So these trials drew **three to four
times** the normal running current.

### 5b. The provocation's arithmetic is correct — I checked it against the logs

DERIVED, from the shifts the log printed. `faultShiftDeg()` computes `shift = (err + 128) & 255`, in
degrees. Inverting the two shifts the run recorded:

| Wheel | Shift recorded | Implied mean `err` at speed | Where the shift should land `err` |
|---|---|---|---|
| LEFT | 240° → 171 units | **+43** | 43 − 171 = **−128** ✅ |
| RIGHT | 108° → 77 units | **−51** | −51 − 77 = **−128** ✅ |

Both land exactly on the wrap, three units past the `|err| >= 125` fault test. **The redesigned
provocation is not the defect**, and the opposite signs are right — the steering object reverses the
right wheel.

### 5c. What actually stops the fault

DERIVED: **the driver's lag limiter holds the field back as `err` grows, so `err` never reaches the
fault test.** Instead the motor sits badly commutated and draws current until the harness's abort fires.
The limiter is doing its job; the provocation was designed against a test the limiter now prevents from
being reached.

⭐ **This is the same mechanism as PL-46**, already recorded against the commutation scan: *"its window
edge is found by walking until the motor FAULTS … the lag limiter now makes it DROOP instead."* The scan
and the fault provocation are two instruments with one broken assumption, and «#3575» is already
redesigning the first of them.

### 5d. ⭐ But it faults once per wheel — and then nothing else works

**MEASURED, `dual-c` POSTFLT, all twelve traces:**

| tid | Motor | Cause | Mode | Ended |
|---|---|---|---|---|
| 9 | LEFT | FAULT | FLOAT | **REST**, `rest_k 278` |
| 10 | LEFT | FAULT | BRAKE | ABORT |
| 11–14 | LEFT | ESTOP | both | ABORT |
| 15 | RIGHT | FAULT | FLOAT | **REST**, `rest_k 257` |
| 16 | RIGHT | FAULT | BRAKE | ABORT |
| 17–20 | RIGHT | ESTOP | both | ABORT |

**The first trace on each wheel faults properly** — `st,FAULTED, flt,TRUE, e,-101` — and coasts to rest.
**Every trace after it aborts**, including the e-stop traces, which write no offsets at all. The aborted
traces carry **no samples**: the abort fires during the next trial's drive-up, before the instrument
arms. The offsets were correctly restored each time (`BM-OFFREST … ok,TRUE`).

**MEASURED, and this is what makes it new:** at Visit 3 the same segment ran **all twenty traces to
`end,REST` with zero aborts**. What changed is that the provocation now really faults — so this is the
first visit at which anything downstream of a real fault has ever been exercised.

**DERIVED:** after a genuine fault and the harness's own recovery (`BM-RECOVER … step,RESET,
cleared,TRUE, ms,31, st,STOPPED, flt,FALSE` — the recovery reports success), the next drive-up on that
wheel draws three to four times normal current. Whether that belongs to the driver's post-fault state or
to the harness's recovery sequence is **not settled by these logs**, and it is the next thing to chase.
It is a user-visible shape either way: fault, recover, drive again.

**What is NOMEAS because of all this:** `R17-DUAL-FLTCAUSE-B`, `R14-DUAL-FLTAPI-B`,
`R16-DUAL-FLTRETRY-B`, `R14-DUAL-RSTPROV-B` (both wheels), and **`R17-DUAL-FLTSTOP-C` (both wheels)**.

⛔ **So both halves of R17.1's fault claim are un-evidenced.** `FLTSTOP-C` is NOMEAS here, and the
attended rows that would have measured the same thing by hand never ran (§2). *A fault delivers your
`holdAtStop()` choice* remains **designed and unproven**.

### 5e. What did pass in `dual-b` and `dual-c`

`R17-DUAL-OFFREST-B` (both wheels) — the offset restore takes, which part B never checked before.
`R17-DUAL-IDLEMOVE-B/-C` (all four instances, measured **0** ticks) — the uncommanded wheel does not
move, so no command is reaching the wrong wheel; PL-76's class of defect is absent.
`R17-DUAL-TURNDIST-B` — an unequal `driveForDistance(10, 2)` stops each wheel at its own limit, worst
case **1 tick** (AB).

---

## 6. `dual-a` — every cell passes, and the kick instrument reads zero

**MEASURED:** 21 instances, **21 PASS**, including PL-87's new instrument.

`R17-DUAL-TRKICK-A`: **0 kicks of 22 rungs, each wheel.** The transition records behind it
(`BM-RUNGTR`, 48 of them) show `tr_over` of **36–39 on the starts from rest** and **≤ 5 on every change
of speed**, with three at or below zero.

**DERIVED:** the transition overshoot on a change of speed is now far smaller than on a start from rest,
which is what `caa5e3c` set out to achieve, and the start from rest legitimately keeps the largest
transition. Visit 5's table could not see any of this — rung 0, the control, read the same as every
suspect.

⚠ **This is exactly the case the sheet asked an observation for, and the observation was not recorded.**
The instrument now says there is no kick. At Visit 5 Stephen said *"some are not kicking but many still
are."* If he still felt one today, the instrument is wrong and this cell is a false pass; if he felt
none, PL-87 and PL-78 are both closed. **One reading decides it, and only he has it** (§10).

---

## 7. ⭐ The clock sweep — PL-69 is closed

**MEASURED:** three loads, 18 instances, **all PASS**.

`R17-DUAL-HALL-K200`, `-K270`, `-K300`, both wheels: **zero illegal hall codes** over every lifetime at
200, 270 and 300 MHz. Visit 3's 200 MHz load read **3 and 5** illegal codes on the RIGHT motor with
nothing judging it (PL-69).

**DERIVED:** the atomic hall read (`PL-90`, `6be991a`) removes the illegal codes across the whole clock
range. The negative case is on file from Visit 3, on the same rig, at the same clock — so this is a
measured fix, not an absence of evidence.

---

## 8. What this visit changes

1. **PL-69 is closed** (§7) and **finding AC is confirmed fixed** (§4).
2. **The S-8 command timeout and the three API-promise cells are certified** (§3, §4) — five of
   «#3569»'s and «#3570»'s promises now have run-time evidence.
3. **PL-87's instrument is built and reads clean** (§6), pending Stephen's own reading.
4. **PL-86 is re-diagnosed, not merely re-failed** (§5c): the lag limiter, not the provocation, and it
   is the same cause as PL-46. That merges two open findings into one problem with one fix.
5. **PL-85 is reduced but open** (§3a): the dual harness is clean; `t0` still loses verdicts.
6. **A new defect class is exposed** (§5d): everything downstream of a real fault. It was unreachable
   until the provocation started working.
7. **The release is not affected by any of this yet** — no cell that failed is a driver promise. But
   two promises are still unproven: the fault half of `holdAtStop()` (§5d) and the board refusal (§3a).

---

## 9. New findings filed

| id | Summary |
|---|---|
| **PL-92** | The bench runner runs the terminal in console mode, which cannot draw a panel — so every attended tier (`t0-hand`, `dual-brake`, `dual-floor`, `dual-ui`, `t0-stopmode`) is unrunnable through it, and has been since 2026-09-10 |
| **PL-93** | After a real fault and a successful recovery, the next drive-up on that wheel draws 3–4× normal current and trips the absolute-current abort; every trial after the first fault is lost |
| **PL-94** | `t0` still truncates and loses records at cog-start bursts, despite the quiet windows: two verdicts lost and one record cut mid-word this visit (PL-85's remainder) |

**Updated:** PL-86 — cause identified (the lag limiter, shared with PL-46); the computed provocation's
arithmetic is confirmed correct and is not the defect.

---

## 10. What is owed, and by whom

| Owed | Who | Why it matters |
|---|---|---|
| Which `pnut-term-ts` invocation gives a GUI session | **Stephen** | Blocks every attended tier, including Visit 6b's first two loads. Asked as this report's one question. |
| Whether he felt a kick on any `dual-a` rung | **Stephen** | Decides whether `TRKICK`'s 0-of-22 is a real pass or a false one (§6). Queued behind the question above. |
| The fault half of `holdAtStop()` | the bench | NOMEAS unattended (§5d) and never run attended (§2). |
| PL-73's board refusal | the bench | The cell ran and its verdict was lost (§3a). |
| A provocation the lag limiter cannot absorb | design | PL-86 + PL-46, one problem (§5c). «#3575» already owns the scan half. |

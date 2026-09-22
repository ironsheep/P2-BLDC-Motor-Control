# Bench Readiness — Sprint Plan

**Written:** 2026-09-10
**Entry build:** `VERSION` = 5.0.2 · `main` = `develop` = `a80f8e6`
**Target build:** ~~5.0.3 (patch)~~ → **6.0.0** *(revised 2026-09-11)*

> ⛔ **READ THE REVISIONS BEFORE THE BODY.** Two things on this line were true on
> 2026-09-10 and are not true now. The build is **6.0.0**, a major bump, and this
> plan **does** change motor behaviour. The live ordering is
> [*Execution model — revised 2026-09-11*](#execution-model--revised-2026-09-11);
> the dated findings are in [*Sprint Revision — 2026-09-11*](#sprint-revision--2026-09-11).
> Everything between them is preserved as written and is dated, not current.
>
> **Newest, and it governs:** [*Sprint Revision — 2026-09-17 (night)*](#sprint-revision--2026-09-17-night-not-shippable-and-the-release-widened)
> — 6.0.0 ruled not shippable; the release widened (API promises, hall, faults, style gate, confirmed offsets);
> the R17 work set and its order. Earlier revisions (2026-09-11, -13, -15, -16) are dated history.

**Scope as written 2026-09-10 — SUPERSEDED:** *"get the bench suite built, run it, and
record what it decides. The driver fixes are a separate sprint. Nothing in this plan changes
motor behaviour."*

**Scope now:** the driver fixes are **in** this plan, built in parallel silos and certified
in batched bench passes, and the motor subsystem's cog shape changes before release. That is
why the bump is major.

**Governing analysis:** [`../analyses/BENCH-TEST-PLAN-2026-09-10.md`](../analyses/BENCH-TEST-PLAN-2026-09-10.md),
[`../analyses/DRIVER-AUDIT-2026-09-09.md`](../analyses/DRIVER-AUDIT-2026-09-09.md),
[`../analyses/DRIVER-SAFETY-AND-CAPABILITY-STUDY-2026-09-09.md`](../analyses/DRIVER-SAFETY-AND-CAPABILITY-STUDY-2026-09-09.md),
[`../analyses/BOARD-REVISION-FACTS.md`](../analyses/BOARD-REVISION-FACTS.md)

---

## Sprint Start Record — 2026-09-10

Recorded by `sprint-start`. These are the things that depend on *when* execution begins and
could not be pinned at plan-authoring time.

### 1. Outgoing build number — **5.0.3**

Agreed with Stephen 2026-09-10: *"this will be a patch release of the driver as we build it,
but we're not fixing the driver yet."* Entry `VERSION` = 5.0.2; `git describe` = `v5.0.2-13`.
`VERSION` is bumped in §10 and tagged after §8 completes, so the release carries the bench
results rather than only the scaffolding.

### 2. Working tree audit — **clean, no decision needed**

Re-checked live rather than trusting the session preamble:

| Check | Result |
| --- | --- |
| Uncommitted edits | **none** |
| Untracked files in `src/`, `tools/`, `DOCs/`, `.claude/` | **none** |
| Branch vs. origin | `main` in sync; `develop` identical |

Neither hazard this step exists to catch is present: nothing mid-edit in a file the sprint
will modify, and no untracked source the plan assumes exists. The 5,035 lines of study work
that were uncommitted earlier on 2026-09-10 were committed and pushed before this audit.

### 3. Tracking-tool readiness — **READY**

| System | State | Action |
| --- | --- | --- |
| todo-mcp tasks | 1 total, 1 completed (`#3470`), 0 pending / in-progress / paused | Archived to `tasks/archives/archive_20260910_152316.md` |
| todo-mcp context | **0 keys** | None needed — iron rule #3 fired correctly on `#3470`'s completion |
| auto-memory | 7 files, `MEMORY.md` 13 lines (audit threshold ~150) | Superseded the time-bounded `project_driver_audit_resume_2026_09_09.md` with a sprint pointer; predecessor deleted in the same operation |

No stranded `task_#N_*` keys, no leftover pending tasks, no in-progress task to adjudicate.
**Cross-audit (§4): no prior audit exists for this project, so there is no recurrence signal
yet — a single occurrence is data, not a process finding.**

### 4. Entry baseline — **clean build, gate green, zero failure groups**

**§1 Clean build** — `BUILD_COMMAND` over the six library objects: exit 0,
**0 warnings, 0 errors.** §1's zero-warnings rule is absolute and is met with nothing to sweep.

**§2 / §2a Substitute gate.** This project has no automated behavioural suite, so `TEST_COMMAND`
is a **compile-all sweep**, `tools/build-check.sh`. Restated in its own terms per the project
overlay:

- **Failure unit:** a `.spin2` file in `src/` that compiles under **no** config block. Failing
  under *some* blocks is normal and expected — a dual-motor top cannot compile under a
  single-motor configuration — so a per-config failure is not a finding.
- **Result: PASS — 39/39 tops certified**, both release demos certified
  (`demo_single_motor` @ config `:130`, `demo_dual_motor` @ config `:180`).
- **Failure groups: none.** The overlay's first triage question — config mismatch or real
  error — does not arise.

**§3 Skips — one exclusion, named.** `hng034rm.spin2`, printed on every run with its reason.
39 examined + 1 excluded = 40 files in `src/`, matching the tree. The gate derives its file
list **mechanically** from `src/*.spin2` rather than a hand-kept roster, so it cannot report
green because files were never examined. PL-1 records why the exclusion is permanent.

> **A green gate is a compile result and nothing more.** It says every file compiles somewhere
> and both flagship demos are certified. **It says nothing about whether a motor turns, holds
> position, or ramps correctly.** Behavioural verification lives on hardware — against
> `{{CANONICAL_TEST_TARGET}}`, the P2 Edge Module with Universal Motor Driver boards — and
> producing it is precisely what §3-§8 of this sprint exist to do.

**Fix-when decision: not required.** There are no failure groups to fix, fold, or defer.

**This is the entry baseline `sprint-closeout` will assert the exit baseline against:** build
clean with 0 warnings, gate 39/39 with both release demos certified, one named exclusion.
Exit must be no worse. §1 adds `tools/check_style.sh`, whose **entry state is expected to be
red** on the pre-existing tree — that is a new instrument being introduced, not a regression.
**§1b commits to clearing it tree-wide before the tag**, so at closeout this gate is green
rather than deferred.

---

## Open Questions

**None.** The questions pass reached empty on 2026-09-10. Every item that was open has been
resolved and the resolution is recorded in the section that depends on it:

| Was open | Resolved |
| --- | --- |
| Which dual config block for the bench | §4 — block at `:181`, with `:198` as the alternate |
| How the harness reaches per-wheel driver state | Shipped 2026-09-10 — `c22dba1`, TEST-USE ONLY pass-throughs |
| Are the 64010's 4th-channel FETs populated | Yes, all four — §7, and `BOARD-REVISION-FACTS.md` §2 |
| Vendor deadtime minimum | 250 ns, **both** revisions — §7, and finding **A1** |
| `DEBUG_MASK` scope | **Per-file**, but sourceable from a shared config object — §2, proven by compile experiment |
| How far the DEBUG conversion goes | Option A, two objects — §2 |
| PL-2 in scope? | Not a scope choice — conformance is owed on every Spin2 deliverable. §1 builds the instrument |
| Meter peak-register reset behaviour | **Deliberately designed around** rather than resolved — §5, §8 |

**One input is still unknown and is handled by design rather than by waiting:** how the
system meter's `Ap`/`Vm`/`Wp` peak registers reset. §5 and §8 make the harness indifferent to
the answer. Stephen characterises the meter during the Tier 0 session (§8.1) and the answer
changes session *pacing*, never harness *code*.

---

## Sprint Revision — 2026-09-11

**The Open Questions section above reached empty on 2026-09-10 and is preserved as written.
It is no longer true.** The Tier 0 regression run and the analysis around it reopened
questions and added work. This section records what changed; the sections it amends are
marked inline below rather than rewritten.

### Tier 0 regression — PASSED

Evidence: [`DOCs/analyses/bench/2026-09-11/debug_260911-143911.log`](../analyses/bench/2026-09-11/debug_260911-143911.log)

All five fixes committed in `aea4981` confirmed against their predictions:

| Fix | Predicted | Measured |
| --- | --- | --- |
| **F** | 175 ticks, `agree,1` | `ddu_m` / `ddu_cm` / `ddu_mm` all 175, `agree,1` |
| **A1** | `dead_gap,70` unchanged | `dead_gap,70` |
| **A2/A3** | `detected_board,21`, "Rev A -USER FORCED" | exactly that |
| **AE** | abort on P8_P23, success on P32_P47 | `! ERROR: validatePinBase() … overlaps`, then clean |
| **PL-14** | no observable change | none |

«#3484» and «#3476» are closed on this run.

### Five new findings

1. **AD+ — the `start()` return contract is wrong at six sites.** DERIVED from the 2026-09-09
   audit (finding C): the chained `ok := motorCog := coginit(…) + 1`, at **six** sites, returns
   cog id + 1 on success and 0 on failure, while its doc comment promises the cog id or −1. The
   two-wheel mask `(1<<(ltcog-1))|(1<<(rtcog-1))` therefore released both motors on success; only
   a failed start stranded the survivor (finding AD; PL-22). `if motorCog == 0` also cannot detect
   failure — cog exhaustion returns `$8000_000F`. *(`NEWCOG` was checked for the COGINIT pair-form
   trap and cleared.)* *(Corrected 2026-09-14: this item said the chained assignment "does not
   propagate", so every `start()` returned 0 whether it succeeded or failed. Its evidence,
   `start_return,0,raw_motor_cog,2`, was captured through an abort trap, and every trapped capture
   reads 0 — PL-44. The propagation argument rested on `p2kbSpin2Operators` documenting no
   assignment-as-expression, an argument from absence that the field report's two running motors
   contradict.)*
2. **`getBoardType()` is order-dependent and false-positives.** In one run the same board on
   P16_P31 read Rev B (`pinSum 99`) then Rev A (`pinSum 0`) five milliseconds apart, an empty
   P32_P47 read a confident "64010 Rev B" (`pinSum 104`), and a populated P0_P15 read "not
   detected" (`pinSum 500`). `rSenseForBoard` is 150 vs 5 — **a 30× swing in current scaling**,
   which would silently invalidate T1-5.
3. **C-3 has a mechanism.** The distance-stop check runs in `taskPostionSense()` at 8 Hz, so
   `stopAfterDistance()` is up to 125 ms late before the stop is commanded — ~51 ticks,
   **~294 mm** at top speed. That cog is idle 99.99 % of the time.
4. **`tickInMM_x10` truncates** — 5186/90 = 57, i.e. 5.7 mm/tick against a true 5.763, a
   systematic **−1.1 %** in every distance conversion.
5. **Hall integrity is unmeasured.** The `deltas` table returns 0 for illegal codes *and* for
   skipped transitions, with no counter and no fault. A dead hall faults via lag; an
   intermittently missed one silently under-counts `pos` — the basis of every distance API and
   every published curve.

### Decisions taken 2026-09-11

| Decision | Outcome |
| --- | --- |
| Hall integrity counters | **Build them** — a robustness defect, not a bench fixture. No ask. |
| §2A front end | **Build it** (option A over anchoring on the meter). Order parts first. |
| 360 P/R encoder | **Unavailable** — incompatible with 6.5″ wheels. Hand-rotation ground truth replaces it. |
| DOCO single-motor bench | **Deferred past the next release.** Dual 6.5″ only. |
| Instrument cog shape | **One** cog sampling front end *and* driver status on one timebase. |
| `TASKSPIN` for the instrument | **Rejected** — cooperative; an instrument must not yield. |
| `TASKSPIN` for the shipped sense cog | **DECIDED 2026-09-11 — REJECTED.** The library never conscripts the caller's cog. See *The motor subsystem's cog shape* in the Execution model. Still live *inside* the subsystem boundary. |

### Amendments to the sections above

- **§4 (Tier 1 harness)** — three new requirements before it is written: force `BRD_REV_B`
  rather than trusting auto-detect; read the extended status block (14 → 16 longs) for the
  integrity counters; drive the merged instrument cog. Settle the `TASKSPIN` question first —
  if the sense cog becomes a task, the harness wants writing against that shape.
- **§4 / T1-2 criterion is wrong as written.** It predicts `hallWindowSum == 0`. Because
  `:1539` subtracts real values while `:1541` adds zero, the sum goes **negative** after the
  window wraps (~1 s). Expect zero for one second, then increasingly negative.
- **§3 (Tier 0)** — extended with T0-11 quiescent current-sense baseline, T0-12 hand-rotation
  ground truth, T0-13 counter readback, T0-14 detection repeatability, T0-15 `start()` return
  matrix.
- **§10 (release)** — **ANSWERED 2026-09-11: 6.0.0, not 5.0.3.** A major bump, because the
  behaviour changes are real (`AE` now rejects pin configurations that work today, `DDU_M` stops
  10× further, distance shifts 1.1 %, `rpm` starts returning real numbers) *and* because the
  motor subsystem's cog shape changes before release. See *Version — 6.0.0* in the Execution
  model.
- **Exit criteria** — `tools/build-check.sh` is now **41/41**, not 39/39, and the bench carries
  its own peer config selected by `-D BENCH_CFG`.

### Re-baseline — SUPERSEDED the same day by the silo model

A two-release split (stability / characterization) was proposed here and is
**no longer the plan**. Stephen replaced it with vertical silos built in parallel
and certified in batched passes — see **Execution model — revised 2026-09-11**
below, which is the live ordering. The A/B split was still a *schedule*; the silo
model is not, and it collapses what would have been four bench passes into
roughly one.

What survives from it: **§2 DEBUG channels is not near-term work** (its whole
justification is silencing chatter in silo 5's timed sections), and the ten tasks
created 2026-09-11 carry `stability` / `characterization` tags which remain useful
as a rough silo hint. The tasks themselves are to be **archived and regenerated
from this plan** via `plan-to-tasks` once it is fully scoped — with the plan
absorbing their operational detail *first*, since archiving otherwise discards it.

**One gap this revision closes:** nothing tasked the **S-3 scale fix** itself. The
old plan deferred every driver fix to a later sprint, so `#3490` is the front-end
*build* with no task for the correction it exists to validate. Silo 3 owns it now;
the mechanism and the four-instruction fix are written up in the Execution model.

---

## Sprint Revision — 2026-09-12 (after Bench Pass 1)

**Bench Pass 1 («#3498») is complete.** All six steps ran and every log is valid and curated.
Evaluations: [`CHAR-RUN-EVALUATION.md`](../analyses/bench/2026-09-12/CHAR-RUN-EVALUATION.md)
(step 4) and [`DETECT-A-EVALUATION.md`](../analyses/bench/2026-09-12/DETECT-A-EVALUATION.md)
(steps 5–6 against the Rev B step 3). This section records what the pass changed; the sections
it amends are named below rather than rewritten.

### What Bench Pass 1 established

| Result | Provenance |
|---|---|
| **A negative increment draws 1.76–1.97× the current of a positive one**, both motors, meter and on-board sense agreeing; the motors match each other within 6% at the same sign | MEASURED |
| The negative increment is served by `offset_fwd_` (43°), the positive by `offset_rev_` (317°) — the high-current direction runs on the *characterised* value; 43/−43 assumes the hall pattern's electrical zero is at 0° | DERIVED (`isp_bldc_motor.spin2:2416`, `:2329`) |
| **S-3 confirmed end to end:** sense = 150.1 mV/A × amps + 9.1 mV; implied factor 6138 against the predicted 6136 | MEASURED + DERIVED fit |
| **Board detection:** a real Rev B board reads Rev A after its own cog stops (4 of 4); `pinclear` before the read restores Rev B; on Rev A the defect is invisible | MEASURED |
| The deadtime conditional (A1 / PL-9) is **already deleted** in the tree; `dead_gap` = 70 under both detections | MEASURED |
| On the 6.5″ motor neither offsets nor power limits depend on the detected board, so fixing detection changes only the current scale on this rig | DERIVED (`:1092-1118`, `:1158-1175`) + MEASURED (`maxFwdIncreAtPwr` identical under both) |
| Meter: `Ap`/`Vm`/`Wp` latch; a pack disconnect clears `Ah`/`Wh` with them; `A`/`V`/`W` show on every screen; meter V agrees with a DMM to 0.01 V | MEASURED + STEPHEN |

### Rulings taken 2026-09-12

> **STEPHEN:** *"I don't want to do any more meter transcription that's very costly in time.
> That was 25 minutes just to capture those values, transcribe them, and hand them to you. I
> don't want to do that. We should have enough learning from that."*

> **STEPHEN:** *"fix all you can now, and then the first effort in the bench run, automated
> without my help, is for you to run the scan. Let's try and get the motor load forward and
> reverse near-identical, if at all possible."*

> **STEPHEN:** *"this all looks good let's do it... should be able to do bench if you get it
> ready"* — approving the shape below.

### Consequences — the meter is retired from live use

The meter's work is done: it calibrated the on-board current sense. **From here every current
reading comes from the driver's own sense channel** (after «#3503» and «#3500»), sampled every
control cycle. DERIVED consequences, applied to the tasks in this revision:

- **Deleted:** the printable reading sheet («#3510») — it existed only for transcription.
- **Removed from every harness:** hold-and-announce prompts, the 25-second dwell floor (sized to
  the meter's screen rotation), operator advance by click or key, and the hand-typed
  `manual.csv` input to the analyser.
- **Fault-boundary trials** no longer need one power cycle per trial to clear the meter's peak
  registers; the driver's own sense peak is the reading.
- **§2A front end** validates its current channel against the calibrated on-board sense, not
  against the meter.

### Consequences — Bench Pass 2 becomes an automated session

Pass 2 is split into two tasks with a fix between them:

1. **Bench Pass 2a — the automated offset scan**, loaded, run and evaluated by Claude
   (delegated by STEPHEN above). It begins with a **self-check at today's offsets** that must
   reproduce Pass 1's pattern on the on-board sense; a miss means a foundation fix is wrong and
   the scan aborts. It then sweeps each increment sign's offset **independently**, per motor,
   at ¼ speed with a ½-speed confirmation, and reports each sign's minimum-current offset.
   **The goal is each direction at its own minimum; the load is never equalised by detuning
   the better direction.**
2. **Apply the measured offsets** to `offsetsForMotor()` for the 6.5″ motor — only if both
   motors and both speeds agree.
3. **Bench Pass 2b — certification**, automated: the characterisation regression run
   (sense-based, against the Pass 1 tables), extended Tier 0, and the detection sweep re-run on
   Rev B. **Stephen's hands** are needed only for T0-12's hand rotation and the Rev A board swap.

**Moved out of Bench Pass 3:** T1-10 (the offset sweep) is Pass 2a. T1-11 (both wheels on both
offsets) was largely answered by Pass 1 step 4, which ran each motor alone on both signs.

### New work

- **Independent offset setter** on the motor object — the driver already carries `offset_fwd`
  and `offset_rev` as separate parameter longs; only the test API ties them together.
- **The scan binary** `src/test_bench_scan.spin2` — two-phase: design reviewed before
  implementation. Follows `util_char_motor.spin2`'s drive-measure-fault-reset loop (Stephen's
  proven approach), with stated deltas.
- **Automated characterisation binary** — `test_bench_char.spin2` without panel, prompts or
  meter; PL-19, PL-20, PL-21 fixed; logs `getCurrent()`, rpm, hall counters, detected board,
  applied offsets.

### Amendments to tasks already written

- **«#3502»** — rpm's hardware check moves to Pass 2b's automated characterisation run.
- **«#3503»** — its pre-fix measurement is done (factor 6138). The "pre-fix quiescent baseline"
  its verify line relied on **does not exist** (PL-21); verify against the 150 mV/A fit instead.
- **«#3504»** — do **not** force `BRD_REV_B` (the bench config is on auto-detect, and forcing
  would hide the fix being certified); T0-11 reads a running driver; T0-14 is judged on Rev B;
  T0-12 separable so the automated part runs without Stephen.
- **«#3505»** — becomes Bench Pass 2b.
- **«#3506», «#3508», «#3509», «#3511»** — meter dependence removed as above.
- **«#3515»** — the offset change is user-visible and joins the release-note list.

**Dispatch shape unchanged:** `arbiter-serial`. Two-phase: the scan binary, «#3501», «#3507»,
«#3508», «#3513». The cross-reference table at the end of this plan is regenerated.

---

## Sprint Revision — 2026-09-13 (after scan runs 3–5)

**Bench Pass 2a has run five times.** Evaluations are in `DOCs/analyses/bench/`:
- [`SCAN-ABORT-EVALUATION.md`](../analyses/bench/2026-09-12/SCAN-ABORT-EVALUATION.md) (runs 1–2)
- [`SCAN-RUN-3-EVALUATION.md`](../analyses/bench/2026-09-12/SCAN-RUN-3-EVALUATION.md)
- [`SCAN-RUN-4-EVALUATION.md`](../analyses/bench/2026-09-13/SCAN-RUN-4-EVALUATION.md)
- [`SCAN-RUN-5-EVALUATION.md`](../analyses/bench/2026-09-13/SCAN-RUN-5-EVALUATION.md)

No offsets have been applied. This section records what the runs changed. The live order is
the cross-reference table at the end of this section.

### What the runs established

| Result | Provenance |
|---|---|
| The driver drove the hall inputs low at start, so the first hall read went illegal. **Fixed** («#3524»); `illegal 0` at every start since | MEASURED |
| Both motors put the hall electrical zero near **−3.5°**. Each direction's quarter-speed minimum-current offset agrees across motors within ~2°: negative increment ≈ +14°, positive ≈ −21° | MEASURED + DERIVED fit |
| At those minima the forward/reverse current ratio falls from ~1.9 to ~1.1–1.2. With no load the defaults draw 8–14× the minimum current | DERIVED from MEASURED |
| Each minimum sits **7–10° from a fault edge with no load**; the edge is not sharp, and at half speed the usable window closes in on the minimum | MEASURED |
| Half-speed minima are **not yet resolved**; the scan could not probe toward the fault edge at half speed | MEASURED + DERIVED from source |
| **The driver calibrates its ADCs once per start from a single settling sample**, so every channel's zero is re-drawn at each start (up to 75 mV ≈ 0.5 A). PL-30's "right board offset" was one such value (**PL-32**) | MEASURED + DERIVED from source and `p2kbAppNoteP2an001SinglePinInstrumentationAdc` |
| Run 5's log stopped because **the P2 stopped emitting debug** while it kept running (no reset, no power loss, host logging fine). Cog 0 locked up somewhere after zeroing the motor command; the cause is «#3534» | STEPHEN + MEASURED (last log line) |

### Rulings and observations taken 2026-09-13

> **STEPHEN:** *"processor was running, no power loss... just logging stopped so no furhter
> debug output. you can tell from the log that no P2 reset occurred"*

> **STEPHEN:** *"one thing i'm noticiing is that some speeds? show significant vibration... in a
> couple of days i'd like to characterise the cause so note this as an upcoming study."*

> **STEPHEN:** *"how do we appply what we've just leanred and then get back to our plan and also
> keep moving against the plan, we need to do both from here forward measurements while
> advancing the driver state as required by the plan"*

### The cadence from here: a bench visit is earned by a batch

> **STEPHEN, 2026-09-13:** *"another way to think about bench prep. - a force - we don't go to
> bench until we have delivered a number of fixes, or new capabilites we need to ceritfy. not
> just one each time."*

This sharpens the 2026-09-11 rule (*the unit of cost is a bench pass*):
- **A bench visit is earned by a batch.** We go only once a number of fixes or new capabilities
  have landed that need certifying, never for one or two.
- **Every visit both measures and certifies.** It carries the measurements the plan still needs
  and certifies everything landed since the previous visit.
- **Every visit signs off automatically.** Each feature that landed since the last visit has a
  test that exercises it and emits a PASS / FAIL / NOT_BUILT / NOMEAS verdict. A host script
  collates the verdicts into that visit's sign-off sheet, and a feature with no test is a gap to
  close before the visit. STEPHEN, 2026-09-13: *"this should be done in every bench run too so we
  are maximizing our progress with every run"*. The mechanism is «#3537».
- **Code that needs no hardware keeps landing** in the order below until the batch is complete.
- **A measurement that decides later code** (the offset pair, C-3's overshoot) rides the visit
  whose batch is ready. It does not trigger a visit of its own.
- **Anything that could lose a visit's data is fixed before that visit.** Run 5 stopped emitting
  debug partway through, so «#3534» precedes visit 1.

### The order, as three batches and three bench visits

**Batch 1** — everything that has landed or is certifiable without the motion harness:
1. «#3534» — find and fix scan run 5's lock-up, so a visit cannot silently lose its data.
2. «#3529» — ADC calibration fix (PL-32). **Landed** (`02d29cf`).
3. «#3535» — free driver cog RAM by moving driver *code* into the cog's lookup RAM
   (`$200-$3FF`), keeping every register, constant and table in cog RAM. The driver uses 492 of
   496 longs after «#3529», and every coming driver change needs room.
   - **No execution penalty.** LUT code runs at 2 clocks per instruction, the same as cog RAM
     (`p2kbArchCog`).
   - **`COGINIT` does not load the LUT,** so a loader at the driver's start copies the section in
     with `SETQ2` + `RDLONG`.
   - Stephen asked whether the LUT could help.
4. «#3530» — scan v4: judge on each point's net-of-own-zero, probe the half-speed fault edge,
   fix the pair record.
4b. **Visit 1 sign-off** (task filed 2026-09-13). Every Batch 1 feature gets an automated verdict:
    PASS, FAIL, NOT_BUILT or NOMEAS, emitted by the binary that exercises it. A host script
    collates them into `VISIT-1-SIGNOFF.md`. STEPHEN: *"on the bench run have you added automated
    testing of the new features arriving so we can sign them off as present and working as
    desired?"*
    - The audit found most features only logged, a few with no test at all, and the
      log-to-verdict analyser («#3509») still in Batch 2.
    - Gaps with no test: the watchdog firing (a forced-stall self-test), the calibration's
      cross-start zero spread, recovery from a fault via `testResetFault()` alone, `stop()`'s
      not-running state, the steering start, and a start in SM_BRAKE.
    - Designed now. Implemented after «#3530» and before «#3504» / «#3521» are built, so both
      are built with their verdicts.
5. «#3502» — position math: rpm and mm/tick precision.
6. «#3533» — PL-28 fault recovery and the PL-9 rename. *(2026-09-13: its PL-22 steering
   start-result item is already in the tree, `isp_steering_2wheel.spin2:120-129` and `:152-158`,
   found while reviewing «#3537». The item is dropped from the task; Visit 1 still certifies it.)*
7. «#3504» — Tier 0 extension, T0-11…T0-15. T0-11 restarts the driver repeatedly, which
   certifies «#3529».
8. «#3521» — the automated, meter-free characterisation run with the steering liveness phase.

**Visit 1 — Bench Pass 2a scan run 6 («#3522») and Bench Pass 2b («#3505»), one session,
mostly unattended.**
- *Measures:*
  - the right motor's complete scan legs and both motors' half-speed minima;
  - a hold-for-hold regression against Pass 1 on the default offsets;
  - the first vibration evidence, if «#3532» has been scoped by then.
- *Certifies:* «#3499»–«#3503», «#3524», «#3529» (zeros across the scan's restarts and T0-11),
  «#3530», «#3533», «#3534», «#3535» (every start reaches ready, hall counters 0 and tick rate
  unchanged with driver code running from the LUT), and the steering object's fixed synchronized
  start path, whose mask is built from real cog ids (PL-22). *(Corrected 2026-09-14: this does not
  mean 5.0.2's start could not release its motors; that premise rested on a trapped capture —
  PL-44.)*
- *Stephen's hands:* T0-12 hand rotation and the Rev A detection re-run.
- *Then Stephen's decision:* which offset pair, if any, and with what margin, given fault edges
  7–10° from the minima.

**Visit 1 ran on 2026-09-14** ([`VISIT-1-RESULTS.md`](../analyses/bench/2026-09-14/VISIT-1-RESULTS.md)).
- Eleven of thirteen sign-off rows signed off.
- The start-return and brake-start cells were hidden by a test-capture defect (PL-44).
- Scan run 7: do not apply. The half-speed confirmation is unmeasured (PL-46).
- Run 6 went silent under load. The supply connection was found unsound and repaired. STEPHEN: *"the
  repair is certified as proven by the completed logs after the bench rewireing"* (PL-43, closed).

**Batch 1b** — Visit 1's follow-ups (added 2026-09-14). They are certified at Visit 2, alongside
Batch 2, per the cadence rule.
- **Design rule for every Batch 1b item: correct by construction.**
  - STEPHEN 2026-09-14: *"never see the bench as an esy way out to avoid doing real engineering.
    design for "correct by construction" to reduce side-effects"*.
  - Each design names the invariant its construction guarantees.
  - The bench certifies that invariant; it is never used to characterise a pattern we would not
    choose. So no probe binaries are built for the trap or cog-stop questions.
- **Scope is held to the plan's goal.** STEPHEN 2026-09-14: *"my goal right now is to get our
  driver working per plan - i think adjusting scope keeps us away from that goal longer... punch
  list the need then let's work on what we should be"*. Two follow-ups had grown past what the
  driver path needs, and both are **deferred to the punch list**:
  - **The library's abort and error contract** (PL-47; «#3538», paused).
    - The design is on file, `ABORT-ERROR-CONTRACT-DESIGN.md`.
    - The defects its inventory found are PL-48 and PL-49.
  - **Cog-lifecycle and lock patterns** (PL-41; «#3543», paused).
- **Scan v5** (PL-46): a measurable half-speed confirmation, a half-speed cell that can fail, and a
  top-level trap whose value is always printed. It comes first, because it unblocks the offsets
  («#3523»).
- **The bench harness stops hiding the owed cells** («#3539», PL-44), with no library change:
  - value captures through a trap on a normal return are removed; `start()` already returns the cog
    id or -1;
  - each binary has one top-level trap, and its value is always printed;
  - the checks that masked the owed cells are fixed;
  - the comments carrying the refuted PL-22 premise are corrected.
- **The collation** reads a verdict inside a corrupted log line (PL-40). Done («#3541»).
- **The T0-12 panel** is rebuilt on Stephen's proven display technique, and records turn
  direction (PL-42, PL-39).
- **Visit 2 carries Visit 1's owed items:**
  - R1-T0-START, R1-T0-EXHAUST, R10-CHAR-STEERFAIL and R13-CHAR-BRAKESTART re-measured;
  - T0-12;
  - the Rev A detection re-run;
  - scan v5.
- **Offsets:** «#3523» stays blocked until scan v5 meets the half-speed confirmation and Stephen
  has weighed the margin.

**Batch 2** — the motion capabilities:
- «#3523» — apply the offsets, per that decision.
- ~~«#3506» — the §2A front end (parts first).~~ **Deferred 2026-09-14.** STEPHEN: *"we are not doing
  any external measurement that was a plan left behind for the moment we are not going forward with
  that for now"*. Every current reading comes from the driver's own calibrated sense channel.
- «#3507» — DEBUG channels.
- «#3508» — the motion harness.
- ~~«#3509» — the analyser.~~ **Withdrawn 2026-09-15.** No log-analysis tooling; see *Sprint Revision — 2026-09-15*.
- «#3532»'s instrument, once its scope is set.

**Visit 2 — Bench Pass 3 («#3511»).**
- *Measures:* the speed law in both directions, C-4 deceleration, the fault boundary, C-3
  overshoot, and the vibration study.
- *Certifies:* the applied offsets (the characterisation run repeated on them) and the harness. The
  front end is deferred, so there is no external measurement (STEPHEN 2026-09-14).
- *Also carries:* Visit 1's owed items, including T0-12 on the rebuilt panel. There is no desk run
  before the visit. STEPHEN 2026-09-14: *"no i just want to run the test at the bench"*.

**Batch 3** — the release-shaping changes:
- «#3512» — C-3 stop latency, fixed from visit 2's overshoot.
- «#3513» — the fixed cog shape.

**Visit 3 — release certification.**
- *Measures:* the C-3 rate sweep.
- *Certifies:* «#3512», and «#3513»'s cog shape re-confirming C-3 and the stop behaviour.

**Then:** «#3514» write-back, «#3515» documentation, «#3517» gate binding, «#3516» ship.

**Vibration study «#3532»:** starts about 2026-09-15, when Stephen calls it and sets its scope.
Its first evidence rides the first visit after it is scoped. Its discriminator is the same speeds
on the default and the candidate offsets.

### Section ↔ task cross-reference — regenerated 2026-09-13

This supersedes the 2026-09-12 table at the end of this plan. The table order is the live order.

| order | Task | Batch | Silo | Deliverable | Certified at |
|---|---|---|---|---|---|
| 1 | «#3534» | 1 | — | Find and fix scan run 5's lock-up (P2 stopped emitting debug) | Visit 1 (a run that does not lock up and ends on its own) |
| 2 | «#3529» | 1 | 3 | ADC calibration: settle and average at start (PL-32) — landed `02d29cf` | Visit 1 (zeros across the scan's restarts, T0-11) |
| 2b | «#3535» | 1 | — | Free driver cog RAM: driver code into the cog's lookup RAM ($200-$3FF), data stays in cog RAM | Visit 1 (every start reaches ready, hall counters 0, tick rate unchanged) |
| 3 | «#3530» | 1 | 5 | Scan v4 | Visit 1 |
| 4 | «#3502» | 1 | 2 | Position math — rpm + `tickInMM_x10` | Visit 1 |
| 5 | «#3533» | 1 | 1 | PL-28 / PL-9 (PL-22 start result already in tree, 2026-09-13) | Visit 1 |
| 6 | «#3504» | 1 | 2 | Tier 0 extension, T0-11…T0-15 | Visit 1 |
| 7 | «#3521» | 1 | 3 | Automated characterisation + steering liveness | Visit 1 |
| 8 | «#3522» + «#3505» | — | — | **VISIT 1 — Bench Pass 2a scan run 6 + Bench Pass 2b** (ran 2026-09-14; «#3522» closed; «#3505» closed: T0-12 and the Rev A re-run completed at Visit 2's attended steps, 2026-09-15) | — |
| 8a | «#3540» | 1b | 5 | Scan v5: measurable half-speed confirmation (PL-46) | Visit 2 (scan run 8) |
| 8b | «#3539» | 1b | — | Harness stops hiding the owed cells: no trap captures, one printed top-level trap, masking checks fixed, PL-22 comments corrected (PL-44) | Visit 2 (the re-measured start-return, steer-fail and brake-start cells) |
| 8c | «#3542» | 1b | 2 | T0-12 panel on the proven technique, with turn direction (PL-42, PL-39) | Visit 2 (Stephen's hands) |
| 8d | «#3541» | 1b | 6 | Collation reads verdicts in corrupted lines (PL-40) — done | host selftest + Visit 1 re-collation |
| — | «#3538» | deferred | 1 | Library abort/error contract (PL-47): design on file, implementation deferred to the punch list (STEPHEN 2026-09-14) | — |
| — | «#3543» | deferred | — | Cog-lifecycle and lock patterns (PL-41): deferred to the punch list (STEPHEN 2026-09-14) | — |
| 9 | «#3523» | 2 | 5 | Apply offsets, per Stephen's decision after visit 1 | Visit 2 |
| — | «#3506» | deferred | 6 | §2A front end: deferred, no external measurement for now (STEPHEN 2026-09-14) | — |
| 11 | «#3507» | 2 | 6 | DEBUG channels (PL-8), done in tree | Visit 2 |
| 12 | «#3508» | 2 | 5 | Motion harness | Visit 2 |
| 13 | ~~«#3509»~~ | 2 | 6 | ~~Analyser~~ — withdrawn 2026-09-15 (STEPHEN: no log-analysis tooling) | — |
| 13a | «#3544» | 2 | 5 | Visit 2 prep: attended UI, `dual-ui` walkthrough gate, retired log tooling, run sheet | Visit 2 (`dual-ui`, `t0-hand`) |
| 14 | «#3532» | 2 | — | Vibration study (scope: Stephen, ~2026-09-15) | first visit after scoping |
| 15 | «#3511» | — | — | **VISIT 2 — Bench Pass 3** | — |
| 16 | «#3512» | 3 | 4 | C-3 stop latency, fixed from visit 2's overshoot | Visit 3 (rate sweep) |
| 17 | «#3513» | 3 | 1 | Fixed cog shape | Visit 3 (re-confirms C-3) |
| 18 | — | — | — | **VISIT 3 — release certification** | — |
| 19 | «#3514» | — | — | Write results back into the findings | — |
| 20 | «#3515» | — | — | Documentation blast radius | — |
| 21 | «#3517» | — | — | v12(g) gate binding | — |
| 22 | «#3516» | — | — | **Ship 6.0.0** | three release gates |

**Dispatch:** `arbiter-serial`, unchanged. «#3529», «#3502» and «#3533» all write
`src/isp_bldc_motor.spin2`, and no two tasks share the board.

---

## Sprint Revision — 2026-09-15 (before Visit 2)

Stephen narrowed the work between the bench and the driver fixes. This section amends the 2026-09-13
revision above; that revision's order stays the live order, with the changes below.

> **STEPHEN:** *"Why are you building any tooling to analyze logs? I would think that's extra work we
> don't need. I want to keep our work between here in the bench and then the driver fixes to the absolute
> minimum possible to get the work done. As far as tracking bench results, all we need to do is analyze the
> logs and write an analysis report every time we get a set of logs back. Nothing else."*

> **STEPHEN:** *"Let's minimize work on tooling, maximize work on investigations that are essential to
> building the driver that we're trying to build, and get the repairs in the driver as rapidly as possible
> through this effort."*

> **STEPHEN:** *"I want this next bench run to lead with everything that can run unattended, and then I want
> a very careful working user interface this time that can lead me through the attended."* and *"at the bench
> have a no-motor-control test form of run that takes me thru the series of UI controls to make sure they
> work. If they do work then i run the attended test. if they don't that series doesnt run and we do it next
> bench run."*

> **STEPHEN:** *"I run each test through your single script, and I give it the parameter that says which tests
> we're running. That's what we do. That'll be for attended and unattended tests."* and *"what creates movement
> every time we go to the bench is that we carry something new with us every time. Every time we leave the
> bench, we end up certifying some of those new pieces. This still has to stay in place"*.

### What changed

- **No log-analysis tooling.**
  - «#3509», the analyser, is withdrawn and closed.
  - The sign-off collation (`tools/signoff-collate.py`), its fixtures, the manifest and the detection
    prediction list are deleted.
  - Every set of bench logs gets an analysis report written by reading the logs. The verdict lines the
    bench binaries print stay, and are read there.
- **Every visit still carries new plan mechanisms and certifies them.** Only the machinery around the verdicts
  is gone.
- **Stephen runs every tier** with `tools/bench-run.sh <tier>`, attended and unattended.
- **Visit 2 leads with every unattended load.** The attended loads follow, gated by a no-motor walkthrough of the
  operator panel («#3544»).

### Visit 2 order

The bench card is [`VISIT-2-RUNSHEET.md`](../analyses/bench/VISIT-2-RUNSHEET.md).

| # | Tier | Rig | Hands | Gate |
|---|---|---|---|---|
| 1 | `dual-a` | Rev B, wheels up | none | first, so stop-mode traces precede the other motion loads |
| 2–4 | `dual-clock` 200 / 270 / 300 MHz | Rev B, wheels up | none | — |
| 5 | `dual-b` | Rev B, wheels up | none | — |
| 6 | `dual-c` | Rev B, wheels up | none | — |
| 7 | `t0` | Rev B | none | — |
| 8 | `char` | Rev B, wheels up | none | — |
| 9 | `scan` (run 8) | Rev B, wheels up | none | — |
| 10 | `t0-hand` | Rev B | turns the right wheel by hand | none: it starts no driver cog |
| 11 | `dual-ui` | Rev B | clicks and keys only; nothing moves | PASSED → 12 and 13 run; FAILED → they move to the next visit |
| 12 | `dual-brake` | Rev B, wheels up | one hand-brake | 11 |
| 13 | `dual-floor` | Rev B, wheels down | watches a 2 s drive | 11 |
| 14 | `detect-phase2` | Rev A, motors unplugged | the platform swap | none: no motion, no panel |

The design put the hand-brake load between parts B and C. It moves to the attended block. Part C records its
own float and brake baselines in its own load (`MOTION-HARNESS-DESIGN.md` I7), so nothing it measures depends
on the brake load (DERIVED).

### The attended interface («#3544»)

- **The motion panel:**
  - it names the braked wheel, LEFT (the P32 board);
  - the RELEASE screen counts down the untouched window;
  - a HANDS CLEAR screen is drawn before the harness drives the wheels again.
- **The walkthrough, `dual-ui`:**
  - it never starts a wheel or the steering object;
  - it takes every button once by mouse and once by key, then shows every attended screen for Stephen to
    read, START when it reads right and SKIP when it does not;
  - it prints one verdict line, R14-DUAL-UICHECK-U, and holds the result screen until START.
- **The T0-12 panel:** it names the RIGHT wheel (the P16 board) and shows the 270-transition target. Only S
  starts the count and only SPACE stops it.

### Consequences for the order above

- **«#3509»:** withdrawn 2026-09-15 (row 13).
- **«#3544»:** the Visit 2 prep work. It is certified at Visit 2 by the `dual-ui` and `t0-hand` runs.
- **«#3507»:** was to be certified through two collation host cells, which are retired. Visit 2's analysis
  report reads the DUAL logs for library debug lines instead.
- **The applied offsets:** Visit 2 cannot certify them. «#3523» stays blocked until scan run 8 and Stephen's
  margin decision, so that certification moves to the first visit after «#3523» lands (DERIVED).

---

## 1. Spin2 conformance gate — `tools/check_style.sh`

**Why, and why first.** `.claude/skill-conventions.md` declares `central:spin2-authoring-guide`
at `strength: gate` for `src/**/*.spin2`, with `STYLE_GATE_COMMAND` unset — which records the
gate as **owed, not waived**. This is not a scope choice; it applies to every Spin2 line this
sprint authors, and this sprint authors a lot of it.

**The evidence it is load-bearing** is from 2026-09-10, recorded in PL-2: the TEST-USE ONLY
pass-throughs were first written *without* consulting the guide and matched surrounding legacy
style — no blank `''` separator, no `@param`/`@returns`, no blank line before code. **Nothing
caught it.** `tools/build-check.sh` compiles conformant and non-conformant code identically,
because conformance is not a compile property. It was found only by reading the guide by hand
and reverting.

**It is built first so the harness is the first thing it protects.**

**Starting point.** No instrument exists. The fleet reference is `tools/check_style.sh` in
`P2-uSD-FAT32-FS`. `tools/build-check.sh` and `tools/doc-audit.sh` establish this project's
house style for an instrument: mechanical file discovery, named exclusions printed on every
run, restore-on-interrupt.

**Target behaviour.** A shell script over `src/*.spin2` checking the mechanically checkable
subset of the guide:

| Check | Guide § |
| --- | --- |
| No non-ASCII bytes | 1.1 |
| No `=>` used as comparison | 1.2 |
| Every `PUB` has `''` docs; blank `''` separator; blank line before code | 4.3 |
| `@param` / `@returns` names match the signature; none for absent elements | 4.3 |
| `@local` uses `'` never `''` | 4.3 |
| `PRI` docs use `'` never `''` | 4.4 |
| Block declaration lines (`CON`/`DAT`/`VAR`/`OBJ`/`PUB`/`PRI`) use `'` never `''` | 4.5 |
| `{{ }}` appears only in the file header and licence footer | 4.1 |
| No single-letter locals outside PASM2 | 2.1 |

**Deliberately not checked** (needs judgment, would produce noise): generic container names,
single-exit-point, magic numbers.

**Integration.** `STYLE_GATE_COMMAND: tools/check_style.sh` is set in
`.claude/skill-conventions.md`. Advisory-exit like `doc-audit.sh`? **No** — this one exits
non-zero on failure. It is a gate, and the guide says a FAIL is a defect like any other.

**Verification.**
- *Normal:* a conformant file passes; the two objects from §2 pass after their edits.
- *Edge:* a file with **no** `PUB` methods (`isp_bldc_motor_userconfig.spin2` has one,
  `PUB null()` at `:232`) must not crash or report spuriously.
- *Error:* deliberately break one rule per check in a scratch file and confirm each is caught
  by name — a checker whose failure path has never fired is not known to work.
- **Baseline expectation: the existing tree will FAIL.** It predates the guide.

### 1b. Bring the whole tree to conformance — **scope decision, Stephen 2026-09-10**

> *"we'll close out the work prior to release with the style gate green"*

**This widens §1 from "hold new and modified code" to "the tree is conformant before
`v5.0.3` is tagged."** It is recorded here as a scope decision made at sprint start, not as
a discovery made mid-sprint.

**The size is genuinely unknown until §1 builds the instrument.** No honest estimate exists
before then — 40 files all predating the guide, but the guide's mechanically-checkable subset
may flag a handful of patterns repeated everywhere (one fix shape, many sites) or many
distinct ones. **The first action of this section is to measure, and report the count and its
grouping before any file is edited.**

**Fix by group, not by file** — `baseline-health` §4's rule applies to conformance findings
exactly as it does to test failures. One diagnosis usually clears a cluster: every missing
blank `''` separator is one fix shape; every `''` on a `PRI` is another.

**If the measured count is large enough to threaten the bench sessions, that is a scope
conversation, not something to silently defer or half-do.** The bench work is the sprint's
reason for existing; conformance is a release gate on it. Report the number and let Stephen
decide whether to widen the sprint, split the cleanup out, or delay the tag.

**Hazard this section must respect:** these are edits to files with **no behavioural test
coverage**, made for style reasons. A conformance fix that changes behaviour is the worst
possible outcome of a cosmetic pass.
- Doc-comment, spacing and tag changes are safe by construction — they cannot alter emitted
  code. **Prefer them; do them first.**
- Any finding whose fix would touch an *expression, identifier or control flow* — a renamed
  local, a single-letter variable, a restructured exit path — is **held and listed**, not
  applied in a batch. Each is a code change wearing a style finding's clothes.
- After every group: `tools/build-check.sh` green, 39/39, both release demos certified.

**Verification.** *Normal:* `tools/check_style.sh` exits 0 over all of `src/`. *Edge:* files
with no `PUB` methods, and `hng034rm.spin2` — which cannot compile and is excluded from the
build gate; decide explicitly whether the style gate also excludes it and record the answer
next to PL-1. *Error:* the compile gate stays green after every group, so a cosmetic pass
cannot silently break a release demo.

---

## 2. DEBUG channels, and remove `useDebug` — PL-8

**Why.** The bench suite must silence library chatter during timed sections — T1-1 polls at
2 ms, T1-7 captures a 500 µs ramp — and `isp_bldc_motor.spin2` alone emits 80 `debug()`
statements, `isp_steering_2wheel.spin2` another 39. The bench plan originally said to quiet
them with `useDebug`. **That does not work:** `useDebug` is declared at
`isp_bldc_motor.spin2:294` and set `FALSE` at `:151`, and **nothing ever reads it.** Every
`debug()` in the object is unconditional.

**And a runtime flag is the wrong mechanism anyway.** Even wired up, every `debug()` would
still be compiled in and gated by a runtime test — inside a 500 µs control loop that is not
free, and the records still occupy the binary.

**Mechanism, established by compile experiment 2026-09-10** (not from documentation alone):

- `DEBUG_MASK` is **per-file**. A top-level defining it does *not* reach an included object;
  the object fails with *"DEBUG_MASK symbol must be defined for DEBUG[0..31] usage"*.
- **But it can be sourced from a shared constants object.**
  `DEBUG_MASK = user.MOTOR_DBG_MASK` compiles, and setting that constant to 0 **eliminated
  code** — binary went 9283 → 9270 bytes. Verified by size, not by trusting the doc.
- Plain `debug()` **ignores the mask entirely**, so silencing requires *rewriting* calls, not
  just adding a constant.
- No `{Spin2_v##}` directive is needed; `DEBUG_MASK` is a `CON`, v46+ compilers.

**Target behaviour.**

1. **Delete `useDebug`** — the declaration at `isp_bldc_motor.spin2:294` and the assignment at
   `:151`. It is a false affordance: it reads as a verbosity control and is not one.
2. Add a channel section to `isp_bldc_motor_userconfig.spin2`, **outside the six
   mutually-exclusive config blocks** — verbosity is orthogonal to motor configuration, and
   burying it inside a block would make it change silently when the config is switched:

   ```spin2
   CON ' ---- DEBUG channel masks ----
     ' Per-object DEBUG_MASK values. Channel bits are per file (see the objects).
     ' Set an object's mask to 0 to compile out ALL of its debug output.
     MOTOR_DBG_MASK  = %1111        ' isp_bldc_motor
     STEER_DBG_MASK  = %1111        ' isp_steering_2wheel
   ```
3. Convert the 119 calls in the two objects the bench stack loads, grouped by purpose —
   lifecycle/init, drive commands, sense/telemetry, fault/error. **Fault and error channels
   stay enabled by default**; a silent driver is worse than a chatty one for ordinary users.
4. Each object declares `DEBUG_MASK = user.<ITS>_DBG_MASK` and its own channel constants.

**Explicitly not converted:** the other 37 files, ~639 calls. Option A, chosen 2026-09-10.
The mixed idiom is a real and accepted cost; converting both certified release demos during a
bench-prep sprint is the larger risk.

**Integration.** No top-level changes — verified: because the mask is per-file and each object
supplies its own, all 39 top-levels compile unchanged. `isp_bldc_motor_userconfig.spin2` is a
declared `EXCLUSIVE_RESOURCE`; this edit adds a section and touches no existing block.

**Conformance:** `central:spin2-authoring-guide`, gate — `tools/check_style.sh` from §1 must
pass on both modified objects.

**Verification.**
- *Normal:* default masks — output matches today's for both objects; a demo behaves identically.
- *Edge:* `MOTOR_DBG_MASK = 0` — the object compiles, emits nothing, **and the binary shrinks.**
  Size is the proof; absence of output alone does not distinguish "compiled out" from "not reached".
- *Error:* a channel number outside 0..31 must fail the build with the documented compiler error.
- *Regression:* `tools/build-check.sh` green — 39/39, both release demos certified.
- **Measure headroom:** report actual debug-record count for a bench build against the
  compiler's 255-record ceiling. If it is close, **stop and confirm the measurement** before
  concluding channels are insufficient — record counts and statement counts are not 1:1.

---

## 3. Tier 0 harness — `src/test_bench_t0.spin2`

**Why.** Ten findings are provable with **no motor, no motion, no risk**, in about 30 minutes:
**A1, A2, A3, F, O, G, I/T, K, AE, AD** — plus T0-10's read of the fourth ADC channel. This is
the sprint's highest value-per-hour, and it can run before the Tier 1 harness exists.

**Starting point.** `isp_bldc_motor.spin2:125` — `PUB testSetup()` runs the whole of `init()`
(board detection, constant derivation, power tables, unit conversion) **without starting the
driver cog.** Every derived value can be read back and printed, and nothing can move.

**Target behaviour.** A top-level running T0-1..T0-8 and T0-10 per the bench plan, emitting one
tagged CSV line per data point on the plain debug stream: `#T0-n,field,value,...`.

**Two corrections to the bench plan that this harness must honour:**

- **T0-1's criterion is inverted** from the original writing. At 270 MHz, `dead_gap == 70`
  confirms A1's enum defect **and is the vendor-compliant 260 ns value**. `dead_gap == 14`
  would mean the comparison matched and the board is running ~52 ns, **five times below the
  250 ns minimum both manuals specify.** If 14 is observed: **stop and confirm the
  measurement** — re-read at a second clock frequency before concluding, since a single
  reading of a derived constant is one instrument, not two. If confirmed, do not run Tier 1
  until it is corrected.
- **T0-10 needs no configuration.** `pin_adc_x_i` (base+3) falls inside `adc_pins`
  (`(4 << 6) + 0` = base+0 addpins 4 = five pins), so the driver already runs it as a
  calibrated, frame-locked ADC — it is simply never read.
  **Read it with `RQPIN`, never `RDPIN`** (see §4's hazard).

**Integration.** Built against the single-motor 6.5″ block, **or** the dual block from §4 —
`testSetup()` starts no cog, so it is config-agnostic. Building it into the §4 binary is
preferred (see §4).

**Verification.**
- *Normal:* every T0 test emits its tagged line; `bench-verdict.py` renders a verdict for each.
- *Edge:* T0-7 deliberately constructs two overlapping pin groups — must not fault the harness.
- *Error:* T0-4 and T0-6 deliberately provoke `abort()`. Each must be caught by `\` and
  reported, not unwind the harness. **A harness that dies on the finding it is testing for
  reports nothing.**

---

## 4. Tier 1 harness — `src/test_bench_dual.spin2`

**Why.** Everything that needs the motor turning: **S-9a/C-4, W, C-1, S-3, C-5's gate, Z, C-3,
M, AF, S-4, S-5, AI, AJ**, the user's field discriminator, and **AC**.

**Starting point — this is an extension, not a new file.** `src/test_dual_motor.spin2` already
exists: *"Test framework for testing problem code on a two-wheeled platform"*, Feb 2025, 170
lines, `CLK_FREQ = 270_000_000`. `src/util_char_motor.spin2` already solves the
drive-measure-fault-reset loop that T1-3, T1-7, T1-10 and T1-11 all need — **reuse it, do not
rewrite it.** The TEST-USE ONLY pass-throughs shipped 2026-09-10 in `c22dba1`.

**Config.** The dual 6.5″ / 18.5 V block at `isp_bldc_motor_userconfig.spin2:181`
(`LEFT = PINS_P0_P15`, `RIGHT = PINS_P16_P31`). The block at `:198` is the alternate; both
leave **P50/P51/P52** free for the §2A front end if it is ever built.

**One binary, both tiers.** Tier 0 and Tier 1 live in one program under one config, selected
from a menu. Tier 0 runs entirely through `testSetup()` and starts no driver cog, so the
pin-contention that forced the pass-through design does not apply to it. **This is what makes
Stephen's back-to-back bench session possible without a rebuild** — with one exception, T1-4's
clock sweep, which is inherently three builds and is driven by §5.

**Interaction — `PC_KEY`, verified against P2KB 2026-09-10:**

- Works **only inside a graphical DEBUG display** (a `TERM` window), never a plain `debug()`.
- Must be the **last command** in the `DEBUG()` statement.
- **Needs its own backtick**: `` DEBUG(`BenchTerm `PC_KEY(@key)) ``. Written without it, the
  text is sent as literal characters, no command runs, and the long is never written.
  **It compiles clean and fails silently at runtime** — this is the single most likely way to
  lose a bench evening, and it must be smoke-tested before the session, not during it.
- The display **must have focus**. 100 ms latch — poll faster or keypresses are missed.
  Enter = 13. Spin2 pointer must be hub: `@key`.
- Consequence: the bench runs **headed** (`pnut-term-ts --ide -r`, already the project's
  configured loader), not `--headless`.

> ### HAZARD — `RQPIN`, never `RDPIN`, on any driver-owned pin
>
> `RDPIN` **acknowledges** a smart pin and lowers its `IN`; `RQPIN` ("read quiet") deliberately
> does not, which is why the silicon documentation states it *"can be used by any number of
> cogs, concurrently, to read a pin without bus conflict."*
>
> The driver `rdpin`s `pin_adc_u/v/w_i` and `pin_adc_cur_i` **every control cycle**. A harness
> `rdpin` on any of those races the driver for the acknowledge and **silently corrupts the
> drive loop under test** — with numbers that still look plausible. This applies to T0-10's
> `base+3` read and every phase/current read in Tier 1.

**Two hazards carried from the bench plan §6.**

1. **No `debug()` inside a timed section.** Buffer `(getct(), value)` into hub RAM and dump
   after. Applies to T1-1's 2 ms polling and T1-7's 500 µs capture.
2. **Library chatter** — solved structurally by §2: the bench build sets `MOTOR_DBG_MASK` and
   `STEER_DBG_MASK` to 0 in the user config. No library file is edited per build.

**Hold-and-announce mode** (this is what makes the meter usable — §5, §8): at each ladder rung,
drive it, let it settle, print `#HOLD,<test>,<rung>,<incr>`, then hold **until Enter** with a
**25 s minimum** — MEASURED 2026-09-10: the display cycles **5 screens** (`Ah`, `Wh`, `Ap`,
`Vm`, `Wp`) at **~4 s each, 20 s per rotation**; `A`/`V`/`W` are on every screen (STEPHEN 2026-09-12). This
supersedes the earlier estimate of 8 readings at 2 s (~16 s). 20 s is one rotation exactly, so
arriving mid-screen can need ~24 s to see all five — hence 25 s. The dwell is a floor;
the keypress advances. **T1-7 is trial-selectable** — prompt for a `ramp_inc` trial index, or `0` for
the whole sequence. That single design choice makes the harness indifferent to how the meter's
peak registers reset: button-reset runs `0`; power-cycle-reset runs one trial per invocation,
with the power cycle as the natural boundary. **No persistence, no branch, no code change
either way.**

**Verification.**
- *Normal:* each test emits its tagged records; `#HOLD` prompts appear and Enter advances.
- *Edge:* T1-1 must characterise **all four** stop modes including post-fault. Per the study's
  2026-09-10 revision, the post-fault mode is an **open question with two opposite plausible
  answers** — today's fault sets a `driveoff` flag that commands duty 0 with the smart pins
  still enabled, and whether that floats or shorts the phases must be measured. **The harness
  must not label this outcome in advance.** Emit the coast-down curve; let the analyser compare
  it to the float and brake baselines from the same run.
- *Error:* provoked faults (T1-7) must be recoverable in-session via `testResetFault()` without
  a power cycle. If a fault ever proves unrecoverable, that is itself a finding — record it and
  continue with the remaining tests rather than ending the session.
- **Panic:** `emergencyCutoff()` is **not** the session panic button — per **S-4** it
  self-cancels in ~250 ms. **Physical battery disconnect only.** State this in the harness
  banner at startup.

---

## 5. Runner — `tools/bench-run.sh`

**Why.** T1-4 needs three builds at 200/270/300 MHz, and every run needs its log curated into
evidence rather than left in scratch.

**Starting point.** `tools/build-check.sh` already implements config-block activation and
restore-on-exit-including-interrupt. **Reuse that machinery.** Logs land at
`src/logs/<timestamped>.log` — the `pnut-term-ts` convention, confirmed by Stephen.

**Target behaviour.**
- `bench-run.sh <tier> [clkfreq]` — patch `CLK_FREQ` if given, build, load headed, and on exit
  copy the run's log to `DOCs/analyses/bench/<date>/<tier>[-<clk>].log`.
- **Keep the `.log` extension.** `.gitignore` excludes `*.txt`; a curated log saved as `.txt`
  silently vanishes from git.
- Add `src/logs/` to `.gitignore` — scratch. The curated copies under
  `DOCs/analyses/bench/` are **tracked**, because they are the evidence behind every verdict.
- Restore `CLK_FREQ` on exit, including on interrupt — same discipline as `build-check.sh`.

**Verification.** *Normal:* a tier runs and its log is curated. *Edge:* interrupt mid-run
restores `CLK_FREQ` and the active config block. *Error:* a failed compile aborts before
loading and says which clock and config were active.

---

## 6. Analyser — `tools/bench-verdict.py`

**Why.** *"The session should end with verdicts, not with a pile of CSV to interpret next
week."* **Thresholds are written in before the bench session, not after.**

**Target behaviour.** Consume the curated log plus `manual.csv` (the human-read meter values,
keyed `<test>,<rung>`) and emit one line per test:

```
T0-1   A1    dead_gap=70 expected=70 (260ns, vendor min 250ns)   CONFIRMED-SAFE
T1-4   S-3   ratio 270/200 = 1.349 (exp 1.350)                   CONFIRMED
T1-7   C-5   fault @ duty=duty_max, err rising, Ap=23.4A         GATE VALID
```

**Thresholds carried from the analyses**, each traceable to its finding: T1-4's 1.350 / 1.111
clock ratios; T1-5's expected scale `adc_fram` (6136 @ 270 MHz) from `sense_i_mV = 150 × amps`
(Rev B, 3 mΩ × INA180B2 at 50 V/V, vendor-confirmed); T0-1's `dead_gap == 70`.

> **C-6's rejection criterion must be loosened, or the wiring drop will produce a false
> negative.** The meter reads pack-side; the board sees pack-side minus `I × R_wiring`, which
> **grows along the ladder**. C-6 rejects on "ratio varies with commanded duty" — a
> current-dependent Vbus reference error has exactly that signature. ~20 mΩ at 25 A is 0.5 V,
> **2.7 % at 18.5 V**, comparable to the drift being measured.
>
> **The analyser must not report C-6 WITHDRAWN on a drift smaller than the computable
> wiring-drop bound.** Below that bound it reports **INCONCLUSIVE** and names the missing
> measurement: one DMM reading across the board's own supply terminals at a high rung, which
> yields `R_wiring` and corrects every rung.

**Verification.** *Normal:* a synthetic log produces the expected verdicts. *Edge:* a missing
`manual.csv` degrades to machine-only verdicts and says which tests are unresolvable without
it — it must not crash. *Error:* a malformed or truncated log names the last good record
rather than reporting a false verdict. **A truncated log must never yield a verdict**; per
`p2-dev-cycle` §4, exit code 125 means the log tail is untrustworthy.

---

## 7. The printable reading sheet — `DOCs/analyses/bench/READING-SHEET.md`

**Why.** Stephen reads the meter by hand; the harness cannot. Values must join to the machine
log afterwards, and **if the sheet's rung IDs and the harness's prompt IDs ever disagree the
session is wasted.**

**Target behaviour.** **Generated from the same test table the harness drives** — one source,
two outputs. Not written alongside it. Pre-printed rows carrying `<test>,<rung>` with blank
cells for **V · A · W · Ap · Vm · Wp · Ah**, plus:

- the **quiescent zero** row, taken first: system powered, motors stopped, rail on;
- a **float-the-idle-wheel** reminder on every anchored rung — each board has its own shunt, so
  `sense_i_mV` is per-board while the meter is system-total, and a wheel at `holdAtStop(true)`
  draws real holding current into the reading;
- the **§8.1 meter characterisation** checklist;
- the **panic note**: physical battery disconnect, not `emergencyCutoff()`.

**Verification.** *Normal:* every `#HOLD` the harness can emit has a matching printed row.
*Edge:* regenerating after a test-table change produces a sheet with no orphaned or missing
rows — verify by diffing generated IDs against the harness's emitted IDs, mechanically.

---

## 8. Bench execution

### 8.1 Session one — Tier 0 and meter characterisation, together

Runs as soon as §3 exists; does not wait for §4-§7.

**Safe with the pack connected:** Tier 0 runs entirely through `testSetup()`, which starts no
driver cog, so nothing can move. T0-10 wants the rail on anyway.

While Tier 0 runs, characterise the meter — the answers shape §4's pacing, not its code:

1. ~~Is there a reset control for `Ap`/`Vm`/`Wp`, or does it need a power cycle?~~
   **ANSWERED 2026-09-10 (Stephen): power cycle only, no reset control.** The harness needs no
   change — T1-7's trial-selectable design already absorbs it. Procedure updated in the bench
   plan's T1-7 and §2B.
2. **ANSWERED 2026-09-10 (Stephen) — NO, the P2 does NOT survive a pack disconnect.**
   *Original question retained below for the record; it needs no bench time.* With the pack
   connected **the P2 is powered from the pack**, so a disconnect drops the P2 with it.
   Therefore: every pack power cycle reboots the P2 and restarts the program; **T1-7 is one
   trial per program load** (cycle pack, re-zero, load, select trial index, run to fault, read
   `Ap`/`Vm`/`Wp`); the peaks must be **read before cycling**, since the cycle is what clears
   them; and in §8.1 the Tier 0 run and any power-cycling meter work are **sequential, not
   concurrent** — cycling mid-run loses the run. Changes session length substantially, changes
   no code. The harness's trial-selectable design already absorbs it.
   *(Original: the meter sits between pack and system, so resetting it breaks the pack
   connection. If the P2 Edge were USB-powered from the Mac it would stay alive and trials
   could be prompted in sequence inside one run.)*
3. Do `Ah`/`Wh` reset with the peaks, or separately?
   **Also record the display's ROTATION ORDER and full cycle time** — the sheet's column order
   is generated from it (§7), and it sets the hold dwell.
4. Quiescent zero: with motors stopped and rail on, what are **V**, **A**, **W**?
5. **Does `Ap` latch after the current drops, or decay?** — *If it decays, the
   `Ap`-for-fault-current technique in T1-7 collapses and that measurement returns to needing
   the §2A front end.* Determine this before relying on it.

**Output:** ten findings closed, plus the meter's behaviour.

### 8.2 Session two — Tier 1, then Tier 2

Ordering is not negotiable: **T1-1 first** — it establishes what the hardware does every time
the driver stops, and the rest of the suite stops the motor several hundred times.

Then T1-2, T1-3, T1-4 (three builds via §5), T1-5, T1-6, T1-7, T1-8, T1-9, T1-10, T1-11,
T1-12, and T1-1d. **T1-13's switched read is deliberately deferred** — the shoot-through hazard
means PWMing a live half-bridge with hand-rolled dead time is the one genuinely risky act on
the list, and it needs the ≥250 ns timing scope-verified first. T0-10's passive read stands.

Tier 2 is one 30-second wheels-down observation (**AC**).

**Verification.** Every test emits a verdict, or an explicit INCONCLUSIVE naming what was
missing. **A test that produced no data is recorded as such** — not silently dropped.

---

## 9. Record the results

**Why.** A bench session whose findings are not written back is a session that has to be run
again.

**Deliverables.** For each finding the suite touched: update its entry in the audit or study
with the measured result and the date, following the in-place dated-revision convention those
documents already use (see **A1**, **S-9a**, **C-6b**). Add the **C-4** decel table to
`DRIVE-OBJECTS.md` — it is the deceleration data the public documentation currently lacks.
Sweep closed items from `DOCs/PUNCH-LIST.md` per `punch-list-maintenance`. Curated logs land
under `DOCs/analyses/bench/<date>/` as tracked evidence.

---

## 10. Patch release — 5.0.2 → 5.0.3

**Why a release at all.** No driver behaviour changes. But the tree gains two instruments, a
conformance gate, test scaffolding in two shipped objects, and a substantial documentation set —
and `VERSION` is already one commit behind its tag (`git describe` reads `v5.0.2-1-g2592a7c`).
A patch bump makes the tooling generation identifiable.

**Deliverables.** `VERSION` → `5.0.3`. README *Latest Changes* dated block updated —
`central:changelog-voicing`, reference strength. Tag `v5.0.3` after §8 completes, so the
release includes the bench results rather than only the scaffolding. `build-wrapup` produces
the release notes.

**Verification.** `tools/build-check.sh` green with both release demos certified — that is the
project's release gate and it is non-negotiable. `tools/check_style.sh` green on every file
this sprint modified. `tools/doc-audit.sh` reports no new ORPHAN or COUNT drift.

---

## Documentation Blast Radius

`tools/doc-audit.sh`, run at plan time 2026-09-10. **Verbatim output, not composed from
memory:**

```
 Documentation drift audit
 16 documents | 40 Spin2 sources

-- ORPHAN: documented methods absent from src/ --
    ORPHAN DOCs/PUNCH-LIST.md: debug() exists in no src/*.spin2

-- DUPLICATE: substantial prose maintained in 2+ documents --
    DUPLICATE: Single and Two-motor driver objects P2 Spin2/Pasm2 for our 6.5" Hu...
               CONTRIBUTING.md:3  DRAWINGS.md:3  DRIVE-OBJECTS.md:4
               Movement-STUDY.md:3  README.md:3
    DUPLICATE: The object **isp\_steering_2wheel.spin2** provides the following m...
               DRIVE-OBJECTS-SERIAL.md:46  DRIVE-OBJECTS.md:42
    DUPLICATE: The top-level file `demo_dual_motor_rc.spin2` provided by this pro...
               AUTHORS-Platform.md:63  README.md:231
    DUPLICATE: There are two objects in our motor control system...
               DRIVE-OBJECTS-SERIAL.md:10  DRIVE-OBJECTS.md:10
    DUPLICATE: This steering object makes it easy to make your robot drive forwar...
               DRIVE-OBJECTS-SERIAL.md:18  DRIVE-OBJECTS.md:17
    DUPLICATE: Video of author running the system...
               AUTHORS-Platform.md:10  SERIAL-CONTROL.md:55

-- COUNT: asserted numbers vs. reality --
    (none)
```

**The ORPHAN is an instrument artifact, not a defect.** PL-8's prose names `debug()`, and the
audit reads that as a documented method absent from source. **Doubt the instrument before the
document:** the finding is the checker's heuristic matching a word in running text. Action —
teach `doc-audit.sh` to ignore code-spans in punch-list prose, or accept it as known noise.
Do **not** edit PL-8 to appease the checker.

**The six DUPLICATEs are PL-7 and are not this sprint's scope**, but they are now *visibly*
declined rather than silently carried. The fix, when taken, is **one canonical copy and links
from the others** — never "edit both and keep them aligned", which is the arrangement that
produced them.

**Artifacts this sprint's own changes touch:**

| Artifact | Why it is in scope |
| --- | --- |
| `README.md` — *Latest Changes*, *Known Issues* | §10; the project's changelog. Always in scope |
| `DRIVE-OBJECTS.md` | §9 — the C-4 decel table. **Not** the TEST-USE methods: test scaffolding is deliberately undocumented there, matching how `isp_bldc_motor`'s existing `test*` methods are handled |
| `DOCs/PUNCH-LIST.md` | PL-2 closes (§1); PL-8 closes (§2); §1 opens a new item for the entry conformance-failure count |
| `.claude/skill-conventions.md` | `STYLE_GATE_COMMAND` set (§1). **Local-only** — now gitignored, so this change does not reach other clones |
| `DOCs/analyses/BENCH-TEST-PLAN-2026-09-10.md` | T0-1's inverted criterion, `RQPIN` hazard, hold-and-announce, T1-13 deferral |
| `DOCs/analyses/*` findings | §9 — measured results written back in place, dated |
| `VERSION`, tag `v5.0.3` | §10 |
| `isp_bldc_motor.txt` | **Generated** object-interface report, tracked because it predates the gitignore rule. §2's channel work and the shipped `test*` methods change the motor object's public interface, so it is **stale**. It is produced by the VSCode Spin2 extension, not from the CLI — regenerating it is Stephen's action, or it is left knowingly stale and noted |
| **Docstrings on modified code** | Every `debug()` converted in §2 sits in a method whose docs must still describe current behaviour |

**Counts asserted anywhere:** `tools/build-check.sh` prints "39 files"; §1 and §2 do not change
the file count. If any file is added to `src/`, that string and `DOCs/analyses/` references to
39/40 coverage move together.

---

## Execution model — revised 2026-09-11

**This section supersedes *Sequencing* below.** The original plan ordered work by
**layer**: build every instrument, then run every measurement, then write it all
back. Stephen replaced that on 2026-09-11 with vertical silos built in parallel
and certified in **batched passes**. His words, and the correction that matters:

> *"For every vertical slice, I build the foundational pieces simultaneously, and
> then I certify the vertical piece. I certify as many foundational pieces as I
> have built in one pass. This way you're running a bunch of vertical silos side
> by side, and you're reducing the number of bench runs."*

### The unit of cost is a bench pass, not a task

Code costs nothing but my time. **A bench pass costs Stephen, the hardware, the
pack and a block of his attention.** So the objective is not "finish a silo" — it
is **maximise certified capability per bench pass**. Everything follows from that.

⚠ **A vertical silo is not a schedule.** Four silos executed in sequence is four
bench passes, which is the layered shape wearing different clothes. The silos are
built **concurrently** and certified **together**.

### Dependency is on the FIX landing, not on a prior certification

The current magnitude anchor does not require board detection to be *certified*
first. It requires detection to be **fixed in the same binary** — then one pass
certifies both, and detection's own test in that same run is what licenses the
current reading. Read the foundation results first, then the results that rest
on them.

This is the single reordering insight. It is what collapses four passes into one.

### The silos

Each is *foundation* (code, no bench) plus *certification* (bench). Foundations
are built in parallel; they serialise only because
`src/isp_bldc_motor.spin2` is a declared `EXCLUSIVE_RESOURCE`, which is a
dispatch constraint and not a plan one.

| # | Silo | Foundation | Certified by |
| --- | --- | --- | --- |
| **1** | **Measurement trust** | `start()` return contract (cog id + 1 / 0 → cog id / −1), 6 sites *(corrected 2026-09-14, PL-44)*; board detection | `start()` return matrix; the A/B sweep binary (own artifact — see below) |
| **2** | **Hall / position** | integrity counters **in the driver control loop**; rpm accumulator; `tickInMM_x10` | hand-rotation ground truth; counter readback; `rpm` tracking the raw tick delta |
| **3** | **Current sensing** | the S-3 scale restore (see below) | quiescent baseline; **the magnitude anchor against Stephen's meter** |
| **4** | **Stop latency** | `SENSE_LOOP_HZ` / C-3 | measured overshoot against the ~294 mm prediction, then a rate sweep |
| **5** | **Motion behaviour** | — | speed law, C-4 decel curves, fault boundary, commutation offsets, clock sweep |
| **6** | **Instrumentation** | §2A front end; DEBUG channels; analyser; reading sheet | serves silo 5 |

**Silo 2's "right location" is already settled:** the counters must sit beside the
existing `altgb hall_, #deltas` in the driver control loop. The sense cog runs at
`SENSE_LOOP_HZ = 8` and the motor turns ~411 ticks/s at top speed, so a counter
there would miss essentially every transition.

### Silo 3 — "the right location" for current sensing, and the fix

⭐ **The fix is to restore a shift, not to add a divide — four instructions, and
they belong in the driver loop.**

`isp_bldc_motor.spin2:2435` still carries the original fixed-point form as its
DAT default:

```
numerator       LONG    3300 << 11
```

`init()` at `:276` overwrites it with `3300 * adc_fram`, and the matching
`sar` was never restored. So `scl ≈ 3300`, `(pin − gio)` spans `0..adc_fram`,
and `sense_x_mV` comes out as **millivolts × `adc_fram`** — 6136× at 270 MHz.
That is S-3, and its error factor is exactly `adc_fram`.

Restoring `numerator = 3300 << 11` and adding `sar sense_x_, #11` after each of
the four `muls` puts it back: `scl = 3300·2048/6136 = 1101`, full scale
`6136 × 1101 >> 11 = 3299` — correct, ~0.5 mV per count. A larger shift buys
headroom if wanted.

**Correcting at the source rather than in `getCurrent()` is deliberate.** A
future current limiter (S-2 / C-5) needs the corrected value *inside* the control
loop, so an API-level correction would have to be undone later. The cost is four
instructions against a ~6100-clock iteration.

⚠ This is a reading of the PASM, not a measurement. **The magnitude anchor is
what verifies it**, and that measurement should be taken *before* the fix is
written — see the early characterisation run.

### Two harness requirements that batching forces

**1. `NOT-BUILT` must be distinct from `FAILED`.** "Certify as many as I have
built" means passes are opportunistic: whatever is ready gets run. A test whose
foundation has not landed must report as *not built*, never as a failure —
otherwise a partial pass reads as a regression and the session is spent chasing
it. **Three outcomes, not two.**

**2. Foundation results come first, and dependents are tagged.** If a foundation
fix is wrong, everything certified through it in that pass is void — detection
being wrong makes every current number 30× suspect. The harness emits foundation
results first and names which tests depend on them, so a bad foundation
invalidates a **named set** rather than silently poisoning the log.

### Three bench binaries, not one

The original plan had one Tier 1 harness. Blast radius — no motor may turn on the
Rev A boards — forces a split. *(Corrected 2026-09-12: this read "one-shot hardware".)*

#### (a) The A/B detection sweep — its own binary, detached from every pass

**The A boards are a no-motion resource — repeatable, but no motor may turn on
them.** STEPHEN 2026-09-11: *"A is not one-off just no motor movement"*. They are at
risk because the protection that would make them safe — correct revision detection
feeding correct current scaling, `rSenseForBoard` 5 vs 150 — is the thing that is
broken, so **A-board protection needs the A-board data.** *(Corrected 2026-09-12:
this paragraph called them "one-shot", a DERIVED paraphrase of "this might be the
only sweep we need".)*

**How it runs (Stephen, 2026-09-11):** two systems side by side, identically
wired. Connect to the B boards, run it, capture the log. Disconnect, connect to
the A boards, run the same binary, capture the log. Both logs come back for
comparison.

**Why a separate binary, decisively:** the main harness contains motion tests, and
loading it on the A rig puts a menu between an unprotected board and a spinning
motor. **A binary with no motion code compiled into it at all is the guard**, and
it is a better guard than discipline. It also makes the two logs diffable
line-for-line — no menu, no branch, one fixed sequence — and it can sweep
**all six declared pin groups** rather than assuming a config. *(Corrected
2026-09-12: this cited P32_P47 as an empty group reading Rev B. P32_P47 is the left
board — MEASURED by `test_bench_spin`, 2026-09-11, pin groups corrected in `fe83cb0` —
so that reading was a true positive.)*

⭐ **Measure the discharge in microseconds, not in counts.** `getBoardType()`
charges the cap, floats the pin, and sums 500 `pinread`s. **That sum is
clock-dependent** — the code's own comment says so — because 500 reads take less
wall time at 270 MHz than at whatever clock the `0` / `≤250` / `>250` thresholds
were characterised against. **That alone could be the entire defect.** So the
binary records the sample index and `getct()` at which the pin first reads low —
the real RC discharge time, convertible to µs and clock-independent — alongside
the raw sum, the loop's elapsed ticks, N repeats per group for a distribution,
and the verdict today's code *would* return.

**Two phases, and the second is skippable:**

- **Phase 1 — fully passive.** No driver cog, no PWM. All six groups, N repeats.
  Safe on any board in any state. Its data is written to the log before phase 2
  begins.
- **Phase 2 — the poisoning probe.** Start a driver cog at zero on the populated
  group, stop it, re-read. This is the only thing that separates *"the threshold
  is wrong"* from *"`stop()` clears only the top 8 pins and poisons the next
  read"* — which want opposite fixes. **Run with the motors physically unplugged
  from the A boards**; with no motor connected there is no current path whatever
  the output stage does. The binary states that precondition and waits.

*Note: sweeping all six groups briefly drives `base+4` on each, which for
`PINS_P40_P55` is P44, inside the commented-out LA header range.*

#### (b) The early motor characterisation run — offered by Stephen, accepted

Quarter speed, constant rate, forward and reverse, **before** the current and hall
infrastructure exists. Accepted because **almost nothing it measures is
invalidated by the pending fixes**:

| Fix | Effect on this data |
| --- | --- |
| S-3 restore | divides `sense_i_mV` by a constant |
| board detection | affects `getCurrent()`, **not** raw `sense_i_mV` |
| hall counters | purely additive |
| W / rpm | makes `rpm` work; does not touch `pos` |
| `tickInMM_x10` | distance conversions only; not raw ticks |
| `SENSE_LOOP_HZ` | stop latency only; steady state unaffected |

**A constant scale error hides neither a ratio, an asymmetry, nor a shape.**
Quarter speed helps independently: ~100 ticks/s against a 43.9 kHz loop is one
transition per ~440 iterations, so `pos` is as trustworthy as it will ever be —
which matters because the integrity counters do not exist yet.

**What it buys, most valuable first:**

1. ⭐ **It turns the S-3 prediction into a measurement before we build on it.**
   `adc_fram` = 6136 is *derived from reading the PASM* and has never been
   measured. Known pack voltage + our raw reading + Stephen's meter amps is
   exactly that experiment. Land near 6136 and the fix becomes verification; land
   elsewhere and the whole current-sensing analysis is wrong — **found before the
   fix is written or the front-end parts are bought.**
2. **Forward vs reverse asymmetry (AI/AJ) — the user's actual field fault.** The
   reverse offset is derived (`360 − 43`), never measured, and the field report is
   one wheel in one direction. An asymmetry shows straight through a constant
   scale error.
3. **A go/no-go on the current channel itself.** Nothing has ever confirmed it is
   alive and load-responsive. Dead or stuck ⇒ the S-3 fix is pointless and the
   front-end build is premature.
4. **Left/right hardware equivalence baseline** at matched commanded rate.

**Deliberately not attempted early:** the fault boundary (needs ramp
instrumentation, and it is the one genuinely risky item); anything depending on
stop distance (`SENSE_LOOP_HZ` unfixed); `rpm` or `cntsInSec` (broken); 
`getCurrent()` absolute (depends on two unfixed things); high speed (where missed
hall ticks are most likely and there are no counters to see them).

**Shape:** quiescent zero, then holds per wheel and direction — the hold table in
`src/test_bench_char.spin2` is the authority for which — idle wheel **floating**, never `holdAtStop(true)`, whose holding
current lands straight in the meter reading. Quarter speed is ~37×10⁶ against the
147×10⁶ ceiling at 18.5 V, well inside the linear region. Optionally a second
rung at half speed to confirm current scales with load. **25-second dwell floor**
— the meter cycles five screens at ~4 s each.

⛔ **The condition this run is accepted under: record raw values as raw.** Ratios,
asymmetries and liveness are fair game. Absolute magnitudes are logged with the
scale factor **unresolved** and converted afterward — never asserted during the
session.

**It rides along with the A/B visit** — both rigs are up anyway; this is B-only
and motion-only, so it is a second binary in the same bench session, not a
separate trip.

#### (c) The main harness — silo 5, and smaller than it was

`src/test_bench_dual.spin2` is no longer an 8-hour monolith built before anything
is certified. Board detection leaves it entirely (→ binary *a*), and the early
characterisation leaves it (→ binary *b*). What remains is silo 5: the speed law,
the C-4 decel curves, the fault boundary, commutation offsets and the clock
sweep — built once the instruments it reads have been certified.

### What cannot be batched

Three things are irreducibly multi-load. Group them so the churn lands in one
place rather than scattered through a session:

- **The A/B swap** — physical, and now detached into its own artifact, which
  removes a hardware swap from the middle of a certification pass.
- **The clock sweep (T1-4)** — three builds by construction.
- **T1-7 fault trials** — one trial per program load, since the P2 dies with the
  pack.

### The motor subsystem's cog shape — decided 2026-09-11, executed before release

**Stephen's ruling, which overturns a proposal made earlier the same day:**

> *"I'm going to push back on your suggestion that we push tasking to the caller.
> That's not a shape that I want. What I want is a motor subsystem that is a fixed
> number of cogs, that is highly reliable, and that is the minimum number of cogs
> we can do a motor system in."*

⛔ **The library never conscripts the user's application cog.** A `TASKSPIN`'d
sense task running on the *caller's* cog was proposed in order to hand users back
a cog. **Rejected.** A fixed, known cog cost the user can budget around is worth
more than a cog returned with strings attached — and the proposal would have made
the library dictate the consumer's structure, which a drop-in object must not do.

**The target shape:** two PASM driver cogs as **backend**, plus one **front cog**
that is the API for the entire motor system and the only thing that talks to the
drivers. Three cogs is fine. Two is fine if it can be made to work correctly.

The existing code is already the seed of this and never grew into the role:
`taskPostionSense()` services both wheels, owns the distance and time stop checks,
and is the only Spin2 code reading driver state.

**Timing: this is a final shape change before release, not now.** But near-term
work must not fight it:

- C-3's `SENSE_LOOP_HZ` change lands in the cog that becomes the front cog
- the integrity counters' readback path must be reachable from that cog
- ⭐ **`TASKSPIN` is still live *inside* the subsystem boundary** — if the front
  cog needs both a sense loop and an API service loop, tasks on that one cog do it
  without a fourth cog. Same tool, right side of the line.

### Version — 6.0.0

**Stephen, 2026-09-11:** *"I'm assuming that this is not a 5.0 driver, that this is
a 6.0.0 driver, because it's going to be so much better."*

*(Noted with it: the version question was raised too early. It is a release-time
decision, not a plan-time one.)*

⭐ **A major bump licenses things a patch did not, and that changes the near-term
calculus.** Under 5.0.3 several of the confirmed fixes were breaking changes to be
apologised for; at a major boundary they are expected corrections:

- **AE** now *rejects* pin configurations that are accepted today
- **`DDU_M`** stops 10× further — anyone using it was stopping short
- distance readings shift ~1.1% when `tickInMM_x10` stops truncating
- **`rpm`** starts returning real numbers where callers may have coded around a
  constant 0
- the **cog shape change** above is major-version-appropriate and no longer has to
  be smuggled in

**So the fixes do not need to be contorted to preserve bad behaviour.** Say what
changed, plainly, in the README's *Latest Changes* block — which is this project's
changelog, per `CONFORMANCE_GUIDES`.

`BUILD_VERSION_LOCATION` is `VERSION` (whole file) and git tags match it: bump
`VERSION`, then tag `v6.0.0`.

### Pre-execution research — 2026-09-11, and it moved two findings

#### Board detection: the mechanism is found, and the discriminator is not the defect

**`pinbase+4` is simultaneously the detection pin and `pin_adc_cur_i`.**
`getBoardType()` sets `pSenseCommon := pinbase + 4` (`:777`); the driver declares
`pin_adc_cur_i  res 1  ' basepin + 4` (`:2550`). `BOARD-REVISION-FACTS.md` §2.6
already established this and concluded *"the heuristic is sound"* — and it is. The
**circuit** discriminates correctly. What is broken is the **read**.

The chain:

1. `adc_pins LONG (4 << 6) + 0` (`:2428`) — base+0 **addpins 4**, so five pins,
   base+0 through **base+4**. The driver puts all five into `P_ADC_1X |
   P_COUNT_HIGHS` smart-pin mode.
2. `stop()` (`:125`) does `pinclear(pinbase+8 addpins 7)` — it clears base+8..14
   only. Its comment, *"Bottom 8 pins are sensed, top 8 are driven, so clear only
   the top 8"*, is the error: the sensed pins are **smart pins too**, and nothing
   releases them.
3. So after any driver cog has run and stopped, **base+4 is still a configured ADC
   smart pin.**
4. `getBoardType()` then does `pinhigh` → `waitms(1)` → `pinfloat` → 500×
   `pinread`. **Neither `pinhigh` nor `pinfloat` clears a smart-pin mode** — only
   `pinclear` (`wrpin #0`) does.
5. `pinread` reads the **IN register**, and p2kb (`p2kbSpin2Pinread`) confirms it
   "can read pins configured as smart pins." For an ADC in `COUNT_HIGHS`, **IN is
   the conversion-ready flag**, not the pin's electrical level — which is exactly
   why the driver reads the *value* with `rdpin`.

**So the 500 reads sample a data-ready flag toggling, not an RC discharge.** The
result is a plausible-looking number with no physical meaning.

This explains the 2026-09-11 log precisely: **T0-10 ran a driver cog on P16_P31,
`stop()` left base+4 in ADC mode, and T0-8's detection on that same board five
milliseconds later returned `pinSum 0` → "64010 Rev A"** where T0-10 itself had
read 99 → Rev B.

**The fix follows, and it is small — but do both halves:**

- **`stop()` must release every pin it configured**, not just the driven half.
- **`getBoardType()` must `pinclear(pSenseCommon)` before measuring** — defensive,
  and correct regardless of who else leaves a pin dirty.

⚠ **CORRECTED — the poisoning is only half the defect, and §2.6's "the heuristic
is sound" does not survive contact with the bench.**

The bench is a **dual** 6.5" platform, so there are **two** boards, and
`isp_bldc_motor_userconfig_bench.spin2:48-49` says where — it is explicit and
comments itself *"the bench, as it actually is"*:

```
LEFT_MOTOR_BASE  = PINS_P0_P15
RIGHT_MOTOR_BASE = PINS_P16_P31
```

Against that, the 2026-09-11 log shows detection failing in **three** distinct
ways in one run:

| Group | Populated? | Read | Verdict | Mode |
| --- | --- | --- | --- | --- |
| P16_P31 | **yes** | 99 | Rev B ✓ | correct, cold |
| P16_P31 *(after a cog ran)* | **yes** | 0 | **Rev A ✗** | **poisoned** — the smart-pin leak above |
| P0_P15 | no | 500 | "Board not detected!" ✓ | correct — nothing is wired there *(row corrected 2026-09-12)* |
| P32_P47 | yes — the left board | 104 | Rev B ✓ | correct *(row corrected 2026-09-12)* |

**Only the second row is a defect, and the smart-pin leak explains it.**
*(Corrected 2026-09-12: this section read the bench config's copied
`LEFT_MOTOR_BASE = PINS_P0_P15` as fact and called rows 3 and 4 a false negative and a
false positive. The boards are at P16_P31 and P32_P47 — MEASURED, `test_bench_spin`,
2026-09-11; STEPHEN 2026-09-11: *"right is pin group p16 left is p32"*. The invented
defect is withdrawn in «#3500».)*

**An open question, not an axis this rig can test:** the RC model in the code
assumes a *passive* sense-common node.
On Rev B that node is the **INA180B2 output**, and the rail was on for this run.
A powered INA180 **actively drives** its output, so there is no capacitor
discharge to measure — the pin reads the amplifier's output for the current
flowing, which at rest is near zero and would read *low* immediately. Whether a
Rev B board reads as "Rev B" may therefore depend on **whether its rail is
powered**, which is not something `getBoardType()` knows or checks.

**Removing rail power cannot settle it here** — the P2 is powered from the pack, so
no rail means no P2 (STEPHEN 2026-09-11: *"rail off (no power means no p2)"*). Every
bench log is rail-on. It stays an open question until an experiment that keeps the
P2 alive is designed. *(Corrected 2026-09-12: this proposed a rail-on/rail-off sweep
axis.)*

**Consequence for the sweep binary:** it can now *test the hypothesis directly*
rather than only gather data. Read each group **paired** — once as the code does
it today, once with a `pinclear` first — and **before vs after** a driver cog has
run and stopped. If the paired reads diverge only in the after-cog case, the
mechanism above is confirmed on the bench in one pass.

#### S-3 is verified against three reference implementations, not hypothesised

All three read-only reference drivers in the repo root carry the missing
instruction immediately after each `muls`:

| File | |
| --- | --- |
| `BLDC_Motor_Driver-REF.spin2` | `sar sense_u_,#11` … ×4 |
| `BLDC_Motor_Driver_ChipNew.spin2` | `sar sense_u_, #11` … ×4 |
| `isp_bldc_motor-REF.spin2` | `sar sense_u_,#11` … ×4 |

The shipped driver deleted all four and replaced `numerator = 3300 << 11` with
`3300 * adc_fram`. **The fix is now mechanical** — restore the DAT default and
re-add four `sar` — with three working implementations to copy from. It is no
longer a reading that needs defending.

*The magnitude anchor in binary (b) still runs. It converts a verified-by-source
fix into a verified-by-measurement one, and it is the only thing that can catch a
second, unrelated error in the same path.*

#### `util_char_motor.spin2` gives more than the reuse claim assumed

530 lines, and it already does most of binary (b): `driveForwardAtSpeed()` /
`driveReverseAtSpeed()`, `waitUntilMotorReady()` / `waitUntilMotorDone()`,
`clearFault()`, `testSetFwdRevOffsets()`, and — the useful surprise —
`evalOffset()` already returns **`fwd_mV, rev_mV`**, a per-direction current
measurement. **The AI/AJ forward-vs-reverse asymmetry measurement is therefore
nearly free.**

⚠ **It is single-motor** (`wheel.`), which suits the bench's apparent state — see
the open question on how many boards are actually connected.

### Standing rules

⛔ **All development and all vertical testing happens on the B boards**
(Stephen, 2026-09-11). The A boards are touched exactly once, by binary *a*, with
no motion, and not again until the driver genuinely protects them. This is a
rule, not a preference.

~~⛔ **Force `BRD_REV_B` in every bench build** rather than trusting auto-detect,
until board detection is fixed. Only possible because the A2/A3 fix landed in
`aea4981`; T0-2 in the 2026-09-11 log proves forcing now takes effect.~~
*Retired 2026-09-12:* detection is fixed («#3500»), the bench config is on auto-detect, and Bench
Pass 2 certifies auto-detect, which forcing would hide. Struck on 2026-09-13; it stayed live in
this list for a day after the reversal.

⚠ **`pnut-ts` silently ignores an unknown `-D`** — measured 2026-09-11: exit 0,
binary written, no warning. A typo in `-D BENCH_CFG` falls through to the regular
user config and the harness measures the wrong pin group while producing entirely
plausible numbers. **Confirm the config banner in the run log; no banner voids the
run.**

### Effect on the sections above

| Section | Effect |
| --- | --- |
| §3 Tier 0 | extended — T0-11 quiescent sense baseline, T0-12 hand-rotation ground truth, T0-13 counter readback, T0-14 detection repeatability, T0-15 `start()` return matrix |
| §4 Tier 1 | reduced to silo 5; detection and early characterisation move to their own binaries |
| §5 Runner | unchanged; gains two more binaries to drive |
| §6 Analyser | serves silo 5; must also diff the two A/B logs |
| §7 Reading sheet | serves silo 5 |
| §2 DEBUG channels | moves to silo 6 — its whole justification is silencing chatter in silo 5's timed sections |
| §8.1 / §8.2 | replaced by batched passes; §8.1 is closed («#3476») |
| §10 Release | **5.0.3 → 6.0.0** (Stephen, 2026-09-11). The major bump licenses the breaking fixes and the cog shape change; see *Version* above. |

## Sequencing

> ⛔ **SUPERSEDED 2026-09-11** by *Execution model* above. Preserved as written;
> the layered ordering it describes is no longer the plan.

§1 precedes all Spin2 authoring — it is the instrument that protects §2, §3 and §4.
§2 precedes §4, which depends on masking the library to 0.
§3 can reach the bench (§8.1) before §4-§7 exist, and should.
§5-§7 precede §8.2. §9 follows §8. §10 closes.

## Exit criteria

- `tools/build-check.sh` — every top certified, both release demos certified *(pinned count removed 2026-09-12: a count goes stale as files are added)*
- `tools/check_style.sh` — **green over all of `src/`** (§1b, Stephen's call at sprint start), not merely on files this sprint modified
- `tools/doc-audit.sh` — no new ORPHAN or COUNT drift
- Both bench sessions run; every test carries a verdict or an explicit INCONCLUSIVE naming
  what was missing
- Findings updated in place with measured results
- `VERSION` = ~~5.0.3~~ **6.0.0**, tagged `v6.0.0`, release notes written *(revised 2026-09-11)*
- **Silo foundations certified**, each by a bench pass that emitted foundation results first
  and reported `NOT-BUILT` distinctly from `FAILED`
- **The A/B detection sweep run on both rigs** and its two logs compared

**~~Not in this sprint, and deliberately so:~~ SUPERSEDED 2026-09-11 — the driver fixes are
now in scope.** The sentence below stood while the plan was scaffolding-only.
**Not in this sprint:** every driver fix. **PL-9 stands as a hazard
guard** — A1's apparent one-word fix must not be applied here or anywhere until the fix sprint
takes it with the value change in the same commit.

---

## Section ↔ task cross-reference

> ⛔ **STALE as of 2026-09-11.** This maps the plan's original §-numbered
> deliverables onto the task set generated 2026-09-10. That task set is to be
> **archived and regenerated** from *Execution model — revised 2026-09-11*, which
> is organised by silo rather than by §. Preserved for provenance — do not
> dispatch from it.

Generated by `plan-to-tasks` 2026-09-10. Sprint tag: **`bench-readiness`**. `seq` is the only
ordering signal — `priority` is deliberately unset on every task.

| Plan § | Deliverable | Task | seq | Profile |
| --- | --- | --- | --- | --- |
| §1 | `tools/check_style.sh` — the owed conformance gate | «#3471» | 1 | task-design **(two-phase)** |
| §1b | Bring all of `src/` to conformance | «#3472» | 2 | task-standard |
| §2 | DEBUG channels; delete `useDebug` (PL-8) | «#3473» | 3 | task-design **(two-phase)** |
| §3 | Tier 0 harness `src/test_bench_t0.spin2` | «#3474» | 4 | task-standard |
| §5 | Runner `tools/bench-run.sh` | «#3475» | 5 | task-mechanical |
| §8.1 | **Bench session one** — Tier 0 + meter characterisation | «#3476» | 6 | task-survey |
| §4 | Tier 1 harness `src/test_bench_dual.spin2` | «#3477» | 7 | task-design **(two-phase)** |
| §7 | Printable reading sheet | «#3478» | 8 | task-mechanical |
| §6 | Analyser `tools/bench-verdict.py` | «#3479» | 9 | task-standard |
| §8.2 | **Bench session two** — Tier 1, then Tier 2 | «#3480» | 10 | task-survey |
| §9 | Write bench results back into the findings | «#3481» | 11 | task-standard |
| Doc Blast Radius | The documentation artifact list | «#3482» | 12 | task-standard |
| §10 | Patch release 5.0.3 | «#3483» | 13 | task-mechanical |

### Why this order — the rework and green passes

**Standards before application.** §1 and §1b run first so every later Spin2 task is authored
against a green gate and cannot regress it. A conformance pass run *after* the harnesses would
decertify the tree they were verified on — a verification run certifies the tree it ran
against, and any edit afterwards decertifies it.

**Discovery before utilisation.** §8.1 precedes §6 because one of its answers — whether `Ap`
latches or decays — decides whether the analyser can carry an `Ap`-based fault-current
threshold at all.

**Generated artifacts follow their source.** §7's reading sheet is generated from §4's test
table, so it cannot precede it. §6 parses §4's record format for the same reason.

**Non-hardware work is scheduled early**, so it runs during the waits for bench availability
rather than queuing behind them. §8.1 is placed as early as its two prerequisites allow — the
Tier 0 harness and the runner — rather than at the end with §8.2.

### ATOMIC GREEN-UNIT — «#3471» + «#3472»

**«#3471» leaves `tools/check_style.sh` reporting RED at its own completion.** The tree
predates the guide, and switching a new detection on makes latent instances visible. That is
the instrument working, **not a regression**, and «#3472» repairs it. Both task texts say so
explicitly, because without it an executing agent finishes «#3471», sees red, correctly
concludes it broke something, and then either burns time proving the red was expected or
"fixes" it by weakening the very checks it just wrote.

`tools/build-check.sh` stays green at 39/39 throughout both — the compile gate is never the
thing that goes red here.

### Dispatch shape — `arbiter-serial`, matching the project default

Both inputs point the same way:

- **Exclusive resources.** `EXCLUSIVE_RESOURCES` names
  `src/isp_bldc_motor_userconfig.spin2`, `src/isp_bldc_motor.spin2` and the single P2 board on
  USB. §2 touches the first two; §1b touches every file; §8.1 and §8.2 need the board. The
  board is a **physical device** — the one grade of exclusivity no design can remove.
- **Coupling.** §4's record format is the shape §6 and §7 are both generated against. A
  coupled set is not fanned out; it is cured by two-phase dispatch, not by staging.

**Three tasks are two-phase** — first dispatch returns the design only, the arbiter reviews,
a second agent implements the approved design:

| Task | What later work inherits from its shape |
| --- | --- |
| «#3471» | The check set determines «#3472»'s entire size |
| «#3473» | The channel scheme is inherited by the Tier 1 harness and every future conversion |
| «#3477» | The tagged record format is what «#3478» and «#3479» are generated against |

Reviewing a design costs one round trip. Reviewing four hours of implementation built on the
wrong one costs four hours plus every task that already built on it.

---

## Silo ↔ task cross-reference — generated 2026-09-11

Generated by `plan-to-tasks` from *Execution model — revised 2026-09-11*. Sprint
tag **`bench-readiness`**. `seq` is the only ordering signal; `priority` is
deliberately unset on every task. This table supersedes the §-numbered one above.

| seq | Task | Silo | Deliverable | Profile | est |
| --- | --- | --- | --- | --- | --- |
| 1 | «#3496» | 1 | A/B detection sweep binary | task-design **(two-phase)** | 3h |
| 2 | «#3497» | 3 | Early motor characterisation binary | task-standard | 2h30 |
| 3 | «#3498» | — | **BENCH PASS 1** — both pre-fix binaries | task-survey | 2h |
| 4 | «#3499» | 1 | `start()` return contract (cog id + 1 / 0 → cog id / −1), 6 sites *(corrected 2026-09-14: read "returns 0", a trapped capture — PL-44)* | task-standard | 1h30 |
| 5 | «#3500» | 1 | Board detection — the smart-pin leak | task-design | 3h |
| 6 | «#3501» | 2 | Hall integrity counters, ABI 14→16 | task-design **(two-phase)** | 2h30 |
| 7 | «#3502» | 2 | Position math — rpm + `tickInMM_x10` | task-standard | 1h30 |
| 8 | «#3503» | 3 | S-3 scale restore — four `sar` | task-mechanical | 1h |
| 9 | «#3504» | 2 | Tier 0 extension, T0-11…T0-15 | task-standard | 2h30 |
| 10 | «#3505» | — | **BENCH PASS 2** — certify the foundations | task-survey | 1h30 |
| 11 | «#3506» | 6 | §2A front end build | task-mechanical | 3h |
| 12 | «#3507» | 6 | DEBUG channels (closes PL-8) | task-design **(two-phase)** | 3h |
| 13 | «#3508» | 5 | Motion harness `test_bench_dual.spin2` | task-design **(two-phase)** | 7h |
| 14 | «#3509» | 6 | Analyser `bench-verdict.py` + A/B diff | task-standard | 3h30 |
| 15 | «#3510» | 6 | Printable reading sheet | task-mechanical | 1h30 |
| 16 | «#3511» | — | **BENCH PASS 3** — motion behaviour | task-survey | 3h |
| 17 | «#3512» | 4 | C-3 stop latency — measure then raise | task-standard | 2h |
| 18 | «#3513» | 1 | **Fixed cog shape** — final pre-release change | task-design **(two-phase)** | 5h |
| 19 | «#3514» | — | Write results back into the findings | task-standard | 3h |
| 20 | «#3515» | — | Documentation blast radius | task-standard | 3h |
| 21 | «#3516» | — | **Ship 6.0.0** | task-mechanical | 1h30 |
| 22 | «#3517» | — | v12(g) gate binding *(skills adoption)* | task-design | 4h |

**Total ≈ 60 h of effort.** Three bench passes, each requiring Stephen.

*Superseded by the regenerated table below (2026-09-12).*

## Silo ↔ task cross-reference — regenerated 2026-09-12

> ⛔ **SUPERSEDED 2026-09-13** by the table in *Sprint Revision — 2026-09-13*. That table is the
> live order. This one is preserved for provenance.

Regenerated by `plan-to-tasks` §6 from *Sprint Revision — 2026-09-12*. Bench Pass 1 done;
the reading sheet («#3510») deleted; Bench Pass 2 split into an automated scan (2a) and an
automated certification (2b), with the offset fix between them. `seq` is the only ordering
signal.

| seq | Task | Silo | Deliverable | Profile | est |
| --- | --- | --- | --- | --- | --- |
| 1 | «#3496» | 1 | A/B detection sweep binary — **done** | task-design (two-phase) | 3h |
| 2 | «#3497» | 3 | Early characterisation binary — **done** | task-standard | 2h30 |
| 3 | «#3498» | — | **BENCH PASS 1** — **done** | task-survey | 2h |
| 4 | «#3499» | 1 | `start()` return — 6 sites | task-standard | 1h30 |
| 5 | «#3500» | 1 | Board detection — the smart-pin leak, fix measured | task-design | 3h |
| 6 | «#3501» | 2 | Hall integrity counters, ABI 14→16 | task-design (two-phase) | 2h30 |
| 7 | «#3503» | 3 | S-3 scale restore — four `sar` | task-mechanical | 1h |
| 8 | «#3502» | 2 | Position math — rpm + `tickInMM_x10` | task-standard | 1h30 |
| 9 | «#3519» | 5 | Independent fwd/rev offset setter | task-mechanical | 45m |
| 10 | «#3520» | 5 | Automated offset scan `test_bench_scan.spin2` | task-design (two-phase) | 5h |
| 11 | «#3504» | 2 | Tier 0 extension, T0-11…T0-15 | task-standard | 2h30 |
| 12 | «#3521» | 3 | `test_bench_char` automated, meter-free | task-standard | 2h30 |
| 13 | «#3522» | — | **BENCH PASS 2a** — automated offset scan | inline run + task-survey | 1h30 |
| 14 | «#3523» | 5 | Apply the measured offsets (if 2a says apply) | task-mechanical | 30m |
| 15 | «#3505» | — | **BENCH PASS 2b** — automated certification | inline runs + task-survey | 1h30 |
| 16 | «#3506» | 6 | §2A front end build | task-mechanical | 3h |
| 17 | «#3507» | 6 | DEBUG channels (closes PL-8) | task-design (two-phase) | 3h |
| 18 | «#3508» | 5 | Motion harness `test_bench_dual.spin2` | task-design (two-phase) | 7h |
| 19 | «#3509» | 6 | Analyser `bench-verdict.py` + detection/scan diffs | task-standard | 3h30 |
| 20 | «#3511» | — | **BENCH PASS 3** — motion behaviour | task-survey | 3h |
| 21 | «#3512» | 4 | C-3 stop latency — measure then raise | task-standard | 2h |
| 22 | «#3513» | 1 | Fixed cog shape — final pre-release change | task-design (two-phase) | 5h |
| 23 | «#3514» | — | Write results back into the findings | task-standard | 3h |
| 24 | «#3515» | — | Documentation blast radius | task-standard | 3h |
| 25 | «#3516» | — | **Ship 6.0.0** | task-mechanical | 1h30 |
| 26 | «#3517» | — | v12(g) gate binding *(skills adoption)* | task-design | 4h |

**Rework check (§3a), DERIVED:** the offset setter precedes both binaries that call it; S-3,
detection and the counters precede the scan, whose self-check depends on all three; the scan
precedes the apply task, which precedes 2b, so the certification runs on the final constants;
the Tier 0 extension precedes 2b. **Green-ordering (§3b):** no pair is expected to leave the
gates red. **Dispatch:** `arbiter-serial`, unchanged — `src/isp_bldc_motor.spin2` is touched by
«#3499»–«#3503», «#3519» and «#3523».

### Dispatch shape — `arbiter-serial`, unchanged

Confirmed against `{{EXCLUSIVE_RESOURCES}}` rather than inherited. Two entries
force it and neither can be designed away for this sprint:

- **The P2 board on USB** — a physical device, the top grade. One device, one
  agent, never negotiable.
- **`src/isp_bldc_motor.spin2`** — nominally a single-file artifact (the grade
  that *can* often be staged per agent and merged), but it is 2 400 lines of
  interleaved Spin2 API, PASM2 driver and sense task, and **six of the twenty-two
  tasks write to it**. Staging and merging that file is more risk than the
  concurrency buys.

`src/isp_bldc_motor_userconfig.spin2` adds a third: one config block is active at
a time and every compile depends on which.

**Coupling independently forbids fan-out** at the head of the set: the hall
counters change the status-block ABI that the Tier 0 extension reads, and the
harness record format is what the analyser and reading sheet are generated from.

**Five tasks are two-phase** — «#3496», «#3501», «#3507», «#3508», «#3513» —
design returned and reviewed before implementation. Each is one whose *shape*
later work inherits: an A/B-comparable hardware record format, the most fragile ABI in
the codebase, a channel numbering scheme, a record format with two generated
consumers, and an architecture every caller inherits.

### RESOLVED 2026-09-11 — the cog shape change is gated, and the decertification is accepted

**«#3513» (the fixed cog shape) decertifies «#3511» (bench pass 3).** A
verification run certifies the tree it ran against, and §3a-ii's rule is that any
edit afterwards decertifies it — so an architecture change scheduled *after* the
motion pass invalidates what that pass proved.

It is placed late anyway because **Stephen scoped it that way**: *"That's going to
be a final shape change before release."* The exposure is bounded and worth
stating precisely rather than pretending it is zero:

- **Safe** — the C-4 deceleration curves, the speed law, the fault boundary and
  the commutation offsets are **driver-cog** behaviour, and the two PASM driver
  cogs are unchanged by «#3513».
- **Not safe** — anything touching the Spin2-side coordination: the distance and
  time stop checks, telemetry cadence, and therefore **C-3's measured overshoot**,
  which «#3512» produces from the very loop «#3513» restructures.

So «#3513» must re-confirm C-3 and the stop behaviour, and «#3516»'s three
release gates are the re-certification of everything else.

**The trade was put to Stephen and he took the decertification.** In his words,
2026-09-11:

> *"No, I don't want to do this yet. We'll decertify and recertify later. I want
> to stay with the existing cog shape because I want to get to the bench with all
> the fixes we can as soon as possible. Changing cog shapes means we have to
> certify that the new cog shape is working, and that's going to be a distractor.
> No cog shape change before we get our first bench results. Let's not take on
> more work that can perturb our ability to get to the bench and get good
> findings."*

⛔ **So «#3513» stays at seq 18 and does not start before «#3498» has produced
results.** Do not propose pulling it earlier to tidy the decertification problem
— that is the exact trade he declined.

*DERIVED — my generalisation of that ruling, not his words (labelled 2026-09-12):*
nothing that changes **what the first bench results measure** is taken on before
them. Tooling that does not change what gets measured is outside it (doctrine
overlay P2).


---

## Sprint Revision -- 2026-09-16: the 6.0.0 driver work

**Why this revision exists.** Visit 3 certified every repair this plan carried
(`DOCs/analyses/bench/2026-09-16/VISIT-3-RESULTS.md` §0). Stephen then set the scope and the rules for the rest
of the sprint. Every question they raised is answered. His words, 2026-09-16:

- **The sprint structure:** *"we are characterizing 6.5" motor and dirver shape and correcting it. we also have
  a potential vibration study and we have a doco characterization effort. This wis why i was thinking we have
  multiple sprints"*.
  - **This sprint ships 6.0.0:** the 6.5″ driving shape made correct.
  - **After it:** motor characterisation of both motors, as its own sprint (STEPHEN 2026-09-15: *"might be better
    done as its own independent sprint plan for both motors"*).
  - **Also after it:** the vibration study, when the piezo hardware arrives; the Doco effort.
- **Scope is his:** *"please do not decide what's in this sprint or latest sprint that's always my decision"*.
- **The API rule:** *"The API is the contract with the user. I want the API to make as much sense as possible,
  and so the actions requested through the API should be what we'd expect the actions to do in a clean way. If
  you find that we're not meeting the contract of the API with any of these API members, we need to fix it."*
- **PL-48:** *"yes, fix it now"*.
- **The error contract:** *"We can actually change the contract to say an error code is returned. The success
  and error code is returned, and that will not affect any users today until they decide to use it."* For
  getters and for conditions found after a call returns: *"yes, option 1"*, a documented neutral value plus a
  read-and-clear `getError()`.
- **Current limiting:** *"yes A - i want intelligent behavior to limit current vs. aborting where this is the
  right thing to do for the dirving system"*. That is S-2, C-5, the PL-55 stop and the protective stop, as one
  design.
- **The protective stop:** *"yes your A"*. Drive calls refuse and return the code while latched, nothing
  aborts, and the names are `clearProtectiveStop()`, `getProtectiveStop()` and `ERR_PLATFORM_BLOCKED`.
- **The fixed cog shape («#3513»):** *"I would like A"*, then, for its N-motor part, *"yes, after 6.0.0"*.
  - **In this sprint:** the front cog for today's two forms.
  - **After 6.0.0, with the Doco effort:** the roster owner, `demo_n_motor`, the `nmotor` config blocks and the
    gate classifier.
- **Time stops:** *"stopped by T"*.
- **The attended pair:** dropped from Visit 3 (*"yes, your recommendation"*).

**Open questions: none.**

**Governing designs, each carrying a dated amendment block of these rulings:**
- `DOCs/plans/ABORT-ERROR-CONTRACT-DESIGN.md`;
- `DOCs/plans/FIXED-COG-SHAPE-DESIGN.md`.

### R16.1 · The error contract in the motor object (PL-47, PL-48, PL-49)

- **Commands** return a status: 0, or a negative `ERR_*`.
- **`start()`/`startEx()`/`startSenseCog()`** keep cog id 0–7 or −1, with the cause in `getError()`.
- **Getters that cannot measure** return a documented neutral value and record the code.
- **`getError()`** reads and clears the calling cog's first error.
- **Validate, acquire, commit** in `startEx()`. This removes PL-48, F-2, F-3, F-8 and F-9.
- **One power-table lookup.**
- **Stop limits** validate, then commit (F-4, F-5a/b).
- **`SyncStatus()`** is bounded (F-6).
- **No `abort` anywhere.** The protective-stop code range is reserved; its API lands in R16.6.

### R16.2 · The error contract in the steering and serial objects, and the demos

- **Steering:** three-result `getError()`, F-5c, F-13.
- **Serial:** call first, then reply with the error name (F-7), and counts must be at least 1.
- **Demos:** the five release and HDMI demos adopt the contract.

### R16.3 · The front cog (fixed cog shape, today's two forms)

`FIXED-COG-SHAPE-DESIGN.md` §2–§3 and §5, as amended:

- **One owner.** The sense cog becomes the front cog, the only writer of each driver's command, e-stop, stop
  limits and tracking. Public methods post a request per calling cog, wait bounded, and return its status.
- **A 1 ms loop:**
  - stops are commanded within one pass;
  - the rpm window is kept;
  - late passes are counted.
- **Synchronized drive** over the owned motors is issued from the front cog. The lockstep start is unchanged,
  and the right wheel's `forwardIsReverse()` is kept.
- **Cooperative shutdown** (PL-41's pattern).
- **Fixed cog cost:** a single motor is 2 cogs, with the front cog always started by `start()`, so
  `startSenseCog()` is no longer needed; two wheels are 3 cogs.
- **Built to take a roster later without rework.** No roster owner, N-motor API, `demo_n_motor`, config block or
  gate change in this sprint.
- **Two-phase:** it returns the implementation plan for review, reconciling the design with R16.1's status
  returns and R16.4's e-stop latch, before the code.

### R16.4 · API members that break their contract

Each is a fix with one correct remedy under the API rule. Front-cog items are built in the front cog.

- **PL-52:** `getPower()` reads 0 after every stop path.
- **PL-66:** a command after a fault restarts the motor, even at the same power. This is the PASM request
  comparison.
- **The e-stop latches until `clearEmergency()`.** The auto-clear is deleted, and study finding S-4 is retired.
  A drive refused while e-stopped returns a status.
- **PL-51:** the steering object's `getMaxSpeedForDistance()`.
- **PL-45:** `getCurrent()` subtracts the rest zero.
- **PL-25:** a board not detected gives 0 and records the code.
- **PL-38:** the 6.0 V and 7.4 V ceilings err low.
- **PL-13:** the serial objects' method names are aligned.
- **PL-58:** the stop and hold docs.
- **Closed, not a defect:** PL-18. The motor type is the compile-time `user.MOTOR_TYPE`, so two instances cannot
  differ, and the hazard is unreachable through the API.

### R16.5 · Current limiting and stopping from speed: the design (two-phase)

**One design** covers:
- S-2, a current fold-back in the driver loop;
- C-5, a lag-limited ramp;
- the PL-55 stop;
- the protective stop.

The governing direction is STEPHEN's *"intelligent behavior to limit current vs. aborting"*.

**MEASURED:**
- `stopMotor()` decelerates at 242–256 ticks/s² from every speed, and current rises 20–50 % above running
  current during the stop.
- Every stop from 75 % trips 10 A on all four combinations (Visit 2 §3–§4; Visit 3 §2.1).
- The provoked faults arrive with duty not saturated (Visit 2 §6). The study's C-5 trigger, which requires
  saturated duty, would miss them, so it must be redesigned.
- The sense scale is certified (S-3, Visits 1–3).

**Phase 1:**
- Reads the traces on disk and names the stop-current mechanism.
- Designs the fold-back limit and its bound.
- Designs C-5's trigger from the measured fault signature.
- Designs the blocked-platform detector in the front cog, with its criterion and persistence.
- Settles whether the sense channel sees regenerative current, from the board facts and the traces. A residual
  that depends on the rig goes to Stephen as a confirm question (overlay P8).
- States the Visit 4 cells. No bench run.

### R16.6 · Current limiting and stopping from speed: the change

- Implements the approved R16.5 design in the PASM driver, with any params-block change and its count
  constant together.
- Adds the protective-stop detector and API in both objects: `clearProtectiveStop()`, `getProtectiveStop()`,
  `ERR_PLATFORM_BLOCKED`, and refuse-and-return while latched.

### R16.7 · Distance, rotation and time stops at rest at their limit

- **API rule and *"stopped by T"*:** the front cog begins the stop early, by the ramp's stopping distance or
  time, computed from the running increment and the ramp as the driver applies it.
- **After R16.6**, because the ramp may change.

### R16.8 · Visit 4 harness and run sheet

- **Every change in R16.1–R16.7 arrives with a cell** that prints its verdict, with its unfixed value stated
  (overlay P1).
- **Front cog cells** (`FIXED-COG-SHAPE-DESIGN.md` §6, today's two forms):
  - the fixed cog count;
  - lockstep;
  - stop latency;
  - no hang while e-stopped;
  - an ordered stop during a drive;
  - cooperative shutdown;
  - tracking reset.
- **Current-limit cells:**
  - a stop from 75 % without the 10 A abort;
  - the fold-back holding current under its bound;
  - the lag limiter turning a provoked overload into droop instead of a fault;
  - the protective stop latching, refusing and releasing, where the rig can provoke it with wheels lifted.
- **Also covers** what Visit 3 left unqualified:
  - the steering `getDistance()` and metre path;
  - DS_ESTOP and `isEmergency()`;
  - the PL-36 pin-claim release.
- **Runner:** tier names only. Correct the S-4 panic-line text.

### R16.9 · Visit 4: run, and the analysis report

Stephen runs the sheet. The logs are read and the report written.

### Documentation Blast Radius

Owned by «#3515», whose artifact list gains:
- **`DRIVE-OBJECTS.md`:**
  - the "Errors" section and every changed signature;
  - the protective-stop methods and codes;
  - current limiting;
  - the fixed cog cost for both forms;
  - `startSenseCog()` no longer needed.
- **`DRIVE-OBJECTS-SERIAL.md` / `SERIAL-CONTROL.md`:** error replies.
- **`DEVELOP.md`:** the cog cost, and the single-motor example without `startSenseCog()`.
- **README Latest Changes:**
  - the e-stop latch;
  - `getPower()` after a stop;
  - a retry after a fault;
  - stops at rest at their limit;
  - current limiting, with stops from speed staying under a bound and overloads drooping instead of faulting;
  - the protective stop;
  - the fixed cog count;
  - the lower 6.0 V / 7.4 V placeholders;
  - PL-48.
- **Repo-root reference docs for the hardware** (STEPHEN 2026-09-16: *"we need detail docs at the repo root we have
  one for motors, needs updating. we need somthing for the boards too which are just facts for each some of which
  you just captured. This is not to facilitate choice but to inform a user about the boards they have and when to
  be careful with each"*):
  - **A new board document, `DRIVER_BOARDS.md`,** at the repo root, one section per revision (Rev A, Rev B). It holds the facts a user
    needs about the board they have:
    - how to tell which revision they have, and what `getBoardType()` reports
    - gate supply (10 V / 12 V)
    - gate driver
    - MOSFET and its ratings
    - current-sense scale and resolution
    - the deadtime requirement
    - what the driver protects against, and what it does not
    - **when to be careful with each board:**
      - Rev A's damage history with large hub motors and its lack of the Rev B driver's negative-spike
        protection
      - Rev A's coarse 5 mV/A current sense
      - regeneration not visible to the current sense

    Source: `DOCs/analyses/BOARD-REVISION-FACTS.md`, distilled for users; no analysis history and no
    recommendation to buy one board over the other. Linked from README and from the doc table in `CLAUDE.md`
    (raised with Stephen, his file).
  - **The existing motor document, `MOTOR_CHOICE.md`, brought current**, alongside item (e) of «#3515»: the speed model at the real
    drive-pass rate, the placeholders, and the current limits the motors now run under.
- **The three "two objects / two cogs" copies** (README, `DRIVE-OBJECTS.md`, `DRIVE-OBJECTS-SERIAL.md`), and
  `images/objects-cogs.png`. The image is generated and is Stephen's to regenerate.
- **`CLAUDE.md`:** its stale ABI and deadtime paragraphs. Stephen's file: raised with him, not edited.

**Withdrawn:**
- the scan-measured offsets (STEPHEN 2026-09-15);
- anything describing the N-motor shape (after 6.0.0).

### Dispatch and ordering

- **Dispatch:** `arbiter-serial`. Every code task touches `src/isp_bldc_motor.spin2`, an exclusive resource.
- **Two-phase:** R16.3 (front cog) and R16.5 (current-limit design).
- **Order:**
  1. The error contract, R16.1–R16.2, which restructures the start, stop-limit and command paths.
  2. The front cog, R16.3, which owns every sense-task write that follows.
  3. The contract fixes, R16.4.
  4. The current-limit design, then the change, R16.5–R16.6.
  5. Stops at their limit, R16.7.
  6. The harness, then the visit, R16.8–R16.9.

### Cross-reference (2026-09-16)

| Plan § | Deliverable | Task | Order |
|---|---|---|---|
| R16.1 | Error contract, motor object (PL-47, PL-48, PL-49) | «#3554» | 1 |
| R16.2 | Error contract, steering, serial, demos | «#3555» | 2 |
| R16.3 | Front cog, today's two forms (two-phase) | «#3513» | 3 |
| R16.4 | API members keep their contract | «#3556» | 4 |
| R16.5 | Current-limit and stop design (two-phase) | «#3557» | 5 |
| R16.6 | Current-limit and stop change, protective stop | «#3558» | 6 |
| R16.7 | Stops at rest at their limit | «#3559» | 7 |
| R16.8 | Visit 4 cells and run sheet | «#3560» | 8 |
| R16.9 | Visit 4 run and report | «#3561» | 9 |
| — | Write-back to the findings documents | «#3514» | 10 |
| Blast radius | Documentation | «#3515» | 11 |
| — | Ship 6.0.0 | «#3516» | 12 |

- **Superseded:** «#3538»; its design is carried by «#3554»/«#3555».
- **After 6.0.0 (STEPHEN):**
  - the N-motor shape, «#3562», with the Doco effort;
  - motor characterisation of both motors (its own sprint; «#3523» is its offsets task);
  - the vibration study «#3532», when the hardware arrives.
- **Closed, not a defect:** PL-18.

---

## Sprint Revision — 2026-09-17 (night): not shippable, and the release widened

**Why.** Visit 5 ran clean (0 FAIL, 0 NOT_BUILT across 66 cell instances), and STEPHEN ruled: *"v6.0.0 is not
shippable as is. we need better behavior"*. A findings audit followed
([`../analyses/FINDINGS-AUDIT-2026-09-17.md`](../analyses/FINDINGS-AUDIT-2026-09-17.md)); its §7 carries every
ruling below verbatim.

**Rulings (STEPHEN, 2026-09-17), which override this plan's earlier text where they conflict:**
- **Aged state is cleaned first** — *"it always misguides to keep it clean is priority!"* Done under «#3567».
- **Order of work:** API promises → hall fix and characterisation → fault handling → code/comment sync (always,
  on every line touched) → the style gate → every outstanding task → the commutation scan and offset confirmation.
- **The style guide is a GATE** over every `.spin2` this project authored; imported files are excluded. This
  brings PL-10 (`@param`/`@returns` completeness) and PL-11 (PUB-before-PRI) into the release.
- **Every outstanding task is in the release**, except three: the measurement front end «#3506», the vibration
  study «#3532» and the N-motor roster «#3562» (*"no those three are not in"*).
- **The commutation offsets are confirmed before release** — this reverses the 2026-09-15 exclusion. Confirmation
  is the redesigned scan (wheels lifted) and then an attended **spin-in-place** floor run, tethered, with a hard
  travel limit (*"yes spin in place but max revolutions limit so we don't stress cable"*).
- **Stop behaviour is the user's `holdAtStop()` selection**; every stop path must deliver it.
- **Safety scope (*"yes to all"*):** PL-73 in (refuse an undetected board unless a revision is forced); S-8 in
  (opt-in link-loss timeout); S-6 out (document the status values); AK measured feedback out as a Known Issue,
  with a getter for the compiled-in battery size / voltage in.

**Plan-state corrections found by the audit** (the plan is expanded to cover what is actually being done):
- The scan's own geometry assumes the motor FAULTS at each window edge; the lag limiter now makes it droop. The
  scan is redesigned, not merely re-run (R17.8).
- Visit 3 had already certified M, AF and S-5 with a provoked fault; what is missing is a provocation on today's
  lag-limited driver under the harness's 10 A abort (R17.5).
- PL-78's slam fix is in the binary with its effect unmeasured, because the ladder statistic cannot see a
  transition (R17.6).

### The work set (R17)

| Plan § | Deliverable | Task | Order |
|---|---|---|---|
| R17.0 | Clean all aged state | «#3567» | 0 (in progress) |
| R17.1 | Every stop path delivers `holdAtStop()` (PL-89) | «#3568» | 1 |
| R17.2 | API members keep their promises (AB, G, K, AC, AK getter) | «#3569» | 2 |
| R17.3 | Refuse an undetected board (PL-73); opt-in link-loss timeout (S-8) | «#3570» | 3 |
| R17.4 | Fix and characterise the hall read (PL-90, PL-69) | «#3571» | 4 |
| R17.5 | Fault handling on today's driver (PL-86, PL-59, PL-66, S-7, harness gaps) | «#3572» | 5 |
| — | The style gate, earned (PL-2, PL-10, PL-11, PL-29 rule) | «#3517» | 6 |
| — | Cog lifecycle and locks (PL-41, PL-85) | «#3543» | 7 |
| R17.6 | Measure the transition, settle the slam (PL-87, PL-78) | «#3573» | 8 |
| R17.7 | Bench cleanup: retire what feeds nothing, one builder (PL-53) | «#3574» | 9 |
| R17.8 | Scan redesign + spin-in-place floor tier | «#3575» | 10 |
| R17.9 | Visit 6: certify R17.1-R17.8, confirm the offsets — **split into 6a/6b 2026-09-19, see the revision below** | «#3576» | 11 |
| — | Apply the confirmed offsets | «#3523» | 12 |
| Blast radius | Documentation | «#3515» | 13 |
| — | Ship 6.0.0 | «#3516» | 14 (last) |

- **Dispatch:** `arbiter-serial` for anything touching `src/isp_bldc_motor.spin2` (an exclusive resource: R17.1,
  R17.2, R17.3, R17.4, R17.5, and the style pass). Bench-only work (R17.6, R17.7, R17.8) may overlap it.
- **Two-phase:** R17.1, R17.3, R17.4, R17.5, R17.8 and «#3543» return a design for review before code.
- **Out of this release:** «#3506», «#3532», «#3562» (backlog, marked in their task bodies).

## Sprint Revision — 2026-09-19: Visit 6 splits in two, and R17.2 gets its bench cells

**Why.** The path-to-Visit-6 study ([`../analyses/PATH-TO-VISIT-6-STUDY-2026-09-19.md`](../analyses/PATH-TO-VISIT-6-STUDY-2026-09-19.md))
found that the driver changed after Visit 5 (stop states, the hall read, board refusal, command timeout, fault
cause), so Visit 5 no longer certifies today's binary; that none of R17.2's five promises has a bench cell
(study F1, F2); and that the attended stop-mode hand test is not built (F3).

**Ruling (STEPHEN, 2026-09-19): *"yes, let's split"*.** Visit 6 becomes two visits, so the driver changes are
certified before the commutation scan is redesigned on top of them:

- **Visit 6a** — unattended `t0`, `dual-d`, `dual-b`, `dual-c`, `dual-a`, `dual-clock-200/-270/-300`; attended:
  the stop-mode hand test. Certifies R17.1-R17.6 and «#3543».
- **Visit 6b** — the redesigned `scan`, `dual-ui`, and the tethered spin-in-place floor run. Confirms the offsets.

**Rig fact recorded for R17.8:** track width 15.25 in (387 mm), tyre centre to centre (STEPHEN 2026-09-19).

### The work set (R17, revised 2026-09-19)

| Plan § | Deliverable | Task | Order |
|---|---|---|---|
| R17.10 | R17.2's promises get bench cells: G, K, AK in `t0`; AB (unequal distances) and AC (direction sign, lifted) in an unattended dual part; the dead `steerSetRamp()`/`steerRestoreRamp()` deleted | «#3577» | 1 |
| R17.7 | Bench cleanup: retire what feeds nothing, one builder (PL-53) | «#3574» | 2 |
| R17.11 | The attended stop-mode hand test (R17.1's at-rest and e-stop proof), on the `t0-hand` panel technique | «#3578» | 3 |
| R17.9a | Visit 6a: run sheet, run, report | «#3579» | 4 |
| R17.8 | Scan redesign + spin-in-place floor tier | «#3575» | 5 |
| R17.9b | Visit 6b: run sheet, run, report — confirm the offsets | «#3576» | 6 |
| — | Apply the confirmed offsets | «#3523» | 7 |
| — | «#3573»'s driver half, only if Visit 6a's `R17-DUAL-TRKICK-A` says the kick survives | «#3573» follow-up | with R17.8 |
| Blast radius | Documentation | «#3515» | 8 |
| — | Ship 6.0.0 | «#3516» | 9 (last) |

R17.10 and R17.11 are bench-only source (no library change). Visit 6a's sheet reviews that every new cell can
FAIL (D2) before the visit is offered.


## Sprint Revision — 2026-09-20: the drive comes first, and the observables are respecified

**Why.** Visit 6a's own data, re-read at Stephen's direction. Four rulings, all 2026-09-20:

- *"you are too focused on the braking when the ramps and proper integration of hall and current into
  motor drive is much more important"*
- *"you should always be weighing effect measure/fix/verify correct against the most imortant aspects of
  the driver changes first least important last"*
- *"if we have measures that are topping out we need to respecify them so they do not - as they are not
  useful once topped out"*
- *"if we also weigh-in what a user can command we are going to have to handle small delta
  speed-up/slow-down requests as well as large, near max throttle... our drive mech. has to handle this
  well"*

**What the data says** ([PL-95](../PUNCH-LIST.md)). Read as a ramp rather than as rungs, the Visit 6a
ladder shows three things happening together at the middle rung: `duty_pk` reaches `duty_max` and pins
there for the whole top half of the range; the steady current peaks and then *falls* while commanded
speed keeps rising; and `err_pk` climbs toward `LAG_HOLD`. The driver reports `AT_SPEED` throughout.
That is the same state PL-93 reached through a provoked fault, so **it is not an edge case — it is the
normal top half of this driver's range.** The transition current peaks at the same rung, which is the
kick Stephen feels at every increment; and the same 20×10⁶ step taken at six places in the range
produces a six-fold spread, so **where** a change happens dominates **how big** it is. Of the user's
command space we hold one cell of twelve: 44 speed-ups are measured and **zero speed-downs**.

**The reprioritisation.** The driver's core — how a commanded speed becomes correct commutation, which
is the halls, the current and the ramp — outranks stop behaviour, which outranks guards, instruments and
bench plumbing (doctrine overlay P10, added 2026-09-20). The stop-state work (R17.1) is landed and owes
only verification; it is not reopened. **The drive core becomes R18 and precedes everything else.**

⛔ **A sequencing consequence that changes what happens next:** the commutation scan and the offsets
(«#3575», «#3523») **must not run before the drive change.** They would confirm offsets for a drive we
are about to replace, and a drive change invalidates the speed-ceiling table regardless. They move
behind R18.

### R18 — the work set

| Plan § | Deliverable | Depends on | Order |
|---|---|---|---|
| **R18.1** | **Respecify the observables.** Driver publishes the unbounded quantities — the limiting actually applied, duty demand and its deficit, measured rate against commanded — **with no change to control behaviour**. Harness: emit a transition record for *every* segment (LIVE emits none today), and extend the ladder to descend as well as climb and to carry a small and a large delta at low / knee / high. | — | 1 |
| **R18.2** | **Visit 7 — characterisation, not certification.** Measure today's drive across the user's command space with the new observables, and certify the sensors are read fast enough and fresh enough to build a loop on. | R18.1 | 2 |
| **R18.3** | **The design.** Sensors and what each can actually tell us (measured, not assumed) → the observables → what the integration must provide as effects on the drive → the drive change → its acceptance numbers. | R18.2 | 3 |
| **R18.4** | **Build the drive change.** | R18.3 | 4 |
| **R18.5** | **Visit 8 — certify the change** against R18.3's numbers, across the whole command space. | R18.4 | 5 |

Then the existing tail, unchanged in content but moved behind R18: the scan redesign and floor tier
(«#3575»), Visit 6b («#3576»), the offsets («#3523»), documentation («#3515»), ship («#3516»).

**«#3573»'s driver half is subsumed.** Visit 6a proved the kick survives (Stephen's own reading, and the
transition current agrees), but the kick is a symptom of the drive integration, not a separate defect —
it peaks exactly where duty saturates. It is folded into R18.4 rather than built separately.

**Riding along, because they are cheap and block bench work:** PL-92's `t0-hand`/`t0-stopmode` A/B (one
minute, settles why no panel drew), and PL-94 (`t0` loses verdicts at cog bursts, cost two cells).

### Visit 7 — what it must gather, and why each reading is needed

A characterisation visit. Every measurement below feeds R18.3's design, and nothing is run that does not.

1. **The command space, both directions.** Speed-up *and* speed-down, at small / medium / large delta,
   from low / knee / high starting speed, plus near-max throttle. Today's ladder covers one cell; the
   gap that matters most is that **no slow-down has ever been measured**, and slowing is the direction
   where the field must fall back through the rotor — the opposite sign of error.
2. **Per transition, the respecified quantities:** limiting applied, duty demand and deficit, measured
   rate against commanded, transition current — with the old `err`/`duty` kept alongside for continuity
   with Visits 5 and 6a.
3. **Sensor-rate certification, which is its own question and not a by-product.** Control passes per
   hall edge across the whole speed range (if that approaches 1 at the top, no observer can work);
   missed and illegal hall counts at the extremes rather than only at the tested middle; and for the
   current, **how fresh the sample is when the loop acts on it and what it represents** — one
   PWM-synchronous instant, or an average. Rate alone does not answer whether a loop can be closed on it.
4. **The ceiling question, which the new observables answer directly.** At and above the saturation
   knee: does the duty *deficit* grow (the drive is giving up before the motor's limit) or is demand met
   at the cap (a real ceiling)? Current falling past rung 7 while duty is pinned reads like the former.
   This decides whether R18.4 is recovering lost range or protecting a real limit.
5. **Low speed and startup, which no test has ever covered.** As speed → 0 the halls stop informing —
   edges have not happened yet — so creep, startup and the last moments before rest are a distinct
   regime needing its own readings.

### Two questions this section once carried — both are closed, neither was his

⛔ **Release scope was never open.** STEPHEN 2026-09-20: *"Your role is to know that 6.0 release is
coming up. It is not to prompt me, 'Is it time to close it yet?' I'll decide that. I will continue to
tell you things we need to fix until I'm happy with the shape of the driver, so don't ask me about 6.0
anymore."* The version is settled, the ship trigger is his judgement of the driver's content, and
**everything in this plan lands in 6.0.0 by default.** R18's size is not a reason to reopen it; work
growing is not new information. Doctrine overlay P5 and P8 carry the rule.

⛔ **The "feedback fork" was built on a FALSE PREMISE OF MINE, and there is no fork.** This section said
until 2026-09-20 that the driver reads *three per-phase currents* and that choosing between them and the
aggregate shaped R18.3. **`sense_u/v/w` are phase VOLTAGES, not currents.** VERIFIED 2026-09-20 against
four sources that agree:

- **The Parallax 64010 manual, quoted verbatim** in `../analyses/BOARD-REVISION-FACTS.md` §Rev A and
  §Rev B 8: the board carries **one** low-side sense resistor, between common MOSFET GND and common
  system GND, measuring *"Total MOSFET load current"*. **There is no per-phase current sensing on this
  board at all** — 5 mΩ on Rev A, 3 mΩ plus an INA180B2 on Rev B, one shunt either way.
- `CURRENT-LIMIT-AND-STOP-DESIGN.md`, in its own words: *"The quantity that matters is phase current,
  and the board measures DC-link current."* The fold-back limiter therefore derives phase current as a
  **lower-bound estimate** from the DC-link reading and the modulation depth, precisely because no
  direct measurement exists.
- `../analyses/DRIVER-SAFETY-AND-CAPABILITY-STUDY-2026-09-09.md`, the observables table:
  `sense_u_/v_/w_` → *"phase voltages, 44 kHz."*
- The driver's own interface documentation: `nSenseI` is the *"current-sense reading"*; `nSenseU/V/W`
  are each a *"phase-U/V/W **sense** reading, in mV."* The getter never calls them current.

**What is actually unused, and what it is for.** Three phase-voltage channels are read and scaled on
every control pass and reach nothing but the status block. `../analyses/BLDC-COMMUTATION-PRINCIPLES.md`
already names their use, and it is **rotor angle, not current**: *"Resolve rotor angle better than 60°:
interpolate within a sector from the time since the last hall edge and the current speed, or estimate it
from the phase voltages the driver already samples every cycle (`sense_u/v/w`)."*

⭐ **This sharpens R18 rather than shrinking it.** PL-95's gap is that the field free-runs between hall
edges — a **position** problem, and phase voltage is a position source. The design question R18.3 must
answer is therefore *"can the phase voltages carry usable rotor angle between hall edges, and over what
speed range"*, not *"which current do we close the loop on."* There is one current channel; the only
current question left is how fresh it is when the loop acts.

⚠ **Consequences for R18.2, to design before the visit:**

- Characterise the phase voltages **as an angle source** — against the hall edges that bracket them,
  across the speed range, including where back-EMF is too small to read. Their failure mode at low speed
  is the same regime item 5 already calls out.
- The bench instrument stores the three phase readings as their **sum** (it packs `i` and `u+v+w` into
  one long), which is a *bus-voltage* estimator and discards exactly the per-phase difference an angle
  estimate needs. Carrying them apart costs hub or ring depth; instrument design is mine.

## Sprint Revision — 2026-09-21: phasing is corrected BEFORE the drive is designed

**Why.** Stephen, 2026-09-21, naming the two corrections the board designer's principles demand:

> *"1. We need to correct the phase offset in both directions so that we are running at the lowest
> peak current. 2. We need to inject power at the right timing."*

and, on why this cannot wait for R18.3:

> *"We know the angles that we're running at are out of phase, and we know that if we get in phase,
> we draw a lot less power. Where are we on correcting these two things so our measurements are
> measuring our corrected behavior versus our current state?"*

**The answer was: nowhere — and Visit 7 measured the uncorrected drive.** Every number R18.2
produced was taken at `off_neg,43 off_pos,317`, the uncorrected default, and the direction
asymmetry is fully present in it (MEASURED, `src/logs/debug_260920-182503.log`, `BM-RUNG2`/`BM-RUNG3`,
reverse-over-forward current at the same commanded speed):

| motor | rung 2 | rung 3 | rung 4 | rung 5 | rung 6 |
|---|---|---|---|---|---|
| LEFT | 1.93× | 2.02× | 2.04× | 1.97× | 1.10× |
| RIGHT | 1.88× | 1.91× | 1.93× | 1.87× | 1.06× |

Rung 6 closes the window because forward reaches duty saturation there, exactly as
[`../analyses/BLDC-COMMUTATION-PRINCIPLES.md`](../analyses/BLDC-COMMUTATION-PRINCIPLES.md) predicts.
This is the **third independent reproduction** of the ~2×: 2026-09-12 (1.76–1.97×), Visit 4 on
2026-09-17 (2.16/2.00/2.02/1.97), and Visit 7 on 2026-09-20.

### ⛔ This reverses one half of the 2026-09-20 ordering call, and the reversal is the point

The 2026-09-20 revision moved «#3575»/«#3523» behind R18 because *"they would confirm offsets for a
drive we are about to replace."* **Half of that reasoning was backwards.**

**The hall zero is physics, not algorithm.** Where the hall pattern's zero sits relative to true
electrical angle is a property of *sensor placement in the wheel*. It does not change when the
control loop is rewritten, and it is not invalidated by R18.4. Correcting it is not confirming
offsets for a doomed drive — it is **removing a known, measured, physical error from the baseline
that R18.3 designs against and R18.5 certifies to.**

What *was* right in that call stands: the **speed-ceiling table** dies with the drive change
regardless, and the **attended floor tier** (loaded, operator-observed) stays behind R18.

### The two corrections are different in kind, and only the first comes forward

| | **Correction 1 — the offset** | **Correction 2 — the timing** |
|---|---|---|
| What it is | Where the hall zero sits; a **constant**, plus a lead sign per direction | Placing *current* at ±90° of the rotor **at every speed and rotor position** |
| Why it is wrong today | The pair is symmetric about 0 (±43) instead of about the true zero | The servo holds **60°** (`sub tmpY, #256/6`), not 90°; the field **free-runs** between hall edges; current lag grows with speed while the lead is fixed |
| Its signature | **Asymmetry** — one direction costs ~2× the other | **A symmetric tax** — both directions pay |
| Its metric | reverse/forward ratio → **1.0** | **absolute** current at a rung falls, once the ratio is already near 1.0 |
| Where it belongs | **Here, before R18.3** | **Inside R18.3/R18.4** |

**The order is forced by the measurement, not by preference.** Everything in correction 2 is measured
*relative to* the zero. A speed-dependent lead built on a wrong reference silently absorbs the
constant error, looks right at the speed it was tuned at, and is wrong everywhere else — and the two
errors can no longer be told apart.

**⭐ The decomposition also gives two independent acceptance numbers from one run:** after correction
1 the ratio should collapse toward 1.0 while absolute current stays above ideal, and **what is left
over is the size of correction 2's prize.** The offset run is therefore not only a fix — it is the
measurement that *scopes* the driver work R18.3 designs.

### ⛔ A structural finding: the driver cannot express the corrected pair

`offsetsForMotor()` (`src/isp_bldc_motor.spin2:2507`, the `other:` branch) sets the 6.5″ hub's pair as:

```spin2
fwdDegrees := ofsDegr := 43
revDegrees := 360 - fwdDegrees
```

**The reverse offset is forced to be the negation of the forward one.** The pair is symmetric about 0
by construction. The scan's candidate minima are **+13.4 / −20.9** — symmetric about **−3.75**, which
matches the independently estimated hall zero of **−3.8**, exactly as the principles predict. That
pair *cannot be written* in today's code.

So correction 1 is a small, well-defined driver change, and it is the one
`BLDC-COMMUTATION-PRINCIPLES.md` §"How the principles apply" item 3 already named: **separate the two
meanings the offsets carry** — one hall-alignment constant `Z`, and a lead `L` applied `+`/`−` per
direction, giving `fwd = Z + L`, `rev = Z − L`. Setting `Z = 0` reproduces today's behaviour exactly,
so the change is backward-compatible and its own control.

### R18.2a–c — the work set

| Plan § | Deliverable | Depends on | Order |
|---|---|---|---|
| **R18.2a** | **Separate the offset's two meanings** in `offsetsForMotor()` — hall zero `Z` plus per-direction lead `L`, so an asymmetric pair can be expressed at all. `Z = 0` reproduces today bit-for-bit and is the A/B's control leg. Offsets selectable at build time, since the A/B recompiles between legs. | — | 1 |
| **R18.2b** | **Carry the three phase voltages apart** in the bench instrument. `instPackSense()` (`src/test_bench_dual.spin2:6557`) packs `i` and `u+v+w` into one long — a bus-voltage estimator that discards precisely the per-phase difference a rotor-angle estimate needs. Costs hub or ring depth (one sample is `INST_SAMPLE_LONGS` 9; the ring is 4_096 samples = 147_456 bytes = 8.19 s at 500 Hz). | — | 2 |
| **R18.2c** | **Visit 7b — the phasing A/B.** Run sheet with its expectations and falsifiers written **first**, cells confirmed able to FAIL, then the run: ladder rungs 2–5 both directions both motors at `Z=0,L=43` and at the candidate pair, plus per-direction ceilings, plus the phase-voltage characterisation. | R18.2a, R18.2b | 3 |

Then R18.3 as before — **designed against the corrected baseline**, and owning correction 2 — followed
by R18.4, R18.5, and the existing tail.

### What goes to this visit, and what is deliberately left off

**The filter:** correcting phasing changes the interpretation of every phase-sensitive measurement —
the duty knee moves, the current curve moves, the transition kick changes, the ceiling moves. So a
load is carried **only** if it is insensitive to phasing, or is deliberately run at *both* offset
settings as part of the A/B.

**Carried:**
- The **A/B itself** — rungs 2–5, both directions, both motors, both offset settings.
- **Per-direction speed ceilings**, inside the A/B rather than as a separate load. The principles
  document predicts the expensive direction faults lower, and records that the ceilings in source are
  single numbers applied to both directions, **never measured per direction**. Its stop condition is
  built on R18.1's unbounded observables (duty demand and deficit, measured vs commanded rate), not on
  the fault-edge walk the lag limiter broke.
- The **phase-voltage characterisation** (R18.2b). It is the sensor correction 2 depends on, it cannot
  be answered at the desk, and it is *not* invalidated by the offset change — the question is whether
  the signal carries angle at all, not what the angle is at a given offset.

**Left off, and why:** the missing 2-rung and 4-rung speed-**down** delta cells, the rung-6 current
collapse, and the low-speed duty floor. Each reads differently once phasing is corrected, so measuring
them now buys a number we would have to discard.

### The expectations, written before the run (D2)

| Outcome | Reading | Decision |
|---|---|---|
| Ratio moves from ~1.95 toward **1.0**, and absolute current at rungs 3–5 falls | the offset model holds; the depth below today's default **is** the prize | apply the pair; R18.3 designs against the corrected baseline, and the residual absolute current scopes correction 2 |
| Minima found but a **residual imbalance** remains at them | offsets are not the whole story | **do not redesign yet** — name the remaining cause first (unequal hall sectors, sensor placement, the one-sector table shift) |
| Ratio barely moves — within a few percent of the default | we are already near optimum | the ~2× is **elsewhere**; correction 1 is closed and correction 2 carries the whole driver case |

**Every cell must be able to fail**, and the run sheet declares the seven attributes, before the visit
is offered.

---

## Sprint Revision — 2026-09-21 (evening): Visit 7b returns, and the two knobs turn out to be one

**Visit 7b ran.** Two unattended legs, control first, both `src_rev,23 fmt,11`, both `exit,COMPLETE`,
zero faults. Evidence and full findings register:
[`../analyses/bench/2026-09-21/VISIT-7B-EVALUATION.md`](../analyses/bench/2026-09-21/VISIT-7B-EVALUATION.md);
logs filed at `../analyses/bench/2026-09-21/`, and the Visit 7 baseline — which existed only in the
runner's rotating gitignored `src/logs/_OLD/` — at `../analyses/bench/2026-09-20/`.

**The verdict is the top row of the table above, met on its own terms and not renegotiated.**

| motor | rung | VISIT 7 | CONTROL | **CANDIDATE** |
|---|---|---|---|---|
| LEFT | 2–5 | 1.93 / 2.02 / 2.04 / 1.97 | 1.96 / 2.04 / 2.06 / 1.99 | **0.99 / 1.01 / 0.95 / 0.98** |
| RIGHT | 2–5 | 1.88 / 1.91 / 1.93 / 1.87 | 1.89 / 1.92 / 1.94 / 1.88 | **0.95 / 1.01 / 0.92 / 0.91** |

⭐ **The control reproduced Visit 7 within 0.02 on all eight cells**, across a day and a source
revision. That is what makes this an A/B rather than two runs.

### ⛔ The prize was budgeted to the wrong correction, and the reason matters

The revision above predicted the two corrections would separate cleanly: *"after correction 1 the
ratio should collapse toward 1.0 **while absolute current stays above ideal**, and what is left over
is the size of correction 2's prize."*

**That is not what happened. Correction 1 delivered both.** Absolute netted current at rungs 3–5 fell
**15× to 26×** at the same met rate — `amps_x10k` at rung 6 goes LEFT 7.40 A → 0.46 A, RIGHT
7.75 A → 0.49 A — corroborated independently by the duty servo's own demand (83.7% → 53.9% at rung 5)
and by `win_cap` (1_890_038 → 278_434 frames). Commanded rate is met in both legs at `rate/pred`
0.989–1.009.

**Why the prediction failed is the most important finding of the visit:**

> ⭐⭐ **The commutation offset and the duty-servo setpoint are the same knob.**
> `err_ = hall_angles[sector] + offset − angle_` (`src/isp_bldc_motor.spin2:4458-4465`), and the servo
> holds `|err_|` at `sub tmpY, #256/6` = **60°** (`:4477`). The field therefore settles at
> `hall + offset ∓ 60°`. **Offset and setpoint add.**

And the arithmetic closes:

- the scan moved the lead **L: 43° → 18°** — a **−25°** correction
- the designer's prescription moves the setpoint **60° → 90°** — a **−30°** correction to the *same
  quantity*

**The same correction, reached independently, agreeing within 5°.**

### This refines — not reverses — the "different in kind" table above

That table remains right about correction 1 and about two of correction 2's three parts. What changes
is the third:

| Correction 2's parts | Status after Visit 7b |
|---|---|
| The servo holds **60°, not 90°** | ⛔ **Collapses into correction 1.** It is the same knob, and the scan has already turned it. |
| The field **free-runs** between hall edges (60° sectors) | Unchanged — still genuinely separate, still R18.3's |
| **Current lag grows with speed** while the lead is fixed | Unchanged — still genuinely separate, still R18.3's |

Three consequences the plan now carries:

1. **The commutation offsets were probably never wrong.** The 60° setpoint was, and the scan
   compensated for it by moving the offsets. The source comment at `:4477` reads *"256 frac 6 — where
   6 is # of hall cycles"*: **the 60° is one hall sector width, a structural number, never a torque
   angle.**
2. ⛔⛔ **Both corrections must never be applied together.** Adopting 14/338 *and* moving the setpoint
   to 90° double-corrects by ~55°. The basin is **steep, not broad** — 167.1 → 13.1 mV over 30°, a
   12.7× change — so that is catastrophic rather than marginal. This is the single largest trap in
   R18.3 and it is now written into «#3589».
3. **R18.3's correction 2 is no longer "hold 90° instead of 60°."** It is **"decide which knob carries
   the lead."** The split matters for three reasons the sum does not capture: the offset is
   feedforward and instant while the setpoint is servo-regulated; the **start transient is a setpoint
   problem** (below); and only a servo setpoint can be made speed-dependent, so the split decides what
   is *able* to adapt.

⚠ **One prediction of `BLDC-COMMUTATION-PRINCIPLES.md` is contradicted, in our favour.** It warned the
minimum would be broad — *"±15° from the optimum costs only a few percent."* Measured, it is a 12.7×
basin. Consistent with off-optimum current being dominated by **circulating current that makes heat
and no torque**, which is also the cleanest reading of the 15–26× collapse.

### The start transient — an operator observation the sheet failed to ask for

**Stephen, 2026-09-21, volunteered after the run:** *"there is an interesting thump at every ramp
start. It's not immediate; it's just after the ramp starts, but it's every single ramp start for that
second run."*

The logs carry it, and the reading inverts the question. Startup peak current at the from-rest starts
is **essentially unchanged across all three legs — 90 to 120 counts.** What collapsed is the *settled*
current around it, ~109 → ~32, taking peak/settled from 1.01 to **2.6–4.1**.

> **The thump is not new. The silence around it is.**

Mechanism (source-grounded, **hypothesis, no control yet**): `initAngleFmHall` (`:4570-4584`) seeds
`angle_ = hall + offset` at every spin-up from rest, and the control loop forms `err_` from the same
table and the same offset — **the offset cancels, so `err_ ≡ 0` at every start, at any offset pair.**
The servo's setpoint is 60°, so it sits in a **deadband** until `|err_|` climbs past it, then catches
up; that catch-up is the surge. Offset-independent by construction, which is exactly what three legs
across two offset pairs show.

**Consequence:** the start transient is now the drive's worst *relative* excursion, it fires at every
spin-up, **the commutation correction does nothing for it**, and it belongs to R18.3's low-speed and
startup regime. Carrying more lead in the feedforward offset and less in the setpoint should shrink it
— testable, and correct by construction.

⚠ **Instrument gap, ours:** the run performs 48 spin-ups in 209 s, its most-repeated event, and no
cell, record or trace covers a start — all 48 `BM-TS` traces trigger on stops. The only instrument
that caught this was a person standing next to the rig.

### What Visit 7b established about the offsets, and what it did not

⛔ **Every scan to date swept −63° to +63° electrical — 126° of 360°, about 35%**, bounded by
`ABORT_I` outside and by the motor faulting inside. One minimum per direction inside that window,
cross-confirmed on two motors and reproducible across runs 4–7. **So 14/338 is a proven *local*
minimum; it is not established as the global one.** Theory bounds it — one maximum per cycle per
direction, and the 180° rival is the reverse-torque solution, excluded because both legs tracked their
commanded direction at `rate/pred` ≈ 1.000 — but that is an argument, not a measurement.

The wheel has **15 electrical cycles per mechanical revolution** (`hallTicInfoForMotor()`,
`:1464-1466`), so one electrical cycle is 24° of wheel and any commutation feature repeats **15 times
around the circumference**: one optimum seen fifteen times, not fifteen optima. The offset is an
electrical angle applied identically in all fifteen, so "which one around the circumference" is not a
question the parameter can express.

### R18.2d–e — the work set, inserted before R18.3

**Why a visit is inserted.** R18.3 + R18.4 is 13 hours of design and build, and under the previous
order all of it rested on three unverified things: the start mechanism, whether our basin is global,
and the offset/setpoint split. **One ~40-minute unattended wheels-up visit converts all three from
assumption to measurement before those 13 hours are spent.**

| Plan § | Deliverable | Task | Order |
|---|---|---|---|
| **R18.2d** | **Land what Visit 7b proved, instrument what it exposed.** Adopt `Z=−4, L=18` as the shipped 6.5″ default (the old pair becomes the flagged build). Fix `R17-DUAL-TRKICK-A` to carry kick **magnitude** — its count was flat (105 vs 109 of 178) while peak `tr_i_over` fell **6×** (1_247 → 204), so as built it reports no improvement on the run's second-largest gain and would mis-certify the drive change. Fix `R18-DUAL-OFFSETS-A`'s `crit,?` (`APPLIED_EQ_COMPILED` is 19 bytes against `TOKMAX_CRIT` 18). Add a **START trigger** to the `BM-TS` trace machinery. ⛔ **No start-transient fix here** — its mechanism has no control, and building on it is the error D2 exists to prevent. | «#3593» | 1 |
| **R18.2e** | **Measure the hall zero `Z` COLD, from back-EMF, with no drive current.** *(Rescoped and split — see "R18.2e, rescoped" below; it is no longer a driven sweep.)* Bridge floating, wheel turned **by hand**, 8 legs = 2 wheels × 2 directions × 2 hand speeds. Settles `Z` absolutely over the whole circle at zero current. ⛔ Non-goals, so they are not re-added: no parameterisation by motor, no user documentation. **Do** keep the seams clean — per-motor quantities in one named block. Generalising to a real motor-adoption tool is «#3592», out of this release. | «#3590» | 2 |
| **R18.2e′** | **Rebuild the driven arc sweep for the LEAD `L`, stopping on droop.** The other half of the split: `Z` is geometry and is measured cold above; `L` is dynamics and can only be measured under drive. Rebuild the stop condition on R18.1's **unbounded** observables (measured rate against commanded, duty demand and its deficit), because the lag limiter now makes the motor **droop instead of fault** and the old fault walk cannot fire. Measure rate at **every** point including failing ones, and report the arc reached with each boundary's **type**. | «#3595» | 2b |
| **R18.2f** | **Visit 7c — one visit, three answers.** (1) the **cold hall-zero tier** `dual-align` — **attended, and nothing is ever driven**: Stephen turns each wheel by hand for 8 legs *(this load changed shape at the rescope below; it used to be the unattended full-cycle sweep)*; (2) the **start trace**, whose falsifier is stated in advance: if the surge is the servo deadband, duty stays pinned at `duty_min_` while `|err|` climbs and current surges only as `|err|` crosses 60° — *if duty moves before that crossing, the story is wrong*; (3) a **servo setpoint A/B**, `256/6` against `256/4`, **each at its own compensating lead so total field placement is held constant**, isolating the *split* rather than re-testing placement. Without that compensation the 90° leg runs 30° off-optimum, looks catastrophic, and teaches nothing. | «#3594» | 3 |

Then **R18.3 as before** — designed against the corrected baseline and Visit 7c's three answers, and
owning what is genuinely left of correction 2 — followed by R18.4, R18.5 and the existing tail.

### R18.2e, rescoped 2026-09-21 — a driven 360° sweep is physically impossible, so `Z` is measured cold

**The finding, from re-reading the run-7 scan log directly rather than the report of it.** Only about
**45 of 360 electrical degrees are reachable at a commanded speed**: `ABORT_I` at a swept ±63, lag
`FAULT` from +7 down to −11. **Both walls are the motor's, not the instrument's** — too much lead
explodes the current, too little cannot make the torque, and at 90° from optimum torque is zero at any
speed. No instrument, however good, sweeps a cycle the motor cannot run.

⚠ And the old instrument was worse than incomplete: **`rate_x10` reads `NA` at every one of the 19
non-OK points**, so it recorded fault and abort as a **binary** and never measured how far the drive
had already fallen behind. It could not characterise a boundary, only crash into one.

**Why the question is nonetheless answered — by physics, not by coverage.** The unreachable region is
unreachable *because* torque per amp is too low there, and a commutation optimum **is** a torque-per-amp
maximum. So the region that cannot be swept cannot be hiding one. **Per direction: one reachable arc,
one minimum.** The "is our basin global?" question does not need the sweep it originally asked for.

**The split, and why the two constants finally get the instruments that suit them.**

| | `Z` — the hall zero | `L` — the lead |
|---|---|---|
| What it is | **Geometry**: where the sensors sit in the wheel | **Dynamics**: how far the field leads the rotor |
| Varies with speed? | **No** — and a `Z` that does falsifies the instrument | Yes — current lag grows with electrical frequency |
| Measurable cold? | **Yes**: bridge floating, wheel turned by hand, back-EMF crossings against hall edges, full circle, **zero current** | **No** — only under drive |
| Plan § / task | R18.2e / «#3590» | R18.2e′ / «#3595» |

«#3586» had already separated these two constants in the driver. This is the measurement side catching
up with that separation.

**Why the cold measurement is a 2×2 and not a convenience.** Hall hysteresis and the P2 input filter's
delay **both** make an edge late in the direction of travel, so averaging the two **directions**
cancels both. The two **speeds** separate them, because hysteresis is a fixed **angle** and the filter
delay is a fixed **time** whose angle error grows with speed. Since `Z` cannot vary with speed, **a `Z`
that differs between the two speeds falsifies the instrument** — and the difference then solves for the
latency and extrapolates `Z` to zero speed. That is the instrument's own negative case, built in.

**Consequence for Visit 7c.** Its first load is no longer an unattended full-cycle sweep. It is an
**attended hand-turn tier** (`dual-align`) in which nothing is ever driven, alongside the two unattended
loads. That is a change in what the visit asks of Stephen and is stated here rather than discovered at
the rig.

### Sequence, as re-ordered 2026-09-21 (evening)

Stephen, delegating: *"I'm going to let you control priority because of findings and interactions with
other tasks. You know better what the priority should be."*

| seq | Task | Plan § | Who | est |
|---|---|---|---|---|
| 4 | «#3593» Land what 7b proved, instrument what it exposed | R18.2d | desk | 3h |
| 5 | «#3590» Measure the hall zero cold, from back-EMF | R18.2e | desk | 4h |
| 6 | «#3595» Rebuild the driven arc sweep for the lead | R18.2e′ | desk | 4h |
| 7 | **«#3594» Visit 7c** | **R18.2f** | **bench, ~40 min + an attended hand-turn tier** | 3h |
| 8 | «#3596» R18.3's **desk half** — the contract, the two wheels, the cog budget | R18.3 | desk, **needs no bench answer** | 2h |
| 9 | «#3589» Design the sensor integration — the **bench-gated** half | R18.3 | desk, after Visit 7c | 3h |
| 10 | «#3583» Build the drive change | R18.4 | desk | 8h |
| 11 | «#3584» Visit 8 | R18.5 | bench | 4h |

The tail is unchanged: «#3585» (benched), «#3591», «#3576», «#3515», «#3516». Out of release:
«#3506», «#3532», «#3562», and now «#3592».

### R18.3 split 2026-09-22 — so the roster can always offer an unblocked item

**The defect this fixes is in the plan, not in the execution.** R18 was written as a strict chain, so
every driver decision sat behind every measurement, and the moment the desk work ran out the roster
had nothing to offer but the instrument in front of me. That is the random walk the front ledger was
built to detect, and a ledger that detects it without a startable alternative only reports the problem.

**The split is by gate, not by size.** A decision belongs in «#3589» if and only if a Visit 7c answer
decides it: which knob carries the lead (the setpoint A/B), the start-transient mechanism (the START
trace), the speed law for `L` (`L` at a half, still never obtained), and back-EMF's usable range (the
ALIGN tier). **Everything else in R18.3 was never bench-gated** and moves to «#3596»: the user-visible
contract, the two-wheel consequence, the PASM cog budget, and the halls/current-sense rows of the
sensor table.

⭐ **What made the contract ripe is that the measurement already shipped.** `PUB testGetFollowing()`
landed at `31c8b91` (`isp_bldc_motor.spin2:1468`) and has **no ceiling**, unlike `err` held near
`LAG_HOLD` or duty pinned at its cap. Meanwhile `DCS_AT_SPEED` is set by the PASM driver at `:4269`
and `:4302` purely on reaching the commanded increment — **AT_SPEED is a commanded claim today**. So
"does AT_SPEED become a *measured* claim, and what do `getPower()`, `isTurning()` and `setMaxSpeed()`
mean when the drive knows a command is unachievable" is answerable at the desk **now**. R18.1's rule
is untouched: «#3596» decides the contract, **no control path reads the observable until R18.4**.

### Ruling carried into the plan: build the instrument now, generalise it later

**Stephen, 2026-09-21:** *"we could just build this as our standard instrument today and use it for
this phase for the 6.5, and use it for the doco when we get there. After having experience with it, we
can generalize it to a real tool and make that part of a later effort."*

Adopted, and it corrected an error this plan's own first rescope of «#3590» had made — specifying that
the instrument take the motor as a parameter and carry a stop condition for *"a motor whose fault
behaviour is unknown."* **That is designing against an imagined requirement.** The crux of generalising
is precisely the stop condition, and it cannot be derived until a second real motor has been observed:
the 6.5″ droops rather than faults (measured); the Doco's edge behaviour is not observed at all. The
phasing buys **two real motors before generalising, instead of one real and one imagined** — D7 applied
where this plan had just violated it. During the Doco run, **record what had to be edited** in the
named constants block; that list *is* «#3592»'s specification.

⛔ `ADDING_MOTOR.md` must describe the offset procedure **as it actually is** in 6.0.0 and must not
promise a generalised tool. That constraint belongs to «#3515».

### Ruling carried into the plan: dynamic lead in, back-EMF deferred — build, measure, then adjust

«#3589» wrote the drive change (`DRIVE-INTEGRATION-DESIGN.md` §5) and priced every candidate function
(§7). Stephen chose from that table.

**STEPHEN, 2026-09-22:** *"I'm very interested in the dynamic lead, and I'm also very interested in the
back EMF, but I'm thinking the back EMF is an added capability, and so I might make that a delta release
after we get the current driver stabilized. My current thinking is to defer back EMF. Let's go with dynamic
lead. Let's build the driver as you need to now so we can do the testing to calculate dynamic lead, and then
we'll make final adjustments once we understand the results from the testing."*

**The phasing, as R18.4 → R18.5 → R18.6:**
1. **R18.4, «#3583» — build.**
   - D-1, D-2, D-4, D-5 and D-6.
   - **The dynamic-lead mechanism**: the front cog writes the offsets from a table of L against
     `drv_incr_now`, every 8 ms slot. **The table is FLAT at the shipped L = 18**, so the drive behaves
     as shipped in placement until the table is measured.
   - **The live L-step bench tier** that measures the table.
2. **R18.5, «#3584» — Visit 8.** It certifies A-1 to A-10 and carries the live L-step run, which fills
   the table and prices it (§7 C-A).
3. **R18.6, a new task after «#3584» — fill the table and make the final adjustments**, certified by
   the rerun they need.

**Deferred to a delta release after 6.0.0 (Stephen's word, above):**
- back-EMF as a position source (§7 C-B);
- with it, the torque-peak hold (C-D, PL-105), which needs a sub-sector angle;
- hall-timing interpolation (C-C), which was priced only as C-D's other route.

The release-window capture (§7 C-B) is that delta release's first measurement.

### R18.7 — move the limits the old drive set, on purpose

Visits 8 and 8b certified the drive change and filled the lead table (R18.5, R18.6, both closed). Cruise current
fell 22–74 %, and the top rungs no longer saturate. **STEPHEN, 2026-09-22:** *"look for values that were limits
that were put in place before we had the new drive technology … let's move them purposefully"*, and *"Identify
which limits are in consideration, and then how you'd run experiments to move them … and then let's plan for
that."*

The inventory, the experiments and the steps are in [`LIMITS-RESET-PLAN.md`](LIMITS-RESET-PLAN.md), with tasks
«#3603» (E0: split the feedforward constant from the ceiling), «#3604» (build E1–E4 and the Visit 9 sheet) and
«#3605» (Visit 9, then move the limits). The loaded margin stays with the floor run («#3591» at «#3576»).

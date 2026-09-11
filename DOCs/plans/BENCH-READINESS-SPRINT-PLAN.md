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

1. **AD+ is answered, and it is library-wide.** `start_return,0,raw_motor_cog,2` with the cog
   demonstrably running. The chained `ok := motorCog := coginit(…) + 1` does not propagate;
   `p2kbSpin2Operators` documents no assignment-as-expression in Spin2. The same idiom is at
   **six** sites, so **every `start()` in this library returns 0 whether it succeeded or
   failed.** `if motorCog == 0` also cannot detect failure — cog exhaustion returns
   `$8000_000F`. *(`NEWCOG` was checked for the COGINIT pair-form trap and cleared.)*
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
`Vm`, `Wp`) at **~4 s each, 20 s per rotation**; `A`/`V`/`W` are not in the rotation. This
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
| **1** | **Measurement trust** | `start()` return (6 sites); board detection | `start()` return matrix; the A/B sweep binary (own artifact — see below) |
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

The original plan had one Tier 1 harness. Blast radius and one-shot hardware
force a split.

#### (a) The A/B detection sweep — its own binary, detached from every pass

**The A boards are a one-shot, no-motion resource.** They are at risk precisely
because the protection that would make them safe — correct revision detection
feeding correct current scaling, `rSenseForBoard` 5 vs 150 — is the thing that is
broken. **A-board protection needs the A-board data**, so a thin run leaves us
stuck in that loop. Over-capture.

**How it runs (Stephen, 2026-09-11):** two systems side by side, identically
wired. Connect to the B boards, run it, capture the log. Disconnect, connect to
the A boards, run the same binary, capture the log. Both logs come back for
comparison.

**Why a separate binary, decisively:** the main harness contains motion tests, and
loading it on the A rig puts a menu between an unprotected board and a spinning
motor. **A binary with no motion code compiled into it at all is the guard**, and
it is a better guard than discipline. It also makes the two logs diffable
line-for-line — no menu, no branch, one fixed sequence — and it can sweep
**all six declared pin groups** rather than assuming a config, which is what
yields the false-positive data (the B run showed an *empty* P32_P47 reading a
confident "64010 Rev B" at `pinSum 104`).

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

**Shape:** reuse `src/util_char_motor.spin2`'s drive-measure loop rather than
rewriting it. Quiescent zero, then four holds — left fwd, left rev, right fwd,
right rev — idle wheel **floating**, never `holdAtStop(true)`, whose holding
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
| **P0_P15** | **yes** | 500 | **"Board not detected!" ✗** | **false negative on a real board, read cold** |
| P32_P47 | **no** | 104 | **Rev B ✗** | **false positive on empty pins** |

**Only the second row is explained by the smart-pin leak.** P0_P15 was touched for
the first time in T0-7, with no cog ever having run on it, and still missed a
board that is physically there. That is a separate defect and it is the more
serious one — a false negative silently drops a wheel.

**A hypothesis worth testing rather than assuming, because it would explain both
remaining rows:** the RC model in the code assumes a *passive* sense-common node.
On Rev B that node is the **INA180B2 output**, and the rail was on for this run.
A powered INA180 **actively drives** its output, so there is no capacitor
discharge to measure — the pin reads the amplifier's output for the current
flowing, which at rest is near zero and would read *low* immediately. Whether a
Rev B board reads as "Rev B" may therefore depend on **whether its rail is
powered**, which is not something `getBoardType()` knows or checks.

**So the sweep binary must vary board power, not just pin state.** Per group, per
population: cold vs after-a-cog, `pinclear`ed vs not, **and rail on vs rail off**.
That is the 2×2×2 that separates three failure modes which currently look like one
flaky heuristic.

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

⛔ **Force `BRD_REV_B` in every bench build** rather than trusting auto-detect,
until board detection is fixed. Only possible because the A2/A3 fix landed in
`aea4981`; T0-2 in the 2026-09-11 log proves forcing now takes effect.

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

- `tools/build-check.sh` — ~~39/39~~ **41/41**, both release demos certified *(count corrected 2026-09-11)*
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
| 4 | «#3499» | 1 | `start()` returns 0 — 6 sites | task-standard | 1h30 |
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
later work inherits: a one-shot hardware record format, the most fragile ABI in
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
— that is the exact trade he declined. The principle generalises for the rest of
this sprint: **nothing that perturbs the path to the first bench results gets
taken on before them**, however tidy it would make the ordering.


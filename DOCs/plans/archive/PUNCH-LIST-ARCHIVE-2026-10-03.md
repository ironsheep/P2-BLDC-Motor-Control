# Punch-list archive — 2026-10-03

Items swept out of [`DOCs/PUNCH-LIST.md`](../../PUNCH-LIST.md) at the 6.1.0 (Hold Speed Under Load) sprint closeout
([`2026-10-03-HOLD-SPEED-CLOSEOUT.md`](2026-10-03-HOLD-SPEED-CLOSEOUT.md)). Each entry is copied verbatim; its top
status line says what closed it. Before the sweep, each closing status was checked against the tree and the three 6.1.0
bench visits' logs (`DOCs/analyses/bench/2026-10-02*/`).

Swept (20):
- **Shipped in v6.1.0 and certified on the bench:** PL-167 (speed held under load), PL-179 (the blocked stop latches),
  PL-180 (closed by evidence), PL-186 (the pivot holds), PL-187 (top speed runs clean), PL-189 (the limit hold's gaps),
  PL-132 (the protective stop coasts under coast), PL-169 (the FlySky knob deadband), PL-160 (the ramp a user shapes:
  every limb certified, the last the quarter-speed start under load).
- **Harness, certified on the bench:** PL-68 (every log names its commit), PL-96 + PL-97 (the record labels check
  themselves), PL-168 (the floor premises), PL-183 (SPINPEAK), PL-185 (the grab's limit), PL-188 (the obstacle count).
- **Done and proved by its gate:** PL-12 and PL-172 (the style gate), PL-37 (the unused assets), PL-67 (the compile-time
  pin-group refusal).

One residue left active: PL-185's `dual-floor` panel bitmap still reads 4 A until it is regenerated; it is carried on the
active list beside PL-64 / PL-65 (that tier has not run since its rebuild).

**This file is never re-edited.** If an archived item must be reopened, it returns to the active
punch list as a *new* item that references this archive.

---

### PL-12 -- latent: `check_pri_docs` conflates "has a trailing comment" with "is a comment line"

> **Status (2026-10-01): DONE** («#3646»). `check_pri_docs()` now ends the doc scan at any line whose code portion is
> not blank, as `check_pub_docs()` does. The audit of the other checks found the same conflation in two more: A5 (a CON
> constant with a trailing `' ----` counted as a separator line) and A4 (a code line with a trailing `''` at the top
> counted as header); both now require a comment-only line. C3a-C3f already read the code portion; C6, C6b and the
> signature's trailing-comment test are about declaration lines and are correct as written. `conformant.spin2` carries
> a PRI body line with a trailing `'`, one with a trailing `''`, and a CON constant with a trailing `' ----`; MEASURED:
> before the fixes the self-test reported C4 and then A5 on it, after them it exits 0 and `tools/check_style.sh` passes
> over `src/`.
>
> **6.0 status (2026-09-26 audit):** ANCILLARY — not chased for 6.0 (Stephen, 2026-09-26: only work that makes a 6.0 feature operational is chased) (style-gate tooling, latent)

`tools/check_style.sh`'s C4 check (guide 4.4, PRI docs must use `'` not `''`)
tests `rec['comment_kind'] == "''"` line-by-line after a PRI signature without
first checking that the line's **code portion is blank**. `comment_kind` records
*"this line carries a comment"*, not *"this line is comment-only"* -- so a PRI
**code** line ending in a trailing `''` comment would be reported as "PRI method
doc uses `''`" when it is not a doc line at all.

**No in-tree site trips this today** -- verified independently, no PRI body line
in `src/` carries a trailing `''`. So C4's current count of 9 is correct and
there is no observable defect. It is recorded because it is *latent*: the first
PRI body line written with a trailing `''` comment turns it into a false
positive, and a gate's false positives are what get gates switched off.

This is the **same conflation class** that caused the C3c defect fixed during
#3471 (see the root cause note in `tools/check_style.sh`), found while auditing
the other checks for that pattern. C3a/C3b/C3c/C3d/C3e are not affected -- they
all read the `prologue` list, which the C3c fix corrected at source. The
remaining checks were not exhaustively audited for it; doing that audit is part
of this item.

### PL-37 -- the meter-panel assets outlived the panel they drew

> **Status (2026-10-01): DONE** («#3648»). The five `bc_*.bmp` and `tools/gen_bench_char_assets.py` are removed
> (`git rm`); the note on measuring text width now lives in the `fit()` of `tools/gen_t0hand_assets.py` and
> `tools/gen_dual_assets.py`, and the two "same discipline" pointers name `tools/gen_dual_assets.py`. MEASURED: no
> reference outside `DOCs/` remains; both generators import; `test_bench_t0` (`t0-hand`) compiles.
>
> **6.0 status (2026-09-26 audit):** ANCILLARY — not chased for 6.0 (Stephen, 2026-09-26: only work that makes a 6.0 feature operational is chased) (unused bench panel assets)

**Found 2026-09-14 in «#3521».** The meter-free rework removed `test_bench_char.spin2`'s PLOT panel
(commit `7595274`), so nothing in that binary references its layer assets any more.

**The assets:**
- `src/bc_bg.bmp`
- `src/bc_caption.bmp`
- `src/bc_digits.bmp`
- `src/bc_labels.bmp`
- `src/bc_button.bmp`
- the generator `tools/gen_bench_char_assets.py`

**Why they are still in the tree.** Deleting them first needs a tree-wide search confirming that
nothing else consumes them. Neither the arbiter nor its agents had a search tool in that session,
and the project does not search through the shell.

**Decision.** STEPHEN, 2026-09-14: *"leave them for now"*.

**What has been read so far:**
- There is no reference in `src/test_bench_char.spin2`, `tools/build-check.sh`,
  `tools/check_style.sh`, `tools/bench-run.sh` or `.gitignore`.
- The rest of the tree has not been searched.
- `DOCs/PUNCH-LIST.md` PL-19 still mentions the generator.

**To close:** in a session with a search tool, confirm there are no consumers, then delete the six
files and update PL-19's mention.

### PL-68 -- no bench log names the commit it was built from, so a visit ran on an older commit unnoticed

> **Status (2026-10-02): ✅ CERTIFIED by the 6.1.0 visit:** all seven logs print `commit,0ba9b96` (`BM-COMMIT` in the
> six dual logs, `RC-BANNER` in `floor-rc`), the pack's commit. **Earlier: BUILT** («#3652», c60c0df and its follow-up). Every harness
> banner prints the commit (`test_bench_dual`: a `BM-COMMIT` record after `BM-BANNER`); `src/isp_bench_commit.spin2`
> reads `NOT_A_PACK` in the tree and is rewritten only in the pack's archive copy. MEASURED: a pack from c60c0df holds
> `c60c0df` in `dual-a.bin` and `t0.bin` and no `NOT_A_PACK`; a source-tree build holds `NOT_A_PACK`; `git status` is
> clean after the pack build. The runner echoes `git rev-parse --short HEAD` and the `src`/`tools` status before a
> source-tree compile (both limbs exercised), and skips it in a pack build.
>
> **Earlier status (2026-10-01):** IN 6.1.0, harness work for this plan's runs. **Design RULED (STEPHEN 2026-10-01, "re pl68
> yes A"):** the pack builder writes a tiny object holding the commit into its temporary `git archive` copy (never this
> tree), and every harness banner prints it; a tracked default copy reads "not a pack", so a build from the tree says
> so; the runner also echoes `git rev-parse HEAD` and the tree's clean state before any source-tree compile.
>
> **6.0 status (2026-09-26 audit):** ANCILLARY — not chased for 6.0 (Stephen, 2026-09-26: only work that makes a 6.0 feature operational is chased) (bench provenance tooling)

**Found 2026-09-16 in Visit 3** (`analyses/bench/2026-09-16/VISIT-3-RESULTS.md` §1).

**MEASURED:**
- The Visit 3 sheet was written for tree `9bdb9ea`, harness `SRC_REV 11 / FMT 3`.
- Both motion logs print `src_rev 7, fmt 1` (`debug_260916-120132.log:21`, `debug_260916-120254.log:21`).
- OVERSHT ran at 75 % with no `BM-FLTAPI`, and the runner was the one from before `13d5c46`.
- The four repairs the visit existed to certify did not run. It was found only by reading the banners.
- The cause, from `git reflog show origin/main`: the remote stood at `6aed714` until 2026-09-16 12:18, so the
  bench's pull (STEPHEN: *"i'll pull before running. I always do"*) got `6aed714`. The Visit 3 commits were not
  yet on the remote.

**The gap (DERIVED):**
- `SRC_REV` is hand-bumped per harness file, so it identifies the harness, not the tree.
- A library-only commit such as `17122f2` leaves every banner unchanged. So even a careful read cannot say
  whether a given driver fix was in the binary.
- Nothing on the console or in any log names the commit.

**Fix direction (for Stephen: the runner is a tool that fronts his toolchain, doctrine P2):** the bench
runner echoes the checkout's commit, and whether the tree is clean, before it compiles. Every console then
records what was built, visibly and replayably. Carrying the commit into the log banner too, via a `-D`
value, would make each log self-describing.

*Note, 2026-09-16:* the cause was commits not yet on the remote; the next run on `53c1f2b` had the right banners.
The finding stands: a log still cannot name its commit.

### PL-67 -- `R2-DETECT-OVERLAP` is owed to a motors-unplugged session, but no build can produce it

> **Status (2026-10-01): DONE** («#3650»). Both configurations of `isp_bldc_motor_userconfig.spin2`, and the bench
> config, carry `CHECK_` constants that divide by "the base is a legal group" and (dual) "the bases are 16 or more
> apart"; each check line's comment tells the user what to change. `tools/build-check.sh` step 3a compiles temporary
> copies with a right base of 24, an overlapping 16/8, an equal 32/32 and a single base of 24, and requires each to
> refuse at its named `CHECK_` line; the swapped legal pair 32/16 must compile. MEASURED: all five behave; with the
> checks disarmed in a scratch copy the step fails all four refusals. `DEVELOP.md` says what the refusal looks like.
>
> **Earlier status (2026-10-01, closeout): 6.1.0 work, by Stephen's ruling.** *"it can be produced and should be failed at
> compile time."* Two motor pin groups that overlap are a configuration error the compiler can see (both bases are
> constants in `isp_bldc_motor_userconfig.spin2`), so the build is refused, and `tools/build-check.sh` proves the refusal
> the way it proves a build with no `CFG_*` selected. The runtime `GATE_OVERLAP` skip in `test_bench_detect` stays as it is.
>
> **Shape (2026-10-01, plan research).** The preprocessor cannot compare numbers (p2kb `p2kbSpin2PreprocessorOverview`: no
> `#IF`, no expression evaluation), so the refusal is a CON constant that divides by "the bases are legal and clear";
> pnut-ts refuses it with `Divide by zero (m145)` at that line and a non-zero exit (prototyped). Legal enums alone do not
> prevent an overlap: bases 0/8, 8/16 and 32/40 share pins, and equal bases are one group (Stephen asked 2026-10-01). So
> the config checks both membership in the legal set and the pair's separation (`|L - R| >= 16`). At run time `start()`
> already refuses both (`ERR_BAD_PIN_GROUP`, `ERR_PIN_GROUP_IN_USE`, `isp_bldc_motor.spin2:4107, :4122-4125`).
>
> *Was (2026-09-26 audit):* ANCILLARY — not chased for 6.0 (Stephen, 2026-09-26: only work that makes a 6.0 feature operational is chased) (detection harness gap)

**Found 2026-09-15** while writing the Visit 3 run sheet. DERIVED from source. It is a **gap in the harness**,
not a driver defect.

**The claim that fails.** Every record since Visit 1 says the deferred cell `R2-DETECT-OVERLAP` is "owed to the
first session where the motors are unplugged" (`plans/VISIT-SIGNOFF-DESIGN.md` §J.2), and the Visit 3 scope
carried it as a no-code rider on the Rev A swap load.

**MEASURED, in `src/test_bench_detect.spin2`:** the gate-input guard is computed at runtime from
`user.LEFT_MOTOR_BASE` and `user.RIGHT_MOTOR_BASE` "in every sweep of every build" (its header, and the
`-D DETECT_NO_TAIL` note states plainly that the guard is not disabled by any flag). The two cells the deferred
sign-off names -- `P40_P55` (sense pin P44 = the LEFT board's `pin_pwm_w_l`) and `NO_USE_P24_P39` (P28 = the
RIGHT board's) -- are therefore skipped as `GATE_OVERLAP` whatever is physically plugged in. **Unplugging the
motors is the safety precondition for relaxing the guard; the relaxation itself was never built.**

**What it costs.** `«#3500»`'s behaviour that an overlapping pin group reports *not detected* rather than Rev B
has no bench evidence, so the 6.0.0 release line for it stays DERIVED (`«#3515»` already treats it that way).
Nothing else waits on it.

**Fix direction, for its own scoping -- not a run-sheet rider.** A compile-time flag on the passive build
(`detect` / `detect-lib`, no driver cog at all) that suppresses `GATE_OVERLAP` only, leaving `COG_OVERLAP`
refused, plus a tier that states the motors-unplugged precondition in the log the way the other preconditions
are stated. It deliberately drives a board's gate input, so it is a change to a hardware safety guard and wants
a review before its first run, not a slot before a bench session.

### PL-96 -- an over-length record token prints as `?` with no signal, so a label can be lost silently

> **Status (2026-10-02): ✅ CERTIFIED by the 6.1.0 visit:** `dual-tokneg` FAILs on its planted token (`BM-TOKCHK
> ...first_bad,tokScope,...,ok,FALSE`) and every other dual log PASSes R21-DUAL-TOKTAB (45-70 tables). **Earlier (2026-10-01): BUILT** («#3651», `test_bench_dual` SRC_REV 71). Every count is
> derived from its enum; all 80 token tables end in a sentinel; `tokenTablesSelfTest()` walks every table the build
> holds, plus the sign-off cell and criterion strings, and prints `BM-TOKCHK` and cell `R21-DUAL-TOKTAB` in every dual
> build. Its negative is the one-off tier `dual-tokneg` (one table a token short, one token too long), which must print
> FAIL. Found while building it: `sFenWords`' fourth word was 37 bytes against `tokenAt()`'s 32-byte scan, so fence
> words 4 and up printed wrong text; the scan bound is now 40. Footprints unchanged within 4 bytes (dual-a 6,649,
> floor-auto 6,858, limit 12,404). The bench owes: the first dual log's cell PASS, and `dual-tokneg`'s FAIL.
>
> **Earlier status (2026-10-01):** IN 6.1.0, together with PL-97, as one start-up self-check (STEPHEN 2026-10-01: harness work
> for this plan's runs). **A fourth instance since this entry:** `sSfCritSpPeak` was `START_I_OVER_STEADY_X100`, 24
> bytes against `TOKMAX_CRIT` 18, and printed `?` until SRC_REV 70 shortened it (`test_bench_dual.spin2:3338`).
>
> **6.0 status (2026-09-26 audit):** ANCILLARY — not chased for 6.0 (Stephen, 2026-09-26: only work that makes a 6.0 feature operational is chased) (bench record vocabulary)

**Found 2026-09-21 while judging Visit 7b.** Open. **One instance is fixed; the class is not.**

**MEASURED (`DOCs/analyses/bench/2026-09-21/debug_260921-124024.log`):** the visit's load-bearing cell
emitted `SIGNOFF,...,cell,R18-DUAL-OFFSETS-A,...,crit,?,...` -- the criterion name replaced by a single
question mark. **Cause proven by counting, not inferred:** `sSfCritOffsets` was
`"APPLIED_EQ_COMPILED"`, **19 bytes against `TOKMAX_CRIT = 18`** (`src/test_bench_dual.spin2:740`), and
`tokenField()` prints `@sBadTok` for any token longer than its declared max, by design and without
complaint (`src/isp_bench_log.spin2:121-131`). One byte over.

**FIXED at R18.2d («#3593»):** the token is now `"OFFSETS_AS_BUILT"` (16). An audit of every
`sSfCrit*` token found this was the **only** one over the limit; the next longest sit at exactly 18, so
`TOKMAX_CRIT` is correctly sized and this string was the outlier.

⚠ **WHAT IS NOT FIXED, and why this entry exists.** Shortening the string dodges today's instance of a
defect class that can recur on any future token edit with **no compile-time and no run-time signal**.
The verdict and the count survived here, so the A/B was not compromised -- but the cell that certifies
that the driver runs the offsets it was built with could not name its own criterion, and nothing
reported that. **The deeper fix belongs in the mechanism:** either a compile-time length check so an
over-length token fails the build loudly, or a start-up self-check over the token tables that emits a
verdict like every other mechanism does. Neither is in R18.2d's scope.

**Cost if left:** a silent `?` is indistinguishable from a criterion nobody named, and doctrine D2 is
explicit that a check reporting something ABSENT routes to opposite owners -- the run failed to emit
it, or the contract describes something never emitted. This defect makes the second case look like the
first.

### PL-97 -- a token table shorter than its enum walks off the end and prints adjacent DAT as text

> **Status (2026-10-03, closeout): ✅ CERTIFIED with PL-96** — one mechanism: the start-up pass checks each table's
> length to its sentinel as well as each token's length. TOKTAB read TRUE on all 14 judged dual logs of the three visits,
> and FALSE only on `dual-tokneg`'s planted defects (`debug_261002-095938.log`: `bad_count,1,bad_len,1`).
>
> **Earlier status (2026-10-01): BUILT with PL-96** («#3651»; see PL-96's status). **Earlier:** IN 6.1.0, together with PL-96 (one mechanism).
>
> **6.0 status (2026-09-26 audit):** ANCILLARY — not chased for 6.0 (Stephen, 2026-09-26: only work that makes a 6.0 feature operational is chased) (bench record vocabulary)

**Found 2026-09-21 while adding the ALIGN segment.** Instance fixed; **the class is the same one as
PL-96 and is not fixed.**

`tokenAt()` (`src/test_bench_dual.spin2:8699-8711`) bounds the index against **`tokenCount`, which the
caller supplies** -- not against the table's actual length. Callers pass the *enum* count. So a token
table with fewer entries than its enum does not return `"?"`; it walks past its own last entry into
whatever `DAT` follows and returns that as the field's text.

**MEASURED, first instance:** `tokFinds` carried **15** entries against `SEG_COUNT` **16**.
`SEG_LOWSPD` is index 15, so `BM-PLAN`'s `finds` field for LOWSPD already indexed past the end.

**MEASURED, second instance — and it is the one that proves the class.** `tokPart` carried **9**
entries against `PART_COUNT` **10** from the moment `PART_ALIGN` joined the part enum. `PART_ID` is the
index, so an ALIGN build printed adjacent `DAT` in the `part` field of **`BM-BANNER`, `BM-PLAN`,
`BM-EXIT`, every `SIGNOFF` and the watchdog record** — five record types, the run's own identity among
them. ⚠ **It was introduced by the very commit that fixed the first instance** (`5a8969b`): the same
enum addition broke two tables, one was found and one was not, and nothing in between could tell.
That is the argument for the mechanism below rather than for another careful edit — a class this easy
to re-open while fixing it cannot be closed by attention.

⚠ **It never showed, because a second defect hid it:** `BM-PLAN` never emitted a LOWSPD row at all --
`PART_A` hard-codes four `emitPlan()` calls (the earlier study's F1, still open). **Two defects, each
concealing the other.** Fixing F1 alone would have started printing garbage into a user-visible field
with nothing reporting it.

**FIXED at R18.2e («#3590»):** `tokFinds` extended to `SEG_COUNT`, and the `estS`/`estKb` `lookupz`
tables extended with it -- those were also one entry short and would have returned 0 for a new segment
rather than failing. `tokPart` extended to `PART_COUNT` in the follow-on commit that built the ALIGN
measurement core.

**MEASURED, third instance (2026-09-22, found by «#3604»).** `SEG_LEAD` («#3583») and `SEG_TAKE` («#3584»)
joined the segment enum with no `tokFinds` row and no `estS`/`estKb` entry. The Visit 8b `dual-lead` log shows
it: `BM-PLAN,...,seg,LEAD,...,finds,?,est_s,0,est_kb,0` (`debug_260922-164207.log`). This time the adjacent DAT
happened to begin with `"?"`, so the field read as unknown rather than as a wrong word. **FIXED at «#3604»:** both
rows filled, the LIMITS part's three rows added after them, and part A now prints its LOWSPD and TAKE plan rows
(F1's two missing rows). The class below is still open, and this is its third instance in three segment additions.

⛔ **WHAT IS NOT FIXED.** Nothing prevents the next table from being short. **A table's length and its
enum's count are asserted nowhere**, in either direction, and the failure is silent in both: short
table prints adjacent memory, and PL-96's over-length token prints `?`. Both are the same underlying
gap -- **the record vocabulary has no self-check.** The fix is one mechanism, not two: a start-up pass
that walks every token table against its enum count and emits a verdict, which would have caught this,
PL-96, and the short `lookupz` tables in one run.

**Cost if left:** a `finds`, `crit` or `seg` field can misdescribe itself with no signal, and doctrine
17 requires that a field never print a value under a label that misdescribes it.

### PL-132 -- the blocked-wheel protective stop shorts the phases even when the user chose coast

> **6.1.0 status (2026-10-03): ✅ CERTIFIED** by the second visit: after a protective stop the COAST trial's phases read
> 166 / 160 mV (coasting, BLKCOAST PASS) and the BRAKE trial's 16 / 13 mV (shorted, BLKSHORT PASS)
> (`debug_261002-143413.log`).
>
> **Earlier 6.1.0 status (2026-10-02, the visit): STILL UNMEASURED.** The COAST trial never latched under DRIVER_REV 47 (PL-179),
> so BLKCOAST read NOMEAS; the BRAKE trial faulted at contact (PL-180), so BLKSHORT did too. The COAST half waits for
> PL-179's fix and its visit.
>
> **Earlier 6.1.0 status (2026-10-02):** the no-latch bound replaced by one timed from the driver's own count (735bc9d);
> D-5 was expected to make the COAST trial latch. It did not.
>
> **6.0 status (2026-10-01):** AWAITS CERT — the short control PASSed on both visits (BLKSHORT 14 / 15 / 13 mV); the COAST
> cell is NOMEAS twice: a lag fault pre-empted the latch (first visit), then the harness's no-latch bound gave up about
> 240 ms before the driver would have latched against a rocking obstacle (the rerun). Rerun once PL-168 corrects the bound.

**Found 2026-09-23** as fault study F-5, and **filed 2026-09-25** («#3609» phase 3). `frontProtectiveStop()` secures
the motor with `frontEStop(TRUE)`. The PASM e-stop takes `.shortBridge` "whatever the stop mode"
(`isp_bldc_motor.spin2`, the `.eStop` branch). So a blocked wheel under SM_FLOAT is shorted, and the user's
`holdAtStop(FALSE)` is not honoured on this path (P3: behaviour the API lets the user select is theirs). The wheel is
stationary by construction, so the short brakes nothing. The cost is on a slope: a short at rest creeps, and the user
who chose coast gets a state they did not choose. The e-stop itself stays a hard short by Stephen's ruling. Only its
reuse here is the defect.

**Disposition:** ⛔ fix in the driver, «#3609». The protective stop gets its own immediate stop that takes the stop mode's
at-rest state: SM_FLOAT coasts, SM_BRAKE holds, and the hold's own hand-off to the short still applies. It still latches
and refuses drives until `clearProtectiveStop()`. **Unmeasurable wheels-up** (PL-106: a lifted wheel cannot be
blocked), so it is certified by construction and by the floor run (the OBSTACLE runs, «#3628»). Building it gates no load on the current
bench pass.

**FIXED (DRIVER_REV 20, 2026-09-25), not bench-certified:** `e_stop` carries its kind: ES_OFF, ES_HARD (emergency
stop, walk guard, `frontSecure()`) or ES_PROTECT (`frontProtectiveStop()`), written in one store by `frontLatchStop()`.
The PASM latch calls `estopBridge` (LUT), which shorts for ES_HARD and for ES_PROTECT under SM_BRAKE, and coasts for
ES_PROTECT under SM_FLOAT. Every reader tests non-zero, so the refusal semantics are unchanged. DRIVE-OBJECTS.md's
*Protection and limits* says which state the stop takes. ⚠ It is a user-visible behaviour change, so it needs a release
note line («#3516»).

### PL-167 -- under a heavy load the shipped commutation timing gives up speed with torque to spare

> **Status (2026-10-03, closeout): ✅ SHIPPED in v6.1.0** (DRIVER_REV 49, tag `54f7c43`). PL-179 and PL-180 were fixed
> and certified by the third visit (`DOCs/analyses/bench/2026-10-02c/VISIT-6.1.0C-EVALUATION.md`); the v6.0.0 Known
> Issue is dropped from the v6.1.0 entry by Stephen's ruling.
>
> **Earlier status (2026-10-02, the 6.1.0 visit): SPEED HELD, CERTIFIED; NOT SHIPPABLE until PL-179.** (`DOCs/analyses/bench/2026-10-02/VISIT-6.1.0-EVALUATION.md`.)
> SPINRATE PASS (every leg 100-107 %, against 57-94 %), RAMPARR PASS (1,807 / 1,790 and 323 / 320 ms), no path limiting in
> the FlySky drive, SPINCTL judged 4.64 / 4.74, wheels-up SRVHUNT / SRVKEEP PASS; a hand's load is held. But the blocked
> stop no longer latches (PL-179), two lag faults and a slow-down kick are new (PL-180), and the boost fires in calm running
> (PL-181). SPINHOLD / LIMGIVE's single LEFT holds are PL-182; BLKLIMIT / BLKSTOP NOMEAS.
>
> **Earlier status (2026-10-02): BUILT, DRIVER_REV 47** (9ede499): D-1..D-3 plus PL-167 D-5, as Stephen ruled 2026-10-02 (*"ok
> let's go with A"*).
>
> **Earlier status (2026-10-01, R21):** a **v6.0.0 Known Issue**; the fix is **6.1.0** work. Stephen: *"ok yes, A lets get
> 6.0.0 to release first then we'll follow with this new effort"*. The CHANGELOG, the manual's §6.5 / §9, the REWORK page,
> and every "holds the fastest speed it can sustain" claim in the user docs now state what v6.0.0 does.
>
> *Was (2026-10-01):* RELEASE — Stephen, on hearing it: *"is there something we can do to address this to make
> it more like a professional driver? i'm assuming one wouldn't do this."* Desk work first (Plan A §11).
>
> **Design (2026-10-01):** `DOCs/plans/HOLD-SPEED-UNDER-LOAD-DESIGN.md`. The cause is proven for the quarter-speed
> contrast (schedule against fixed) and unproven for the slow/medium depth (§3.6). D-1 a calmer trim gain, D-2 a fast
> slope past `LAG_SOFT`, D-3 the field gives way only at a limiter, and D-4 `LAG_HOLD` 86 (decided (a), conditional:
> §7 Q1). Phase 2 approved with the slow/medium depth unproven (Stephen 2026-10-01, *"ok A"*; §7 Q3): the desk refit
> first, stopping to ask if it finds a second mechanism.

**Found 2026-09-30**, the hands-off floor rerun (`DOCs/analyses/bench/2026-09-30/floor2/FLOOR-RERUN-EVALUATION.md` §2.1, log
`debug_260930-181811.log`).
- **MEASURED:** spinning a 7.7 kg platform in place, every leg on the shipped lead table (17/336 at slow and medium,
  5-6/346-347 at the quarter) ran at 57-94 % of its commanded rate (`fol_pct`), with the lag at the limiter's hold
  (`err_pk` 84-113), the duty swinging 900-1,650 (SPINHUNT FAIL 4 of 4, both wheels), the mean error off its point
  (SPINERR FAIL) and the path limiter trimming (`path_pm` 629-861). The legacy pair (43/317, medium) and the fixed pair
  (14/338, quarter) held 100 % with the path limiter idle (`path_pm,1_000`) and `err_pk` 72-94, at about twice the current.
- **MEASURED:** the duty used on those schedule legs was 2,000-3,700 of 27,648, and the current 0.05-0.14 A: the drive
  gave up speed far from its current limit.
- **The same signature** appears in the FlySky drive's 200 mm/s² speed-up (about half the set rate realised, the lag
  limiter pulling the field back 15 times) and in the two ramp legs that arrived late.
- **What a professional drive does instead (DERIVED):** holds speed by raising torque up to the current limit and gives
  up speed only there; advances the field with load as well as speed.
- **Not established:** the cause -- the duty servo's authority and stability under load with this timing, the order in
  which the lag limiter and the servo act, the lead's load dependence, or several together.
- **Consequences:** SPINCTL's PASS (schedule current 1.89x / 2.40x below legacy) compares unequal delivered speeds;
  SPINSYM RIGHT 1.36 likely shares the cause.

### PL-168 -- floor-test premises the runs proved wrong

> **Status (2026-10-03, closeout): ✅ CERTIFIED, all five.** The coast bound ran once PL-179 was fixed: both obstacle
> trials latched on the second and third visits, and BLKCOAST / BLKSTOP PASS (third visit: counts 997 / 1,003). Its three
> follow-on premises are PL-182, PL-183 and PL-185.
>
> **Earlier status (2026-10-02, the 6.1.0 visit): four of five premises CERTIFIED; the coast bound UNEXERCISED.** Two-turn quarter
> spins measured SPINSTRT / SPINPEAK / SPINLEAD for the first time; SPINCTL was judged at equal speed; the obstacle trials
> printed their own RESULTs; the labels read true. The coast no-latch bound never ran (the trial timed out, PL-179). Three
> new wrong premises are PL-182 (LIMGIVE), PL-183 (SPINPEAK), PL-185 (the grab).
>
> **Earlier status (2026-10-02): CORRECTED in the tree** (735bc9d, `test_bench_dual` SRC_REV 74-76).
>
> **Earlier status (2026-10-01):** 6.1.0 work (R21); no test harness ships in a release archive set. To be corrected before any rerun (Stephen: *"if we deem a test needing to be run again and it's
> build on wrong premise we should correct that before running again, right?"*).

From `FLOOR-RERUN-EVALUATION.md` §4, §2.1, §7:
- **The coast trial's no-latch bound** (`BLK_STAND_HI_MS`, from `BLK_LAG_MS`) assumes the lag is at the hold at the
  wheel's last tick. On a rocking obstacle it was at -28 and took about 430 ms to reach the latch's 80, so the harness
  gave up about 240 ms before the driver would have latched (`l_stand,1_183`, bound 1,180).
- **SPINCTL** assumes both timings deliver the same speed; under load they did not (PL-167).
- **The obstacle RESULT** reads the session-wide BLKSTOP count, so a passing BRAKE trial printed "a check failed".
- **SPINSTRT / SPINPEAK and the quarter's window** need about 0.5 s at speed; a one-turn quarter spin holds about 0.3 s,
  and one leg missed its window (SPINLEAD NOMEAS). The platform is untethered (R20): two-turn quarter spins.
- **Labels:** a missed window prints `STEADY_TIMEOUT` (the 4 s bound was not reached) and SPINLEAD prints
  `JUDGED_ACROSS_RUNS` inside a single session.

### PL-169 -- the FlySky demos re-send the acceleration setting on knob noise

> **Status (2026-10-03): ✅ CERTIFIED** — the second visit's FlySky drive swept both knobs end to end (raw 240-1,807;
> rates 200-3,000 and 1,000-3,000 mm/s²), still sending only on a move. **Earlier (2026-10-02):** the deadband CERTIFIED; the ends NOT SHOWN. 47 rate updates in the FlySky
> drive (`debug_261002-104014.log`), each more than 10 mm/s² from the one before, and none while a knob stood still. The
> knobs were not turned to both stops (VRA 499-1,735, VRB 270-1,514 raw; rates 662-2,867 and 1,048-2,626), so "both ends
> reached" waits for the next FlySky drive.
>
> **Earlier status (2026-10-01): FIXED IN THE TREE** («#3649»). Both demos send a knob's rate only when it moves more than
> `RC_RATE_DEADBAND_MM_S2` (10) from the rate last sent, or reaches an end of its range (`bRateMoved()`). DERIVED (desk
> simulation of the demos' integer `map()` over the default 240..1807 calibration): a ±2-count still knob moves the rate
> at most 8 (VRA) / 6 (VRB) mm/s², so it sends nothing; one-count sweeps reach 200 / 3,000 and 1,000 / 3,000.

The VRA knob's ±2-count noise (raw 1,504 / 1,506) changes the mapped rate by 4 mm/s², and the demo calls
`setAcceleration()` on every change: about every 250 ms through the last minute of the 2026-09-30 rerun (2,458 / 2,462).
A deadband of a few counts on both knobs would stop it.

### PL-172 -- the style gate's self-test fails: check T128 has no fixture

> **Status (2026-10-01): DONE** («#3646»). `tools/fixtures/style/T128.spin2` fires T128 and only T128; MEASURED:
> `tools/check_style.sh --self-test` exits 0.

**MEASURED 2026-10-01:** `tools/check_style.sh --self-test` exits 1 and ends `SELF-TEST FAIL: no fixture exercises:
['T128']`. T128 (no parenthesis in display text, PL-128) joined `ALL_CHECK_IDS` (`tools/check_style.sh:1151`) in
`13495a7` with no `tools/fixtures/style/T128.spin2`, so since then the self-test cannot prove that every check fires.
The gate itself (`tools/check_style.sh` without `--self-test`) is unaffected. **Fix:** a `T128.spin2` fixture on which
T128 fires, and only T128.

### PL-179 -- under D-5 a blocked platform does not stop itself: the protective stop never latched

> **Status (2026-10-03): ✅ CERTIFIED, cells included** (third visit: BLKSTOP / BLKLIMIT PASS, stands 1,017 / 1,028 ms).
>
> **Earlier status (2026-10-03): the DRIVER fix CERTIFIED by the second visit** — both obstacle trials latched, stands 1,022 / 1,002
> ms (`debug_261002-143413.log` seq 383, 757). BLKSTOP / BLKLIMIT still FAIL on the harness mirror (PL-188), and C4's gaps
> are PL-189.
>
> **Earlier status (2026-10-02): BUILT, DRIVER_REV 48; awaits the second visit** («#3662»). Cause SETTLED at the desk
> (`DOCs/plans/HOLD-SPEED-UNDER-LOAD-DESIGN.md` §4.10.3): at a low limit the fold-back acts in single frames (the stall's
> own counters: 1,677 / 914 fold frames in ~9.5 s, so at most 18 % / 10 % of passes), and the count needed 1,000 in a
> row. STEPHEN 2026-10-02 (*"yes, a"*) ruled all three parts: **F-a** the count's limiter half is sticky from the first
> limiter action after a tick until the next tick; **C4** the limit hold stays armed until the rotor ticks forward;
> **S-1** (PL-180). MODELLED: a solid object latches 1,010-1,116 ms after contact (4 of 4; 15 of 16 in the full grid),
> against never. DERIVED: with C4 and S-1 neutralised the image is equivalent to DRIVER_REV 47 (`tools/pasm_equiv`, 112
> of 112), so nothing else changed. **Earlier:** ⛔ FIX, found by the 6.1.0 visit (evaluation §3.2, F-1).

**MEASURED 2026-10-02** (`debug_261002-103634.log`, DRIVER_REV 47, 2 A obstacle limit): in the COAST obstacle trial both
wheels stood still against the object for about 9.2 s (trace `k` 675-2,975, `pos` frozen, state SPIN_UP), the lag at 64-77
on both, until the harness's own timeout stopped them (`BM-BLOCK` seq 327, `stop_by,TIMEOUT`). Four `EV_FOLDBACK` at contact,
none after. On DRIVER_REV 46 the same trial stood 1,183 / 1,092 ms (`2026-09-30/floor2/debug_260930-182135.log` seq 362).
- **The rule:** `bFrontProtect()` (`isp_bldc_motor.spin2:2896-2902`) counts a pass with no tick when `|err|` ≥ `LAG_SOFT`
  (80) or a limiter count advanced (SPIN_UP / AT_SPEED), and latches at 1,000 in a row. D-5 sets the field back to
  `LAG_LIM` (64) on a limiter pass, so `|err|` never reached 80; the limiter half never ran 1,000 in a row.
- **Not established:** the per-pass limiter counts (not recorded). *Consistent with* a limiter acting on many passes but
  not every one, against design 4.9.5's premise that one acts on every pass. The model (`block`, 2 A, D-5) separates it.
- **Not to do:** lower `LAG_LIM` or `BLOCKED_PASSES` to make it latch; the stop's timing is a safety bound.

### PL-180 -- lag faults on hard transients, and a slow-down current kick, new at DRIVER_REV 47

> **Status (2026-10-03, third visit): CLOSED BY EVIDENCE.** The FlySky drive on DRIVER_REV 49 ran 123 reversal samples at ≥ 150
> tps (more than the three earlier drives together) with no fault; no contact fault on either obstacle trial. The first
> visit's reversal fault is not explained, only not recurring.
>
> **Earlier status (2026-10-03, second visit):** the slow-down kick CERTIFIED gone (TRKICK-A 24 / 30 mV); no fault at obstacle
> contact (BLKFLT PASS); no reversal fault in the FlySky drive, on fewer reversals (9 samples at ≥ 150 tps against 27): not
> settled. A hand-slowed wheel faulted under the grab (PL-189).
>
> **Earlier status (2026-10-02): two of three BUILT, DRIVER_REV 48; the reversal fault UNEXPLAINED** («#3662»; design §4.10.4-5).
> - **The contact fault: consistent with, modelled.** Between fold-back frames the field walked back from 64 through
>   |err| 82..88, where one tick against it faults; C4 keeps it at 64 while blocked. Modelled lag faults against a
>   yielding object 7 → 0 of 16 (DRIVER_REV 46: 1).
> - **The slow-down kick: consistent with, modelled.** The PL-55 ceiling held duty down until the lag reached
>   `LAG_SOFT`, where D-2's boost started from the clamped duty. S-1 lifts it at `SERVO_SETPOINT`: modelled +115 → +52 mV.
> - **The FlySky reversal fault: NOT reproduced, cause not established.** No 6.1 change acts in a slow-down (D-5 acts
>   only in SPIN_UP / AT_SPEED; the "D-2 against D-5" hypothesis is refuted). The next FlySky drive's hard reversals are
>   its reading; if it recurs it is root-caused from that drive's log.
> **Earlier:** root cause first; found by the 6.1.0 visit (evaluation §3.2, §3.4, §2.2; F-2, F-3).

**MEASURED 2026-10-02:**
- **The BRAKE obstacle trial faulted at contact:** RIGHT re-synced and faulted about 80 ms after the wheels stopped
  (`debug_261002-103634.log` seq 336, 338; `o_e` −125). DRIVER_REV 46's trial latched with no fault.
- **A FlySky hard reversal faulted:** from reverse at 175 tps to 98 forward and back to 0; RIGHT in SPIN_DN at `r_err`
  100, duty 8,827, re-synced at 31,942 ms and faulted at 32,134 ms (`debug_261002-104014.log`). The two DRIVER_REV 46
  drives had more reversals at speed (78 and 53 SLOW_TO_CHG samples at ≥ 150 tps, against 27) and no fault.
- **Wheels up, the 80 → 20 ×10⁶ step-down now kicks:** TRKICK-A 79 / 89 mV against 50, `tr_err_pk` 101, `tr_cap` 367
  (`debug_261002-100025.log` seq 16_718-17_291). The same step on the last ladder (2026-09-22, driver 4) read 0-19 mV and
  `tr_err_pk` 84-92. No speed-up kicked.
- **Not established:** a cause, or whether they share one. D-2 acts on the lag in `drv_incr`'s direction and D-5 on
  `err_`'s sign; a slow-down or reversal is where they could disagree. That is a hypothesis for the model.

### PL-183 -- SPINPEAK's 1.80 limit is a wheels-up number; the floor reads the platform's spin-up current

> **Status (2026-10-03, closeout): ✅ CERTIFIED** — SPINPEAK PASS on the second and third visits (third: 22 / 10 mV
> over the steady mean, against 50).
>
> **Earlier status (2026-10-02): CORRECTED, `test_bench_dual` SRC_REV 78** («#3664»): SPINPEAK reads the ARRIVAL (two samples from
> the first AT_SPEED sample), and judges the peak's excess over the steady mean in mV against TRKICK's 50 (criterion
> `ARRIVE_I_OVER_MV`), not a ratio: at a 12-19 mV floor tail one count is 5-8 %, and the ratio read 1.47-1.96 on single
> noisy samples. On the 2026-10-02 legs the excess is 7-13 mV (PASS); its negative is TRKICK's on-file pre-fix arrival kicks
> of 64-183 mV. **Earlier:** OPEN (F-6).

**MEASURED 2026-10-02**, the first measurement (two-turn legs): 3.74 / 4.06 (leg 7) and 3.39 / 3.25 (leg 8) against
1.80 (`BM-SPINSTART` seq 420-421, 762-763). The trace (tid 7) shows a plateau of about 180 ms while SPIN_UP pushes the
platform (LEFT 59-68 at `k` 272-325), falling to 26 by the arrival at `k` 420 with no spike, so the shape is acceleration,
not a kick. SPINSTRT, which judges the arrival, PASSes. The 1.80 came from Visit 8 wheels up, about a fifth of the
inertia. **Fix:** derive the floor limit from the spin-up's own current (the jerk-limited ramp's acceleration on the
platform's yaw inertia), or judge the arrival's excess over the plateau instead.

### PL-186 -- in a fast pivot turn the coasting inner wheel is driven backward, so the platform spins about its centre

> **Status (2026-10-03): ✅ CERTIFIED in the log** by the second visit: `RC-PIVOT,samples,378,moving,0,max_tps,25,unheld,0,
> ...,verdict,PASS` (`debug_261002-143653.log`); Stephen's word on the feel is still to come. **Earlier: BUILT** («#3663»). STEPHEN 2026-10-02 chose option (a), *"yes your
> recommendation"*: the FlySky demos (and `test_bench_rc`, SRC_REV 7) select `holdAtStop(true)`, and `DRIVE-OBJECTS.md`'s
> `driveDirection()` row says a pivot needs hold. Cell `RC-PIVOT` judges it (a wheel at rest in a pivot moving faster than
> 50 tps FAILs; desk arithmetic on the logs: the 2026-10-02 drive fails 65 of 547, the 2026-09-30 drive passes 126 of
> 126). If hold does not stop the spin, option (b), a pivot-only hold in the drive, is the fallback.

**Stephen, 2026-10-02:** in a full left or right turn, *"it would run really well for a little bit, and then ... the
robot would start spinning around its physical center instead of around the stock wheel."* **MEASURED**
(`debug_261002-104014.log`): right turn 118.6-119.2 s and left turn 144.1-145.5 s, the inner wheel at power 0, STOPPED and
coasting (`l_hs` / `r_hs` HS_OFF on every sample), driven backward up to 225-250 tps once the outer wheel passed about 300
tps. **Cause (settled):** in a full turn the steering object gives the inner wheel plain power 0
(`isp_steering_2wheel.spin2:2425-2426`); it ramps to STOPPED and takes the program's stop selection, which in the FlySky
programs is coast (`holdAtStop(false)`, `demo_dual_motor_rc.spin2:114`). A free wheel is pushed back by the platform's
yaw. **Not settled:** whether DRIVER_REV 47 made it worse. The 2026-09-30 pivots (also coasting) were slower and only
crept. **Options for Stephen:** select hold in the demo; or a pivot-only hold for the inner wheel (an exception to "stop
behaviour is the user's selection", needing a driver change); each with its cost (current at the held wheel, the hold's
10 % ceiling and 2-tick slip). *Corrected 2026-10-02:* the first entry read the right wheel's fault flag as its hold
status ("HOLDING while rolling"); no hold was ever engaged.

### PL-187 -- above about 175 ×10⁶ the wheel runs rough: gravelly, vibrating, never settling

> **Status (2026-10-03): ✅ CERTIFIED by the third visit** (`DOCs/analyses/bench/2026-10-02c/VISIT-6.1.0C-EVALUATION.md` §2):
> TOPSPD 245 ×10⁶ on all four wheel/directions, every rung above 175 reaching speed with no limit hold (`win_lag,0`).
> **Earlier: T-1 BUILT, DRIVER_REV 49; awaited the third visit** (its `dual-limits` traces the edge rung; TOPSPD
> should read above 175). **Earlier: cause established at the desk; T-1 RULED** (STEPHEN 2026-10-03 *"yes a"*; design §4.11, «#3668»):
> at the duty ceiling the limit hold (D-5) and D-3 act on a duty-cap pass, yanking the field back every sector. T-1: only
> the current fold-back triggers the limit hold. The second visit's `dual-limits` read 185 ×10⁶ the same way (its
> negative). **Earlier:** OPEN, evidence only (Stephen's report of the first visit's `dual-limits`).

**Stephen, 2026-10-02:** *"at the highest speeds, the motor sounds gravelly. It's having a hard time spinning, and it's
making terrible noises and a huge amount of vibration. That would suggest that we're out of sync with our positioning at
the high speeds."* **MEASURED** (`DOCs/analyses/bench/2026-10-02/debug_261002-101625.log`, DRIVER_REV 47, wheels up,
pack about 20.5 V):
- **Clean through 175 ×10⁶ on all four wheel/direction pairs:** rate on the speed law (e.g. `rate_x10` −4,685 against
  −4,676), lag at the servo's point (`err` −48, `err_pk` 71-73), no missed, illegal or skipped hall reads, PWM room 36
  counts (`BM-RUNG2` / `BM-RUNG3` / `BM-CLIP` seq 141-145).
- **At 185 ×10⁶, on all four:** the rung never settles in 4 s (`STEADY_TIMEOUT`); the PWM sits at its rails
  (`lvl_min` 3, `lvl_max` 2,995 of 3,068, room 3, over about 3,017 samples); and the hall reader skips sectors (`hw_skip`
  3 / 4 / 6 / 2, rids 14, 35, 56, 77), none of which happens below.
- **The over-command (245 ×10⁶ at 1 A):** the field falls to 13 % of the command and the wheel follows 5 % of it
  (`BM-FOLLOW kind,OVER` seq 159, 268, 377, 486).
- **No lag fault and no re-sync anywhere in the segment** (`BM-SEG LIMTOP ... faults,0`), so the field never got 125
  counts from the rotor: whatever the noise is, it is not a pole slip the fault test sees.

**Rival explanations, none separated by this log:** (a) the drive runs out of voltage: at the rails the sine is clipped
and the current, and with it the torque, ripples; (b) the lag rises past the torque peak once the duty can rise no
further (held at `LAG_HOLD`, 140° electrical, PL-105's case), so the wheel labours; (c) commutation timing (the lead)
goes wrong at that speed. The hall skips fit (a) or (b) as vibration and (c) as mis-timing. **What would separate
them:** a trace of the 185 rung and of the over-command (`err`, duty, current per 2 ms sample), and a desk read of what
the drive does once the duty is at its ceiling. **Why it matters to a user:** full power is 165 ×10⁶, which ran clean
here at 92 % duty on a 20.5 V pack; on a pack at the nominal 18.5 V the same speed needs about 102 % of that duty
(DERIVED: 25,460 × 20.5 / 18.5 ≈ 28,200 against the 27,648 ceiling), so a user at full power on a lower pack may reach
this region. Evidence for the "less torque in reserve near top speed" Known Issue (P5).

### PL-188 -- the obstacle mirror zeroes its count on the pass that sees the latch

> **Status (2026-10-03): ✅ CERTIFIED** by the third visit: BLKSTOP PASS, counts 997 / 1,003 passes. **Earlier: FIXED in `test_bench_dual` SRC_REV 80** (the count is kept on the pass that
> first sees ESTOP). **Earlier:** ⛔ FIX, harness, 6.1.0 («#3668»); found by the second 6.1.0 visit
> (`DOCs/analyses/bench/2026-10-02b/VISIT-6.1.0B-EVALUATION.md` §3.2, G-1).

**MEASURED 2026-10-02** (`debug_261002-143413.log` `BM-BLOCK` seq 383, 757): both trials latched with stands of 1,022 and
1,002 ms, yet `l_count,0,r_count,0`, so BLKSTOP and BLKLIMIT FAIL. `blockWatch()` (SRC_REV 77) applies the driver's state
test to its count; on the pass that sees the latch the wheel already reads ESTOP, so the count is zeroed before the latch
is checked. **Fix:** check the latch before the count's bookkeeping, or keep the count on the latching pass.

### PL-189 -- the limit hold (C4) protects a wheel only from its first set-back to its next forward tick, and keeps the field fast

> **Status (2026-10-03): ✅ CERTIFIED by the third visit** (evaluation §2-3): BLKWIN PASS (lag held at 64 while blocked),
> LDFLT PASS (no fault under the grab), OVRSTEP PASS on all four (no surge; field 9-20 % at the over-command's end).
> **Earlier: BUILT, DRIVER_REV 49.** STEPHEN 2026-10-03 *"yes A"* (design §4.12): U-1 the
> hold arms at every fold-back action; U-2 it stays armed until the rotor crosses a whole sector forward with no fold; U-5 its
> release caps the field's speed at 4 sectors over the passes since the fold. MODELLED: over-command end 34 A → 3 A; obstacle
> fault-band readings 4 → 0; steady grab faults 1 → 0 of 16. Certified by BLKWIN, the new LDFLT and OVRSTEP (SRC_REV 81).
> **Earlier:** ⛔ FIX, design then driver; found by the second 6.1.0 visit (§3.2-3.4, §2.2; G-2, G-3, G-4).

**MEASURED 2026-10-02, DRIVER_REV 48:**
- **Before it arms:** on both obstacle trials the RIGHT wheel's lag reached 85 / 83 once inside the window after its first
  limiter action (BLKWIN FAIL; `BM-BLKWIN` seq 386, 760). C4 arms at the first set-back, not the first limiter action.
- **On a wheel the limit slows but does not stop:** under the grab at 2 A, LEFT (slowed to 19 %) re-synced and lag-faulted
  (`debug_261002-143538.log` seq 16, 19). C4 disarms at every forward tick, so the exposure returns each sector.
- **At the end of a sustained limit:** the 1 A over-command now ends with the field at 47-52 % of command (13 % on
  DRIVER_REV 47); the full-power step after it drew ~9.6 A on LEFT (`BM-ABORT ... ABS_CURRENT,value,1_445`, `debug_261002-
  142002.log` seq 161) and the board fell silent at the same step on RIGHT (reset or link, not separated).
**Candidate corrections (to design):** arm at the first limiter action; stay armed while the wheel is limited; let D-3 give
the field's speed way on armed passes at a sustained limit.

### PL-185 -- a hand cannot slow the platform at the grab's 4 A limit, so the grab cells measure nothing

> **Status (2026-10-03, closeout): ✅ CERTIFIED** — at 2 A the third visit's hand slowed the platform to OVERLOAD (LEFT
> 31 %, RIGHT 70 %, `path_min` 733), so the grab cells measured: LDFLT and LDHOLD PASS, LDPATH NOMEAS `LIMIT_HELD` as
> designed; LDHUNT's own definition is PL-192.
>
> **Earlier status (2026-10-02): CORRECTED, `test_bench_dual` SRC_REV 78** («#3664»): `LOAD_LIMIT_A` 4 → 2 A (derived: 2 A drove
> the platform to the obstacle on both 2026-10-02 trials; the hand reached the 4 A fold-back briefly, so at 2 A it is past it
> for most of the hold). `tools/gen_dual_assets.py` matches; the `dual-floor` UI panel bitmap it renders still reads 4 A
> until regenerated where its font exists (that tier is not on the next sheet). **Earlier:** OPEN (F-9).

**MEASURED 2026-10-02**, two runs (`debug_261002-103814.log`, `-103915.log`): `RESULT: GRAB -- too light`, `l_pct` 99 /
`r_pct` 101 and 99 / 98. While held, LEFT's duty rose from about 2,000 to 3,300-4,700 and its sense current from 7-12 to
41-85, and the speed held; the fold-back engaged briefly (`EV_FOLDBACK` 53, 44; 25). That is the fix doing its job, and
design R8 predicted it. **Fix:** a limit a hand can reach (well under 4 A), or a known drag in place of the hand, so
LDPATH / LDHUNT / LDHOLD see path limiting.

### PL-160 -- a user cannot shape the ramp for their robot: deceleration is fixed, settings are lost on start(), and every ramp starts and ends with a torque step

> **Status (2026-10-03, closeout): ✅ CERTIFIED, every limb.** The API half (t0-api, 2026-09-27), the jerk-limited
> generator wheels up (Block A, 2026-09-28), the feel under load (Stephen's FlySky drives, 2026-09-28 and -30) and the
> quarter-speed start under load (below; SPINSTRT and SPINPEAK PASS again on the third visit). Its follow-ons are their
> own entries: PL-102 (a held-ramp report), PL-166 (the inertia term), PL-191 (a speed raised mid-slow-down dips first).
>
> **Earlier 6.1.0 status (2026-10-02, the visit): the quarter-speed start under load CERTIFIED.** SPINSTRT PASS on both wheels,
> duty drop 0 at the arrival (`debug_261002-103332.log` `BM-SPINSTART` seq 420-421, 762-763), with no arrival spike in the
> trace. SPINPEAK's FAIL is its wheels-up limit read against the platform's spin-up current, not the start (PL-183).
>
> **Earlier 6.1.0 status (2026-10-02):** two-turn spins (735bc9d) for SPINSTRT / SPINPEAK.
>
> **6.0 status (2026-09-30):** RELEASE — wheels-up half certified 2026-09-28; the feel under load ✅ CERTIFIED by
> Stephen's first FlySky drive (*"very responsive... no clicking, no unusual motor movement or sounds. Its ramps are
> pretty good."*), which the telemetry agrees with; the second drive (2026-09-30 rerun) confirmed both knobs' rates reach
> the ramps exactly. SPINSTRT / SPINPEAK at the quarter need two-turn spins (PL-168, R20).

**Found 2026-09-26.** `setAcceleration(rate)` sets only speeding up. Every slow-down and stop runs at a fixed
`ramp_down` of about 1,470 mm/s², which only the raw `setRampingValues()` can change. `start()` discards the setting
(`init()`). The ramp steps acceleration from 0 to full and back in one drive pass at both ends. The desk study
(kick spec, 2026-09-26) and its model: the speed-change *current* kick is a separate one-pass defect (the field is not
advanced on the arrival pass, fixed under PL-78/87). The acceleration steps are what a user *feels*, and the jerk
limit is kept for that.

**STEPHEN 2026-09-26 (Q1):** *"yes sep calls"*. So `setDeceleration(rate)` in mm/s² is added beside `setAcceleration(rate)`,
which stays as it is.

**Disposition: ⛔ build**, from the kick spec's section B, as amended by the model:
- one jerk-limited trajectory generator per motor, continuous through every transition and reversal, with
  τ ≥ 250 ms if starts from the lowest speeds are in scope;
- acceleration and deceleration set independently, kept across `start()`, with getters and the steering and serial
  mirrors (`setdecel`);
- the stop prediction and `stopAfter*()` limits kept exact.

Open owner questions, asked one at a time: Q2 the built-in rates; Q3 `setRampingValues()`; Q4 reporting a held ramp;
Q5 the inertia term.

**2026-09-27, Visit 10 pass 7:** the API half — `setDeceleration()`, persistence across `start()`, and the getters —
is CERTIFIED by t0-api (10/10 families, 0 bad). The entry stays OPEN for the jerk-limited trajectory generator (the
feel). Its built-in rates (owner Q2) are unanswered, and do not block anything until that generator is built.

**2026-09-27, built (DRIVER_REV 38), the generator.** Not yet run on hardware.
- **One generator per motor** (`jerkStep`, LUT-resident, called once per drive pass while not at rest). State: v =
  `drv_incr`, a = its change per pass. Each pass, with e = target - v, s = sign(e), E = |e|, alpha = s a: the side toward
  s takes the speed-up pair when v is 0 or has s's sign, else the slow-down pair (J, A); x*(E) is the largest alpha from
  which a pure J ramp-out lands exactly on the target; U is the jerk-limited step toward A; alpha' = min(U, max(alpha -
  J, x*)). So every ramp eases its acceleration in and out, and lands exactly on its target with a = 0 (arrival advances
  the field: DRIVER_REV 34's kick fix kept). A reversal passes through zero in one continuous ramp; only a start from
  DCS_STOPPED seeds the field from the halls; SLOW_TO_CHG is only reported.
- **Departures from the survey spec, each for a stated reason.** (1) The survey's "|e| > dvStop + |a|, else toward 0"
  test is made exact by the x* bound, so the ramp-out lands on the target instead of creeping back to it in bumps; that
  is what lets the stop prediction be closed form. (2) The pair is chosen by the side a is on, not by the target's
  direction alone, and an acceleration on the far side (or above a lowered limit) unwinds at the larger jerk: with the
  target's pair, a stop read mid-speed-up unwound the up-ramp's acceleration at the slow-down jerk, for up to ~10 s at
  the setter limits (DERIVED, desk model). (3) At the target (e = 0) any |a| up to max(jerk_up, jerk_dn) ends at 0: with
  the survey's snap only (|a| <= J of the side), an arrival's last step met the other side's smaller jerk on the next
  pass and overshot (desk model); zeroing a on the arrival pass itself let a command on the next pass step it by 2J.
  (4) The LAG_SOFT gate eases a toward 0 by J, as specified. (5) x* costs two CORDIC divisions and a square root per
  pass (~230 clocks); the survey's own dvStop divides by J too. J itself is computed on the Spin2 side, as specified. No held-ramp count is kept: without an ABI long the Spin2 side cannot read a cog register, and a PASM
  debug() would print every pass.
- **ABI:** params run unchanged at 27 (`ramp_down`/`ramp_max`/`ramp_min`/`ramp_inc` reused in place as
  `accel_dn`/`accel_up`/`jerk_up`/`jerk_dn`); status run 21 -> 22 (`drv_accel_now` appended, `fault` after it;
  `isAbiLayoutValid()` checks it). `testGetAccelNow()` (motor) and `testGetAccelNow() : nLeftAccel, nRightAccel`
  (steering). The path-scale and hold-decay floor is the constant DRV_INCR_FLOOR (1_500), no longer `ramp_min`.
- **Built-in rates (owner Q2 still open; named constants a ruling only retunes):** ACCEL_BUILTIN_MM_S2 1_000,
  DECEL_BUILTIN_MM_S2 1_470, RAMP_TAU_MS 250. Each jerk = its limit / 478.3 passes, rounded, at least 1, on the Spin2
  side. `getAcceleration()` now returns 1_000 until set. `setRampingValues()`: maxRamp and decrRamp are the two limits,
  minRamp and incRamp have no effect (owner Q3 open); `getRampingValues()` returns the four driver parameters.
- **Stop prediction:** `frontStopTicks()` / `frontStopMs()` read one closed form of the rule (`stopPlan()`: take pass,
  unwind, rise, plateau, ramp-out, and the stop-at-zero corner). DERIVED against a pass-by-pass model of the rule over
  ~7_000 random stops: passes exact, travel within 0.02 tick. The PASM routine's own source lines, executed by an
  instruction-level interpreter, match that model on 4.5 million passes (desk checks, not bench).
- **Rev A fold-back (same revision):** the fold compares the whole-mV reading ABOVE the floored threshold (was at or
  above it). At the duty floor on Rev A the threshold is 0.375 x amps mV, which floored to 0 under ~2.7 A and folded
  every driven frame.
- **Negatives** (what shows it did not work): a ramp's drv_accel_now stepping by more than max(jerk_up, jerk_dn) in a
  pass other than a stop read just before a reversal's zero crossing; a drive that does not settle on its target with
  drv_accel_now 0 from the pass after its arrival, or overshoots it; a stop that crosses zero; the field stopping
  (DCS_STOPPED, a hall re-seed) at a reversal's crossing; a distance, rotation or time limit that no longer comes to
  rest inside the tolerance its existing cell judges; the speed-change current kick back above pass 7's 16/13 mV. Rev A: with `testSetCurrentLimits(2, 2)` a driven, unloaded
  wheel still counting foldback_frames every frame.
- **Costs:** cog RAM 403/496 (was 487), LUT 402/512 (was 293), read from the compiler listing. A stop now takes
  RAMP_TAU_MS longer and travels speed x 0.125 s further than DRIVER_REV 37's (DERIVED; ~100 ticks from 196 ticks/s,
  was 75 measured). `stopPlan()` adds Spin2 work to every front pass with a limit armed (unmeasured: PL-161's
  R16-DUAL-FRONTST re-certifies it).

**2026-09-27, owner Q3 RULED (STEPHEN: *"Yes, remove the set ramping values and get ramping values calls. We don't need
them."*).** DRIVER_REV 46: `setRampingValues()` / `getRampingValues()` are gone; `setAcceleration()` /
`setDeceleration()` (mm/s²) are the only ramp settings, identical on the motor and steering objects and over serial.
The four driver parameters stay readable to a harness as the TESTING USE `testGetRampLimits()`. The steering setters
now set the right wheel only once the left accepted (a rejected call changes neither wheel, by construction). README
lists the removal as BREAKING. Q2 (the built-in rates): Stephen asked whether the defaults make sense; the answer given
was keep them and confirm on the floor (the floor sheet's PL-160 feel line). Q4 RULED 2026-09-27 (STEPHEN: *"no
public api change"*): nothing is added for 6.0; the held-ramp report moves to PL-102, after v6.0.0. **Q5 RULED
2026-09-28 (STEPHEN: "Q5: A"): no inertia term in 6.0**; it is filed after v6.0.0 as PL-166. All of PL-160's owner
questions are now answered; what remains is the wheels-up re-run (t0 SRC_REV 28) and the feel on the floor.

**2026-09-28, Block A: the wheels-up half is CERTIFIED** (`analyses/bench/2026-09-28/blockA/BLOCK-A-EVALUATION.md`,
`debug_260928-113930.log`, t0 SRC_REV 28): R22-T0-RAMP-SHAPE, -REVERSE and -UNWIND PASS, every stop's largest step of
acceleration equal to the jerk (`jerk_pk,104`), the reversal `crossed,TRUE,stop_seen,FALSE`, STOPPLAN-C/-M PASS again.
PL-160 stays open only for the feel under load (the floor run).

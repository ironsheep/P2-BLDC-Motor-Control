# Findings audit — what was recorded and not acted on

**Opened 2026-09-17** at Stephen's direction, after the commutation discussion showed that a week-old
evaluation already answered the question being asked.

**STEPHEN 2026-09-17:** *"It seems like you've got enough test results, and now you've demonstrated that
you've ignored some of the findings. Maybe we should treat this as a class issue and audit all of your
test result findings, and see which ones we haven't paid attention to and which ones are beneficial."*

**The question this asks of every finding is TWO questions, and the second was never asked before:**

1. Was it acted on?
2. ⭐ **Does what has landed since make it actionable, or make its data worth more than when it was
   written?** A disposition of *do not apply* or *deferred* carries the conditions it was written under,
   and later work removes those conditions.

Doctrine overlay **P11** was written from this and states the rule: *a finding's value changes when the
system changes; the sweep is owed before a criterion, a run or a recommendation.*

---

## 0 · COVERAGE — read this first

⛔ **THIS AUDIT IS PARTIAL AND SAYS SO.** Recording coverage honestly is the point: a partial audit
presented as complete would repeat the failure it exists to correct.

| Document | Read | Represented below |
|---|---|---|
| `bench/2026-09-13/SCAN-RUN-4-EVALUATION.md` | full | yes |
| `bench/2026-09-14/SCAN-RUN-7-EVALUATION.md` | full | yes |
| `bench/2026-09-16/VISIT-3-RESULTS.md` | full | yes |
| `bench/2026-09-17/VISIT-4-RESULTS.md` | substantial | yes |
| `bench/2026-09-17/VISIT-5-RESULTS.md` | authored today | yes |
| `bench/2026-09-15/VISIT-2-RESULTS.md` | **sections 0-2 only** | partially |
| `DOCs/PUNCH-LIST.md` | substantial, not end to end | partially |
| `bench/2026-09-12/CHAR-RUN-EVALUATION.md` | **NOT READ** | no |
| `bench/2026-09-12/DETECT-A-EVALUATION.md` | **NOT READ** | no |
| `bench/2026-09-12/SCAN-ABORT-EVALUATION.md` | **NOT READ** | no |
| `bench/2026-09-12/SCAN-RUN-3-EVALUATION.md` | **NOT READ** | no |
| `bench/2026-09-13/SCAN-RUN-5-EVALUATION.md` | **NOT READ** | no |
| `bench/2026-09-14/VISIT-1-RESULTS.md` | **NOT READ** | no |
| `bench/2026-09-14/VISIT-1-SIGNOFF.md` | **NOT READ** | no |
| `bench/2026-09-15/VISIT-2-ATTENDED-RESULTS.md` | **NOT READ** | no |
| `DRIVER-AUDIT-2026-09-09.md` | **NOT READ** this session | no |
| `DRIVER-SAFETY-AND-CAPABILITY-STUDY-2026-09-09.md` | **NOT READ** this session | no |
| `BLDC-COMMUTATION-PRINCIPLES.md` | **NOT READ** this session | no |
| `BOARD-REVISION-FACTS.md` | **NOT READ** this session | no |
| `PL-44-ROOT-CAUSE-STUDY.md` | **NOT READ** | no |
| `user-report-2026-09-09-ANALYSIS.md` | **NOT READ** this session | no |
| `ATTENDED-UI-AUDIT-2026-09-15.md` | **NOT READ** | no |
| `BENCH-TEST-PLAN-2026-09-10.md` | **NOT READ** this session | no |

**14 of 22 documents are unread.** Everything below comes from the 8 that were read, so the list of
ignored findings is a LOWER BOUND.

---

## 1 · The class defect, stated

**Findings are filed and then never re-read.** The punch list and the evaluations are a filing system;
nothing sweeps them when something changes. Three distinct failure shapes, all observed today:

| Shape | What it looks like | Instance |
|---|---|---|
| **A. The blocker is removed and nobody returns** | A finding parked on a condition; later work removes the condition; the finding stays parked | The scan's half-speed legs failed **on faults**; the lag limiter now makes the driver **droop instead of faulting** |
| **B. The finding is fixed and the record never says so** | Later measurements close it; no one updates the entry | PL-55, the stop-current abort (§3.2) |
| **C. The data outlives the question and nobody asks the new question** | Measurements taken for one cell answer a later question completely | Scan runs 7 and 8 already answer the commutation question |

⛔ **And a fourth, demonstrated while writing this audit:** I asserted that scan v5 "was never built and
never ran". It ran at Visit 2 as **run 8**. **The record is now larger than I can hold, so any claim
about it must come from a read, not from memory.**

---

## 2 · ⭐ THE BIGGEST ITEM — the commutation scan is 80% done and stalled

**Where it lives:** `SCAN-RUN-7-EVALUATION.md` (2026-09-14, complete, 41 of 41 sign-off cells PASS) and
`VISIT-2-RESULTS.md` section 11 (run 8, 2026-09-15).

**What is already MEASURED, on both motors, and reproduced across two runs:**

| | LEFT | RIGHT | agreement |
|---|---|---|---|
| negative-increment minimum | +13.4° ± 0.5 | +13.7° ± 0.7 | **0.3°** |
| positive-increment minimum | −20.9° ± 0.7 | −22.3° ± 0.4 | **1.4°** |
| hall electrical zero | −3.8° ± 0.4 | −4.3° ± 0.4 | **0.5°** |

Run 8 reproduced the quarter-speed minima within 0.1–1.6°. The sweep step is 5°, so **the two motors
agree to better than the instrument's resolution.**

**What it says about the driver:** the defaults 43 / 317 are symmetric about 0°, but the hall zero is at
about −4°. That asymmetry IS the 2:1 current split measured at the defaults, three separate times. **At
the minima the ratio collapses to 0.93–1.29.**

**The candidate pair, already written down:** `offset_fwd ≈ 14°`, `offset_rev ≈ 338°`.

**What it would buy, at no load (DERIVED in that evaluation):** 86–92% less current at quarter speed,
92–97% at half speed. The left motor at half speed falls from 6.26 A to about 0.20 A.

**Why it says DO NOT APPLY, and this is the only thing standing in the way:** the half-speed
confirmation has never been demonstrated. In every half-speed leg the lowest current sat at the last
clean point **before a fault**, with nothing measured between it and the fault. The candidate sits
6.5–8.5° from a fault edge at quarter speed and an extrapolated 2.4–4.7° at half speed.

### ⭐ What changed since, and nobody went back

**Every half-speed leg failed on FAULTS.** Since run 8:

- **The lag limiter («#3558») makes the driver droop instead of faulting** — certified `RMPDROOP` PASS on
  both motors at Visit 4 **and** Visit 5.
- **The sense-zero calibration is fixed** — the right motor's zero fell from 71–76 mV to 0.2–1.8 mV, and
  Visit 5 measured 0.1–0.6 mV across four starts and 0.0–1.6 mV across five in the t0 tier.
- **The current scale is certified** — implied R-sense 149–162 against a 135–165 band.

**So the exact condition that prevented the half-speed measurement has been removed, and the scan has
not run since 15 September.** Visits 3, 4 and 5 did not carry it.

**This is the single highest-value unactioned item in the project.** It is one ~12-minute unattended
load, on an instrument that already works, against a question whose answer is 80% written.

⚠ **Not a proposal to apply the offsets.** The evaluation's disposition stands until the half-speed
minimum is measured with margin, and what margin is enough under load is Stephen's decision.

---

## 3 · Other findings that are unactioned or whose status is now wrong

### 3.1 PL-69 — illegal hall codes on the right motor at 200 MHz — OPEN, UNTOUCHED

`VISIT-3-RESULTS.md` section 1, filed 2026-09-16. MEASURED: `illegal_d 3` and `5` in two 1-second
windows on the RIGHT motor at **200 MHz only**; 0 at 270 and 300 MHz, 0 on the LEFT at all clocks, and
0 at every Visit 1 and Visit 2 hold.

- **The owner is the driver's hall sampling, not the instrument** — the instrument's independent hall
  count lost nothing.
- **It has had no attention since it was filed**, across three visits.
- ⛔ **It is shipping-relevant.** Visit 3 certifies clock independence and the documentation will tell a
  user they may run at 200, 270 or 300 MHz. At one of those three, one motor logged hall integrity
  errors. **A user running at 200 MHz is the case we have the least evidence for.**
- Visit 3 states plainly what it does NOT establish: one run, one motor, 8 events, possibly transient.
  **That is a reason to re-measure, not a reason to leave it.**

### 3.2 PL-55 — the stop-current abort — LOOKS FIXED, AND THE RECORD DOES NOT SAY SO

`VISIT-3-RESULTS.md` section 6 calls it *"the driver's largest open behaviour"*, scheduled by Stephen
for this release.

- **Visit 3, MEASURED:** every stop from 75% tripped the harness's 10 A abort, all four motor/sign
  combinations.
- **Visit 4, MEASURED:** 20 stop trials at the same ±110_250_000 (75%), `stop_pk_mV` **971–1 055**
  against a 1 500 mV abort — flat to ±4%, and the abort never approached.
- **Visit 5, MEASURED:** `STOPCUR` PASS on both motors.

**DERIVED: «#3558»'s feed-forward duty ceiling closed it.** Nothing in the punch list or the visit
reports says so, and PL-55 is still described as the largest open behaviour. **Status to be corrected
after a direct read of the PL-55 entry** — this audit has not read it end to end.

### 3.3 "Float may be a brake" — an unverified hardware fact under a documented API

`VISIT-2-RESULTS.md` section 0. MEASURED: `emergencyCutoff()` stops a half-speed wheel **within one
tick**, while `stop()` (which releases the pins) lets it coast 38–48 ticks.

> *"The source suggests the driver's 'drive off' state holds all three low-side FETs on, which brakes
> the motor. That rests on one unverified hardware fact. **If it holds, 'float' is also that brake, and
> so is every fault.**"*

⛔ **If true, this contradicts a documented public contract.** `holdAtStop(FALSE)` is documented as
coast. The user-visible behaviour, the release notes and `DRIVE-OBJECTS.md` all rest on FLOAT and BRAKE
being different things.

> ## ⭐ SETTLED FROM SOURCE, 2026-09-17, same day. The hypothesis was right, and it is worse.
>
> `pwmn` carries `P_INVERT_OUTPUT` and is written to the three LOW-side pins; `pwmt` without it goes to
> the high side. So the drive-off action `wypin #0, drive_pins` leaves the high side low (FETs off) and
> the **low side HIGH — all three low-side FETs on, phases shorted, a dynamic brake.** The code comment
> "all drive pins low" describes the register value, not the pin state, and is wrong.
>
> **Three behaviours, not two:** `holdAtStop(FALSE)` leaves the PWM ENABLED at `duty_min` — a powered
> hold, not a coast; `holdAtStop(TRUE)` shorts the phases; only `stop()` truly floats. **And every fault
> and e-stop takes the brake path regardless of `holdAtStop()`.** That is exactly Visit 2's 1-tick
> e-stop against a 38-48 tick `stop()` coast.
>
> **Filed as PL-89**, with the one unestablished link (whether the board's gate driver adds another
> inversion) and Stephen's hand test, with predictions written so the test can fail.
>
> ⚠ **This is the audit paying for itself on its first day**: a finding parked on "one unverified
> hardware fact" for two days, where the verification was a source read.

### 3.4 The e-stop hold in passes — never measured

`VISIT-3-RESULTS.md` section 4.3. The motor object's sense task releases an e-stop after
`ESTOP_HOLD_PASSES`, and that path is only reached by part A's LIVE segment — so no load has ever
exercised it. The report is explicit: *"equivalent by arithmetic, not by measurement."*

### 3.5 Board-to-board phase-sense difference

`VISIT-2-RESULTS.md` section 0: the LEFT board's `ph_x10` reading sags 2.4–2.8% under load; the RIGHT
board's moves 0.2–0.3% at the same currents. Recorded, never followed up. Relevance unknown — it may
matter to any future use of the phase channels.

---

## 4 · What to do with this

**Nothing here is scheduled by this audit** (doctrine overlay P5: what is in a release or a sprint is
Stephen's decision). Ranked by what it would buy:

| # | Item | Cost | What it buys |
|---|---|---|---|
| 1 | **Re-run the commutation scan** | one ~12 min unattended load, plus a read-through of the scan binary against the 6.0.0 driver | The half-speed confirmation that is the only thing between us and a candidate offset pair worth 86–97% of the no-load current |
| 2 | **Settle "is float actually a brake"** | a source and schematic read, no bench time | Whether a documented public contract is true |
| 3 | **Re-measure PL-69's hall codes at 200 MHz** | rides any load at that clock | Whether we can honestly tell a user 200 MHz is supported |
| 4 | **Correct PL-55's status** | a read | The record stops describing a closed behaviour as the largest open one |
| 5 | **Finish this audit** | reading 14 documents | The lower bound above becomes a real number |

---

## Revision history

- **2026-09-17** — opened. Partial: 8 of 22 documents read. The scan stall, PL-69, PL-55's status, the
  float/brake question, the e-stop hold and the board phase-sense difference are the findings surfaced
  so far.

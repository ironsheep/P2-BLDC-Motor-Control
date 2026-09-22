# Processing a set of bench-run logs

**What this is.** The same nine steps, every time a set of logs comes back from the rig. Derived
2026-09-22 from the five most recent passes — `SCAN-RUN-7`, `VISIT-7B`, `SHAKEDOWN`,
`SCAN-SELFLOCATE`, `SCAN-GUARD` — which had converged on this shape without it being written down.
Every rule below is here because skipping it cost something real; the citation says what.

**Scope.** This covers what happens *after* the logs exist. What happens before is the run sheet
(seven attributes, cells each confirmed able to fail) — see any `VISIT-*-RUNSHEET.md`.

**Two standing constraints, from Stephen:**

- **One analysis report per set of logs.** *"all we need to do is analyze the logs and write an
  analysis report every time we get a set of logs back. Nothing else."* (2026-09-15) No collation
  script, no manifest, no sign-off sheet.
- **Read the logs yourself.** Never build tooling that interprets them. A task whose deliverable is a
  tool for reading logs is the tell (doctrine P10).

---

## The nine steps

### 1 · Park the logs and record the identity of what ran

Copy into `DOCs/analyses/bench/<YYYY-MM-DD>/`. The report's first block names, for each log: the
**log filename**, the **binary name and byte size**, its **rebuild timestamp**, and the **source
commit**.

> *Why:* the byte size and rebuild time are what distinguish a fresh binary from a stale one when the
> banner alone looks right.

### 2 · Banner check — before reading anything else

Verify `src_rev`, `fmt`, every build flag (`wd_selftest`, `droop_selftest`, …), and the compiled-in
constants the run is *about* (offsets in `BM-RUNG`, thresholds in `BS-LIMITS`).

⛔ **If it does not match the run sheet, STOP.** The wrong binary is on the board and nothing below
means anything.

> *Why:* **a load that re-exercises an unchanged binary certifies nothing.** `SCAN-GUARD` verified
> `point_abort_ceil_mV,1_200` was present *before* concluding the fix had failed — otherwise "the fix
> didn't work" and "the fix wasn't in the image" are indistinguishable.

### 3 · State the outcome in one line

From `BS-END`: `exit`, `reason`, `elapsed_s`, `points`, and the **per-motor progress** counts
(`left_rungs` / `right_rungs` against `rungs_planned`).

⚠ On an aborted run the `*_done` booleans are both FALSE and say nothing about how far it got. Read
the counts.

### 4 · If it aborted — root cause first, before any measurement

Find why it died, from the **primary log**, before reading anything built on top of it.

> *Why:* `SCAN-GUARD` and `SCAN-SELFLOCATE` both aborted at the same point at the same second. The
> value came from the cause (a 20 ms fatal guard racing a 200 ms survivable one), not from the
> numbers around it.

### 5 · Give every declared cell a verdict

Every cell in `SIGNOFF-DECL` gets `PASS` / `FAIL` / `NOMEAS` from the log.

- **`NOMEAS` is not `PASS`.** "The condition did not arise" is an honest result and is *not* evidence
  the mechanism works.
- **A cell declared but never emitted is itself a finding.**
- **A cell that could not have failed on this run is coverage, not evidence** — say so, and count it
  as neither. (PL-98 is two cells in exactly that state.)

### 6 · Report the measurement against the table fixed *before* the run

Quote log lines; do not paraphrase them. Judge against the expectations and falsifiers the run sheet
declared in advance, and **never renegotiate them after seeing the result** (D2).

### 7 · Findings register — every finding gets an id and a disposition

| Disposition | Means |
|---|---|
| ⛔ **FIX** | A change to make now, named specifically. Becomes a task or a commit in this session. |
| **Closed** | Confirmed working; the question is retired. |
| **Watch** | Real but not yet actionable. Names what would make it actionable. |
| **Unvalidated** | The mechanism has not been exercised. **Do not claim it.** |
| **Punch list** | Deferred with evidence → a real `PL-N` entry. |

### 8 · "What is NOT established" — its own section, always

List explicitly: everything `NOMEAS`; anything about a motor or leg that never ran; every run-sheet
question this run did not answer; and any measurement whose negative case has never been seen.

> *Why:* this is the section that stops a sheet reading as though minima had been demonstrated when
> they had not — run 7's failure, which is why the section exists.

### 9 · Discharge every disposition **in the same session**

- **FIX** → a task or a commit, now. *Findings are acted on before the next visit and narrow it.*
- **Punch list** → **write the `PL-N` entry.** ⛔ **A deferral that names no PL number has not
  happened.** Naming the destination is not arriving at it.
- **Watch** → recorded where the next run's reader will see it.
- Then update the plan/tasks and the sprint resume key, and **commit the evaluation together with its
  logs**.

> *Why:* 2026-09-22 — two instrument defects were correctly deferred, announced as "on the punch
> list" in the breadcrumb, the run sheet and to Stephen, and **never written down**. The breadcrumb is
> deleted at task close, so the only record would have vanished.

---

## Operator observations

- **Ask for observations, never verdicts.**
- **Never ask for an observation the run sheet did not ask for in advance.** An event nobody was told
  to watch for is a gap to design out of the next run, not a question for Stephen.
  *(2026-09-15: "you are asking me to report observations you never asked me to make".)*
- An observation that arrives anyway is a **finding to chase in the logs**, not a verdict. Visit 7b's
  ramp-start thump was resolved from the logs, not from the report of it.

---

## The report's standard shape

```
Title — what ran, when, and the outcome in the title itself
  Log / binary / size / rebuild time / source commit
  Outcome: the BS-END line
  Banner check, verified first
§1  Root cause            (aborted runs only)
§2… The measurement, quoted from log lines
§n  What it means for the driver
§n+1 Findings register     (id + disposition)
§n+2 What is NOT established
```

**Naming:** `DOCs/analyses/bench/<date>/<WHAT-RAN>-EVALUATION.md`. Put the outcome in the **title** —
`"… 2026-09-21 20:09, ABORTED IDENTICALLY"` tells a later reader more than the filename can.

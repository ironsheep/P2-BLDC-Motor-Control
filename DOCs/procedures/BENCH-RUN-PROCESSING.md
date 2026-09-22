# Processing a set of bench-run logs

**What this is.** The same steps, every time a set of logs comes back from the rig. Derived
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

**The report has two layers and both are required.** Steps 1–8 are the **analysis** — what the logs
say. Steps 9–10 are the **outcome** — what it changes, written so Stephen can read the result without
reading the analysis. The outcome layer is the point of the exercise; the analysis is what earns it.

---

## The ten steps

### 0 · List everything the governing documents require — before opening a log

Compile the full action list first: this procedure, the `p2-dev-cycle` and `task-execution` overlays,
`dual-agent-handoff` (§5a–§9), *the bench visit*, the run sheet's own falsifiers and carried-in items,
and the open tasks the pass should discharge. Show it, then start step 1. STEPHEN 2026-09-22, stopping a
read already under way: *"you wrote the skill overlay to identify everything you should do when
processing these results do not process them until you have this list."*

> *Why:* a log read before the list shapes the list. The items the list exists to guarantee —
> discharging dispositions, correcting aged records, closing tasks — are exactly the ones a
> results-first read forgets.

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

### 8a · Tell Stephen the findings and the planned actions — BEFORE acting on them

When steps 1–8 are done, post the findings and the actions they lead to, in plain words, **then** start
steps 9–10. He reads while the work proceeds, and anything he would redirect is caught before it is
built rather than after. STEPHEN 2026-09-22: *"summarize the findings and planned actions to me before
you start work on it so i can be reading while you are working."*

This is not a request for approval. It does not wait for an answer; it makes the plan visible at the
moment it is formed.

### 9 · Close the loop — the four-part outcome, and this is what the run was *for*

⭐ **This is the layer Stephen reads.** Four parts, every run, none of them optional. Each answers a
different question and each feeds a different front of the outer loop
(`.claude/skills/p2-dev-cycle/project-overlay.md`).

| Part | The question it answers | Front it feeds |
|---|---|---|
| **1 · The learnings** | What do we now know that we did not know before the run? | *information* |
| **2a · What it means for the driver — what it now DOES** | Which driver changes do these answers license, and which do they **forbid**? | *completion* |
| **2b · What it means for the driver — what it now KNOWS** | Does the drive itself gain a sensor it can act on, or did this only teach the harness? | *robustness* |
| **3 · What it changes about the next run** | What should the next pass carry, drop, or re-centre because of this? | *information* + *completion* |
| **4 · Questions left open** | What still gates a decision, and what would settle it? | names the next question |

⛔ **2a AND 2b ARE SEPARATE, AND BUNDLING THEM IS HOW FRONT 3 GOES MISSING.** *Does the driver do more
of what it must* and *does the driver now know something it did not* are different questions, and a
run can advance the first while the second stays flat. That is the documented failure: `follow_pct`
was built so the **instrument** could tell the drive was not following, while the **drive** stayed
blind to it — front 1 advanced, front 3 did not, and nothing in the write-up made that visible
because the two lived in one paragraph.

### Every run is checked against all three fronts — but need not advance all three

⚠ **Requiring every run to advance every front would manufacture driver changes the evidence does not
license** — the exact trap 2a's *does NOT license* paragraph exists to prevent.

So the rule is about **silence, not motion**: each of the three fronts is **named explicitly** in the
outcome and is either *advanced* (with the change named) or *recorded as not advanced, with why*. An
honest **"this run moved nothing on front 3, because it certified a harness mechanism and integrated
no sensor"** is a correct outcome. A front that simply **is not mentioned** is the failure — that is
how a pass advances one front and nobody notices the other two did not move.

**Close the outcome with the ledger reading, before and after**, so the claim is computed rather than
asserted (`.claude/skills/task-execution/project-overlay.md`):

```
FRONTS  (after this run)
  completion   driver last changed <N> commits ago
  information  <K> loads ready and unrun: <names>
  robustness   sensors the DRIVER acts on: halls <y/n> current <y/n> back-EMF <y/n> follow <y/n>
```

⛔ Read `robustness` from what the **driver declares** — a `PUB`, an addressed `VAR`, a named `CON` —
never a word grep. The ledger's first run reported follow-detection present when all five matches
were the word *follow* in prose comments. A word match lies in the one direction that matters.

**Part 1 goes at the TOP of the report as a `## Headline` table** — one row per learning, claim on the
left, the number that carries it on the right. **It is written last and placed first**, because it
cannot be written until the analysis is done but it is the first thing read.

**Part 2 is THE CONTINUOUS HARVEST and it is not a phase at the end.** With the answers now in hand,
name every driver change they inform — and build them. State plainly what the run **confirmed** as
well as what it broke: *"the shipped pair is right, to about 1°, at quarter speed"* is a result and
deserves saying. Then the ⚠ **what this does NOT license** paragraph, which is the part that stops a
measured fact being spent on a change it does not support.

**Part 3 designs the next pass, here, while the evidence is fresh.** The worked instance: *"the
cheapest way to get a third point is the existing half-speed rung… re-centring its confirm set on its
own extrapolated optimum is a one-constant change and would likely convert four POOR fits into four
usable minima."* That is the next run's load, specified in the report that justified it — and it is
what makes *every bench pass do two jobs*: certify what was built since the last pass, and measure
for the answers still needed.

⭐ **Part 3 IS the next run sheet's draft load list — it carries forward, it is not re-decided.** The
next sheet inherits these loads and their justification; what it still owns is the seven attributes,
the cells, and confirming each can fail. Re-deriving the loads from scratch would discard the one
moment when the evidence and the reasoning were both in hand. **A load may still be dropped at the
next sheet — but the sheet says why it was dropped**, so a load cannot vanish by being forgotten
between the report that called for it and the pass that should have carried it.

**Part 4 is not the same as "What is NOT established" (§8).** §8 is a fence around this run's claims.
Part 4 is forward-looking: the open question, what would settle it, and which task owns it.

### 10 · Discharge every disposition **in the same session**

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
§1   HEADLINE                     <- part 1. Written last, placed first.
§2   Root cause                   (aborted runs only)
§3…  The measurement, quoted from log lines
§n   What this means for the driver   <- 2a what it DOES + 2b what it KNOWS,
                                         with the "does NOT license" paragraph
§n+1 What this changes about the next run  <- part 3
§n+2 Findings register            (id + disposition)
§n+3 What is NOT established      (a fence around THIS run)
§n+4 Questions left open          <- part 4 (forward-looking; may merge with §n+1)
§n+5 FRONTS ledger, after         <- computed; every front named, advanced or not
```

**A reader who stops after §1 should already have the outcome.** A reader who stops after the driver
and next-run sections should know everything that changes. The rest is the evidence for it.

**Naming:** `DOCs/analyses/bench/<date>/<WHAT-RAN>-EVALUATION.md`. Put the outcome in the **title** —
`"… 2026-09-21 20:09, ABORTED IDENTICALLY"` tells a later reader more than the filename can.

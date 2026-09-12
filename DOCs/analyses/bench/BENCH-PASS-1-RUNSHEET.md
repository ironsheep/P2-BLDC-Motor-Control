# Bench Pass 1 — run sheet

**Task:** «#3498» · **Authoring side:** Claude (this session) · **Executing side:** Stephen
**Source SHA to run** (scoped to `src/`): **`441c9d9`** — verify before starting:

```bash
git log --oneline -1 -- src/          # must print 441c9d9 Add the early motor characterisation binary
```

Protocol: `central:dual-agent-handoff`. This document is **current-state only** — finished steps
collapse to a result line. Observations go to `BENCH-OBSERVATIONS.md`, never here.

---

## Two facts corrected 2026-09-11, before this sheet was first run

**The Rev A boards are NOT one-shot.** The constraint is narrower and ordinary: **no motor
movement on the A boards.** They can be re-run freely. An earlier draft of this sheet — and the
sprint plan behind it — treated them as a single unrepeatable opportunity, which shaped an
ordering argument that is no longer needed. If bench time runs short, **the A steps can simply be
done another day.**

**The rail on/off axis is UNREACHABLE on this rig, not merely unrun.** The P2 is powered from the
pack: rail off means no P2, so a rail-off run cannot exist. Every step below is therefore a
**rail-ON** run, and the 2×2×2 matrix is really 2×2×1.

That is itself a finding for «#3500»: the hypothesis that Rev B detection depends on the
INA180B2 output being actively driven **cannot be tested by removing rail power** on this
hardware. It needs a different experiment — or a board modification — and that should be said
plainly in the findings rather than left looking untested.

---

## Before you start

**Panic procedure, and it is the only one: PHYSICAL BATTERY DISCONNECT.**
`emergencyCutoff()` self-cancels in about 250 ms (finding S-4) and is **not** a panic button.
Nothing in this pass calls it.

**The pack is connected for every step**, because the P2 needs it. The motor rail is therefore
live throughout. What keeps the passive steps safe is not a dead rail — it is that those builds
contain **no driver code in the image at all**, so no cog can be started to drive anything.

**A log with no config banner is VOID.** `pnut-ts` silently ignores an unknown `-D` — exit 0,
binary written, no warning — so a typo falls through to the regular user config and the harness
measures the wrong pin group while producing entirely plausible numbers. Every step says what the
banner must read. **If it does not read that, stop and re-run.**

**Run everything through `tools/bench-run.sh <tier>`.** It names the `-D` options once so they
cannot be mistyped at the bench — which matters because `pnut-ts` ignores an unknown `-D`
*silently*, turning a typo into a plausible wrong run rather than an error. It still echoes both
commands verbatim with a `+ ` prefix before running them, so you can always see and replay exactly
what ran. Tiers: `detect`, `detect-lib`, `detect-phase2`, `char`, `char-nopanel`, `t0`.

**Logs stay where the tool puts them:** `src/logs/debug_<date>-<time>.log`. Curated **copies** go
to `DOCs/analyses/bench/2026-09-11/` **keeping the `.log` extension** — `*.txt` is gitignored and
a curated log saved as `.txt` silently vanishes from git.

---

## Ordering

**One board swap, B rig complete first, A rig last.** B is the development rig and the only one
that may turn a motor, so everything needing motion happens there; A is passive-only and, being
repeatable, is the safe thing to leave until last or defer entirely.

Within each rig: passive sweeps with motors connected (the hall bits in `pre` then corroborate
that the rail is powered, for free), then unplug for the driver-cog probe.

---

## Step 1 — B boards, passive sweep, default build · motors connected

```bash
tools/bench-run.sh detect
```

- Banner: `BD-CFG,cfg_id,BENCH` and `BD-BUILD,...,phase2_compiled,0,lib_linked,0`
- Expect **384** `BD-REP` — `grep -c '^BD-REP' <log>`
- Expect `BD-CLK,...,match,1`

**Result:** ______ · **Log:** ______________ · pass / fail

---

## Step 2 — B boards, passive sweep + library cross-check · motors connected

```bash
tools/bench-run.sh detect-lib
```

- Banner: `lib_linked,1`, still `phase2_compiled,0` — **no driver cog starts**
- Still **384** `BD-REP`
- **The line that matters:** `grep -o 'agree,[01A-Z]*' <log> | sort | uniq -c`
- **Any `agree,0` is a finding, not something to work around** — the replica and the library
  disagree about the same board in the same second, and the whole `vrd` column is void. Capture
  it and tell me before going further.

**Result:** ______ · **Log:** ______________ · pass / fail

---

## Step 3 — ⚠ UNPLUG THE B MOTORS ⚠ the poisoning probe

**Precondition: motors physically unplugged from the B boards.** With no motor connected there is
no current path whatever the output stage does. This build starts a real driver cog at commanded
zero.

```bash
tools/bench-run.sh detect-phase2
```

- Banner: `phase2_compiled,1` **and** `BD-GATE,mark,build,answer,COMPILED` — the same fact from
  two places; if they disagree the run is void
- Expect **1168** `BD-REP`
- This separates *"the threshold is wrong"* from *"`stop()` clears only the top 8 pins and poisons
  the next read"* — the two want opposite fixes

**Result:** ______ · **Log:** ______________ · pass / fail

---

## Step 4 — B boards, characterisation run · MOTORS RECONNECTED

**Say the pack voltage and write it at the top of your sheet.** Without it the S-3 ratio cannot
be computed afterward and the run is worth much less.

```bash
tools/bench-run.sh char          # or: char-nopanel, if the PLOT window misbehaves
```

A **PLOT window** opens. At each hold: read the meter, write the row, then click **GO AHEAD** —
or press **G** with the window focused. The button is inert until the 25-second dwell floor has
elapsed from steady state; the counter shows it. An early click flashes the counter white and is
logged, not obeyed.

**Nine holds are compiled in** (`HOLD_LAST = HOLD_R_REV_HALF`). **For the short version** — five
holds, the essential set — change `HOLD_LAST` to `HOLD_R_REV_QTR` and rebuild. Your call on bench
time; the half-speed rung only confirms that current scales with load.

| # | Hold | Amps | Notes |
|---|---|---|---|
| 0 | quiescent zero | | V ___ A ___ W ___ |
| 1 | LEFT forward ¼ | | |
| 2 | LEFT reverse ¼ | | |
| 3 | RIGHT forward ¼ | | |
| 4 | RIGHT reverse ¼ | | |
| 5 | LEFT forward ½ | | |
| 6 | LEFT reverse ½ | | |
| 7 | RIGHT forward ½ | | |
| 8 | RIGHT reverse ½ | | |

**Pack voltage: __________**

**Result:** ______ · **Log:** ______________ · pass / fail

### While the motors are turning — three meter questions

1. Does **Ah/Wh** reset with the peaks, or separately? ______
2. **Quiescent zero** — V, A, W with the rail on and motors stopped? ______
3. **Does Ap LATCH after the current drops, or decay?** ______

Question 3 can change a design decision: if Ap decays, T1-7's Ap-for-fault-current technique
collapses and that measurement depends on the section 2A front end instead.

Settled, do not re-derive: the meter cycles **five** screens (Ah, Wh, Ap, Vm, Wp) at ~4 s each,
~20 s per rotation; A/V/W are not in that cycle. Peaks must be **read before cycling**.

---

## Step 5 — swap to the A boards · passive sweep · NO MOTOR MOVEMENT

```bash
tools/bench-run.sh detect-lib
```

Same tier as step 2, so the same binary is rebuilt from the same source — that is what makes the
two logs diffable.

- Banner: `cfg_id,BENCH`, `lib_linked,1`, `phase2_compiled,0`
- Expect **384** `BD-REP` — this log is meant to diff line-for-line against step 2's

**Result:** ______ · **Log:** ______________ · pass / fail

---

## Step 6 — ⚠ UNPLUG THE A MOTORS ⚠ poisoning probe on Rev A

Now worth doing, because the A boards are repeatable. It gives the A/B diff a second dimension
rather than one.

```bash
tools/bench-run.sh detect-phase2
```

- Banner: `phase2_compiled,1`, `BD-GATE,...,COMPILED`; expect **1168** `BD-REP`
- Diffs against step 3

**Result:** ______ · **Log:** ______________ · pass / fail

---

## Hard stops — stop the step and hand back

Per `dual-agent-handoff` §4. Any of these stops the binary it belongs to; steps that do not depend
on it stay runnable, and you cross back when nothing runnable remains.

- **No config banner, `cfg_id` ≠ `BENCH`, or `BD-CLK,match,0`** — void, not suspect
- **Any `agree,0`** — the replica disagrees with the library
- **`BD-GATE` and `phase2_compiled` disagreeing** — two records of one fact, drifted
- **A `BD-REP` count that is not 384 / 1168** — truncated run
- **A driver fault during step 4** — the hold ends itself with `result,FAULT`; that reading is void
- **Anything that would need a source edit to proceed** — hand back; I turn it into a build option
- **Any motor movement on the A boards** — the one hard constraint there

---

## Open questions this pass is trying to settle

Stated as questions deliberately, not predictions — a prediction written here contaminates the
answer.

1. Is the 500-read `pinSum` threshold clock-dependent, and is that the whole of the detection
   defect? `fltix` is the clock-independent measurement that answers it.
2. Does a driver cog that has run and stopped change what the next detection read sees?
3. What does a genuinely empty pin group read, and does it land inside the documented Rev B band?
4. Does the A/B difference appear where the circuit says it should?
5. What is the ratio of raw `sense_i_mV` to meter amps, and is it near 6136?
6. Is there a forward-versus-reverse asymmetry at matched commanded rate?
7. Is the current channel alive and load-responsive at all?

**Not answerable by this pass, and it is worth stating so it is not silently assumed:** whether
Rev B detection depends on the INA180B2 being powered. Rail-off is unreachable here — no pack, no
P2. That question needs a different experiment.

# Bench Pass 1 — run sheet

**Task:** «#3498» · **Authoring side:** Claude (this session) · **Executing side:** Stephen
**Source SHA to run** (scoped to `src/`): **`441c9d9`** — verify before starting:

```bash
git log --oneline -1 -- src/          # must print 441c9d9 Add the early motor characterisation binary
```

Protocol: `central:dual-agent-handoff`. This document is **current-state only** — finished steps
collapse to a result line. Observations go to `BENCH-OBSERVATIONS.md`, never here.

---

## Before you start

**Panic procedure, and it is the only one: PHYSICAL BATTERY DISCONNECT.**
`emergencyCutoff()` self-cancels in about 250 ms (finding S-4) and is **not** a panic button.
Nothing in this pass calls it.

**A log with no config banner is VOID.** `pnut-ts` silently ignores an unknown `-D` — exit 0,
binary written, no warning — so a typo in `-D BENCH_CFG` falls through to the regular user config
and the harness measures the wrong pin group while producing entirely plausible numbers. Every
step below says what the banner must read. **If it does not read that, stop and re-run.**

**`bench-run.sh` only knows the `t0` tier.** These two binaries are run by hand, two commands
each, exactly as the script would have echoed them. That is deliberate — no new wrapper before a
bench pass.

**Logs stay where the tool puts them.** `pnut-term-ts` writes `src/logs/debug_<date>-<time>.log`.
Curated **copies** go to `DOCs/analyses/bench/2026-09-11/` **keeping the `.log` extension** —
`*.txt` is gitignored and a curated log saved as `.txt` silently vanishes from git.

---

## Ordering, and why it is this order

1. **B boards first, A boards second.** The A boards are one-shot. Running the binary on the B
   rig first proves the instrument works before the single A opportunity is spent.
2. **`-D DETECT_LIB` on B before A.** That build carries `agree` — the check that our replica of
   `getBoardType()` matches the real library. Confirm the replica is faithful on repeatable
   hardware *before* relying on it for the run that cannot be repeated.
3. **All motor-unplugged work together**, so there is one unplug and one replug.
4. **Characterisation last.** It is the longest step, it needs the pack connected and wheels
   turning, and if anything goes wrong earlier the detection data is already captured.

---

## Step 1 — B boards, passive sweep, default build

Motors may stay connected. Nothing moves; this build contains no driver code at all.

```bash
cd src
/Applications/pnut_ts/pnut-ts -l -d -D BENCH_CFG test_bench_detect.spin2
pnut-term-ts -r test_bench_detect.bin --console-mode --exit-on-end-session
```

- Banner must read `BD-CFG,cfg_id,BENCH` and `BD-BUILD,...,phase2_compiled,0,lib_linked,0`
- Expect **384** `BD-REP` records — `grep -c '^BD-REP' <log>`
- Expect `BD-CLK,...,match,1`

**Result:** ______ · **Log:** ______________ · pass / fail

---

## Step 2 — B boards, passive sweep + library cross-check

```bash
/Applications/pnut_ts/pnut-ts -l -d -D BENCH_CFG -D DETECT_LIB test_bench_detect.spin2
pnut-term-ts -r test_bench_detect.bin --console-mode --exit-on-end-session
```

- Banner must read `lib_linked,1` and still `phase2_compiled,0` — **no driver cog starts**
- Still **384** `BD-REP`
- **The line that matters:** every `BD-CELL` carries `agree,1` or `agree,0`.
  `grep -o 'agree,[01N][A]*' <log> | sort | uniq -c`
- **Any `agree,0` is a finding, not a failure to work around** — it means the replica and the
  library disagree on the same board in the same second, and the whole `vrd` column is void.
  Capture it and tell me; do not proceed to step 3.

**Result:** ______ · **Log:** ______________ · pass / fail

---

## Step 3 — ⚠ A BOARDS, ONE-SHOT, NO MOTION ⚠

**Same binary as step 2, unchanged. Do not rebuild. Do not run anything else on the A boards.**

Connect the A boards, then:

```bash
pnut-term-ts -r test_bench_detect.bin --console-mode --exit-on-end-session
```

- Banner must read `cfg_id,BENCH`, `lib_linked,1`, `phase2_compiled,0`
- Expect **384** `BD-REP`, same as step 2 — the two logs are meant to diff line-for-line
- Copy this log to `DOCs/analyses/bench/2026-09-11/` **immediately**, before anything else

**Result:** ______ · **Log:** ______________ · pass / fail

---

## Step 4 — ⚠ MOTORS PHYSICALLY UNPLUGGED ⚠ B boards, the poisoning probe

**Precondition: the motors must be physically unplugged from the B boards.** With no motor
connected there is no current path whatever the output stage does. This build starts a real
driver cog at commanded zero.

```bash
/Applications/pnut_ts/pnut-ts -l -d -D BENCH_CFG -D DETECT_PHASE2 test_bench_detect.spin2
pnut-term-ts -r test_bench_detect.bin --console-mode --exit-on-end-session
```

- Banner must read `phase2_compiled,1` **and** `BD-GATE,mark,build,answer,COMPILED` — those two
  carry the same fact from two places and must agree
- Expect **1168** `BD-REP`
- This is the step that separates *"the threshold is wrong"* from *"`stop()` clears only the top
  8 pins and poisons the next read"* — the two want opposite fixes

**Result:** ______ · **Log:** ______________ · pass / fail

---

## Step 5 — B boards, characterisation run

**Reconnect the motors. Pack connected.** Say the pack voltage out loud and write it at the top
of your sheet — without it the S-3 ratio cannot be computed afterward and the run is worth much
less.

```bash
/Applications/pnut_ts/pnut-ts -l -d -D BENCH_CFG test_bench_char.spin2
pnut-term-ts -r test_bench_char.bin --console-mode --exit-on-end-session
```

A **PLOT window** opens. At each hold: read the meter, write the row, then click **GO AHEAD** —
or press **G** with the window focused. The button is inert until the 25-second dwell floor has
elapsed from steady state; the counter shows it. An early click flashes the counter white and is
logged, not obeyed.

**Nine holds are compiled in** (`HOLD_LAST = HOLD_R_REV_HALF`) — quiescent zero, four at quarter
speed, four at half speed. That is roughly 4 minutes of dwell alone plus your reading time. **If
you want the short version**, change `HOLD_LAST` to `HOLD_R_REV_QTR` in `src/test_bench_char.spin2`
and rebuild — five holds, the essential set. Your call on bench time; the half-speed rung only
confirms that current scales with load.

### Reading sheet

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

---

## Step 6 — the three meter questions

While the motors are turning, these cost no extra setup:

1. Does **Ah/Wh** reset with the peaks, or separately? ______
2. What is the **quiescent zero** — V, A, W with the rail on and motors stopped? ______
3. **Does Ap LATCH after the current drops, or decay?** ______

Question 3 can change a design decision: if Ap decays, T1-7's Ap-for-fault-current technique
collapses and that measurement depends on the section 2A front end instead. Say so rather than
working around it.

Already settled, do not re-derive: the meter cycles **five** screens (Ah, Wh, Ap, Vm, Wp) at ~4 s
each, ~20 s per rotation; A/V/W are not in that cycle. Peaks must be **read before cycling**.

---

## Hard stops — stop the step and hand back

Per `dual-agent-handoff` §4. Any of these stops the binary it belongs to; steps that do not
depend on it stay runnable, and you cross back when nothing runnable remains.

- **No config banner, or `cfg_id` ≠ `BENCH`, or `BD-CLK,match,0`** — the run is void, not suspect
- **Any `agree,0`** in step 2 or 3 — the replica disagrees with the library
- **`BD-GATE` and `BD-BUILD,phase2_compiled` disagreeing** — two records of one fact, drifted
- **A `BD-REP` count that is not 384 / 1168** — the run was truncated
- **A driver fault during step 5** — the hold ends itself with `result,FAULT`; the reading is void
- **Anything that would need a source edit to proceed** — hand back; I turn it into a build option
- **Anything irreversible on the A boards** — they are one-shot and cannot be recaptured

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

---

## ⛔ One thing I need from you before step 1, because it changes this sheet

The sweep design has a **rail on / rail off** axis — the idea being that on Rev B the sense node
is the INA180B2 *output*, and a powered INA180 actively drives it, so there may be no capacitor
discharge to measure at all. That would mean detection depends on whether the board's rail is
powered, which `getBoardType()` neither knows nor checks.

**I cannot tell from the repo whether a rail-off run is even possible.** Two of your own notes
disagree: the doctrine overlay says the P2 Edge is USB-powered and takes a RAM download any time,
while the meter notes say the P2 does not survive a pack disconnect because it is powered from
the pack. If the second is right for this rig, "rail off" means the P2 is off and the axis cannot
be run at all — in which case every step above is a rail-ON run and should be labelled as such.

The sheet above assumes **rail ON throughout** and does not attempt the axis. Tell me which it
is and I will either add the rail-off steps or write the axis off as unreachable on this rig and
say so in the findings.

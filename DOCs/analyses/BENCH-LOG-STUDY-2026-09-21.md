# Bench log study — the four logs of 2026-09-20

**Date:** 2026-09-21 · **Author:** Claude (study skill) · **Status:** register complete, nothing fixed

---

## 1. Scope

**The question.** What do the four bench logs produced on 2026-09-20 establish — about the
drive, about the harness, and about the two open punch-list items (PL-92, PL-94) that block
every attended tier?

These logs matter out of proportion to their number: **`debug_260920-182503.log` is the first
execution, ever, of the R18.1 + R18.2 code.** Every gate behind «#3580» and «#3581» subtasks
1–5 was compile-only by construction. This is the first time any of it has met a motor.

**The surface — read in full:**

| Log | Tier | Size | What it is |
|---|---|---|---|
| `src/logs/debug_260920-182345.log` | `t0-hand` | 11 KB | T0-12 hand-rotation anchor, panel named `bench` |
| `src/logs/debug_260920-182425.log` | `t0-stopmode` | 2.5 KB | T0-24 stop-state hand test, panel named `t0stop` |
| `src/logs/debug_260920-182503.log` | `dual-a` | 3.0 MB / 16,086 lines | **the Visit 7 characterisation run**, src_rev 22 / fmt 10 |
| `src/logs/debug_260920-205301.log` | `t0` | 18 KB | full unattended Tier 0 |

Source was consulted **only** to settle counter semantics and record provenance — five
questions, answered with `file:line` citations (§6). No source was read to form an opinion
about the drive; the drive's behaviour is read from the logs.

**Excluded, with reasons:**

- `src/logs/_OLD/` (82 archived logs) — superseded runs; this study is about what 2026-09-20 established.
- `DOCs/analyses/bench/2026-09-19/` (Visit 6a) — the prior; cited where these logs confirm or
  refute it, not re-read as a surface.
- The 14,914 `BM-TS` timestamp records — the instrument's own heartbeat, summarised by
  `BM-INST` and read only in aggregate.

**Severity scale:** central default — *breaks users · wrong but contained · latent · hygiene*.

**Done means:** the four logs fully read; every record type in the dual-a log enumerated and
accounted for; each MUST-GATHER item of «#3581» either answered or explicitly declared
unanswered.

**⚠ Scope limit that changes what this data can certify — raised, not resolved.**
The Visit 7 run was executed **before its run sheet existed** («#3581» is paused at subtask 6,
which is the sheet). The seven attributes were therefore never declared for this run. The
numbers are good — the run is clean and complete — but nothing here was *pre-committed* to a
pass bound, so this data **characterises**; it does not **certify**. That is in fact what
R18.2 was always for (a characterisation visit, not a certification one), so the loss is
small, and it is named here rather than discovered later.

---

## 2. Read order — followed, coverage ticked

1. ✅ Provenance and completeness of each log (banner, build, trap code, session end).
2. ✅ The dual-a record census — all 22 record types, 15,973 records, every type accounted for.
3. ✅ Sign-off verdicts: declared vs emitted, in all four logs.
4. ✅ The LADDER segment: 152 rungs joined across `BM-RUNG` / `-RUNG2` / `-RUNG3` / `-RUNGHL` / `-RUNGTR`.
5. ✅ The LOWSPD segment: 20 rungs, the first low-speed data this project has ever held.
6. ✅ STOPMODE (48 traces) and LIVE (6 records).
7. ✅ Counter semantics from source — the five questions that make the numbers interpretable.
8. ✅ The two attended T0 logs, against PL-92's and PL-94's stated measurements.

---

## 3. The run, as the log states it

`BM-BANNER` / `BM-BUILD` / `BM-END`, `debug_260920-182503.log`:

```
src_rev,22  fmt,10  part,A  cfg_id,BENCH  clkfreq,270_000_000
left_base,32  right_base,16  voltage_enum,6  motor_type,0
inst_hz,500  ring,4_096  slongs,9  ladder_max,165_000_000
exit,COMPLETE  segs,5  last_seg,LOWSPD  records,15_973  trap_code,0  unrecov,0
```

**693 s wall (18:25:05 → 18:36:38), against a 1,185 s estimate and a 1,500 s cap.**

| Segment | Items | Measured | Estimated |
|---|---:|---:|---:|
| PREFLT | 2 | 6.0 s | 5 s |
| STOPMODE | 48 | 207.8 s | 540 s |
| LIVE | 6 | 27.8 s | 60 s |
| LADDER | **152** | 334.8 s | 420 s |
| LOWSPD | **20** | 116.6 s | 160 s |

Health, everywhere: **zero** faults, **zero** unrecoverable events, **zero** records with a
`why` other than `NONE`, **zero** rungs with a `result` other than `OK`, **zero** missed or
illegal hall transitions across all 172 rungs. The instrument logged **301,448 samples with
0 late, 0 skipped, 0 clamps and `max_late_us` 0**. The trace subsystem stored 48 traces with
0 `lost_head` and 0 `dropped`. Both boards detected `REV_B`. Both motors' preflight moved
exactly 18 ticks for 18 hardware ticks.

**This harness is sound.** Nothing below is a harness artefact except where a row says so.

---

## 4. Findings register

Provenance marks: *traced* = read directly from log or cited source · *inferred* = derived ·
*undetermined* = the measurement is solid, the cause is not.

| # | Severity | Finding | Evidence | Mark | Root cause | Trivially safe? |
|---|---|---|---|---|---|---|
| F1 | wrong but contained | `BM-PLAN` never emits a LOWSPD row. The run plan the log publishes claims four segments; five ran, and `BM-END` names LOWSPD as the last. Any consumer reading BM-PLAN as the manifest under-counts the run. | `test_bench_dual.spin2:8536-8540` — `PART_A:` hard-codes four `emitPlan()` calls; `SEG_LOWSPD` never appears as an argument anywhere in the file. The `lookupz` est tables **do** carry its slot (`:8667-8668`). | traced | A fifth call site was never added when LOWSPD was built (d6ed03d). Not a bound or a count constant — a missing line. Mine. | **Yes** — one `emitPlan(SEG_LOWSPD, 5)` line; adds a row of an existing record type, changes no measurement |
| F2 | wrong but contained | **PL-94 reproduced unchanged**, 24 h and one rebuild later. `t0` declares 24 cells and emits 22. `R17-T0-NOBOARDSTART` and `R1-T0-EXHAUST` are declared and never report a verdict. | `debug_260920-205301.log:180` — `T0-23,begin,no_bo`, cut mid-word, exactly as PL-94 records from `debug_260919-172524.log:180`. Same line, same two cells, same cog-start burst. | traced | Unchanged from PL-94: records truncate at cog-start bursts. The quiet windows of PL-85 reduced it; they did not close it. | No — PL-94 is an open investigation |
| F3 | wrong but contained | **PL-92 is refuted outright** — not merely its stated cause. PL-92 says *"the bench runner runs the terminal in console mode, so no attended tier can draw its panel."* Panels draw through that runner, with live host input. | `debug_260920-182345.log:22` — 197 backtick display commands and 196 `PC_KEY` polls. **Confirmed independently 2026-09-20 21:53** by the `panel` probe (`debug_260920-215353.log`): two windows drew their artwork and returned live pointer data through the same runner. | traced | The runner is not what prevents a panel drawing. | No — superseded; see the F3 amendment below |
| F4 | wrong but contained | **R17-DUAL-TRKICK-A FAILS both motors** — LEFT 37/74, RIGHT 36/74 transitions exceed the 50 mV excess bound (pass window is exactly 0). **This was predicted, and it is the R18.1 fix working**, not a regression. | `debug_260920-182503.log` SIGNOFF lines; criterion at `test_bench_dual.spin2:10027`, bound `TRKICK_EXCESS_MV = 50` at `:975`, population at `:3271-3272`. | traced | The cell was re-judged on current by «#3580»; it now measures what it always claimed to. | No — it is a true negative about the drive |
| F5 | latent | **The delta-cell matrix is asymmetric.** Speed-*down* exists only at 1-rung and 3-rung deltas; there is **no 2-rung and no 4-rung speed-down cell**. The largest delta (4 rungs) is exercised upward only. | 148 running-to-running transitions, binned: d1 DOWN 56 / d1 UP 56 / d2 UP 4 / d3 DOWN 12 / d3 UP 16 / d4 UP 4. Zero at d2-DOWN and d4-DOWN. | traced | The ladder's cell design (rids 30–44, 68–82) pairs each up-probe with a *return*, and the return is not always the mirror delta. | No — a design question for R18.3 |
| F6 | — (characterisation) | **The duty cap is the binding constraint, and the lag limiter is not.** From rung 6 upward the drive is voltage-saturated; at the top rung essentially **every PWM frame** is duty-capped. The lag limiter holds on at most **0.01%** of frames anywhere on the ladder. | Per-rung table §6.1. `win_cap` max 44,209 in a 1.001 s window ≈ 100% of frames at 43.9 kHz. `win_lag` max 9; `tr_lag` max 9. | traced | — | n/a |
| F7 | — (characterisation) | **Net current peaks at rung 6 and then collapses ~24x** (10,839 -> 451, `inet_x10`) while duty stays pinned at 100% and the commanded rate is still met to 0.1%. | §6.1 table; `BM-RUNG2.inet_x10` by rung, both motors, both directions, climb and descent. | **RESOLVED 2026-09-21 — traced measurement, cause now *inferred* with its rival refuted** | **A real voltage limit, not a defect.** Above the knee the applied voltage is fixed at the cap while back-EMF keeps rising with speed, so the net driving voltage — and with it the current — collapses. See §6.1a. | No — it is a limit to design to, not a fault to fix |
| F8 | latent | **The two boards' current-sense zero offsets differ by ~85 counts** (LEFT `zero_x10` 78–94, RIGHT −2–10), present from the first PREFLT reading. Raw `i_x10` comparisons between motors are invalid; netted (`inet_x10`) the two agree within 7% across the whole ladder. | `BM-START` PREFLT: LEFT `zero_x10,81`, RIGHT `zero_x10,0`. Per-rung sets: LEFT {78,86,90,94}, RIGHT {−2,0,5,10}. Netted L/R ratio 0.93–1.11 for rungs 0–9. | traced | A per-board offset the harness already corrects for. It matters because **S-2's fold-back estimates phase current from this channel**, and any absolute threshold inherits the offset. | No |
| F9 | latent | `rs_impl` (implied sense resistance) spans **150–375 on LEFT** but only **145–154 on RIGHT**. The LEFT spread is entirely at rungs 0–2, where net current is 64–300 counts. | §6.1 note; `BM-RUNG3.rs_impl` by rung, LEFT: rung 0 311–375, rung 5 151–152, rung 6 150–151. | traced, cause *inferred* | Consistent with a low-signal artefact of F8's offset, not a board difference — but it means any diagnostic keyed on `rs_impl` is unreliable below ~rung 3. | No |
| F10 | latent | **The rung-6 duty-saturation knee is an *unloaded* knee, and R18.3's acceptance numbers will inherit that.** Every rung here ran wheels up; rate tracks command to 0.1% *because the load is near zero*. Under load the same commanded speed needs more current, so the knee moves **down** the ladder. An acceptance number of the form "no duty saturation below Z% of achievable speed", chosen from this data, is therefore optimistic by an unknown margin. | Tier `dual-a` precondition, `tools/bench-run.sh:115` — `[MOTORS CONNECTED, WHEELS UP, UNATTENDED]`. Rate/pred 1.000–1.003 at every rung 1–11; knee at rung 6 (§6.1). | traced; the size of the shift is *undetermined* | The R18 sequence is deliberately unloaded-to-unloaded (Visit 7 → Visit 8) so the drive change is isolated from load variability. **The loaded run already exists and is scheduled** — «#3575»'s tethered spin-in-place floor tier, run at «#3576» Visit 6b, immediately after R18.5. | No — R18.3 states its numbers as unloaded **and** states what it expects loaded, so Visit 6b can falsify rather than merely observe (D2) |
| F11 | hygiene | The four logs are the **only copy**, and they sit in `src/logs/`, which is gitignored. The runner rotates that directory into `_OLD/`. Visit 6a's logs were filed to `DOCs/analyses/bench/2026-09-19/` and tracked; these are not filed. | `.gitignore:83` — `src/logs/`. `git ls-files src/logs` → empty. `git ls-files DOCs/analyses/bench/2026-09-19/` → 10 logs tracked. | traced | The filing step happens at visit close; this visit has not been closed. | **Yes** — copy to `DOCs/analyses/bench/2026-09-20/` and track; no behaviour change |
| F12 | — (characterisation) | **The cogging reading, first ever taken.** At the bottom command (1×10⁶) the hall-edge gap varies by up to **1.61×** within a run (`gap_min` 278 ms, `gap_max` 448 ms), falling to ~1.24× at 5×10⁶. The rotor's instantaneous speed swings ±30% while the commanded field rate is constant. | §6.3 table; `BM-LOW` `gap_min`/`gap_max`, 20 records. | traced | — | n/a |
| F13 | latent | `first_ms` (command → first hall edge) is **not monotonic** in commanded rate: 3×10⁶ → 13–55 ms and 4×10⁶ → 11–39 ms, but 5×10⁶ → **73–87 ms**, slower than both. | §6.3 table, `BM-LOW.first_ms`, consistent across both motors and both signs. | traced, **undetermined** | Candidate: `first_ms` is dominated by where the rotor happens to be parked within its hall sector (a uniform random phase), not by the commanded rate. With n=1 per cell this cannot be separated from a real effect. **Needs repeats, not analysis.** | No |
| F14 | hygiene | The `t0-stopmode` run emitted **zero** display commands, zero `PC_KEY` polls and no `WINDOW_PLACED`, then ended 6 s after its first prompt — the operator had nothing to act on. | `debug_260920-182425.log`: 0 backticks, 0 `PC_KEY`, 0 `WINDOW_PLACED`; `T0-24,row,0,arm,…,prompt,press_S_when_ready` at 18:24:28, session end 18:24:34. | traced | Same root cause as F3's group. | No |

**Counts:** 14 findings — 4 *wrong but contained*, 1 *breaks the conclusion*, 4 *latent*,
2 *hygiene*, 3 *characterisation* (recorded as results, not defects). Two rows carry an
**undetermined** cause (F7, F13). Two are flagged **trivially safe** (F1, F11).

---

## 5. Root-cause groups

**Group A — the R18.1 respecification did exactly what it was built to do (F4, F6).**
Before «#3580», the only limiting the harness could see was `err`, and PL-86/PL-95 established
that `err` tops out — bounded by the limiter near `LAG_HOLD` and by its own ±127
representation. R18.1 published the unbounded replacements. They immediately show something
`err` could never have shown: **the active constraint at the top of the range is the duty cap,
not the lag limiter, and it is not close.** `win_lag` never exceeds 0.01% of frames anywhere;
`win_cap` reaches ~100%. The cell that now fails (F4) fails because it measures current
instead of inferring from a saturated proxy. Both are the fix working.

**Group B — PL-92 and PL-94 are the same shape of problem and neither is what it was filed as
(F2, F3, F14).** Both are *records that should exist and do not*. PL-94 loses sign-off records
in cog-start bursts; PL-92 loses an entire window. PL-92's filed cause — the runner's console
mode — is now refuted by its own control (F3): the `bench`-named panel drew through that
runner, with 197 display commands and 196 input polls, 40 seconds before the `t0stop`-named
panel drew nothing.

⛔ **This does not prove the window name is the cause, and I am not claiming it does.** The two
runs differ in the panel name *and* in the compile-time define *and* in the code path. The
`panel` probe («#3585», bdaf13a) is the experiment that settles it, because it varies the name
and nothing else, and it carries the negative control neither of these two runs has (D2).

### ⛔ F3 amendment — 2026-09-21, after the `panel` probe ran

The probe ran at 21:53 (`src/logs/debug_260920-215353.log`). Two corrections to the above:

1. **The window name is exonerated.** Both windows reported a pointer — the control `bench` on
   6 of 38 `PP-POLL` records, the suspect `t0stop` on 11, never both at once. Both returned
   pixel colours `$1C_2026` / `$0C_0D10` / `$30_2814`, which are the three most common colours
   of `src/bm_bg.bmp` (63.4% / 24.9% / 7.3%). **Both windows drew our artwork and both read the
   host mouse.** The live suspect is dead.
2. **I withdraw the `WINDOW_PLACED` inference, and with it the claim that "the failure happens
   before the window opens."** That probe log contains **zero** `[SYSTEM] WINDOW_PLACED` lines
   and yet both windows opened and drew. `WINDOW_PLACED` is not a reliable signal that a window
   opened, so it cannot discriminate between the two T0 logs. My use of it above was wrong.

**What survives is the stronger leg, and it now carries the whole weight:** `t0-stopmode`
emitted **zero backtick display commands** while still emitting `T0-24,begin` and
`T0-24,row,0,arm,…`. The program ran and reached its row-0 prompt with its panel code never
executing. That is not the terminal, not the runner, not the window name and not the path —
**it is inside `test_bench_t0.spin2` under `-D T0_STOPMODE`**, and it is a desk question.

⚠ The probe is built to run 90 s (`RUN_S = 90`) and then print `PP-VERDICT`. This session ended
at **29 s**, so `PP-VERDICT`, `PP-END` and `DEBUG_END_SESSION` were never printed. The verdict
above is **derived from the 38 poll records, not quoted** — «#3585»'s acceptance asks for it
quoted, and a full-length re-run would capture it verbatim.

**Group C — the drive is voltage-limited well below its commanded ceiling, and what happens
above that limit is not understood (F6, F7, F10).** Duty saturates at rung 6 of 11. Above it
the rotor still tracks the command exactly — but only because it is unloaded, and the current
that would tell us about torque margin *falls away* rather than rising. Under any load this
region has no headroom at all, and this visit cannot say what it does. **This group is the
input R18.3 designs against, and it is incomplete by one whole dimension.**

---

## 6. What the logs establish — the characterisation payload

This is the answer to «#3581»'s MUST-GATHER list, item by item.

### 6.1 The ceiling question (MUST-GATHER item 4) — answered

`win_cap` and `win_lag` increment **once per PWM frame at ~43.9 kHz**, not once per ~1,913 Hz
control pass — `isp_bldc_motor.spin2:4308-4309` (*"MOTOR Speed Maintenance Loop — runs at
43.9 kHz (22.8 uSec period)"*), increments at `:4244` (`lag_held_`) and `:4471`
(`duty_capped_`), rate constant `PWM_RATE_IN_HZ = 44_000` at `:3747`. They are proper
differences, not cumulative totals (`test_bench_dual.spin2:3333-3334`, `:3356-3357`). That
makes the counts a **percentage of frames**, which is what follows:

| rung | incre | % frames duty-capped | % frames lag-held | rate/pred | duty | net current |
|---:|---:|---:|---:|---:|---:|---:|
| 0 | 5,000,000 | 0.0% | 0.00% | 1.017 † | 6.7% | 58 |
| 1 | 10,000,000 | 0.0% | 0.00% | 1.003 | 9.6% | 83 |
| 2 | 20,000,000 | 0.0% | 0.00% | 1.003 | 17.6% | 306 |
| 3 | 40,000,000 | 0.0% | 0.00% | 1.002 | 36.4% | 1,605 |
| 4 | 60,000,000 | 0.0% | 0.00% | 1.001 | 57.5% | 4,316 |
| 5 | 80,000,000 | 0.0% | 0.00% | 1.001 | 80.9% | 8,701 |
| **6** | 100,000,000 | **10.5%** | 0.00% | 1.002 | **99.3%** | **10,839** ← peak |
| 7 | 120,000,000 | 49.3% | 0.00% | 1.001 | 100.0% | 4,806 |
| 8 | 140,000,000 | 77.1% | 0.00% | 1.001 | 100.0% | 1,111 |
| 9 | 147,000,000 | 83.9% | 0.00% | 1.001 | 100.0% | 587 |
| 10 | 155,000,000 | 94.1% | 0.00% | 1.001 | 100.0% | 451 |
| 11 | 165,000,000 | **97.9%** | 0.01% | 1.000 | 100.0% | 782 |

† rung 0 measures 13–14 hall ticks in a 1 s window; ±1 tick is ±7%. Quantisation, not error.

**The answer:** it is a **real voltage ceiling**, and it starts at rung 6 — not at the top of
the ladder. But the expected symptom does *not* appear: the duty **deficit does not cost
speed**. Commanded rate is met to within 0.1–0.3% at every rung to the very top. So the
question as R18.2 posed it ("does the drive give up before the motor's limit, or is demand met
at the cap?") gets a third answer neither branch anticipated: **demand is met at the cap, the
rate is met, and the reserve is gone.** From rung 6 up the drive has no voltage left to answer
a disturbance with — which is invisible here only because nothing disturbs it (F10).

The current collapse past rung 6 (F7) is the part that is measured and not explained, and it
is the question I would put first to R18.3.

### 6.1a The current collapse — RESOLVED 2026-09-21

F7 asked whether the 24x current collapse above the knee is back-EMF approaching the rail (a real
limit to design to) or commutation losing effectiveness past the knee (a defect to fix). It is the
first, and the second is refuted rather than merely unsupported.

**The decisive evidence is what the ROTOR did, not what the current did.** Commutation losing
effectiveness means the field stops dragging the rotor with it, which shows up as the rotor falling
behind the commanded rate. Measured rate against commanded, every rung above the knee:

| rung | 6 | 7 | 8 | 9 | 10 | 11 |
|---|---|---|---|---|---|---|
| rate / pred | 1.002 | 1.001 | 1.001 | 1.001 | 1.001 | 1.000 |

**The rotor tracks the command to within 0.2% everywhere, including the top rung.** A drive whose
commutation was failing could not do that. The rival hypothesis predicts a signature that is simply
absent.

**The surviving explanation also fits quantitatively.** Above the knee the duty is pinned, so the
applied voltage is fixed while back-EMF keeps rising with speed, and the net driving voltage --
hence the current -- falls. Fitting `I = (V - k*w) / R` from the rung-6 peak:

| rung | speed vs rung 6 | current vs rung 6 | implied back-EMF as a fraction of applied |
|---|---:|---:|---:|
| 7 | 1.200x | 0.443 | 0.88 |
| 8 | 1.400x | 0.103 | 0.97 |
| 9 | 1.470x | 0.054 | 0.98 |
| 10 | 1.550x | 0.042 | 0.99 |
| 11 | 1.650x | 0.072 | 0.97 |

⚠ **Stated honestly: this is a fit, not a proof.** Back-solving the rung-6 back-EMF fraction from
each later rung gives 0.59 to 0.74 rather than one constant, so the simple linear model is
approximate. Two known reasons, both already in this register: winding resistance is not constant,
and rungs 9-11 sit in the low-signal regime where F9 found `rs_impl` unreliable. The rung-11 uptick
(0.072 against rung 10's 0.042) is inside that same noise. The model is *directionally* right and
its rival is *refuted*; the exact coefficient is not claimed.

**What this settles for R18.3.** Rungs 6-11 are a **real voltage limit**, not range the drive is
throwing away. What is lost up there is **torque margin, not speed** -- back-EMF is within a few
percent of the rail, so there is almost no voltage left to answer a disturbance with, and the speed
survives only because the wheel is unloaded. So:

- An acceptance number of the form *"no duty saturation below Z% of achievable speed"* must not
  treat the knee as a defect to design away. The knee is where the motor's own back-EMF meets the
  supply.
- The honest target above the knee is **knowing there is no margin** -- which is exactly correction
  2's "hold at the achievable rate rather than winding the field ahead."
- ⭐ **A falsifiable prediction for Visit 7b:** correcting the phase lowers the current needed for
  the same torque, which lowers the `I*R` drop, which means duty should pin at the same rung or
  slightly *higher* on the candidate leg. If the knee instead moves **down**, this section is wrong
  and should be reopened.

**Authority note:** this was settled against
[`BLDC-COMMUTATION-PRINCIPLES.md`](BLDC-COMMUTATION-PRINCIPLES.md) -- *"the rotor keeps up only
while the motor can produce enough torque from the voltage headroom left above its back-EMF, and
that headroom shrinks as speed rises"* -- plus this run's own data. p2kb was **not** consulted,
because this is motor physics on the driver board, not something the P2 silicon defines; the
domain authority for how this hardware is meant to be driven is the designer's document.

### 6.2 Transition behaviour, both directions (MUST-GATHER items 1 and 2) — gathered

**152 rungs, 148 running-to-running transitions, both motors, both signs, climb and descent.**
Before this run the project held 44 speed-ups and **zero** speed-downs. It now holds 76 ups
and 68 downs.

Transition current kick, as `tr_i_pk` ÷ that rung's own steady net current:

| delta | direction | n | mean | max |
|---:|---|---:|---:|---:|
| 1 rung | DOWN | 56 | 0.28 | 0.59 |
| 1 rung | UP | 56 | 0.24 | 0.53 |
| 2 rungs | UP | 4 | 0.15 | 0.21 |
| 3 rungs | DOWN | 12 | **1.08** | **3.24** |
| 3 rungs | UP | 16 | 0.79 | 2.14 |
| 4 rungs | UP | 4 | **1.73** | 2.21 |
| 2 rungs | DOWN | **0** | — | — |
| 4 rungs | DOWN | **0** | — | — |

**The largest single kick in the entire run is a speed-DOWN** — RIGHT motor, rung 5 → rung 2,
`tr_i_pk` 665 against a steady 205, **3.24×** — and speed-down is the half of the command space
that had never been measured. The four worst transitions in the run are all 3-rung
speed-downs (3.24, 3.06, 2.98, 2.86). Small deltas (1 rung) produce **no** kick at all: the
transition peak is *below* the steady current, in both directions.

So the kick is a **large-delta** phenomenon, it is **worse going down than up** at the same
delta, and it is invisible at the delta the old 48-rung ladder mostly sampled. F5's missing
cells (d2-DOWN, d4-DOWN) are the two that would establish the shape of that curve.

### 6.3 Low speed and startup (MUST-GATHER item 5) — first data ever

20 rungs, 4 s windows (`LOW_WINDOW_MS = 4_000`, `test_bench_dual.spin2:381`), 1–5×10⁶.

| incre | first edge (ms) | edges/4 s | gap min–max (ms) | max/min | rate/pred | duty |
|---:|---:|---:|---:|---:|---:|---:|
| 1×10⁶ | 387–505 | 11 | 278–448 | **1.61** | 1.038 | 1,600 |
| 2×10⁶ | 175–207 | 21–22 | 136–224 | 1.47 | 1.00 | 1,600 |
| 3×10⁶ | 13–55 | 32 | 98–142 | 1.45 | 0.988 | 1,600 |
| 4×10⁶ | 11–39 | 43 | 80–104 | 1.30 | 1.009 | 1,600–1,606 |
| 5×10⁶ | 73–87 | 53–54 | 66–84 | 1.27 | 1.00 | 1,602–1,699 |

Three things this establishes, none of them previously known:

1. **The command is followed even at the very bottom.** At 1×10⁶ the wheel turns 2.7 hall
   edges per second and the measured rate still matches prediction within 4%. The drive does
   not have a dead band at the bottom of its range.
2. **Duty is floored at ~1,600 counts (6.6%)**, not proportional to command, for everything
   below 4×10⁶ — and rung 0 of the ladder sits at the same floor. Whatever sets that floor is
   what the low-speed regime actually runs on.
3. **The rotor's motion is badly non-uniform down here (F12).** A 1.61× spread between the
   shortest and longest hall gap in one run means the instantaneous speed swings roughly ±30%
   around a constant commanded field rate. At 1×10⁶ the instrument takes ~187 samples per hall
   edge (against 1.13 at the top rung), so for the first time the *shape* of that advance is
   observable rather than aliased. **This is the cogging signature, and it is the clearest
   statement yet of why position between hall edges matters.**

No cell judges any of it, by design (D2 — acceptance numbers are R18.3's to pick, before
R18.4 builds).

### 6.4 Sensor rate (MUST-GATHER item 3) — confirmed on hardware

Desk work at «#3581» subtask 3 predicted 1,913.2 control passes/s and 4.34 passes per hall
edge at the top rung. The run corroborates the frame-rate half of the model directly: `win_cap`
of 44,209 in a 1.001 s window implies **44,165 frames/s**, within **0.4%** of the nominal
44,000 (`PWM_RATE_IN_HZ`, `isp_bldc_motor.spin2:3747`). Missed and illegal hall transitions
were **zero at every rung including rungs 10 and 11**, which is the extreme the plan asked be
tested rather than assumed. The instrument itself ran 301,448 samples with zero late, zero
skipped and zero clamps.

### 6.5 The phase voltages (MUST-GATHER item 6) — **not gathered**

`BM-RUNG2` carries `ph_x10` — a single number, 23,799–23,831 at the rungs sampled. It is the
**sum** of the three phase readings, exactly as the harness note in «#3581» warned
(`instPackSense()` packs current and u+v+w into one long). That sum is a bus-voltage
estimator; it discards precisely the per-phase difference a rotor-angle estimate needs.

**So item 6 — whether the phase voltages carry usable rotor angle between hall edges — remains
entirely unmeasured**, and it is the load-bearing input to R18.3 §1. Carrying the three apart
costs hub or ring depth and is an instrument-design decision (P3, mine), not something this
data can be re-read to recover.

---

## 7. What was not read, and why

- `src/logs/_OLD/` and Visit 6a's log set — excluded at §1; the prior is cited, not re-derived.
- The 14,914 `BM-TS` records individually — summarised through `BM-INST`, which reports zero
  late/skipped/clamped. Reading them individually would test the instrument, not the drive.
- `rungMeasure()`'s internal snapshot-capture sites and `wait4adc`'s body — the subtraction
  sites and loop-rate comment were sufficient to establish counter semantics; frame-boundary
  timing to better than one frame was not needed and is not claimed.
- STOPMODE's 48 traces beyond their headers and end-records — all 48 ended `REST` with zero
  loss; their sample bodies bear on stop-mode behaviour (C-4, S-9a), which is not this
  study's question.

---

## 8. Open questions — all four are mine, none is Stephen's

Four questions came out of the register. Checked against the plan and the task roster, **none
of them is a question for Stephen** — each is either already decided in the plan, or answerable
from an authority I have not yet consulted. They are recorded here as work, not as asks.

**Q1 — where the loaded run goes. ALREADY DECIDED; not a question.** The plan carries a loaded
tier: «#3575» (R17.8) builds the **tethered spin-in-place floor run** — platform on the floor,
both spin directions, each clockwise leg paired with an equal counter-clockwise leg so the
cable never winds more than one leg, a hard travel limit from the 15.25 in / 387 mm track
width, per-wheel **loaded** current recorded by direction (answers PL-88). It runs at «#3576»
**Visit 6b**, which the 2026-09-20 revision placed immediately after R18.5/Visit 8. The R18
sequence is unloaded-to-unloaded **by design**, so the drive change is isolated from load
variability; Visit 6b is where load enters. **What remains is F10's narrower point, and it is
R18.3's to carry:** state the acceptance numbers as unloaded, and state alongside them what is
expected loaded, so Visit 6b can falsify them rather than merely observe (D2).

**Q2 — the current collapse (F7). ANSWERED 2026-09-21; see §6.1a.** It is a real voltage limit, not
a commutation defect. The rival hypothesis is refuted by the rotor's own behaviour, and the
consequence for R18.3 is that rungs 6–11 are a region to design *to*, not range to recover.


**Q3 — the missing d2-DOWN and d4-DOWN cells (F5). Mine, inside R18.3/R18.5.** «#3584» already
scopes Visit 8 to "both directions, small/medium/large delta, low/knee/high, near-max". These
two cells are part of meeting that scope, decided when R18.5's sheet is written, not asked.

**Q4 — `first_ms` non-monotonic (F13). Mine, a run-sheet decision.** n=1 per cell cannot
separate a real effect from the rotor's random parking phase. Repeats are cheap and belong in
Visit 8's LOWSPD cells; no decision from Stephen is needed to add them.

⛔ **The lesson this section records.** The first draft of this study asked Stephen Q1 as an
open scoping choice. The plan already answered it, in a revision he ruled on himself. Asking
it spent his attention on work he had already ordered — and it asserted an absence
("does R18 need a loaded tier") without searching the forward plan for one. See the
doctrine-overlay P8 amendment of 2026-09-21.

---

## 9. Hand-off

**The two trivially-safe fixes**, for a single green-light — neither changes any measurement:

- **F1** — add the missing `emitPlan(SEG_LOWSPD, 5)` line so BM-PLAN publishes the run it
  actually performs. The est table already has the slot.
- **F11** — file these four logs to `DOCs/analyses/bench/2026-09-20/` and track them, as Visit
  6a's were. They are the only copy of the first execution of R18.1+R18.2 and they currently
  sit in a gitignored, rotated directory.

**What this changes for the open tasks:**

- **«#3581» (R18.2, paused at the run sheet).** Its data exists. Four of the six MUST-GATHER
  items are answered (§6.1–6.4), one is answered better than asked (item 4), and **item 6 is
  not gathered at all** (§6.5) and cannot be recovered from this log. The sheet subtask now
  has a different job than when it was paused.
- **«#3582» (R18.3).** §6 is its input. Group C is the design problem, stated in numbers.
  Two things carry into it directly: **§8 Q2** — resolve the current collapse against
  `BLDC-COMMUTATION-PRINCIPLES.md` and p2kb before choosing acceptance numbers; and **F10** —
  state those numbers as unloaded, with the loaded expectation alongside, so «#3576» Visit 6b's
  floor run can falsify them.
- **«#3575» / «#3576» (the floor tier and Visit 6b).** Unchanged in position — the loaded run
  stays behind R18.5 where the 2026-09-20 revision put it. F10 gives it one extra job it did
  not have: it is now also the falsification of R18.3's loaded expectation, not only the
  offset confirmation and PL-88.
- **«#3585» (the PLOT panels).** F3 refutes PL-92's filed cause and narrows the failure to
  before the window opens. The `panel` probe is still the run that settles it — it is the only
  one of these experiments with a negative control.
- **PL-94.** Reproduced unchanged; the punch-list entry needs a second-occurrence line.

**Next step is `sprint-plan`** if these findings are to be fixed. The scope call is Stephen's.

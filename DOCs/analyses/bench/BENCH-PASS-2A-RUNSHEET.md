# Bench Pass 2a — run sheet

**The automated commutation-offset scan.** Claude loads, runs and evaluates it. Your part is
the rig. STEPHEN 2026-09-12: *"the first effort in the bench run, automated without my help, is
for you to run the scan."*

**No meter readings, no keypresses.** Every number comes from the P2's own telemetry.

---

## Your part — set the rig, then tell Claude it is ready

| | Check |
|---|---|
| 1 | **Rev B boards** connected — the dual 6.5″ platform |
| 2 | **Both motors plugged in** |
| 3 | **Both wheels up and free to turn** — the scan drives each wheel both ways, up to half speed |
| 4 | **Pack charged** |
| 5 | **P2 on USB** to the Mac |

The pin groups are the bench config's (LEFT P32_P47, RIGHT P16_P31); nothing to change.

**Panic, if you are at the bench: PHYSICAL BATTERY DISCONNECT.** `emergencyCutoff()` is not a
panic button — it self-cancels in about 250 ms (finding S-4). Unattended, the scan's own current
aborts, fault caps and time cap end the run, and the driver's lag fault disables PWM regardless.

---

## Claude's part

```bash
tools/bench-run.sh scan
```

Run from the project root; the runner switches to `src/` itself. It echoes both commands before
running them:

```
+ pnut-ts -l -d -D BENCH_CFG test_bench_scan.spin2
+ pnut-term-ts -r test_bench_scan.bin --console-mode --exit-on-end-session
```

**Expected length:** longer than Pass 2a's earlier runs -- scan v3 re-measures the zero before
every point, not just the references (about 1s added per point, run-wide). Budget at least 20
minutes, at most about 30, ending on its own.

**Before trusting any number:**
- The banner must say `cfg_id BENCH`, `fmt 6`, left base 32, right base 16. `pnut-ts` silently
  ignores an unknown `-D`, so no banner voids the run.
- The **self-check** must pass, per motor, at the default 43/317 offsets. It checks (scan v3.1):
  Rev B at every start, `start()` returning a cog id, hall counters at 0, the zero health (not
  frozen, spread <= 10 mV, |mean| <= 300 mV), net-of-zero ¼-speed currents and their ratio, and
  the tick rate. **If it aborts, the scan did not run and a foundation fix is wrong.** Report which,
  stop the pass, and never loosen a band to get past it.

**What the evaluation reports, per motor and increment sign:**
- the fitted minimum-current offset, its uncertainty and the fit residual;
- the current at the minimum against the current at the default;
- whether the minimum was bracketed (a minimum at the window edge is not a minimum) -- and when it
  is not, the fault edge instead: scan v2/v3 (PL-31) fine-walks into a coarse-walk fault stop (5°,
  then 2° if that also faults) and reports the last-good/first-fault swept degrees, the edge
  estimate (their midpoint) and the margin from the fitted minimum, or from the lowest measured
  point when there is no fit (`BS-CLIFF`, per motor/speed/sign);
- scan v3 (from run 4): a side that stopped on faults is now bounded, not excluded -- the last
  good point before that fault becomes the sweep window's limit on that side, and a point inside
  the window brackets the minimum at a smaller rise (4%, `fault_rise_pct` in `BS-LIMITS2`) than an
  unbounded side needs (15%, `rise_pct`), justified against the points' own standard error. Fine
  points, the one extension and the fit never cross that limit, at either speed. `BS-FIT`'s new
  `pinned` field is TRUE when the fitted vertex sits within one `FINE_STEP_DEG` of a fault-derived
  limit -- treat a pinned minimum as up against the wall, not as a free minimum;
- the half-speed re-located minimum and its shift. Scan v4 (from run 5, PL-32): a half-speed
  confirm point that faults is now followed by the same fine-walk-into-the-fault-edge probe the
  quarter-speed coarse walk already had (`BS-POINT`/`BS-POINT2`/`BS-POINT3` phase `CLIFF`), so a
  fault no longer leaves an unmeasured gap between the last good confirm point and the edge, and
  those probe points count toward the half-speed fit. `BS-CLIFF` at half speed reports its margin
  from the fit whenever the fit solved, exactly as it already does at quarter speed.

**Per-point zero and net (scan v4, PL-32; record split fixed at review):** the driver's sense zero
is re-drawn at every driver start, so a zero is valid only within its own driver lifetime, never
across a restart. A new record, **`BS-POINT3`**, is now emitted immediately after every
`BS-POINT2` and carries `zero_mV_x10` (the `BS-ZERO` reading taken immediately before that point,
`NA` when no sample was taken) and `net_mV_x10` (`BS-POINT`'s `i_mean_mV_x10` minus that zero,
`NA` when the point has no valid mean). These two fields were first appended directly to
`BS-POINT2` at v4's first cut, but that pushed `BS-POINT2`'s own worst case past the 280-byte
bound (the longest record measured intact through one `debug(zstr_())` line -- a hard limit, not
a style note), so review split them into `BS-POINT3` instead; `BS-POINT2` is back to its exact
v3.1 field list. **Every judgement now runs on net means, not raw:** the coarse walk's low point,
the rise/bracket tests, the quadratic fit itself (so `BS-FIT2`'s `min_mV_x10`/`rms_mV_x10` and
`BS-RESULT`'s `i_min_mV_x10`/`i_def_mV_x10`/`saving_pct_x10` are net **from `fmt 6`**, under
unchanged field names), the `BS-LEG` drift percent/flag, and `BS-PAIR2`'s two minima and their
ratio. Every raw field (`BS-POINT`'s `i_mean_mV_x10`, `BS-LEG`'s `ref_start_mV_x10`/
`ref_end_mV_x10`, `BS-PAIR2`'s `zero_mV_x10`) is kept unchanged for comparison. The one exception
by design, not oversight: the per-point relative current abort's threshold (`pointLimitMv`) stays
RAW, because `pollSample()` compares it against a raw live sample inside the tight polling loop,
where no zero is available to subtract.

**Per motor, it also reports:**
- the midpoint of the two minima, which estimates the hall zero;
- the current ratio at the pair of minima — the designer's principle predicts near-equal current.
  Scan v4: since the fit is now net (above), `BS-PAIR2`'s two minima are already net of their own
  leg's zero, so there is no separate raw minimum left to ratio. **`ratio_raw_x1000` prints `NA`
  from `fmt 6`** (review fix: printing the same net-derived number under both the raw and net
  names would misrepresent it as an independent check); `ratio_net_x1000` carries the one ratio
  that exists, and `imbalance` is computed from it. The old `ratio_net_x1000` (re-subtracting a
  single `ZERO_INIT` from both minima) was the PL-32 bug: after a restart mid-run, `ZERO_INIT` is
  the wrong lifetime's zero for a later leg;
- the current-sense zero, re-measured (driver running, zero commanded) immediately before **every**
  point, of any phase (`BS-ZERO`, phase-tagged), because run 3 found a ~13-16 mV sense-side bias
  that appeared after some high-current or fault events, and run 4 confirmed it as a zero shift
  (not a current change) that can appear soon after a driver restart (scan v3.1: now checked by
  a health verdict — not frozen, spread <= 10 mV, absolute <= 300 mV — instead of a fixed band,
  and the `BS-ZERO` record now includes phase-voltage means to help locate the offset source).
  Every zero is read with the drive floated (the driver's default stop mode, which
  disables PWM at zero command), so an out-of-band zero is not bridge current. Run 5 showed
  where it comes from: the driver calibrates its ADCs once per start from a single settling
  sample, so every channel's zero is re-drawn at each driver start (PL-32; this replaces
  PL-30's board-offset reading). A zero is valid only within its own driver lifetime.

**Disposition:** apply the measured pair («#3523») only if both motors agree on each sign's
minimum within the fit uncertainty and the half-speed result holds. Otherwise the disagreement
goes to Stephen as a finding before any constant changes.

The log is curated to `DOCs/analyses/bench/<date>/` (`.log` extension), with the evaluation
beside it.

**The run now ends itself on a stall (task 3534).** Scan run 5 locked up mid-run: cog 0 stopped
emitting debug while still running, with both wheels stopped and free, and the log simply
stopped -- no `BS-END`, no session-end marker
(`DOCs/analyses/bench/2026-09-13/SCAN-RUN-5-EVALUATION.md` section 7). A second cog now watches
cog 0's heartbeat and last checkpoint (`fmt 5`'s new instrumentation) and, if cog 0 has not
advanced for `WD_STALL_MS` (4 s -- above every legitimate gap this file's own loops or the
motor library's own methods can leave between beats), it:
1. emits `BS-WATCHDOG` (cog 0's last checkpoint, since when, and its sampling-loop state) and
   `BS-WATCHDOG2` (both wheels' raw driver telemetry, read directly);
2. stops both wheels;
3. emits `BS-END` with `exit ABORTED` and `reason WATCHDOG`;
4. emits the `DEBUG_END_SESSION` marker, then idles forever.

**A recurrence now names its own state**, from `BS-WATCHDOG`'s `checkpoint`/`checkpoint_tok`
field: which loop, library call, or `lineEmit()` cog 0 was last known to be inside.
`BS-WATCHDOG2`'s last field, `stack_ok`, reports whether the watchdog cog's own stack sentinel
survived building the stall report -- `FALSE` means the watchdog's 128-long stack itself
overran on that path and everything else in the record is suspect.

**A silent stop with NO `BS-WATCHDOG` record is itself evidence:** it means the stall was not
confined to cog 0 (the watchdog cog also stopped advancing, or the whole P2 stopped), which is a
different, more serious class of failure than task 3534 was built to catch -- treat it as a
finding for Stephen, not as "the watchdog didn't fire this time."

**`BS-WDSTART`, the first record of every run, confirms the watchdog cog itself started**
(`started TRUE/FALSE`, `cog` = the cog id or the negative failure code). `started FALSE` means
the run is proceeding unwatched -- the scan's own current aborts, fault caps, time cap and the
driver's own angle-lag fault are still in force, but a cog-0 lockup like run 5's would not be
caught or reported; treat it as a finding, not as "the scan is fine, just quieter."

**A single `BS-END`/`DEBUG_END_SESSION`, always.** cog 0 stops the watchdog cog before its own
`BS-END`/marker on every normal-ending path, so a normal run never produces a second, bogus
`BS-WATCHDOG`/`BS-END` a few seconds after the real one (found and fixed in review, before this
was ever run). If a run's log ever shows two `BS-END` records, that fix regressed -- report it,
do not curate the log as if it were two runs.

---

## Stop and tell Claude if

- A wheel does not turn when the scan starts it, or turns the wrong way on a hold
- Anything smells, gets hot, or makes a noise it did not make in Bench Pass 1
- The run is still going after 30 minutes
- A `BS-WATCHDOG` record appears at all -- the run ended itself on a detected stall

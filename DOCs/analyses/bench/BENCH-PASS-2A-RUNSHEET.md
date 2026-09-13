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
- The banner must say `cfg_id BENCH`, `fmt 4`, left base 32, right base 16. `pnut-ts` silently
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
- the half-speed re-located minimum and its shift.

**Per motor, it also reports:**
- the midpoint of the two minima, which estimates the hall zero;
- the current ratio at the pair of minima — the designer's principle predicts near-equal current;
- the current-sense zero, re-measured (driver running, zero commanded) immediately before **every**
  point, of any phase (`BS-ZERO`, phase-tagged), because run 3 found a ~13-16 mV sense-side bias
  that appeared after some high-current or fault events, and run 4 confirmed it as a zero shift
  (not a current change) that can appear soon after a driver restart (scan v3.1: now checked by
  a health verdict — not frozen, spread <= 10 mV, absolute <= 300 mV — instead of a fixed band,
  and the `BS-ZERO` record now includes phase-voltage means to help locate the offset source).
  The evaluation nets each point's current against the `BS-ZERO` record before it; the binary's
  fits run on the raw mean, and only the first zero (`ZERO_INIT`) verdict is used for the
  self-check. Every zero is read with the drive floated (the driver's default stop mode, which
  disables PWM at zero command), so an out-of-band zero is not bridge current. Run 5 showed
  where it comes from: the driver calibrates its ADCs once per start from a single settling
  sample, so every channel's zero is re-drawn at each driver start (PL-32; this replaces
  PL-30's board-offset reading). A zero is valid only within its own driver lifetime.

**Disposition:** apply the measured pair («#3523») only if both motors agree on each sign's
minimum within the fit uncertainty and the half-speed result holds. Otherwise the disagreement
goes to Stephen as a finding before any constant changes.

The log is curated to `DOCs/analyses/bench/<date>/` (`.log` extension), with the evaluation
beside it.

---

## Stop and tell Claude if

- A wheel does not turn when the scan starts it, or turns the wrong way on a hold
- Anything smells, gets hot, or makes a noise it did not make in Bench Pass 1
- The run is still going after 30 minutes

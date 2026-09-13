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

**Expected length:** about 13 minutes, at most about 20, ending on its own.

**Before trusting any number:**
- The banner must say `cfg_id BENCH`, left base 32, right base 16. `pnut-ts` silently ignores an
  unknown `-D`, so no banner voids the run.
- The **self-check** must pass, per motor, at the default 43/317 offsets. It checks: Rev B at
  every start, `start()` returning a cog id, hall counters at 0, the zero reading, the ¼-speed
  currents and their ratio, and the tick rate. **If it aborts, the scan did not run and a
  foundation fix is wrong.** Report which, stop the pass, and never loosen a band to get past it.

**What the evaluation reports, per motor and increment sign:**
- the fitted minimum-current offset, its uncertainty and the fit residual;
- the current at the minimum against the current at the default;
- whether the minimum was bracketed (a minimum at the window edge is not a minimum);
- the half-speed re-located minimum and its shift.

**Per motor, it also reports:**
- the midpoint of the two minima, which estimates the hall zero;
- the current ratio at the pair of minima — the designer's principle predicts near-equal current.

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

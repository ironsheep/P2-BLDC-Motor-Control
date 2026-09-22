# Visit 7c — run sheet (CLOSED 2026-09-22)

**Plan section:** R18.2f ([`../../plans/BENCH-READINESS-SPRINT-PLAN.md`](../../plans/BENCH-READINESS-SPRINT-PLAN.md)).
**Task:** «#3594», closed.

**Nothing is left to run under this sheet.** The next pass's loads are carried, with their
justification, in [`2026-09-22/VISIT-7C-PASS2-EVALUATION.md`](2026-09-22/VISIT-7C-PASS2-EVALUATION.md) §6.
The next run sheet inherits them.

---

## Passes

| Pass | When | Ran | Result | Report |
|---|---|---|---|---|
| 1 | 2026-09-21/22 | `scan-droop`, `scan`, `dual-a` | droop stop certified; `L` at an eighth and a quarter; the start trace's first reading (its "mechanism settled" verdict was superseded by pass 2) | [`VISIT-7C-EVALUATION.md`](2026-09-22/VISIT-7C-EVALUATION.md) |
| 2 | 2026-09-22 18:25–18:39Z | `dual-align` ×2, `dual-a` | **Z = −3.3° cold**, agreeing with the driven −3.6 ± 0.4; ALIGN detector certified (PL-99); sectors equal to ±1°; back-EMF readable coasting from 43 edges/s; **start seed falsified and removed** | [`VISIT-7C-PASS2-EVALUATION.md`](2026-09-22/VISIT-7C-PASS2-EVALUATION.md) |

## Retired, not deferred

- **The servo setpoint A/B.** The driver places the field at the commanded angle
  (`isp_bldc_motor.spin2:4467-4474`) and the servo integrates duty to its setpoint (`:4591`), so setpoint
  and lead combine by construction. A run could only confirm the equation.

## What the passes changed (for the next sheet's §7 resume)

- **Subject:** the driver's start seed (`4014b92`) was measured and **removed**. The driver is the
  `12413b1` drive again, with comment corrections only. Nothing the passes certified is invalidated.
- **Harness:** `test_bench_dual.spin2` is at SRC_REV 26 / FMT 14 (ALIGN hysteresis and band test).
  `BM-BUILD` now carries **`drv_rev`**, the driver's own `DRIVER_REV` (1), so every later log names the
  driver that ran. The next sheet checks it in its banner table.

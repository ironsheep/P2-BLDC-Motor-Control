# Visit 9b — the moved limits reach the drive, and the driver's following reading is certified falling as well as holding

**Tasks:** «#3605» (the limits moved from Visit 9) and «#3597» (the FOLLOW certification). **Run sheet:**
[`../VISIT-9B-RUNSHEET.md`](../VISIT-9B-RUNSHEET.md). **Before it:** [`VISIT-9-EVALUATION.md`](VISIT-9-EVALUATION.md).
**Procedure:** `DOCs/procedures/BENCH-RUN-PROCESSING.md`. Evaluated 2026-09-23.

| Log | Tier | Binary | Rebuilt (UTC) | Source |
|---|---|---|---|---|
| `debug_260922-193000.log` | `dual-limits-top` | `test_bench_dual.bin`, 93,053 B | 2026-09-23 01:29:59 | `3403024` |

**Outcome:** `BM-END,...,exit,COMPLETE,...,trap_code,0,unrecov,0`. LIMTOP took 208 s. One trial aborted by design:
`BM-ABORT,...,motor,RIGHT,incre,245_000_000,reason,ABS_CURRENT,value,3_599,scope,TRIAL`.

**Banner, checked first:** `src_rev,33,fmt,19,part,LIM`, `drv_rev,7`, `BM-CLIPTEST,...,judge_ok,TRUE`, and all 80 `BM-CLIP`
read `duty_max,27_648`.

---

## §1 Headline

| Learning | The number that carries it |
|---|---|
| ⭐ **The moved power table reaches the drive through the public API** | `R18-DUAL-POWERMAP-M` PASS both motors: ±100 holds ±165,000,000, ±1 holds ±100,000 |
| ⭐ **The driver's following reading is right when the wheel falls short** (never measured before) | `R18-DUAL-FOLFALL-M` PASS, gap 0: the wheel at 2–4 %, the driver reading 3–4 % |
| …and when it follows | `R18-DUAL-FOLLOW-M` PASS, gap 0, 75 rungs |
| The path limiter's fraction agrees at the shortfall (A-8's not-following case, lifted) | `permille` 24–78 against `d_pct` 3–4 |
| A 1 A limit nearly stalls a wheel commanded into field weakening (the prediction was 76–80 %) | `h_pct` 2–4, field walked to 6–19 × 10⁶ |
| RIGHT forward slips between 235 and 245 × 10⁶, now for the third run running | ≥ 10 A for ≥ 8 ms, peak 3,495 mV (~23 A); the harness abort stopped it |
| No regression below the ceiling | rungs 3–8 within ±10 % or ±5 mV of Visit 9 run 2; duty within 0.2 % |

---

## §2 The abort (root cause first)

```
BM-RUNG,...,RIGHT,incre,235_000_000,result,OK ... rate_x10,6_293,pred_x10,6_280
BM-ABORT,seq,587,...,RIGHT,incre,245_000_000,reason,ABS_CURRENT,value,3_599,scope,TRIAL
BM-RUNGTR,...,incre,245_000_000,from_incre,235_000_000,...,tr_err_pk,113,tr_i_pk,3_495,...,why,ABORTED
BM-RUNGHL,...,incre,245_000_000,tr_lag,9,tr_cap,23_362,...,drv_incr,218_595_176,why,ABORTED
```

The step from 235 to 245 × 10⁶ took RIGHT forward out of its field-weakened synchronism. `err` reached 113, the
lag limiter held 9 times, and the field walked back to 218.6 × 10⁶. The current stayed at or above 10 A for the 4
consecutive samples the harness's abort needs, then stopped. The cause is the slip, not the harness. The same
wheel-direction slipped at Visit 9 on both builds (245 on the old ceiling with a small peak, 235 on the new one with
a 3,718 mV single sample). On this run it was sustained. The abort ended that climb (`edge_why,NOWIN`), so RIGHT
forward's over-command step and power check did not run.

## §3 The measurements, against the sheet

| Id | Result | Verdict |
|---|---|---|
| `R18-DUAL-POWERMAP-M` | LEFT n 4, RIGHT n 2; every `BM-POWER` `held,TRUE`, e.g. `power,100,expect,165_000_000,cmd_incr,165_000_000,...,follow_pct,100` | **PASS** both |
| `R18-DUAL-FOLLOW-M` | measured 0 (gap in points), n 38 / 37 | **PASS** both |
| `R18-DUAL-FOLFALL-M` | measured 0, n 2 / 1 | **PASS** both |
| FOLFALL's population exists | `BM-FOLLOW,...,kind,OVER`: LEFT −245 `h_pct,3,d_pct,3`; LEFT +245 `h_pct,2,d_pct,3`; RIGHT −245 `h_pct,4,d_pct,4` — all < 90 | **Yes**, 3 of the 4 planned (RIGHT forward did not run, §2) |
| `BM-OCLIM` | `set_a,1,peak_a,40,cont_a,27,restored,TRUE` ×3 | **PASS** |
| `R18-DUAL-PWMCLIP-M` | room 2 / 2 | **PASS** |
| No regression, rungs 3–8 | 24 pairs; the largest, LEFT reverse at 40–80, +10.6 to +12.3 % = 1.0–2.3 mV, inside ±5 mV; duty within 0.2 % | **PASS** |
| `R18-DUAL-TOPSPD-M` | 245 / 235 | PASS (coverage, not evidence) |
| `R14-DUAL-TRACES-M` | NOMEAS | by design |
| `R18-DUAL-NOSTALL-M`, `-DBGMASK-M` | PASS, PASS | — |

**The negative limb is strong.** The shortfall it was judged on is 96–98 points, so a reading stuck at 100 would
have missed by the whole of that, not by the 10–20 points the sheet expected.

⚠ **The sheet's prediction for the 1 A step was wrong.** It said 185–195 × 10⁶, about 76–80 % of the command. The
wheel fell to 2–4 %. The prediction was built from the DC-link current, but the fold-back limits an estimate of
*phase* current, which reads far higher than the DC current wherever the modulation is low. So once the limit bit,
it kept biting all the way down. The construction worked. The arithmetic behind the number did not.

**Also read:** `follow_pct,100` at ±100 on both motors. At ±1, `drv_incr` still read ±164,950,000–165,000,000 when
read, because the check reads at once and the field was still ramping down from 165 × 10⁶, as designed. After the
step the field settled at the rotor (`drv_incr` 6–19 × 10⁶) and `short` read FALSE: the lag limiter had stopped
holding once D-5 walked the field down.

---

## §4 What this means for the driver

**What it now DOES.** DRIVER_REV 7's limits are confirmed in the drive. `power` 100 is 165 × 10⁶ (+12 %), `power`
1 is 100,000, and the clip-free duty ceiling holds with 2 counts of room. Nothing changed below the ceiling. «#3605»
is complete.

**What it now KNOWS.** ⭐ **Front 3 moves on this run.** The driver's own following reading, the rpm window against
its derived command (R18.1, integrated at `31c8b91`), is certified falling as well as holding, against an
independent count. Until now that negative limb had never been measured anywhere (Visit 7c C-2, PL-98). The path
limiter's fraction agrees with it at a real shortfall, which part D's stall has never provoked on this rig (PL-106).

⚠ **What this does NOT license:**
- **Trusting `short` as "falling short now".** It means "the lag limiter held in the last 32 ms", and it clears once
  the field has walked down to the rotor, even at 3 % of command. D-6 acts on it at once and releases slowly, which
  is the design. How that release behaves under a one-sided load is the floor run's to show (Watch).
- **Any claim about the new ceiling under load** (E5).

## §5 What this changes about the next run

- **PL-106 gains a construction.** An over-command under a 1 A limit drove a lifted wheel to 2–4 % of command
  without a fault. That is one short step from the "commanded and standing still" state the protective stop needs,
  and the first time a lifted rig has come close. The part-D BLOCKED step should use it (over-command plus a lowered
  limit) in place of its 1 A limit at power 50, which never crosses.
- **`dual-limits-top` is not needed again** unless the limits move. RIGHT forward's slip at 245 is repeatable, so
  a future climb should expect the abort there.
- **The floor run (E5)** carries the loaded margin under 165 × 10⁶, the `ramp_down` 100,000 stop (PL-109), and
  D-6's release under a one-sided load.

## §6 Findings register

| Id | Finding | Disposition |
|---|---|---|
| G-1 | The moved power table reaches the drive | **Closed** («#3605») |
| G-2 | The driver's following reading is right falling and holding | **Closed**: Visit 7c C-2 / PL-98 (3) discharged («#3597») |
| G-3 | A 1 A limit under an over-command nearly stalls a lifted wheel | **Punch list** PL-106, as its construction |
| G-4 | RIGHT forward's slip between 235 and 245 is repeatable, and now sustained ≥ 10 A | **Punch list** PL-108, updated |
| G-5 | The 1 A prediction was built on DC current; the limiter acts on estimated phase current | **Closed**, recorded here and in PL-98 (3) |
| G-6 | `short` clears once D-5 settles, even at 3 % of command | **Watch**: D-6's release under load, at the floor run |

## §7 What is NOT established

- **FOLFALL on RIGHT forward.** It did not run (§2). The limb holds on the other three wheel-directions.
- **The protective stop.** 2–4 % is not zero, so G-3 is a construction to try, not a result.
- **Anything under load.**

## §8 FRONTS

```
FRONTS  (after this pass)
  completion   driver last changed 1 commit ago (3403024); the moved limits are confirmed in the drive
  information  0 loads ready and unrun; the next measurement needs the floor run (E5, «#3591», blocked on «#3585»)
  robustness   ADVANCED -- the driver's following reading is certified falling as well as holding; halls y current y back-EMF n follow y
```

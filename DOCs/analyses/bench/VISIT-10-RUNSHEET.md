# Visit 10 — run sheet, pass 6 (NOT READY: being prepared)

**Task:** «#3613» runs it. **Plan:** `BENCH-READINESS-SPRINT-PLAN.md`, R20.6.

**Done so far:**
- Pass 3 (09-24): certified the fault fallback, the graded short (BRAKE_PCT 10), the hold's rise, the start checks, the
  REST window and the rest-zero band.
- Pass 4 (09-25 11:41): certified the winding check (363–460 mΩ) with its negative. The right died on its first drive
  (PL-120), and the walk FAILed falsely once (PL-137).
- Pass 5 (09-25 19:52), [evaluation](2026-09-25/VISIT-10-PASS5-EVALUATION.md):
  - the right certified its fault cells (RESTFLAT 1 mV over, PL-139);
  - start refusal, opt-out and retry certified;
  - PL-137's cause was found and fixed (09e128d);
  - PL-120 struck twice after driving and outlasted a reload, so T0-25 was voided.

---

## ⛔ Not ready — what remains before this sheet carries commands

- «#3622»: PL-141's fix. The path limiter must not throttle a healthy start from rest. It changes what `dual-d`'s
  EV-PATH can certify.
- PL-138's design: decide whether the gate-pin window rides this pass.
- Then write the declared attributes and cells, and confirm each can fail.

## Draft loads (from the pass 5 evaluation §8; each is dropped only with a stated reason)

| Order | Tier | Why it is on the pass |
|---|---|---|
| 1 | `t0-stopreason` | Every SR_* and EV_* cell, never measured. First, so a wheel dead at load is seen fresh. It falls back to the LEFT if the right is refused (t0 src_rev 19) |
| 2 | `dual-start` | Certifies PL-137's fix: WALK 0/10 per wheel, no leg ending OTHER. PL-140's `BM-FRONTST`. `BM-RPROBE` if PL-120 strikes |
| 3 | `dual-start-swapneg` | The fix's other side: the healthy RIGHT passes all 3 walks while the swapped left fails |
| 4 | `dual-d` | ORDERED..DIRSIGN, the LIMIT segment, EV-FOLDBACK/CLIMIT/PATH (owed); PL-141's negative once «#3622» lands |

**Dropped, with reasons:**
- `dual-fault-rightfirst`: the right certified at pass 5. RESTFLAT rides with the next fault-response change.
- `dual-start-phaseneg`: certified 3/3, 6/6 and 3/3 on an unchanged path.

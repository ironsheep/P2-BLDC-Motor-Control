# Visit 9b — run sheet (the moved limits confirmed; the driver's following reading certified, both limbs)

**Tasks:** «#3605» (the limits moved from Visit 9) and «#3597» (the FOLLOW certification moved out of the scan).
**Why this pass:** Visit 9 ([evaluation](2026-09-23/VISIT-9-EVALUATION.md)) moved three limits in the driver, and
DRIVER_REV 7 has never run. The same pass is the first place the driver's following reading can be judged falling as
well as holding.

---

## Check the banner before reading anything else

| Every `BM-BANNER` / `BM-BUILD` / record must read |
|---|
| `src_rev,33` · `fmt,19` · `drv_rev,7` · part `LIM` · segments `PREFLT`, `LIMTOP` only |
| every `BM-CLIP` `duty_max,27_648` (the clip-free ceiling is now the default build) · `BM-CLIPTEST ... judge_ok,TRUE` |

---

## The visit, declared

| | |
|---|---|
| **Purpose** | **Certification.** The moved power table reaches the drive, the clip-free duty ceiling holds as the default, and the driver's following reading is right when the wheel follows **and** when it falls short. |
| **Hardware risk** | As Visit 9's climb: each wheel and direction to 245 × 10⁶ (about 440 rpm), where it follows by field weakening at 2–3 A, or may slip and be recovered. **New:** after each climb the wheel is held at that command with its current limits **lowered to 1 A**, which only lowers current, then put back and read back. Then full power and least power through the public API. The 10 A abort applies throughout. Wheels up, no hands near the rig. Panic: physical battery disconnect. |
| **Who can observe** | Nobody needs to. One observation is worth having if you are near: during the four 1 A holds, does the wheel **slow audibly and smoothly**, or does it stutter? Observation, not verdict. |
| **Runs that carry state** | None. `maxSpeed` and the current limits are read first and put back after (`BM-OCLIM`). |
| **Run length** | **About 4 minutes (ESTIMATED):** Visit 9 run 2's climb took 186 s, plus 4 × (4 s over-command + 4 s at full power; least power is read at once). |
| **Repeatability** | Repeatable and idempotent. |
| **Variant matrix** | One build of `test_bench_dual.spin2` part LIMITS with `-D LIMITS_TOP_ONLY`, on the Visit 9 rig (Rev B, the paired 6.5in hubs, 18.5 V, 270 MHz). One log. |

**New information:** DRIVER_REV 7's power table and floor through the API (never run); the driver's following
reading in a not-following state (never measured with a full window, anywhere); the fold-back at a limit a lifted
wheel actually crosses on the new drive (Visit 8's FOLDBACK passed at 695 mA against 8 A). **Carried:** the climb,
because it is the load the other three stand on and it re-certifies the new default's PWM room.

---

## The command

```bash
tools/bench-run.sh dual-limits-top
```

---

## What each load decides, and how each can fail

| Id | Judged by | Criterion | Fails if | Negative case |
|---|---|---|---|---|
| **`R18-DUAL-POWERMAP-M`** | cell, per motor | `power` ±100 holds exactly ±165,000,000 and ±1 holds exactly ±100,000 (`BM-POWER` `held`) | the table did not reach the drive, or `driveAtPower()` maps it differently | **The table it replaced** (147,000,000 / 544,628) fails it exactly, by construction |
| **`R18-DUAL-FOLLOW-M`** | cell, per motor | among readings the harness says FOLLOWED (≥ 98 %), worst \|driver − harness\| less quantisation ≤ 5 points | the driver's reading disagrees with the wheel while it follows (C-1's defect read 89) | a reading stuck low; C-1's pre-fix sign defect |
| **`R18-DUAL-FOLFALL-M`** | cell, per motor | among readings the harness says did NOT follow (< 90 %), the same ≤ 5 points | the driver's reading does not fall with the wheel | **a reading stuck at 100 fails by the whole shortfall** (~20 points on Visit 9's figures) |
| **FOLFALL's population exists** | `BM-FOLLOW,kind,OVER` | every over-command step reads `h_pct` < 90 | the 1 A limit did not force a shortfall, so the construction failed (a finding about the construction, not a PASS or FAIL of the reading) | Visit 9: without the limit, 3 of 4 read ~100 |
| **The limits restored** | `BM-OCLIM` | `restored,TRUE` on all four | a later measurement ran under 1 A | — |
| **`R18-DUAL-PWMCLIP-M`** | cell, per motor | least room ≥ 0; report the room (Visit 9: 2) | the default build clips | `BM-CLIPTEST`, as at Visit 9 |
| **No regression below the ceiling** | `BM-RUNG2` net current, rungs 3–8, against Visit 9 run 2 | within ±10 % or ±5 mV | the move changed the drive below the ceiling | — |
| `R18-DUAL-TOPSPD-M` | cell | as Visit 9 | as Visit 9 | coverage, not evidence (a regression guard) |
| `R14-DUAL-TRACES-M` | cell | **NOMEAS by design** (the build takes no trace) | — | — |
| `R18-DUAL-NOSTALL-M`, `-DBGMASK-M` | cells | as every part | as every part | as every part |

**Also read, not judged:** `BM-POWER` `follow_pct` at `power` ±100, which should be ~100. At ±1 no window is run
(under one hall edge a second), so `follow_pct` prints NA; the check there is the held increment alone. `BM-FOLLOW` `permille` beside `d_pct`
on the OVER steps is A-8's not-following comparison, which part D's stall has never been able to provoke (PL-106).

**What this pass cannot measure:** any loaded margin under the new ceiling. That is E5, the floor run.

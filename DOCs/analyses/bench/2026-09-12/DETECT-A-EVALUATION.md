# Bench Pass 1, steps 5 and 6 — detection on the Rev A boards, compared with Rev B

**Runs:** `src/test_bench_detect.spin2` on the Rev A boards, 2026-09-12, source `d4f9d39`.

| Step | Log (this folder) | Build | Motors |
|---|---|---|---|
| 5 | `debug_260912-170246.log` | `detect-lib` — no driver cog | connected, never commanded |
| 6 | `debug_260912-170646.log` | `detect-phase2` — driver cog started at zero and stopped | **unplugged** |

**Comparison run:** Rev B boards, step 3,
[`../2026-09-11/debug_260911-210229.log`](../2026-09-11/debug_260911-210229.log) — the same
`detect-phase2` build, so the two are like-for-like.

**Both A logs are valid** (MEASURED): `BD-BANNER` present; `BD-CFG cfg_id BENCH`, `left_base 32`,
`right_base 16`; `BD-CLK match 1`; all six `BD-ENUM match 1`; `BD-GATE` agrees with
`BD-BUILD phase2_compiled` (`NOTCOMPILED`/0 in step 5, `COMPILED`/1 in step 6); the three
`BD-CAL` values agree within each log (400, and 408); `BD-DONE` present.

**Provenance tags:** MEASURED = a log record · DERIVED = my reading or inference · STEPHEN = his
words.

---

## The sweep matrix, per group

`sum` is the 500-read pin sum; `vrd` the verdict. Each cell is 32 repeats, except the running-cog
cells (8); spread within every non-running cell is at most 5.

| Sweep | Condition | P16_P31 on A | P16_P31 on B | P0_P15 (empty), A | P0_P15 (empty), B |
|---|---|---|---|---|---|
| 1 | cold | 0 **REVA** | 97–99 **REVB** | 500 NODET | 500 NODET |
| 2 | cold, pinclear first | 0 REVA | 97–101 REVB | 500 NODET | 500 NODET |
| 3 | P0 driver **running** | — | — | *void — `agree 0`* | *void — `agree 0`* |
| 4 | P0 driver **stopped** | 0 REVA | 93–98 REVB | 0 **REVA ✗** | 0 **REVA ✗** |
| 5 | P0 stopped, **pinclear first** | 0 REVA | 93–97 REVB | 500 **NODET ✓** | 500 **NODET ✓** |
| 6 | P16 driver **running** | *void — `agree 0`* | 1–3 REVB (`agree 1`) | — | — |
| 7 | P16 driver **stopped** | 0 REVA | 0 **REVA ✗** | 500 NODET | 500 NODET |
| 8 | P16 stopped, **pinclear first** | 0 REVA | 93–97 **REVB ✓** | 500 NODET | 500 NODET |

P32_P47 matches P16_P31 on each rig in every sweep, apart from sweeps 7 and 8, where it is the
untouched group and reads clean on both rigs. P8_P23 reads 500 NODET throughout on both.

## What this establishes

### 1 · Clearing the smart-pin state before reading fixes detection

MEASURED on the Rev B rig, with both limbs:

- **A real board:** P16_P31 reads **0 → REVA** after its driver cog stops (sweep 7) and
  **93–97 → REVB** when the pins are cleared first (sweep 8).
- **An empty group:** P0_P15 reads **0 → REVA** after its cog stops (sweep 4) and
  **500 → NODET** when cleared first (sweep 5).
- **Per group:** in sweeps 4 and 7, only the group whose cog ran is affected.

The library's own `getBoardType()` agrees with the local replica in every non-running cell
(`agree 1`), so this is the shipped routine's behaviour, not the harness's.

### 2 · The Rev A board cannot show the defect — and that is the reason to test on B

DERIVED from MEASURED: a poisoned read returns 0, and 0 is Rev A's correct answer. Sweeps 7 and
8 are identical on A. **An A-board test of the fix passes whether or not the fix works.** The
A rig's contribution is the other limb: **clearing never changes a correct verdict** — REVA
stays REVA and every untouched group is unchanged across the NOCLR/CLR pairs, on both rigs.

### 3 · Detection is deterministic and repeatable on A

MEASURED: steps 5 and 6 give identical cold cells (sweeps 1–2) — REVA at sum 0 on both A boards,
32 of 32. STEPHEN's *"A is not one-off"* holds.

### 4 · Detection while the driver runs is void

MEASURED: three of the four running-cog cells across the two rigs have `agree 0`. Reading the
sense pin while the driver owns it as an ADC smart pin is meaningless — and pinclearing it would
destroy the running driver. **Constraint on the fix** (DERIVED): any defensive clear inside
`getBoardType()` must not run while this instance's driver cog is running.

### 5 · The four signatures

| What is at base+4 | sum | first low read (`fltix`) |
|---|---|---|
| Rev A sense pin (1 kΩ pulldown) | 0 | 1 |
| Rev B sense pin (0.1 µF discharging) | 93–101 | 47–51 |
| Nothing (empty group) | 500 | never |
| **Another board's W low-side gate input** (P28, P44) | 7–9 on A, 1 on B | 5 on A, 2 on B |

The last row is **reported as Rev B on both rigs** (P40_P55 `libvrd REVB`). No real Rev B board
reads that low, so the band between the two real signatures can reject it. That belongs to
«#3500»'s detection contract.

### 6 · `start()` returns 0 on the A rig too

MEASURED: both phase-2 starts log `start_ret 0` with `motorcog 2` (`BD-PH2 step started`) — the
«#3499» defect, reproduced on the second platform.

---

## Consequence for «#3500»

- **The fix shape is measured, not argued:** release the smart-pin state before the sense pin is
  read. `pinclear()` is the call that does it (DIR := 0 and WRPIN := 0).
- **The verify check must run on Rev B hardware.** On Rev A a broken fix passes.
- **Any clear inside `getBoardType()` must be guarded** against this instance's running driver.
- **A group overlapping another board's gate pins reads Rev B.** Rejecting sums below the real
  Rev B band is a candidate for the contract, alongside what an empty group reports.

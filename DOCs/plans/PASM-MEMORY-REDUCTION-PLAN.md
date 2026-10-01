# PASM driver memory reduction — design

> **6.0.0 sprint closed 2026-10-01: PARTLY IMPLEMENTED, STILL GOVERNS.** WP1-WP5 shipped (DRIVER_REV 41-45; cog 441 of
> 496, LUT run image 457 of 512). WP6-WP9 are not built; they are re-evaluated when the space is next needed
> (Stephen 2026-10-01: *"we can reevaluate what we need when we next need the space"*), not tracked as work. Audit: `DOCs/plans/archive/2026-10-01-BENCH-READINESS-CLOSEOUT.md`.

Status: **DESIGN ONLY. No source is changed by this document.** Every line number below is
`src/isp_bldc_motor.spin2` at tag `mem-reduce-start` (HEAD `2e1215f`, DRIVER_REV 40).

The trigger is P13 (*"it fits" is not done; headroom is a design requirement*) and P10 (*correct by
construction*). STEPHEN 2026-09-27: *"you have to do better engineering... reduce without losing any fidelity
in the algorithm implementation."* So every candidate in this plan is held to one bar: **the driver's hub
writes, pin writes and live registers stay bit-identical, pass by pass and frame by frame**, proved at the
desk (§4). Nothing here changes what the motor does, and no candidate needs a bench cell of its own.

The provenance labels are this project's own (P8): MEASURED, DERIVED, STEPHEN.

---

## 0. The rules the budget obeys (from p2kb, P7)

- Code runs from cog RAM or LUT RAM at the same speed: 2 clocks per instruction and 4 per branch
  (`p2kbPasm2ExecutionModes`). **Instruction operands address cog RAM only.** The ALTx forms build a 9-bit
  register address, `(S + D) & $1FF` (`p2kbPasm2Altd`), so registers, constants and ALTx tables must be in cog
  RAM. Code can live in either memory. LUT can also hold data that is read with `RDLUT` (3 clocks,
  `p2kbPasm2Rdlut`).
- `SETQ2` + `RDLONG 0, S` block-loads up to 512 longs into LUT from any hub address in a register
  (`p2kbPasm2SetqBlockOps`, `p2kbPasm2Rdlong`). This is the overlay mechanism the driver already uses.
- **LUT use is max(start image, overlay) + resident.** The start sequence and the planner overlay occupy the
  same LUT window at different times. The resident code is paid for once.
- Hub execution runs at 2 clocks per sequential instruction. Every branch costs 13 to 20 clocks, and FIFO
  instructions are forbidden (`p2kbPasm2CogHubExecution`). In a Spin2 object, bare `ORGH` code is relocated at
  run time and uses relative addressing (`p2kbSpin2AsmOrgh`), so cog code must reach it through a pointer
  register.
- A debug interrupt saves cog `$000..$00F` to hub on entry and restores it on exit (`p2kbArchDebugInterrupt`).
  Registers placed at `$000..$004` are therefore safe in `-d` builds as well.

---

## 1. THE MAP

**MEASURED.** The addresses come from the compiler listing of a scratch copy of the tree, with
`pnut-ts -l <scratch>/memmap/src/isp_bldc_motor.spin2` (symbol table, listing lines 1046-1268). Each
`DAT_LONG VALUE` carries the cog/LUT address in its top 12 bits. Group sizes are the differences between
consecutive label addresses. "When" gives the phase in which the group runs or is read:

- *start*: once, before the drive loop.
- *frame*: every PWM frame at 44 kHz.
- *pass*: every drive pass, every 23 frames.
- *stage n*: the planner's stage n, one per frame on frames 1-9 after a pass.
- *event*: only on that event.

### 1.1 Cog RAM — 492 of 496 (`$000`-`$1EB`)

| Addr | Longs | Group (source line) | Kind | When |
|---|---:|---|---|---|
| $000-$004 | 5 | `driver` entry: state, LUT start-image load, jump (7485) | code | start only |
| $005-$00A | 6 | `drvMotor` head: `lag_s`, e-stop test (7536) | code | pass |
| $00B-$010 | 6 | `.eStop` (7553) | code | event: e-stop |
| $011-$019 | 9 | `.noEStop`: command take, fault latch (7560) | code | pass |
| $01A-$01C | 3 | `.resetFault` (7575) | code | event |
| $01D-$022 | 6 | `.notFaulted`: rest dispatch (7579) | code | pass |
| $023-$025 | 3 | `.fromRest` / `.running` (7605) | code | pass |
| $026-$02A | 5 | `.endAtZero` (7614) | code | event: arrival at rest |
| $02B-$02E | 4 | `.justIncr`: LAG_HOLD gate (7625) | code | pass |
| $02F-$042 | 20 | `.endRqst`: publish, plan kick, `passEnd`, PL-55 duty ceiling (7633) | code | pass |
| $043-$046 | 4 | `.capDone`: pass timing, CT1 (7657) | code | pass |
| $047-$09E | 88 | `.ctlMotor`: frame timer and `wait4adc` call (2), ADC read and scale (16), CORDIC phase levels (11), min/max re-centre (10+5), bias (3), bridge and dead-gap writes (14), hall read (7), deltas (4), hall integrity (16) (7694) | code | frame |
| $09F-$0B3 | 21 | `.hallCounted`: params block read, direction, `err_`, fault test (7813) | code | frame |
| $0B4-$0C0 | 13 | `.noFault`: current fold-back (7839) | code | frame |
| $0C1-$0CA | 10 | `.servoTrim` (7883) | code | frame |
| $0CB-$0DC | 18 | `.dutyLimits`, anti-windup, status write, planner hook (7893) | code | frame |
| $0DD-$0DE | 2 | `.loop` (7920) | code | frame |
| $0DF-$0E3 | 5 | `.clearRun` (7941) | code | event |
| $0E4-$0EB | 8 | `.checkstopfloatoff` + `checkstop` (7948) | code | start, rest transitions |
| $0EC-$0EE | 3 | `wait4adc` (7959) | code | frame + start |
| $0EF-$0F2 | 4 | `loadOverlay` (7964) | code | start only (last act) |
| $0F3-$102 | 16 | `planFp` (7970) | code | stage 3/6/9, or early completion |
| $103-$12F | 45 | `planCorner` (7986) | code | stage 1/4/7, corner case |
| $130-$13A | 11 | `initAngleFmHall(C)` (8036) | code | from rest, `checkstop`, fault re-sync |
| $13B-$148 | 14 | constants (8052): `all_pins`, `pwmt`, `pwmn`, `fram`, `numerator`, `sync_required`, `lutCodePtr`, `planCodePtr` (start only); `drive_pins`, `bias`, `third`, `maxNeg`, `adc_pins`, `adc_fram` (run) | constant | mixed |
| $149-$14B | 3 | `adc_modes` (8078) | table | start only |
| $14C-$15B | 16 | `deltas`, 64 bytes (8091) | table | frame |
| $15C-$16B | 16 | `hall_angles` (8120) | table | frame + `initAngleFmHall` |
| $16C-$16F | 4 | `tmpX`, `tmpY`, `fold_net`, `calibPeriod` (start only) | register | |
| $170-$172 | 3 | `drvrSrtTix`, `ctrlSrtTix`, `ctrlEndTix` | register | frame / pass |
| $173-$175 | 3 | `tgt_incr`, `sv_tgt_incr`, `drv_incr` | register | pass |
| $176-$17A | 5 | `jrk_e`, `jrk_s`, `jrk_j`, `jrk_lim`, `jrk_x` | register | pass (+ `xStar` I/O in the planner) |
| $17B-$17E | 4 | `angle_`, `prior_angle`, `fwdrev`, `bridge` | register | frame |
| $17F-$182 | 4 | `lowy_tbl`, `coast_y`, `lowy_brake`, `lowy_probe` | register table | undriven frames |
| $183-$188 | 6 | `fault_stop`, `force_seen`, `brake_frame`, `fault_clr_seen`, `curr_stop`, `lag_s` | register | pass / frame |
| $189-$18D | 5 | `duty_cap_`, `duty0`, `incr0`, `duty_ff`, `servo_acc` | register | pass / frame |
| $18E-$19D | 16 | 14 pin registers, `hall_port`, `hall_shift` | register | frame |
| $19E-$1A5 | 8 | `gio_levels`[4], `scl_levels`/`vio_levels`[4] | register | frame |
| $1A6-$1C1 | 28 | `params_ptr_` + the 27-long parameter mirror (ABI) | register | frame |
| $1C2-$1D9 | 24 | the 24-long status mirror (ABI) | register | frame |
| $1DA-$1EB | 18 | `plan_stage`, `pl_v` … `pl_q` (14), `sc_v`, `sp_P`, `sp_F` | register | stages |

**Reconciliation:** code 5+66+152+5+8+3+4+16+45+11 = **315**; constants and tables 14+3+16+16 = **49**;
registers **128**. 315 + 49 + 128 = **492** (SP_F at $1EB). ✓

**Dead after start (MEASURED by reading every reference):** 21 cog longs are never read or executed once
`loadOverlay` has jumped to `drvMotor`:

| Longs | Items |
|---:|---|
| 5 | the entry code |
| 4 | `loadOverlay` |
| 1 each | `all_pins`, `pwmt`, `pwmn`, `fram`, `numerator`, `sync_required`, `lutCodePtr`, `planCodePtr`, `calibPeriod` |
| 3 | `adc_modes` |

### 1.2 LUT — 507 of 512 (`$200`-`$3FA`)

| Addr | Longs | Routine (line) | When |
|---|---:|---|---|
| $200-$280 | 129 | start sequence `lutCodeStart` (8319-8512): pins, hall port, gate parking, PWM frame, ADC GIO/VIO calibration, ATN park, state zeroing, first param read, `checkstop`, jump to `loadOverlay` | start only, then overwritten |
| $281-$289 | 9 | `gettgtincr` (8523) | pass |
| $28A-$296 | 13 | `countIllegal` (8534) | frame on an illegal entry; start once |
| $297-$2A5 | 15 | `driveinit` (8550) | **start only** |
| $2A6-$2AE | 9 | `passEnd` + `feedForward` (8578) | pass |
| $2AF-$2B8 | 10 | `holdDecay` (8593) | pass, when lag-held |
| $2B9-$312 | 90 | `jerkStep` (8634) | pass, not at rest |
| $313-$333 | 33 | `undrivenPins` (8730): 14 general + 19 `.probe` | frame, bridge undriven |
| $334-$33E | 11 | `restBridge` (8765) | pass, at rest |
| $33F-$343 | 5 | `driveFromRest` (8778) | event |
| $344-$359 | 22 | `faultResponse` (8785) | event: fault frame |
| $35A-$35E | 5 | `estopBridge` (8809) | event: e-stop latch |
| $35F-$380 | 34 | `driverRelease` (8816) | event: release, terminal |
| $381-$395 | 21 | `xStar` (8879) | pass (`jerkStep`) + stages A and C |
| $396-$3C5 | 48 | `run` (8912) | stages |
| $3C6-$3FA | 53 | `planStage` (8980) | stages 1-9 |

**Reconciliation:** 129+9+13+15+9+10+90+33+11+5+22+5+34+21+48+53 = **507** (`lutCodeEnd` $3FB). ✓

### 1.3 The planner overlay — 126 of 129 (`$200`-`$27D`, over the spent start sequence)

| Addr | Longs | Routine (line) | When |
|---|---:|---|---|
| $200-$226 | 39 | `planA` (9074), incl. `.done` | stage 1/4/7 |
| $227-$247 | 33 | `planB` (9114) | stage 2/5/8 |
| $248-$26B | 36 | `planC` (9148) | stage 3/6/9 |
| $26C-$270 | 5 | `planSat` (9183) | saturation |
| $271-$27D | 13 | `rampOut` (9192) | stages B, C |
| $27E-$280 | 3 | free, below `gettgtincr` | |

**Reconciliation:** 39+33+36+5+13 = **126**. ✓

### 1.4 Frame budget today

MEASURED with `frame_clocks.py` and `desk_driverplan2.py 1 600` (E) on the current source. The model counts
2 clocks per instruction, 4 per taken branch, and a CORDIC result 55 clocks after its issue. Every branch is
counted as taken, so the figures are upper bounds.

- **Frame work:** ≤ 699 clocks. That is the body ≤ 529, `undrivenPins` ≤ 74, `countIllegal` ≤ 28 and
  `faultResponse` ≤ 68.
- **Worst planner stage, stages 1-9:** 1,296 / 1,052 / 1,726 / 1,324 / 1,052 / 1,740 / 1,328 / 1,052 /
  1,750 clocks.
- **Drive pass:** ≤ 1,184 clocks. The drive-pass frame carries no stage: ≤ 1,883 clocks in all.

| Clock | Frame | Stage frame (699 + 1,750) | Pass frame (1,883) |
|---|---:|---:|---:|
| 160 MHz | 3,636 | 2,449 (67 %) | 1,883 (52 %) |
| 270 MHz | 6,136 | 2,449 (40 %) | 1,883 (31 %) |

---

## 2. CANDIDATES

Longs are DERIVED by reading the source instruction by instruction, and clocks come from the same 2/4/55
model. **The compiler listing is the authority**: each work package reads its real figures from `pnut-ts -l`
and records them in the `fit` comments, as the current comments do. Where a candidate depends on flags being
dead, §4 names the liveness proof.

### C1. Reuse the start-only cog longs as run-time registers (registers live in disjoint phases)

- **What.** The 21 longs listed in §1.1 as dead after start become the homes of registers that are first
  written only after the drive loop starts. Each gets a second label at the same address.
  - The file already does this. `vio_levels` / `scl_levels` (8211) is the precedent.
  - Examples: `pl_v` labels `$000`; `pl_Dl`..`pl_f` label `loadOverlay`'s four longs; `sp_P` labels `lutCodePtr`.
- **Hosts.** The candidate hosts must never be written or read during start. These qualify:
  - the 14 `pl_*` registers (not `plan_stage`, which the start sequence zeroes);
  - `sc_v`, `sp_P`, `sp_F`;
  - the five `jrk_*` registers.

  That is 22 names for 21 slots. `calibPeriod` (start only) and a run-only register share one slot the
  same way.
- **Frees** 21 cog longs from the `res` block.
- **Clocks** 0. **No instruction changes.**
- **Risk: low.** The invariant is purely static: every read of a dead long happens on the start path before
  any write to its alias. The start path is straight-line apart from the `.pin` loop, the `wait4adc` spins and
  its calls. The debug ISR saves and restores `$000..$00F` (§0). Two things must stay excluded:
  - `planCodePtr`, if C8 wants a run-time pointer (C8 uses its own `relCodePtr`, so it does not);
  - `adc_fram` / `adc_pins`, which `driverRelease` uses. They are not candidates.

### C2. One run image: every post-start LUT routine joins the overlay

- **What.** The LUT holds a **start image** until `loadOverlay`, then a **run image**. Today the run image is
  only the 126-long planner core, and 378 longs of run code are resident underneath it. Proposed:
  - **Start image** = the start sequence + `driveinit` (15, start only). 144 longs.
  - **Run image** = every routine that only runs after start: `gettgtincr` … `planStage`, plus the planner
    core. 476 longs, loaded by the existing `loadOverlay` (count 476 − 1).
  - **`countIllegal`**, the one routine both phases call (8480 at start, 7806 per frame), moves to cog RAM:
    +13 cog. The start image is fully hidden under the run image, so it costs no LUT.
- **Frees** LUT 507 → **476** (−31), for cog +13. It also dissolves the "126 of 129" overlay squeeze by
  construction: the planner core is now ordinary run-image code.
- **Clocks.** 0 per frame. The one-time load at start grows by ~350 longs (~1.3 µs at 270 MHz). Both wheels
  load the same size after the same ATN release, so their lockstep is unchanged.
- **Risk: low.** No instruction changes, only relocation. The invariant is a partition: the call graph from
  the start entry reaches no run-image address, and the run image's call graph from `drvMotor` reaches no
  start-image address. §4 proves both mechanically.
- **Spin2.** `planCodePtr := @runCodeStart` (4367). The `fit` lines and the §4 *Cog and LUT memory* section
  of the theory of operations follow.
- **Depends on C1** for cog room: 492 + 13 is over 496.

### C3. Frame- and pass-loop peepholes (cog)

Each item is an exact instruction-level equivalence. The frame and pass items save 14 longs in all.

**(a) Re-centring min/max** (7739-7749): `mov tmpX,u / fles tmpX,v / fles tmpX,w`, and the same with `fges`
for the maximum.

- Same value: `cmps`+`if_nc mov` is exactly signed min (`p2kbPasm2Fles`).
- The C the old `cmps` wrote is dead up to `.hallCounted`'s `cmpm wcz`, and `undrivenPins` writes C only.
- **−4 longs, −8 clocks/frame.**

**(b) Fold the bias and the dead gap into the one centre offset** (7751-7780):
`add tmpX,tmpY / sar #1 / sub tmpX,bias / sub tmpX,dead_gap_ / sub drive_x_,tmpX ×3`. Then per phase:
`if_z wypin drive_x_,low / sub drive_x_,dead_gap_ / if_z wypin drive_x_,high`.

- Same Y values in the same order: mod-2³² arithmetic.
- The final `drive_x_` equals the level, as the status run reports it.
- `undrivenPins`, called between, reads no `drive_x_`.
- **−4 longs, −8 clocks/frame.**

**(c) Fold-back compare without `fold_net`** (7850-7860):
`mov tmpX,duty_ / fges tmpX,duty_floor_ / sca tmpX,i_limit_k_ / mov tmpX,0-0 / add tmpX,sense_zero_ /
cmps sense_i_,tmpX wcz`.

- The fold condition `max(d,0) > t` equals `d > t` for any `t ≥ 0`. SCA's result is an unsigned 16×16>>16
  (`p2kbPasm2Sca`), so t ≥ 0 holds.
- Moving `sense_zero_` to the other side is exact at mV magnitudes.
- The C/Z that differ, only when d < 0 and t = 0, are dead before `.dutyLimits`' `fles wc`.
- **−1 long, −1 register, −2 clocks.**

**(d) `drvMotor` head** (7538-7552):

- `testb drv_incr,#31 wc / negc lag_s,err_` (`p2kbPasm2Negc`), and `tjz e_stop_,#.noEStop` for the
  `or wz / if_z jmp`.
- TJZ writes no flag (`p2kbPasm2Tjz`), and the Z it replaces is rewritten at `.noEStop` and `.eStop`.
- **−2 longs.**

**(e) `ctrlEndTix`** (7661-7662): `addct1 ctrlSrtTix,cfg_ctcks_`.

- ADDCT1 writes the sum into D (`p2kbPasm2Addct1`).
- `ctrlSrtTix` is dead after `.capDone`'s `sub`.
- **−1 long, −1 register.**

### C4. The hall delta table as nibbles that also carry the event class (cog, Spin2 `init`)

- **What.** `deltas` becomes 8 longs of nibbles, indexed by the unchanged `altgn hall_,#deltas`
  (`p2kbPasm2Altgn`: register = base + `hall_[5:3]` = old, nibble = `hall_[2:0]` = new). Each nibble holds:
  - bits 1:0: the step −1/0/+1 (`signx #1`, `p2kbPasm2Signx`);
  - bit 2: *a legal change with no step* (`hall_missed_`);
  - bit 3: *a change into `%000`/`%111`* (`countIllegal`).

  The 16-instruction integrity block (7797-7812) and the byte lookup (7789-7792) become 11 instructions:
  `altgn / getnib tmpX / mov tmpY,tmpX / signx tmpY,#1 / add pos_,tmpY / testb tmpX,#2 wc / if_c add
  hall_missed_,#1 / testb tmpX,#3 wc / if_c mov tmpY,hall_ / if_c and tmpY,#%111 / if_c call #countIllegal`.
- **The classes are static functions of (old, new, delta).** They are exactly the PASM's rules today:
  - unchanged → nothing;
  - step ≠ 0 → nothing;
  - new ∈ {000, 111} → illegal entry;
  - old ∈ {000, 111} → nothing;
  - else → missed.

  Spin2 computes them once at `init()` (4345-4354). It packs straight from the source byte table with the
  test swap applied on the fly (`hallBitsSwapped`), so neither `swapHallTables` (4269-4282) nor the stack
  needs a 64-byte staging buffer.
- **The user-facing byte tables `deltas65` / `deltas4k` stay the authoring format** (`ADDING_MOTOR.md`
  unchanged). A step outside −1/0/+1 cannot be packed. Every shipped table is inside that range, and the
  theory of operations defines the table that way. The §4 harness checks the DAT tables statically, so no
  run-time error path is added.
- **Frees** 8 (table) + 9 (code) = **17 cog**.
- **Clocks.** +2 on an ordinary frame; an event frame is about equal.
- **Risk: medium** (PASM + Spin2), and the proof is exhaustive (§4).

### C5. The planner, consolidated

**(a) `planStage` as one parameterised pass** (8980-9032, 53 longs). The three *plans* are the part worth
parameterising: the m = 1 plan, the low end and the high end differ only in their prologue and fold.

- Encode `plan_stage` as `end << 2 | part`:
  - `part` 1 = A, 2 = B, 3 = C;
  - `end` 0 = m1, 1 = lo, 2 = hi;
  - `.endRqst` still writes 1.
- The dispatch becomes `mov pl_t,plan_stage / and pl_t,#3 / jmprel pl_t`. The table is `ret`, `jmp .a`,
  `jmp .b`, with `.c` falling through (`p2kbPasm2Jmprel`).
- One `.a` sets `a' = a + k·Jx`, k ∈ {0, −1, +1}, chosen by `testb plan_stage,#2/#3`:
  - m1 also zeroes `sp_P` / `sp_F` and `sc_v`;
  - m2 sets `v' = v + a'` and `sc_v`.
- One `.fold` adds the take pass only when `end ≠ 0`. For m1, `sc_v = 0`, so the U sum gains 0.
  - `max(0, x) = x` for the unsigned `fge`.
  - It advances with `andn #3 / add #5` and publishes at 13.
- **The same stage lands on the same frame**, so the status run is identical frame by frame. That includes
  the early completion out of A (C = 1), which folds in the same frame as it does today.
- **−10 longs** (53 → 43).
- **Clocks:** +~22 on stage 1, +~16 on stage 3, ±4 on stages 6 and 9.

**(b) `run`** (8912-8960):

- Compute `h = n(n−1)/2` straight after the (n−1)V product, while `pl_t` still holds n−1. The second
  `mov pl_t,pl_n / sub #1` goes; `|first|` and `|d|` move to `pl_q` / `pl_u`.
- Use `tjz pl_n,#.runEnd` for `cmp wz / if_z ret`.
- Every value is the same, and the scratch and flags at exit are dead in every caller (planA, planB tail,
  planC tail, planCorner).
- **−3 longs, −4 clocks per call.**

**(c) Immediates** (`p2kbPasm2Decod`, `p2kbPasm2Bmask`):

| Line | Change | Saves |
|---|---|---:|
| 9184 | `planSat mov pl_P,##PLAN_PASSES_MAX` → `decod pl_P,#20` | 1 |
| 9185 | `mov pl_Uh,##$0100_0000` → `decod pl_Uh,#24` | 1 |
| 7983 | `planFp if_nc mov pl_t,##$7FFF_FFFF` → `if_nc bmask pl_t,#30` | 1 cog |

The constants must be written as shifts of named constants so a change to `PLAN_PASSES_MAX` still flows.

**(d) `planCorner` trims** (7986-8031, 45 → 38). Each is exact.

- **B = 2α − J** is `pl_a + pl_f`. `planA` left `pl_f = α − J` (9087-9088), and `planCorner` never writes
  `pl_f`: −1.
- **The tail's `mov pl_f,pl_a / sub pl_f,jerk_dn_`** recomputes a value already there: −2.
- **`mov pl_u,pl_c / add pl_u,#1`** is `mov pl_u,pl_n`: −1.
- **8JV** is `qmul (J<<3), V` in place of `qmul V,J` plus a five-instruction 64-bit shift: −3. Exact while
  8J < 2³².
  - This rests on a proven domain, not a sample. `jerk_dn` has one writer, `applyRamps()`. It takes
    `rampsFor()` (4626-4629: A ≤ `ACCEL_STEP_CAP` = 10⁶), so J ≤ 2,091.
  - The proof checks that there is still one writer, and still that cap.
- **−7 cog**, about −14 clocks on the corner path.

### C6. Jx computed once per frame, and the LUT peepholes that go with it

- **What.** Add a register `jerk_x := max(jerk_up_, jerk_dn_)` computed right after each params block read:
  the frame's (7814) and the start's (8499).
  - Every consumer today computes the same `max` from the same registers. The registers change only at
    that read, so the value is identical by construction.
  - The five sites that compute it are `jerkStep` 8640-8641 and 8661-8662, `planStage` `.aLo` / `.aHi`, and
    `planA` 9093-9094.
- **Rejected: Spin2 writing a Jx long.** A hub long Spin2 writes can tear against the driver's block read.
  The driver could then use a Jx that is not max(jerk_up, jerk_dn) of its own read, which breaks PL-161's
  take-pass range. It would also be an ABI append.
- **`jerkStep`, other than Jx:**
  - `negc jrk_e,err_` (8674-8676) and `negc accel_now_,tmpY` (8689-8691): −2.
  - The two `SPIN_DN`-or-`SLOW_TO_CHG` tests in `.report` (8717-8721) become `cmp #DCS_SPIN_DN wc` range
    tests: −2. Exact under the invariant that `tmpX` ∈ {2,3,4,5} and `drv_state_` ∈ {1..5} whenever
    `jerkStep` runs. Proof: the drive pass reaches `.running` only past the e-stop exit and the FAULTED
    latch, and every writer of `drv_state_` is on the list.
- **`faultResponse`** (8790-8803):
  - `and tmpX,#%111 wz` for `and` + `cmp #%000 wz`: −1.
  - Drop `.blunt`'s `cmp fault_mode_,#FR_GRADED wz`. On all three paths into `.blunt`, Z already equals
    "graded": the `if_nz jmp`, the flag-free `tjnz`, and the illegal-code `if_z jmp`, which is reachable
    only when graded. −1.
- **`undrivenPins .probe`** (8745-8762): fold `sub #PRB_U` into the ALTS base,
  `alts tmpX,#pin_pwm_u_l - 2*PRB_U` (and `_u_h`), at both sites. −2.
- **Frees** LUT −8 (`jerkStep`) −1 (`.a`) −1 (`planA`) −2 −2 = **−14**, for **cog +3** (2 code + 1
  register) and start image +2.
- **Clocks:** frame +4, pass about −12.
- **Risk: low to medium.** The range test rests on a proven state invariant.

### C7. Registers used only inside `jerkStep`, or only inside one pass, share planner registers

- **What.** `jrk_s`, `jrk_lim` and `lag_s` take the addresses of planner registers.
  - `jrk_s` and `jrk_lim` are written and read only inside `jerkStep`. `xStar`, which the planner also
    calls, touches neither.
  - `lag_s` is live only from `drvMotor`'s entry to `.capDone`, and no stage runs in that span.
  - **The invariant is that a drive pass always restarts the plan.** Every path through `drvMotor` reaches
    `.endRqst`'s `mov plan_stage,#1` (7635), and the release path never returns. So a pass clobbering any
    planner register is harmless: stage 1 rewrites everything it reads. In the other direction, a stage
    clobbering `jrk_s` / `jrk_lim` / `lag_s` hits registers that are dead between passes.
- **Frees** 3 cog. Clocks 0.
- **Risk: low.** The proof is static.

### C8. `driverRelease` as an overlay loaded on demand (cold code)

- **What.** `driverRelease` (34 LUT) leaves the run image and becomes its own image in hub.
  - `passEnd`'s `tjnz drv_release_,#driverRelease` (8579) targets a cog loader instead:
    `setq2 #REL_LEN-1 / rdlong 0,relCodePtr / jmp #relStart`.
  - The release image is block-loaded over the start of the run image at `$200`. The release never
    returns and the planner is abandoned, so nothing it overwrites is needed again.
  - `relCodePtr` is a new DAT long that `init()` sets, the way `lutCodePtr` is set.
- **Frees** LUT −34, for cog +4.
- **Clocks.** 0 in the loop. The release path gains ~50 clocks of load before its COAST writes, against
  stop()'s 1,704 µs bound (`RELEASE_TIMEOUT_US`).
- **The PL-138 gate windows stay in LUT execution, deterministic at 2 clocks per instruction.** This is why
  C8 loads an overlay rather than running the release by hub execution.
- **Risk: low.** The instructions are the same and so is the pin sequence.

### C9. `planCorner` back into the LUT (a trade, not a saving)

- **What.** With C2, C5, C6 and C8 banked, the LUT has room again. `planCorner` sits in cog RAM only "for
  room" (7986). It moves into the run image beside `planA`, which tail-jumps to it.
- **Moves** 38 longs from cog to LUT. Clocks 0.
- **Why:** free cog longs can hold registers *or* code, and free LUT longs only code. So cog headroom is the
  more valuable of the two, as long as the LUT keeps a margin.

### C10. Assessed and not in the chosen set

Every candidate class the design question named was assessed. These are the ones kept out, with the reason
and the price.

| Candidate | Longs | Cost | Verdict |
|---|---:|---|---|
| **The planner by hub execution** (`planStage`, `run`, `planA`..`planC`, `planCorner`, `planFp`; `xStar` stays for `jerkStep`) | frees ~288 (cog 61, LUT 101, the whole overlay 126) | each taken branch 13-20 clocks instead of 4. DERIVED ~+300 clocks on the worst stage, putting the stage frame at ~2,770 of 3,636 clocks at 160 MHz (76 %). Branch timing is non-deterministic but bounded. Cog code needs a pointer to call it (`p2kbSpin2AsmOrgh`) | **The largest lever there is.** Not needed for the target. The reserve if a later feature needs a PL-161-sized block. The results would still be bit-identical, since the instructions are the same |
| Hub execution for the start sequence | 0 LUT (C2 already hides it) | non-deterministic branches around the PL-138 gate window in `driveinit` | rejected |
| `hall_angles` into LUT, read by `rdlut err_,hall_` at LUT 0-15 (also in the start image, or `checkstop` moved into `loadOverlay`) | cog −18, LUT +16 | −1 clock/frame; Spin2 writes the LUT image | reserve lever (the LUT trade C9 is the better one first) |
| Spin2 precomputes the feedforward (`feedForward`) and the PL-55 ceiling reciprocal (7648-7654) | −3 to −4 | floor(a·b/c) ≠ floor(a·floor(b·2³²/c)/2³²) | rejected: **not bit-identical** |
| `planA`/`planB`/`planC` merged into one routine | — | they are three different closed forms: corner/unwind, rise, plateau + ramp-out. They already share `run`, `rampOut` and `xStar` | rejected. The parameterisable part is the three *plans*, which C5(a) merges |
| A shared `J·m(m+1)/2` helper for `xStar`, `rampOut` and `planCorner` | −2 net | +8 clocks per call; J sits in a different register per caller | reserve |
| Accumulate W = 3U + D in `run`, dropping `pl_Dl` / `pl_Dh` and most of `planFp` | −2 code, −2 registers | +~12 clocks per `run` (two ×3); exact mod 2⁶⁴ | reserve |
| ADC scaling (7703-7722) as REP + ALTx | −3 | +~56 clocks/frame | rejected |
| The three per-phase write groups as an ALTI loop | −4 | +~12 clocks/frame | reserve |
| `faultResponse` or the `.probe` code loaded on demand | −22 / −19 | the fault frame continues into a re-synced stop, and the probe runs at rest while the planner runs: either load would evict live code | rejected |
| SKIPF/EXECF to merge the three plan prologues | — | needs a pattern register or `##` per variant; conditional execution is cheaper (C5a) | rejected. SKIP is already used where it pays (`checkstop`) |
| `maxNeg` as `wrlong ##-1` | cog −1, LUT +1 | — | only if cog becomes the binding memory |
| LUT sharing (`SETLUTS`, `p2kbPasm2Setluts`) | 0 | mirrors a companion cog's LUT writes. It adds no capacity, and C8's release overlay would then overwrite the partner wheel's run image | rejected |
| Dropping `jerkStep`'s `fge jrk_j,#1` (8657) | −1 | relies on the one writer's J ≥ 1 | excluded: the bit-identity proof would then hold only over the writer's domain |

**How each candidate class the design question listed is answered:**

| Class | Answer |
|---|---|
| Duplicated arithmetic between `jerkStep` and the planner | x* is already shared (`xStar`). The residue is Jx, handled by C6, and the J·T(m) kernel, a reserve lever |
| planA/B/C as one stage | C5(a) |
| Disjoint-phase registers | C1, C7 |
| Immediates | C5(c). The other constants are either clock-derived (`bias`, `adc_fram`, `fram`), or cost more as `##` than as a register (`third`), or are freed by C1 anyway (`pwmt`) |
| Cold code in overlays | C2 (start) and C8 (release). Fault and probe are rejected above. Two small loaders, not a general demand pager: only one run-time image qualifies |
| Tables | C4 (`deltas`), C5(a) (the jump table). `hall_angles` is a reserve lever |
| What Spin2 computes | C4 (the event classes). Jx and the reciprocals are rejected above |
| SKIPF/EXECF | rejected above |
| Algorithmic restructuring | C3(b), C3(c), C4, C5(a), C5(b) |

---

## 3. HUB / ABI IMPACT

- **None.** No `VAR` long moves. `DRVR_LAUNCH/STATUS/PARAMS_LONGS_COUNT` and the `DRVR_STATUS_*_IDX`
  constants are unchanged, and `isAbiLayoutValid()` is untouched.
- **What changes is the driver's own DAT image,** which is not ABI:
  - C4: the `deltas` format;
  - C2: what `planCodePtr` points at;
  - C8: the new `relCodePtr`.
  
  `init()` fills all three before `coginit`, as it fills them today.
- **Bench harnesses read only the status run, so they are unaffected.**
- **Documents:**
  - `DRIVER-THEORY-OF-OPERATIONS.md`:
    - §2, *One-shot DAT initialization*: the pointers.
    - §4, *Cog and LUT memory*: the start/run/release images and the new figures.
    - §4, *Commutation*: the packed table.
  - The `fit` comments.
  - `ADDING_MOTOR.md`: no change, since the byte tables remain the authoring format. Re-read it in C4 to
    confirm.

---

## 4. FIDELITY PROOF METHOD

### 4.1 What exists in the scratchpad, and what it covers (MEASURED by reading each script)

| Script | Executes | Compares against | Covers | Does not cover |
|---|---|---|---|---|
| `desk_driverplan.py` (library: `load()`, `Cog`) | the PASM *source* of `jerkStep`, `xStar`, `run`, `planStage`, `planA`..`rampOut`, `planFp`, `planCorner`: ~30 opcodes, C/Z, conditions, `_ret_`, a call stack, a CORDIC queue with the 55-clock latency, AUGS clocks | — | the planner and `jerkStep` | its own `main()` is stale: it calls `stopPlanner` and reads `sc_a`, both gone since DRIVER_REV 39. Registers are keyed by **name**, so it cannot model two names at one address (C1, C7) |
| `desk_driverplan2.py` | the above | **models**: `desk_stopbound`'s Python `jerkStep` walk, the take-pass range, a never-late timeline | B (plan vs walk), C (published vs definition), G (take-pass range), D (never late), E (clocks per stage) | the baseline PASM. It certifies the algorithm, not a refactor |
| `pasm_exec.py` | the source of `jerkStep` only | `jerk_model.step` | `jerkStep` against its model | everything else |
| `frame_clocks.py` | nothing (a static count from source spans by label) | — | the upper bounds on the frame, stage and pass | its spans are keyed to today's label order (`countIllegal`→`driveinit`, `undrivenPins`→`restBridge`), which C2 and C4 move |
| `desk_models.py`, `desk_stopbound.py`, `jerk_model.py`, `jerksim.py`, `walksim.py`, `spin_mirror.py` | Python models | — | the ramp, walk and fold models | no PASM |

**Gap.** Nothing executes the frame loop, `drvMotor`, the start sequence, `undrivenPins`, `faultResponse`,
`restBridge`, `countIllegal` or `driverRelease`. Nothing compares *baseline PASM against candidate PASM*.
Nothing models addresses.

### 4.2 The harness each work package needs: a baseline-vs-candidate differential interpreter

1. **Execute the compiled image, not the source.**
   - Decode the driver's longs from each `.bin`, at `@driver`'s hub offset from the listing, using p2kb's
     encodings.
   - Resolve names only for reporting, from the listing's symbol table.
   - This tests what `pnut-ts` emitted: `##` AUGS, relative against absolute branches, ALTx bases, two
     labels at one address. It also makes C1 and C7 real, because a write to `pl_v` lands on `$000`.
   - Baseline = `git show mem-reduce-start:src/isp_bldc_motor.spin2` compiled in scratch. Candidate = the
     work tree, compiled in scratch.
2. **Machine model.**
   - Memory and state: cog 512 (with PTRA/PTRB/INA/INB), LUT 512, the hub block (the launch quartet, status
     24, `fault`, params 27, and the image regions for the three block loads), C/Z, the hardware call stack,
     Q (SETQ/SETQ2), pending AUGS/AUGD/ALTx, the SKIP pattern.
   - The CORDIC queue: QMUL/QDIV/QSQRT exact. QROTATE through any fixed deterministic function: the two
     images must present identical QROTATE inputs, and the harness compares those inputs, so bit-exact
     silicon CORDIC is not needed.
   - CT: the model advances it; CT1 holds the compare.
   - Pins: WRPIN/WXPIN/WYPIN/DIR/OUT/DRVL recorded as an ordered trace; RDPIN, TESTP, INA/INB and
     ATN/POLLATN scripted.
   - The driver's opcodes, all to be modelled:
     - existing: `mov add addx adds sub subx subs subr neg abs fge fle fges fles cmp cmps cmpm test testb(wc/wz/xorc) testp and or xor shl shr sar rcl mul muls sca signx bitc bitl wrc modc modz incmod getbyte getword setword alts altd altgb altgw altsw getct addct1 jnct1 waitx djnz tjz tjnz jmp jmprel call ret skip rdlong wrlong setq setq2 rdpin wrpin wxpin wypin dirl dirh outl drvl pollatn waitatn qmul qdiv qsqrt qrotate getqx getqy augs augd`;
     - added by this plan: `negc andn decod bmask altgn getnib`.
3. **Stimulus, indexed by (frame, read ordinal), never by clock.**
   - Clock shifts are then invisible to what is read. Every candidate that moves a read in time moves it
     within the same frame.
   - The generator is seeded. Each scenario draws from:
     - **clocks:** frame_cnt, dead_gap, bias, duty_min/max and cfg_ctcks from `init()`'s formulas at
       160/200/270/300 MHz;
     - **tables:** `MOTOR_TYPE` ∈ {6.5″, 4k}, and every `HSW_*` swap;
     - **start:** `sync_required` 0/1;
     - **commands:** random ±(2³⁰−1), zero, the sync bit;
     - **parameters:** any of the 27 changed at any frame, *including mid-plan* (between stage A and stage
       C). This matters: `planC`'s `xStar` reuses the `jrk_j` that `planA` set, while `rampOut` reads a
       fresh `jerk_dn_`;
     - **halls:** from a rotor that follows the field with lag, plus injected bounces, missed transitions,
       `%000`/`%111`, and stuck lines;
     - **ADC:** random and extreme counts;
     - **CT1:** 22- and 23-frame passes, and an adversarial short `cfg_ctcks`.
4. **The edge suite, deterministic.**
   - An e-stop of each kind in each state.
   - Each fault mode × stop mode, a second fault on a re-synced stop, `force_seq`.
   - Each probe phase and sink, `hold_short`, `drv_release` from every state.
   - `hall_illegal` words at `$FFFF`; `PLAN_PASSES_MAX`, `PLAN_UNWIND_MAX` and the planner corner.
   - J = 1, A = 1, A = 10⁶; v at ±(2³⁰−1).
5. **Compare after every frame and every drive pass:**
   - the status run and `fault` in hub (exact);
   - `targetIncre` acknowledgements;
   - the pin trace (values and order, exact);
   - the QROTATE inputs;
   - the CT1 target;
   - every register live at that boundary, by name.

   **Liveness is computed, not assumed.** A register or flag is excluded at a boundary only if every path
   from it writes before it reads, on the decoded baseline. Each WP lists its exclusions, for example:
   `tmpX`/`tmpY`; `pl_t/u/q` between stages; `jrk_*` between passes; C/Z at `.ctlMotor`; the removed
   `fold_net` and `ctrlEndTix`.
6. **Coverage gate.** Every instruction in a changed routine is executed, and every conditional both ways.
   Any exception names the static reason it is unreachable.
7. **Volume, per WP.**
   - ≥ 10⁶ frames of random scenarios, plus the edge suite.
   - ≥ 10⁵ planner runs through `desk_driverplan2.py`'s B/C/D/G. These still pass unchanged, because the
     results are identical; this is a regression check, not the proof.

### 4.3 Exact proofs, beside the differential run

| Candidate | Exact proof |
|---|---|
| C1 | A static def-use check on the decoded start path. For each dead address: last read < first write under its alias. The alias has no read on the start path. No run-phase instruction names the dead long |
| C2 | Call-graph partition: the start closure reaches no run-image address, and vice versa. Each relocated routine decodes to the same instructions, modulo the relocation of its branch targets |
| C3 | The identities stated in C3(a)-(e). The flag liveness for (a) and (c). (c) is also checked exhaustively over sense_i ∈ [−4,096, 4,096] × zero ∈ [0, 512] × every t the SCA can produce, sampled, plus the boundaries |
| C4 | **Exhaustive.** 64 (old, new) × 2 motor tables × 4 swap modes × counter states {0, $FFFE, $FFFF} × old/new illegal. Every `pos_`, `hall_missed_` and `hall_illegal_` result equals the baseline. A static check that every DAT delta table is inside {−1, 0, +1} |
| C5 | (a): the stage-transition table enumerated for all nine stages × planA's C = 0/1 × saturation. (b): value identity plus scratch/flag liveness in each caller. (c): `decod`/`bmask` constants equal the `##` constants. (d): the stated identities, plus the J domain from the one `jerk_dn` writer |
| C6 | Jx: every consumer reads the same two registers, which change only at the block read. The range tests: reachability of `jerkStep` states from the `drv_state_` writers |
| C7 | The "pass restarts the plan" invariant: every path from `drvMotor` to `.capDone` passes `mov plan_stage,#1`. Live ranges |
| C8 | The same instructions and pin trace: the release trace is compared in full. The release image covers no code that runs after the load |
| C9 | Relocation equivalence, as in C2 |

### 4.4 The frame-timing re-check, per WP

- Re-run `frame_clocks.py`, with its spans updated for C2 and C4, and `desk_driverplan2.py` E.
- From the differential run's clock model, take the per-window maximum for the baseline and the candidate:
  frame work, frame + stage n, and the pass frame.
- Tabulate both at 160 and 270 MHz against 3,636 and 6,136 clocks.
- **Acceptance:** every window ≤ its frame period with a 25 % guard at 160 MHz. Any window that grows by more
  than 32 clocks over the baseline is named in the WP's commit.

**DERIVED net after all nine WPs:**

| Window | Today | After | Share at 160 MHz | Share at 270 MHz |
|---|---:|---:|---:|---:|
| Frame work | ≤ 699 | ~≤ 687 | | |
| Worst stage | 1,750 | ~1,760 | | |
| Stage frame | 2,449 | ~2,447 | 67 % | 40 % |
| Pass frame | 1,883 | ~1,865 | 51 % | 30 % |

---

## 5. HEADROOM TARGET AND WORK PACKAGES

**Why a target at all.** PL-161 (DRIVER_REV 39) alone took cog 403 → 492 and LUT 402 → 507. That is MEASURED
in its record and in the `fit` comments. So one feature of that size needs ~90 cog and ~100 LUT longs.

**Targets** (read from the listing, not hand counts):

| Memory | Target | Reached by the chosen set (DERIVED) |
|---|---|---|
| Cog RAM | ≤ 432 of 496 (≥ 64 free) | **411 (85 free)** |
| LUT (run image) | ≤ 464 of 512 (≥ 48 free) | **451 (61 free)** |
| Start image | ≤ 256 | **146** (hidden under the run image, 0 LUT cost) |
| Release overlay | ≤ 64 | **34** |
| Planner overlay | the "126 of 129" squeeze | dissolved by C2 |

In total this recovers ~135 longs, about 70 % of one PL-161. The hub-execution planner in C10 is the priced
reserve for more.

**Order and cumulative figures (DERIVED; each WP records the listing's real figures):**

| WP | Content | Cog | LUT | Depends on | Risk |
|---|---|---:|---:|---|---|
| — | baseline | 492 | 507 | | |
| **WP1** | C1: start-dead longs host run-only registers | 471 | 507 | — | low |
| **WP2** | C2: start image / run image; `countIllegal` → cog | 484 | 476 | WP1 | low |
| **WP3** | C3: frame and pass peepholes | 470 | 476 | — | low |
| **WP4** | C4: nibble `deltas` with event classes (+ Spin2 packer) | 453 | 476 | — | medium |
| **WP5** | C5: `planStage` unified, `run`, `decod`/`bmask`, `planCorner` trims | 445 | 461 | — (ordered after WP2, so it edits the run image) | medium |
| **WP6** | C6: per-frame Jx; `jerkStep` / `faultResponse` / `.probe` peepholes | 448 | 447 | WP5 (`.a`) | low-medium |
| **WP7** | C7: `jerkStep`-only and pass-only registers share planner registers | 445 | 447 | WP1 | low |
| **WP8** | C8: `driverRelease` on demand | 449 | 413 | WP2 | low |
| **WP9** | C9: `planCorner` into the run image | **411** | **451** | WP2, WP5 | low |

**Each WP is one commit and stands alone:**

- Edit, read the diff, compile the one file, then prove:
  - the §4.3 exact proof;
  - the §4.2 differential run against `mem-reduce-start`, with coverage;
  - the §4.4 timing table.
- Update the `fit` comments from the listing, then run the gate once, then commit.
- **DRIVER_REV:** recommended one bump per WP, with a history line *"memory: <what>; bit-identical, no
  behaviour change"*.
  - The image differs, so a bench log should say which image ran.
  - The arbiter owns this call. The convention bumps for behaviour, and this plan changes none.
- **No WP needs a bench cell.** The next scheduled pass runs the new image as its certification.

**Stopping points:**

- **WP1-WP4** reach cog 453 / LUT 476. These are the zero- or low-instruction-change set.
- **WP1-WP8** reach cog 449 / LUT 413. LUT-rich; this is the alternative if the LUT margin is preferred over
  the cog margin.
- **WP9** is the trade that meets the cog target.

---

## 6. OPEN POINTS FOR THE ARBITER (none blocking)

1. The DRIVER_REV bump policy for image-only changes (§5).
2. WP4 is the only package that changes Spin2 behaviour in `init()`, where the packer replaces
   `bytemove(@deltas, …)` and the byte half of `swapHallTables`. It is desk-proved exhaustively. It is listed
   in case the owner wants Spin2 changes kept out of a memory pass.
3. The hub-execution planner (C10) is the reserve lever. It is priced here so it can be brought to Stephen
   with its measure of benefit if a later feature needs the space (P5).

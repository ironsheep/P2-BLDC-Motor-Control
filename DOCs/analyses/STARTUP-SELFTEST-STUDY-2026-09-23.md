# Startup self-test study — what start() proves today, and what each proposed check needs

**Task:** «#3610» phase 1 (desk). **Date:** 2026-09-23. **Status:** report only, nothing in the driver changed.
Phase 2 (wheels-up cells) and the design are open; §6 carries their inputs. It shares one health model with
`FAULT-STRATA-STUDY-2026-09-23.md` («#3609»).

## 1. Scope

**Question.** What does the driver prove about board, halls, sense and motor before it first drives? For each
proposed check, what does the silicon and the board give, where would it live, and what can it not tell apart?

**Surface.** In `src/isp_bldc_motor.spin2`: the start chain (`start`/`startEx`/`startOwned` → `setupForStart` →
`init` → `launchDriver` → PASM `lutCodeStart` → `launchFront` → `captureRestZero`), `getBoardType()`,
`calibrate()`, and the ADC path. In `tools/bench-run.sh` and `src/test_bench_*.spin2`: harness checks, used only
to list what the driver lacks. p2kb (P7) is the authority for silicon facts.

**Excluded.** Steering's own two-wheel start sequence, which was not re-read (see §7). The 64010 board manual PDFs,
which are not in the tree; board facts come from `DOCs/analyses/BOARD-REVISION-FACTS.md`.

**Marks** are MEASURED / DERIVED / undetermined (doctrine overlay P8). **Method:** a read-only survey agent traced
the chain. I re-opened the anchors findings rest on: `:171-231`, `:410-421`, `:883-902`, `:2174-2289`,
`:2218-2230`, `:5031-5033`, `:5270`, `:5306`, `:5340-5368`. I fetched p2kb `p2kbArchSmartPin11000AdcInternalClock`
myself.

## 2. Read order (ticked)

- [x] Public entry points `start`/`startEx`/`startOwned` (`:171-231`)
- [x] Validation and claim `setupForStart` (`:2174-2207`); board gate in `launchDriver` (`:2222-2228`)
- [x] `getBoardType()` (`:1023-1108`)
- [x] PASM start sequence in LUT: calibration, live ADC mode, ATN wait, `driveinit`, boot hall read (`:5222-5410`)
- [x] Front-cog launch and heartbeat wait (`:2251-2289`); rest-zero capture (`:836-902`)
- [x] `calibrate()` (`:414-420`)
- [x] Harness tiers in `tools/bench-run.sh`
- [ ] Steering's own `start()`: not re-read

## 3. Today's start sequence

| Step | Where | Proves | Can refuse with | Leaves unproven |
|---|---|---|---|---|
| Validate enums, ABI layout, claim the pin range | `setupForStart` `:2174-2207` | the arguments are legal; no other instance owns the pins | `ERR_BAD_PIN_GROUP`, `ERR_BAD_VOLTAGE`, `ERR_BAD_DETECT_MODE`, `ERR_ABI_MISMATCH`, `ERR_PIN_GROUP_IN_USE` | any hardware |
| Board and revision | `init` → `getBoardType()` `:1023-1108`; gate `:2222-2228` | a 64010 is present, and which revision | `ERR_BOARD_NOT_DETECTED` | **bypassed when the user forces a revision** (by design, `:2222-2224`); nothing about the motor |
| Driver cog launch | `:2238-2249` | a cog was free | `ERR_NO_FREE_COG` | — |
| GIO/VIO sense calibration | PASM `:5270-5333` | computes a per-channel scale | nothing: never judged | whether the channel is sane |
| Boot hall read | PASM `:5360-5365` | one hall sample; an illegal code is **counted** in `hall_illegal_` | nothing: `start()` still returns success | whether any hall line toggles |
| Front cog heartbeat | `launchFront` `:2251-2289` | the front cog runs its loop | `ERR_NO_FREE_COG`, `ERR_NO_RESPONSE` | — |
| Rest-zero of the DC-link current | `captureRestZero` `:883-902` (bridge floated) | a ~1 s mean | `ERR_NO_RESPONSE` if no status lands | whether the mean is in a plausible range |
| `calibrate()` | `:414-420` | nothing: a stub marked *"NOT WORKING: (we may or may not need this?)"*, returns `NO_ERROR` | — | everything |

**Summary, MEASURED from source.** Start proves the board, the cogs and the arguments. It proves nothing
about the motor, the windings, the FETs or the hall sequence. It computes but never judges the sense
calibration, the rest zero and the boot hall code.

## 4. Capability per proposed check

**The sense channels (corrects the dispatch brief).** `sense_i` is the **DC-link current** shunt
(BOARD-REVISION-FACTS §2.3). `sense_u/v/w` are the **phase voltages**; MOTOR-6.5IN-TECHNICAL-MANUAL §9.1
reads back-EMF through them with the bridge coasting. There is no supply-voltage channel on the board. The mean
phase voltage while switching is an unconfirmed bus proxy (PL-60: CONSISTENT on the left board, INCONCLUSIVE
on the right).

**The ADC path today** (MEASURED from source, mode names from p2kb). Live mode is `p_adc_1x | p_count_highs`
(`:5033`, set `:5347`). Each channel counts the ADC bitstream's highs over one PWM frame, and the driver reads all
four once per frame (`wait4adc` then `rdpin`, `:4736-4743`). Each reading is therefore an **average over the
whole ~22.8 µs frame**. Calibration temporarily switches to GIO then VIO, widens the period, and discards the
first widened frame (`:5270-5333`).

**Can a microsecond current rise be seen?** Not in today's mode, which averages it over the frame (DERIVED). p2kb
documents two faster forms of the same `%11000` ADC mode: **bitstream capture** (X[5:4] = `%11`), a new raw
32-bit snapshot every 32 clocks, and a triggered **scope mode** `%11010`. At the drive's clock, 32 clocks is a
fraction of a microsecond. Whether either resolves a DC-link current rise well enough to judge continuity or
estimate R is undetermined. p2kb gives the mechanism, not the analogue settling, so it is a bench question
(cell B-4).

| Check | Detects | Needs (silicon / board) | Existing pieces | Lives in | Blind spots | Negative control |
|---|---|---|---|---|---|---|
| **1a Board + revision** | board present, Rev A/B | plain GPIO timing on the sense pin | `getBoardType()` `:1023-1108`, gate `:2222-2228` | caller, before launch (it sets the current scale the driver needs) | skipped when forced; says nothing of the motor | pin group with no board → `ERR_BOARD_NOT_DETECTED` |
| **1b Sense zero in range** | a dead or mis-wired current channel | GIO/VIO calibration (p2kb `%11000`, P2AN001 flush-then-sum) | calibration `:5270-5333`; rest zero `:883-902` | judged in Spin2 (only it knows `eDetectedBoard`, which picks the band) | a channel that is sane at rest but wrong under load | a band set to exclude the measured value must FAIL |
| **1c Halls legal and powered** | unplugged harness (pull-ups → `%111`), a line stuck to an illegal code | filtered digital input, one INA/INB read (PL-90) | boot read + `countIllegal` `:5360-5365`, **counted, never surfaced** | driver computes; front/caller reports | a line stuck at a **legal** level passes; one sample cannot show a toggle | hall connector unplugged → `%111` → FAIL |
| **1d Phase continuity (voltage)**, a new option | missing motor, open winding, dead high-side FET | the phase-voltage channels already sampled | none | driver cog (owns PWM and the frame timing) | cannot measure R; cannot see a shorted winding | one phase lead unplugged → that phase's voltage stops following → FAIL |
| **1e Continuity + winding R (current)** | as 1d plus R (the input «#3609» needs, U-3) | a sub-frame DC-link current read: bitstream or scope mode (above) | none: searched `continuity`, `winding resistance`, `short pulse` across `src/`; only design prose in `DOCs/` | driver cog | resolution undetermined (B-4) | phase unplugged → no rise; two phases shorted → fast rise |
| **1f Supply voltage** | a low or wrong pack | Stephen's 5S divider on a spare ADC pin («#3611»); PL-60's proxy only while switching | none | wherever «#3611» reads it | nothing until «#3611» lands | sensor unplugged → ABSENT, not 0 V |
| **2 One-e-cycle walk, hall order** | dead or swapped halls, swapped phase/hall wiring, a wrong offset, a motor that does not respond | the running control loop at low duty; `deltas`/`hall_angles` tables | `moveShaftToAngle()` `:461` (TEST-USE, one target angle); `initAngleFmHall` | front cog sequences (sole command writer); driver reports each hall code | a weak winding may not turn the rotor at low duty, and reads as "no motion" | two hall wires swapped → order check FAILS |
| **3 User-assisted `calibrate()`** | distance per tick, each motor's commutation pair on the platform | existing `pos` tracking and `isp_dist_utils` | stub `:414-420` | caller, on request only | manual by definition | a known ground distance vs the reading |

## 5. Findings register

| # | Severity | Finding | Evidence | Mark | Root cause | Trivially safe? |
|---|---|---|---|---|---|---|
| S-1 | breaks users | **`start()` returns success with the hall harness unplugged.** The boot read counts the illegal code and nothing reports it. The first drive then faults as FC_HALL. | `:5360-5365`; `start` `:171-215` | MEASURED (source) | G-1 | no |
| S-2 | wrong but contained | **Sense calibration and rest zero are computed, never judged.** A dead or mis-wired current channel starts cleanly, and with it the current limit and the blocked test that depend on it. | `:5270-5333`, `:883-902` | MEASURED (source) | G-1 | no |
| S-3 | breaks users | **Nothing proves a motor is attached.** A missing motor, an open winding or a dead FET is first seen as a position fault at speed, classified FC_LAG ("a load problem"; the fault study, F-4). | absence: `continuity`, `winding resistance`, `short pulse` over `src/`; control search `countIllegal` finds `:4977` | DERIVED (traced absence) | G-1 | no |
| S-4 | hygiene | **`calibrate()` is a public method that does nothing** and says it is not working. It is the named home for stage 3. | `:414-420` | MEASURED (source) | — | no: removing or implementing it is an API change (P3) |
| S-5 | latent | **A phase-voltage continuity check needs no fast current sampling.** The phase voltages are already read every frame, so stage 1's "is a motor there" can be answered without resolving the open 1e question. Only R needs the current read. | `:4738-4758`; technical manual §9.1 | DERIVED | — (a capability) | — |
| S-6 | wrong but contained | **The claim "I/U/V/W are phase current shunts" is wrong** (see §4). It was in this study's dispatch brief (from the task breadcrumb) and in «#3611»'s body; both records are corrected with this study. | BOARD-REVISION-FACTS §2.3 | MEASURED (records) | — (aged state) | **yes**: record-only |
| S-7 | latent | **Every "alive" check the project runs lives in the harness.** Examples: tick counts against hand revolutions (`t0-hand`), stop states (`t0-stopmode`), board detection across pin groups (`detect*`), the stall watchdog (`scan-wdtest`), the hall zero turned by hand (`dual-align`). The driver owns none of them (front 3). | `tools/bench-run.sh:113-136` | MEASURED (source) | G-1 | — |

**Root-cause group G-1 · start proves the platform, not the drive** (S-1, S-2, S-3, S-7). Every check start
runs is about the P2 side (arguments, cogs, board). Everything on the motor side is left to the first drive to
discover, and a fault at speed reports it, often under the wrong cause.

## 6. Inputs to phase 2: cells, each able to FAIL, wheels up

- **B-1 · Boot with the hall harness unplugged.** *Expect today:* `start()` succeeds and `getHallIllegalCodes()`
  is non-zero (S-1). *Fails the finding* if start refuses.
- **B-2 · Rest zero per board.** Log the rest zero on both Rev B boards across several starts. The spread sets
  the band for 1b. It FAILS as an instrument if repeated starts on one board spread wider than the gap between
  the two boards (a band could not separate them).
- **B-3 · Phase-voltage continuity (1d).** A test build drives one high side briefly at low duty with the other
  two floating and reads all three phase voltages. *Expect* the undriven phases to follow through the windings.
  Negative control: one phase lead unplugged, and the follow must disappear on that phase.
- **B-4 · Sub-frame current rise (1e).** The same pulse, with the DC-link channel read in bitstream-capture mode.
  *Expect* a rise whose slope gives L/R. Negative control: a phase unplugged, so no rise. **Fails** (1e is not
  buildable on this ADC) if the rise cannot be told from the unplugged case.
- **B-5 · One-e-cycle walk (2).** Walk the field one electrical cycle each way at low duty. *Expect* six legal hall
  codes in the order the direction predicts. Negative control: two hall wires swapped, and the order check must
  FAIL.

## 7. Not read, and undetermined

- Steering's two-wheel `start()`: where a two-wheel stage-2 walk would be sequenced.
- The hall input filter's p2kb mode detail (the code site was read, not the mode page).
- **U-1:** the resolution of bitstream/scope-mode current reads for a phase pulse (B-4).
- **U-2:** whether PL-60's bus proxy holds on both boards (one DMM reading per board, already named in PL-60).

## 8. Hand-off

The design phase takes G-1, the capability in S-5 and the B-cells' results. It also takes Stephen's ruling on
levels and defaults, which the task reserves to him once phases 1-2 are reported. S-6 is record-only and
trivially safe.

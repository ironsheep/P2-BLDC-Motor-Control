# pasm_equiv — prove a candidate driver image equivalent to the baseline

`tools/pasm_equiv/run.sh` compiles the PASM motor driver twice, the baseline (`git show
mem-reduce-start:src/isp_bldc_motor.spin2`, with the OBJ files it names) and the candidate (the work tree's
`src/`). It runs both images on the same stimulus in an instruction-level P2 cog emulator and compares them at
every PWM frame. It is the §4.2 harness of `DOCs/plans/PASM-MEMORY-REDUCTION-PLAN.md`: every work package there
must pass it before its commit.

```bash
tools/pasm_equiv/run.sh                          # the 55 named edge scenarios + 50 random seeds
tools/pasm_equiv/run.sh --seeds 2000 --coverage  # the full proof run, with the coverage gate report
tools/pasm_equiv/run.sh --scenario rand-1234     # replay one scenario (a divergence report prints this line)
tools/pasm_equiv/run.sh --scenario named         # the edge suite only
tools/pasm_equiv/run.sh --list                   # the named scenarios
tools/pasm_equiv/run.sh --candidate-dir /path/to/other/src   # any source tree as the candidate
```

It needs `pnut-ts` on `PATH` (or `--pnut`), `git` for the baseline tag, and Python 3.8+. It builds into a new
temp directory (or `--work DIR`), never into `src/`. **Exit status:** 0 equivalent and inside the frame budget;
1 a divergence; 2 a frame-budget failure (the start frame included); 3 incomplete (a build error, an opcode the
emulator does not model, an operation p2kb calls undefined, an init() change the model does not know, or, under
`--coverage`, moved code the candidate covers less than the baseline did).

## The images

The tool finds the driver's code images in each build's listing; it holds no list of them. It prints each one,
with its use, for both builds:

- **`cog`**: the org-0 image COGINIT loads from `driver`. Its use counts every org-0 long, RES included (the
  `fit 496` figure). For coverage, its code ends at the first org-0 data long, `all_pins` (or, without that label,
  at the first RES long).
- **a LUT image** for every global label pair `<name>Start` / `<name>End` under an `org` at or above `$200`:
  `lutCodeStart`/`lutCodeEnd` (the start image), `runCodeStart`/`runCodeEnd` (the run image),
  `planOvlStart`/`planOvlEnd` (the baseline's overlay), and any later pair, such as a release image. Each is
  listed with the `SETQ2 #n-1` sites whose block size is its own, or `no SETQ2 load found`.

LUT images share LUT addresses (the run image is loaded over the start image) but never hub bytes. Coverage and
names are kept by hub position, so each image is reported separately.

## What it proves

For every scenario, at every frame boundary (the cog seeing the next ADC sample), for the frame just ended:

| Compared | How |
|---|---|
| every hub long the cog wrote | address and value, in order: the status run, `fault`, the `targetIncre` acknowledgement. `loop_ticks` and `loop_ctcks` are clock counts, so for them only the write itself is compared, not the value |
| every pin operation | `WRPIN/WXPIN/WYPIN/AKPIN/DIR*/OUT*/DRV*/FLT*`, in order, with pins and value |
| every `QROTATE`/`QVECTOR` input | exactly (see *limits*) |
| the CT1 target | as an offset from the pass's entry, plus `COGATN` strobes and the start ATN |
| every live register | by **name**, at the boundary: a register that moved (a C1/C7 alias) is checked at its new address. **Liveness is computed, not assumed:** a register is live at boundary *k* if its first access after *k*, on the baseline's own path, is a read. A register is compared only once the baseline has written it, since until then it holds COGINIT's copy of whatever hub bytes follow the image. Registers written from `CT` (`GETCT`, `ADDCT1` destinations) hold timing and are excluded |
| C and Z | when live, by the same rule |

It stops at the first difference and reports it with the instructions that led to it in both images (the
differing write, or the last write of the differing register). It also prints a replay line.

**Findings, reported but not failed.** Every read of a `res` register the baseline has not yet written is listed
under `FINDING`. At `mem-reduce-start` there is one: the first drive pass reads `err_` (`mov lag_s, err_`,
`DRVMOTOR+1`) before any frame has written it. At rest that value is dead. With a drive command already pending
at the first pass, `jerkStep`'s lag gate and LAG_HOLD would act on it. That value changes with every build, so a
work package that moves registers changes it. The scenarios keep `targetIncre` at 0 until the first pass, as
`launchDriver()` and every front cog do.

**The emulator executes the compiled longs**, taken from the `.bin` and checked byte for byte against the
listing's hex dump. It never reads the source text. Names are used only to report and to match registers
between the two images. The encodings and flag rules come from p2kb (one `p2kbPasm2*` key per instruction group,
named in `p2cog.py`). Every compiled form the driver and the plan's work packages use was checked by compiling
it with `pnut-ts` and decoding it back. Any opcode or operand form outside the modelled set stops the run with
`Unmodelled`; nothing is skipped silently.

**Modelled:** conditions and `_RET_`; C/Z with WC/WZ/WCZ; AUGS/AUGD, including the errata where an intervening
ALTx `#S` uses the AUGS value without cancelling it; ALTS/ALTD/ALTGB/ALTGW/ALTSW/ALTGN with auto-index;
SETQ/SETQ2 block RDLONG/WRLONG into cog RAM and LUT; PTRA/PTRB expressions, including the block-size PTR delta
and its ALTx/AUGx errata; CALL/CALLPA/CALLD/RET, `_RET_` and an 8-deep hardware stack; REP; SKIP; JMPREL;
TJZ/TJNZ/DJNZ/JNCT1; RDLUT/WRLUT; the CORDIC queue (QMUL, QDIV, QFRAC, QSQRT exact; QROTATE, QVECTOR); GETQX/GETQY
pipeline visibility; GETCT, ADDCT1, WAITX, WAITCT1; POLLATN/WAITATN/COGATN; RDPIN/RQPIN/AKPIN; TESTP/TESTPN;
INA/INB; the arithmetic and logic set in `p2cog.py`'s `_OPS` table; NOP.

**Stimulus** (`scenarios.py`, `drvenv.py`) is a function of the scenario, the frame index and the hub-read
ordinal. It never depends on the clock, so a candidate that moves a read in time within its frame sees the same
input. It is closed-loop only through things the comparison itself checks:

- **Configuration.** `init()`'s launch block and 27-long parameter run, built with its own formulas: motor 6.5″ or
  4k, board Rev A or B, the voltage, 160, 176, 200, 264, 270 or 300 MHz, every pin group (so ports A and B),
  `sync_required`, and every `HSW_*` hall swap.
- **Rotor and halls.** The halls come from a rotor that follows the field angle each frame fed to QROTATE, with a
  lag that changes gradually. Injected faults: stalls, hand turns, free runs, illegal `%000`/`%111` codes, skips
  and bounces, and stuck lines.
- **ADC.** GIO/VIO calibration counts, then a DC-link reading from duty and load, fold-back stretches above the
  threshold, and readings at either rail.
- **Commands and parameters.** `targetIncre` with and without the sync bit, a target equal to the present speed,
  ±(2³⁰−1), and every one of the 27 parameters. They are written at a frame boundary or before a given hub read,
  so a change can land mid-plan, between planner stages.
- **Other stimulus.** ATN deliveries, and a front-cog reflex that clears the fault latch and writes the stop after a
  re-sync.
- **CT1 schedule.** 22- and 23-frame passes, a coin-flip at clocks where `frame_cnt` divides `cfg_ctcks` (176 and
  264 MHz), and adversarial 1- to 12-frame passes.

The 55 named scenarios are the plan's §4.2.4 edge suite (`--list`):

- e-stops of each kind in each state;
- each fault mode × stop mode, with a second fault on a re-synced stop and `force_seq`;
- probe phases and sinks, `hold_short`, and release from rest, running, faulted and e-stopped;
- `hall_illegal` saturated at `$FFFF` (132,000 frames);
- `PLAN_PASSES_MAX` and `PLAN_UNWIND_MAX`, and the planner corner;
- J = 1, A = 1, A = 10⁶, and v = ±(2³⁰−1).

Random seeds run 1,500–3,500 frames, and every tenth runs 20,000.

**Frame budget.** For both images the tool prints the worst clocks per window: the start frame, frame work, the
pass frame, and each planner stage. Each figure runs from the ADC sample to the next wait, with every hub and
CORDIC wait at its worst, so it is an upper bound. They are set against the 3,636-clock frame at 160 MHz and the
6,136-clock frame at 270 MHz. **A candidate fails if any window exceeds 75 % of the 160 MHz frame** (`--guard`,
the plan's §4.4). Any window more than 32 clocks over the baseline is flagged. Frames under an adversarial CT1
schedule, and the release, are excluded.

**The start frame** is the frame of the first drive pass, which carries the end of the start sequence. It has no
sample at its start: it opens when `driveinit`'s `dirh adc_pins` raises DIR on the ADC pins, which restarts the
ADC count period. The first sample after that lands one period later. The window runs from that DIRH through the
rest of the start sequence, `loadOverlay`'s SETQ2 load of the run image and the first drive pass, to the first
frame wait (the first `wait4adc` TESTP). A late cog is caught the same way: the window then ends at the TESTP that
finds the sample already there. The tool prints the worst start frame for each build, split at the drive pass
entry, with the SETQ2 load's clocks and longs. The block RDLONG is costed as p2kb gives it: the RDLONG's hub wait
at its worst, 16 clocks (`p2kbPasm2Rdlong`), then one long per clock (`p2kbPasm2SetqBlockOps`). At
`mem-reduce-start` the start frame takes 645 clocks: 363 to the pass entry, 141 of them a 126-long overlay load.
At DRIVER_REV 42 it takes 995: 713 to the pass entry, 491 of them the 476-long run-image load. Both figures come
from `start_brake_idle` and agree with an instruction trace counted by hand.

**Coverage** (`--coverage`, the plan's §4.2.6). It covers **both builds, image by image**, each mapped by address
in its own image. It reports every instruction never executed, every conditional seen one way only, and every
test-and-branch seen one way only, over the scenarios run. At `mem-reduce-start`, the named suite plus 2,000
seeds cover:

- 945 of 948 instructions;
- every conditional both ways but two;
- every test-and-branch both ways.

**Moved code must stay covered.** The tool matches every baseline instruction to its copy in the candidate,
wherever the work package put it. It works routine by routine: the code under each global label that both builds
carry on a code long. It takes the longest common subsequence of instructions whose opcode, condition, flags and
immediates are equal and whose registers and branch targets share a name, so a register that moved or was aliased
(C1, C7) still matches. A matched instruction was moved. An unmatched one was changed or removed. **The run is
INCOMPLETE (exit 3) if the baseline executed a moved instruction and the candidate never did, or if the baseline
took a moved decision both ways and the candidate took it one way only.** Otherwise the equivalence proof would not
reach that code in its new place. The report also lists the baseline longs left unmatched, which this check does
not cover. Baseline against itself matches 948 of 948. At DRIVER_REV 42, over the named suite plus 2,000 seeds,
945 of the 948 match, 942 were executed in both builds, and none was lost. The three unmatched longs are WP2's own
edits: the two SETQ2 block sizes (`DRIVER+2`, `LOADOVERLAY+1`) and the dead `mov sv_tgt_incr, #0` that became
`mov err_, #0` (`LUTCODESTART.PIN+109`).

The three instructions never executed are each unreachable for a static reason:

- `PLANSTAGE+1`: the stage-0 `ret`. `planStage` is called only after `tjz plan_stage`.
- `DRVMOTOR.ENDRQST+10`: `if_z jmp` on `incr0 == 0`. `incr0` is set to |v'| ≥ 1 on the pass that first reports
  SPIN_DN or SLOW_TO_CHG, and only `jerkStep` sets those states.
- `PLANCORNER+37`: `if_nc mov pl_n, pl_c`. The isqrt-based *n* is never one over the least *n*. An overshoot needs
  an integer strictly between `isqrt(D)` and `√D`.

## What it does not prove

- **One cog, not the system.** It proves the driver cog's behaviour under the modelled stimulus: its hub writes, pin
  writes and live state. It does not model the other cogs' timing. A front cog's multi-long write lands whole at
  a boundary or before a chosen hub read, never torn inside the driver's 27-long block read.
- **No analog physics.** It does not model the motor's analog physics or the smart pins' analog behaviour: PWM
  output, ADC integration, filtering. The rotor model exists to drive the code's paths, not to predict a wheel.
- **QROTATE and QVECTOR are not silicon-exact.** p2kb states no bit count for the trig residual, so the model uses
  a fixed deterministic function (float, rounded) and the harness compares the inputs, as the plan's §4.2 allows.
  QMUL, QDIV, QFRAC and QSQRT are exact. A QDIV/QFRAC by zero or with a quotient over 32 bits stops the run as
  undefined, because p2kb documents no result.
- **CORDIC read semantics.** GETQX and GETQY each take the next result whose own half is unread, and wait for it,
  so `GETQY` ×3 after `QROTATE` ×3 reads the three Y values. A result with one half read is retired by the next
  CORDIC operation. The driver depends on this: its frame reads only the Y halves, and on its drive pass `xStar`'s
  first `GETQX` must see its own `QDIV`. The P2 overwrites an unread result (P2AN002). A result never read before a
  newer one arrives, or a GETQx with nothing pending, stops the run rather than being guessed.
- **Timing is a worst-case model, not cycle-exact.** Instructions take 2 clocks; a taken branch or `_RET_` 4;
  RDLONG 16 (+1 per extra block long, into cog RAM or, after SETQ2, LUT RAM); WRLONG 10 (+1 per extra block
  long); a CORDIC issue 9, with the result 55
  clocks after the issue ends. A drive pass lands on the frame the CT1 schedule names, so the proof does not
  depend on a clock count.
- **Not modelled:** hub execution, interrupts and the debug ISR, SKIPF, the streamer, the FIFO, locks and events
  other than CT1 and ATN. Each stops the run if met.
- **Only exercised paths are compared.** Liveness is taken on the baseline's actual path, so a register is checked
  wherever that path next reads it. A path no scenario takes is not compared; the coverage report shows which.

## Extending it for a work package

- **Keep register names.** A register moved or aliased (C1, C7) is found by name. If a work package removes a name
  that is live, the tool reports `register-missing`.
- **init() changes.** The tool reads `init()`, `swapHallTables()` and `launchDriver()`. It follows every
  `<ptr> := @<label>` into the image by itself, which covers C2's and C8's pointers. It refuses to run if they
  write any other driver DAT symbol it does not fill. C4's packed `deltas` must extend `initmodel.py`
  (`hall_tables()` and `KNOWN_DAT_WRITES`).
- **A new instruction** is added to `p2cog.py`'s decode table with its p2kb key, after compiling it with `pnut-ts`
  and decoding it back.
- **Labels the timing report watches:** `drvMotor` (the pass, and the end of the start frame's first part),
  `planStage` (a stage) and `driverRelease`. If a label is renamed, the report loses that window's name; the
  comparison itself is unaffected. The start frame needs no label: it opens at the last DIR rise on the ADC pins
  before the first pass.
- **A new image** needs nothing but its label pair, `<name>Start` / `<name>End`, under an `org $200`. The tool
  finds it, its SETQ2 loader and its coverage by itself. Keep `all_pins` as the first data long of the cog image,
  or the cog image's coverage ends at its first RES long instead.
- **Keep routine labels** when code moves. The moved-code check matches instructions under a global label both
  builds carry; code whose routine was renamed is counted as changed, not moved, and escapes that check.

## Files

| File | Holds |
|---|---|
| `run.sh`, `pasm_equiv.py` | the command line, the parallel runner, the report, and the coverage and moved-code check |
| `p2image.py` | staging, `pnut-ts -l`, listing and `.bin` extraction, symbols, and image discovery |
| `p2cog.py` | the cog emulator: decode, execute, clocks |
| `drvenv.py` | the hub layout, pins, ADC and hall stimulus, ATN, the CT1 schedule, and the start-frame clock |
| `initmodel.py` | `init()`'s parameter run and DAT patches, and the guard on them |
| `scenarios.py` | the named edge suite and the random scenario generator |
| `equiv.py` | one run, liveness, and the frame-by-frame comparison |

# DEBUG Channels -- Design (task «#3507», PL-8)

**Date:** 2026-09-14
**Status:** Design reviewed by the arbiter. Phase 2 implements it.

**Governs:**
- PL-8;
- plan §2, *DEBUG channels, and remove `useDebug`*;
- Batch 2 of `BENCH-READINESS-SPRINT-PLAN.md`.

**Provenance** follows the project convention:
- **MEASURED** means a log line or a command's output.
- **DERIVED** means a reading of source or of p2kb.
- **STEPHEN** means his words, quoted verbatim.

## 1 · What the language gives (DERIVED, `p2kbSpin2DebugMask`)

- **Compile-time selection.** `DEBUG[n](...)` compiles only when bit `n` of `DEBUG_MASK` is set. A clear bit means "no code generated", and `n` must be 0..31.
- **The mask must exist.** Without `DEBUG_MASK`, the `DEBUG[n]` syntax is a compile error. The mask is an integer CON.
- **Plain `DEBUG()` ignores the mask**, so silencing means rewriting each call.
- **The mask is per file.** A top-level's `DEBUG_MASK` does not reach an included object. MEASURED by compile experiment on 2026-09-10 (plan §2).
- **The mask can come from an included constants object.** `DEBUG_MASK = user.MOTOR_DBG_MASK` compiles, and mask 0 shrank the binary from 9283 to 9270 bytes. MEASURED 2026-09-10, plan §2.
- **No `{Spin2_v##}` directive is needed.**

## 2 · Inventory (DERIVED, read 2026-09-14)

### Counts

| Object | Live `debug()` statements | Commented out (not converted) |
|---|---|---|
| `src/isp_bldc_motor.spin2`, Spin2 section (`:1-2074`) | **75** | `:569`, `:904`, `:927`, `:953-954`, `:1129`, `:1268-1270`, LA block `:1717` |
| `src/isp_steering_2wheel.spin2` | **38** | `:111-113`, `:979` |

The plan's "80 / 39" was counted earlier.

**PASM `DAT` section (`:2076-end`), read in phase 2:** no active `debug` directive. There are two inactive ones:
- `:2361` is commented out with `'`;
- `:2389` sits inside a `{ ... }` block-comment region (the special drive test code).

Neither is converted. This agrees with «#3534»'s read.

### Two false affordances, one class

**`useDebug`** (`isp_bldc_motor.spin2`):
- declared at `:447`;
- set FALSE at `:270`;
- read nowhere.

**`showHDMIDebug`:**
- In `isp_bldc_motor.spin2` it is a VAR at `:448`, set FALSE at `:271`, and read only at `:1596` to gate 16 data-list dump lines.
- In `isp_steering_2wheel.spin2` it is a DAT long at `:1171`, FALSE, and read only at `:1223` to gate 12 dump lines.
- Nothing ever sets it TRUE, in either object.

Both read as verbosity controls and neither is one. Both are removed in the same change: plan §2 says to delete `useDebug`, and D5 says to take the whole family. The dump lines move onto a channel instead.

## 3 · The channel scheme

### One vocabulary, two masks

The same channel numbers mean the same thing in both objects. Each object has its own mask:
- `MOTOR_DBG_MASK` for `isp_bldc_motor`;
- `STEER_DBG_MASK` for `isp_steering_2wheel`.

A user reads one list of channels and picks which object is quiet.

| Ch | Name (`user.`) | What it carries | Default |
|---|---|---|---|
| 0 | `DBGCH_ERROR` | a call could not do what was asked: `!`/`!!` ERROR lines, `*???*`, `[CODE]` | **on** |
| 1 | `DBGCH_WARNING` | an argument was corrected (out-of-range power or speed clamped) | **on** |
| 2 | `DBGCH_FAULT` | driver fault, e-stop and their clearing | **on** |
| 3 | `DBGCH_LIFECYCLE` | cog start, init-derived values, power limits, offsets | on |
| 4 | `DBGCH_DETECT` | board-revision detection results | on |
| 5 | `DBGCH_COMMAND` | drive commands and settings as they are applied (`setTargetAccel`, `driveAtPowerEx`, `setMaxSpeed*`, stop-at-time, direction mix) | on |
| 6 | `DBGCH_SENSE` | sense-task events: stop limit reached, driver state/status changes, distance/rotation reads | on |
| 7 | `DBGCH_VALIDATE` | `*VAL*` results of the `valid*ForChoice()` methods | on |
| 8 | `DBGCH_TEST` | TEST-USE ONLY methods' own lines | on |
| 9 | `DBGCH_HDMI_DUMP` | HDMI data-list address dumps in `getDebugData()` | **off** |

**Why these defaults:**
- **Error, warning and fault stay on.** The plan rules this, and a silent driver is worse than a chatty one for ordinary users.
- **Channels 3–8 stay on**, so every line printed today is still printed: the "default masks reproduce today's output" criterion.
- **Channel 9 is off.** Its lines never print today, because `showHDMIDebug` is never TRUE, so default-off changes no output. It only removes 28 records of dead code.

**Why categories and not severity levels:**
- The bench's need is purpose-shaped: silence command chatter (`setTargetAccel` prints on every command, twice per steering drive) while keeping errors and faults.
- A severity ladder would force errors and command chatter onto one axis.

### Where the constants live

**`isp_bldc_motor_userconfig.spin2`:**
- **Section (1), fixed constants:** the channel enum, `#0, DBGCH_ERROR, ...`. Users do not edit it.
- **A new `CON { DEBUG output }` block,** placed after the six mutually exclusive config blocks and before the "Adjust your configuration ABOVE here" marker. It holds `MOTOR_DBG_MASK` and `STEER_DBG_MASK`, built with `DECOD`:

  ```spin2
  MOTOR_DBG_MASK = DECOD DBGCH_ERROR | DECOD DBGCH_WARNING | ...
  ```

  - It is outside every block, so switching configuration never changes verbosity (plan §2).
  - It is a user-editable section, so it follows the file's "(2)" rule.
  - The file stays CONSTANTS ONLY.

**`isp_bldc_motor_userconfig_bench.spin2`** mirrors both parts with the same default values, so the bench build prints what it prints today. A bench binary that needs silence, such as «#3508»'s timed sections, changes the bench masks as part of its own task, with its own verify line.

**Mirroring rule (`CLAUDE.md`):** none is owed. The constants are in the user config, which both objects already reach as `user.`, and neither object declares a new public enum.

### In each object

```spin2
CON { DEBUG channels -- masks and channel names come from the user config }
    DEBUG_MASK = user.MOTOR_DBG_MASK          ' STEER_DBG_MASK in isp_steering_2wheel
```

**Call form:** `debug[user.DBGCH_ERROR]("! ERROR: ...")`.
- The channel index is a compile-time constant from the user config. Whether pnut-ts accepts an object-constant expression inside `debug[...]` is **tool behaviour**, so the compiler answers it (overlay P7), and phase 2's first edit proves it before converting the rest.
- **Fallback, if it does not compile:** a local CON alias per channel (`DBG_ERR = user.DBGCH_ERROR`) used as `debug[DBG_ERR]`. If that also fails, literal indices with the channel name in a trailing comment.

## 4 · Per-call channel map

Line numbers are as read 2026-09-14; phase 2 confirms each by content.

### `isp_bldc_motor.spin2` (75)

| Channel | Lines |
|---|---|
| ERROR (0) | 113, 258, 367, 421, 578, 594, 604, 609, 631, 641, 649, 725, 743, 827, 1407, 1421, 1454 |
| WARNING (1) | 494, 504, 563 |
| FAULT (2) | 679, 686, 980 |
| LIFECYCLE (3) | 122, 294, 295, 310, 382, 383, 1374, 1434 |
| DETECT (4) | 895, 899, 917, 920, 922, 924 |
| COMMAND (5) | 495, 505, 564, 664, 1441 |
| SENSE (6) | 1792, 1797 |
| VALIDATE (7) | 990, 1003, 1012, 1021 |
| TEST (8) | 532, 534, 1051, 1070, 1071, 1099, 1100, 1136, 1148, 1155, 1157 |
| HDMI_DUMP (9) | 1597–1612 (16) |

17 + 3 + 3 + 8 + 6 + 5 + 2 + 4 + 11 + 16 = **75**.

**Notes on the judgement calls:**
- `:1155` "WAIT-fault-reset ended still-FAULT!" sits in TEST-USE `testResetFault()`. It stays TEST, because it reports a test method's own outcome.
- `:980` "did reset fault ind." is a fault-latch clear, used by steering, so it is FAULT.

### `isp_steering_2wheel.spin2` (38)

| Channel | Lines |
|---|---|
| ERROR (0) | 133, 167, 274, 292, 306, 313, 345, 358, 366, 447 |
| FAULT (2) | 409, 530, 532, 540, 542, 1007, 1136, 1138 |
| LIFECYCLE (3) | 138 |
| COMMAND (5) | 294, 381, 846 |
| SENSE (6) | 417, 453, 1117, 1132 |
| HDMI_DUMP (9) | 1224–1235 (12) |

10 + 8 + 1 + 3 + 4 + 12 = **38**.

**Notes:**
- `:1136`/`:1138` are fault-status lines, so they are FAULT.
- `:1117`/`:1132` are state and status change reports, so they are SENSE.
- `:1007` "WHEEL in EMERGENCY" is FAULT.

## 5 · Removals in the same change

- **`isp_bldc_motor.spin2`:** the `useDebug` VAR (`:447`) and its assignment (`:270`); the `showHDMIDebug` VAR (`:448`), its assignment (`:271`), and the `if showHDMIDebug` gate (`:1596`). The 16 lines under the gate become unconditional `debug[user.DBGCH_HDMI_DUMP]` statements, re-indented.
- **`isp_steering_2wheel.spin2`:** the `showHDMIDebug` DAT long (`:1171`) and its gate (`:1223`). The 12 lines become `debug[user.DBGCH_HDMI_DUMP]`.

**No ABI risk.** None of these longs is in a PASM-addressed VAR run:
- `useDebug` and `showHDMIDebug` are in `VAR { * user request values * }` (`:426-455`), textually before the driver data structure at `:1978`;
- steering has no ABI at all.

Phase 2 still proves the driver VAR runs byte-identical by content diff.

## 6 · Verification (phase 2)

| Check | How | What it proves |
|---|---|---|
| Output unchanged at default masks | Every converted line's text is unchanged, only `debug(` → `debug[ch](`, and every channel 0–8 is on by default. `git diff` shows no string-literal change | today's output is reproduced |
| Channels really compile out | Build once with `MOTOR_DBG_MASK = 0` and once with the default, compare the `.bin` sizes, then restore | **size is the proof**, not silence (plan §2) |
| Range guard | Temporarily use `debug[32](...)` in one statement, expect "DEBUG mask bit-number must be 0..31", then revert | the documented compiler error fires |
| Record ceiling | Count the debug statements a bench top compiles in (both objects plus the binary's own), and report them against the 255-record ceiling. Records and statements are not 1:1: if close, **stop and confirm the measurement** | headroom for «#3508» |
| Gates | `tools/build-check.sh` (every top, both release demos certified); `tools/check_style.sh` exit 0 | no regression |
| ABI | `git diff` of `isp_bldc_motor.spin2` shows no hunk inside `VAR { * Data Structure for PASM Driver * }` or `VAR { Motor Parameters }` | the driver contract is untouched |

**Temporary edits in the size and range checks** go in the user config, the declared `EXCLUSIVE_RESOURCE`. Each is restored and the restore is shown in `git diff`; `tools/build-check.sh` is not run while one is in place.

### Results, phase 2 (2026-09-14)

| Check | Result |
|---|---|
| Call form `debug[user.DBGCH_*](...)` | Compiles under the default config and `-D BENCH_CFG`; no fallback was needed. MEASURED |
| Output unchanged at default masks | `git diff` shows only `debug(` → `debug[user.DBGCH_*](` and the removed flags. No string literal changed: a dropped space in steering's four fault lines was caught in review and restored. DERIVED from the diff |
| Channels really compile out | `isp_steering_2wheel.spin2` compiled with `-d`, which includes the motor object: default masks **24,477 bytes**; both masks 0 **20,262 bytes**. 4,215 bytes eliminated. MEASURED |
| Range guard | `debug[32](...)` gives `src/isp_steering_2wheel.spin2:421:error:DEBUG mask bit-number must be 0..31`, then reverted. MEASURED |
| Record ceiling | **Library contribution:** 75 + 38 = 113 statements with every channel on, and 85 with the default (HDMI_DUMP off). **Whole build:** every bench top compiles under `tools/build-check.sh` at the defaults, so none exceeds the compiler's record limit today. The per-top total (the library plus each binary's own statements) was not counted. «#3508» measures it for its own binary. DERIVED |
| Conversion counts | `isp_bldc_motor.spin2` 75, `isp_steering_2wheel.spin2` 38, counted line by line in the diff. DERIVED |

## 7 · What this does not do

- **The other 37 files are not converted** (roughly 639 calls; option A, STEPHEN 2026-09-10). The two release demos stay on plain `debug()`.
- **No bench mask is chosen.** The bench config copies the defaults; «#3508» chooses its own quiet set.
- **No debug text changes.** A message's wording, typos included ("filed to start"), is not touched here, so the output diff stays empty.

**Outcome:** there are no questions for Stephen. The channel set and names are an implementation call under overlay P3, the placement follows plan §2, and the defaults follow plan §2's "fault and error channels stay enabled".

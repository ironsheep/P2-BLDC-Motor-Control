# PL-44 root-cause study — trapped returns reading 0 (2026-09-14)

**Question:** why every value captured through `x := \method()` in the bench binaries read 0.
**Measured:** 12 instances at 6 sites, 0 counterexamples (`bench/2026-09-14/VISIT-1-RESULTS.md`
§6).

**Standing direction** (STEPHEN, 2026-09-14): *"please expect the compiler to be behaving correctly
and then chase to root cause... don't be giving up without do the proper work required"*.

**Method:**
- A read-only study of every trapped site, end to end.
- The library call chains they run through, and the log lines they produced.
- The P2 knowledge base.

**Result:** no defect in our code explains the zeros.
- Five of the seven hypotheses are refuted.
- The two left, H1 and H7, are confounded: every failing capture had both properties.
- A no-motion probe binary (§3) separates them, and the toolchain hypothesis, in one run.

**Provenance tags:** MEASURED = a log line; DERIVED = a source or knowledge-base reading. Line
references abbreviate as follows:
- `lib` = `src/isp_bldc_motor.spin2`, `steer` = `src/isp_steering_2wheel.spin2`;
- `t0` / `char` / `scan` = `src/test_bench_*.spin2`;
- `114636` / `115953` = `bench/2026-09-14/debug_260914-*.log`.

---

## 1 · Hypotheses

| # | Hypothesis | Verdict | Evidence |
|---|---|---|---|
| H1 | A `debug()` inside the trapped call disturbs the result | **Undetermined** | See the H1 details below. |
| H2 | The capture is right but the print path is wrong | **Refuted** | The wrong value is in memory, not just printed. T0-15a's `bPass` is computed from `startResult` and is FALSE (t0:903, 114636:970), while `rawMotorCog` in the same frame is correct. T0-15b's `bPass` FALSE shows `startResult` ≠ −1 in memory. char's brake guard `wheelMotorCog(side) == startRet + 1` failed in memory (char:2213 → 115953:471 `ready NA`). The same emit path prints the untrapped `BC-START` cog correctly (char:2429). |
| H3 | Multi-result methods lose the first result | **Refuted** | T0-10 and T0-8 trap `\motor.start()` directly as single-result calls and read 0 (t0:1131, :1017). The untrapped two-result `startSide()` delivers its cog (char:1210, :1223-1240). |
| H4 | An abort really happened and the completion flag misreports it | **Refuted** | See the H4 details below. |
| H5 | Caller and callee share a result-variable name | **Refuted** | T0-10 and T0-8 capture into `startResult` while `start()`'s result is `ok` (lib:80), and both read 0. |
| H6 | Stack or frame exhaustion | **Refuted** | Every failing site runs on cog 0's main stack. The untrapped char start chain is deeper and works (`main → \runSession → runAllHolds → measureHold → startHoldWheel → startSide → start → startEx → init`, char:893, :945, :1007, :1113, :1223). The 32-long spacer stacks never run a trapped chain, and T0-15a and T0-10 fail with no spacers. |
| H7 | A trap inside another trap's frame | **Survives, confounded with H1** | See the H7 details below. |

**H1 in detail:**
- **Consistent:** every trapped call expected non-zero ran library debug inside it (114636:957-967; 115953:258-281, :404-407).
- **No counterexample exists:** the only trapped callees without debug inside return 0 by design (t0:1073-1082, :1098-1108).
- **Weak mechanism:** the debug ISR saves registers `$000-$00F` only (`p2kbArchDebugInterrupt`), but Spin2 locals live in the hub stack frame except inside inline PASM (`p2kbSpin2InlinePasm`), and none was found in the chain.
- **Against it, measured:** untrapped calls return correctly with a debug as their last statement (lib:122; char:1238; scan:3452).

**H4 in detail:**
- T0-15a logs `aborted,FALSE` (114636:969), and `startCall` has nothing after clearing the flag (t0:1056-1057).
- Every library abort site read is either preceded by an ERROR line or was passed without firing.
- For `steerDriveTrapped`, `driveAtPowerEx` completed for both wheels (115953:405, :407), and the rest cannot abort (steer:262-264; lib:1444-1448). So `aborted,DRIVE` came from `bDriveDone <> TRUE` (char:1982), a wrong value, not an abort.

**H7 in detail:**
- **Shared by every failing site:** each capture is a `\` call inside another trap's frame (T0 main per-test traps t0:257-295; char `\runSession()` char:893).
- **The untrapped successes are nested too:** they run inside a top-level trap (char:893, scan:1186), but they are not themselves trapped.
- **No clean capture exists:** no trapped capture made from a frame with no enclosing trap was ever logged. `\runSession()` and `\runScan()` print their value only on abort (char:2556, scan:1187-1188).

**Not yet separable:** whether the trap assigns 0 or assigns nothing. Every receiving variable was
already 0.

## 2 · Where it stands

- **The value is lost at the trapped expression call itself.** In `startTrapped`, the inner
  `motor.start()` is untrapped and returns correctly, as its sibling calls show. The loss is at
  `\startCall()` (t0:1046).
- **Confidence is low** that the cause is H1 or H7. Neither has a mechanism derivable from documented
  behaviour.
- **Per the standing direction, no conclusion about the toolchain is drawn.** The probe decides.
- **If the probe's top-level, no-debug trap cell also reads 0,** the evidence would point at how a
  trapped expression call returns its result. That can then be examined statically, by comparing
  the compiled form of `v := retK()` against `v := \retK()`, before anything is taken to Stephen.

### Disposition (2026-09-14): design the patterns out; the probe below is not built

STEPHEN: *"you are leaning to bench runs when you should be leaning to choosing code patterns that
are not problemmatic... the possible patterns you cite sound like antipatterns that we shouldn't
have in our code in the first place."*

The suspects that remain are a trap used to capture a normal return value, and a trap nested inside
another trap. Neither belongs in our code. «#3539» removes them:
- normal calls are checked with `getError()`;
- one top-level trap prints its value on every run;
- traps remain only in deliberate abort-path tests, which assert a named code.

The spec below is kept as a record of the analysis, not as planned work.

## 3 · Discriminating probe — `test_trap_probe.spin2` (spec, not built)

No motion. Cog 0 only. One child object, `probe_child`.

**Cell rules:**
- **K = 1000 + cell number**, so a crossed variable shows up as another cell's K.
- **Pre-load the receiving variable with `$5A5A_0000 + cell` before the call.** Reading the sentinel
  means the trap assigned nothing; reading 0 means it assigned 0.
- **The callee also writes K to a VAR `echo`** (a hub write, no debug), proving it computed the value.
- **The caller does nothing** between the call and its record line.

**Callees:**
- `retK()`: `r := K`, no debug.
- `retKText()`: `debug("in")`, then `r := K`.
- `retKLocal()`: `loc := K`, `debug(sdec(loc))`, `r := loc`.
- `retMulti()`: `r := K`, `s := 2000 + cell`.
- `wrapMulti() : a, b`: `a := \retKText()`, `b := 2000 + cell`, called as `v, w := wrapMulti()`.
  This mirrors `startTrapped`.
- `retSameName() : r`, captured into a caller local also named `r`.
- `abort7()`: `r := K`, then `abort -7`.
- `abort7Dbg()`: a debug, then `abort -7`.
- `deep(12)`: recurses 12 levels with a debug at the bottom and returns K.
- `child.retK()` and `child.retKText()`.

**Cells.** Cells 01-13 run directly from `main` with no enclosing trap. Cells 21-33 are the same,
inside `nestRunner()`, which `main` calls as `\nestRunner()`.

| Top / nested | Call | Axes |
|---|---|---|
| 01 / 21 | `v := retK()` | untrapped control |
| 02 / 22 | `v := \retK()` | debug NONE, single result, different name |
| 03 / 23 | `v := \retKText()` | debug TEXT |
| 04 / 24 | `v := \retKLocal()` | debug LOCAL |
| 05 / 25 | `v, w := wrapMulti()` | multi through a wrapper |
| 06 / 26 | `v := \retMulti()` | multi, direct |
| 07 / 27 | `r := \retSameName()` | same name |
| 08 / 28 | `v := \child.retK()` | object, debug NONE |
| 09 / 29 | `v := \child.retKText()` | object, debug TEXT |
| 10 / 30 | `v := \abort7()` | abort, expect −7 |
| 11 / 31 | `v := \abort7Dbg()` | abort after debug, expect −7 |
| 12 / 32 | `v := \deep(12)` | deep chain, trapped |
| 13 / 33 | `v := deep(12)` | deep chain, untrapped |

**Library bisection, run last and nested:**
- **40:** `v := \motor.start(P16…)`, echo `testGetMotorCog()-1`, then `stop()`. Positive control: the
  symptom reproduces in this binary.
- **41:** a trapped wrapper that calls `motor.testSetup()` untrapped, then returns K.
- **42:** a trapped wrapper that calls `motor.getBoardType()`, then returns K.

**Record format:**

```
PROBE,cell,NN,ctx,TOP|NEST,trap,Y|N,dbg,NONE|TEXT|LOCAL|DEEP,res,SINGLE|MULTI,name,SAME|DIFF,callee,LOCAL|OBJ|LIB,expect,<sdec>,pre,<uhex>,got,<sdec>,got_hex,<uhex>,echo,<sdec>,eq,TRUE|FALSE,flag,TRUE|FALSE
```

- `eq` is computed in memory.
- `flag` is the completion flag.
- The run ends with `PROBE-END`, then `DEBUG_END_SESSION`.

**Expected failures by hypothesis.** "Fail" means 0 or the sentinel; abort cells read −7 unless the
trap is broken outright.

| Hypothesis | Cells that fail |
|---|---|
| Documented semantics | none of 01-33; if only 40-42 fail, the cause is in the library call chain |
| H0 — the trap never returns a normal value | 02-09, 12, 22-29, 32 |
| H1 — debug inside the callee | 03, 04, 05, 09, 12, 23-25, 29, 32 |
| H1, local-read variant | 04, 12, 24, 32 |
| H3 — multi-result | 05, 06, 25, 26 |
| H5 — same name | 07, 27 |
| H7 — nested trap | 22-29, 32 |
| H1 and H7 together | 23-25, 29, 32 |
| H6 — stack depth | 12, 32 (and 13, 33 if depth alone) |

Two further readings:
- **H2** shows as `eq` TRUE while `got` prints wrong, or `got` equal to another cell's K.
- **H4** shows as `flag` TRUE on a non-abort cell, or an abort cell not reading −7.

## 4 · Other defects found (DERIVED), for «#3539»

1. **The char PL-36 claims check was masked.** `char:1887-1888` calls `steerStop()` whenever the
   return is not −1, and the broken capture made it always not −1, contradicting its own comment at
   `:1892`. So `claims_free,TRUE` (115953:420) was measured after the claims had been released.
2. **T0 guards accept a stuck 0:** `startResult >= 0` at t0:942, :621 and :685. R10-T0-STOPREADY's
   PASS (114636:1004) rests on :942. The free-cog counts 7 → 6 → 6 → 7 independently show the
   starts happened.
3. **The completion-flag rationale** (t0:191-192) rejects a pre-loaded sentinel, the one value that
   tells "assigns 0" from "assigns nothing".
4. **A false comment:** t0:69-72 says an ERROR line precedes every abort. lib:1375-1376 aborts bare,
   with no ERROR line (PL-47).
5. **`steerDriveTrapped` reports a wrong value as an abort** (char:1982). Report the two separately.
6. **Both harnesses print the top-level trap value only on abort** (char:2556, scan:1187-1188).
   Printing it every time gives a free single-level trap check on every run.
7. **Misleading comments:** t0:1000-1006 says −1 "overlaps" the trapped-abort 0; t0:160 calls −1
   "coginit()'s documented failure form", but −1 is `start()`'s own contract and coginit's observed
   form is `$8000_xxxx` (lib:110-112).
8. **Outside this repo:** `p2kbSpin2MethodDefinition`'s register-mapping note contradicts
   `p2kbSpin2InlinePasm`.

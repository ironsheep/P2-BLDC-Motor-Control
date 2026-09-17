# Visit 5 — run sheet (unattended)

Run each command from the project root, in order. I read every log.

**Panic: PHYSICAL BATTERY DISCONNECT.** Nothing on the rig reaches the harness while it drives.

**Pull first.** Then check each banner before anything else — a load whose banner reads an older revision
certifies nothing, and Visit 3's first attempt was lost exactly that way (PL-68):

| Load | Banner must read |
|---|---|
| `t0` | `src_rev 2` |
| every `dual-*` | `src_rev 14`, `fmt 5` |

⭐ **The runner now checks this for you as well, in a way it could not at Visit 4.** After each load it
reads the log the run just wrote and **refuses** if the image emitted nothing — no `CogN INIT` line, or
INIT lines and not one program line. That is the Visit 4 `t0` failure (PL-74), which cost the whole tier
and was not noticed until the logs were read hours later. If you see an `ERROR:` line from
`bench-run.sh` after a run, that load certified nothing: power-cycle the P2 and run that tier again.

**Every run is wheels-lifted.** Rev B platform, on blocks, both wheels up and free, both motors connected,
pack charged. Nothing on this sheet needs the platform to move across a surface.

## The visit, declared

Seven attributes, per *Shared vocabulary — the bench visit* (`~/.claude/skills-docs/SKILLS-AUTHORING.md`).

| | |
|---|---|
| **Purpose** | **Certification of a repair cycle.** Visit 4 found no driver defect that survived the source read; every change since is to the harness or to a criterion. This visit says whether the instruments now measure what they name. |
| **Hardware risk** | Lower than Visit 4, and the same in kind: half speed, stopped dead, an e-stop latched and held, and the current limits lowered until the motor cannot turn. All of it wheels-up, and **no step needs your hands on the platform at any moment.** Panic: physical battery disconnect. |
| **Who can observe** | **Nobody.** Every load is unattended and every verdict is printed in the log. You are present for safety only — no cell asks you to read, judge or type anything. |
| **Runs that carry state** | **None across loads.** Within `dual-d` the current limits are lowered and restored with a read-back; within `dual-b` the commutation offsets are written 180° out and restored with a read-back. A load that ends early leaves its restore undone, so **if one stops short, say so and leave the next one until I have read that log.** |
| **Run length** | **~14 minutes of running.** Measured at Visit 4: `dual-a` 5 min 39 s, `dual-b` 5 min 18 s, `dual-d` 54 s. **`dual-b` should run LONGER this time, not the same** — its four distance trials moved nothing at Visit 4 and its fault trial aborted after 200 ms, so if the segment works it gains roughly half a minute of actual driving. `t0` has never completed since its cells were added; ~2 min, derived from its own holds. |
| **Repeatability** | Every tier is repeatable and idempotent — a re-run costs only time. Faults are provoked and recovered inside the run; nothing needs a power cycle between loads. |
| **Variant matrix** | Four tiers × one clock (270 MHz, the file's own default) × one rig (Rev B, paired 6.5in, 18.5 V). |

---

## What each load can decide that Visit 4 could not

Every load below is here because a specific reading changed underneath it. A load whose result would be
arithmetic on Visit 4's numbers is not on this sheet.

| # | Command | Time | What the RUN decides |
|---|---|---|---|
| 1 | `tools/bench-run.sh t0` | ~2 min | **Ten cells that are NOT_BUILT.** Nothing about this binary changed; the runner around it did. |
| 2 | `tools/bench-run.sh dual-d` | ~1 min | **The repair cycle's own proof.** The stray errors, the time stop, and the derate criterion. |
| 3 | `tools/bench-run.sh dual-b` | ~6 min | **Whether the OVERSHT segment runs at all** — at Visit 4 every distance trial was refused and nothing moved — plus the stop-current bound. |
| 4 | `tools/bench-run.sh dual-a` | ~5½ min | The split rate/fold verdict, and the lag bound on a full ladder. |

---

## Step 1 · `t0` — **the error contract has no run-time evidence at all**

Ten cells have been NOT_BUILT since Visit 4, and **they gate the 6.0.0 tag** («#3516»): `R16-T0-BADGROUP`,
`PINSKEEP`, `LIMKEEP`, `NOABORT`, `STRNOTSTART`, `STEERCOGS`, `RESTZERO`, `NOBOARD`, `FRONTFAIL` and
`R1-T0-RESTART`. Nothing else in the tree carries them.

**The binary is unchanged and that is deliberate.** Visit 4's image was a debug build — measured: 43 784
bytes with `-d`, 25 764 without, against the 43 780 that downloaded — so the compile was right and the
kernel that was in it never spoke. Why it did not is undetermined, and no mechanism is offered for it
(PL-74). What changed is that a repeat now costs seconds instead of the tier.

**No motion at all.** Every start commands zero speed.

---

## Step 2 · `dual-d` — **this is where the repair cycle is actually proved**

Run this second, not last: it is under a minute and it is the load that says whether the fixes took.

- **The stray errors should be gone.** At Visit 4 the single-wheel half printed five
  `driveAtPowerEx() motor not started` / `clearEmergency() -1_007` lines while its cells passed. The
  cause is identified: a `? :` selecting between two method calls runs **both**, so every command
  addressed to the LEFT wheel also reached the never-started RIGHT one, which answered and printed
  (PL-76, PL-29). Eleven sites are now `if`/`else`. **The observable is the absence of those lines** —
  and the steering half, which never had them, is the control.
- **`TIMESTOP` should return a number instead of NOMEAS.** In both forms. It could not pass before: the
  rest wait was as long as the stop limit it was waiting past, and the criterion was smaller than the
  harness's own 300 ms rest-confirmation dwell (PL-83). Both are computed from their constants now.
- **`DERATE` judges derating, not a clock.** The arrival-time window is deleted — it could not be derived
  on a lifted wheel, and Visit 4 put the two wheels on opposite sides of it from one drive. A wheel that
  never reaches the continuous limit is now NOMEAS, not a FAIL (PL-80).
- **`FRONTST` is the one to watch for a change in the driver's favour.** Visit 4 read `stack_hi 128` of
  `stack_of 128` — saturated, and indistinguishable from an overrun. The steering object now has its own
  256-long stack (PL-75), so `stack_of` should read 256 and `stack_hi` should land well under it. **If
  `stack_hi` still equals `stack_of`, stop and tell me**; that would mean the true requirement is above
  256 and the measurement is still saturated.

**It still lowers the current limits until the motor cannot turn.** The wheels stand still under power and
buzz for about four seconds during the protective-stop step, then release themselves. That is the test,
not a fault.

---

## Step 3 · `dual-b` — **faults on purpose, and twenty stops from speed**

- **`STOPCUR` is judged against a fixed bound now.** Visit 4 failed it on its own reference: the hold
  current it was compared against drifts ~25 % as a motor warms and resets when the other motor starts,
  while the stop peak is flat to ±4 % across a 455× sweep of ramp rate (PL-82). The record gains
  `hold_pk_mV` and `bound_mV`, so the comparison is readable without the verdict carrying it.
- **`DISTM` can certify something for the first time.** At Visit 4 it compared a saved tick snapshot
  against a live distance read while claiming both came from one instant, and its prediction took
  `abs()` while the library's getter is signed — so it could not tell a conversion fault from two reads
  taken moments apart. Both are fixed and the record now prints the tick count the getter saw (PL-77).

### ⭐ The one field that matters most on this sheet: `str_mm_x100`

**At Visit 4 the whole OVERSHT segment did nothing, and nobody knew.** Every distance trial was refused
— `driveForDistance() rejected eError = -1_012` (`ERR_LIMIT_UNRESOLVABLE`) — and every captured sample
reads `pos,0 st,STOPPED`. The cause is one value: **the steering object's own `tickInMM_x100` held about
−544,643 instead of 576.** That single number produces both the refusals and `getDistance(DDU_M)`
returning −14,640, and the record could not show it because the harness was printing the *motor*
object's copy (PL-84).

`BM-DISTM` now prints **both** copies. They are equal by construction, so:

- **`str_mm_x100` reads 576** → the corruption is gone, the OVERSHT segment runs for real, and
  `R16-DUAL-STOPLIM-B`, `R14-DUAL-FLTAPI-B` and `R16-DUAL-FLTRETRY-B` come back with it. **Finding C-3,
  the distance overshoot, is unmeasured at Visit 4 and is this segment's primary job** — this is the run
  that gets it.
- **`str_mm_x100` reads anything else** → the cell FAILs and names the cause, instead of the segment
  quietly measuring nothing for a second visit.

⚠ **Either answer is worth the load, and neither needs anything extra from you.** The leading suspect is
the steering front cog's stack, which read *saturated* in the same visit and sits two longs before this
variable — that is why `dual-d`'s `FRONTST` reading (step 2) and this field are worth reading together.
**It is a suspect, not a conclusion.**

---

## Step 4 · `dual-a` — **the ladder, and the two cells that were one**

- **`NOFOLD` and `RATELAW` are separate cells now.** One compound verdict used to cover both claims over
  every base rung, and rung 0 failed it unconditionally — ±3 % is narrower than the ~7.5 % one tick is
  worth in a 13-tick count — so a real fold-back at any rung was indistinguishable from that arithmetic
  (PL-79). `RATELAW`'s band now carries each rung's own quantisation. **What the run adds over arithmetic
  on Visit 4's numbers is the split verdict itself**: a `NOFOLD` that speaks alone, on a fresh ladder.
- **`LAGBND` against the new bound, on the widest range of speeds we drive.** The bound is the driver's
  own fault test, 124, rather than the round 110 that failed a correct driver in every part (PL-78).
  Part A is the ladder, so it is the part with the most chances to exceed it.
- **`err_pk` at rungs 1–11 is the slam's own measurement, and rung 0 is the built-in control.** PL-78's
  driver fix resets the ramp to `ramp_min_` on **every** speed change, not only from rest. The prediction
  is that `err_pk` falls toward `err` at rungs 1–11 while rung 0 is unchanged. That is read from the log;
  nothing is asked of you.

⭐ **If the platform still slams through the rung changes the way you felt it at Visit 4, tell me** — that
is the one observation this visit asks for, and it is named here **before** the run rather than after.
Everything else is in the log.

---

## Stop and tell me if

- a wheel keeps turning when the log says the run is over
- `bench-run.sh` prints an `ERROR:` line after a load
- anything hangs, smells, or gets hot
- anything happens the sheet didn't say would

Notes go in `BENCH-OBSERVATIONS.md` — what you saw, not what you think it means.

---

## Not on this sheet, and why

- **`dual-c`** — nothing underneath it moved. `STPDECEL` measured 75 ticks on both motors at Visit 4
  against Visit 3's 74–77, and `OFFREST` passed. Its `LAGBND` instances would be re-measured against the
  new bound, but Visit 4's own 116 already sits under 124, so that is a division, not a run.
- **`dual-clock-200/-270/-300`** — `CLKFRAME` was certified at all three clocks at Visit 3, and nothing
  since has touched the frame count.
- **`char`** — every cell passed at Visit 4 and nothing it measures has changed.
- **`scan`** — the offset scan is motor characterisation, which is its own sprint (doctrine overlay P10).
- **`dual-brake`, `dual-ui`, `dual-floor`, `t0-hand`** — attended, and nothing in this repair cycle needs
  a person at the rig.
- **`detect`, `detect-lib`, `detect-phase2`, `spin`** — nothing owed: no change touches detection or
  wiring. `R2-DETECT-OVERLAP` is still owed to a build that does not exist yet (PL-67).

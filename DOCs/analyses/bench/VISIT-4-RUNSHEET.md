# Visit 4 — run sheet (unattended)

Run each command from the project root, in order. I read every log.

**Panic: PHYSICAL BATTERY DISCONNECT.** Nothing on the rig reaches the harness while it drives.

**Pull first.** Then check each banner before anything else — a load whose banner reads an older revision
certifies nothing, and Visit 3's first attempt was lost exactly that way (PL-68):

| Load | Banner must read |
|---|---|
| `t0` | `src_rev 2` |
| `char` | `src_rev 7`, `fmt 7` |
| every `dual-*` | `src_rev 13`, `fmt 4` |

**Every run is wheels-lifted.** Rev B platform, on blocks, both wheels up and free, both motors connected,
pack charged. Nothing on this sheet needs the platform to move across a surface.

## The visit, declared

Seven attributes, per *Shared vocabulary — the bench visit* (`~/.claude/skills-docs/SKILLS-AUTHORING.md`).

| | |
|---|---|
| **Purpose** | **Certification**, not diagnosis. Six committed code tasks, none yet on the bench. |
| **Hardware risk** | The platform is driven at half speed, stopped dead, jerked to a stop by a provoked fault, and **held under power against a lowered current limit until the driver latches a protective stop**. All of it wheels-up. **No step needs your hands on the platform at any moment.** Panic: physical battery disconnect. |
| **Who can observe** | **Nobody.** Every load is unattended and every verdict is printed in the log. You are present for safety only — no cell asks you to read, judge or type anything. |
| **Runs that carry state** | **None across loads** — each tier is a fresh load on a fresh start. Within `dual-d` the current limits are lowered and restored with a read-back before the load ends; within `dual-b` the commutation offsets are written 180° out and restored with a read-back before the retry. A load that ends early leaves its restore undone, so **if one stops short, say so and leave the next one until I have read that log.** |
| **Run length** | ~20 min of running; longest single load `dual-b` at ~6 min. No load can exceed its own 15–20 min run cap. |
| **Repeatability** | Every tier is repeatable and idempotent — a re-run costs only time. Faults are provoked and recovered inside the run; nothing needs a power cycle between loads. |
| **Variant matrix** | Six tiers × one clock (270 MHz, the file's own default) × one rig (Rev B, paired 6.5in, 18.5 V). The 200/300 MHz clock sweep is **not** in this visit — `CLKFRAME` was certified at all three at Visit 3 and nothing since has touched the frame count. |

---

## What this visit is for

Six code tasks are committed and **none of them has been on the bench**: the error contract («#3554»,
«#3555»), the front cog («#3513»), the API contract fixes («#3556»), current limiting with the bounded stop
and the protective stop («#3558»), and stops at rest at their limit («#3559»). Every load below certifies
part of that, and each cell prints its own verdict — PASS, FAIL, NOMEAS or NOT_BUILT.

| # | Command | Time | Certifies, and what the unfixed driver did |
|---|---|---|---|
| 1 | `tools/bench-run.sh t0` | ~1–2 min | The error contract, with **no motion at all**: an illegal pin group returns −1 and starts no cog (it used to abort the program); validate-then-start leaves P8–P15 alone (PL-48); a stop limit with bad units returns a code and leaves an armed limit armed; `getPower()` reads 0 after a stop; a steering stop limit before `start()` returns `ERR_NOT_STARTED`; `getCurrent()` reads 0 at rest and 0 with no board detected (PL-45, PL-25) |
| 2 | `tools/bench-run.sh char` | ~2 min | The brake-mode start, rebuilt on the front-cog contract — the harness no longer sends its own ATN to a driver the front cog owns — and the steering object's per-wheel `getError()` naming the wheel that failed |
| 3 | `tools/bench-run.sh dual-d` | ~3 min | **New load.** The front cog's contract and current limiting; see below |
| 4 | `tools/bench-run.sh dual-b` | ~6 min | Stops land **at** their limit (they used to run ~77 ticks past); a stop from speed stays inside the current the hold drew (it used to surge 20–50 % above it and trip the 10 A abort, PL-55); a ramp the rotor cannot follow **droops instead of faulting** (3 of 3 faulted at Visit 2 in 96–186 ms); the fault API, and the same power after a fault running again (PL-66); `getDistance(DDU_M)` against the ticks it comes from |
| 5 | `tools/bench-run.sh dual-c` | ~2 min | The stop from half speed still takes about as long as it did (74–77 ticks at Visit 3) now that current limiting and the lag limiter act on that ramp; provoked faults and e-stops as before |
| 6 | `tools/bench-run.sh dual-a` | ~5 min | Below the MOSFET limits the new current limiting must do **nothing**: every base ladder rung still turns at the rate the speed law predicts and the derate never engages |

About 20 minutes of running. Times 4, 5 and 6 are what Visit 3 measured, plus the new work each load
carries; times 1 and 3 are derived from the steps' own holds and are first runs.

**Every motion load now also prints `BM-LAG`** — the largest position error the instrument saw, per wheel.
That is the lag limiter's invariant. A driver without it saturates the field at 127; the cell passes at 110
or below.

---

## Step 3 · `dual-d` — **the wheels stop dead, jerk, and stand still under power on purpose**

This is the one load that has never run. Everything it does, it does deliberately:

- **It latches an emergency stop and holds it.** The platform stops hard and stays stopped for a second and
  a half while the harness reads it back. The old e-stop cancelled itself after about 125–250 ms (finding
  S-4); this is the load that says whether it still does.
- **It orders a stop while a second cog is driving.** A helper cog issues drive calls every 25 ms through
  the whole step; the stop arrives in the middle of them. Both wheels must end in one state.
- **It runs a time stop**, and measures how far past the deadline the platform actually came to rest.
- **It lowers the current limits until the motor cannot turn.** At 1 A the drive cannot serve the rotor, so
  the wheels stand still under power, buzz, and the driver latches a **protective stop**. The harness then
  proves the stop refuses every drive, that clearing the *emergency* stop does **not** release it, that
  `clearProtectiveStop()` does, and that the platform drives again once the real limits are back. **The
  MOSFET limits are restored and read back before the load ends.**
- **It stops the objects and times the shutdown**, for both shapes: the steering object (3 cogs) and one
  wheel on its own (2 cogs).

If a wheel is still standing under power when you expect the load to be over, that is the protective-stop
step, and it releases itself within about four seconds.

---

## Step 4 · `dual-b` — **faults on purpose, twice, and now stops from speed twenty times**

The ramp sweep runs as it always has, but each trial that reaches speed now **stops from speed inside the
same capture** — that is the new measurement, and it is why this load is a minute longer than at Visit 3.

At the very end, after the four distance runs, the harness provokes one more fault. **The provocation
changed:** the hard ramp it used at Visit 3 no longer faults anything (that is what the lag limiter is
for), so it now writes a commutation offset 180° from the running pair on both wheels, which holds the
field where the rotor cannot follow. Both wheels jerk and stop. Then it restores the offsets, reads them
back, and drives again **at the same power** to see the motor run. That last drive is PL-66.

---

## Stop and tell me if

- a wheel keeps turning when the panel or the log says the run is over
- anything hangs, smells, or gets hot
- anything happens the sheet didn't say would

Notes go in `BENCH-OBSERVATIONS.md` — what you saw, not what you think it means.

---

## Not on this sheet, and why

- **`dual-clock-200/-270/-300`** — `CLKFRAME` was certified at all three clocks at Visit 3. Nothing in the
  six tasks touches the frame count, so a re-run could not tell a working build from a broken one.
- **`scan`** — the offset scan is motor characterisation, which is its own sprint (doctrine overlay P10).
- **`dual-brake`, `dual-ui`, `dual-floor`, `t0-hand`** — attended, and nothing in this visit's six tasks
  needs a person at the rig. The rebuilt panel still has not run; it waits for a visit that needs it.
- **`detect-phase2`, `spin`, `detect`** — nothing owed: no task in this revision touches detection or
  wiring.

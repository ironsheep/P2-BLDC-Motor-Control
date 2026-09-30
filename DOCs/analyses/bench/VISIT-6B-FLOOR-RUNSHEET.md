# The window-free visit — run sheet (your only instructions)

**Plan:** `DOCs/plans/WINDOW-FREE-BENCH-SPRINT-PLAN.md` (Plan A). **Rewritten 2026-09-30** for the window-free tests; the
countdown-board sheet it replaces is in git history.

Everything you need is on this page. No window opens, nothing is clicked, no key is pressed and no board is moved. Each
command does **one action once**; a repeat is the same command again. Every run starts with a **10-second lead-in**: the
terminal prints a `LEAD-IN` line and **nothing moves for 10 seconds**. Every floor run ends with a line starting
**`RESULT:`** that says in plain words what happened and, where it matters, what to do next.

---

## 1. Get the tests onto the Pi

Use one of these, not both.

- **The pack (simplest).** Copy `dist/bench-<commit>.zip` (the commit is named in the hand-back's BENCH line) to the Pi,
  unzip it, `cd` into its `bench-<commit>/` folder, and type each command below with `./bench-run.sh` in place of
  `tools/bench-run.sh`. It prints the commit it was built from before each run. Its logs land in the folder's `logs/`.
- **Pull.** On the Pi: `git pull`, then run the commands as written. `git log --oneline -1` must show the commit the
  hand-back names.

## 2. Check the first lines of each log

| Test | The banner line must read |
|---|---|
| `t0-reva` | `* test_bench_t0 -- T0-27 Rev A fold-back, Rev A platform: ... -- src_rev 29` |
| every `floor-*` except `floor-rc` | `BM-BANNER,...,src_rev,69,fmt,43,part,SPIN,...,action,<the action>`; `BM-PLAN` lists that one action only |
| `floor-rc` | `RC-BANNER,...,src_rev,3,...` |

An older number means an old tree or pack: stop and tell me.

## 3. The visit, declared

| | |
|---|---|
| **Purpose** | **Certification** on the release-candidate driver (DRIVER_REV 46): the Rev A current fold-back (Rev A platform, wheels up), then every claim that needs a load (Rev B platform, on the floor), then your drive of the new ramps with the FlySky |
| **Hardware risk** | Rev A: wheels up, current limited to 2 A, power 20 at most. Floor: **wheels down, you present.** Every drive is armed with its own limit before it moves: straight drives at most 1 m, spins at most one platform turn; the program stops any drive 35 mm (6 hall ticks) past its limit; the 10 A abort applies. Speeds: a slow walk (0.16–0.23 m/s) and spins up to a quarter of full speed. **There is no stop button: to stop a run, lift the wheels and disconnect the battery.** |
| **Who acts** | You. Rev A: one grip. Floor: you are (or place) the obstacle, you hold the platform back in `floor-grab`, you put the platform back by hand between runs, and you drive `floor-rc` |
| **Runs that carry state** | None. Each run starts and stops its own motors; a changed setting is restored before its run ends |
| **Run length** | About 50 s for Rev A; 20–65 s for each floor run, with the terminal's start and load before it; `floor-rc` as long as you drive. With set-up between runs, about 30–40 minutes for the day |
| **Repeatability** | Every run is repeatable and independent: rerun any command whenever its result line says to, or whenever you want |
| **Variant matrix** | Rev A platform (two Rev A boards) for `t0-reva`; Rev B platform for the rest. 6.5in hub motors, 18.5 V pack, 270 MHz, DRIVER_REV 46, the built-in ramp rates |

---

## 4. First: the Rev A platform, on the bench, wheels up

**Set-up:** the Rev A platform as it is (nothing is moved or swapped), wheels up and free, pack connected.

```bash
tools/bench-run.sh t0-reva
```

| From Enter | What happens | What you do |
|---|---|---|
| a few seconds | the terminal starts and loads the program; its first lines are records | nothing |
| 10 s | `LEAD-IN` line: nothing moves | stand where you can reach the **RIGHT** tyre |
| ~3 s | both motors start (a faint pulse, nothing turns); it prints which board each side read | nothing. If a side prints **FINDING**, it did not read as Rev A and is not driven: note it |
| ~16 s | the **LEFT** wheel turns slowly, stops, turns more slowly, stops | nothing |
| ~14 s | the **RIGHT** wheel does the same, but its second slow turn **does not stop: it speeds up**, and the terminal says **GRIP** | **grip the RIGHT tyre firmly at once, and keep holding** (it may slow or stop against your hand; that is expected) |
| ~7 s | the program stops the wheel and says to let go | let go |

**It decides:** the Rev A fold-back no longer cuts the drive on an unloaded wheel (the four slow turns), and it still
cuts in under your grip. If your grip came late or was light, the log says so and I will tell you; you do not need to
judge it.

Then: battery off, the Rev B platform onto the floor.

---

## 5. Then: the Rev B platform, on the floor

**Before the first run.**

| What | Why |
|---|---|
| A straight lane 1.5 m long, 0.5 m wide, hard floor, clear | the straight runs go at most 1 m |
| A level space 1 m clear all round | a spin is at most one turn |
| The tether routed from above the centre, or with 3 m free, slack | the runs go 1 m out and one turn each way |
| An obstacle: you, or an object that cannot move | `floor-obstacle-*` |

"LEFT" is the platform's left, seen standing behind it facing forward.

**After every floor run:** read the `RESULT:` line, put the platform back at its start **by hand** (its wheels roll
freely once a run ends), then run the next command.

### 5.1 `floor-obstacle-coast`, then `floor-obstacle-short`

```bash
tools/bench-run.sh floor-obstacle-coast
tools/bench-run.sh floor-obstacle-short
```

| | |
|---|---|
| **Where you stand** | 0.3–0.8 m in front of the platform, square across its path (or put the object there); keep clear of the wheels |
| **Timeline from Enter** | terminal start and load; the 10 s lead-in; the platform creeps forward at 0.16 m/s (current limited to 2 A), meets the obstacle and pushes gently; **about one second after it stops moving it stops itself**; a few seconds of checks (it may push once more for an instant). About 40 s in all |
| **What you do** | nothing: stand still if you are the obstacle |
| **The result line** | `RESULT: OBSTACLE COAST -- the platform stopped itself on the obstacle (the protective stop latched)` (and the same for SHORT). If it says it **never met the obstacle**, stand it nearer and run it again |
| **The difference between the two** | after the stop, COAST leaves the wheels free and SHORT leaves them braked (harder to push back) |

### 5.2 `floor-grab`

```bash
tools/bench-run.sh floor-grab
```

| | |
|---|---|
| **Where you stand** | beside its **LEFT** side, a hand ready, the lane clear ahead |
| **Timeline from Enter** | terminal start and load; the 10 s lead-in; it rolls straight at a slow walk (0.16 m/s, current limited to 4 A) and stops itself at 1 m. About 45 s in all |
| **What you do** | **about 3 seconds after it starts rolling, take hold of its LEFT side firmly and keep holding until it stops by itself at 1 m**: enough to slow it to about half speed, not enough to stop it. No click, no key, no let-go cue: the program times its own window from the start of the drive, and a hold begun between about 2.5 and 3.5 s after it starts rolling covers it |
| **The result line** | `RESULT: GRAB -- judged: the hold was read`. If it says `too light: hold harder next run` or `stalled: hold less next run`, run it again and do as it says |

A hold let go and taken again counts as two, and fails the check that the platform does not hunt. Hold once, steadily.

### 5.3 `floor-faultrun`

```bash
tools/bench-run.sh floor-faultrun
```

| | |
|---|---|
| **Where you stand** | beside the lane, clear of it |
| **Timeline from Enter** | terminal start and load; the 10 s lead-in; **1 m forward** at 0.23 m/s; `STAND CLEAR: the platform drives back in 5 s`, 5 still seconds; it **drives back**; about a second later the LEFT wheel is **faulted on purpose** and both wheels stop within half a second, the platform turning a few degrees at most; it recovers; `STAND CLEAR: the platform drives on to its start in 5 s`, 5 still seconds; it **drives on to its start**. About 65 s in all |
| **What you do** | nothing |
| **The result line** | `RESULT: FAULT RUN -- fault seen and recovered: the drive on to the start drew normal current` |
| **After** | it ends at or near its start: put it exactly there by hand |

### 5.4 The ten spins

Run them in this order, so each clockwise turn is followed by the counter-clockwise one and the tether unwinds:

```bash
tools/bench-run.sh floor-spin-slow-right
tools/bench-run.sh floor-spin-slow-left
tools/bench-run.sh floor-spin-med-right
tools/bench-run.sh floor-spin-med-left
tools/bench-run.sh floor-spin-legacy-right
tools/bench-run.sh floor-spin-legacy-left
tools/bench-run.sh floor-spin-fast-right
tools/bench-run.sh floor-spin-fast-left
tools/bench-run.sh floor-spin-fixed-right
tools/bench-run.sh floor-spin-fixed-left
```

| | |
|---|---|
| **Where you stand** | outside the circle it turns in, 1 m clear all round, tether slack |
| **What you do** | nothing |
| **Timeline from Enter** | terminal start and load; the 10 s lead-in; **one turn at most**, and it stops itself. RIGHT is clockwise seen from above, LEFT counter-clockwise |
| **How long the turn takes** | slow about 8 s; medium and legacy about 4 s; fast and fixed about 3 s. Each run about 20–30 s in all |
| **The result line** | `RESULT: SPIN <SPEED> <DIRECTION> -- ended at its turn limit` |
| **legacy and fixed** | these two pairs use a comparison setting of the motor timing (the old v5.0.2 values, and a fixed value) so their current can be compared with the matching standard spin. Nothing else differs for you |

---

## 6. Last: the FlySky run (`floor-rc`)

**Set-up:** the SBUS receiver wired to P58 and bound; the transmitter ON with **swD (the kill switch) up** in its run
position and **swC not down** (swC down ends the run). Platform on the floor, space clear.

```bash
tools/bench-run.sh floor-rc
```

The program starts the motors and checks the wiring (each wheel turns a little one way and back, so the platform twists
a little in place). Then **swA down** lets the sticks drive: right stick up/down is speed, left stick left/right is
direction. There is no switch E. Flip **swC down** to end the run; the program closes the terminal itself.

**This is your drive, at your pace.** A few things worth trying, in any order:

- spins left and right
- forward and back
- slow speed-ups and rapid ones
- the stick straight from full forward to full reverse
- letting the stick centre from full speed
- **swD down** to e-stop at speed, then **swD up** to re-arm
- turning while moving
- crawling, as slowly as the stick allows

**This is your first drive of the new ramps.** Every start and stop should ease in and out; nothing should jolt, lurch,
clunk or rock the platform. Please jot down how each one felt:

| Tried | How it felt |
|---|---|
| spins | |
| forward and back | |
| slow speed-ups | |
| rapid speed-ups | |
| full forward straight to full reverse | |
| stick centred from full speed | |
| e-stop at speed, then re-arm | |
| turning while moving | |
| crawling | |
| anything else | |

The same applies to every floor run above: if any start or stop felt like a step or a jolt, a line here is enough.

---

## 7. Send back

- Every log from the run: the pack's `logs/` folder, or `src/logs/` if you pulled.
- The feel notes above, and anything you noticed that a line in the log would not show.
- If `t0-reva` printed a FINDING for either side, say so.

---

## What this visit cannot measure

- The current of a phase short: the board's current sensor does not see it.
- The 27 A derate: the rig cannot reach it.
- Floor speeds above a quarter of full speed.
- An overload the platform meets on its own: `floor-grab`'s overload is your hold, against a limit lowered to 4 A.
- The hold on an incline: postponed (2026-09-29).

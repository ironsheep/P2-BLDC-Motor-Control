# The floor run — run sheet (the last bench visit before 6.0)

**Task:** «#3576» runs it; «#3591» built it, SRC_REV 58 added the load cells, SRC_REV 60 re-checked every cell against
DRIVER_REV 38's jerk-limited ramp and DRIVER_REV 39's stop plan, and **SRC_REV 62 rebuilt it on Stephen's floor rules and
the five situations he chose (2026-09-27)**; **SRC_REV 63 applies his two rulings on it (2026-09-28)**, below; **SRC_REV 64
records what the run needs to say how the drive works for a platform of this size** ("record all we should to understand
how we are working for this size platform", Stephen, 2026-09-28): see *The platform's size* below. **SRC_REV 65 makes
it a countdown run and postpones INCLINE (Stephen, 2026-09-29)**: see *The countdown run* below.
**Tier:** `dual-spin` (part `DUAL_PART_SPIN`, one binary). **Burn-down:** `DOCs/PUNCH-LIST.md`, "Release burn-down".

**Stephen's rulings (2026-09-28).**

1. **The fault return run uses the guarded test fault**, `testForceFault()`, not POSTFLT's wrong-offset write (which
   plugged the motor at 18–25 A in 3 of 5 uses, PL-119).
2. **Only GRAB ONE SIDE proves the overload hold; the INCLINE proves only the hold on a slope.** The incline's overloaded
   climb and its LDHOLD judgement are removed. The incline now climbs in three steps with a stop after each, then
   drives down.

**Stephen's rulings (2026-09-29).**

3. **INCLINE is postponed**: "postpone the incline testing until we've returned all other results and have corrected
   the driver using them." It is not in this run (SRC_REV 65); section 3 below is kept for when it returns.
4. **No interaction with the PC once the run starts**: "I'll be 4 ft away from the monitor telling me what to do when
   i'm at the platform... so there can't be any interaction by me with the plot window after the test is running... i'll
   need to know before test starts what to look for to know when to interact a timer-countdown with large numbers could
   tell me when to interact." One START click, then the countdown board (below) runs the visit.
5. **A mid-run stop is his own**: "i'll find a way... at the very least i lift the wheels and disconned the battery."
6. **The countdown durations** in the timeline below: "durations seem ok."

**Why this visit exists:** the floor run keeps only the claims that need a load (Stephen, 2026-09-26). It is the last
bench visit before 6.0, so it has to decide every load-dependent release item in one visit:

| Closes | What it proves | Situation |
|---|---|---|
| PL-106 | the protective stop latches on a really blocked wheel, as `SR_BLOCKED`, about a second after the wheel stops | 1 OBSTACLE STOP |
| PL-111 (API half) | a latched protective stop is refused a drive, is not released by `clearEmergency()`, and is released by `clearProtectiveStop()`. The serial half (`protclear`) is not in this release. | 1 OBSTACLE STOP |
| PL-132 | the protective stop coasts under `holdAtStop(FALSE)` (its control: it shorts under `TRUE`) | 1 OBSTACLE STOP |
| PL-150 | under a real one-sided load both wheels slow together and the platform keeps its line; the overloaded wheel holds the speed it can sustain, without faulting | 2 GRAB ONE SIDE (only; ruling 2) |
| PL-144 | the path limiter does not hunt under a load (one engage for one hold) | 2 GRAB ONE SIDE |
| PL-95 | the drive never reports AT_SPEED while its field is held | 1 and 2 |
| PL-93 | after a fault and its recovery, the next drive draws no extra current | 4 FAULT RETURN RUN |
| PL-117 (X-5) | one wheel's fault stops the other along its ramp, on the floor | 4 FAULT RETURN RUN |
| PL-160 (the feel, under load) | the jerk-limited ramp eases every start and stop in and out under a real load: SPINSTRT and SPINPEAK judge the quarter's START, and **you record what you feel** (below) | every drive |

It also carries the floor run's own claims, unchanged since «#3591»: the commutation offsets under load and R18.3's
loaded expectations (5 SPINS), and the hold on an incline, which sizes `HOLD_CEILING_PCT` (3 INCLINE — postponed by
ruling 3, so `HOLD_CEILING_PCT` is not sized by this visit).

**The demos ran at the release-candidate pass (PL-149 certified).** The 27 A derate cannot be reached on this rig.

---

## Block A — wheels up, BEFORE the platform goes on the floor (added after the release-candidate pass)

The release-candidate pass left three wheels-up items. They run first, on the same pull, while the wheels are still up.
`git log --oneline -1 -- src/` must show the commit carrying **test_bench_t0 SRC_REV 28** (harness only; DRIVER_REV 46).

| Order | Command | Why | Minutes |
|---|---|---|---|
| A1 | `tools/bench-run.sh t0-stopreason` | re-certifies RAMP-SHAPE, RAMP-UNWIND, RAMP-REVERSE, SR-ATLIMIT and EV-STOP after the three harness fixes (RC evaluation F1–F3); banner `src_rev 28` | 2 |
| A2 | `tools/bench-run.sh t0-reva` | **pending your decision (PL-163)**, on a Rev A platform | 1 |

Serial is not in this release (Stephen, 2026-09-27), so no serial step runs.

What A1 decides (criteria in source, unchanged except as the SRC_REV 28 note says): R22-T0-RAMP-SHAPE, -REVERSE and
-UNWIND PASS; R20-T0-SR-ATLIMIT reads SR_COMMANDED on its negative (`T0-25,leg,ATLIMIT_NEG,...,sr_stop,41`); R20-T0-EV-STOP
reads `41 42 41 47 41 46 41`. Everything else in the tier as at the RC pass.

Then battery off, the platform on the floor, and the floor run below.

---

## ⛔ First: push, then pull at the bench — or use the prebuilt pack

**The prebuilt pack (2026-09-28).** Instead of pulling and compiling at the rig, you can send it one file,
`dist/bench-<commit>.zip` (built by `tools/make-bench-pack.sh` from a commit). Unzip it on the platform's Pi,
`cd` into its `bench-<commit>/` folder, and type the same commands as below with `./bench-run.sh` in place of
`tools/bench-run.sh`. It holds this visit's binaries (`t0-stopreason`, `t0-reva`, `dual-spin`, `floor-rc`),
already compiled; it prints the commit it was built from and each binary's SHA-256 before it runs, and its logs
land in the folder's `logs/`. Its `README.txt` says which binary each test runs. pnut-term-ts must be on the PATH.

Pulling instead: `git log --oneline -1 -- src/` at the bench must show the commit that carries **test_bench_dual SRC_REV 67** and the
release-candidate driver, **DRIVER_REV 46** (or later, if the release-candidate pass leads to a fix).

## Check the banner before reading anything else

| Every `dual-spin` log must read |
|---|
| `BM-BANNER,...,src_rev,67,fmt,42,part,SPIN` |
| `BM-BUILD ... drv_rev,46`: the driver under test. A lower number means an old tree. |
| `BM-PLAN` rows in this order: `OBSTACLE`, `GRAB`, `FAULTRUN`, `SPIN` (no `INCLINE`: ruling 3) |
| `BM-FLBUILD`, `BM-BLKBUILD`, `BM-LDBUILD`, `BM-CRPBUILD` and `BM-RDBUILD` present: every bound below was pre-registered |
| `BM-FLBUILD ... leg_mm,1000,leg_tk,173,over_tk,6`: the floor rule's 1 m, and the harness's own cap 6 ticks past it |
| `BM-CRPBUILD` is still written (the build records are one block); with INCLINE not run, its cells read NOMEAS |
| ten `BM-SPINLEG` rows; the quarter's (legs 7–10) read `win_ms,300` |

---

## Your floor rules (Stephen, 2026-09-27), and how the harness keeps them

| Your rule | How it is built |
|---|---|
| Only distance-controlled test rigs run on the floor; spinning in place is allowed. | Every drive is armed with the steering object's own distance limit **before it moves** (`stopAfterDistance()` / `stopAfterRotation()`); a refused limit and the drive is never made. Each drive ends at rest at that limit. |
| Straight runs at most 1 m forward and 1 m back to the start. | Every straight leg is armed at 1 m (173 hall ticks) or less. A drive back is armed with the travel the drive out actually made, never more. |
| The incline at most 1 m up and 1 m back down, with stops. | Three climbs of 328 mm (57 ticks, 171 in all), each ending at a stop on the slope, the last at the top, then one drive down by the net climb. |
| The operator must know which test is running before it moves. | Every situation starts on a READY screen that names it, says what it will do and how far. **SRC_REV 65:** the countdown board shows it in large type, and a red STAND CLEAR countdown precedes every drive; only the run's first READY waits for your START (rulings 4–6). Every drive back, and FAULTRUN's two later drives, has a READY of its own. |
| The platform can damage its surroundings, so motion stays inside these limits. | **The harness's own hard cap:** every drive is watched on the drivers' own hall positions and the platform is e-stopped the moment either wheel is **6 ticks (35 mm) past** its drive's declared travel. The distance stop promises rest within 3 ticks of its limit, so 6 past it is a stop that did not happen. STOP (click or space bar) is live whenever a wheel can move; the 10 A abort and the fold-back apply throughout. |

## Before the run: you measure, gather and write down

| What | Value | Why |
|---|---|---|
| Incline angle | **not this visit** (ruling 3) | — |
| Platform mass | **7.71 kg (17.0 lb)** — given 2026-09-28, nothing to do | with the angle, the holding torque per wheel = m·g·sinθ·0.08255 m / 2 |
| *(optional)* FAULTRUN's leg out, measured with a tape: how far the platform really went | ____ mm (the driver says 1,000) | the loaded tyre's rolling size: how true a distance command is on this platform. One reading; skip it if it costs more than it is worth to you |
| The obstacle for OBSTACLE STOP | you / an object (circle one) | the log cannot tell which |
| A straight lane | 1.5 m long, 0.5 m wide, hard floor, clear | GRAB and FAULTRUN drive 1 m out and back; OBSTACLE drives at most 1 m |
| A monitor you can read from the platform | the PC's screen, turned toward the lane and the spin space, about 1.2 m (4 ft) away | the countdown board is how the run talks to you once START is clicked |
| Space for SPIN | level floor, 1 m clear all round | a spin leg is at most one platform turn |
| Tether routing | from above the centre, or ≥ 3 m free | 1 m out and back, and one turn in each direction |

"LEFT" is the platform's left, the P32 board, as seen standing behind it facing forward.

## The visit, declared

| | |
|---|---|
| **Purpose** | **Certification** of the load claims above, on the release-candidate driver (DRIVER_REV 46), plus the floor run's measurements: loaded current by direction and pair. (The hold on the incline is postponed: ruling 3.) |
| **Hardware risk** | **The highest this project has: wheels down, a person present.** Every drive is at most 1 m (a spin leg at most one turn), armed before it moves, e-stopped by the harness 35 mm past its limit. The speeds are a slow walk: 0.16 m/s (OBSTACLE, GRAB), 0.23 m/s (FAULTRUN), and SPIN's at most power 23 (about half a platform turn a second). OBSTACLE pushes on its obstacle — you, if you choose — with at most about 14 N at each tyre (2 A) for about a second before it stops itself. FAULTRUN faults the LEFT wheel on purpose at 0.23 m/s: both wheels ramp down within half a second, the platform turning under 1° (up to about 7° if the faulted wheel coasts instead). **Stand outside the swept circle while it spins. Once START is clicked nobody is at the PC: a stop is yours — lift the wheels, disconnect the battery (ruling 5).** |
| **Who observes / acts** | Stephen, at the platform, reading the countdown board from about 4 ft: it names the situation, gives one action word in its colour (amber: your move; red: it is about to drive; blue: hands off), counts down to the next drive in large digits, and says what he should see. He is the obstacle (OBSTACLE), holds the frame back (GRAB), moves it to the spin space (SPIN), and records the ramp's feel (PL-160). |
| **Runs that carry state** | None. Every OBSTACLE and GRAB trial and the fault run each run in their own steering lifetime; SPIN pairs share one; a written offset pair is restored and read back (`BM-OFFREST`); the lowered current limits are restored before each lifetime stops. |
| **Run length** | About **10 minutes of run**, the countdowns included (the timeline below): OBSTACLE about 2.5 with its two pull-backs, GRAB about 3.5 (up to three tries), FAULTRUN about 1, SPIN about 3. **One click**: START on the briefing. |
| **Repeatability** | Repeatable. To start at a later situation, stay at the PC: SKIP on the briefing ends that situation, the briefing shows again at the next one, and START there begins the run from it. After START, nothing more can be skipped. |
| **Variant matrix** | One binary, `-D BENCH_QUIET -D DUAL_PART_SPIN`, on the Visit 10 rig: Rev B, 6.5in hubs, 18.5 V pack, 270 MHz, DRIVER_REV 46, built-in ramp rates (1,000 / 1,470 mm/s²). DEBUG footprint 8,385 bytes (limit 12,404; SRC_REV 65 adds the countdown board's 21 debug() statements). |

## The command — one

```bash
tools/bench-run.sh dual-spin    # the floor run: OBSTACLE, GRAB, FAULTRUN, SPIN (INCLINE postponed)
```

## The countdown run (SRC_REV 65): what you will see, and when to act

Two windows open. The small **operator panel** (`bmpanel`, top left) is the one you click, once. The large
**countdown board** (`fboard`, 1000 × 620, beside it) is the one you read from the platform. Before you walk away
the board shows the briefing; **click anywhere on the board** (or START on the operator panel; SRC_REV 67), then go to
the platform. **Check before you click:** the operator panel shows its READY screen with START and SKIP, and the board
shows the yellow CLICK HERE TO START band
over the four-line briefing. **Give the board about 15 s to appear**: on the platform's Pi the terminal takes about
11 s to load both windows' bitmaps, and the program waits for it (SRC_REV 66). If either window is still blank after
30 s, the bitmaps did not load: do not click; close the terminal and send the logs. From then on nothing
waits for the PC: each step ends on its countdown, or, for a pull-back, when the wheels' own hall sensors saw the
platform move and then stay still for 3 s.

**Read the colour first.** Amber = your move. Red STAND CLEAR = it drives when the count reaches 0. Blue WATCH = it is
moving; hands off. Grey WAIT = nothing moves. Green DONE / red ENDED EARLY = the run is over and the wheels are off.

| Situation | Board says | Count | What you do | Ends when |
|---|---|---|---|---|
| — | CLICK HERE TO START | — (120 s at the PC) | read the briefing, click the board, walk to the platform | your click |
| OBSTACLE, each of 2 trials | TAKE YOUR PLACE | 20 s | stand 0.3–0.8 m in front of it, square across its path, still | the count |
| | STAND STILL | — | it drives into you and stops itself about 1 s after it is blocked | its stop |
| | WATCH | — | it may push once more, for an instant | the check |
| | PULL IT BACK | up to 60 s | pull it back to where it started, aimed at you, and let go | wheels moved then still 3 s, or 60 s |
| GRAB, up to 3 tries | AIM IT DOWN THE LANE (1st) / HOLD HARDER / HOLD LESS (retries) | 30 s / 15 s | aim it down the 1.5 m lane, stand at its LEFT side, hands off | the count |
| | GET READY | seconds to the grab point | walk beside its LEFT side | the wheels reach the grab point |
| | GRAB NOW | about 4 s; the wheel's speed % below | hold its LEFT side back so the speed falls to about 50, never 0 | the count |
| | LET GO | — | let go, step away; it stops itself at 1 m | its stop |
| | STAND CLEAR, then WATCH | 5 s | stand clear of the lane behind it; it drives back to its start | its stop |
| | *(or)* PULL IT BACK | up to 60 s | when there was no drive back: push it back to its start | wheels moved then still 3 s, or 60 s |
| FAULTRUN | STAND CLEAR | 15 s | leave it aimed down the lane, stand clear | the count |
| | WATCH | — | it drives 1 m forward and stops | its stop |
| | STAND CLEAR, then WATCH | 5 s | it drives back; about 1 s in its LEFT wheel is faulted on purpose and both stop | its stop |
| | STAND CLEAR, then WATCH | 5 s | the drive back goes on to its start | its stop |
| SPIN, 10 legs | MOVE IT TO THE SPIN SPACE (leg 1) | 45 s | move it to level floor, 1 m clear all round; stand outside that circle | the count |
| | STAND CLEAR (legs 2–10) | 5 s | stay outside the circle; the small readout is the leg number | the count |
| | WATCH | — | it spins in place, at most one turn | its stop |
| — | WAIT (writing results), then DONE or ENDED EARLY | — | lift the wheels or disconnect the battery | — |

During a countdown the operator panel draws no buttons (nothing reads them); its STOP stays live on the drive screens
for anyone at the PC.

`dual-ui` is not on this sheet: it previews only `dual-brake`'s screens, which SRC_REV 62 and 63 left byte-for-byte as they
were (the generator rewrote only the SPIN part's own rows), and a tier re-run to certify only the panel earns no slot
(doctrine P10). `ATTENDED-PANEL-SCREENS.md` lists every screen's wording.

---

## The five situations, in order (four run: INCLINE is postponed)

Each drive's travel below is hall ticks at 5.76 mm a tick. Every start and stop number comes from the pass-by-pass model
of the driver's jerk-limited ramp at the built-in rates (the model gives the sheet's own stops to the tenth of a tick):

| Speed | Rate | Start | Stop |
|---|---|---|---|
| SLOW (power 7): OBSTACLE, GRAB, INCLINE, SPIN legs 1–2 | 26.9 ticks/s, 0.16 m/s | 0.39 s, 5.3 ticks | 0.31 s, 4.4 ticks |
| power 10: FAULTRUN | 40.3 ticks/s, 0.23 m/s | 0.48 s, 9.7 ticks | 0.39 s, 8.0 ticks |
| MEDIUM (power 13): SPIN legs 3–6 | 53.7 ticks/s | 0.56 s, 15.0 ticks | 0.46 s, 12.3 ticks |
| the quarter (power 23): SPIN legs 7–10 | 98.2 ticks/s | 0.82 s, 40.1 ticks | 0.64 s, 31.2 ticks |

### 1. OBSTACLE STOP (segment `OBSTACLE`; PL-106, PL-111's API half, PL-132, PL-95)

**What you do and see.**

| When the panel shows | You do | You should see |
|---|---|---|
| OBSTACLE STOP, "TRIAL 1: THE STOP COASTS" | Stand 0.3–0.8 m in front of the platform's front (or put an object there that cannot move), square across its path. Click START. | About 2 s later it drives slowly (0.16 m/s) straight at the obstacle. If you are the obstacle, stand still. |
| DRIVING SLOWLY INTO THE OBSTACLE | Nothing. STOP stops it. | It meets the obstacle and pushes gently (at most about 14 N at each tyre); about **one second** after it stops moving, it stops itself. |
| IT STOPPED ITSELF: CHECKING | Nothing. | It may push the obstacle once more for an instant (the harness checks a drive is taken again after the clear, and stops it at once). |
| PULL IT BACK TO THE START | Pull the platform back to where it started, aimed at the obstacle again. Click DONE. | The wheels roll freely. |
| "TRIAL 2: THE STOP BRAKES" | The same again. | The same, except that after it stops itself the wheels are shorted (harder to pull back). |

**The motion envelope.** Both wheels at SLOW, straight ahead, armed at 1 m (173 ticks) before moving; the harness
e-stops at 179 ticks. Current limited to 2 A on both wheels (restored before the lifetime stops). The obstacle must be
met at speed and before the drive's own stop begins: 0.3 m leaves ten times the 31 mm the start takes, and 0.8 m leaves
the stop's 31 mm and the platform's own reach ahead of its wheels.

**What it decides.**

| Cell | Criterion | Fails if (the negative) | NOMEAS when |
|---|---|---|---|
| **R21-DUAL-BLKSTOP-P** (BOTH, COUNT of bad trials) | both codes `ERR_PLATFORM_BLOCKED`; one wheel `SR_BLOCKED` and the other `SR_BLOCKED` or `SR_PARTNER`; **every SR_BLOCKED wheel stood still, no hall tick, from 988 ms to 1,168 ms before the latch** (criterion token `STILL_TO_LATCH_SR`, was `BLOCKED_STOP_SR`) | no latch after a wheel stood 1,180 ms (a driver without the stop leaves a stalled wheel commanded: Visit 6a's wheel sat at duty_max reporting AT_SPEED); a latch under 988 ms (a false fire, PL-116's class); another stop reason | the drive's own 1 m stop fired first (`why NOT_BLOCKED`: the obstacle was not met) |
| **R21-DUAL-PROTCLR-P** (BOTH, COUNT) | every latched trial: a drive refused with `ERR_PLATFORM_BLOCKED`; `clearEmergency()` leaves it latched; `clearProtectiveStop()` returns NO_ERROR and both codes read NO_ERROR; the rest of the leg armed; the next drive taken | any step otherwise. The in-run negative is the refused drive, the same call the last step makes, before the clear; `clearEmergency()` was the serial host's only release before the fix (`emerclear`) and must not release it | no trial latched |
| **R21-DUAL-BLKSHORT-P** (per motor, MV) | the BRAKE trial's phase sum at rest after the stop **< 80 mV**: a short | at or above: the instrument cannot see a short on that wheel, and its BLKCOAST PASS does not count | the BRAKE trial did not latch |
| **R21-DUAL-BLKCOAST-P** (per motor, MV) | the COAST trial's phase sum at rest **≥ 80 mV**: a coast | under 80: shorted. **Measured negative:** before DRIVER_REV 20 the stop shorted under coast; a short reads 11–25 mV and a coast 160–174 mV (`debug_260923-192848.log`) | the COAST trial did not latch |

**How the latch window is derived (re-derived for an obstacle, never fitted).** The driver's own test (`bFrontProtect()`)
latches when a commanded wheel's |err| is at least LAG_SOFT and its hall position has not changed for BLOCKED_PASSES
(1,000) front passes at 1 kHz. So the latch cannot come sooner than **1,000 ms after the wheel's last tick**. It comes no
later than the field's own travel to LAG_SOFT after that tick, plus the same 1,000 ms: the lag limiter holds |err| under
LAG_HOLD, so the field travels at most LAG_HOLD + LAG_SOFT = 180 of its 256 units a cycle, 4.2 ticks, at the commanded
26.9 ticks/s: **156 ms**. Each end carries 12 ms for when the harness sees each event (a watch pass and one instrument
period). Band: 1,000 − 12 = **988** to 1,000 + 156 + 12 = **1,168 ms**; a wheel still 1,180 ms with no latch is the stop
overdue. A wheel the obstacle met before both wheels read AT_SPEED had a slower field, so its trial is judged on
everything but the upper bound. (SRC_REV 58's chocked-wheel trial timed 1–4 s from the command, which included the
ramp; an obstacle is met at speed, so the time is taken from the wheel's own stop.)

**Recorded, not judged:** `BM-BLOCK` (the latch time from the command, each wheel's stand still, both stop reasons),
`BM-BLKCLR` (both codes, every API return, each wheel's phase sum and the bridge it reads, HELDATSPD's counts), a trace
per trial, `BM-SR`.

### 2. GRAB ONE SIDE (segment `GRAB`; PL-150, PL-144, PL-95)

**What you do and see.**

| When the panel shows | You do | You should see |
|---|---|---|
| GRAB ONE SIDE, "NEXT: GRAB WHEN TOLD" | Aim the platform down the lane (1.5 m clear), tether slack. Click START. Walk beside its **LEFT** side, hands off. | It drives straight at a slow walk (0.16 m/s). |
| GRAB (the number is its LEFT wheel's speed, % of command) | At about 0.4 m the panel says GRAB: take hold of the frame's LEFT side and hold it back, firmly and steadily, walking, **so the number falls to about 50 — never to 0**. Hold until LET GO. | Both wheels slow together; the platform keeps its line (it may yaw slightly toward you). |
| LET GO | Let go and step away. | It picks up speed again and stops by itself at 1 m. |
| NEXT: DRIVE BACK TO START | Stand clear of the lane behind it. Click START (or SKIP, and push it back yourself). | It drives straight back 1 m and stops by itself at its start. |
| "LAST TOO LIGHT: HOLD HARDER" / "LAST STALLED: HOLD LESS" | Adjust your hold and click START. Up to three tries; the first judged one ends GRAB. | |

A hold that stops the platform for a second latches the protective stop (`STALLED`): correct behaviour, not judged, and
the next try asks for less. **Hold once and steadily:** a hold let go and taken again is two engages and fails LDHUNT.

**The motion envelope.** Both wheels at SLOW, current limited to 4 A (about 28 N at the left tyre). Out: armed at 1 m
(173 ticks), guard at 179. Back: armed at the farther wheel's travel out, guard 6 past it.

**The length and speed fit the judged window inside the half metre after the grab** (derived; the old LOAD, at power 13
over 2 m, spent about 1.2 m on its window, and at power 13 the window alone would now cover 134 of the 173 ticks). At
SLOW the platform is at speed by 5.3 ticks. GRAB comes at 69 ticks (0.4 m), so you take hold within the 1 s lead, at
0.4–0.55 m. The lead at up to full speed is 27 ticks, and the 2.5 s window at up to 88 % (the held wheel under 80 %, the
other within LDPATH's 10 % of it) is 59.4: 155.4 in all, against the stop's start at 173 − 4.4 − 1 = 167.6 — **12 ticks
spare**. A try you hardly slow (100 % throughout) still ends its window at 163.5, before the stop begins.

**What it decides. This is the only run that proves the overload hold (ruling 2).** A try is judged only if your grip
really held the LEFT wheel below its command. In the window that wheel must read SHORT (its lag limiter held) and run
under **80 %** of its command's rate, with no protective stop. A try where a wheel faulted is also judged (LDHOLD's
negative). Any other try is not judged, and LDPATH, LDHUNT and LDHOLD read NOMEAS for it:
- too light (`NOT_OVERLOADED`): the next READY screen says "LAST TOO LIGHT: HOLD HARDER";
- stalled (`STALLED`): it says "LAST STALLED: HOLD LESS".

There are up to three tries, and the first judged one ends GRAB. If none is judged, all three cells read NOMEAS and the
overload hold is not certified at this visit.

| Cell | Criterion | Fails if (the negative) | NOMEAS when |
|---|---|---|---|
| **R21-DUAL-LDPATH-P** (PL-150, BOTH, PERMILLE) | in the judged window, \|left − right\| hall ticks ÷ the larger **≤ 100 ‰**: both slowed together, the line kept | above. **By construction:** without the limiter the free wheel keeps its whole command while the held one runs under 80 %: at least 200 ‰, which still reads over 133 ‰ at the least travel judged | no judged try, or the larger travel under **30 ticks** (re-derived from 20: two ticks of window-edge quantisation and one of the follower's delay must stay inside 100 ‰) |
| **R21-DUAL-LDHUNT-P** (PL-144, BOTH, COUNT) — new | the path limiter's EV_PATH_LIMIT engages in the judged try's lifetime **exactly 1**: one engage for one hold, released after it | more: a hunting limiter. **Measured negative:** pass 6's pre-fix limiter cycled five times in 4 s (one every 720–790 ms), about four in this hold | no judged try |
| **R21-DUAL-LDHOLD-P** (PL-150, the gripped wheel, LEFT only, MS) | in the judged window, the LEFT wheel's longest gap between hall ticks **≤ 1,000 ms**, and no fault. The bound is the protective stop's own 1 s: a wheel held still that long latches, which is `STALLED` and not judged | a fault (a driver with no lag limiter faults FC_LAG at \|err\| 125), or a longer gap with no protective stop (a hold whose field decayed to zero and stood still) | the grip never held the LEFT wheel SHORT and under 80 % of its command in any try (it is not printed for the RIGHT, which is never gripped) |
| **R21-DUAL-HELDATSPD-P** (PL-95, BOTH, COUNT) | over every OBSTACLE drive and every GRAB window, both wheels: **no two samples in a row read AT_SPEED at \|err\| ≥ LAG_HOLD** | any such pair. **Measured negative:** PL-93's trace read AT_SPEED at e −101 and duty_max for eight samples running | no sample was ever held |

**Recorded, not judged:** `BM-LOAD`/`BM-LOADW` for every try (each wheel's travel and % of command, the mismatch, the
least path scale, the SHORT polls, each wheel's longest tick gap, the engages), `BM-FLLEG` for the drive back, a trace.

### 3. INCLINE (segment `INCLINE`; the hold on a slope: its creep and `HOLD_CEILING_PCT`)

> **⏸ POSTPONED — not run at SRC_REV 65 (ruling 3).** "postpone the incline testing until we've returned all other
> results and have corrected the driver using them." The section is kept as written for when it returns; its screens
> still use clicks and will need the countdown treatment then.

**What it proves, and what it does not (ruling 2).** The incline proves only the hold on a slope. It does not prove the
overload hold; GRAB ONE SIDE alone does. SRC_REV 62's overloaded climb is removed: its fourth step at a lowered 2 A
limit, judged for LDHOLD only if the platform's mass happened to overload a wheel on its start. So the platform's mass
no longer decides anything here. It is still recorded, because it sets the torque the hold must supply.

**What you do and see.** ONE START runs the whole sequence, so the platform never waits on a screen while on the slope.

| When the panel shows | You do | You should see |
|---|---|---|
| INCLINE, "NEXT: CLIMB, 3 STOPS, DOWN" | Put the platform on the flat at the foot of the slope, facing up it, its drive wheels just short of the slope. Click START. Stand beside it, a hand near. | It climbs about a third of a metre (328 mm). |
| STOPPED ON THE SLOPE, "EXPECT: ROLLS DOWNHILL" (stop 1) | Hands off, hand near. | It rolls back about 2 cm (3 ticks) and the harness brakes it; then it climbs another 328 mm. |
| "EXPECT: SLIPS, THEN DRAGS" (stop 2) | Hands off. | Its hold slips and hands over to the short, which drags as it creeps down; the harness brakes it by 35 mm; then it climbs the last 328 mm to the top. |
| "EXPECT: DOES NOT MOVE" (stop 3, at the top) | Hands off, for 15 s. | It holds still. |
| DRIVING 1 M BACK DOWN TO THE START | Nothing. | It drives back down and stops by itself at its start, on the flat. |
| TAKE HOLD OF THE PLATFORM (only if the sequence ended early on the slope) | Hold it still, click DONE; the wheels are then switched off: lift it off the slope. | |

STOP on the incline **brakes the wheels at once** (it shorts them), as its screens say.

**The motion envelope (re-derived for three steps).**
- **The climbs.** Three climbs of 57 ticks (328 mm) at SLOW (0.16 m/s), each armed with its own limit before it moves
  and guarded 6 ticks past. That is 171 ticks, 0.98 m, at most, inside the rule's metre.
- **Each climb's time.** 5.3 ticks to get up to speed, 4.4 + 1 to stop, and 46.3 at 26.9 ticks/s: about 2.4 s against
  its 12 s bound.
- **Where it rests.** The coast control is braked after 3 ticks (17 mm) of roll, plus the little it rolls while braking.
  A hold stop that creeps 6 ticks (35 mm) is braked. So the stops rest at about 53, 104–108 and 161–165 ticks up.
- **The drive down.** It is armed at the net climb: the mean of both wheels' displacement from the start, on the
  drivers' own hall positions. That is at most 171 ticks, about 6.7 s.
- **The slope.** It must run at least 1 m past the drive wheels plus the platform's own length, as before.

**What it decides.**

| Cell | Criterion | Fails if | Control / NOMEAS |
|---|---|---|---|
| **R19-DUAL-CRPCOAST-P** (control) | stop 1, floated: rolls **≥ 3 ticks** | it does not: the incline does not load the wheels past friction and cogging, and CREEP / CRPHOLD go NOMEAS | — |
| **R19-DUAL-CRPLOW-P** (control) | stop 2, the hold at a 1 % ceiling (under duty_min): creeps **≥ 2 ticks** | it does not: the slope never asks more than duty_min, so the ceiling is not sized; repeat steeper | — |
| **R19-DUAL-CREEP-P** (per motor) | stop 3, the hold at the provisional 10 % ceiling: **0 ticks** of creep while HOLDING, counted from where both wheels came to rest (where the driver arms its hold) | any creep | CRPCOAST; NOMEAS unless the coast control rolled |
| **R19-DUAL-CRPHOLD-P** (per motor) | still HOLDING when the 15 s watch ends | LIMITED or SLIPPED | as CREEP |

No load cell is judged on the incline.

**Wheel slip is invisible to the halls.** A tyre that slides on a loose surface moves the platform with no hall tick,
and one that spins in place ticks with no motion: to the harness either reads as rest, or as creep or travel. Use a
surface the tyres grip.

**Recorded, not judged:** `BM-CREEP`/`BM-CREEPW` per stop (how the hold resolved, the hold duty against its ceiling,
the time at the ceiling, current at hold: this sizes `HOLD_CEILING_PCT` under load), `BM-FLLEG` per climb and the drive
down, each with its steady second's current per wheel and the pack voltage after it (SRC_REV 64). No trace and no
`BM-LOAD` come from the incline any more.

### 4. FAULT RETURN RUN (segment `FAULTRUN`; PL-93, X-5 / PL-117)

**What you do and see.**

| When the panel shows | You do | You should see |
|---|---|---|
| FAULT RETURN RUN, "NEXT: 1 M FORWARD, NO FAULT" | Aim the platform down the lane (1.5 m long, 0.5 m wide), tether slack. Stand clear. Click START. | It drives 1 m forward at 0.23 m/s and stops by itself. |
| "NEXT: BACK, LEFT FAULTED" | Stand clear. Click START. | It drives back; about a second later the LEFT wheel is faulted on purpose and **both wheels stop within half a second**, the platform turning a few degrees at most. |
| FAULT CLEARED. "NEXT: THE RETURN GOES ON" (after about 5 s) | Stand clear. Click START (or SKIP, and push it back yourself). | The same drive back goes on at the same speed and stops by itself at its start. |

**The motion envelope and why power 10 (derived).** Out: armed at 1 m, guarded at 179 ticks. Back: armed at 1 m before
it moves; the guard's zero and its 179 cover the re-drive too, and the re-drive is armed with what is left of the 1 m.
Both steady seconds must fit inside the 1 m back with room for the fault: 9.7 ticks up + 40.3 of the steady "before" =
50.0 at the fault, 8.0 for both ramps down (58.0), then the re-drive's 9.7 up + 40.3 of "after" + 8.0 down + the stop
plan's early tick = 59.0 — **117 of 173 ticks, 56 spare**. Power 13 would leave 10, too few if the faulted wheel coasts
(a free wheel at 0.31 m/s rolls about 40 ticks); power 10 leaves over twice the ~24 ticks such a coast takes at 0.23 m/s.
A re-drive needs at least **64 ticks** left (re-derived from 80: the 59.0 needed, plus a tick for the model, a tick of
quantisation and the stop's 3-tick tolerance).

**The fault is the driver's own forced fault (ruling 1, Stephen, 2026-09-28: the guarded test fault stands)**
(`testForceFault()`: taken at the driver's own fault test on its next
driven frame, FC_LAG, the path a real lag fault takes), guarded by the harness. **The fault response is the shipped
default, FR_GRADED:** the faulted wheel re-seeds from its halls and ramps down; the steering object ramps the other down
at the same rate (`SR_PARTNER`).

**The arc the platform turns during the partner's ramp-down.** Two equal ramps from one speed differ by the pass the
fault is seen on and a hall step: about a tick, **6 mm of tyre over the 387 mm track, under 1°**. If the graded stop falls
back to a coast (its halls lost, or a second fault), the arc is at most the partner's whole stop, 8.0 ticks (46 mm):
**6.8°**, pivoting about the faulted wheel; the ~0.66 m still to go then ends about 8 cm to one side.

**What it decides.**

| Cell | Criterion | Fails if | NOMEAS when |
|---|---|---|---|
| **R21-DUAL-POSTFLT-P** (PL-93, per motor, X100) | the re-drive's getCurrent() over its first second at speed ÷ the leg back's own over its second before the fault **≤ 1.50** | above; an absolute-current abort scores 99.99. **Measured negative:** Visit 6a drew 3.8–4.2× and hit the 10 A abort on the drive-up (PL-93) | the fault did not latch, the recovery did not clear, under 64 ticks left, he skipped it, or the "before" is under **0.02 A** (re-derived from 0.05: before and after share a lifetime and a rest zero, each good to 3.3 mA, so a true 1.0 cannot read over 1.5 above 16.7 mA) |
| **R19-DUAL-SPINPLAT-P** (X-5, the RIGHT wheel, PCT) | 2 s after the LEFT wheel's fault, the RIGHT runs at **≤ 10 %** of its rate before it (FLTPLAT's own criterion) | it keeps driving (a steering object with no platform fault policy: PL-117) | the fault did not latch, or the RIGHT was not turning before it |
| R14-DUAL-RSTPROV-P (per motor) | the fault's recovery cleared it | as every part | as every part |

**The second reference.** The leg out's own second at speed is printed beside the two (`BM-RDRIVE l_fwd, r_fwd`), not
judged: it runs the other way on the same floor, and a direction may differ by 25 % (SPINSYM's band), so it cannot be held
to 1.5 without its own derivation. It shows whether the "before" was itself ordinary.

**Recorded, not judged:** `BM-FLLEG` for the leg out, the fault's trace and `BM-FRPLAT`, `BM-SR` (the faulted wheel's own
reason, the other `SR_PARTNER`), `BM-RDRIVE`.

### 5. SPINS (segment `SPIN`; the commutation offsets under load, R18.3's loaded expectations)

**What you do and see.** On each READY screen: stand outside the circle, tether slack, click START. It spins in place
as the screen says and stops by itself within one turn. Odd legs spin right (clockwise from above), even legs left.

| Legs | Pair | Speed (power) | Pair each driver must apply | Steady window |
|---|---|---|---|---|
| 1–2 | the shipped lead schedule | SLOW (7) | 17 / 336 | 2,000 ms |
| 3–4 | schedule | MEDIUM (13) | 15 / 337 | 1,000 ms |
| 5–6 | **legacy 43/317, the control** | MEDIUM | 43 / 317 | 1,000 ms |
| 7–8 | schedule, traced | BRISK (23), the quarter | 1 / 351 | 300 ms |
| 9–10 | fixed 14/338 | BRISK | 14 / 338 | 300 ms |

SRC_REV 62 removed the old legs 11–12 (one wheel faulted, then a re-drive): FAULTRUN judges X-5 and PL-93 on a straight
run instead, so no spin leg faults a wheel.

**The motion envelope.** One revolution of the platform: π × 387 mm = 1,216 mm, 211 hall ticks. Each leg's limit is armed
before it moves, and the harness e-stops 6 ticks past it. Each clockwise leg is followed by a counter-clockwise one, so
the tether winds at most one turn.

| Cell | Criterion | Fails if | Control |
|---|---|---|---|
| **R19-DUAL-SPINSTOP-P** | every leg ends within **±3 ticks** of the limit | an overshoot, an undershoot, or the guard fires | — |
| **R19-DUAL-SPINOFF-P** | every driver applied the table's pair | a write that did not land | — |
| **R19-DUAL-SPINDIR-P** | no wheel ran against its commanded direction | any did | — |
| **R19-DUAL-SPINHUNT-P** (A-3) | slow and medium schedule legs: no window with duty_pk − duty > 400 or err_pk > 76 | any such window | the shipped servo read 800–1,650 / 75–89 wheels up |
| **R19-DUAL-SPINERR-P** (A-4) | \|mean err\| within 47–49 in every schedule window | outside | — |
| **R19-DUAL-SPINSTRT-P** (A-1, PL-160) | worst duty drop over the START's rise ≤ 100 ‰ | above: the shipped servo's hunting read 340–530 | — |
| **R19-DUAL-SPINPEAK-P** (A-2, PL-160) | worst START current peak ÷ 60 ms of steady running, 420 ms after the first AT_SPEED, ≤ 1.80 | above: the shipped servo's start spike read 1.94–3.04 | NOMEAS when the reference was not all AT_SPEED |
| **R19-DUAL-SPINFOL-P** (A-8) | the two following readings within 5 points | they differ more | — |
| **R19-DUAL-SPINSYM-P** | medium, schedule: larger direction's current ÷ smaller ≤ 1.25 | above | **SPINCTL** |
| **R19-DUAL-SPINCTL-P** (control) | legacy current ÷ schedule current ≥ 1.25 | below: the load masks the offsets' effect | — |
| **R19-DUAL-SPINLEAD-P** | schedule ÷ fixed at the quarter ≤ 1.05 | above | — |
| NOSTALL, DBGMASK, TRACES, RSTPROV, LAGBND (-P) | as every part | as every part | — |

**Recorded, not judged:** `BM-SPINW` gives loaded current per wheel and direction; `BM-SPINSTART` each quarter START's
peak and its steady reference.

---

## The platform's size: what the run records, and what the analysis computes from it (SRC_REV 64)

Stephen, 2026-09-28: *"record all we should to understand how we are working for this size platform"*. The Rev B platform
is **7.71 kg (17.0 lb)**; its track is 387 mm and its wheel radius 82.55 mm. Nothing here adds a cell, a screen or a
motion: every figure is computed at analysis from records the run already makes, and SRC_REV 64 adds the steady current
per wheel and the pack voltage to every plain floor leg (`BM-FLLEG` gains `n`, `l_amps`, `r_amps`, `pack_mv`; `NA` when
the leg's steady second was cut short).

| What it tells a user about a platform this size | From | Expectation written before the run |
|---|---|---|
| **The force a slope asks, and what it costs in current.** m·g·sinθ, split between the wheels | the three climbs' `BM-FLLEG` against the flat drives back at the same power (GRAB's), per wheel | at 10°: **13.1 N** in all, 6.6 N and 0.54 N·m per wheel. At 0.155 m/s that is **2.0 W** of climbing work, so by energy alone a climb draws at least **2.0 W ÷ the pack voltage, about 0.05 A per wheel** more than the flat leg. Less than that means the current channel under-reads under load, or the slope is shallower than measured |
| **How much of the pack's power reaches the slope.** climbing work ÷ the extra electrical power | the same, with `pack_mv` | none written: it is a first measurement, and it is judged against the energy bound above |
| **The hold's force per unit of effort.** m·g·sinθ against the hold's duty and current at rest | stop 3's `BM-CREEPW` | the hold's 10 % ceiling holds at 10° (CREEP, CRPHOLD); its duty tells how much of the ceiling that slope used, and so what slope the ceiling leaves room for |
| **Rolling on the floor.** the flat drives' steady current against the same speed wheels up | GRAB's drives back, FAULTRUN's leg out (`BM-RDRIVE l_fwd, r_fwd`) | none written: wheels up, the same power draws only the motors' own losses |
| **Stops with the platform's mass behind them.** where each leg came to rest against its limit | every `BM-FLLEG` `l_trav`, `r_trav` against `ticks` | within 3 ticks of the limit, as wheels up: the built-in 1,470 mm/s² asks 11.3 N of the pair to stop this platform |
| **How true a distance is on the floor** | the optional tape reading above | within the hall resolution, 5.76 mm, if the loaded tyre rolls at its nominal 6.5 in |

**Not measured, named:** the force during a start or a stop (at the built-in rates it is 7.7–11.3 N for under half a
second, too brief and too small against the current channel's noise to separate from the steady draw); the platform's
centre of gravity, so nothing here says how hard a stop tips it; the platform's rotational inertia, so the spins say
nothing about mass.

---

## ⭐ PL-160: feel the new ramp, and write it down

PL-160's feel is a floor item: no cell can judge it. **During every drive, watch and listen at every start and every stop
— and at GRAB's slow-down when you hold and speed-up when you let go — and after the run write one line on the sheet:**
"PL-160 feel: ____".

- **What to expect.** Every start eases in and every stop eases out, over the times in the table above. Nothing should
  jolt, lurch, clunk or rock the platform.
- **What counts against it.** A step you can feel at either end of a ramp is PL-160's negative. So is the platform
  pitching at a stop, or a stop that stops dead (other than the incline's braked stops and OBSTACLE's stop against the
  obstacle, which are meant to).

---

## floor-rc — the FlySky RC run (placeholder)

FlySky testing is in this release (Stephen, 2026-09-27). This block is a **placeholder for the `floor-rc` tier**, which
another agent is building; its commands, envelope and what it decides are written there. It runs on the floor, after the
floor run.

---

## Known confounds

- OBSTACLE: an obstacle that yields (you step back) lets the wheels tick again, and the stand restarts; the stop then
  comes a second after the last tick, which the cell measures correctly.
- GRAB: a hold that stops the platform for a second latches the protective stop (`STALLED`): correct behaviour, not the
  overload claim, so that try is not judged and the next asks for less. A hold let go and taken again reads 2 on LDHUNT.
- INCLINE: wheel slip on a loose surface is indistinguishable from motion to the halls (above).

## What this visit cannot measure, named

- A phase short's current (PL-118).
- The 27 A derate: the rig cannot reach it.
- Speeds above power 23 on the floor.
- An overload the platform meets on its own, unassisted. GRAB's overload is your hold, against a limit lowered to 4 A.
  That is how the claim is built, stated here.
- The overload hold on a slope (ruling 2: the incline proves only the hold at rest on a slope). At a current limit the
  torque is fixed, and a constant slope asks the same torque at any speed. So a climb either keeps its command or
  cannot hold the slope at all. Whether its start overloads a wheel depends on the platform's mass.
- The feel of the ramp beyond what you report: no cell measures jerk under load (t0-stopreason's R22 cells measure it
  wheels up, pass by pass).
- The serial `protclear` path (PL-111's own certification): not in this release.

## After the visit

One analysis per set of logs, under `DOCs/procedures/BENCH-RUN-PROCESSING.md`, with your "PL-160 feel" line, the incline
angle and the platform mass quoted, and a section on the platform's size that computes each row of the table above. Its
results go into the 6.5″ motor manual (§6.5 and §9's "behaviour under load"), with their sources in
`DOCs/analyses/MOTOR-6.5IN-MANUAL-SOURCES.md`. Then close every punch-list item its cells certify (PL-93, PL-95, PL-106, PL-132,
PL-144, PL-150, PL-111's API half, and PL-160's feel), and re-count the burn-down. PL-150's overload hold closes on
GRAB's LDHOLD alone. If GRAB judged no try, LDHOLD is NOMEAS and PL-150 stays open.

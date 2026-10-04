# Doco visit D1a — the motor recheck (your only instructions)

**Plan:** `DOCs/plans/DOCO-AND-CLOCK-SPRINT-PLAN.md` §10, step 1 (task «#3692»). **Driver:** DRIVER_REV 52. **Harness:**
`test_bench_single` SRC_REV 8. **Pack:** `dist/bench-bc03e6d.zip` (commit `bc03e6d`).

**What this session is for:** the first thing we did on the 6.5″ — prove the motor is what its documentation says before
anything else rests on it. By hand, with the motor unpowered: the hall ticks per revolution (the pole count), which way
the halls count against the turn, and the order the hall codes come in. Then, under power: the start checks and the
wiring check. The encoder, bolted to the shaft, counts the exact turns.

Everything you need is on this page. Nothing is marked for the log: the log records everything.

---

## The bench

The Doco bench: the DocoEng motor on the Rev A board (P16 group), the encoder on the shaft (A on P48, B on P49), the
bench supply **on, at 12.0 V** (the hall sensors are powered from the board; the motor is not driven during the turn).
Nothing on the shaft but the encoder.

**Get the test:** copy the pack to the bench machine, unzip it, `cd` into its folder.

## ⭐ The session: one command

| # | Supply | Command | What happens | You |
|---|---|---|---|---|
| 1 | **12.0 V** | `./bench-run.sh single-recheck-v12p0` | About 3 minutes. A panel opens. **The hand turn:** click START STEP, then turn the shaft **clockwise, looking at the encoder end**, about three full turns, at an easy steady pace; the motor is unpowered, so the shaft turns freely with the light, even bumps of its magnets; click DONE. The result stays on the screen: click NEXT (or REDO to turn again). **Then hands off:** the motor starts and turns a little each way (the wiring check), and the panel says ALL STEPS DONE; click FINISH | Turn the shaft when the panel says YOUR TURN; keep your hands off after the hand turn |

**What to watch for, named in advance:** if the panel's RESULT screen says *under two turns* or *too fast*, click REDO and
turn again, more turns or slower. If the wiring check makes the shaft jerk hard or buzz, turn the supply off and send
the log.

**A stop is yours: turn the supply off.** Send back the log in `logs/`.

---

## Check the first lines of the log

| Test | The banner lines must read |
|---|---|
| `single-recheck-v12p0` | `B1-BANNER,src_rev,8,commit,bc03e6d,fmt,7,driver_rev,52,...,told_mv,12000,...`, and `B1-BOARD` reading Rev A |

## The session, declared

| | |
|---|---|
| **Purpose** | **Recheck of the motor against its documentation** (`DOCOENG_MOTOR.md`, `MOTOR_CHOICE.md`): hall ticks per revolution against 24 (4 pole pairs), the hall count's sign against the encoder's (and which way your clockwise turn makes them count), the hall code order against 1-5-4-6-2-3 / 1-3-2-6-4-5; the start checks and `checkWiring()`; the distance methods refused with no wheel (`ERR_NO_WHEEL_DIA`, nothing moves) |
| **Hardware risk** | The hand turn is unpowered. The wiring check turns the shaft a little each way under the driver's normal start; the harness's 2 A test limit and its stops apply |
| **Who acts** | You: turn the shaft by hand on the panel's word; click the panel's buttons |
| **Runs that carry state** | None |
| **Run length** | About 3 minutes, about 10 with set-up |
| **Repeatability** | Repeatable; REDO repeats the hand turn within the run |
| **Variant matrix** | Rev A board (P16), DocoEng motor, 12.0 V told, 270 MHz, DRIVER_REV 52 |

## What this session does not measure

- Anything under load or at speed: the offsets, the speed ladder and the qualification are the next sessions, after the
  motor documentation is corrected to what this one shows.
- The wire colours in `DOCOENG_MOTOR.md` (your cabling): the wiring check proves the motor runs as connected, not the
  colour names.

## Revision history

- **2026-10-04** — written («#3692»).

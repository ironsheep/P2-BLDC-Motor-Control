#!/bin/bash
#
# bench-run.sh -- Bench tier runner for P2-BLDC-Motor-Control
#
# Stephen runs the underlying tools (pnut-ts, pnut-term-ts) by hand and wants
# to be able to keep doing that: "when you hide them behind scripts i have no
# idea what's going to run. then i can't help you figure out why." This
# script exists ONLY because a tier run is a fixed sequence of two separate
# tool invocations, and it does exactly those two steps and nothing else:
#
#   1. COMPILE  -- pnut-ts, with -D BENCH_CFG, src/ as the working directory.
#                  BENCH_CFG selects isp_bldc_motor_userconfig_bench.spin2 --
#                  the fixed, plainly-stated peer config describing the real
#                  bench (dual 6.5" wheels, two Rev B boards, 18.5V pack) --
#                  in place of isp_bldc_motor_userconfig.spin2, the file end
#                  users edit and whose active block this script no longer
#                  reads or cares about.
#   2. RUN      -- pnut-term-ts, batch mode, also with src/ as the working
#                  directory (so its logs land in src/logs/ as a natural
#                  consequence, not because this script moves them there).
# It does NOT write, move or rename the logs. pnut-term-ts names them by
# timestamp and puts them in src/logs/; that is already right and this script
# leaves it alone. Since PL-74 it does READ the log the run just wrote, once,
# to refuse a load that emitted nothing -- see the check after step 2.
#
# Every external command this script runs is echoed verbatim, immediately
# before it runs, prefixed "+ " -- so the transcript is something you can
# replay by hand line for line.
#
# --exit-on-end-session makes pnut-term-ts close itself once the tier's binary
# prints its DEBUG_END_SESSION marker, so this produces one binary and one
# log with no keypress and no interrupt needed. Beside it the script passes -u,
# ahead of -r, so every run also leaves a USB-traffic capture (see step 2's
# comment) -- those two are the only terminal flags (PL-92). Every tier's binary emits that marker:
# test_bench_t0, test_bench_spin, test_bench_detect, test_bench_char,
# test_bench_scan and test_bench_dual, and the release demos demo_single_motor
# and demo_dual_motor when built with -D BENCH_CFG (PL-149).
#
# Usage:  tools/bench-run.sh <tier> [<clock>]
#   <tier>      -- tier name, see usage() below.
#   <clock>     -- optional, a clock NAME (clk-floor, clk-200, clk-270, clk-300, clk-350, clk-frac), for the tiers of
#                  test_bench_dual, test_bench_t0, the Doco harness test_bench_single (task 3675) and the motor-adoption
#                  tool util_adopt_motor (task 3685) only. In a prebuilt
#                  package (tools/make-bench-pack.sh <tier>@<clock>) the name picks the binary built at that clock.
#                  The Doco bench (-D BENCH_DOCO, doco-* tiers): one motor, one Rev A board, a TOLD voltage chosen by NAME in
#                  the tier (doco_voltage() below); it is built as its own fixed statement, never the 6.5in one. Nothing numeric is ever typed at the bench (STEPHEN
#                  2026-09-16: "please don't create commands where the data entry due to length causes risk to me
#                  typeing it correctly (e.g., Hz values that's silly)"): a name is the only way to choose a clock,
#                  and the one table that maps a name to its Hz is clock_hz() below. Task 3674 chose a second argument
#                  over a tier variant per clock (dual-clock-NNN, t0-NNN, ...) because six clocks times every tier of
#                  two tops is a table that grows with every clock and tier; a name list grows with the clocks only.
#
# The three original clock tiers, dual-clock-200 / -270 / -300, still work: each is `dual-clock` with its clock named
# (and `dual-clock <clock>` takes any name). A clock name is the ONLY thing that may cause this script to write to a
# source file (the top's "CLK_FREQ = ..." line); every other run is read-only with respect to the tree. Restored on
# exit, including on interrupt.

set -u

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# A PREBUILT PACKAGE (tools/make-bench-pack.sh, STEPHEN 2026-09-28: "i need pre-compiled binaries for our test runs
# zipped up so i can send one file to the test revB platform unpack it and then run them"). The package holds this
# script, a BENCH-PACKAGE file naming the commit it was built from, and <tier>.bin, each compiled by this script
# with exactly the flags below. Run from inside the unpacked package, this script compiles nothing: it runs the tier's
# packaged binary with the same pnut-term-ts line, the same precondition banner and the same PL-74 checks, with the
# package folder as the working directory (so the logs land in its logs/). pnut-ts is not needed there.
# Every binary sits in the package folder itself, beside the bitmaps its panels load, never in a subfolder: at the
# source tree the binary, the bitmaps and the working directory are all src/, and the package keeps all three in one
# place too. (2026-09-29 14:16: with the binaries in bins/ and the bitmaps one folder up, in the working directory,
# no layer loaded -- so the terminal does not find a LAYER file from its working directory alone.)
PACKAGE_FILE="${SCRIPT_DIR}/BENCH-PACKAGE"
PREBUILT=""
[ -f "$PACKAGE_FILE" ] && PREBUILT=1
if [ -n "$PREBUILT" ]; then
    SRC_DIR="$SCRIPT_DIR"
else
    SRC_DIR="$(cd "${SCRIPT_DIR}/../src" && pwd)"
fi
# Resolved, not "${SCRIPT_DIR}/.." -- otherwise every path this script prints
# carries a "tools/.." in the middle and is annoying to copy-paste.
PROJECT_ROOT="$(cd "${SCRIPT_DIR}/.." && pwd)"
# Both tools are on PATH -- invoke them by name, exactly as they are run by
# hand. The echoed command line is then the same one you would type, which is
# the point. PNUT_TS / PNUT_TERM_TS override for testing without a board.
PNUT="${PNUT_TS:-pnut-ts}"
PNUT_TERM="${PNUT_TERM_TS:-pnut-term-ts}"

# BENCH_MEASURE_ONLY=1 -- set by tools/build-check.sh, never typed at the bench. The tier
# is compiled and its DEBUG footprint gated exactly as for a run, then the script exits
# before any terminal, precondition banner or source patch. It lets the commit-time gate
# measure every tier through this one tier table instead of a copy of it.
MEASURE_ONLY="${BENCH_MEASURE_ONLY:-}"

# BENCH_PACK_DIR=<dir> -- set by tools/make-bench-pack.sh, never typed at the bench. The tier is compiled exactly as
# for a run (the one -l -d compile below), its binary is copied to <dir>/<tier>.bin, and the script exits before
# any terminal or banner.
PACK_DIR="${BENCH_PACK_DIR:-}"

# THE CLOCK TABLE (task 3674): every clock a run can name, in ONE place. A name maps to Hz here and nowhere else, so a
# later task that rules a clock changes ONE line. Since task 3674 test_bench_dual's CLOCK part and test_bench_t0 judge
# any clock (the expected frame is computed from the running clock), so the names are chosen to cover the range:
#   clk-floor  the lowest supported clock. PROVISIONAL 120 MHz: task 3683 rules the real floor and sets it HERE, this line only.
#   clk-200    200 MHz, as the original dual-clock-200
#   clk-270    270 MHz, the files' own default, as dual-clock-270
#   clk-300    300 MHz, as dual-clock-300
#   clk-350    350 MHz, the fastest the P2 PLL makes (VCO / 1): getct() differences wrap at 6.1 s
#   clk-frac   271.25 MHz, a clock that is NOT a whole number of MHz (every whole-MHz arithmetic goes wrong on it).
#              An integer in Hz, and the P2's PLL makes it EXACTLY from the 20 MHz crystal: 20 MHz x 217 / 16 (pnut-ts
#              writes CLKMODE $013CD8FB: divide 16, multiply 217, VCO / 1) -- verified by compiling it, not on a board.
# pnut-ts needs no _errfreq for any of them: each is reached exactly, so the default tolerance is never used.
CLOCK_NAMES="clk-floor clk-200 clk-270 clk-300 clk-350 clk-frac"
clock_hz() {
    case "$1" in
        clk-floor) echo "120000000" ;;
        clk-200)   echo "200000000" ;;
        clk-270)   echo "270000000" ;;
        clk-300)   echo "300000000" ;;
        clk-350)   echo "350000000" ;;
        clk-frac)  echo "271250000" ;;
        *)         return 1 ;;
    esac
}
# THE DOCO VOLTAGE TABLE (task 3675, STEPHEN 2026-10-03): the Doco bench (one DocoEng motor on one Rev A board, no voltage
# sensing) is TOLD its drive voltage, so the voltage is a build parameter of every Doco tier, chosen by NAME exactly as a clock
# is. A name maps to the -D symbol that src/isp_bldc_motor_userconfig_bench.spin2 turns into DRIVE_VOLTAGE (and the voltage in
# mV, which every log banner prints) HERE and nowhere else; the names follow the PWR_* enum (v12p0 = PWR_12p0V). A Doco tier is
# named <base>-<voltage name> (doco-demo-v12p0), and it compiles with -D BENCH_DOCO -D <the symbol>.
DOCO_VOLTAGE_NAMES="v7p4 v11p1 v12p0 v14p8 v18p5 v22p2 v24p0"
# The one table: echoes "<symbol> <millivolts>" for a voltage name.
doco_voltage() {
    case "$1" in
        v7p4)  echo "DOCO_V7P4 7400" ;;
        v11p1) echo "DOCO_V11P1 11100" ;;
        v12p0) echo "DOCO_V12P0 12000" ;;
        v14p8) echo "DOCO_V14P8 14800" ;;
        v18p5) echo "DOCO_V18P5 18500" ;;
        v22p2) echo "DOCO_V22P2 22200" ;;
        v24p0) echo "DOCO_V24P0 24000" ;;
        *)     return 1 ;;
    esac
}
# The clock a shorthand tier names, if it is one: dual-clock-200 / -270 / -300 are `dual-clock` with that clock.
tier_clock() {
    case "$1" in
        dual-clock-200) echo "clk-200" ;;
        dual-clock-270) echo "clk-270" ;;
        dual-clock-300) echo "clk-300" ;;
    esac
}

# echo a command verbatim, then run it. "$@" is the real argv -- nothing
# paraphrased, nothing elided.
run() {
    echo "+ $*"
    "$@"
}

# Refuse, and say why where it will be seen. The message goes to BOTH stdout and
# stderr because the operator's console capture holds stdout only: at Visit 2 a
# ten-digit clock reached the compiler, the run stopped with no error line in the
# capture and no log, and all three dual-clock loads were lost (PL-62). At Visit 3
# the same loads were lost again to a clock typed as 200 -- which is why no clock
# is typed any more.
die() {
    echo "ERROR: $*"
    echo "ERROR: $*" >&2
    exit 2
}

# Where pnut-term-ts puts its logs, relative to SRC_DIR (this script never writes there).
LOG_DIR="logs"

# The newest run log, or nothing when none exists yet. Used only to tell the log this run
# wrote from the one before it -- see the PL-74 check after the run.
newest_log() {
    ls -1t "${LOG_DIR}"/debug_*.log 2>/dev/null | head -1
}

# ---- usage and argument validation ----------------------------------------------
usage() {
    # stdout, not stderr (PL-62): the operator's console capture holds stdout, so a
    #  refusal that only reaches stderr leaves them with a run that stopped for no
    #  visible reason.
    cat <<'EOF'
Usage:  tools/bench-run.sh <tier> [<clock>]
  <clock>     -- optional, for the tiers of test_bench_dual, test_bench_t0, test_bench_single and util_adopt_motor only: the clock the run is built at, by NAME
                 (nothing numeric is typed). One of:
                   clk-floor  120 MHz  the lowest supported clock (PROVISIONAL: task 3683 rules it)
                   clk-200    200 MHz
                   clk-270    270 MHz  (what a run without a clock uses)
                   clk-300    300 MHz
                   clk-350    350 MHz  the fastest clock the P2 makes
                   clk-frac   271.25 MHz  not a whole number of MHz
  <tier>      -- one of:
                   t0             Tier 0 -- no motor, no motion, no risk
                   panel          PLOT pipeline probe: two windows differing ONLY in name, no motors, reads out in the log  [NOTHING MOVES, ATTENDED]
                   t0-hand        Tier 0's T0-12 hand-rotation anchor only -- OPERATOR TURNS ONE WHEEL, waits on a keypress, no sign-off cell
                   t0-stopmode    Tier 0's T0-24 stop-state hand test only -- 8 ROWS: OPERATOR PUSHES OR SPINS ONE WHEEL SIX TIMES, TWO ROWS SPIN IT UNDER POWER  [WHEELS UP, ATTENDED]
                   t0-stopmode-fltfirst  as t0-stopmode with the two powered fault rows before the e-stop row (PL-116's discriminator)  [WHEELS UP, ATTENDED]
                   t0-stopreason  Tier 0's T0-25 only -- the RIGHT wheel driven slowly and stopped each way a program can, to read why it stopped and the driver's event log; then driven up to power 50, slowed, stopped and reversed while the ramp is watched pass by pass (PL-160) and every PWM frame's slack is watched (PL-161)  [MOTORS CONNECTED, WHEELS UP, UNATTENDED]
                   t0-reva        Tier 0's T0-27 only, ON THE REV A PLATFORM: at a 2 A limit each wheel is driven slowly twice and must fold back no frame, then each speeds up hard once and must fold back (PL-163, the Rev A current fold-back)  [REV A PLATFORM, WHEELS UP, HANDS OFF]
                   spin           wiring check -- BOTH WHEELS TURN at 50%, fwd then reverse
                   spin-auto      as spin, the board revision auto-detected (PL-120's first factor)  [WHEELS UP, UNATTENDED]
                   spin-quiet     as spin, built quiet like the dual and T0 tests (PL-120's second factor)  [WHEELS UP, UNATTENDED]
                   detect         board-detection sweep, PASSIVE (no driver code in the image)
                   detect-lib     as above + the library cross-check (still no driver cog)
                   detect-phase2  adds the driver-cog poisoning probe  [MOTORS MAY STAY CONNECTED, GATE-OVERLAP GROUPS SKIPPED]
                   char           automated motor characterisation, nine holds  [MOTORS CONNECTED, UNATTENDED]
                   scan           automated per-direction commutation-offset scan  [MOTORS CONNECTED, UNATTENDED]
                   scan-wdtest    watchdog self-test: preflight, deliberate stall, watchdog ends the run  [MOTORS CONNECTED]
                   scan-droop     droop-stop self-test: pure logic, three point sequences through the real stop decision  [NOTHING MOVES]
                   dual-a         motion harness part A: PREFLT, STOPMODE, LIVE, LADDER, LOWSPD  [MOTORS CONNECTED, WHEELS UP, UNATTENDED]
                   dual-a-legacy  as dual-a, on the LEGACY commutation offsets 43/317 -- the control leg, draws far more current  [MOTORS CONNECTED, WHEELS UP, UNATTENDED]
                   dual-clock     motion harness clock load at the clock you name: PREFLT, CLOCK -- takes the <clock> argument, e.g. dual-clock clk-350  [WHEELS UP, UNATTENDED]
                   dual-clock-200 motion harness clock load at 200 MHz: PREFLT, CLOCK  [WHEELS UP, UNATTENDED]
                   dual-clock-270 motion harness clock load at 270 MHz: PREFLT, CLOCK  [WHEELS UP, UNATTENDED]
                   dual-clock-300 motion harness clock load at 300 MHz: PREFLT, CLOCK  [WHEELS UP, UNATTENDED]
                   dual-b         motion harness part B: PREFLT, FAULTB, OVERSHT  [MOTORS CONNECTED, WHEELS UP, UNATTENDED]
                   dual-fault     motion harness part FAULTRESP: PREFLT, FLTRESP, FLTPLAT -- the fault study's X-cells, faults forced at speed  [MOTORS CONNECTED, WHEELS UP, UNATTENDED]
                   dual-fault-rightfirst  as dual-fault with the RIGHT wheel's own trials run before the LEFT's (PL-120's order test)  [MOTORS CONNECTED, WHEELS UP, UNATTENDED]
                   dual-start     motion harness part START: SKCHECK -- 10 starts through the steering object reading every start check; every one calls checkWiring() (the platform turns a few degrees in place) and prints the driver's own record of each leg  [MOTORS CONNECTED, WHEELS UP, UNATTENDED]
                   dual-start-nowalk  as dual-start without checkWiring(), each start told to go ahead despite a failed check: nothing is commanded -- the load for B-1 (one wheel's hall connector unplugged)  [WHEELS UP, ATTENDED WIRING CHANGE]
                   dual-start-phaseneg  12 starts with one LEFT phase withheld from the lead check in firmware (B-3's negative), in three kinds: started anyway, refused, withheld on the first try only; nothing is commanded  [WHEELS UP, UNATTENDED]
                   dual-start-swapneg   as dual-start, with the LEFT wheel reading two halls as swapped in the walk lifetimes (B-5's negative): the left wheel may jerk  [MOTORS CONNECTED, WHEELS UP, UNATTENDED]
                   floor-obstacle-coast  the FLOOR RUN, ONE ACTION, NO WINDOW: a slow drive of at most 1 m into an obstacle you place 0.3-0.8 m ahead, the platform's own protective stop (bridge coasts), and the checks after it; you pull it back by hand afterwards  [WHEELS DOWN, ATTENDED]
                   floor-obstacle-short  as floor-obstacle-coast with the stop shorting the bridge (the control)  [WHEELS DOWN, ATTENDED]
                   floor-grab     the FLOOR RUN, ONE ACTION, NO WINDOW: a slow 1 m straight drive; about 3 s after it starts rolling you take hold of its LEFT side and hold until it stops by itself; you return it by hand afterwards  [WHEELS DOWN, ATTENDED: ONE HAND HOLD]
                   floor-faultrun the FLOOR RUN, ONE ACTION, NO WINDOW: 1 m out, 1 m back with the LEFT wheel faulted on purpose, the recovery, and the drive on to the start  [WHEELS DOWN, ATTENDED]
                   floor-spin-slow-left  the FLOOR RUN, ONE ACTION, NO WINDOW: one slow spin in place, at most one platform turn, counter-clockwise seen from above  [WHEELS DOWN, ATTENDED]
                   floor-spin-slow-right as floor-spin-slow-left, clockwise  [WHEELS DOWN, ATTENDED]
                   floor-spin-med-left   one medium-speed spin in place, at most one platform turn, counter-clockwise  [WHEELS DOWN, ATTENDED]
                   floor-spin-med-right  as floor-spin-med-left, clockwise  [WHEELS DOWN, ATTENDED]
                   floor-spin-fast-left  one fast (quarter-speed) spin in place, at most two platform turns, counter-clockwise  [WHEELS DOWN, ATTENDED]
                   floor-spin-fast-right as floor-spin-fast-left, clockwise  [WHEELS DOWN, ATTENDED]
                   floor-spin-legacy-left  a medium spin, counter-clockwise, on a comparison setting of the motor timing (the old 5.0.2 values), for comparing its current with floor-spin-med  [WHEELS DOWN, ATTENDED]
                   floor-spin-legacy-right as floor-spin-legacy-left, clockwise  [WHEELS DOWN, ATTENDED]
                   floor-spin-fixed-left   a fast spin, counter-clockwise, on a comparison setting of the motor timing (a fixed value), for comparing its current with floor-spin-fast  [WHEELS DOWN, ATTENDED]
                   floor-spin-fixed-right  as floor-spin-fixed-left, clockwise  [WHEELS DOWN, ATTENDED]
                   floor-auto     SESSION 2 -- THE HANDS-OFF FLOOR RUN, inside a 2 m x 2 m square, from your fixed start point and back to it: the ten spins in place, the fault run (1 m out, 1 m back with a wheel faulted on purpose, the drive on to the start), and four straight 1 m ramp legs at three acceleration and three deceleration settings; about 3 minutes, you do nothing  [WHEELS DOWN, ATTENDED: STAND BY]
                   floor-obstacle SESSION 3 -- the obstacle at 0.3-0.8 m ahead, twice: the coast trial and a drive back to the start, then the brake trial and a drive back; about 1 minute, you do nothing after placing the object  [WHEELS DOWN, ATTENDED: STAND BY]
                   dual-pack     motion harness part PACK: the pack voltage sensor -- NOTHING MOVES: 60 s hands off, then you unplug and replug the sensor at the pack twice; a meter reading only when the terminal asks  [ATTENDED]
                   dual-brake     motion harness part BRAKE: OUTSIDE -- OPERATOR HAND-BRAKES THE LEFT WHEEL ONCE  [WHEELS UP, ATTENDED]
                   dual-c         motion harness part C: PREFLT, BASELINE, POSTFLT  [MOTORS CONNECTED, WHEELS UP, UNATTENDED]
                   dual-d         motion harness part D: PREFLT, STEERSEG, LIMIT -- the front cog's contract and current limiting  [MOTORS CONNECTED, WHEELS UP, UNATTENDED]
                   dual-floor     motion harness part FLOOR -- WHEELS DOWN, OPERATOR OBSERVES ABOUT 2 S OF DRIVING  [ATTENDED]
                   dual-ui        motion harness part UICHECK -- NO MOTOR CONTROL: walks the operator through every panel control and attended screen  [ATTENDED]
                   dual-align     motion harness part ALIGN -- NO MOTOR IS DRIVEN: the operator turns each wheel BY HAND, 8 legs, to measure the hall zero cold  [ATTENDED]
                   dual-lead      motion harness part LEAD: PREFLT, LEAD -- the live lead-step run that measures the dynamic-lead table  [MOTORS CONNECTED, WHEELS UP, UNATTENDED]
                   dual-limits    motion harness part LIMITS: PREFLT, LIMTOP, LIMRAMP, LIMLOW -- the limits reset's top speed, ramps and low-speed floor  [MOTORS CONNECTED, WHEELS UP, UNATTENDED]
                   dual-limits-top  as dual-limits' LIMTOP only: the climb and the power check that confirm moved limits  [MOTORS CONNECTED, WHEELS UP, UNATTENDED]
                   dual-reg       motion harness part REG: PREFLT, REGRESS -- two turns by distance, then one fault forced per wheel and the same power sent again (PL-151, PL-66), under a minute  [MOTORS CONNECTED, WHEELS UP, UNATTENDED]
                   dual-kick      motion harness part KICK: PREFLT, KICK -- the seven top-of-range speed changes per wheel and direction, for the kick fix (PL-78, PL-87), under 2 minutes  [MOTORS CONNECTED, WHEELS UP, UNATTENDED]
                   dual-tokneg    the record labels' self-check's own negative: no part runs, nothing moves, seconds; two token tables are built wrong on purpose (one a token short, one with a token too long) and the R21-DUAL-TOKTAB cell must print FAIL  [NOTHING MOVES, UNATTENDED]
                   demo-single    the single-motor release demo on the RIGHT wheel: wiring check, 15 s forward and 15 s reverse at full power (PL-149), about 1 minute  [MOTORS CONNECTED, WHEELS UP, UNATTENDED]
                   demo-rc        the FlySky RC demo, driven by you with the transmitter (in this release, Stephen 2026-09-27); SBUS receiver on P58  [ATTENDED]
                   floor-rc       the RC demo's control loop ON THE FLOOR, driven by you with the transmitter, with a 25 Hz telemetry line of both wheels (RC-TEL) and every drive event (RC-EVT); SBUS receiver on P58; runs until you close the terminal  [WHEELS DOWN, ATTENDED]
                   doco-demo-<voltage>  the DOCO BENCH (one motor, P16 board, a Rev A): the single-motor release demo, told its drive voltage by the tier's NAME -- one of doco-demo-v7p4, -v11p1, -v12p0, -v14p8, -v18p5, -v22p2, -v24p0 (7.4 11.1 12 14.8 18.5 22.2 24 V; nothing is sensed on this bench)  [MOTOR CONNECTED, FREE TO TURN, UNATTENDED]
                   single-hallmap-<voltage>  the DOCO BENCH's measurement harness, its hall-map leg: the encoder angle at every hall edge, eight two-revolution crawls (60 and 240 rpm, each way) under a 2 A test limit; the voltage told by NAME as doco-demo's is (-v7p4 ... -v24p0); takes a <clock> name  [MOTOR CONNECTED, ENCODER COUPLED, SHAFT FREE, UNATTENDED]
                   single-mininc-<voltage>   the Doco harness's slowest-steady-speed leg: crawls each way, slower each step, until one does not turn smoothly on the encoder (PL-71); voltage and clock as above  [MOTOR CONNECTED, ENCODER COUPLED, SHAFT FREE, UNATTENDED]
                   single-ladder-<voltage>   the Doco harness's speed ladder: a quarter to all of the voltage's top speed (and, from 12 V up, to 400e6), each from rest and by a step, each held ~6 s, each way; the duty line, the reserve ceiling, the misdial check; voltage and clock as above  [MOTOR CONNECTED, ENCODER COUPLED, SHAFT FREE, UNATTENDED]
                   single-ramp-<voltage>     the Doco harness's built-in speed-up to the top and stop, each way, and a reversal through zero at the top; voltage and clock as above  [MOTOR CONNECTED, ENCODER COUPLED, SHAFT FREE, UNATTENDED]
                   single-stops-<voltage>    the Doco harness's stop limits: stopAfterRotation() and stopAfterTime() at the top and at a crawl, each way; voltage and clock as above  [MOTOR CONNECTED, ENCODER COUPLED, SHAFT FREE, UNATTENDED]
                   single-coast-<voltage>    the Doco harness's coast-down: at a quarter, half and all of the top speed, each way, the drive cut on purpose and the free coast to rest read on the encoder; at v12p0 and v24p0 only (single-coast-v12p0, -v24p0); clock as above  [MOTOR CONNECTED, ENCODER COUPLED, SHAFT FREE, UNATTENDED]
                   single-offscan-<voltage>  the Doco harness's timing (commutation offset) scan: the offset stepped 5 degrees over +-30 at a quarter, half and all of the top speed, each way; the current minimum, the lead check, the hall zero at speed (~11 minutes); at v12p0 and v24p0 only; clock as above  [MOTOR CONNECTED, ENCODER COUPLED, SHAFT FREE, UNATTENDED]
                   single-passprobe-<voltage>  the Doco harness's drive-pass probe: half speed for 10 s each way, the encoder's speed against the drive's pass rate to +-0.1 %; voltage as above, and run at each clock NAME (single-passprobe-v12p0 clk-floor, ... clk-frac)  [MOTOR CONNECTED, ENCODER COUPLED, SHAFT FREE, UNATTENDED]
                   single-measure-<voltage>  EVERY hands-off leg of the Doco harness in one run, in order: hall map, slowest speed, ladder, ramp, stop limits, coast-down and timing scan (at 12 V and 24 V only), drive-pass probe (~25 minutes at v12p0 / v24p0, ~13 elsewhere); voltage and clock as above  [MOTOR CONNECTED, ENCODER COUPLED, SHAFT FREE, UNATTENDED]
                   single-qualify-<voltage>  the Doco harness's D2 QUALIFICATION in one run, judged against the encoder: the wiring check, the power steps each way, the speed ladder, the built-in speed-up, stop and reversal, and the stop limits; every Doco voltage (-v7p4 ... -v24p0), clock as above (~12 minutes)  [MOTOR CONNECTED, ENCODER COUPLED, SHAFT FREE, UNATTENDED]
                   single-handload-<voltage> the Doco harness's hand load, on a panel: the shaft turns slowly by itself and you slow it by hand to a stop, at a 4 A and a 2 A test limit and (12 V only) briefly at the default limits; at v12p0 and v24p0 only (single-handload-v12p0, -v24p0)  [MOTOR CONNECTED, ENCODER COUPLED, ATTENDED: YOUR HAND ON THE SHAFT]
                   single-heldpush-<voltage> the Doco harness's held stop, on a panel: the stopped motor holds the shaft and you turn it slowly by hand until the hold gives way, one way, then the other; at v12p0 and v24p0 only  [MOTOR CONNECTED, ENCODER COUPLED, ATTENDED: YOUR HAND ON THE SHAFT]
                   single-sag-<voltage>      OPTIONAL, ask first: the Doco harness's supply sag, on a panel: at the top speed you turn the bench supply down about 1 V a second until the speed is lost; at v22p2 and v18p5 only  [MOTOR CONNECTED, ENCODER COUPLED, ATTENDED: YOUR HAND ON THE SUPPLY]
                   single-pinch-<voltage>    OPTIONAL, ask first: the Doco harness's cloth pinch, on a panel: at the top speed you pinch the bare shaft end lightly with a cloth for 1 to 2 seconds; at v18p5 only (single-pinch-v18p5)  [MOTOR CONNECTED, ENCODER COUPLED, ATTENDED: A CLOTH ON THE SHAFT END]
                   doco-adopt-<voltage>  the motor-adoption tool (util_adopt_motor.spin2) on the DOCO BENCH's one motor, as a user runs it: the timing (offset) scan at two speeds each way, then the speed ceiling each way, from the motor's record; the voltage told by NAME as doco-demo's is (-v7p4 ... -v24p0); takes a <clock> name; 15-30 minutes  [MOTOR CONNECTED, SHAFT FREE, UNATTENDED]
                   adopt-wheel    the motor-adoption tool on the 6.5in platform's RIGHT wheel (the P16 board, 18.5 V), as a user runs it; takes a <clock> name; 15-30 minutes  [MOTORS CONNECTED, WHEELS UP, UNATTENDED]
                   demo-dual      the two-wheel release demo: wiring check, 1 ft forward, two 15 s steered drives, then each wheel alone 15 s at full power (PL-149), about 1.5 minutes  [MOTORS CONNECTED, WHEELS UP, UNATTENDED]

Examples:
  tools/bench-run.sh detect
  tools/bench-run.sh char
  tools/bench-run.sh dual-clock-200
  tools/bench-run.sh dual-clock clk-350
  tools/bench-run.sh t0 clk-frac
  tools/bench-run.sh single-passprobe-v12p0 clk-floor
EOF
    exit "${1:-2}"          # usage 0 for --help; a refusal is 2
}

if [ $# -lt 1 ] || [ $# -gt 2 ]; then
    if [ $# -gt 2 ]; then
        echo "ERROR: at most two arguments, the tier name and optionally a clock NAME (never a number)"
    fi
    usage
fi

TIER="$1"
CLOCK_NAME="${2:-}"
CLK_OVERRIDE=""
CLOCK_FROM_ARG="$CLOCK_NAME"          # a clock the operator typed, as against one a shorthand tier names
# --help / -h print the usage and clock names; usage() starts no terminal and touches no file
case "$TIER" in
    -h|--help|help) usage 0 ;;
esac

# a shorthand tier (dual-clock-200 ...) names its clock; a second argument beside it must say the same
SHORTHAND_CLOCK="$(tier_clock "$TIER")"
if [ -n "$SHORTHAND_CLOCK" ]; then
    if [ -n "$CLOCK_NAME" ] && [ "$CLOCK_NAME" != "$SHORTHAND_CLOCK" ]; then
        die "tier '$TIER' already names its clock ($SHORTHAND_CLOCK); give no second argument (or use: dual-clock $CLOCK_NAME)"
    fi
    CLOCK_NAME="$SHORTHAND_CLOCK"
    CLOCK_FROM_ARG=""
fi
# the name is looked up in the ONE table (clock_hz); anything else is refused and the names are listed
if [ -n "$CLOCK_NAME" ]; then
    CLK_OVERRIDE="$(clock_hz "$CLOCK_NAME")" || die "unknown clock '$CLOCK_NAME' -- a clock is chosen by NAME, one of: $CLOCK_NAMES"
fi

# Validate tier name, and map it to a top file plus its -D options.
#
# WHY THE OPTIONS LIVE HERE. pnut-ts SILENTLY IGNORES AN UNKNOWN -D -- exit 0,
# binary written, no warning -- so a mistyped option does not fail, it produces
# a plausible WRONG run against the wrong config or the wrong build variant.
# Typing "-D BENCH_CFG -D DETECT_LIB" by hand at a bench, repeatedly, is exactly
# where that typo comes from. Naming each combination once, here, removes the
# whole failure class. Every command is still echoed verbatim before it runs, so
# nothing is hidden -- you can always see, and replay, precisely what ran.
#
# EXTRA_DEFS is an array so the echoed line is the real argv, not a re-quoted
# approximation of it.
EXTRA_DEFS=()
PRECONDITION=""
# The words every floor-* tier's PRECONDITION shares (the fourteen single-action floor commands, SRC_REV 69): what a floor
# run is, what a spin does, and how it ends. Plain words for Stephen on the floor with the Rev B platform; no window, no key.
FLOOR_FRAME="PLATFORM ON THE FLOOR, WHEELS DOWN, THE REV B PLATFORM -- ATTENDED, BUT NO WINDOW OPENS AND NOTHING IS CLICKED OR TYPED: you start the command and read the terminal. THIS IS ONE ACTION, RUN ONCE -- a repeat is this same command again. The terminal prints its records, then 'LEAD-IN: the platform starts moving in 10 s' (printed once; it does not count down): you have those 10 seconds to be standing where this says, and NOTHING MOVES BEFORE THEY ARE UP. YOUR FLOOR RULES ARE BUILT IN: every drive is armed with its own distance limit before it moves; the program stops any drive 6 hall ticks (35 mm) past that limit; a straight drive goes at most 1 m and a spin at most one platform turn (two at the fast, quarter-speed setting); the 10 A abort applies. BEFORE THE RUN: a clear straight lane 1.5 m long and 0.5 m wide on a hard floor, a clear level space 1 m all round for a spin."
FLOOR_SPIN_WHAT="WHAT IT DOES: spins the platform in place, ONE turn at most (TWO at the fast, quarter-speed setting), and stops itself at its turn limit. WHERE YOU STAND: outside the circle it turns in, at least 1 m clear all round. WHAT YOU DO: nothing. WHAT YOU SEE: the lead-in line and 10 still seconds, then the platform turning once (twice at the fast setting) and stopping."
FLOOR_TAIL="WHEN IT ENDS: the terminal's LAST line starts 'RESULT:' and says what happened. Read it, put the platform back at its start BY HAND (its wheels roll freely once it ends) and run the next command. THERE IS NO STOP BUTTON: to stop it mid-run, lift the wheels and disconnect the battery."
# The words the two floor SESSIONS share (floor-auto and floor-obstacle, SRC_REV 70, Plan A sec 10: R15 a command may chain every check that
# needs no hand between them, R17 a hands-off run stays inside a 2 m x 2 m square). Plain words; no window, no key, nothing to do but stand by.
FLOOR_SESSION_FRAME="PLATFORM ON THE FLOOR, WHEELS DOWN, THE REV B PLATFORM -- ATTENDED, BUT YOU ONLY STAND BY: no window opens and nothing is clicked or typed. THIS IS A SESSION: one command runs several checks one after another and needs you for none of them. THE SQUARE: mark a 2 m by 2 m square on a hard, level floor and put the platform on your FIXED START POINT -- its wheel axle 0.5 m in from one edge of the square, in the middle of that edge, FACING ACROSS THE SQUARE. The session starts there and ENDS THERE: it drives straight 1 m at most each way, always out and back, and the program keeps the platform inside the square by itself -- it tracks where the platform is from its wheels, and before every straight drive it refuses the drive, and prints a line starting 'FENCE:', if the drive could end outside the square. Spins are in place. Any drive the program cannot complete stops the straight drives after it ('SKIPPED:' lines say so); the spins always run. The terminal prints its records, then 'LEAD-IN: the platform starts moving in 10 s' (printed once; it does not count down): you have those 10 seconds to be standing where this says, and NOTHING MOVES BEFORE THEY ARE UP. YOUR FLOOR RULES ARE BUILT IN: every drive is armed with its own distance limit before it moves; the program stops any drive 6 hall ticks (35 mm) past that limit; the 10 A abort applies. THE SPINS: floor-auto's spins alternate direction, each pair leaving the platform facing where it began."
FLOOR_SESSION_TAIL="WHEN IT ENDS: the terminal's LAST line starts 'RESULT:' and says in one line what each part concluded and, in plain numbers, where the platform ended (x, y in mm and heading in degrees from the start point, estimated from the wheels). Read it, put the platform back on its start point BY HAND if it is not there (its wheels roll freely once it ends) and run the next command. THERE IS NO STOP BUTTON: to stop it mid-run, lift the wheels and disconnect the battery."
case "$TIER" in
    # PL-74: t0 is built QUIET. It carries SIX isp_bldc_motor instances plus a steering
    #  object (motor, motorA, motorB, motorP, steer's two) -- more than any other tier --
    #  and it was the only tier compiled with the library's nine debug channels live in
    #  every one of them. MEASURED: -D BENCH_QUIET removes 2_866 bytes of library debug
    #  data from this build. t0 judges RETURN CODES, not library chatter, and its own ten
    #  cells print through plain debug() in test_bench_t0.spin2, which no channel mask
    #  touches -- so nothing it measures is lost. See PL-74 for what is and is not
    #  established about why the tier emitted nothing.
    # panel -- the PLOT pipeline probe (2026-09-21). The control that was never built: two PLOT
    #  windows identical but for their NAME, one layer each, no motor object and no pin driven.
    #  It answers, FROM THE LOG, whether a window draws at all, whether host input arrives, what
    #  coordinate basis PLOT reports by default, and whether the window name is what kills a
    #  display. Run it before spending a bench slot on any attended tier.
    panel)          BENCH_FILE="test_bench_panel.spin2"
                    PRECONDITION="NO MOTORS NEEDED, nothing moves -- move the mouse over each window"
                    ;;
    t0)             BENCH_FILE="test_bench_t0.spin2"
                    EXTRA_DEFS=(-D BENCH_QUIET)
                    ;;
    t0-hand)        BENCH_FILE="test_bench_t0.spin2"
                    EXTRA_DEFS=(-D BENCH_QUIET -D T0_HAND)
                    PRECONDITION="OPERATOR TURNS ONE WHEEL BY HAND, EXACTLY N REVOLUTIONS -- T0-12 waits on a keypress, never a timer"
                    ;;
    # T0-24 (task 3578): the one build of test_bench_t0.spin2 that drives a motor. Two of its six
    #  rows provoke a fault at power 50 to reach the post-fault bridge state; the other four are
    #  built at rest. It is BENCH_QUIET for the same reason t0 is -- it judges what the wheel does
    #  under a hand, not library chatter.
    t0-stopmode)    BENCH_FILE="test_bench_t0.spin2"
                    EXTRA_DEFS=(-D BENCH_QUIET -D T0_STOPMODE)
                    PRECONDITION="MOTORS CONNECTED, WHEELS UP -- ATTENDED stop-state hand test on the RIGHT wheel, 8 rows: click the t0stop window first; nothing happens until you click START ROW. Each row's panel says what to do and what you should feel BEFORE it runs. Every hand row WAITS FOR YOU after START ROW: nothing is timed until you touch the wheel. Rows 1-3 (the hold): push the wheel off where it stopped and hold it. Rows 4, 5 and 8: spin the wheel briskly and let go -- the row ends itself once the wheel is at rest. ROWS 6 AND 7 SPIN THE WHEEL UNDER POWER AND FAULT IT ON PURPOSE: hands off, ABORT stops a powered row. THREE PANEL TESTS, each asked on its own screen: row 1 first asks you to click a grey box, row 4 asks for one REDO ROW, row 6 asks you to click ABORT as it spins up and then REDO ROW. Buttons only: START ROW, DONE, ABORT, NEXT ROW, REDO ROW (Enter = the right button, Esc = the left)"
                    ;;
    # t0-stopmode-fltfirst (task 3607, PL-116's discriminator) -- the same tier with the two powered fault rows
    #  run BEFORE the e-stop row. After Visit 6a both powered rows latched ERR_PLATFORM_BLOCKED on a lifted wheel
    #  straight after the e-stop row's clearEmergency(): reaching AT_SPEED here and faulting as designed points at
    #  the e-stop clear path; a second block points at the blocked test itself (PL-106). -D T0_24_FLT_FIRST only
    #  reorders the rows; the binary is otherwise the same.
    t0-stopmode-fltfirst)
                    BENCH_FILE="test_bench_t0.spin2"
                    EXTRA_DEFS=(-D BENCH_QUIET -D T0_STOPMODE -D T0_24_FLT_FIRST)
                    PRECONDITION="MOTORS CONNECTED, WHEELS UP -- ATTENDED stop-state hand test on the RIGHT wheel, 8 rows, the TWO POWERED FAULT ROWS NOW COME BEFORE THE E-STOP ROW (rows 5 and 6): click the t0stop window first; nothing happens until you click START ROW. Rows 1-3: push the wheel off where it stopped and hold it. Rows 4, 7 and 8: spin briskly and let go. ROWS 5 AND 6 SPIN THE WHEEL UNDER POWER AND FAULT IT ON PURPOSE: hands off, ABORT stops a powered row"
                    ;;
    # t0-stopreason (task 3621, R20.1; DOCs/plans/DRIVER-REPORTING-DESIGN.md SS6) -- T0-25 only, the stop-reason and
    #  event-log cells. Plain t0 promises no motion and every one of these cells has to drive the wheel, so it is its own
    #  build of the t0 binary, as t0-stopmode is; unlike it, nothing waits on a person. BENCH_QUIET for the same reason.
    t0-api)         BENCH_FILE="test_bench_t0.spin2"
                    EXTRA_DEFS=(-D BENCH_QUIET -D T0_API)
                    PRECONDITION="MOTORS CONNECTED, WHEELS UP, HANDS OFF -- UNATTENDED, YOU DO NOTHING, NOTHING MOVES: the program calls every API setting with good and bad values and reads each back. It starts the right motor (the P16 board) five times and the platform once, and never drives a wheel. No window opens. About 20 seconds"
                    ;;
    # t0-stopreason (test_bench_t0 SRC_REV 25, DRIVER_REV 38/39, PL-160): after T0-25's stop-reason legs, the same build drives
    #  the wheel at powers 50 and 25 for the jerk-limited ramp's cells -- a speed-up, a slow-down, a stop, a reversal, a
    #  stop read mid speed-up, and five stops by distance, rotation and time limits (two at cruise, three mid-ramp) --
    #  while a sampler cog watches every drive pass. About 30 s more than the legs alone. SRC_REV 26 (PL-161): a frame
    #  watcher cog reads every PWM frame's slack over the same drives (R22-T0-FRAMESLACK); it adds no motion and no time.
    t0-stopreason)  BENCH_FILE="test_bench_t0.spin2"
                    EXTRA_DEFS=(-D BENCH_QUIET -D T0_STOPREASON)
                    PRECONDITION="MOTORS CONNECTED, WHEELS UP, HANDS OFF -- UNATTENDED, YOU DO NOTHING: the program drives the RIGHT wheel (the P16 board; THE LEFT, the P32 board, INSTEAD if the right fails its start checks) slowly, at power 15, about 30 short times, and stops it each way a program can -- a normal stop, a timed stop, an EMERGENCY STOP THAT BRAKES IT ABRUPTLY, and the stop that comes when commands stop arriving -- then reads why each drive stopped and what the driver logged. Then it drives the wheel ONE FULL TURN to a stop-after-rotation limit, drives it again for a few seconds with no limit, and e-stops it once more at rest. THEN THE RAMP TESTS, FASTER: the wheel spins up to power 50 (about 145 rpm), slows to power 25, stops, spins up to 25 and REVERSES to -25 without stopping, stops, and then six more spin-ups to power 50, each ended by a stop the program or a limit sends -- every speed change is a smooth ramp of a second or two. IF THE RIGHT WAS REFUSED, it then tries to start the right every 10 s, for up to 3 minutes, to time its return. Nothing waits for you and no window opens. About 2 minutes, or up to about 5 if the right is refused"
                    ;;
    # t0-reva (test_bench_t0 SRC_REV 30, DRIVER_REV 40, PL-163) -- T0-27 only: the Rev A fold-back on the Rev A platform
    #  (two Rev A boards; boards are never moved between platforms, Stephen 2026-09-30). Both groups start and print
    #  their board and each lead probe's reading; each Rev A group runs two unloaded legs (no fold), then a hard
    #  speed-up (must fold: the positive control). Hands-off: no window, no key, no grip. A group that does not come up as
    #  REV_A is printed and not driven. BENCH_QUIET for the same reason as t0.
    t0-reva)        BENCH_FILE="test_bench_t0.spin2"
                    EXTRA_DEFS=(-D BENCH_QUIET -D T0_REVA)
                    PRECONDITION="THE REV A PLATFORM (its two Rev A boards, as they are -- nothing is moved or swapped), ON THE BENCH, WHEELS UP, BOTH WHEELS FREE TO TURN -- HANDS OFF: NO WINDOW OPENS AND NOTHING IS CLICKED, TYPED OR HELD. BEFORE THE RUN: check the LEFT motor's leads are seated and continuous. The terminal prints its records, then a LEAD-IN line: nothing moves for 10 seconds. Then the program starts the LEFT motor, then the RIGHT (each start pulses the motor leads with nothing able to move), prints which board each read and what each motor lead read; a side whose START CHECK refuses it is printed as a FINDING and not driven. With the current limit lowered to 2 A, each wheel in turn, LEFT then RIGHT, turns SLOWLY twice (power 10, then power 5, about 6.5 s each, stopping between), then SPEEDS UP HARD ONCE from rest (to power 40 in well under a second) and stops. Stand clear of the wheels; you do nothing. About 50 seconds in all"
                    ;;
    spin)           BENCH_FILE="test_bench_spin.spin2"
                    PRECONDITION="BOTH WHEELS WILL TURN AT 50% POWER -- lift or support the platform"
                    ;;
    # spin-auto / spin-quiet (task 3613, PL-120): the spin wiring check with ONE thing changed each -- the board
    #  revision auto-detected (as the dual and T0 harnesses do), or the quiet debug build (as they are built). The
    #  right wheel turns in plain spin and not in those harnesses; whichever of these stops it names the factor.
    spin-auto)      BENCH_FILE="test_bench_spin.spin2"
                    EXTRA_DEFS=(-D SPIN_AUTO_DET)
                    PRECONDITION="BOTH WHEELS WILL TURN AT 50% POWER, WHEELS UP, HANDS OFF -- the spin check with the board revision auto-detected. Under 20 seconds"
                    ;;
    spin-quiet)     BENCH_FILE="test_bench_spin.spin2"
                    EXTRA_DEFS=(-D BENCH_QUIET)
                    PRECONDITION="BOTH WHEELS WILL TURN AT 50% POWER, WHEELS UP, HANDS OFF -- the spin check built quiet, as the dual and T0 tests are. Under 20 seconds"
                    ;;
    detect)         BENCH_FILE="test_bench_detect.spin2"
                    ;;
    detect-lib)     BENCH_FILE="test_bench_detect.spin2"
                    EXTRA_DEFS=(-D DETECT_LIB)
                    ;;
    detect-phase2)  BENCH_FILE="test_bench_detect.spin2"
                    EXTRA_DEFS=(-D DETECT_PHASE2)
                    PRECONDITION="MOTORS MAY STAY CONNECTED -- this build starts a real driver cog at commanded zero; groups whose sense pin lands on a board's gate input are skipped (GATE_OVERLAP) and a driver cog that overlaps another board is refused (COG_OVERLAP)"
                    ;;
    char)           BENCH_FILE="test_bench_char.spin2"
                    PRECONDITION="MOTORS CONNECTED, BOTH WHEELS FREE TO TURN -- UNATTENDED characterisation run"
                    ;;
    scan)           BENCH_FILE="test_bench_scan.spin2"
                    PRECONDITION="MOTORS CONNECTED, BOTH WHEELS FREE TO TURN -- UNATTENDED offset scan, up to 30 minutes, each wheel both directions to half speed"
                    ;;
    scan-wdtest)    BENCH_FILE="test_bench_scan.spin2"
                    EXTRA_DEFS=(-D WD_SELFTEST)
                    PRECONDITION="MOTORS CONNECTED, BOTH WHEELS FREE TO TURN -- WATCHDOG SELF-TEST: a brief preflight nudge per wheel, then the scan stalls ON PURPOSE; the watchdog must stop both drivers and end the session within about 15 s"
                    ;;
    # scan-droop (task 3594) -- the DROOP STOP's self-test, on the scan-wdtest precedent: certify an
    #  instrument mechanism in seconds instead of spending a sweep on it. The stop it certifies has
    #  never fired on hardware (MEASURED: 4 runs, 0 WS_DROOP), because every real droop point is the
    #  first point of a walk side and the walk then recovers, so the droop run never reaches 2.
    #  This build never starts a driver cog and never runs preflight, so nothing can move.
    scan-droop)     BENCH_FILE="test_bench_scan.spin2"
                    EXTRA_DEFS=(-D DROOP_SELFTEST)
                    PRECONDITION="NOTHING MOVES -- pure logic. No preflight, no driver cog, no wheel is ever commanded; the motors may stay connected or be disconnected, it makes no difference. Finishes in seconds and emits three BS-DROOPTEST records and three R18-SCAN-DROOPLOGIC verdicts"
                    ;;
    # The motion harness (task 3508; DOCs/plans/MOTION-HARNESS-DESIGN.md sec 4.1). One source, one part
    # per build: every part adds -D BENCH_QUIET (the quiet debug masks) and exactly one DUAL_PART_* flag.
    dual-a)         BENCH_FILE="test_bench_dual.spin2"
                    EXTRA_DEFS=(-D BENCH_QUIET -D DUAL_PART_A)
                    PRECONDITION="MOTORS CONNECTED, WHEELS UP, BOTH WHEELS FREE TO TURN, HANDS: NONE -- UNATTENDED motion harness part A (PREFLT, STOPMODE, LIVE, LADDER; the two ladder probe rungs above the speed ceiling may fault on purpose), run cap 25 minutes"
                    ;;
    # dual-a-legacy -- the LEGACY-offset leg, and the control any later phasing comparison needs.
    #  Same binary and the same loads as dual-a; the ONLY difference is that -D HUB_OFFSETS_LEGACY
    #  compiles the pre-6.0.0 commutation pair (offset_fwd 43, offset_rev 317) instead of the shipped
    #  scanned one (14 / 338). The polarity of this flag INVERTED after Visit 7b certified the scanned
    #  pair: dual-a now carries the shipped offsets and the flag reaches back for the old ones. The
    #  offsets are compiled in rather than written at run time, which is why such an A/B is two builds
    #  and not one run -- nothing is left modified on the board afterwards.
    dual-a-legacy)  BENCH_FILE="test_bench_dual.spin2"
                    EXTRA_DEFS=(-D BENCH_QUIET -D DUAL_PART_A -D HUB_OFFSETS_LEGACY)
                    PRECONDITION="MOTORS CONNECTED, WHEELS UP, BOTH WHEELS FREE TO TURN, HANDS: NONE -- UNATTENDED motion harness part A on the LEGACY commutation offsets (43 / 317). These draw 15x to 26x MORE current than the shipped pair at the same commanded speed (Visit 7b), so this leg runs hotter than any current dual-a: it is a control, not a normal run. The 10 A abort and the fold-back limiter are unchanged and both still apply. Run cap 25 minutes"
                    ;;
    # PL-62: the clock is chosen by NAME, so a mistyped clock is impossible rather than merely detectable -- a wrong name
    #  is refused. Task 3674: dual-clock takes any name in the clock table (clock_hz), and dual-clock-200 / -270 / -300 are
    #  shorthand for it with the clock named (tier_clock), so every name that ever worked still does. The CLOCK part judges
    #  ANY clock now (its expected frame is computed), not only these three.
    dual-clock-200|dual-clock-270|dual-clock-300|dual-clock)
                    BENCH_FILE="test_bench_dual.spin2"
                    EXTRA_DEFS=(-D BENCH_QUIET -D DUAL_PART_CLOCK)
                    if [ -z "$CLOCK_NAME" ]; then
                        die "tier 'dual-clock' needs a clock NAME: dual-clock <clock>, one of: $CLOCK_NAMES (or the shorthand tiers dual-clock-200, dual-clock-270, dual-clock-300)"
                    fi
                    PRECONDITION="MOTORS CONNECTED, WHEELS UP, BOTH WHEELS FREE TO TURN, HANDS: NONE -- UNATTENDED motion harness clock load (PREFLT, CLOCK) at the clock $CLOCK_NAME, clkfreq $CLK_OVERRIDE, about 1 minute"
                    ;;
    dual-b)         BENCH_FILE="test_bench_dual.spin2"
                    EXTRA_DEFS=(-D BENCH_QUIET -D DUAL_PART_B)
                    PRECONDITION="MOTORS CONNECTED, WHEELS UP, BOTH WHEELS FREE TO TURN, HANDS: NONE -- UNATTENDED motion harness part B (PREFLT, FAULTB ramp trials that fault on purpose, OVERSHT distance moves through the steering object), run cap 20 minutes"
                    ;;
    # dual-fault (task 3613, plan R19.7; DOCs/analyses/FAULT-STRATA-STUDY-2026-09-23.md sec 7) -- the fault responses.
    #  Every fault is FORCED through testForceFault() (DRIVER_REV 12), taken at the driver's own fault test: the old
    #  offset-shift provocation plugged the motor more often than it faulted it (PL-119). Each trial runs in its own
    #  driver lifetime; a forced fault that does not latch within 8 ms stops the wheel at once. PL-120 (src_rev 44): a
    #  trial whose wheel shows no hall tick 150 ms into its drive dumps that driver's runs, and after the first trial
    #  that never reaches speed the harness retries that wheel on its own (the recovery probe) before going on.
    #  PL-136 (src_rev 46): the same diagnosis at the start check (PREFLT). A nudge with no hall tick by 150 ms dumps
    #  the driver mid-nudge and is traced per phase; a wheel whose nudge does not turn is retried at once, 3 times about
    #  1 s apart, and, if none turns it, probed (6 tries, 20 s apart) before the fault trials. A wheel either turns runs
    #  its trials.
    dual-fault)     BENCH_FILE="test_bench_dual.spin2"
                    EXTRA_DEFS=(-D BENCH_QUIET -D DUAL_PART_FAULTRESP)
                    PRECONDITION="MOTORS CONNECTED, WHEELS UP, BOTH WHEELS FREE TO TURN, HANDS: NONE -- UNATTENDED motion harness part FAULTRESP (PREFLT, FLTRESP, FLTPLAT): FAULTS ARE FORCED ON PURPOSE AT SPEED (testForceFault(), DRIVER_REV 12), one wheel at a time at 40, 80 and 120 x 10^6 (up to about 220 rpm commanded), and each wheel stops per the response under test -- a phase short that STOPS IT DEAD, a free coast, a re-synced ramp down, or a graded short at 10, 25, 50 and 100 % entered by a second forced fault on that ramp; then, through the steering object at power 50, one wheel is faulted and the other must stop. FIRST EACH WHEEL GETS A SHORT NUDGE (under 1 s, slow). IF A WHEEL DOES NOT TURN ON ITS NUDGE (PL-120/PL-136), the program nudges it again at once, up to 3 more times about 1 s apart; if none turns it, it tries that wheel alone up to 6 more times, one every 20 s, each a 2 s drive at 40 x 10^6, BEFORE any fault trial: you will see one wheel still, twitch, or start turning again during this pause of up to about 2 minutes. IF A WHEEL STOPS DRIVING LATER, in a fault trial, the run pauses the same way once more. You do nothing throughout; the program decides and records everything. The 10 A abort and the fold-back limiter both apply. Run cap 15 minutes, expected about 6 (about 8.5 with one pause, at most about 10.5 with both)"
                    ;;
    # dual-fault-rightfirst (PL-120, src_rev 44) -- the same part built with -D FRESP_RIGHT_FIRST: the RIGHT wheel's own
    #  FLTRESP trials run before the LEFT's; PREFLT, FLTPLAT and everything else are identical. At 2026-09-24 21:21 the
    #  right stopped driving after the left's trials had run; this order decides whether they are its precondition.
    #  (Pass 4 settled that: they are not -- the right failed PREFLT on the first drive of the load. PL-136, src_rev 46:
    #  PREFLT now dumps, traces, retries and probes a wheel that does not turn, as dual-fault's note says.)
    dual-fault-rightfirst)
                    BENCH_FILE="test_bench_dual.spin2"
                    EXTRA_DEFS=(-D BENCH_QUIET -D DUAL_PART_FAULTRESP -D FRESP_RIGHT_FIRST)
                    PRECONDITION="MOTORS CONNECTED, WHEELS UP, BOTH WHEELS FREE TO TURN, HANDS: NONE -- UNATTENDED motion harness part FAULTRESP (PREFLT, FLTRESP, FLTPLAT) with the RIGHT WHEEL'S TRIALS FIRST, then the left's: FAULTS ARE FORCED ON PURPOSE AT SPEED (testForceFault()), one wheel at a time at 40, 80 and 120 x 10^6 (up to about 220 rpm commanded), and each wheel stops per the response under test -- a phase short that STOPS IT DEAD, a free coast, a re-synced ramp down, or a graded short at 10, 25, 50 and 100 % entered by a second forced fault on that ramp; then, through the steering object at power 50, one wheel is faulted and the other must stop. FIRST EACH WHEEL GETS A SHORT NUDGE (under 1 s, slow; left, then right). IF A WHEEL DOES NOT TURN ON ITS NUDGE (PL-120/PL-136), the program nudges it again at once, up to 3 more times about 1 s apart; if none turns it, it tries that wheel alone up to 6 more times, one every 20 s, each a 2 s drive at 40 x 10^6, BEFORE any fault trial: you will see one wheel still, twitch, or start turning again during this pause of up to about 2 minutes. IF A WHEEL STOPS DRIVING LATER, in a fault trial, the run pauses the same way once more. You do nothing throughout; the program decides and records everything. The 10 A abort and the fold-back limiter both apply. Run cap 15 minutes, expected about 6 (about 8.5 with one pause, at most about 10.5 with both)"
                    ;;
    # dual-start (task 3613, plan R19.7; DOCs/analyses/STARTUP-SELFTEST-STUDY-2026-09-23.md sec 6) -- the start checks.
    #  Ten steering lifetimes read what start() judged (getHealth(), the lead probe, the pack sensor) and a floated
    #  window's rest zero and coast floor; every one calls checkWiring() (PL-137, src_rev 47: was the last three) and
    #  prints the driver's own record of each leg (BM-SKWLEG). No PREFLT: the attended negatives load this part with a
    #  wheel mis-wired on purpose.
    dual-start)     BENCH_FILE="test_bench_dual.spin2"
                    EXTRA_DEFS=(-D BENCH_QUIET -D DUAL_PART_START)
                    PRECONDITION="MOTORS CONNECTED, WHEELS UP, BOTH WHEELS FREE TO TURN, HANDS: NONE -- UNATTENDED motion harness part START (SKCHECK): the steering object is started and stopped 10 times; each start pulses each motor lead at 50 % for a few ms with nothing able to move. In the first 2 starts the winding check also drives each pair of leads in turn for up to 0.3 s: EACH WHEEL TWITCHES A LITTLE, three times, as it lines up with each pair. AFTER EVERY START, all 10 of them, the wiring check turns the platform in place and back: EACH WHEEL TURNS A LITTLE ONE WAY, then back (about 3.5 cm at the tyre each way, slowly, about 1.5 s in all), the two wheels turning opposite ways. Each start ends with a still second while the program reads what the driver recorded. You do nothing. Run cap 3 minutes, expected about 1"
                    ;;
    # dual-start-nowalk -- the same part built with -D START_NO_WALK: checkWiring() is never called, so nothing in the
    #  build commands a wheel. The load for the attended B-1 (one wheel's hall connector unplugged): a mis-wired wheel is
    #  only read, never driven. The only wiring change this rig allows (Rig facts, STEPHEN 2026-09-23).
    dual-start-nowalk)
                    BENCH_FILE="test_bench_dual.spin2"
                    EXTRA_DEFS=(-D BENCH_QUIET -D DUAL_PART_START -D START_NO_WALK)
                    PRECONDITION="WHEELS UP -- YOU CHANGE WIRING: battery off, unplug the RIGHT wheel's hall-sensor connector, battery on, then run. The program does 10 startup checks, each told to go ahead even though the unplugged wheel fails its check, and no wheel moves. Afterwards: battery off, replug the connector, battery on. Under 1 minute"
                    ;;
    # dual-start-phaseneg (task 3614) -- B-3's negative in firmware, since the rig cannot open a motor lead: each start's
    #  lead check leaves one LEFT phase undriven (testLeftSetProbeWithhold(), rotating U, V, W), so exactly that phase's
    #  HLT_PHASE bit must fail. No walk. Task 3610: the opt-out starts also run the winding check, whose two pairs through
    #  the withheld phase must read NOT_VISIBLE (R19-DUAL-WINDNEG-X); the pairs it does drive twitch the wheels.
    #  Task 3621: a failing check now refuses the start, so the 12 starts rotate three ways in blocks of three (U, V, W):
    #  opt-out (setStartChecks(FALSE), where PHNEG-X and WINDNEG-X are judged as before, and R20-DUAL-OPTOUT), refusal
    #  (R20-DUAL-REFUSE), and withheld from the first attempt only (R20-DUAL-RETRY).
    dual-start-phaseneg)
                    BENCH_FILE="test_bench_dual.spin2"
                    EXTRA_DEFS=(-D BENCH_QUIET -D DUAL_PART_START -D START_NEG_PHASE)
                    PRECONDITION="WHEELS UP, HANDS OFF, DO NOT TOUCH ANY WIRING -- UNATTENDED, YOU DO NOTHING: the program fakes a dead motor wire on the LEFT wheel at each of 12 startup checks and must catch it. At 6 of them it has the start go ahead anyway; at 3 it lets the start refuse and checks it says why; at 3 it fakes the wire only on the first try and checks the retry is reported. At those first 6 it also checks the motor windings: BOTH WHEELS TWITCH A LITTLE then (the right three times, the left once). Under 2 minutes"
                    ;;
    # dual-start-swapneg (task 3614) -- B-5's negative in firmware, since the rig cannot swap hall wires: in the walk
    #  lifetimes the LEFT wheel reads two halls as swapped (testLeftSetHallSwap()), so checkWiring() must fail it.
    dual-start-swapneg)
                    BENCH_FILE="test_bench_dual.spin2"
                    EXTRA_DEFS=(-D BENCH_QUIET -D DUAL_PART_START -D START_NEG_SWAP)
                    PRECONDITION="WHEELS UP, HANDS OFF, DO NOT TOUCH ANY WIRING -- the program fakes crossed hall-sensor wires on the LEFT wheel, then nudges both wheels 3 times and must notice the left is miswired. The LEFT WHEEL MAY JERK, BUZZ OR TURN BACKWARDS for up to 2 s at a time until it stops itself. Panic: battery disconnect. Under 1 minute"
                    ;;
    # The FLOOR RUN as FOURTEEN single-action commands with no window (Stephen, 2026-09-30, DOCs/plans/WINDOW-FREE-BENCH-
    #  SPRINT-PLAN.md section 2; the old dual-spin tier -- the five-situation run behind the operator panel and the countdown
    #  board -- is abandoned, R10). Each tier is part SPIN of test_bench_dual.spin2 with ONE action chosen by its own -D
    #  FLOOR_ACT_*: it runs that action once (a repeat is a rerun, R4), after a 10 s lead-in (R3), opens no window and reads
    #  no key or click (R1), and prints one plain RESULT line last. The floor rules are the construction: only distance-
    #  controlled drives, every leg armed before it moves, at most 1 m straight and one turn in place (two at the quarter speed), the harness's travel
    #  guard and the 10 A abort. -D BENCH_QUIET for the motion harness's reason (I5). No PREFLT: its single-wheel nudge would
    #  pivot a platform standing on the floor. The slow, med and fast spins are the confirmed-offset (SCHED) pairs at the three
    #  speeds; legacy and fixed are the comparison pairs, so the analysis can judge the ratios that compare pairs across logs.
    floor-obstacle-coast)
                    BENCH_FILE="test_bench_dual.spin2"
                    EXTRA_DEFS=(-D BENCH_QUIET -D DUAL_PART_SPIN -D FLOOR_ACT_OBST_COAST)
                    PRECONDITION="$FLOOR_FRAME WHAT IT DOES: drives straight at an obstacle, slowly (0.16 m/s, current limited to 2 A), until the platform's own protective stop latches about a second after it is blocked -- with the motor bridge left to COAST -- then checks that stop: it must refuse a new drive until the stop is cleared, and take one after. WHERE YOU STAND: 0.3-0.8 m in front of the platform, square across its path, or put an object there that cannot move; keep clear of the wheels. WHAT YOU DO: nothing. WHAT YOU SEE: the lead-in line and 10 still seconds, then the platform creeping forward and stopping itself against the obstacle, then a few seconds of checks. THE LAST LINE TO EXPECT: 'RESULT: OBSTACLE COAST -- the platform stopped itself on the obstacle (the protective stop latched)'. If it says it never met the obstacle, stand it nearer and run it again. About 40 seconds. $FLOOR_TAIL"
                    ;;
    floor-obstacle-short)
                    BENCH_FILE="test_bench_dual.spin2"
                    EXTRA_DEFS=(-D BENCH_QUIET -D DUAL_PART_SPIN -D FLOOR_ACT_OBST_SHORT)
                    PRECONDITION="$FLOOR_FRAME WHAT IT DOES: the same drive into the obstacle as floor-obstacle-coast, but the protective stop leaves the motor bridge SHORTED instead of coasting -- the control that shows the coast run's reading can tell the two apart. Then the same checks of the stop. WHERE YOU STAND: 0.3-0.8 m in front of the platform, square across its path, or put an object there that cannot move; keep clear of the wheels. WHAT YOU DO: nothing. WHAT YOU SEE: the lead-in line and 10 still seconds, then the platform creeping forward and stopping itself against the obstacle, then a few seconds of checks. THE LAST LINE TO EXPECT: 'RESULT: OBSTACLE SHORT -- the platform stopped itself on the obstacle (the protective stop latched)'. About 40 seconds. $FLOOR_TAIL"
                    ;;
    floor-grab)
                    BENCH_FILE="test_bench_dual.spin2"
                    EXTRA_DEFS=(-D BENCH_QUIET -D DUAL_PART_SPIN -D FLOOR_ACT_GRAB)
                    PRECONDITION="$FLOOR_FRAME WHAT IT DOES: drives 1 m straight at a slow walk (0.16 m/s, current limited to 4 A) and stops itself at 1 m. WHERE YOU STAND: beside its LEFT side, hand ready, the lane clear ahead. WHAT YOU DO: about 3 seconds after it starts rolling, take hold of its LEFT side (the frame) firmly and KEEP HOLDING until it stops by itself at 1 m -- enough to slow it to about half speed, not enough to stop it. There is nothing to click, no key to press, and no let-go cue: the program times its own window from the start of the drive, and that window lies inside any hold taken between about 2.5 and 3.5 seconds after it starts rolling. WHAT YOU SEE: the lead-in line and 10 still seconds, then the platform rolling away, your hold slowing it, then the stop. THE LAST LINE TO EXPECT: 'RESULT: GRAB -- judged: the hold was read'. If it says 'too light: hold harder next run', 'stalled: hold less next run' or 'the hold was too firm to judge the line, so hold less next run', run it again as it says: slow it to about half speed, not nearly to a stop. About 45 seconds. $FLOOR_TAIL"
                    ;;
    floor-faultrun)
                    BENCH_FILE="test_bench_dual.spin2"
                    EXTRA_DEFS=(-D BENCH_QUIET -D DUAL_PART_SPIN -D FLOOR_ACT_FAULTRUN)
                    PRECONDITION="$FLOOR_FRAME WHAT IT DOES, as one sequence: drives 1 m forward (0.23 m/s); the terminal prints 'STAND CLEAR: the platform drives back in 5 s' and it drives back; after about a second the LEFT wheel is faulted on purpose -- both wheels stop within half a second and the platform turns a few degrees; it recovers; the terminal prints 'STAND CLEAR: the platform drives on to its start in 5 s' and it drives on to its start. WHERE YOU STAND: beside the lane, clear of it. WHAT YOU DO: nothing. WHAT YOU SEE: the lead-in line and 10 still seconds, the drive out, the first STAND CLEAR line and 5 still seconds, the drive back and the sudden stop, the second STAND CLEAR line and 5 seconds, the drive to the start. THE LAST LINE TO EXPECT: 'RESULT: FAULT RUN -- fault seen and recovered: the drive on to the start drew normal current'. About 65 seconds. The platform ends at or near its start: put it exactly there by hand before the next run. $FLOOR_TAIL"
                    ;;
    floor-spin-slow-left)
                    BENCH_FILE="test_bench_dual.spin2"
                    EXTRA_DEFS=(-D BENCH_QUIET -D DUAL_PART_SPIN -D FLOOR_ACT_SPIN_SLOW_LEFT)
                    PRECONDITION="$FLOOR_FRAME $FLOOR_SPIN_WHAT SPEED: SLOW, LEFT (counter-clockwise seen from above). The turn takes about 8 seconds. THE LAST LINE TO EXPECT: 'RESULT: SPIN SLOW LEFT -- ended at its turn limit'. About 25 seconds. $FLOOR_TAIL"
                    ;;
    floor-spin-slow-right)
                    BENCH_FILE="test_bench_dual.spin2"
                    EXTRA_DEFS=(-D BENCH_QUIET -D DUAL_PART_SPIN -D FLOOR_ACT_SPIN_SLOW_RIGHT)
                    PRECONDITION="$FLOOR_FRAME $FLOOR_SPIN_WHAT SPEED: SLOW, RIGHT (clockwise seen from above). The turn takes about 8 seconds. THE LAST LINE TO EXPECT: 'RESULT: SPIN SLOW RIGHT -- ended at its turn limit'. About 25 seconds. $FLOOR_TAIL"
                    ;;
    floor-spin-med-left)
                    BENCH_FILE="test_bench_dual.spin2"
                    EXTRA_DEFS=(-D BENCH_QUIET -D DUAL_PART_SPIN -D FLOOR_ACT_SPIN_MED_LEFT)
                    PRECONDITION="$FLOOR_FRAME $FLOOR_SPIN_WHAT SPEED: MEDIUM, LEFT (counter-clockwise seen from above). The turn takes about 4 seconds. THE LAST LINE TO EXPECT: 'RESULT: SPIN MEDIUM LEFT -- ended at its turn limit'. About 20 seconds. $FLOOR_TAIL"
                    ;;
    floor-spin-med-right)
                    BENCH_FILE="test_bench_dual.spin2"
                    EXTRA_DEFS=(-D BENCH_QUIET -D DUAL_PART_SPIN -D FLOOR_ACT_SPIN_MED_RIGHT)
                    PRECONDITION="$FLOOR_FRAME $FLOOR_SPIN_WHAT SPEED: MEDIUM, RIGHT (clockwise seen from above). The turn takes about 4 seconds. THE LAST LINE TO EXPECT: 'RESULT: SPIN MEDIUM RIGHT -- ended at its turn limit'. About 20 seconds. $FLOOR_TAIL"
                    ;;
    floor-spin-fast-left)
                    BENCH_FILE="test_bench_dual.spin2"
                    EXTRA_DEFS=(-D BENCH_QUIET -D DUAL_PART_SPIN -D FLOOR_ACT_SPIN_FAST_LEFT)
                    PRECONDITION="$FLOOR_FRAME $FLOOR_SPIN_WHAT SPEED: FAST, the quarter of full speed, LEFT (counter-clockwise seen from above). The two turns take about 5 seconds. THE LAST LINE TO EXPECT: 'RESULT: SPIN FAST LEFT -- ended at its turn limit'. About 32 seconds. $FLOOR_TAIL"
                    ;;
    floor-spin-fast-right)
                    BENCH_FILE="test_bench_dual.spin2"
                    EXTRA_DEFS=(-D BENCH_QUIET -D DUAL_PART_SPIN -D FLOOR_ACT_SPIN_FAST_RIGHT)
                    PRECONDITION="$FLOOR_FRAME $FLOOR_SPIN_WHAT SPEED: FAST, the quarter of full speed, RIGHT (clockwise seen from above). The two turns take about 5 seconds. THE LAST LINE TO EXPECT: 'RESULT: SPIN FAST RIGHT -- ended at its turn limit'. About 32 seconds. $FLOOR_TAIL"
                    ;;
    floor-spin-legacy-left)
                    BENCH_FILE="test_bench_dual.spin2"
                    EXTRA_DEFS=(-D BENCH_QUIET -D DUAL_PART_SPIN -D FLOOR_ACT_SPIN_LEGACY_LEFT)
                    PRECONDITION="$FLOOR_FRAME $FLOOR_SPIN_WHAT SPEED: MEDIUM, LEFT (counter-clockwise seen from above). This spin uses a comparison setting of the motor timing -- the old version 5.0.2 values -- so its current can be compared with the matching standard medium spin (floor-spin-med); nothing else differs for you. The turn takes about 4 seconds. THE LAST LINE TO EXPECT: 'RESULT: SPIN LEGACY LEFT -- ended at its turn limit'. About 22 seconds. $FLOOR_TAIL"
                    ;;
    floor-spin-legacy-right)
                    BENCH_FILE="test_bench_dual.spin2"
                    EXTRA_DEFS=(-D BENCH_QUIET -D DUAL_PART_SPIN -D FLOOR_ACT_SPIN_LEGACY_RIGHT)
                    PRECONDITION="$FLOOR_FRAME $FLOOR_SPIN_WHAT SPEED: MEDIUM, RIGHT (clockwise seen from above). This spin uses a comparison setting of the motor timing -- the old version 5.0.2 values -- so its current can be compared with the matching standard medium spin (floor-spin-med); nothing else differs for you. The turn takes about 4 seconds. THE LAST LINE TO EXPECT: 'RESULT: SPIN LEGACY RIGHT -- ended at its turn limit'. About 22 seconds. $FLOOR_TAIL"
                    ;;
    floor-spin-fixed-left)
                    BENCH_FILE="test_bench_dual.spin2"
                    EXTRA_DEFS=(-D BENCH_QUIET -D DUAL_PART_SPIN -D FLOOR_ACT_SPIN_FIXED_LEFT)
                    PRECONDITION="$FLOOR_FRAME $FLOOR_SPIN_WHAT SPEED: FAST, the quarter of full speed, LEFT (counter-clockwise seen from above). This spin uses a comparison setting of the motor timing -- a fixed value in place of the speed-dependent one -- so its current can be compared with the matching standard fast spin (floor-spin-fast); nothing else differs for you. The two turns take about 5 seconds. THE LAST LINE TO EXPECT: 'RESULT: SPIN FIXED LEFT -- ended at its turn limit'. About 32 seconds. $FLOOR_TAIL"
                    ;;
    floor-spin-fixed-right)
                    BENCH_FILE="test_bench_dual.spin2"
                    EXTRA_DEFS=(-D BENCH_QUIET -D DUAL_PART_SPIN -D FLOOR_ACT_SPIN_FIXED_RIGHT)
                    PRECONDITION="$FLOOR_FRAME $FLOOR_SPIN_WHAT SPEED: FAST, the quarter of full speed, RIGHT (clockwise seen from above). This spin uses a comparison setting of the motor timing -- a fixed value in place of the speed-dependent one -- so its current can be compared with the matching standard fast spin (floor-spin-fast); nothing else differs for you. The two turns take about 5 seconds. THE LAST LINE TO EXPECT: 'RESULT: SPIN FIXED RIGHT -- ended at its turn limit'. About 32 seconds. $FLOOR_TAIL"
                    ;;
    # The two FLOOR SESSIONS (SRC_REV 70; Plan A sec 10, R15, R16, R17): several checks chained in one command because none of
    #  them needs him in between, all inside a 2 m x 2 m square from his fixed start point and back to it. Each is part SPIN of
    #  test_bench_dual.spin2 with the session's own -D FLOOR_ACT_*: the 10 s lead-in (R3), no window, no key or click (R1), no
    #  PREFLT, -D BENCH_QUIET (I5), one plain RESULT line last. floor-auto is SESSION 2 (the ten spins, the fault run, the ramp
    #  legs), floor-obstacle SESSION 3 (the coast trial and the brake trial, each with a drive back); floor-grab stays a command
    #  of its own (SESSION 4: it needs his hand).
    floor-auto)
                    BENCH_FILE="test_bench_dual.spin2"
                    EXTRA_DEFS=(-D BENCH_QUIET -D DUAL_PART_SPIN -D FLOOR_ACT_AUTO)
                    PRECONDITION="$FLOOR_SESSION_FRAME WHAT IT DOES, in three parts one after another, with nothing for you to do between them: PART 1, TEN SPINS IN PLACE, one platform turn each at three settings and two turns each at the fast, quarter-speed ones, clockwise and then counter-clockwise at each -- slow (about 8 seconds a turn), medium (about 4), a medium on the old version 5.0.2 motor timing, fast (two turns, about 5 seconds), and a fast on a fixed motor timing (two turns, about 5) -- about 90 seconds in all, the terminal printing 'PART 1 OF 3'. PART 2, THE FAULT RUN: 1 m forward (0.23 m/s); the terminal prints 'STAND CLEAR: the platform drives back in 5 s' and it drives back; after about a second the LEFT wheel is faulted on purpose -- both wheels stop within half a second and the platform turns a few degrees; it recovers; the terminal prints 'STAND CLEAR: the platform drives on to its start in 5 s' and it drives on to its start -- about 50 seconds, 'PART 2 OF 3'. PART 3, THE RAMP LEGS: four straight 1 m legs at a walking pace (0.31 m/s), out, back, out, back, each at its own speeding-up and slowing-down rate (200 and 1,000, then 1,000 and 1,470, then 3,000 and 3,000, then 1,000 and 1,470 millimetres per second per second): the first leg takes about 4.5 seconds and speeds up slowly and gently, the third speeds up and stops quickly, with a second's rest between legs -- about 30 seconds, 'PART 3 OF 3'. The program records what each leg achieved against its setting. WHERE YOU STAND: outside the square, beside it, clear of the platform's path and of its turning circle. WHAT YOU DO: nothing but stand by. WHAT YOU SEE: the lead-in line and 10 still seconds; ten slow turns of the platform on the spot; the first STAND CLEAR line and 5 still seconds, the drive out and back, the sudden stop, the second STAND CLEAR line and 5 seconds, the drive to the start; then four 1 m drives, out and back twice. THE LAST LINE TO EXPECT: 'RESULT: AUTO SESSION -- spins: 10 of 10 ended at their turn limit; fault run: fault seen and recovered: the drive on to the start drew normal current; ramp legs: 4 of 4 ran to their limit; the platform ended at x ... mm, y ... mm, heading ... degrees, from where it began'. If a part cannot run or a drive is refused you will also see a line starting 'FENCE:' or 'SKIPPED:' and the RESULT line will say which part. About 3 minutes (180 seconds, the 10-second lead-in included). $FLOOR_SESSION_TAIL"
                    ;;
    floor-obstacle)
                    BENCH_FILE="test_bench_dual.spin2"
                    EXTRA_DEFS=(-D BENCH_QUIET -D DUAL_PART_SPIN -D FLOOR_ACT_OBSTACLE)
                    PRECONDITION="$FLOOR_SESSION_FRAME WHAT IT DOES, two trials one after the other: TRIAL 1, COAST: drives straight at the obstacle, slowly (0.16 m/s, current limited to 2 A), until the platform's own protective stop latches about a second after it is blocked -- with the motor bridge left to COAST -- then checks that stop (it must refuse a new drive until the stop is cleared, and take one after); then the terminal prints 'STAND CLEAR: the platform drives back to its start in 5 s' and it drives BACK to its start, slowly, the distance it moved forward (measured, at most 1 m, armed first). It drives back only if both wheels are at rest and any fault has been recovered; otherwise it stops there and says so. TRIAL 2, BRAKE: the same, but the protective stop leaves the motor bridge SHORTED instead of coasting -- the control that shows the coast trial's reading can tell the two apart -- and back to the start again. Each trial takes about 25 seconds. WHERE YOU STAND AND WHAT YOU PLACE: put a fixed object that cannot move 0.3-0.8 m ahead of the platform, square across its path (the platform runs into it twice, so it cannot be you); you stand beside the lane, clear of the wheels. WHAT YOU DO: nothing but stand by. WHAT YOU SEE: the lead-in line and 10 still seconds, the platform creeping forward and stopping itself against the object, a few seconds of checks, the STAND CLEAR line and 5 still seconds, the platform backing slowly to its start, then the same again. THE LAST LINE TO EXPECT: 'RESULT: OBSTACLE SESSION -- COAST: the platform stopped itself on the obstacle (the protective stop latched), then drove back to its start; BRAKE: the platform stopped itself on the obstacle (the protective stop latched), then drove back to its start; the platform ended at x ... mm, y ... mm, heading ... degrees, from where it began'. If it says it never met the obstacle, stand it nearer and run it again; if a coast trial ends in a wheel fault it recovers it and drives back if it can, and says so. About 1 minute (60 seconds, the 10-second lead-in included). $FLOOR_SESSION_TAIL"
                    ;;
    # dual-pack (task 3611, plan R20.4) -- the pack voltage sensor on Stephen's fitted unit (VOLTAGE-SENSOR.md). One
    #  steering lifetime whose start checks run and nothing more: no wheel is ever commanded. Step 1 reads the pack
    #  steady for 60 s (R20-PACK-EV's negative); steps 2-5 unplug and replug the sensor at the PACK end twice, each step
    #  ended by the sensor itself seeing it, so there is no key and no click (R20-PACK-ABSENT, R20-PACK-EV). When a meter
    #  pair is still owed the terminal asks for ONE meter reading just before step 2; he sends the number to the agent in
    #  chat, which compiles it in, and the next dual-pack run prints the pair's verdict (R20-PACK-METER). Nothing numeric
    #  is typed at the bench. Built with PACK_SENSOR_FITTED FALSE it reads nothing and every pack cell prints NOT_BUILT.
    dual-pack)      BENCH_FILE="test_bench_dual.spin2"
                    EXTRA_DEFS=(-D BENCH_QUIET -D DUAL_PART_PACK)
                    PRECONDITION="RETIRED 2026-09-27 (Stephen: no more unplug testing -- it wears the connector; PL-162 closed). Do not run it. NOTHING MOVES: the wheels are never driven. ATTENDED -- you unplug and replug the pack voltage sensor, twice. WATCH THE TERMINAL: each step prints one line starting PACK STEP n OF 5, then the terminal goes quiet while you do it; the program sees each unplug and plug-in by itself -- no key, no click. STEP 1: hands off for 60 s. IF THE TERMINAL SAYS METER READING NEEDED (only then): read the pack voltage on your meter once, remember it, and send it to the agent in chat after the run -- type nothing here. STEP 2: unplug the sensor Powerpole AT THE PACK (not the header at the P2) within 60 s. STEP 3: plug it back in within 60 s. STEPS 4 AND 5: the same again. A step not seen in 60 s is counted as a FAIL and nothing more runs. Built without the sensor fitted, it reads nothing, says NOT BUILT and ends. Under 5 minutes"
                    ;;
    dual-brake)     BENCH_FILE="test_bench_dual.spin2"
                    EXTRA_DEFS=(-D BENCH_QUIET -D DUAL_PART_BRAKE)
                    PRECONDITION="MOTORS CONNECTED, WHEELS UP -- ATTENDED motion harness part BRAKE (OUTSIDE): STEPHEN AT THE RIG FOR ONE HAND-BRAKE OF THE LEFT WHEEL; click the bmpanel window first; nothing moves until START; brake only when the panel says BRAKE, release when it says RELEASE"
                    ;;
    dual-c)         BENCH_FILE="test_bench_dual.spin2"
                    EXTRA_DEFS=(-D BENCH_QUIET -D DUAL_PART_C)
                    PRECONDITION="MOTORS CONNECTED, WHEELS UP, BOTH WHEELS FREE TO TURN, HANDS: NONE -- UNATTENDED motion harness part C (PREFLT, BASELINE, POSTFLT: provoked faults and e-stops at half speed), run cap 15 minutes"
                    ;;
    dual-d)         BENCH_FILE="test_bench_dual.spin2"
                    EXTRA_DEFS=(-D BENCH_QUIET -D DUAL_PART_D)
                    PRECONDITION="MOTORS CONNECTED, WHEELS UP, BOTH WHEELS FREE TO TURN, HANDS: NONE -- UNATTENDED motion harness part D (PREFLT, STEERSEG, LIMIT): the front cog's contract and current limiting. THE WHEELS STOP DEAD, JERK AND STAND STILL UNDER POWER ON PURPOSE -- an emergency stop is latched and held, a stop is ordered while another cog drives, and the current limits are lowered until the motor cannot turn (the protective-stop test) before being restored. After each lowered-limit step the wheels rest about a second while the program reads the driver's event log. TWICE, both wheels are spun up to about half speed and the platform is switched off while they turn -- the second time switched straight back on -- and the wheels are left to coast to a stop by themselves (about 30 s in all, at most about 1 minute). You do nothing. Run cap 15 minutes"
                    ;;
    dual-floor)     BENCH_FILE="test_bench_dual.spin2"
                    EXTRA_DEFS=(-D BENCH_QUIET -D DUAL_PART_FLOOR)
                    PRECONDITION="PLATFORM ON THE FLOOR, WHEELS DOWN, SPACE CLEAR -- ATTENDED motion harness part FLOOR: STEPHEN OBSERVES A BRIEF (ABOUT 2 SECOND) WHEELS-DOWN DRIVE at power 50, direction +50; click the bmpanel window first; nothing moves until START; STOP (click or space) is live throughout"
                    ;;
    dual-ui)        BENCH_FILE="test_bench_dual.spin2"
                    EXTRA_DEFS=(-D BENCH_QUIET -D DUAL_PART_UICHECK)
                    PRECONDITION="NO MOTOR CONTROL -- UI walkthrough: no wheel or steering object is ever started, nothing moves; click the bmpanel window first; click each button it shows and press the key named on it; then judge each dual-brake screen with the two buttons in the strip at the bottom (LOOKS RIGHT = key Y, SOMETHING WRONG = key W) -- the screen's own buttons do nothing there; PASSED -> run dual-brake; FAILED -> it waits for the next bench run"
                    ;;
    # dual-align (task 3590) -- the ONE tier that never drives a motor. Both drivers are started so
    #  their ADCs read, both are set to FLOAT at stop so the bridge coasts (all six FETs off), and the
    #  wheels are then turned BY HAND. Only a DRIVEN bridge can fault, so this tier cannot fault, abort
    #  on current or run away; the R18-DUAL-ALIGN-ND cell measures that the promise held.
    dual-align)     BENCH_FILE="test_bench_dual.spin2"
                    EXTRA_DEFS=(-D BENCH_QUIET -D DUAL_PART_ALIGN)
                    PRECONDITION="MOTORS CONNECTED, WHEELS UP, HANDS ON THE WHEEL -- ATTENDED motion harness part ALIGN: NO MOTOR IS EVER DRIVEN, so it cannot fault, current-abort or run away. 8 legs (left wheel then right, each forward and reverse, each slow and fast). JUST FOLLOW THE 'TURN ...' LINE: each leg prints one plain line naming the wheel, the direction and the pace -- e.g. 'TURN LEFT WHEEL FORWARD, SLOW' -- then the run goes SILENT. Turn that wheel that way until the output starts again; you never count turns and you never have to hit a speed, because the leg ends on its own tick total and the pace you actually used is measured. WHEN A LEG ENDS, HOLD THE WHEEL STILL: the next leg reads its zero level first and needs the wheel stopped. No panel and no keyboard, run cap 30 minutes"
                    ;;
    # dual-lead (task 3583, R18.4) -- measures the driver's dynamic-lead table. At the eighth, quarter,
    #  half and full speeds, per wheel and direction, the commutation pair is stepped LIVE through a lead
    #  of 18, 13, 8, 3, -2, -7, 23, 28 and 33 degrees while the wheel runs; each step is a measured rung, and
    #  each speed ends with BM-LEADMIN. The low leads at high speed can reach the torque wall and fault:
    #  a fault is recovered and the next step runs, and the ladder's current abort still applies.
    dual-lead)      BENCH_FILE="test_bench_dual.spin2"
                    EXTRA_DEFS=(-D BENCH_QUIET -D DUAL_PART_LEAD)
                    PRECONDITION="MOTORS CONNECTED, WHEELS UP, BOTH WHEELS FREE TO TURN, HANDS: NONE -- UNATTENDED motion harness part LEAD (PREFLT, LEAD): each wheel, each direction, held at four speeds up to full while its lead is stepped through nine values. At the higher speeds a low lead may FAULT the motor on purpose (the torque wall); it is recovered and the run goes on. The 10 A abort and the fold-back limiter both apply. Run cap 25 minutes"
                    ;;
    # dual-limits (task 3604, DOCs/plans/LIMITS-RESET-PLAN.md E1, E3, E4) -- where the limits the old drive set
    #  now lie. LIMTOP climbs each wheel and direction past today's 147 x 10^6 ceiling, 10 x 10^6 at a time, until
    #  the wheel stops following (at most 245 x 10^6); LIMRAMP traces starts and speed-downs at faster ramps;
    #  LIMLOW runs four speeds from today's low-speed floor down, then again with duty_min halved.
    # dual-limits-top (task 3605) -- the SAME part's LIMTOP only (-D LIMITS_TOP_ONLY): each wheel and direction
    #  climbs to the edge, then is commanded power 100 and power 1 through the public API to confirm the moved
    #  power table reached the drive. (It replaces dual-limits-svm: the duty ceiling that tier compared is now
    #  the drive's own.)
    dual-limits)    BENCH_FILE="test_bench_dual.spin2"
                    EXTRA_DEFS=(-D BENCH_QUIET -D DUAL_PART_LIMITS)
                    PRECONDITION="MOTORS CONNECTED, WHEELS UP, BOTH WHEELS FREE TO TURN, HANDS: NONE -- UNATTENDED motion harness part LIMITS (PREFLT, LIMTOP, LIMRAMP, LIMLOW). THE WHEELS RUN FASTER THAN ANY RUN BEFORE: each wheel, each direction, climbs past today's top speed until it stops keeping up (at most about 440 rpm commanded). At the edge a wheel may FAULT on purpose; it is recovered and the run goes on. Then faster starts, faster slow-downs, and very slow speeds that may barely turn. The 10 A abort and the fold-back limiter both apply. Run cap 30 minutes"
                    ;;
    dual-limits-top) BENCH_FILE="test_bench_dual.spin2"
                    EXTRA_DEFS=(-D BENCH_QUIET -D DUAL_PART_LIMITS -D LIMITS_TOP_ONLY)
                    PRECONDITION="MOTORS CONNECTED, WHEELS UP, BOTH WHEELS FREE TO TURN, HANDS: NONE -- UNATTENDED motion harness part LIMITS, TOP-SPEED CLIMB ONLY: each wheel, each direction, climbs to about 440 rpm commanded as at Visit 9, then runs at full power and at least power through the public API. At the edge a wheel may slip or FAULT on purpose; it is recovered. The 10 A abort and the fold-back limiter both apply. Run cap 30 minutes, expected about 5"
                    ;;
    # dual-reg (PL-151's part-B half, PL-152's pointed form) -- part REG only: TURNDIST, FLTCAUSE and PL-66's FLTRETRY,
    #  under part B's own cell ids, in a load that runs nothing else. The fault is forced with testForceFault() (PL-119),
    #  one wheel per steering lifetime, under FR_SHIPPED so it latches; see the part's CON in test_bench_dual.spin2.
    dual-reg)       BENCH_FILE="test_bench_dual.spin2"
                    EXTRA_DEFS=(-D BENCH_QUIET -D DUAL_PART_REG)
                    PRECONDITION="MOTORS CONNECTED, WHEELS UP, BOTH WHEELS FREE TO TURN, HANDS: NONE -- UNATTENDED, YOU DO NOTHING: first each wheel gets a short slow nudge on its own (under 1 s each). Then BOTH WHEELS TURN TOGETHER AT HALF POWER, TWICE, for a measured distance -- one wheel runs about 10 ft of tyre travel while the other runs about 2 ft and stops first, then the other way round (a few seconds each). Then, TWICE MORE, both wheels spin up to half power and ONE WHEEL IS FAULTED ON PURPOSE (the left, then the right): it coasts, the other wheel slows to a stop beside it, and a second later BOTH SPIN UP AGAIN at half power for a moment before stopping. No window opens. The 10 A abort applies throughout. Run cap 5 minutes, expected under 1"
                    ;;
    # dual-kick (the kick fix's certificate; PL-78, PL-87) -- part KICK only: the ladder's own rung walk over the seven
    #  top-of-range speed changes that carried the pre-fix kicks, per wheel and direction; see the part's CON.
    dual-kick)      BENCH_FILE="test_bench_dual.spin2"
                    EXTRA_DEFS=(-D BENCH_QUIET -D DUAL_PART_KICK)
                    PRECONDITION="MOTORS CONNECTED, WHEELS UP, BOTH WHEELS FREE TO TURN, HANDS: NONE -- UNATTENDED, YOU DO NOTHING: first each wheel gets a short slow nudge on its own (under 1 s each). Then ONE WHEEL AT A TIME, left then right, each direction in turn (4 runs): the wheel spins up from rest to high speed, then steps UP through four faster speeds to its top speed (about 300 rpm commanded) and back DOWN three steps, holding each speed about 2 seconds, then stops. The other wheel stays still. The 10 A abort and the fold-back limiter both apply. Run cap 5 minutes, expected under 2"
                    ;;
    # dual-tokneg (task 3651, HOLD-SPEED plan sec 4) -- the negative case of the record labels' start-up self-check
    #  (tokenTablesSelfTest(), cell R21-DUAL-TOKTAB, which every dual tier prints and which must PASS there). -D TOKCHK_NEG
    #  builds the harness with two of its own token tables WRONG on purpose: the scope table one token short of its count,
    #  and the exit table with one token past its field's width. The cell must print FAIL, and BM-TOKCHK must say so (bad_count 1,
    #  bad_len 1, first_bad tokScope). No part flag, so no part runs: nothing is started and nothing moves, the run ends in
    #  seconds. It is the same source as every dual tier and nothing else: a one-off tier for a visit's pack, run once.
    dual-tokneg)    BENCH_FILE="test_bench_dual.spin2"
                    EXTRA_DEFS=(-D BENCH_QUIET -D TOKCHK_NEG)
                    PRECONDITION="NOTHING MOVES -- UNATTENDED, YOU DO NOTHING: no wheel or steering object is started and no motor is commanded; the motors may stay connected or be disconnected, it makes no difference. The harness prints its records, builds two of its own token tables wrong on purpose, and must print R21-DUAL-TOKTAB FAIL. Finishes in seconds"
                    ;;
    # demo-single / demo-dual (PL-149) -- the two release demos, run as shipped. Under -D BENCH_CFG each reads the bench
    #  config instead of the end-user one (demo_single_motor drives the bench's RIGHT motor, as it names no single motor)
    #  and prints DEBUG_END_SESSION after its sequence; a normal build of either is unchanged. Built with the library's
    #  full debug channels, as a user's -d build is: what the demos print is what is under test.
    demo-single)    BENCH_FILE="demo_single_motor.spin2"
                    PRECONDITION="MOTORS CONNECTED, WHEELS UP, RIGHT WHEEL FREE TO TURN, HANDS: NONE -- UNATTENDED, YOU DO NOTHING: the single-motor release demo on the RIGHT wheel (the P16 board); the left wheel is never started. The start checks pulse the motor leads with nothing able to move, then the wiring check TURNS THE RIGHT WHEEL A LITTLE FORWARD AND BACK (about 3.5 cm at the tyre). Then the right wheel runs FORWARD AT FULL POWER for 15 seconds, stops, runs IN REVERSE AT FULL POWER for 15 seconds, and stops; the program then waits 20 seconds with the wheel still and ends. It also starts its HDMI output on P8-P15, which the bench config does not use. About 1 minute"
                    ;;
    # doco-demo-<voltage> (task 3675) -- the Doco bench: the single-motor release demo on the DOCO BENCH's one motor (one DocoEng
    #  4k-rpm motor on the P16 board, which must read Rev A), built under -D BENCH_CFG -D BENCH_DOCO -D <the voltage's symbol>.
    #  One tier per Doco voltage, the voltage chosen by NAME in the tier (doco_voltage above): this bench has no voltage sensing,
    #  so the told voltage is the only source, and the precondition names it. A later harness tier adds its own labels the same way.
    doco-demo-v7p4|doco-demo-v11p1|doco-demo-v12p0|doco-demo-v14p8|doco-demo-v18p5|doco-demo-v22p2|doco-demo-v24p0)
                    BENCH_FILE="demo_single_motor.spin2"
                    DOCO_VNAME="${TIER#doco-demo-}"
                    DOCO_VINFO="$(doco_voltage "$DOCO_VNAME")" || die "unknown Doco voltage '$DOCO_VNAME' -- a voltage is chosen by NAME, one of: $DOCO_VOLTAGE_NAMES"
                    EXTRA_DEFS=(-D BENCH_DOCO -D "${DOCO_VINFO% *}")
                    PRECONDITION="THE DOCO BENCH, MOTOR CONNECTED AND FREE TO TURN, HANDS: NONE -- the single-motor release demo on the Doco bench's one motor (the P16 board, a Rev A -- THIS DEMO BUILD DOES NOT CHECK THE BOARD, the Doco harness will). THE DRIVE VOLTAGE IS TOLD, NOT SENSED: this build is told ${DOCO_VNAME} = ${DOCO_VINFO#* } mV (${DOCO_VINFO% *}); this bench has no pack sensor, so make sure the pack is that voltage. The start checks pulse the motor leads with nothing able to move, then the wiring check turns the motor a little forward and back, then it runs forward and in reverse at full power for 15 seconds each. About 1 minute"
                    ;;
    # single-hallmap-<voltage> (task 3679 phase 1, test_bench_single.spin2 SRC_REV 1) -- the Doco measurement harness's hall-map
    #  leg (L-hallmap) on the Doco bench: built under -D BENCH_CFG -D BENCH_DOCO -D <the voltage's symbol> (doco_voltage above, as
    #  doco-demo-<voltage> is), -D BENCH_QUIET for the motion harness's reason (nothing prints from the front cog), and the leg's
    #  part symbol -D SINGLE_PART_HALLMAP. It takes a clock NAME too, as every test_bench_single tier does (the check below).
    #  Phase 2 adds the other legs' part symbols and a tier that chains every hands-off leg in one command (doctrine P1).
    single-hallmap-v7p4|single-hallmap-v11p1|single-hallmap-v12p0|single-hallmap-v14p8|single-hallmap-v18p5|single-hallmap-v22p2|single-hallmap-v24p0)
                    BENCH_FILE="test_bench_single.spin2"
                    DOCO_VNAME="${TIER#single-hallmap-}"
                    DOCO_VINFO="$(doco_voltage "$DOCO_VNAME")" || die "unknown Doco voltage '$DOCO_VNAME' -- a voltage is chosen by NAME, one of: $DOCO_VOLTAGE_NAMES"
                    EXTRA_DEFS=(-D BENCH_QUIET -D BENCH_DOCO -D "${DOCO_VINFO% *}" -D SINGLE_PART_HALLMAP)
                    PRECONDITION="THE DOCO BENCH, MOTOR CONNECTED, ENCODER COUPLED TO ITS SHAFT, SHAFT FREE TO TURN, HANDS OFF -- UNATTENDED, YOU DO NOTHING: the Doco harness's hall map. It reads the board first and starts NOTHING unless it reads a Rev A. THE DRIVE VOLTAGE IS TOLD, NOT SENSED: this build is told ${DOCO_VNAME} = ${DOCO_VINFO#* } mV (${DOCO_VINFO% *}); this bench has no pack sensor, so set the supply to that voltage before the run. The start checks pulse the motor leads with nothing able to move; then the motor CRAWLS under a 2 A test current limit, in EIGHT SHORT DRIVES of two shaft revolutions each, stopping between them: two each way at 60 rpm, then two each way at 240 rpm. It stops itself on an over-current, a fault, a stall or an encoder that disagrees with the halls. About 1 minute"
                    ;;
    # single-<leg>-<voltage> and single-measure-<voltage> (task 3679 phase 2a, test_bench_single.spin2 SRC_REV 2) -- the Doco
    #  harness's hands-off measuring legs, each alone (one -D SINGLE_PART_* symbol) or all chained in one run (single-measure:
    #  the hall map, then every 2a leg, in the order the harness runs them -- doctrine P1, a command boundary only where he
    #  must act, and in these he never does). Built as single-hallmap-<voltage> is (-D BENCH_QUIET -D BENCH_DOCO -D <the
    #  voltage's symbol>); each takes a clock NAME. Every one's PRECONDITION opens with the same Doco-bench words.
    single-mininc-v7p4|single-mininc-v11p1|single-mininc-v12p0|single-mininc-v14p8|single-mininc-v18p5|single-mininc-v22p2|single-mininc-v24p0)
                    BENCH_FILE="test_bench_single.spin2"
                    DOCO_VNAME="${TIER#single-mininc-}"
                    DOCO_VINFO="$(doco_voltage "$DOCO_VNAME")" || die "unknown Doco voltage '$DOCO_VNAME' -- a voltage is chosen by NAME, one of: $DOCO_VOLTAGE_NAMES"
                    EXTRA_DEFS=(-D BENCH_QUIET -D BENCH_DOCO -D "${DOCO_VINFO% *}" -D SINGLE_PART_MININC)
                    PRECONDITION="THE DOCO BENCH, MOTOR CONNECTED, ENCODER COUPLED TO ITS SHAFT, SHAFT FREE TO TURN, HANDS OFF -- UNATTENDED, YOU DO NOTHING: the Doco harness. It reads the board first and starts NOTHING unless it reads a Rev A. THE DRIVE VOLTAGE IS TOLD, NOT SENSED: this build is told ${DOCO_VNAME} = ${DOCO_VINFO#* } mV (${DOCO_VINFO% *}); this bench has no pack sensor, so set the supply to that voltage before the run. The start checks pulse the motor leads with nothing able to move. It stops itself on an over-current, a charge it did not expect, an encoder that disagrees with the halls, or its time cap; a fault inside a leg is recorded and cleared, and the leg goes on. THE LEG: the slowest steady speed, each way. From rest the motor CRAWLS at a falling speed -- 60 rpm, then slower, down to under 2 rpm -- for 2 to 10 seconds a step, stopping between them, until one step does not turn smoothly; then the other way. Under a 2 A test current limit. About 2 minutes"
                    ;;
    single-ladder-v7p4|single-ladder-v11p1|single-ladder-v12p0|single-ladder-v14p8|single-ladder-v18p5|single-ladder-v22p2|single-ladder-v24p0)
                    BENCH_FILE="test_bench_single.spin2"
                    DOCO_VNAME="${TIER#single-ladder-}"
                    DOCO_VINFO="$(doco_voltage "$DOCO_VNAME")" || die "unknown Doco voltage '$DOCO_VNAME' -- a voltage is chosen by NAME, one of: $DOCO_VOLTAGE_NAMES"
                    EXTRA_DEFS=(-D BENCH_QUIET -D BENCH_DOCO -D "${DOCO_VINFO% *}" -D SINGLE_PART_LADDER)
                    PRECONDITION="THE DOCO BENCH, MOTOR CONNECTED, ENCODER COUPLED TO ITS SHAFT, SHAFT FREE TO TURN, HANDS OFF -- UNATTENDED, YOU DO NOTHING: the Doco harness. It reads the board first and starts NOTHING unless it reads a Rev A. THE DRIVE VOLTAGE IS TOLD, NOT SENSED: this build is told ${DOCO_VNAME} = ${DOCO_VINFO#* } mV (${DOCO_VINFO% *}); this bench has no pack sensor, so set the supply to that voltage before the run. The start checks pulse the motor leads with nothing able to move. It stops itself on an over-current, a charge it did not expect, an encoder that disagrees with the halls, or its time cap; a fault inside a leg is recorded and cleared, and the leg goes on. THE LEG: the speed ladder, each way. The motor SPINS UP to a quarter, a half, three quarters and all of this voltage's top speed (and, from 12 V up, two steps more, never past about 2,800 rpm), each time from rest and back to rest, holding each speed about 6 seconds; then climbs the same steps one after another without stopping, and stops. Up to about 3,600 rpm (11.1 V). Under a 2 A test current limit (3 A at 11.1 V). About 5 minutes"
                    ;;
    single-ramp-v7p4|single-ramp-v11p1|single-ramp-v12p0|single-ramp-v14p8|single-ramp-v18p5|single-ramp-v22p2|single-ramp-v24p0)
                    BENCH_FILE="test_bench_single.spin2"
                    DOCO_VNAME="${TIER#single-ramp-}"
                    DOCO_VINFO="$(doco_voltage "$DOCO_VNAME")" || die "unknown Doco voltage '$DOCO_VNAME' -- a voltage is chosen by NAME, one of: $DOCO_VOLTAGE_NAMES"
                    EXTRA_DEFS=(-D BENCH_QUIET -D BENCH_DOCO -D "${DOCO_VINFO% *}" -D SINGLE_PART_RAMP)
                    PRECONDITION="THE DOCO BENCH, MOTOR CONNECTED, ENCODER COUPLED TO ITS SHAFT, SHAFT FREE TO TURN, HANDS OFF -- UNATTENDED, YOU DO NOTHING: the Doco harness. It reads the board first and starts NOTHING unless it reads a Rev A. THE DRIVE VOLTAGE IS TOLD, NOT SENSED: this build is told ${DOCO_VNAME} = ${DOCO_VINFO#* } mV (${DOCO_VINFO% *}); this bench has no pack sensor, so set the supply to that voltage before the run. The start checks pulse the motor leads with nothing able to move. It stops itself on an over-current, a charge it did not expect, an encoder that disagrees with the halls, or its time cap; a fault inside a leg is recorded and cleared, and the leg goes on. THE LEG: the built-in speed-up and stop. From rest the motor SPINS UP to this voltage's top speed (4 to 9 seconds), holds it 2 seconds, and slows to a stop (3 to 6 seconds); one way, then the other; then at the top it REVERSES STRAIGHT THROUGH ZERO to the top the other way, and back again, and stops. Under a 2 A test current limit. About 1.5 minutes"
                    ;;
    single-stops-v7p4|single-stops-v11p1|single-stops-v12p0|single-stops-v14p8|single-stops-v18p5|single-stops-v22p2|single-stops-v24p0)
                    BENCH_FILE="test_bench_single.spin2"
                    DOCO_VNAME="${TIER#single-stops-}"
                    DOCO_VINFO="$(doco_voltage "$DOCO_VNAME")" || die "unknown Doco voltage '$DOCO_VNAME' -- a voltage is chosen by NAME, one of: $DOCO_VOLTAGE_NAMES"
                    EXTRA_DEFS=(-D BENCH_QUIET -D BENCH_DOCO -D "${DOCO_VINFO% *}" -D SINGLE_PART_STOPS)
                    PRECONDITION="THE DOCO BENCH, MOTOR CONNECTED, ENCODER COUPLED TO ITS SHAFT, SHAFT FREE TO TURN, HANDS OFF -- UNATTENDED, YOU DO NOTHING: the Doco harness. It reads the board first and starts NOTHING unless it reads a Rev A. THE DRIVE VOLTAGE IS TOLD, NOT SENSED: this build is told ${DOCO_VNAME} = ${DOCO_VINFO#* } mV (${DOCO_VINFO% *}); this bench has no pack sensor, so set the supply to that voltage before the run. The start checks pulse the motor leads with nothing able to move. It stops itself on an over-current, a charge it did not expect, an encoder that disagrees with the halls, or its time cap; a fault inside a leg is recorded and cleared, and the leg goes on. THE LEG: the stop limits. Twelve drives, each stopping itself on a limit set before it starts: at this voltage's top speed for 300 and 400 shaft turns and for 15 seconds, and at a crawl for 1 and 5 turns and for 3 seconds; one way, then the other. Under a 2 A test current limit. About 2.5 minutes"
                    ;;
    # single-coast-<voltage>, single-offscan-<voltage>, single-passprobe-<voltage> (task 3679 phase 2b, test_bench_single.spin2
    #  SRC_REV 3) -- the coast-down (L1) and the offset scan (L3) drive only at the 12 V and 24 V rows the analysis names, so
    #  their tiers exist at v12p0 and v24p0 only (the harness prints B1-LEGSKIP and drives nothing at another row, as it does
    #  inside single-measure); the pass-period probe (plan sec 1.4) at every voltage, and like every Doco tier it takes a clock
    #  NAME: the D1 sheet runs it once per clock name at one voltage, and a pack carries each as <tier>@<clock>.bin.
    single-coast-v12p0|single-coast-v24p0)
                    BENCH_FILE="test_bench_single.spin2"
                    DOCO_VNAME="${TIER#single-coast-}"
                    DOCO_VINFO="$(doco_voltage "$DOCO_VNAME")" || die "unknown Doco voltage '$DOCO_VNAME' -- a voltage is chosen by NAME, one of: $DOCO_VOLTAGE_NAMES"
                    EXTRA_DEFS=(-D BENCH_QUIET -D BENCH_DOCO -D "${DOCO_VINFO% *}" -D SINGLE_PART_COAST)
                    PRECONDITION="THE DOCO BENCH, MOTOR CONNECTED, ENCODER COUPLED TO ITS SHAFT, SHAFT FREE TO TURN, HANDS OFF -- UNATTENDED, YOU DO NOTHING: the Doco harness. It reads the board first and starts NOTHING unless it reads a Rev A. THE DRIVE VOLTAGE IS TOLD, NOT SENSED: this build is told ${DOCO_VNAME} = ${DOCO_VINFO#* } mV (${DOCO_VINFO% *}); this bench has no pack sensor, so set the supply to that voltage before the run. The start checks pulse the motor leads with nothing able to move. It stops itself on an over-current, a charge it did not expect, an encoder that disagrees with the halls, or its time cap. THE LEG: the coast-down. The motor SPINS UP to a quarter, a half and all of this voltage's top speed, each way; at each speed, after a few seconds, the program CUTS THE DRIVE ON PURPOSE (a fault it makes itself) and the motor COASTS FREELY TO A STOP, in under a second; then it is reset and the next speed starts from rest. Six coasts. Up to about 2,600 rpm. Under a 2 A test current limit. About 1.5 minutes"
                    ;;
    single-offscan-v12p0|single-offscan-v24p0)
                    BENCH_FILE="test_bench_single.spin2"
                    DOCO_VNAME="${TIER#single-offscan-}"
                    DOCO_VINFO="$(doco_voltage "$DOCO_VNAME")" || die "unknown Doco voltage '$DOCO_VNAME' -- a voltage is chosen by NAME, one of: $DOCO_VOLTAGE_NAMES"
                    EXTRA_DEFS=(-D BENCH_QUIET -D BENCH_DOCO -D "${DOCO_VINFO% *}" -D SINGLE_PART_OFFSCAN)
                    PRECONDITION="THE DOCO BENCH, MOTOR CONNECTED, ENCODER COUPLED TO ITS SHAFT, SHAFT FREE TO TURN, HANDS OFF -- UNATTENDED, YOU DO NOTHING: the Doco harness. It reads the board first and starts NOTHING unless it reads a Rev A. THE DRIVE VOLTAGE IS TOLD, NOT SENSED: this build is told ${DOCO_VNAME} = ${DOCO_VINFO#* } mV (${DOCO_VINFO% *}); this bench has no pack sensor, so set the supply to that voltage before the run. The start checks pulse the motor leads with nothing able to move. It stops itself on an over-current, a charge it did not expect, an encoder that disagrees with the halls, or its time cap; a fault inside the leg is recorded and cleared, and the leg goes on. THE LEG: the motor timing scan. At a quarter, a half and all of this voltage's top speed, each way, the motor runs while the program shifts its timing a little at a time, holding each setting about 6 seconds; the motor may sound rougher or hunt at some settings, which is what is being measured. Twelve runs from rest, each about 50 seconds. Up to about 2,600 rpm. Under a 2 A test current limit. The motor's own timing is put back at the end, whatever happens. About 11 minutes"
                    ;;
    single-passprobe-v7p4|single-passprobe-v11p1|single-passprobe-v12p0|single-passprobe-v14p8|single-passprobe-v18p5|single-passprobe-v22p2|single-passprobe-v24p0)
                    BENCH_FILE="test_bench_single.spin2"
                    DOCO_VNAME="${TIER#single-passprobe-}"
                    DOCO_VINFO="$(doco_voltage "$DOCO_VNAME")" || die "unknown Doco voltage '$DOCO_VNAME' -- a voltage is chosen by NAME, one of: $DOCO_VOLTAGE_NAMES"
                    EXTRA_DEFS=(-D BENCH_QUIET -D BENCH_DOCO -D "${DOCO_VINFO% *}" -D SINGLE_PART_PASSPROBE)
                    PRECONDITION="THE DOCO BENCH, MOTOR CONNECTED, ENCODER COUPLED TO ITS SHAFT, SHAFT FREE TO TURN, HANDS OFF -- UNATTENDED, YOU DO NOTHING: the Doco harness. It reads the board first and starts NOTHING unless it reads a Rev A. THE DRIVE VOLTAGE IS TOLD, NOT SENSED: this build is told ${DOCO_VNAME} = ${DOCO_VINFO#* } mV (${DOCO_VINFO% *}); this bench has no pack sensor, so set the supply to that voltage before the run. The start checks pulse the motor leads with nothing able to move. It stops itself on an over-current, a charge it did not expect, an encoder that disagrees with the halls, or its time cap. THE LEG: the drive's timing at this build's clock. The motor runs at half of this voltage's top speed for 10 seconds one way, stops, then 10 seconds the other way, and stops. Under a 2 A test current limit. Under a minute"
                    ;;
    single-measure-v7p4|single-measure-v11p1|single-measure-v12p0|single-measure-v14p8|single-measure-v18p5|single-measure-v22p2|single-measure-v24p0)
                    BENCH_FILE="test_bench_single.spin2"
                    DOCO_VNAME="${TIER#single-measure-}"
                    DOCO_VINFO="$(doco_voltage "$DOCO_VNAME")" || die "unknown Doco voltage '$DOCO_VNAME' -- a voltage is chosen by NAME, one of: $DOCO_VOLTAGE_NAMES"
                    EXTRA_DEFS=(-D BENCH_QUIET -D BENCH_DOCO -D "${DOCO_VINFO% *}" -D SINGLE_PART_HALLMAP -D SINGLE_PART_MININC -D SINGLE_PART_LADDER -D SINGLE_PART_RAMP -D SINGLE_PART_STOPS -D SINGLE_PART_COAST -D SINGLE_PART_OFFSCAN -D SINGLE_PART_PASSPROBE)
                    # the coast-down and the timing scan drive only at 12 V and 24 V: the run is ~25 minutes there, ~13 elsewhere
                    DOCO_MEASURE_TIME="About 13 minutes"
                    case "$DOCO_VNAME" in v12p0|v24p0) DOCO_MEASURE_TIME="About 25 minutes: at this voltage it also coasts the motor down six times (it CUTS THE DRIVE ON PURPOSE and the motor coasts freely to a stop) and runs the motor timing scan (the motor may sound rougher or hunt at some settings; its own timing is put back at the end)" ;; esac
                    PRECONDITION="THE DOCO BENCH, MOTOR CONNECTED, ENCODER COUPLED TO ITS SHAFT, SHAFT FREE TO TURN, HANDS OFF -- UNATTENDED, YOU DO NOTHING: the Doco harness. It reads the board first and starts NOTHING unless it reads a Rev A. THE DRIVE VOLTAGE IS TOLD, NOT SENSED: this build is told ${DOCO_VNAME} = ${DOCO_VINFO#* } mV (${DOCO_VINFO% *}); this bench has no pack sensor, so set the supply to that voltage before the run. The start checks pulse the motor leads with nothing able to move. It stops itself on an over-current, a charge it did not expect, an encoder that disagrees with the halls, or its time cap; a fault inside a leg is recorded and cleared, and the leg goes on. EVERY HANDS-OFF LEG, ONE AFTER ANOTHER, NOTHING BETWEEN THEM FOR YOU TO DO: the hall map (eight short crawls), the slowest steady speed (crawls, each way), the speed ladder (spin-ups to a quarter, half, three quarters and all of the top speed and, from 12 V up, two steps more, each held about 6 seconds, each way), the built-in speed-up and stop (each way, then a reversal straight through zero at the top), the stop limits (twelve drives that stop themselves), and the drive's timing (half speed, 10 seconds each way). Up to about 3,600 rpm (11.1 V). Under a 2 A test current limit (3 A for the ladder at 11.1 V). ${DOCO_MEASURE_TIME}"
                    ;;
    # single-qualify-<voltage> (task 3686, test_bench_single.spin2 SRC_REV 5) -- the D2 QUALIFICATION (plan sec 7) at every
    #  Doco voltage: the hands-off qualification legs chained in one run -- L-wiring (the public start path and checkWiring(),
    #  R23-SGL-START), L-power (driveAtPower() rungs on the encoder, R23-SGL-POWER), the ladder (FOLLOW, MISDIAL, SMOOTH,
    #  TOPSPD), the ramp (RAMPARR, SMOOTH, TOPSPD) and the stop limits (STOPROT, STOPTIME) -- under -D SINGLE_QUALIFY, which
    #  builds the misdial check on the fitted Ke (KE_FITTED_MV_PER_KRPM, set from D1's evaluation before the D2 pack is
    #  built: arbiter decision D5). The hand-load qualification at 12 V and 24 V is single-handload and single-heldpush,
    #  reused, never duplicated here (doctrine overlay P1: a command boundary goes where he acts). Takes a clock NAME.
    single-qualify-v7p4|single-qualify-v11p1|single-qualify-v12p0|single-qualify-v14p8|single-qualify-v18p5|single-qualify-v22p2|single-qualify-v24p0)
                    BENCH_FILE="test_bench_single.spin2"
                    DOCO_VNAME="${TIER#single-qualify-}"
                    DOCO_VINFO="$(doco_voltage "$DOCO_VNAME")" || die "unknown Doco voltage '$DOCO_VNAME' -- a voltage is chosen by NAME, one of: $DOCO_VOLTAGE_NAMES"
                    EXTRA_DEFS=(-D BENCH_QUIET -D BENCH_DOCO -D "${DOCO_VINFO% *}" -D SINGLE_QUALIFY -D SINGLE_PART_WIRING -D SINGLE_PART_POWER -D SINGLE_PART_LADDER -D SINGLE_PART_RAMP -D SINGLE_PART_STOPS)
                    PRECONDITION="THE DOCO BENCH, MOTOR CONNECTED, ENCODER COUPLED TO ITS SHAFT, SHAFT FREE TO TURN, HANDS OFF -- UNATTENDED, YOU DO NOTHING: the Doco harness's D2 QUALIFICATION. It reads the board first and starts NOTHING unless it reads a Rev A. THE DRIVE VOLTAGE IS TOLD, NOT SENSED: this build is told ${DOCO_VNAME} = ${DOCO_VINFO#* } mV (${DOCO_VINFO% *}); this bench has no pack sensor, so set the supply to that voltage before the run. The start checks pulse the motor leads with nothing able to move. It stops itself on an over-current, a charge it did not expect, an encoder that disagrees with the halls, a wiring check that does not pass, or its time cap; a fault inside a leg is recorded and cleared, and the leg goes on. EVERY HANDS-OFF CHECK, ONE AFTER ANOTHER, NOTHING BETWEEN THEM FOR YOU TO DO: the wiring check (the motor turns a little one way and back, about a quarter turn each way); the power steps (the motor spins up by power to a quarter, half, three quarters and all of this voltage's top speed, each from rest, each held about 6 seconds, one way then the other); the speed ladder (as single-ladder: each step from rest and then one after another, each way); the built-in speed-up and stop (each way, then a reversal straight through zero at the top); and the stop limits (twelve drives that stop themselves). Up to about 3,600 rpm (11.1 V). Under a 2 A test current limit (3 A for the power steps and the ladder at 11.1 V). About 12 minutes"
                    ;;
    # single-handload-<voltage>, single-heldpush-<voltage>, single-sag-<voltage>, single-pinch-<voltage> (task 3679 phase 2c,
    #  test_bench_single.spin2 SRC_REV 4) -- the Doco harness's ATTENDED legs, each its own tier and never in single-measure (a
    #  command boundary goes where Stephen acts, doctrine overlay P1). Built as the other Doco tiers are, with the leg's own
    #  -D SINGLE_PART_* symbol, which also builds the operator panel sgpanel (src/sg_*.bmp, tools/gen_single_assets.py; the pack
    #  reads their names from the binary and carries them beside it). Only the voltages the analysis names
    #  (DOCs/analyses/DOCO-DESK-MODEL-2026-10-03.md sec 8): L5 and L6 at 12 V and 24 V, L4 at 22.2 V and 18.5 V, L2b at 18.5 V.
    #  L4 and L2b are OPTIONAL (arbiter decision D4): the run sheet asks Stephen before they are relied on.
    single-handload-v12p0|single-handload-v24p0)
                    BENCH_FILE="test_bench_single.spin2"
                    DOCO_VNAME="${TIER#single-handload-}"
                    DOCO_VINFO="$(doco_voltage "$DOCO_VNAME")" || die "unknown Doco voltage '$DOCO_VNAME' -- a voltage is chosen by NAME, one of: $DOCO_VOLTAGE_NAMES"
                    EXTRA_DEFS=(-D BENCH_QUIET -D BENCH_DOCO -D "${DOCO_VINFO% *}" -D SINGLE_PART_HANDLOAD)
                    DOCO_HAND_STEPS="TWO STEPS: the 4 A limit, then the 2 A limit -- never the default limits at this voltage"
                    case "$DOCO_VNAME" in v12p0) DOCO_HAND_STEPS="THREE STEPS: the 4 A limit, the 2 A limit, then -- only if the charge left in the test allows it, and the panel says when it does not -- the default limits, briefly: a much stronger push (about 120 mN.m) and a hum for about a second" ;; esac
                    PRECONDITION="THE DOCO BENCH, MOTOR CONNECTED, ENCODER COUPLED TO ITS SHAFT, SHAFT FREE TO TURN -- ATTENDED AT THE PC: A PANEL OPENS AND YOU CLICK ITS BUTTONS (NO KEYS ARE READ). THE HAND LOAD. It reads the board first and starts NOTHING unless it reads a Rev A. THE DRIVE VOLTAGE IS TOLD, NOT SENSED: this build is told ${DOCO_VNAME} = ${DOCO_VINFO#* } mV (${DOCO_VINFO% *}); this bench has no pack sensor, so set the supply to that voltage before the run. The start checks pulse the motor leads with nothing able to move. ${DOCO_HAND_STEPS}. EACH STEP: the panel says what comes and what you should feel; nothing turns until you click START STEP. Then the shaft turns slowly by itself (about 200 rpm); when the green YOUR TURN banner shows, slow the shaft by hand until it stops, and hold it still. About a second after it stops, the drive stops itself and the panel says so; let go. A steady push of about 60 to 80 mN.m at the test limits. STOP MOTOR on the panel stops the shaft at any time. The result stays on the panel until you click NEXT STEP or REDO STEP. It stops itself on an over-current, a charge it did not expect or its time cap. About 5 minutes, at your pace"
                    ;;
    single-heldpush-v12p0|single-heldpush-v24p0)
                    BENCH_FILE="test_bench_single.spin2"
                    DOCO_VNAME="${TIER#single-heldpush-}"
                    DOCO_VINFO="$(doco_voltage "$DOCO_VNAME")" || die "unknown Doco voltage '$DOCO_VNAME' -- a voltage is chosen by NAME, one of: $DOCO_VOLTAGE_NAMES"
                    EXTRA_DEFS=(-D BENCH_QUIET -D BENCH_DOCO -D "${DOCO_VINFO% *}" -D SINGLE_PART_HELDPUSH)
                    PRECONDITION="THE DOCO BENCH, MOTOR CONNECTED, ENCODER COUPLED TO ITS SHAFT -- ATTENDED AT THE PC: A PANEL OPENS AND YOU CLICK ITS BUTTONS (NO KEYS ARE READ). THE HELD STOP: THE MOTOR NEVER TURNS BY ITSELF IN THIS TEST. It reads the board first and starts NOTHING unless it reads a Rev A. THE DRIVE VOLTAGE IS TOLD, NOT SENSED: this build is told ${DOCO_VNAME} = ${DOCO_VINFO#* } mV (${DOCO_VINFO% *}); set the supply to that voltage before the run. The start checks pulse the motor leads with nothing able to move. TWO STEPS: after you click START STEP the stopped motor holds the shaft where it is; when the green YOUR TURN banner shows, turn the shaft slowly by hand, about a twelfth of a turn, until the hold gives way, then let go -- step 1 either way, step 2 the other way. You should feel almost nothing for up to 15 degrees, then a light push back (about 20 to 45 mN.m) that firms up in a quarter second, then it gives way and drags. The panel sees you let go and shows the result until you click NEXT STEP or REDO STEP. About 2 minutes, at your pace"
                    ;;
    single-sag-v22p2|single-sag-v18p5)
                    BENCH_FILE="test_bench_single.spin2"
                    DOCO_VNAME="${TIER#single-sag-}"
                    DOCO_VINFO="$(doco_voltage "$DOCO_VNAME")" || die "unknown Doco voltage '$DOCO_VNAME' -- a voltage is chosen by NAME, one of: $DOCO_VOLTAGE_NAMES"
                    EXTRA_DEFS=(-D BENCH_QUIET -D BENCH_DOCO -D "${DOCO_VINFO% *}" -D SINGLE_PART_SAG)
                    DOCO_SAG_WHAT="at 18.5 V the speed should slip away near 8 V with no fault"
                    case "$DOCO_VNAME" in v22p2) DOCO_SAG_WHAT="at 22.2 V the drive should FAULT and stop by itself somewhere between about 18 V and 10 V, without slowing first (it runs this voltage's full shipped top, 3,140 rpm, on purpose)" ;; esac
                    PRECONDITION="OPTIONAL -- RUN IT ONLY IF YOU AGREED TO IT ON THE RUN SHEET. THE DOCO BENCH, MOTOR CONNECTED, ENCODER COUPLED TO ITS SHAFT, SHAFT FREE TO TURN, HANDS OFF THE SHAFT -- ATTENDED AT THE PC AND THE SUPPLY: A PANEL OPENS AND YOU CLICK ITS BUTTONS (NO KEYS ARE READ). THE SUPPLY SAG. It reads the board first and starts NOTHING unless it reads a Rev A. THE DRIVE VOLTAGE IS TOLD, NOT SENSED: this build is told ${DOCO_VNAME} = ${DOCO_VINFO#* } mV (${DOCO_VINFO% *}); set the supply to that voltage before the run. ONE STEP: after START STEP the motor speeds up to this voltage's top speed; when the green YOUR TURN banner shows, turn the bench supply down slowly, about 1 V a second, until the panel says the speed is lost; ${DOCO_SAG_WHAT}. The program then stops the motor, and the panel asks you to turn the supply back up to ${DOCO_VINFO#* } mV and click DONE. STOP MOTOR on the panel stops it at any time. About 1 minute"
                    ;;
    single-pinch-v18p5)
                    BENCH_FILE="test_bench_single.spin2"
                    DOCO_VNAME="${TIER#single-pinch-}"
                    DOCO_VINFO="$(doco_voltage "$DOCO_VNAME")" || die "unknown Doco voltage '$DOCO_VNAME' -- a voltage is chosen by NAME, one of: $DOCO_VOLTAGE_NAMES"
                    EXTRA_DEFS=(-D BENCH_QUIET -D BENCH_DOCO -D "${DOCO_VINFO% *}" -D SINGLE_PART_PINCH)
                    PRECONDITION="OPTIONAL -- RUN IT ONLY IF YOU AGREED TO IT ON THE RUN SHEET. THE DOCO BENCH, MOTOR CONNECTED, ENCODER COUPLED TO ITS SHAFT, THE OTHER SHAFT END BARE AND REACHABLE -- ATTENDED AT THE PC: A PANEL OPENS AND YOU CLICK ITS BUTTONS (NO KEYS ARE READ). THE CLOTH PINCH. It reads the board first and starts NOTHING unless it reads a Rev A. THE DRIVE VOLTAGE IS TOLD, NOT SENSED: this build is told ${DOCO_VNAME} = ${DOCO_VINFO#* } mV (${DOCO_VINFO% *}); set the supply to that voltage before the run. ONE STEP: after START STEP the motor speeds up to this voltage's top speed (about 2,660 rpm) and runs 2 seconds untouched; when the green YOUR TURN banner shows, pinch the bare shaft end lightly with a cloth for 1 to 2 seconds, let go, and click DONE. You should feel a light drag and see no slowing; the panel shows the current rise and fall. STOP MOTOR on the panel stops it at any time. Under a minute"
                    ;;
    # doco-adopt-<voltage> and adopt-wheel (task 3685, plan sec 8, util_adopt_motor.spin2 TOOL_REV 1) -- the motor-adoption tool,
    #  the SAME source a user compiles under isp_bldc_motor_userconfig.spin2, here built under the bench's statement: on the Doco
    #  bench (-D BENCH_DOCO and the voltage's symbol, as every Doco tier) and on the 6.5in platform's RIGHT wheel (the bench
    #  statement's RIGHT_* values, as demo-single), both -D BENCH_QUIET for the motion harness's reason (nothing prints from the
    #  front cog). The tool reads no encoder: on the Doco bench the harness's legs (single-offscan, single-ladder) are its
    #  judge. Both take a clock NAME (plan sec 0.2: the 6.5in session runs the tool at the lowest supported clock and at 270 MHz).
    doco-adopt-v7p4|doco-adopt-v11p1|doco-adopt-v12p0|doco-adopt-v14p8|doco-adopt-v18p5|doco-adopt-v22p2|doco-adopt-v24p0)
                    BENCH_FILE="util_adopt_motor.spin2"
                    DOCO_VNAME="${TIER#doco-adopt-}"
                    DOCO_VINFO="$(doco_voltage "$DOCO_VNAME")" || die "unknown Doco voltage '$DOCO_VNAME' -- a voltage is chosen by NAME, one of: $DOCO_VOLTAGE_NAMES"
                    EXTRA_DEFS=(-D BENCH_QUIET -D BENCH_DOCO -D "${DOCO_VINFO% *}")
                    PRECONDITION="THE DOCO BENCH, MOTOR CONNECTED, SHAFT FREE TO TURN, HANDS OFF -- UNATTENDED, YOU DO NOTHING: the motor-adoption tool, run as a user runs it (the encoder may stay coupled; the tool does not read it). THE DRIVE VOLTAGE IS TOLD, NOT SENSED: this build is told ${DOCO_VNAME} = ${DOCO_VINFO#* } mV (${DOCO_VINFO% *}); this bench has no pack sensor, so set the supply to that voltage before the run. It finds the DocoEng motor's record first and starts nothing without one. The start checks pulse the motor leads with nothing able to move. THE TIMING SCAN: at 560 rpm and then at 1,120 rpm, each way, the motor runs while the tool shifts its timing 5 degrees at a time, each side from rest, holding each setting about 6 seconds, until the current climbs, the motor slows, hunts or faults; the motor may sound rougher or hunt near the ends, which is what is being found. Its own timing is put back. THE CEILING: each way, from rest the motor climbs from 280 rpm in 140 rpm steps, about 9 seconds a step, never past about 2,660 rpm, until its duty reaches the reserve or the motor slows, hunts or faults; then it stops. Under a 2 A test current limit (3 A for the climb). It stops itself on an over-current, a charge it did not expect, a fault that will not clear or its time cap. 15 to 30 minutes"
                    ;;
    adopt-wheel)    BENCH_FILE="util_adopt_motor.spin2"
                    EXTRA_DEFS=(-D BENCH_QUIET)
                    PRECONDITION="THE REV B PLATFORM, MOTORS CONNECTED, WHEELS UP, RIGHT WHEEL FREE TO TURN, HANDS OFF -- UNATTENDED, YOU DO NOTHING: the motor-adoption tool on the RIGHT wheel (the P16 board), run as a user runs it; the left wheel is never started. It finds the 6.5in motor's record first and starts nothing without one. The start checks pulse the motor leads with nothing able to move. THE TIMING SCAN: at 33 rpm and then at 65 rpm, each way, the wheel turns while the tool shifts its timing 5 degrees at a time, each side from rest, holding each setting about 6 seconds, until the current climbs, the wheel slows or faults; its own timing is put back. THE CEILING: each way, from rest the wheel climbs from 30 rpm in 15 rpm steps, about 9 seconds a step, never past 435 rpm, until its duty reaches the reserve or the wheel slows or faults; then it stops. Under a 4 A test current limit; the 10 A abort applies. It stops itself on an over-current, a charge it did not expect, a fault that will not clear or its time cap. 15 to 30 minutes"
                    ;;
    demo-rc)        BENCH_FILE="demo_dual_motor_rc.spin2"
                    PRECONDITION="ATTENDED -- YOU DRIVE IT WITH THE FLYSKY TRANSMITTER: the SBUS receiver wired to P58 and bound, the transmitter ON with swD (the kill switch) in its run position BEFORE the load. The two-wheel RC demo, as shipped: start checks, the wiring check (each wheel turns a little one way and back), then the sticks drive the platform and every event and stop is printed as it happens. Drive forward, reverse and both turns at low and full stick; flip swD to e-stop, then back to re-arm. It runs until you close the terminal. About 3 minutes, at your pace"
                    ;;
    # floor-rc (test_bench_rc.spin2, SRC_REV 4) -- the RC demo's control loop, unchanged, driven ON THE FLOOR, with a
    #  logger cog streaming both wheels' state at 25 Hz (RC-TEL) and every drive event (RC-EVT), so the log shows any
    #  erratic handling. -D BENCH_QUIET for the motion harness's reason (I5): nothing may print from the steering front
    #  cog or the drivers, and the quiet masks compile out every debug() the front cog could reach. Its DEBUG footprint
    #  is gated like every tier's, by build-check.sh's measure-only walk of this table.
    floor-rc)       BENCH_FILE="test_bench_rc.spin2"
                    EXTRA_DEFS=(-D BENCH_QUIET)
                    PRECONDITION="PLATFORM ON THE FLOOR, WHEELS DOWN, SPACE CLEAR -- ATTENDED: YOU DRIVE IT WITH THE FLYSKY TRANSMITTER. BEFORE THE LOAD: the SBUS receiver wired to P58 and bound; the transmitter ON with swD (the kill switch) in its run position, and swC NOT down (swC down ends the run). The RC demo's own control loop: the start checks, the wiring check (each wheel turns a little one way and back -- on the floor the platform twists a little in place), then swA down lets the sticks drive: right stick up/down is speed, left stick left/right is direction. Drive the roster at your pace: spins left and right; forward and back; rapid and slow speed-ups; the stick straight from forward to reverse; centring the stick from full speed; swD to e-stop at speed, then back up to re-arm; turning while moving; crawling. THE KNOBS: VRA sets how fast it speeds up (200-3,000 mm/s^2) and VRB how fast it slows and stops (1,000-3,000 mm/s^2; at the gentle end a stop from full speed rolls about 2 m) -- try each end of each. YOUR MARKER: flip swB whenever something feels or sounds odd; the log records the moment. Every event and stop prints as it happens, and a telemetry line (RC-TEL) prints 25 times a second throughout. It runs until you close the terminal; or flip swC down, and the program ends and closes the terminal itself"
                    ;;
    demo-dual)      BENCH_FILE="demo_dual_motor.spin2"
                    PRECONDITION="MOTORS CONNECTED, WHEELS UP, BOTH WHEELS FREE TO TURN, HANDS: NONE -- UNATTENDED, YOU DO NOTHING: the two-wheel release demo. The start checks pulse each motor's leads with nothing able to move, then the wiring check TURNS EACH WHEEL A LITTLE ONE WAY AND BACK, the two opposite ways (about 3.5 cm at the tyre). Then: BOTH WHEELS FORWARD for 1 ft of tyre travel (about a second); BOTH WHEELS at power 80 steering one way for 15 seconds (one wheel faster than the other), then the other way for 15 seconds; then THE LEFT WHEEL ALONE AT FULL POWER for 15 seconds, then THE RIGHT WHEEL ALONE AT FULL POWER for 15 seconds, the other wheel still each time. Each drive ends on its own limit; the wheels coast at rest. About 1.5 minutes, at most about 2"
                    ;;
    *)  echo "ERROR: unknown tier '$TIER'" >&2
        usage
        ;;
esac

# a clock name belongs only to the tops that judge a clock (test_bench_dual's CLOCK part and test_bench_t0); any other
# tier's source is never patched, so a name beside it would run at the file's own clock while saying otherwise
if [ -n "$CLOCK_NAME" ]; then
    case "$BENCH_FILE" in
        test_bench_dual.spin2|test_bench_t0.spin2|test_bench_single.spin2|util_adopt_motor.spin2) ;;   # test_bench_single: the Doco harness (task 3679); util_adopt_motor: the adoption tool (task 3685)
        *) die "tier '$TIER' (top $BENCH_FILE) takes no clock: a clock name is for the tiers of test_bench_dual.spin2, test_bench_t0.spin2, the Doco harness test_bench_single.spin2 and the adoption tool util_adopt_motor.spin2" ;;
    esac
fi
# A prebuilt package and a pack build hold one binary per tier name, its clock built in: <tier>.bin. A tier built at a NAMED
# clock is <tier>@<clock>.bin (task 3675, for Visit D1's per-clock pass-period probe): the pack builder stores it, and the
# packaged runner given the same clock name picks it. No number is typed there either, and a package never compiles one.
PACK_KEY="$TIER"
[ -n "$CLOCK_FROM_ARG" ] && PACK_KEY="$TIER@$CLOCK_FROM_ARG"

# ---- sanity checks ----------------------------------------------------------
# command -v, not [ -x ] -- these are PATH names, not paths, and -x on a bare
# name tests a file in the current directory.
if [ -n "$PREBUILT" ] && { [ -n "$MEASURE_ONLY" ] || [ -n "$PACK_DIR" ]; }; then
    die "this is a prebuilt package: it runs its binaries and builds none (BENCH_MEASURE_ONLY / BENCH_PACK_DIR belong to the source tree)"
fi
if [ -n "$PREBUILT" ]; then
    PACK_BIN="$PACK_KEY.bin"
    if [ ! -f "$SCRIPT_DIR/$PACK_BIN" ]; then
        die "this package has no binary for tier '$TIER'${CLOCK_FROM_ARG:+ at clock '$CLOCK_FROM_ARG'} (looked for $PACK_BIN). It carries: $(cd "$SCRIPT_DIR" 2>/dev/null && ls *.bin 2>/dev/null | sed 's/\.bin$//' | tr '\n' ' ')"
    fi
    # Every file this binary loads at run time (a panel's LAYER bitmaps, loaded by bare name) must
    #  be beside it: BENCH-PACKAGE lists them, read from the binary when the pack was built. A missing one is a blank
    #  panel and a lost visit (2026-09-29), so it refuses here, before anything moves.
    for asset in $(sed -n "s/^asset $PACK_KEY //p" "$PACKAGE_FILE"); do
        [ -f "$SCRIPT_DIR/$asset" ] || die "tier '$TIER' loads '$asset' at run time and it is not in this package folder -- its panel would draw nothing. Unzip the whole package again."
    done
elif ! command -v "$PNUT" >/dev/null 2>&1; then
    echo "ERROR: '$PNUT' not found on PATH (override with PNUT_TS=/path/to/pnut-ts)" >&2
    exit 2
fi

if [ -z "$MEASURE_ONLY" ] && [ -z "$PACK_DIR" ] && ! command -v "$PNUT_TERM" >/dev/null 2>&1; then
    echo "ERROR: '$PNUT_TERM' not found on PATH (override with PNUT_TERM_TS=/path/to/pnut-term-ts)" >&2
    exit 2
fi

if [ -n "$PRECONDITION" ] && [ -z "$MEASURE_ONLY" ] && [ -z "$PACK_DIR" ]; then
    echo ""
    echo "  ****************************************************************"
    echo "  ** $PRECONDITION"
    echo "  ** PANIC PROCEDURE IS PHYSICAL BATTERY DISCONNECT ONLY."
    echo "  ** No operator control can stop a runaway: the harness holds every stop."
    echo "  ** (Finding S-4: emergencyCutoff() used to self-cancel in ~125-250 ms. Task"
    echo "  **  3556 made the latch hold until clearEmergency(), which dual-d certifies --"
    echo "  **  it is still not a panic button, because nothing reaches it but the harness.)"
    echo "  ****************************************************************"
    echo ""
fi

echo "bench-run.sh: cd $SRC_DIR"
cd "$SRC_DIR" || exit 2
echo "bench-run.sh: pwd is now $(pwd)"

# ---- a prebuilt package runs its tier's binary; everything down to the run is the source tree's ----------------
if [ -n "$PREBUILT" ]; then
    BINARY="$PACK_BIN"
    echo "bench-run.sh: prebuilt package -- nothing is compiled here; running $BINARY"
    if [ -n "$CLOCK_FROM_ARG" ]; then
        echo "bench-run.sh: clock $CLOCK_FROM_ARG = $CLK_OVERRIDE Hz is built into $BINARY (picked by name)"
    fi
    sed 's/^/bench-run.sh: package: /' "$PACKAGE_FILE"
fi
if [ -z "$PREBUILT" ]; then

# ---- optionally patch CLK_FREQ in the tier's top (test_bench_dual / test_bench_t0) ----------
# The ONLY source mutation this script ever performs, and only when a clock
# NAME is given (or a shorthand tier names one). Restored on exit, including
# on interrupt.
BACKUP_BENCH=""
if [ -n "$MEASURE_ONLY" ] && [ -n "$CLK_OVERRIDE" ]; then
    # The clock is one CON value; it does not move the DEBUG footprint, and a measurement
    # must never write a source file.
    echo "bench-run.sh: measure-only -- clock override $CLK_OVERRIDE not applied, no source file written"
elif [ -n "$CLK_OVERRIDE" ]; then
    if ! [[ "$CLK_OVERRIDE" =~ ^[0-9]+$ ]]; then
        die "CLK_FREQ must be a number (got '$CLK_OVERRIDE')"
    fi

    BACKUP_BENCH="$(mktemp "${TMPDIR:-/tmp}/bench-clkfreq.XXXXXX")"     # (a template with X's: `mktemp -t NAME` is BSD-only)
    cp -p "$BENCH_FILE" "$BACKUP_BENCH"
    cleanup() {
        if [ -n "$BACKUP_BENCH" ] && [ -f "$BACKUP_BENCH" ]; then
            cp -p "$BACKUP_BENCH" "$BENCH_FILE"
            rm -f "$BACKUP_BENCH"
        fi
    }
    trap cleanup EXIT
    trap 'cleanup; exit 130' INT TERM

    # the line must be there to patch, or the run would be at the file's own clock while saying otherwise
    if ! grep -q '^ *CLK_FREQ = [0-9_]*' "$BENCH_FILE"; then
        die "$BENCH_FILE has no 'CLK_FREQ = <number>' line to set the clock $CLOCK_NAME in"
    fi
    echo "bench-run.sh: clock $CLOCK_NAME = $CLK_OVERRIDE Hz: patching CLK_FREQ in $BENCH_FILE (restored on exit)"
    # (no `sed -i`: its argument differs between BSD and GNU sed. The untouched copy is read, the file written.)
    if ! sed "s/^\( *\)CLK_FREQ = [0-9_]*/\1CLK_FREQ = $CLK_OVERRIDE/" "$BACKUP_BENCH" > "$BENCH_FILE"; then
        echo "ERROR: failed to patch CLK_FREQ in $BENCH_FILE" >&2
        exit 2
    fi
else
    CLK_OVERRIDE="270000000"  # the tier binary's own CLK_FREQ default; no file touched
    echo "bench-run.sh: no clkfreq override given -- using the file's own default (270000000), no source file written"
fi

# ---- compile the bench top, with src/ as cwd -----------------------------------
# NOTE: capture $? from the command itself, NOT from inside `if ! cmd; then`
# -- there $? is the status of the negation (always 0), so the error line
# would report a failure with "exit 0" and hide the one number worth having.
#
# ONE COMPILE AT THE BENCH; TWO ONLY WHEN MEASURING (PL-152, 2026-09-26). The
# DEBUG footprint is the -d image's size minus the same build's size without -d
# (P2-HAZARD-REGISTER DBG-1: subtract binary sizes -- no parsing, nothing that
# can drift), which takes two compiles, and until now every bench run made both:
# about 26 s of a test_bench_dual tier's time went to compiling (STEPHEN
# 2026-09-26: "The script is now compiling files twice").
#
# WHERE THE FOOTPRINT IS ENFORCED NOW: at commit time. tools/build-check.sh runs
# this script with BENCH_MEASURE_ONLY=1 over every tier in the case table above,
# and the measure-only path below makes both compiles and refuses a tier over
# DEBUG_FOOTPRINT_MAX exactly as a run used to -- so a tier that would lose its
# records fails the commit gate, before it can reach the bench.
#
# WHY THE BENCH TRUSTS IT: the bench runs a commit that gate passed -- it pulls
# the gated tree, and the footprint is a property of the source and these flags,
# not of the machine that compiles them. Measuring it again at the bench bought
# nothing but the second compile. So a run compiles once, with -d and -l, the
# very binary it downloads, and says in its transcript that the footprint was
# not measured here and where it was.
#
# Measure-only writes both images under names of its own (-o) and removes them,
# so build-check.sh can measure tiers side by side without two compiles sharing
# one .bin; the flags are the run's own.
BINARY="${BENCH_FILE%.spin2}.bin"
if [ -n "$MEASURE_ONLY" ]; then
    MEASURE_PLAIN=".footprint-$TIER-plain.bin"
    MEASURE_DEBUG=".footprint-$TIER-debug.bin"
    trap 'rm -f "$MEASURE_PLAIN" "$MEASURE_DEBUG"' EXIT
    trap 'rm -f "$MEASURE_PLAIN" "$MEASURE_DEBUG"; exit 130' INT TERM   # as the clock patch's cleanup does

    # the plain one FIRST, as it always ran: its size is the subtrahend
    run "$PNUT" -o "$MEASURE_PLAIN" -D BENCH_CFG ${EXTRA_DEFS[@]+"${EXTRA_DEFS[@]}"} "$BENCH_FILE"
    STATUS=$?
    if [ $STATUS -ne 0 ] || [ ! -f "$MEASURE_PLAIN" ]; then
        die "command failed (exit $STATUS): $PNUT -o $MEASURE_PLAIN -D BENCH_CFG ${EXTRA_DEFS[@]+${EXTRA_DEFS[@]}} $BENCH_FILE"
    fi
    PLAIN_BYTES=$(wc -c < "$MEASURE_PLAIN" | tr -d ' ')

    run "$PNUT" -o "$MEASURE_DEBUG" -d -D BENCH_CFG ${EXTRA_DEFS[@]+"${EXTRA_DEFS[@]}"} "$BENCH_FILE"
    STATUS=$?
    if [ $STATUS -ne 0 ] || [ ! -f "$MEASURE_DEBUG" ]; then
        die "command failed (exit $STATUS): $PNUT -o $MEASURE_DEBUG -d -D BENCH_CFG ${EXTRA_DEFS[@]+${EXTRA_DEFS[@]}} $BENCH_FILE"
    fi
    DEBUG_BYTES=$(( $(wc -c < "$MEASURE_DEBUG" | tr -d ' ') - PLAIN_BYTES ))
else
    # PL-68: a source-tree build prints NOT_A_PACK in its banner, so the log names its commit here: HEAD, and
    #  whether src/ and tools/ match it (with changes, the binary is NOT that commit). A pack build (BENCH_PACK_DIR)
    #  compiles in a git-archive copy, not a checkout: its banner and BENCH-PACKAGE carry the commit instead.
    if [ -n "$PACK_DIR" ]; then
        :
    elif run git -C "$SRC_DIR/.." rev-parse --short HEAD; then
        echo "+ git -C $SRC_DIR/.. status --porcelain -- src tools"
        TREE_CHANGES=$(git -C "$SRC_DIR/.." status --porcelain -- src tools)
        if [ -z "$TREE_CHANGES" ]; then
            echo "bench-run.sh: src/ and tools/ match that commit -- this binary is that commit"
        else
            printf '%s\n' "$TREE_CHANGES"
            echo "bench-run.sh: src/ or tools/ has CHANGES -- this binary is NOT that commit"
        fi
    else
        echo "bench-run.sh: not a git checkout -- the commit is unknown"
    fi
    # the bench: the one compile, -d (every tier's debug kernel and records) and -l (the listing kept beside it)
    run "$PNUT" -l -d -D BENCH_CFG ${EXTRA_DEFS[@]+"${EXTRA_DEFS[@]}"} "$BENCH_FILE"
    STATUS=$?
    if [ $STATUS -ne 0 ] || [ ! -f "$BINARY" ]; then
        die "command failed (exit $STATUS): $PNUT -l -d -D BENCH_CFG ${EXTRA_DEFS[@]+${EXTRA_DEFS[@]}} $BENCH_FILE"
    fi
    echo "bench-run.sh: DEBUG footprint not measured at the bench (PL-152) -- it is enforced at commit time by tools/build-check.sh, which measures every tier; image $(wc -c < "$BINARY" | tr -d ' ') bytes"
    if [ -n "$PACK_DIR" ]; then
        run cp -p "$BINARY" "$PACK_DIR/$PACK_KEY.bin" || die "could not copy $BINARY to $PACK_DIR/$PACK_KEY.bin"
        echo "bench-run.sh: packed -- tier '$TIER'${CLOCK_FROM_ARG:+ at clock $CLOCK_FROM_ARG} compiled for a prebuilt package as $PACK_KEY.bin; not run"
        exit 0
    fi
fi

# ---- refuse an image whose DEBUG data runs past its end (DBG-1) ----------------
# WHY THIS EXISTS. A -d image's DEBUG data has a hard end, and no tool reports
# crossing it: any debug() record whose bytes lie past image offset 13,684 is
# cut at that byte or never sent. MEASURED three times -- 2026-09-20 t0-hand's
# PLOT create stopped at "hand-rotation an", t0's "T0-23,begin,no_bo" (PL-94)
# stopped at the same offset, and 2026-09-22's USB captures of t0-hand and
# t0-stopmode carried no display command at all. Every attended panel was lost
# this way, and the losses were blamed on cog bursts and the terminal first.
#
# THE LIMIT IS THE LARGEST FOOTPRINT MEASURED TO RUN INTACT, never the
# documented cap (DBG-1): 12,404 bytes, 2026-09-15's t0-hand (6aed714), which
# drew its panel and delivered every record. The smallest measured to lose
# records is 15,619 (2026-09-20's t0-hand, a37bac1). Raise the limit only on a
# larger build shown, on the wire, to deliver its last record.
#
# OVER THE LIMIT, DO NOT CUT DIAGNOSTICS. Compile out what the tier never runs
# (DBG-16), move record text into DAT and emit it with zstr_() (DBG-2), or
# channel it (DBG-5/6).
#
# PL-152: this gate runs in measure-only, the commit gate's path (the compile
# section above says why the bench no longer repeats it). build-check.sh reads
# the "DEBUG footprint N bytes" line below; keep its wording.
DEBUG_FOOTPRINT_MAX=12404
if [ -n "$MEASURE_ONLY" ]; then
    echo "bench-run.sh: DEBUG footprint $DEBUG_BYTES bytes (limit $DEBUG_FOOTPRINT_MAX; -d $((PLAIN_BYTES + DEBUG_BYTES)) - plain $PLAIN_BYTES)"
    if [ "$DEBUG_BYTES" -gt "$DEBUG_FOOTPRINT_MAX" ]; then
        die "tier '$TIER' carries $DEBUG_BYTES bytes of DEBUG data, over the $DEBUG_FOOTPRINT_MAX measured to run intact: its last debug() records would be cut or never sent (DBG-1). Shrink the footprint without cutting output (DBG-16, DBG-2, DBG-5/6) before this tier can pass the commit gate and run."
    fi
    echo "bench-run.sh: measure-only -- tier '$TIER' within the DEBUG footprint limit; not run"
    exit 0
fi

fi   # the source tree's compile; a prebuilt package resumes here, at the run

# ---- run, with src/ as cwd, batch mode -----------------------------------------
# --exit-on-end-session makes pnut-term-ts close itself once the tier's binary
# prints its DEBUG_END_SESSION marker (the tool's own documented default
# end-marker phrase), instead of waiting on a keypress or a fixed timeout.
#
# NO --console-mode (PL-92, removed 2026-09-19). It was here for "a
# console-friendly run" and it silently cost every attended tier its panel: a
# console session opens no window, so the DEBUG display commands a panel is
# made of went nowhere and PC_KEY could never answer. At Visit 6a t0-stopmode
# emitted its records, waited on a keypress that could not arrive, and lost all
# eight of its cells; t0-hand, dual-brake, dual-floor and dual-ui had the same
# defect and had simply not been run through this script since their panels
# were added. STEPHEN 2026-09-19: "i don't think there is any benefit to our
# running with --console-mode". One invocation serves every tier -- an
# unattended tier draws no window because it creates none, not because the
# terminal was told it may not.
#
# -u ON EVERY RUN, and BEFORE -r (STEPHEN 2026-09-23: "always specify -u along
# with the -r (-u first)"). The USB-traffic capture is the wire-level record that
# the debug log is not (PL-85: a verdict the log lost survived only on USB), so
# every tier carries one rather than the run that happened to be repeated with it.
LOG_BEFORE="$(newest_log)"

run "$PNUT_TERM" -u -r "$BINARY" --exit-on-end-session
STATUS=$?
if [ $STATUS -ne 0 ]; then
    echo "ERROR: command failed (exit $STATUS): $PNUT_TERM -u -r $BINARY --exit-on-end-session" >&2
    exit 2
fi

# ---- refuse a load that emitted nothing (PL-74) --------------------------------
# WHY THIS EXISTS. At Visit 4 the t0 tier downloaded successfully and then emitted
# NOTHING -- not one program line, and not even the debug kernel's own "CogN INIT"
# lines. All ten t0 cells were lost and nobody knew until the logs were read hours
# later. The compile was not at fault: this script passes -d to every tier, and the
# sizes settle it (MEASURED 2026-09-17, test_bench_t0 with -D BENCH_CFG: 43,784
# bytes with -d, 25,764 without, against the 43,780 bytes that was downloaded). So
# the image carried the debug kernel and the kernel never spoke -- a load failure,
# not a build failure, and one that is visible in milliseconds. It must not cost a
# bench slot again.
#
# THE CHECK IS TIER-INDEPENDENT ON PURPOSE. It looks for the debug kernel's own
# "CogN INIT" line, which EVERY -d image emits at load whatever the tier does next,
# rather than for a per-tier banner string this script would have to keep in step
# with six binaries. The second check is for any program line at all, which
# separates "the image never started" from "it started and stayed silent".
#
# It READS the newest log and never writes, moves or renames it: log curation is
# still the operator's, and pnut-term-ts still owns the name and the location.
LOG_AFTER="$(newest_log)"
if [ -z "$LOG_AFTER" ] || [ "$LOG_AFTER" = "$LOG_BEFORE" ]; then
    die "the run wrote no new log under $SRC_DIR/$LOG_DIR -- nothing was captured, so this load certified nothing. Re-run tier '$TIER'."
fi

if ! grep -qE 'Cog[0-7][[:space:]]+INIT' "$LOG_AFTER"; then
    die "$SRC_DIR/$LOG_AFTER has no 'CogN INIT' line: the downloaded image never emitted, so EVERY cell in tier '$TIER' is NOT_BUILT. This is the PL-74 failure. Power-cycle the P2 and re-run tier '$TIER' before spending more bench time."
fi

if ! grep -E 'Cog[0-7][[:space:]]+' "$LOG_AFTER" | grep -qvE 'INIT[[:space:]]+\$'; then
    die "$SRC_DIR/$LOG_AFTER carries the load's 'CogN INIT' lines and NOT ONE program line: the image started and said nothing, so tier '$TIER' judged no cell. Re-run it before spending more bench time."
fi

# ---- done ---------------------------------------------------------------------
# NO LOG CURATION. pnut-term-ts already writes src/logs/debug_<date>-<time>.log,
# whose name carries when the run happened. Copying that to a name of this
# script's choosing threw the timestamp away and silently overwrote the earlier
# run of the same tier on the same day. The log stays where the tool put it,
# under the name the tool gave it.
echo "bench-run.sh: binary:  $SRC_DIR/$BINARY"
echo "bench-run.sh: log:     $SRC_DIR/logs/ (newest debug_*.log -- named by the tool, left where it landed)"

exit 0

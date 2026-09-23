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
# test_bench_scan and test_bench_dual.
#
# Usage:  tools/bench-run.sh <tier>
#   <tier>      -- tier name, see usage() below. It is the ONLY argument: nothing
#                  numeric is ever typed at the bench (STEPHEN 2026-09-16: "please
#                  don't create commands where the data entry due to length causes
#                  risk to me typeing it correctly (e.g., Hz values that's silly)").
#
# The clock sweep is three tiers, dual-clock-200 / -270 / -300, each naming its
# clock. Those tiers are the ONLY thing that may cause this script to write to a
# source file (test_bench_dual.spin2's "CLK_FREQ = ..." line); every other tier is
# read-only with respect to the tree. Restored on exit, including on interrupt.

set -u

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SRC_DIR="$(cd "${SCRIPT_DIR}/../src" && pwd)"
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

# The three clocks the dual-clock-* tiers sweep, in Hz, each named once by its tier
# below. test_bench_dual.spin2 judges its CLKFRAME sign-off cell only at these (its
# SF_CLOCK_* constants), so a run at any other clock judges nothing -- see PL-62.
CLOCK_200_HZ="200000000"
CLOCK_270_HZ="270000000"
CLOCK_300_HZ="300000000"

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
Usage:  tools/bench-run.sh <tier>
  <tier>      -- one of:
                   t0             Tier 0 -- no motor, no motion, no risk
                   panel          PLOT pipeline probe: two windows differing ONLY in name, no motors, reads out in the log  [NOTHING MOVES, ATTENDED]
                   t0-hand        Tier 0's T0-12 hand-rotation anchor only -- OPERATOR TURNS ONE WHEEL, waits on a keypress, no sign-off cell
                   t0-stopmode    Tier 0's T0-24 stop-state hand test only -- OPERATOR TURNS ONE WHEEL SIX TIMES, TWO ROWS SPIN IT UNDER POWER  [WHEELS UP, ATTENDED]
                   spin           wiring check -- BOTH WHEELS TURN at 50%, fwd then reverse
                   detect         board-detection sweep, PASSIVE (no driver code in the image)
                   detect-lib     as above + the library cross-check (still no driver cog)
                   detect-phase2  adds the driver-cog poisoning probe  [MOTORS MAY STAY CONNECTED, GATE-OVERLAP GROUPS SKIPPED]
                   char           automated motor characterisation, nine holds  [MOTORS CONNECTED, UNATTENDED]
                   scan           automated per-direction commutation-offset scan  [MOTORS CONNECTED, UNATTENDED]
                   scan-wdtest    watchdog self-test: preflight, deliberate stall, watchdog ends the run  [MOTORS CONNECTED]
                   scan-droop     droop-stop self-test: pure logic, three point sequences through the real stop decision  [NOTHING MOVES]
                   dual-a         motion harness part A: PREFLT, STOPMODE, LIVE, LADDER, LOWSPD  [MOTORS CONNECTED, WHEELS UP, UNATTENDED]
                   dual-a-legacy  as dual-a, on the LEGACY commutation offsets 43/317 -- the control leg, draws far more current  [MOTORS CONNECTED, WHEELS UP, UNATTENDED]
                   dual-clock-200 motion harness clock load at 200 MHz: PREFLT, CLOCK  [WHEELS UP, UNATTENDED]
                   dual-clock-270 motion harness clock load at 270 MHz: PREFLT, CLOCK  [WHEELS UP, UNATTENDED]
                   dual-clock-300 motion harness clock load at 300 MHz: PREFLT, CLOCK  [WHEELS UP, UNATTENDED]
                   dual-b         motion harness part B: PREFLT, FAULTB, OVERSHT  [MOTORS CONNECTED, WHEELS UP, UNATTENDED]
                   dual-brake     motion harness part BRAKE: OUTSIDE -- OPERATOR HAND-BRAKES THE LEFT WHEEL ONCE  [WHEELS UP, ATTENDED]
                   dual-c         motion harness part C: PREFLT, BASELINE, POSTFLT  [MOTORS CONNECTED, WHEELS UP, UNATTENDED]
                   dual-d         motion harness part D: PREFLT, STEERSEG, LIMIT -- the front cog's contract and current limiting  [MOTORS CONNECTED, WHEELS UP, UNATTENDED]
                   dual-floor     motion harness part FLOOR -- WHEELS DOWN, OPERATOR OBSERVES ABOUT 2 S OF DRIVING  [ATTENDED]
                   dual-ui        motion harness part UICHECK -- NO MOTOR CONTROL: walks the operator through every panel control and attended screen  [ATTENDED]
                   dual-align     motion harness part ALIGN -- NO MOTOR IS DRIVEN: the operator turns each wheel BY HAND, 8 legs, to measure the hall zero cold  [ATTENDED]
                   dual-lead      motion harness part LEAD: PREFLT, LEAD -- the live lead-step run that measures the dynamic-lead table  [MOTORS CONNECTED, WHEELS UP, UNATTENDED]
                   dual-limits    motion harness part LIMITS: PREFLT, LIMTOP, LIMRAMP, LIMLOW -- the limits reset's top speed, ramps and low-speed floor  [MOTORS CONNECTED, WHEELS UP, UNATTENDED]
                   dual-limits-top  as dual-limits' LIMTOP only: the climb and the power check that confirm moved limits  [MOTORS CONNECTED, WHEELS UP, UNATTENDED]

Examples:
  tools/bench-run.sh detect
  tools/bench-run.sh char
  tools/bench-run.sh dual-clock-200
EOF
    exit 2
}

if [ $# -ne 1 ]; then
    if [ $# -gt 1 ]; then
        echo "ERROR: one argument only, the tier name -- a clock is chosen by the tier (dual-clock-200, dual-clock-270, dual-clock-300)"
    fi
    usage
fi

TIER="$1"
CLK_OVERRIDE=""

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
                    PRECONDITION="MOTORS CONNECTED, WHEELS UP -- ATTENDED stop-state hand test on the RIGHT wheel: click the t0stop window first; nothing happens until you press S. Each row names on the panel what to do BEFORE it runs -- turn or spin the wheel by hand, then SPACE. ROWS 4 AND 5 SPIN THE WHEEL UNDER POWER AND FAULT IT ON PURPOSE: hands off until the panel asks, SPACE aborts a powered row"
                    ;;
    spin)           BENCH_FILE="test_bench_spin.spin2"
                    PRECONDITION="BOTH WHEELS WILL TURN AT 50% POWER -- lift or support the platform"
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
    # PL-62: the clock is part of the tier name, so a mistyped clock is impossible rather than merely
    #  detectable -- a wrong name is an unknown tier and is refused.
    dual-clock-200|dual-clock-270|dual-clock-300)
                    BENCH_FILE="test_bench_dual.spin2"
                    EXTRA_DEFS=(-D BENCH_QUIET -D DUAL_PART_CLOCK)
                    case "$TIER" in
                        dual-clock-200) CLK_OVERRIDE="$CLOCK_200_HZ" ;;
                        dual-clock-270) CLK_OVERRIDE="$CLOCK_270_HZ" ;;
                        dual-clock-300) CLK_OVERRIDE="$CLOCK_300_HZ" ;;
                    esac
                    PRECONDITION="MOTORS CONNECTED, WHEELS UP, BOTH WHEELS FREE TO TURN, HANDS: NONE -- UNATTENDED motion harness clock load (PREFLT, CLOCK) at clkfreq $CLK_OVERRIDE, about 1 minute; one of three runs: dual-clock-200, dual-clock-270, dual-clock-300"
                    ;;
    dual-clock)     die "tier 'dual-clock' is now three tiers that name their clock: dual-clock-200, dual-clock-270, dual-clock-300" ;;
    dual-b)         BENCH_FILE="test_bench_dual.spin2"
                    EXTRA_DEFS=(-D BENCH_QUIET -D DUAL_PART_B)
                    PRECONDITION="MOTORS CONNECTED, WHEELS UP, BOTH WHEELS FREE TO TURN, HANDS: NONE -- UNATTENDED motion harness part B (PREFLT, FAULTB ramp trials that fault on purpose, OVERSHT distance moves through the steering object), run cap 20 minutes"
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
                    PRECONDITION="MOTORS CONNECTED, WHEELS UP, BOTH WHEELS FREE TO TURN, HANDS: NONE -- UNATTENDED motion harness part D (PREFLT, STEERSEG, LIMIT): the front cog's contract and current limiting. THE WHEELS STOP DEAD, JERK AND STAND STILL UNDER POWER ON PURPOSE -- an emergency stop is latched and held, a stop is ordered while another cog drives, and the current limits are lowered until the motor cannot turn (the protective-stop test) before being restored, run cap 15 minutes"
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
    *)  echo "ERROR: unknown tier '$TIER'" >&2
        usage
        ;;
esac

# ---- sanity checks ----------------------------------------------------------
# command -v, not [ -x ] -- these are PATH names, not paths, and -x on a bare
# name tests a file in the current directory.
if ! command -v "$PNUT" >/dev/null 2>&1; then
    echo "ERROR: '$PNUT' not found on PATH (override with PNUT_TS=/path/to/pnut-ts)" >&2
    exit 2
fi

if [ -z "$MEASURE_ONLY" ] && ! command -v "$PNUT_TERM" >/dev/null 2>&1; then
    echo "ERROR: '$PNUT_TERM' not found on PATH (override with PNUT_TERM_TS=/path/to/pnut-term-ts)" >&2
    exit 2
fi

if [ -n "$PRECONDITION" ] && [ -z "$MEASURE_ONLY" ]; then
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

# ---- optionally patch CLK_FREQ in test_bench_t0.spin2 -------------------------
# The ONLY source mutation this script ever performs, and only when a
# clkfreq argument is explicitly given. Restored on exit, including on
# interrupt.
BACKUP_BENCH=""
if [ -n "$MEASURE_ONLY" ] && [ -n "$CLK_OVERRIDE" ]; then
    # The clock is one CON value; it does not move the DEBUG footprint, and a measurement
    # must never write a source file.
    echo "bench-run.sh: measure-only -- clock override $CLK_OVERRIDE not applied, no source file written"
elif [ -n "$CLK_OVERRIDE" ]; then
    if ! [[ "$CLK_OVERRIDE" =~ ^[0-9]+$ ]]; then
        die "CLK_FREQ must be a number (got '$CLK_OVERRIDE')"
    fi

    BACKUP_BENCH="$(mktemp -t bench-clkfreq)"
    cp -p "$BENCH_FILE" "$BACKUP_BENCH"
    cleanup() {
        if [ -n "$BACKUP_BENCH" ] && [ -f "$BACKUP_BENCH" ]; then
            cp -p "$BACKUP_BENCH" "$BENCH_FILE"
            rm -f "$BACKUP_BENCH"
        fi
    }
    trap cleanup EXIT
    trap 'cleanup; exit 130' INT TERM

    echo "bench-run.sh: patching CLK_FREQ to $CLK_OVERRIDE in $BENCH_FILE (restored on exit)"
    if ! sed -i '' "s/CLK_FREQ = [0-9_]*/CLK_FREQ = $CLK_OVERRIDE/" "$BENCH_FILE"; then
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
# TWO COMPILES, the plain one FIRST: the DEBUG footprint is measured as the -d
# image's size minus the same build's size without -d (P2-HAZARD-REGISTER DBG-1:
# subtract binary sizes -- no parsing, nothing that can drift). The -d build runs
# second so the binary left in src/ is the one that is downloaded.
#
# Measure-only writes both images under names of its own (-o) and removes them,
# so build-check.sh can measure tiers side by side without two compiles sharing
# one .bin; the flags are the run's own.
BINARY="${BENCH_FILE%.spin2}.bin"
PLAIN_OUT=()
DEBUG_OUT=()
MEASURE_PLAIN="$BINARY"
MEASURE_DEBUG="$BINARY"
LIST_OPT=(-l)
if [ -n "$MEASURE_ONLY" ]; then
    MEASURE_PLAIN=".footprint-$TIER-plain.bin"
    MEASURE_DEBUG=".footprint-$TIER-debug.bin"
    PLAIN_OUT=(-o "$MEASURE_PLAIN")
    DEBUG_OUT=(-o "$MEASURE_DEBUG")
    LIST_OPT=()
    trap 'rm -f "$MEASURE_PLAIN" "$MEASURE_DEBUG"' EXIT
    trap 'rm -f "$MEASURE_PLAIN" "$MEASURE_DEBUG"; exit 130' INT TERM   # as the clock patch's cleanup does
fi

run "$PNUT" ${PLAIN_OUT[@]+"${PLAIN_OUT[@]}"} -D BENCH_CFG ${EXTRA_DEFS[@]+"${EXTRA_DEFS[@]}"} "$BENCH_FILE"
STATUS=$?
if [ $STATUS -ne 0 ] || [ ! -f "$MEASURE_PLAIN" ]; then
    die "command failed (exit $STATUS): $PNUT ${PLAIN_OUT[*]+${PLAIN_OUT[*]}} -D BENCH_CFG ${EXTRA_DEFS[@]+${EXTRA_DEFS[@]}} $BENCH_FILE"
fi
PLAIN_BYTES=$(wc -c < "$MEASURE_PLAIN" | tr -d ' ')

run "$PNUT" ${DEBUG_OUT[@]+"${DEBUG_OUT[@]}"} ${LIST_OPT[@]+"${LIST_OPT[@]}"} -d -D BENCH_CFG ${EXTRA_DEFS[@]+"${EXTRA_DEFS[@]}"} "$BENCH_FILE"
STATUS=$?
if [ $STATUS -ne 0 ] || [ ! -f "$MEASURE_DEBUG" ]; then
    die "command failed (exit $STATUS): $PNUT ${DEBUG_OUT[*]+${DEBUG_OUT[*]}} ${LIST_OPT[*]+${LIST_OPT[*]}} -d -D BENCH_CFG ${EXTRA_DEFS[@]+${EXTRA_DEFS[@]}} $BENCH_FILE"
fi
DEBUG_BYTES=$(( $(wc -c < "$MEASURE_DEBUG" | tr -d ' ') - PLAIN_BYTES ))

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
DEBUG_FOOTPRINT_MAX=12404
echo "bench-run.sh: DEBUG footprint $DEBUG_BYTES bytes (limit $DEBUG_FOOTPRINT_MAX; -d $((PLAIN_BYTES + DEBUG_BYTES)) - plain $PLAIN_BYTES)"
if [ "$DEBUG_BYTES" -gt "$DEBUG_FOOTPRINT_MAX" ]; then
    die "tier '$TIER' carries $DEBUG_BYTES bytes of DEBUG data, over the $DEBUG_FOOTPRINT_MAX measured to run intact: its last debug() records would be cut or never sent (DBG-1). Nothing was downloaded. Shrink the footprint without cutting output (DBG-16, DBG-2, DBG-5/6) before this tier runs."
fi
if [ -n "$MEASURE_ONLY" ]; then
    echo "bench-run.sh: measure-only -- tier '$TIER' within the DEBUG footprint limit; not run"
    exit 0
fi

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
echo "bench-run.sh: binary:  src/$BINARY"
echo "bench-run.sh: log:     src/logs/ (newest debug_*.log -- named by the tool, left where it landed)"

exit 0

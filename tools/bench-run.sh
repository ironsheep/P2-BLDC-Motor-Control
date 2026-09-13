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
# It does NOT touch the logs. pnut-term-ts names them by timestamp and puts
# them in src/logs/; that is already right and this script leaves it alone.
#
# Every external command this script runs is echoed verbatim, immediately
# before it runs, prefixed "+ " -- so the transcript is something you can
# replay by hand line for line.
#
# --exit-on-end-session (batch mode, not --ide -- that flag is for VSCode/IDE
# integration only) makes pnut-term-ts close itself once the tier's binary
# prints its DEBUG_END_SESSION marker, so this produces one binary and one
# log with no keypress and no interrupt needed. Every tier's binary emits
# that marker: test_bench_t0, test_bench_spin, test_bench_detect,
# test_bench_char and test_bench_scan.
#
# Usage:  tools/bench-run.sh <tier> [clkfreq]
#   <tier>      -- tier name, see usage() below
#   [clkfreq]   -- optional clock frequency in Hz (e.g., 270000000). The ONLY
#                  thing that may cause this script to write to a source file
#                  (the tier binary's "CLK_FREQ = ..." line) -- omit it and the
#                  script is read-only with respect to the tree. Restored on
#                  exit, including on interrupt. test_bench_t0, test_bench_detect,
#                  test_bench_char and test_bench_scan carry that line;
#                  test_bench_spin does not, so for the spin tier the patch
#                  changes nothing.

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

# echo a command verbatim, then run it. "$@" is the real argv -- nothing
# paraphrased, nothing elided.
run() {
    echo "+ $*"
    "$@"
}

# ---- usage and argument validation ----------------------------------------------
usage() {
    cat >&2 <<'EOF'
Usage:  tools/bench-run.sh <tier> [clkfreq]
  <tier>      -- one of:
                   t0             Tier 0 -- no motor, no motion, no risk
                   spin           wiring check -- BOTH WHEELS TURN at 50%, fwd then reverse
                   detect         board-detection sweep, PASSIVE (no driver code in the image)
                   detect-lib     as above + the library cross-check (still no driver cog)
                   detect-phase2  adds the driver-cog poisoning probe  [MOTORS UNPLUGGED]
                   char           motor characterisation, PLOT panel   [MOTORS CONNECTED]
                   char-nopanel   as above, no PLOT window, keyboard only
                   scan           automated per-direction commutation-offset scan  [MOTORS CONNECTED, UNATTENDED]
  [clkfreq]   -- optional clock frequency in Hz (default: 270000000)

Examples:
  tools/bench-run.sh detect
  tools/bench-run.sh detect-lib
  tools/bench-run.sh char
EOF
    exit 2
}

if [ $# -lt 1 ]; then
    usage
fi

TIER="$1"
CLK_OVERRIDE="${2:-}"

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
    t0)             BENCH_FILE="test_bench_t0.spin2"
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
                    PRECONDITION="THE MOTORS MUST BE PHYSICALLY UNPLUGGED -- this build starts a real driver cog"
                    ;;
    char)           BENCH_FILE="test_bench_char.spin2"
                    PRECONDITION="MOTORS CONNECTED and the pack voltage recorded -- the wheels will turn"
                    ;;
    char-nopanel)   BENCH_FILE="test_bench_char.spin2"
                    EXTRA_DEFS=(-D BENCH_NO_PANEL)
                    PRECONDITION="MOTORS CONNECTED and the pack voltage recorded -- the wheels will turn"
                    ;;
    scan)           BENCH_FILE="test_bench_scan.spin2"
                    PRECONDITION="MOTORS CONNECTED, BOTH WHEELS FREE TO TURN -- UNATTENDED offset scan, up to 30 minutes, each wheel both directions to half speed"
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

if ! command -v "$PNUT_TERM" >/dev/null 2>&1; then
    echo "ERROR: '$PNUT_TERM' not found on PATH (override with PNUT_TERM_TS=/path/to/pnut-term-ts)" >&2
    exit 2
fi

if [ -n "$PRECONDITION" ]; then
    echo ""
    echo "  ****************************************************************"
    echo "  ** $PRECONDITION"
    echo "  ** PANIC PROCEDURE IS PHYSICAL BATTERY DISCONNECT ONLY."
    echo "  ** emergencyCutoff() self-cancels in ~250ms and is NOT a panic button."
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
if [ -n "$CLK_OVERRIDE" ]; then
    if ! [[ "$CLK_OVERRIDE" =~ ^[0-9]+$ ]]; then
        echo "ERROR: CLK_FREQ must be a number (got '$CLK_OVERRIDE')" >&2
        exit 2
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
run "$PNUT" -l -d -D BENCH_CFG ${EXTRA_DEFS[@]+"${EXTRA_DEFS[@]}"} "$BENCH_FILE"
STATUS=$?
if [ $STATUS -ne 0 ]; then
    echo "ERROR: command failed (exit $STATUS): $PNUT -l -d -D BENCH_CFG ${EXTRA_DEFS[@]+${EXTRA_DEFS[@]}} $BENCH_FILE" >&2
    exit 2
fi

BINARY="${BENCH_FILE%.spin2}.bin"
if [ ! -f "$BINARY" ]; then
    echo "ERROR: compilation succeeded but binary not found: $BINARY" >&2
    exit 2
fi

# ---- run, with src/ as cwd, batch mode -----------------------------------------
# Batch (not --ide -- that's VSCode/IDE integration, not a terminal session):
# --console-mode for a console-friendly run, --exit-on-end-session so
# pnut-term-ts closes itself once the tier's binary prints its
# DEBUG_END_SESSION marker (the tool's own documented default end-marker
# phrase), instead of waiting on a keypress or a fixed timeout.
run "$PNUT_TERM" -r "$BINARY" --console-mode --exit-on-end-session
STATUS=$?
if [ $STATUS -ne 0 ]; then
    echo "ERROR: command failed (exit $STATUS): $PNUT_TERM -r $BINARY --console-mode --exit-on-end-session" >&2
    exit 2
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

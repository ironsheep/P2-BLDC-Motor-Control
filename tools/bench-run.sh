#!/bin/bash
#
# bench-run.sh -- Bench tier runner for P2-BLDC-Motor-Control
#
# Stephen runs the underlying tools (pnut-ts, pnut-term-ts) by hand and wants
# to be able to keep doing that: "when you hide them behind scripts i have no
# idea what's going to run. then i can't help you figure out why." This
# script exists ONLY because a tier run is a fixed sequence of three separate
# tool invocations, and it does exactly those three steps and nothing else:
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
#   3. CURATE   -- copy the one log the run just produced to
#                  DOCs/analyses/bench/<date>/<tier>.log (tracked; kept as
#                  .log because .gitignore excludes *.txt).
#
# Every external command this script runs is echoed verbatim, immediately
# before it runs, prefixed "+ " -- so the transcript is something you can
# replay by hand line for line.
#
# --exit-on-end-session (batch mode, not --ide -- that flag is for VSCode/IDE
# integration only) makes pnut-term-ts close itself once test_bench_t0.spin2
# prints its DEBUG_END_SESSION marker, so this produces one binary and one
# log with no keypress and no interrupt needed.
#
# Usage:  tools/bench-run.sh <tier> [clkfreq]
#   <tier>      -- tier name: currently "t0" only
#   [clkfreq]   -- optional clock frequency in Hz (e.g., 270000000). The ONLY
#                  thing that may cause this script to write to a source file
#                  (test_bench_t0.spin2's CLK_FREQ) -- omit it and the script
#                  is read-only with respect to the tree. Restored on exit,
#                  including on interrupt.

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
  <tier>      -- tier name: "t0" (Tier 0, no motor, no motion, no risk)
  [clkfreq]   -- optional clock frequency in Hz (default: 270000000)

Examples:
  tools/bench-run.sh t0
  tools/bench-run.sh t0 200000000
EOF
    exit 2
}

if [ $# -lt 1 ]; then
    usage
fi

TIER="$1"
CLK_OVERRIDE="${2:-}"

# Validate tier name.
case "$TIER" in
    t0) BENCH_FILE="test_bench_t0.spin2"
        ;;
    *)  echo "ERROR: unknown tier '$TIER' (only 't0' is supported)" >&2
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
    CLK_OVERRIDE="270000000"  # default already in test_bench_t0.spin2; no file touched
    echo "bench-run.sh: no clkfreq override given -- using the file's own default (270000000), no source file written"
fi

# ---- compile the bench top, with src/ as cwd -----------------------------------
# NOTE: capture $? from the command itself, NOT from inside `if ! cmd; then`
# -- there $? is the status of the negation (always 0), so the error line
# would report a failure with "exit 0" and hide the one number worth having.
run "$PNUT" -l -d -D BENCH_CFG "$BENCH_FILE"
STATUS=$?
if [ $STATUS -ne 0 ]; then
    echo "ERROR: command failed (exit $STATUS): $PNUT -l -d -D BENCH_CFG $BENCH_FILE" >&2
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
# pnut-term-ts closes itself once test_bench_t0.spin2 prints its
# DEBUG_END_SESSION marker (the tool's own documented default end-marker
# phrase), instead of waiting on a keypress or a fixed timeout.
LOG_CUTOFF=$(date +%s)
run "$PNUT_TERM" -r "$BINARY" --console-mode --exit-on-end-session
STATUS=$?
if [ $STATUS -ne 0 ]; then
    echo "ERROR: command failed (exit $STATUS): $PNUT_TERM -r $BINARY --console-mode --exit-on-end-session" >&2
    exit 2
fi

# ---- curate the log -------------------------------------------------------------
# Only accept a log file newer than LOG_CUTOFF (taken before the run started)
# -- a stale log already in src/logs/ must never be curated as if it were
# this run's evidence.
if [ ! -d "logs" ]; then
    echo "ERROR: no src/logs directory found after pnut-term-ts run" >&2
    exit 2
fi

NEW_LOG=""
for f in logs/*.log; do
    [ -e "$f" ] || continue
    MTIME=$(stat -f %m "$f" 2>/dev/null || stat -c %Y "$f" 2>/dev/null)
    if [ -n "$MTIME" ] && [ "$MTIME" -ge "$LOG_CUTOFF" ]; then
        if [ -z "$NEW_LOG" ] || [ "$MTIME" -gt "$(stat -f %m "$NEW_LOG" 2>/dev/null || stat -c %Y "$NEW_LOG" 2>/dev/null)" ]; then
            NEW_LOG="$f"
        fi
    fi
done

if [ -z "$NEW_LOG" ]; then
    echo "bench-run.sh: no new log produced in src/logs/ since this run started -- nothing curated"
    exit 2
fi

DATE=$(date +%Y-%m-%d)
BENCH_LOGS_DIR="${PROJECT_ROOT}/DOCs/analyses/bench/${DATE}"
if [ "$CLK_OVERRIDE" = "270000000" ]; then
    CURATED_LOG="${BENCH_LOGS_DIR}/${TIER}.log"
else
    CURATED_LOG="${BENCH_LOGS_DIR}/${TIER}-${CLK_OVERRIDE}.log"
fi

mkdir -p "$BENCH_LOGS_DIR" || exit 2
cp "$NEW_LOG" "$CURATED_LOG" || exit 2

# ---- summary ----------------------------------------------------------------
echo "bench-run.sh: binary:       src/$BINARY"
echo "bench-run.sh: log curated:  $CURATED_LOG"

exit 0

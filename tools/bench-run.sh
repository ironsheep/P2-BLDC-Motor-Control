#!/bin/bash
#
# bench-run.sh -- Bench tier runner for P2-BLDC-Motor-Control
#
# Compiles and loads a specified tier (currently T0 only) of the bench harness
# to the P2 and captures evidence into DOCs/analyses/bench/.
#
# The bench harness uses PC_KEY for interactive testing, which only works inside
# a graphical DEBUG display with focus. Therefore, the load MUST be headed
# (--ide -r) and NOT headless (--headless), because headless cannot serve an
# interactive session. This is not a preference; it is a requirement.
#
# Logs are named with .log extension, not .txt, because .gitignore excludes *.txt
# and a curated log saved as .txt is silently untracked — the evidence behind a
# verdict is lost. The curated copies go to DOCs/analyses/bench/ where they are
# TRACKED and remain discoverable by the same audit that settled them.
#
# This script reuses the config-block activation and restore-on-exit machinery
# from build-check.sh; do not rewrite it. The user config file and test_bench_t0's
# CLK_FREQ are both restored on exit, including on interrupt (Ctrl-C), so that
# the next build runs with the original settings.
#
# Usage:  tools/bench-run.sh <tier> [clkfreq]
#   <tier>      -- tier name: currently "t0" only
#   [clkfreq]   -- optional clock frequency in Hz (e.g., 270000000)

set -u

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SRC_DIR="${SCRIPT_DIR}/../src"
PROJECT_ROOT="${SCRIPT_DIR}/.."
CONFIG="isp_bldc_motor_userconfig.spin2"
BENCH_TOP="test_bench_t0.spin2"
PNUT="${PNUT_TS:-/Applications/pnut_ts/pnut-ts}"
PNUT_TERM="${PNUT_TERM_TS:-/Applications/PNut-Term-TS.app/Contents/Resources/bin/pnut-term-ts}"

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

# Validate tier name
case "$TIER" in
    t0) BENCH_FILE="test_bench_t0.spin2" ;;
    *)  echo "ERROR: unknown tier '$TIER' (only 't0' is supported)" >&2
        usage
        ;;
esac

# ---- sanity checks ----------------------------------------------------------
if [ ! -x "$PNUT" ]; then
    echo "ERROR: pnut-ts not found at $PNUT (override with PNUT_TS=/path)" >&2
    exit 2
fi

if [ ! -x "$PNUT_TERM" ]; then
    echo "ERROR: pnut-term-ts not found at $PNUT_TERM (override with PNUT_TERM_TS=/path)" >&2
    exit 2
fi

cd "$SRC_DIR" || exit 2

# ---- back up files that will be restored on exit ------------------------------
BACKUP_CONFIG="$(mktemp -t bldc-userconfig)"
BACKUP_BENCH="$(mktemp -t bench-clkfreq)"
cp -p "$CONFIG" "$BACKUP_CONFIG"
cp -p "$BENCH_FILE" "$BACKUP_BENCH"

cleanup() {
    # Restore only if backup still exists (idempotent)
    if [ -f "$BACKUP_CONFIG" ]; then
        cp -p "$BACKUP_CONFIG" "$CONFIG"
        rm -f "$BACKUP_CONFIG"
    fi
    if [ -f "$BACKUP_BENCH" ]; then
        cp -p "$BACKUP_BENCH" "$BENCH_FILE"
        rm -f "$BACKUP_BENCH"
    fi
    # Delete only the binaries and listings for this run, not all artifacts
    rm -f "${BENCH_FILE%.spin2}.bin" "${BENCH_FILE%.spin2}.lst" 2>/dev/null
}
trap cleanup EXIT
# On interrupt, cleanup and exit instead of falling through to later checks
trap 'cleanup; exit 130' INT TERM

# ---- discover and activate the correct config block ---------------------------
# test_bench_t0 requires the single-motor 6.5" config (ONLY_MOTOR_BASE / MOTR_6_5_INCH)
# Find the block opener via Python (same tool as build-check.sh)
CONFIG_LINENO=$(python3 - "$CONFIG" <<'PYEOF'
import re, sys
lines = open(sys.argv[1]).read().split('\n')
end = next((i for i, l in enumerate(lines)
            if 'Adjust your configuration' in l), len(lines))
i = 0
while i < end:
    if re.match(r"^'?\{\s*$", lines[i]):
        body = []
        j = i + 1
        while j < end and not re.match(r"^'?\}\s*$", lines[j]):
            body.append(lines[j]); j += 1
        text = '\n'.join(body)
        # Look for the single-motor 6.5" config: ONLY_MOTOR_BASE + MOTR_6_5_INCH
        if 'ONLY_MOTOR_BASE' in text and 'MOTR_6_5_INCH' in text:
            print(i)
            sys.exit(0)
        i = j + 1
    else:
        i += 1
print("", file=sys.stderr)
sys.exit(1)
PYEOF
)

if [ -z "$CONFIG_LINENO" ]; then
    echo "ERROR: could not find single-motor 6.5\" config block in $CONFIG" >&2
    echo "       (looking for ONLY_MOTOR_BASE + MOTR_6_5_INCH)" >&2
    exit 2
fi

# Activate the config block (same activate() function as build-check.sh)
python3 - "$CONFIG" "$CONFIG_LINENO" <<'PYEOF'
import re, sys
path, want = sys.argv[1], int(sys.argv[2])
lines = open(path).read().split('\n')
end = next((i for i, l in enumerate(lines)
            if 'Adjust your configuration' in l), len(lines))
for i in range(end):
    if re.match(r"^'?\{\s*$", lines[i]):
        lines[i] = "'{" if i == want else "{"
open(path, 'w').write('\n'.join(lines))
PYEOF

echo "bench-run.sh: tier=$TIER, config_block_line=$((CONFIG_LINENO + 1))"

# ---- optionally patch CLK_FREQ in test_bench_t0.spin2 -------------------------
if [ -n "$CLK_OVERRIDE" ]; then
    # Validate that it looks like a number
    if ! [[ "$CLK_OVERRIDE" =~ ^[0-9]+$ ]]; then
        echo "ERROR: CLK_FREQ must be a number (got '$CLK_OVERRIDE')" >&2
        exit 2
    fi

    # Patch CLK_FREQ = <old_value> to CLK_FREQ = <new_value>
    # This is a simple sed operation; the line is at the top of the file
    if ! sed -i '' "s/CLK_FREQ = [0-9_]*/CLK_FREQ = $CLK_OVERRIDE/" "$BENCH_FILE"; then
        echo "ERROR: failed to patch CLK_FREQ in $BENCH_FILE" >&2
        exit 2
    fi
    echo "bench-run.sh: CLK_FREQ patched to $CLK_OVERRIDE"
else
    CLK_OVERRIDE="270000000"  # default from test_bench_t0
    echo "bench-run.sh: using default CLK_FREQ (270000000)"
fi

# ---- compile the bench top ---------------------------------------------------
echo "bench-run.sh: compiling $BENCH_FILE..."

# Capture compile output and return code
COMPILE_OUT=$(mktemp -t bench-compile-out)
if ! "$PNUT" -l "$BENCH_FILE" >"$COMPILE_OUT" 2>&1; then
    echo "ERROR: compilation failed" >&2
    echo "       tier=$TIER, CLK_FREQ=$CLK_OVERRIDE, config_block_line=$((CONFIG_LINENO + 1))" >&2
    echo >&2
    cat "$COMPILE_OUT" >&2
    rm -f "$COMPILE_OUT"
    exit 2
fi
rm -f "$COMPILE_OUT"

# The binary is named after the top, with .bin extension
BINARY="${BENCH_FILE%.spin2}.bin"
if [ ! -f "$BINARY" ]; then
    echo "ERROR: compilation succeeded but binary not found: $BINARY" >&2
    echo "       tier=$TIER, CLK_FREQ=$CLK_OVERRIDE, config_block_line=$((CONFIG_LINENO + 1))" >&2
    exit 2
fi

echo "bench-run.sh: binary ready: $BINARY"

# ---- load and run on the P2 (headed, interactive) ------------------------------
echo "bench-run.sh: loading $BINARY (headed, interactive)..."
if ! "$PNUT_TERM" --ide -r "$BINARY"; then
    echo "ERROR: load/run failed" >&2
    echo "       tier=$TIER, CLK_FREQ=$CLK_OVERRIDE, config_block_line=$((CONFIG_LINENO + 1))" >&2
    exit 2
fi

# ---- curate the log -----
# pnut-term-ts saves logs to src/logs/<timestamp>.log
# We need to find the most recent log and copy it to DOCs/analyses/bench/
if [ ! -d "logs" ]; then
    echo "ERROR: no src/logs directory found after pnut-term-ts run" >&2
    exit 2
fi

# Find the most recent log file (by modification time)
LATEST_LOG=$(ls -t logs/*.log 2>/dev/null | head -1)
if [ -z "$LATEST_LOG" ]; then
    echo "ERROR: no log file found in src/logs/ after pnut-term-ts run" >&2
    exit 2
fi

# Create the curated log directory structure: DOCs/analyses/bench/<date>/
DATE=$(date +%Y-%m-%d)
BENCH_LOGS_DIR="${PROJECT_ROOT}/DOCs/analyses/bench/${DATE}"
mkdir -p "$BENCH_LOGS_DIR" || exit 2

# Name the curated log: <tier>[-<clk>].log
# If CLK_OVERRIDE == 270000000 (default), omit the clock suffix
if [ "$CLK_OVERRIDE" = "270000000" ]; then
    CURATED_LOG="${BENCH_LOGS_DIR}/${TIER}.log"
else
    CURATED_LOG="${BENCH_LOGS_DIR}/${TIER}-${CLK_OVERRIDE}.log"
fi

# Copy the log
cp "$LATEST_LOG" "$CURATED_LOG" || exit 2
echo "bench-run.sh: log curated: $CURATED_LOG"

exit 0

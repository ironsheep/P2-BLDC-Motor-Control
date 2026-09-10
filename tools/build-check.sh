#!/bin/bash
#
# build-check.sh -- compile gate for P2-BLDC-Motor-Control
#
# The user configuration file carries several mutually-exclusive config
# blocks; exactly one is active at a time (its opening brace is commented
# as '{ rather than {). A single-motor config cannot compile the dual-motor
# tops and vice versa, so "compile everything" is not a thing you can do in
# one pass. This walks every config block in turn.
#
# Enforced:
#   1. Every library object compiles under EVERY config block.
#   2. Every top-level file compiles under AT LEAST ONE config block.
#   3. RELEASE CERTIFICATION: both flagship demos -- demo_single_motor and
#      demo_dual_motor -- compile. Neither ships uncertified.
#
# The user config file is restored on exit, including on interrupt.
#
# Usage:  tools/build-check.sh [-v]      (-v lists per-config detail)

set -u

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SRC_DIR="${SCRIPT_DIR}/../src"
CONFIG="isp_bldc_motor_userconfig.spin2"
PNUT="${PNUT_TS:-/Applications/pnut_ts/pnut-ts}"

VERBOSE=0
[ "${1:-}" = "-v" ] && VERBOSE=1

# Objects that must compile regardless of which config is active.
LIB_OBJECTS="isp_bldc_motor isp_steering_2wheel isp_bldc_motor_userconfig
             isp_dist_utils isp_queue_serial isp_mem_strings"

# Demos that gate a release. Both must compile before anything ships.
RELEASE_TOPS="demo_single_motor demo_dual_motor"

if [ ! -x "$PNUT" ]; then
    echo "ERROR: pnut-ts not found at $PNUT (override with PNUT_TS=/path)" >&2
    exit 2
fi

cd "$SRC_DIR" || exit 2

# ---- reference/legacy sources must never enter the build ----------------
# These live in the repo ROOT as read-only history (Chip's original driver,
# superseded copies) and are gitignored. The gate only ever runs in src/, so
# they are out of scope by construction -- but a stray copy landing in src/
# would be compiled, and worse, could shadow the real object. Fail loudly.
STRAY=$(ls *-REF.spin2 *-OLD.spin2 angleTest.spin2 BLDC_Motor_Driver*.spin2 \
        2>/dev/null)
if [ -n "$STRAY" ]; then
    echo "ERROR: reference/legacy source found in src/ -- these belong in the" >&2
    echo "       repo root as history and must never be built:" >&2
    for s in $STRAY; do echo "         src/$s" >&2; done
    exit 2
fi

# ---- restore the user's config no matter how we leave -------------------
BACKUP="$(mktemp -t bldc-userconfig)"
cp -p "$CONFIG" "$BACKUP"
cleanup() {
    cp -p "$BACKUP" "$CONFIG"
    rm -f "$BACKUP"
    rm -f ./*.bin ./*.lst 2>/dev/null
}
trap cleanup EXIT INT TERM

# ---- discover the config blocks -----------------------------------------
# Emits one "lineno:kind" row per block opener, kind = single|dual.
# (macOS ships bash 3.2 -- no mapfile, no associative arrays. Newline-
# delimited strings throughout.)
BLOCKS=$(python3 - "$CONFIG" <<'PYEOF'
import re, sys
lines = open(sys.argv[1]).read().split('\n')
# The config region ends at the "Adjust your configuration ABOVE here" marker;
# past it lie doc-comment braces that are not config blocks.
end = next((i for i, l in enumerate(lines)
            if 'Adjust your configuration' in l), len(lines))
i, out = 0, []
while i < end:
    if re.match(r"^'?\{\s*$", lines[i]):
        body = []
        j = i + 1
        while j < end and not re.match(r"^'?\}\s*$", lines[j]):
            body.append(lines[j]); j += 1
        text = '\n'.join(body)
        if 'LEFT_MOTOR_BASE' in text:
            kind = 'dual'
        elif 'ONLY_MOTOR_BASE' in text:
            kind = 'single'
        else:
            kind = 'other'
        if kind != 'other':
            out.append(f"{i}:{kind}")
        i = j + 1
    else:
        i += 1
print('\n'.join(out))
PYEOF
)

if [ -z "$BLOCKS" ]; then
    echo "ERROR: found no config blocks in $CONFIG" >&2
    exit 2
fi
N_BLOCKS=$(printf '%s\n' "$BLOCKS" | wc -l | tr -d ' ')

# Activate block whose opener is at 0-based line $1; comment out all others.
activate() {
    python3 - "$CONFIG" "$1" <<'PYEOF'
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
}

# The candidate list is derived MECHANICALLY from the tree, not hand-maintained
# -- a hand-kept list silently drifts behind the files and reports green because
# the missing ones were never compiled, not because they passed.
#
# Exclusions must be named here with a reason, and are printed on every run.
# Nothing is excluded silently.
EXCLUDED="hng034rm"
# hng034rm  -- dead. Requires a DAT preload of vgafont.def, which is not in the
#              repo, so it cannot compile. Its only reference (isp_hdmi_debug.spin2
#              line 36) is commented out. Tracked in git but built by nothing.
#              Remove the file or restore vgafont.def, then drop this exclusion.

TOPS=$(ls *.spin2 2>/dev/null | sed 's/\.spin2$//' \
       | while read -r n; do
             skip=0
             for x in $EXCLUDED; do [ "$n" = "$x" ] && skip=1; done
             [ $skip -eq 0 ] && echo "$n"
         done)

# PASSED holds "name=label" rows, one per certified top.
PASSED=""
N_PASSED=0
FAILED_LIB=0
N_TOPS=$(echo $TOPS | wc -w | tr -d ' ')

passed_label() {   # $1 = top name; echoes its label, empty if not yet passed
    printf '%s\n' "$PASSED" | sed -n "s/^$1=//p" | head -1
}

echo "P2-BLDC-Motor-Control build gate -- $N_BLOCKS config blocks, $N_TOPS files"
if [ -n "$EXCLUDED" ]; then
    echo "  excluded (not examined):"
    for x in $EXCLUDED; do echo "    $x -- see EXCLUDED in $(basename "$0") for why"; done
fi
echo

for row in $BLOCKS; do
    lineno="${row%%:*}"
    kind="${row##*:}"
    activate "$lineno"
    label="config@line$((lineno + 1)) ($kind)"

    # 1. library objects must compile under this config
    for obj in $LIB_OBJECTS; do
        if ! "$PNUT" -q "$obj.spin2" >/dev/null 2>&1; then
            echo "  FAIL  [$label] library object $obj"
            FAILED_LIB=1
        fi
    done

    # 2. tops: try the ones not yet known good
    n_new=0
    for top in $TOPS; do
        [ -n "$(passed_label "$top")" ] && continue
        if "$PNUT" -q "$top.spin2" >/dev/null 2>&1; then
            PASSED="$PASSED
$top=$label"
            N_PASSED=$((N_PASSED + 1))
            n_new=$((n_new + 1))
            [ $VERBOSE -eq 1 ] && echo "  ok    [$label] $top"
        fi
    done
    [ $VERBOSE -eq 0 ] && echo "  $label: objects ok, +$n_new tops newly certified"
    rm -f ./*.bin ./*.lst 2>/dev/null
done

echo
RC=0
[ $FAILED_LIB -ne 0 ] && RC=1

# 3. every top must have compiled somewhere
UNBUILT=""
for top in $TOPS; do
    [ -z "$(passed_label "$top")" ] && UNBUILT="$UNBUILT $top"
done
if [ -n "$UNBUILT" ]; then
    echo "FAIL: tops that compile under no config:$UNBUILT"
    RC=1
fi

# 4. release certification -- both flagship demos
echo "Release certification:"
for top in $RELEASE_TOPS; do
    lbl=$(passed_label "$top")
    if [ -n "$lbl" ]; then
        echo "  CERTIFIED  $top  ($lbl)"
    else
        echo "  BLOCKED    $top  -- compiles under no config block"
        RC=1
    fi
done

echo
if [ $RC -eq 0 ]; then
    echo "PASS: $N_PASSED/$N_TOPS tops certified; both release demos certified."
else
    echo "FAIL: build gate not satisfied -- see above."
fi
exit $RC

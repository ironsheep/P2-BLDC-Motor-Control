#!/bin/bash
#
# build-check.sh -- compile gate for P2-BLDC-Motor-Control
#
# The user configuration file carries two configurations, selected by a
# preprocessor symbol: CFG_SINGLE_MOTOR or CFG_DUAL_MOTOR. A top-level program
# selects one itself (#DEFINE plus #PRAGMA EXPORTDEF at its top); with neither,
# the config refuses to compile. So the gate never edits the config: it compiles
# each program as written, and compiles objects under each symbol with -D.
#
# Enforced:
#   1. Every library object compiles under EVERY configuration (-D each symbol).
#   2. Every file in src/ and test/ compiles: a program that selects its
#      configuration compiles as written; any other file compiles under AT LEAST
#      ONE configuration. test/ holds the bench; it builds against src/ (-I).
#   3. The config refuses a build that selects no configuration, with its
#      message (the negative case: a silent fallback would drive a motor with
#      another motor's settings).
#      The config refuses an illegal or overlapping motor pin group: copies of it with
#      one bad choice each must stop at the CHECK_ line that names the mistake (3a).
#      Every PNut-TS-only directive (#PRAGMA, #ERROR, #WARN, #INCLUDE) sits directly inside
#      #IFDEF __PNUT_TS__, so PNut can still build the sources.
#   4. RELEASE CERTIFICATION: both flagship demos -- demo_single_motor and
#      demo_dual_motor -- compile. Neither ships uncertified. Every demo_* top
#      must also compile with -d (DEBUG), which a plain compile never checks.
#   5. Every bench tier's DEBUG footprint is within the limit measured to run
#      intact, checked through test/bench-run.sh's own tier table in
#      measure-only mode -- so an image that would lose its last debug()
#      records fails here, at commit time, not at the rig.
#
# Nothing in src/ or test/ is modified; every image it compiles is removed as
# soon as it is built.
#
# Usage:  tools/build-check.sh [-v]      (-v lists per-file detail)

set -u

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SRC_DIR="$(cd "${SCRIPT_DIR}/../src" && pwd)"
TEST_DIR="$(cd "${SCRIPT_DIR}/../test" && pwd)"
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

# ---- clean up our own outputs no matter how we leave --------------------
FP_DIR=""                                       # step 5's per-tier results, removed here too
cleanup() {
    rm -f ./*.bin ./*.lst "$SRC_DIR"/.build-check-*.bin "$TEST_DIR"/.build-check-*.bin 2>/dev/null
    [ -n "$FP_DIR" ] && rm -rf "$FP_DIR"
}
trap cleanup EXIT
trap 'exit 130' INT
trap 'exit 143' TERM

# Every compile sees both folders, by absolute path (pnut-ts resolves a relative -I against the
# top file's folder). pnut-ts also writes -o relative to the top file's folder, so each image
# gets a name of this script's own beside its source and is removed straight after.
compile() {   # compile [flags...] <name>: a file in src/ or test/, by name
    local name="${!#}" path out rc
    path="$SRC_DIR/$name.spin2"
    [ -f "$path" ] || path="$TEST_DIR/$name.spin2"
    out=".build-check-$name.bin"
    "$PNUT" -q -I "$SRC_DIR" -I "$TEST_DIR" -o "$out" "${@:1:$#-1}" "$path"
    rc=$?
    rm -f "$(dirname "$path")/$out"
    return $rc
}
path_of() {   # $1 = name; echoes its file in src/ or test/
    if [ -f "$SRC_DIR/$1.spin2" ]; then echo "$SRC_DIR/$1.spin2"; else echo "$TEST_DIR/$1.spin2"; fi
}

# The configuration symbols, and the message the config gives when a build selects neither.
# (macOS ships bash 3.2 -- no mapfile, no associative arrays. Newline- or space-delimited
# strings throughout.)
CFG_SYMBOLS="CFG_SINGLE_MOTOR CFG_DUAL_MOTOR"
NO_CFG_MESSAGE="No configuration selected"
N_CFGS=$(echo $CFG_SYMBOLS | wc -w | tr -d ' ')

selects_config() {   # $1 = file; echoes the CFG_* symbol the file #DEFINEs for itself, empty if none
    sed -nE 's/^#[Dd][Ee][Ff][Ii][Nn][Ee][[:space:]]+(CFG_[A-Z_]+).*/\1/p' "$1" | head -1
}

# The candidate list is derived MECHANICALLY from the tree, not hand-maintained
# -- a hand-kept list silently drifts behind the files and reports green because
# the missing ones were never compiled, not because they passed.
#
# Exclusions must be named here with a reason, and are printed on every run.
# Nothing is excluded silently.
EXCLUDED=""

TOPS=$( (cd "$SRC_DIR" && ls *.spin2; cd "$TEST_DIR" && ls *.spin2) 2>/dev/null | sed 's/\.spin2$//' \
       | while read -r n; do
             skip=0
             for x in $EXCLUDED; do [ "$n" = "$x" ] && skip=1; done
             [ $skip -eq 0 ] && echo "$n"
         done)

# PASSED holds "name=label" rows, one per certified top.
PASSED=""
N_PASSED=0
DEBUG_FAILED=""                                  # demo_* tops that compile plain but not with -d
FAILED_LIB=0
N_TOPS=$(echo $TOPS | wc -w | tr -d ' ')

passed_label() {   # $1 = top name; echoes its label, empty if not yet passed
    printf '%s\n' "$PASSED" | sed -n "s/^$1=//p" | head -1
}

echo "P2-BLDC-Motor-Control build gate -- $N_CFGS configurations ($CFG_SYMBOLS), $N_TOPS files"
if [ -n "$EXCLUDED" ]; then
    echo "  excluded (not examined):"
    for x in $EXCLUDED; do echo "    $x -- see EXCLUDED in $(basename "$0") for why"; done
fi
echo

# 1. library objects must compile under every configuration
for sym in $CFG_SYMBOLS; do
    for obj in $LIB_OBJECTS; do
        if ! compile -D "$sym" "$obj" >/dev/null 2>&1; then
            echo "  FAIL  [-D $sym] library object $obj"
            FAILED_LIB=1
        fi
    done
done
[ $VERBOSE -eq 0 ] && [ $FAILED_LIB -eq 0 ] && echo "  library objects: ok under every configuration"

# 2. every file: a program that selects its configuration compiles as written; any other file
#    under at least one configuration
for top in $TOPS; do
    sym=$(selects_config "$(path_of "$top")")
    label=""
    if [ -n "$sym" ]; then
        compile "$top" >/dev/null 2>&1 && label="selects $sym"
    else
        for try in $CFG_SYMBOLS; do
            if compile -D "$try" "$top" >/dev/null 2>&1; then
                label="-D $try"
                break
            fi
        done
    fi
    [ -z "$label" ] && continue
    PASSED="$PASSED
$top=$label"
    N_PASSED=$((N_PASSED + 1))
    [ $VERBOSE -eq 1 ] && echo "  ok    [$label] $top"
    # a shipped demo must also compile with DEBUG -- a plain compile skips every debug()
    #  line, so a broken one would ship unseen
    case "$top" in
        demo_*)
            dflag=""
            [ -z "$sym" ] && dflag="-D ${label#-D }"
            if ! compile -d $dflag "$top" >/dev/null 2>&1; then
                DEBUG_FAILED="$DEBUG_FAILED $top"
                echo "  FAIL  [$label] $top does not compile with -d (DEBUG)"
            fi
            ;;
    esac
done
rm -f ./*.bin ./*.lst 2>/dev/null
[ $VERBOSE -eq 0 ] && echo "  files: $N_PASSED of $N_TOPS compile"

echo
RC=0
[ $FAILED_LIB -ne 0 ] && RC=1

UNBUILT=""
for top in $TOPS; do
    [ -z "$(passed_label "$top")" ] && UNBUILT="$UNBUILT $top"
done
if [ -n "$UNBUILT" ]; then
    echo "FAIL: files that compile under no configuration:$UNBUILT"
    RC=1
fi
if [ -n "$DEBUG_FAILED" ]; then
    echo "FAIL: demos that do not compile with -d (DEBUG):$DEBUG_FAILED"
    RC=1
fi

# 3. the negative case: with no configuration selected, the config refuses, with its message
NOCFG_OUT=$("$PNUT" -q "$CONFIG" 2>&1)
NOCFG_RC=$?
rm -f ./*.bin ./*.lst 2>/dev/null
if [ $NOCFG_RC -ne 0 ] && printf '%s\n' "$NOCFG_OUT" | grep -q "$NO_CFG_MESSAGE"; then
    echo "No configuration selected: refused, with its message (as it must be)"
else
    echo "FAIL: $CONFIG compiled with no configuration selected, or refused without '$NO_CFG_MESSAGE'"
    RC=1
fi

# 3a. the pin-group checks: a copy of the config (in a temporary directory, never src/) with one bad
#     pin choice must refuse with "Divide by zero" AT the CHECK_ line that names the mistake; the swapped
#     legal pair must compile. Each copy differs from the config only in the line the sed sets.
PIN_TMP=$(mktemp -d)
pin_case() {    # $1 symbol, $2 sed expression for the copy, $3 expected CHECK_ name or "compiles"
    sed -e "$2" "$CONFIG" > "$PIN_TMP/$CONFIG"
    if cmp -s "$CONFIG" "$PIN_TMP/$CONFIG"; then
        echo "FAIL: pin-group case '$2' changed nothing in the copy"; RC=1; return
    fi
    echo "+ $PNUT -q -D $1 $CONFIG   (copy in $PIN_TMP: $2)"
    local out rc line
    out=$(cd "$PIN_TMP" && "$PNUT" -q -D "$1" "$CONFIG" 2>&1); rc=$?
    if [ "$3" = "compiles" ]; then
        if [ $rc -eq 0 ]; then echo "    compiles (as it must)"; else
            echo "FAIL: a legal pin choice was refused: $(printf '%s\n' "$out" | grep -m1 -i error)"; RC=1; fi
        return
    fi
    line=$(printf '%s\n' "$out" | sed -n "s/^$CONFIG:\([0-9][0-9]*\):error:Divide by zero.*/\1/p" | head -1)
    if [ $rc -ne 0 ] && [ -n "$line" ] && sed -n "${line}p" "$PIN_TMP/$CONFIG" | grep -q "^ *$3 = "; then
        echo "    refused at line $line, $3 (as it must be)"
    else
        echo "FAIL: expected a refusal at $3; got exit $rc: $(printf '%s\n' "$out" | grep -m1 -i error)"; RC=1
    fi
}
pin_case CFG_DUAL_MOTOR 's/^\(    RIGHT_MOTOR_BASE = \).*/\1PINS_NO_USE_P24_P39/;s/^\(    LEFT_MOTOR_BASE = \).*/\1PINS_P16_P31/' CHECK_RIGHT_PIN_GROUP
pin_case CFG_DUAL_MOTOR 's/^\(    LEFT_MOTOR_BASE = \).*/\1PINS_P16_P31/;s/^\(    RIGHT_MOTOR_BASE = \).*/\1PINS_P8_P23/' CHECK_GROUPS_APART
pin_case CFG_DUAL_MOTOR 's/^\(    LEFT_MOTOR_BASE = \).*/\1PINS_P32_P47/;s/^\(    RIGHT_MOTOR_BASE = \).*/\1PINS_P32_P47/' CHECK_GROUPS_APART
pin_case CFG_SINGLE_MOTOR 's/^\(    ONLY_MOTOR_BASE = \).*/\1PINS_NO_USE_P24_P39/' CHECK_ONLY_PIN_GROUP
pin_case CFG_DUAL_MOTOR 's/^\(    LEFT_MOTOR_BASE = \).*/\1PINS_P32_P47/;s/^\(    RIGHT_MOTOR_BASE = \).*/\1PINS_P16_P31/' compiles
rm -rf "$PIN_TMP"

# 3b. PNut stays able to build the sources: every PNut-TS-only directive (#PRAGMA, #ERROR, #WARN,
#     #INCLUDE) must sit directly inside #IFDEF __PNUT_TS__, the symbol only PNut-TS defines (DEVELOP.md,
#     "Building with PNut"). PNut-TS itself cannot show a missing guard, so this reads the source.
UNGUARDED=$(awk '
    FNR == 1 { prev = "" }
    /^[[:space:]]*#(PRAGMA|ERROR|WARN|INCLUDE)([[:space:]]|$)/ && toupper(prev) !~ /^[[:space:]]*#IFDEF[[:space:]]+__PNUT_TS__[[:space:]]*$/ {
        print "    " FILENAME ":" FNR ": " $0
    }
    /[^[:space:]]/ { prev = $0 }
' $(for top in $TOPS; do path_of "$top"; done))
if [ -n "$UNGUARDED" ]; then
    echo "FAIL: PNut-TS-only directives outside #IFDEF __PNUT_TS__ (PNut could not build these):"
    printf '%s\n' "$UNGUARDED"
    RC=1
else
    echo "PNut-TS-only directives: every one inside #IFDEF __PNUT_TS__"
fi

# 4. release certification -- both flagship demos
echo "Release certification:"
for top in $RELEASE_TOPS; do
    lbl=$(passed_label "$top")
    if [ -n "$lbl" ] && printf '%s\n' $DEBUG_FAILED | grep -qx "$top"; then
        echo "  BLOCKED    $top  -- does not compile with -d (DEBUG)"
        RC=1
    elif [ -n "$lbl" ]; then
        echo "  CERTIFIED  $top  ($lbl, plain and -d)"
    else
        echo "  BLOCKED    $top  -- does not compile"
        RC=1
    fi
done

# 5. every bench tier's DEBUG footprint -- the limit and its reasons live in
#    test/bench-run.sh beside the gate that refuses a run; this only walks its tiers.
#    The tier list is read from bench-run.sh's case labels (4-space indent), and
#    finding NONE is a failure, never a clean pass.
echo
echo "Bench-tier DEBUG footprint (test/bench-run.sh measure-only):"
BENCH_RUN="${TEST_DIR}/bench-run.sh"
# The dual-clock-270 and -300 tiers are skipped: measure-only never applies a clock, so
# they compile exactly what dual-clock-200 compiles, and it stands for all three.
TIERS=$(sed -nE 's/^    ([a-z0-9|-]+)\).*/\1/p' "$BENCH_RUN" | tr '|' '\n' \
        | grep -vx -e 'dual-clock' -e 'dual-clock-270' -e 'dual-clock-300')
if [ -z "$TIERS" ]; then
    echo "  FAIL  no tiers found in $BENCH_RUN -- the footprint was not checked"
    RC=1
fi
# Tiers are measured in parallel (each writes its own images, see bench-run.sh), one
# output and one exit status per tier, then judged in tier order. bench-run.sh's exit
# status is the verdict; its output supplies only the number printed beside it.
FP_DIR="$(mktemp -d "${TMPDIR:-/tmp}/bldc-footprint.XXXXXX")" || { echo "ERROR: no temp dir" >&2; exit 2; }
JOBS=$(getconf _NPROCESSORS_ONLN 2>/dev/null || echo 4)
printf '%s\n' $TIERS | xargs -P "$JOBS" -I{} sh -c \
    'PNUT_TS="$1" BENCH_MEASURE_ONLY=1 "$2" "$3" > "$4/$3.out" 2>/dev/null; echo $? > "$4/$3.rc"' \
    _ "$PNUT" "$BENCH_RUN" {} "$FP_DIR"
for tier in $TIERS; do
    out=$(cat "$FP_DIR/$tier.out" 2>/dev/null)
    fp=$(printf '%s\n' "$out" | sed -n 's/^bench-run.sh: DEBUG footprint \([0-9]*\) bytes.*/\1/p')
    if [ "$(cat "$FP_DIR/$tier.rc" 2>/dev/null)" = "0" ]; then
        [ $VERBOSE -eq 1 ] && echo "  ok    $tier  $fp bytes"
    else
        echo "  FAIL  $tier  ${fp:-no measurement} -- $(printf '%s\n' "$out" | grep -m1 '^ERROR:' | cut -c8-)"
        RC=1
    fi
done
[ $VERBOSE -eq 0 ] && [ $RC -eq 0 ] && echo "  all $(echo $TIERS | wc -w | tr -d ' ') tiers within the limit"

echo
if [ $RC -eq 0 ]; then
    echo "PASS: $N_PASSED/$N_TOPS tops certified; both release demos certified; every bench tier within the DEBUG footprint limit."
else
    echo "FAIL: build gate not satisfied -- see above."
fi
exit $RC

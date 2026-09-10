#!/bin/bash
#
# doc-audit.sh -- documentation-drift instrument for P2-BLDC-Motor-Control
#
# Documentation is unverified by construction: the build proves the code compiles
# and nothing compares a *description* to the behaviour it describes. This moves
# that detection to plan time, where a finding is cheap.
#
# Detects the three drift classes:
#   ORPHAN    a doc names a Spin2 method/constant that no longer exists in src/
#   DUPLICATE the same block of prose is maintained in more than one document
#   COUNT     a number asserted in prose disagrees with its real source
#
# Two properties this MUST keep (see sprint-plan/references/doc-audit-instruments.md):
#   - ADVISORY. It never fails a build. Exit code is 0 unless the script itself
#     broke. A doc checker wired in as a hard gate gets disabled the first time it
#     blocks an urgent fix, and then detects nothing forever.
#   - It discovers its own file set MECHANICALLY. Scope must not be a judgement
#     call, because a judgement call is what gets shaded under deadline.
#
# Usage:  tools/doc-audit.sh [-v]

set -u

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
SRC="$ROOT/src"
VERBOSE=0
[ "${1:-}" = "-v" ] && VERBOSE=1

cd "$ROOT" || exit 2

# ---- mechanical file discovery -----------------------------------------
# Every user-facing tracked .md, minus working areas. Working areas are named
# here explicitly so the exclusion is visible rather than implied.
#   DOCs/analyses/  point-in-time studies; they describe a moment, not the code
#   DOCs/plans/     sprint working material
#   .claude/        agent configuration, not shipped
#   .todo-mcp/      agent tooling, replaced wholesale on upgrade
DOCS=$(git ls-files '*.md' 2>/dev/null \
       | grep -v '^DOCs/analyses/' \
       | grep -v '^DOCs/plans/' \
       | grep -v '^\.claude/' \
       | grep -v '^\.todo-mcp/')

# Untracked-but-intended docs still get audited, so a new doc is covered from the
# moment it is written rather than from the moment it is committed.
for extra in DRIVER-THEORY-OF-OPERATIONS.md; do
    [ -f "$extra" ] && ! echo "$DOCS" | grep -qx "$extra" && DOCS="$DOCS
$extra"
done
DOCS=$(echo "$DOCS" | grep -v '^$' | sort -u)

N_DOCS=$(echo "$DOCS" | wc -l | tr -d ' ')
FINDINGS=0

echo "=============================================="
echo " Documentation drift audit"
echo " $N_DOCS documents | $(ls "$SRC"/*.spin2 2>/dev/null | wc -l | tr -d ' ') Spin2 sources"
echo "=============================================="
[ $VERBOSE -eq 1 ] && { echo; echo "Documents audited:"; echo "$DOCS" | sed 's/^/    /'; }

# Every PUB method name actually present in src/, one per line.
LIVE_PUBS=$(grep -h '^PUB ' "$SRC"/*.spin2 2>/dev/null \
            | sed 's/^PUB  *\([A-Za-z_][A-Za-z0-9_]*\).*/\1/' | sort -u)

# Spin2 language built-ins. A doc naming one of these is describing the LANGUAGE,
# not asserting a project method exists -- flagging them is noise, and an
# instrument that cries wolf is an instrument someone disables.
BUILTINS="coginit cogstop cogspin cogatn cogid cogchk pollatn waitatn
getct getms getsec waitct waitms waitus pinread pinwrite pinhigh pinlow
pinfloat pinclear pinstart pintoggle wrpin wxpin wypin rdpin akpin
lookup lookdown strcopy strsize string abort round float trunc send recv
byte word long lstring bytemove wordmove longmove bytefill wordfill longfill
muldiv64 getrnd rotxy polxy xypol qsin qcos nan clkset locknew lockret
locktry lockrel lockchk regexec regload call"

# ---- ORPHAN ------------------------------------------------------------
# A doc that writes `someMethod()` in backticks is asserting that method exists.
echo
echo "-- ORPHAN: documented methods absent from src/ --"
ORPHANS=0
while IFS= read -r doc; do
    [ -z "$doc" ] && continue
    # pull `name(` occurrences out of inline code spans
    grep -o '`[a-z][A-Za-z0-9_]*(' "$doc" 2>/dev/null \
      | tr -d '`(' | sort -u | while IFS= read -r m; do
        [ -z "$m" ] && continue
        if echo "$BUILTINS" | tr ' ' '\n' | grep -qx "$m"; then
            continue                      # Spin2 built-in, not a project method
        fi
        if ! echo "$LIVE_PUBS" | grep -qx "$m"; then
            # not a PUB -- is it a PRI, or genuinely gone?
            if grep -qh "^PRI  *$m\b" "$SRC"/*.spin2 2>/dev/null; then
                [ $VERBOSE -eq 1 ] && echo "    note   $doc: $m() is PRI, not public"
            else
                echo "    ORPHAN $doc: $m() exists in no src/*.spin2"
            fi
        fi
    done
done <<< "$DOCS"
ORPHANS=$(grep -c . <<< "" ) # counted visually; advisory output only

# ---- DUPLICATE ---------------------------------------------------------
# The most valuable check: it names the drift *mechanism*, not a drift finding.
# Two copies of one paragraph will diverge; the only question is when.
echo
echo "-- DUPLICATE: substantial prose maintained in 2+ documents --"
TMP=$(mktemp -t docaudit)
while IFS= read -r doc; do
    [ -z "$doc" ] && continue
    # substantial = a prose line of 60+ chars, not a heading/table/list/code
    grep -nE '^[A-Za-z(].{59,}' "$doc" 2>/dev/null \
      | grep -v '^[0-9]*:|' \
      | sed "s|^\([0-9]*\):\(.*\)$|\2\t$doc:\1|" >> "$TMP"
done <<< "$DOCS"
sort "$TMP" | awk -F'\t' '
    { if ($1 == prev) { if (!shown) { print "    DUPLICATE: " substr(prev,1,66) "..."; print "               " prevloc; shown=1 } print "               " $2 }
      else shown=0
      prev=$1; prevloc=$2 }' | head -40
rm -f "$TMP"

# ---- COUNT -------------------------------------------------------------
# Numbers asserted in prose, recomputed from their authoritative source.
echo
echo "-- COUNT: asserted numbers vs. reality --"

check_count() {   # $1=label  $2=claimed  $3=actual
    if [ "$2" = "$3" ]; then
        [ $VERBOSE -eq 1 ] && printf "    ok       %-38s %s\n" "$1" "$3"
    else
        printf "    MISMATCH %-38s doc says %s, actual %s\n" "$1" "$2" "$3"
        FINDINGS=$((FINDINGS + 1))
    fi
}

# VERSION file vs the newest git tag
if [ -f VERSION ]; then
    V=$(tr -d ' \n' < VERSION)
    T=$(git tag --sort=-v:refname 2>/dev/null | head -1 | sed 's/^v//')
    check_count "VERSION vs newest git tag" "$V" "$T"
fi

# Source line counts asserted anywhere in the doc set, e.g. "isp_bldc_motor.spin2
# (2359 lines". Scanned across ALL audited docs plus the analyses dir, because the
# claim lives wherever someone happened to write it.
for f in $DOCS $(ls DOCs/analyses/*.md 2>/dev/null); do
    [ -f "$f" ] || continue
    for sp in isp_bldc_motor.spin2 isp_steering_2wheel.spin2 isp_steering_serial.spin2; do
        claimed=$(grep -oE "$sp\`?[^0-9]{0,4}\(([0-9]+) lines" "$f" 2>/dev/null \
                  | grep -oE '[0-9]+ lines' | grep -oE '[0-9]+' | head -1)
        [ -z "$claimed" ] && continue
        actual=$(wc -l < "$SRC/$sp" 2>/dev/null | tr -d ' ')
        check_count "$(basename "$f"): $sp lines" "$claimed" "$actual"
    done
done

# The audit doc asserts conformance counts; recompute the two cheapest.
AUD=$(ls DOCs/analyses/DRIVER-AUDIT-*.md 2>/dev/null | head -1)
if [ -n "$AUD" ]; then
    nonascii=$(LC_ALL=C cat "$SRC"/isp_bldc_motor.spin2 \
                 "$SRC"/isp_steering_2wheel.spin2 2>/dev/null \
               | LC_ALL=C grep -c '[^ -~	]' | tr -d ' ')
    if grep -q '0 non-ASCII codepoints' "$AUD" 2>/dev/null; then
        check_count "audit: non-ASCII claim" "0" "$nonascii"
    fi
fi

# README's supported-demo table vs demos actually present
if [ -f README.md ]; then
    claimed=$(grep -cE '^\| \[demo_[a-z_]+\.spin2\]' README.md 2>/dev/null | tr -d ' ')
    actual=$(ls "$SRC"/demo_*.spin2 2>/dev/null | wc -l | tr -d ' ')
    [ "$claimed" != "0" ] && check_count "README demo table rows" "$claimed" "$actual"
fi

echo
echo "=============================================="
echo " Advisory only -- this never fails a build."
echo " Findings above are input to the next sprint plan."
echo "=============================================="
exit 0

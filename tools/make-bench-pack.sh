#!/bin/bash
#
# make-bench-pack.sh -- one zip of prebuilt bench binaries, to send to the rig
#
# STEPHEN 2026-09-28: "i need pre-compiled binaries for our test runs zipped up so i can send one file to the test
# revB platform unpack it and then run them" ... "then the test script for me is then which binary to run for each
# test".
#
# Usage:  tools/make-bench-pack.sh [<tier> ...]
#
#   <tier>  bench tiers to include, by the names tools/bench-run.sh knows. With none, the next visit's set: the
#           hands-off rerun after FLOOR-VISIT-EVALUATION.md (2026-09-30; Plan A section 10) -- one command per physical
#           setup: t0-reva (Rev A, bench), floor-auto (spins, fault run, ramp legs), floor-obstacle (coast and brake
#           trials), floor-grab (the one attended load) and floor-rc (STEPHEN 2026-09-30, R9: "I have no reason why you'd
#           carry anything that's done in the pack"; R15: several checks per command when none needs him).
#   <tier>@<clock>  a tier built at a named clock (task 3675; the clock NAMES are bench-run.sh's clock table: clk-200 ...),
#           stored as <tier>@<clock>.bin -- one tier can be in the pack at several clocks, e.g. dual-clock@clk-200
#           dual-clock@clk-350. The packaged ./bench-run.sh <tier> <clock> picks that binary by the same name. The Doco
#           tiers (doco-demo-v12p0 ... one per told drive voltage) are named here like any other.
#
# Builds from the COMMITTED tree (git archive of HEAD), never the working directory, so the zip is exactly a commit.
# Each tier is compiled by that tree's own tools/bench-run.sh (BENCH_PACK_DIR mode): the same one -l -d compile, with
# the same -D flags, that a run at the bench would make. The zip holds one folder:
#
#   bench-<commit>/
#     bench-run.sh     the runner itself; run from here it compiles nothing and runs <tier>.bin
#     BENCH-PACKAGE    the commit, when it was built, and each binary's SHA-256 (every banner also prints the commit)
#     README.txt       per test: its binary, what to type, and the exact pnut-term-ts line that runs
#     <tier>.bin
#     *.bmp            every file a binary loads at run time (a panel's LAYER bitmaps), read from the binary itself
#
# One folder, no subfolders: each binary sits beside the bitmaps it loads, as it does in src/ (2026-09-29 14:16: a
# pack with the binaries in bins/ loaded no layer; tools/bench-run.sh's PREBUILT note says why).
#
# At the rig: unzip it, cd into the folder, and run ./bench-run.sh <tier>. The logs land in the folder's logs/.
# pnut-term-ts must be on the PATH; pnut-ts is not needed. Every command here is echoed, prefixed "+ ".

set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT"

run() { echo "+ $*"; "$@"; }

TIERS=("$@")
[ ${#TIERS[@]} -eq 0 ] && TIERS=(t0-reva floor-auto floor-obstacle floor-grab floor-rc)

REF="${BENCH_PACK_REF:-HEAD}"                             # a commit other than HEAD: for testing this script only
if [ "$REF" = "HEAD" ] && ! git diff --quiet HEAD -- src tools; then
    echo "NOTE: src/ or tools/ has uncommitted changes -- they are NOT in this pack, which is built from HEAD"
fi
COMMIT=$(git rev-parse --short "$REF")
NAME="bench-$COMMIT"

WORK="$(mktemp -d "${TMPDIR:-/tmp}/bldc-benchpack.XXXXXX")"
trap 'rm -rf "$WORK"' EXIT
mkdir -p "$WORK/tree" "$WORK/$NAME"
echo "+ git archive $REF | tar -x -C $WORK/tree"
git archive "$REF" | tar -x -C "$WORK/tree"

# ---- the commit goes into every binary's banner ---------------------------------------------------------------
# src/isp_bench_commit.spin2 is tracked reading NOT_A_PACK and is never edited in the tree; only the archive COPY
# here is rewritten, so every harness banner in this pack prints the commit it was built from (PL-68).
COMMIT_OBJ="$WORK/tree/src/isp_bench_commit.spin2"
run sed -i -e 's/^\(    COMMIT_PACKED = \)FALSE/\1TRUE/' -e "s/\"NOT_A_PACK\"/\"$COMMIT\"/" "$COMMIT_OBJ"
grep -q "^    COMMIT_PACKED = TRUE" "$COMMIT_OBJ" && grep -q "\"$COMMIT\"" "$COMMIT_OBJ" \
    || { echo "ERROR: could not write commit $COMMIT into $COMMIT_OBJ -- no pack built" >&2; exit 1; }

for entry in "${TIERS[@]}"; do
    echo
    echo "== $entry"
    tier="${entry%%@*}"; clock=""
    [ "$entry" != "$tier" ] && clock="${entry#*@}"
    # a tier built at a named clock: the runner stores <tier>@<clock>.bin (the clock is a NAME, bench-run.sh refuses any other)
    BENCH_PACK_DIR="$WORK/$NAME" run "$WORK/tree/tools/bench-run.sh" "$tier" ${clock:+"$clock"}
done

# ---- every file a binary asks pnut-term-ts to load comes with it ----------------------------------------------
# A panel's LAYER bitmaps are loaded by bare name, and they sit beside the binary in the folder the terminal runs
# from: src/ in the tree, the pack's own folder here. The names are read from each COMPILED binary (its DEBUG data carries them as 'name.bmp'), never from a
# list kept by hand, and a name with no file in the tree refuses the pack. (2026-09-29: the first pack carried no
# bitmaps, dual-spin's panel loaded nothing, and the floor run ended at its first screen.)
ASSETS=""
for tier in "${TIERS[@]}"; do      # here a "tier" is the entry as given: <tier> or <tier>@<clock>, the binary's own name
    # a binary that loads nothing (an unattended tier) matches nothing: grep's exit 1 there is not an error
    names=$( { LC_ALL=C grep -aoE "'[A-Za-z0-9_.-]+\.(bmp|BMP|png|PNG|jpg|JPG)'" "$WORK/$NAME/$tier.bin" || true; } | tr -d "'" | sort -u)
    for f in $names; do
        [ -f "$WORK/tree/src/$f" ] || { echo "ERROR: $tier.bin loads '$f' at run time and src/ has no such file -- no pack built" >&2; exit 1; }
        [ -f "$WORK/$NAME/$f" ] || run cp -p "$WORK/tree/src/$f" "$WORK/$NAME/$f"
        ASSETS="$ASSETS
asset $tier $f"
    done
done

cp -p "$WORK/tree/tools/bench-run.sh" "$WORK/$NAME/bench-run.sh"

# The run sheets travel with the binaries (Stephen 2026-10-04: the sheet was not at the bench). They are committed in
#  DOCs/runsheets/; every one in the packed commit is copied beside the binaries, so the sheet a pack names is in it.
for sheet in "$WORK/tree/DOCs/runsheets/"*.md; do
    [ -f "$sheet" ] && run cp -p "$sheet" "$WORK/$NAME/"
done

{
    echo "commit $COMMIT ($(git log -1 --format=%cd --date=format:'%Y-%m-%d %H:%M' "$REF")): $(git log -1 --format=%s "$REF" | cut -c1-100)"
    echo "built $(date '+%Y-%m-%d %H:%M') by tools/make-bench-pack.sh with $(pnut-ts --version 2>/dev/null | head -1 | sed 's/^pnut-ts: *//')"
    (cd "$WORK/$NAME" && sha256sum *.bin) | sed 's/^/sha256 /'
    printf '%s\n' "$ASSETS" | sed '/^$/d'
} > "$WORK/$NAME/BENCH-PACKAGE"

# README: per test, its binary, the command, and the line the runner runs -- descriptions from bench-run.sh's usage
{
    echo "Prebuilt bench binaries, commit $COMMIT"
    echo
    echo "Unzip, then in this folder:   ./bench-run.sh <test>"
    echo "It runs <test>.bin with the same safety banner and checks as the source tree's runner, and compiles"
    echo "nothing. The logs land in logs/ here. pnut-term-ts must be on the PATH."
    echo
    for entry in "${TIERS[@]}"; do
        tier="${entry%%@*}"; clock=""
        [ "$entry" != "$tier" ] && clock="${entry#*@}"
        desc=$(sed -n "s/^ \{19\}$tier  *\(.*\)/\1/p" "$WORK/tree/tools/bench-run.sh" | head -1)
        # the Doco tiers share one usage line per family, <family>-<voltage> (doco-demo-v12p0 -> doco-demo-<voltage>,
        #  single-ladder-v24p0 -> single-ladder-<voltage>)
        [ -z "$desc" ] && case "$tier" in
            doco-demo-*|single-*-v*)
                family="${tier%-v*}"
                desc=$(sed -n "s/^ \{19\}$family-<voltage>  *\(.*\)/\1/p" "$WORK/tree/tools/bench-run.sh" | head -1) ;;
        esac
        echo "$entry"
        echo "    binary:   $entry.bin"
        echo "    type:     ./bench-run.sh $tier${clock:+ $clock}"
        echo "    runs:     pnut-term-ts -u -r $entry.bin --exit-on-end-session"
        echo "    what:     $desc"
        echo
    done
} > "$WORK/$NAME/README.txt"

mkdir -p dist
rm -f "dist/$NAME.zip"
(cd "$WORK" && run zip -q -r -X "$ROOT/dist/$NAME.zip" "$NAME")

echo
echo "Bench pack ready: dist/$NAME.zip"
unzip -l "dist/$NAME.zip" | sed -n '4,$p' | grep -v -- '----' | sed 's/^/  /'

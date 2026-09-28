#!/bin/bash
#
# make-release.sh -- build a release's three archive sets and its release notes
#
# Usage:  tools/make-release.sh <vX.Y.Z> [--ref <git-ref>] [--out <dir>] [--preview]
#
#   <vX.Y.Z>    the version being released. CHANGELOG.md must carry its entry, headed
#               "## vX.Y.Z (YYYY-MM-DD)", and VERSION must read X.Y.Z.
#   --ref       the commit to package (default HEAD). Only COMMITTED files are packaged: the tree is
#               taken with `git archive`, never from the working directory.
#   --out       where the results go (default dist/<vX.Y.Z>/)
#   --preview   a local dry run before VERSION is bumped: a VERSION mismatch is reported, not refused
#
# Produces, in the output directory:
#   demo-1mot-archive-set.zip       demo_single_motor and every file it needs
#   demo-2mot-archive-set.zip       the four demo_dual_motor* demos and every file they need
#   serial-control-archive-set.zip  p2Src/ (isp_steering_serial and every file it needs) and pythonSrc/
#   release-notes.md                the version's CHANGELOG.md entry, which becomes the release page
#
# Each archive holds one folder named after it, flat like a Propeller Tool archive, with a _README_ per
# top-level program drawing its object tree. A top's files are found from its OBJ blocks by
# tools/release_closure.py, and then, when pnut-ts is on the PATH, every top is compiled from inside the
# staged folder: an archive that is missing a file fails here, not in a user's hands.
#
# The GitHub workflow .github/workflows/release.yml runs exactly this script on a pushed tag. Every
# external command is echoed, prefixed "+ ", immediately before it runs, so a run can be replayed by hand.

set -euo pipefail

usage() { sed -n '3,13p' "$0" | sed 's/^# \{0,1\}//'; exit 2; }

VERSION_TAG=""
REF="HEAD"
OUT=""
PREVIEW=0
while [ $# -gt 0 ]; do
    case "$1" in
        --ref)     REF="${2:?--ref needs a value}"; shift 2 ;;
        --out)     OUT="${2:?--out needs a value}"; shift 2 ;;
        --preview) PREVIEW=1; shift ;;
        -h|--help) usage ;;
        v*)        VERSION_TAG="$1"; shift ;;
        *)         echo "ERROR: unexpected argument '$1'" >&2; usage ;;
    esac
done
[[ "$VERSION_TAG" =~ ^v[0-9]+\.[0-9]+\.[0-9]+$ ]] || { echo "ERROR: give the version as vX.Y.Z" >&2; usage; }

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT"
OUT="${OUT:-dist/$VERSION_TAG}"

run() { echo "+ $*"; "$@"; }

# ---- the archive sets: name | top-level programs | extra files (repo paths) -----------------------------
# The names and layouts are the ones every release has shipped; changing them breaks users' links.
SET_1MOT_TOPS="demo_single_motor"
SET_2MOT_TOPS="demo_dual_motor demo_dual_motor_hdmi demo_dual_motor_rc demo_dual_motor_rc_hdmi"
SET_SERIAL_TOPS="isp_steering_serial"
SET_SERIAL_PYTHON="pythonSrc/P2-BLDC-Motor-Control-Demo.py pythonSrc/requirements.txt"

# ---- 1. the release notes: this version's CHANGELOG.md entry ----------------------------------------------
# The heading is matched in full, brackets optional and the " (" required, so v6.0.1 never matches v6.0.10.
NOTES=$(git show "$REF:CHANGELOG.md" | awk -v v="${VERSION_TAG//./\\.}" '
    $0 ~ "^## \\[?" v "\\]? \\(" { found = 1; next }
    found && /^## / { exit }
    found { print }
')
if [ -z "$(printf '%s' "$NOTES" | tr -d '[:space:]')" ]; then
    echo "ERROR: CHANGELOG.md at $REF has no entry headed '## $VERSION_TAG (YYYY-MM-DD)' -- the release page would be empty" >&2
    exit 1
fi

# ---- 2. VERSION must agree ----------------------------------------------------------------------------------
FILE_VERSION=$(git show "$REF:VERSION" 2>/dev/null | tr -d '[:space:]')
if [ "$FILE_VERSION" != "${VERSION_TAG#v}" ]; then
    if [ $PREVIEW -eq 1 ]; then
        echo "PREVIEW: VERSION at $REF reads '$FILE_VERSION', not '${VERSION_TAG#v}' -- a real release refuses this"
    else
        echo "ERROR: VERSION at $REF reads '$FILE_VERSION', not '${VERSION_TAG#v}'" >&2
        exit 1
    fi
fi

# ---- 3. the committed tree -----------------------------------------------------------------------------------
WORK="$(mktemp -d "${TMPDIR:-/tmp}/bldc-release.XXXXXX")"
trap 'rm -rf "$WORK"' EXIT
mkdir -p "$WORK/tree" "$WORK/stage"
echo "+ git archive $REF | tar -x -C $WORK/tree"
git archive "$REF" | tar -x -C "$WORK/tree"
SRC="$WORK/tree/src"
COMMIT=$(git rev-parse --short "$REF")
STAMP=$(git log -1 --format=%cd --date=format:'%Y-%m-%d %H:%M' "$REF")

PNUT="${PNUT_TS:-$(command -v pnut-ts || true)}"
PNUT_NOTE="not compiled here (pnut-ts not found)"
[ -n "$PNUT" ] && PNUT_NOTE="each top compiled from this folder by $("$PNUT" --version 2>/dev/null | head -1 | sed 's/^pnut-ts: *//')"

readme() {   # $1 = top name, $2 = destination file: the archive's _README_ for one top-level program
    {
        echo "P2-BLDC-Motor-Control -- Project Archive"
        echo
        echo "  Project  : \"$1\""
        echo "  Release  : $VERSION_TAG  (commit $COMMIT, $STAMP)"
        echo "  Built by : tools/make-release.sh; $PNUT_NOTE"
        echo
        python3 "$ROOT/tools/release_closure.py" "$SRC" "$1.spin2" tree | sed 's/^/    /'
        echo
        echo "  https://github.com/ironsheep/P2-BLDC-Motor-Control"
    } > "$2"
}

stage_set() {   # $1 = set folder (relative to the stage), $2 = README style (single|per-top), $3.. = tops
    local dir="$1" style="$2"; shift 2
    mkdir -p "$WORK/stage/$dir"
    for top in "$@"; do
        for f in $(python3 "$ROOT/tools/release_closure.py" "$SRC" "$top.spin2" files); do
            cp -p "$SRC/$f" "$WORK/stage/$dir/"
        done
        if [ "$style" = "single" ]; then
            readme "$top" "$WORK/stage/$dir/_README_.txt"
        else
            readme "$top" "$WORK/stage/$dir/_README_${top}_.txt"
        fi
    done
    if [ -n "$PNUT" ]; then
        for top in "$@"; do
            (cd "$WORK/stage/$dir" && run "$PNUT" -q "$top.spin2" > /dev/null) \
                || { echo "ERROR: $top does not compile from its archive folder $dir -- a file is missing" >&2; exit 1; }
            rm -f "$WORK/stage/$dir"/*.bin
        done
    fi
}

echo "Packaging $VERSION_TAG from $REF ($COMMIT)"
stage_set "demo-1mot-archive-set" single $SET_1MOT_TOPS
stage_set "demo-2mot-archive-set" per-top $SET_2MOT_TOPS
stage_set "serial-control-archive-set/p2Src" single $SET_SERIAL_TOPS
mkdir -p "$WORK/stage/serial-control-archive-set/pythonSrc"
for f in $SET_SERIAL_PYTHON; do
    cp -p "$WORK/tree/$f" "$WORK/stage/serial-control-archive-set/pythonSrc/"
done

# ---- 4. the zips and the notes ----------------------------------------------------------------------------------
mkdir -p "$OUT"
OUT_ABS="$(cd "$OUT" && pwd)"
for set in demo-1mot-archive-set demo-2mot-archive-set serial-control-archive-set; do
    rm -f "$OUT_ABS/$set.zip"
    (cd "$WORK/stage" && run zip -q -r -X "$OUT_ABS/$set.zip" "$set")
done
printf '%s\n' "$NOTES" | sed -e '/./,$!d' > "$OUT_ABS/release-notes.md"

echo
echo "Release $VERSION_TAG ready in $OUT:"
for set in demo-1mot-archive-set demo-2mot-archive-set serial-control-archive-set; do
    echo "  $set.zip  ($(unzip -Z1 "$OUT_ABS/$set.zip" | grep -vc '/$') files)"
done
echo "  release-notes.md  (the CHANGELOG.md entry for $VERSION_TAG)"

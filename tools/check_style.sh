#!/bin/bash
#
# check_style.sh -- Spin2 conformance gate for P2-BLDC-Motor-Control
#
# .claude/skill-conventions.md declares central:spin2-authoring-guide at
# strength:gate for src/**/*.spin2. This is that gate: it was OWED (PL-2)
# until this script existed. Unlike tools/doc-audit.sh (advisory, always
# exits 0) this is a GATE -- the guide says a FAIL is a defect like any
# other, so this exits NON-ZERO on any finding.
#
# Checks the MECHANICALLY-CHECKABLE subset of the central Spin2 authoring
# guide (~/.claude/skills-docs/guides/spin2-authoring-guide.md):
#   1.1  ASCII only (box-drawing diagram ranges excepted)
#   1.2  '=>' is always a compile error -- never a valid comparison OR case
#        range (D5: kept despite being compiler-redundant; see the check)
#   1.3  signature names colliding with the guide's known-hazard table
#   1.8  '@""' empty string literal is invalid
#   2.1  no single-letter names in PUB/PRI signatures
#   2.2  the seven ENUMERATED forbidden generic names in a signature
#        (result/value/temp/data/ret/buf/info -- NOT the judgement half)
#   4.1  '{{ }}' doc-comment used outside the license footer
#   4.2  file header carries File/Purpose/Author/E-mail/Started/Updated
#   4.2.1 file ends with a '{{ }}' license footer
#   4.3  PUB doc structure: description, blank '' separator, blank line
#        before code; @param/@returns must name a real signature element
#        (tag->element direction ONLY -- see PUNCH-LIST A1 for the
#        deferred element->tag half); @local must use ' not ''
#   4.4  PRI method docs use ' , never ''
#   4.5  CON/DAT/VAR/OBJ/PUB/PRI declaration-line comments use ' , never ''
#   4.9  no horizontal separator lines inside CON blocks
# and, added by task 3517 to cover the guide's T1 assignment:
#   1.5  no parameter, return or local named after a method in the file
#   1.9  no OBJ override of a constant the file also defines
#   2.4  a child object's constant is referenced through the object, never
#        copied into a local CON (NAME = alias.NAME re-exports are references)
#   3.1  the file opens with CON, and no OBJ block follows a method
#   3.2  every PUB precedes every PRI (PUNCH-LIST PL-11)
#   4.3  element->tag: every parameter, return and local has its @param /
#        @returns / @local tag, PUB and PRI alike (C3f, PUNCH-LIST PL-10)
#   4.5  a block declaration label is text, never a bare border (C6b)
#   5.0  no parameter or local the body never names
#   5.1  every return value is assigned
#   5.2  one exit, at the method's end; 5.3 no return inside a repeat
#   5.4  a method returning one boolean is named is/has/b; 5.4.1 no boolean
#        set to 1 or compared to 0/1
#   PL-29 (project rule): a ? : with a method call in either branch (T29)
#
# What the gate does NOT check prints on every run (COVERAGE_LINES): the T2
# rules (an agent audit), the T3 rules (Stephen's read), the T1+T2 detection
# halves, and 3.1.1. A check joins ENFORCED in the commit that brings the tree
# clean for it; until then its count prints under PENDING.
#
# Usage additions: tools/check_style.sh --pending   (the gate, listing every
#                                                    PENDING site as well)
#
# A5 reconciles guide section 4.5 (which requires '---- Label ----' on block
# declaration lines with label text) and 4.9 (which forbids bare separator
# lines inside CON blocks). The key distinction: 4.5 applies to block-decl
# lines like "CON ' ---- Error Codes ----" (with label text), while 4.9
# forbids individual separator lines inside the CON block without label text.
# A5 does not fire inside { } or {{ }} block comments, since those contents
# are not extracted into the API document.
#
# Usage:  tools/check_style.sh              (gate over src/*.spin2)
#         tools/check_style.sh --self-test   (run every check against
#                                              tools/fixtures/style/ and
#                                              assert each fires BY NAME,
#                                              and ONLY that check fires)
#
# Exit codes: 0 = no findings, 1 = one or more findings, 2 = instrument
# failure (no files discovered, python3 missing, unbalanced { } comment
# nesting at EOF -- a gate that discovers nothing has not passed, it has
# not run; see D8: a file with unbalanced braces makes every finding AND
# non-finding in it suspect).

set -u

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
SRC_DIR="$ROOT/src"
FIXTURE_DIR="$SCRIPT_DIR/fixtures/style"

if ! command -v python3 >/dev/null 2>&1; then
    echo "ERROR: python3 not found -- this instrument requires it." >&2
    exit 2
fi

MODE="gate"
GATE_MODE="gate"
[ "${1:-}" = "--self-test" ] && MODE="self-test"
[ "${1:-}" = "--pending" ] && GATE_MODE="gate-pending"

# ---------------------------------------------------------------------------
# D1 project convention (recorded next to CONFORMANCE_GUIDES in
# .claude/skill-conventions.md): the gate covers .spin2 files Stephen
# authored, or Stephen and Claude authored together. We do not modify code
# we did not author, so files imported from elsewhere for use in this
# project are excluded from the gate along with everything else about them.
# Named here, with reasons, and printed on every run -- nothing is excluded
# silently. See PL-1 in DOCs/PUNCH-LIST.md for the hng034rm half of this
# answer (it is ALSO excluded from tools/build-check.sh, for an unrelated
# reason: it cannot compile).
EXCLUDED="p2videodrv p2textdrv jm_ez_analog jm_nstr jm_sbus_rx hng034rm"
# p2videodrv, p2textdrv -- Parallax-forum video driver; no ISP header, not
#                           Stephen's.
# jm_ez_analog, jm_nstr, jm_sbus_rx -- Jon McPhalen upstream ("E-mail.....
#                           jon.mcphalen@gmail.com" in each header).
# hng034rm             -- pik33/MIT, vendored, and cannot compile (PL-1).
#
# isp_serial.spin2 and isp_serial_singleton.spin2 are IN SCOPE despite
# crediting Eric Smith / Chip Gracey / Jon McPhalen as original authors:
# their headers carry stephen@ironsheep.biz, the ISP header block, the ISP
# filename namespace, and an explicit "singleton adaptation by Stephen M.
# Moraco". Stephen maintains them.

# ---------------------------------------------------------------------------
# D9: file discovery is `ls src/*.spin2`, NOT `git ls-files` -- test_angle
# is gitignored but present and IS compiled by build-check.sh, so the style
# gate must see the same roster the build gate sees.
cd "$SRC_DIR" || exit 2
ALL=$(ls *.spin2 2>/dev/null | sed 's/\.spin2$//')

FILES=""
N_TOTAL=0
for n in $ALL; do
    N_TOTAL=$((N_TOTAL + 1))
    skip=0
    for x in $EXCLUDED; do [ "$n" = "$x" ] && skip=1; done
    [ $skip -eq 0 ] && FILES="$FILES $SRC_DIR/$n.spin2"
done
N_IN_SCOPE=$(echo $FILES | wc -w | tr -d ' ')

# Create temp file for Python checker and arrange cleanup
PYFILE=$(mktemp)
trap "rm -f $PYFILE" EXIT INT TERM

# Emit the Python checker once
cat > "$PYFILE" << 'PYEOF'
#!/usr/bin/env python3
"""
check_style.sh's checker -- lexes each .spin2 file into a per-line structural
view (D7) and runs the mechanically-checkable subset of the central Spin2
authoring guide against it.

Usage: checker.py gate FILE...
       checker.py self-test FILE...   (each FILE names its own expected check
                                        ID via a marker comment; see below)
"""
import sys, re, os

BLOCK_RE = re.compile(r'^(CON|DAT|VAR|OBJ|PUB|PRI)\b', re.IGNORECASE)

GENERIC_NAMES = {"result", "value", "temp", "data", "ret", "buf", "info"}
HAZARD_NAMES = {"cogid", "bool", "string", "send", "wc", "step", "neg",
                 "skip", "skipf", "pa", "pb", "ptra", "ptrb", "dira"}

BOX_LO, BOX_HI = (0x2500, 0x257F), (0x2580, 0x259F)


# ---------------------------------------------------------------------------
# D7 -- lexed view. One embedded python3 scanner (precedent: build-check.sh's
# config-block parser -- macOS ships bash 3.2, no mapfile/assoc-arrays).
# ---------------------------------------------------------------------------
def lex_file(path, text):
    raw_lines = text.split('\n')
    if raw_lines and raw_lines[-1] == '':
        raw_lines = raw_lines[:-1]

    lines = []
    cur_block = None
    brace_depth = 0
    brace_doc_outer = False

    for raw in raw_lines:
        rec = {
            'raw': raw, 'block': cur_block, 'block_starts': False,
            'code': '', 'comment_kind': None, 'comment_text': '',
            'in_brace': brace_depth > 0,
            'brace_opens': False, 'brace_closes_to_zero': False,
        }
        i, n = 0, len(raw)
        code_chars = []
        line_comment_kind = None
        line_comment_text_start = None

        while i < n:
            ch = raw[i]

            if brace_depth > 0:
                if ch == '{':
                    brace_depth += 1
                    i += 1
                    continue
                if ch == '}':
                    brace_depth -= 1
                    i += 1
                    if brace_depth == 0:
                        rec['brace_closes_to_zero'] = True
                        brace_doc_outer = False
                    continue
                i += 1
                continue

            if ch == '"':
                # String literal -- consumed but its CONTENTS are masked out
                # of the code view (blanked, not copied) so nothing inside a
                # string (e.g. a debug() format string containing "=>") is
                # ever mistaken for code. This is what makes the '=>' check
                # false-positive-free (D7): all 3 raw '=>' hits in this tree
                # are inside debug() string literals.
                j = i + 1
                while j < n and raw[j] != '"':
                    j += 1
                span = min(j + 1, n) - i
                code_chars.append('"' + (' ' * max(span - 2, 0)) + ('"' if j < n else ''))
                i = j + 1
                continue

            if ch == "'":
                if i + 1 < n and raw[i + 1] == "'":
                    line_comment_kind = "''"
                    line_comment_text_start = i + 2
                else:
                    line_comment_kind = "'"
                    line_comment_text_start = i + 1
                break

            if ch == '{':
                is_doc = i + 1 < n and raw[i + 1] == '{'
                consumed = 2 if is_doc else 1
                brace_depth += 1
                brace_doc_outer = is_doc
                rec['brace_opens'] = True
                line_comment_kind = "{{" if is_doc else "{"
                i += consumed
                continue

            code_chars.append(ch)
            i += 1

        rec['code'] = ''.join(code_chars)
        if line_comment_kind is not None:
            rec['comment_kind'] = line_comment_kind
            if line_comment_kind in ("'", "''"):
                rec['comment_text'] = raw[line_comment_text_start:]
            else:
                rec['comment_text'] = raw

        stripped_code = rec['code'].strip()
        if not rec['in_brace'] and stripped_code:
            m = BLOCK_RE.match(stripped_code)
            if m:
                cur_block = m.group(1).upper()
                rec['block'] = cur_block
                rec['block_starts'] = True

        lines.append(rec)

    return lines, brace_depth


# ---------------------------------------------------------------------------
# Method table: one entry per PUB/PRI, with its parsed signature and the
# line range of its "prologue" (doc-comment zone between signature and code).
# ---------------------------------------------------------------------------
SIG_RE = re.compile(
    r'^(PUB|PRI)\s+([A-Za-z_]\w*)\s*(\((.*?)\))?\s*(:\s*([^|]*))?\s*(\|\s*(.*))?$',
    re.IGNORECASE)


def split_names(s):
    names = []
    for p in s.split(','):
        p = p.strip()
        if not p:
            continue
        p = re.sub(r'^\^?(BYTE|WORD|LONG)\s+', '', p, flags=re.IGNORECASE)
        p = re.sub(r'^\^\w+\s+', '', p)
        p = p.lstrip('^')
        p = re.sub(r'\[[^\]]*\]', '', p)
        p = p.split('=')[0].strip()
        if p:
            names.append(p)
    return names


def parse_methods(lines):
    methods = []
    idx = 0
    n = len(lines)
    while idx < n:
        rec = lines[idx]
        if rec['block_starts'] and rec['block'] in ('PUB', 'PRI'):
            # gather multi-line "..." continuation
            code_parts = [rec['code'].strip()]
            sig_end = idx
            while code_parts[-1].endswith('...'):
                sig_end += 1
                if sig_end >= n:
                    break
                code_parts[-1] = code_parts[-1][:-3].rstrip()
                code_parts.append(lines[sig_end]['code'].strip())
            full_sig = ' '.join(code_parts)
            m = SIG_RE.match(full_sig)
            # end of method body: next block_starts line, or EOF
            nxt = sig_end + 1
            while nxt < n and not lines[nxt]['block_starts']:
                nxt += 1
            body_end = nxt  # exclusive

            has_trailing_comment = rec['comment_kind'] is not None
            if m:
                kind = m.group(1).upper()
                name = m.group(2)
                params = split_names(m.group(4) or '')
                returns = split_names(m.group(6) or '')
                locals_ = split_names(m.group(8) or '')
            else:
                kind = rec['block']
                name = '?'
                params = returns = locals_ = []

            methods.append({
                'kind': kind, 'name': name, 'params': params,
                'returns': returns, 'locals': locals_,
                'decl_line': idx, 'sig_end': sig_end, 'body_end': body_end,
                'has_trailing_comment': has_trailing_comment,
            })
            idx = sig_end + 1
            continue
        idx += 1
    return methods


# ---------------------------------------------------------------------------
# Checks. Each returns a list of (check_id, guide_section, lineno, message).
# lineno is 1-based.
# ---------------------------------------------------------------------------
def check_ascii(text):
    out = []
    line_no = 1
    for ch in text:
        if ch == '\n':
            line_no += 1
            continue
        o = ord(ch)
        if o <= 127:
            continue
        if BOX_LO[0] <= o <= BOX_LO[1] or BOX_HI[0] <= o <= BOX_HI[1]:
            continue
        out.append(('S1.1', '1.1', line_no,
                     "illegal non-ASCII character U+%04X" % o))
    return out


def check_arrow(lines):
    out = []
    for i, rec in enumerate(lines, 1):
        if '=>' in rec['code']:
            out.append(('S1.2', '1.2', i,
                         "'=>' found -- always a compile error in Spin2 "
                         "(use '>=' for comparison, '..' for case ranges)"))
    return out


def check_emptystr(lines):
    out = []
    for i, rec in enumerate(lines, 1):
        if '@""' in rec['code']:
            out.append(('A8', '1.8', i, "empty string literal @\"\" is invalid"))
    return out


def check_hazard(methods):
    out = []
    for meth in methods:
        i = meth['decl_line'] + 1
        for nm in meth['params'] + meth['returns'] + meth['locals']:
            if nm.lower() in HAZARD_NAMES:
                out.append(('A7', '1.3', i,
                             "%s() - identifier '%s' collides with a known "
                             "hazard (see guide 1.3)" % (meth['name'], nm)))
    return out


def check_singleletter(methods):
    out = []
    for meth in methods:
        i = meth['decl_line'] + 1
        for nm in meth['params'] + meth['returns'] + meth['locals']:
            if re.match(r'^[A-Za-z]$', nm):
                out.append(('C9', '2.1', i,
                             "%s() - single-letter name '%s' in signature"
                             % (meth['name'], nm)))
    return out


def check_generic(methods):
    out = []
    for meth in methods:
        i = meth['decl_line'] + 1
        for nm in meth['params'] + meth['returns'] + meth['locals']:
            if nm.lower() in GENERIC_NAMES:
                out.append(('A6', '2.2', i,
                             "%s() - generic container name '%s'"
                             % (meth['name'], nm)))
    return out


TAG_RE = re.compile(r'^@(param|returns)\s+(\S+)', re.IGNORECASE)
LOCAL_TAG_RE = re.compile(r'^@local\s+(\S+)', re.IGNORECASE)


def check_pub_docs(lines, methods):
    """C3a/b/c (4.3 doc structure), C3d (tag<->signature), C3e (@local marker)."""
    out = []
    for meth in methods:
        if meth['kind'] != 'PUB':
            continue
        name = meth['name']
        # A signature line that itself carries a trailing comment is a
        # distinct 4.5 (block-decl-label) matter, not a 4.3 doc block --
        # e.g. isp_bldc_motor_userconfig.spin2's "PUB null() '' ..." has no
        # doc lines following it at all, and IS handled (once) by 4.5.
        if meth['has_trailing_comment']:
            continue

        start = meth['sig_end'] + 1
        end = meth['body_end']

        # Walk the prologue: consecutive comment/blank lines right after
        # the signature, up to the first genuine code line or EOF/next block.
        j = start
        prologue = []
        while j < end:
            rec = lines[j]
            # rec['code'] already excludes trailing '/'' comment text (and
            # brace-comment interiors) -- a code line that also carries a
            # trailing comment must still end the prologue. Testing
            # rec['comment_kind'] here (as an earlier version of this loop
            # did) is wrong: comment_kind marks "this line has a comment
            # attached", not "this line is comment-only", so it wrongly
            # swallowed lines like "x := 1  ' note" into the prologue.
            code_nonblank = rec['code'].strip() != ''
            if code_nonblank:
                break
            prologue.append((j, rec))
            j += 1
        first_code_idx = j if j < end else None

        if not prologue or prologue[0][1]['comment_kind'] != "''" or \
           prologue[0][1]['comment_text'].strip() == '':
            out.append(('C3a', '4.3', meth['decl_line'] + 1,
                         "%s() - no '' doc comment immediately after signature"
                         % name))
            continue  # can't usefully evaluate structure further

        # description run = consecutive non-empty '' lines from the top
        k = 0
        while k < len(prologue) and prologue[k][1]['comment_kind'] == "''" \
                and prologue[k][1]['comment_text'].strip() != '':
            k += 1
        # blank '' separator required next
        if k >= len(prologue) or prologue[k][1]['comment_kind'] != "''" or \
                prologue[k][1]['comment_text'].strip() != '':
            out.append(('C3b', '4.3', meth['decl_line'] + 1,
                         "%s() - no blank '' separator after description" % name))
        else:
            k += 1  # consume the blank separator

        # tag zone: remaining '' lines (with content) are @param/@returns
        seen_tag_names = set()
        while k < len(prologue) and prologue[k][1]['comment_kind'] == "''" \
                and prologue[k][1]['comment_text'].strip() != '':
            ln, rec = prologue[k]
            content = rec['comment_text'].strip()
            m = TAG_RE.match(content)
            if m:
                tagtype, tagname = m.group(1).lower(), m.group(2)
                pool = meth['params'] if tagtype == 'param' else meth['returns']
                if tagname not in pool:
                    out.append(('C3d', '4.3', ln + 1,
                                 "%s() - @%s %s does not name a real %s"
                                 % (name, tagtype, tagname,
                                    'parameter' if tagtype == 'param' else 'return value')))
            elif content.lower().startswith('@local'):
                out.append(('C3e', '4.3', ln + 1,
                             "%s() - @local tag uses '' (must use ')" % name))
            k += 1

        # @local zone: ' comment lines, tags may use @local
        while k < len(prologue) and prologue[k][1]['comment_kind'] == "'":
            ln, rec = prologue[k]
            content = rec['comment_text'].strip()
            m = LOCAL_TAG_RE.match(content)
            if m:
                tagname = m.group(1)
                if tagname not in meth['locals']:
                    out.append(('C3d', '4.3', ln + 1,
                                 "%s() - @local %s does not name a real local"
                                 % (name, tagname)))
            k += 1

        # blank line before code: guide 4.3 requires a blank line
        # immediately after the last '' doc-comment line. A trailing '
        # comment or a { } block comment may legitimately sit between
        # THAT blank line and the first code line (e.g. doc / blank /
        # ' note / code is conformant -- the note doesn't un-blank the
        # separator that's already there) -- but if something other than
        # a blank line comes directly after the last '' line (e.g. a '
        # comment, with or without a later blank before the code), the
        # doc block was never actually separated from what follows it,
        # and that is the violation, regardless of what happens further
        # down the prologue.
        if first_code_idx is not None:
            last_doc_idx = None
            for pi, (_, prec) in enumerate(prologue):
                if prec['comment_kind'] == "''":
                    last_doc_idx = pi
            after_doc_pos = (last_doc_idx + 1) if last_doc_idx is not None else 0
            if after_doc_pos < len(prologue):
                immediately_after = prologue[after_doc_pos][1]
                has_blank = immediately_after['raw'].strip() == ''
            else:
                has_blank = False  # doc line is immediately followed by code
            if not has_blank:
                out.append(('C3c', '4.3', meth['decl_line'] + 1,
                             "%s() - no blank line before code" % name))
    return out


def check_pri_docs(lines, methods):
    """C4: PRI method docs must use ' , never ''."""
    out = []
    for meth in methods:
        if meth['kind'] != 'PRI':
            continue
        if meth['has_trailing_comment']:
            continue
        j = meth['sig_end'] + 1
        end = meth['body_end']
        while j < end:
            rec = lines[j]
            if rec['comment_kind'] == "''":
                out.append(('C4', '4.4', j + 1,
                             "%s() - PRI method doc uses '' (must use ')"
                             % meth['name']))
            elif rec['comment_kind'] == "'" or rec['raw'].strip() == '':
                pass
            else:
                break
            j += 1
    return out


def check_block_decl(lines):
    """C6: comment on a CON/DAT/VAR/OBJ/PUB/PRI declaration line must use
    ' , never ''."""
    out = []
    for i, rec in enumerate(lines, 1):
        if rec['block_starts'] and rec['comment_kind'] == "''":
            out.append(('C6', '4.5', i,
                         "%s declaration line uses '' (must use ')"
                         % rec['block']))
    return out


def check_brace_footer(lines):
    """C7: {{ }} only permitted as the file's final license footer (D6:
    footer-only, per the guide's normative body, not its Checklist).
    A3: the file MUST end with one."""
    out = []
    doc_blocks = []
    depth = 0
    is_doc = False
    start = None
    for i, rec in enumerate(lines, 1):
        if depth == 0 and rec['brace_opens']:
            depth = 1
            is_doc = (rec['comment_kind'] == '{{')
            start = i
        if depth > 0 and rec['brace_closes_to_zero']:
            if is_doc:
                doc_blocks.append((start, i))
            depth = 0

    # true end of file content = last non-blank line index (1-based)
    last_content = 0
    for i, rec in enumerate(lines, 1):
        if rec['raw'].strip() != '':
            last_content = i

    if not doc_blocks:
        out.append(('A3', '4.2.1', last_content or 1,
                     "file has no {{ }} license footer"))
    else:
        footer = doc_blocks[-1]
        if footer[1] != last_content:
            out.append(('A3', '4.2.1', last_content or 1,
                         "file does not END with its {{ }} license footer"))
        for blk in doc_blocks[:-1]:
            out.append(('C7', '4.1', blk[0],
                         "{{ }} doc-comment used outside the license footer"))
    return out


HEADER_FIELDS = [
    ('File....', 'File'), ('Purpose', 'Purpose'), ('Author', 'Author(s)'),
    ('E-mail', 'E-mail'), ('Started', 'Started'), ('Updated', 'Updated'),
]


def check_header(lines):
    """A4: file header carries File/Purpose/Author/E-mail/Started/Updated."""
    out = []
    # header = the leading run of '' comment lines (allowing an optional
    # {Spin2_v##} directive line first, and blank lines before it).
    i = 0
    n = len(lines)
    while i < n and lines[i]['raw'].strip() == '':
        i += 1
    if i < n and lines[i]['raw'].strip().startswith('{Spin2_v'):
        i += 1
        while i < n and lines[i]['raw'].strip() == '':
            i += 1
    header_text = []
    start_i = i
    while i < n and lines[i]['comment_kind'] == "''":
        header_text.append(lines[i]['comment_text'])
        i += 1
    blob = '\n'.join(header_text)
    if not header_text:
        out.append(('A4', '4.2', 1, "file has no '' header block at all"))
        return out
    missing = [label for key, label in HEADER_FIELDS if key.lower() not in blob.lower()]
    if missing:
        out.append(('A4', '4.2', start_i + 1,
                     "file header missing: %s" % ', '.join(missing)))
    return out




def check_con_dashes(lines):
    """A5 (guide 4.9): No horizontal separator lines inside CON blocks.

    Fires on a comment line inside a CON block whose body — after stripping
    the leading ' or '' marker — consists ONLY of whitespace and runs of
    dashes/equals/underscores/tildes, containing NO label text.

    Does NOT fire for lines inside { } or {{ }} block comments, since those
    contents are not extracted into the API document (which is the rationale
    for the rule). The reconciliation with 4.5 (which REQUIRES '---- Label ----'
    on block declaration lines) is that 4.5 applies to block-decl lines with
    label text, while 4.9 forbids bare separator lines.
    """
    out = []
    for i, rec in enumerate(lines, 1):
        # Must be in CON block and not inside braces
        if rec['block'] != 'CON' or rec['in_brace']:
            continue
        # Must be a comment line with ' or ''
        if rec['comment_kind'] not in ("'", "''"):
            continue
        # Not a block-start line (the CON declaration itself)
        if rec['block_starts']:
            continue
        # Check if comment text is ONLY dashes/equals/underscores/tildes
        text = rec['comment_text'].strip()
        # Must be non-empty and match only separator characters
        if text and re.match(r'^[-=_~]+$', text):
            out.append(('A5', '4.9', i,
                         "horizontal separator (no label text) in CON block"))
    return out


# ---------------------------------------------------------------------------
# T1 coverage (task 3517). Every check below reads the lexed code view --
# string contents blanked, comments stripped -- so nothing inside a string
# literal or a comment can fire one.
# ---------------------------------------------------------------------------
RETURN_RE = re.compile(r'(?<![\w.])return\b', re.IGNORECASE)
RETURN_EXPR_RE = re.compile(r'(?<![\w.])return\b\s*\S', re.IGNORECASE)
REPEAT_RE = re.compile(r'^repeat\b', re.IGNORECASE)
PASM_START_RE = re.compile(r'^org(h)?\b', re.IGNORECASE)
PASM_END_RE = re.compile(r'^end\b', re.IGNORECASE)
ASSIGN_OPS = r'(?::=|\+=|-=|\*=|//=|/=|\+//=|\+/=|&=|\|=|\^=|<<=|>>=|#>=|<#=|\+\+|--)'
BOOL_NAME = r'(?<![\w.])b[A-Z]\w*'
BOOL_CMP_RE = re.compile(BOOL_NAME + r'\s*(?:==|<>)\s*[01](?![\w.])')
BOOL_SET_RE = re.compile(BOOL_NAME + r'\s*:=\s*1(?![\w.])')
BOOL_METHOD_RE = re.compile(r'^(is|has|b[A-Z])')
CALL_RE = re.compile(r'(?<![\w@])[A-Za-z_][\w.]*\s*\(')
TAG_ANY_RE = re.compile(r'@(param|returns|local)\s+([A-Za-z_]\w*)', re.IGNORECASE)


def body_lines(lines, meth):
    """(lineno, code, indent, bPasm) for each non-blank code line of a method body.
    bPasm marks inline PASM (org .. end), which has no Spin2 return and its own
    operand syntax."""
    out = []
    in_pasm = False
    for j in range(meth['sig_end'] + 1, meth['body_end']):
        code = lines[j]['code']
        stripped = code.strip()
        if not stripped:
            continue
        indent = len(code) - len(code.lstrip(' \t'))
        if PASM_START_RE.match(stripped):
            in_pasm = True
            out.append((j + 1, code, indent, True))
            continue
        if in_pasm and PASM_END_RE.match(stripped):
            in_pasm = False
            out.append((j + 1, code, indent, True))
            continue
        out.append((j + 1, code, indent, in_pasm))
    return out


def check_pub_before_pri(methods):
    """S3.2 (guide 3.2): every PUB precedes every PRI."""
    out = []
    first_pri = None
    for meth in methods:
        if meth['kind'] == 'PRI' and first_pri is None:
            first_pri = meth
        elif meth['kind'] == 'PUB' and first_pri is not None:
            out.append(('S3.2', '3.2', meth['decl_line'] + 1,
                         "%s() - PUB after PRI %s() (all PUB methods precede all PRI)"
                         % (meth['name'], first_pri['name'])))
    return out


def check_layout(lines):
    """S3.1 (guide 3.1): the file opens with CON, and no OBJ block follows a
    method. Later CON / DAT / VAR blocks are permitted by 3.4; OBJ is not."""
    out = []
    blocks = [(i + 1, rec['block']) for i, rec in enumerate(lines) if rec['block_starts']]
    if not blocks:
        return out
    first_method = next((ln for ln, blk in blocks if blk in ('PUB', 'PRI')), None)
    if first_method is not None:
        for ln, blk in blocks:
            if blk == 'OBJ' and ln > first_method:
                out.append(('S3.1', '3.1', ln, "OBJ block after the first method (OBJ precedes every PUB/PRI)"))
    if any(blk == 'CON' for _, blk in blocks) and blocks[0][1] != 'CON':
        out.append(('S3.1', '3.1', blocks[0][0],
                     "the file's first block is %s -- the layout opens with CON" % blocks[0][1]))
    return out


def check_exits(lines, methods):
    """S5.2 (guide 5.2) an early return; S5.3 (guide 5.3) a return inside a
    repeat. A return on the method's last code line, outside any loop, is its
    single exit and is permitted."""
    out = []
    for meth in methods:
        body = body_lines(lines, meth)
        if not body:
            continue
        last_ln = body[-1][0]
        repeat_stack = []
        for ln, code, indent, b_pasm in body:
            if b_pasm:
                continue
            while repeat_stack and repeat_stack[-1] >= indent:
                repeat_stack.pop()
            if RETURN_RE.search(code):
                if repeat_stack:
                    out.append(('S5.3', '5.3', ln,
                                 "%s() - return inside a repeat (set the result and quit)" % meth['name']))
                elif ln != last_ln:
                    out.append(('S5.2', '5.2', ln,
                                 "%s() - early return (one exit, at the method's end)" % meth['name']))
            if REPEAT_RE.match(code.strip()):
                repeat_stack.append(indent)
    return out


def check_unused(lines, methods):
    """S5.0 (guide 5.0): a parameter or local the body never names. Return
    values are 5.1's: a 'return expr' assigns them without naming them.
    Parameters are consecutive longs on the stack, so a method that takes a
    parameter's address (a format helper passing @arg1) reads the parameters
    after it through that address: those count as used."""
    out = []
    for meth in methods:
        text = '\n'.join(code for _, code, _, _ in body_lines(lines, meth))
        addr_taken = [idx for idx, nm in enumerate(meth['params'])
                      if re.search(r'@' + re.escape(nm) + r'\b', text, re.IGNORECASE)]
        reached = set(meth['params'][addr_taken[0]:]) if addr_taken else set()
        for kind, names in (('parameter', meth['params']), ('local', meth['locals'])):
            for nm in names:
                if kind == 'parameter' and nm in reached:
                    continue
                if not re.search(r'(?<![\w.])' + re.escape(nm) + r'\b', text, re.IGNORECASE):
                    out.append(('S5.0', '5.0', meth['decl_line'] + 1,
                                 "%s %s() - %s '%s' is never used" % (meth['kind'], meth['name'], kind, nm)))
    return out


def is_assigned(name, body):
    esc = re.escape(name)
    pat_op = re.compile(r'(?<![\w.@])' + esc + r'\b\s*(?:\[[^\]]*\])?\s*' + ASSIGN_OPS, re.IGNORECASE)
    pat_pre = re.compile(r'(?:\+\+|--)\s*' + esc + r'\b', re.IGNORECASE)
    pat_addr = re.compile(r'@' + esc + r'\b', re.IGNORECASE)
    pat_pasm = re.compile(r'^\s*(?:if_\w+\s+|_ret_\s+)?[A-Za-z]\w*\s+' + esc + r'\b', re.IGNORECASE)
    for _, code, _, b_pasm in body:
        if b_pasm:
            if pat_pasm.search(code):
                return True
            continue
        if pat_op.search(code) or pat_pre.search(code) or pat_addr.search(code):
            return True
        if ':=' in code:
            lhs = code.split(':=')[0]
            if ',' in lhs:
                for part in lhs.split(','):
                    part = re.sub(r'\[[^\]]*\]', '', part).strip()
                    if part.lower() == name.lower():
                        return True
    return False


def check_returns_assigned(lines, methods):
    """S5.1 (guide 5.1): every return value is explicitly assigned. A method
    that ends in 'return expr' assigns its results there."""
    out = []
    for meth in methods:
        body = body_lines(lines, meth)
        if any(RETURN_EXPR_RE.search(code) for _, code, _, b_pasm in body if not b_pasm):
            continue
        for nm in meth['returns']:
            if not is_assigned(nm, body):
                out.append(('S5.1', '5.1', meth['decl_line'] + 1,
                             "%s() - return value '%s' is never assigned" % (meth['name'], nm)))
    return out


def check_boolean(lines, methods):
    """S5.4 (guide 5.4 / 5.4.1): a method returning one boolean (b-prefixed)
    is named is/has/b; S5.41: a boolean is never set to 1 or compared to 0/1."""
    out = []
    for meth in methods:
        rets = meth['returns']
        if len(rets) == 1 and re.match(r'^b[A-Z]', rets[0]) and not BOOL_METHOD_RE.match(meth['name']):
            out.append(('S5.4', '5.4', meth['decl_line'] + 1,
                         "%s %s() - returns boolean '%s' but is not named is/has/b (a query) "
                         "-- or it is an operation, which returns a status" % (meth['kind'], meth['name'], rets[0])))
        for ln, code, _, b_pasm in body_lines(lines, meth):
            if b_pasm:
                continue
            if BOOL_CMP_RE.search(code) or BOOL_SET_RE.search(code):
                out.append(('S5.41', '5.4.1', ln,
                             "%s() - boolean set to 1 or compared to 0/1 (use TRUE / FALSE)" % meth['name']))
    return out


def check_shadow(methods):
    """S1.5 (guide 1.5): no parameter, return or local shares a method's name."""
    out = []
    method_names = {m['name'].lower() for m in methods}
    for meth in methods:
        for nm in meth['params'] + meth['returns'] + meth['locals']:
            if nm.lower() in method_names:
                out.append(('S1.5', '1.5', meth['decl_line'] + 1,
                             "%s() - '%s' shadows the method of that name" % (meth['name'], nm)))
    return out


def con_names(lines):
    """name_lower -> (lineno, value expression, or None for an enum member)."""
    names = {}
    b_enum_cont = False
    for i, rec in enumerate(lines, 1):
        if rec['block'] != 'CON' or rec['in_brace']:
            b_enum_cont = False
            continue
        code = rec['code'].strip()
        if rec['block_starts']:
            code = re.sub(r'^CON\b', '', code, flags=re.IGNORECASE).strip()
        if not code:
            continue
        cont = code.endswith('...')
        if cont:
            code = code[:-3].rstrip()
        if re.match(r'^#[A-Za-z]', code) or re.match(r'^STRUCT\b', code, re.IGNORECASE):
            b_enum_cont = False
            continue
        if code.startswith('#') or b_enum_cont:
            parts = code.split(',')
            if code.startswith('#'):
                parts = parts[1:]
            for part in parts:
                m = re.match(r'^\s*([A-Za-z_]\w*)', part)
                if m:
                    names.setdefault(m.group(1).lower(), (i, None))
            b_enum_cont = cont
            continue
        for part in re.split(r',(?![^(]*\))', code):
            m = re.match(r'^\s*([A-Za-z_]\w*)\s*=\s*(.*)$', part)
            if m:
                names.setdefault(m.group(1).lower(), (i, m.group(2).strip()))
        b_enum_cont = False
    return names


OBJ_LINE_RE = re.compile(r'^([A-Za-z_]\w*)\s*(?:\[[^\]]*\])?\s*:\s*"([^"]*)"\s*(?:\|\s*(.*))?$')


def obj_refs(lines, raw_lines):
    """(lineno, alias, file, override text) for each OBJ declaration. The file
    name is read from the raw line, because the code view blanks strings."""
    refs = []
    for i, rec in enumerate(lines, 1):
        if rec['block'] != 'OBJ' or rec['in_brace']:
            continue
        raw = raw_lines[i - 1]
        raw_code = raw.split("'")[0].strip()
        if rec['block_starts']:
            raw_code = re.sub(r'^OBJ\b', '', raw_code, flags=re.IGNORECASE).strip()
        m = OBJ_LINE_RE.match(raw_code)
        if m:
            refs.append((i, m.group(1), m.group(2), m.group(3) or ''))
    return refs


def check_obj_constants(path, lines, raw_lines):
    """S1.9 (guide 1.9): an OBJ override of a CON this file also defines;
    S2.4 (guide 2.4): a child object's constant copied into a local CON
    instead of referenced through the object (NAME = alias.NAME re-exports
    are references, and pass)."""
    out = []
    parent = con_names(lines)
    src_dir = os.path.dirname(path)
    child_names = {}
    for ln, alias, fname, override in obj_refs(lines, raw_lines):
        for part in override.split(','):
            m = re.match(r'^\s*([A-Za-z_]\w*)\s*=', part)
            if m and m.group(1).lower() in parent:
                out.append(('S1.9', '1.9', ln,
                             "OBJ %s overrides %s, which this file's CON also defines (the parent's value wins)"
                             % (alias, m.group(1))))
        child_path = os.path.join(src_dir, fname if fname.lower().endswith('.spin2') else fname + '.spin2')
        if not os.path.isfile(child_path):
            continue
        if child_path not in child_names:
            ctext = open(child_path, 'r', encoding='utf-8', errors='replace').read()
            clines, cdepth = lex_file(child_path, ctext)
            child_names[child_path] = (con_names(clines) if cdepth == 0 else {}, [])
        child_names[child_path][1].append(alias)
    all_aliases = [a for _, (_, aliases) in child_names.items() for a in aliases]
    for name_l, (ln, value) in sorted(parent.items(), key=lambda kv: kv[1][0]):
        # a value read through any object is a reference to that object's constant, not a copy
        if value is not None and any(re.search(r'(?<![\w.])' + re.escape(a) + r'\s*(\[[^\]]*\])?\s*\.', value, re.IGNORECASE)
                                     for a in all_aliases):
            continue
        for cpath, (cnames, aliases) in child_names.items():
            if name_l not in cnames:
                continue
            out.append(('S2.4', '2.4', ln,
                         "constant %s duplicates %s's -- reference it as %s.%s"
                         % (name_l.upper(), os.path.basename(cpath), aliases[0], name_l.upper())))
            break
    return out


def ternary_branches(rest):
    """Split the text after a '?' into its two branches: the true branch ends
    at the ':' at nesting depth 0; the false branch ends at the first ')' or
    ',' that closes the enclosing expression, or at the end of the line.
    (None, None) when no ':' follows at depth 0."""
    depth = 0
    colon = None
    for idx, ch in enumerate(rest):
        if ch in '([':
            depth += 1
        elif ch in ')]':
            depth -= 1
            if depth < 0:
                return None, None
        elif ch == ':' and depth == 0 and not rest.startswith(':=', idx):
            colon = idx
            break
    if colon is None:
        return None, None
    depth = 0
    end = len(rest)
    for idx in range(colon + 1, len(rest)):
        ch = rest[idx]
        if ch in '([':
            depth += 1
        elif ch in ')]':
            if depth == 0:
                end = idx
                break
            depth -= 1
        elif ch == ',' and depth == 0:
            end = idx
            break
    return rest[:colon], rest[colon + 1:end]


def check_ternary_call(lines):
    """T29 (PUNCH-LIST PL-29, project rule): a ? : whose branch calls a method
    evaluated both branches' calls, twice measured on this rig. Select values
    with ? :, and choose between calls with if / else."""
    out = []
    for i, rec in enumerate(lines, 1):
        code = rec['code']
        for qpos in [m.start() for m in re.finditer(r'(?<!\?)\?(?!\?)', code)]:
            branch_a, branch_b = ternary_branches(code[qpos + 1:])
            if branch_a is None:
                continue
            if CALL_RE.search(branch_a) or CALL_RE.search(branch_b):
                out.append(('T29', 'PL-29', i,
                             "? : with a method call in a branch -- both calls run; use if / else"))
                break
    return out


def check_doc_completeness(lines, methods):
    """C3f (guide 4.3 / 4.4, PUNCH-LIST PL-10): every parameter, return value
    and local has its @param / @returns / @local tag."""
    out = []
    for meth in methods:
        tags = {'param': set(), 'returns': set(), 'local': set()}
        j = meth['sig_end'] + 1
        while j < meth['body_end'] and lines[j]['code'].strip() == '':
            rec = lines[j]
            if rec['comment_kind'] in ("'", "''"):
                m = TAG_ANY_RE.search(rec['comment_text'])
                if m:
                    tags[m.group(1).lower()].add(m.group(2).lower())
            j += 1
        for kind, word, names in (('param', 'parameter', meth['params']),
                                  ('returns', 'return value', meth['returns']),
                                  ('local', 'local', meth['locals'])):
            for nm in names:
                if nm.lower() not in tags[kind]:
                    out.append(('C3f', '4.3', meth['decl_line'] + 1,
                                 "%s() - %s '%s' has no @%s tag" % (meth['name'], word, nm, kind)))
    return out


def check_decl_border(lines):
    """C6b (guide 4.5): a block declaration's label is text, never a bare
    decorative border."""
    out = []
    for i, rec in enumerate(lines, 1):
        if rec['block_starts'] and rec['comment_kind'] == "'":
            text = rec['comment_text'].strip()
            if text and not re.search(r'[A-Za-z0-9]', text):
                out.append(('C6b', '4.5', i, "%s declaration label is a bare border, not text" % rec['block']))
    return out


def check_storage_names(lines):
    """C9 (guide 2.1) for storage: a single-letter VAR name or DAT data label."""
    out = []
    for i, rec in enumerate(lines, 1):
        if rec['in_brace']:
            continue
        code = rec['code']
        if rec['block'] == 'VAR':
            body = re.sub(r'^VAR\b', '', code.strip(), flags=re.IGNORECASE) if rec['block_starts'] else code
            m = re.match(r'^\s*(BYTE|WORD|LONG)\s+(.*)$', body, re.IGNORECASE)
            if m:
                for nm in split_names(m.group(2)):
                    if re.match(r'^[A-Za-z]$', nm):
                        out.append(('C9', '2.1', i, "VAR single-letter name '%s'" % nm))
        elif rec['block'] == 'DAT' and not rec['block_starts']:
            m = re.match(r'^([A-Za-z])\s+(BYTE|WORD|LONG)\b', code, re.IGNORECASE)
            if m:
                out.append(('C9', '2.1', i, "DAT single-letter label '%s'" % m.group(1)))
    return out


ALL_CHECK_IDS = ["S1.1", "S1.2", "A7", "A8", "C9", "A6", "C3a", "C3b", "C3c",
                  "C3d", "C3e", "C4", "C6", "C7", "A3", "A4", "A5",
                  "S1.5", "S1.9", "S2.4", "S3.1", "S3.2", "S5.0", "S5.1", "S5.2",
                  "S5.3", "S5.4", "S5.41", "C3f", "C6b", "T29"]

# The checks that FAIL the gate. A check joins this set in the same commit that
# brings the tree clean for it; until then its count prints under PENDING on
# every run. When every ID above is here, the set is the whole list.
ENFORCED = {"S1.1", "S1.2", "A7", "A8", "C9", "A6", "C3a", "C3b", "C3c",
            "C3d", "C3e", "C4", "C6", "C7", "A3", "A4", "A5",
            "S1.5", "S1.9", "S2.4", "S3.1", "S3.2", "S5.0", "S5.1", "S5.2", "S5.3", "S5.4", "S5.41", "C6b", "T29"}

# What this gate covers, against the guide's own tier assignment (the guide's
# "Enforcement tiers"): printed on every run, so a rule nobody wrote is never
# mistaken for a rule that passed.
COVERAGE_LINES = [
    "T1 checked here (20 of 26): 1.1 1.3 1.5 1.8 1.9 2.1 2.4 3.1 3.2 4.1 4.2 4.2.1 4.5 4.9 "
    "5.0 5.1 5.2 5.3 5.4 5.4.1 -- partial: 1.3 (the guide's hazard table), 4.2.1 (footer present, "
    "license text not compared)",
    "T1 enforced elsewhere: 1.4 (a duplicate method name does not compile -- tools/build-check.sh)",
    "T1 not applicable: 3.4 (permits placement, forbids nothing); 6.2 6.4 6.7 (Part 6 is conditional "
    "and this project has no Spin2 regression harness)",
    "T1 NOT YET IMPLEMENTED (1): 3.1.1 (needs P2KB's feature-to-version answer at check time; the guide "
    "forbids a local table)",
    "T1+T2 detection halves not implemented (5): 2.1.4 2.5 4.6 5.7 6.1 -- judged in the T2 audit",
    "T2 NOT CHECKED by this gate (20): an agent audit, DOCs/procedures/STYLE-T2-AUDIT.md; T3 (2): 5.8 5.9, "
    "Stephen's read",
    "Project checks: C3f (4.3/4.4 element->tag, PL-10), T29 (? : with a call, PL-29)",
]


def run_all_checks(path):
    text = open(path, 'r', encoding='utf-8', errors='replace').read()
    lines, depth = lex_file(path, text)
    if depth != 0:
        return None, depth  # signals instrument failure for this file
    methods = parse_methods(lines)
    raw_lines = text.split('\n')
    findings = []
    findings += check_pub_before_pri(methods)
    findings += check_layout(lines)
    findings += check_exits(lines, methods)
    findings += check_unused(lines, methods)
    findings += check_returns_assigned(lines, methods)
    findings += check_boolean(lines, methods)
    findings += check_shadow(methods)
    findings += check_obj_constants(path, lines, raw_lines)
    findings += check_ternary_call(lines)
    findings += check_doc_completeness(lines, methods)
    findings += check_decl_border(lines)
    findings += check_storage_names(lines)
    findings += check_ascii(text)
    findings += check_arrow(lines)
    findings += check_emptystr(lines)
    findings += check_hazard(methods)
    findings += check_singleletter(methods)
    findings += check_generic(methods)
    findings += check_pub_docs(lines, methods)
    findings += check_pri_docs(lines, methods)
    findings += check_block_decl(lines)
    findings += check_brace_footer(lines)
    findings += check_header(lines)
    findings += check_con_dashes(lines)
    findings.sort(key=lambda f: f[2])
    return findings, depth


def fmt(path, cid, section, lineno, msg):
    loc = "%s:%d" % (path, lineno)
    return "  FAIL  %-6s %-46s %s" % (section, loc, msg)


def gate(paths, show_pending):
    all_findings = {}
    by_check = {}
    instrument_fail = False
    for path in paths:
        findings, depth = run_all_checks(path)
        if findings is None:
            print("ERROR: %s has unbalanced { } comment nesting at EOF "
                  "(depth=%d) -- every finding AND non-finding in this file "
                  "is suspect." % (path, depth), file=sys.stderr)
            instrument_fail = True
            continue
        if findings:
            all_findings[path] = findings
            for f in findings:
                by_check.setdefault(f[0], []).append((path, f))

    if instrument_fail:
        return 2

    print("Coverage (the guide's tier assignment):")
    for line in COVERAGE_LINES:
        print("  " + line)
    print()

    # a check being brought in prints its count on every run until the tree is clean for it
    pending = {cid: hits for cid, hits in by_check.items() if cid not in ENFORCED}
    if pending:
        print("PENDING -- checked, not yet enforced (the tree is being brought clean for them; "
              "--pending lists every site):")
        for cid in sorted(pending):
            print("  %-6s %d" % (cid, len(pending[cid])))
        print()
        if show_pending:
            for cid in sorted(pending):
                for path, f in pending[cid]:
                    print(fmt(os.path.relpath(path), *f))
            print()

    enforced = {path: [f for f in fs if f[0] in ENFORCED] for path, fs in all_findings.items()}
    enforced = {path: fs for path, fs in enforced.items() if fs}
    total = sum(len(v) for v in enforced.values())
    if total == 0:
        print("PASS: no enforced style findings across %d file(s)." % len(paths))
        return 0

    for path in sorted(enforced):
        for f in enforced[path]:
            print(fmt(os.path.relpath(path), *f))

    print()
    print("Findings by rule:")
    for cid in sorted(by_check):
        if cid in ENFORCED:
            print("  %-6s %d" % (cid, len(by_check[cid])))
    print()
    print("FAIL: %d finding(s) across %d file(s)." % (total, len(enforced)))
    return 1


def self_test(paths):
    # fixture filename convention: <checkid>.spin2, e.g. S1.1.spin2, C3a.spin2
    # A fixture named "conformant.spin2" must produce ZERO findings.
    rc = 0
    for path in paths:
        base = os.path.splitext(os.path.basename(path))[0]
        findings, depth = run_all_checks(path)
        if findings is None:
            print("SELF-TEST FAIL: %s -- unbalanced braces (instrument failure)" % path)
            rc = 1
            continue
        fired = sorted(set(f[0] for f in findings))
        if base == 'conformant':
            if fired:
                print("SELF-TEST FAIL: conformant.spin2 should have ZERO findings, got: %s" % fired)
                rc = 1
            else:
                print("SELF-TEST OK: conformant.spin2 -- clean, as required")
            continue
        expect = base
        if expect not in fired:
            print("SELF-TEST FAIL: %s -- expected check %s to fire, it did NOT. Fired: %s"
                  % (path, expect, fired))
            rc = 1
        elif fired != [expect]:
            print("SELF-TEST FAIL: %s -- expected ONLY %s to fire, but also got: %s"
                  % (path, expect, [c for c in fired if c != expect]))
            rc = 1
        else:
            print("SELF-TEST OK: %s -- %s fired, and only %s" % (path, expect, expect))

    tested = set(os.path.splitext(os.path.basename(p))[0] for p in paths) - {'conformant'}
    missing = set(ALL_CHECK_IDS) - tested
    if missing:
        print("SELF-TEST FAIL: no fixture exercises: %s" % sorted(missing))
        rc = 1
    return rc


def main():
    if len(sys.argv) < 3:
        print("usage: checker.py {gate|self-test} FILE...", file=sys.stderr)
        return 2
    mode = sys.argv[1]
    paths = sys.argv[2:]
    if mode == 'gate':
        return gate(paths, False)
    elif mode == 'gate-pending':
        return gate(paths, True)
    elif mode == 'self-test':
        return self_test(paths)
    else:
        print("unknown mode: %s" % mode, file=sys.stderr)
        return 2


if __name__ == '__main__':
    sys.exit(main())
PYEOF

if [ "$MODE" = "gate" ]; then
    if [ $N_IN_SCOPE -eq 0 ]; then
        echo "ERROR: no .spin2 files discovered in $SRC_DIR -- aborting." >&2
        echo "  A gate that discovers nothing has not passed -- it has not run." >&2
        exit 2
    fi

    echo "P2-BLDC-Motor-Control Spin2 style gate -- $N_IN_SCOPE of $N_TOTAL src/*.spin2 files in scope"
    echo "  excluded (not Stephen's, not modified -- see script header for D1):"
    for x in $EXCLUDED; do echo "    $x.spin2"; done
    echo

    python3 "$PYFILE" $GATE_MODE $FILES
    exit $?
fi

# ---------------------------------------------------------------------------
# --self-test: every check ID must fire, BY NAME, against a fixture built to
# break exactly that rule -- and no OTHER check may fire on that fixture. A
# check that has never been watched fail is not known to work.
if [ ! -d "$FIXTURE_DIR" ]; then
    echo "ERROR: fixture dir not found: $FIXTURE_DIR" >&2
    exit 2
fi
FIXTURES=$(ls "$FIXTURE_DIR"/*.spin2 2>/dev/null)
if [ -z "$FIXTURES" ]; then
    echo "ERROR: no fixtures found in $FIXTURE_DIR" >&2
    exit 2
fi

python3 "$PYFILE" self-test $FIXTURES
exit $?

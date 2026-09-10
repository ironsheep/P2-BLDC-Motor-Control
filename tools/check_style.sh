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
#
# Deliberately NOT checked, because they need judgement and would produce
# noise rather than signal: generic-name-by-semantics (2.2's judgement
# half), single-exit-point (5.2), magic numbers (5.7), PUB-before-PRI
# reordering (3.2 -- see PUNCH-LIST PL-11), and the element->tag half of
# 4.3's doc-completeness rule (see PUNCH-LIST PL-10).
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
[ "${1:-}" = "--self-test" ] && MODE="self-test"

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


ALL_CHECK_IDS = ["S1.1", "S1.2", "A7", "A8", "C9", "A6", "C3a", "C3b", "C3c",
                  "C3d", "C3e", "C4", "C6", "C7", "A3", "A4", "A5"]


def run_all_checks(path):
    text = open(path, 'r', encoding='utf-8', errors='replace').read()
    lines, depth = lex_file(path, text)
    if depth != 0:
        return None, depth  # signals instrument failure for this file
    methods = parse_methods(lines)
    findings = []
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


def gate(paths):
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

    total = sum(len(v) for v in all_findings.values())
    if total == 0:
        print("PASS: no style findings across %d file(s)." % len(paths))
        return 0

    for path in sorted(all_findings):
        for f in all_findings[path]:
            print(fmt(os.path.relpath(path), *f))

    print()
    print("Findings by rule:")
    for cid in sorted(by_check):
        print("  %-6s %d" % (cid, len(by_check[cid])))
    print()
    print("FAIL: %d finding(s) across %d file(s)." % (total, len(all_findings)))
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
        return gate(paths)
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

    python3 "$PYFILE" gate $FILES
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

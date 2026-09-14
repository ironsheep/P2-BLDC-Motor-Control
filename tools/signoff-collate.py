#!/usr/bin/env python3
"""signoff-collate.py -- collate a bench visit's SIGNOFF records into a sign-off sheet.

PURPOSE
    Every bench visit signs off each newly landed feature automatically. Bench
    binaries print SIGNOFF-DECL records (what they will judge) and SIGNOFF
    records (one verdict per instance) into the pnut-term-ts debug log. This
    script reads a visit's logs, checks every record against the sign-off
    manifest, and writes the visit's sign-off sheet. It never turns a
    measurement record (BS-ZERO, BC-SENSE, T0-n, ...) into a verdict.

    Specification: DOCs/plans/VISIT-SIGNOFF-DESIGN.md -- section 0 (the rules),
    A (manifest), B.1/B.5 (record and parser), C.1-C.3 (host cells), D
    (collation), E (the negative case), G.4 (R11-HOST-WDTEND), including the
    arbiter-review amendments of 2026-09-13 and the corrections of 2026-09-14.

THE THREE RULES (design section 0)
    1. A verdict exists only where a binary printed one. The host never turns a
       measurement record into a verdict. The host-side cells each name their
       own required input; if that input is absent the cell is NOT_BUILT.
    2. A cell starts at NOT_BUILT and reaches PASS only by positive evidence:
       at least min_inst PASS instances and no FAIL instance. NOMEAS and
       NOT_BUILT never count as PASS. No code path maps "no failure seen" to PASS.
    3. A binary declares what it will judge before it judges anything: one
       SIGNOFF-DECL per cell at start-up, then a SIGNOFF for every declared cell
       on every exit path it controls. Declared but no verdict is NOMEAS
       (NOT_REACHED); declared by no log is NOT_BUILT.

INPUTS
    - the visit's curated debug logs, named explicitly on the command line
      (never globbed by this script);
    - the manifest, DOCs/analyses/bench/SIGNOFF-MANIFEST.tsv (--manifest);
    - for R2-HOST-DETDIFF: a detect-phase2 log among the inputs, the prediction
      list DOCs/analyses/bench/SIGNOFF-DETECT-PREDICTIONS.tsv (--predictions) and
      the 2026-09-11 baseline log (--baseline-detect);
    - for R2-DETECT-GUARD: a detect-phase2 log among the inputs only -- the skip
      set it checks is computed from that log's BD-CFG bases and BD-PLAN;
    - for R10-HOST-PL9: --static-tree (reads src/isp_bldc_motor.spin2).

OUTPUTS
    - the sign-off sheet (--out, default
      DOCs/analyses/bench/<date>/VISIT-<n>-SIGNOFF.md): header, input logs with
      identity and COMPLETE/TRUNCATED, one line per row, one entry per cell with
      every proving file:line, and sections for NOT_BUILT, superseded logs,
      unmanifested cells, parse errors, deferred cells and the DETDIFF list;
    - with --update only: the manifest .tsv statuses are rewritten and
      SIGNOFF-MANIFEST.md (a GENERATED view) is regenerated beside it. Without
      --update the manifest is read-only.

CORRUPTED LINES (PL-40)
    pnut-term-ts can print a cog message on the tail of another line: after a
    "[ROUTING ERROR ...]" / "[BINARY DATA ...]" hex dump's closing '|', or joined
    to a truncated message ("Cog1Cog0  ..."). The log reader therefore finds a
    record token -- "CogN  " followed by SIGNOFF, SIGNOFF-DECL, DEBUG_END_SESSION,
    a banner, a header or a BD- record -- anywhere in a line, with two limits:
      - on a hex-dump row only the text after the fixed-width ASCII gutter is
        searched; bytes shown inside the gutter are never parsed;
      - a message ends at the end of its line. One that runs into a terminal
        marker or into another record token on the same line has no observed
        end: a SIGNOFF/SIGNOFF-DECL so cut is MALFORMED (never counted), any
        other message so cut is not read. Missing fields are never supplied.
    A recovered record keeps its file:line, is judged exactly like a line-start
    record, and is flagged in the cell's proving lines and in the sheet's
    "Records recovered from corrupted lines" section, which also lists any
    SIGNOFF text seen inside a gutter or on a corrupted line that yielded no
    record (listed only; it never carries a verdict).

USAGE
    tools/signoff-collate.py --visit N --date D [--update] [--static-tree]
        [--manifest PATH] [--predictions PATH] [--baseline-detect PATH]
        [--out PATH] <log> [<log> ...]
    tools/signoff-collate.py --check-ready N
    tools/signoff-collate.py --selftest

EXIT CODES
    0  sheet written (collate), no gaps (--check-ready), all checks passed (--selftest)
    1  --selftest: at least one check failed
    2  usage, input or manifest error; nothing written
    3  --check-ready: at least one OWED cell for that visit has no test

    Verdict content lives in the sheet, never in the exit code, so a FAIL never
    looks like a tool failure.

EXTERNAL COMMANDS
    None. Anything that ever needs one must go through run(), which prints
    "+ <argv>" verbatim before running it (the tools/bench-run.sh contract).
    --selftest asserts that no subprocess use exists outside run().

Python 3, standard library only.
"""

import argparse
import ast
import re
import sys
from pathlib import Path

SCRIPT_PATH = Path(__file__).resolve()
REPO_ROOT = SCRIPT_PATH.parent.parent
DESIGN_DOC = "DOCs/plans/VISIT-SIGNOFF-DESIGN.md"
DEFAULT_MANIFEST = REPO_ROOT / "DOCs" / "analyses" / "bench" / "SIGNOFF-MANIFEST.tsv"
DEFAULT_PREDICTIONS = REPO_ROOT / "DOCs" / "analyses" / "bench" / "SIGNOFF-DETECT-PREDICTIONS.tsv"
DEFAULT_BASELINE = REPO_ROOT / "DOCs" / "analyses" / "bench" / "2026-09-11" / "debug_260911-210229.log"
PL9_SOURCE = REPO_ROOT / "src" / "isp_bldc_motor.spin2"
FIXTURE_DIR = REPO_ROOT / "tools" / "fixtures" / "signoff"
NEGCASE_LOG = REPO_ROOT / "DOCs" / "analyses" / "bench" / "2026-09-13" / "debug_260913-120844.log"

EXIT_OK = 0
EXIT_SELFTEST_FAILED = 1
EXIT_INPUT = 2
EXIT_GAPS = 3

MANIFEST_COLUMNS = (
    "cell", "row", "task", "feature", "bin", "test", "crit", "lo", "hi", "units",
    "min_inst", "prov", "basis", "visit_owed", "status", "status_ref", "count_filter",
)
UNITS = {"COUNT", "MV_X10", "RPM", "TICKS", "MS", "PCT_X10", "BOOL", "COGID"}
BINS = {"SCAN", "SCANWD", "T0", "CHAR", "HOST"}
STATUSES = {"OWED", "SIGNED_OFF", "FAILED"}
BIN_SOURCES = {
    "SCAN": "src/test_bench_scan.spin2",
    "SCANWD": "src/test_bench_scan.spin2",
    "T0": "src/test_bench_t0.spin2",
    "CHAR": "src/test_bench_char.spin2",
}
VERDICT_TOKENS = ("PASS", "FAIL", "NOT_BUILT", "NOMEAS")
MOTOR_TOKENS = ("LEFT", "RIGHT", "NONE")
SIGNOFF_FIELDS = ("sf", "bin", "cell", "task", "motor", "crit", "measured", "lo", "hi", "units", "n", "verdict")
DECL_FIELDS = ("sf", "bin", "cell", "task")
SF_SUPPORTED = 1

CELL_ID_RE = re.compile(r"^R[0-9]+-[A-Z0-9]+-[A-Z0-9-]+$")
CRIT_RE = re.compile(r"^[A-Z0-9_]+$")
TOKEN_RE = re.compile(r"^[A-Za-z0-9_\-]+$")
PROV_RE = re.compile(r"^[MDS](/[MDS])*$")
PAIR_RE = re.compile(r"^(LEFT|RIGHT|NONE):([A-Z0-9_]+)$")
INT_RE = re.compile(r"^-?[0-9]+$")

# pnut-term-ts log lines (design B.5): "[timestamp] CogN  payload". Any cog number.
LOG_LINE_RE = re.compile(r"^\[([^\]]+)\] Cog([0-7])\s+(.*?)\s*$")
DOWNLOAD_RE = re.compile(
    r"^\[[^\]]+\] \[SYSTEM\] \[DOWNLOAD TO RAM\] File: (.+?) \| Size: ([0-9]+) bytes \| Modified: (\S+)\s*$")
SESSION_RE = re.compile(r"^=== Debug Logger Session Started at (\S+) ===")
BANNER_TAGS = ("BS-BANNER", "BC-BANNER", "BD-BANNER")
T0_BANNER_PREFIX = "* test_bench_t0"
HEADER_TAGS = ("BS-BUILD", "BC-BUILD", "BD-BUILD", "BD-CFG")
PL9_RE = re.compile(r"(?<![A-Za-z0-9_])gapinms(?![A-Za-z0-9_])", re.IGNORECASE)
WDT_CELLS = ("R11-WDT-FIRES", "R11-WDT-CKPT", "R11-WDT-STOPPED", "R11-WDT-STACK")
DECL_CALL_RE = re.compile(r"\b\w*signoffdecl\w*\s*\(", re.IGNORECASE)

# PL-40: record tokens are found anywhere in a line. The families are exactly the payloads this script reads.
READ_FAMILY_STARTS = ("SIGNOFF-DECL,", "SIGNOFF,", "DEBUG_END_SESSION", "BD-", T0_BANNER_PREFIX) + tuple(
    tag + "," for tag in BANNER_TAGS + HEADER_TAGS if not tag.startswith("BD-"))
RECORD_START_RE = re.compile(r"Cog([0-7])\s+(?=" + "|".join(re.escape(start) for start in READ_FAMILY_STARTS) + ")")
LINE_TS_RE = re.compile(r"^\[[^\]]+\] ")
# a pnut-term-ts hex-dump row: offset, 1-16 hex bytes, the 16-character ASCII gutter between '|', then any tail
HEX_ROW_RE = re.compile(r"^\[[^\]]+\]\s+([0-9A-Fa-f]{4,8}): (?:[0-9A-Fa-f]{2} ){1,16} *\|(.{16})\|(.*)$")
HEX_ROW_PREFIX_RE = re.compile(r"^\[[^\]]+\]\s+[0-9A-Fa-f]{4,8}: [0-9A-Fa-f]{2}\b")
CORRUPTION_MARKERS = ("[ROUTING ERROR", "[BINARY DATA")


# ---------------------------------------------------------------------------------------------
# External commands -- the single permitted route (none are used today)
# ---------------------------------------------------------------------------------------------

def run(argv):
    """Run one external command, echoing it verbatim first as "+ <argv>".

    This is the ONLY place this script may start a process (design D.1, the
    tools/bench-run.sh contract). Nothing calls it today; --selftest asserts
    that no subprocess use exists anywhere else.
    """
    print("+ " + " ".join(str(arg) for arg in argv), flush=True)
    import subprocess
    return subprocess.run([str(arg) for arg in argv], check=False).returncode


# ---------------------------------------------------------------------------------------------
# Small helpers
# ---------------------------------------------------------------------------------------------

def display_path(path):
    """Return path relative to the repo root when it lies inside it, else as given."""
    try:
        return str(Path(path).resolve().relative_to(REPO_ROOT))
    except (ValueError, OSError):
        return str(path)


def parse_int_token(token):
    """Parse an integer token that may carry '_' digit grouping (PL-17). None when not an integer."""
    stripped = token.replace("_", "")
    if INT_RE.match(stripped):
        return int(stripped)
    return None


def norm_limit(token, units):
    """Normalise a measured/lo/hi token for units.

    Returns ("NA", None), ("BOOL", 1|0) or ("INT", n); None when the token is
    illegal for the units (design B.1: TRUE/FALSE only under BOOL, numbers
    never under BOOL).
    """
    if token == "NA":
        return ("NA", None)
    if units == "BOOL":
        if token == "TRUE":
            return ("BOOL", 1)
        if token == "FALSE":
            return ("BOOL", 0)
        return None
    if token in ("TRUE", "FALSE"):
        return None
    value = parse_int_token(token)
    return None if value is None else ("INT", value)


def pairs_of(payload):
    """Split a tag-first record into a name -> value dict (first occurrence wins)."""
    tokens = payload.split(",")
    result = {}
    for name, value in zip(tokens[1::2], tokens[2::2]):
        result.setdefault(name.strip(), value.strip())
    return result


def worst_verdict(verdicts):
    """Row precedence, deliberately pessimistic (design D.4): FAIL > NOT_BUILT > NOMEAS > PASS."""
    for candidate in ("FAIL", "NOT_BUILT", "NOMEAS"):
        if candidate in verdicts:
            return candidate
    return "PASS" if verdicts else "NOT_BUILT"


# ---------------------------------------------------------------------------------------------
# Manifest
# ---------------------------------------------------------------------------------------------

class ManifestError(Exception):
    """The manifest is missing or does not satisfy design section A.2."""


class Cell:
    """One manifest line."""

    def __init__(self, raw, lineno):
        self.raw = dict(raw)
        self.lineno = lineno
        self.cell = raw["cell"]
        self.bin = raw["bin"]
        self.test = raw["test"]
        self.crit = raw["crit"]
        self.units = raw["units"]
        self.status = raw["status"]
        self.status_ref = raw["status_ref"]
        self.visit_owed = raw["visit_owed"]
        self.row_n = None
        self.task_norm = None
        self.lo_n = None
        self.hi_n = None
        self.min_n = None
        self.visit_n = None
        self.filter_set = set()

    def crit_matches(self, crit):
        """Design A.2: equal, or the manifest crit followed by '_' (per-channel variants)."""
        return crit == self.crit or crit.startswith(self.crit + "_")

    def set_status(self, status, status_ref):
        self.status = status
        self.status_ref = status_ref
        self.raw["status"] = status
        self.raw["status_ref"] = status_ref

    def fields(self):
        return [self.raw[name] for name in MANIFEST_COLUMNS]


def _validate_cell(cell, where):
    raw = cell.raw

    def bad(message):
        raise ManifestError(f"{where}: cell {raw.get('cell') or '?'}: {message}")

    if not CELL_ID_RE.match(raw["cell"]) or len(raw["cell"]) > 20:
        bad("cell id must match R<row>-<BIN>-<SHORT> and be at most 20 chars")
    if not raw["row"].isdigit() or int(raw["row"]) < 1:
        bad("row must be a positive integer")
    cell.row_n = int(raw["row"])
    if not raw["cell"].startswith(f"R{cell.row_n}-"):
        bad("cell id must start with R<row>-")
    task = parse_int_token(raw["task"])
    if task is None or task < 0:
        bad("task must be a todo-mcp task number")
    cell.task_norm = str(task)
    if not raw["feature"]:
        bad("feature is empty")
    if raw["bin"] not in BINS:
        bad(f"bin must be one of {sorted(BINS)}")
    if not raw["test"]:
        bad("test is empty")
    if not CRIT_RE.match(raw["crit"]) or len(raw["crit"]) > 18:
        bad("crit must be an upper-case token of at most 18 chars")
    if raw["units"] not in UNITS:
        bad(f"units must be one of {sorted(UNITS)}")
    cell.lo_n = norm_limit(raw["lo"], raw["units"])
    cell.hi_n = norm_limit(raw["hi"], raw["units"])
    if cell.lo_n is None or cell.hi_n is None:
        bad("lo/hi must be NA, TRUE/FALSE under BOOL, or an integer otherwise")
    if cell.lo_n[0] != "NA" and cell.hi_n[0] != "NA" and cell.lo_n[1] > cell.hi_n[1]:
        bad("lo is greater than hi")
    if not raw["min_inst"].isdigit() or int(raw["min_inst"]) < 1:
        bad("min_inst must be a positive integer")
    cell.min_n = int(raw["min_inst"])
    if not PROV_RE.match(raw["prov"]):
        bad("prov must be M, D or S (or a slash-joined combination)")
    if not raw["basis"]:
        bad("basis is empty")
    if raw["visit_owed"] == "DEFERRED":
        cell.visit_n = None
    elif raw["visit_owed"].isdigit() and int(raw["visit_owed"]) >= 1:
        cell.visit_n = int(raw["visit_owed"])
    else:
        bad("visit_owed must be a positive integer or DEFERRED")
    if raw["status"] not in STATUSES:
        bad(f"status must be one of {sorted(STATUSES)}")
    if raw["status"] == "OWED" and raw["status_ref"]:
        bad("status_ref must be empty while OWED")
    if raw["status"] != "OWED" and not raw["status_ref"]:
        bad("status_ref is required for SIGNED_OFF/FAILED")
    if raw["count_filter"]:
        for pair in raw["count_filter"].split(","):
            match = PAIR_RE.match(pair.strip())
            if not match:
                bad(f"count_filter entry {pair!r} is not MOTOR:CRIT")
            if not cell.crit_matches(match.group(2)):
                bad(f"count_filter crit {match.group(2)} does not match crit {raw['crit']}")
            cell.filter_set.add(f"{match.group(1)}:{match.group(2)}")
        if cell.min_n > len(cell.filter_set):
            bad("min_inst exceeds the count_filter pairs, so the cell could never PASS")


def load_manifest(path):
    """Load and validate the manifest. Raises ManifestError."""
    path = Path(path)
    if not path.is_file():
        raise ManifestError(f"manifest not found: {path}")
    lines = path.read_text(encoding="utf-8").splitlines()
    if not lines:
        raise ManifestError(f"{path}: manifest is empty")
    if tuple(lines[0].split("\t")) != MANIFEST_COLUMNS:
        raise ManifestError(f"{path}:1: header must be the tab-separated columns {', '.join(MANIFEST_COLUMNS)}")
    cells = []
    seen = {}
    for lineno, line in enumerate(lines[1:], start=2):
        where = f"{path}:{lineno}"
        if not line.strip():
            raise ManifestError(f"{where}: blank line")
        parts = line.split("\t")
        # the two trailing columns (status_ref, count_filter) may be empty and their tabs omitted
        if not (len(MANIFEST_COLUMNS) - 2 <= len(parts) <= len(MANIFEST_COLUMNS)):
            raise ManifestError(f"{where}: {len(parts)} tab-separated fields, expected {len(MANIFEST_COLUMNS)}")
        parts = [part.strip() for part in parts] + [""] * (len(MANIFEST_COLUMNS) - len(parts))
        cell = Cell(dict(zip(MANIFEST_COLUMNS, parts)), lineno)
        _validate_cell(cell, where)
        if cell.cell in seen:
            raise ManifestError(f"{where}: duplicate cell {cell.cell} (first at line {seen[cell.cell]})")
        seen[cell.cell] = lineno
        cells.append(cell)
    return cells


def write_manifest(path, cells):
    """Rewrite the manifest .tsv (only statuses ever change)."""
    out = ["\t".join(MANIFEST_COLUMNS)]
    for cell in cells:
        fields = cell.fields()
        while len(fields) > len(MANIFEST_COLUMNS) - 2 and fields[-1] == "":
            fields.pop()
        out.append("\t".join(fields))
    Path(path).write_text("\n".join(out) + "\n", encoding="utf-8")


def _md_cell(text):
    return text.replace("|", "\\|") if text else "-"


def render_manifest_md(cells):
    """Render SIGNOFF-MANIFEST.md, the GENERATED view of the .tsv (design A.1)."""
    out = [
        "# GENERATED -- edit the .tsv",
        "",
        "This view is regenerated from `SIGNOFF-MANIFEST.tsv` by `tools/signoff-collate.py`. Never edit it by "
        f"hand: the `.tsv` is the single source (design `{DESIGN_DOC}` section A.1).",
        "",
    ]
    row_numbers = sorted({cell.row_n for cell in cells})
    for row_n in row_numbers:
        members = [cell for cell in cells if cell.row_n == row_n]
        tasks = []
        for cell in members:
            if cell.raw["task"] not in tasks:
                tasks.append(cell.raw["task"])
        out.append(f"## Row {row_n} -- task {', '.join(tasks)}: {members[0].raw['feature']}")
        out.append("")
        out.append("| cell | bin | test | crit | lo | hi | units | min_inst | count_filter | prov | visit_owed "
                   "| status | status_ref | basis |")
        out.append("|---|---|---|---|---|---|---|---|---|---|---|---|---|---|")
        for cell in members:
            values = [cell.raw[name] for name in ("cell", "bin", "test", "crit", "lo", "hi", "units", "min_inst",
                                                  "count_filter", "prov", "visit_owed", "status", "status_ref",
                                                  "basis")]
            out.append("| " + " | ".join(_md_cell(value) for value in values) + " |")
        out.append("")
    return "\n".join(out).rstrip("\n") + "\n"


# ---------------------------------------------------------------------------------------------
# Log reader (design B.5, D.3) -- the part the 3509 analyser should import rather than copy
# ---------------------------------------------------------------------------------------------

class Message:
    """One cog message of a family this script reads, found in one log line (PL-40).

    recovered: the message did not start the line -- it sat after a hex-dump
    row's ASCII gutter, mid-line after other text, or on a line with no
    timestamp prefix; context says which, and which terminal markers the line
    carries. cut: why the message has no observed end (it runs into a terminal
    marker or another record token on the same line), else None.
    """

    def __init__(self, lineno, cog, payload, recovered, context, cut):
        self.lineno = lineno
        self.cog = cog
        self.payload = payload
        self.recovered = recovered
        self.context = context
        self.cut = cut
        self.record = None                  # the Record built from it, for SIGNOFF / SIGNOFF-DECL

    @property
    def tag(self):
        return self.payload.split(",", 1)[0]

    @property
    def flag(self):
        return f"RECOVERED from a corrupted line: {self.context}" if self.recovered else ""


def scan_line(lineno, line):
    """Find every read-family cog message anywhere in one log line (PL-40).

    Returns (messages, row, loose_signoff): row is (offset, gutter) for a
    hex-dump row, else None; loose_signoff is True when a corrupted line shows
    SIGNOFF text outside every SIGNOFF / SIGNOFF-DECL message found on it.
    Only the text after a hex-dump row's gutter is searched; a row that does not
    parse as a dump row is not searched at all.
    """
    row = HEX_ROW_RE.match(line)
    if row:
        region, row_info = row.group(3), (int(row.group(1), 16), row.group(2))
        where = ["text after a hex-dump row's ASCII gutter"]
    elif HEX_ROW_PREFIX_RE.match(line):
        return [], None, "SIGNOFF" in line
    else:
        stamp = LINE_TS_RE.match(line)
        region, row_info = (line[stamp.end():] if stamp else line), None
        where = [] if stamp else ["a line with no timestamp prefix"]
    markers = [marker for marker in CORRUPTION_MARKERS if marker in line]
    starts = list(RECORD_START_RE.finditer(region))
    messages = []
    remainder = region
    for index, match in enumerate(starts):
        begin, end, cut = match.end(), len(region), None
        if index + 1 < len(starts):
            following = starts[index + 1]
            end = following.start()
            cut = (f"runs into another record token ({region[following.start():following.end()].strip()} "
                   f"{region[following.end():following.end() + 16]}...) on the same line")
        for marker in CORRUPTION_MARKERS:
            at = region.find(marker, begin)
            if at != -1 and at < end:
                end, cut = at, f"runs into '{marker}' on the same line"
        context = list(where)
        if row is None and match.start() > 0:
            context.append("mid-line, after other text")
        recovered = bool(context)
        context += [f"the line carries '{marker}'" for marker in markers]
        payload = region[begin:end].rstrip()
        messages.append(Message(lineno, int(match.group(1)), payload, recovered, "; ".join(context), cut))
        if payload.startswith(("SIGNOFF,", "SIGNOFF-DECL,")):
            remainder = remainder.replace(payload, "", 1)
    corrupted = row is not None or bool(markers) or any(message.recovered for message in messages)
    return messages, row_info, corrupted and "SIGNOFF" in remainder


class Record:
    """One SIGNOFF or SIGNOFF-DECL record."""

    def __init__(self, kind, log, lineno, cog, payload, message=None):
        self.kind = kind                    # "SIGNOFF" or "DECL"
        self.log = log
        self.lineno = lineno
        self.cog = cog
        self.payload = payload
        self.message = message
        self.fields = {}
        self.norm = {}
        self.error = None
        self.cell = None
        self._parse()

    @property
    def kind_tag(self):
        return "SIGNOFF" if self.kind == "SIGNOFF" else "SIGNOFF-DECL"

    @property
    def ref(self):
        return f"{self.log.display}:{self.lineno}"

    @property
    def recovered(self):
        return self.message is not None and self.message.recovered

    @property
    def flag(self):
        return self.message.flag if self.message is not None else ""

    def _parse(self):
        expected = SIGNOFF_FIELDS if self.kind == "SIGNOFF" else DECL_FIELDS
        rest = [token.strip() for token in self.payload.split(",")[1:]]
        names = rest[0::2]
        values = rest[1::2]
        for index, name in enumerate(names):
            if name == "cell" and index < len(values) and values[index]:
                self.cell = values[index]
                break
        if self.message is not None and self.message.cut:
            # its end was not observed: never judged, whatever its fields look like (PL-40)
            self.error = f"MALFORMED: the record {self.message.cut}, so its end was not observed"
            return
        if len(rest) != 2 * len(expected):
            self.error = f"MALFORMED: {len(rest)} fields after the tag, expected {2 * len(expected)} ({len(expected)} name/value pairs)"
            return
        if tuple(names) != expected:
            self.error = f"MALFORMED: field names/order {','.join(names)} != {','.join(expected)}"
            return
        fields = dict(zip(names, values))
        self.fields = fields
        sf_value = parse_int_token(fields["sf"])
        if sf_value != SF_SUPPORTED:
            self.error = f"MALFORMED: sf {fields['sf']!r} is not the supported sign-off format {SF_SUPPORTED}"
            return
        for name in ("bin", "cell"):
            if not TOKEN_RE.match(fields[name]):
                self.error = f"MALFORMED: {name} {fields[name]!r} is not a token"
                return
        task = parse_int_token(fields["task"])
        if task is None or task < 0:
            self.error = f"MALFORMED: task {fields['task']!r} is not a task number"
            return
        self.norm["task"] = str(task)
        if self.kind == "DECL":
            return
        if fields["motor"] not in MOTOR_TOKENS:
            self.error = f"MALFORMED: motor {fields['motor']!r} is not LEFT/RIGHT/NONE"
            return
        for name in ("crit", "units"):
            if not TOKEN_RE.match(fields[name]):
                self.error = f"MALFORMED: {name} {fields[name]!r} is not a token"
                return
        for name in ("measured", "lo", "hi"):
            normalised = norm_limit(fields[name], fields["units"])
            if normalised is None:
                if fields["units"] == "BOOL":
                    self.error = f"MALFORMED: {name} {fields[name]!r} under units BOOL (needs TRUE/FALSE/NA)"
                else:
                    self.error = f"MALFORMED: {name} {fields[name]!r} is not a number or NA under units {fields['units']}"
                return
            self.norm[name] = normalised
        count = parse_int_token(fields["n"])
        if count is None or count < 0:
            self.error = f"MALFORMED: n {fields['n']!r} is not a non-negative integer"
            return
        self.norm["n"] = count
        if fields["verdict"] not in VERDICT_TOKENS:
            self.error = f"MALFORMED: verdict {fields['verdict']!r} is not PASS/FAIL/NOT_BUILT/NOMEAS"
            return


class LogInfo:
    """One debug log: identity, completeness and its sign-off records."""

    def __init__(self, name, text, path=None):
        self.path = Path(path) if path is not None else None
        self.display = display_path(path) if path is not None else name
        self.records = []
        self.downloads = []                 # (file, size, mtime, lineno)
        self.first_ts = None
        self.end_lineno = None
        self.end_cog = None
        self.banner_tag = None
        self.banner_lineno = None
        self.banner_pairs = {}
        self.header_pairs = {}
        self.header_lines = {}
        self.header_messages = {}
        self.banner_message = None
        self.end_message = None
        self.messages = []                  # every read-family message, in line order (the BD- reader uses it)
        self.unparsed_signoff = []          # (first line, last line, what): SIGNOFF text that yielded no record
        self._dump = None                   # [first line, last line, concatenated gutter text] of the open dump
        lines = text.splitlines()
        self.lines = lines
        self.line_count = len(lines)
        for lineno, line in enumerate(lines, start=1):
            self._scan_line(lineno, line)
        self._close_dump()
        self.declared_cells = {rec.cell for rec in self.records if rec.kind == "DECL" and rec.cell}

    def _close_dump(self):
        if self._dump is not None and "SIGNOFF" in self._dump[2]:
            self.unparsed_signoff.append((self._dump[0], self._dump[1],
                                          "SIGNOFF text inside a hex dump's ASCII gutter (bytes the terminal "
                                          "routed as binary; never parsed)"))
        self._dump = None

    def _scan_line(self, lineno, line):
        session = SESSION_RE.match(line)
        if session:
            self._close_dump()
            if self.first_ts is None:
                self.first_ts = session.group(1)
            return
        download = DOWNLOAD_RE.match(line)
        if download:
            self._close_dump()
            self.downloads.append((download.group(1).strip(), download.group(2), download.group(3), lineno))
            return
        match = LOG_LINE_RE.match(line)
        if match and self.first_ts is None:
            self.first_ts = match.group(1)
        messages, row, loose_signoff = scan_line(lineno, line)
        if row is None or row[0] == 0:
            self._close_dump()
        if row is not None:
            if self._dump is None:
                self._dump = [lineno, lineno, ""]
            self._dump[1] = lineno
            self._dump[2] += row[1]
        if loose_signoff:
            self.unparsed_signoff.append((lineno, lineno, "SIGNOFF text on a corrupted line outside any whole "
                                                          "SIGNOFF / SIGNOFF-DECL record token; not parsed"))
        for message in messages:
            self._take(message)

    def _take(self, message):
        self.messages.append(message)
        lineno, cog, payload = message.lineno, message.cog, message.payload
        # the ONLY verdict-bearing parse: nothing else in a log is read for a verdict (design E.1)
        if payload.startswith("SIGNOFF,"):
            message.record = Record("SIGNOFF", self, lineno, cog, payload, message)
            self.records.append(message.record)
            return
        if payload.startswith("SIGNOFF-DECL,"):
            message.record = Record("DECL", self, lineno, cog, payload, message)
            self.records.append(message.record)
            return
        if message.cut:
            return                          # no observed end: never read (PL-40)
        if payload == "DEBUG_END_SESSION":
            if self.end_lineno is None:
                self.end_lineno, self.end_cog, self.end_message = lineno, cog, message
            return
        if self.banner_tag is None:
            for tag in BANNER_TAGS:
                if payload.startswith(tag + ","):
                    self.banner_tag, self.banner_lineno, self.banner_pairs = tag, lineno, pairs_of(payload)
                    self.banner_message = message
                    break
            if self.banner_tag is None and payload.startswith(T0_BANNER_PREFIX):
                self.banner_tag, self.banner_lineno, self.banner_pairs = "T0", lineno, {}
                self.banner_message = message
        for tag in HEADER_TAGS:
            if payload.startswith(tag + ",") and tag not in self.header_pairs:
                self.header_pairs[tag] = pairs_of(payload)
                self.header_lines[tag] = lineno
                self.header_messages[tag] = message

    @property
    def flagged_messages(self):
        """Messages recovered from a corrupted line, or cut short on their line (PL-40)."""
        return [message for message in self.messages if message.recovered or message.cut]

    def message_status(self, message):
        """How the collation used one flagged message, for the sheet."""
        if message.record is not None:
            if message.record.error:
                return f"MALFORMED, not counted: {message.record.error}"
            return "parsed and counted like a line-start record"
        if message.cut:
            return f"not read: it {message.cut}, so its end was not observed"
        return "read like a line-start message"

    # ---- identity and completeness -------------------------------------------------------

    @property
    def complete(self):
        """COMPLETE iff a CogN DEBUG_END_SESSION line exists (design D.3.2)."""
        return self.end_lineno is not None

    @property
    def completeness_text(self):
        if self.complete:
            return f"COMPLETE (DEBUG_END_SESSION at line {self.end_lineno}, Cog{self.end_cog})"
        return "TRUNCATED (no DEBUG_END_SESSION line)"

    @property
    def download(self):
        return self.downloads[-1] if self.downloads else None

    @property
    def src_rev(self):
        value = self.banner_pairs.get("src_rev")
        if value is None:
            for tag in ("BS-BUILD", "BC-BUILD", "BD-BUILD"):
                if "src_rev" in self.header_pairs.get(tag, {}):
                    value = self.header_pairs[tag]["src_rev"]
                    break
        return value.replace("_", "") if value is not None else None

    @property
    def fmt(self):
        value = self.banner_pairs.get("fmt")
        return value.replace("_", "") if value is not None else None

    @property
    def build_key(self):
        """Build identity used to group logs (design D.4 as amended).

        banner tag + src_rev + fmt + .bin name + .bin size. The .bin modified
        time is recorded and printed but is NOT part of the key: tools/bench-run.sh
        recompiles on every run, so the modified time differs on every rerun of
        unchanged source, and keying on it would let a rerun supersede a FAIL.
        """
        download = self.download
        return (
            self.banner_tag or "NO_BANNER",
            self.src_rev or "NA",
            self.fmt or "NA",
            download[0] if download else "NO_DOWNLOAD_HEADER",
            download[1] if download else "NA",
        )

    @property
    def order_key(self):
        download = self.download
        return (download[2] if download else "", self.first_ts or "", self.display)

    def identity_text(self):
        parts = []
        if self.banner_tag == "T0":
            parts.append(f"banner '* test_bench_t0' at line {self.banner_lineno} -- Tier 0 prints no src_rev/fmt, "
                         "so the download header identifies its build")
        elif self.banner_tag:
            parts.append(f"{self.banner_tag} src_rev {self.src_rev or 'NA'} fmt {self.fmt or 'NA'} "
                         f"(line {self.banner_lineno})")
        else:
            parts.append("no banner record")
        download = self.download
        if download:
            parts.append(f"download {download[0]}, {download[1]} bytes, modified {download[2]} (line {download[3]})")
            distinct = {entry[:3] for entry in self.downloads}
            if len(distinct) > 1:
                parts.append(f"NOTE {len(distinct)} distinct download headers; the last is used")
        else:
            parts.append("no download header")
        return "; ".join(parts)


def build_key_text(key):
    return f"banner {key[0]}, src_rev {key[1]}, fmt {key[2]}, bin {key[3]}, size {key[4]}"


def read_log_file(path):
    path = Path(path)
    return LogInfo(path.name, path.read_text(encoding="utf-8", errors="replace"), path=path)


# ---------------------------------------------------------------------------------------------
# Verdicts
# ---------------------------------------------------------------------------------------------

class Instance:
    """One judged instance of a cell from one log line."""

    def __init__(self, rec, verdict, reason, counts, pair):
        self.rec = rec
        self.log = rec.log
        self.verdict = verdict
        self.reason = reason
        self.counts = counts
        self.pair = pair

    @property
    def ref(self):
        return self.rec.ref

    def describe(self):
        fields = self.rec.fields
        if self.rec.kind == "SIGNOFF" and fields:
            body = (f"motor {fields['motor']} crit {fields['crit']} measured {fields['measured']} lo {fields['lo']} "
                    f"hi {fields['hi']} units {fields['units']} n {fields['n']} printed {fields['verdict']}")
        else:
            body = f"{self.rec.kind_tag} {self.rec.payload}"
        text = f"{self.ref} {body} -> {self.verdict}"
        if self.reason:
            text += f" ({self.reason})"
        if not self.counts:
            text += " [outside count_filter]"
        if self.rec.flag:
            text += f" [{self.rec.flag}]"
        return text


def decl_issue(rec, cell):
    """A declaration that does not match the manifest yields a NOMEAS instance."""
    if rec.error:
        return "MALFORMED"
    if rec.fields["bin"] != cell.bin:
        return "DECL_BIN_MISMATCH"
    if rec.norm["task"] != cell.task_norm:
        return "DECL_TASK_MISMATCH"
    return None


def judge_signoff(rec, cell, declared, complete):
    """Validate one SIGNOFF record against its manifest cell (design D.3.4 as amended)."""
    if rec.error:
        return Instance(rec, "NOMEAS", "MALFORMED", True, None)
    fields = rec.fields
    norm = rec.norm
    pair = f"{fields['motor']}:{fields['crit']}"
    counts = (not cell.filter_set) or (pair in cell.filter_set)
    if fields["bin"] != cell.bin:
        return Instance(rec, "NOMEAS", "BIN_MISMATCH", counts, pair)
    if norm["task"] != cell.task_norm:
        return Instance(rec, "NOMEAS", "TASK_MISMATCH", counts, pair)
    if not cell.crit_matches(fields["crit"]):
        return Instance(rec, "NOMEAS", "CRIT_MISMATCH", counts, pair)
    if fields["units"] != cell.units:
        return Instance(rec, "NOMEAS", "UNITS_MISMATCH", counts, pair)
    if norm["lo"] != cell.lo_n or norm["hi"] != cell.hi_n:
        return Instance(rec, "NOMEAS", "LIMIT_MISMATCH", counts, pair)
    printed = fields["verdict"]
    if printed == "NOT_BUILT":
        return Instance(rec, "NOMEAS", "BIN_NOT_BUILT", counts, pair)
    if printed == "NOMEAS":
        return Instance(rec, "NOMEAS", "BIN_NOMEAS", counts, pair)
    verdict, reason = printed, ""
    measured = norm["measured"]
    if measured[0] == "NA":
        # a PASS with nothing measured contradicts itself; a FAIL with NA is legitimate (e.g. never cleared)
        if printed == "PASS":
            verdict, reason = "FAIL", "VERDICT_INCONSISTENT"
    else:
        value = measured[1]
        low, high = norm["lo"], norm["hi"]
        inside = (low[0] == "NA" or value >= low[1]) and (high[0] == "NA" or value <= high[1])
        if printed == "PASS" and not inside:
            verdict, reason = "FAIL", "VERDICT_INCONSISTENT"
        elif printed == "FAIL" and inside:
            verdict, reason = "FAIL", "VERDICT_INCONSISTENT"
    if verdict == "PASS" and not declared:
        verdict, reason = "NOMEAS", "UNDECLARED"
    if verdict == "PASS" and not complete:
        verdict, reason = "NOMEAS", "LOG_TRUNCATED"
    return Instance(rec, verdict, reason, counts, pair)


class LogCell:
    """One log's verdict for one cell."""

    def __init__(self, log, verdict, reason, instances, note=""):
        self.log = log
        self.verdict = verdict
        self.reason = reason
        self.instances = instances
        self.note = note

    def text(self):
        extra = "; ".join(part for part in (self.reason, self.note) if part)
        return f"{self.log.display}: {self.verdict}" + (f" ({extra})" if extra else "")


def evaluate_log_for_cell(cell, log, instances):
    """Per-log verdict (design D.4 table), with min_inst met inside this one log only."""
    if not instances:
        return LogCell(log, "NOMEAS", "NOT_REACHED", instances, "declared, no SIGNOFF instance")
    fails = [inst for inst in instances if inst.verdict == "FAIL"]
    if fails:
        return LogCell(log, "FAIL", fails[0].reason or "BINARY_FAIL", instances)
    # outside a count_filter an instance can only FAIL the cell; its NOMEAS does not block
    blocking = [inst for inst in instances if inst.verdict != "PASS" and inst.counts]
    if blocking:
        return LogCell(log, "NOMEAS", blocking[0].reason, instances)
    passes = [inst for inst in instances if inst.verdict == "PASS" and inst.counts]
    if cell.filter_set:
        counted = len({inst.pair for inst in passes})
    else:
        counted = len(passes)
    note = f"{counted} of {cell.min_n} counted PASS instances"
    if counted >= cell.min_n:
        return LogCell(log, "PASS", "", instances, note)
    return LogCell(log, "NOMEAS", "TOO_FEW_INSTANCES", instances, note)


class CellResult:
    def __init__(self, verdict, reason="", detail=None, proving=None, refs=None, superseded=None):
        self.verdict = verdict
        self.reason = reason
        self.detail = detail or []
        self.proving = proving or []
        self.refs = refs or []
        self.superseded = superseded or []
        self.extra = {}                     # R2-HOST-DETDIFF: {"logs": [(LogInfo, per-log diff dict)]}


def evaluate_signoff_cell(cell, logs):
    """A binary-judged cell (design D.4 as amended: a rerun cannot hide a FAIL)."""
    speaking = []
    for log in logs:
        declared = cell.cell in log.declared_cells
        instances = []
        for rec in log.records:
            if rec.cell != cell.cell:
                continue
            if rec.kind == "DECL":
                issue = decl_issue(rec, cell)
                if issue:
                    instances.append(Instance(rec, "NOMEAS", issue, True, None))
            else:
                instances.append(judge_signoff(rec, cell, declared, log.complete))
        if declared or instances:
            speaking.append((log, instances))
    if not speaking:
        return CellResult("NOT_BUILT", "NO_DECLARING_LOG",
                          ["no input log declares this cell (SIGNOFF-DECL) or prints a verdict for it"])
    builds = {}
    for log, instances in speaking:
        builds.setdefault(log.build_key, []).append((log, instances))
    ordered = sorted(builds.items(), key=lambda item: max(log.order_key for log, _ in item[1]))
    latest_key, latest_members = ordered[-1]
    latest_members = sorted(latest_members, key=lambda member: member[0].order_key)
    results = [evaluate_log_for_cell(cell, log, instances) for log, instances in latest_members]
    superseded = []
    for key, members in ordered[:-1]:
        for log, instances in members:
            superseded.append((key, evaluate_log_for_cell(cell, log, instances)))
    detail = [f"speaking build: {build_key_text(latest_key)} ({len(results)} log(s))"]
    detail += [result.text() for result in results]
    if superseded:
        detail.append(f"{len(superseded)} log(s) from earlier builds superseded (see Superseded logs)")
    fails = [result for result in results if result.verdict == "FAIL"]
    if fails:
        failing = [inst for result in fails for inst in result.instances if inst.verdict == "FAIL"]
        return CellResult("FAIL", fails[0].reason, detail, [inst.describe() for inst in failing],
                          [inst.ref for inst in failing], superseded)
    passes = [result for result in results if result.verdict == "PASS"]
    if passes:
        proving_log = passes[0]
        counted = [inst for inst in proving_log.instances if inst.verdict == "PASS" and inst.counts]
        if cell.filter_set:
            detail.append("counted channels that passed: " + ", ".join(sorted({inst.pair for inst in counted})))
        return CellResult("PASS", "", detail, [inst.describe() for inst in proving_log.instances],
                          [inst.ref for inst in counted], superseded)
    if cell.filter_set:
        counted = sorted({inst.pair for result in results for inst in result.instances
                          if inst.verdict == "PASS" and inst.counts})
        detail.append("counted channels that passed: " + (", ".join(counted) if counted else "none"))
    return CellResult("NOMEAS", results[-1].reason, detail,
                      [inst.describe() for result in results for inst in result.instances], [], superseded)


# ---------------------------------------------------------------------------------------------
# HOST cells (design C.1-C.3, G.4)
# ---------------------------------------------------------------------------------------------

def check_pl9_text(text):
    """R10-HOST-PL9 on one source text: PASS iff the identifier gapInMS appears nowhere.

    Spin2 identifiers are case-insensitive, so the match is too. Returns
    (verdict, [line numbers]).
    """
    hits = [lineno for lineno, line in enumerate(text.splitlines(), start=1) if PL9_RE.search(line)]
    return ("PASS" if not hits else "FAIL"), hits


def host_pl9(static_tree, source_path):
    if not static_tree:
        return CellResult("NOT_BUILT", "STATIC_NOT_REQUESTED",
                          ["run with --static-tree to evaluate this static source cell"])
    source_path = Path(source_path)
    if not source_path.is_file():
        return CellResult("NOT_BUILT", "INPUT_ABSENT", [f"source not found: {display_path(source_path)}"])
    verdict, hits = check_pl9_text(source_path.read_text(encoding="utf-8", errors="replace"))
    rel = display_path(source_path)
    if verdict == "PASS":
        return CellResult("PASS", "", ["measured 0 occurrences, lo 0, hi 0, COUNT"],
                          [f"{rel}: identifier gapInMS absent (case-insensitive)"], [f"STATIC:{rel}"])
    return CellResult("FAIL", "GAPINMS_PRESENT", [f"measured {len(hits)} occurrence line(s), lo 0, hi 0, COUNT"],
                      [f"{rel}:{lineno}: gapInMS present" for lineno in hits],
                      [f"{rel}:{lineno}" for lineno in hits])


def host_wdtend(logs):
    """R11-HOST-WDTEND (design G.4)."""
    candidates = [log for log in logs if log.header_pairs.get("BS-BUILD", {}).get("wd_selftest") == "TRUE"]
    if not candidates:
        return CellResult("NOT_BUILT", "NO_WD_SELFTEST_LOG",
                          ["no input log carries BS-BUILD wd_selftest,TRUE"])
    builds = {}
    for log in candidates:
        builds.setdefault(log.build_key, []).append(log)
    ordered = sorted(builds.items(), key=lambda item: max(log.order_key for log in item[1]))
    latest_key, members = ordered[-1]
    detail = [f"speaking build: {build_key_text(latest_key)}"]
    failing, proving, refs = [], [], []
    for log in sorted(members, key=lambda entry: entry.order_key):
        problems = []
        if not log.complete:
            problems.append("LOG_TRUNCATED: the session did not end itself")
        log_refs, record_lines = [], []
        for cell_id in WDT_CELLS:
            records = [rec for rec in log.records if rec.kind == "SIGNOFF" and rec.cell == cell_id]
            if not records:
                problems.append(f"{cell_id}_MISSING")
            for rec in records:
                log_refs.append(rec.ref)
                record_lines.append(f"{rec.ref} R11-WDT record from a non-zero cog" + (f" [{rec.flag}]" if rec.flag else ""))
                if rec.cog == 0:
                    problems.append(f"{cell_id}_FROM_COG0 at {rec.ref}")
                if log.end_lineno is not None and rec.lineno > log.end_lineno:
                    problems.append(f"{cell_id}_AFTER_END at {rec.ref}")
        build_flag = log.header_messages["BS-BUILD"].flag
        build_line = (f"{log.display}:{log.header_lines['BS-BUILD']} BS-BUILD wd_selftest TRUE"
                      + (f" [{build_flag}]" if build_flag else ""))
        if problems:
            failing.append(log)
            detail.append(f"{log.display}: FAIL ({'; '.join(problems)})")
        else:
            detail.append(f"{log.display}: PASS")
            if not proving:
                end_flag = log.end_message.flag
                proving = [build_line] + record_lines
                proving.append(f"{log.display}:{log.end_lineno} DEBUG_END_SESSION after them"
                               + (f" [{end_flag}]" if end_flag else ""))
                refs = [f"{log.display}:{log.header_lines['BS-BUILD']}"] + log_refs + [f"{log.display}:{log.end_lineno}"]
    if failing:
        return CellResult("FAIL", "WDTEND_CONDITION_FAILED", detail + ["measured FALSE, lo TRUE, hi TRUE, BOOL"],
                          [f"{log.display}: see detail" for log in failing],
                          [f"{log.display}:{log.header_lines['BS-BUILD']}" for log in failing])
    return CellResult("PASS", "", detail + ["measured TRUE, lo TRUE, hi TRUE, BOOL"], proving, refs)


def is_detect_phase2_log(log):
    """Design C.2 input 1: BD-BANNER tool test_bench_detect, BD-BUILD phase2_compiled 1, BD-CFG cfg_id BENCH."""
    return (log.banner_tag == "BD-BANNER"
            and log.banner_pairs.get("tool") == "test_bench_detect"
            and log.header_pairs.get("BD-BUILD", {}).get("phase2_compiled") in ("1", "TRUE")
            and log.header_pairs.get("BD-CFG", {}).get("cfg_id") == "BENCH")


def _same_file(first, second):
    try:
        return first is not None and Path(first).resolve() == Path(second).resolve()
    except OSError:
        return False


def _detect_inputs(logs, ctx, need_baseline, need_predictions):
    missing = []
    detect_logs = [log for log in logs if is_detect_phase2_log(log) and not _same_file(log.path, ctx["baseline"])]
    if not detect_logs:
        missing.append("no detect-phase2 log among the inputs (BD-BANNER tool test_bench_detect, "
                       "BD-BUILD phase2_compiled 1, BD-CFG cfg_id BENCH)")
    if need_predictions and not Path(ctx["predictions"]).is_file():
        missing.append(f"prediction list absent: {display_path(ctx['predictions'])}")
    if need_baseline and not Path(ctx["baseline"]).is_file():
        missing.append(f"baseline log absent: {display_path(ctx['baseline'])}")
    return detect_logs, missing


def host_detdiff(logs, ctx):
    """R2-HOST-DETDIFF (design C.2): needs a detect-phase2 log, the baseline and the prediction list."""
    detect_logs, missing = _detect_inputs(logs, ctx, need_baseline=True, need_predictions=True)
    if missing:
        return CellResult("NOT_BUILT", "INPUT_ABSENT", missing)
    return detdiff_compare(detect_logs, read_log_file(ctx["baseline"]), Path(ctx["predictions"]))


def host_detect_guard(logs, ctx):
    """R2-DETECT-GUARD (design C.3 item 5): needs only a detect-phase2 log; its skip set comes from that log."""
    detect_logs, missing = _detect_inputs(logs, ctx, need_baseline=False, need_predictions=False)
    if missing:
        return CellResult("NOT_BUILT", "INPUT_ABSENT", missing)
    return detect_guard_check(detect_logs)


# ---- the detection binary's BD- records (test_bench_detect.spin2, SRC_REV 3 / FMT 2) -----------

DETECT_GROUPS = {"P0_P15": 0, "P8_P23": 8, "P16_P31": 16, "NO_USE_P24_P39": 24, "P32_P47": 32, "P40_P55": 40}
DETECT_SWEEP_ORDER = ("P0_P15", "P16_P31", "P32_P47", "P40_P55", "P8_P23", "NO_USE_P24_P39")   # grpSweepOrder
DETECT_TAIL_GROUPS = 2                      # TAIL_GROUP_COUNT, dropped by -D DETECT_NO_TAIL
DETECT_GROUP_SPAN = 16                      # GROUP_SPAN
DETECT_SENSE_OFFSET = 4                     # SENSE_PIN_OFFSET
DETECT_VOID_SWEEPS = (3, 6)                 # running-driver cells, void by design (design C.2)
DETECT_POSTSTOP_SWEEPS = (4, 5, 7, 8)
DETECT_POSTSTOP_GROUPS = ("P0_P15", "P16_P31")
DETDIFF_EXACT_FIELDS = ("modal", "libvrd", "agree", "va", "vb", "vn")
DETDIFF_SUM_FIELDS = ("sum_min", "sum_max", "sum_mean")
DETDIFF_SUM_EXACT_BASELINES = (0, 500)
DETDIFF_SUM_TOLERANCE = 11                  # measured Rev B band 93-104, isp_bldc_motor.spin2:851-853
DETDIFF_ENUM_FIELDS = ("local", "lib", "match")
DETDIFF_VARIANT_FIELDS = ("lib_linked", "phase2_compiled", "tail_groups")
PREDICTION_COLUMNS = ("sw", "grp", "field", "baseline_value", "predicted_value", "status", "prov", "note")
PREDICTION_STATUSES = ("COMPARED", "EXCLUDED_VOID", "NOT_COMPARED_GATE_OVERLAP")
PREDICTION_PROVS = ("DERIVED_3505", "DERIVED_P2D")
RANGE_RE = re.compile(r"^(-?[0-9_]+)\.\.(-?[0-9_]+)$")
FLAG_TRUE_TOKENS = ("1", "TRUE")
FLAG_FALSE_TOKENS = ("0", "FALSE")


class DetectLog:
    """The semantic BD- records of one test_bench_detect log (design C.2).

    Everything between a BD-LIB mark begin and its mark end is excluded, as the
    binary's own DIFF rule says, and BD-NOTE prose is not parsed. Records are
    keyed the way design C.2 compares them; a repeated key keeps its first record
    and is listed in duplicates.
    """

    def __init__(self, log):
        self.log = log
        self.headers = {}                   # tag -> (pairs, lineno): BD-BANNER, BD-CFG, BD-CLK, BD-BUILD
        self.enums = {}                     # gnm -> (pairs, lineno)
        self.maps = {}                      # gnm -> (pairs, lineno)
        self.plans = {}                     # sw -> (pairs, lineno)
        self.cells = {}                     # (sw, gnm) -> (pairs, lineno)
        self.skipped = {}                   # (sw, gnm) -> (pairs, lineno)
        self.reps = []                      # (sw, gnm, lineno)
        self.sweep_ends = {}                # sw -> (pairs, lineno)
        self.duplicates = []
        in_lib = False
        for message in log.messages:         # line-start and recovered messages alike; a cut one is never read
            if message.cut or not message.payload.startswith("BD-"):
                continue
            lineno, payload = message.lineno, message.payload
            tag = payload.split(",", 1)[0]
            if tag == "BD-NOTE":
                continue
            pairs = pairs_of(payload)
            if tag == "BD-LIB":
                in_lib = pairs.get("mark") == "begin"
                continue
            if in_lib:
                continue
            sw = parse_int_token(pairs.get("sw", ""))
            if tag in ("BD-BANNER", "BD-CFG", "BD-CLK", "BD-BUILD"):
                self._put(self.headers, tag, pairs, lineno, tag)
            elif tag == "BD-ENUM":
                self._put(self.enums, pairs.get("gnm"), pairs, lineno, tag)
            elif tag == "BD-MAP":
                self._put(self.maps, pairs.get("gnm"), pairs, lineno, tag)
            elif tag == "BD-PLAN":
                self._put(self.plans, sw, pairs, lineno, tag)
            elif tag == "BD-CELL":
                self._put(self.cells, (sw, pairs.get("gnm")), pairs, lineno, tag)
            elif tag == "BD-SKIPPED":
                self._put(self.skipped, (sw, pairs.get("gnm")), pairs, lineno, tag)
            elif tag == "BD-REP":
                self.reps.append((sw, pairs.get("gnm"), lineno))
            elif tag == "BD-SWEEP" and pairs.get("mark") == "end":
                self._put(self.sweep_ends, sw, pairs, lineno, tag)

    def _put(self, table, key, pairs, lineno, tag):
        if key in table:
            self.duplicates.append(f"{self.ref(lineno)}: duplicate {tag} {key} (first at line {table[key][1]})")
            return
        table[key] = (pairs, lineno)

    def header(self, tag):
        return self.headers.get(tag, ({}, None))[0]

    def ref(self, lineno):
        return f"{self.log.display}:{lineno}"


def _sort_sw(key):
    return (key is None, key or 0)


def detect_guard_plan(dlog):
    """What the gate-input guard must skip, computed host-side (design C.3 items 1-2).

    Returns (skips, plan_groups, gate_groups, problems). skips maps (sw, gnm) to
    GATE_OVERLAP or COG_OVERLAP; plan_groups maps each BD-PLAN sweep to the groups
    it plans; gate_groups is the set of gate-overlap groups. The inputs are the
    log's BD-CFG bases, BD-BUILD tail_groups and BD-PLAN only -- never the binary's
    own BD-MAP guard or BD-SKIPPED claim -- so a binary cannot certify its own guard.
      GATE_OVERLAP: the group's sense pin (base+4) lies on a declared board's pin
                    other than that board's own sense pin.
      COG_OVERLAP:  a phase-2 sweep whose driver-cog group shares a pin with a
                    declared board based elsewhere; every cell of that sweep.
    """
    problems = []
    cfg, build = dlog.header("BD-CFG"), dlog.header("BD-BUILD")
    left, right = parse_int_token(cfg.get("left_base", "")), parse_int_token(cfg.get("right_base", ""))
    if left is None or right is None:
        return {}, {}, set(), ["BD-CFG carries no numeric left_base/right_base"]
    tail = build.get("tail_groups")
    if tail not in ("0", "1"):
        return {}, {}, set(), [f"BD-BUILD tail_groups {tail!r} is not 0 or 1"]
    boards = (left, right)
    swept = DETECT_SWEEP_ORDER if tail == "1" else DETECT_SWEEP_ORDER[:len(DETECT_SWEEP_ORDER) - DETECT_TAIL_GROUPS]

    def gate_overlap(gnm):
        sense = DETECT_GROUPS[gnm] + DETECT_SENSE_OFFSET
        return any(base <= sense < base + DETECT_GROUP_SPAN and sense != base + DETECT_SENSE_OFFSET for base in boards)

    def cog_overlap(cog_base):
        return any(base != cog_base and abs(base - cog_base) < DETECT_GROUP_SPAN for base in boards)

    gate_groups = {gnm for gnm in DETECT_GROUPS if gate_overlap(gnm)}
    skips, plan_groups = {}, {}
    if not dlog.plans:
        problems.append("no BD-PLAN record")
    for sw, (plan, lineno) in sorted(dlog.plans.items(), key=lambda item: _sort_sw(item[0])):
        groups = list(swept) if plan.get("groups") == "ALL" else [plan.get("groups")]
        if sw is None or any(gnm not in DETECT_GROUPS for gnm in groups):
            problems.append(f"{dlog.ref(lineno)}: BD-PLAN names an unknown sweep or group")
            continue
        plan_groups[sw] = groups
        cog = plan.get("cog")
        refused = plan.get("phase") == "2" and cog in DETECT_GROUPS and cog_overlap(DETECT_GROUPS[cog])
        for gnm in groups:
            if refused:
                skips[(sw, gnm)] = "COG_OVERLAP"
            elif gnm in gate_groups:
                skips[(sw, gnm)] = "GATE_OVERLAP"
    return skips, plan_groups, gate_groups, problems


def recovered_bd_note(log, role=""):
    """A detail line naming every BD- message recovered from a corrupted line or cut short (PL-40)."""
    flagged = [message for message in log.flagged_messages if message.payload.startswith("BD-")]
    if not flagged:
        return []
    return [f"{role}{log.display}: {len(flagged)} BD- message(s) recovered from corrupted lines or cut short -- "
            + "; ".join(f"line {message.lineno} {message.tag}: {log.message_status(message)}" for message in flagged)]


def _latest_build(logs):
    """The logs of the latest build, oldest first, and a detail line (design D.4: a rerun cannot hide a FAIL)."""
    builds = {}
    for log in logs:
        builds.setdefault(log.build_key, []).append(log)
    ordered = sorted(builds.items(), key=lambda item: max(log.order_key for log in item[1]))
    latest_key, members = ordered[-1]
    detail = [f"speaking build: {build_key_text(latest_key)} ({len(members)} log(s))"]
    superseded = [log.display for _, group in ordered[:-1] for log in group]
    if superseded:
        detail.append("superseded earlier-build log(s), not judged: " + ", ".join(superseded))
    return sorted(members, key=lambda log: log.order_key), detail


def _aggregate(results):
    """Worst of [(verdict, reason)]: FAIL > NOMEAS > PASS; every log of the speaking build speaks."""
    for wanted in ("FAIL", "NOMEAS"):
        for verdict, reason in results:
            if verdict == wanted:
                return verdict, reason
    return ("PASS", "") if results else ("NOT_BUILT", "NO_LOG")


def load_predictions(path):
    """Read SIGNOFF-DETECT-PREDICTIONS.tsv. Returns (rows, problems); '#' lines are comments."""
    rows, problems, seen = [], [], {}
    where_file = display_path(path)
    lines = Path(path).read_text(encoding="utf-8").splitlines()
    if not lines or tuple(lines[0].split("\t")) != PREDICTION_COLUMNS:
        return [], [f"{where_file}:1: header must be the tab-separated columns {', '.join(PREDICTION_COLUMNS)}"]
    for lineno, line in enumerate(lines[1:], start=2):
        if not line.strip() or line.startswith("#"):
            continue
        where = f"{where_file}:{lineno}"
        parts = line.split("\t")
        if len(parts) != len(PREDICTION_COLUMNS):
            problems.append(f"{where}: {len(parts)} tab-separated fields, expected {len(PREDICTION_COLUMNS)}")
            continue
        row = dict(zip(PREDICTION_COLUMNS, (part.strip() for part in parts)))
        row["lineno"] = lineno
        row["sw_n"] = parse_int_token(row["sw"])
        if row["sw_n"] is None:
            problems.append(f"{where}: sw {row['sw']!r} is not a sweep number")
        elif row["grp"] not in DETECT_GROUPS:
            problems.append(f"{where}: grp {row['grp']!r} is not a group name")
        elif row["field"] not in DETDIFF_EXACT_FIELDS + DETDIFF_SUM_FIELDS:
            problems.append(f"{where}: field {row['field']!r} is not a compared BD-CELL field (design C.2)")
        elif row["status"] not in PREDICTION_STATUSES:
            problems.append(f"{where}: status {row['status']!r} is not one of {', '.join(PREDICTION_STATUSES)}")
        elif row["prov"] not in PREDICTION_PROVS:
            problems.append(f"{where}: prov {row['prov']!r} is not one of {', '.join(PREDICTION_PROVS)}")
        elif (row["status"] == "EXCLUDED_VOID") != (row["sw_n"] in DETECT_VOID_SWEEPS):
            problems.append(f"{where}: EXCLUDED_VOID must be used for sweeps 3 and 6, and only there")
        elif not row["note"]:
            problems.append(f"{where}: note is empty")
        elif (row["sw_n"], row["grp"], row["field"]) in seen:
            problems.append(f"{where}: duplicate prediction (first at line {seen[(row['sw_n'], row['grp'], row['field'])]})")
        else:
            seen[(row["sw_n"], row["grp"], row["field"])] = lineno
            rows.append(row)
    return rows, problems


def _same_token(first, second):
    """Equal as integers when both are ('_' grouping stripped), else as strings."""
    first_n, second_n = parse_int_token(first or ""), parse_int_token(second or "")
    if first_n is not None and second_n is not None:
        return first_n == second_n
    return first == second


def prediction_matches(predicted, value):
    """A predicted token, or an inclusive range lo..hi that the visit value must lie inside."""
    match = RANGE_RE.match(predicted)
    if match:
        number = parse_int_token(value or "")
        return number is not None and parse_int_token(match.group(1)) <= number <= parse_int_token(match.group(2))
    return _same_token(predicted, value)


def field_unchanged(field, baseline, visit):
    """Design C.2's "unchanged": sums exact when the baseline is 0 or 500, else within +-11; others exact."""
    if field in DETDIFF_SUM_FIELDS:
        baseline_n, visit_n = parse_int_token(baseline or ""), parse_int_token(visit or "")
        if baseline_n is not None and visit_n is not None:
            if baseline_n in DETDIFF_SUM_EXACT_BASELINES:
                return visit_n == baseline_n
            return abs(visit_n - baseline_n) <= DETDIFF_SUM_TOLERANCE
    return _same_token(baseline, visit)


def _unchanged_rule(field, baseline):
    if field not in DETDIFF_SUM_FIELDS:
        return "exact"
    return "exact, baseline 0 or 500" if parse_int_token(baseline or "") in DETDIFF_SUM_EXACT_BASELINES else "+-11"


def detect_void_reasons(dlog, role):
    """The binary's own VOID rules (baseline log :56-57): no banner, BD-CLK match 0, BD-ENUM match 0, cfg not BENCH."""
    reasons = []
    name = f"{role} {dlog.log.display}"
    if "BD-BANNER" not in dlog.headers:
        reasons.append(f"VOID: {name} has no BD-BANNER")
    clk = dlog.headers.get("BD-CLK")
    if clk is None or clk[0].get("match") not in FLAG_TRUE_TOKENS:
        reasons.append(f"VOID: {name} BD-CLK match {clk[0].get('match') if clk else 'ABSENT'}"
                       + (f" ({dlog.ref(clk[1])})" if clk else ""))
    for gnm, (pairs, lineno) in sorted(dlog.enums.items(), key=lambda item: item[1][1]):
        if pairs.get("match") in FLAG_FALSE_TOKENS:
            reasons.append(f"VOID: {name} BD-ENUM {gnm} match {pairs.get('match')} ({dlog.ref(lineno)})")
    if dlog.header("BD-CFG").get("cfg_id") != "BENCH":
        reasons.append(f"VOID: {name} BD-CFG cfg_id {dlog.header('BD-CFG').get('cfg_id', 'ABSENT')}, not BENCH")
    return reasons


def _change(text, visit_line, field_level):
    """One diff entry. field_level is True when both logs carry the record being compared."""
    return {"text": text, "visit_line": visit_line, "field_level": field_level}


def detdiff_log(visit_log, base, rows):
    """R2-HOST-DETDIFF for one qualifying visit log against the baseline (design C.2).

    Compared: BD-CELL (sw, gnm) modal/libvrd/agree/va/vb/vn exactly and
    sum_min/sum_max/sum_mean exactly when the baseline is 0 or 500, else within
    +-11; BD-ENUM (gnm) local/lib/match exactly; BD-PLAN (sw) every field exactly.
    Excluded and listed: sweeps 3 and 6; BD-CFG and BD-MAP as INFO; BD-LIB
    brackets and every timing record (BD-REP, BD-RUN, BD-CAL).
    measured = unpredicted changes + predicted changes that did not occur. A cell
    the visit log marks BD-SKIPPED is NOT_COMPARED and listed, whatever the
    prediction status; a NOT_COMPARED_GATE_OVERLAP prediction whose cell the visit
    log does carry is compared (design C.2: NOT_COMPARED needs the SKIPPED mark).
    PASS iff measured 0, no COMPARED predicted cell was skipped, every skip is one
    the declared bases imply, and a post-stop cell was compared on each of P0_P15
    and P16_P31; otherwise NOMEAS. VOID is NOMEAS; a TRUNCATED log is never PASS.
    """
    visit = DetectLog(visit_log)
    out = {"verdict": None, "reason": "", "measured": None, "unpredicted": [], "not_occurred": [], "occurred": [],
           "not_compared": [], "excluded": [], "info": [], "blockers": [], "void": [], "refs": []}
    void = detect_void_reasons(visit, "visit") + detect_void_reasons(base, "baseline")
    visit_build, base_build = visit.header("BD-BUILD"), base.header("BD-BUILD")
    for name in DETDIFF_VARIANT_FIELDS:
        if visit_build.get(name) != base_build.get(name):
            void.append(f"VOID: build variant mismatch, BD-BUILD {name} visit {visit_build.get(name)} vs baseline "
                        f"{base_build.get(name)} (the binary's DIFF rule: different build variants are not comparable)")
    if void:
        out.update(verdict="NOMEAS", reason="VOID", void=void)
        return out

    def both(base_line, visit_line):
        return f"baseline {base.ref(base_line)}, visit {visit.ref(visit_line)}"

    for sw in sorted(set(base.plans) | set(visit.plans), key=_sort_sw):
        base_rec, visit_rec = base.plans.get(sw), visit.plans.get(sw)
        if base_rec is None or visit_rec is None:
            where = f"visit {visit.ref(visit_rec[1])}" if base_rec is None else f"baseline {base.ref(base_rec[1])}"
            out["unpredicted"].append(_change(f"BD-PLAN sw {sw}: present in one log only ({where})",
                                              visit_rec[1] if visit_rec else None, False))
            continue
        for name in sorted(set(base_rec[0]) | set(visit_rec[0])):
            if base_rec[0].get(name) != visit_rec[0].get(name):
                out["unpredicted"].append(_change(
                    f"BD-PLAN sw {sw} {name}: {base_rec[0].get(name, 'ABSENT')} -> {visit_rec[0].get(name, 'ABSENT')} "
                    f"(exact) -- {both(base_rec[1], visit_rec[1])}", visit_rec[1], True))
    for gnm in sorted(set(base.enums) | set(visit.enums), key=str):
        base_rec, visit_rec = base.enums.get(gnm), visit.enums.get(gnm)
        if base_rec is None or visit_rec is None:
            where = f"visit {visit.ref(visit_rec[1])}" if base_rec is None else f"baseline {base.ref(base_rec[1])}"
            out["unpredicted"].append(_change(f"BD-ENUM {gnm}: present in one log only ({where})",
                                              visit_rec[1] if visit_rec else None, False))
            continue
        for name in DETDIFF_ENUM_FIELDS:
            if not _same_token(base_rec[0].get(name), visit_rec[0].get(name)):
                out["unpredicted"].append(_change(
                    f"BD-ENUM {gnm} {name}: {base_rec[0].get(name)} -> {visit_rec[0].get(name)} (exact) -- "
                    f"{both(base_rec[1], visit_rec[1])}", visit_rec[1], True))
    base_cfg, visit_cfg = base.headers.get("BD-CFG"), visit.headers.get("BD-CFG")
    for name in sorted(set(base_cfg[0]) | set(visit_cfg[0])):
        if base_cfg[0].get(name) != visit_cfg[0].get(name):
            out["info"].append(f"BD-CFG {name}: {base_cfg[0].get(name, 'ABSENT')} -> {visit_cfg[0].get(name, 'ABSENT')} "
                               f"-- {both(base_cfg[1], visit_cfg[1])}")
    for gnm in sorted(set(base.maps) | set(visit.maps), key=str):
        base_rec, visit_rec = base.maps.get(gnm), visit.maps.get(gnm)
        if base_rec is None or visit_rec is None:
            out["info"].append(f"BD-MAP {gnm}: present in one log only")
            continue
        for name in sorted(set(base_rec[0]) | set(visit_rec[0])):
            if base_rec[0].get(name) != visit_rec[0].get(name):
                out["info"].append(f"BD-MAP {gnm} {name}: {base_rec[0].get(name, 'ABSENT')} -> "
                                   f"{visit_rec[0].get(name, 'ABSENT')} -- {both(base_rec[1], visit_rec[1])}")

    predictions = {}
    for row in rows:
        predictions.setdefault((row["sw_n"], row["grp"]), {})[row["field"]] = row
    expected_skips, _, _, plan_problems = detect_guard_plan(visit)
    for problem in plan_problems:
        out["blockers"].append(f"GUARD_PLAN_UNREADABLE: {problem}")
    poststop = {gnm: 0 for gnm in DETECT_POSTSTOP_GROUPS}
    keys = set(base.cells) | set(visit.cells) | set(visit.skipped) | set(predictions)
    for key in sorted(keys, key=lambda item: (_sort_sw(item[0]), str(item[1]))):
        sw, gnm = key
        where = f"sw {sw} {gnm}"
        cell_preds = predictions.get(key, {})
        base_rec, visit_rec, skip_rec = base.cells.get(key), visit.cells.get(key), visit.skipped.get(key)
        if sw in DETECT_VOID_SWEEPS:
            text = f"{where}: excluded -- running-driver cell, void by design (design C.2)"
            if cell_preds:
                text += f"; {len(cell_preds)} EXCLUDED_VOID prediction line(s)"
            out["excluded"].append(text)
            continue
        if skip_rec is not None:
            reason = skip_rec[0].get("reason")
            text = f"{where}: NOT_COMPARED -- the visit log marks it SKIPPED {reason} ({visit.ref(skip_rec[1])})"
            if cell_preds:
                text += "; prediction line(s) not compared: " + ", ".join(
                    f"{field} {row['baseline_value']} -> {row['predicted_value']} ({row['status']})"
                    for field, row in sorted(cell_preds.items()))
            out["not_compared"].append(text)
            if expected_skips.get(key) != reason:
                out["blockers"].append(f"UNEXPECTED_SKIP: {where} is SKIPPED {reason} at {visit.ref(skip_rec[1])}, but "
                                       f"the declared bases imply {expected_skips.get(key, 'no skip')} "
                                       "(see R2-DETECT-GUARD)")
            if any(row["status"] == "COMPARED" for row in cell_preds.values()):
                out["blockers"].append(f"PREDICTED_CELL_SKIPPED: {where} carries COMPARED predictions but the visit "
                                       "log skipped it, so not every COMPARED predicted cell is present in both logs")
            if visit_rec is not None:
                out["unpredicted"].append(_change(f"{where}: the visit log carries both a BD-CELL "
                                                  f"({visit.ref(visit_rec[1])}) and a BD-SKIPPED record",
                                                  visit_rec[1], False))
            continue
        if base_rec is None or visit_rec is None:
            if base_rec is None and visit_rec is None:
                where_text = "neither log carries the cell"
            elif base_rec is None:
                where_text = f"the BD-CELL is in the visit log only ({visit.ref(visit_rec[1])})"
            else:
                where_text = f"the BD-CELL is in the baseline only ({base.ref(base_rec[1])})"
            visit_line = visit_rec[1] if visit_rec else None
            if cell_preds:
                for field, row in sorted(cell_preds.items()):
                    out["not_occurred"].append(_change(
                        f"{where} {field}: predicted {row['baseline_value']} -> {row['predicted_value']} "
                        f"(predictions line {row['lineno']}), but {where_text}", visit_line, False))
            else:
                out["unpredicted"].append(_change(f"{where}: {where_text}", visit_line, False))
            continue
        if sw in DETECT_POSTSTOP_SWEEPS and gnm in poststop:
            poststop[gnm] += 1
        for field in DETDIFF_SUM_FIELDS + DETDIFF_EXACT_FIELDS:
            base_value, visit_value = base_rec[0].get(field), visit_rec[0].get(field)
            row = cell_preds.get(field)
            lines = both(base_rec[1], visit_rec[1])
            if row is None:
                if not field_unchanged(field, base_value, visit_value):
                    out["unpredicted"].append(_change(
                        f"{where} {field}: {base_value} -> {visit_value}, not predicted "
                        f"({_unchanged_rule(field, base_value)}) -- {lines}", visit_rec[1], True))
            elif not _same_token(row["baseline_value"], base_value):
                out["not_occurred"].append(_change(
                    f"{where} {field}: predictions line {row['lineno']} expects baseline {row['baseline_value']}, "
                    f"the baseline reads {base_value} -- {lines}", visit_rec[1], True))
            elif prediction_matches(row["predicted_value"], visit_value):
                out["occurred"].append(f"{where} {field}: {base_value} -> {visit_value} as predicted "
                                       f"({row['predicted_value']}, {row['status']}, {row['prov']}) -- {lines}")
            else:
                out["not_occurred"].append(_change(
                    f"{where} {field}: predicted {base_value} -> {row['predicted_value']} ({row['status']}, "
                    f"{row['prov']}), the visit reads {visit_value} -- {lines}", visit_rec[1], True))
    for gnm, count in poststop.items():
        if count == 0:
            out["blockers"].append(f"NO_POSTSTOP_COMPARED: no post-stop cell (sweeps 4, 5, 7, 8) was compared on "
                                   f"{gnm}; an all-skipped diff is never PASS")

    changes = out["unpredicted"] + out["not_occurred"]
    out["measured"] = len(changes)
    banner_line = visit.headers.get("BD-BANNER", ({}, None))[1]
    if not visit_log.complete:
        field_level = [change for change in changes if change["field_level"]]
        if field_level:
            out.update(verdict="FAIL", reason="CHANGES_BEFORE_TRUNCATION")
            out["refs"] = [visit.ref(change["visit_line"]) for change in field_level]
        else:
            out.update(verdict="NOMEAS", reason="LOG_TRUNCATED")
    elif changes:
        out.update(verdict="FAIL", reason="UNPREDICTED_OR_NOT_OCCURRED")
        out["refs"] = [visit.ref(change["visit_line"]) for change in changes if change["visit_line"]] or \
            [visit.ref(banner_line)]
    elif out["blockers"]:
        out.update(verdict="NOMEAS", reason=out["blockers"][0].split(":", 1)[0])
    else:
        out.update(verdict="PASS")
        out["refs"] = [visit.ref(banner_line)]
    return out


def detdiff_compare(visit_logs, baseline_log, predictions_path):
    """R2-HOST-DETDIFF across the qualifying visit logs of the latest build (design C.2, D.4)."""
    rows, problems = load_predictions(predictions_path)
    if problems:
        return CellResult("NOMEAS", "PREDICTIONS_MALFORMED", problems)
    base = DetectLog(baseline_log)
    members, detail = _latest_build(visit_logs)
    detail.append(f"baseline {baseline_log.display}; predictions {display_path(predictions_path)} "
                  f"({len(rows)} prediction line(s))")
    detail.extend(recovered_bd_note(baseline_log, "baseline "))
    results, per_log, refs_by_verdict = [], [], {"PASS": [], "FAIL": [], "NOMEAS": []}
    for log in members:
        out = detdiff_log(log, base, rows)
        results.append((out["verdict"], out["reason"]))
        per_log.append((log, out))
        measured = "NA" if out["measured"] is None else out["measured"]
        detail.append(f"{log.display}: {out['verdict']}" + (f" ({out['reason']})" if out["reason"] else "")
                      + f"; measured {measured} = {len(out['unpredicted'])} unpredicted change(s) + "
                      f"{len(out['not_occurred'])} predicted change(s) that did not occur, lo 0, hi 0, COUNT; "
                      f"{len(out['occurred'])} predicted change(s) occurred; {len(out['not_compared'])} cell(s) "
                      "NOT_COMPARED; itemised in the DETDIFF change list")
        detail.extend(recovered_bd_note(log))
        detail.extend(out["void"] + out["blockers"])
        refs_by_verdict[out["verdict"]].extend(out["refs"])
    verdict, reason = _aggregate(results)
    result = CellResult(verdict, reason, detail, [], refs_by_verdict.get(verdict, []))
    result.extra["logs"] = per_log
    return result


def detect_guard_log(log):
    """R2-DETECT-GUARD on one qualifying detect-phase2 log (design C.3 item 5).

    Returns (verdict, reason, detail lines, refs). TRUE (PASS) needs all of:
      - no BD-REP and no BD-CELL for a cell the guard must skip;
      - one BD-SKIPPED per such cell with its reason, and none anywhere else;
      - BD-MAP guard GATE_OVERLAP on exactly the gate-overlap groups;
      - every BD-SWEEP end's cells, skipped and reps equal to the BD-PLAN less the
        skipped cells, and equal to the records the log actually carries.
    The skip set comes from detect_guard_plan(), never from the binary's own claim.
    NOMEAS when the declared bases imply no skip: the guard was not exercised.
    """
    dlog = DetectLog(log)
    skips, plan_groups, gate_groups, problems = detect_guard_plan(dlog)
    if problems:
        return "NOMEAS", "GUARD_INPUT_MALFORMED", [f"{log.display}: {problem}" for problem in problems], []
    if not skips:
        return ("NOMEAS", "NOTHING_TO_GUARD",
                [f"{log.display}: the declared bases imply no skipped cell, so the guard was not exercised"], [])
    failures = []

    def fail(lineno, text):
        failures.append((dlog.ref(lineno) if lineno else log.display, text))

    for sw, gnm, lineno in dlog.reps:
        if (sw, gnm) in skips:
            fail(lineno, f"BD-REP for sw {sw} {gnm}, a cell the guard must skip ({skips[(sw, gnm)]})")
    for key, (_, lineno) in sorted(dlog.cells.items(), key=lambda item: item[1][1]):
        if key in skips:
            fail(lineno, f"BD-CELL for sw {key[0]} {key[1]}, a cell the guard must skip ({skips[key]})")
    for gnm in DETECT_GROUPS:
        want = "GATE_OVERLAP" if gnm in gate_groups else "NONE"
        entry = dlog.maps.get(gnm)
        if entry is None:
            fail(None, f"no BD-MAP record for {gnm}")
        elif entry[0].get("guard") != want:
            fail(entry[1], f"BD-MAP {gnm} guard {entry[0].get('guard', 'ABSENT')} (ovl {entry[0].get('ovl', 'ABSENT')}); "
                           f"the declared bases give {want}")
    for key, (pairs, lineno) in sorted(dlog.skipped.items(), key=lambda item: item[1][1]):
        want = skips.get(key)
        if want is None:
            fail(lineno, f"BD-SKIPPED sw {key[0]} {key[1]} reason {pairs.get('reason')}, but the declared bases "
                         "imply no skip")
        elif pairs.get("reason") != want:
            fail(lineno, f"BD-SKIPPED sw {key[0]} {key[1]} reason {pairs.get('reason')}; the declared bases give {want}")
    for key, want in sorted(skips.items()):
        if key not in dlog.skipped:
            fail(None, f"no BD-SKIPPED record for sw {key[0]} {key[1]} (expected reason {want})")
    count_lines = []
    for sw, groups in sorted(plan_groups.items()):
        plan_n = parse_int_token(dlog.plans[sw][0].get("n", ""))
        n_skipped = sum(1 for gnm in groups if (sw, gnm) in skips)
        n_cells = len(groups) - n_skipped
        want = {"cells": n_cells, "skipped": n_skipped, "reps": None if plan_n is None else n_cells * plan_n}
        counted = {"cells": sum(1 for key in dlog.cells if key[0] == sw),
                   "skipped": sum(1 for key in dlog.skipped if key[0] == sw),
                   "reps": sum(1 for rep in dlog.reps if rep[0] == sw)}
        end = dlog.sweep_ends.get(sw)
        if end is None:
            fail(None, f"no BD-SWEEP end mark for sw {sw}")
            continue
        for name in ("cells", "skipped", "reps"):
            printed = parse_int_token(end[0].get(name, ""))
            if want[name] is None or printed != want[name]:
                fail(end[1], f"BD-SWEEP sw {sw} {name} {end[0].get(name, 'ABSENT')}; the plan less its skipped cells "
                             f"gives {want[name]}")
            if counted[name] != want[name]:
                fail(end[1], f"sw {sw} carries {counted[name]} {name} record(s); the plan less its skipped cells "
                             f"gives {want[name]}")
        count_lines.append(end[1])
    cfg = dlog.header("BD-CFG")
    cog_sweeps = sorted({sw for (sw, _), reason in skips.items() if reason == "COG_OVERLAP"})
    summary = (f"{log.display}: skip set from BD-CFG left_base {cfg.get('left_base')} right_base {cfg.get('right_base')}"
               f" -- GATE_OVERLAP groups {', '.join(sorted(gate_groups)) or 'none'}; COG_OVERLAP sweeps "
               f"{', '.join(map(str, cog_sweeps)) or 'none'}; {len(skips)} skipped cell(s) across {len(plan_groups)} "
               "planned sweep(s)")
    if failures:
        return ("FAIL", "GUARD_NOT_HELD",
                [summary, f"{log.display}: FALSE -- {len(failures)} condition failure(s)"]
                + [f"{ref}: {text}" for ref, text in failures],
                [ref for ref, _ in failures])
    refs = [dlog.ref(dlog.maps[gnm][1]) for gnm in sorted(gate_groups)] + [dlog.ref(line) for line in count_lines]
    return ("PASS", "",
            [summary, f"{log.display}: TRUE -- no BD-REP or BD-CELL for a skipped cell, one BD-SKIPPED per skipped "
                      f"cell, BD-MAP guard matches, {len(count_lines)} BD-SWEEP end count(s) equal the plan less "
                      "the skipped cells"],
            refs)


def detect_guard_check(visit_logs):
    """R2-DETECT-GUARD across the qualifying logs of the latest build (a rerun cannot hide a FAIL)."""
    members, detail = _latest_build(visit_logs)
    results, refs_by_verdict = [], {"PASS": [], "FAIL": [], "NOMEAS": []}
    for log in members:
        verdict, reason, lines, refs = detect_guard_log(log)
        if verdict == "PASS" and not log.complete:
            verdict, reason = "NOMEAS", "LOG_TRUNCATED"
            lines.append(f"{log.display}: TRUNCATED, so its TRUE cannot yield PASS (design D.3.2)")
        results.append((verdict, reason))
        detail.extend(lines)
        detail.extend(recovered_bd_note(log))
        refs_by_verdict[verdict].extend(refs)
    verdict, reason = _aggregate(results)
    detail.append(f"measured {dict(PASS='TRUE', FAIL='FALSE').get(verdict, 'NA')}, lo TRUE, hi TRUE, BOOL")
    refs = refs_by_verdict.get(verdict, [])
    return CellResult(verdict, reason, detail, [f"{ref} (proving line)" for ref in refs], refs)


def evaluate_host_cell(cell, logs, ctx):
    if cell.cell == "R10-HOST-PL9":
        return host_pl9(ctx["static_tree"], ctx["pl9_source"])
    if cell.cell == "R11-HOST-WDTEND":
        return host_wdtend(logs)
    if cell.cell == "R2-HOST-DETDIFF":
        return host_detdiff(logs, ctx)
    if cell.cell == "R2-DETECT-GUARD":
        return host_detect_guard(logs, ctx)
    return CellResult("NOT_BUILT", "NO_HOST_EVALUATOR", ["this script has no evaluator for this HOST cell"])


# ---------------------------------------------------------------------------------------------
# Collation
# ---------------------------------------------------------------------------------------------

def cell_in_scope(cell, visit):
    """Owed to this visit, or carried over from an earlier visit while still OWED/FAILED."""
    if cell.visit_n is None:
        return False
    return cell.visit_n == visit or (cell.visit_n < visit and cell.status in ("OWED", "FAILED"))


class Collation:
    def __init__(self):
        self.scope = []
        self.deferred = []
        self.results = {}
        self.rows = []                      # (row_n, tasks, feature, verdict)
        self.logs = []
        self.unmanifested = {}
        self.parse_errors = []
        self.notes = []


def collate(cells, logs, visit, static_tree, predictions_path, baseline_path, pl9_source=PL9_SOURCE):
    col = Collation()
    col.logs = logs
    by_id = {cell.cell: cell for cell in cells}
    col.scope = [cell for cell in cells if cell_in_scope(cell, visit)]
    col.deferred = [cell for cell in cells if cell.visit_n is None]
    for log in logs:
        for rec in log.records:
            if rec.error:
                owner = f"cell {rec.cell}" if rec.cell else "cell not recoverable"
                col.parse_errors.append(f"{rec.ref}: {rec.kind_tag} {rec.error} ({owner})"
                                        + (f" [{rec.flag}]" if rec.flag else ""))
            if rec.cell is None:
                continue
            cell = by_id.get(rec.cell)
            if cell is None:
                col.unmanifested.setdefault(rec.cell, []).append(f"{rec.ref} {rec.kind_tag}")
            elif cell.bin == "HOST":
                col.notes.append(f"{rec.ref}: {rec.kind_tag} names HOST cell {rec.cell}; "
                                 "host cells take no binary verdict, record ignored")
    ctx = {"static_tree": static_tree, "predictions": Path(predictions_path), "baseline": Path(baseline_path),
           "pl9_source": Path(pl9_source)}
    for cell in col.scope:
        if cell.bin == "HOST":
            col.results[cell.cell] = evaluate_host_cell(cell, logs, ctx)
        else:
            col.results[cell.cell] = evaluate_signoff_cell(cell, logs)
    for row_n in sorted({cell.row_n for cell in col.scope}):
        members = [cell for cell in col.scope if cell.row_n == row_n]
        tasks = []
        for cell in members:
            if cell.raw["task"] not in tasks:
                tasks.append(cell.raw["task"])
        verdict = worst_verdict([col.results[cell.cell].verdict for cell in members])
        col.rows.append((row_n, tasks, members[0].raw["feature"], verdict))
    return col


def plan_updates(col, visit):
    """Status transitions of design A.2. Returns [(cell, old_status, new_status, new_ref)]."""
    changes = []
    for cell in col.scope:
        result = col.results[cell.cell]
        ref = ";".join(f"V{visit}:{entry}" for entry in result.refs)
        if result.verdict == "PASS" and cell.status in ("OWED", "FAILED") and ref:
            changes.append((cell, cell.status, "SIGNED_OFF", ref))
        elif result.verdict == "FAIL" and cell.status == "OWED" and ref:
            changes.append((cell, cell.status, "FAILED", ref))
    return changes


RECOVERED_SECTION = "## Records recovered from corrupted lines"


def render_sheet(col, visit, date, manifest_path, static_tree, update, predictions_path, baseline_path, changes):
    out = [f"# Visit {visit} sign-off sheet -- {date}", ""]
    out.append("- Script: `tools/signoff-collate.py`")
    out.append(f"- Manifest: `{display_path(manifest_path)}` -- "
               + ("statuses updated by this run (--update)" if update else "read-only this run (no --update)"))
    out.append(f"- Design: `{DESIGN_DOC}`")
    out.append(f"- Flags: --static-tree {'yes' if static_tree else 'no'}; --update {'yes' if update else 'no'}")
    out.append(f"- Detect prediction list: `{display_path(predictions_path)}` "
               f"({'present' if Path(predictions_path).is_file() else 'absent'}); detect baseline: "
               f"`{display_path(baseline_path)}` ({'present' if Path(baseline_path).is_file() else 'absent'})")
    out.append("- Rules: a verdict exists only where a binary printed one; a cell reaches PASS only by positive "
               "evidence; a declared cell without a verdict is NOMEAS (design section 0)")
    out.append("")
    out.append("## Input logs")
    out.append("")
    for index, log in enumerate(col.logs, start=1):
        declarations = sum(1 for rec in log.records if rec.kind == "DECL")
        verdicts = sum(1 for rec in log.records if rec.kind == "SIGNOFF")
        malformed = sum(1 for rec in log.records if rec.error)
        recovered = sum(1 for message in log.messages if message.recovered)
        out.append(f"{index}. `{log.display}` -- **{'COMPLETE' if log.complete else 'TRUNCATED'}** -- "
                   f"{log.completeness_text}")
        out.append(f"   - identity: {log.identity_text()}")
        out.append(f"   - build key: {build_key_text(log.build_key)} (modified time recorded, not keyed)")
        out.append(f"   - records: {declarations} SIGNOFF-DECL, {verdicts} SIGNOFF, {malformed} malformed; "
                   f"{recovered} message(s) recovered from corrupted lines")
    out.append("")
    out.append("## Rows")
    out.append("")
    out.append("| row | task | feature | verdict |")
    out.append("|---|---|---|---|")
    for row_n, tasks, feature, verdict in col.rows:
        out.append(f"| {row_n} | {', '.join(tasks)} | {_md_cell(feature)} | **{verdict}** |")
    out.append("")
    out.append("## Cells")
    out.append("")
    change_by_cell = {change[0].cell: change for change in changes}
    for cell in col.scope:
        result = col.results[cell.cell]
        head = f"- **{cell.cell}** (row {cell.row_n}, bin {cell.bin}) -- **{result.verdict}**"
        if result.verdict != "PASS" and result.reason:
            head += f" ({result.reason})"
        head += (f" -- crit {cell.crit}, lo {cell.raw['lo']}, hi {cell.raw['hi']}, units {cell.units}, "
                 f"min_inst {cell.min_n}")
        if cell.filter_set:
            head += f", counts only {cell.raw['count_filter']}"
        head += f"; manifest status {cell.status}"
        if cell.status_ref:
            head += f" (ref {cell.status_ref})"
        if cell.cell in change_by_cell:
            _, old, new, _ = change_by_cell[cell.cell]
            head += f"; {'updated' if update else 'would update'} {old} -> {new}"
        out.append(head)
        for line in result.detail:
            out.append(f"  - {line}")
        for line in result.proving:
            out.append(f"  - {line}")
    out.append("")
    out.append("## NOT_BUILT")
    out.append("")
    not_built = [cell for cell in col.scope if col.results[cell.cell].verdict == "NOT_BUILT"]
    if not not_built:
        out.append("- (none)")
    for cell in not_built:
        result = col.results[cell.cell]
        out.append(f"- {cell.cell} -- {result.reason}" + (f": {'; '.join(result.detail)}" if result.detail else ""))
    out.append("")
    out.append("## Superseded logs")
    out.append("")
    superseded_lines = []
    for cell in col.scope:
        for key, logcell in col.results[cell.cell].superseded:
            superseded_lines.append(f"- {cell.cell}: {logcell.text()} -- earlier build {build_key_text(key)}")
    out.extend(superseded_lines or ["- (none)"])
    out.append("")
    out.append("## Unmanifested cells")
    out.append("")
    if not col.unmanifested:
        out.append("- (none)")
    for cell_id in sorted(col.unmanifested):
        out.append(f"- {cell_id}: {', '.join(col.unmanifested[cell_id])} (no effect)")
    out.append("")
    out.append("## Parse errors")
    out.append("")
    out.extend([f"- {line}" for line in col.parse_errors + col.notes] or ["- (none)"])
    out.append("")
    out.append(RECOVERED_SECTION)
    out.append("")
    out.append("A record token is found anywhere in a line but never inside a hex dump's ASCII gutter. A recovered "
               "record keeps its file:line and is judged like a line-start record; a message whose end is not "
               "observed on its line is MALFORMED (SIGNOFF, SIGNOFF-DECL) or not read (any other family), never "
               "counted (PL-40).")
    out.append("")
    recovered_lines = []
    for log in col.logs:
        for message in log.flagged_messages:
            cell = f" {message.record.cell}" if message.record is not None and message.record.cell else ""
            where = f"recovered: {message.context}" if message.recovered else "line-start, cut short"
            recovered_lines.append(f"- {log.display}:{message.lineno} Cog{message.cog} {message.tag[:40]}{cell} -- "
                                   f"{where} -- {log.message_status(message)}")
        for first, last, what in log.unparsed_signoff:
            span = str(first) if first == last else f"{first}-{last}"
            recovered_lines.append(f"- {log.display}:{span} {what} -- no record, no verdict")
    out.extend(recovered_lines or ["- (none)"])
    out.append("")
    out.append("## Deferred cells (not owed to this visit)")
    out.append("")
    out.extend([f"- {cell.cell} (row {cell.row_n}): {cell.test}" for cell in col.deferred] or ["- (none)"])
    out.append("")
    out.append("## DETDIFF change list")
    out.append("")
    detdiff = col.results.get("R2-HOST-DETDIFF")
    per_log = detdiff.extra.get("logs", []) if detdiff is not None else []
    if detdiff is None:
        out.append("- not computed: R2-HOST-DETDIFF is not in this visit's scope")
    elif not per_log:
        out.append(f"- not computed: R2-HOST-DETDIFF is {detdiff.verdict}"
                   + (f" ({detdiff.reason})" if detdiff.reason else "")
                   + (f": {'; '.join(detdiff.detail)}" if detdiff.detail else ""))
    for log, diff in per_log:
        out.append(f"### `{log.display}` -- {diff['verdict']}" + (f" ({diff['reason']})" if diff["reason"] else "")
                   + f", measured {'NA' if diff['measured'] is None else diff['measured']}")
        out.append("")
        out.append("- Never compared (design C.2): BD-LIB brackets, BD-REP/BD-RUN/BD-CAL timing, BD-NOTE text, "
                   "BD-PH2; BD-CFG and BD-MAP appear under INFO only.")
        sections = (
            ("VOID", diff["void"]),
            ("Unpredicted changes", [change["text"] for change in diff["unpredicted"]]),
            ("Predicted changes that did not occur", [change["text"] for change in diff["not_occurred"]]),
            ("Blocking PASS", diff["blockers"]),
            ("NOT_COMPARED (the visit log marks the cell SKIPPED)", diff["not_compared"]),
            ("Excluded by design (sweeps 3 and 6)", diff["excluded"]),
            ("Predicted changes that occurred", diff["occurred"]),
            ("INFO (BD-CFG, BD-MAP; not in the verdict)", diff["info"]),
        )
        for title, entries in sections:
            out.append(f"- **{title}** ({len(entries)})")
            out.extend(f"  - {entry}" for entry in entries)
        out.append("")
    return "\n".join(out) + "\n"


# ---------------------------------------------------------------------------------------------
# --check-ready (design A.3 rule 2, D.5)
# ---------------------------------------------------------------------------------------------

def strip_spin2_comments(text):
    """Remove ' line comments and { } block comments (nesting), keeping "..." strings intact.

    A brace inside a backtick debug display could open a false comment; that can
    only hide a declaration (a reported gap), never invent one.
    """
    out = []
    depth = 0
    for line in text.split("\n"):
        kept = []
        in_string = False
        for char in line:
            if depth > 0:
                if char == "{":
                    depth += 1
                elif char == "}":
                    depth -= 1
            elif in_string:
                kept.append(char)
                if char == '"':
                    in_string = False
            elif char == '"':
                in_string = True
                kept.append(char)
            elif char == "'":
                break
            elif char == "{":
                depth += 1
            else:
                kept.append(char)
        out.append("".join(kept))
    return "\n".join(out)


def source_declares_cell(source_text, cell_id):
    """True when the literal cell id appears inside a SIGNOFF-DECL emission (outside comments).

    Two emission styles are recognised:
      T0:   debug("SIGNOFF-DECL,...,cell,<ID>,...") -- the id on the emitting line;
      CHAR: <label> BYTE "<ID>" in DAT, and @<label> passed on a line calling a
            *SignoffDecl*( method, in a source that emits the "SIGNOFF-DECL" tag.
    """
    code = strip_spin2_comments(source_text)
    lines = code.split("\n")
    cell_re = re.compile(r"(?<![A-Za-z0-9\-])" + re.escape(cell_id) + r"(?![A-Za-z0-9\-])")
    for line in lines:
        if "SIGNOFF-DECL" in line and cell_re.search(line):
            return True, "a literal SIGNOFF-DECL emission names the cell"
    if '"SIGNOFF-DECL"' not in code:
        return False, "no SIGNOFF-DECL emission names this cell"
    label_re = re.compile(r'^\s*([A-Za-z_]\w*)\s+BYTE\s+"' + re.escape(cell_id) + r'"', re.IGNORECASE | re.MULTILINE)
    for label in label_re.findall(code):
        use_re = re.compile(r"@" + re.escape(label) + r"\b", re.IGNORECASE)
        for line in lines:
            if use_re.search(line) and DECL_CALL_RE.search(line):
                return True, f"DAT string {label} is passed to a SIGNOFF-DECL emitter"
    return False, "no SIGNOFF-DECL emission names this cell"


def host_inputs_ready(cell):
    """HOST cells name their inputs in the test column after 'inputs:' (flag:, file:, src:PATH:TOKEN)."""
    match = re.search(r"\binputs:\s*(.*)$", cell.test)
    if not match or not match.group(1).split():
        return False, "HOST cell names no input in its test column (expected 'inputs: ...')"
    problems = []
    for spec in match.group(1).split():
        kind, _, rest = spec.partition(":")
        if kind == "flag":
            continue
        if kind == "file":
            if not (REPO_ROOT / rest).is_file():
                problems.append(f"input file absent: {rest}")
        elif kind == "src":
            path_text, _, token = rest.rpartition(":")
            source = REPO_ROOT / path_text
            if not path_text or not token:
                problems.append(f"bad src input {spec!r}")
            elif not source.is_file():
                problems.append(f"source absent: {path_text}")
            elif token not in strip_spin2_comments(source.read_text(encoding="utf-8", errors="replace")):
                problems.append(f"{path_text} has no {token} outside comments")
        else:
            problems.append(f"unknown input kind {spec!r}")
    if problems:
        return False, "; ".join(problems)
    return True, "named inputs present: " + " ".join(match.group(1).split())


def check_ready(manifest_path, visit):
    try:
        cells = load_manifest(manifest_path)
    except ManifestError as exc:
        print(f"signoff-collate: manifest error: {exc}", file=sys.stderr)
        return EXIT_INPUT
    owed = [cell for cell in cells if cell.visit_n == visit and cell.status == "OWED"]
    sources = {}
    gaps = 0
    print(f"check-ready visit {visit}: {len(owed)} OWED cell(s) in {display_path(manifest_path)}")
    for cell in owed:
        if cell.bin == "HOST":
            ready, why = host_inputs_ready(cell)
        else:
            rel = BIN_SOURCES[cell.bin]
            if rel not in sources:
                path = REPO_ROOT / rel
                sources[rel] = path.read_text(encoding="utf-8", errors="replace") if path.is_file() else None
            if sources[rel] is None:
                ready, why = False, f"source absent: {rel}"
            else:
                ready, why = source_declares_cell(sources[rel], cell.cell)
                why = f"{rel}: {why}"
        gaps += 0 if ready else 1
        print(f"{'READY' if ready else 'GAP  '} {cell.cell:<20} bin {cell.bin:<6} {why}")
    print(f"check-ready visit {visit}: {len(owed) - gaps} ready, {gaps} gap(s)")
    return EXIT_GAPS if gaps else EXIT_OK


# ---------------------------------------------------------------------------------------------
# --selftest
# ---------------------------------------------------------------------------------------------

def find_external_command_uses(source_text):
    """Return subprocess/os-exec uses that are not inside the top-level run() function."""
    offenders = []
    os_exec = ("system", "popen", "fork", "forkpty")
    os_exec_prefixes = ("exec", "spawn", "posix_spawn")

    def visit(node, stack):
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            stack = stack + [node.name]
        inside_run = stack[:1] == ["run"]
        if not inside_run:
            if isinstance(node, ast.Import):
                for alias in node.names:
                    if alias.name.split(".")[0] in ("subprocess", "pty"):
                        offenders.append(f"line {node.lineno}: import {alias.name}")
            elif isinstance(node, ast.ImportFrom):
                module = (node.module or "").split(".")[0]
                if module in ("subprocess", "pty"):
                    offenders.append(f"line {node.lineno}: from {node.module} import")
                if module == "os" and any(alias.name in os_exec or alias.name.startswith(os_exec_prefixes)
                                          for alias in node.names):
                    offenders.append(f"line {node.lineno}: from os import an exec function")
            elif isinstance(node, ast.Name) and node.id == "subprocess":
                offenders.append(f"line {node.lineno}: subprocess")
            elif (isinstance(node, ast.Attribute) and isinstance(node.value, ast.Name) and node.value.id == "os"
                  and (node.attr in os_exec or node.attr.startswith(os_exec_prefixes))):
                offenders.append(f"line {node.lineno}: os.{node.attr}")
        for child in ast.iter_child_nodes(node):
            visit(child, stack)

    visit(ast.parse(source_text), [])
    return offenders


def _fx_signoff(cell, task, motor, crit, measured, low, high, units, count, verdict, bin_token="T0"):
    return (f"SIGNOFF,sf,1,bin,{bin_token},cell,{cell},task,{task},motor,{motor},crit,{crit},measured,{measured},"
            f"lo,{low},hi,{high},units,{units},n,{count},verdict,{verdict}")


def _fx_decl(cell, task, bin_token="T0"):
    return f"SIGNOFF-DECL,sf,1,bin,{bin_token},cell,{cell},task,{task}"


def _fx_log(name, body, complete=True, bin_file="test_bench_t0.bin", size=21000,
            mtime="2026-09-13T18:00:00.000Z", banner="* test_bench_t0 -- Tier 0 (in-memory fixture)",
            session="2026-09-13T12:00:00.000"):
    """Build an in-memory log in the pnut-term-ts line format. body items: payload or (cog, payload)."""
    lines = [f"=== Debug Logger Session Started at {session} ===",
             f"[{session}] [SYSTEM] [DOWNLOAD TO RAM] File: {bin_file} | Size: {size} bytes | Modified: {mtime}",
             f"[{session}] Cog0  {banner}"]
    for item in body:
        cog, payload = item if isinstance(item, tuple) else (0, item)
        lines.append(f"[{session}] Cog{cog}  {payload}")
    if complete:
        lines.append(f"[{session}] Cog0  DEBUG_END_SESSION")
    return LogInfo(name, "\n".join(lines) + "\n")


def _fx_collate(logs):
    return collate(load_manifest(FIXTURE_DIR / "fx-manifest.tsv"), logs, visit=1, static_tree=False,
                   predictions_path=FIXTURE_DIR / "absent-predictions.tsv",
                   baseline_path=FIXTURE_DIR / "absent-baseline.log")


def _verdict(col, cell_id):
    result = col.results[cell_id]
    return result.verdict, result.reason


def _st_a_negative_case():
    cells = load_manifest(DEFAULT_MANIFEST)
    log = read_log_file(NEGCASE_LOG)
    col = collate(cells, [log], visit=1, static_tree=False, predictions_path=DEFAULT_PREDICTIONS,
                  baseline_path=DEFAULT_BASELINE)
    problems = []
    if log.complete:
        problems.append("log reads COMPLETE")
    if log.records:
        problems.append(f"log unexpectedly holds {len(log.records)} sign-off records")
    if len(col.rows) != 13:
        problems.append(f"{len(col.rows)} rows, expected 13")
    problems += [f"row {row_n} is {verdict}" for row_n, _, _, verdict in col.rows if verdict != "NOT_BUILT"]
    problems += [f"{cell.cell} is {col.results[cell.cell].verdict}" for cell in col.scope
                 if col.results[cell.cell].verdict != "NOT_BUILT"]
    row8 = [verdict for row_n, _, _, verdict in col.rows if row_n == 8]
    if row8 != ["NOT_BUILT"]:
        problems.append(f"row 8 is {row8}")
    detail = (f"{display_path(NEGCASE_LOG)}: {len(col.rows)} rows and {len(col.scope)} cells all NOT_BUILT, "
              f"row 8 NOT_BUILT, log {'COMPLETE' if log.complete else 'TRUNCATED'}")
    return not problems, "; ".join(problems) if problems else detail


def _st_b_verdict_inconsistent():
    col = _fx_collate([read_log_file(FIXTURE_DIR / "b-inconsistent.log")])
    got_ticks = _verdict(col, "R4-T0-1M-TICKS")
    got_dirty = _verdict(col, "R2-T0-DIRTY")
    proving = col.results["R4-T0-1M-TICKS"].refs
    control = _fx_collate([_fx_log("b-control", [
        _fx_decl("R4-T0-1M-TICKS", 3502), _fx_decl("R2-T0-DIRTY", 3500),
        _fx_signoff("R4-T0-1M-TICKS", 3502, "NONE", "DDU_M_TICKS", 173, 173, 174, "TICKS", 1, "PASS"),
        _fx_signoff("R2-T0-DIRTY", 3500, "RIGHT", "POSTSTOP_REVB", "TRUE", "TRUE", "TRUE", "BOOL", 1, "PASS"),
        _fx_signoff("R2-T0-DIRTY", 3500, "LEFT", "POSTSTOP_REVB", "TRUE", "TRUE", "TRUE", "BOOL", 1, "PASS")])])
    ok = (got_ticks == ("FAIL", "VERDICT_INCONSISTENT") and got_dirty == ("FAIL", "VERDICT_INCONSISTENT")
          and proving == ["tools/fixtures/signoff/b-inconsistent.log:10"]
          and _verdict(control, "R4-T0-1M-TICKS")[0] == "PASS" and _verdict(control, "R2-T0-DIRTY")[0] == "PASS")
    return ok, (f"PASS measured 175 outside 173..174 -> {got_ticks}, proving {proving}; BOOL PASS measured FALSE -> "
                f"{got_dirty}; control measured 173 / TRUE -> {_verdict(control, 'R4-T0-1M-TICKS')[0]} / "
                f"{_verdict(control, 'R2-T0-DIRTY')[0]}")


def _st_c_pl9():
    with_it = check_pl9_text("CON\n    DEAD_GAP = 1\nPRI calc() | gapInMS\n    gapInMS := 3\n")
    upper = check_pl9_text("PRI calc() | GAPINMS\n")
    without = check_pl9_text("CON\n    DEAD_GAP = 1\nPRI calc() | gapInNS, gapInMSx\n    gapInNS := 3\n")
    ok = with_it == ("FAIL", [3, 4]) and upper == ("FAIL", [1]) and without == ("PASS", [])
    return ok, f"with gapInMS -> {with_it}; GAPINMS -> {upper}; without (gapInNS, gapInMSx) -> {without}"


def _st_d_same_build_rerun():
    log_a = read_log_file(FIXTURE_DIR / "d-rerun-A-fail.log")
    log_b = read_log_file(FIXTURE_DIR / "d-rerun-B-pass.log")
    body_b = [_fx_decl("R3-T0-STOPPED", 3501),
              _fx_signoff("R3-T0-STOPPED", 3501, "NONE", "STOPPED_COUNTS", 0, 0, 0, "COUNT", 1, "PASS")]
    rebuilt = _fx_log("d-rebuilt-same-source", body_b, size=21000, mtime="2026-09-13T20:00:00.000Z",
                      session="2026-09-13T14:00:00.000")
    newbuild = _fx_log("d-new-build", body_b, size=21016, mtime="2026-09-13T20:00:00.000Z",
                       session="2026-09-13T14:00:00.000")
    fwd = _verdict(_fx_collate([log_a, log_b]), "R3-T0-STOPPED")
    rev = _verdict(_fx_collate([log_b, log_a]), "R3-T0-STOPPED")
    alone = _verdict(_fx_collate([log_b]), "R3-T0-STOPPED")
    same_src = _verdict(_fx_collate([log_a, rebuilt]), "R3-T0-STOPPED")
    col_new = _fx_collate([log_a, newbuild])
    new = _verdict(col_new, "R3-T0-STOPPED")
    superseded = [logcell.log.display for _, logcell in col_new.results["R3-T0-STOPPED"].superseded]
    ok = (fwd[0] == "FAIL" and rev[0] == "FAIL" and alone[0] == "PASS" and same_src[0] == "FAIL"
          and new[0] == "PASS" and superseded == ["tools/fixtures/signoff/d-rerun-A-fail.log"])
    return ok, (f"A FAIL + later B PASS, same build -> {fwd[0]} (reversed order {rev[0]}); B alone -> {alone[0]}; "
                f"A + same source rebuilt (new mtime) -> {same_src[0]}; A + genuinely new build -> {new[0]}, "
                f"superseded {superseded}")


def _st_e_no_pooling():
    col = _fx_collate([read_log_file(FIXTURE_DIR / "e-partial-right.log"),
                       read_log_file(FIXTURE_DIR / "e-partial-left.log")])
    pooled = _verdict(col, "R2-T0-REPEAT")
    whole = _verdict(_fx_collate([_fx_log("e-whole", [
        _fx_decl("R2-T0-REPEAT", 3500),
        _fx_signoff("R2-T0-REPEAT", 3500, "RIGHT", "READS_NOT_REVB", 0, 0, 0, "COUNT", 32, "PASS"),
        _fx_signoff("R2-T0-REPEAT", 3500, "LEFT", "READS_NOT_REVB", 0, 0, 0, "COUNT", 32, "PASS")])]),
        "R2-T0-REPEAT")
    ok = pooled == ("NOMEAS", "TOO_FEW_INSTANCES") and whole[0] == "PASS"
    return ok, f"RIGHT-only log + LEFT-only log (min_inst 2) -> {pooled}; both in one log -> {whole[0]}"


def _st_f_truncated():
    log = read_log_file(FIXTURE_DIR / "f-truncated.log")
    col = _fx_collate([log])
    passed = _verdict(col, "R3-T0-STOPPED")
    failed = _verdict(col, "R1-T0-RESTART")
    ok = (not log.complete) and passed == ("NOMEAS", "LOG_TRUNCATED") and failed[0] == "FAIL"
    return ok, (f"log {'COMPLETE' if log.complete else 'TRUNCATED'}; its PASS -> {passed}; its FAIL -> "
                f"{failed[0]}")


def _st_g_count_filter():
    scan = _verdict(_fx_collate([read_log_file(FIXTURE_DIR / "g-row8-nonfalsifiable.log")]), "R8-SCAN-ZXS")

    def t0_row8(name, w_verdict, channels=("I", "U", "V", "W")):
        body = [_fx_decl("R8-T0-ZXS", 3529)]
        for channel in channels:
            verdict = w_verdict if channel == "W" else "PASS"
            measured = "NA" if verdict == "NOMEAS" else (80 if verdict == "FAIL" else 12)
            body.append(_fx_signoff("R8-T0-ZXS", 3529, "RIGHT", f"ZXS_{channel}", measured, 0, 50, "MV_X10", 5,
                                    verdict))
        return _verdict(_fx_collate([_fx_log(name, body)]), "R8-T0-ZXS")

    only_w = t0_row8("g-only-w", "PASS", channels=("W",))
    all_pass = t0_row8("g-all-pass", "PASS")
    w_fail = t0_row8("g-w-fail", "FAIL")
    w_nomeas = t0_row8("g-w-nomeas", "NOMEAS")
    ok = (scan == ("NOMEAS", "TOO_FEW_INSTANCES") and only_w == ("NOMEAS", "TOO_FEW_INSTANCES")
          and all_pass[0] == "PASS" and w_fail[0] == "FAIL" and w_nomeas[0] == "PASS")
    return ok, (f"scan row 8 with only LEFT u, LEFT w, RIGHT w passing -> {scan}; T0 only w -> {only_w}; "
                f"T0 i,u,v,w PASS -> {all_pass[0]}; i,u,v PASS + w FAIL (outside filter) -> {w_fail[0]}; "
                f"i,u,v PASS + w NOMEAS -> {w_nomeas[0]}")


def _st_h_manifest_view():
    md_path = DEFAULT_MANIFEST.with_suffix(".md")
    expected = render_manifest_md(load_manifest(DEFAULT_MANIFEST))
    actual = md_path.read_text(encoding="utf-8") if md_path.is_file() else ""
    if expected == actual:
        return True, f"{display_path(md_path)} equals the view rendered from {display_path(DEFAULT_MANIFEST)}"
    exp_lines, act_lines = expected.split("\n"), actual.split("\n")
    for index in range(max(len(exp_lines), len(act_lines))):
        exp = exp_lines[index] if index < len(exp_lines) else "<EOF>"
        act = act_lines[index] if index < len(act_lines) else "<EOF>"
        if exp != act:
            return False, f"{display_path(md_path)} line {index + 1} differs: expected {exp!r} got {act!r}"
    return False, "views differ"


def _st_i_malformed():
    log = _fx_log("i-malformed", [
        _fx_decl("R2-T0-EMPTY", 3500),
        _fx_signoff("R2-T0-EMPTY", 3500, "NONE", "EMPTY_NODET", "1", "TRUE", "TRUE", "BOOL", 1, "PASS")])
    col = collate(load_manifest(DEFAULT_MANIFEST), [log], visit=1, static_tree=False,
                  predictions_path=FIXTURE_DIR / "absent-predictions.tsv",
                  baseline_path=FIXTURE_DIR / "absent-baseline.log")
    got = _verdict(col, "R2-T0-EMPTY")
    ok = got == ("NOMEAS", "MALFORMED") and any(line.startswith("i-malformed:5:") for line in col.parse_errors)
    return ok, f"BOOL cell with measured 1 -> {got}; parse error {col.parse_errors[:1]}"


def _st_j_no_subprocess():
    own = find_external_command_uses(SCRIPT_PATH.read_text(encoding="utf-8"))
    planted = find_external_command_uses("import subprocess\nsubprocess.run(['ls'])\n")
    allowed = find_external_command_uses("def run(argv):\n    import subprocess\n    subprocess.run(argv)\n")
    ok = own == [] and len(planted) == 2 and allowed == []
    return ok, (f"this script: {own or 'no subprocess use outside run()'}; planted module-level use found "
                f"{len(planted)}; use inside run() found {len(allowed)}")


def _st_k_check_ready_detector():
    t0_style = '    debug("SIGNOFF-DECL,sf,1,bin,T0,cell,R9-T0-FAKE,task,1")\n'
    char_style = ('PRI decls()\n    emitSignoffDecl(@sFakeCell, @sFakeTask)   \' declares it\n'
                  'PRI emitSignoffDecl(pCell, pTask)\n    lineAddText(@"SIGNOFF-DECL")\n'
                  'DAT\nsFakeCell       BYTE    "R9-CHAR-FAKE", 0\n')
    commented = ('\' debug("SIGNOFF-DECL,sf,1,bin,T0,cell,R9-T0-FAKE,task,1")\n'
                 '{ debug("SIGNOFF-DECL,sf,1,bin,T0,cell,R9-T0-FAKE,task,1") }\n')
    prefix = '    debug("SIGNOFF-DECL,sf,1,bin,T0,cell,R9-T0-FAKEX,task,1")\n'
    verdict_only = '    debug("SIGNOFF,sf,1,bin,T0,cell,R9-T0-FAKE,task,1,motor,NONE")\n'
    results = {
        "T0 style": source_declares_cell(t0_style, "R9-T0-FAKE")[0],
        "CHAR style": source_declares_cell(char_style, "R9-CHAR-FAKE")[0],
        "comment only": source_declares_cell(commented, "R9-T0-FAKE")[0],
        "longer id only": source_declares_cell(prefix, "R9-T0-FAKE")[0],
        "SIGNOFF verdict only": source_declares_cell(verdict_only, "R9-T0-FAKE")[0],
    }
    expected = {"T0 style": True, "CHAR style": True, "comment only": False, "longer id only": False,
                "SIGNOFF verdict only": False}
    return results == expected, ", ".join(f"{name} -> {'ready' if value else 'gap'}" for name, value in results.items())


def _st_l_wdtend():
    def wd_log(name, flag, cogs, complete=True):
        body = [f"BS-BUILD,wd_selftest,{flag},sf,1,zxs_starts,5,zxs_max_mV_x10,50"]
        for cell_id, cog in zip(WDT_CELLS, cogs):
            body.append((cog, _fx_signoff(cell_id, 3534, "NONE", "X", "TRUE", "TRUE", "TRUE", "BOOL", 1, "PASS",
                                          bin_token="SCANWD")))
        return _fx_log(name, body, complete=complete, bin_file="test_bench_scan.bin",
                       banner="BS-BANNER,src_rev,7,fmt,7,cfg_id,BENCH")

    good = host_wdtend([wd_log("wd-good", "TRUE", (2, 2, 2, 2))]).verdict
    cog0 = host_wdtend([wd_log("wd-cog0", "TRUE", (2, 0, 2, 2))]).verdict
    trunc = host_wdtend([wd_log("wd-trunc", "TRUE", (2, 2, 2, 2), complete=False)]).verdict
    noflag = host_wdtend([wd_log("wd-noflag", "FALSE", (2, 2, 2, 2))]).verdict
    ok = good == "PASS" and cog0 == "FAIL" and trunc == "FAIL" and noflag == "NOT_BUILT"
    return ok, (f"flag TRUE + 4 records from Cog2 + end -> {good}; one from Cog0 -> {cog0}; truncated -> {trunc}; "
                f"wd_selftest FALSE -> {noflag}")


DETDIFF_PASS_FIXTURE = "m-detdiff-visit-pass.log"
GUARD_PASS_FIXTURE = "n-guard-guarded.log"
GUARD_FAIL_FIXTURE = "n-guard-unguarded.log"
DETDIFF_MUTATED_CELL = "BD-CELL,sw,5,grp,32,gnm,P32_P47,cog,P0_P15,cogst,STOPPED,clr,CLR,n,32,sum_min,94,sum_max,99,"


def _detdiff_on_text(name, text):
    """Run R2-HOST-DETDIFF on an in-memory visit log against the real baseline and prediction list."""
    result = detdiff_compare([LogInfo(name, text)], read_log_file(DEFAULT_BASELINE), DEFAULT_PREDICTIONS)
    diff = result.extra["logs"][0][1] if result.extra.get("logs") else None
    return result, diff


def _detdiff_summary(result, diff):
    if diff is None:
        return f"{result.verdict} ({result.reason}): {'; '.join(result.detail[:3])}"
    first = [change["text"] for change in diff["unpredicted"] + diff["not_occurred"]][:2] + diff["blockers"][:2]
    return (f"{result.verdict} ({result.reason or '-'}), measured {diff['measured']} = {len(diff['unpredicted'])} "
            f"unpredicted + {len(diff['not_occurred'])} not occurred; {len(diff['occurred'])} occurred; "
            f"{len(diff['not_compared'])} NOT_COMPARED" + (f"; first: {first}" if first else ""))


def _st_m_detdiff_pass():
    text = (FIXTURE_DIR / DETDIFF_PASS_FIXTURE).read_text(encoding="utf-8")
    result, diff = _detdiff_on_text(DETDIFF_PASS_FIXTURE, text)
    rows, _ = load_predictions(DEFAULT_PREDICTIONS)
    compared = sum(1 for row in rows if row["status"] == "COMPARED")
    ok = (result.verdict == "PASS" and diff is not None and diff["measured"] == 0
          and len(diff["occurred"]) == compared and not diff["blockers"])
    return ok, f"visit applying exactly the {compared} COMPARED predictions -> {_detdiff_summary(result, diff)}"


def _st_n_detdiff_unpredicted():
    text = (FIXTURE_DIR / DETDIFF_PASS_FIXTURE).read_text(encoding="utf-8")
    mutated = text.replace(DETDIFF_MUTATED_CELL, DETDIFF_MUTATED_CELL.replace("sum_max,99,", "sum_max,120,"))
    visit_line = next((index for index, line in enumerate(mutated.splitlines(), start=1)
                       if "BD-CELL,sw,5,grp,32," in line), None)
    result, diff = _detdiff_on_text("n-unpredicted", mutated)
    listed = diff["unpredicted"][0]["text"] if diff and diff["unpredicted"] else ""
    ok = (mutated != text and result.verdict == "FAIL" and diff["measured"] == 1 and len(diff["unpredicted"]) == 1
          and "sw 5 P32_P47 sum_max: 99 -> 120" in listed
          and f"{display_path(DEFAULT_BASELINE)}:1072" in listed and f"n-unpredicted:{visit_line}" in listed
          and result.refs == [f"n-unpredicted:{visit_line}"])
    return ok, f"sw 5 P32_P47 sum_max 99 -> 120 (+21, outside +-11) -> {_detdiff_summary(result, diff)}; listed: {listed}"


def _st_o_detdiff_baseline_self():
    baseline = read_log_file(DEFAULT_BASELINE)
    result = detdiff_compare([baseline], baseline, DEFAULT_PREDICTIONS)
    diff = result.extra["logs"][0][1] if result.extra.get("logs") else None
    rows, _ = load_predictions(DEFAULT_PREDICTIONS)
    judged = sum(1 for row in rows if row["status"] != "EXCLUDED_VOID")
    ok = (result.verdict == "FAIL" and diff is not None and not diff["unpredicted"]
          and len(diff["not_occurred"]) == judged)
    return ok, (f"baseline against itself: {judged} non-void predicted changes cannot occur -> "
                f"{_detdiff_summary(result, diff)}")


def _st_p_detdiff_void():
    text = (FIXTURE_DIR / DETDIFF_PASS_FIXTURE).read_text(encoding="utf-8")
    mutated = text.replace("clkfreq_runtime,270_000_000,match,1", "clkfreq_runtime,270_000_000,match,0")
    result, diff = _detdiff_on_text("p-void", mutated)
    ok = mutated != text and result.verdict == "NOMEAS" and result.reason == "VOID"
    return ok, f"visit BD-CLK match 0 -> {result.verdict} ({result.reason}); {diff['void'] if diff else result.detail}"


def _st_q_detdiff_all_skipped():
    lines = (FIXTURE_DIR / DETDIFF_PASS_FIXTURE).read_text(encoding="utf-8").splitlines()
    replaced = 0
    for index, line in enumerate(lines):
        for sw in DETECT_POSTSTOP_SWEEPS:
            marker = f"Cog0  BD-CELL,sw,{sw},grp,0,"
            if marker in line:
                cog = "P0_P15" if sw in (4, 5) else "P16_P31"
                clr = "NOCLR" if sw in (4, 7) else "CLR"
                lines[index] = (line.split("Cog0  ")[0] + f"Cog0  BD-SKIPPED,sw,{sw},grp,0,gnm,P0_P15,pin,4,ovl,NONE,"
                                f"cog,{cog},cogst,STOPPED,clr,{clr},n,32,reason,GATE_OVERLAP")
                replaced += 1
    result, diff = _detdiff_on_text("q-all-skipped", "\n".join(lines) + "\n")
    ok = (replaced == 4 and result.verdict == "NOMEAS" and diff["measured"] == 0
          and any(blocker.startswith("NO_POSTSTOP_COMPARED") and "P0_P15" in blocker for blocker in diff["blockers"]))
    return ok, f"every post-stop P0_P15 cell ({replaced}) SKIPPED -> {_detdiff_summary(result, diff)}"


def _st_r_guard_unguarded():
    result = detect_guard_check([read_log_file(FIXTURE_DIR / GUARD_FAIL_FIXTURE)])
    rep_lines = [line for line in result.detail if "BD-REP for sw" in line and "P40_P55" in line]
    ok = result.verdict == "FAIL" and len(rep_lines) == 6
    return ok, (f"SRC_REV 2 binary on the bench bases (BD-REP for P40_P55) -> {result.verdict} ({result.reason}); "
                f"{len(rep_lines)} P40_P55 BD-REP failure(s), e.g. {rep_lines[:1]}")


def _st_s_guard_guarded():
    result = detect_guard_check([read_log_file(FIXTURE_DIR / GUARD_PASS_FIXTURE)])
    skip_line = next((line for line in result.detail if "skip set from BD-CFG" in line), "")
    ok = (result.verdict == "PASS" and "GATE_OVERLAP groups NO_USE_P24_P39, P40_P55;" in skip_line
          and "COG_OVERLAP sweeps none" in skip_line)
    return ok, f"guarded log -> {result.verdict} ({result.reason or '-'}); {skip_line}"


# PL-40 fixtures. t- copies DOCs/analyses/bench/2026-09-14/debug_260914-114636.log lines 993-1004 verbatim (the
# R1-T0-RESTART record sits after the dump's closing '|' on fixture line 19 = log line 1002) with that log's
# header, banner, two of its declarations and its DEBUG_END_SESSION line. u- is the same stretch with the record
# cut: R1-T0-RESTART stops before ",verdict,PASS" (which follows in a second dump) and R10-T0-STOPREADY runs into a
# "[BINARY DATA" marker on its own line. w- holds a deliberately built dump whose ASCII gutter carries a whole
# SIGNOFF (one row's gutter shows ".|Cog0  SIGNOFF,"), then debug_260914-115953.log lines 250-254, 282-364,
# 375-379 and 432-459 verbatim.
RECOVERY_POSITIVE_FIXTURE = "t-recovered-after-dump.log"
RECOVERY_TRUNCATED_FIXTURE = "u-truncated-in-dump.log"
RECOVERY_GUTTER_FIXTURE = "w-gutter-no-recovery.log"
LEGACY_FIXTURES = ("b-inconsistent.log", "d-rerun-A-fail.log", "d-rerun-B-pass.log", "e-partial-right.log",
                   "e-partial-left.log", "f-truncated.log", "g-row8-nonfalsifiable.log", DETDIFF_PASS_FIXTURE,
                   GUARD_PASS_FIXTURE, GUARD_FAIL_FIXTURE, RECOVERY_POSITIVE_FIXTURE)


def _real_collate(logs):
    return collate(load_manifest(DEFAULT_MANIFEST), logs, visit=1, static_tree=False,
                   predictions_path=FIXTURE_DIR / "absent-predictions.tsv",
                   baseline_path=FIXTURE_DIR / "absent-baseline.log")


def _recovered_section(col):
    sheet = render_sheet(col, 1, "selftest", DEFAULT_MANIFEST, False, False, FIXTURE_DIR / "absent-predictions.tsv",
                         FIXTURE_DIR / "absent-baseline.log", [])
    return sheet.split(RECOVERED_SECTION, 1)[1].split("\n## ", 1)[0] if RECOVERED_SECTION in sheet else ""


def _st_t_recovered_after_dump():
    path = FIXTURE_DIR / RECOVERY_POSITIVE_FIXTURE
    log = read_log_file(path)
    col = _real_collate([log])
    tail_line = next((lineno for lineno, line in enumerate(log.lines, start=1)
                      if HEX_ROW_RE.match(line) and "Cog0  SIGNOFF," in HEX_ROW_RE.match(line).group(3)), None)
    ref = f"{display_path(path)}:{tail_line}"
    restart, stopready = col.results["R1-T0-RESTART"], col.results["R10-T0-STOPREADY"]
    rec = next((rec for rec in log.records if rec.lineno == tail_line), None)
    proving = [line for line in restart.proving if line.startswith(ref + " ")]
    section = _recovered_section(col)
    ok = (tail_line is not None and rec is not None and rec.recovered and rec.error is None and rec.cog == 0
          and restart.verdict == "PASS" and restart.refs == [ref]
          and len(proving) == 1 and "RECOVERED from a corrupted line" in proving[0]
          and stopready.verdict == "PASS" and not any("RECOVERED" in line for line in stopready.proving)
          and f"- {ref} Cog0 SIGNOFF R1-T0-RESTART -- recovered:" in section
          and "parsed and counted" in section and not col.parse_errors)
    return ok, (f"R1-T0-RESTART on the dump tail at {ref} -> {restart.verdict}, refs {restart.refs}, proving "
                f"{proving[:1]}; ordinary R10-T0-STOPREADY -> {stopready.verdict} unflagged; "
                f"listed in the recovered section: {f'- {ref} Cog0 SIGNOFF R1-T0-RESTART' in section}")


def _st_u_truncated_in_dump():
    path = FIXTURE_DIR / RECOVERY_TRUNCATED_FIXTURE
    log = read_log_file(path)
    col = _real_collate([log])
    got = {cell_id: _verdict(col, cell_id) for cell_id in ("R1-T0-RESTART", "R10-T0-STOPREADY")}
    verdict_recs = {rec.cell: rec for rec in log.records if rec.kind == "SIGNOFF"}
    restart, stopready = verdict_recs.get("R1-T0-RESTART"), verdict_recs.get("R10-T0-STOPREADY")
    ok = (got == {"R1-T0-RESTART": ("NOMEAS", "MALFORMED"), "R10-T0-STOPREADY": ("NOMEAS", "MALFORMED")}
          and len(verdict_recs) == 2 and restart is not None and stopready is not None
          and restart.recovered and stopready.recovered
          and restart.error is not None and "22 fields after the tag, expected 24" in restart.error
          and stopready.error is not None and "[BINARY DATA" in stopready.error
          and len(col.parse_errors) == 2 and all("RECOVERED from a corrupted line" in line for line in col.parse_errors)
          and not any(result.verdict == "PASS" for result in col.results.values()))
    return ok, (f"cut records -> {got}; parse errors {col.parse_errors}")


def _legacy_scan(text):
    """The pre-PL-40 reader: a message only where LOG_LINE_RE matches at line start."""
    records, end, bd = [], None, []
    for lineno, line in enumerate(text.splitlines(), start=1):
        match = LOG_LINE_RE.match(line)
        if not match:
            continue
        payload = match.group(3)
        if payload == "DEBUG_END_SESSION":
            end = end or lineno
        elif payload.startswith(("SIGNOFF,", "SIGNOFF-DECL,")):
            records.append((lineno, int(match.group(2)), payload))
        elif payload.startswith("BD-"):
            bd.append((lineno, payload))
    return records, end, bd


def _st_v_line_start_regression():
    problems, compared = [], 0
    sources = [(name, (FIXTURE_DIR / name).read_text(encoding="utf-8")) for name in LEGACY_FIXTURES]
    sources.append((display_path(NEGCASE_LOG), NEGCASE_LOG.read_text(encoding="utf-8", errors="replace")))
    sources.append(("in-memory", "\n".join(_fx_log("v-inline", [
        _fx_decl("R3-T0-STOPPED", 3501),
        _fx_signoff("R3-T0-STOPPED", 3501, "NONE", "STOPPED_COUNTS", 0, 0, 0, "COUNT", 1, "PASS")]).lines) + "\n"))
    for name, text in sources:
        log = LogInfo(name, text)
        legacy_records, legacy_end, legacy_bd = _legacy_scan(text)
        ordinary = [rec for rec in log.records if not rec.recovered]
        if [(rec.lineno, rec.cog, rec.payload) for rec in ordinary] != legacy_records:
            problems.append(f"{name}: line-start records differ from the legacy reader")
        for rec in ordinary:
            legacy = Record(rec.kind, log, rec.lineno, rec.cog, rec.payload)
            compared += 1
            if (rec.fields, rec.norm, rec.error, rec.cell) != (legacy.fields, legacy.norm, legacy.error, legacy.cell):
                problems.append(f"{rec.ref}: parse differs from the legacy parse")
        if log.end_lineno != legacy_end:
            problems.append(f"{name}: DEBUG_END_SESSION line {log.end_lineno} != legacy {legacy_end}")
        if [(m.lineno, m.payload) for m in log.messages if m.payload.startswith("BD-") and not m.recovered] != legacy_bd:
            problems.append(f"{name}: line-start BD- messages differ from the legacy reader")
        extra = [message for message in log.flagged_messages if name != RECOVERY_POSITIVE_FIXTURE or message.cut]
        if extra:
            problems.append(f"{name}: unexpected recovered/cut message(s) at line(s) {[m.lineno for m in extra]}")
    positive = LogInfo(RECOVERY_POSITIVE_FIXTURE, sources[LEGACY_FIXTURES.index(RECOVERY_POSITIVE_FIXTURE)][1])
    if [rec.lineno for rec in positive.records if rec.recovered] != [19]:
        problems.append("the positive fixture's only recovered record is not its line 19")
    return not problems, ("; ".join(problems) if problems else
                          f"{len(sources)} logs: every line-start SIGNOFF/SIGNOFF-DECL, BD- record and DEBUG_END_SESSION "
                          f"matches the legacy line-start reader; {compared} records re-parsed identically; the only "
                          "addition anywhere is the positive fixture's recovered line 19")


def _st_w_gutter_no_recovery():
    path = FIXTURE_DIR / RECOVERY_GUTTER_FIXTURE
    log = read_log_file(path)
    col = _real_collate([log])
    gutter_rows = [lineno for lineno, line in enumerate(log.lines, start=1)
                   if HEX_ROW_RE.match(line) and "Cog0  SIGNOFF," in HEX_ROW_RE.match(line).group(2)]
    naive_hits = [lineno for lineno, line in enumerate(log.lines, start=1)
                  if "Cog0  SIGNOFF," in line and not LOG_LINE_RE.match(line)]
    listed = [entry for entry in log.unparsed_signoff if gutter_rows and entry[0] <= gutter_rows[0] <= entry[1]]
    section = _recovered_section(col)
    ok = (len(gutter_rows) == 1 and naive_hits == gutter_rows
          and not [rec for rec in log.records if rec.kind == "SIGNOFF"] and not log.flagged_messages
          and _verdict(col, "R1-T0-RESTART") == ("NOMEAS", "NOT_REACHED") and not col.parse_errors
          and len(listed) == 1 and "gutter" in listed[0][2] and "no record, no verdict" in section)
    return ok, (f"gutter row(s) carrying 'Cog0  SIGNOFF,' at line(s) {gutter_rows}; SIGNOFF records "
                f"{len([rec for rec in log.records if rec.kind == 'SIGNOFF'])}; recovered messages "
                f"{len(log.flagged_messages)}; R1-T0-RESTART -> {_verdict(col, 'R1-T0-RESTART')}; listed unparsed "
                f"{listed}")


def selftest():
    checks = [
        ("(a)", "run-5 negative case", _st_a_negative_case),
        ("(b)", "PASS outside lo..hi is FAIL VERDICT_INCONSISTENT", _st_b_verdict_inconsistent),
        ("(c)", "R10-HOST-PL9 static check", _st_c_pl9),
        ("(d)", "same-build rerun cannot hide a FAIL", _st_d_same_build_rerun),
        ("(e)", "min_inst never pooled across logs", _st_e_no_pooling),
        ("(f)", "TRUNCATED log: PASS -> NOMEAS, FAIL kept", _st_f_truncated),
        ("(g)", "row 8 count_filter", _st_g_count_filter),
        ("(h)", "SIGNOFF-MANIFEST.md is the rendered view of the .tsv", _st_h_manifest_view),
        ("(i)", "malformed record -> NOMEAS MALFORMED with file:line", _st_i_malformed),
        ("(j)", "no subprocess use outside run()", _st_j_no_subprocess),
        ("(k)", "--check-ready declaration detector", _st_k_check_ready_detector),
        ("(l)", "R11-HOST-WDTEND conditions", _st_l_wdtend),
        ("(m)", "R2-HOST-DETDIFF: visit applying exactly the COMPARED predictions is PASS", _st_m_detdiff_pass),
        ("(n)", "R2-HOST-DETDIFF: one unpredicted change is FAIL, listed with both line numbers",
         _st_n_detdiff_unpredicted),
        ("(o)", "R2-HOST-DETDIFF: the baseline against itself is FAIL (unfixed value)", _st_o_detdiff_baseline_self),
        ("(p)", "R2-HOST-DETDIFF: BD-CLK match 0 is NOMEAS VOID", _st_p_detdiff_void),
        ("(q)", "R2-HOST-DETDIFF: no post-stop P0_P15 cell compared is NOMEAS", _st_q_detdiff_all_skipped),
        ("(r)", "R2-DETECT-GUARD: BD-REP for P40_P55 (SRC_REV 2 binary) is FAIL", _st_r_guard_unguarded),
        ("(s)", "R2-DETECT-GUARD: a guarded log is PASS", _st_s_guard_guarded),
        ("(t)", "PL-40: a SIGNOFF after a hex dump's closing | is recovered, counted and flagged",
         _st_t_recovered_after_dump),
        ("(u)", "PL-40: a SIGNOFF cut short across a dump is MALFORMED and not counted", _st_u_truncated_in_dump),
        ("(v)", "PL-40: line-start records parse exactly as before", _st_v_line_start_regression),
        ("(w)", "PL-40: SIGNOFF text inside a dump's ASCII gutter is never a record", _st_w_gutter_no_recovery),
    ]
    failures = 0
    for label, title, function in checks:
        try:
            ok, detail = function()
        except Exception as exc:              # a crashing check is a failing check
            ok, detail = False, f"raised {type(exc).__name__}: {exc}"
        failures += 0 if ok else 1
        print(f"SELFTEST {label} {'PASS' if ok else 'FAIL'}: {title} -- {detail}")
    if PL9_SOURCE.is_file():
        verdict, hits = check_pl9_text(PL9_SOURCE.read_text(encoding="utf-8", errors="replace"))
        print(f"SELFTEST info: R10-HOST-PL9 on the working tree reads {verdict} "
              f"({len(hits)} line(s) with gapInMS{': ' + ', '.join(map(str, hits)) if hits else ''}); "
              "informational, not asserted")
    print(f"SELFTEST {'PASS' if failures == 0 else 'FAIL'}: {len(checks) - failures} of {len(checks)} checks passed")
    return EXIT_OK if failures == 0 else EXIT_SELFTEST_FAILED


# ---------------------------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------------------------

def main(argv=None):
    parser = argparse.ArgumentParser(
        prog="tools/signoff-collate.py",
        description="Collate a bench visit's SIGNOFF records into a sign-off sheet "
                    f"(design {DESIGN_DOC}).",
        formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--selftest", action="store_true", help="run the built-in checks and exit")
    parser.add_argument("--check-ready", type=int, metavar="N",
                        help="scheduling gate: every OWED cell for visit N must have its test")
    parser.add_argument("--visit", type=int, metavar="N", help="visit number the sheet is for")
    parser.add_argument("--date", metavar="D", help="visit date (names the default --out directory)")
    parser.add_argument("--update", action="store_true",
                        help="rewrite manifest statuses and regenerate SIGNOFF-MANIFEST.md")
    parser.add_argument("--static-tree", action="store_true",
                        help="evaluate static HOST cells (R10-HOST-PL9) against the working tree")
    parser.add_argument("--manifest", default=str(DEFAULT_MANIFEST), metavar="PATH")
    parser.add_argument("--predictions", default=str(DEFAULT_PREDICTIONS), metavar="PATH",
                        help="detection prediction list for R2-HOST-DETDIFF / R2-DETECT-GUARD")
    parser.add_argument("--baseline-detect", default=str(DEFAULT_BASELINE), metavar="PATH",
                        help="baseline detect-phase2 log for R2-HOST-DETDIFF")
    parser.add_argument("--out", metavar="PATH",
                        help="sheet path (default DOCs/analyses/bench/<date>/VISIT-<n>-SIGNOFF.md)")
    parser.add_argument("logs", nargs="*", metavar="log", help="the visit's debug logs, named explicitly")
    args = parser.parse_args(argv)

    collate_args = args.visit is not None or args.date is not None or args.logs or args.update or args.static_tree \
        or args.out is not None
    if args.selftest:
        if args.check_ready is not None or collate_args:
            parser.error("--selftest takes no other options")
        return selftest()
    if args.check_ready is not None:
        if collate_args:
            parser.error("--check-ready takes only --manifest")
        if args.check_ready < 1:
            parser.error("--check-ready needs a visit number >= 1")
        return check_ready(Path(args.manifest), args.check_ready)
    if args.visit is None or args.date is None or not args.logs:
        parser.error("collation needs --visit N, --date D and at least one log")
    if args.visit < 1:
        parser.error("--visit must be >= 1")

    manifest_path = Path(args.manifest)
    try:
        cells = load_manifest(manifest_path)
    except ManifestError as exc:
        print(f"signoff-collate: manifest error: {exc}", file=sys.stderr)
        return EXIT_INPUT
    logs = []
    for name in args.logs:
        path = Path(name)
        if not path.is_file():
            print(f"signoff-collate: input log not found: {name}", file=sys.stderr)
            return EXIT_INPUT
        logs.append(read_log_file(path))

    col = collate(cells, logs, visit=args.visit, static_tree=args.static_tree,
                  predictions_path=Path(args.predictions), baseline_path=Path(args.baseline_detect))
    changes = plan_updates(col, args.visit)
    out_path = Path(args.out) if args.out else (
        REPO_ROOT / "DOCs" / "analyses" / "bench" / args.date / f"VISIT-{args.visit}-SIGNOFF.md")
    sheet = render_sheet(col, args.visit, args.date, manifest_path, args.static_tree, args.update,
                         Path(args.predictions), Path(args.baseline_detect), changes)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(sheet, encoding="utf-8")
    print(f"sheet written: {display_path(out_path)}")
    for log in logs:
        print(f"  log {log.display}: {'COMPLETE' if log.complete else 'TRUNCATED'}")
    for row_n, tasks, _, verdict in col.rows:
        print(f"  row {row_n:>2} (task {', '.join(tasks)}): {verdict}")
    if args.update:
        for cell, _, new_status, ref in changes:
            cell.set_status(new_status, ref)
        write_manifest(manifest_path, cells)
        md_path = manifest_path.with_suffix(".md")
        md_path.write_text(render_manifest_md(cells), encoding="utf-8")
        print(f"manifest updated: {len(changes)} status change(s); view regenerated: {display_path(md_path)}")
    return EXIT_OK


if __name__ == "__main__":
    sys.exit(main())

#!/usr/bin/env python3
"""Print named fields of one record type from a bench log.

Usage:
    tools/logfield.py LOG RECORD FIELD [FIELD ...]

    tools/logfield.py debug_261002-182037.log RC-TEL ms r_hs r_flt
    tools/logfield.py debug_261002-182037.log BM-LOADW l_pct r_pct flips

Two record shapes are read, both by name, never by counted position:
  - positional records (RC-TEL, RC-EVT): the log's own `RC-FIELDS,<RECORD>,...` line names each column;
    a log with no FIELDS line for the record is refused rather than guessed at.
  - labelled records (BM-*): `RECORD,name,value,name,value,...` pairs.
Hex-dump lines the debug terminal interleaves are skipped. A field the record does not carry is an error, so
a misspelt name cannot print an empty column that reads as a value.

Why (2026-10-02): RC-TEL field 48 (r_flt) was counted as r_hs and gave a wrong finding. Reading by name is the fix.
"""

import re
import sys

LINE_RE = re.compile(r"Cog\d\s+([A-Z][A-Z0-9]*-[A-Z0-9-]+),(.*)$")


def records(path):
    """Yield (record name, list of comma fields) for each record line in the log."""
    with open(path, encoding="utf-8", errors="replace") as fh:
        for line in fh:
            match = LINE_RE.search(line.rstrip("\n"))
            if match:
                yield match.group(1), match.group(2).split(",")


def main(argv):
    if len(argv) < 4:
        sys.stderr.write(__doc__)
        return 2
    path, wanted, names = argv[1], argv[2], argv[3:]
    columns = None
    rows = 0
    for name, fields in records(path):
        if name.endswith("-FIELDS") and fields and fields[0] == wanted:
            columns = fields[1:]
            missing = [n for n in names if n not in columns]
            if missing:
                sys.stderr.write(f"{wanted} has no field {', '.join(missing)}; its FIELDS line names: "
                                 f"{','.join(columns)}\n")
                return 1
            continue
        if name != wanted:
            continue
        if columns is not None:
            values = dict(zip(columns, fields))
        else:
            if len(fields) % 2:
                sys.stderr.write(f"{wanted} is not a labelled record and the log has no FIELDS line for it; "
                                 "refusing to read it by position\n")
                return 1
            values = dict(zip(fields[0::2], fields[1::2]))
            missing = [n for n in names if n not in values]
            if missing:
                sys.stderr.write(f"{wanted} has no field {', '.join(missing)}; it carries: "
                                 f"{','.join(fields[0::2])}\n")
                return 1
        print(",".join(f"{n},{values.get(n, '')}" for n in names))
        rows += 1
    if rows == 0:
        sys.stderr.write(f"no {wanted} record in {path}\n")
        return 1
    return 0


if __name__ == "__main__":
    try:
        sys.exit(main(sys.argv))
    except BrokenPipeError:                                 # piped into head: the reader has what it wanted
        sys.stderr.close()
        sys.exit(0)

#!/usr/bin/env python3
"""
release_closure.py -- the object tree of a Spin2 top-level file, for tools/make-release.sh

Usage:  release_closure.py <src-dir> <top.spin2> files   -- every file the top needs, one per line
        release_closure.py <src-dir> <top.spin2> tree    -- the object tree, drawn, for the archive's _README_

A file "needs" what its OBJ blocks name (".spin2" added), what its DAT `file` directives load, and what it
#INCLUDEs. Preprocessor conditionals are honoured: the symbols defined are the ones the top #DEFINEs and
#PRAGMA EXPORTDEFs (so a -D BENCH_CFG branch, never taken in a release build, contributes nothing). Every
file the tree names must exist in <src-dir>; a missing one is an error, never a silent omission.
"""

import os
import re
import sys


def strip_comments(text):
    """Remove Spin2 comments: {{ }} and { } blocks (nesting), and ' to end of line (outside strings)."""
    out, depth, i, n = [], 0, 0, len(text)
    while i < n:
        c = text[i]
        if depth == 0 and c == '"':
            j = text.find('"', i + 1)
            j = n if j < 0 else j + 1
            out.append(text[i:j])
            i = j
            continue
        if c == "{":
            depth += 1
            i += 1
            continue
        if c == "}" and depth > 0:
            depth -= 1
            i += 1
            continue
        if depth == 0 and c == "'":
            j = text.find("\n", i)
            i = n if j < 0 else j
            continue
        if depth == 0 or c == "\n":
            out.append(c)
        i += 1
    return "".join(out)


def active_lines(lines, defined):
    """Yield the lines the preprocessor keeps, given the set of defined symbols (upper case)."""
    stack = []          # per level: [this branch active, some branch already taken]
    for line in lines:
        s = line.strip()
        m = re.match(r"#(\w+)\s*(\w*)", s)
        word = m.group(1).upper() if m else ""
        sym = m.group(2).upper() if m else ""
        outer = all(level[0] for level in stack)
        if word in ("IFDEF", "IFNDEF"):
            hit = (sym in defined) == (word == "IFDEF")
            stack.append([outer and hit, hit])
        elif word in ("ELSEIFDEF", "ELSEIFNDEF"):
            hit = (sym in defined) == (word == "ELSEIFDEF")
            parent = all(level[0] for level in stack[:-1])
            stack[-1] = [parent and hit and not stack[-1][1], stack[-1][1] or hit]
        elif word == "ELSE":
            parent = all(level[0] for level in stack[:-1])
            stack[-1] = [parent and not stack[-1][1], True]
        elif word == "ENDIF":
            stack.pop()
        elif outer:
            yield line


def top_symbols(path):
    """The symbols a top-level file defines for itself (#DEFINE)."""
    return {m.group(1).upper() for m in re.finditer(r"^\s*#DEFINE\s+(\w+)", open(path, encoding="utf-8", errors="replace").read(), re.M | re.I)}


def children(src, fname, defined):
    """(objects, data files) a file names, in source order, duplicates removed."""
    path = os.path.join(src, fname)
    if not os.path.isfile(path):
        sys.exit(f"release_closure: {fname} is needed but not in {src}")
    if not fname.endswith(".spin2"):
        return [], []
    raw = open(path, encoding="utf-8", errors="replace").read().split("\n")
    text = "\n".join(active_lines(raw, defined))
    text = strip_comments(text)
    objs, data, section = [], [], None
    for line in text.split("\n"):
        m = re.match(r"^(CON|VAR|OBJ|PUB|PRI|DAT)\b", line, re.I)
        if m:
            section = m.group(1).upper()
        if section == "OBJ":
            for om in re.finditer(r':\s*"([^"]+)"', line):
                name = om.group(1)
                objs.append(name if name.endswith(".spin2") else name + ".spin2")
        for fm in re.finditer(r'\bFILE\s+"([^"]+)"', line, re.I):
            data.append(fm.group(1))
        for im in re.finditer(r'^\s*#INCLUDE\s+"([^"]+)"', line, re.I):
            name = im.group(1)
            data.append(name if name.endswith(".spin2") else name + ".spin2")
    return list(dict.fromkeys(objs)), list(dict.fromkeys(data))


def walk(src, fname, defined, depth, files, tree):
    files.setdefault(fname, None)
    objs, data = children(src, fname, defined)
    for d in data:
        files.setdefault(d, None)
    kids = data + objs
    for idx, kid in enumerate(kids):
        last = idx == len(kids) - 1
        tree.append((depth, kid, last))
        if kid in objs:
            walk(src, kid, defined, depth + 1, files, tree)


def main():
    if len(sys.argv) != 4 or sys.argv[3] not in ("files", "tree"):
        sys.exit(__doc__)
    src, top, mode = sys.argv[1], sys.argv[2], sys.argv[3]
    defined = top_symbols(os.path.join(src, top))
    files, tree = {}, []
    walk(src, top, defined, 0, files, tree)
    if mode == "files":
        print("\n".join(sorted(files)))
        return
    # Draw the tree: a vertical bar continues under every ancestor that has later siblings.
    print(top)
    open_levels = []
    for depth, name, last in tree:
        open_levels = open_levels[:depth]
        prefix = "".join("│   " if o else "    " for o in open_levels)
        print(prefix + ("└── " if last else "├── ") + name)
        open_levels.append(not last)


if __name__ == "__main__":
    main()

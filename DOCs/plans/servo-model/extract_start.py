"""Extract BM-TRACE cause START traces from a bench log into per-tid rows.

usage: python3 extract_start.py <log> [tid ...]
Prints a header per trace, then k, pos, i, d, e, st for every sample (or a summary with -s).
"""
import re, sys

def num(s):
    if s in ('NA', 'TRUE', 'FALSE'):
        return s
    try:
        return int(s.replace('_', ''))
    except ValueError:
        return s

def rec(line):
    m = re.search(r'(BM-[A-Z0-9-]+),(.*)$', line.strip())
    if not m:
        return None, None
    parts = m.group(2).split(',')
    d = {}
    for a, b in zip(parts[0::2], parts[1::2]):
        d[a] = num(b)
    return m.group(1), d

def load(path):
    traces = {}
    heads = {}
    for line in open(path, errors='replace'):
        kind, d = rec(line)
        if kind == 'BM-TRACE':
            heads[d['tid']] = d
            traces[d['tid']] = []
        elif kind == 'BM-TS' and d.get('tid') in traces:
            traces[d['tid']].append(d)
    return heads, traces

if __name__ == '__main__':
    args = sys.argv[1:]
    summary = '-s' in args
    args = [a for a in args if a != '-s']
    heads, traces = load(args[0])
    want = [int(t) for t in args[1:]]
    for tid, h in heads.items():
        if h.get('cause') != 'START' and not want:
            continue
        if want and tid not in want:
            continue
        rows = traces[tid]
        print(f"## tid {tid} motor {h['motor']} seg {h['seg']} cause {h['cause']} incre {h['incre']} "
              f"period_us {h['period_us']} ramp_inc {h['ramp_inc']} n {len(rows)}")
        if summary:
            continue
        for r in rows:
            print(f"{r['k']:4} pos {r['pos']:5} i {r['i']:5} d {r['d']:6} e {r['e']:5} {r['st']}")

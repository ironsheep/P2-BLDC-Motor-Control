"""Summarise the PL-167 signature from the primary floor logs (read-only).

Desk evidence for DOCs/plans/HOLD-SPEED-UNDER-LOAD-DESIGN.md (sections 1.1 and 7 Q1). Reads the 2026-09-30 floor2
session logs in DOCs/analyses/bench/2026-09-30/floor2/, located relative to this file.

usage: python3 logscan.py [all | trace | rc | obst]
  trace  the leg-7 BM-TS trace (schedule BRISK, the one traced schedule spin) compactly, both wheels
  rc     the FlySky 200 mm/s^2 speed-up window 18:28:55-18:29:00, RC-TEL fields, both wheels
  obst   the obstacle session's two BM-TS stand traces (tid 1 COAST, tid 2 BRAKE): per wheel, every hall tick and
         every crossing of |err| 80 during the stand, the longest run of samples with |err| >= 80 and no tick (the
         driver's blocked count, bFrontProtect()), and the BM-BLOCK verdict lines
  all    trace and rc (the default)
"""
import os
import sys

PART = sys.argv[1] if len(sys.argv) > 1 else 'all'
BASE = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)),
                                     '..', '..', 'analyses', 'bench', '2026-09-30', 'floor2')) + os.sep
AUTO = BASE + 'debug_260930-181811.log'
OBST = BASE + 'debug_260930-182135.log'
RC = BASE + 'debug_260930-182653.log'


def kv(line, tag):
    i = line.find(tag + ',')
    if i < 0:
        return None
    parts = line[i + len(tag) + 1:].strip().split(',')
    d = {}
    for j in range(0, len(parts) - 1, 2):
        d[parts[j]] = parts[j + 1]
    return d


def num(s):
    try:
        return int(s.replace('_', ''))
    except Exception:
        return None


def leg_trace(tid, path=AUTO):
    rows = []
    with open(path) as f:
        for line in f:
            if 'BM-TS,' in line:
                d = kv(line, 'BM-TS')
                if d and d.get('tid') == str(tid):
                    rows.append(d)
    return rows


if PART in ('all', 'trace'):
    print('=== (1) BM-TS tid 7 (schedule BRISK, RIGHT): k, st, pos, i, d, e | o_pos, o_i, o_e, o_st (every 5th + all holds) ===')
    rows = leg_trace(7)
    print('samples', len(rows))
    for r in rows:
        k = num(r['k'])
        e = num(r['e']); oe = num(r['o_e'])
        if (k % 5 == 0) or (e is not None and abs(e) >= 95) or (oe is not None and abs(oe) >= 95):
            print(f"k {k:4} {r['st']:9} pos {r['pos']:>5} i {r['i']:>5} d {r['d']:>6} e {r['e']:>5} | "
                  f"o_pos {r['o_pos']:>5} o_i {r['o_i']:>5} o_e {r['o_e']:>5} o_st {r['o_st']}")

    # duty swing and error statistics over the AT_SPEED / SPIN_UP running part
    run = [r for r in rows if r['st'] in ('AT_SPEED', 'SPIN_UP') and num(r['pos']) is not None and abs(num(r['pos'])) > 20]
    if run:
        ds = [num(r['d']) for r in run]; es = [num(r['e']) for r in run]
        print(f"running samples {len(run)}: duty min {min(ds)} max {max(ds)} mean {sum(ds)/len(ds):.0f}; "
              f"err min {min(es)} max {max(es)} mean {sum(es)/len(es):.1f}; e>=100: {sum(1 for x in es if x >= 100)}")
    print()

if PART in ('all', 'rc'):
    print('=== (2) RC-TEL 18:28:55 - 18:29:00 (VRA 200 mm/s^2 speed-up) ===')
    fields = None
    with open(RC) as f:
        for line in f:
            if 'RC-FIELDS,RC-TEL,' in line:
                fields = line.split('RC-FIELDS,')[1].strip().split(',')[1:]
            if 'RC-TEL,' in line and fields:
                ts = line[1:24]
                if '18:28:55' <= ts[11:19] <= '18:29:00':
                    vals = line.split('RC-TEL,')[1].strip().split(',')
                    if len(vals) != len(fields):
                        continue
                    d = dict(zip(fields, vals))
                    print(f"{ts[11:23]} acc {d['acc_set']:>5} cmd {d['cmd_spd']:>4} path {d['path_pm']:>5} | "
                          f"L pwr {d['l_pwr']:>4} tps {d['l_tps']:>5} ma {d['l_ma']:>5} dcs {d['l_dcs']} err {d['l_err']:>4} duty {d['l_duty']:>6} short {d['l_short']} fol {d['l_fol_pct']:>4} | "
                          f"R tps {d['r_tps']:>5} err {d['r_err']:>4} duty {d['r_duty']:>6} short {d['r_short']} fol {d['r_fol_pct']:>4}")
    print()

if PART == 'obst':
    with open(OBST) as f:
        for line in f:
            for tag in ('BM-BLKBUILD', 'BM-STRACE', 'BM-TRACE-END', 'BM-BLOCK,'):
                if tag in line:
                    print(line[line.find(tag):].strip())
    for tid in (1, 2):
        rows = leg_trace(tid, OBST)
        print(f"=== BM-TS tid {tid} ({'COAST' if tid == 1 else 'BRAKE'}): {len(rows)} samples emitted ===")
        for side, P_, E_, S_ in (('LEFT', 'pos', 'e', 'st'), ('RIGHT', 'o_pos', 'o_e', 'o_st')):
            last_pos = None; last_hi = None; run_n = 0; run_best = 0; run_best_k = None; run_k0 = None
            lines = []
            for r in rows:
                k = num(r['k']); pos = num(r[P_]); e = num(r[E_]); st = r[S_]
                if None in (k, pos, e):
                    continue
                hi = abs(e) >= 80
                tick = last_pos is not None and pos != last_pos
                if tick or (last_hi is not None and hi != last_hi):
                    d = f" d {r['d']}" if side == 'LEFT' else ''
                    lines.append(f"k {k:4} {st:9} pos {pos:5} e {e:5}{d}" + ('  TICK' if tick else '') +
                                 ('  |e|>=80' if hi and not last_hi else ('  |e|<80' if (not hi and last_hi) else '')))
                if hi and not tick and st in ('SPIN_UP', 'AT_SPEED', 'SPIN_DN'):
                    if run_n == 0:
                        run_k0 = k
                    run_n += 1
                    if run_n > run_best:
                        run_best = run_n; run_best_k = (run_k0, k)
                else:
                    run_n = 0
                last_pos = pos; last_hi = hi
            print(f"-- {side}: ticks and |err| 80 crossings (k, state, pos, err)")
            for s in lines:
                print('  ' + s)
            print(f"-- {side}: longest run of samples with |err| >= 80 and no tick: {run_best} samples, k {run_best_k}")

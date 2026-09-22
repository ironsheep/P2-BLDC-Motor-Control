"""Steady-state duty and error per ladder rung, joined by rid, both motors, from BM-RUNG + BM-RUNG2.

usage: python3 rungs.py <log>
"""
import sys
sys.path.insert(0, __file__.rsplit('/', 1)[0])
from extract_start import rec

rung, r2 = {}, {}
for line in open(sys.argv[1], errors='replace'):
    kind, d = rec(line)
    if kind == 'BM-RUNG':
        rung[(d['rid'], d['motor'])] = d
    elif kind == 'BM-RUNG2':
        r2[(d['rid'], d['motor'])] = d
print('motor  rung      incre  rate_x10  duty  duty_pk  err  err_pk  i_x10  inet_x10  duty/|incr|e6')
for key in sorted(rung, key=lambda k: (k[1], k[0])):
    a, b = rung[key], r2.get(key)
    if not b:
        continue
    inc = abs(a['incre'])
    print(f"{a['motor']:6} {a['rung']:3} {a['incre']:12} {a['rate_x10']:8} {b['duty']:6} {b['duty_pk']:7} "
          f"{b['err']:4} {b['err_pk']:6} {b['i_x10']:6} {b['inet_x10']:8}  {b['duty']/inc*1e6:8.1f}")

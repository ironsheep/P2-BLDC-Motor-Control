"""Does the conclusion survive the parameters that were guessed, not fitted?

For each (J, R, Tc, e90) variant: shipped vs ff+integral trim. Reports, per design, the steady duty
swing (pk - mean) at 10e6 and 20e6 and the start's current peak relative to its settled level.
"""
import sys
sys.path.insert(0, __file__.rsplit('/', 1)[0])
import sim_servo as s

def steady(p, inc):
    rows = s.run(p, inc, 4.0)
    tail = rows[len(rows) // 2:]
    d = [r[4] for r in tail]
    e = [r[3] for r in tail]
    return max(d) - sum(d) / len(d), max(e)

def start(p):
    rows = s.run(p, 36_750_000, 1.4)
    i_all = [r[5] for r in rows]
    settled = sum(i_all[-60:]) / 60
    d = [r[4] for r in rows if 0.5 < r[0] < 1.0]
    return max(i_all) / max(settled, 1e-9), max(d) - min(d)

variants = [
    ('fit', {}),
    ('J/2', {'J': 0.003}), ('J*2', {'J': 0.012}),
    ('R/2', {'R': 0.125}), ('R*2', {'R': 0.5}),
    ('e90=52', {'e90': 52.0}), ('e90=60', {'e90': 60.0}),
    ('load Tc*3', {'Tc': 0.6}),
]
designs = [('shipped', {'mode': 'shipped'}),
           ('ff+int', {'mode': 'ffpi', 'kff': 165.0, 'ki': 1 / 64}),
           ('ff+sch', {'mode': 'ffpi', 'kff': 165.0, 'ki': 1 / 32, 'ksched': 1})]
print(f"{'variant':10} {'design':8} | swing@10e6 epk | swing@20e6 epk | start i_pk/settled  duty range 0.5-1s")
for vn, vv in variants:
    for dn, dv in designs:
        p = dict(s.P); p['e90'] = 56.0; p.update(vv); p.update(dv)
        s10, e10 = steady(p, 10e6)
        s20, e20 = steady(p, 20e6)
        r, dr = start(p)
        print(f"{vn:10} {dn:8} | {s10:8.0f} {e10:4} | {s20:8.0f} {e20:4} | {r:8.2f}  {dr:8.0f}")

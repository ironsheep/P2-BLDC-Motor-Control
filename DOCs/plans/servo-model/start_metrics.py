"""The START acceptance metrics, computed the same way on real traces and on the model.

  drop   -- the largest fall of duty from its running maximum, as a fraction of that maximum, between
            duty leaving its floor for good and the ramp reaching target (hunting makes this large;
            a duty that climbs with the ramp keeps it near 0)
  i_ratio -- the start's current peak over the mean current in the last 60 ms of the trace

usage: python3 start_metrics.py log <log>       (every START trace in a bench log)
       python3 start_metrics.py model [k=v ...] (the desk model)
"""
import sys
sys.path.insert(0, __file__.rsplit('/', 1)[0])

def metrics(rows, floor=1600):
    # rows: (t_s, duty, current, at_target)
    leave = 0
    for n, r in enumerate(rows):
        if r[1] <= floor:
            leave = n + 1
    end = next((n for n, r in enumerate(rows) if r[3]), len(rows))
    run_max, drop = 0, 0.0
    for r in rows[leave:end]:
        run_max = max(run_max, r[1])
        if run_max:
            drop = max(drop, (run_max - r[1]) / run_max)
    tail_t = rows[-1][0] - 0.06
    tail = [r[2] for r in rows if r[0] >= tail_t]
    return drop, max(r[2] for r in rows) / (sum(tail) / len(tail))

if sys.argv[1] == 'log':
    from extract_start import load
    heads, traces = load(sys.argv[2])
    for tid, h in heads.items():
        if h.get('cause') != 'START':
            continue
        rows = [(r['k'] * 0.002, r['d'], r['i'] - 0, r['st'] == 'AT_SPEED') for r in traces[tid]]
        d, i = metrics(rows)
        print(f"tid {tid:3} {h['motor']:5} {h['incre']:>12}  drop {d:5.2f}  i_ratio {i:5.2f}")
else:
    import sim_servo as s
    p = s.parse(sys.argv[2:])
    rows = s.run(p, 36_750_000, 1.4)
    rows = [(r[0], r[4], r[5], r[6] >= 36_750_000) for r in rows]
    d, i = metrics(rows)
    print(f"model {' '.join(sys.argv[2:])}: drop {d:5.2f}  i_ratio {i:5.2f}")

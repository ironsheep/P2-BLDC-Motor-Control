#!/usr/bin/env python3
"""pasm_equiv: prove a candidate PASM driver image equivalent to the baseline, frame by frame.

See README.md beside this file. Exit status: 0 every scenario equal and every frame inside its budget;
1 a divergence; 2 a frame-budget failure; 3 the proof could not be completed (a build error, an unmodelled
opcode, an undefined operation, or a scenario the baseline itself cannot run).
"""
import argparse
import multiprocessing as mp
import os
import shutil
import sys
import tempfile
import time

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.dont_write_bytecode = True           # no __pycache__ left in the tree

import p2image       # noqa: E402
import drvenv        # noqa: E402
import equiv         # noqa: E402
import scenarios     # noqa: E402
import initmodel     # noqa: E402

REPO = os.path.dirname(os.path.dirname(HERE))
FRAME_160 = 160_000_000 // 44_000        # 3636 clocks
FRAME_270 = 270_000_000 // 44_000        # 6136 clocks
LONG_EVERY = 10                          # every 10th random seed runs a long scenario

_G = {}


def _worker_init(base_img, cand_img, coverage):
    _G['base'] = base_img
    _G['cand'] = cand_img
    _G['lay'] = drvenv.Layout(base_img)
    _G['con'] = base_img.con
    _G['cov'] = coverage
    _G['named'] = {s.name: s for s in scenarios.named_scenarios(base_img.con)}


def _scenario(name, frames=None, long_frames=None):
    if name.startswith('rand-'):
        seed = int(name[5:])
        n = frames
        if n is None and long_frames and seed % LONG_EVERY == 0:
            n = long_frames
        return scenarios.random_scenario(seed, _G['con'], n)
    return _G['named'][name]


def _job(args):
    name, frames, long_frames = args
    t0 = time.time()
    try:
        sc = _scenario(name, frames, long_frames)
        out = equiv.run_pair(_G['base'], _G['cand'], sc, _G['lay'], _G['con'], coverage=_G['cov'])
        out['budget'] = sc.budget
    except Exception as e:           # a tool failure is reported, never swallowed
        import traceback
        out = {'scenario': name, 'status': 'error', 'detail': 'tool: %s\n%s' % (e, traceback.format_exc()),
               'frames': 0}
    out['seconds'] = time.time() - t0
    return out


def build(args, work):
    pnut = p2image.find_pnut(args.pnut)
    if args.baseline_dir:
        base = p2image.build_image('baseline', os.path.join(work, 'baseline'), pnut, srcdir=args.baseline_dir)
        base_desc = args.baseline_dir
    else:
        base = p2image.build_image('baseline', os.path.join(work, 'baseline'), pnut, git_ref=args.baseline_ref,
                                   repo=REPO)
        base_desc = 'git %s:src/%s' % (args.baseline_ref, p2image.DRIVER_FILE)
    if args.candidate_ref:
        cand = p2image.build_image('candidate', os.path.join(work, 'candidate'), pnut, git_ref=args.candidate_ref,
                                   repo=REPO)
        cand_desc = 'git %s:src/%s' % (args.candidate_ref, p2image.DRIVER_FILE)
    else:
        cdir = args.candidate_dir or os.path.join(REPO, 'src')
        cand = p2image.build_image('candidate', os.path.join(work, 'candidate'), pnut, srcdir=cdir)
        cand_desc = os.path.join(cdir, p2image.DRIVER_FILE)
    return base, cand, base_desc, cand_desc


def main(argv=None):
    ap = argparse.ArgumentParser(prog='run.sh', description=__doc__.split('\n')[0])
    ap.add_argument('--seeds', type=int, default=50, help='random scenarios to run (default 50)')
    ap.add_argument('--seed-base', type=int, default=1, help='first random seed (default 1)')
    ap.add_argument('--scenario', action='append', default=[],
                    help='run only this scenario (a named one, rand-<seed>, or "named" for the edge suite); repeatable')
    ap.add_argument('--no-named', action='store_true', help='skip the named edge suite')
    ap.add_argument('--frames', type=int, default=None, help='frames per random scenario (default: 1500-3500 each)')
    ap.add_argument('--long-frames', type=int, default=20_000,
                    help='frames for every %dth random seed (default 20000; 0 disables)' % LONG_EVERY)
    ap.add_argument('--jobs', type=int, default=max(1, (os.cpu_count() or 2) - 2))
    ap.add_argument('--baseline-ref', default='mem-reduce-start', help='git ref of the baseline (default mem-reduce-start)')
    ap.add_argument('--baseline-dir', default=None, help='take the baseline from this src directory instead of git')
    ap.add_argument('--candidate-dir', default=None, help='the candidate src directory (default: the work tree src/)')
    ap.add_argument('--candidate-ref', default=None, help='take the candidate from this git ref instead')
    ap.add_argument('--work', default=None, help='scratch directory for the builds (default: a new temp dir)')
    ap.add_argument('--guard', type=float, default=0.25, help='frame-budget guard at 160 MHz (default 0.25)')
    ap.add_argument('--pnut', default=None, help='path to pnut-ts')
    ap.add_argument('--coverage', action='store_true', help='report baseline instructions never executed')
    ap.add_argument('--list', action='store_true', help='list the named scenarios and exit')
    args = ap.parse_args(argv)

    own = args.work is None
    work = args.work or tempfile.mkdtemp(prefix='pasm_equiv_')
    try:
        return _run(args, work, own)
    finally:
        if own:
            shutil.rmtree(work, ignore_errors=True)


def _run(args, work, own):
    os.makedirs(work, exist_ok=True)
    real_src = os.path.realpath(os.path.join(REPO, 'src'))
    if os.path.realpath(work).startswith(real_src):
        print('refusing a work directory inside src/')
        return 3
    try:
        base, cand, bdesc, cdesc = build(args, work)
    except p2image.BuildError as e:
        print('BUILD ERROR: %s' % e)
        return 3

    _worker_init(base, cand, args.coverage)
    named = list(_G['named'])
    if args.list:
        for n in named:
            print(n)
        return 0

    names = []
    if args.scenario:
        for s in args.scenario:
            if s == 'named':
                names.extend(named)
            elif s.startswith('rand-') or s in _G['named']:
                names.append(s)
            else:
                print('unknown scenario %r (see --list)' % s)
                return 3
    else:
        if not args.no_named:
            names.extend(named)
        names.extend('rand-%d' % k for k in range(args.seed_base, args.seed_base + args.seeds))

    print('pasm_equiv: baseline  %s' % bdesc)
    print('            candidate %s' % cdesc)
    print('            work dir  %s%s' % (work, ' (removed at exit; --work DIR keeps the builds)' if own else ''))
    for img in (base, cand):
        u = img.usage()
        print('            %-9s cog %d/496, LUT resident %s/512, overlay %s' % (
            img.label, u['cog_used'], u.get('lut_used', '?'), u.get('overlay_used', '?')))
    ptrs_b, unk_b = initmodel.dat_writes_checked(base)
    ptrs_c, unk_c = initmodel.dat_writes_checked(cand)
    print('            init() pointers: baseline %s, candidate %s' % (ptrs_b, ptrs_c))
    if unk_b or unk_c:
        print('INIT MODEL: init()/launchDriver() write driver DAT symbols the model does not fill: %s / %s'
              % (unk_b, unk_c))
        print('            extend tools/pasm_equiv/initmodel.py for this work package')
        return 3
    print('            %d scenarios (%d named, %d random), %d jobs' % (
        len(names), sum(1 for n in names if not n.startswith('rand-')), sum(1 for n in names if n.startswith('rand-')),
        args.jobs))
    sys.stdout.flush()

    t0 = time.time()
    jobs = [(n, args.frames, args.long_frames or None) for n in names]
    results = []

    shown = [0]

    def note(r):
        results.append(r)
        if r['status'] == 'equal':
            return
        shown[0] += 1
        if shown[0] <= 20:
            if r['status'] == 'diverged':
                print('  %-34s DIVERGED at frame %d (%s)' % (r['scenario'], r['div'][0], r['div'][1]))
            else:
                print('  %-34s %s' % (r['scenario'], r['status'].upper()))
        elif shown[0] == 21:
            print('  ... (the rest are counted in RESULT)')
        sys.stdout.flush()
    if args.jobs > 1 and len(jobs) > 1:
        with mp.get_context('fork').Pool(args.jobs, initializer=_worker_init,
                                          initargs=(base, cand, args.coverage)) as pool:
            for r in pool.imap_unordered(_job, jobs, chunksize=1):
                note(r)
    else:
        for j in jobs:
            note(_job(j))
    wall = time.time() - t0
    return report(args, results, wall, base, cand)


def report(args, results, wall, base, cand):
    by = {'equal': [], 'diverged': [], 'error': []}
    for r in results:
        by.setdefault(r['status'], []).append(r)
    frames = sum(r.get('frames', 0) for r in results)
    secs = [r['seconds'] for r in results]
    print('')
    print('RESULT: %d equal, %d diverged, %d error; %d frames compared; %.0f s wall, %.2f s per scenario (mean, '
          'both images), %.3f ms per frame pair' % (len(by['equal']), len(by['diverged']), len(by['error']), frames,
                                                    wall, sum(secs) / max(1, len(secs)),
                                                    1000.0 * sum(secs) / max(1, frames)))
    ends = {}
    for r in results:
        ends[r.get('base_end')] = ends.get(r.get('base_end'), 0) + 1
    print('        baseline run ends: %s' % ', '.join('%s %d' % (k, v) for k, v in sorted(ends.items(), key=str)))

    rc = 0
    if by['error']:
        rc = 3
        for r in by['error'][:10]:
            print('')
            print('ERROR in %s: %s' % (r['scenario'], r.get('detail', '')))
    if by['diverged']:
        rc = 1
        first = sorted(by['diverged'], key=lambda r: (r['div'][0], r['scenario']))
        r = first[0]
        fr, kind, detail, where = r['div']
        print('')
        print('FIRST DIVERGENCE: %s, frame %d (%s)' % (r['scenario'], fr, kind))
        print('    %s' % detail.replace('\n', '\n    '))
        print('    replay: tools/pasm_equiv/run.sh --scenario %s%s' % (
            r['scenario'], (' --candidate-dir %s' % args.candidate_dir) if args.candidate_dir else ''))
        try:
            _context(r['scenario'], fr, where, base, cand, args)
        except Exception as e:
            print('    (context unavailable: %s)' % e)
        if len(first) > 1:
            print('    also diverged: ' + ', '.join('%s@%d(%s)' % (x['scenario'], x['div'][0], x['div'][1])
                                                  for x in first[1:12]) + (' ...' if len(first) > 12 else ''))

    # ---- the frame budget
    worst = {}
    for r in results:
        if not r.get('budget', True):
            continue
        for cls, (bb, cb) in (r.get('windows') or {}).items():
            w = worst.setdefault(cls, [0, 0, None, None])
            if bb > w[0]:
                w[0], w[2] = bb, r['scenario']
            if cb > w[1]:
                w[1], w[3] = cb, r['scenario']
    lim160 = int(FRAME_160 * (1.0 - args.guard))
    print('')
    print('FRAME BUDGET (clocks from the ADC sample to the next wait; worst case hub/CORDIC waits):')
    print('    %-12s %9s %9s   %-22s %-22s' % ('window', 'baseline', 'candidate', 'of 3636 @160 MHz', 'of 6136 @270 MHz'))
    over = []

    def order(k):
        return (k.startswith('stage'), k)
    for cls in sorted(worst, key=order):
        bb, cb = worst[cls][0], worst[cls][1]
        print('    %-12s %9d %9d   %5.1f%% / %5.1f%%        %5.1f%% / %5.1f%%' % (
            cls, bb, cb, 100.0 * bb / FRAME_160, 100.0 * cb / FRAME_160, 100.0 * bb / FRAME_270,
            100.0 * cb / FRAME_270))
        if cb > lim160:
            over.append((cls, cb, worst[cls][3]))
        if cb - bb > 32:
            print('        ^ grew by %d clocks over the baseline (name it in the commit)' % (cb - bb))
    print('    budget: every window <= %d clocks (%d%% guard at 160 MHz)' % (lim160, int(args.guard * 100)))
    stb, stc = {}, {}
    for r in results:
        for k, v in (r.get('stage_base') or {}).items():
            stb[k] = max(stb.get(k, 0), v)
        for k, v in (r.get('stage_cand') or {}).items():
            stc[k] = max(stc.get(k, 0), v)
    if stb:
        print('    planStage clocks (call entry to return), worst seen: ' + ', '.join(
            '%s: %d/%d' % (k, stb[k], stc.get(k, 0)) for k in sorted(k for k in stb if k is not None)))
    if over:
        for cls, cb, sc in over:
            print('BUDGET FAILURE: %s takes %d clocks in %s, over %d' % (cls, cb, sc, lim160))
        if rc == 0:
            rc = 2
    un = {}
    for r in results:
        for name, (where, ep) in (r.get('uninit') or {}).items():
            e = un.setdefault((name, where), [0, ep])
            e[0] += 1
            e[1] = min(e[1], ep)
    if un:
        print('')
        print('FINDING: the baseline reads RES registers before writing them (COGINIT loads them with whatever hub')
        print('    bytes follow the org-0 image, which change with every build). Not compared until written:')
        for (name, where), (n, ep) in sorted(un.items()):
            print('    %-16s first read at %-26s (in frame %d), in %d scenarios' % (name, where, ep, n))
    if args.coverage:
        _coverage(results, base)
    print('')
    print('VERDICT: %s' % {0: 'EQUIVALENT (every scenario equal, every window inside its budget)',
                          1: 'NOT EQUIVALENT', 2: 'BUDGET FAILURE', 3: 'INCOMPLETE'}[rc])
    return rc


def _context(name, frame, where, base, cand, args):
    sc = _scenario(name, args.frames, args.long_frames or None)
    lay, con = _G['lay'], _G['con']
    for img, side in ((base, 'base'), (cand, 'cand')):
        lines, r = equiv.context(img, sc, lay, con, frame, where, side)
        for ln in lines:
            print(ln)
        st = r.env.hub[(lay.status >> 2):(lay.status >> 2) + lay.n_status]
        print('    %s status run at the end of frame %d: %s' % (
            img.label, frame, ' '.join('%d' % (x - (1 << 32) if x >> 31 else x) for x in st)))


def _coverage(results, base):
    """The plan's coverage gate: every instruction executed, every conditional both ways, every branch both ways."""
    cov = set()
    for r in results:
        if r.get('coverage'):
            cov |= r['coverage']
    ob = drvenv.OBJ_BASE + ((-base.driver_hub) % 4)
    print('')
    print('COVERAGE of the baseline image over these scenarios:')
    import p2cog
    for label, start, end in (('cog', 'DRIVER', 'ALL_PINS'), ('LUT resident', 'LUTCODESTART', 'LUTCODEEND'),
                              ('overlay', 'PLANOVLSTART', 'PLANOVLEND')):
        hs, he = base.sym_hub(start), base.sym_hub(end)
        if hs is None or he is None:
            continue
        never, oneway, br1 = [], [], []
        n = nc = nb = 0
        for h in range(hs, he, 4):
            n += 1
            a = ob + h
            w = base.long_at(h)
            if (a, 1) not in cov:
                never.append(base.name_for_hub(h))
            cond = w >> 28
            if w and cond not in (0, 15) and ((a, 0) in cov or (a, 1) in cov):
                nc += 1
                if not ((a, 0) in cov and (a, 1) in cov):
                    oneway.append('%s(%s)' % (base.name_for_hub(h), 'always' if (a, 1) in cov else 'never'))
            nm = p2cog.disasm(w).split()
            nm = nm[1] if nm and nm[0].startswith(('if_', '_ret_')) and len(nm) > 1 else (nm[0] if nm else '')
            if nm in ('tjz', 'tjnz', 'djnz', 'jnct1') and (a, 1) in cov:
                nb += 1
                if not ((a, 2) in cov and (a, 3) in cov):
                    br1.append('%s(%s)' % (base.name_for_hub(h), 'taken' if (a, 2) in cov else 'not taken'))
        print('    %-13s executed %d/%d; never: %s' % (label, n - len(never), n, ', '.join(never) or 'none'))
        print('    %-13s conditionals both ways %d/%d; one way only: %s' % ('', nc - len(oneway), nc,
                                                                            ', '.join(oneway) or 'none'))
        print('    %-13s test-and-branch both ways %d/%d; one way only: %s' % ('', nb - len(br1), nb,
                                                                               ', '.join(br1) or 'none'))


if __name__ == '__main__':
    sys.exit(main())

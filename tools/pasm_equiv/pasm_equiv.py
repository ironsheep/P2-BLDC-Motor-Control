#!/usr/bin/env python3
"""pasm_equiv: prove a candidate PASM driver image equivalent to the baseline, frame by frame.

See README.md beside this file. Exit status: 0 every scenario equal and every frame inside its budget;
1 a divergence; 2 a frame-budget failure (the start frame included); 3 the proof could not be completed (a build
error, an unmodelled opcode, an undefined operation, a scenario the baseline itself cannot run, or, with
--coverage, moved code the candidate covers less than the baseline did).
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
    ap.add_argument('--coverage', action='store_true',
                    help='report coverage of every code image of both builds, and fail (exit 3) if moved code '
                         'lost coverage')
    ap.add_argument('--list', action='store_true', help='list the named scenarios and exit')
    args = ap.parse_args(argv)

    own = args.work is None
    work = args.work or tempfile.mkdtemp(prefix='pasm_equiv_')
    try:
        return _run(args, work, own)
    finally:
        if own:
            shutil.rmtree(work, ignore_errors=True)


def _print_images(img):
    """Every code image the listing shows (p2image.Image.images): the cog image and each LUT image."""
    for k, im in enumerate(img.images()):
        if im.kind == 'cog':
            where = 'org $%03X..$%03X' % (im.org, im.org + im.used - 1)
            how = 'COGINIT'
        else:
            where = 'org $%03X..$%03X' % (im.org, im.org + im.used - 1) if im.used else 'empty'
            how = ('SETQ2 at ' + ', '.join(im.loaders)) if im.loaders else 'no SETQ2 load found'
        print('            %-9s %-14s %3d/%d  %-17s loaded by %s' % (img.label if k == 0 else '', im.title, im.used,
                                                                    im.size, where, how))


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
        _print_images(img)
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
        return (k != equiv.START_WINDOW, k.startswith('stage'), k)
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
    _print_start(results)
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
        if _coverage(results, base, cand) and rc in (0, 2):
            rc = 3
    print('')
    print('VERDICT: %s' % {0: 'EQUIVALENT (every scenario equal, every window inside its budget)',
                          1: 'NOT EQUIVALENT', 2: 'BUDGET FAILURE',
                          3: 'INCOMPLETE' + (' (moved code lost coverage)' if not (by['error'] or by['diverged'])
                                             else '')}[rc])
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


def _print_start(results):
    """The start frame: from the ADC period restart (driveinit's DIRH on the ADC pins) through the rest of the start
    sequence, the SETQ2 load of the run image and the first drive pass, to the first frame wait. The first sample
    after the restart lands one ADC period (one frame) later, so the whole span must fit in a frame."""
    best = {}
    for r in results:
        if not r.get('budget', True) or not r.get('start'):
            continue
        for side, sw in zip(('baseline', 'candidate'), r['start']):
            if sw is not None and (side not in best or sw[0] > best[side][0][0]):
                best[side] = (sw, r['scenario'])
    if not best:
        print('    start frame: not measured (no scenario reached its first drive pass)')
        return
    print('    start frame (ADC period restart -> first frame wait), worst:')
    for side in ('baseline', 'candidate'):
        if side not in best:
            print('        %-9s not measured' % side)
            continue
        (tot, to_pass, lc, ll), sc = best[side]
        print('        %-9s %5d clocks = %s to the drive pass entry (of which %d in a %d-long SETQ2 LUT load) + %s '
              'first pass to the wait; %.1f%% of 3636 @160 MHz, %.1f%% of 6136 @270 MHz  [%s]' % (
                  side, tot, '?' if to_pass is None else '%d' % to_pass, lc, ll,
                  '?' if to_pass is None else '%d' % (tot - to_pass), 100.0 * tot / FRAME_160,
                  100.0 * tot / FRAME_270, sc))


# ---------------------------------------------------------------------------------------------- coverage
_BR_ABS = {0x6C, 0x6D, 0x70, 0x71, 0x72, 0x73}      # JMP/CALL/CALLD #A (p2kbPasm2Jmp, p2kbPasm2Call, p2kbPasm2Calld)
_BR_S = {0x59, 0x5A, 0x5B, 0x5C, 0x5E}              # CALLD/CALLPA/DJNZ../TJZ../JNCT1 with a relative #S
_ALT = {0x4A, 0x4B, 0x4C}                           # ALTx: a #S is a register base


def _union(results, key):
    cov = set()
    for r in results:
        if r.get(key):
            cov |= r[key]
    return cov


def _obj_base(img):
    return drvenv.OBJ_BASE + ((-img.driver_hub) % 4)


def _image_rows(img, cov):
    """Per code image: (image, longs, never, conditionals seen, one-way, test-and-branches seen, one-way)."""
    import p2cog
    ob = _obj_base(img)
    rows = []
    for im in img.images():
        never, oneway, br1 = [], [], []
        n = nc = nb = 0
        for h in range(im.hub_start, im.hub_end, 4):
            n += 1
            a = ob + h
            w = img.long_at(h)
            if (a, 1) not in cov:
                never.append(img.name_for_hub(h))
            cond = w >> 28
            if w and cond not in (0, 15) and ((a, 0) in cov or (a, 1) in cov):
                nc += 1
                if not ((a, 0) in cov and (a, 1) in cov):
                    oneway.append('%s(%s)' % (img.name_for_hub(h), 'always' if (a, 1) in cov else 'never'))
            nm = p2cog.disasm(w).split()
            nm = nm[1] if nm and nm[0].startswith(('if_', '_ret_')) and len(nm) > 1 else (nm[0] if nm else '')
            if nm in ('tjz', 'tjnz', 'djnz', 'jnct1') and (a, 1) in cov:
                nb += 1
                if not ((a, 2) in cov and (a, 3) in cov):
                    br1.append('%s(%s)' % (img.name_for_hub(h), 'taken' if (a, 2) in cov else 'not taken'))
        rows.append((im, n, never, nc, oneway, nb, br1))
    return rows


class _Names:
    """Names for the operands of one image's code, for matching an instruction to its moved copy in the other.

    A register is the set of names at its address (a C1 alias carries two); a branch target the set of code labels,
    global or local, at its org address. Two operands match when their sets share a name, so an instruction reading
    a register that was aliased, or jumping to a routine that moved, still matches."""

    def __init__(self, img):
        self.img = img
        self.code = {}            # (image name, org) -> {label}
        self.globals = {}         # name -> hub, global labels on a code long
        for name, (org, hub, typ) in img.dat.items():
            if org is None or typ == 'DAT_LONG_RES':
                continue
            im = img.image_at_hub(hub)
            if im is None or im.org_of(hub) != org:
                continue
            self.code.setdefault((im.name, org), set()).add(name)
            if '.' not in name:
                self.globals[name] = hub
        self.lut = [im for im in img.images() if im.kind == 'lut']

    def reg(self, a):
        """A register's names: its own labels, LABEL+k for every label 1..3 longs below it (an element of a short
        array, such as adc_modes+1, keeps that name when a C1 alias gives its long a label of its own), and, for a
        long with no label, LABEL+k from the nearest label below it."""
        if a >= 0x1F0:
            return frozenset(['$%03X' % a])
        names = self.img.cog_names
        s = set(names.get(a, ()))
        for k in range(1, 4):
            for x in names.get(a - k, ()):
                s.add('%s+%d' % (x, k))
        if not names.get(a):
            for k in range(1, a + 1):
                if names.get(a - k):
                    s.update('%s+%d' % (x, k) for x in names[a - k])
                    break
        return frozenset(s) if s else frozenset(['$%03X' % a])

    def target(self, im, t):
        """A LUT target is named from EVERY LUT image: which image is loaded at the time of the branch is a run-time
        fact (resident code calls into an overlay loaded over the start image at the same addresses)."""
        if t < 0x200:
            s = self.code.get(('cog', t))
        else:
            s = set()
            for li in self.lut:
                s |= self.code.get((li.name, t), set())
        return frozenset(s) if s else frozenset(['@$%03X' % t])


def _desc(nm, im, h):
    """(core bits, D operand, S operand) of the long at hub h: a register or a target as a name set, else a value."""
    import p2cog
    img = nm.img
    w = img.long_at(h)
    if w == 0:
        return (0, None, None)
    pc = im.org_of(h)
    op = (w >> 21) & 0x7F
    if op in _BR_ABS:
        a = w & 0xF_FFFF
        t = ((pc + 1 + (p2cog.sx(a, 20) >> 2)) & 0xF_FFFF) if (w >> 20) & 1 else a
        return (w >> 21, None, nm.target(im, t))
    if op >= 0x78:                                   # AUGS/AUGD: the value itself
        return (w, None, None)
    fn = p2cog._OPS.get(op)
    dec = fn(w) if fn else None
    if dec is None:
        return (w, None, None)
    # fields that select an operation rather than a register are compared as values: the D-only group's S
    #  (p2kbPasm2Setq ...), and D for POLLx/WAITx, MODCZ and JNCT1's event code
    if op == 0x6B:
        d = dec.d if (dec.imm_d or dec.s in (0x024, 0x06F)) else nm.reg(dec.d)
        return (w >> 18, d, dec.s)
    d = dec.d if (dec.imm_d or op == 0x5E) else nm.reg(dec.d)
    if dec.imm_s and op in _BR_S:
        s = nm.target(im, (pc + 1 + p2cog.sx(dec.s, 9)) & 0xF_FFFF)
    elif dec.imm_s and op in _ALT:
        s = nm.reg(dec.s)
    else:
        s = dec.s if dec.imm_s else nm.reg(dec.s)
    return (w >> 18, d, s)


def _same(x, y):
    if x[0] != y[0]:
        return False
    for u, v in ((x[1], y[1]), (x[2], y[2])):
        if isinstance(u, frozenset) and isinstance(v, frozenset):
            if not (u & v):
                return False
        elif u != v:
            return False
    return True


def _routines(nm, common):
    """{routine: [(image, hub)]}: each image's code longs, grouped under the last label both images carry."""
    img = nm.img
    at = {}
    for name in common:
        at.setdefault(nm.globals[name], []).append(name)
    out = {}
    for im in img.images():
        cur = None
        for h in range(im.hub_start, im.hub_end, 4):
            here = sorted(n for n in at.get(h, ()) if img.dat[n][0] == im.org_of(h))
            if here:
                cur = here[0]
            if cur is not None:
                out.setdefault(cur, []).append((im, h))
    return out


def _align(a, b):
    """The longest common subsequence of two descriptor lists under _same: the index pairs."""
    n, m = len(a), len(b)
    L = [[0] * (m + 1) for _ in range(n + 1)]
    for i in range(n - 1, -1, -1):
        Li, Li1 = L[i], L[i + 1]
        ai = a[i]
        for j in range(m - 1, -1, -1):
            Li[j] = Li1[j + 1] + 1 if _same(ai, b[j]) else max(Li1[j], Li[j + 1])
    i = j = 0
    pairs = []
    while i < n and j < m:
        if _same(a[i], b[j]) and L[i][j] == L[i + 1][j + 1] + 1:
            pairs.append((i, j))
            i += 1
            j += 1
        elif L[i + 1][j] >= L[i][j + 1]:
            i += 1
        else:
            j += 1
    return pairs


def moved_code(base, cand, bcov, ccov):
    """Match every baseline instruction to its copy in the candidate, wherever the candidate put it: routine by
    routine (the code under each global label both images carry on a code long), by the longest common subsequence
    of instructions whose opcode, condition, flags and immediates are equal and whose registers and branch targets
    share a name. A matched instruction was MOVED; an unmatched one was changed or removed by the work package.
    Returns [(routine, base hub, cand hub, executed b, executed c, both-ways b, both-ways c)]."""
    nb, nc = _Names(base), _Names(cand)
    common = set(nb.globals) & set(nc.globals)
    rb, rc = _routines(nb, common), _routines(nc, common)
    obb, obc = _obj_base(base), _obj_base(cand)
    out = []

    def ways(cov, a, w):
        cond = w >> 28
        if w and cond not in (0, 15):
            return (a, 0) in cov and (a, 1) in cov
        op = (w >> 21) & 0x7F
        if op in (0x5B, 0x5C, 0x5E):
            return (a, 2) in cov and (a, 3) in cov
        return None
    for r in sorted(set(rb) & set(rc)):
        la = [_desc(nb, im, h) for im, h in rb[r]]
        lb = [_desc(nc, im, h) for im, h in rc[r]]
        for i, j in _align(la, lb):
            hb, hc = rb[r][i][1], rc[r][j][1]
            ab, ac = obb + hb, obc + hc
            wb, wc = base.long_at(hb), cand.long_at(hc)
            out.append((r, hb, hc, (ab, 1) in bcov, (ac, 1) in ccov, ways(bcov, ab, wb), ways(ccov, ac, wc)))
    return out


def _coverage(results, base, cand):
    """The plan's coverage gate, for both images: every instruction executed, every conditional both ways, every
    test-and-branch both ways; then moved code, which must be covered in the candidate at least as the baseline
    covered it. Returns True when moved code lost coverage (the run is then INCOMPLETE, exit 3)."""
    bcov, ccov = _union(results, 'coverage'), _union(results, 'cand_coverage')
    rows = {}
    for img, cov in ((base, bcov), (cand, ccov)):
        rows[img.label] = _image_rows(img, cov)
    print('')
    print('COVERAGE over these scenarios (every code image, both builds):')
    print('    %-9s %-14s %13s %17s %17s' % ('', 'image', 'executed', 'cond. both ways', 'branch both ways'))
    for img in (base, cand):
        for k, (im, n, never, nc, oneway, nb, br1) in enumerate(rows[img.label]):
            print('    %-9s %-14s %6d/%-6d %8d/%-8d %8d/%-8d' % (img.label if k == 0 else '', im.title,
                                                               n - len(never), n, nc - len(oneway), nc,
                                                               nb - len(br1), nb))
    for img in (base, cand):
        print('    %s:' % img.label)
        for im, n, never, nc, oneway, nb, br1 in rows[img.label]:
            print('      %-14s never: %s' % (im.title, ', '.join(never) or 'none'))
            print('      %-14s conditionals one way only: %s' % ('', ', '.join(oneway) or 'none'))
            print('      %-14s test-and-branch one way only: %s' % ('', ', '.join(br1) or 'none'))
    mv = moved_code(base, cand, bcov, ccov)
    eb = sum(1 for x in mv if x[3])
    ec = sum(1 for x in mv if x[4])
    lost = [x for x in mv if x[3] and not x[4]]
    wlost = [x for x in mv if x[5] and x[6] is False]
    nb_total = sum(r[1] for r in rows[base.label])
    print('    moved code: %d of the baseline\'s %d code longs matched in the candidate (the rest changed or removed);'
          % (len(mv), nb_total))
    matched = set(x[1] for x in mv)
    gone = [base.name_for_hub(h) for im in base.images() for h in range(im.hub_start, im.hub_end, 4)
            if h not in matched]
    print('      not matched (changed or removed; not checked here): %s' % (
        ', '.join(gone[:40]) + (' ...' if len(gone) > 40 else '') if gone else 'none'))
    print('      executed: baseline %d, candidate %d; executed in the baseline only: %s' % (
        eb, ec, ', '.join('%s -> %s' % (base.name_for_hub(x[1]), cand.name_for_hub(x[2])) for x in lost[:40])
        or 'none'))
    print('      both ways in the baseline, one way in the candidate: %s' % (
        ', '.join('%s -> %s' % (base.name_for_hub(x[1]), cand.name_for_hub(x[2])) for x in wlost[:40]) or 'none'))
    if lost or wlost:
        print('COVERAGE FAILURE: moved code the candidate covers less than the baseline did (%d instructions never '
              'executed, %d decisions one way only); the proof does not reach it' % (len(lost), len(wlost)))
        return True
    return False


if __name__ == '__main__':
    sys.exit(main())

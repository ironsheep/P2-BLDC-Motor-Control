"""Run one scenario on the baseline image, then on the candidate, and compare them at every frame boundary.

Compared at each boundary k (the cog observing the k-th ADC sample), for the frame that just ended:
  * every hub long the cog wrote, in order (address and value); the two status longs that carry a clock count
    (loop_ticks, loop_ctcks) are compared as writes but not by value -- they are timing, reported separately;
  * every pin operation (WRPIN/WXPIN/WYPIN/AKPIN/DIR*/OUT*/DRV*/FLT*), in order, with its pins and value;
  * every QROTATE/QVECTOR input (the model's trig is not bit-exact silicon, so equal inputs are what is proved);
  * ADDCT1's target relative to the pass's entry (the next pass's schedule), COGATN strobes, the start ATN;
and, at the boundary itself:
  * every register that is LIVE at k on the baseline's own path (its first access after k is a read), found
    in the candidate by NAME, so a register that moved (a C1/C7 alias) is checked at its new address; and C/Z
    when live. Liveness is computed from the baseline run, never assumed. Registers the cog loads from CT
    (GETCT and ADDCT1 destinations) are timing, not behaviour, and are excluded.
"""
import array
import bisect
import collections

from p2cog import Cog, EmuError, Unmodelled, Undefined, Parked, M32, disasm
from drvenv import Env, FrameLog

WATCHDOG_INSTR = 400_000       # no frame boundary in this many instructions: the run is stuck


class Divergence(Exception):
    def __init__(self, frame, kind, detail, where=None):
        super().__init__('%s at frame %d' % (kind, frame))
        self.frame = frame
        self.kind = kind
        self.detail = detail
        self.where = where            # ('hub'|'pins'|'qin'|'events', base index, cand index) or ('reg', a, ca)


class Tracker:
    """The kind of the first access to each register (and flag) after each boundary: 0 read (live), 1 write.

    Events are kept run-length merged: a first access of the same kind as the previous one only moves that
    event's epoch forward, since liveness at boundary k is the kind of the first event at or after k."""

    def __init__(self, res_regs=(), cog=None):
        self.epoch = 0
        self.last = [-1] * 512
        self.events = [[] for _ in range(512)]
        self.written = bytearray(512)
        self.first_write = [None] * 512
        self.flast = [-1, -1]
        self.fevents = [[], []]
        self.res = bytearray(512)          # RES registers: COGINIT fills them with whatever hub bytes follow the image
        for a in res_regs:
            self.res[a] = 1
        self.cog = cog
        self.uninit = {}                   # register -> (pc, epoch) of its first read before any write

    def _add(self, evs, kind):
        if evs and evs[-1][1] == kind:
            evs[-1] = (self.epoch, kind)
        else:
            evs.append((self.epoch, kind))

    def read(self, a):
        if self.last[a] != self.epoch:
            self.last[a] = self.epoch
            self._add(self.events[a], 0)
            if not self.written[a] and self.res[a] and a not in self.uninit:
                self.uninit[a] = (self.cog.last_pc, self.epoch)

    def write(self, a):
        if not self.written[a]:
            self.written[a] = 1
            self.first_write[a] = self.epoch
        if self.last[a] != self.epoch:
            self.last[a] = self.epoch
            self._add(self.events[a], 1)

    def flag_read(self, f):
        if self.flast[f] != self.epoch:
            self.flast[f] = self.epoch
            self._add(self.fevents[f], 0)

    def flag_write(self, f):
        if self.flast[f] != self.epoch:
            self.flast[f] = self.epoch
            self._add(self.fevents[f], 1)


def _switches(items, nb):
    """{k: [(item, becomes_live)]}: where each item's liveness changes, boundaries 1..nb."""
    sw = collections.defaultdict(list)
    for item, evs in items:
        prev_ep = 0
        state = False
        for ep, kind in evs:
            if ep < 1:
                prev_ep = ep
                continue
            live = (kind == 0)
            k0 = max(prev_ep + 1, 1)
            if k0 <= nb and live != state:
                sw[k0].append((item, live))
                state = live
            prev_ep = ep
            if ep >= nb:
                break
        if state and prev_ep + 1 <= nb:
            sw[prev_ep + 1].append((item, False))
    return sw


class RunResult:
    def __init__(self):
        self.logs = []
        self.snaps = [None]           # index k -> (register changes since boundary k-1, C, Z)
        self.cog0 = None
        self.end = None
        self.end_detail = ''
        self.frames = 0
        self.stage_clocks = {}        # stage number -> max clocks inside planStage
        self.instr = 0
        self.timing_regs = set()
        self.trace = None
        self.coverage = None


class Runner:
    def __init__(self, img, scen, layout, con, track=False, compare=None, stop_at=None, trace=0, coverage=False,
                 trace_ic=False):
        self.img = img
        self.scen = scen
        self.lay = layout
        self.con = con
        self.track = track
        self.compare = compare
        self.stop_at = stop_at
        self.trace = trace
        self.coverage = coverage
        self.trace_ic = trace_ic

    def _coginit(self, env, cog):
        img = self.img
        base = (env.obj_base + img.driver_hub) >> 2
        for k in range(0x1F8):
            cog.cog[k] = env.hub[base + k]
        cog.cog[0x1F8] = self.lay.launch                    # PTRA = @pinbase
        cog.cog[0x1F9] = env.obj_base + img.driver_hub      # PTRB = the start address (p2kbArchPtraRegister)
        cog.pc = 0

    def run(self):
        img = self.img
        scen = self.scen
        lay = self.lay
        res = RunResult()
        env = Env(img, scen, lay, self.con)
        cog = Cog(env, ct0=scen.ct0)
        env.cog = cog
        env.t_boundary = cog.ct
        env.trace_ic = self.trace_ic
        self._coginit(env, cog)
        res.cog0 = list(cog.cog)
        prev = list(cog.cog)
        tr = None
        if self.track:
            resv = [a for n, (c, h, t) in img.dat.items() if t == 'DAT_LONG_RES' and c is not None and c < 0x200
                    for a in [c]]
            first_res = min(resv) if resv else 0x1F8
            tr = Tracker(range(first_res, 0x1F8), cog)
        cog.track = tr
        if self.trace:
            cog.trace = collections.deque(maxlen=self.trace)
        cov = set() if self.coverage else None
        cog.cov = cov
        cog.cog_src_base = env.obj_base + img.driver_hub
        watch = {}
        for sym, tag in (('DRVMOTOR', 1), ('PLANSTAGE', 2), ('DRIVERRELEASE', 3)):
            a = img.sym_addr(sym)
            if a is not None:
                watch[a] = (tag, img.sym_hub(sym))
        ps_reg = img.sym_cog('PLAN_STAGE')
        drive_pin = scen.cfg.base + 9
        mask = lay.timing_status
        n_frames = scen.n_frames if self.stop_at is None else min(scen.n_frames, self.stop_at)
        stage_on = None
        since = 0
        cmp = self.compare
        keep = self.trace_ic
        try:
            while True:
                pc = cog.pc
                w = watch.get(pc)
                if w is not None:
                    tag, hub = w
                    if pc < 0x200 or cog.lut_src[pc - 0x200] == env.obj_base + hub:
                        if tag == 1:
                            env.pass_ct0 = cog.ct
                            env.log.tags.add('pass')
                        elif tag == 2:
                            st = cog.cog[ps_reg] if ps_reg is not None else None
                            env.log.tags.add('stage')
                            env.log.stage = st
                            stage_on = (cog.ct, len(cog.stack), st)
                        else:
                            env.log.tags.add('release')
                cog.step()
                if stage_on is not None and len(cog.stack) < stage_on[1]:
                    d = cog.ct - stage_on[0]
                    s = stage_on[2]
                    if d > res.stage_clocks.get(s, 0):
                        res.stage_clocks[s] = d
                    stage_on = None
                since += 1
                if env.boundary_pending:
                    env.boundary_pending = False
                    since = 0
                    env.frame += 1
                    k = env.frame
                    env.logs.append(env.log.freeze(mask, drive_pin, keep))
                    env.log = FrameLog()
                    if cmp is not None:
                        cmp(k, env, cog)
                    else:
                        delta = array.array('I')
                        for i, (v, p) in enumerate(zip(cog.cog, prev)):
                            if v != p:
                                delta.append(i)
                                delta.append(v)
                                prev[i] = v
                        res.snaps.append((delta, cog.C, cog.Z))
                    if tr is not None:
                        tr.epoch = k
                    if k >= n_frames:
                        res.end = 'frames'
                        break
                    env.begin_frame(k)
                elif since > WATCHDOG_INSTR:
                    raise EmuError('no frame boundary in %d instructions (PC $%03X)' % (WATCHDOG_INSTR, cog.pc))
        except Parked as e:
            res.end = 'parked'
            res.end_detail = str(e)
            env.logs.append(env.log.freeze(mask, drive_pin, keep))
            if cmp is not None:
                cmp(env.frame + 1, env, cog, final=True)
        except (Unmodelled, Undefined, EmuError) as e:
            res.end = 'error'
            res.end_detail = '%s: %s (%s at $%03X, frame %d)' % (type(e).__name__, e,
                                                                 pc_name(img, env, cog, cog.last_pc),
                                                                 cog.last_pc, env.frame)
            env.logs.append(env.log.freeze(mask, drive_pin, keep))
        res.logs = env.logs
        res.frames = env.frame
        res.instr = cog.icount
        res.timing_regs = set(cog.timing_regs)
        res.tracker = tr
        res.trace = cog.trace
        res.coverage = cov
        res.env = env
        res.cog = cog
        return res


def pc_name_static(img, pc):
    """A name for a cog-RAM PC, or the LUT address (the image loaded there is not known outside a run)."""
    if pc < 0x200:
        return img.name_for_hub(img.driver_hub + 4 * pc)
    return 'LUT$%03X' % pc


def pc_name(img, env, cog, pc):
    if pc < 0x200:
        return img.name_for_hub(img.driver_hub + 4 * pc)
    src = cog.lut_src[pc - 0x200]
    if src is None:
        return 'LUT$%03X' % pc
    return img.name_for_hub(src - env.obj_base)


# ====================================================================== comparison
class Plan:
    """What to compare, derived once per scenario from the baseline run."""

    def __init__(self, base_img, cand_img, bres, layout):
        self.base = base_img
        self.cand = cand_img
        self.bres = bres
        self.lay = layout
        nb = len(bres.snaps) - 1
        tr = bres.tracker
        timing = set(bres.timing_regs)
        # a clock count must reach the hub only through the two status longs the layout names as timing
        du = base_img.sym_cog('DRIVE_U_')
        for r in timing:
            if du is not None and du <= r < du + layout.n_status:
                a = layout.status + 4 * (r - du)
                if a not in layout.timing_status:
                    raise EmuError('a CT-derived register (%s) is copied to status long %d, not a clock-count long'
                                   % ('/'.join(base_img.cog_names.get(r, ['$%03X' % r])), r - du))
        self.timing_names = sorted(n for r in timing for n in base_img.cog_names.get(r, []))
        # every written baseline cog address -> the candidate address(es) holding the same named register
        addrs = sorted(set(base_img.cog_sym.values()))
        self.map = {}
        self.names = {}
        for a in range(0x1F8):
            if not tr.written[a] or a in timing:
                continue
            owners = list(base_img.cog_names.get(a, []))
            off = 0
            if not owners:
                i = bisect.bisect_right(addrs, a) - 1
                if i < 0:
                    continue
                a0 = addrs[i]
                owners = base_img.cog_names[a0]
                off = a - a0
            cands = []
            for n in owners:
                ca = cand_img.sym_cog(n)
                if ca is not None:
                    cands.append(ca + off)
            self.map[a] = sorted(set(cands))
            self.names[a] = '/'.join(owners) + ('+%d' % off if off else '')
        for a, n in ((0x1F8, 'PTRA'), (0x1F9, 'PTRB')):
            self.map[a] = [a]
            self.names[a] = n
        self.switch = _switches([(a, tr.events[a]) for a in self.map], nb)
        self.fswitch = _switches([(0, tr.fevents[0]), (1, tr.fevents[1])], nb)
        # a register is compared only once the baseline has written it: before that it holds COGINIT's copy of
        #  whatever hub bytes follow the org-0 image, which moves with every build (reported as a finding instead)
        self.first_write = list(tr.first_write)
        self.first_write[0x1F8] = self.first_write[0x1F9] = -1
        self.uninit = {'/'.join(base_img.cog_names.get(a, ['$%03X' % a])): (pc_name_static(base_img, pc), ep)
                       for a, (pc, ep) in tr.uninit.items()}


def make_comparator(plan, clog):
    bres = plan.bres
    blogs = bres.logs
    live = set()
    flive = set()
    bcur = list(bres.cog0)
    state = {'k': 0}

    def cmp(k, env, cog, final=False):
        fi = k - 1
        if fi >= len(blogs):
            raise Divergence(k, 'extra-frames', 'the candidate reached frame %d; the baseline ended at %d (%s)'
                             % (k, len(blogs), bres.end))
        bl = blogs[fi]
        cl = env.logs[fi]
        if bl.blob != cl.blob:
            _explain(fi, bl, cl, plan)
        clog.append((bl.busy, cl.busy, bl.overrun, cl.overrun, frozenset(bl.tags), bl.stage))
        if final:
            if bres.end != 'parked' or len(blogs) != len(env.logs):
                raise Divergence(fi, 'end', 'the candidate parked in frame %d; the baseline ended %s after %d frames'
                                 % (fi, bres.end, len(blogs)))
            return
        if k >= len(bres.snaps):
            raise Divergence(fi, 'extra-frames', 'the baseline has no boundary %d (it ended %s)' % (k, bres.end))
        # bring the baseline's registers and live sets to boundary k
        while state['k'] < k:
            state['k'] += 1
            kk = state['k']
            d = bres.snaps[kk][0]
            for j in range(0, len(d), 2):
                bcur[d[j]] = d[j + 1]
            for a, on in plan.switch.get(kk, ()):
                if on:
                    live.add(a)
                else:
                    live.discard(a)
            for f, on in plan.fswitch.get(kk, ()):
                if on:
                    flive.add(f)
                else:
                    flive.discard(f)
        _, bc, bz = bres.snaps[k]
        fw = plan.first_write
        for a in live:
            if fw[a] is None or fw[a] >= k:
                continue
            bv = bcur[a]
            homes = plan.map[a]
            if not homes:
                raise Divergence(fi, 'register-missing', 'register %s is live at boundary %d but the candidate '
                                 'has no symbol for it' % (plan.names[a], k), ('reg', a, None))
            for ca in homes:
                cv = cog.cog[ca]
                if cv != bv:
                    raise Divergence(fi, 'register', 'register %s, live at boundary %d: baseline $%08X (%d) at $%03X, '
                                     'candidate $%08X (%d) at $%03X'
                                     % (plan.names[a], k, bv, _s(bv), a, cv, _s(cv), ca), ('reg', a, ca))
        for f in flive:
            bv = bc if f == 0 else bz
            cv = cog.C if f == 0 else cog.Z
            if bv != cv:
                raise Divergence(fi, 'flag', '%s live at boundary %d: baseline %d, candidate %d' % ('CZ'[f], k, bv, cv),
                                 ('flag', f, f))

    return cmp


def _explain(fi, bl, cl, plan):
    """The two frames' blobs differ: find and describe the first difference."""
    bh, bp, bq, be = bl.lists()
    ch, cp, cq, ce = cl.lists()
    if bh != ch:
        txt, i = _first_diff(bh, ch, 'hub write', lambda x: '$%05X <- $%08X (%d)%s' % (x[0], x[1], _s(x[1]),
                                                                                      _hub_name(x[0], plan)))
        raise Divergence(fi, 'hub-writes', txt, ('hub', i, i))
    if bp != cp:
        txt, i = _first_diff(bp, cp, 'pin op', _fmt_pin)
        raise Divergence(fi, 'pin-writes', txt, ('pins', i, i))
    if bq != cq:
        txt, i = _first_diff(bq, cq, 'qrotate/qvector input', repr)
        raise Divergence(fi, 'cordic-inputs', txt, ('qin', i, i))
    txt, i = _first_diff(be, ce, 'event', repr)
    raise Divergence(fi, 'events', txt, ('events', i, i))


def _hub_name(x, plan):
    lay = plan.lay
    if lay.status <= x < lay.status + 4 * lay.n_status:
        k = (x - lay.status) // 4
        n = [nm for nm, i in lay.sidx.items() if i == k]
        return '  [status long %d: %s]' % (k, '/'.join(n))
    if x == lay.fault:
        return '  [fault]'
    if x == lay.target_incre:
        return '  [targetIncre]'
    return ''


def _s(v):
    return v - (1 << 32) if v & 0x8000_0000 else v


def _fmt_pin(p):
    name, pins, val = p
    ps = ','.join(str(x) for x in pins)
    return '%s pins[%s]%s' % (name, ps, '' if val is None else ' = $%08X (%d)' % (val, _s(val)))


def _first_diff(a, b, what, fmt):
    n = min(len(a), len(b))
    for i in range(n):
        if a[i] != b[i]:
            return ('%s #%d of the frame differs:\n  baseline : %s\n  candidate: %s' % (what, i, fmt(a[i]), fmt(b[i]))), i
    if len(a) != len(b):
        longer, who = (a, 'baseline') if len(a) > len(b) else (b, 'candidate')
        return ('%s count differs: baseline %d, candidate %d; the first extra one (%s): %s'
                % (what, len(a), len(b), who, fmt(longer[n]))), n
    return 'no difference', 0


# ====================================================================== the frame budget
def classify(tags, stage):
    """The budget window a frame belongs to, or None (release, an adversarial CT1 schedule)."""
    if 'release' in tags or 'ct1short' in tags:
        return None
    if 'pass' in tags and 'stage' in tags:
        return 'pass+stage'
    if 'pass' in tags:
        return 'pass frame'
    if 'stage' in tags:
        return 'stage %s' % stage
    return 'frame work'


def budget_windows(clog):
    """{window: [baseline max, candidate max]} over the frames after the first drive pass (whose frame carries
    the end of the start sequence)."""
    worst = {}
    seen = 0
    for bb, cb, bo, co, tags, stage in clog:
        if 'pass' in tags:
            seen += 1
            if seen == 1:
                continue
        if not seen:
            continue
        cls = classify(tags, stage)
        if cls is None:
            continue
        w = worst.setdefault(cls, [0, 0])
        if bb is not None and bb > w[0]:
            w[0] = bb
        if cb is not None and cb > w[1]:
            w[1] = cb
    return worst


# ====================================================================== one scenario, both images
def run_pair(base_img, cand_img, scen, layout, con, coverage=False):
    """Returns a dict: status ('equal'|'diverged'|'error'), details, timing."""
    b = Runner(base_img, scen, layout, con, track=True, coverage=coverage).run()
    out = {'scenario': scen.name, 'frames': b.frames, 'base_end': b.end, 'base_instr': b.instr,
           'stage_base': b.stage_clocks, 'coverage': b.coverage}
    if b.end == 'error':
        out['status'] = 'error'
        out['detail'] = 'baseline: ' + b.end_detail
        return out
    try:
        plan = Plan(base_img, cand_img, b, layout)
    except EmuError as e:
        out['status'] = 'error'
        out['detail'] = 'baseline: %s' % e
        return out
    out['uninit'] = plan.uninit
    clog = []
    cmp = make_comparator(plan, clog)
    try:
        c = Runner(cand_img, scen, layout, con, compare=cmp).run()
    except Divergence as d:
        out['status'] = 'diverged'
        out['div'] = (d.frame, d.kind, d.detail, d.where)
        out['windows'] = budget_windows(clog)
        return out
    out['cand_end'] = c.end
    out['cand_instr'] = c.instr
    out['stage_cand'] = c.stage_clocks
    out['windows'] = budget_windows(clog)
    if c.end == 'error':
        out['status'] = 'error'
        out['detail'] = 'candidate: ' + c.end_detail
        return out
    if c.end != b.end or c.frames != b.frames:
        out['status'] = 'diverged'
        out['div'] = (c.frames, 'end', 'baseline ended %s at frame %d, candidate %s at frame %d'
                      % (b.end, b.frames, c.end, c.frames), None)
        return out
    out['status'] = 'equal'
    out['timing_names'] = plan.timing_names
    return out


_NO_D_WRITE = {'cmp', 'cmps', 'cmpm', 'test', 'tjz', 'tjnz', 'jnct1', 'wrlong', 'wypin', 'wxpin', 'wrpin', 'qmul',
               'qdiv', 'qsqrt', 'qfrac', 'qrotate', 'qvector', 'setq', 'setq2', 'alts', 'altd', 'altgb', 'altgw',
               'altsw', 'altgn', 'sca', 'testp', 'dirl', 'dirh', 'outl', 'outh', 'drvl', 'drvh', 'fltl', 'flth',
               'jmp#', 'call#', 'ret', 'nop', 'augs', 'augd', 'skip', 'jmprel', 'waitx', 'cogatn', 'pollatn', 'waitatn'}


def context(img, scen, layout, con, frame, where, side, n=24):
    """Re-run one image to the end of frame `frame` with a trace, and render the instructions leading to the
    differing write (or, for a register, to the last instruction naming it as D before the boundary)."""
    r = Runner(img, scen, layout, con, stop_at=frame + 1, trace=60_000, trace_ic=True).run()
    env, cog = r.env, r.cog
    tr = list(r.trace or [])
    target = None
    why = 'the end of the frame'
    if where and where[0] in ('hub', 'pins', 'qin', 'events') and frame < len(r.logs):
        ics = (r.logs[frame].ic or {}).get(where[0], [])
        idx = where[1] if side == 'base' else where[2]
        if idx is not None and idx < len(ics):
            target = ics[idx]
            why = 'the differing %s write' % where[0]
    elif where and where[0] == 'reg':
        addr = where[1] if side == 'base' else where[2]
        for ic, ct, pc, w in reversed(tr):
            if w and ((w >> 9) & 0x1FF) == addr and _mnem(w) not in _NO_D_WRITE:
                target = ic
                why = 'the last instruction writing $%03X before the boundary' % addr
                break
    sel = [t for t in tr if t[0] <= target][-n:] if target is not None else tr[-n:]
    lines = ['    %s -- up to %s:' % (img.label, why)]
    for ic, ct, pc, w in sel:
        mark = '>>' if ic == target else '  '
        lines.append('    %s %11d  $%03X %-24s %s' % (mark, ct, pc, pc_name(img, env, cog, pc)[:24], disasm(w, pc)))
    return lines, r


def _mnem(w):
    parts = disasm(w).split()
    if not parts:
        return ''
    return parts[1] if parts[0].startswith(('if_', '_ret_')) and len(parts) > 1 else parts[0]

"""An instruction-level P2 cog emulator for the subset of PASM2 the BLDC driver (and its planned WPs) use.

It executes the real 32-bit encodings the compiler emitted, never the source text. Every encoding and flag rule
below was taken from the p2kb-mcp knowledge base (the key is named beside each group); an opcode that is not
listed here stops the run with Unmodelled -- nothing is ever skipped silently.

The cog talks to the outside world only through an Environment object (drvenv.py): hub RAM, pins (smart-pin
writes, RDPIN/RQPIN/AKPIN, TESTP, INA/INB), the attention flag, and the CT1 event, which the environment
schedules by frame (an "event point") so a change in a routine's clock count cannot move a drive pass.

Timing model (worst case, the same model as the desk scripts): 2 clocks per instruction, 4 for a taken branch or
a _RET_, RDLONG 16 (+1 per extra block long, into cog or LUT: SETQ/SETQ2 move one long per clock after the hub
window, p2kbPasm2SetqBlockOps), WRLONG 10 (+1 per extra block long), RDLUT 3, a CORDIC issue 9
clocks with its result ready 55 clocks after the issue ends (GETQX/GETQY end at max(start + 2, ready)), WAITX
2 + D. Hub-window and CORDIC-slot waits are taken at their maximum, so every figure is an upper bound.
"""
import math

M32 = 0xFFFF_FFFF

# ---- clocks ----
CLK_INSTR = 2
CLK_BRANCH = 4
CLK_RDLONG = 16          # p2kbPasm2Rdlong: 9..16
CLK_WRLONG = 10          # p2kbPasm2Wrlong: 3..10
CLK_RDLUT = 3            # p2kbPasm2Rdlut
CLK_CORDIC_ISSUE = 9     # p2kbPasm2Qmul etc.: 2..9
CORDIC_LATENCY = 55      # p2kbArchCordic: results 55 clocks after issue

STACK_DEPTH = 8          # p2 hardware stack (p2kbPasm2Call: pushed to K)


class EmuError(Exception):
    """The run cannot continue faithfully."""


class Unmodelled(EmuError):
    """An opcode or an operand form the emulator does not model."""


class Undefined(EmuError):
    """An operation whose result p2kb documents as undefined (QDIV by zero, a quotient over 32 bits, ...)."""


class Parked(Exception):
    """The cog waits for an event that will never come (WAITATN with nothing scheduled): the run's end."""


def s32(x):
    x &= M32
    return x - 0x1_0000_0000 if x & 0x8000_0000 else x


def sx(v, bits):
    v &= (1 << bits) - 1
    return v - (1 << bits) if v >> (bits - 1) else v


def parity(x):
    return bin(x & M32).count('1') & 1


# condition code -> (reads C, reads Z); p2kbPasm2ConditionalExecution: true iff EEEE bit [C*2+Z] is 1
COND_READS = {}
for _e in range(16):
    _t = [(_e >> _k) & 1 for _k in range(4)]            # index C*2 + Z
    COND_READS[_e] = (_t[0] != _t[2] or _t[1] != _t[3], _t[0] != _t[1] or _t[2] != _t[3])
COND_READS[0] = (False, False)          # _RET_: always
COND_NAMES = ['_ret_', 'if_nc_and_nz', 'if_nc_and_z', 'if_nc', 'if_c_and_nz', 'if_nz', 'if_c_ne_z', 'if_nc_or_nz',
              'if_c_and_z', 'if_c_eq_z', 'if_z', 'if_nc_or_z', 'if_c', 'if_c_or_nz', 'if_c_or_z', '']


class Dec:
    __slots__ = ('w', 'name', 'fn', 'cond', 'c', 'z', 'i', 'l', 'd', 's', 'n', 'frc', 'frz', 'fwc', 'fwz',
                 'prefix', 'imm_s', 'imm_d', 'rel')

    def __init__(self, w, name, fn):
        self.w = w
        self.name = name
        self.fn = fn
        self.cond = w >> 28
        self.c = (w >> 20) & 1
        self.z = (w >> 19) & 1
        self.i = (w >> 18) & 1
        self.l = (w >> 19) & 1
        self.d = (w >> 9) & 0x1FF
        self.s = w & 0x1FF
        self.n = 0
        self.frc = self.frz = False
        self.fwc = self.fwz = False
        self.prefix = False
        self.imm_s = False       # the S field is an immediate (AUGS applies)
        self.imm_d = False       # the D field is an immediate (AUGD applies)
        self.rel = False


def _czi(name, fn, w, wc=True, wz=True, frc=False, frz=False):
    d = Dec(w, name, fn)
    d.imm_s = bool(d.i)
    d.fwc = wc and bool(d.c)
    d.fwz = wz and bool(d.z)
    d.frc, d.frz = frc, frz
    return d


def _li(name, fn, w):
    d = Dec(w, name, fn)
    d.imm_s = bool(d.i)
    d.imm_d = bool(d.l)
    return d


class Cog:
    """One cog. `env` supplies hub RAM, pins, attention and the CT1 schedule."""

    def __init__(self, env, ct0=0):
        self.env = env
        self.cog = [0] * 512
        self.lut = [0] * 512
        self.lut_valid = bytearray(512)
        self.lut_src = [None] * 512       # hub byte address each LUT long was loaded from (for naming)
        self.C = 0
        self.Z = 0
        self.pc = 0
        self.stack = []
        self.ct = ct0
        self.q = 0
        self.q_armed = False              # SETQ/SETQ2 immediately before (ALTx/AUGx pass it through)
        self.q_lut = False
        self.q_clean = True               # no ALTx/AUGS/AUGD between the SETQ and its block transfer
        self.augs = None
        self.augd = None
        self.alt_d = None
        self.alt_s = None
        self.alt_n = None
        self.sca = None
        self.skip = 0
        self.rep = None                   # [start, end, left] (left 0: forever)
        self.atn = 0
        self.ct1_target = None
        self.cq = []                      # CORDIC results in flight / held: dicts
        self.dcache = {}
        self.br = False
        self.extra = 0
        self.icount = 0
        self.track = None                 # liveness tracker (see Tracker) or None
        self.trace = None                 # ring buffer of recent (icount, ct, pc, w, hub source) or None
        self.halted = False
        self.last_pc = 0
        self.timing_regs = set()          # registers written from CT (GETCT, ADDCT1): timing, not behaviour
        self.cov = None                   # coverage: {(hub source address, outcome)} or None
        self.cog_src_base = 0

    # =============================================================== registers
    def rreg(self, a):
        if self.track is not None:
            self.track.read(a)
        if a >= 0x1FE:
            return self.env.read_in_port(self, a - 0x1FE)
        return self.cog[a]

    def wreg(self, a, v):
        v &= M32
        if self.track is not None:
            self.track.write(a)
        if 0x1FA <= a <= 0x1FF:
            if a <= 0x1FD:
                self.env.write_port_reg(self, a, v)
            self.cog[a] = v
            return
        self.cog[a] = v

    def dfield(self, dec):
        return self.alt_d if self.alt_d is not None else dec.d

    def sfield(self, dec):
        return self.alt_s if self.alt_s is not None else dec.s

    def S(self, dec):
        """The instruction's S operand value (register, #imm, ##imm, or SCA's substitute)."""
        if self.sca is not None:
            v = self.sca
            self.sca = None
            return v
        s = self.sfield(dec)
        if dec.imm_s:
            if self.augs is not None:
                v = ((self.augs << 9) | s) & M32
                if not dec.prefix:
                    self.augs = None       # an ALTx #S uses AUGS without cancelling it (p2kbPasm2Augs errata)
                return v
            return s
        return self.rreg(s)

    def D(self, dec):
        d = self.dfield(dec)
        if dec.imm_d:
            if self.augd is not None:
                v = ((self.augd << 9) | d) & M32
                self.augd = None
                return v
            return d
        return self.rreg(d)

    def wD(self, dec, v):
        self.wreg(self.dfield(dec), v)

    # =============================================================== decode
    def decode(self, w):
        op = (w >> 21) & 0x7F
        fn = _OPS.get(op)
        if w == 0:                                       # NOP is the all-zero long (p2kbPasm2Nop), not _RET_ ROR
            dec = Dec(w, 'nop', Cog.x_nop)
            dec.cond = 15
        elif fn is None:
            dec = Dec(w, '?%02X' % op, Cog.x_unmodelled)
        else:
            dec = fn(w)
        self.dcache[w] = dec
        return dec

    # =============================================================== run
    def step(self):
        pc = self.pc
        if pc < 0x200:
            w = self.cog[pc]
        elif pc < 0x400:
            if not self.lut_valid[pc - 0x200]:
                raise EmuError('executing an uninitialised LUT long at $%03X' % pc)
            w = self.lut[pc - 0x200]
        else:
            raise Unmodelled('hub execution (PC $%05X) is not modelled' % pc)
        self.last_pc = pc
        self.pc = pc + 1
        self.icount += 1
        if self.trace is not None:          # + the hub source, so a LUT long is named from the image loaded then
            self.trace.append((self.icount, self.ct, pc, w, self._src(pc)))
        dec = self.dcache.get(w)
        if dec is None:
            dec = self.decode(w)
        # SKIP (p2kbPasm2Skip): each 1 bit cancels the next instruction; a cancelled one takes 2 clocks
        if self.skip:
            b = self.skip & 1
            self.skip >>= 1
            if b:
                if self.cov is not None:
                    self.cov.add((self._src(pc), 4))
                self._consume_prefixes(dec)
                self.ct += CLK_INSTR
                self._rep_check()
                return
        cond = dec.cond
        tr = self.track
        if tr is not None:
            rc, rz = COND_READS[cond]
            if rc:
                tr.flag_read(0)
            if rz:
                tr.flag_read(1)
        if cond and not (cond >> ((self.C << 1) | self.Z)) & 1:
            # condition false: the instruction passes as a 2-clock no-op and consumes the prefixes aimed at it
            if self.cov is not None:
                self.cov.add((self._src(pc), 0))
            self._consume_prefixes(dec)
            self.ct += CLK_INSTR
            self._rep_check()
            return
        if tr is not None:
            if dec.frc:
                tr.flag_read(0)
            if dec.frz:
                tr.flag_read(1)
        self.br = False
        self.extra = 0
        if self.cov is not None:
            self.cov.add((self._src(pc), 1))
        dec.fn(self, dec)
        if self.cov is not None and dec.name in ('tjz', 'tjnz', 'djnz', 'jnct1'):
            self.cov.add((self._src(pc), 2 if self.br else 3))
        if tr is not None:
            if dec.fwc:
                tr.flag_write(0)
            if dec.fwz:
                tr.flag_write(1)
        if not dec.prefix:
            self.alt_d = self.alt_s = self.alt_n = None
            nm = dec.name
            if nm != 'setq' and nm != 'setq2':
                self.q_armed = False
            if nm != 'sca':
                self.sca = None
        else:
            self.q_clean = False if self.q_armed else self.q_clean
        cost = (CLK_BRANCH if self.br else CLK_INSTR) + self.extra
        if cond == 0 and not self.br:
            self._ret()
            cost += 2
        self.ct += cost
        if self.br:
            self.rep = None
            if self.skip:
                raise Unmodelled('a branch inside a SKIP pattern at $%03X' % pc)
        else:
            self._rep_check()

    def _src(self, pc):
        """The hub byte address an executing long was loaded from (coverage is kept by image position)."""
        if pc < 0x200:
            return self.cog_src_base + 4 * pc
        return self.lut_src[pc - 0x200]

    def _consume_prefixes(self, dec):
        if dec.prefix:
            return
        self.alt_d = self.alt_s = self.alt_n = None
        self.sca = None
        self.q_armed = False
        if dec.imm_s and self.augs is not None:
            self.augs = None
        if dec.imm_d and self.augd is not None:
            self.augd = None

    def _rep_check(self):
        r = self.rep
        if r is not None and self.pc == r[1]:
            if r[2] == 1:
                self.rep = None
            else:
                if r[2]:
                    r[2] -= 1
                self.pc = r[0]

    def _ret(self):
        if not self.stack:
            raise EmuError('RET with an empty hardware stack at $%03X' % self.last_pc)
        k = self.stack.pop()
        self.pc = k & 0xF_FFFF
        return k

    def _push(self, ret_pc):
        self.stack.append(((self.C << 31) | (self.Z << 30) | (ret_pc & 0xF_FFFF)))
        if len(self.stack) > STACK_DEPTH:
            del self.stack[0]

    def _jump(self, target):
        if target >= 0x400:
            raise Unmodelled('a branch into hub RAM ($%05X) is not modelled' % target)
        self.pc = target
        self.br = True

    # =============================================================== unmodelled
    def x_nop(self, dec):
        pass

    def x_unmodelled(self, dec):
        raise Unmodelled('opcode %s (word $%08X) at $%03X is not modelled' % (dec.name, dec.w, self.last_pc))

    # =============================================================== shifts (p2kbPasm2Shr/Shl/Sar/Rcl)
    def x_shr(self, dec):
        v = self.rreg(self.dfield(dec))
        n = self.S(dec) & 31
        r = v >> n
        if dec.c:
            self.C = ((v >> (n - 1)) & 1) if n else (v & 1)
        self.wD(dec, r)
        if dec.z:
            self.Z = int(r == 0)

    def x_shl(self, dec):
        v = self.rreg(self.dfield(dec))
        n = self.S(dec) & 31
        r = (v << n) & M32
        if dec.c:
            self.C = ((v >> (32 - n)) & 1) if n else (v >> 31)
        self.wD(dec, r)
        if dec.z:
            self.Z = int(r == 0)

    def x_sar(self, dec):
        v = self.rreg(self.dfield(dec))
        n = self.S(dec) & 31
        r = (s32(v) >> n) & M32
        if dec.c:
            self.C = ((v >> (n - 1)) & 1) if n else (v & 1)
        self.wD(dec, r)
        if dec.z:
            self.Z = int(r == 0)

    def x_rcl(self, dec):
        v = self.rreg(self.dfield(dec))
        n = self.S(dec) & 31
        cin = self.C
        r = ((v << n) | (((1 << n) - 1) if cin else 0)) & M32
        if dec.c:
            self.C = ((v >> (32 - n)) & 1) if n else (v >> 31)
        self.wD(dec, r)
        if dec.z:
            self.Z = int(r == 0)

    # =============================================================== add/sub (p2kbPasm2Add/Addx/Adds/Sub/Subx/Subs/Subr)
    def x_add(self, dec):
        a = self.rreg(self.dfield(dec))
        b = self.S(dec)
        r = a + b
        self.wD(dec, r)
        if dec.c:
            self.C = r >> 32
        if dec.z:
            self.Z = int((r & M32) == 0)

    def x_addx(self, dec):
        a = self.rreg(self.dfield(dec))
        b = self.S(dec)
        r = a + b + self.C
        self.wD(dec, r)
        if dec.c:
            self.C = r >> 32
        if dec.z:
            self.Z = int(self.Z and (r & M32) == 0)

    def x_adds(self, dec):
        a = self.rreg(self.dfield(dec))
        b = self.S(dec)
        r = s32(a) + s32(b)
        self.wD(dec, r)
        if dec.c:
            self.C = int(r < 0)
        if dec.z:
            self.Z = int((r & M32) == 0)

    def x_sub(self, dec):
        a = self.rreg(self.dfield(dec))
        b = self.S(dec)
        r = a - b
        self.wD(dec, r)
        if dec.c:
            self.C = int(r < 0)
        if dec.z:
            self.Z = int((r & M32) == 0)

    def x_subx(self, dec):
        a = self.rreg(self.dfield(dec))
        b = self.S(dec)
        r = a - (b + self.C)
        self.wD(dec, r)
        if dec.c:
            self.C = int(r < 0)
        if dec.z:
            self.Z = int(self.Z and (r & M32) == 0)

    def x_subs(self, dec):
        a = self.rreg(self.dfield(dec))
        b = self.S(dec)
        r = s32(a) - s32(b)
        self.wD(dec, r)
        if dec.c:
            self.C = int(r < 0)
        if dec.z:
            self.Z = int((r & M32) == 0)

    def x_subr(self, dec):
        a = self.rreg(self.dfield(dec))
        b = self.S(dec)
        r = b - a
        self.wD(dec, r)
        if dec.c:
            self.C = int(r < 0)
        if dec.z:
            self.Z = int((r & M32) == 0)

    # =============================================================== compares (p2kbPasm2Cmp/Cmps/Cmpm)
    def x_cmp(self, dec):
        a = self.rreg(self.dfield(dec))
        b = self.S(dec)
        if dec.c:
            self.C = int(a < b)
        if dec.z:
            self.Z = int(a == b)

    def x_cmps(self, dec):
        a = s32(self.rreg(self.dfield(dec)))
        b = s32(self.S(dec))
        if dec.c:
            self.C = int(a < b)
        if dec.z:
            self.Z = int(a == b)

    def x_cmpm(self, dec):
        a = self.rreg(self.dfield(dec))
        b = self.S(dec)
        if dec.c:
            self.C = ((a - b) >> 31) & 1
        if dec.z:
            self.Z = int(a == b)

    # =============================================================== limits (p2kbPasm2Fge/Fle/Fges/Fles)
    def _limit(self, dec, signed, lower):
        a = self.rreg(self.dfield(dec))
        b = self.S(dec)
        av, bv = (s32(a), s32(b)) if signed else (a, b)
        lim = (av < bv) if lower else (av > bv)
        r = b if lim else a
        self.wD(dec, r)
        if dec.c:
            self.C = int(lim)
        if dec.z:
            self.Z = int(r == 0)

    def x_fge(self, dec):
        self._limit(dec, False, True)

    def x_fle(self, dec):
        self._limit(dec, False, False)

    def x_fges(self, dec):
        self._limit(dec, True, True)

    def x_fles(self, dec):
        self._limit(dec, True, False)

    # =============================================================== bit tests / ops (p2kbPasm2Testb/Testbn/Bitl/Bith/Bitc)
    def x_testb(self, dec):
        a = self.rreg(self.dfield(dec))
        b = self.S(dec)
        bit = (a >> (b & 31)) & 1
        op7 = (dec.w >> 21) & 0x7F
        if op7 & 1:
            bit ^= 1                        # TESTBN
        fn = (op7 >> 1) & 3                 # 0 set, 1 AND, 2 OR, 3 XOR
        if dec.c:
            self.C = bit if fn == 0 else (self.C & bit if fn == 1 else (self.C | bit if fn == 2 else self.C ^ bit))
        else:
            self.Z = bit if fn == 0 else (self.Z & bit if fn == 1 else (self.Z | bit if fn == 2 else self.Z ^ bit))

    def _bitop(self, dec, kind):
        da = self.dfield(dec)
        a = self.rreg(da)
        b = self.S(dec)
        first = b & 31
        cnt = ((b >> 5) & 31) + 1
        orig = (a >> first) & 1
        mask = 0
        for k in range(cnt):
            mask |= 1 << ((first + k) & 31)
        if kind == 'l':
            r = a & ~mask
        elif kind == 'h':
            r = a | mask
        else:                               # 'c'
            r = (a | mask) if self.C else (a & ~mask)
        self.wreg(da, r & M32)
        if dec.c:
            self.C = orig
        if dec.z:
            self.Z = orig

    def x_bitl(self, dec):
        self._bitop(dec, 'l')

    def x_bith(self, dec):
        self._bitop(dec, 'h')

    def x_bitc(self, dec):
        self._bitop(dec, 'c')

    # =============================================================== logic (p2kbPasm2And/Andn/Or/Xor/Test)
    def _logic(self, dec, r, write=True):
        if write:
            self.wD(dec, r)
        if dec.c:
            self.C = parity(r)
        if dec.z:
            self.Z = int(r == 0)

    def x_and(self, dec):
        self._logic(dec, self.rreg(self.dfield(dec)) & self.S(dec))

    def x_andn(self, dec):
        self._logic(dec, self.rreg(self.dfield(dec)) & ~self.S(dec) & M32)

    def x_or(self, dec):
        self._logic(dec, self.rreg(self.dfield(dec)) | self.S(dec))

    def x_xor(self, dec):
        self._logic(dec, self.rreg(self.dfield(dec)) ^ self.S(dec))

    def x_test(self, dec):
        self._logic(dec, self.rreg(self.dfield(dec)) & self.S(dec), write=False)

    # =============================================================== moves / unary (p2kbPasm2Mov/Not/Abs/Neg/Negc)
    def x_mov(self, dec):
        v = self.S(dec)
        self.wD(dec, v)
        if dec.c:
            self.C = v >> 31
        if dec.z:
            self.Z = int(v == 0)

    def x_not(self, dec):
        v = self.S(dec)
        r = ~v & M32
        self.wD(dec, r)
        if dec.c:
            self.C = (v >> 31) ^ 1
        if dec.z:
            self.Z = int(r == 0)

    def x_abs(self, dec):
        v = self.S(dec)
        r = abs(s32(v)) & M32
        self.wD(dec, r)
        if dec.c:
            self.C = v >> 31
        if dec.z:
            self.Z = int(r == 0)

    def x_neg(self, dec):
        v = self.S(dec)
        r = (-s32(v)) & M32
        self.wD(dec, r)
        if dec.c:
            self.C = r >> 31
        if dec.z:
            self.Z = int(r == 0)

    def x_negc(self, dec):
        v = self.S(dec)
        r = ((-s32(v)) if self.C else v) & M32
        self.wD(dec, r)
        if dec.c:
            self.C = r >> 31
        if dec.z:
            self.Z = int(r == 0)

    # =============================================================== misc math (p2kbPasm2Incmod/Zerox/Signx/Decod/Bmask/Mul/Muls/Sca)
    def x_incmod(self, dec):
        da = self.dfield(dec)
        a = self.rreg(da)
        b = self.S(dec)
        wrap = a == b
        r = 0 if wrap else (a + 1) & M32
        self.wreg(da, r)
        if dec.c:
            self.C = int(wrap)
        if dec.z:
            self.Z = int(r == 0)

    def x_zerox(self, dec):
        da = self.dfield(dec)
        a = self.rreg(da)
        n = self.S(dec) & 31
        r = a & ((2 << n) - 1)
        self.wreg(da, r)
        if dec.c:
            self.C = r >> 31
        if dec.z:
            self.Z = int(r == 0)

    def x_signx(self, dec):
        da = self.dfield(dec)
        a = self.rreg(da)
        n = self.S(dec) & 31
        r = sx(a, n + 1) & M32
        self.wreg(da, r)
        if dec.c:
            self.C = r >> 31
        if dec.z:
            self.Z = int(r == 0)

    def x_decod(self, dec):
        self.wD(dec, 1 << (self.S(dec) & 31))

    def x_bmask(self, dec):
        self.wD(dec, (2 << (self.S(dec) & 31)) - 1)

    def x_mul(self, dec):
        da = self.dfield(dec)
        a = self.rreg(da) & 0xFFFF
        b = self.S(dec) & 0xFFFF
        self.wreg(da, a * b)
        if dec.z:
            self.Z = int(a == 0 or b == 0)

    def x_muls(self, dec):
        da = self.dfield(dec)
        a = sx(self.rreg(da), 16)
        b = sx(self.S(dec), 16)
        self.wreg(da, (a * b) & M32)
        if dec.z:
            self.Z = int(a == 0 or b == 0)

    def x_sca(self, dec):
        a = self.rreg(self.dfield(dec)) & 0xFFFF
        b = self.S(dec) & 0xFFFF
        p = a * b
        self.sca = (p >> 16) & M32
        if dec.z:
            self.Z = int(p == 0)

    # =============================================================== nibble/byte/word (p2kbPasm2Getnib/Getbyte/Getword/Setword)
    def x_getnib(self, dec):
        v = self.S(dec)
        n = self.alt_n if self.alt_n is not None else dec.n
        self.wD(dec, (v >> (4 * n)) & 0xF)

    def x_getbyte(self, dec):
        v = self.S(dec)
        n = self.alt_n if self.alt_n is not None else dec.n
        self.wD(dec, (v >> (8 * n)) & 0xFF)

    def x_getword(self, dec):
        v = self.S(dec)
        n = self.alt_n if self.alt_n is not None else dec.n
        self.wD(dec, (v >> (16 * n)) & 0xFFFF)

    def x_setword(self, dec):
        v = self.S(dec) & 0xFFFF
        n = self.alt_n if self.alt_n is not None else dec.n
        da = self.dfield(dec)
        a = self.rreg(da)
        sh = 16 * n
        self.wreg(da, (a & ~(0xFFFF << sh)) | (v << sh))

    # =============================================================== ALTx (p2kbPasm2Alts/Altd/Altgb/Altgw/Altsw/Altgn)
    def _alt_index(self, dec):
        da = dec.d
        dv = self.rreg(da)
        sv = self.S(dec)
        return da, dv, sv

    def _alt_advance(self, da, dv, sv, dec):
        inc = sx(sv >> 9, 9)
        if inc:
            self.wreg(da, dv + inc)

    def x_alts(self, dec):
        da, dv, sv = self._alt_index(dec)
        self.alt_s = (dv + sv) & 0x1FF
        self._alt_advance(da, dv, sv, dec)

    def x_altd(self, dec):
        da, dv, sv = self._alt_index(dec)
        self.alt_d = (dv + sv) & 0x1FF
        self._alt_advance(da, dv, sv, dec)

    def x_altgb(self, dec):
        da, dv, sv = self._alt_index(dec)
        self.alt_s = ((dv >> 2) + sv) & 0x1FF
        self.alt_n = dv & 3
        self._alt_advance(da, dv, sv, dec)

    def x_altgw(self, dec):
        da, dv, sv = self._alt_index(dec)
        self.alt_s = ((dv >> 1) + sv) & 0x1FF
        self.alt_n = dv & 1
        self._alt_advance(da, dv, sv, dec)

    def x_altsw(self, dec):
        da, dv, sv = self._alt_index(dec)
        self.alt_d = ((dv >> 1) + sv) & 0x1FF
        self.alt_n = dv & 1
        self._alt_advance(da, dv, sv, dec)

    def x_altgn(self, dec):
        da, dv, sv = self._alt_index(dec)
        self.alt_s = ((dv >> 3) + sv) & 0x1FF
        self.alt_n = dv & 7
        self._alt_advance(da, dv, sv, dec)

    # =============================================================== hub RAM (p2kbPasm2Rdlong/Wrlong/SetqBlockOps)
    def _hub_addr(self, dec):
        """The hub address of a RDxxxx/WRxxxx S operand, applying a PTRx expression's update."""
        s = self.sfield(dec)
        if not dec.imm_s:
            return self.rreg(s) & 0xF_FFFF, None
        if self.augs is not None:
            v = ((self.augs << 9) | s) & M32
            self.augs = None
            if (v >> 23) == 1:
                raise Unmodelled('an augmented PTRx expression (##) is not modelled')
            return v & 0xF_FFFF, None
        if not (s >> 8) & 1:
            return s & 0xFF, None
        # %1 S U ...: U = 0 is PTRx[index] with a 6-bit signed index (the compiler emits ptra[24] as %1_0_0_011000
        #  and ptra[-1] as %1_0_0_111111); U = 1 is %1 S 1 P NNNNN, P = 1 post-modify, a 5-bit signed index.
        if not (s >> 6) & 1:
            return self._ptr_expr((s >> 7) & 1, 0, 0, sx(s, 6), 4)
        return self._ptr_expr((s >> 7) & 1, 1, (s >> 5) & 1, sx(s, 5), 4)

    def _ptr_expr(self, which, upd, post, idx, scale):
        reg = 0x1F9 if which else 0x1F8
        p = self.rreg(reg)
        delta = idx * scale
        if not upd:
            return (p + delta) & 0xF_FFFF, None
        if post:
            return p & 0xF_FFFF, (reg, delta, idx)
        np_ = (p + delta) & M32
        self.wreg(reg, np_)
        return np_ & 0xF_FFFF, None

    def _ptr_post(self, upd, count):
        if upd is None:
            return
        reg, delta, idx = upd
        if count > 1 and self.q_clean:
            delta = (1 if idx > 0 else -1) * count * 4     # block-size PTRx delta
        self.wreg(reg, (self.cog[reg] + delta) & M32)

    def x_rdlong(self, dec):
        addr, upd = self._hub_addr(dec)
        if addr & 3:
            raise Unmodelled('an unaligned RDLONG at hub $%05X' % addr)
        env = self.env
        if self.q_armed:
            n = (self.q & 0x1FF) + 1
            vals = env.hub_read_block(self, addr, n)
            if self.q_lut:
                base = self.dfield(dec) & 0x1FF
                for k, v in enumerate(vals):
                    j = (base + k) & 0x1FF
                    self.lut[j] = v
                    self.lut_valid[j] = 1
                    self.lut_src[j] = addr + 4 * k
            else:
                base = self.dfield(dec)
                for k, v in enumerate(vals):
                    self.wreg((base + k) & 0x1FF, v)
            # p2kbPasm2Rdlong (9..16, the hub window) + p2kbPasm2SetqBlockOps (then one long per clock)
            self.extra = CLK_RDLONG - CLK_INSTR + (n - 1)
            if self.q_lut:
                self.env.lut_load(self, addr, n, CLK_RDLONG + (n - 1))
            self._ptr_post(upd, n)
            if dec.c or dec.z:
                raise Unmodelled('a block RDLONG with WC/WZ')
            return
        v = env.hub_read_block(self, addr, 1)[0]
        self.wD(dec, v)
        if dec.c:
            self.C = v >> 31
        if dec.z:
            self.Z = int(v == 0)
        self.extra = CLK_RDLONG - CLK_INSTR
        self._ptr_post(upd, 1)

    def x_wrlong(self, dec):
        # WRLONG {#}D,{#}S/P: D is the data (L = immediate)
        addr, upd = self._hub_addr(dec)
        if addr & 3:
            raise Unmodelled('an unaligned WRLONG at hub $%05X' % addr)
        if self.q_armed:
            n = (self.q & 0x1FF) + 1
            if dec.imm_d:
                raise Unmodelled('a block WRLONG fill (#D) is not modelled')
            base = self.dfield(dec)
            if self.q_lut:
                vals = []
                for k in range(n):
                    j = (base + k) & 0x1FF
                    vals.append(self.lut[j])
            else:
                vals = [self.rreg((base + k) & 0x1FF) for k in range(n)]
            self.env.hub_write_block(self, addr, vals)
            self.extra = CLK_WRLONG - CLK_INSTR + (n - 1)
            self._ptr_post(upd, n)
            return
        v = self.D(dec)
        self.env.hub_write_block(self, addr, [v])
        self.extra = CLK_WRLONG - CLK_INSTR
        self._ptr_post(upd, 1)

    # =============================================================== LUT (p2kbPasm2Rdlut/Wrlut)
    def _lut_addr(self, dec):
        s = self.sfield(dec)
        if not dec.imm_s:
            return self.rreg(s) & 0x1FF, None
        if self.augs is not None:
            raise Unmodelled('RDLUT/WRLUT with ## (p2kbPasm2Rdlut: lands on the pointer path)')
        if not (s >> 8) & 1:
            return s & 0xFF, None
        which, upd, post = (s >> 7) & 1, (s >> 6) & 1, (s >> 5) & 1
        idx = sx(s, 5) if upd else sx(s, 6)
        reg = 0x1F9 if which else 0x1F8
        p = self.rreg(reg)
        if not upd:
            return (p + idx) & 0x1FF, None
        if post:
            self.wreg(reg, (p + idx) & M32)
            return p & 0x1FF, None
        self.wreg(reg, (p + idx) & M32)
        return (p + idx) & 0x1FF, None

    def x_rdlut(self, dec):
        a, _ = self._lut_addr(dec)
        if not self.lut_valid[a]:
            raise EmuError('RDLUT of an uninitialised LUT long %d' % a)
        v = self.lut[a]
        self.wD(dec, v)
        if dec.c:
            self.C = v >> 31
        if dec.z:
            self.Z = int(v == 0)
        self.extra = CLK_RDLUT - CLK_INSTR

    def x_wrlut(self, dec):
        v = self.D(dec)
        a, _ = self._lut_addr(dec)
        self.lut[a] = v
        self.lut_valid[a] = 1
        self.lut_src[a] = None

    # =============================================================== branches (p2kbPasm2Jmp/Call/Ret/Calld/Callpa/Djnz/Tjz/Tjnz/Jmprel/Rep)
    def _rel9(self, dec):
        """A #S branch operand: relative, in instructions (cog/LUT); ##S: 20-bit relative. Register S: absolute."""
        s = self.sfield(dec)
        if dec.imm_s:
            if self.augs is not None:
                v = ((self.augs << 9) | s) & 0xF_FFFF
                self.augs = None
                return (self.pc + sx(v, 20)) & 0xF_FFFF
            return (self.pc + sx(s, 9)) & 0xF_FFFF
        return self.rreg(s) & 0xF_FFFF

    def _addr20(self, w):
        a = w & 0xF_FFFF
        if (w >> 20) & 1:
            if self.pc < 0x400:
                return (self.pc + (sx(a, 20) >> 2)) & 0xF_FFFF   # cog/LUT: the offset is in bytes (verified on the image)
            raise Unmodelled('a relative branch in hub execution')
        return a if a < 0x400 else a

    def x_jmp_a(self, dec):
        self._jump(self._addr20(dec.w))

    def x_call_a(self, dec):
        t = self._addr20(dec.w)
        self._push(self.pc)
        self._jump(t)

    def x_calld_a(self, dec):
        t = self._addr20(dec.w)
        ww = (dec.w >> 21) & 3
        reg = [0x1F6, 0x1F7, 0x1F8, 0x1F9][ww]
        self.wreg(reg, (self.C << 31) | (self.Z << 30) | self.pc)
        self._jump(t)

    def x_calld(self, dec):
        da = self.dfield(dec)
        t = self._rel9(dec)
        self.wreg(da, (self.C << 31) | (self.Z << 30) | self.pc)
        self._jump(t)
        if dec.c or dec.z:
            raise Unmodelled('CALLD D,S with WC/WZ')

    def x_callpa(self, dec):
        v = self.D(dec)
        t = self._rel9(dec)
        self.wreg(0x1F6, v)
        self._push(self.pc)
        self._jump(t)

    def x_djnz(self, dec):
        da = self.dfield(dec)
        r = (self.rreg(da) - 1) & M32
        self.wreg(da, r)
        t = self._rel9(dec)
        if r != 0:
            self._jump(t)

    def x_tjz(self, dec):
        v = self.rreg(self.dfield(dec))
        t = self._rel9(dec)
        if v == 0:
            self._jump(t)

    def x_tjnz(self, dec):
        v = self.rreg(self.dfield(dec))
        t = self._rel9(dec)
        if v != 0:
            self._jump(t)

    def x_jnct1(self, dec):
        t = self._rel9(dec)
        fired = self.env.ct1_poll(self)       # reads, then clears, the CT1 event flag
        if not fired:
            self._jump(t)

    def x_rep(self, dec):
        n = self.D(dec) & 0x1FF
        cnt = self.S(dec)
        if n:
            self.rep = [self.pc, self.pc + n, cnt]

    # =============================================================== smart pins (p2kbPasm2Wrpin/Wxpin/Wypin/Akpin/Rdpin/Rqpin)
    def _pinfield(self, v):
        base = v & 63
        extra = (v >> 6) & 31
        if self.q_armed:
            extra = self.q & 31
        return [(base & 32) | ((base + k) & 31) for k in range(extra + 1)]

    def x_wrpin(self, dec):
        if dec.l and self.dfield(dec) == 1 and self.augd is None:
            pins = self._pinfield(self.S(dec))           # AKPIN {#}S (p2kbPasm2Akpin)
            self.env.pin_op(self, 'akpin', pins, None)
            return
        v = self.D(dec)
        pins = self._pinfield(self.S(dec))
        self.env.pin_op(self, 'wrpin', pins, v)

    def x_wxpin(self, dec):
        v = self.D(dec)
        self.env.pin_op(self, 'wxpin', self._pinfield(self.S(dec)), v)

    def x_wypin(self, dec):
        v = self.D(dec)
        self.env.pin_op(self, 'wypin', self._pinfield(self.S(dec)), v)

    def x_rdpin(self, dec):
        pin = self.S(dec) & 63
        v, c = self.env.rdpin(self, pin, ack=((dec.w >> 19) & 1) == 1)
        self.wD(dec, v)
        if dec.c:
            self.C = c

    # =============================================================== CORDIC (p2kbPasm2Qmul/Qdiv/Qfrac/Qsqrt/Qrotate/Qvector/Getqx/Getqy)
    def _cordic_issue(self, kind, x, y):
        now = self.ct
        for r in self.cq:
            if not r['xr'] and not r['yr'] and r['ready'] <= now + CLK_CORDIC_ISSUE:
                raise Unmodelled('a CORDIC result was never read before a new operation (overwrite semantics)')
        # a partly read result at the head is retired by a new operation
        while self.cq and (self.cq[0]['xr'] or self.cq[0]['yr']):
            self.cq.pop(0)
        self.extra = CLK_CORDIC_ISSUE - CLK_INSTR
        self.cq.append({'ready': now + CLK_CORDIC_ISSUE + CORDIC_LATENCY, 'x': x & M32, 'y': y & M32,
                        'xr': False, 'yr': False, 'kind': kind})

    def x_qmul(self, dec):
        a = self.D(dec)
        b = self.S(dec)
        p = a * b
        self.env.cordic_input(self, 'qmul', a, b, None)
        self._cordic_issue('qmul', p & M32, p >> 32)

    def x_qdiv(self, dec):
        a = self.D(dec)
        b = self.S(dec)
        hi = self.q if self.q_armed and not self.q_lut else 0
        n = (hi << 32) | a
        self.env.cordic_input(self, 'qdiv', a, b, hi)
        if b == 0:
            raise Undefined('QDIV by zero at $%03X (p2kbPasm2Qdiv: undefined)' % self.last_pc)
        qq, rr = divmod(n, b)
        if qq > M32:
            raise Undefined('QDIV quotient over 32 bits at $%03X ({%08X,%08X} / %08X)' % (self.last_pc, hi, a, b))
        self._cordic_issue('qdiv', qq, rr)

    def x_qfrac(self, dec):
        a = self.D(dec)
        b = self.S(dec)
        lo = self.q if self.q_armed and not self.q_lut else 0
        n = (a << 32) | lo
        self.env.cordic_input(self, 'qfrac', a, b, lo)
        if b == 0:
            raise Undefined('QFRAC by zero at $%03X' % self.last_pc)
        qq, rr = divmod(n, b)
        if qq > M32:
            raise Undefined('QFRAC quotient over 32 bits at $%03X' % self.last_pc)
        self._cordic_issue('qfrac', qq, rr)

    def x_qsqrt(self, dec):
        a = self.D(dec)
        b = self.S(dec)
        self.env.cordic_input(self, 'qsqrt', a, b, None)
        self._cordic_issue('qsqrt', math.isqrt((b << 32) | a), 0)

    def x_qrotate(self, dec):
        x = s32(self.D(dec))
        ang = self.S(dec)
        y = s32(self.q) if self.q_armed and not self.q_lut else 0
        self.env.cordic_input(self, 'qrotate', x & M32, ang, y & M32)
        th = ang * (2 * math.pi / 4294967296.0)
        c, s = math.cos(th), math.sin(th)
        rx = int(round(x * c - y * s))
        ry = int(round(x * s + y * c))
        self._cordic_issue('qrotate', rx, ry)

    def x_qvector(self, dec):
        x = s32(self.D(dec))
        y = s32(self.S(dec))
        self.env.cordic_input(self, 'qvector', x & M32, y & M32, None)
        ln = int(round(math.hypot(x, y)))
        ang = int(round(math.atan2(y, x) * 4294967296.0 / (2 * math.pi)))
        self._cordic_issue('qvector', ln, ang)

    def _getq(self, dec, comp):
        # GETQx retires a head result whose same component was read; waits for the head's result
        while self.cq and self.cq[0][comp + 'r']:
            self.cq.pop(0)
        if not self.cq:
            raise Unmodelled('GETQ%s with no CORDIC result pending (QMT event behaviour not modelled) at $%03X'
                             % (comp.upper(), self.last_pc))
        r = self.cq[0]
        if len(self.cq) > 1 and self.cq[1]['ready'] <= self.ct and not r[comp + 'r']:
            other = 'y' if comp == 'x' else 'x'
            if not r[other + 'r']:
                raise Unmodelled('a CORDIC result overwritten before it was read (reads too slow) at $%03X'
                                 % self.last_pc)
        end = max(self.ct + CLK_INSTR, r['ready'])
        self.extra = end - self.ct - CLK_INSTR
        v = r[comp]
        r[comp + 'r'] = True
        if r['xr'] and r['yr']:
            self.cq.pop(0)
        self.wD(dec, v)
        if dec.c:
            self.C = v >> 31
        if dec.z:
            self.Z = int(v == 0)

    def x_getqx(self, dec):
        self._getq(dec, 'x')

    def x_getqy(self, dec):
        self._getq(dec, 'y')

    # =============================================================== D-only group
    def x_getct(self, dec):
        v = (self.ct >> 32) & M32 if dec.c else self.ct & M32
        self.timing_regs.add(self.dfield(dec))
        self.wD(dec, v)

    def x_waitx(self, dec):
        if dec.c or dec.z:
            raise Unmodelled('WAITX with WC/WZ (random delay)')
        self.extra = self.D(dec)

    def x_pollatn(self, dec):
        f = self.env.atn_poll(self)
        if dec.c:
            self.C = f
        if dec.z:
            self.Z = f

    def x_waitatn(self, dec):
        if self.q_armed:
            raise Unmodelled('WAITATN with a SETQ timeout')
        t = self.env.atn_wait(self)          # returns the clock the flag is (or was) set, or raises Parked
        if t > self.ct:
            self.extra = t - self.ct
        if dec.c:
            self.C = 0
        if dec.z:
            self.Z = 0

    def x_waitct1(self, dec):
        if self.ct1_target is None:
            raise EmuError('WAITCT1 with no CT1 target set')
        t = self.env.ct1_wait(self)
        if t > self.ct:
            self.extra = t - self.ct
        if dec.c:
            self.C = 0
        if dec.z:
            self.Z = 0

    def x_addct1(self, dec):
        da = self.dfield(dec)
        self.timing_regs.add(da)
        v = (self.rreg(da) + self.S(dec)) & M32
        self.wreg(da, v)
        self.ct1_target = v
        self.env.ct1_set(self, v)

    def x_setq(self, dec):
        self.q = self.D(dec)
        self.q_armed = True
        self.q_lut = False
        self.q_clean = True

    def x_setq2(self, dec):
        self.q = self.D(dec)
        self.q_armed = True
        self.q_lut = True
        self.q_clean = True

    def x_jmp_d(self, dec):
        v = self.rreg(self.dfield(dec))
        if dec.c:
            self.C = v >> 31
        if dec.z:
            self.Z = (v >> 30) & 1
        self._jump(v & 0xF_FFFF)

    def x_call_d(self, dec):
        v = self.rreg(self.dfield(dec))
        self._push(self.pc)
        if dec.c:
            self.C = v >> 31
        if dec.z:
            self.Z = (v >> 30) & 1
        self._jump(v & 0xF_FFFF)

    def x_ret(self, dec):
        k = self._ret()
        self.br = True
        if dec.c:
            self.C = k >> 31
        if dec.z:
            self.Z = (k >> 30) & 1

    def x_jmprel(self, dec):
        v = self.D(dec)
        self._jump((self.pc + sx(v, 20)) & 0xF_FFFF)

    def x_skip(self, dec):
        self.skip = self.D(dec)

    def x_skipf(self, dec):
        raise Unmodelled('SKIPF')

    def x_cogatn(self, dec):
        self.env.cogatn(self, self.D(dec) & 0xFF)

    def x_wrc(self, dec):
        self.wD(dec, self.C)

    def x_modcz(self, dec):
        cc = (dec.d >> 4) & 0xF
        zz = dec.d & 0xF
        idx = (self.C << 1) | self.Z
        nc = (cc >> idx) & 1
        nz = (zz >> idx) & 1
        if dec.c:
            self.C = nc
        if dec.z:
            self.Z = nz

    def x_pinop(self, dec):
        """DIR*/OUT*/FLT*/DRV* (and TESTP*, when exactly one of WC/WZ is given)."""
        sub = dec.s & 0x3F      # 0o00-0o37 over 001000000..001011111
        grp = (sub >> 3) & 3    # 0 DIR, 1 OUT, 2 FLT, 3 DRV
        var = sub & 7
        v = self.D(dec)
        if grp == 0 and (dec.c ^ dec.z):
            pin = v & 63
            bit = self.env.testp(self, pin)
            if var & 1:
                bit ^= 1
            fn = var >> 1
            if dec.c:
                self.C = bit if fn == 0 else (self.C & bit if fn == 1 else (self.C | bit if fn == 2 else self.C ^ bit))
            else:
                self.Z = bit if fn == 0 else (self.Z & bit if fn == 1 else (self.Z | bit if fn == 2 else self.Z ^ bit))
            return
        if var > 1:
            raise Unmodelled('pin op %s variant %d (only L/H are modelled)' % (['DIR', 'OUT', 'FLT', 'DRV'][grp], var))
        pins = [((v & 63) & 32) | (((v & 63) + k) & 31) for k in range(((v >> 6) & 31) + 1)]
        name = ['dir', 'out', 'flt', 'drv'][grp] + ('h' if var else 'l')
        orig = self.env.pin_op(self, name, pins, None)
        if dec.c:
            self.C = orig
        if dec.z:
            self.Z = orig

    # =============================================================== prefixes
    def x_augs(self, dec):
        self.augs = (dec.w & 0x7F_FFFF)

    def x_augd(self, dec):
        self.augd = (dec.w & 0x7F_FFFF)


# ====================================================================== decode table
def _d_simple(name, fn, **kw):
    def mk(w):
        return _czi(name, fn, w, **kw)
    return mk


def _dec_shift(name, fn, rc=False):
    return _d_simple(name, fn, frc=rc)


def _dec_testb_family(w):
    op7 = (w >> 21) & 0x7F
    c, z = (w >> 20) & 1, (w >> 19) & 1
    if c ^ z:
        fn_bits = (op7 >> 1) & 3
        nm = 'testb' + ('n' if op7 & 1 else '') + ['', ' andc/z', ' orc/z', ' xorc/z'][fn_bits]
        d = _czi(nm, Cog.x_testb, w)
        if fn_bits:
            d.frc = bool(c)
            d.frz = bool(z)
        return d
    if op7 == 0x20:
        return _czi('bitl', Cog.x_bitl, w)
    if op7 == 0x21:
        return _czi('bith', Cog.x_bith, w)
    if op7 == 0x22:
        return _czi('bitc', Cog.x_bitc, w, frc=True)
    return Dec(w, 'bit?%02X' % op7, Cog.x_unmodelled)


def _dec_getnib(w):
    d = _czi('getnib', Cog.x_getnib, w, wc=False, wz=False)
    d.n = (w >> 19) & 7
    return d


def _dec_getbyte(w):
    d = _czi('getbyte', Cog.x_getbyte, w, wc=False, wz=False)
    d.n = (w >> 19) & 3
    return d


def _dec_word(w):
    if (w >> 20) & 1:
        d = _czi('getword', Cog.x_getword, w, wc=False, wz=False)
    else:
        d = _czi('setword', Cog.x_setword, w, wc=False, wz=False)
    d.n = (w >> 19) & 1
    return d


def _alt(name, fn):
    def mk(w):
        d = _czi(name, fn, w, wc=False, wz=False)
        d.prefix = True
        return d
    return mk


def _dec_4a(w):
    if ((w >> 19) & 3) == 3:
        return _alt('altgn', Cog.x_altgn)(w)
    return Dec(w, 'op4A?', Cog.x_unmodelled)


def _dec_4b(w):
    sub = (w >> 19) & 3
    if sub == 1:
        return _alt('altgb', Cog.x_altgb)(w)
    if sub == 2:
        return _alt('altsw', Cog.x_altsw)(w)
    if sub == 3:
        return _alt('altgw', Cog.x_altgw)(w)
    return Dec(w, 'op4B?', Cog.x_unmodelled)


def _dec_4c(w):
    sub = (w >> 19) & 3
    if sub == 1:
        return _alt('altd', Cog.x_altd)(w)
    if sub == 2:
        return _alt('alts', Cog.x_alts)(w)
    return Dec(w, 'op4C?', Cog.x_unmodelled)


def _dec_4e(w):
    sub = (w >> 19) & 3
    if sub == 0:
        return _czi('decod', Cog.x_decod, w, wc=False, wz=False)
    if sub == 1:
        return _czi('bmask', Cog.x_bmask, w, wc=False, wz=False)
    return Dec(w, 'op4E?', Cog.x_unmodelled)


def _dec_50(w):
    if (w >> 20) & 1:
        return _czi('muls', Cog.x_muls, w, wc=False)
    return _czi('mul', Cog.x_mul, w, wc=False)


def _dec_51(w):
    if (w >> 20) & 1:
        return Dec(w, 'scas', Cog.x_unmodelled)
    return _czi('sca', Cog.x_sca, w, wc=False)


def _dec_53(w):
    if ((w >> 19) & 3) == 0:
        return _czi('addct1', Cog.x_addct1, w, wc=False, wz=False)
    return Dec(w, 'addct?', Cog.x_unmodelled)


def _dec_54(w):
    nm = 'rdpin' if (w >> 19) & 1 else 'rqpin'
    return _czi(nm, Cog.x_rdpin, w, wz=False)


def _dec_59(w):
    return _czi('calld', Cog.x_calld, w, wc=False, wz=False)


def _dec_5a(w):
    if (w >> 20) & 1:
        return Dec(w, 'callpb', Cog.x_unmodelled)
    return _li('callpa', Cog.x_callpa, w)


def _dec_5b(w):
    if ((w >> 19) & 3) == 1:
        return _czi('djnz', Cog.x_djnz, w, wc=False, wz=False)
    return Dec(w, 'dj?', Cog.x_unmodelled)


def _dec_5c(w):
    sub = (w >> 19) & 3
    if sub == 2:
        return _czi('tjz', Cog.x_tjz, w, wc=False, wz=False)
    if sub == 3:
        return _czi('tjnz', Cog.x_tjnz, w, wc=False, wz=False)
    return Dec(w, 'ij?', Cog.x_unmodelled)


def _dec_5e(w):
    if ((w >> 19) & 3) == 1 and ((w >> 9) & 0x1FF) == 0b000010001:
        return _czi('jnct1', Cog.x_jnct1, w, wc=False, wz=False)
    return Dec(w, 'jevent?', Cog.x_unmodelled)


def _dec_60(w):
    if (w >> 20) & 1:
        return _li('wxpin', Cog.x_wxpin, w)
    return _li('wrpin', Cog.x_wrpin, w)


def _dec_61(w):
    if (w >> 20) & 1:
        return _li('wrlut', Cog.x_wrlut, w)
    return _li('wypin', Cog.x_wypin, w)


def _dec_63(w):
    if (w >> 20) & 1:
        return Dec(w, 'rdfast', Cog.x_unmodelled)
    return _li('wrlong', Cog.x_wrlong, w)


def _dec_66(w):
    if (w >> 20) & 1:
        return _li('rep', Cog.x_rep, w)
    return Dec(w, 'xcont', Cog.x_unmodelled)


def _dec_68(w):
    return _li('qdiv' if (w >> 20) & 1 else 'qmul', Cog.x_qdiv if (w >> 20) & 1 else Cog.x_qmul, w)


def _dec_69(w):
    return _li('qsqrt' if (w >> 20) & 1 else 'qfrac', Cog.x_qsqrt if (w >> 20) & 1 else Cog.x_qfrac, w)


def _dec_6a(w):
    return _li('qvector' if (w >> 20) & 1 else 'qrotate', Cog.x_qvector if (w >> 20) & 1 else Cog.x_qrotate, w)


def _dec_6b(w):
    s = w & 0x1FF
    d_ = (w >> 9) & 0x1FF
    c, z, l = (w >> 20) & 1, (w >> 19) & 1, (w >> 18) & 1

    def mk(name, fn, wc=False, wz=False, imm_d=True):
        dd = Dec(w, name, fn)
        dd.imm_d = bool(l) and imm_d
        dd.fwc = wc and bool(c)
        dd.fwz = wz and bool(z)
        return dd

    if s == 0x018:
        return mk('getqx', Cog.x_getqx, True, True, imm_d=False)
    if s == 0x019:
        return mk('getqy', Cog.x_getqy, True, True, imm_d=False)
    if s == 0x01A:
        return mk('getct', Cog.x_getct, imm_d=False)
    if s == 0x01F:
        return mk('waitx', Cog.x_waitx, True, True)
    if s == 0x024:
        if d_ == 0b000001110:
            return mk('pollatn', Cog.x_pollatn, True, True, imm_d=False)
        if d_ == 0b000011110:
            return mk('waitatn', Cog.x_waitatn, True, True, imm_d=False)
        if d_ == 0b000010001:
            return mk('waitct1', Cog.x_waitct1, True, True, imm_d=False)
        return Dec(w, 'pollwait?%03X' % d_, Cog.x_unmodelled)
    if s == 0x028:
        return mk('setq', Cog.x_setq)
    if s == 0x029:
        return mk('setq2', Cog.x_setq2)
    if s == 0x02C:
        return mk('jmp', Cog.x_jmp_d, True, True, imm_d=False)
    if s == 0x02D:
        if l:
            return mk('ret', Cog.x_ret, True, True, imm_d=False)
        return mk('call', Cog.x_call_d, True, True, imm_d=False)
    if s == 0x030:
        return mk('jmprel', Cog.x_jmprel)
    if s == 0x031:
        return mk('skip', Cog.x_skip)
    if s == 0x032:
        return mk('skipf', Cog.x_skipf)
    if s == 0x03F:
        return mk('cogatn', Cog.x_cogatn)
    if 0x040 <= s <= 0x05F:
        grp = (s >> 3) & 3
        var = s & 7
        if grp == 0 and (c ^ z):
            nm = 'testp' + ('n' if var & 1 else '')
            dd = mk(nm, Cog.x_pinop, True, True)
            if var >> 1:
                dd.frc, dd.frz = bool(c), bool(z)
            return dd
        nm = ['dir', 'out', 'flt', 'drv'][grp] + ['l', 'h', 'c', 'nc', 'z', 'nz', 'rnd', 'not'][var]
        return mk(nm, Cog.x_pinop, True, True)
    if s == 0x06C and not c and not z and not l:
        dd = mk('wrc', Cog.x_wrc, imm_d=False)
        dd.frc = True
        return dd
    if s == 0x06F and l:
        dd = mk('modcz', Cog.x_modcz, True, True, imm_d=False)
        cc, zz = (d_ >> 4) & 0xF, d_ & 0xF
        rc = rz = False
        for code, fl in ((cc, c), (zz, z)):
            if fl:
                a, b = COND_READS[code]
                rc, rz = rc or a, rz or b
        dd.frc, dd.frz = rc, rz
        return dd
    return Dec(w, 'dop?%03X' % s, Cog.x_unmodelled)


def _dec_jmp_a(w):
    d = Dec(w, 'jmp#', Cog.x_jmp_a)
    return d


def _dec_call_a(w):
    return Dec(w, 'call#', Cog.x_call_a)


def _dec_calld_a(w):
    return Dec(w, 'calld#', Cog.x_calld_a)


def _dec_augs(w):
    d = Dec(w, 'augs', Cog.x_augs)
    d.prefix = True
    return d


def _dec_augd(w):
    d = Dec(w, 'augd', Cog.x_augd)
    d.prefix = True
    return d


def _dec_rdlong(w):
    d = _czi('rdlong', Cog.x_rdlong, w)
    return d


def _dec_rdlut(w):
    return _czi('rdlut', Cog.x_rdlut, w)


_OPS = {
    0x02: _dec_shift('shr', Cog.x_shr), 0x03: _dec_shift('shl', Cog.x_shl),
    0x05: _dec_shift('rcl', Cog.x_rcl, rc=True), 0x06: _dec_shift('sar', Cog.x_sar),
    0x08: _d_simple('add', Cog.x_add), 0x09: None, 0x0A: _d_simple('adds', Cog.x_adds),
    0x0C: _d_simple('sub', Cog.x_sub), 0x0D: None, 0x0E: _d_simple('subs', Cog.x_subs),
    0x10: _d_simple('cmp', Cog.x_cmp), 0x12: _d_simple('cmps', Cog.x_cmps), 0x15: _d_simple('cmpm', Cog.x_cmpm),
    0x16: _d_simple('subr', Cog.x_subr),
    0x18: _d_simple('fge', Cog.x_fge), 0x19: _d_simple('fle', Cog.x_fle), 0x1A: _d_simple('fges', Cog.x_fges),
    0x1B: _d_simple('fles', Cog.x_fles),
    0x20: _dec_testb_family, 0x21: _dec_testb_family, 0x22: _dec_testb_family, 0x23: _dec_testb_family,
    0x24: _dec_testb_family, 0x25: _dec_testb_family, 0x26: _dec_testb_family, 0x27: _dec_testb_family,
    0x28: _d_simple('and', Cog.x_and), 0x29: _d_simple('andn', Cog.x_andn), 0x2A: _d_simple('or', Cog.x_or),
    0x2B: _d_simple('xor', Cog.x_xor),
    0x30: _d_simple('mov', Cog.x_mov), 0x31: _d_simple('not', Cog.x_not), 0x32: _d_simple('abs', Cog.x_abs),
    0x33: _d_simple('neg', Cog.x_neg), 0x34: _d_simple('negc', Cog.x_negc, frc=True),
    0x38: _d_simple('incmod', Cog.x_incmod), 0x3A: _d_simple('zerox', Cog.x_zerox),
    0x3B: _d_simple('signx', Cog.x_signx), 0x3E: _d_simple('test', Cog.x_test),
    0x42: _dec_getnib, 0x43: _dec_getnib, 0x47: _dec_getbyte, 0x49: _dec_word,
    0x4A: _dec_4a, 0x4B: _dec_4b, 0x4C: _dec_4c, 0x4E: _dec_4e,
    0x50: _dec_50, 0x51: _dec_51, 0x53: _dec_53, 0x54: _dec_54, 0x55: _dec_rdlut, 0x58: _dec_rdlong,
    0x59: _dec_59, 0x5A: _dec_5a, 0x5B: _dec_5b, 0x5C: _dec_5c, 0x5E: _dec_5e,
    0x60: _dec_60, 0x61: _dec_61, 0x63: _dec_63, 0x66: _dec_66, 0x68: _dec_68, 0x69: _dec_69, 0x6A: _dec_6a,
    0x6B: _dec_6b, 0x6C: _dec_jmp_a, 0x6D: _dec_call_a,
    0x70: _dec_calld_a, 0x71: _dec_calld_a, 0x72: _dec_calld_a, 0x73: _dec_calld_a,
    0x78: _dec_augs, 0x79: _dec_augs, 0x7A: _dec_augs, 0x7B: _dec_augs,
    0x7C: _dec_augd, 0x7D: _dec_augd, 0x7E: _dec_augd, 0x7F: _dec_augd,
}
_OPS[0x09] = lambda w: _czi('addx', Cog.x_addx, w, frc=True, frz=bool((w >> 19) & 1))
_OPS[0x0D] = lambda w: _czi('subx', Cog.x_subx, w, frc=True, frz=bool((w >> 19) & 1))


def disasm(w, pc=None):
    """A readable rendering of one decoded long (mnemonic, condition, fields) for reports."""
    op = (w >> 21) & 0x7F
    fn = _OPS.get(op)
    if w == 0:
        return 'nop'
    dec = fn(w) if fn else Dec(w, '?%02X' % op, Cog.x_unmodelled)
    cond = COND_NAMES[w >> 28]
    fx = []
    if dec.fwc and dec.fwz:
        fx.append('wcz')
    elif dec.fwc:
        fx.append('wc')
    elif dec.fwz:
        fx.append('wz')
    if dec.name in ('jmp#', 'call#', 'calld#'):
        a = w & 0xF_FFFF
        if (w >> 20) & 1 and pc is not None:
            ops = '#$%03X' % ((pc + 1 + (sx(a, 20) >> 2)) & 0xF_FFFF)
        else:
            ops = '#\\$%05X' % a
    else:
        dpart = ('#' if dec.imm_d else '') + '$%03X' % dec.d
        spart = ('#' if dec.imm_s else '') + '$%03X' % dec.s
        ops = '%s, %s' % (dpart, spart)
        if dec.name in ('tjz', 'tjnz', 'djnz', 'jnct1') and dec.imm_s and pc is not None:
            ops = '$%03X, #$%03X' % (dec.d, (pc + 1 + sx(dec.s, 9)) & 0xFFFFF)
    return ('%-12s %-8s %s %s' % (cond, dec.name, ops, ' '.join(fx))).rstrip()

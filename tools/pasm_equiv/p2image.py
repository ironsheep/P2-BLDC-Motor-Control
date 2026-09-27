"""Build a driver source with pnut-ts and read its compiled image and symbols.

The baseline comes from `git show <ref>:src/<file>`, the candidate from a source directory (the work tree's
src/ by default). Both are copied into a scratch directory this module creates, never into src/, and compiled
there with `pnut-ts -l`. The driver's bytes are taken from the .bin (located through the listing's object hex
dump, which must agree with it byte for byte); names come from the listing's symbol table and are used only for
reporting and for mapping registers between the two images by name.
"""
import os
import re
import shutil
import subprocess

M32 = 0xFFFF_FFFF
DRIVER_FILE = 'isp_bldc_motor.spin2'


class BuildError(Exception):
    pass


def find_pnut(explicit=None):
    for cand in ([explicit] if explicit else []) + [shutil.which('pnut-ts'), '/Applications/pnut_ts/pnut-ts']:
        if cand and os.path.isfile(cand) and os.access(cand, os.X_OK):
            return cand
    raise BuildError('pnut-ts not found (PATH, /Applications/pnut_ts/pnut-ts); pass --pnut PATH')


def _obj_files(text):
    """The OBJ files a source names (every `name : "file"` line, whichever #ifdef branch it sits in)."""
    return sorted(set(re.findall(r'^\s*\w+\s*:\s*"([^"]+)"', text, re.MULTILINE)))


def stage_from_git(repo, ref, dest):
    """Write <ref>:src/<driver> and the OBJ files it names into dest. Read-only on the repository."""
    os.makedirs(dest, exist_ok=True)

    def show(name):
        r = subprocess.run(['git', '-C', repo, 'show', '%s:src/%s' % (ref, name)], capture_output=True)
        if r.returncode != 0:
            return None
        return r.stdout

    main = show(DRIVER_FILE)
    if main is None:
        raise BuildError('git show %s:src/%s failed (is the ref/tag present?)' % (ref, DRIVER_FILE))
    with open(os.path.join(dest, DRIVER_FILE), 'wb') as f:
        f.write(main)
    for name in _obj_files(main.decode('utf-8', 'replace')):
        fname = name if name.endswith('.spin2') else name + '.spin2'
        data = show(fname)
        if data is not None:
            with open(os.path.join(dest, fname), 'wb') as f:
                f.write(data)
    return os.path.join(dest, DRIVER_FILE)


def stage_from_dir(srcdir, dest):
    """Copy <srcdir>/<driver> and the OBJ files it names into dest."""
    os.makedirs(dest, exist_ok=True)
    main = os.path.join(srcdir, DRIVER_FILE)
    if not os.path.isfile(main):
        raise BuildError('no %s in %s' % (DRIVER_FILE, srcdir))
    shutil.copy2(main, dest)
    with open(main, encoding='utf-8', errors='replace') as f:
        text = f.read()
    for name in _obj_files(text):
        fname = name if name.endswith('.spin2') else name + '.spin2'
        p = os.path.join(srcdir, fname)
        if os.path.isfile(p):
            shutil.copy2(p, dest)
    return os.path.join(dest, DRIVER_FILE)


def compile_driver(path, pnut):
    r = subprocess.run([pnut, '-l', path], capture_output=True, text=True)
    base = os.path.splitext(path)[0]
    if r.returncode != 0 or not os.path.isfile(base + '.lst') or not os.path.isfile(base + '.bin'):
        raise BuildError('pnut-ts -l %s failed:\n%s\n%s' % (path, r.stdout, r.stderr))
    return base + '.lst', base + '.bin'


_SYM = re.compile(r'^TYPE:\s+(\S+)\s+VALUE:\s+([0-9A-F]{8})\s+NAME:\s+(\S+)\s*$')
_HEX = re.compile(r'^([0-9A-F]{5})-\s+((?:[0-9A-F]{2}\s)+)')


class Image:
    """One compiled driver: the object bytes, the driver's symbols, and its constants."""

    def __init__(self, label, src_path, lst_path, bin_path):
        self.label = label
        self.src_path = src_path
        self.lst_path = lst_path
        self.bin_path = bin_path
        self.con = {}            # CON_INT name -> value (signed)
        self.dat = {}            # DAT symbol name (upper case, locals as GLOBAL.LOCAL) -> (cog_addr or None, hub_off)
        self.var = {}            # VAR_LONG name -> offset
        self._parse_listing()
        self._load_bin()
        with open(src_path, encoding='utf-8', errors='replace') as f:
            self.source = f.read()
        self._index()

    # ---- listing ----
    def _parse_listing(self):
        obj = bytearray()
        last_global = None
        in_dump = False
        with open(self.lst_path, encoding='utf-8', errors='replace') as f:
            for line in f:
                m = _SYM.match(line)
                if m:
                    typ, val, name = m.group(1), int(m.group(2), 16), m.group(3)
                    if typ == 'CON_INT':
                        self.con[name] = val - (1 << 32) if val & 0x8000_0000 else val
                    elif typ.startswith('DAT_'):
                        cog = val >> 20
                        hub = val & 0xF_FFFF
                        if "'" in name:
                            local = name.split("'")[0]
                            key = '%s.%s' % (last_global, local) if last_global else local
                        else:
                            key = name
                            last_global = name
                        self.dat[key] = (None if cog == 0xFFF else cog, hub, typ)
                    elif typ == 'VAR_LONG':
                        self.var[name] = val
                    continue
                if line.startswith('OBJ bytes:'):
                    in_dump = True
                    continue
                if in_dump:
                    h = _HEX.match(line)
                    if h:
                        off = int(h.group(1), 16)
                        data = bytes(int(b, 16) for b in h.group(2).split())
                        if off != len(obj):
                            if off < len(obj):
                                continue
                            obj.extend(b'\0' * (off - len(obj)))
                        obj.extend(data)
        if 'DRIVER' not in self.dat:
            raise BuildError('%s: no DRIVER symbol in the listing' % self.lst_path)
        self.obj_listing = bytes(obj)

    def _load_bin(self):
        with open(self.bin_path, 'rb') as f:
            binary = f.read()
        drv = self.dat['DRIVER'][1]
        probe = self.obj_listing[drv:drv + 64]
        at = binary.find(probe)
        if at < 0:
            raise BuildError('%s: the listing\'s driver bytes are not in the .bin' % self.label)
        base = at - drv
        n = len(self.obj_listing)
        from_bin = binary[base:base + n]
        if from_bin != self.obj_listing:
            raise BuildError('%s: the .bin and the listing hex dump disagree' % self.label)
        self.obj = from_bin
        self.bin_obj_offset = base

    # ---- lookups ----
    def _index(self):
        drv_hub = self.dat['DRIVER'][1]
        self.driver_hub = drv_hub
        self.cog_names = {}      # cog addr -> [names]   (org-0 image, $000..$1FF)
        self.cog_sym = {}        # NAME -> cog addr (org-0 symbols only)
        self.hub_names = []      # sorted (hub_off, name) for every driver-region symbol, for naming PCs
        for name, (cog, hub, typ) in self.dat.items():
            if cog is None:
                continue
            if typ != 'DAT_LONG_RES':
                self.hub_names.append((hub, name))       # RES symbols occupy no hub bytes
            if cog < 0x200:
                self.cog_sym[name] = cog
                self.cog_names.setdefault(cog, []).append(name)
        self.hub_names.sort()
        self._hub_keys = [h for h, _ in self.hub_names]

    def sym_cog(self, name):
        return self.cog_sym.get(name.upper())

    def sym_hub(self, name):
        v = self.dat.get(name.upper())
        return None if v is None else v[1]

    def sym_addr(self, name):
        """The org address (cog/LUT) of a symbol, whichever org it is under."""
        v = self.dat.get(name.upper())
        return None if v is None else v[0]

    def long_at(self, hub_off):
        return int.from_bytes(self.obj[hub_off:hub_off + 4], 'little')

    def name_for_hub(self, hub_off):
        """'LABEL+n' for a hub byte offset inside the object."""
        import bisect
        i = bisect.bisect_right(self._hub_keys, hub_off) - 1
        if i < 0:
            return '$%05X' % hub_off
        # prefer a code label over a same-address alias only for readability: take the first listed
        h, n = self.hub_names[i]
        d = (hub_off - h) // 4
        return n if d == 0 else '%s+%d' % (n, d)

    def usage(self):
        """Cog / LUT / overlay use as the listing gives it (the `fit` figures)."""
        out = {}
        out['cog_used'] = max(self.cog_sym.values()) + 1
        s, e = self.sym_addr('LUTCODESTART'), self.sym_addr('LUTCODEEND')
        if s is not None and e is not None:
            out['lut_resident_end'] = e
            out['lut_used'] = e - s
        s, e = self.sym_addr('PLANOVLSTART'), self.sym_addr('PLANOVLEND')
        if s is not None and e is not None:
            out['overlay_used'] = e - s
        return out


def build_image(label, stage_dir, pnut, git_ref=None, repo=None, srcdir=None):
    if git_ref is not None:
        path = stage_from_git(repo, git_ref, stage_dir)
    else:
        path = stage_from_dir(srcdir, stage_dir)
    lst, binp = compile_driver(path, pnut)
    return Image(label, path, lst, binp)

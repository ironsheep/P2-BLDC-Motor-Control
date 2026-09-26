#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
serial_certify.py -- host-side certification of the P2 serial control path (PL-148)

WHAT IT PROVES
  The serial top level (src/isp_steering_serial.spin2) answers a real host as DRIVE-OBJECTS-SERIAL.md says, on
  the dual-motor platform. Five cells, each printed as a SIGNOFF verdict line in the bench logs' shape:

    R20-SER-ERRREPLY   an out-of-range command is refused with an ERROR naming the value and its range; a command
                       the drive refuses (a drive while e-stopped) is refused with "ERROR {cmd} failed: {NAME} ({code})";
                       valid commands reply OK
    R20-SER-TIMEOUT    settimeout {ms} then silence stops a drivepwr drive AND a drivedist drive within ms + a rest
                       bound, with stop reason SR_LINK_LOST (46) and ERR_COMMAND_TIMEOUT (-1019) from geterror; drive
                       commands re-sent inside ms keep it running
    R20-SER-VOLT       getvoltage returns the configured PWR_* number and its nominal mV
    R20-SER-FAULTRESP  getfaultresp reads FR_GRADED (1) at 10 % after start; setfaultresp round-trips; refused values
                       change nothing
    R20-SER-PROTCLEAR  with no protective stop latched, getprot reads 0 0 and protclear is harmless (it does not
                       release a user's e-stop). The latched half is NOMEAS: it needs a provoked protective stop (PL-106)

PRECONDITION
  - WHEELS UP (platform on blocks, both wheels free) and HANDS OFF for the whole run. The wheels turn at power 30.
  - The P2 runs src/isp_steering_serial.spin2 (the dual-motor serial top level), built at DRIVER_REV 32 or later.
  - Wired as SERIAL-CONTROL.md describes: host Tx -> P2 pin 57, host Rx <- P2 pin 56, grounds joined, 624,000 baud.
  - Best: start this script, THEN reset/power the P2, so the script sees the P2's "ident:" line and the fault-response
    default is read from a fresh start. A P2 already waiting for its ident answer also counts as fresh.
  - Pass --drive-voltage with the DRIVE_VOLTAGE of the user configuration the P2 was built with (e.g. PWR_18p5V).

HOW LONG
  About 3 minutes. The P2's command loop sleeps up to 1 s when its queue is empty, so each command costs up to ~1 s;
  the three timeout cases add about 45 s of timed motion and silence.

PANIC PROCEDURE
  Physically disconnect the drive battery. Ctrl-C makes the script send "stopmotors" and "settimeout 0" on the way
  out, but do not rely on that. While a timeout case is driving, the P2's own command timeout (5 s) is on, so a
  dead host stops the wheels by itself.

USAGE
  ./serial_certify.py --drive-voltage PWR_18p5V            # /dev/serial0 at 624000 (the demo's defaults)
  ./serial_certify.py --port /dev/ttyUSB0 --baud 624000 --drive-voltage PWR_12p0V
  ./serial_certify.py --dry-run                            # print the planned command sequence; no port is opened

OUTPUT
  Every line sent and received, with a host timestamp, goes to serial-certify_<YYMMDD-HHMMSS>.log beside this script
  (none in a dry run). The SIGNOFF lines are printed to the console and written to the same log.
"""

import argparse
import os
import re
import sys
import time
from datetime import datetime

SCRIPT_VERSION = "1.0.0"

# -----------------------------------------------------------------------------
# Values copied from the P2 source. Keep in sync with src/isp_bldc_motor.spin2 and src/isp_steering_serial.spin2.
# -----------------------------------------------------------------------------
DEFAULT_PORT = "/dev/serial0"       # P2-BLDC-Motor-Control-Demo.py
DEFAULT_BAUD = 624000               # GW_BAUDRATE in isp_steering_serial.spin2

# ERR_* names and codes (isp_bldc_motor.spin2 CON), as errorName() in isp_steering_serial.spin2 names them
ERR_CODES = {
    "ERR_BAD_PIN_GROUP": -1001, "ERR_PIN_GROUP_IN_USE": -1002, "ERR_BAD_VOLTAGE": -1003,
    "ERR_BAD_DETECT_MODE": -1004, "ERR_NO_FREE_COG": -1005, "ERR_ABI_MISMATCH": -1006,
    "ERR_NOT_STARTED": -1007, "ERR_NO_SENSE_TASK": -1008, "ERR_BAD_UNITS": -1009, "ERR_BAD_COUNT": -1010,
    "ERR_NO_WHEEL_DIA": -1011, "ERR_LIMIT_UNRESOLVABLE": -1012, "ERR_SYNC_TIMEOUT": -1013, "ERR_BUSY": -1014,
    "ERR_FAULT_NOT_CLEARED": -1015, "ERR_EMERGENCY_STOPPED": -1016, "ERR_NO_RESPONSE": -1017,
    "ERR_BOARD_NOT_DETECTED": -1018, "ERR_COMMAND_TIMEOUT": -1019, "ERR_START_CHECK_FAILED": -1020,
    "ERR_PROTECTIVE_STOP": -2000, "ERR_PLATFORM_BLOCKED": -2001,
}

# PWR_* enum (isp_bldc_motor_userconfig.spin2) and nominalMilliVolts() (isp_bldc_motor.spin2)
PWR_ENUM = {"PWR_6p0V": 1, "PWR_7p4V": 2, "PWR_11p1V": 3, "PWR_12p0V": 4, "PWR_14p8V": 5,
            "PWR_18p5V": 6, "PWR_22p2V": 7, "PWR_24p0V": 8, "PWR_25p9V": 9}
PWR_NOMINAL_MV = {1: 6000, 2: 7400, 3: 11100, 4: 12000, 5: 14800, 6: 18500, 7: 22200, 8: 24000, 9: 25900}

DS_MOVING, DS_HOLDING, DS_OFF, DS_FAULTED, DS_ESTOP = 11, 12, 13, 14, 15
AT_REST = (DS_HOLDING, DS_OFF)
SR_NONE, SR_LINK_LOST = 40, 46
FR_SHIPPED, FR_GRADED, BRAKE_PCT_DEFAULT = 0, 1, 10
DRU_HALL_TICKS, DDU_M = 1, 5
MAX_SPEED_DEFAULT = 75              # setMaxSpeedForDistance() default, restored after the bounded case

# -----------------------------------------------------------------------------
# Test constants
# -----------------------------------------------------------------------------
REPLY_TIMEOUT_S = 3.0       # the P2 loop sleeps up to 1 s with an empty queue, plus the front cog's bounded answer
DRIVE_POWER = 30            # gentle, wheels up
TIMEOUT_MS = 5000           # settimeout value. Must exceed the P2's ~1 s idle sleep plus the getters read after the
                            #  last drive in the negative case (three getters at up to ~1 s each)
REST_BOUND_MS = 2500        # ramp down to rest after the timeout fires. DRIVE-OBJECTS.md: from top speed (441 ticks/s)
                            #  the ramp takes ~380 ticks, about 1.7 s; power 30 takes far less. 2.5 s covers full speed
MID_POLL_S = 1.0            # when the "still running before the timeout" getstatus is sent after the drive
RESEND_S = 0.5              # the negative case re-sends a drive at least this often (the P2's latency sets the real gap)
RESEND_SPAN_MS = 3 * TIMEOUT_MS
STILL_TICKS = 2             # at rest: hall ticks either wheel may move across the 1 s stillness check
MIN_MOVE_TICKS = 10         # it ran: hall ticks each wheel must have moved
DIST_SPEED = 30             # setspeedfordist for the bounded case
DIST_METERS = 20            # far beyond what the wheels cover before the timeout (~2.5 m/s top speed x 5 s < 20 m)

SF_VERSION = 1
SF_BIN = "SERIAL"
CELLS = ["R20-SER-FAULTRESP", "R20-SER-VOLT", "R20-SER-PROTCLEAR", "R20-SER-ERRREPLY", "R20-SER-TIMEOUT"]


class LinkDead(Exception):
    """The P2 stopped answering, or reset mid-run: the remaining cells cannot be judged."""


def fmt(value):
    """Format a SIGNOFF field as the bench logs do: ints grouped with '_', booleans TRUE/FALSE, None as NA."""
    if value is None:
        return "NA"
    if isinstance(value, bool):
        return "TRUE" if value else "FALSE"
    if isinstance(value, int):
        return "{:_}".format(value)
    return str(value)


class Log:
    """Console plus the timestamped log file. A dry run writes no file."""

    def __init__(self, path):
        self.path = path
        self.fh = open(path, "w", encoding="utf-8") if path else None

    def line(self, text, console=False):
        stamp = datetime.now().isoformat(timespec="milliseconds")
        if self.fh:
            self.fh.write("[{}] HOST  {}\n".format(stamp, text))
            self.fh.flush()
        if console or self.fh is None:
            print(text, flush=True)

    def close(self):
        if self.fh:
            self.fh.close()


class Link:
    """One command, one reply, logged both ways. In a dry run it prints the plan and returns no replies."""

    def __init__(self, log, port, baud, dry):
        self.log = log
        self.port_name = port
        self.baud = baud
        self.dry = dry
        self.ser = None
        self.buf = b""
        self.silent_misses = 0

    def open(self):
        if self.dry:
            self.log.line("PLAN open {} at {} baud".format(self.port_name, self.baud))
            return
        import serial                               # pyserial, as P2-BLDC-Motor-Control-Demo.py uses
        self.ser = serial.Serial(self.port_name, self.baud, timeout=0.05)
        self.log.line("SER-OPEN,port,{},baud,{}".format(self.port_name, self.baud))

    def close(self):
        if self.ser:
            self.ser.close()

    def _send_raw(self, text):
        self.log.line("TX  {}".format(text))
        self.ser.write((text + "\n").encode("utf-8"))

    def _read_line(self, deadline):
        # a line ends with LF (sendOK / sendResponse / sendError in isp_queue_serial.spin2)
        while True:
            if b"\n" in self.buf:
                raw, self.buf = self.buf.split(b"\n", 1)
                return raw.decode("utf-8", "replace").rstrip("\r")
            if time.monotonic() >= deadline:
                return None
            chunk = self.ser.read(self.ser.in_waiting or 1)
            if chunk:
                self.buf += chunk

    def _answer_ident(self, text):
        # the P2 announces itself at start and blocks until the host answers (isp_host_serial.spin2 identify())
        self.log.line("RX  {}".format(text))
        self._send_raw("fident:status=True")

    def handshake(self, wait_s):
        """Return T/F where T means the P2 had processed no command before this run (a fresh start)."""
        if self.dry:
            self.log.line("PLAN wait up to {} s for the P2's 'ident:' line; answer 'fident:status=True'".format(wait_s))
            self.log.line("PLAN if none: send 'fident:status=True' once; no reply within 2.5 s means fresh")
            return True
        deadline = time.monotonic() + wait_s
        print("Waiting up to {} s for the P2 to announce itself (reset the P2 now for a fresh start)...".format(wait_s))
        while time.monotonic() < deadline:
            text = self._read_line(deadline)
            if text is None:
                break
            if text.startswith("ident:"):
                self._answer_ident(text)
                self.log.line("SER-IDENT,seen,TRUE,fresh,TRUE", console=True)
                return True
            if text:
                self.log.line("RX-STRAY  {}".format(text))
        # no ident: either the P2 already waits for our answer (fresh) or it is past it (not fresh)
        self._send_raw("fident:status=True")
        text = self._read_line(time.monotonic() + 2.5)
        if text is None:
            self.log.line("SER-IDENT,seen,FALSE,fresh,TRUE", console=True)
            return True
        self.log.line("RX  {}".format(text))
        self.log.line("SER-IDENT,seen,FALSE,fresh,FALSE", console=True)
        return False

    def cmd(self, text):
        """Send one command and return its one reply line, or None (dry run, or no reply in REPLY_TIMEOUT_S)."""
        if self.dry:
            self.log.line("PLAN TX  {}".format(text))
            return None
        # anything already waiting is not this command's reply
        while self.ser.in_waiting or b"\n" in self.buf:
            stray = self._read_line(time.monotonic() + 0.1)
            if stray is None:
                break
            if stray.startswith("ident:"):
                self._answer_ident(stray)
                raise LinkDead("P2_RESET_MID_RUN")
            if stray:
                self.log.line("RX-STRAY  {}".format(stray))
        self._send_raw(text)
        deadline = time.monotonic() + REPLY_TIMEOUT_S
        while True:
            reply = self._read_line(deadline)
            if reply is None:
                self.log.line("RX-NONE  (no reply in {} s to '{}')".format(REPLY_TIMEOUT_S, text))
                self.silent_misses += 1
                if self.silent_misses >= 3:
                    raise LinkDead("NO_REPLIES")
                return None
            if reply.startswith("ident:"):
                self._answer_ident(reply)
                raise LinkDead("P2_RESET_MID_RUN")
            if reply == "":
                continue
            self.silent_misses = 0
            self.log.line("RX  {}".format(reply))
            return reply

    def wait_until(self, t_abs, t_ref, label):
        """Stay silent until monotonic time t_abs; t_ref is the moment the plan's offset is counted from."""
        if self.dry:
            self.log.line("PLAN silent until +{} ms after {}".format(int(round((t_abs - t_ref) * 1000)), label))
            return
        remain = t_abs - time.monotonic()
        if remain > 0:
            time.sleep(remain)

    def pause(self, seconds, label):
        if self.dry:
            self.log.line("PLAN silent {} ms ({})".format(int(seconds * 1000), label))
            return
        time.sleep(seconds)


def is_ok(reply):
    return reply == "OK"


def nums(reply, prefix, count):
    """Parse '{prefix} n1 .. n{count}'; return the ints, or None when the reply is not that shape."""
    if reply is None:
        return None
    parts = reply.split()
    if len(parts) != count + 1 or parts[0] != prefix:
        return None
    try:
        return [int(p) for p in parts[1:]]
    except ValueError:
        return None


class Cell:
    """One cell's verdict lines. A cell PASSes only when every crit line it emits PASSes."""

    def __init__(self, cell_id, task):
        self.cell_id = cell_id
        self.task = task
        self.lines = []

    def _emit(self, motor, crit, measured, lo, hi, units, n, verdict):
        self.lines.append("SIGNOFF,sf,{},bin,{},cell,{},task,{},motor,{},crit,{},measured,{},lo,{},hi,{},units,{},n,{},verdict,{}".format(
            SF_VERSION, SF_BIN, self.cell_id, self.task, motor, crit, fmt(measured), fmt(lo), fmt(hi), units, n, verdict))

    def judge(self, motor, crit, measured, lo, hi, units, n=1):
        """PASS when measured is within [lo, hi] (BOOL: equals lo); FAIL otherwise, including when nothing was read."""
        if measured is None:
            verdict = "FAIL"
        elif isinstance(measured, bool):
            verdict = "PASS" if measured == lo else "FAIL"
        else:
            verdict = "PASS" if lo <= measured <= hi else "FAIL"
        self._emit(motor, crit, measured, lo, hi, units, n, verdict)

    def nomeas(self, motor, crit, lo, hi, units, why, log):
        log.line("SER-NOMEAS,cell,{},crit,{},why,{}".format(self.cell_id, crit, why))
        self._emit(motor, crit, None, lo, hi, units, 0, "NOMEAS")


# -----------------------------------------------------------------------------
# The cells
# -----------------------------------------------------------------------------

def cell_faultresp(link, cell, fresh, log):
    # Claim: the default after start is FR_GRADED (1) at 10 (DRIVER_REV 31); setfaultresp round-trips through getfaultresp.
    # NEGATIVE: a refused setfaultresp (mode 2, pct 101) must leave getfaultresp unchanged, and the two round trips use
    #  different values (0/50, then 1/25) so a getter that echoed a constant, or the default, would FAIL.
    first = nums(link.cmd("getfaultresp"), "faultresp", 2)
    if fresh:
        cell.judge("NONE", "DEFAULT_MODE_GRADED", first[0] if first else None, FR_GRADED, FR_GRADED, "ENUM")
        cell.judge("NONE", "DEFAULT_BRAKE_PCT", first[1] if first else None, BRAKE_PCT_DEFAULT, BRAKE_PCT_DEFAULT, "PCT")
    else:
        cell.nomeas("NONE", "DEFAULT_MODE_GRADED", FR_GRADED, FR_GRADED, "ENUM", "NOT_FRESH_START", log)
        cell.nomeas("NONE", "DEFAULT_BRAKE_PCT", BRAKE_PCT_DEFAULT, BRAKE_PCT_DEFAULT, "PCT", "NOT_FRESH_START", log)

    misses = 0
    for mode, pct in ((FR_SHIPPED, 50), (FR_GRADED, 25)):
        if not is_ok(link.cmd("setfaultresp {} {}".format(mode, pct))):
            misses += 1
        if nums(link.cmd("getfaultresp"), "faultresp", 2) != [mode, pct]:
            misses += 1
    cell.judge("NONE", "SET_GET_MISMATCHES", misses, 0, 0, "COUNT", n=2)

    # refused values: an ERROR reply, and the value in effect (1 25) unchanged
    bad = 0
    for mode, pct in ((2, 10), (FR_GRADED, 101)):
        reply = link.cmd("setfaultresp {} {}".format(mode, pct))
        if reply is None or not reply.startswith("ERROR "):
            bad += 1
        if nums(link.cmd("getfaultresp"), "faultresp", 2) != [FR_GRADED, 25]:
            bad += 1
    cell.judge("NONE", "REFUSED_CHANGED_NOTHING", bad, 0, 0, "COUNT", n=2)

    # restore the default, and read it back
    restored = is_ok(link.cmd("setfaultresp {} {}".format(FR_GRADED, BRAKE_PCT_DEFAULT)))
    restored = (nums(link.cmd("getfaultresp"), "faultresp", 2) == [FR_GRADED, BRAKE_PCT_DEFAULT]) and restored
    cell.judge("NONE", "DEFAULT_RESTORED", restored, True, True, "BOOL")


def cell_volt(link, cell, expected_enum, log):
    # Claim (DRIVE-OBJECTS-SERIAL.md): "volt {pwrEnum} {milliVolts}", the configured PWR_* number and its nominal mV.
    # NEGATIVE: a P2 built for another voltage, or a wrong mV table entry, reads a different number and FAILs; the
    #  configured value comes from the owner (--drive-voltage), not from the reply, so a reply cannot pass by itself.
    reply = nums(link.cmd("getvoltage"), "volt", 2)
    got_enum = reply[0] if reply else None
    got_mv = reply[1] if reply else None
    if expected_enum is None:
        cell.nomeas("NONE", "ENUM_IS_CONFIGURED", "NA", "NA", "ENUM", "NO_DRIVE_VOLTAGE_ARG", log)
        want_mv = PWR_NOMINAL_MV.get(got_enum) if got_enum is not None else None
    else:
        cell.judge("NONE", "ENUM_IS_CONFIGURED", got_enum, expected_enum, expected_enum, "ENUM")
        want_mv = PWR_NOMINAL_MV[expected_enum]
    if want_mv is None:
        cell.judge("NONE", "MV_IS_NOMINAL", got_mv, 0, -1, "MV")      # an unknown enum cannot pass
    else:
        cell.judge("NONE", "MV_IS_NOMINAL", got_mv, want_mv, want_mv, "MV")


def cell_protclear(link, cell, log):
    # Claim: with no protective stop latched, getprot reads "prot 0 0" and protclear replies OK and changes nothing.
    # NEGATIVE: protclear must not release a user's e-stop (only emerclear does): after emercutoff + protclear a drive
    #  is still refused with ERR_EMERGENCY_STOPPED. A protclear that released everything would FAIL here.
    before = nums(link.cmd("getprot"), "prot", 2)
    clear_ok = is_ok(link.cmd("protclear"))
    after = nums(link.cmd("getprot"), "prot", 2)
    stat = nums(link.cmd("getstatus"), "stat", 2)
    drive_ok = is_ok(link.cmd("drivepwr 0 0"))
    cell.judge("NONE", "GETPROT_NONE", before == [0, 0] and after == [0, 0], True, True, "BOOL", n=2)
    cell.judge("NONE", "PROTCLEAR_HARMLESS",
               clear_ok and stat is not None and all(s in AT_REST for s in stat) and drive_ok, True, True, "BOOL")

    # the e-stop is taken at rest, so its hard stop moves nothing
    estop_ok = is_ok(link.cmd("emercutoff"))
    clear2_ok = is_ok(link.cmd("protclear"))
    refused = link.cmd("drivepwr 10 10")
    if is_ok(refused):
        link.cmd("stopmotors")                       # it drove: stop it before anything else
    kept = refused is not None and refused.endswith("ERR_EMERGENCY_STOPPED (-1016)")
    link.cmd("emerclear")
    cell.judge("NONE", "PROTCLEAR_KEEPS_ESTOP", estop_ok and clear2_ok and kept, True, True, "BOOL")

    cell.nomeas("BOTH", "LATCHED_STOP_RELEASED", True, True, "BOOL", "NEEDS_PROVOKED_PROTECTIVE_STOP_PL-106", log)


ERR_REPLY_RE = re.compile(r"^ERROR (\S+) failed: (ERR_[A-Z_]+) \((-?\d+)\)$")


def cell_errreply(link, cell, log):
    # Claim (DRIVE-OBJECTS-SERIAL.md, "An ERROR reply comes in one of two forms"): an out-of-range value is refused
    #  naming the value and its range; a command the drive refuses replies "ERROR {cmd} failed: {ERR_NAME} ({code})".
    # NEGATIVE: the in-range twin of each refused command replies OK (drivepwr 0 0 before the e-stop, and again after
    #  emerclear), so a link that answered ERROR to everything would FAIL.
    oks = []
    oks.append(is_ok(link.cmd("drivepwr 0 0")))

    rng = link.cmd("drivepwr 150 0")
    range_named = rng is not None and rng.startswith("ERROR ") and "(150)" in rng and "[-100, 100]" in rng
    cell.judge("NONE", "RANGE_NAMES_VALUE", range_named, True, True, "BOOL")

    oks.append(is_ok(link.cmd("emercutoff")))       # at rest: nothing moves
    refused = link.cmd("drivepwr 10 10")
    if is_ok(refused):
        link.cmd("stopmotors")
    match = ERR_REPLY_RE.match(refused) if refused else None
    code = int(match.group(3)) if match else None
    name_ok = bool(match) and match.group(1) == "drivepwr" and match.group(2) == "ERR_EMERGENCY_STOPPED" \
        and ERR_CODES.get(match.group(2)) == code
    cell.judge("NONE", "REFUSAL_CODE", code, ERR_CODES["ERR_EMERGENCY_STOPPED"], ERR_CODES["ERR_EMERGENCY_STOPPED"], "CODE")
    cell.judge("NONE", "REFUSAL_NAMES_CMD_AND_ERR", name_ok, True, True, "BOOL")

    oks.append(is_ok(link.cmd("emerclear")))
    oks.append(is_ok(link.cmd("drivepwr 0 0")))
    cell.judge("NONE", "VALID_NOT_OK", sum(1 for ok in oks if not ok), 0, 0, "COUNT", n=len(oks))


def stopped_checks(link, label):
    """After the bound: return (at_rest, stop reasons, first geterror code, rotation after), reading only getters."""
    stat = nums(link.cmd("getstatus"), "stat", 2)
    pwr = nums(link.cmd("getpwr"), "pwr", 2)
    reason = nums(link.cmd("getstopreason"), "stopreason", 2)
    err = nums(link.cmd("geterror"), "err", 3)
    rot1 = nums(link.cmd("getrot {}".format(DRU_HALL_TICKS)), "rot", 2)
    link.pause(1.0, "stillness check, " + label)
    rot2 = nums(link.cmd("getrot {}".format(DRU_HALL_TICKS)), "rot", 2)
    still = rot1 is not None and rot2 is not None and all(abs(b - a) <= STILL_TICKS for a, b in zip(rot1, rot2))
    at_rest = stat is not None and all(s in AT_REST for s in stat) and pwr == [0, 0] and still
    return at_rest, reason, (err[0] if err else None), rot1


def moved(before, after):
    if before is None or after is None:
        return False
    return all(abs(b - a) >= MIN_MOVE_TICKS for a, b in zip(before, after))


def cell_timeout(link, cell, log):
    # Claim (DRIVE-OBJECTS-SERIAL.md settimeout): with the guard on, a driven platform not sent a drive command within
    #  {ms} stops; per the 2026-09-26 ruling (PL-143, "no carve-outs", DRIVER_REV 32) a drivedist is watched too.
    # How it is judged: only getters are sent during the silence. Source check: in isp_steering_2wheel.spin2 only
    #  REQ_DRIVE / REQ_DRIVE_DISTANCE (frontWatchCommand) and REQ_SET_TIMEOUT touch lastDriveMs; getstatus, getpwr,
    #  getstopreason, geterror and getrot read status directly and post no request, so they cannot refresh the timeout.
    # NEGATIVE: the same drive re-sent inside {ms} for 3 x {ms} keeps running: status DS_MOVING throughout, stop reason
    #  still SR_NONE (40), no ERR_COMMAND_TIMEOUT, and the wheels advanced. A guard that fired regardless would FAIL it.
    T = TIMEOUT_MS
    bound_s = (T + REST_BOUND_MS) / 1000.0
    log.line("SER-TIMEOUT-PLAN,timeout_ms,{},rest_bound_ms,{},power,{},resend_s,{},span_ms,{}".format(
        T, REST_BOUND_MS, DRIVE_POWER, RESEND_S, RESEND_SPAN_MS))

    # --- positive, open-ended: drivepwr then silence
    link.cmd("geterror")                                           # drain: the next report is this case's own
    rot0 = nums(link.cmd("getrot {}".format(DRU_HALL_TICKS)), "rot", 2)
    set_ok = is_ok(link.cmd("settimeout {}".format(T)))
    t_send = time.monotonic()
    drove = is_ok(link.cmd("drivepwr {} {}".format(DRIVE_POWER, DRIVE_POWER)))
    link.wait_until(t_send + MID_POLL_S, t_send, "drivepwr")
    mid = nums(link.cmd("getstatus"), "stat", 2)
    running = set_ok and drove and mid == [DS_MOVING, DS_MOVING]
    link.wait_until(t_send + bound_s, t_send, "drivepwr (timeout + rest bound)")
    at_rest, reason, err0, rot1 = stopped_checks(link, "drivepwr")
    cell.judge("BOTH", "PWR_RUNNING_BEFORE_MS", running and moved(rot0, rot1), True, True, "BOOL")
    cell.judge("BOTH", "PWR_AT_REST_BY_BOUND", at_rest, True, True, "BOOL")
    cell.judge("BOTH", "PWR_REASON_LINK_LOST", reason == [SR_LINK_LOST, SR_LINK_LOST], True, True, "BOOL")
    cell.judge("NONE", "PWR_ERR_TIMEOUT", err0, ERR_CODES["ERR_COMMAND_TIMEOUT"], ERR_CODES["ERR_COMMAND_TIMEOUT"], "CODE")
    link.cmd("stopmotors")

    # --- negative: the same drive re-sent inside {ms}
    link.cmd("geterror")
    rot0 = nums(link.cmd("getrot {}".format(DRU_HALL_TICKS)), "rot", 2)
    set_ok = is_ok(link.cmd("settimeout {}".format(T)))
    t_start = time.monotonic()
    t_last = None
    max_gap_ms = 0
    iterations = 0
    all_ok = set_ok
    while True:
        t_now = time.monotonic()
        if t_last is not None:
            max_gap_ms = max(max_gap_ms, int((t_now - t_last) * 1000))
        t_last = t_now
        all_ok = is_ok(link.cmd("drivepwr {} {}".format(DRIVE_POWER, DRIVE_POWER))) and all_ok
        all_ok = (nums(link.cmd("getstatus"), "stat", 2) == [DS_MOVING, DS_MOVING]) and all_ok
        iterations += 1
        if link.dry:
            link.log.line("PLAN repeat the two lines above, a drive at least every {} ms, for {} ms".format(
                int(RESEND_S * 1000), RESEND_SPAN_MS))
            break
        if time.monotonic() - t_start >= RESEND_SPAN_MS / 1000.0:
            break
        link.wait_until(t_last + RESEND_S, t_last, "the last drive")
    reason = nums(link.cmd("getstopreason"), "stopreason", 2)
    err = nums(link.cmd("geterror"), "err", 3)
    rot1 = nums(link.cmd("getrot {}".format(DRU_HALL_TICKS)), "rot", 2)
    checked_in_ms = link.dry or (time.monotonic() - t_last) * 1000 < T
    link.cmd("stopmotors")
    cell.judge("BOTH", "RESEND_MAX_GAP", max_gap_ms, 0, T - 1, "MS", n=iterations)
    if checked_in_ms:
        still_running = all_ok and reason == [SR_NONE, SR_NONE] and moved(rot0, rot1)
        cell.judge("BOTH", "RESEND_KEPT_RUNNING", still_running, True, True, "BOOL", n=iterations)
        cell.judge("NONE", "RESEND_NO_TIMEOUT_ERR", err[0] if err else None, 0, 0, "CODE")
    else:
        # the getters after the last drive outlasted the timeout, so a stop now would not be a failure of the guard
        cell.nomeas("BOTH", "RESEND_KEPT_RUNNING", True, True, "BOOL", "CHECKS_OUTLASTED_TIMEOUT", log)
        cell.nomeas("NONE", "RESEND_NO_TIMEOUT_ERR", 0, 0, "CODE", "CHECKS_OUTLASTED_TIMEOUT", log)
    link.pause(REST_BOUND_MS / 1000.0, "ramp down after stopmotors")

    # --- positive, bounded: drivedist far beyond reach, then silence (no carve-outs, DRIVER_REV 32)
    link.cmd("geterror")
    spd_ok = is_ok(link.cmd("setspeedfordist {}".format(DIST_SPEED)))
    set_ok = is_ok(link.cmd("settimeout {}".format(T)))
    t_send = time.monotonic()
    drove = is_ok(link.cmd("drivedist {} {} {}".format(DIST_METERS, DIST_METERS, DDU_M)))   # resets tracking
    link.wait_until(t_send + MID_POLL_S, t_send, "drivedist")
    mid = nums(link.cmd("getstatus"), "stat", 2)
    running = spd_ok and set_ok and drove and mid == [DS_MOVING, DS_MOVING]
    link.wait_until(t_send + bound_s, t_send, "drivedist (timeout + rest bound)")
    at_rest, reason, err0, rot1 = stopped_checks(link, "drivedist")
    cell.judge("BOTH", "DIST_RUNNING_BEFORE_MS", running and moved([0, 0], rot1), True, True, "BOOL")
    cell.judge("BOTH", "DIST_AT_REST_BY_BOUND", at_rest, True, True, "BOOL")
    cell.judge("BOTH", "DIST_REASON_LINK_LOST", reason == [SR_LINK_LOST, SR_LINK_LOST], True, True, "BOOL")
    cell.judge("NONE", "DIST_ERR_TIMEOUT", err0, ERR_CODES["ERR_COMMAND_TIMEOUT"], ERR_CODES["ERR_COMMAND_TIMEOUT"], "CODE")
    link.cmd("stopmotors")
    link.cmd("settimeout 0")                                      # off, as the serial top level leaves it
    link.cmd("setspeedfordist {}".format(MAX_SPEED_DEFAULT))


# -----------------------------------------------------------------------------
# Main
# -----------------------------------------------------------------------------

def parse_voltage(text):
    if text is None:
        return None
    if text in PWR_ENUM:
        return PWR_ENUM[text]
    if text.isdigit() and int(text) in PWR_NOMINAL_MV:
        return int(text)
    raise SystemExit("--drive-voltage: expected one of {} or its number 1-9".format(", ".join(PWR_ENUM)))


def main():
    parser = argparse.ArgumentParser(description="Certify the P2 serial control path (PL-148). Wheels up, hands off.")
    parser.add_argument("--port", default=DEFAULT_PORT, help="serial port (default {})".format(DEFAULT_PORT))
    parser.add_argument("--baud", type=int, default=DEFAULT_BAUD, help="baud rate (default {})".format(DEFAULT_BAUD))
    parser.add_argument("--drive-voltage", help="the DRIVE_VOLTAGE the P2 was built with, e.g. PWR_18p5V")
    parser.add_argument("--task", default="NA", help="todo task id for the SIGNOFF lines' task field (default NA)")
    parser.add_argument("--ident-wait", type=float, default=10.0, help="seconds to wait for the P2's ident line")
    parser.add_argument("--dry-run", action="store_true", help="print the planned command sequence; open no port")
    args = parser.parse_args()
    expected_enum = parse_voltage(args.drive_voltage)

    log_path = None
    if not args.dry_run:
        here = os.path.dirname(os.path.abspath(__file__))
        log_path = os.path.join(here, "serial-certify_{}.log".format(datetime.now().strftime("%y%m%d-%H%M%S")))
    log = Log(log_path)
    link = Link(log, args.port, args.baud, args.dry_run)

    log.line("SER-BANNER,script,serial_certify.py,ver,{},port,{},baud,{},drive_voltage,{},dry_run,{}".format(
        SCRIPT_VERSION, args.port, args.baud, args.drive_voltage or "NA", fmt(args.dry_run)), console=True)
    for cell_id in CELLS:
        log.line("SIGNOFF-DECL,sf,{},bin,{},cell,{},task,{}".format(SF_VERSION, SF_BIN, cell_id, args.task), console=True)

    cells = {cell_id: Cell(cell_id, args.task) for cell_id in CELLS}
    done = set()
    abort_why = None
    try:
        link.open()
        fresh = link.handshake(args.ident_wait)

        # preflight: drain this link's errors; the platform must be at rest and not e-stopped or faulted
        link.cmd("geterror")
        stat = nums(link.cmd("getstatus"), "stat", 2)
        if not args.dry_run and (stat is None or not all(s in AT_REST for s in stat)):
            link.cmd("stopmotors")
            link.pause(REST_BOUND_MS / 1000.0, "preflight stop")
            stat = nums(link.cmd("getstatus"), "stat", 2)
            if stat is None or not all(s in AT_REST for s in stat):
                raise LinkDead("PREFLIGHT_NOT_AT_REST_{}".format("_".join(str(s) for s in stat) if stat else "NO_REPLY"))

        cell_faultresp(link, cells["R20-SER-FAULTRESP"], fresh, log)
        done.add("R20-SER-FAULTRESP")
        cell_volt(link, cells["R20-SER-VOLT"], expected_enum, log)
        done.add("R20-SER-VOLT")
        cell_protclear(link, cells["R20-SER-PROTCLEAR"], log)
        done.add("R20-SER-PROTCLEAR")
        cell_errreply(link, cells["R20-SER-ERRREPLY"], log)
        done.add("R20-SER-ERRREPLY")
        cell_timeout(link, cells["R20-SER-TIMEOUT"], log)
        done.add("R20-SER-TIMEOUT")
    except LinkDead as why:
        abort_why = str(why)
    except KeyboardInterrupt:
        abort_why = "OPERATOR_ABORT"
    except Exception as exc:                          # a port that will not open, a pyserial error, ...
        abort_why = "HOST_ERROR_{}".format(type(exc).__name__)
        log.line("SER-HOST-ERROR,{}".format(exc), console=True)
    finally:
        if link.ser is not None:
            for text in ("stopmotors", "settimeout 0"):
                try:
                    link.cmd(text)
                except Exception:
                    pass
        link.close()

    if args.dry_run:
        log.line("PLAN no verdicts in a dry run: every SIGNOFF above is judged from live replies", console=True)
        log.close()
        return 0

    counts = {"PASS": 0, "FAIL": 0, "NOMEAS": 0}
    for cell_id in CELLS:
        cell = cells[cell_id]
        if cell_id not in done:
            # a cell cut short: its partial lines stand, and it closes with a NOMEAS saying why
            cell.nomeas("NONE", "CELL_COMPLETED", True, True, "BOOL", abort_why or "NOT_RUN", log)
        for text in cell.lines:
            log.line(text, console=True)
            counts[text.rsplit(",", 1)[1]] += 1
    log.line("SER-SUMMARY,pass,{},fail,{},nomeas,{},abort,{}".format(
        counts["PASS"], counts["FAIL"], counts["NOMEAS"], abort_why or "NONE"), console=True)
    if log_path:
        print("log: {}".format(log_path))
    log.close()
    return 1 if counts["FAIL"] or abort_why else 0


if __name__ == "__main__":
    sys.exit(main())

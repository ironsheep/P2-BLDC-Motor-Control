#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
serial_certify.py -- host-side certification of the P2 serial control path (PL-148)

WHAT IT PROVES
  The serial top level (src/isp_steering_serial.spin2) answers a real host as DRIVE-OBJECTS-SERIAL.md says, on
  the dual-motor platform, and the Python demo's wrapper class (P2-BLDC-Motor-Control-Demo.py, BLDCMotorControl) sends
  and reads those commands correctly. Eleven cells, each printed as a SIGNOFF verdict line in the bench logs' shape.
  Every expectation below follows the source as of DRIVER_REV 52 (reconciled for task 3681; each constant's comment in
  this file cites the source line it follows):

    R20-SER-ERRREPLY   an out-of-range command is refused with an ERROR naming the value and its range; a command
                       the drive refuses (a drive while e-stopped) is refused with "ERROR {cmd} failed: {NAME} ({code})";
                       valid commands reply OK
    R20-SER-TIMEOUT    settimeout {ms} then silence stops a drivepwr drive AND a drivedist drive within ms + a rest
                       bound, with stop reason SR_LINK_LOST (46) and ERR_COMMAND_TIMEOUT (-1019) from geterror; drive
                       commands re-sent inside ms keep it running
    R20-SER-VOLT       getvoltage returns the configured PWR_* number and its nominal mV
    R20-SER-FAULTRESP  getfaultresp reads FR_GRADED (1) at 10 % after start; setfaultresp round-trips; refused values
                       change nothing
    R20-SER-PROTCLEAR  (PL-111, the serial half) with no protective stop latched, getprot reads 0 0 and protclear
                       replies OK and changes nothing: at rest, and during a drive, which keeps running; it does not
                       release a user's e-stop; both commands refuse a parameter. The latched half is NOMEAS BY
                       CONSTRUCTION (see below): it needs a provoked protective stop (PL-106), which a lifted rig
                       cannot make
    R20-SER-LATENCY    (PL-154) a harmless getter's round trip, send to reply, stays under LATENCY_BOUND_MS: the P2's
                       idle poll plus the wire time at the baud rate plus this script's read poll
    R20-SER-NUMPARSE   (PL-154) a parameter that is not a decimal integer is refused with "ERROR Parameter {n} ({text})
                       is not a decimal integer" and changes nothing; valid numbers, and a CR before the LF, still work
    R20-SER-GETTERS    (PL-157) each new getter returns a well-formed reply; checkwiring runs and its verdict reads back
                       in gethealth (HLT_WIRING); setstartchecks is refused while the motors run; getevent's kind and
                       wheel are in their enums and getevtotal takes EV_STOP .. EV_FOLDBACK (62 .. 75) and refuses
                       61 and 76. The refused-start half of setstartchecks is NOMEAS BY CONSTRUCTION (see below):
                       it needs a platform whose start checks fail
    R20-SER-RAMP       (PL-160) setaccel and setdecel round-trip through getaccel and getdecel; a value just outside
                       either range is refused with an ERROR and changes nothing; after a fresh start getaccel reads
                       the built-in 1_000 and getdecel the built-in 1_470 (ACCEL_BUILTIN_MM_S2, DECEL_BUILTIN_MM_S2,
                       DRIVER_REV 38; getaccel read 0 before it). Both rates are put back at the end
    R20-SER-BACKTOBACK (plan 1.4, serial) maximum-length lines (128 characters before the LF, the receive buffer's
                       limit) sent back to back with no wait for a reply, two bursts of 100 lines: every line is
                       answered once, in order, with the value it set, and the link answers normally after each burst.
                       It is also the load for the P2's receive-loop cost record (see RECEIVE-LOOP COST below)
    R20-SER-DEMOWRAP   (PL-148) the demo's BLDCMotorControl wrappers, loaded from the demo's own source, send each
                       command in its documented form and return what the P2 replied; every reply over the whole run
                       was one LF-terminated line (the demo reads one line per command). Run last

NOMEAS BY CONSTRUCTION (stated here and in the output; NOT counted by the evaluation)
  Two criteria cannot be measured on a lifted rig that starts cleanly, by what they are, so they are not a gap in the run:
    R20-SER-PROTCLEAR  LATCHED_STOP_RELEASED    protclear releasing a LATCHED protective stop needs one latched, and a
                                                protective stop needs a commanded wheel held still (PL-106)
    R20-SER-GETTERS    STARTCHECKS_OPT_OUT_STARTS  setstartchecks 0 starting motors that a start check refused needs a
                                                platform whose start checks fail; this one's start succeeded
  Each prints a "SER-NOMEAS-BY-CONSTRUCTION" line and its SIGNOFF line with verdict NOMEAS; the SER-SUMMARY counts them
  apart (nomeas_by_construction) from the NOMEAS a run can avoid (nomeas), so the evaluation counts only the latter.

RECEIVE-LOOP COST (the P2 side, not measured here)
  The P2's receive loop records its worst per-character cost (isp_queue_serial.spin2 testGetRxCharCostMax(), :432), and a
  -d build of the serial top prints "** Rx max cost: <n> clocks" on the debug port as the worst grows
  (isp_steering_serial.spin2:300-302). That record is on the P2, so this script does not measure it: keep the debug
  terminal's log for the run. R20-SER-BACKTOBACK is the load that drives it hardest (16 us a character at 624,000 baud
  is the budget it is judged against, isp_queue_serial.spin2:703-705); the script says when that leg runs.

PRECONDITION
  - WHEELS UP (platform on blocks, both wheels free) and HANDS OFF for the whole run. The wheels turn at power 30.
  - The P2 runs src/isp_steering_serial.spin2 (the dual-motor serial top level), built at DRIVER_REV 52 or later (the
    serial changes of commit 0c1e911 -- the smart pin's fractional bit period, the receive-loop cost record -- are in
    isp_serial*.spin2 / isp_queue_serial.spin2, no host-visible protocol change), with isp_queue_serial.spin2's one-LF
    reply lines. Before them, OK and ERROR replies ended with the two characters "\\n" and no LF: this script then
    stops at once with abort REPLY_NOT_LF_TERMINATED. (getaccel's 1_000 needs DRIVER_REV 38; the walk band
    checkwiring judges, 40.)
  - THE CLOCK IS CHOSEN BY NAME (--clock), and the P2 must have been built at that clock. The serial top fixes its
    clock in one line, isp_steering_serial.spin2:23, "CLK_FREQ = 270_000_000"; there is no serial tier in
    tools/bench-run.sh. For each run: set that line to the Hz this script prints for the chosen clock name (the same
    names and values as tools/bench-run.sh's clock_hz()), build with pnut-ts (plain build) or pnut-ts -d (debug build),
    load, and restore the line afterwards. The script cannot read the P2's clock back: the P2 derives its bit period
    from the clock it actually runs at, so a wrong build still talks. The name only labels the run (banner, the
    SER-CLOCK line, the log) and gives the expected bit period and baud error for the evaluation to read.
  - A dual-motor configuration has a wheel diameter, so getaccel and getdecel read mm/s^2 (0 only without one).
  - For R20-SER-DEMOWRAP, P2-BLDC-Motor-Control-Demo.py beside this script (or --demo PATH). Only its source is read;
    it is never run, so its own packages (sendgrid, watchdog, ...) are not needed. Missing: that cell is NOMEAS.
  - Wired as SERIAL-CONTROL.md describes: host Tx -> P2 pin 57, host Rx <- P2 pin 56 (GW_RX2 / GW_TX2,
    isp_steering_serial.spin2:28-29), grounds joined, 624,000 baud (GW_BAUDRATE, :31) through a USB-serial adapter.
  - Best: start this script, THEN reset/power the P2, so the script sees the P2's "ident:" line and the fault-response
    default is read from a fresh start. A P2 already waiting for its ident answer also counts as fresh.
  - --drive-voltage names the DRIVE_VOLTAGE the P2 was built with; its default, PWR_18p5V, is the dual-motor
    configuration's (isp_bldc_motor_userconfig.spin2:176).

NOTHING NUMERIC IS TYPED (doctrine overlay P2)
  The port, the clock and the build are chosen by NAME from the tables in this file (PORT_NAMES, CLOCK_NAMES,
  BUILD_NAMES); the baud rate is the P2's fixed GW_BAUDRATE. The script echoes every line it sends, before it sends it.
  --list-ports prints the names, what each resolves to on this host, and the adapters pyserial sees.

HOW LONG
  About 2 minutes. The P2's command loop looks for a command every 1 ms (PL-154; it slept up to 1 s before), so most
  of the run is the three timeout cases' 45 s of timed motion and silence. Each checkwiring takes about 1.3 s.

PANIC PROCEDURE
  Physically disconnect the drive battery. Ctrl-C makes the script send "stopmotors" and "settimeout 0" on the way
  out, but do not rely on that. While a timeout case is driving, the P2's own command timeout (5 s) is on, so a
  dead host stops the wheels by itself.

USAGE
  ./serial_certify.py --list-ports                                    # the port names and clock names
  ./serial_certify.py --port usb-auto --clock clk-270 --build plain   # the one USB-serial adapter this host has
  ./serial_certify.py --port mac-usbserial --clock clk-floor --build debug
  ./serial_certify.py --port linux-usb0 --clock clk-frac --build plain --drive-voltage PWR_18p5V
  ./serial_certify.py --dry-run --clock clk-270                       # print the planned command sequence; no port is opened
  ./serial_certify.py --port usb-auto --clock clk-270 --demo ../P2-BLDC-Motor-Control-Demo.py   # the demo elsewhere

OUTPUT
  Every line sent and received, with a host timestamp, goes to serial-certify_<YYMMDD-HHMMSS>.log beside this script
  (none in a dry run). The SIGNOFF lines, the lines sent, and the SER-* lines are printed to the console and written to
  the same log.
"""

import argparse
import ast
import os
import re
import sys
import time
from collections import deque
from datetime import datetime
from enum import Enum

SCRIPT_VERSION = "2.0.0"            # 2.0.0: reconciled with DRIVER_REV 52 (task 3681); named ports and clocks; BACKTOBACK cell

# -----------------------------------------------------------------------------
# Values copied from the P2 source. Keep in sync with src/isp_bldc_motor.spin2 and src/isp_steering_serial.spin2.
# Each comment cites the source line it follows (DRIVER_REV 52); a line number is a pointer, the named constant is the claim.
# -----------------------------------------------------------------------------
BAUD = 624000                       # GW_BAUDRATE, isp_steering_serial.spin2:31 (fixed: nothing numeric is typed on the command line)

# Port names -> where the adapter is. A name ending in "*" is a glob, resolved on this host and refused unless exactly one
# device matches (never guessed). "usb-auto" is the one USB-serial adapter pyserial lists. Add a host's name here.
PORT_NAMES = {
    "usb-auto": None,                               # resolved by pyserial's port list: exactly one USB serial adapter
    "rpi-uart": "/dev/serial0",                     # the Pi's own UART (the Python demo's default port)
    "linux-usb0": "/dev/ttyUSB0",                   # FTDI / CP210x / CH340 adapters on Linux
    "linux-usb1": "/dev/ttyUSB1",
    "linux-acm0": "/dev/ttyACM0",
    "mac-usbserial": "/dev/cu.usbserial-*",         # FTDI / CP210x on macOS
    "mac-usbmodem": "/dev/cu.usbmodem*",
    "win-com3": "COM3", "win-com4": "COM4", "win-com5": "COM5", "win-com6": "COM6", "win-com7": "COM7",
    "win-com8": "COM8",
}

# Clock names -> the Hz the serial top must be built at (isp_steering_serial.spin2:23, CLK_FREQ). The names and values are
# tools/bench-run.sh's clock_hz() table; clk-floor is PROVISIONAL (the lowest supported clock is not yet certified).
CLOCK_NAMES = {
    "clk-floor": 120_000_000,       # provisional lowest supported clock
    "clk-200": 200_000_000,
    "clk-270": 270_000_000,         # the serial top's shipped clock
    "clk-300": 300_000_000,
    "clk-350": 350_000_000,         # the overclock ceiling
    "clk-frac": 271_250_000,        # a non-integer-MHz clock: its bit period is not a whole number of clocks (fractional bits)
}
BUILD_NAMES = ("plain", "debug")    # pnut-ts / pnut-ts -d of the serial top: a label; the -d build prints "** Rx max cost"
DEFAULT_DRIVE_VOLTAGE = "PWR_18p5V"     # CFG_DUAL_MOTOR's DRIVE_VOLTAGE, isp_bldc_motor_userconfig.spin2:176

# ERR_* names and codes (isp_bldc_motor.spin2:191-215), as errorName() in isp_steering_serial.spin2:928-984 names them
ERR_CODES = {
    "ERR_BAD_PIN_GROUP": -1001, "ERR_PIN_GROUP_IN_USE": -1002, "ERR_BAD_VOLTAGE": -1003,
    "ERR_BAD_DETECT_MODE": -1004, "ERR_NO_FREE_COG": -1005, "ERR_ABI_MISMATCH": -1006,
    "ERR_NOT_STARTED": -1007, "ERR_NO_SENSE_TASK": -1008, "ERR_BAD_UNITS": -1009, "ERR_BAD_COUNT": -1010,
    "ERR_NO_WHEEL_DIA": -1011, "ERR_LIMIT_UNRESOLVABLE": -1012, "ERR_SYNC_TIMEOUT": -1013, "ERR_BUSY": -1014,
    "ERR_FAULT_NOT_CLEARED": -1015, "ERR_EMERGENCY_STOPPED": -1016, "ERR_NO_RESPONSE": -1017,
    "ERR_BOARD_NOT_DETECTED": -1018, "ERR_COMMAND_TIMEOUT": -1019, "ERR_START_CHECK_FAILED": -1020,
    "ERR_NOT_IMPLEMENTED": -1021, "ERR_BAD_MOTOR_TABLE": -1022,
    "ERR_CLOCK_TOO_SLOW": -1023, "ERR_PROTECTIVE_STOP": -2000, "ERR_PLATFORM_BLOCKED": -2001,
}

# PWR_* enum (isp_bldc_motor_userconfig.spin2) and nominalMilliVolts() (isp_bldc_motor.spin2:5465-5472, getvoltage's reply
#  isp_steering_serial.spin2:652-658)
PWR_ENUM ={"PWR_6p0V": 1, "PWR_7p4V": 2, "PWR_11p1V": 3, "PWR_12p0V": 4, "PWR_14p8V": 5,
            "PWR_18p5V": 6, "PWR_22p2V": 7, "PWR_24p0V": 8, "PWR_25p9V": 9}
PWR_NOMINAL_MV = {1: 6000, 2: 7400, 3: 11100, 4: 12000, 5: 14800, 6: 18500, 7: 22200, 8: 24000, 9: 25900}

DS_MOVING, DS_HOLDING, DS_OFF, DS_FAULTED, DS_ESTOP = 11, 12, 13, 14, 15   # isp_bldc_motor.spin2:73 (#10, DS_Unknown, ...)
AT_REST = (DS_HOLDING, DS_OFF)      # hold defaults to coast (isp_steering_2wheel.spin2:495), so DS_OFF; a hold at rest reads
                                    #  DS_HOLDING only while holding (isp_steering_2wheel.spin2:1504): either is at rest
SR_NONE, SR_LINK_LOST = 40, 46      # isp_bldc_motor.spin2:136 (#40, SR_NONE, SR_COMMANDED, SR_AT_LIMIT, SR_FAULT_CONTROLLED,
                                    #  SR_FAULT_LOST, SR_BLOCKED, SR_LINK_LOST, ...)
FR_SHIPPED, FR_GRADED = 0, 1        # isp_bldc_motor.spin2:119
BRAKE_PCT_DEFAULT = 10              # isp_bldc_motor.spin2:6976; FAULT_RESPONSE_DEFAULT = FR_GRADED, :6974
DRU_HALL_TICKS, DDU_M = 1, 5        # isp_bldc_motor.spin2:64, :67
MAX_SPEED_DEFAULT = 75              # MAX_SPEED_DEFAULT, isp_bldc_motor.spin2:240; restored after the bounded case
SPEED_MIN, SPEED_MAX = 1, 100       # setspeed / setspeedfordist range, isp_steering_serial.spin2:537, :550
ACCEL_MIN_MM_S2, ACCEL_MAX_MM_S2 = 1, 10000     # setaccel's range, isp_bldc_motor.spin2:218-219; refusal text :499-502
DECEL_MIN_MM_S2, DECEL_MAX_MM_S2 = 250, 10000   # setdecel's range, isp_bldc_motor.spin2:224-225; refusal text :512-515
ACCEL_BUILTIN_MM_S2 = 1000          # getaccel until setaccel: isp_bldc_motor.spin2:230, read back :546 (the driver's
                                    #  RAMP_ACCEL_BUILTIN_STEP, :4755, is the same rate as a step; it read 0 before DRIVER_REV 38)
DECEL_BUILTIN_MM_S2 = 1470          # getdecel until setdecel: isp_bldc_motor.spin2:231, read back :558 (RAMP_DECEL_BUILTIN_STEP, :4756)
HOLD_CEILING_PCT, HOLD_RISE_MS, HOLD_LIMIT_MS = 10, 250, 10000  # setholdlimits' defaults: HOLD_CEILING_PCT / HOLD_RISE_MS /
                                    #  HOLD_LIMIT_MS, isp_bldc_motor.spin2:7391-7395 (restored at start)
EV_STOP, EV_FOLDBACK = 62, 75       # getevtotal's first and last counted kinds, isp_bldc_motor.spin2:157 (EV_FOLDBACK is 6.1.0's)
EV_NONE, EV_FIRST_KIND = 60, 60     # getevent's kind is EV_NONE (60) .. EV_FOLDBACK (75), :157
EVENT_WHEELS = (0, 50, 51, 52)      # 0 with EV_NONE, else EVW_LEFT / EVW_RIGHT / EVW_PLATFORM (DRIVE-OBJECTS-SERIAL.md)
WALK_LEG_TIMEOUT_MS = 2000          # WALK_LEG_TIMEOUT_MS, isp_bldc_motor.spin2:7504: the motor object's bound on one checkwiring leg
CMD_LINE_MAX = 128                  # MAX_SINGLE_STRING_LEN, isp_queue_serial.spin2:35: the longest line the P2 reads (before the LF)

# -----------------------------------------------------------------------------
# Test constants
# -----------------------------------------------------------------------------
REPLY_TIMEOUT_S = 3.0       # generous: the P2 answers within ms (1 ms idle poll, PL-154), plus the front cog's bounded
                            #  answer: a request waits at most REQ_ACK_TIMEOUT_MS (20) times the slots a late front pass
                            #  has stood for (reqAckTimeoutMs(), isp_bldc_motor.spin2:4903-4911, :5723; DRIVER_REV 51).
                            #  At the lowest clock a pass can stand for a few slots: still under 3 s
CHECKWIRING_REPLY_S = 2 * WALK_LEG_TIMEOUT_MS / 1000.0 + 2.0   # checkwiring replies only after both legs: about 1.3 s
                            #  (two ~0.63 s legs on the built-in ramp, isp_steering_2wheel.spin2:1362; at most 2 x
                            #  WALK_LEG_TIMEOUT_MS, :2175)
DRIVE_POWER = 30            # gentle, wheels up
TIMEOUT_MS = 5000           # settimeout value. Must exceed the getters read after the last drive in the negative case
                            #  (sized when each could take ~1 s; now far more than enough). The guard counts getms()
                            #  against lastDriveMs (isp_steering_2wheel.spin2:3217), so it is in time, not slots
REST_BOUND_MS = 2500        # ramp down to rest after the timeout fires. DRIVER_REV 38's jerk-limited stop from a cruise
                            #  speed v takes v / A + A / J passes (A 49_918 = RAMP_DECEL_BUILTIN_STEP, :4756; J 104 =
                            #  A x 23 / 11_000, :4766-4767), a pass is 23 PWM frames = 522.7 us at every clock (DRIVER_REV
                            #  50: drivePassUs, isp_bldc_motor.spin2:4589-4591; its nominal DRIVE_PASS_US, :5720, is 523).
                            #  Power 30 is v = 48_404_024 at 18.5 V (map(30, 1, 100, HUB_FLOOR_INCR 100_000, ceiling
                            #  165_000_000), :5063, :5201-5203, :5440): 1_450 passes, 0.76 s; 67_737_367 at 25.9 V: 0.96 s.
                            #  Even the default top speed (75) at 25.9 V, v = 172_691_902, takes 2.06 s. 2.5 s covers all
                            #  of them
MID_POLL_S = 1.0            # when the "still running before the timeout" getstatus is sent after the drive
RESEND_S = 0.5              # the negative case re-sends a drive at least this often (the P2's latency sets the real gap)
RESEND_SPAN_MS = 3 * TIMEOUT_MS
STILL_TICKS = 2             # at rest: hall ticks either wheel may move across the 1 s stillness check
MIN_MOVE_TICKS = 10         # it ran: hall ticks each wheel must have moved
DIST_SPEED = 30             # setspeedfordist for the bounded case
DIST_METERS = 20            # far beyond what the wheels cover before the timeout: speed 30 is 0.75 m/s at 18.5 V and
                            #  1.04 m/s at 25.9 V, so 5 s plus the ramps is under 6 m

# PL-154 latency: LATENCY_BOUND_MS = P2_IDLE_POLL_MS + the wire time of command and reply + READ_POLL_S
P2_IDLE_POLL_MS = 1         # IDLE_POLL_MS, isp_steering_serial.spin2:69 (used :299): the command loop's look-again period when idle
READ_POLL_S = 0.05          # this script's serial read timeout (Link.open): the longest one read waits before it looks again
BITS_PER_CHAR = 10          # 8N1: start + 8 data + stop
LATENCY_CMD = "getmaxspd"   # harmless: a getter that reads a status variable and posts nothing to the front cog
LATENCY_SAMPLES = 20        # the old 1 s idle sleep would put most samples far above the bound, so 20 cannot all pass

# PL-157 getters: command, reply prefix, value count (the replies' formats: isp_steering_serial.spin2:762-796, :685-689)
NEW_GETTERS = [("getpackvolt", "packvolt", 2), ("getcurrent", "current", 4), ("getfaultcause", "faultcause", 2),
               ("getholdstatus", "holdstatus", 4), ("gethallcounts", "hallcounts", 4), ("gethallillegal", "hallillegal", 4),
               ("getevent", "event", 4)]
PACK_STATES = (0, 1, 2)     # PACK_NOT_FITTED, PACK_ABSENT, PACK_PRESENT (isp_bldc_motor.spin2:112)
FC_CAUSES = (0, 1, 2)       # FC_NONE, FC_LAG, FC_HALL (:82)
HS_STATES = (0, 1, 2, 3)    # HS_OFF, HS_HOLDING, HS_SLIPPED, HS_LIMITED (:89)
HLT_WIRING = 32             # 1 << 5, isp_bldc_motor.spin2:104

SF_VERSION = 1
SF_BIN = "SERIAL"
CELLS = ["R20-SER-LATENCY", "R20-SER-NUMPARSE", "R20-SER-FAULTRESP", "R20-SER-VOLT", "R20-SER-PROTCLEAR",
         "R20-SER-ERRREPLY", "R20-SER-GETTERS", "R20-SER-TIMEOUT", "R20-SER-RAMP", "R20-SER-BACKTOBACK",
         "R20-SER-DEMOWRAP"]

# R20-SER-BACKTOBACK (plan 1.4, serial): maximum-length lines sent with no wait for a reply. The P2's character queue holds
# RX_CHR_Q_MAX_BYTES (512, isp_queue_serial.spin2:34) and its line queue RX_STR_Q_MAX_LONGS (10, :36) lines; a line is at
# most MAX_SINGLE_STRING_LEN (128, :35) characters before the LF, so 129 bytes on the wire: a burst of 100 is 12_900 bytes
# (about 206 ms at 16 us a byte) against queues that hold 3 lines.
BURST_LINES = 100           # lines per burst: 50 setspeed / getmaxspd pairs
BURSTS = 2                  # the second burst runs on whatever the first left behind (a queue that leaked would show there)
OVERLONG_LINES = 12         # over-long lines, one at a time: 12 x 172 leaked bytes would have filled the 512-byte queue 4 times
OVERLONG_LEN = 300          # characters before the LF: 172 over MAX_SINGLE_STRING_LEN, and under the 512-byte queue
BURST_SPEED_STEP = 37       # the pair's speed is 1 + (i x 37) mod 100: 37 is coprime with 100, so 50 consecutive pairs are all different
BURST_REPLY_S = 3.0 + BURST_LINES * 0.02    # the replies' deadline after the last byte is written: 1 ms poll + the getter's
                                            #  work per line is far under 20 ms, so this is generous without hiding a stall
PROTCLEAR_DRIVE_S = 1.5     # PL-111: the drive protclear must leave running is read this long after it starts, and again
                            #  after the protclear: past the ~1 s speed-up at power 30, so it is at speed both times
DEMO_FILE = "P2-BLDC-Motor-Control-Demo.py"

# PL-160 ramp round trips: (command, value) pairs set in turn, each read back; and the refused values, one step outside
RAMP_SETS = [("setaccel", 800), ("setaccel", 1500), ("setdecel", 1000), ("setdecel", 2000)]
RAMP_REFUSED = [("setaccel", ACCEL_MIN_MM_S2 - 1), ("setaccel", ACCEL_MAX_MM_S2 + 1),
                ("setdecel", DECEL_MIN_MM_S2 - 1), ("setdecel", DECEL_MAX_MM_S2 + 1)]


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
        self.framing_defects = 0        # blank lines and literal "\n" text received: one reply must be one LF line

    def open(self):
        if self.dry:
            self.log.line("PLAN open {} at {} baud".format(self.port_name, self.baud))
            return
        import serial                               # pyserial, as P2-BLDC-Motor-Control-Demo.py uses
        self.ser = serial.Serial(self.port_name, self.baud, timeout=READ_POLL_S)
        self.log.line("SER-OPEN,port,{},baud,{}".format(self.port_name, self.baud))

    def close(self):
        if self.ser:
            self.ser.close()

    def _send_raw(self, text):
        # the line is shown on the console BEFORE it is sent (nothing is sent that the run did not first say)
        self.log.line("TX  {}".format(text), console=True)
        self.ser.write((text + "\n").encode("utf-8"))

    def burst(self, lines, reply_s):
        """Write every line back to back in ONE write (no wait for a reply between them), then return (the reply lines
        read, in order, elapsed ms writing, None | 'ident'). Each line is echoed before anything is sent. A dry run
        prints the plan and returns ([], 0, None)."""
        if self.dry:
            self.log.line("PLAN TX burst of {} lines, {} characters before each LF, one write, no wait for replies".format(
                len(lines), len(lines[0]) if lines else 0))
            return [], 0, None
        while self.ser.in_waiting or b"\n" in self.buf:             # anything already waiting is not the burst's reply
            stray = self._read_line(time.monotonic() + 0.1)
            if stray is None:
                break
            self.log.line("RX-STRAY  {}".format(stray))
        for line in lines:
            self.log.line("TX  {}  [{} characters before the LF]".format(line.strip(), len(line)), console=True)
        data = "".join(line + "\n" for line in lines).encode("utf-8")
        t0 = time.monotonic()
        self.ser.write(data)
        write_ms = int(round((time.monotonic() - t0) * 1000))
        replies = []
        deadline = time.monotonic() + reply_s
        while len(replies) < len(lines):
            reply = self._read_line(deadline)
            if reply is None:
                break
            if reply.startswith("ident:"):
                self._answer_ident(reply)
                return replies, write_ms, "ident"
            if reply == "":
                self.framing_defects += 1
                self.log.line("RX-FRAMING  blank line")
                continue
            self.log.line("RX  {}".format(reply))
            replies.append(reply)
        return replies, write_ms, None

    def _read_line(self, deadline):
        # a line ends with ONE LF (sendOK / sendResponse / sendError in isp_queue_serial.spin2). A reply that ended
        #  with the two characters "\n" and no LF is the pre-6.0 framing: no host that reads lines can read it
        while True:
            if b"\n" in self.buf:
                raw, self.buf = self.buf.split(b"\n", 1)
                text = raw.decode("utf-8", "replace").rstrip("\r")
                if "\\n" in text:
                    self.framing_defects += 1
                    self.log.line("RX-FRAMING  literal \\n in [{}]".format(text))
                return text
            if time.monotonic() >= deadline:
                if self.buf.endswith(b"\\n"):
                    self.log.line("RX-FRAMING  [{}] ends with a literal \\n and no LF".format(
                        self.buf.decode("utf-8", "replace")))
                    raise LinkDead("REPLY_NOT_LF_TERMINATED")
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

    def cmd(self, text, reply_s=REPLY_TIMEOUT_S):
        """Send one command and return its one reply line, or None (dry run, or no reply in reply_s)."""
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
            else:
                self.framing_defects += 1
                self.log.line("RX-FRAMING  blank line")
        self._send_raw(text)
        deadline = time.monotonic() + reply_s
        while True:
            reply = self._read_line(deadline)
            if reply is None:
                self.log.line("RX-NONE  (no reply in {} s to '{}')".format(reply_s, text))
                self.silent_misses += 1
                if self.silent_misses >= 3:
                    raise LinkDead("NO_REPLIES")
                return None
            if reply.startswith("ident:"):
                self._answer_ident(reply)
                raise LinkDead("P2_RESET_MID_RUN")
            if reply == "":
                # a blank line is a framing defect: a host reading one line per command (the demo) takes it as the
                #  next command's reply
                self.framing_defects += 1
                self.log.line("RX-FRAMING  blank line")
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
        self.by_construction = set()        # indexes into lines: NOMEAS that no run could avoid (not counted)

    def _emit(self, motor, crit, measured, lo, hi, units, n, verdict):
        self.lines.append("SIGNOFF,sf,{},bin,{},cell,{},task,{},motor,{},crit,{},measured,{},lo,{},hi,{},units,{},n,{},verdict,{}".format(
            SF_VERSION, SF_BIN, self.cell_id, self.task, motor, crit, fmt(measured), fmt(lo), fmt(hi), units, n, verdict))

    def nomeas_by_construction(self, motor, crit, lo, hi, units, why, log):
        """A criterion this rig cannot measure BY WHAT IT IS (not for want of effort): stated in the output, and not
        counted by the evaluation (SER-SUMMARY's nomeas_by_construction, apart from nomeas)."""
        log.line("SER-NOMEAS-BY-CONSTRUCTION,cell,{},crit,{},why,{},counted,FALSE".format(self.cell_id, crit, why), console=True)
        self._emit(motor, crit, None, lo, hi, units, 0, "NOMEAS")
        self.by_construction.add(len(self.lines) - 1)

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
    # Claim: the default after start is FR_GRADED (1) at 10 (FAULT_RESPONSE_DEFAULT, BRAKE_PCT_DEFAULT, isp_bldc_motor.spin2:
    #  6974, :6976; DRIVER_REV 31); setfaultresp round-trips through getfaultresp (the refusals: mode not 0 or 1,
    #  isp_steering_serial.spin2:709-712; pct outside 0 .. 100, :713-716; reply "faultresp {mode} {pct}", :722-725).
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
    # Claim (PL-111's serial half, DRIVE-OBJECTS-SERIAL.md protclear): with no protective stop latched, getprot reads
    #  "prot 0 0" and protclear replies OK and changes nothing (isp_steering_2wheel.spin2:3098-3106, REQ_CLEAR_PROTECT, releases
    #  only a wheel whose getProtectiveStop() is set, and writes nothing otherwise; the reply is replyWithStatus(),
    #  isp_steering_serial.spin2:660-663; getprot's reply form :665-671).
    # NEGATIVES: protclear must not release a user's e-stop (only emerclear does): after emercutoff + protclear a drive
    #  is still refused with ERR_EMERGENCY_STOPPED. It must not stop a running drive: a protclear that wrote a stop or
    #  a zero command would leave status 13 (DS_OFF) or power 0 and FAIL NOOP_WHILE_DRIVING. And both commands take no
    #  parameter, so "protclear 1" and "getprot 1" are refused by the parser, never run (isp_queue_serial.spin2:296-297,
    #  the table entries' parameter count 0, isp_steering_serial.spin2:142-143).
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

    # the parser refuses a parameter to either: the command path's own refusal, and its reply form
    extra = 0
    for command in ("protclear", "getprot"):
        if link.cmd("{} 1".format(command)) == "ERROR Missing/Extra parameter(s)":
            extra += 1
    cell.judge("NONE", "PROTCLEAR_COUNT_ENFORCED", extra if not link.dry else None, 2, 2, "COUNT", n=2)

    # a no-op while a drive runs: the drive is still open (SR_NONE), moving, at its power, after the protclear
    link.cmd("geterror")
    drove = is_ok(link.cmd("drivepwr {} {}".format(DRIVE_POWER, DRIVE_POWER)))
    link.pause(PROTCLEAR_DRIVE_S, "drive at speed before protclear")
    stat1 = nums(link.cmd("getstatus"), "stat", 2)
    clear3_ok = is_ok(link.cmd("protclear"))
    link.pause(PROTCLEAR_DRIVE_S, "drive after protclear")
    stat2 = nums(link.cmd("getstatus"), "stat", 2)
    pwr2 = nums(link.cmd("getpwr"), "pwr", 2)
    reason2 = nums(link.cmd("getstopreason"), "stopreason", 2)
    prot2 = nums(link.cmd("getprot"), "prot", 2)
    link.cmd("stopmotors")
    link.pause(REST_BOUND_MS / 1000.0, "ramp down after stopmotors")
    running = [DS_MOVING, DS_MOVING]
    cell.judge("BOTH", "NOOP_WHILE_DRIVING",
               drove and clear3_ok and stat1 == running and stat2 == running and pwr2 == [DRIVE_POWER, DRIVE_POWER]
               and reason2 == [SR_NONE, SR_NONE] and prot2 == [0, 0], True, True, "BOOL")

    # the latched half is NOMEAS BY CONSTRUCTION: a lifted rig cannot latch a protective stop (it needs a commanded wheel
    #  held still, PL-106), so protclear's release of one cannot be seen. Stated in the output and the docstring; not counted
    cell.nomeas_by_construction("BOTH", "LATCHED_STOP_RELEASED", True, True, "BOOL",
                                "NEEDS_PROVOKED_PROTECTIVE_STOP_PL-106_A_LIFTED_RIG_CANNOT_LATCH_ONE", log)


ERR_REPLY_RE = re.compile(r"^ERROR (\S+) failed: (ERR_[A-Z_]+) \((-?\d+)\)$")


def cell_errreply(link, cell, log):
    # Claim (DRIVE-OBJECTS-SERIAL.md, "An ERROR reply comes in one of two forms"): an out-of-range value is refused
    #  naming the value and its range ("LT-Power (150) out of range [-100, 100]", isp_steering_serial.spin2:416-419); a
    #  command the drive refuses replies "ERROR {cmd} failed: {ERR_NAME} ({code})" (replyWithStatus(), :833-851, with
    #  driveAtPower()'s ERR_EMERGENCY_STOPPED while e-stopped, isp_steering_2wheel.spin2:690-697, refused :3225-3283).
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
    #  REQ_DRIVE / REQ_DRIVE_DISTANCE (frontWatchCommand, :3196, :3198-3205, :3365, :3370) and REQ_SET_TIMEOUT (:3129) touch
    #  lastDriveMs; getstatus, getpwr, getstopreason, geterror and getrot read status directly and post no request, so
    #  they cannot refresh the timeout. The firing (bFrontCommandTimedOut(), :3207-3222) stops both wheels as stopMotors()
    #  does (:2702-2705) with SR_LINK_LOST (46), counts it for geterror (reported once per cog, :1191-1194), and only
    #  while a wheel's power is non-zero (:3218).
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
    # PL-153 (DRIVER_REV 33): getrot is the odometer, total travel, which a drive never resets -- so the run is judged
    #  against a reading taken just before it, not against 0 (every earlier case's travel would pass that)
    rot0 = nums(link.cmd("getrot {}".format(DRU_HALL_TICKS)), "rot", 2)
    spd_ok = is_ok(link.cmd("setspeedfordist {}".format(DIST_SPEED)))
    set_ok = is_ok(link.cmd("settimeout {}".format(T)))
    t_send = time.monotonic()
    drove = is_ok(link.cmd("drivedist {} {} {}".format(DIST_METERS, DIST_METERS, DDU_M)))
    link.wait_until(t_send + MID_POLL_S, t_send, "drivedist")
    mid = nums(link.cmd("getstatus"), "stat", 2)
    running = spd_ok and set_ok and drove and mid == [DS_MOVING, DS_MOVING]
    link.wait_until(t_send + bound_s, t_send, "drivedist (timeout + rest bound)")
    at_rest, reason, err0, rot1 = stopped_checks(link, "drivedist")
    cell.judge("BOTH", "DIST_RUNNING_BEFORE_MS", running and moved(rot0, rot1), True, True, "BOOL")
    cell.judge("BOTH", "DIST_AT_REST_BY_BOUND", at_rest, True, True, "BOOL")
    cell.judge("BOTH", "DIST_REASON_LINK_LOST", reason == [SR_LINK_LOST, SR_LINK_LOST], True, True, "BOOL")
    cell.judge("NONE", "DIST_ERR_TIMEOUT", err0, ERR_CODES["ERR_COMMAND_TIMEOUT"], ERR_CODES["ERR_COMMAND_TIMEOUT"], "CODE")
    link.cmd("stopmotors")
    link.cmd("settimeout 0")                                      # off, as the serial top level leaves it
    link.cmd("setspeedfordist {}".format(MAX_SPEED_DEFAULT))


def latency_bound_ms(baud):
    """The PL-154 bound: the P2's idle poll + the wire time of LATENCY_CMD and its reply + this script's read poll."""
    reply_chars = len("speedmax 100") + 1                        # the longest getmaxspd reply, with its LF
    wire_ms = (len(LATENCY_CMD) + 1 + reply_chars) * BITS_PER_CHAR * 1000.0 / baud
    return P2_IDLE_POLL_MS + wire_ms + READ_POLL_S * 1000.0


def cell_latency(link, cell, log):
    # Claim (PL-154): the P2 looks for a command every 1 ms when idle (waitms(IDLE_POLL_MS), isp_steering_serial.spin2:299), so
    #  a command is answered within the bound. A getter replies from status variables and posts no front-cog request
    #  (getmaxspd: isp_steering_serial.spin2:623-629). The wire time uses the fixed BAUD; the P2's bit period is fractional
    #  (isp_serial_singleton.spin2:126-130), which changes the wire time by well under a bit at any clock in CLOCK_NAMES.
    # NEGATIVE: under the old 1 s idle sleep a command waited 0-1000 ms, so the max of LATENCY_SAMPLES round trips spread
    #  over time would almost surely pass the bound (~52 ms at 624,000 baud) and FAIL. Samples are spaced irregularly so
    #  they do not lock to any P2 period.
    bound = latency_bound_ms(link.baud)
    log.line("SER-LATENCY-PLAN,cmd,{},samples,{},p2_poll_ms,{},read_poll_ms,{},baud,{},bound_ms,{:.1f}".format(
        LATENCY_CMD, LATENCY_SAMPLES, P2_IDLE_POLL_MS, int(READ_POLL_S * 1000), link.baud, bound))
    worst_ms = 0
    replies = 0
    for idx in range(LATENCY_SAMPLES):
        t0 = time.monotonic()
        reply = link.cmd(LATENCY_CMD)
        elapsed_ms = int(round((time.monotonic() - t0) * 1000))
        if link.dry:
            log.line("PLAN repeat {} x, 7 to 103 ms apart; judge the slowest round trip".format(LATENCY_SAMPLES))
            break
        if nums(reply, "speedmax", 1) is not None:
            replies += 1
            worst_ms = max(worst_ms, elapsed_ms)
        log.line("SER-LATENCY,sample,{},ms,{}".format(idx + 1, elapsed_ms))
        link.pause((7 + (13 * idx) % 97) / 1000.0, "latency spacing")
    cell.judge("NONE", "REPLIES_WELL_FORMED", replies, LATENCY_SAMPLES, LATENCY_SAMPLES, "COUNT", n=LATENCY_SAMPLES)
    cell.judge("NONE", "MAX_ROUND_TRIP", worst_ms if replies else None, 0, int(bound), "MS", n=LATENCY_SAMPLES)


BAD_PARAM_RE = re.compile(r"^ERROR Parameter (\d+) \((.*)\) is not a decimal integer$")


def cell_numparse(link, cell, log):
    # Claim (PL-154): each parameter must be a decimal integer with an optional leading minus (or true / false); any other
    #  text is refused with "ERROR Parameter {n} ({text}) is not a decimal integer" and the command is not run
    #  (decimalForToken(), isp_queue_serial.spin2:521-552: digits only, within +-2_147_483_647, at most RX_VALUE_MAX_LEN 32
    #  characters; refusal text sendBadParam(), :510-519; checked after the parameter count, :296-300). A CR before the LF
    #  is white space (:967).
    # NEGATIVE: "setspeed 6O" (letter O) parsed as a number before PL-154 (6*10 + 31 = 91, in range, accepted); here the
    #  speed must stay at the value set before, so a parser that still turned text into numbers would FAIL. The valid
    #  "setspeed 60" and a CR-LF terminated "setspeed 70" must reply OK and take effect.
    set_ok = is_ok(link.cmd("setspeed 60"))
    before = nums(link.cmd("getmaxspd"), "speedmax", 1)
    bad_texts = ["6O", "5abc", "-", "--5", "+50", "99999999999", "0x20"]
    wrong = 0
    for text in bad_texts:
        reply = link.cmd("setspeed {}".format(text))
        match = BAD_PARAM_RE.match(reply) if reply else None
        if not (match and match.group(1) == "1" and match.group(2) == text):
            wrong += 1
    after = nums(link.cmd("getmaxspd"), "speedmax", 1)
    cell.judge("NONE", "NON_NUMBERS_REFUSED", wrong if not link.dry else None, 0, 0, "COUNT", n=len(bad_texts))
    cell.judge("NONE", "REFUSED_CHANGED_NOTHING", set_ok and before == [60] and after == [60], True, True, "BOOL")

    # the second parameter is named by its position; a negative number is still a number
    reply = link.cmd("drivepwr 0 zero")
    match = BAD_PARAM_RE.match(reply) if reply else None
    cell.judge("NONE", "NAMES_POSITION", bool(match) and match.group(1) == "2", True, True, "BOOL")
    neg_ok = is_ok(link.cmd("drivepwr -0 0"))                     # "-0" is a number: power 0, nothing moves

    crlf_ok = is_ok(link.cmd("setspeed 70\r"))
    crlf_read = nums(link.cmd("getmaxspd"), "speedmax", 1)
    cell.judge("NONE", "VALID_STILL_WORK", neg_ok and crlf_ok and crlf_read == [70], True, True, "BOOL")
    link.cmd("setspeed {}".format(MAX_SPEED_DEFAULT))


def cell_getters(link, cell, log):
    # Claim (PL-157): each new getter replies "{prefix} n1 .. nk" with k integers, its enums in their documented ranges
    #  (the replies: isp_steering_serial.spin2:685-689, :762-796; enums isp_bldc_motor.spin2:82, :89, :112, :157).
    # NEGATIVE: each getter sent with an extra parameter must be refused "ERROR Missing/Extra parameter(s)" -- a table
    #  entry with the wrong parameter count, or a missing command ("ERROR Command NOT found"), FAILs one or the other.
    malformed = 0
    out_of_range = 0
    extra_refused = 0
    for command, prefix, count in NEW_GETTERS:
        values = nums(link.cmd(command), prefix, count)
        if values is None:
            malformed += 1
        elif prefix == "packvolt":
            out_of_range += 0 if (values[0] in PACK_STATES and values[1] >= 0) else 1
        elif prefix == "faultcause":
            out_of_range += 0 if all(v in FC_CAUSES for v in values) else 1
        elif prefix == "holdstatus":
            out_of_range += 0 if (values[0] in HS_STATES and values[2] in HS_STATES) else 1
        elif prefix in ("hallcounts", "hallillegal"):
            out_of_range += 0 if all(v >= 0 for v in values) else 1
        elif prefix == "event":
            # {kind} EV_NONE (60) .. EV_FOLDBACK (75); {ms}; {wheel} 0 with EV_NONE, else 0 / 50 / 51 / 52; {value}
            kind_ok = EV_NONE <= values[0] <= EV_FOLDBACK
            wheel_ok = values[2] in EVENT_WHEELS and (values[0] != EV_NONE or values[2] == 0)
            out_of_range += 0 if (kind_ok and wheel_ok) else 1
        if link.cmd("{} 1".format(command)) == "ERROR Missing/Extra parameter(s)":
            extra_refused += 1
    n = len(NEW_GETTERS)
    cell.judge("NONE", "GETTERS_MALFORMED", malformed if not link.dry else None, 0, 0, "COUNT", n=n)
    cell.judge("NONE", "GETTERS_OUT_OF_RANGE", out_of_range if not link.dry else None, 0, 0, "COUNT", n=n)
    cell.judge("NONE", "GETTERS_COUNT_ENFORCED", extra_refused if not link.dry else None, n, n, "COUNT", n=n)

    # getevtotal counts EV_STOP (62) .. EV_FOLDBACK (75) (isp_steering_serial.spin2:691-702): the ends answer with three
    #  counts, one outside either end is refused naming the range (EV_FOLDBACK is 6.1.0's: 76 was in range before it)
    ends_ok = 0
    for kind in (EV_STOP, EV_FOLDBACK):
        if nums(link.cmd("getevtotal {}".format(kind)), "evtotal", 3) is not None:
            ends_ok += 1
    refused_ok = 0
    for kind in (EV_STOP - 1, EV_FOLDBACK + 1):
        reply = link.cmd("getevtotal {}".format(kind))
        if reply == "ERROR EventKind ({}) out of range [{}, {}]".format(kind, EV_STOP, EV_FOLDBACK):
            refused_ok += 1
    cell.judge("NONE", "EVTOTAL_ENDS_ANSWER", ends_ok if not link.dry else None, 2, 2, "COUNT", n=2)
    cell.judge("NONE", "EVTOTAL_OUTSIDE_REFUSED", refused_ok if not link.dry else None, 2, 2, "COUNT", n=2)

    # checkwiring turns the platform a few degrees in place and back (wheels up): OK, then HLT_WIRING is checked on both.
    #  The verdict itself (a failed bit) is logged, not judged: DRIVER_REV 40 re-derived its band (3 .. 11 ticks a leg,
    #  WALK_SHORT_TICKS / WALK_OVERSHOOT_TICKS, isp_bldc_motor.spin2:7501-7502; judged by bJudgeWalk(), :1546-1547).
    #  "checkwiring" replies OK once the walk has run, whatever its verdict (isp_steering_2wheel.spin2:1369; reply
    #  isp_steering_serial.spin2:798-802)
    walk_ok = is_ok(link.cmd("checkwiring", CHECKWIRING_REPLY_S))      # replies after both legs, about 1.3 s
    health = nums(link.cmd("gethealth"), "health", 6)
    checked = health is not None and (health[0] & HLT_WIRING) != 0 and (health[3] & HLT_WIRING) != 0
    if health is not None:
        log.line("SER-WIRING,lt_failed,{},rt_failed,{}".format(health[1] & HLT_WIRING, health[4] & HLT_WIRING))
    cell.judge("BOTH", "CHECKWIRING_VERDICT_READ", walk_ok and checked, True, True, "BOOL")

    # the motors are running, so there is no start left for setstartchecks to choose for: "ERROR StartChecks apply only to
    #  a start its checks refused: the motors are running" (isp_steering_serial.spin2:812-814, bStartRefused FALSE)
    reply = link.cmd("setstartchecks 0")
    cell.judge("NONE", "STARTCHECKS_REFUSED_RUNNING", reply is not None and reply.startswith("ERROR StartChecks"),
               True, True, "BOOL")
    # NOMEAS BY CONSTRUCTION: setstartchecks 0 starting motors a check refused (retryStart(), :882-917) needs a platform whose
    #  start checks fail, and this one's start succeeded or this script would have no motors to certify. Stated, not counted
    cell.nomeas_by_construction("BOTH", "STARTCHECKS_OPT_OUT_STARTS", True, True, "BOOL",
                                "NEEDS_A_REFUSED_START_THIS_PLATFORM_STARTED", log)


def read_rates(link):
    """Return [accel, decel] from getaccel and getdecel, or None when either reply is malformed."""
    accel = nums(link.cmd("getaccel"), "accel", 1)
    decel = nums(link.cmd("getdecel"), "decel", 1)
    if accel is None or decel is None:
        return None
    return [accel[0], decel[0]]


def cell_ramp(link, cell, fresh, log):
    # Claim (PL-160, DRIVE-OBJECTS-SERIAL.md): setaccel {rate} and setdecel {rate} take mm/s^2 at the rim and read back
    #  through getaccel and getdecel as the rate given. Until set, since DRIVER_REV 38, they read the built-in rates:
    #  getaccel ACCEL_BUILTIN_MM_S2 (1_000; it read 0 before 38, when the built-in ramp had no single rate) and getdecel
    #  DECEL_BUILTIN_MM_S2 (1_470). isp_bldc_motor.spin2 getAcceleration()/getDeceleration() (:535-558) with a wheel diameter
    #  set; the constants :230-231; the steps the driver runs them as, RAMP_ACCEL_BUILTIN_STEP / RAMP_DECEL_BUILTIN_STEP
    #  :4755-4756 (init() converts them once, :4605-4606). Ranges: setaccel 1 .. 10_000 (:218-219, serial :499-502),
    #  setdecel 250 .. 10_000 (:224-225, serial :512-515); replies "accel {rate}" / "decel {rate}" (serial :521-531).
    # NEGATIVE: each round trip uses two different values per setter, so a getter that echoed a constant FAILs; a value one
    #  step outside either range must be refused with an ERROR and leave both rates as they were, so a range check that
    #  was missing (or a refusal that still stored) FAILs. getaccel/getdecel sent with a parameter must be refused. A P2
    #  before DRIVER_REV 38 reads getaccel 0 on a fresh start and FAILs DEFAULT_ACCEL_BUILTIN.
    first = read_rates(link)
    log.line("SER-RAMP,start,accel,{},decel,{}".format(first[0] if first else "NA", first[1] if first else "NA"))
    if fresh:
        cell.judge("NONE", "DEFAULT_ACCEL_BUILTIN", first[0] if first else None, ACCEL_BUILTIN_MM_S2, ACCEL_BUILTIN_MM_S2,
                   "MM_S2")
        cell.judge("NONE", "DEFAULT_DECEL_BUILTIN", first[1] if first else None, DECEL_BUILTIN_MM_S2, DECEL_BUILTIN_MM_S2,
                   "MM_S2")
    else:
        cell.nomeas("NONE", "DEFAULT_ACCEL_BUILTIN", ACCEL_BUILTIN_MM_S2, ACCEL_BUILTIN_MM_S2, "MM_S2", "NOT_FRESH_START",
                    log)
        cell.nomeas("NONE", "DEFAULT_DECEL_BUILTIN", DECEL_BUILTIN_MM_S2, DECEL_BUILTIN_MM_S2, "MM_S2", "NOT_FRESH_START",
                    log)

    misses = 0
    for command, value in RAMP_SETS:
        if not is_ok(link.cmd("{} {}".format(command, value))):
            misses += 1
        rates = read_rates(link)
        got = None if rates is None else (rates[0] if command == "setaccel" else rates[1])
        if got != value:
            misses += 1
    cell.judge("NONE", "SET_GET_MISMATCHES", misses if not link.dry else None, 0, 0, "COUNT", n=len(RAMP_SETS))

    # refused values: an ERROR reply, and both rates in effect (1500, 2000) unchanged
    bad = 0
    for command, value in RAMP_REFUSED:
        reply = link.cmd("{} {}".format(command, value))
        if reply is None or not reply.startswith("ERROR "):
            bad += 1
        if read_rates(link) != [RAMP_SETS[1][1], RAMP_SETS[3][1]]:
            bad += 1
    cell.judge("NONE", "REFUSED_CHANGED_NOTHING", bad if not link.dry else None, 0, 0, "COUNT", n=len(RAMP_REFUSED))

    extra = 0
    for command in ("getaccel", "getdecel"):
        if link.cmd("{} 1".format(command)) == "ERROR Missing/Extra parameter(s)":
            extra += 1
    cell.judge("NONE", "GETTERS_COUNT_ENFORCED", extra if not link.dry else None, 2, 2, "COUNT", n=2)

    # both rates read at the start are put back. Since DRIVER_REV 38 the built-in speed-up rate is a rate like any other
    #  (setaccel 1000 converts to the built-in step, RAMP_ACCEL_BUILTIN_STEP, as the built-in does), so it can be
    if first is not None and ACCEL_MIN_MM_S2 <= first[0] <= ACCEL_MAX_MM_S2:
        link.cmd("setaccel {}".format(first[0]))
    if first is not None and DECEL_MIN_MM_S2 <= first[1] <= DECEL_MAX_MM_S2:
        link.cmd("setdecel {}".format(first[1]))


def burst_lines(first_pair):
    """The lines of one burst: BURST_LINES / 2 pairs of 'setspeed {v}' then 'getmaxspd', each padded with spaces to
    CMD_LINE_MAX characters (the longest line the P2 reads). Even pairs pad after the command, odd pairs before it, so
    both the trailing and the leading white space of a full line are read. Returns (lines, expected replies)."""
    lines = []
    expected = []
    for k in range(BURST_LINES // 2):
        i = first_pair + k
        speed = SPEED_MIN + (i * BURST_SPEED_STEP) % (SPEED_MAX - SPEED_MIN + 1)
        for text, reply in (("setspeed {}".format(speed), "OK"), ("getmaxspd", "speedmax {}".format(speed))):
            line = text.ljust(CMD_LINE_MAX) if k % 2 == 0 else text.rjust(CMD_LINE_MAX)
            lines.append(line)
            expected.append(reply)
    return lines, expected


def cell_backtoback(link, cell, build, log):
    # Claim (plan 1.4, serial): the P2 keeps up with lines of the longest length arriving back to back at 624,000 baud: a
    #  line is read up to MAX_SINGLE_STRING_LEN (128) characters (isp_queue_serial.spin2:35, :574, copyWrappedStr() :791-814),
    #  its characters are queued by the receive task (RX_CHR_Q_MAX_BYTES 512, :34, bTskEnqueueChar() :644-674; a full queue
    #  drops characters, bQueOverrun) and the command loop drains one line a pass (isp_steering_serial.spin2:288-299).
    # How it is judged: a burst of setspeed {v} / getmaxspd pairs, v different every pair, is written in ONE write with no wait
    #  for a reply. The replies must be, in order, "OK" then "speedmax {v}": a dropped, doubled, truncated or reordered line
    #  breaks the sequence at that line, and a getter that read the wrong speed shows which command was lost.
    # NEGATIVE: a P2 whose receive task fell behind drops characters (the line is then a different command, or none), and a
    #  queue that leaked accounting would pass the first burst and fail the second: the count of replies, the sequence and
    #  the link's answer after each burst are three separate criteria. A reply that is not the one expected FAILs ORDER.
    # NOT judged here: the receive loop's own per-character cost. The P2 records it (testGetRxCharCostMax()) and the -d build
    #  prints "** Rx max cost: <n> clocks" (isp_steering_serial.spin2:300-302): keep the debug terminal's log for this leg.
    log.line("SER-BACKTOBACK-PLAN,build,{},bursts,{},lines_per_burst,{},chars_per_line,{},bytes_per_burst,{},baud,{}".format(
        build, BURSTS, BURST_LINES, CMD_LINE_MAX, BURST_LINES * (CMD_LINE_MAX + 1), BAUD), console=True)
    if build == "debug":
        log.line("SER-BACKTOBACK-NOTE,keep the PNut debug terminal log for this leg: the P2 prints '** Rx max cost: <n> clocks' "
                 "as its receive loop's worst per-character cost grows", console=True)
    else:
        log.line("SER-BACKTOBACK-NOTE,plain build: the P2's receive-loop cost is only printed by the debug build "
                 "(rerun with --build debug on the -d build to record it)", console=True)

    all_answered = 0
    out_of_order = 0
    alive = 0
    framing_before = link.framing_defects
    total = 0
    for burst in range(BURSTS):
        lines, expected = burst_lines(burst * (BURST_LINES // 2))
        replies, write_ms, event = link.burst(lines, BURST_REPLY_S)
        if event == "ident":
            raise LinkDead("P2_RESET_MID_RUN")
        if not link.dry:
            log.line("SER-BACKTOBACK,burst,{},lines,{},replies,{},write_ms,{}".format(burst + 1, len(lines), len(replies), write_ms),
                     console=True)
            total += len(lines)
            if len(replies) == len(lines):
                all_answered += 1
            out_of_order += sum(1 for got, want in zip(replies, expected) if got != want) + max(0, len(expected) - len(replies))
            for idx, (got, want) in enumerate(zip(replies, expected)):
                if got != want:
                    log.line("SER-BACKTOBACK-MISMATCH,burst,{},line,{},expected,{},got,{}".format(burst + 1, idx + 1, want, got))
                    break
        # the link answers normally after the burst: a getter, one reply, and the last speed the burst set
        after = nums(link.cmd("getmaxspd"), "speedmax", 1)
        want_speed = int(expected[-1].split()[1])
        if not link.dry and after == [want_speed]:
            alive += 1
    # OVER-LONG lines (fixed with this leg, 2026-10-04): a line longer than MAX_SINGLE_STRING_LEN is truncated when it is
    #  copied out, and the P2 used to free only the truncated length from its character queue (getLine(), :396-399), so each
    #  one leaked (length - 128) bytes of the 512: after about three 300-character lines every later character was dropped.
    #  Each line here is "getmaxspd" padded with spaces to OVERLONG_LEN, so its first 128 characters still parse as the
    #  getter. UNFIXED VALUE: about 3 of OVERLONG_LINES answered, then none, and the link dead after.
    overlong_answered = 0
    for _ in range(OVERLONG_LINES):
        if nums(link.cmd("getmaxspd".ljust(OVERLONG_LEN)), "speedmax", 1) == [want_speed]:
            overlong_answered += 1
    if not link.dry:
        log.line("SER-BACKTOBACK-OVERLONG,lines,{},chars_per_line,{},answered,{}".format(OVERLONG_LINES, OVERLONG_LEN,
                                                                                        overlong_answered), console=True)
    framing = link.framing_defects - framing_before
    cell.judge("NONE", "OVERLONG_LINES_ANSWERED", overlong_answered if not link.dry else None, OVERLONG_LINES, OVERLONG_LINES,
               "COUNT", n=OVERLONG_LINES)
    cell.judge("NONE", "BURSTS_FULLY_ANSWERED", all_answered if not link.dry else None, BURSTS, BURSTS, "COUNT", n=BURSTS)
    cell.judge("NONE", "REPLIES_IN_ORDER_AS_SET", out_of_order if not link.dry else None, 0, 0, "COUNT", n=max(total, 1))
    cell.judge("NONE", "ONE_LF_LINE_PER_REPLY", framing if not link.dry else None, 0, 0, "COUNT", n=BURSTS)
    cell.judge("NONE", "LINK_ANSWERS_AFTER_BURST", alive if not link.dry else None, BURSTS, BURSTS, "COUNT", n=BURSTS)
    link.cmd("setspeed {}".format(MAX_SPEED_DEFAULT))                  # the default put back


# -----------------------------------------------------------------------------
# The demo's wrappers (PL-148: "the Python demo"), certified from the demo's own source
# -----------------------------------------------------------------------------
# P2-BLDC-Motor-Control-Demo.py cannot be imported: its module level parses its own arguments, opens /dev/serial0,
#  starts a listener thread and drives a square, and it needs sendgrid, watchdog, unidecode and colorama. So only its
#  BLDCMotorControl class, its unit and status enums and its responseOK / responseERROR strings are taken from its source
#  (ast), compiled, and run against this script's link through two stand-ins for the demo's own serial port and line
#  queue. The code under test is the demo's, byte for byte; nothing of it is copied here.

DEMO_NAMES = ("DrvDistUnits", "DrvRotUnits", "DrvTimeUnits", "DrvStatus", "DrvStopState", "responseOK", "responseERROR")


class DemoLineQueue:
    """Stands in for the demo's RxLineQueue (queueRxLines): the reply lines its listener thread would have queued."""

    def __init__(self):
        self.lines = deque()

    def pushLine(self, text):
        self.lines.append(text)

    def popLine(self):
        return self.lines.popleft() if self.lines else ""

    def lineCount(self):
        return len(self.lines)


class DemoPort:
    """Stands in for the demo's serial.Serial: each write() is one command, sent over this script's link; its one reply
    line is queued as the demo's listener would queue it (a missing reply as an empty line, so the demo never waits)."""

    def __init__(self, link, queue):
        self.link = link
        self.queue = queue
        self.sent = None
        self.reply = None

    def write(self, data):
        self.sent = data.decode("utf-8", "replace")
        text = self.sent[:-1] if self.sent.endswith("\n") else self.sent
        timeout_s = CHECKWIRING_REPLY_S if text == "checkwiring" else REPLY_TIMEOUT_S
        self.reply = self.link.cmd(text, timeout_s)
        self.queue.pushLine(self.reply if self.reply is not None else "")
        return len(data)


def load_demo_wrappers(path, log):
    """Return (the demo's BLDCMotorControl class, its namespace), compiled from the demo's source only."""
    with open(path, "r", encoding="utf-8") as fh:
        tree = ast.parse(fh.read(), filename=path)
    keep = []
    for node in tree.body:
        if isinstance(node, ast.ClassDef) and node.name == "BLDCMotorControl":
            keep.append(node)
        elif isinstance(node, ast.Assign) and any(isinstance(t, ast.Name) and t.id in DEMO_NAMES for t in node.targets):
            keep.append(node)
    module = ast.Module(body=keep, type_ignores=[])
    namespace = {
        "Enum": Enum,
        "sleep": time.sleep,
        "print_line": lambda text, **kwargs: log.line("DEMO-PRINT  {}".format(text)),
        "queueRxLines": DemoLineQueue(),
    }
    exec(compile(module, path, "exec"), namespace)
    return namespace["BLDCMotorControl"], namespace


def as_ints(value):
    """A demo getter's result as a list of ints (it returns str, a tuple of str, int, or DrvStatus members); None if not."""
    if value is None:
        return None
    items = value if isinstance(value, tuple) else (value,)
    out = []
    try:
        for item in items:
            out.append(int(item.value) if isinstance(item, Enum) else int(item))
    except (TypeError, ValueError):
        return None
    return out


def cell_demowrap(link, cell, demo_path, log):
    # Claim (PL-148, "the Python demo"): each BLDCMotorControl wrapper sends its command in the form DRIVE-OBJECTS-SERIAL.md
    #  documents, and each getter returns exactly the values the P2 replied; and every reply of the run was one line
    #  ending in one LF, which is what the demo's reader (readline, one line per command) needs.
    # NEGATIVES: the expected lines are written here from the document, not from the demo, so a wrapper that sends a
    #  wrong name, order, enum value or boolean FAILs LINES; each command's reply is judged (OK, or the one refusal it
    #  must get), so a line the P2 parsed differently FAILs REPLIES; each getter's return is compared with the reply read
    #  on the wire, so a wrapper that mis-parsed or dropped a value FAILs GETTERS. Commands are chosen so nothing moves
    #  but the walk: drives at power 0, limits of 0 (refused by value, after their units are parsed), and settings put
    #  back to their defaults -- which also restores the ramp the RAMP cell changed (setaccel 1000, setdecel 1470).
    if not os.path.isfile(demo_path):
        for crit in ("WRAPPER_LINES_AS_DOCUMENTED", "WRAPPER_REPLIES_AS_EXPECTED", "WRAPPER_GETTERS_MATCH_REPLY"):
            cell.nomeas("NONE", crit, 0, 0, "COUNT", "DEMO_NOT_FOUND", log)
    else:
        try:
            wrapper_class, ns = load_demo_wrappers(demo_path, log)
        except (SyntaxError, KeyError, OSError) as exc:
            log.line("SER-DEMOWRAP,load_error,{}".format(exc))
            wrapper_class = None
        if wrapper_class is None:
            for crit in ("WRAPPER_LINES_AS_DOCUMENTED", "WRAPPER_REPLIES_AS_EXPECTED", "WRAPPER_GETTERS_MATCH_REPLY"):
                cell.nomeas("NONE", crit, 0, 0, "COUNT", "DEMO_NOT_LOADED", log)
        else:
            _demowrap_calls(link, cell, wrapper_class, ns, log)
    cell.judge("NONE", "REPLY_FRAMING_DEFECTS", link.framing_defects if not link.dry else None, 0, 0, "COUNT")


def _demowrap_calls(link, cell, wrapper_class, ns, log):
    port = DemoPort(link, ns["queueRxLines"])
    wheels = wrapper_class(port)
    dist, rot, tim = ns["DrvDistUnits"], ns["DrvRotUnits"], ns["DrvTimeUnits"]
    ok = "OK"
    # (wrapper call, the documented line, the reply it must get: "OK", an ERROR prefix, or None for a getter
    #  with (prefix, count) to compare its return against)
    commands = [
        (lambda: wheels.setMaxSpeed(MAX_SPEED_DEFAULT), "setspeed 75", ok),
        (lambda: wheels.setMaxSpeedForDistance(MAX_SPEED_DEFAULT), "setspeedfordist 75", ok),
        (lambda: wheels.holdAtStop(False), "hold 0", ok),
        (lambda: wheels.setFaultResponse(FR_GRADED, BRAKE_PCT_DEFAULT), "setfaultresp 1 10", ok),
        (lambda: wheels.setHoldLimits(HOLD_CEILING_PCT, HOLD_RISE_MS, HOLD_LIMIT_MS), "setholdlimits 10 250 10000", ok),
        (lambda: wheels.setCommandTimeout(0), "settimeout 0", ok),
        (lambda: wheels.setAcceleration(ACCEL_BUILTIN_MM_S2), "setaccel 1000", ok),
        (lambda: wheels.setDeceleration(DECEL_BUILTIN_MM_S2), "setdecel 1470", ok),
        (lambda: wheels.clearProtectiveStop(), "protclear", ok),
        (lambda: wheels.driveAtPower(0, 0), "drivepwr 0 0", ok),
        (lambda: wheels.driveDirection(0, 0), "drivedir 0 0", ok),
        (lambda: wheels.emergencyCutoff(), "emercutoff", ok),
        (lambda: wheels.driveAtPower(10, 10), "drivepwr 10 10", "ERROR drivepwr failed: ERR_EMERGENCY_STOPPED (-1016)"),
        (lambda: wheels.clearEmergency(), "emerclear", ok),
        (lambda: wheels.driveForDistance(0, 0, dist.DDU_M), "drivedist 0 0 5", "ERROR LT-distance (0)"),
        (lambda: wheels.stopAfterRotation(0, rot.DRU_HALL_TICKS), "stopaftrot 0 1", "ERROR Rotation Count (0)"),
        (lambda: wheels.stopAfterDistance(0, dist.DDU_MM), "stopaftdist 0 1", "ERROR Distance Value (0)"),
        (lambda: wheels.stopAfterTime(0, tim.DTU_SECS), "stopafttime 0 2", "ERROR Time Value (0)"),
        (lambda: wheels.setStartChecks(False), "setstartchecks 0", "ERROR StartChecks apply only"),
        (lambda: wheels.checkWiring(), "checkwiring", ok),
        (lambda: wheels.resetTracking(), "resettracking", ok),
        (lambda: wheels.stopMotors(), "stopmotors", ok),
    ]
    getters = [
        (lambda: wheels.getDistance(dist.DDU_MM), "getdist 1", ("dist", 2)),
        (lambda: wheels.getRotationCount(rot.DRU_HALL_TICKS), "getrot 1", ("rot", 2)),
        (lambda: wheels.getPower(), "getpwr", ("pwr", 2)),
        (lambda: wheels.getStatus(), "getstatus", ("stat", 2)),
        (lambda: wheels.getMaxSpeed(), "getmaxspd", ("speedmax", 1)),
        (lambda: wheels.getMaxSpeedForDistance(), "getmaxspdfordist", ("speeddistmax", 1)),
        (lambda: wheels.getAcceleration(), "getaccel", ("accel", 1)),
        (lambda: wheels.getDeceleration(), "getdecel", ("decel", 1)),
        (lambda: wheels.getDriveVoltage(), "getvoltage", ("volt", 2)),
        (lambda: wheels.getProtectiveStop(), "getprot", ("prot", 2)),
        (lambda: wheels.getStopReason(), "getstopreason", ("stopreason", 2)),
        (lambda: wheels.getEvent(), "getevent", ("event", 4)),
        (lambda: wheels.getEventTotal(EV_STOP), "getevtotal 62", ("evtotal", 3)),
        (lambda: wheels.getError(), "geterror", ("err", 3)),
        (lambda: wheels.getHealth(), "gethealth", ("health", 6)),
        (lambda: wheels.getFaultResponse(), "getfaultresp", ("faultresp", 2)),
        (lambda: wheels.getHoldLimits(), "getholdlimits", ("holdlimits", 3)),
        (lambda: wheels.getPackVoltage(), "getpackvolt", ("packvolt", 2)),
        (lambda: wheels.getCurrent(), "getcurrent", ("current", 4)),
        (lambda: wheels.getFaultCause(), "getfaultcause", ("faultcause", 2)),
        (lambda: wheels.getHoldStatus(), "getholdstatus", ("holdstatus", 4)),
        (lambda: wheels.getHallIntegrityCounts(), "gethallcounts", ("hallcounts", 4)),
        (lambda: wheels.getHallIllegalCodes(), "gethallillegal", ("hallillegal", 4)),
    ]
    bad_lines = 0
    bad_replies = 0
    for call, line, want in commands:
        port.sent = port.reply = None
        try:
            call()
        except Exception as exc:                  # a wrapper that raises is a wrapper that failed
            log.line("SER-DEMOWRAP,cmd,{},raised,{}".format(line, type(exc).__name__))
        if port.sent != line + "\n":
            bad_lines += 1
        reply_ok = port.reply is not None and (port.reply == want if want == ok else port.reply.startswith(want))
        if not reply_ok:
            bad_replies += 1
        log.line("SER-DEMOWRAP,cmd,{},sent,{},reply,{},line_ok,{},reply_ok,{}".format(
            line, repr(port.sent), port.reply, fmt(port.sent == line + "\n"), fmt(reply_ok)))
    bad_getters = 0
    for call, line, (prefix, count) in getters:
        port.sent = port.reply = None
        returned = None
        try:
            returned = call()
        except Exception as exc:
            log.line("SER-DEMOWRAP,get,{},raised,{}".format(line, type(exc).__name__))
        if port.sent != line + "\n":
            bad_lines += 1
        wire = nums(port.reply, prefix, count)
        got = as_ints(returned)
        match = wire is not None and got == wire
        if not match:
            bad_getters += 1
        log.line("SER-DEMOWRAP,get,{},sent,{},reply,{},returned,{},match,{}".format(
            line, repr(port.sent), port.reply, repr(returned), fmt(match)))
    n_all = len(commands) + len(getters)
    cell.judge("NONE", "WRAPPER_LINES_AS_DOCUMENTED", bad_lines, 0, 0, "COUNT", n=n_all)
    cell.judge("NONE", "WRAPPER_REPLIES_AS_EXPECTED", bad_replies if not link.dry else None, 0, 0, "COUNT",
               n=len(commands))
    cell.judge("NONE", "WRAPPER_GETTERS_MATCH_REPLY", bad_getters if not link.dry else None, 0, 0, "COUNT",
               n=len(getters))


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


def resolve_port(name):
    """Return the device path for a port NAME (PORT_NAMES), or exit saying what is wrong. A glob must match exactly one
    device and "usb-auto" exactly one USB serial adapter: this never picks one of several."""
    if name not in PORT_NAMES:
        raise SystemExit("--port: unknown port name '{}'. Names: {}".format(name, ", ".join(PORT_NAMES)))
    path = PORT_NAMES[name]
    if name == "usb-auto":
        try:
            from serial.tools import list_ports
        except ImportError:
            raise SystemExit("--port usb-auto needs pyserial (pip install pyserial); or choose a named port")
        found = [p.device for p in list_ports.comports() if p.vid is not None]
        if len(found) != 1:
            raise SystemExit("--port usb-auto: {} USB serial adapters found ({}); choose a named port{}".format(
                len(found), ", ".join(found) or "none", " from --list-ports" if found else ""))
        return found[0]
    if "*" in path:
        import glob
        found = sorted(glob.glob(path))
        if len(found) != 1:
            raise SystemExit("--port {}: {} devices match {} ({}); choose a named port".format(
                name, len(found), path, ", ".join(found) or "none"))
        return found[0]
    return path


def clock_info(clock_name):
    """What the chosen clock implies for the serial link, for the evaluation to read: the P2's bit period at that clock
    (isp_serial_singleton.spin2:130, X := muldiv64(clkfreq, $1_0000, baud) & $FFFFFC00 | 7: whole clocks in X[31:16],
    64ths in X[15:10]) and the baud rate it therefore runs at."""
    hz = CLOCK_NAMES[clock_name]
    x = ((hz * 0x10000) // BAUD) & 0xFFFFFC00
    period_clocks = (x >> 10) / 64.0
    return hz, period_clocks, hz / period_clocks


def list_ports_and_exit():
    print("port names (--port):")
    for name, path in PORT_NAMES.items():
        print("  {:15s} {}".format(name, path if path else "the one USB serial adapter pyserial lists"))
    print("clock names (--clock), the Hz the serial top is built at (isp_steering_serial.spin2:23):")
    for name, hz in CLOCK_NAMES.items():
        print("  {:10s} {:>12,} Hz{}".format(name, hz, "  (provisional lowest supported clock)" if name == "clk-floor" else ""))
    print("build names (--build): {}".format(", ".join(BUILD_NAMES)))
    try:
        from serial.tools import list_ports
        found = list(list_ports.comports())
        print("serial ports on this host:" if found else "no serial ports on this host")
        for p in found:
            print("  {}  {}".format(p.device, p.description))
    except ImportError:
        print("(pyserial is not installed: its port list is not shown)")
    return 0


def main():
    parser = argparse.ArgumentParser(
        description="Certify the P2 serial control path (PL-148). Wheels up, hands off. The port, the clock and the build are "
                    "chosen by NAME (see --list-ports); nothing numeric is typed. The P2 must have been built at the chosen "
                    "clock (isp_steering_serial.spin2:23, CLK_FREQ) and be wired as SERIAL-CONTROL.md says.")
    parser.add_argument("--port", choices=sorted(PORT_NAMES), help="the serial port, by name")
    parser.add_argument("--clock", choices=sorted(CLOCK_NAMES), help="the clock the P2 was built at, by name")
    parser.add_argument("--build", choices=BUILD_NAMES, default="plain",
                        help="the P2 build under test: plain (pnut-ts) or debug (pnut-ts -d); default plain")
    parser.add_argument("--list-ports", action="store_true", help="print the port, clock and build names and this host's ports")
    parser.add_argument("--drive-voltage", default=DEFAULT_DRIVE_VOLTAGE,
                        help="the DRIVE_VOLTAGE the P2 was built with (default {}, the dual-motor configuration's)".format(
                            DEFAULT_DRIVE_VOLTAGE))
    parser.add_argument("--task", default="NA", help="todo task id for the SIGNOFF lines' task field (default NA)")
    parser.add_argument("--ident-wait", type=float, default=10.0, help="seconds to wait for the P2's ident line")
    parser.add_argument("--dry-run", action="store_true", help="print the planned command sequence; open no port")
    parser.add_argument("--demo", default=os.path.join(os.path.dirname(os.path.abspath(__file__)), DEMO_FILE),
                        help="the Python demo whose wrappers R20-SER-DEMOWRAP certifies (default: {} beside this "
                             "script); only its source is read".format(DEMO_FILE))
    args = parser.parse_args()
    if args.list_ports:
        return list_ports_and_exit()
    if args.clock is None:
        parser.error("--clock is required (choose a name: {}); --list-ports shows them".format(", ".join(CLOCK_NAMES)))
    if args.port is None and not args.dry_run:
        parser.error("--port is required for a run (choose a name: {}); --list-ports shows them".format(", ".join(PORT_NAMES)))
    expected_enum = parse_voltage(args.drive_voltage)
    port_path = resolve_port(args.port) if args.port and not args.dry_run else (args.port or "NA")
    clk_hz, bit_clocks, eff_baud = clock_info(args.clock)

    log_path = None
    if not args.dry_run:
        here = os.path.dirname(os.path.abspath(__file__))
        log_path = os.path.join(here, "serial-certify_{}.log".format(datetime.now().strftime("%y%m%d-%H%M%S")))
    log = Log(log_path)
    link = Link(log, port_path, BAUD, args.dry_run)

    log.line("SER-BANNER,script,serial_certify.py,ver,{},port_name,{},port,{},baud,{},clock,{},build,{},drive_voltage,{},dry_run,{}".format(
        SCRIPT_VERSION, args.port or "NA", port_path, BAUD, args.clock, args.build, args.drive_voltage, fmt(args.dry_run)),
        console=True)
    log.line("SER-CLOCK,name,{},hz,{},p2_built_at_this_clock,DECLARED_NOT_VERIFIED,bit_clocks,{:.4f},p2_baud,{:.1f},"
             "baud_error_ppm,{:.0f}".format(args.clock, fmt(clk_hz), bit_clocks, eff_baud, (eff_baud - BAUD) / BAUD * 1e6),
             console=True)
    log.line("SER-CLOCK-NOTE,the P2 must have been built with CLK_FREQ = {} (isp_steering_serial.spin2:23) and loaded; this "
             "script cannot read the P2's clock back{}".format(fmt(clk_hz), "; clk-floor is a provisional clock" if args.clock == "clk-floor" else ""),
             console=True)
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

        cell_latency(link, cells["R20-SER-LATENCY"], log)
        done.add("R20-SER-LATENCY")
        cell_numparse(link, cells["R20-SER-NUMPARSE"], log)
        done.add("R20-SER-NUMPARSE")
        cell_faultresp(link, cells["R20-SER-FAULTRESP"], fresh, log)
        done.add("R20-SER-FAULTRESP")
        cell_volt(link, cells["R20-SER-VOLT"], expected_enum, log)
        done.add("R20-SER-VOLT")
        cell_protclear(link, cells["R20-SER-PROTCLEAR"], log)
        done.add("R20-SER-PROTCLEAR")
        cell_errreply(link, cells["R20-SER-ERRREPLY"], log)
        done.add("R20-SER-ERRREPLY")
        cell_getters(link, cells["R20-SER-GETTERS"], log)
        done.add("R20-SER-GETTERS")
        cell_timeout(link, cells["R20-SER-TIMEOUT"], log)
        done.add("R20-SER-TIMEOUT")
        cell_ramp(link, cells["R20-SER-RAMP"], fresh, log)            # after every cell a changed ramp could affect
        done.add("R20-SER-RAMP")
        cell_backtoback(link, cells["R20-SER-BACKTOBACK"], args.build, log)   # after the cells whose state a wedged P2 would spoil
        done.add("R20-SER-BACKTOBACK")
        cell_demowrap(link, cells["R20-SER-DEMOWRAP"], args.demo, log)  # last: it judges the whole run's reply framing
        done.add("R20-SER-DEMOWRAP")
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

    counts = {"PASS": 0, "FAIL": 0, "NOMEAS": 0, "NOMEAS_BY_CONSTRUCTION": 0}
    for cell_id in CELLS:
        cell = cells[cell_id]
        if cell_id not in done:
            # a cell cut short: its partial lines stand, and it closes with a NOMEAS saying why
            cell.nomeas("NONE", "CELL_COMPLETED", True, True, "BOOL", abort_why or "NOT_RUN", log)
        for idx, text in enumerate(cell.lines):
            log.line(text, console=True)
            if idx in cell.by_construction:
                counts["NOMEAS_BY_CONSTRUCTION"] += 1          # stated, not counted: no run could measure it
            else:
                counts[text.rsplit(",", 1)[1]] += 1
    log.line("SER-SUMMARY,pass,{},fail,{},nomeas,{},nomeas_by_construction,{},abort,{}".format(
        counts["PASS"], counts["FAIL"], counts["NOMEAS"], counts["NOMEAS_BY_CONSTRUCTION"], abort_why or "NONE"), console=True)
    log.line("SER-SUMMARY-NOTE,nomeas_by_construction lines (PROTCLEAR LATCHED_STOP_RELEASED, GETTERS STARTCHECKS_OPT_OUT_STARTS) "
             "cannot be measured on this rig by what they are: the evaluation does not count them", console=True)
    if log_path:
        print("log: {}".format(log_path))
    log.close()
    return 1 if counts["FAIL"] or abort_why else 0


if __name__ == "__main__":
    sys.exit(main())

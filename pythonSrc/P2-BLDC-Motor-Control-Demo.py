#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import _thread
from datetime import datetime
from math import e
from pickle import TRUE
from time import time, sleep, localtime, strftime
import os
import subprocess
import sys
import os.path
import json
import argparse
from collections import deque
from pkg_resources import UnknownExtra
from unidecode import unidecode
from colorama import init as colorama_init
from colorama import Fore, Back, Style
import serial
from time import sleep
from configparser import ConfigParser
from email.mime.text import MIMEText
from subprocess import Popen, PIPE
import sendgrid
from sendgrid.helpers.mail import Content, Email, Mail
from enum import Enum, unique
from signal import signal, SIGPIPE, SIG_DFL
signal(SIGPIPE,SIG_DFL)
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

if False:
    # will be caught by python 2.7 to be illegal syntax
    print_line('Sorry, this script requires a python3 runtime environment.', file=sys.stderr)
    os._exit(1)

script_version  = "1.0.0"
script_name     = 'P2-BLDC-Motor-Control-Demo.py'
script_info     = '{} v{}'.format(script_name, script_version)
project_name    = 'P2-BLDC-Motor-Control'
project_url     = 'https://github.com/ironsheep/P2-BLDC-Motor-Control'

# -----------------------------------------------------------------------------
# the BELOW are identical to that found in our gateway .spin2 object
#   (!!!they must be kept in sync!!!)
# -----------------------------------------------------------------------------

# markers found within the data arriving from the P2 but likely will NOT be found in normal user data sent by the P2
parm_sep    = '^|^'

# -----------------------------------------------------------------------------
#  External Interface constants (Enums) exposed by isp_bldc_motor.spin2
#  REF: https://github.com/ironsheep/P2-BLDC-Motor-Control/blob/develop/isp_bldc_motor.spin2
# -----------------------------------------------------------------------------
"""
    ' Driver Distance-Units Enum: (Millimeters, Centimeters, Inches, Feet, Meters, Kilometers, Miles)
    #0, DDU_Unknown, DDU_MM, DDU_CM, DDU_IN, DDU_FT, DDU_M, DDU_KM, DDU_MI

    ' Driver Rotation-Units Enum:
    #0, DRU_Unknown, DRU_HALL_TICKS, DRU_DEGREES, DRU_ROTATIONS

    ' Driver Time-Unit Enum:
    #0, DTU_Unknown, DTU_MILLISEC, DTU_SEC

    ' Driver Status Enum:
    #10, DS_Unknown, DS_MOVING, DS_HOLDING, DS_OFF, DS_FAULTED, DS_ESTOP

    ' Driver Control Stop-State Enum:
    #0, SM_Unknown, SM_FLOAT, SM_BRAKE
"""

# the following enum name orders and starting values must be identical to that
#  found in our isp_bldc_motor.spin2 object
DrvDistUnits = Enum('DrvDistUnits', [
     'DDU_Unknown',
     'DDU_MM',
     'DDU_CM',
     'DDU_IN',
     'DDU_FT',
     'DDU_M',
     'DDU_KM',
     'DDU_MI'], start=0)

DrvRotUnits = Enum('DrvRotUnits', [
     'DRU_Unknown',
     'DRU_HALL_TICKS',
     'DRU_DEGREES',
     'DRU_ROTATIONS'], start=0)

DrvTimeUnits = Enum('DrvTimeUnits', [
     'DTU_Unknown',
     'DTU_MILLISEC',
     'DTU_SECS'], start=0)

DrvStatus = Enum('DrvStatus', [
     'DS_Unknown',
     'DS_MOVING',
     'DS_HOLDING',
     'DS_OFF',
     'DS_FAULTED',
     'DS_ESTOP'], start=10)

DrvStopState = Enum('DrvStopState', [
     'SM_Unknown',
     'SM_FLOAT',
     'SM_BRAKE'], start=0)


#   Colorama constants:
#  Fore: BLACK, RED, GREEN, YELLOW, BLUE, MAGENTA, CYAN, WHITE, RESET.
#  Back: BLACK, RED, GREEN, YELLOW, BLUE, MAGENTA, CYAN, WHITE, RESET.
#  Style: DIM, NORMAL, BRIGHT, RESET_ALL
#
# Logging function
def print_line(text, error=False, warning=False, info=False, verbose=False, debug=False, console=True):
    timestamp = strftime('%Y-%m-%d %H:%M:%S', localtime())
    if console:
        if error:
            print(Fore.RED + Style.BRIGHT + '[{}] '.format(timestamp) + Style.NORMAL + '{}'.format(text) + Style.RESET_ALL, file=sys.stderr)
        elif warning:
            print(Fore.YELLOW + Style.BRIGHT + '[{}] '.format(timestamp) + Style.NORMAL + '{}'.format(text) + Style.RESET_ALL)
        elif info or verbose:
            if verbose:
                # conditional verbose output...
                if opt_verbose:
                    print(Fore.GREEN + '[{}] '.format(timestamp) + Fore.YELLOW  + '- ' + '{}'.format(text) + Style.RESET_ALL)
            else:
                # info...
                print(Fore.MAGENTA + '[{}] '.format(timestamp) + Fore.WHITE  + '- ' + '{}'.format(text) + Style.RESET_ALL)
        elif debug:
            # conditional debug output...
            if opt_debug:
                print(Fore.CYAN + '[{}] '.format(timestamp) + '- (DBG): ' + '{}'.format(text) + Style.RESET_ALL)
        else:
            print(Fore.GREEN + '[{}] '.format(timestamp) + Style.RESET_ALL + '{}'.format(text) + Style.RESET_ALL)

# -----------------------------------------------------------------------------
#  Script Argument parsing
# -----------------------------------------------------------------------------

# Argparse
opt_debug = False
opt_verbose = False
opt_useTestFile = False

# Argparse
parser = argparse.ArgumentParser(description=project_name, epilog='For further details see: ' + project_url)
parser.add_argument("-v", "--verbose", help="increase output verbosity", action="store_true")
parser.add_argument("-d", "--debug", help="show debug output", action="store_true")
parse_args = parser.parse_args()

opt_verbose = parse_args.verbose
opt_debug = parse_args.debug

print_line(script_info, info=True)
if opt_verbose:
    print_line('Verbose enabled', verbose=True)
if opt_debug:
    print_line('Debug enabled', debug=True)


# -----------------------------------------------------------------------------
#  CLASS methods indentifying RPi host hardware/software
# -----------------------------------------------------------------------------

#  object that provides access to information about the RPi on which we are running
class RPiHostInfo:

    def getDeviceModel(self):
        out = subprocess.Popen("/bin/cat /proc/device-tree/model | /bin/sed -e 's/\\x0//g'",
                            shell=True,
                            stdout=subprocess.PIPE,
                            stderr=subprocess.STDOUT)
        stdout, _ = out.communicate()
        model_raw = stdout.decode('utf-8')
        # now reduce string length (just more compact, same info)
        model = model_raw.replace('Raspberry ', 'R').replace(
            'i Model ', 'i 1 Model').replace('Rev ', 'r').replace(' Plus ', '+ ')

        print_line('rpi_model_raw=[{}]'.format(model_raw), debug=True)
        print_line('rpi_model=[{}]'.format(model), debug=True)
        return model, model_raw

    def getLinuxRelease(self):
        out = subprocess.Popen("/bin/cat /etc/apt/sources.list | /bin/egrep -v '#' | /usr/bin/awk '{ print $3 }' | /bin/grep . | /usr/bin/sort -u",
                            shell=True,
                            stdout=subprocess.PIPE,
                            stderr=subprocess.STDOUT)
        stdout, _ = out.communicate()
        linux_release = stdout.decode('utf-8').rstrip()
        print_line('rpi_linux_release=[{}]'.format(linux_release), debug=True)
        return linux_release


    def getLinuxVersion(self):
        out = subprocess.Popen("/bin/uname -r",
                            shell=True,
                            stdout=subprocess.PIPE,
                            stderr=subprocess.STDOUT)
        stdout, _ = out.communicate()
        linux_version = stdout.decode('utf-8').rstrip()
        print_line('rpi_linux_version=[{}]'.format(linux_version), debug=True)
        return linux_version


    def getHostnames(self):
        out = subprocess.Popen("/bin/hostname -f",
                            shell=True,
                            stdout=subprocess.PIPE,
                            stderr=subprocess.STDOUT)
        stdout, _ = out.communicate()
        fqdn_raw = stdout.decode('utf-8').rstrip()
        print_line('fqdn_raw=[{}]'.format(fqdn_raw), debug=True)
        lcl_hostname = fqdn_raw
        if '.' in fqdn_raw:
            # have good fqdn
            nameParts = fqdn_raw.split('.')
            lcl_fqdn = fqdn_raw
            tmpHostname = nameParts[0]
        else:
            # missing domain, if we have a fallback apply it
            if len(fallback_domain) > 0:
                lcl_fqdn = '{}.{}'.format(fqdn_raw, fallback_domain)
            else:
                lcl_fqdn = lcl_hostname

        print_line('rpi_fqdn=[{}]'.format(lcl_fqdn), debug=True)
        print_line('rpi_hostname=[{}]'.format(lcl_hostname), debug=True)
        return lcl_hostname, lcl_fqdn

# -----------------------------------------------------------------------------
#  CLASS: Maintain Runtime Configuration values
# -----------------------------------------------------------------------------

#  object that provides access to gateway runtime confiration data
class RuntimeConfig:
    # Host RPi keys
    keyRPiModel = "Model"
    keyRPiMdlFull = "ModelFull"
    keyRPiRel = "OsRelease"
    keyRPiVer = "OsVersion"
    keyRPiName = "Hostname"
    keyRPiFqdn = "FQDN"

    # P2 Hardware/Application keys
    keyHwName = "hwName"
    keyObjVer = "objVer"

    #  searchable list of keys
    configKnownKeys = [ keyHwName, keyObjVer,
                        keyRPiModel, keyRPiMdlFull, keyRPiRel, keyRPiVer, keyRPiName, keyRPiFqdn ]

    configDictionary = {}   # initially empty

    def validateKey(self, name):
        # ensure a key we are trying to set/get is expect by this system
        #   generate warning if NOT
        if name not in self.configKnownKeys:
            print_line('CONFIG-Dict: Unexpected key=[{}]!!'.format(name), warning=True)

    def containsKey(self, possKey):
        # ensure a key we are trying to set/get is expect by this system
        #   generate warning if NOT
        foundKeyStatus = False
        if possKey in self.configDictionary:
            foundKeyStatus = True
        return foundKeyStatus

    def setConfigNamedVarValue(self, name, value):
        # set a config value for name
        global configDictionary
        self.validateKey(name)   # warn if key isn't a know key
        foundKey = False
        if name in self.configDictionary.keys():
            oldValue = self.configDictionary[name]
            foundKey = True
        self.configDictionary[name] = value
        if foundKey and oldValue != value:
            print_line('CONFIG-Dict: [{}]=[{}]->[{}]'.format(name, oldValue, value), debug=True)
        else:
            print_line('CONFIG-Dict: [{}]=[{}]'.format(name, value), debug=True)

    def getValueForConfigVar(self, name):
        # return a config value for name
        # print_line('CONFIG-Dict: get({})'.format(name), debug=True)
        self.validateKey(name)   # warn if key isn't a know key
        dictValue = ""
        if name in self.configDictionary.keys():
            dictValue = self.configDictionary[name]
            print_line('CONFIG-Dict: [{}]=[{}]'.format(name, dictValue), debug=True)
        else:
            print_line('CONFIG-Dict: [{}] NOT FOUND'.format(name, dictValue), warning=True)
        return dictValue


# -----------------------------------------------------------------------------
#  CLASS: Circular queue for serial input lines & serial listener
# -----------------------------------------------------------------------------

# object which is a queue of text lines
#  these arrive at a rate different from our handling them rate
#  so we put them in a queue while they wait to be handled
class RxLineQueue:

    lineBuffer = deque()

    def pushLine(self, newLine):
        self.lineBuffer.append(newLine)
        # show debug every 100 lines more added
        if len(self.lineBuffer) % 100 == 0:
            print_line('- lines({})'.format(len(self.lineBuffer)),debug=True)

    def popLine(self):
        oldestLine = ''
        if len(self.lineBuffer) > 0:
            oldestLine = self.lineBuffer.popleft()
        return oldestLine

    def lineCount(self):
        return len(self.lineBuffer)

# -----------------------------------------------------------------------------
#  CLASS: An interface for easy BLDC Motor control (over serial I/F)
# -----------------------------------------------------------------------------

class BLDCMotorControl:
    serPort = ''

    # create a new instance with the given serial port
    def __init__(self, serialPort):
        self.serPort = serialPort

    # -----------------------
    # PUBLIC Control Methods
    # -----------------------
    # PUB driveDirection(power, direction)
    def driveDirection(self, power, direction):
        commandStr = 'drivedir {} {}\n'.format(power, direction)
        self.sendCommand(commandStr)

    # PUB driveForDistance(leftDistance, rightDistance, distanceUnits)
    def driveForDistance(self, leftDistance, rightDistance, eDistanceUnits):
        commandStr = 'drivedist {} {} {}\n'.format(leftDistance, rightDistance, eDistanceUnits.value)
        self.sendCommand(commandStr)

    # PUB driveAtPower(leftPower, rightPower)
    def driveAtPower(self, leftPower, rightPower):
        commandStr = 'drivepwr {} {}\n'.format(leftPower, rightPower)
        self.sendCommand(commandStr)

    # PUB stopAfterRotation(rotationCount, rotationUnits)
    def stopAfterRotation(self, rotationCount, eRotationUnits):
        commandStr = 'stopaftrot {} {}\n'.format(rotationCount, eRotationUnits.value)
        self.sendCommand(commandStr)

    # PUB stopAfterDistance(distance, distanceUnits)
    def stopAfterDistance(self, distance, eDistanceUnits):
        commandStr = 'stopaftdist {} {}\n'.format(distance, eDistanceUnits.value)
        self.sendCommand(commandStr)

    # PUB stopAfterTime(time, timeUnits)
    def stopAfterTime(self, time, eTimeUnits):
        commandStr = 'stopafttime {} {}\n'.format(time, eTimeUnits.value)
        self.sendCommand(commandStr)

    # PUB stopMotors()
    def stopMotors(self):
        commandStr = 'stopmotors\n'
        self.sendCommand(commandStr)

    # PUB emergencyCutoff()
    def emergencyCutoff(self):
        commandStr = 'emercutoff\n'
        self.sendCommand(commandStr)

    # PUB clearEmergency()
    def clearEmergency(self):
        commandStr = 'emerclear\n'
        self.sendCommand(commandStr)

    # PUB clearProtectiveStop()
    #  releases a latched protective stop (a blocked motor); emerclear does not
    def clearProtectiveStop(self):
        commandStr = 'protclear\n'
        self.sendCommand(commandStr)

    # -------------------------
    # PUBLIC Configure Methods
    # -------------------------
    # PUB setAcceleration(rate)
    def setAcceleration(self, rate):
        commandStr = 'setaccel {}\n'.format(rate)
        self.sendCommand(commandStr)

    # PUB setMaxSpeed(speed)
    def setMaxSpeed(self, speed):
        commandStr = 'setspeed {}\n'.format(speed)
        self.sendCommand(commandStr)

    # PUB setMaxSpeedForDistance(speed)
    def setMaxSpeedForDistance(self, speed):
        commandStr = 'setspeedfordist {}\n'.format(speed)
        self.sendCommand(commandStr)

    # PUB holdAtStop(bEnable)
    #  the P2 takes a boolean as -1 (true) or 0 (false)
    def holdAtStop(self, bEnable):
        commandStr = 'hold {}\n'.format(self.p2Bool(bEnable))
        self.sendCommand(commandStr)

    # PUB setFaultResponse(eMode, brakePct)
    #  eMode 0 (FR_SHIPPED) or 1 (FR_GRADED); brakePct [0 to 100]
    def setFaultResponse(self, eMode, brakePct):
        commandStr = 'setfaultresp {} {}\n'.format(eMode, brakePct)
        self.sendCommand(commandStr)

    # PUB setHoldLimits(ceilingPct, riseMs, limitMs)
    def setHoldLimits(self, ceilingPct, riseMs, limitMs):
        commandStr = 'setholdlimits {} {} {}\n'.format(ceilingPct, riseMs, limitMs)
        self.sendCommand(commandStr)

    # PUB setStartChecks(bRefuse)
    #  answered only when the P2's start checks refused the platform: False starts it anyway, True keeps the refusal.
    #  While the motors run the P2 replies ERROR (they started before the link opened)
    def setStartChecks(self, bRefuse):
        commandStr = 'setstartchecks {}\n'.format(self.p2Bool(bRefuse))
        self.sendCommand(commandStr)

    # PUB checkWiring()
    #  MOVES THE ROBOT: turns it a few degrees in place and back (about 0.5 s). The verdict is each wheel's
    #  HLT_WIRING bit (32) in getHealth()
    def checkWiring(self):
        commandStr = 'checkwiring\n'
        self.sendCommand(commandStr)

    # PUB setCommandTimeout(nMs)
    #  link-loss guard, off (0) by default: once on, resend a drive command at least every nMs
    #  or the P2 stops both motors and reports ERR_COMMAND_TIMEOUT
    def setCommandTimeout(self, nMs):
        commandStr = 'settimeout {}\n'.format(nMs)
        self.sendCommand(commandStr)

    # PUB resetTracking()
    def resetTracking(self):
        commandStr = 'resettracking\n'
        self.sendCommand(commandStr)

    # ----------------------
    # PUBLIC Status Methods
    # ----------------------
    # PUB getDistance(distanceUnits) : leftDistanceInUnits, rightDistanceInUnits
    def getDistance(self, eDistanceUnits):
        commandStr = 'getdist {}\n'.format(eDistanceUnits.value)
        responseStr = self.sendCommand(commandStr)
        ltValue, rtValue = self.getValues('dist', responseStr, 2)
        return ltValue, rtValue

    # PUB getRotationCount(rotationUnits) : leftRotationCount, rightRotationCount
    def getRotationCount(self, eRotationUnits) :
        commandStr = 'getrot {}\n'.format(eRotationUnits.value)
        responseStr = self.sendCommand(commandStr)
        ltValue, rtValue = self.getValues('rot', responseStr, 2)
        return int(ltValue), int(rtValue)

    # PUB getPower() : leftPower, rightPower
    def getPower(self):
        commandStr = 'getpwr\n'
        responseStr = self.sendCommand(commandStr)
        ltValue, rtValue = self.getValues('pwr', responseStr, 2)
        return ltValue, rtValue

    # PUB getStatus() : eLeftStatus, eRightStatus
    def getStatus(self):
        commandStr = 'getstatus\n'
        responseStr = self.sendCommand(commandStr)
        ltValue, rtValue = self.getValues('stat', responseStr, 2)
        return self.statusEnumFor(ltValue), self.statusEnumFor(rtValue)

    # PUB getMaxSpeed() : maxSpeed
    def getMaxSpeed(self):
        commandStr = 'getmaxspd\n'
        responseStr = self.sendCommand(commandStr)
        onlyValue = self.getValues('speedmax', responseStr, 1)
        return onlyValue

    # PUB getMaxSpeedForDistance() : maxSpeed4dist
    def getMaxSpeedForDistance(self):
        commandStr = 'getmaxspdfordist\n'
        responseStr = self.sendCommand(commandStr)
        onlyValue = self.getValues('speeddistmax', responseStr, 1)
        return onlyValue

    # PUB getDriveVoltage() : eVoltage, nMilliVolts
    #  the configured drive (battery) voltage, as the P2's PWR_* value and its nominal mV; not a measurement
    def getDriveVoltage(self):
        commandStr = 'getvoltage\n'
        responseStr = self.sendCommand(commandStr)
        eVoltage, nMilliVolts = self.getValues('volt', responseStr, 2)
        return int(eVoltage), int(nMilliVolts)

    # PUB getProtectiveStop() : eLeftCode, eRightCode
    #  each wheel's latched protective-stop code (e.g. -2001 ERR_PLATFORM_BLOCKED), 0 when none
    def getProtectiveStop(self):
        commandStr = 'getprot\n'
        responseStr = self.sendCommand(commandStr)
        eLeftCode, eRightCode = self.getValues('prot', responseStr, 2)
        return int(eLeftCode), int(eRightCode)

    # PUB getStopReason() : eLeftReason, eRightReason
    #  why each wheel's last drive ended: 40 SR_NONE .. 48 SR_PARTNER (46 SR_LINK_LOST: the command timeout stopped it)
    def getStopReason(self):
        commandStr = 'getstopreason\n'
        responseStr = self.sendCommand(commandStr)
        eLeftReason, eRightReason = self.getValues('stopreason', responseStr, 2)
        return int(eLeftReason), int(eRightReason)

    # PUB getEvent() : eKind, nMs, eWheel, nValue
    #  the oldest event not yet read over this link; eKind 60 (EV_NONE) when there is none
    def getEvent(self):
        commandStr = 'getevent\n'
        responseStr = self.sendCommand(commandStr)
        eKind, nMs, eWheel, nValue = self.getValues('event', responseStr, 4)
        return int(eKind), int(nMs), int(eWheel), int(nValue)

    # PUB getEventTotal(eKind) : nLeft, nRight, nPlatform
    #  eKind [62 to 75]
    def getEventTotal(self, eKind):
        commandStr = 'getevtotal {}\n'.format(eKind)
        responseStr = self.sendCommand(commandStr)
        nLeft, nRight, nPlatform = self.getValues('evtotal', responseStr, 3)
        return int(nLeft), int(nRight), int(nPlatform)

    # PUB getError() : eError, eLeftError, eRightError
    #  read AND clear the first error codes recorded for this link (0 when none); -1019 is ERR_COMMAND_TIMEOUT
    def getError(self):
        commandStr = 'geterror\n'
        responseStr = self.sendCommand(commandStr)
        eError, eLeftError, eRightError = self.getValues('err', responseStr, 3)
        return int(eError), int(eLeftError), int(eRightError)

    # PUB getHealth() : nLeftChecked, nLeftFailed, nLeftRecovered, nRightChecked, nRightFailed, nRightRecovered
    #  HLT_* bits: 1 HALLS, 2 SENSE_ZERO, 4/8/16 PHASE_U/V/W, 32 WIRING, 64 PACK
    def getHealth(self):
        commandStr = 'gethealth\n'
        responseStr = self.sendCommand(commandStr)
        values = self.getValues('health', responseStr, 6)
        return tuple(int(value) for value in values)

    # PUB getFaultResponse() : eMode, brakePct
    def getFaultResponse(self):
        commandStr = 'getfaultresp\n'
        responseStr = self.sendCommand(commandStr)
        eMode, brakePct = self.getValues('faultresp', responseStr, 2)
        return int(eMode), int(brakePct)

    # PUB getHoldLimits() : ceilingPct, riseMs, limitMs
    def getHoldLimits(self):
        commandStr = 'getholdlimits\n'
        responseStr = self.sendCommand(commandStr)
        ceilingPct, riseMs, limitMs = self.getValues('holdlimits', responseStr, 3)
        return int(ceilingPct), int(riseMs), int(limitMs)

    # PUB getPackVoltage() : ePackStatus, nMilliVolts
    #  the optional pack sensor: status 0 PACK_NOT_FITTED, 1 PACK_ABSENT, 2 PACK_PRESENT; mV is 0 unless PACK_PRESENT
    def getPackVoltage(self):
        commandStr = 'getpackvolt\n'
        responseStr = self.sendCommand(commandStr)
        ePackStatus, nMilliVolts = self.getValues('packvolt', responseStr, 2)
        return int(ePackStatus), int(nMilliVolts)

    # PUB getCurrent() : nLtAmps, nLtWatts, nRtAmps, nRtWatts
    #  current in units of 0.1 mA (amps x 10,000) and power in mW, for each motor
    def getCurrent(self):
        commandStr = 'getcurrent\n'
        responseStr = self.sendCommand(commandStr)
        nLtAmps, nLtWatts, nRtAmps, nRtWatts = self.getValues('current', responseStr, 4)
        return int(nLtAmps), int(nLtWatts), int(nRtAmps), int(nRtWatts)

    # PUB getFaultCause() : eLeftCause, eRightCause
    #  0 FC_NONE, 1 FC_LAG (the rotor could not follow the field), 2 FC_HALL (a hall sensor read %000 or %111)
    def getFaultCause(self):
        commandStr = 'getfaultcause\n'
        responseStr = self.sendCommand(commandStr)
        eLeftCause, eRightCause = self.getValues('faultcause', responseStr, 2)
        return int(eLeftCause), int(eRightCause)

    # PUB getHoldStatus() : eLeftState, nLeftDisplacement, eRightState, nRightDisplacement
    #  state 0 HS_OFF, 1 HS_HOLDING, 2 HS_SLIPPED, 3 HS_LIMITED; displacement in signed hall ticks
    def getHoldStatus(self):
        commandStr = 'getholdstatus\n'
        responseStr = self.sendCommand(commandStr)
        eLeftState, nLeftDisp, eRightState, nRightDisp = self.getValues('holdstatus', responseStr, 4)
        return int(eLeftState), int(nLeftDisp), int(eRightState), int(nRightDisp)

    # PUB getHallIntegrityCounts() : nLtMissed, nLtIllegal, nRtMissed, nRtIllegal
    def getHallIntegrityCounts(self):
        commandStr = 'gethallcounts\n'
        responseStr = self.sendCommand(commandStr)
        nLtMissed, nLtIllegal, nRtMissed, nRtIllegal = self.getValues('hallcounts', responseStr, 4)
        return int(nLtMissed), int(nLtIllegal), int(nRtMissed), int(nRtIllegal)

    # PUB getHallIllegalCodes() : nLtAllLow, nLtAllHigh, nRtAllLow, nRtAllHigh
    def getHallIllegalCodes(self):
        commandStr = 'gethallillegal\n'
        responseStr = self.sendCommand(commandStr)
        nLtAllLow, nLtAllHigh, nRtAllLow, nRtAllHigh = self.getValues('hallillegal', responseStr, 4)
        return int(nLtAllLow), int(nLtAllHigh), int(nRtAllLow), int(nRtAllHigh)

    # ------- PRIVATE (Support) Methods --------
    def p2Bool(self, bValue):
        # the P2's serial booleans: -1 true, 0 false
        return -1 if bValue else 0

    # common send method
    def sendCommand(self, cmdStr):
        # format and send command, then wait for single line response
        # if other than error|OK then return the response string
        newOutLine = cmdStr.encode('utf-8')
        print_line('send line({})=({})'.format(len(newOutLine), newOutLine), verbose=True)
        self.serPort.write(newOutLine)
        responseStr = self.processResponse()
        return responseStr

    # common rx repsonse method
    def processResponse(self):
        # wait for 1-line response
        # show debug/error if OK|error
        # otherwise return the response string
        global queueRxLines
        responseStr = ''
        while queueRxLines.lineCount() == 0:
            sleep(0.2)  # wait for 2/10th of second before asking again

        currLine = queueRxLines.popLine().replace('\\n', '')
        if currLine.startswith(responseOK):
            print_line('Incoming OK', debug=True)

        elif currLine.startswith(responseERROR):
            print_line('! {}'.format(currLine), error=True)
        else:
            responseStr = currLine
        return responseStr;

    def getValues(self, linePrefix, line, ctExpected):
        # given the response string, isolate and return the response values
        lineParts = line.split(' ')
        if len(lineParts) < 2:
            print_line('! ERROR: not enough parts in line={}'.format(line.replace('\\n', '')), error=True)
        elif lineParts[0] != linePrefix:
              print_line('! ERROR: BAD line={} missing prefix [{}]'.format(line.replace('\\n', ''), linePrefix), error=True)
        elif len(lineParts) != ctExpected + 1:
              print_line('! ERROR: BAD line={} wrong number reponses, expected ({})'.format(line.replace('\\n', ''), ctExpected), error=True)
        else:
            if ctExpected == 1:
                return lineParts[1]
            else:
                return tuple(lineParts[1:])

    def statusEnumFor(self, iValue):
        # return enum member assoc with int value
        desiredValue = DrvStatus.DS_Unknown
        if int(iValue) in DrvStatus._value2member_map_:
            desiredValue = DrvStatus(int(iValue))
        #print_line('found ENUM {} for {}'.format(desiredValue, iValue), debug=True)
        return desiredValue

# -----------------------------------------------------------------------------
#  TASK: dedicated serial listener
# -----------------------------------------------------------------------------

def taskSerialListener(serPort):
    global queueRxLines
    print_line('Thread: taskSerialListener() started', verbose=True)
    # process lies from serial or from test file
    if opt_useTestFile == True:
        test_file=open("charlie_rpi_debug.out", "r")
        lines = test_file.readlines()
        for currLine in lines:
            queueRxLines.pushLine(currLine)
            #sleep(0.1)
    else:
        # queue lines received as quickly as they come in...
        while True:
            received_data = serPort.readline()              #read serial port
            if len(received_data) > 0:
                print_line('TASK-RX rxD({})=({})'.format(len(received_data),received_data), debug=True)
                currLine = received_data.decode('utf-8', 'replace').rstrip()
                #print_line('TASK-RX line({}=[{}]'.format(len(currLine), currLine), debug=True)
                if currLine != '\\n':    # skip blank lines...
                    queueRxLines.pushLine(currLine)
                    if currLine.startswith(cmdIdentifyHW):
                        processInput(serPort)
                else:
                    print_line('TASK-RX skip empty-line({}=[{}]'.format(len(currLine), currLine), warning=True)


# commands from P2
cmdIdentifyHW  = "ident:"
responseOK  = "OK"
responseERROR = "ERROR"

def processIncomingRequest(newLine, serPort):

    print_line('Incoming line({})=[{}]'.format(len(newLine), newLine), debug=True)

    if newLine.startswith(responseOK):
        print_line('Incoming OK', debug=True)

    elif newLine.startswith(responseERROR):
        print_line('Incoming errStr({})=({})'.format(len(newLine), newLine), error=True)

    elif newLine.startswith(cmdIdentifyHW):
        print_line('* HANDLE id P2 Hardware', verbose=True)
        nameValuePairs = getNameValuePairs(newLine, cmdIdentifyHW)
        if len(nameValuePairs) > 0:
            findingsDict = processNameValuePairs(nameValuePairs)
            # Record the hardware info for later use
            if len(findingsDict) > 0:
                p2ProcDict = {}
                for key in findingsDict:
                    runtimeConfig.setConfigNamedVarValue(key, findingsDict[key])
                    p2ProcDict[key] = findingsDict[key]
                sendValidationSuccess(serPort, "fident", "", "")
            else:
                print_line('processIncomingRequest nameValueStr({})=({}) ! missing hardware keys !'.format(len(newLine), newLine), warning=True)

    else:
        print_line('ERROR: line({})=[{}] ! P2 LINE NOT Recognized !'.format(len(newLine), newLine), error=True)


def processInput(serPort):
    # process all queued lines then stop
    global queueRxLines
    while True:
        # process an incoming line
        currLine = queueRxLines.popLine()

        if len(currLine) > 0:
            processIncomingRequest(currLine, serPort)
        else:
            # if no more lines, exit loop
            break

def getNameValuePairs(strRequest, cmdStr):
    # isolate name-value pairs found within {strRequest} (after removing prefix {cmdStr})
    rmdr = strRequest.replace(cmdStr,'')
    nameValuePairs = rmdr.split(parm_sep)
    print_line('getNameValuePairs nameValuePairs({})=({})'.format(len(nameValuePairs), nameValuePairs), debug=True)
    return nameValuePairs

def processNameValuePairs(nameValuePairsAr):
    # parse the name value pairs - return of dictionary of findings
    findingsDict = {}
    for nameValueStr in nameValuePairsAr:
        if '=' in nameValueStr:
            name,value = nameValueStr.split('=', 1)
            print_line('  [{}]=[{}]'.format(name, value), debug=True)
            findingsDict[name] = value
        else:
            print_line('processNameValuePairs nameValueStr({})=({}) ! missing "=" !'.format(len(nameValueStr), nameValueStr), warning=True)
    return findingsDict

def sendValidationError(serPort, cmdPrefixStr, errorMessage):
    # format and send an error message via outgoing serial
    successStatus = False
    responseStr = '{}:status={}{}msg={}\n'.format(cmdPrefixStr, successStatus, parm_sep, errorMessage)
    newOutLine = responseStr.encode('utf-8')
    print_line('sendValidationError line({})=[{}]'.format(len(newOutLine), newOutLine), error=True)
    serPort.write(newOutLine)

def sendValidationSuccess(serPort, cmdPrefixStr, returnKeyStr, returnValueStr):
    # format and send an error message via outgoing serial
    successStatus = True
    if(len(returnKeyStr) > 0):
        # if we have a key we're sending along an extra KV pair
        responseStr = '{}:status={}{}{}={}\n'.format(cmdPrefixStr, successStatus, parm_sep, returnKeyStr, returnValueStr)
    else:
        # no key so just send final status
        responseStr = '{}:status={}\n'.format(cmdPrefixStr, successStatus)
    newOutLine = responseStr.encode('utf-8')
    print_line('sendValidationSuccess line({})=({})'.format(len(newOutLine), newOutLine), verbose=True)
    serPort.write(newOutLine)


# -----------------------------------------------------------------------------
#  Main loop
# -----------------------------------------------------------------------------

# and allocate our single runtime config store
runtimeConfig = RuntimeConfig()


# alocate our access to our Host Info
rpiHost = RPiHostInfo()

rpi_model, rpi_model_raw = rpiHost.getDeviceModel()
rpi_linux_release = rpiHost.getLinuxRelease()
rpi_linux_version = rpiHost.getLinuxVersion()
rpi_hostname, rpi_fqdn = rpiHost.getHostnames()

# record RPi into to runtimeConfig
runtimeConfig.setConfigNamedVarValue(runtimeConfig.keyRPiModel, rpi_model)
runtimeConfig.setConfigNamedVarValue(runtimeConfig.keyRPiMdlFull, rpi_model_raw)
runtimeConfig.setConfigNamedVarValue(runtimeConfig.keyRPiRel, rpi_linux_release)
runtimeConfig.setConfigNamedVarValue(runtimeConfig.keyRPiVer, rpi_linux_version)
runtimeConfig.setConfigNamedVarValue(runtimeConfig.keyRPiName, rpi_hostname)
runtimeConfig.setConfigNamedVarValue(runtimeConfig.keyRPiFqdn, rpi_fqdn)
colorama_init()  # Initialize our color console system

# start our serial receive listener

# 1,440,000 = 150x 9600 baud  FAILS P2 Tx
#   864,000 =  90x 9600 baud  FAILS P2 Tx
#   720,000 =  75x 9600 baud  FAILS P2 Rx
#   672,000 =  70x 9600 baud  FAILS P2 Rx
#   624,000 =  65x 9600 baud  GOOD (Serial test proven)
#   499,200 =  52x 9600 baud
#   480,000 =  50x 9600 baud
#
baudRate = 624000
print_line('Baud rate: {:,} bits/sec'.format(baudRate), verbose=True)

serialPort = serial.Serial ("/dev/serial0", baudRate, timeout=1)    #Open port with baud rate & timeout

queueRxLines = RxLineQueue()

_thread.start_new_thread(taskSerialListener, ( serialPort, ))

sleep(1)    # allow threads to start...

# create our motor interface handing it our serial port to use
wheels = BLDCMotorControl(serialPort)

# a quick method using wheels lack-of-motion to determine when
#   can ask motors to do another command...
def waitForMotorsStopped():
    bothStopped = False
    priorLtCt = -1
    priorRtCt = -1
    while bothStopped == False:
        # get status
        # PUB getRotationCount(rotationUnits) : leftRotationCount, rightRotationCount
        ltCount, rtCount = wheels.getRotationCount(DrvRotUnits.DRU_HALL_TICKS)
        print_line('- counts {}, {}'.format(ltCount, rtCount), debug=True)
        #while not stopped loop
        # get "stat" response (lt and rt status)
        # if both are stopped the set bothStopped = true
        if priorLtCt == ltCount and priorRtCt == rtCount:
            bothStopped = TRUE
            break
        priorLtCt = ltCount
        priorRtCt = rtCount
        sleep(0.20) # wait for 1/5 second before asking again...

# run our drive pattern
try:
    # wait for runtimeConfig to get our hardware ID from P2 (saying it's alive)
    print_line('- waiting P2 startup', verbose=True)
    while not runtimeConfig.containsKey("hwName"):
        sleep(0.5) # wait for 1/2 second before asking again...

    print_line('- P2 is alive!', verbose=True)

    # -------------------------
    # configure drive system
    # -------------------------
    # override defaults, use 100 %
    wheels.setMaxSpeed(100)
    wheels.setMaxSpeedForDistance(100)
    # and don't draw current at stop
    wheels.holdAtStop(False)

    # -------------------------
    #  drive a square pattern
    #   3-second sides 75% power, 90° corners
    # -------------------------
    # forward for 3 seconds at 75% power
    desiredPower = 75
    lengthOfSideInSeconds = 3
    dirStraightAhead = 0
    wheels.driveDirection(desiredPower, dirStraightAhead)
    wheels.stopAfterTime(lengthOfSideInSeconds, DrvTimeUnits.DTU_SECS)
    waitForMotorsStopped()

    # hard 90° right turn
    #   [circ = 2 * PI * r]
    #   rotate about 1 wheel means effective-platform-radius is actual-platform-diameter!
    #     dist to travel = (effective-platform-circumference / 4) / wheel circumference
    #     effective-platform-radius = 17.5"
    #     wheel diameter = 6.5"
    #     travel dist is 1.346 rotations
    #     rotations * 90 = 121 hall ticks
    dirHardRightTurn = 100
    ticksIn90DegreeTurn = 121
    wheels.driveDirection(desiredPower, dirHardRightTurn)
    wheels.stopAfterRotation(ticksIn90DegreeTurn, DrvRotUnits.DRU_HALL_TICKS)
    waitForMotorsStopped()

    # forward for 2 seconds at 50% power
    wheels.driveDirection(desiredPower, dirStraightAhead)
    wheels.stopAfterTime(lengthOfSideInSeconds, DrvTimeUnits.DTU_SECS)
    waitForMotorsStopped()

    # hard 90° right turn
    wheels.driveDirection(desiredPower, dirHardRightTurn)
    wheels.stopAfterRotation(ticksIn90DegreeTurn, DrvRotUnits.DRU_HALL_TICKS)
    waitForMotorsStopped()

    # forward for 2 seconds at 50% power
    wheels.driveDirection(desiredPower, dirStraightAhead)
    wheels.stopAfterTime(lengthOfSideInSeconds, DrvTimeUnits.DTU_SECS)
    waitForMotorsStopped()

    # hard 90° right turn
    wheels.driveDirection(desiredPower, dirHardRightTurn)
    wheels.stopAfterRotation(ticksIn90DegreeTurn, DrvRotUnits.DRU_HALL_TICKS)
    waitForMotorsStopped()

    # forward for 2 seconds at 50% power
    wheels.driveDirection(desiredPower, dirStraightAhead)
    wheels.stopAfterTime(lengthOfSideInSeconds, DrvTimeUnits.DTU_SECS)
    waitForMotorsStopped()

    # hard 90° right turn
    wheels.driveDirection(desiredPower, dirHardRightTurn)
    wheels.stopAfterRotation(ticksIn90DegreeTurn, DrvRotUnits.DRU_HALL_TICKS)
    waitForMotorsStopped()
    # -------------------------

finally:
    # normal shutdown
    print_line('Done', info=True)

# GENERATED -- edit the .tsv

This view is regenerated from `SIGNOFF-MANIFEST.tsv` by `tools/signoff-collate.py`. Never edit it by hand: the `.tsv` is the single source (design `DOCs/plans/VISIT-SIGNOFF-DESIGN.md` section A.1).

## Row 1 -- task 3499: start() returns cog id 0..7 or -1; a second start() restarts with no orphaned cog

| cell | bin | test | crit | lo | hi | units | min_inst | count_filter | prov | visit_owed | status | status_ref | basis |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| R1-SCAN-COGOK | SCAN | every startSide() | STARTS_COG_BAD | 0 | 0 | COUNT | 2 | - | D | 1 | OWED | - | the contract is start()'s @returns (cog id 0..7, or -1); a start counts bad when its return is outside 0..7 OR does not equal testGetMotorCog()-1, so PL-22's pre-3499 always-0 return FAILs [M: debug_260911-143911.log T0-10 start_return 0, raw_motor_cog 2] (arbiter review 2026-09-14) |
| R1-T0-START | T0 | T0-15a start() on P16 | RET_EQ_COG_M1 | TRUE | TRUE | BOOL | 1 | - | D | 1 | OWED | - | as built BOOL (arbiter review 2026-09-14): TRUE when start()'s return is in 0..7 AND equals testGetMotorCog()-1; start() returns motorCog-1 and testGetMotorCog() returns motorCog (isp_bldc_motor.spin2:115-116, :1208; design A.4 row 1); the pre-3499 start() always returned 0 [M: debug_260911-143911.log T0-10 start_return 0, raw_motor_cog 2], in 0..7 but not raw_motor_cog-1, so it prints FALSE and FAILs |
| R1-T0-EXHAUST | T0 | T0-15b cog exhaustion, runs last | RET_NEG_NOLEAK | TRUE | TRUE | BOOL | 1 | - | D | 1 | OWED | - | as built BOOL (arbiter review 2026-09-14): TRUE when start() under total cog exhaustion returns -1 AND testGetMotorCog()==0 AND free cogs after release == baseline (isp_bldc_motor.spin2:110-113; design A.5-a); the pre-3499 start() returned 0 with every cog occupied [M: debug_260911-143911.log T0-8 cogs_occupied 7, start_return 0], so it prints FALSE and FAILs |
| R1-T0-RESTART | T0 | T0-15c start() twice with no stop() | NO_ORPHAN | TRUE | TRUE | BOOL | 1 | - | D | 1 | OWED | - | as built BOOL (arbiter review 2026-09-14): TRUE when abs(free2-free1) + abs(free3-baseline) == 0 AND free1 == baseline-1 (PL-24 fix isp_bldc_motor.spin2:103-104; design A.4 row 1, A.5-a); before the PL-24 fix a second start() with no stop() orphaned the first driver cog, so free2 = free1-1 and the sum is at least 1 [D], which prints FALSE and FAILs |

## Row 2 -- task 3500, 3537: board detection: Rev B read reliably at every start and after a driver stop; an empty group is not detected

| cell | bin | test | crit | lo | hi | units | min_inst | count_filter | prov | visit_owed | status | status_ref | basis |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| R2-SCAN-REVB | SCAN | every start | STARTS_NOT_REVB | 0 | 0 | COUNT | 2 | - | M | 1 | OWED | - | Rev B at all eight starts in scan run 5 (SCAN-RUN-5-EVALUATION.md section 1) |
| R2-T0-REPEAT | T0 | T0-14a 32 reads per populated base, P16 (RIGHT) and P32 (LEFT) | READS_NOT_REVB | 0 | 0 | COUNT | 2 | - | D | 1 | OWED | - | N = 32 reads per base from test_bench_detect.spin2:142-146; a 1-in-10 flip mode is missed with probability 0.9^32 = 3.4 percent |
| R2-T0-DIRTY | T0 | T0-14b dirtied ADC-mode sense pin, per populated base | POSTSTOP_REVB | TRUE | TRUE | BOOL | 2 | - | M | 1 | OWED | - | before the fix a Rev B board read Rev A after its own cog stopped, 4 of 4 (CHAR-RUN-EVALUATION.md section 3), so this cell can FAIL on the defect |
| R2-T0-EMPTY | T0 | T0-14c testSetup(PINS_P0_P15) | EMPTY_NODET | TRUE | TRUE | BOOL | 1 | - | M | 1 | OWED | - | empty group P0_P15 read sum 500 and was not detected (2026-09-11/debug_260911-210229.log:81-125) |
| R2-HOST-DETDIFF | HOST | detect-phase2 log diffed against the 2026-09-11 baseline over BD-CELL (sw, grp), BD-ENUM (grp) and BD-PLAN (sw) with the 3505 prediction list (design C.2; as built 3537 P2d, tools/signoff-collate.py detdiff_log); inputs: file:DOCs/analyses/bench/SIGNOFF-DETECT-PREDICTIONS.tsv file:DOCs/analyses/bench/2026-09-11/debug_260911-210229.log src:src/test_bench_detect.spin2:phase2_compiled | ONLY_PREDICTED | 0 | 0 | COUNT | 1 | - | D/M | 1 | OWED | - | as built (3537 P2d): measured = unpredicted changes + predicted changes that did not occur; BD-CELL modal/libvrd/agree/va/vb/vn exact, sum_min/sum_max/sum_mean exact when the baseline is 0 or 500 and otherwise +-11 from the measured Rev B band 93-104 (isp_bldc_motor.spin2:851-853) [D]; BD-ENUM local/lib/match and BD-PLAN exact; sweeps 3 and 6 excluded as void by design, BD-CFG and BD-MAP INFO only, BD-LIB brackets and timing records never compared; a cell the visit log marks BD-SKIPPED is NOT_COMPARED and listed; PASS needs measured 0, no COMPARED predicted cell skipped, no skip the declared bases do not imply, and a compared post-stop cell on each of P0_P15 and P16_P31, else NOMEAS; VOID (no banner, BD-CLK match 0, BD-ENUM match 0, cfg_id not BENCH, build-variant mismatch) is NOMEAS; baseline 2026-09-11/debug_260911-210229.log [M]; predictions DOCs/analyses/bench/SIGNOFF-DETECT-PREDICTIONS.tsv (3505's list: 64 lines, 14 COMPARED); unfixed: the baseline itself carries the pre-3500 values, so run against itself all 56 non-void predicted changes do not occur and it FAILs (--selftest check o); design C.2 |
| R2-CHAR-ISCALE | CHAR | each motion hold (8) | RSENSE_IMPLIED | 135 | 165 | COUNT | 8 | - | D | 1 | OWED | - | getCurrent() = sense_i_mV x 10000 / rSenseForBoard (isp_bldc_motor.spin2:749); Rev B 150, a Rev A misdetect 5 (:1597-1598); +-10 percent of 150 absorbs non-atomic sampling of two means, and a 30x error cannot pass |
| R2-DETECT-GUARD | HOST | detect-phase2 log shows the gate-input guard held (design C.3 item 5; as built 3537 P2d, tools/signoff-collate.py detect_guard_log): the skip set is computed from the log's BD-CFG left_base/right_base and BD-PLAN, never from the binary's own claim; inputs: src:src/test_bench_detect.spin2:GATE_OVERLAP | GUARD_SKIPS_OK | TRUE | TRUE | BOOL | 1 | - | D | 1 | OWED | - | as built (3537 P2d): TRUE when no BD-REP or BD-CELL exists for a cell the guard must skip (GATE_OVERLAP: the group's sense pin base+4 lies on a declared board's pin other than that board's own base+4; COG_OVERLAP: a phase-2 driver-cog group sharing a pin with a board based elsewhere), each such cell has one BD-SKIPPED record with that reason and no other cell does, BD-MAP guard reads GATE_OVERLAP on exactly the gate-overlap groups, and every BD-SWEEP end count (cells, skipped, reps) equals the BD-PLAN less the skipped cells and the records the log carries [D]; NOMEAS when the declared bases imply no skip; on the bench bases LEFT 32 RIGHT 16 the skip set is NO_USE_P24_P39 (P28 = RIGHT pin_pwm_w_l) and P40_P55 (P44 = LEFT pin_pwm_w_l) in sweeps 1, 2, 4, 5, 7 and 8; unfixed: the SRC_REV 2 binary emits BD-REP for P40_P55 and NO_USE_P24_P39 and no BD-MAP guard field, so FALSE -> FAIL (--selftest check r); design C.3 item 5 |
| R2-DETECT-OVERLAP | HOST | overlapping-group cells P40_P55 and NO_USE_P24_P39, run only in a session with the motors unplugged (design J.2 ruling) | OVERLAP_NOT_REVB | 0 | 0 | COUNT | 1 | - | D | DEFERRED | OWED | - | the 3500 check that a group whose sense pin lands on a board gate input is not reported as Rev B; deferred to the first session with the motors unplugged for another reason, never re-asked (design J.2) |

## Row 3 -- task 3501: hall integrity counters

| cell | bin | test | crit | lo | hi | units | min_inst | count_filter | prov | visit_owed | status | status_ref | basis |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| R3-SCAN-INTEG | SCAN | all starts and every integrity-valid point | MISSED_ILLEGAL_SUM | 0 | 0 | COUNT | 2 | - | M | 1 | OWED | - | COVERAGE, not a falsifier: it cannot see counters that never count; missed 0 and illegal 0 at every start and every point of scan run 5 (evaluation section 1) [M]; at <= 212 ticks/s against a 43.9 kHz loop no transition can be skipped (isp_bldc_motor.spin2:2363) [D] |
| R3-CHAR-INTEG | CHAR | every hold, summed per motor | MISSED_ILLEGAL_SUM | 0 | 0 | COUNT | 2 | - | M | 1 | OWED | - | same basis as R3-SCAN-INTEG; COVERAGE, not a falsifier |
| R3-T0-STOPPED | T0 | T0-13 start at zero command, hold 1000 ms | STOPPED_COUNTS | 0 | 0 | COUNT | 1 | - | D | 1 | OWED | - | COVERAGE, not a falsifier (it cannot see counters that never count); stationary halls never transition; the 1000 ms hold equals the scan zero window (ZERO_SAMPLES x SAMPLE_MS), long enough to span the start transient that 3524 fixed |

## Row 4 -- task 3502: rpm and mm/tick precision

| cell | bin | test | crit | lo | hi | units | min_inst | count_filter | prov | visit_owed | status | status_ref | basis |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| R4-T0-1M-TICKS | T0 | T0-3 stopAfterDistance() tick targets | DDU_M_TICKS | TRUE | TRUE | BOOL | 1 | - | D | 1 | OWED | - | as built BOOL (arbiter review 2026-09-14): TRUE when the DDU_M tick target is in 173..174 AND the DDU_M, DDU_CM and DDU_MM targets agree; 1000 mm x 90 / 518.6 mm = 173.5, truncated or rounded (design A.5-b); the pre-fix 175 [M debug_260911-143911.log] and finding F's 17 are both outside 173..174, so each prints FALSE and FAILs |
| R4-CHAR-RPM | CHAR | each motion hold (8) | RPM_ERR | -2 | 2 | RPM | 8 | - | D | 1 | OWED | - | library rpm truncation <= 1 rpm plus about 1 tick/s of window mismatch = 0.67 rpm, 1.67 rounded up to 2 (design A.5-c) |

## Row 5 -- task 3503: S-3 ADC scale restore

| cell | bin | test | crit | lo | hi | units | min_inst | count_filter | prov | visit_owed | status | status_ref | basis |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| R5-SCAN-SELF | SCAN | self-check | NET_I_IN_BAND | TRUE | TRUE | BOOL | 2 | - | M | 1 | OWED | - | existing net bands 59-105 / 118-203 mV (test_bench_scan.spin2:313-316); BS-CHECKSUM pos_i_ok and neg_i_ok |
| R5-CHAR-SENSE | CHAR | each motion hold (8) | NET_VS_PASS1_PCT | -150 | 150 | PCT_X10 | 8 | - | D | 1 | OWED | - | 1.5 x the largest run-5 deviation at a matching hold (+10.2 percent) = 15.3, taken as +-15.0 percent against 150.1 mV/A x the Pass 1 meter amps (design A.5-d, D from M) |

## Row 6 -- task 3519: independent offset setter

| cell | bin | test | crit | lo | hi | units | min_inst | count_filter | prov | visit_owed | status | status_ref | basis |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| R6-SCAN-OFFSETS | SCAN | every start and every applyOffsets | READBACK_BAD | 0 | 0 | COUNT | 2 | - | M | 1 | OWED | - | offsets read back exactly at every start of scan run 5 (section 1) [M]; read-back is integer degrees, so exact [D] |

## Row 7 -- task 3524: hall inputs not driven at start

| cell | bin | test | crit | lo | hi | units | min_inst | count_filter | prov | visit_owed | status | status_ref | basis |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| R7-SCAN-STARTILL | SCAN | every start | STARTS_ILLEGAL | 0 | 0 | COUNT | 2 | - | M | 1 | OWED | - | illegal 0 at every start since the fix (plan 2026-09-13 table) [M]; before the fix the first hall read went illegal (isp_bldc_motor.spin2:2945-2946) [D] |

## Row 8 -- task 3529: ADC calibration from a settled average

| cell | bin | test | crit | lo | hi | units | min_inst | count_filter | prov | visit_owed | status | status_ref | basis |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| R8-SCAN-ZXS | SCAN | 5 deliberate starts per motor, each with a zero (PH_XSTART) | ZXS | 0 | 50 | MV_X10 | 5 | LEFT:ZXS_I,LEFT:ZXS_V,RIGHT:ZXS_I,RIGHT:ZXS_V,RIGHT:ZXS_U | D | 1 | OWED | - | threshold 5.0 mV = 2 x the predicted fixed spread of 2.5 mV; unfixed spreads were 62.8 mV on RIGHT i and 84.6 mV on RIGHT u [M PL-32 table]; only the falsifiable channel instances count toward min_inst (design A.5-e) |
| R8-T0-ZXS | T0 | T0-11 five start/stop lifetimes on P16 (RIGHT) | ZXS | 0 | 50 | MV_X10 | 3 | RIGHT:ZXS_I,RIGHT:ZXS_U,RIGHT:ZXS_V | D | 1 | OWED | - | same basis as R8-SCAN-ZXS; counts RIGHT i, u and v only (design A.5-e) |

## Row 9 -- task 3530: scan v4 logic ran

| cell | bin | test | crit | lo | hi | units | min_inst | count_filter | prov | visit_owed | status | status_ref | basis |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| R9-SCAN-HALFLEG | SCAN | each half-speed leg with a probeable confirm fault | CLIFF_PROBED | TRUE | TRUE | BOOL | 2 | - | M | 1 | OWED | - | TRUE when every half-speed confirm fault leaving a gap wider than CLIFF_HALF_STEP_DEG to the leg's last good point is followed by a measured probe point (v4 CHANGE 4); NOMEAS when a leg had no such fault; unfixed, run 5's LEFT half legs faulted at 4 and -11 deg with last good 14 and -21 and nothing measured between, so both FAIL [M evaluation section 3]; min_inst 2 = the two such legs run 5 produced [M]; the first criterion FIT_OR_CLIFF passed on that defect because computeLegCliff finds a good/fault pair without a probe (arbiter review 2026-09-14) |
| R9-SCAN-OWNZERO | SCAN | each fitted leg | PTS_NO_OWN_ZERO | 0 | 0 | COUNT | 4 | - | D | 1 | OWED | - | COVERAGE, not a falsifier: the v4 CHANGE 2 invariant is that every point that feeds a fit carries its own lifetime zero (bPtZeroValid), but scan v3 already re-measured a zero before every point, so the unfixed code counts 0 too; run 5's ratio 0.440 vs 1.16 came from BS-PAIR2 netting both minima against ZERO_INIT [M evaluation section 6 item 1] (arbiter review 2026-09-14) |
| R9-SCAN-PAIR2 | SCAN | each motor's BS-PAIR2 | NET_RATIO_ONLY | TRUE | TRUE | BOOL | 2 | - | D | 1 | OWED | - | COVERAGE, not a falsifier: it proves the fmt 6 net-ratio path ran (both quarter-speed minima exist and emitPair2's net ratio was valid), not that the ratio is right; an incomplete pair is NOMEAS |

## Row 10 -- task 3533: PL-28, PL-22 and PL-9

| cell | bin | test | crit | lo | hi | units | min_inst | count_filter | prov | visit_owed | status | status_ref | basis |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| R10-SCAN-RSTALONE | SCAN | first natural fault per motor (J.1 ruled b): testResetFault() before any zero command | RESET_ALONE_CLEARS | TRUE | TRUE | BOOL | 1 | - | D | 1 | OWED | - | as built BOOL (arbiter review 2026-09-14): TRUE when the wheel is stopped and not faulted after testResetFault() alone with the faulted non-zero command still set; ms in BS-RSTALONE; unfixed (pre-67d11f6) testResetFault waited 2030 ms and stayed FAULTED (isp_bldc_motor.spin2 testResetFault), so FALSE -> FAIL; NOMEAS when a motor has no eligible fault |
| R10-T0-STOPREADY | T0 | T0-15d right after T0-15c's stop() | STOP_NOT_READY | TRUE | TRUE | BOOL | 1 | - | D | 1 | OWED | - | PL-28 item 2: after stop() isReady() and isStopped() must both be FALSE; before the fix drv_state stayed stale (isp_bldc_motor.spin2:916, :123-125) |
| R10-CHAR-STEERSTART | CHAR | steering phase, normal start | STEER_START_COG | TRUE | TRUE | BOOL | 1 | - | D | 1 | OWED | - | as built (design A.4 has COGID 0..7): TRUE when steering start() returns 0..7 AND both wheels leave DCS_Unknown AND nothing aborted (isp_steering_2wheel.spin2:170; test_bench_char.spin2 emitPhaseDSignoffs) |
| R10-CHAR-STEERLIVE | CHAR | steering phase, driveAtPower(13, 13) for 700 ms | WHEEL_TICKS | 6 | NA | TICKS | 2 | - | D | 1 | OWED | - | half of the 13-tick response to an 18_375_000 nudge held 700 ms [M debug_260913-120844.log:46]; PL-22 parked cogs move 0 (design A.5-f) |
| R10-CHAR-STEERFAIL | CHAR | steering phase with exactly one free cog | RET_NEG_NOLEAK | TRUE | TRUE | BOOL | 1 | - | D | 1 | OWED | - | as built (design A.4 has COGID -1..-1): TRUE when start() returns -1 AND free cogs after == baseline AND both bench bases can be claimed again (PL-36) AND nothing aborted (isp_steering_2wheel.spin2:124-133) |
| R10-HOST-PL9 | HOST | static source check of src/isp_bldc_motor.spin2; inputs: flag:--static-tree | GAPINMS_ABSENT | 0 | 0 | COUNT | 1 | - | D | 1 | OWED | - | the PL-9 rename is compile-only, so no run-time behaviour exists to test; this cell proves the identifier gapInMS is gone from src/isp_bldc_motor.spin2 (dispatch: removed by commit 67d11f6); a synthetic source containing it FAILs in --selftest |

## Row 11 -- task 3534: scan watchdog

| cell | bin | test | crit | lo | hi | units | min_inst | count_filter | prov | visit_owed | status | status_ref | basis |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| R11-SCAN-NOSTALL | SCAN | end of a normal run (cog 0 PASS, or watchdog FAIL) | ENDED_BY_COG0 | TRUE | TRUE | BOOL | 1 | - | M | 1 | OWED | - | run 5 stopped emitting without ending (evaluation section 7) [M]; the owner's report in the same section [S] |
| R11-WDT-FIRES | SCANWD | watchdog cog, -D WD_SELFTEST build | STALL_MS | 4000 | 4500 | MS | 1 | - | D | 1 | OWED | - | a stall is declared at >= WD_STALL_MS 4000 by construction; hi = WD_STALL_MS + 2 x WD_POLL_MS = 4500 (design G.4); unfixed (no working watchdog) nothing declares, so cog 0's backstop prints the elapsed stall, >= WD_SELFTEST_BACKSTOP_MS 12000, outside 4000..4500 -> FAIL (as built, arbiter review 2026-09-14) |
| R11-WDT-CKPT | SCANWD | watchdog cog, -D WD_SELFTEST build | CKPT_IS_SELFTEST | TRUE | TRUE | BOOL | 1 | - | D | 1 | OWED | - | COVERAGE, not a falsifier: the stall is placed at CP_SELFTEST, and any other declared checkpoint prints FALSE because the heartbeat contract misattributes (design G.4), but no pre-fix binary exists that printed a wrong one; on the backstop path it is NOMEAS (arbiter review 2026-09-14) |
| R11-WDT-STOPPED | SCANWD | watchdog cog, -D WD_SELFTEST build | WHEELS_STOPPED | TRUE | TRUE | BOOL | 1 | - | D | 1 | OWED | - | COVERAGE, not a falsifier: at least one driver cog running before the stall (snapshot taken before the stops) and both testGetMotorCog()==0 after the watchdog's stop()s (design G.4); it proves the stop path runs, and no unfixed variant of it exists; on the backstop path it is NOMEAS (arbiter review 2026-09-14) |
| R11-WDT-STACK | SCANWD | watchdog cog, -D WD_SELFTEST build | STACK_OK | TRUE | TRUE | BOOL | 1 | - | D | 1 | OWED | - | COVERAGE, not a falsifier: WD_STACK_SENTINEL intact after the deepest watchdog chain has run (43 longs counted against WD_STACK_LONGS 128, test_bench_scan.spin2 watchdog CON block; design G.4); read last in declareStall(); on the backstop path it is NOMEAS (arbiter review 2026-09-14) |
| R11-HOST-WDTEND | HOST | SCANWD log: BS-BUILD wd_selftest TRUE, the four R11-WDT-* records from a non-zero cog before DEBUG_END_SESSION, log COMPLETE (design G.4); inputs: src:src/test_bench_scan.spin2:wd_selftest | FLAG_AND_END | TRUE | TRUE | BOOL | 1 | - | D | 1 | OWED | - | pnut-ts ignores an unknown -D (bench-run.sh:98-104), so the flag must be proven in the log, and the end marker must follow the watchdog's verdicts |

## Row 12 -- task 3535: driver start code in the cog LUT

| cell | bin | test | crit | lo | hi | units | min_inst | count_filter | prov | visit_owed | status | status_ref | basis |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| R12-SCAN-ALIVE | SCAN | every start | STARTS_NOT_ALIVE | 0 | 0 | COUNT | 2 | - | D | 1 | OWED | - | drv_state leaves DCS_Unknown within READY_TIMEOUT_MS 2000 and the lifetime's first zero is not frozen, i min <> max over 200 samples (design A.5-g, D from M) |
| R12-SCAN-RATE | SCAN | self-check | RATE_IN_BAND | TRUE | TRUE | BOOL | 2 | - | M | 1 | OWED | - | run 5 self-check rates 98.1/98.2 ticks/s in band 90-106 (evaluation section 1; test_bench_scan.spin2:283-284) |

## Row 13 -- task 3535: brake-mode start path runs cleanly (prior_angle initialised at driver start, commit b34e109)

| cell | bin | test | crit | lo | hi | units | min_inst | count_filter | prov | visit_owed | status | status_ref | basis |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| R13-CHAR-BRAKESTART | CHAR | brake-start phase, each motor x sign (4) | BRAKE_START_MOVE | TRUE | TRUE | BOOL | 4 | - | D | 1 | OWED | - | as built (design A.4 has TICKS 6..NA): TRUE when the fault state was read from a running driver AND no fault AND sign x tick delta >= 6; start-path coverage that cannot fail on the prior_angle defect (design A.5-h, corrected 2026-09-14) |

# Visit 1 sign-off sheet -- NEGCASE

- Script: `tools/signoff-collate.py`
- Manifest: `DOCs/analyses/bench/SIGNOFF-MANIFEST.tsv` -- statuses updated by this run (--update)
- Design: `DOCs/plans/VISIT-SIGNOFF-DESIGN.md`
- Flags: --static-tree no; --update yes
- Detect prediction list: `DOCs/analyses/bench/SIGNOFF-DETECT-PREDICTIONS.tsv` (absent); detect baseline: `DOCs/analyses/bench/2026-09-11/debug_260911-210229.log` (present)
- Rules: a verdict exists only where a binary printed one; a cell reaches PASS only by positive evidence; a declared cell without a verdict is NOMEAS (design section 0)

## Input logs

1. `DOCs/analyses/bench/2026-09-13/debug_260913-120844.log` -- **TRUNCATED** -- TRUNCATED (no DEBUG_END_SESSION line)
   - identity: BS-BANNER src_rev 4 fmt 4 (line 19); download test_bench_scan.bin, 39364 bytes, modified 2026-09-13T18:08:43.213Z (line 14)
   - build key: banner BS-BANNER, src_rev 4, fmt 4, bin test_bench_scan.bin, size 39364 (modified time recorded, not keyed)
   - records: 0 SIGNOFF-DECL, 0 SIGNOFF, 0 malformed

## Rows

| row | task | feature | verdict |
|---|---|---|---|
| 1 | 3499 | start() returns cog id 0..7 or -1; a second start() restarts with no orphaned cog | **NOT_BUILT** |
| 2 | 3500, 3537 | board detection: Rev B read reliably at every start and after a driver stop; an empty group is not detected | **NOT_BUILT** |
| 3 | 3501 | hall integrity counters | **NOT_BUILT** |
| 4 | 3502 | rpm and mm/tick precision | **NOT_BUILT** |
| 5 | 3503 | S-3 ADC scale restore | **NOT_BUILT** |
| 6 | 3519 | independent offset setter | **NOT_BUILT** |
| 7 | 3524 | hall inputs not driven at start | **NOT_BUILT** |
| 8 | 3529 | ADC calibration from a settled average | **NOT_BUILT** |
| 9 | 3530 | scan v4 logic ran | **NOT_BUILT** |
| 10 | 3533 | PL-28, PL-22 and PL-9 | **NOT_BUILT** |
| 11 | 3534 | scan watchdog | **NOT_BUILT** |
| 12 | 3535 | driver start code in the cog LUT | **NOT_BUILT** |
| 13 | 3535 | brake-mode start path runs cleanly (prior_angle initialised at driver start, commit b34e109) | **NOT_BUILT** |

## Cells

- **R1-SCAN-COGOK** (row 1, bin SCAN) -- **NOT_BUILT** (NO_DECLARING_LOG) -- crit STARTS_COG_BAD, lo 0, hi 0, units COUNT, min_inst 2; manifest status OWED
  - no input log declares this cell (SIGNOFF-DECL) or prints a verdict for it
- **R1-T0-START** (row 1, bin T0) -- **NOT_BUILT** (NO_DECLARING_LOG) -- crit RET_EQ_COG_M1, lo 0, hi 7, units COGID, min_inst 1; manifest status OWED
  - no input log declares this cell (SIGNOFF-DECL) or prints a verdict for it
- **R1-T0-EXHAUST** (row 1, bin T0) -- **NOT_BUILT** (NO_DECLARING_LOG) -- crit RET_NEG_NOLEAK, lo -1, hi -1, units COGID, min_inst 1; manifest status OWED
  - no input log declares this cell (SIGNOFF-DECL) or prints a verdict for it
- **R1-T0-RESTART** (row 1, bin T0) -- **NOT_BUILT** (NO_DECLARING_LOG) -- crit NO_ORPHAN, lo 0, hi 0, units COUNT, min_inst 1; manifest status OWED
  - no input log declares this cell (SIGNOFF-DECL) or prints a verdict for it
- **R2-SCAN-REVB** (row 2, bin SCAN) -- **NOT_BUILT** (NO_DECLARING_LOG) -- crit STARTS_NOT_REVB, lo 0, hi 0, units COUNT, min_inst 2; manifest status OWED
  - no input log declares this cell (SIGNOFF-DECL) or prints a verdict for it
- **R2-T0-REPEAT** (row 2, bin T0) -- **NOT_BUILT** (NO_DECLARING_LOG) -- crit READS_NOT_REVB, lo 0, hi 0, units COUNT, min_inst 2; manifest status OWED
  - no input log declares this cell (SIGNOFF-DECL) or prints a verdict for it
- **R2-T0-DIRTY** (row 2, bin T0) -- **NOT_BUILT** (NO_DECLARING_LOG) -- crit POSTSTOP_REVB, lo TRUE, hi TRUE, units BOOL, min_inst 2; manifest status OWED
  - no input log declares this cell (SIGNOFF-DECL) or prints a verdict for it
- **R2-T0-EMPTY** (row 2, bin T0) -- **NOT_BUILT** (NO_DECLARING_LOG) -- crit EMPTY_NODET, lo TRUE, hi TRUE, units BOOL, min_inst 1; manifest status OWED
  - no input log declares this cell (SIGNOFF-DECL) or prints a verdict for it
- **R2-HOST-DETDIFF** (row 2, bin HOST) -- **NOT_BUILT** (INPUT_ABSENT) -- crit ONLY_PREDICTED, lo 0, hi 0, units COUNT, min_inst 1; manifest status OWED
  - no detect-phase2 log among the inputs (BD-BANNER tool test_bench_detect, BD-BUILD phase2_compiled 1, BD-CFG cfg_id BENCH)
  - prediction list absent: DOCs/analyses/bench/SIGNOFF-DETECT-PREDICTIONS.tsv
- **R2-CHAR-ISCALE** (row 2, bin CHAR) -- **NOT_BUILT** (NO_DECLARING_LOG) -- crit RSENSE_IMPLIED, lo 135, hi 165, units COUNT, min_inst 8; manifest status OWED
  - no input log declares this cell (SIGNOFF-DECL) or prints a verdict for it
- **R2-DETECT-GUARD** (row 2, bin HOST) -- **NOT_BUILT** (INPUT_ABSENT) -- crit GUARD_SKIPS_OK, lo TRUE, hi TRUE, units BOOL, min_inst 1; manifest status OWED
  - no detect-phase2 log among the inputs (BD-BANNER tool test_bench_detect, BD-BUILD phase2_compiled 1, BD-CFG cfg_id BENCH)
  - prediction list absent: DOCs/analyses/bench/SIGNOFF-DETECT-PREDICTIONS.tsv
- **R3-SCAN-INTEG** (row 3, bin SCAN) -- **NOT_BUILT** (NO_DECLARING_LOG) -- crit MISSED_ILLEGAL_SUM, lo 0, hi 0, units COUNT, min_inst 2; manifest status OWED
  - no input log declares this cell (SIGNOFF-DECL) or prints a verdict for it
- **R3-CHAR-INTEG** (row 3, bin CHAR) -- **NOT_BUILT** (NO_DECLARING_LOG) -- crit MISSED_ILLEGAL_SUM, lo 0, hi 0, units COUNT, min_inst 2; manifest status OWED
  - no input log declares this cell (SIGNOFF-DECL) or prints a verdict for it
- **R3-T0-STOPPED** (row 3, bin T0) -- **NOT_BUILT** (NO_DECLARING_LOG) -- crit STOPPED_COUNTS, lo 0, hi 0, units COUNT, min_inst 1; manifest status OWED
  - no input log declares this cell (SIGNOFF-DECL) or prints a verdict for it
- **R4-T0-1M-TICKS** (row 4, bin T0) -- **NOT_BUILT** (NO_DECLARING_LOG) -- crit DDU_M_TICKS, lo 173, hi 174, units TICKS, min_inst 1; manifest status OWED
  - no input log declares this cell (SIGNOFF-DECL) or prints a verdict for it
- **R4-CHAR-RPM** (row 4, bin CHAR) -- **NOT_BUILT** (NO_DECLARING_LOG) -- crit RPM_ERR, lo -2, hi 2, units RPM, min_inst 8; manifest status OWED
  - no input log declares this cell (SIGNOFF-DECL) or prints a verdict for it
- **R5-SCAN-SELF** (row 5, bin SCAN) -- **NOT_BUILT** (NO_DECLARING_LOG) -- crit NET_I_IN_BAND, lo TRUE, hi TRUE, units BOOL, min_inst 2; manifest status OWED
  - no input log declares this cell (SIGNOFF-DECL) or prints a verdict for it
- **R5-CHAR-SENSE** (row 5, bin CHAR) -- **NOT_BUILT** (NO_DECLARING_LOG) -- crit NET_VS_PASS1_PCT, lo -150, hi 150, units PCT_X10, min_inst 8; manifest status OWED
  - no input log declares this cell (SIGNOFF-DECL) or prints a verdict for it
- **R6-SCAN-OFFSETS** (row 6, bin SCAN) -- **NOT_BUILT** (NO_DECLARING_LOG) -- crit READBACK_BAD, lo 0, hi 0, units COUNT, min_inst 2; manifest status OWED
  - no input log declares this cell (SIGNOFF-DECL) or prints a verdict for it
- **R7-SCAN-STARTILL** (row 7, bin SCAN) -- **NOT_BUILT** (NO_DECLARING_LOG) -- crit STARTS_ILLEGAL, lo 0, hi 0, units COUNT, min_inst 2; manifest status OWED
  - no input log declares this cell (SIGNOFF-DECL) or prints a verdict for it
- **R8-SCAN-ZXS** (row 8, bin SCAN) -- **NOT_BUILT** (NO_DECLARING_LOG) -- crit ZXS, lo 0, hi 50, units MV_X10, min_inst 5, counts only LEFT:ZXS_I,LEFT:ZXS_V,RIGHT:ZXS_I,RIGHT:ZXS_V,RIGHT:ZXS_U; manifest status OWED
  - no input log declares this cell (SIGNOFF-DECL) or prints a verdict for it
- **R8-T0-ZXS** (row 8, bin T0) -- **NOT_BUILT** (NO_DECLARING_LOG) -- crit ZXS, lo 0, hi 50, units MV_X10, min_inst 3, counts only RIGHT:ZXS_I,RIGHT:ZXS_U,RIGHT:ZXS_V; manifest status OWED
  - no input log declares this cell (SIGNOFF-DECL) or prints a verdict for it
- **R9-SCAN-HALFLEG** (row 9, bin SCAN) -- **NOT_BUILT** (NO_DECLARING_LOG) -- crit FIT_OR_CLIFF, lo TRUE, hi TRUE, units BOOL, min_inst 4; manifest status OWED
  - no input log declares this cell (SIGNOFF-DECL) or prints a verdict for it
- **R9-SCAN-OWNZERO** (row 9, bin SCAN) -- **NOT_BUILT** (NO_DECLARING_LOG) -- crit PTS_NO_OWN_ZERO, lo 0, hi 0, units COUNT, min_inst 4; manifest status OWED
  - no input log declares this cell (SIGNOFF-DECL) or prints a verdict for it
- **R9-SCAN-PAIR2** (row 9, bin SCAN) -- **NOT_BUILT** (NO_DECLARING_LOG) -- crit NET_RATIO_ONLY, lo TRUE, hi TRUE, units BOOL, min_inst 2; manifest status OWED
  - no input log declares this cell (SIGNOFF-DECL) or prints a verdict for it
- **R10-SCAN-RSTALONE** (row 10, bin SCAN) -- **NOT_BUILT** (NO_DECLARING_LOG) -- crit RESET_ALONE_CLEARS, lo 0, hi 2030, units MS, min_inst 1; manifest status OWED
  - no input log declares this cell (SIGNOFF-DECL) or prints a verdict for it
- **R10-T0-STOPREADY** (row 10, bin T0) -- **NOT_BUILT** (NO_DECLARING_LOG) -- crit STOP_NOT_READY, lo TRUE, hi TRUE, units BOOL, min_inst 1; manifest status OWED
  - no input log declares this cell (SIGNOFF-DECL) or prints a verdict for it
- **R10-CHAR-STEERSTART** (row 10, bin CHAR) -- **NOT_BUILT** (NO_DECLARING_LOG) -- crit STEER_START_COG, lo TRUE, hi TRUE, units BOOL, min_inst 1; manifest status OWED
  - no input log declares this cell (SIGNOFF-DECL) or prints a verdict for it
- **R10-CHAR-STEERLIVE** (row 10, bin CHAR) -- **NOT_BUILT** (NO_DECLARING_LOG) -- crit WHEEL_TICKS, lo 6, hi NA, units TICKS, min_inst 2; manifest status OWED
  - no input log declares this cell (SIGNOFF-DECL) or prints a verdict for it
- **R10-CHAR-STEERFAIL** (row 10, bin CHAR) -- **NOT_BUILT** (NO_DECLARING_LOG) -- crit RET_NEG_NOLEAK, lo TRUE, hi TRUE, units BOOL, min_inst 1; manifest status OWED
  - no input log declares this cell (SIGNOFF-DECL) or prints a verdict for it
- **R10-HOST-PL9** (row 10, bin HOST) -- **NOT_BUILT** (STATIC_NOT_REQUESTED) -- crit GAPINMS_ABSENT, lo 0, hi 0, units COUNT, min_inst 1; manifest status OWED
  - run with --static-tree to evaluate this static source cell
- **R11-SCAN-NOSTALL** (row 11, bin SCAN) -- **NOT_BUILT** (NO_DECLARING_LOG) -- crit ENDED_BY_COG0, lo TRUE, hi TRUE, units BOOL, min_inst 1; manifest status OWED
  - no input log declares this cell (SIGNOFF-DECL) or prints a verdict for it
- **R11-WDT-FIRES** (row 11, bin SCANWD) -- **NOT_BUILT** (NO_DECLARING_LOG) -- crit STALL_MS, lo 4000, hi 4500, units MS, min_inst 1; manifest status OWED
  - no input log declares this cell (SIGNOFF-DECL) or prints a verdict for it
- **R11-WDT-CKPT** (row 11, bin SCANWD) -- **NOT_BUILT** (NO_DECLARING_LOG) -- crit CKPT_IS_SELFTEST, lo TRUE, hi TRUE, units BOOL, min_inst 1; manifest status OWED
  - no input log declares this cell (SIGNOFF-DECL) or prints a verdict for it
- **R11-WDT-STOPPED** (row 11, bin SCANWD) -- **NOT_BUILT** (NO_DECLARING_LOG) -- crit WHEELS_STOPPED, lo TRUE, hi TRUE, units BOOL, min_inst 1; manifest status OWED
  - no input log declares this cell (SIGNOFF-DECL) or prints a verdict for it
- **R11-WDT-STACK** (row 11, bin SCANWD) -- **NOT_BUILT** (NO_DECLARING_LOG) -- crit STACK_OK, lo TRUE, hi TRUE, units BOOL, min_inst 1; manifest status OWED
  - no input log declares this cell (SIGNOFF-DECL) or prints a verdict for it
- **R11-HOST-WDTEND** (row 11, bin HOST) -- **NOT_BUILT** (NO_WD_SELFTEST_LOG) -- crit FLAG_AND_END, lo TRUE, hi TRUE, units BOOL, min_inst 1; manifest status OWED
  - no input log carries BS-BUILD wd_selftest,TRUE
- **R12-SCAN-ALIVE** (row 12, bin SCAN) -- **NOT_BUILT** (NO_DECLARING_LOG) -- crit STARTS_NOT_ALIVE, lo 0, hi 0, units COUNT, min_inst 2; manifest status OWED
  - no input log declares this cell (SIGNOFF-DECL) or prints a verdict for it
- **R12-SCAN-RATE** (row 12, bin SCAN) -- **NOT_BUILT** (NO_DECLARING_LOG) -- crit RATE_IN_BAND, lo TRUE, hi TRUE, units BOOL, min_inst 2; manifest status OWED
  - no input log declares this cell (SIGNOFF-DECL) or prints a verdict for it
- **R13-CHAR-BRAKESTART** (row 13, bin CHAR) -- **NOT_BUILT** (NO_DECLARING_LOG) -- crit BRAKE_START_MOVE, lo TRUE, hi TRUE, units BOOL, min_inst 4; manifest status OWED
  - no input log declares this cell (SIGNOFF-DECL) or prints a verdict for it

## NOT_BUILT

- R1-SCAN-COGOK -- NO_DECLARING_LOG: no input log declares this cell (SIGNOFF-DECL) or prints a verdict for it
- R1-T0-START -- NO_DECLARING_LOG: no input log declares this cell (SIGNOFF-DECL) or prints a verdict for it
- R1-T0-EXHAUST -- NO_DECLARING_LOG: no input log declares this cell (SIGNOFF-DECL) or prints a verdict for it
- R1-T0-RESTART -- NO_DECLARING_LOG: no input log declares this cell (SIGNOFF-DECL) or prints a verdict for it
- R2-SCAN-REVB -- NO_DECLARING_LOG: no input log declares this cell (SIGNOFF-DECL) or prints a verdict for it
- R2-T0-REPEAT -- NO_DECLARING_LOG: no input log declares this cell (SIGNOFF-DECL) or prints a verdict for it
- R2-T0-DIRTY -- NO_DECLARING_LOG: no input log declares this cell (SIGNOFF-DECL) or prints a verdict for it
- R2-T0-EMPTY -- NO_DECLARING_LOG: no input log declares this cell (SIGNOFF-DECL) or prints a verdict for it
- R2-HOST-DETDIFF -- INPUT_ABSENT: no detect-phase2 log among the inputs (BD-BANNER tool test_bench_detect, BD-BUILD phase2_compiled 1, BD-CFG cfg_id BENCH); prediction list absent: DOCs/analyses/bench/SIGNOFF-DETECT-PREDICTIONS.tsv
- R2-CHAR-ISCALE -- NO_DECLARING_LOG: no input log declares this cell (SIGNOFF-DECL) or prints a verdict for it
- R2-DETECT-GUARD -- INPUT_ABSENT: no detect-phase2 log among the inputs (BD-BANNER tool test_bench_detect, BD-BUILD phase2_compiled 1, BD-CFG cfg_id BENCH); prediction list absent: DOCs/analyses/bench/SIGNOFF-DETECT-PREDICTIONS.tsv
- R3-SCAN-INTEG -- NO_DECLARING_LOG: no input log declares this cell (SIGNOFF-DECL) or prints a verdict for it
- R3-CHAR-INTEG -- NO_DECLARING_LOG: no input log declares this cell (SIGNOFF-DECL) or prints a verdict for it
- R3-T0-STOPPED -- NO_DECLARING_LOG: no input log declares this cell (SIGNOFF-DECL) or prints a verdict for it
- R4-T0-1M-TICKS -- NO_DECLARING_LOG: no input log declares this cell (SIGNOFF-DECL) or prints a verdict for it
- R4-CHAR-RPM -- NO_DECLARING_LOG: no input log declares this cell (SIGNOFF-DECL) or prints a verdict for it
- R5-SCAN-SELF -- NO_DECLARING_LOG: no input log declares this cell (SIGNOFF-DECL) or prints a verdict for it
- R5-CHAR-SENSE -- NO_DECLARING_LOG: no input log declares this cell (SIGNOFF-DECL) or prints a verdict for it
- R6-SCAN-OFFSETS -- NO_DECLARING_LOG: no input log declares this cell (SIGNOFF-DECL) or prints a verdict for it
- R7-SCAN-STARTILL -- NO_DECLARING_LOG: no input log declares this cell (SIGNOFF-DECL) or prints a verdict for it
- R8-SCAN-ZXS -- NO_DECLARING_LOG: no input log declares this cell (SIGNOFF-DECL) or prints a verdict for it
- R8-T0-ZXS -- NO_DECLARING_LOG: no input log declares this cell (SIGNOFF-DECL) or prints a verdict for it
- R9-SCAN-HALFLEG -- NO_DECLARING_LOG: no input log declares this cell (SIGNOFF-DECL) or prints a verdict for it
- R9-SCAN-OWNZERO -- NO_DECLARING_LOG: no input log declares this cell (SIGNOFF-DECL) or prints a verdict for it
- R9-SCAN-PAIR2 -- NO_DECLARING_LOG: no input log declares this cell (SIGNOFF-DECL) or prints a verdict for it
- R10-SCAN-RSTALONE -- NO_DECLARING_LOG: no input log declares this cell (SIGNOFF-DECL) or prints a verdict for it
- R10-T0-STOPREADY -- NO_DECLARING_LOG: no input log declares this cell (SIGNOFF-DECL) or prints a verdict for it
- R10-CHAR-STEERSTART -- NO_DECLARING_LOG: no input log declares this cell (SIGNOFF-DECL) or prints a verdict for it
- R10-CHAR-STEERLIVE -- NO_DECLARING_LOG: no input log declares this cell (SIGNOFF-DECL) or prints a verdict for it
- R10-CHAR-STEERFAIL -- NO_DECLARING_LOG: no input log declares this cell (SIGNOFF-DECL) or prints a verdict for it
- R10-HOST-PL9 -- STATIC_NOT_REQUESTED: run with --static-tree to evaluate this static source cell
- R11-SCAN-NOSTALL -- NO_DECLARING_LOG: no input log declares this cell (SIGNOFF-DECL) or prints a verdict for it
- R11-WDT-FIRES -- NO_DECLARING_LOG: no input log declares this cell (SIGNOFF-DECL) or prints a verdict for it
- R11-WDT-CKPT -- NO_DECLARING_LOG: no input log declares this cell (SIGNOFF-DECL) or prints a verdict for it
- R11-WDT-STOPPED -- NO_DECLARING_LOG: no input log declares this cell (SIGNOFF-DECL) or prints a verdict for it
- R11-WDT-STACK -- NO_DECLARING_LOG: no input log declares this cell (SIGNOFF-DECL) or prints a verdict for it
- R11-HOST-WDTEND -- NO_WD_SELFTEST_LOG: no input log carries BS-BUILD wd_selftest,TRUE
- R12-SCAN-ALIVE -- NO_DECLARING_LOG: no input log declares this cell (SIGNOFF-DECL) or prints a verdict for it
- R12-SCAN-RATE -- NO_DECLARING_LOG: no input log declares this cell (SIGNOFF-DECL) or prints a verdict for it
- R13-CHAR-BRAKESTART -- NO_DECLARING_LOG: no input log declares this cell (SIGNOFF-DECL) or prints a verdict for it

## Superseded logs

- (none)

## Unmanifested cells

- (none)

## Parse errors

- (none)

## Deferred cells (not owed to this visit)

- R2-DETECT-OVERLAP (row 2): overlapping-group cells P40_P55 and NO_USE_P24_P39, run only in a session with the motors unplugged (design J.2 ruling)

## DETDIFF change list

- not computed: the detection-sweep diff is a phase 2d stub, so R2-HOST-DETDIFF cannot leave NOT_BUILT

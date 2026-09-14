# Visit 1 sign-off sheet -- 2026-09-14

- Script: `tools/signoff-collate.py`
- Manifest: `DOCs/analyses/bench/SIGNOFF-MANIFEST.tsv` -- statuses updated by this run (--update)
- Design: `DOCs/plans/VISIT-SIGNOFF-DESIGN.md`
- Flags: --static-tree yes; --update yes
- Detect prediction list: `DOCs/analyses/bench/SIGNOFF-DETECT-PREDICTIONS.tsv` (present); detect baseline: `DOCs/analyses/bench/2026-09-11/debug_260911-210229.log` (present)
- Rules: a verdict exists only where a binary printed one; a cell reaches PASS only by positive evidence; a declared cell without a verdict is NOMEAS (design section 0)

## Input logs

1. `DOCs/analyses/bench/2026-09-14/debug_260914-113610.log` -- **TRUNCATED** -- TRUNCATED (no DEBUG_END_SESSION line)
   - identity: BS-BANNER src_rev 9 fmt 9 (line 21); download test_bench_scan.bin, 48748 bytes, modified 2026-09-14T17:36:09.301Z (line 14)
   - build key: banner BS-BANNER, src_rev 9, fmt 9, bin test_bench_scan.bin, size 48748 (modified time recorded, not keyed)
   - records: 14 SIGNOFF-DECL, 0 SIGNOFF, 0 malformed
2. `DOCs/analyses/bench/2026-09-14/debug_260914-114523.log` -- **COMPLETE** -- COMPLETE (DEBUG_END_SESSION at line 82, Cog1)
   - identity: BS-BANNER src_rev 9 fmt 9 (line 21); download test_bench_scan.bin, 48324 bytes, modified 2026-09-14T17:45:22.483Z (line 14)
   - build key: banner BS-BANNER, src_rev 9, fmt 9, bin test_bench_scan.bin, size 48324 (modified time recorded, not keyed)
   - records: 4 SIGNOFF-DECL, 4 SIGNOFF, 0 malformed
3. `DOCs/analyses/bench/2026-09-14/debug_260914-114608.log` -- **COMPLETE** -- COMPLETE (DEBUG_END_SESSION at line 1271, Cog0)
   - identity: BD-BANNER src_rev 3 fmt 2 (line 19); download test_bench_detect.bin, 31637 bytes, modified 2026-09-14T17:46:07.141Z (line 14)
   - build key: banner BD-BANNER, src_rev 3, fmt 2, bin test_bench_detect.bin, size 31637 (modified time recorded, not keyed)
   - records: 0 SIGNOFF-DECL, 0 SIGNOFF, 0 malformed
4. `DOCs/analyses/bench/2026-09-14/debug_260914-114636.log` -- **COMPLETE** -- COMPLETE (DEBUG_END_SESSION at line 1062, Cog0)
   - identity: banner '* test_bench_t0' at line 11 -- Tier 0 prints no src_rev/fmt, so the download header identifies its build; download test_bench_t0.bin, 30455 bytes, modified 2026-09-14T17:46:35.053Z (line 6)
   - build key: banner T0, src_rev NA, fmt NA, bin test_bench_t0.bin, size 30455 (modified time recorded, not keyed)
   - records: 10 SIGNOFF-DECL, 14 SIGNOFF, 0 malformed
5. `DOCs/analyses/bench/2026-09-14/debug_260914-114703.log` -- **COMPLETE** -- COMPLETE (DEBUG_END_SESSION at line 1412, Cog0)
   - identity: BS-BANNER src_rev 9 fmt 9 (line 21); download test_bench_scan.bin, 48748 bytes, modified 2026-09-14T17:47:02.817Z (line 14)
   - build key: banner BS-BANNER, src_rev 9, fmt 9, bin test_bench_scan.bin, size 48748 (modified time recorded, not keyed)
   - records: 14 SIGNOFF-DECL, 41 SIGNOFF, 0 malformed
6. `DOCs/analyses/bench/2026-09-14/debug_260914-115953.log` -- **COMPLETE** -- COMPLETE (DEBUG_END_SESSION at line 521, Cog0)
   - identity: BC-BANNER src_rev 5 fmt 5 (line 21); download test_bench_char.bin, 41233 bytes, modified 2026-09-14T17:59:52.303Z (line 14)
   - build key: banner BC-BANNER, src_rev 5, fmt 5, bin test_bench_char.bin, size 41233 (modified time recorded, not keyed)
   - records: 8 SIGNOFF-DECL, 34 SIGNOFF, 0 malformed
7. `DOCs/analyses/bench/2026-09-14/debug_260914-120126.log` -- **TRUNCATED** -- TRUNCATED (no DEBUG_END_SESSION line)
   - identity: banner '* test_bench_t0' at line 19 -- Tier 0 prints no src_rev/fmt, so the download header identifies its build; download test_bench_t0.bin, 30357 bytes, modified 2026-09-14T18:01:25.719Z (line 14)
   - build key: banner T0, src_rev NA, fmt NA, bin test_bench_t0.bin, size 30357 (modified time recorded, not keyed)
   - records: 0 SIGNOFF-DECL, 0 SIGNOFF, 0 malformed

## Rows

| row | task | feature | verdict |
|---|---|---|---|
| 1 | 3499 | start() returns cog id 0..7 or -1; a second start() restarts with no orphaned cog | **FAIL** |
| 2 | 3500, 3537 | board detection: Rev B read reliably at every start and after a driver stop; an empty group is not detected | **PASS** |
| 3 | 3501 | hall integrity counters | **PASS** |
| 4 | 3502 | rpm and mm/tick precision | **PASS** |
| 5 | 3503 | S-3 ADC scale restore | **PASS** |
| 6 | 3519 | independent offset setter | **PASS** |
| 7 | 3524 | hall inputs not driven at start | **PASS** |
| 8 | 3529 | ADC calibration from a settled average | **PASS** |
| 9 | 3530 | scan v4 logic ran | **PASS** |
| 10 | 3533 | PL-28, PL-22 and PL-9 | **FAIL** |
| 11 | 3534 | scan watchdog | **PASS** |
| 12 | 3535 | driver start code in the cog LUT | **PASS** |
| 13 | 3535 | brake-mode start path runs cleanly (prior_angle initialised at driver start, commit b34e109) | **NOMEAS** |

## Cells

- **R1-SCAN-COGOK** (row 1, bin SCAN) -- **PASS** -- crit STARTS_COG_BAD, lo 0, hi 0, units COUNT, min_inst 2; manifest status SIGNED_OFF (ref V1:DOCs/analyses/bench/2026-09-14/debug_260914-114703.log:1368;V1:DOCs/analyses/bench/2026-09-14/debug_260914-114703.log:1389)
  - speaking build: banner BS-BANNER, src_rev 9, fmt 9, bin test_bench_scan.bin, size 48748 (2 log(s))
  - DOCs/analyses/bench/2026-09-14/debug_260914-113610.log: NOMEAS (NOT_REACHED; declared, no SIGNOFF instance)
  - DOCs/analyses/bench/2026-09-14/debug_260914-114703.log: PASS (2 of 2 counted PASS instances)
  - DOCs/analyses/bench/2026-09-14/debug_260914-114703.log:1368 motor LEFT crit STARTS_COG_BAD measured 0 lo 0 hi 0 units COUNT n 9 printed PASS -> PASS
  - DOCs/analyses/bench/2026-09-14/debug_260914-114703.log:1389 motor RIGHT crit STARTS_COG_BAD measured 0 lo 0 hi 0 units COUNT n 9 printed PASS -> PASS
- **R1-T0-START** (row 1, bin T0) -- **FAIL** (BINARY_FAIL) -- crit RET_EQ_COG_M1, lo TRUE, hi TRUE, units BOOL, min_inst 1; manifest status FAILED (ref V1:DOCs/analyses/bench/2026-09-14/debug_260914-114636.log:970)
  - speaking build: banner T0, src_rev NA, fmt NA, bin test_bench_t0.bin, size 30455 (1 log(s))
  - DOCs/analyses/bench/2026-09-14/debug_260914-114636.log: FAIL (BINARY_FAIL)
  - DOCs/analyses/bench/2026-09-14/debug_260914-114636.log:970 motor NONE crit RET_EQ_COG_M1 measured FALSE lo TRUE hi TRUE units BOOL n 1 printed FAIL -> FAIL
- **R1-T0-EXHAUST** (row 1, bin T0) -- **FAIL** (BINARY_FAIL) -- crit RET_NEG_NOLEAK, lo TRUE, hi TRUE, units BOOL, min_inst 1; manifest status FAILED (ref V1:DOCs/analyses/bench/2026-09-14/debug_260914-114636.log:1060)
  - speaking build: banner T0, src_rev NA, fmt NA, bin test_bench_t0.bin, size 30455 (1 log(s))
  - DOCs/analyses/bench/2026-09-14/debug_260914-114636.log: FAIL (BINARY_FAIL)
  - DOCs/analyses/bench/2026-09-14/debug_260914-114636.log:1060 motor NONE crit RET_NEG_NOLEAK measured FALSE lo TRUE hi TRUE units BOOL n 1 printed FAIL -> FAIL
- **R1-T0-RESTART** (row 1, bin T0) -- **NOMEAS** (NOT_REACHED) -- crit NO_ORPHAN, lo TRUE, hi TRUE, units BOOL, min_inst 1; manifest status OWED
  - speaking build: banner T0, src_rev NA, fmt NA, bin test_bench_t0.bin, size 30455 (1 log(s))
  - DOCs/analyses/bench/2026-09-14/debug_260914-114636.log: NOMEAS (NOT_REACHED; declared, no SIGNOFF instance)
- **R2-SCAN-REVB** (row 2, bin SCAN) -- **PASS** -- crit STARTS_NOT_REVB, lo 0, hi 0, units COUNT, min_inst 2; manifest status SIGNED_OFF (ref V1:DOCs/analyses/bench/2026-09-14/debug_260914-114703.log:1369;V1:DOCs/analyses/bench/2026-09-14/debug_260914-114703.log:1390)
  - speaking build: banner BS-BANNER, src_rev 9, fmt 9, bin test_bench_scan.bin, size 48748 (2 log(s))
  - DOCs/analyses/bench/2026-09-14/debug_260914-113610.log: NOMEAS (NOT_REACHED; declared, no SIGNOFF instance)
  - DOCs/analyses/bench/2026-09-14/debug_260914-114703.log: PASS (2 of 2 counted PASS instances)
  - DOCs/analyses/bench/2026-09-14/debug_260914-114703.log:1369 motor LEFT crit STARTS_NOT_REVB measured 0 lo 0 hi 0 units COUNT n 9 printed PASS -> PASS
  - DOCs/analyses/bench/2026-09-14/debug_260914-114703.log:1390 motor RIGHT crit STARTS_NOT_REVB measured 0 lo 0 hi 0 units COUNT n 9 printed PASS -> PASS
- **R2-T0-REPEAT** (row 2, bin T0) -- **PASS** -- crit READS_NOT_REVB, lo 0, hi 0, units COUNT, min_inst 2; manifest status SIGNED_OFF (ref V1:DOCs/analyses/bench/2026-09-14/debug_260914-114636.log:525;V1:DOCs/analyses/bench/2026-09-14/debug_260914-114636.log:847)
  - speaking build: banner T0, src_rev NA, fmt NA, bin test_bench_t0.bin, size 30455 (1 log(s))
  - DOCs/analyses/bench/2026-09-14/debug_260914-114636.log: PASS (2 of 2 counted PASS instances)
  - DOCs/analyses/bench/2026-09-14/debug_260914-114636.log:525 motor RIGHT crit READS_NOT_REVB measured 0 lo 0 hi 0 units COUNT n 32 printed PASS -> PASS
  - DOCs/analyses/bench/2026-09-14/debug_260914-114636.log:847 motor LEFT crit READS_NOT_REVB measured 0 lo 0 hi 0 units COUNT n 32 printed PASS -> PASS
- **R2-T0-DIRTY** (row 2, bin T0) -- **PASS** -- crit POSTSTOP_REVB, lo TRUE, hi TRUE, units BOOL, min_inst 2; manifest status SIGNED_OFF (ref V1:DOCs/analyses/bench/2026-09-14/debug_260914-114636.log:895;V1:DOCs/analyses/bench/2026-09-14/debug_260914-114636.log:942)
  - speaking build: banner T0, src_rev NA, fmt NA, bin test_bench_t0.bin, size 30455 (1 log(s))
  - DOCs/analyses/bench/2026-09-14/debug_260914-114636.log: PASS (2 of 2 counted PASS instances)
  - DOCs/analyses/bench/2026-09-14/debug_260914-114636.log:895 motor RIGHT crit POSTSTOP_REVB measured TRUE lo TRUE hi TRUE units BOOL n 1 printed PASS -> PASS
  - DOCs/analyses/bench/2026-09-14/debug_260914-114636.log:942 motor LEFT crit POSTSTOP_REVB measured TRUE lo TRUE hi TRUE units BOOL n 1 printed PASS -> PASS
- **R2-T0-EMPTY** (row 2, bin T0) -- **PASS** -- crit EMPTY_NODET, lo TRUE, hi TRUE, units BOOL, min_inst 1; manifest status SIGNED_OFF (ref V1:DOCs/analyses/bench/2026-09-14/debug_260914-114636.log:955)
  - speaking build: banner T0, src_rev NA, fmt NA, bin test_bench_t0.bin, size 30455 (1 log(s))
  - DOCs/analyses/bench/2026-09-14/debug_260914-114636.log: PASS (1 of 1 counted PASS instances)
  - DOCs/analyses/bench/2026-09-14/debug_260914-114636.log:955 motor NONE crit EMPTY_NODET measured TRUE lo TRUE hi TRUE units BOOL n 1 printed PASS -> PASS
- **R2-HOST-DETDIFF** (row 2, bin HOST) -- **PASS** -- crit ONLY_PREDICTED, lo 0, hi 0, units COUNT, min_inst 1; manifest status SIGNED_OFF (ref V1:DOCs/analyses/bench/2026-09-14/debug_260914-114608.log:19)
  - speaking build: banner BD-BANNER, src_rev 3, fmt 2, bin test_bench_detect.bin, size 31637 (1 log(s))
  - baseline DOCs/analyses/bench/2026-09-11/debug_260911-210229.log; predictions DOCs/analyses/bench/SIGNOFF-DETECT-PREDICTIONS.tsv (64 prediction line(s))
  - DOCs/analyses/bench/2026-09-14/debug_260914-114608.log: PASS; measured 0 = 0 unpredicted change(s) + 0 predicted change(s) that did not occur, lo 0, hi 0, COUNT; 14 predicted change(s) occurred; 12 cell(s) NOT_COMPARED; itemised in the DETDIFF change list
- **R2-CHAR-ISCALE** (row 2, bin CHAR) -- **PASS** -- crit RSENSE_IMPLIED, lo 135, hi 165, units COUNT, min_inst 8; manifest status SIGNED_OFF (ref V1:DOCs/analyses/bench/2026-09-14/debug_260914-115953.log:501;V1:DOCs/analyses/bench/2026-09-14/debug_260914-115953.log:502;V1:DOCs/analyses/bench/2026-09-14/debug_260914-115953.log:503;V1:DOCs/analyses/bench/2026-09-14/debug_260914-115953.log:504;V1:DOCs/analyses/bench/2026-09-14/debug_260914-115953.log:505;V1:DOCs/analyses/bench/2026-09-14/debug_260914-115953.log:506;V1:DOCs/analyses/bench/2026-09-14/debug_260914-115953.log:507;V1:DOCs/analyses/bench/2026-09-14/debug_260914-115953.log:508)
  - speaking build: banner BC-BANNER, src_rev 5, fmt 5, bin test_bench_char.bin, size 41233 (1 log(s))
  - DOCs/analyses/bench/2026-09-14/debug_260914-115953.log: PASS (8 of 8 counted PASS instances)
  - DOCs/analyses/bench/2026-09-14/debug_260914-115953.log:501 motor LEFT crit RSENSE_IMPLIED measured 149 lo 135 hi 165 units COUNT n 591 printed PASS -> PASS
  - DOCs/analyses/bench/2026-09-14/debug_260914-115953.log:502 motor LEFT crit RSENSE_IMPLIED measured 149 lo 135 hi 165 units COUNT n 591 printed PASS -> PASS
  - DOCs/analyses/bench/2026-09-14/debug_260914-115953.log:503 motor RIGHT crit RSENSE_IMPLIED measured 149 lo 135 hi 165 units COUNT n 591 printed PASS -> PASS
  - DOCs/analyses/bench/2026-09-14/debug_260914-115953.log:504 motor RIGHT crit RSENSE_IMPLIED measured 150 lo 135 hi 165 units COUNT n 591 printed PASS -> PASS
  - DOCs/analyses/bench/2026-09-14/debug_260914-115953.log:505 motor LEFT crit RSENSE_IMPLIED measured 149 lo 135 hi 165 units COUNT n 591 printed PASS -> PASS
  - DOCs/analyses/bench/2026-09-14/debug_260914-115953.log:506 motor LEFT crit RSENSE_IMPLIED measured 149 lo 135 hi 165 units COUNT n 591 printed PASS -> PASS
  - DOCs/analyses/bench/2026-09-14/debug_260914-115953.log:507 motor RIGHT crit RSENSE_IMPLIED measured 150 lo 135 hi 165 units COUNT n 591 printed PASS -> PASS
  - DOCs/analyses/bench/2026-09-14/debug_260914-115953.log:508 motor RIGHT crit RSENSE_IMPLIED measured 149 lo 135 hi 165 units COUNT n 591 printed PASS -> PASS
- **R2-DETECT-GUARD** (row 2, bin HOST) -- **PASS** -- crit GUARD_SKIPS_OK, lo TRUE, hi TRUE, units BOOL, min_inst 1; manifest status SIGNED_OFF (ref V1:DOCs/analyses/bench/2026-09-14/debug_260914-114608.log:33;V1:DOCs/analyses/bench/2026-09-14/debug_260914-114608.log:35;V1:DOCs/analyses/bench/2026-09-14/debug_260914-114608.log:263;V1:DOCs/analyses/bench/2026-09-14/debug_260914-114608.log:448;V1:DOCs/analyses/bench/2026-09-14/debug_260914-114608.log:489;V1:DOCs/analyses/bench/2026-09-14/debug_260914-114608.log:675;V1:DOCs/analyses/bench/2026-09-14/debug_260914-114608.log:859;V1:DOCs/analyses/bench/2026-09-14/debug_260914-114608.log:897;V1:DOCs/analyses/bench/2026-09-14/debug_260914-114608.log:1083;V1:DOCs/analyses/bench/2026-09-14/debug_260914-114608.log:1267)
  - speaking build: banner BD-BANNER, src_rev 3, fmt 2, bin test_bench_detect.bin, size 31637 (1 log(s))
  - DOCs/analyses/bench/2026-09-14/debug_260914-114608.log: skip set from BD-CFG left_base 32 right_base 16 -- GATE_OVERLAP groups NO_USE_P24_P39, P40_P55; COG_OVERLAP sweeps none; 12 skipped cell(s) across 8 planned sweep(s)
  - DOCs/analyses/bench/2026-09-14/debug_260914-114608.log: TRUE -- no BD-REP or BD-CELL for a skipped cell, one BD-SKIPPED per skipped cell, BD-MAP guard matches, 8 BD-SWEEP end count(s) equal the plan less the skipped cells
  - measured TRUE, lo TRUE, hi TRUE, BOOL
  - DOCs/analyses/bench/2026-09-14/debug_260914-114608.log:33 (proving line)
  - DOCs/analyses/bench/2026-09-14/debug_260914-114608.log:35 (proving line)
  - DOCs/analyses/bench/2026-09-14/debug_260914-114608.log:263 (proving line)
  - DOCs/analyses/bench/2026-09-14/debug_260914-114608.log:448 (proving line)
  - DOCs/analyses/bench/2026-09-14/debug_260914-114608.log:489 (proving line)
  - DOCs/analyses/bench/2026-09-14/debug_260914-114608.log:675 (proving line)
  - DOCs/analyses/bench/2026-09-14/debug_260914-114608.log:859 (proving line)
  - DOCs/analyses/bench/2026-09-14/debug_260914-114608.log:897 (proving line)
  - DOCs/analyses/bench/2026-09-14/debug_260914-114608.log:1083 (proving line)
  - DOCs/analyses/bench/2026-09-14/debug_260914-114608.log:1267 (proving line)
- **R3-SCAN-INTEG** (row 3, bin SCAN) -- **PASS** -- crit MISSED_ILLEGAL_SUM, lo 0, hi 0, units COUNT, min_inst 2; manifest status SIGNED_OFF (ref V1:DOCs/analyses/bench/2026-09-14/debug_260914-114703.log:1370;V1:DOCs/analyses/bench/2026-09-14/debug_260914-114703.log:1391)
  - speaking build: banner BS-BANNER, src_rev 9, fmt 9, bin test_bench_scan.bin, size 48748 (2 log(s))
  - DOCs/analyses/bench/2026-09-14/debug_260914-113610.log: NOMEAS (NOT_REACHED; declared, no SIGNOFF instance)
  - DOCs/analyses/bench/2026-09-14/debug_260914-114703.log: PASS (2 of 2 counted PASS instances)
  - DOCs/analyses/bench/2026-09-14/debug_260914-114703.log:1370 motor LEFT crit MISSED_ILLEGAL_SUM measured 0 lo 0 hi 0 units COUNT n 62 printed PASS -> PASS
  - DOCs/analyses/bench/2026-09-14/debug_260914-114703.log:1391 motor RIGHT crit MISSED_ILLEGAL_SUM measured 0 lo 0 hi 0 units COUNT n 58 printed PASS -> PASS
- **R3-CHAR-INTEG** (row 3, bin CHAR) -- **PASS** -- crit MISSED_ILLEGAL_SUM, lo 0, hi 0, units COUNT, min_inst 2; manifest status SIGNED_OFF (ref V1:DOCs/analyses/bench/2026-09-14/debug_260914-115953.log:509;V1:DOCs/analyses/bench/2026-09-14/debug_260914-115953.log:510)
  - speaking build: banner BC-BANNER, src_rev 5, fmt 5, bin test_bench_char.bin, size 41233 (1 log(s))
  - DOCs/analyses/bench/2026-09-14/debug_260914-115953.log: PASS (2 of 2 counted PASS instances)
  - DOCs/analyses/bench/2026-09-14/debug_260914-115953.log:509 motor LEFT crit MISSED_ILLEGAL_SUM measured 0 lo 0 hi 0 units COUNT n 5 printed PASS -> PASS
  - DOCs/analyses/bench/2026-09-14/debug_260914-115953.log:510 motor RIGHT crit MISSED_ILLEGAL_SUM measured 0 lo 0 hi 0 units COUNT n 4 printed PASS -> PASS
- **R3-T0-STOPPED** (row 3, bin T0) -- **PASS** -- crit STOPPED_COUNTS, lo 0, hi 0, units COUNT, min_inst 1; manifest status SIGNED_OFF (ref V1:DOCs/analyses/bench/2026-09-14/debug_260914-114636.log:202)
  - speaking build: banner T0, src_rev NA, fmt NA, bin test_bench_t0.bin, size 30455 (1 log(s))
  - DOCs/analyses/bench/2026-09-14/debug_260914-114636.log: PASS (1 of 1 counted PASS instances)
  - DOCs/analyses/bench/2026-09-14/debug_260914-114636.log:202 motor NONE crit STOPPED_COUNTS measured 0 lo 0 hi 0 units COUNT n 1 printed PASS -> PASS
- **R4-T0-1M-TICKS** (row 4, bin T0) -- **PASS** -- crit DDU_M_TICKS, lo TRUE, hi TRUE, units BOOL, min_inst 1; manifest status SIGNED_OFF (ref V1:DOCs/analyses/bench/2026-09-14/debug_260914-114636.log:54)
  - speaking build: banner T0, src_rev NA, fmt NA, bin test_bench_t0.bin, size 30455 (1 log(s))
  - DOCs/analyses/bench/2026-09-14/debug_260914-114636.log: PASS (1 of 1 counted PASS instances)
  - DOCs/analyses/bench/2026-09-14/debug_260914-114636.log:54 motor NONE crit DDU_M_TICKS measured TRUE lo TRUE hi TRUE units BOOL n 1 printed PASS -> PASS
- **R4-CHAR-RPM** (row 4, bin CHAR) -- **PASS** -- crit RPM_ERR, lo -2, hi 2, units RPM, min_inst 8; manifest status SIGNED_OFF (ref V1:DOCs/analyses/bench/2026-09-14/debug_260914-115953.log:493;V1:DOCs/analyses/bench/2026-09-14/debug_260914-115953.log:494;V1:DOCs/analyses/bench/2026-09-14/debug_260914-115953.log:495;V1:DOCs/analyses/bench/2026-09-14/debug_260914-115953.log:496;V1:DOCs/analyses/bench/2026-09-14/debug_260914-115953.log:497;V1:DOCs/analyses/bench/2026-09-14/debug_260914-115953.log:498;V1:DOCs/analyses/bench/2026-09-14/debug_260914-115953.log:499;V1:DOCs/analyses/bench/2026-09-14/debug_260914-115953.log:500)
  - speaking build: banner BC-BANNER, src_rev 5, fmt 5, bin test_bench_char.bin, size 41233 (1 log(s))
  - DOCs/analyses/bench/2026-09-14/debug_260914-115953.log: PASS (8 of 8 counted PASS instances)
  - DOCs/analyses/bench/2026-09-14/debug_260914-115953.log:493 motor LEFT crit RPM_ERR measured 0 lo -2 hi 2 units RPM n 295 printed PASS -> PASS
  - DOCs/analyses/bench/2026-09-14/debug_260914-115953.log:494 motor LEFT crit RPM_ERR measured 0 lo -2 hi 2 units RPM n 295 printed PASS -> PASS
  - DOCs/analyses/bench/2026-09-14/debug_260914-115953.log:495 motor RIGHT crit RPM_ERR measured 0 lo -2 hi 2 units RPM n 295 printed PASS -> PASS
  - DOCs/analyses/bench/2026-09-14/debug_260914-115953.log:496 motor RIGHT crit RPM_ERR measured 0 lo -2 hi 2 units RPM n 295 printed PASS -> PASS
  - DOCs/analyses/bench/2026-09-14/debug_260914-115953.log:497 motor LEFT crit RPM_ERR measured 0 lo -2 hi 2 units RPM n 590 printed PASS -> PASS
  - DOCs/analyses/bench/2026-09-14/debug_260914-115953.log:498 motor LEFT crit RPM_ERR measured 0 lo -2 hi 2 units RPM n 590 printed PASS -> PASS
  - DOCs/analyses/bench/2026-09-14/debug_260914-115953.log:499 motor RIGHT crit RPM_ERR measured 0 lo -2 hi 2 units RPM n 590 printed PASS -> PASS
  - DOCs/analyses/bench/2026-09-14/debug_260914-115953.log:500 motor RIGHT crit RPM_ERR measured 0 lo -2 hi 2 units RPM n 590 printed PASS -> PASS
- **R5-SCAN-SELF** (row 5, bin SCAN) -- **PASS** -- crit NET_I_IN_BAND, lo TRUE, hi TRUE, units BOOL, min_inst 2; manifest status SIGNED_OFF (ref V1:DOCs/analyses/bench/2026-09-14/debug_260914-114703.log:1371;V1:DOCs/analyses/bench/2026-09-14/debug_260914-114703.log:1392)
  - speaking build: banner BS-BANNER, src_rev 9, fmt 9, bin test_bench_scan.bin, size 48748 (2 log(s))
  - DOCs/analyses/bench/2026-09-14/debug_260914-113610.log: NOMEAS (NOT_REACHED; declared, no SIGNOFF instance)
  - DOCs/analyses/bench/2026-09-14/debug_260914-114703.log: PASS (2 of 2 counted PASS instances)
  - DOCs/analyses/bench/2026-09-14/debug_260914-114703.log:1371 motor LEFT crit NET_I_IN_BAND measured TRUE lo TRUE hi TRUE units BOOL n 1 printed PASS -> PASS
  - DOCs/analyses/bench/2026-09-14/debug_260914-114703.log:1392 motor RIGHT crit NET_I_IN_BAND measured TRUE lo TRUE hi TRUE units BOOL n 1 printed PASS -> PASS
- **R5-CHAR-SENSE** (row 5, bin CHAR) -- **PASS** -- crit NET_VS_PASS1_PCT, lo -150, hi 150, units PCT_X10, min_inst 8; manifest status SIGNED_OFF (ref V1:DOCs/analyses/bench/2026-09-14/debug_260914-115953.log:485;V1:DOCs/analyses/bench/2026-09-14/debug_260914-115953.log:486;V1:DOCs/analyses/bench/2026-09-14/debug_260914-115953.log:487;V1:DOCs/analyses/bench/2026-09-14/debug_260914-115953.log:488;V1:DOCs/analyses/bench/2026-09-14/debug_260914-115953.log:489;V1:DOCs/analyses/bench/2026-09-14/debug_260914-115953.log:490;V1:DOCs/analyses/bench/2026-09-14/debug_260914-115953.log:491;V1:DOCs/analyses/bench/2026-09-14/debug_260914-115953.log:492)
  - speaking build: banner BC-BANNER, src_rev 5, fmt 5, bin test_bench_char.bin, size 41233 (1 log(s))
  - DOCs/analyses/bench/2026-09-14/debug_260914-115953.log: PASS (8 of 8 counted PASS instances)
  - DOCs/analyses/bench/2026-09-14/debug_260914-115953.log:485 motor LEFT crit NET_VS_PASS1_PCT measured 49 lo -150 hi 150 units PCT_X10 n 591 printed PASS -> PASS
  - DOCs/analyses/bench/2026-09-14/debug_260914-115953.log:486 motor LEFT crit NET_VS_PASS1_PCT measured 47 lo -150 hi 150 units PCT_X10 n 591 printed PASS -> PASS
  - DOCs/analyses/bench/2026-09-14/debug_260914-115953.log:487 motor RIGHT crit NET_VS_PASS1_PCT measured 64 lo -150 hi 150 units PCT_X10 n 591 printed PASS -> PASS
  - DOCs/analyses/bench/2026-09-14/debug_260914-115953.log:488 motor RIGHT crit NET_VS_PASS1_PCT measured 49 lo -150 hi 150 units PCT_X10 n 591 printed PASS -> PASS
  - DOCs/analyses/bench/2026-09-14/debug_260914-115953.log:489 motor LEFT crit NET_VS_PASS1_PCT measured 49 lo -150 hi 150 units PCT_X10 n 591 printed PASS -> PASS
  - DOCs/analyses/bench/2026-09-14/debug_260914-115953.log:490 motor LEFT crit NET_VS_PASS1_PCT measured 106 lo -150 hi 150 units PCT_X10 n 591 printed PASS -> PASS
  - DOCs/analyses/bench/2026-09-14/debug_260914-115953.log:491 motor RIGHT crit NET_VS_PASS1_PCT measured 51 lo -150 hi 150 units PCT_X10 n 591 printed PASS -> PASS
  - DOCs/analyses/bench/2026-09-14/debug_260914-115953.log:492 motor RIGHT crit NET_VS_PASS1_PCT measured 97 lo -150 hi 150 units PCT_X10 n 591 printed PASS -> PASS
- **R6-SCAN-OFFSETS** (row 6, bin SCAN) -- **PASS** -- crit READBACK_BAD, lo 0, hi 0, units COUNT, min_inst 2; manifest status SIGNED_OFF (ref V1:DOCs/analyses/bench/2026-09-14/debug_260914-114703.log:1372;V1:DOCs/analyses/bench/2026-09-14/debug_260914-114703.log:1393)
  - speaking build: banner BS-BANNER, src_rev 9, fmt 9, bin test_bench_scan.bin, size 48748 (2 log(s))
  - DOCs/analyses/bench/2026-09-14/debug_260914-113610.log: NOMEAS (NOT_REACHED; declared, no SIGNOFF instance)
  - DOCs/analyses/bench/2026-09-14/debug_260914-114703.log: PASS (2 of 2 counted PASS instances)
  - DOCs/analyses/bench/2026-09-14/debug_260914-114703.log:1372 motor LEFT crit READBACK_BAD measured 0 lo 0 hi 0 units COUNT n 64 printed PASS -> PASS
  - DOCs/analyses/bench/2026-09-14/debug_260914-114703.log:1393 motor RIGHT crit READBACK_BAD measured 0 lo 0 hi 0 units COUNT n 60 printed PASS -> PASS
- **R7-SCAN-STARTILL** (row 7, bin SCAN) -- **PASS** -- crit STARTS_ILLEGAL, lo 0, hi 0, units COUNT, min_inst 2; manifest status SIGNED_OFF (ref V1:DOCs/analyses/bench/2026-09-14/debug_260914-114703.log:1373;V1:DOCs/analyses/bench/2026-09-14/debug_260914-114703.log:1394)
  - speaking build: banner BS-BANNER, src_rev 9, fmt 9, bin test_bench_scan.bin, size 48748 (2 log(s))
  - DOCs/analyses/bench/2026-09-14/debug_260914-113610.log: NOMEAS (NOT_REACHED; declared, no SIGNOFF instance)
  - DOCs/analyses/bench/2026-09-14/debug_260914-114703.log: PASS (2 of 2 counted PASS instances)
  - DOCs/analyses/bench/2026-09-14/debug_260914-114703.log:1373 motor LEFT crit STARTS_ILLEGAL measured 0 lo 0 hi 0 units COUNT n 9 printed PASS -> PASS
  - DOCs/analyses/bench/2026-09-14/debug_260914-114703.log:1394 motor RIGHT crit STARTS_ILLEGAL measured 0 lo 0 hi 0 units COUNT n 9 printed PASS -> PASS
- **R8-SCAN-ZXS** (row 8, bin SCAN) -- **PASS** -- crit ZXS, lo 0, hi 50, units MV_X10, min_inst 5, counts only LEFT:ZXS_I,LEFT:ZXS_V,RIGHT:ZXS_I,RIGHT:ZXS_V,RIGHT:ZXS_U; manifest status SIGNED_OFF (ref V1:DOCs/analyses/bench/2026-09-14/debug_260914-114703.log:1376;V1:DOCs/analyses/bench/2026-09-14/debug_260914-114703.log:1378;V1:DOCs/analyses/bench/2026-09-14/debug_260914-114703.log:1397;V1:DOCs/analyses/bench/2026-09-14/debug_260914-114703.log:1398;V1:DOCs/analyses/bench/2026-09-14/debug_260914-114703.log:1399)
  - speaking build: banner BS-BANNER, src_rev 9, fmt 9, bin test_bench_scan.bin, size 48748 (2 log(s))
  - DOCs/analyses/bench/2026-09-14/debug_260914-113610.log: NOMEAS (NOT_REACHED; declared, no SIGNOFF instance)
  - DOCs/analyses/bench/2026-09-14/debug_260914-114703.log: PASS (5 of 5 counted PASS instances)
  - counted channels that passed: LEFT:ZXS_I, LEFT:ZXS_V, RIGHT:ZXS_I, RIGHT:ZXS_U, RIGHT:ZXS_V
  - DOCs/analyses/bench/2026-09-14/debug_260914-114703.log:1376 motor LEFT crit ZXS_I measured 16 lo 0 hi 50 units MV_X10 n 5 printed PASS -> PASS
  - DOCs/analyses/bench/2026-09-14/debug_260914-114703.log:1377 motor LEFT crit ZXS_U measured 17 lo 0 hi 50 units MV_X10 n 5 printed PASS -> PASS [outside count_filter]
  - DOCs/analyses/bench/2026-09-14/debug_260914-114703.log:1378 motor LEFT crit ZXS_V measured 12 lo 0 hi 50 units MV_X10 n 5 printed PASS -> PASS
  - DOCs/analyses/bench/2026-09-14/debug_260914-114703.log:1379 motor LEFT crit ZXS_W measured 7 lo 0 hi 50 units MV_X10 n 5 printed PASS -> PASS [outside count_filter]
  - DOCs/analyses/bench/2026-09-14/debug_260914-114703.log:1397 motor RIGHT crit ZXS_I measured 14 lo 0 hi 50 units MV_X10 n 5 printed PASS -> PASS
  - DOCs/analyses/bench/2026-09-14/debug_260914-114703.log:1398 motor RIGHT crit ZXS_U measured 16 lo 0 hi 50 units MV_X10 n 5 printed PASS -> PASS
  - DOCs/analyses/bench/2026-09-14/debug_260914-114703.log:1399 motor RIGHT crit ZXS_V measured 13 lo 0 hi 50 units MV_X10 n 5 printed PASS -> PASS
  - DOCs/analyses/bench/2026-09-14/debug_260914-114703.log:1400 motor RIGHT crit ZXS_W measured 18 lo 0 hi 50 units MV_X10 n 5 printed PASS -> PASS [outside count_filter]
- **R8-T0-ZXS** (row 8, bin T0) -- **PASS** -- crit ZXS, lo 0, hi 50, units MV_X10, min_inst 3, counts only RIGHT:ZXS_I,RIGHT:ZXS_U,RIGHT:ZXS_V; manifest status SIGNED_OFF (ref V1:DOCs/analyses/bench/2026-09-14/debug_260914-114636.log:184;V1:DOCs/analyses/bench/2026-09-14/debug_260914-114636.log:185;V1:DOCs/analyses/bench/2026-09-14/debug_260914-114636.log:186)
  - speaking build: banner T0, src_rev NA, fmt NA, bin test_bench_t0.bin, size 30455 (1 log(s))
  - DOCs/analyses/bench/2026-09-14/debug_260914-114636.log: PASS (3 of 3 counted PASS instances)
  - counted channels that passed: RIGHT:ZXS_I, RIGHT:ZXS_U, RIGHT:ZXS_V
  - DOCs/analyses/bench/2026-09-14/debug_260914-114636.log:184 motor RIGHT crit ZXS_I measured 22 lo 0 hi 50 units MV_X10 n 5 printed PASS -> PASS
  - DOCs/analyses/bench/2026-09-14/debug_260914-114636.log:185 motor RIGHT crit ZXS_U measured 14 lo 0 hi 50 units MV_X10 n 5 printed PASS -> PASS
  - DOCs/analyses/bench/2026-09-14/debug_260914-114636.log:186 motor RIGHT crit ZXS_V measured 10 lo 0 hi 50 units MV_X10 n 5 printed PASS -> PASS
  - DOCs/analyses/bench/2026-09-14/debug_260914-114636.log:187 motor RIGHT crit ZXS_W measured 13 lo 0 hi 50 units MV_X10 n 5 printed PASS -> PASS [outside count_filter]
- **R9-SCAN-HALFLEG** (row 9, bin SCAN) -- **PASS** -- crit CLIFF_PROBED, lo TRUE, hi TRUE, units BOOL, min_inst 2; manifest status SIGNED_OFF (ref V1:DOCs/analyses/bench/2026-09-14/debug_260914-114703.log:1380;V1:DOCs/analyses/bench/2026-09-14/debug_260914-114703.log:1381;V1:DOCs/analyses/bench/2026-09-14/debug_260914-114703.log:1401;V1:DOCs/analyses/bench/2026-09-14/debug_260914-114703.log:1402)
  - speaking build: banner BS-BANNER, src_rev 9, fmt 9, bin test_bench_scan.bin, size 48748 (2 log(s))
  - DOCs/analyses/bench/2026-09-14/debug_260914-113610.log: NOMEAS (NOT_REACHED; declared, no SIGNOFF instance)
  - DOCs/analyses/bench/2026-09-14/debug_260914-114703.log: PASS (4 of 2 counted PASS instances)
  - DOCs/analyses/bench/2026-09-14/debug_260914-114703.log:1380 motor LEFT crit CLIFF_PROBED measured TRUE lo TRUE hi TRUE units BOOL n 1 printed PASS -> PASS
  - DOCs/analyses/bench/2026-09-14/debug_260914-114703.log:1381 motor LEFT crit CLIFF_PROBED measured TRUE lo TRUE hi TRUE units BOOL n 1 printed PASS -> PASS
  - DOCs/analyses/bench/2026-09-14/debug_260914-114703.log:1401 motor RIGHT crit CLIFF_PROBED measured TRUE lo TRUE hi TRUE units BOOL n 1 printed PASS -> PASS
  - DOCs/analyses/bench/2026-09-14/debug_260914-114703.log:1402 motor RIGHT crit CLIFF_PROBED measured TRUE lo TRUE hi TRUE units BOOL n 1 printed PASS -> PASS
- **R9-SCAN-OWNZERO** (row 9, bin SCAN) -- **PASS** -- crit PTS_NO_OWN_ZERO, lo 0, hi 0, units COUNT, min_inst 4; manifest status SIGNED_OFF (ref V1:DOCs/analyses/bench/2026-09-14/debug_260914-114703.log:1382;V1:DOCs/analyses/bench/2026-09-14/debug_260914-114703.log:1383;V1:DOCs/analyses/bench/2026-09-14/debug_260914-114703.log:1384;V1:DOCs/analyses/bench/2026-09-14/debug_260914-114703.log:1385;V1:DOCs/analyses/bench/2026-09-14/debug_260914-114703.log:1403;V1:DOCs/analyses/bench/2026-09-14/debug_260914-114703.log:1404;V1:DOCs/analyses/bench/2026-09-14/debug_260914-114703.log:1405;V1:DOCs/analyses/bench/2026-09-14/debug_260914-114703.log:1406)
  - speaking build: banner BS-BANNER, src_rev 9, fmt 9, bin test_bench_scan.bin, size 48748 (2 log(s))
  - DOCs/analyses/bench/2026-09-14/debug_260914-113610.log: NOMEAS (NOT_REACHED; declared, no SIGNOFF instance)
  - DOCs/analyses/bench/2026-09-14/debug_260914-114703.log: PASS (8 of 4 counted PASS instances)
  - DOCs/analyses/bench/2026-09-14/debug_260914-114703.log:1382 motor LEFT crit PTS_NO_OWN_ZERO measured 0 lo 0 hi 0 units COUNT n 13 printed PASS -> PASS
  - DOCs/analyses/bench/2026-09-14/debug_260914-114703.log:1383 motor LEFT crit PTS_NO_OWN_ZERO measured 0 lo 0 hi 0 units COUNT n 8 printed PASS -> PASS
  - DOCs/analyses/bench/2026-09-14/debug_260914-114703.log:1384 motor LEFT crit PTS_NO_OWN_ZERO measured 0 lo 0 hi 0 units COUNT n 13 printed PASS -> PASS
  - DOCs/analyses/bench/2026-09-14/debug_260914-114703.log:1385 motor LEFT crit PTS_NO_OWN_ZERO measured 0 lo 0 hi 0 units COUNT n 8 printed PASS -> PASS
  - DOCs/analyses/bench/2026-09-14/debug_260914-114703.log:1403 motor RIGHT crit PTS_NO_OWN_ZERO measured 0 lo 0 hi 0 units COUNT n 13 printed PASS -> PASS
  - DOCs/analyses/bench/2026-09-14/debug_260914-114703.log:1404 motor RIGHT crit PTS_NO_OWN_ZERO measured 0 lo 0 hi 0 units COUNT n 8 printed PASS -> PASS
  - DOCs/analyses/bench/2026-09-14/debug_260914-114703.log:1405 motor RIGHT crit PTS_NO_OWN_ZERO measured 0 lo 0 hi 0 units COUNT n 12 printed PASS -> PASS
  - DOCs/analyses/bench/2026-09-14/debug_260914-114703.log:1406 motor RIGHT crit PTS_NO_OWN_ZERO measured 0 lo 0 hi 0 units COUNT n 8 printed PASS -> PASS
- **R9-SCAN-PAIR2** (row 9, bin SCAN) -- **PASS** -- crit NET_RATIO_ONLY, lo TRUE, hi TRUE, units BOOL, min_inst 2; manifest status SIGNED_OFF (ref V1:DOCs/analyses/bench/2026-09-14/debug_260914-114703.log:1386;V1:DOCs/analyses/bench/2026-09-14/debug_260914-114703.log:1407)
  - speaking build: banner BS-BANNER, src_rev 9, fmt 9, bin test_bench_scan.bin, size 48748 (2 log(s))
  - DOCs/analyses/bench/2026-09-14/debug_260914-113610.log: NOMEAS (NOT_REACHED; declared, no SIGNOFF instance)
  - DOCs/analyses/bench/2026-09-14/debug_260914-114703.log: PASS (2 of 2 counted PASS instances)
  - DOCs/analyses/bench/2026-09-14/debug_260914-114703.log:1386 motor LEFT crit NET_RATIO_ONLY measured TRUE lo TRUE hi TRUE units BOOL n 1 printed PASS -> PASS
  - DOCs/analyses/bench/2026-09-14/debug_260914-114703.log:1407 motor RIGHT crit NET_RATIO_ONLY measured TRUE lo TRUE hi TRUE units BOOL n 1 printed PASS -> PASS
- **R10-SCAN-RSTALONE** (row 10, bin SCAN) -- **PASS** -- crit RESET_ALONE_CLEARS, lo TRUE, hi TRUE, units BOOL, min_inst 1; manifest status SIGNED_OFF (ref V1:DOCs/analyses/bench/2026-09-14/debug_260914-114703.log:1387;V1:DOCs/analyses/bench/2026-09-14/debug_260914-114703.log:1408)
  - speaking build: banner BS-BANNER, src_rev 9, fmt 9, bin test_bench_scan.bin, size 48748 (2 log(s))
  - DOCs/analyses/bench/2026-09-14/debug_260914-113610.log: NOMEAS (NOT_REACHED; declared, no SIGNOFF instance)
  - DOCs/analyses/bench/2026-09-14/debug_260914-114703.log: PASS (2 of 1 counted PASS instances)
  - DOCs/analyses/bench/2026-09-14/debug_260914-114703.log:1387 motor LEFT crit RESET_ALONE_CLEARS measured TRUE lo TRUE hi TRUE units BOOL n 1 printed PASS -> PASS
  - DOCs/analyses/bench/2026-09-14/debug_260914-114703.log:1408 motor RIGHT crit RESET_ALONE_CLEARS measured TRUE lo TRUE hi TRUE units BOOL n 1 printed PASS -> PASS
- **R10-T0-STOPREADY** (row 10, bin T0) -- **PASS** -- crit STOP_NOT_READY, lo TRUE, hi TRUE, units BOOL, min_inst 1; manifest status SIGNED_OFF (ref V1:DOCs/analyses/bench/2026-09-14/debug_260914-114636.log:1004)
  - speaking build: banner T0, src_rev NA, fmt NA, bin test_bench_t0.bin, size 30455 (1 log(s))
  - DOCs/analyses/bench/2026-09-14/debug_260914-114636.log: PASS (1 of 1 counted PASS instances)
  - DOCs/analyses/bench/2026-09-14/debug_260914-114636.log:1004 motor NONE crit STOP_NOT_READY measured TRUE lo TRUE hi TRUE units BOOL n 1 printed PASS -> PASS
- **R10-CHAR-STEERSTART** (row 10, bin CHAR) -- **PASS** -- crit STEER_START_COG, lo TRUE, hi TRUE, units BOOL, min_inst 1; manifest status SIGNED_OFF (ref V1:DOCs/analyses/bench/2026-09-14/debug_260914-115953.log:512)
  - speaking build: banner BC-BANNER, src_rev 5, fmt 5, bin test_bench_char.bin, size 41233 (1 log(s))
  - DOCs/analyses/bench/2026-09-14/debug_260914-115953.log: PASS (1 of 1 counted PASS instances)
  - DOCs/analyses/bench/2026-09-14/debug_260914-115953.log:512 motor NONE crit STEER_START_COG measured TRUE lo TRUE hi TRUE units BOOL n 1 printed PASS -> PASS
- **R10-CHAR-STEERLIVE** (row 10, bin CHAR) -- **PASS** -- crit WHEEL_TICKS, lo 6, hi NA, units TICKS, min_inst 2; manifest status SIGNED_OFF (ref V1:DOCs/analyses/bench/2026-09-14/debug_260914-115953.log:513;V1:DOCs/analyses/bench/2026-09-14/debug_260914-115953.log:514)
  - speaking build: banner BC-BANNER, src_rev 5, fmt 5, bin test_bench_char.bin, size 41233 (1 log(s))
  - DOCs/analyses/bench/2026-09-14/debug_260914-115953.log: PASS (2 of 2 counted PASS instances)
  - DOCs/analyses/bench/2026-09-14/debug_260914-115953.log:513 motor LEFT crit WHEEL_TICKS measured 13 lo 6 hi NA units TICKS n 1 printed PASS -> PASS
  - DOCs/analyses/bench/2026-09-14/debug_260914-115953.log:514 motor RIGHT crit WHEEL_TICKS measured 13 lo 6 hi NA units TICKS n 1 printed PASS -> PASS
- **R10-CHAR-STEERFAIL** (row 10, bin CHAR) -- **FAIL** (BINARY_FAIL) -- crit RET_NEG_NOLEAK, lo TRUE, hi TRUE, units BOOL, min_inst 1; manifest status FAILED (ref V1:DOCs/analyses/bench/2026-09-14/debug_260914-115953.log:511)
  - speaking build: banner BC-BANNER, src_rev 5, fmt 5, bin test_bench_char.bin, size 41233 (1 log(s))
  - DOCs/analyses/bench/2026-09-14/debug_260914-115953.log: FAIL (BINARY_FAIL)
  - DOCs/analyses/bench/2026-09-14/debug_260914-115953.log:511 motor NONE crit RET_NEG_NOLEAK measured FALSE lo TRUE hi TRUE units BOOL n 1 printed FAIL -> FAIL
- **R10-HOST-PL9** (row 10, bin HOST) -- **PASS** -- crit GAPINMS_ABSENT, lo 0, hi 0, units COUNT, min_inst 1; manifest status SIGNED_OFF (ref V1:STATIC:src/isp_bldc_motor.spin2)
  - measured 0 occurrences, lo 0, hi 0, COUNT
  - src/isp_bldc_motor.spin2: identifier gapInMS absent (case-insensitive)
- **R11-SCAN-NOSTALL** (row 11, bin SCAN) -- **PASS** -- crit ENDED_BY_COG0, lo TRUE, hi TRUE, units BOOL, min_inst 1; manifest status SIGNED_OFF (ref V1:DOCs/analyses/bench/2026-09-14/debug_260914-114703.log:1410)
  - speaking build: banner BS-BANNER, src_rev 9, fmt 9, bin test_bench_scan.bin, size 48748 (2 log(s))
  - DOCs/analyses/bench/2026-09-14/debug_260914-113610.log: NOMEAS (NOT_REACHED; declared, no SIGNOFF instance)
  - DOCs/analyses/bench/2026-09-14/debug_260914-114703.log: PASS (1 of 1 counted PASS instances)
  - DOCs/analyses/bench/2026-09-14/debug_260914-114703.log:1410 motor NONE crit ENDED_BY_COG0 measured TRUE lo TRUE hi TRUE units BOOL n 1 printed PASS -> PASS
- **R11-WDT-FIRES** (row 11, bin SCANWD) -- **PASS** -- crit STALL_MS, lo 4000, hi 4500, units MS, min_inst 1; manifest status SIGNED_OFF (ref V1:DOCs/analyses/bench/2026-09-14/debug_260914-114523.log:77)
  - speaking build: banner BS-BANNER, src_rev 9, fmt 9, bin test_bench_scan.bin, size 48324 (1 log(s))
  - DOCs/analyses/bench/2026-09-14/debug_260914-114523.log: PASS (1 of 1 counted PASS instances)
  - DOCs/analyses/bench/2026-09-14/debug_260914-114523.log:77 motor NONE crit STALL_MS measured 4_000 lo 4_000 hi 4_500 units MS n 1 printed PASS -> PASS
- **R11-WDT-CKPT** (row 11, bin SCANWD) -- **PASS** -- crit CKPT_IS_SELFTEST, lo TRUE, hi TRUE, units BOOL, min_inst 1; manifest status SIGNED_OFF (ref V1:DOCs/analyses/bench/2026-09-14/debug_260914-114523.log:78)
  - speaking build: banner BS-BANNER, src_rev 9, fmt 9, bin test_bench_scan.bin, size 48324 (1 log(s))
  - DOCs/analyses/bench/2026-09-14/debug_260914-114523.log: PASS (1 of 1 counted PASS instances)
  - DOCs/analyses/bench/2026-09-14/debug_260914-114523.log:78 motor NONE crit CKPT_IS_SELFTEST measured TRUE lo TRUE hi TRUE units BOOL n 1 printed PASS -> PASS
- **R11-WDT-STOPPED** (row 11, bin SCANWD) -- **PASS** -- crit WHEELS_STOPPED, lo TRUE, hi TRUE, units BOOL, min_inst 1; manifest status SIGNED_OFF (ref V1:DOCs/analyses/bench/2026-09-14/debug_260914-114523.log:79)
  - speaking build: banner BS-BANNER, src_rev 9, fmt 9, bin test_bench_scan.bin, size 48324 (1 log(s))
  - DOCs/analyses/bench/2026-09-14/debug_260914-114523.log: PASS (1 of 1 counted PASS instances)
  - DOCs/analyses/bench/2026-09-14/debug_260914-114523.log:79 motor NONE crit WHEELS_STOPPED measured TRUE lo TRUE hi TRUE units BOOL n 1 printed PASS -> PASS
- **R11-WDT-STACK** (row 11, bin SCANWD) -- **PASS** -- crit STACK_OK, lo TRUE, hi TRUE, units BOOL, min_inst 1; manifest status SIGNED_OFF (ref V1:DOCs/analyses/bench/2026-09-14/debug_260914-114523.log:80)
  - speaking build: banner BS-BANNER, src_rev 9, fmt 9, bin test_bench_scan.bin, size 48324 (1 log(s))
  - DOCs/analyses/bench/2026-09-14/debug_260914-114523.log: PASS (1 of 1 counted PASS instances)
  - DOCs/analyses/bench/2026-09-14/debug_260914-114523.log:80 motor NONE crit STACK_OK measured TRUE lo TRUE hi TRUE units BOOL n 1 printed PASS -> PASS
- **R11-HOST-WDTEND** (row 11, bin HOST) -- **PASS** -- crit FLAG_AND_END, lo TRUE, hi TRUE, units BOOL, min_inst 1; manifest status SIGNED_OFF (ref V1:DOCs/analyses/bench/2026-09-14/debug_260914-114523.log:22;V1:DOCs/analyses/bench/2026-09-14/debug_260914-114523.log:77;V1:DOCs/analyses/bench/2026-09-14/debug_260914-114523.log:78;V1:DOCs/analyses/bench/2026-09-14/debug_260914-114523.log:79;V1:DOCs/analyses/bench/2026-09-14/debug_260914-114523.log:80;V1:DOCs/analyses/bench/2026-09-14/debug_260914-114523.log:82)
  - speaking build: banner BS-BANNER, src_rev 9, fmt 9, bin test_bench_scan.bin, size 48324
  - DOCs/analyses/bench/2026-09-14/debug_260914-114523.log: PASS
  - measured TRUE, lo TRUE, hi TRUE, BOOL
  - DOCs/analyses/bench/2026-09-14/debug_260914-114523.log:22 BS-BUILD wd_selftest TRUE
  - DOCs/analyses/bench/2026-09-14/debug_260914-114523.log:77 R11-WDT record from a non-zero cog
  - DOCs/analyses/bench/2026-09-14/debug_260914-114523.log:78 R11-WDT record from a non-zero cog
  - DOCs/analyses/bench/2026-09-14/debug_260914-114523.log:79 R11-WDT record from a non-zero cog
  - DOCs/analyses/bench/2026-09-14/debug_260914-114523.log:80 R11-WDT record from a non-zero cog
  - DOCs/analyses/bench/2026-09-14/debug_260914-114523.log:82 DEBUG_END_SESSION after them
- **R12-SCAN-ALIVE** (row 12, bin SCAN) -- **PASS** -- crit STARTS_NOT_ALIVE, lo 0, hi 0, units COUNT, min_inst 2; manifest status SIGNED_OFF (ref V1:DOCs/analyses/bench/2026-09-14/debug_260914-114703.log:1374;V1:DOCs/analyses/bench/2026-09-14/debug_260914-114703.log:1395)
  - speaking build: banner BS-BANNER, src_rev 9, fmt 9, bin test_bench_scan.bin, size 48748 (2 log(s))
  - DOCs/analyses/bench/2026-09-14/debug_260914-113610.log: NOMEAS (NOT_REACHED; declared, no SIGNOFF instance)
  - DOCs/analyses/bench/2026-09-14/debug_260914-114703.log: PASS (2 of 2 counted PASS instances)
  - DOCs/analyses/bench/2026-09-14/debug_260914-114703.log:1374 motor LEFT crit STARTS_NOT_ALIVE measured 0 lo 0 hi 0 units COUNT n 8 printed PASS -> PASS
  - DOCs/analyses/bench/2026-09-14/debug_260914-114703.log:1395 motor RIGHT crit STARTS_NOT_ALIVE measured 0 lo 0 hi 0 units COUNT n 8 printed PASS -> PASS
- **R12-SCAN-RATE** (row 12, bin SCAN) -- **PASS** -- crit RATE_IN_BAND, lo TRUE, hi TRUE, units BOOL, min_inst 2; manifest status SIGNED_OFF (ref V1:DOCs/analyses/bench/2026-09-14/debug_260914-114703.log:1375;V1:DOCs/analyses/bench/2026-09-14/debug_260914-114703.log:1396)
  - speaking build: banner BS-BANNER, src_rev 9, fmt 9, bin test_bench_scan.bin, size 48748 (2 log(s))
  - DOCs/analyses/bench/2026-09-14/debug_260914-113610.log: NOMEAS (NOT_REACHED; declared, no SIGNOFF instance)
  - DOCs/analyses/bench/2026-09-14/debug_260914-114703.log: PASS (2 of 2 counted PASS instances)
  - DOCs/analyses/bench/2026-09-14/debug_260914-114703.log:1375 motor LEFT crit RATE_IN_BAND measured TRUE lo TRUE hi TRUE units BOOL n 1 printed PASS -> PASS
  - DOCs/analyses/bench/2026-09-14/debug_260914-114703.log:1396 motor RIGHT crit RATE_IN_BAND measured TRUE lo TRUE hi TRUE units BOOL n 1 printed PASS -> PASS
- **R13-CHAR-BRAKESTART** (row 13, bin CHAR) -- **NOMEAS** (BIN_NOMEAS) -- crit BRAKE_START_MOVE, lo TRUE, hi TRUE, units BOOL, min_inst 4; manifest status OWED
  - speaking build: banner BC-BANNER, src_rev 5, fmt 5, bin test_bench_char.bin, size 41233 (1 log(s))
  - DOCs/analyses/bench/2026-09-14/debug_260914-115953.log: NOMEAS (BIN_NOMEAS)
  - DOCs/analyses/bench/2026-09-14/debug_260914-115953.log:515 motor LEFT crit BRAKE_START_MOVE measured NA lo TRUE hi TRUE units BOOL n 0 printed NOMEAS -> NOMEAS (BIN_NOMEAS)
  - DOCs/analyses/bench/2026-09-14/debug_260914-115953.log:516 motor LEFT crit BRAKE_START_MOVE measured NA lo TRUE hi TRUE units BOOL n 0 printed NOMEAS -> NOMEAS (BIN_NOMEAS)
  - DOCs/analyses/bench/2026-09-14/debug_260914-115953.log:517 motor RIGHT crit BRAKE_START_MOVE measured NA lo TRUE hi TRUE units BOOL n 0 printed NOMEAS -> NOMEAS (BIN_NOMEAS)
  - DOCs/analyses/bench/2026-09-14/debug_260914-115953.log:518 motor RIGHT crit BRAKE_START_MOVE measured NA lo TRUE hi TRUE units BOOL n 0 printed NOMEAS -> NOMEAS (BIN_NOMEAS)

## NOT_BUILT

- (none)

## Superseded logs

- (none)

## Unmanifested cells

- (none)

## Parse errors

- (none)

## Deferred cells (not owed to this visit)

- R2-DETECT-OVERLAP (row 2): overlapping-group cells P40_P55 and NO_USE_P24_P39, run only in a session with the motors unplugged (design J.2 ruling)

## DETDIFF change list

### `DOCs/analyses/bench/2026-09-14/debug_260914-114608.log` -- PASS, measured 0

- Never compared (design C.2): BD-LIB brackets, BD-REP/BD-RUN/BD-CAL timing, BD-NOTE text, BD-PH2; BD-CFG and BD-MAP appear under INFO only.
- **VOID** (0)
- **Unpredicted changes** (0)
- **Predicted changes that did not occur** (0)
- **Blocking PASS** (0)
- **NOT_COMPARED (the visit log marks the cell SKIPPED)** (12)
  - sw 1 NO_USE_P24_P39: NOT_COMPARED -- the visit log marks it SKIPPED GATE_OVERLAP (DOCs/analyses/bench/2026-09-14/debug_260914-114608.log:262); prediction line(s) not compared: modal REVB -> NODET (NOT_COMPARED_GATE_OVERLAP), vb 32 -> 0 (NOT_COMPARED_GATE_OVERLAP), vn 0 -> 32 (NOT_COMPARED_GATE_OVERLAP)
  - sw 1 P40_P55: NOT_COMPARED -- the visit log marks it SKIPPED GATE_OVERLAP (DOCs/analyses/bench/2026-09-14/debug_260914-114608.log:216); prediction line(s) not compared: libvrd REVB -> NODET (NOT_COMPARED_GATE_OVERLAP), modal REVB -> NODET (NOT_COMPARED_GATE_OVERLAP), vb 32 -> 0 (NOT_COMPARED_GATE_OVERLAP), vn 0 -> 32 (NOT_COMPARED_GATE_OVERLAP)
  - sw 2 NO_USE_P24_P39: NOT_COMPARED -- the visit log marks it SKIPPED GATE_OVERLAP (DOCs/analyses/bench/2026-09-14/debug_260914-114608.log:447); prediction line(s) not compared: modal REVB -> NODET (NOT_COMPARED_GATE_OVERLAP), vb 32 -> 0 (NOT_COMPARED_GATE_OVERLAP), vn 0 -> 32 (NOT_COMPARED_GATE_OVERLAP)
  - sw 2 P40_P55: NOT_COMPARED -- the visit log marks it SKIPPED GATE_OVERLAP (DOCs/analyses/bench/2026-09-14/debug_260914-114608.log:401); prediction line(s) not compared: libvrd REVB -> NODET (NOT_COMPARED_GATE_OVERLAP), modal REVB -> NODET (NOT_COMPARED_GATE_OVERLAP), vb 32 -> 0 (NOT_COMPARED_GATE_OVERLAP), vn 0 -> 32 (NOT_COMPARED_GATE_OVERLAP)
  - sw 4 NO_USE_P24_P39: NOT_COMPARED -- the visit log marks it SKIPPED GATE_OVERLAP (DOCs/analyses/bench/2026-09-14/debug_260914-114608.log:674); prediction line(s) not compared: modal REVB -> NODET (NOT_COMPARED_GATE_OVERLAP), vb 32 -> 0 (NOT_COMPARED_GATE_OVERLAP), vn 0 -> 32 (NOT_COMPARED_GATE_OVERLAP)
  - sw 4 P40_P55: NOT_COMPARED -- the visit log marks it SKIPPED GATE_OVERLAP (DOCs/analyses/bench/2026-09-14/debug_260914-114608.log:628); prediction line(s) not compared: libvrd REVB -> NODET (NOT_COMPARED_GATE_OVERLAP), modal REVB -> NODET (NOT_COMPARED_GATE_OVERLAP), vb 32 -> 0 (NOT_COMPARED_GATE_OVERLAP), vn 0 -> 32 (NOT_COMPARED_GATE_OVERLAP)
  - sw 5 NO_USE_P24_P39: NOT_COMPARED -- the visit log marks it SKIPPED GATE_OVERLAP (DOCs/analyses/bench/2026-09-14/debug_260914-114608.log:858); prediction line(s) not compared: modal REVB -> NODET (NOT_COMPARED_GATE_OVERLAP), vb 32 -> 0 (NOT_COMPARED_GATE_OVERLAP), vn 0 -> 32 (NOT_COMPARED_GATE_OVERLAP)
  - sw 5 P40_P55: NOT_COMPARED -- the visit log marks it SKIPPED GATE_OVERLAP (DOCs/analyses/bench/2026-09-14/debug_260914-114608.log:812); prediction line(s) not compared: libvrd REVB -> NODET (NOT_COMPARED_GATE_OVERLAP), modal REVB -> NODET (NOT_COMPARED_GATE_OVERLAP), vb 32 -> 0 (NOT_COMPARED_GATE_OVERLAP), vn 0 -> 32 (NOT_COMPARED_GATE_OVERLAP)
  - sw 7 NO_USE_P24_P39: NOT_COMPARED -- the visit log marks it SKIPPED GATE_OVERLAP (DOCs/analyses/bench/2026-09-14/debug_260914-114608.log:1082); prediction line(s) not compared: modal REVB -> NODET (NOT_COMPARED_GATE_OVERLAP), vb 32 -> 0 (NOT_COMPARED_GATE_OVERLAP), vn 0 -> 32 (NOT_COMPARED_GATE_OVERLAP)
  - sw 7 P40_P55: NOT_COMPARED -- the visit log marks it SKIPPED GATE_OVERLAP (DOCs/analyses/bench/2026-09-14/debug_260914-114608.log:1036); prediction line(s) not compared: libvrd REVB -> NODET (NOT_COMPARED_GATE_OVERLAP), modal REVB -> NODET (NOT_COMPARED_GATE_OVERLAP), vb 32 -> 0 (NOT_COMPARED_GATE_OVERLAP), vn 0 -> 32 (NOT_COMPARED_GATE_OVERLAP)
  - sw 8 NO_USE_P24_P39: NOT_COMPARED -- the visit log marks it SKIPPED GATE_OVERLAP (DOCs/analyses/bench/2026-09-14/debug_260914-114608.log:1266); prediction line(s) not compared: modal REVB -> NODET (NOT_COMPARED_GATE_OVERLAP), vb 32 -> 0 (NOT_COMPARED_GATE_OVERLAP), vn 0 -> 32 (NOT_COMPARED_GATE_OVERLAP)
  - sw 8 P40_P55: NOT_COMPARED -- the visit log marks it SKIPPED GATE_OVERLAP (DOCs/analyses/bench/2026-09-14/debug_260914-114608.log:1220); prediction line(s) not compared: libvrd REVB -> NODET (NOT_COMPARED_GATE_OVERLAP), modal REVB -> NODET (NOT_COMPARED_GATE_OVERLAP), vb 32 -> 0 (NOT_COMPARED_GATE_OVERLAP), vn 0 -> 32 (NOT_COMPARED_GATE_OVERLAP)
- **Excluded by design (sweeps 3 and 6)** (2)
  - sw 3 P0_P15: excluded -- running-driver cell, void by design (design C.2); 4 EXCLUDED_VOID prediction line(s)
  - sw 6 P16_P31: excluded -- running-driver cell, void by design (design C.2); 4 EXCLUDED_VOID prediction line(s)
- **Predicted changes that occurred** (14)
  - sw 4 P0_P15 sum_min: 0 -> 500 as predicted (500, COMPARED, DERIVED_3505) -- baseline DOCs/analyses/bench/2026-09-11/debug_260911-210229.log:711, visit DOCs/analyses/bench/2026-09-14/debug_260914-114608.log:537
  - sw 4 P0_P15 sum_max: 0 -> 500 as predicted (500, COMPARED, DERIVED_3505) -- baseline DOCs/analyses/bench/2026-09-11/debug_260911-210229.log:711, visit DOCs/analyses/bench/2026-09-14/debug_260914-114608.log:537
  - sw 4 P0_P15 sum_mean: 0 -> 500 as predicted (500, COMPARED, DERIVED_3505) -- baseline DOCs/analyses/bench/2026-09-11/debug_260911-210229.log:711, visit DOCs/analyses/bench/2026-09-14/debug_260914-114608.log:537
  - sw 4 P0_P15 modal: REVA -> NODET as predicted (NODET, COMPARED, DERIVED_3505) -- baseline DOCs/analyses/bench/2026-09-11/debug_260911-210229.log:711, visit DOCs/analyses/bench/2026-09-14/debug_260914-114608.log:537
  - sw 4 P0_P15 libvrd: REVA -> NODET as predicted (NODET, COMPARED, DERIVED_3505) -- baseline DOCs/analyses/bench/2026-09-11/debug_260911-210229.log:711, visit DOCs/analyses/bench/2026-09-14/debug_260914-114608.log:537
  - sw 4 P0_P15 va: 32 -> 0 as predicted (0, COMPARED, DERIVED_P2D) -- baseline DOCs/analyses/bench/2026-09-11/debug_260911-210229.log:711, visit DOCs/analyses/bench/2026-09-14/debug_260914-114608.log:537
  - sw 4 P0_P15 vn: 0 -> 32 as predicted (32, COMPARED, DERIVED_P2D) -- baseline DOCs/analyses/bench/2026-09-11/debug_260911-210229.log:711, visit DOCs/analyses/bench/2026-09-14/debug_260914-114608.log:537
  - sw 7 P16_P31 sum_min: 0 -> 93 as predicted (93..104, COMPARED, DERIVED_3505) -- baseline DOCs/analyses/bench/2026-09-11/debug_260911-210229.log:1338, visit DOCs/analyses/bench/2026-09-14/debug_260914-114608.log:990
  - sw 7 P16_P31 sum_max: 0 -> 97 as predicted (93..104, COMPARED, DERIVED_3505) -- baseline DOCs/analyses/bench/2026-09-11/debug_260911-210229.log:1338, visit DOCs/analyses/bench/2026-09-14/debug_260914-114608.log:990
  - sw 7 P16_P31 sum_mean: 0 -> 94 as predicted (93..104, COMPARED, DERIVED_3505) -- baseline DOCs/analyses/bench/2026-09-11/debug_260911-210229.log:1338, visit DOCs/analyses/bench/2026-09-14/debug_260914-114608.log:990
  - sw 7 P16_P31 modal: REVA -> REVB as predicted (REVB, COMPARED, DERIVED_3505) -- baseline DOCs/analyses/bench/2026-09-11/debug_260911-210229.log:1338, visit DOCs/analyses/bench/2026-09-14/debug_260914-114608.log:990
  - sw 7 P16_P31 libvrd: REVA -> REVB as predicted (REVB, COMPARED, DERIVED_3505) -- baseline DOCs/analyses/bench/2026-09-11/debug_260911-210229.log:1338, visit DOCs/analyses/bench/2026-09-14/debug_260914-114608.log:990
  - sw 7 P16_P31 va: 32 -> 0 as predicted (0, COMPARED, DERIVED_P2D) -- baseline DOCs/analyses/bench/2026-09-11/debug_260911-210229.log:1338, visit DOCs/analyses/bench/2026-09-14/debug_260914-114608.log:990
  - sw 7 P16_P31 vb: 0 -> 32 as predicted (32, COMPARED, DERIVED_P2D) -- baseline DOCs/analyses/bench/2026-09-11/debug_260911-210229.log:1338, visit DOCs/analyses/bench/2026-09-14/debug_260914-114608.log:990
- **INFO (BD-CFG, BD-MAP; not in the verdict)** (12)
  - BD-CFG left_base: 0 -> 32 -- baseline DOCs/analyses/bench/2026-09-11/debug_260911-210229.log:20, visit DOCs/analyses/bench/2026-09-14/debug_260914-114608.log:20
  - BD-MAP NO_USE_P24_P39 guard: ABSENT -> GATE_OVERLAP -- baseline DOCs/analyses/bench/2026-09-11/debug_260911-210229.log:33, visit DOCs/analyses/bench/2026-09-14/debug_260914-114608.log:33
  - BD-MAP NO_USE_P24_P39 ovl: P16_P31+12_PWM_W_L -> RIGHT+12_PWM_W_L -- baseline DOCs/analyses/bench/2026-09-11/debug_260911-210229.log:33, visit DOCs/analyses/bench/2026-09-14/debug_260914-114608.log:33
  - BD-MAP P0_P15 guard: ABSENT -> NONE -- baseline DOCs/analyses/bench/2026-09-11/debug_260911-210229.log:30, visit DOCs/analyses/bench/2026-09-14/debug_260914-114608.log:30
  - BD-MAP P0_P15 ovl: SELF -> NONE -- baseline DOCs/analyses/bench/2026-09-11/debug_260911-210229.log:30, visit DOCs/analyses/bench/2026-09-14/debug_260914-114608.log:30
  - BD-MAP P16_P31 guard: ABSENT -> NONE -- baseline DOCs/analyses/bench/2026-09-11/debug_260911-210229.log:32, visit DOCs/analyses/bench/2026-09-14/debug_260914-114608.log:32
  - BD-MAP P32_P47 guard: ABSENT -> NONE -- baseline DOCs/analyses/bench/2026-09-11/debug_260911-210229.log:34, visit DOCs/analyses/bench/2026-09-14/debug_260914-114608.log:34
  - BD-MAP P32_P47 ovl: NONE -> SELF -- baseline DOCs/analyses/bench/2026-09-11/debug_260911-210229.log:34, visit DOCs/analyses/bench/2026-09-14/debug_260914-114608.log:34
  - BD-MAP P40_P55 guard: ABSENT -> GATE_OVERLAP -- baseline DOCs/analyses/bench/2026-09-11/debug_260911-210229.log:35, visit DOCs/analyses/bench/2026-09-14/debug_260914-114608.log:35
  - BD-MAP P40_P55 ovl: NONE -> LEFT+12_PWM_W_L -- baseline DOCs/analyses/bench/2026-09-11/debug_260911-210229.log:35, visit DOCs/analyses/bench/2026-09-14/debug_260914-114608.log:35
  - BD-MAP P8_P23 guard: ABSENT -> NONE -- baseline DOCs/analyses/bench/2026-09-11/debug_260911-210229.log:31, visit DOCs/analyses/bench/2026-09-14/debug_260914-114608.log:31
  - BD-MAP P8_P23 ovl: P0_P15+12_PWM_W_L -> NONE -- baseline DOCs/analyses/bench/2026-09-11/debug_260911-210229.log:31, visit DOCs/analyses/bench/2026-09-14/debug_260914-114608.log:31


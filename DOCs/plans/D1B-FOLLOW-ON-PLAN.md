# After D1b — starting point and plan of work and research (v6.2.0)

Written 2026-10-05 at Stephen's request (*"let's document all of this as our starting point and plan of work/research
then let's get all of this completed"*). It extends the sprint plan (`DOCO-AND-CLOCK-SPRINT-PLAN.md` §6, §10, §17); the
sprint plan stays the authority for scope and gates. Evidence: `DOCs/analyses/bench/2026-10-05/D1B-EVALUATION.md` (local)
and the logs it cites; PL-170 for Rev A's sensing.

## 1. Standing rulings this plan works under

- **Best drive per board** (STEPHEN 2026-10-05): *"our goal is best possible drive for revA and then also for revB boards
  if we algorithmically are different for each to achieve then we need to be."* (doctrine overlay P14).
- The library's own 40/27 A limits for the Doco measure runs; the harness's 3.68 A stop is the bench's protection
  (STEPHEN *"yes A"*, 2026-10-05).
- The Doco is qualified the way the 6.5″ was; no new measurements (STEPHEN 2026-10-04).
- What ships, and every Known Issue, is Stephen's; a driver change beyond a table value goes to him priced (overlay P5).

## 2. Starting point — what is established

| Area | Established (MEASURED unless marked) | Evidence |
|---|---|---|
| The drive | DRIVER_REV 53 drives the Doco 7.4-24 V both ways under 40 A: follows 999-1,000 ‰, ramps and stops on plan, stops rest in band | D1b third pass, five complete rows |
| Hall map | Correct order both ways, 0 bad edges of 2,304; sectors 53.6-67.8 e-deg, repeatable to 1.1°; hysteresis 3.0-3.4°; zero independent of speed | `B1-HALLSEQ`, `B1-CODEW`, `B1-HYST` |
| Timing | Half-speed DC-link minimum NEG −55.5..−62.2° (mean −59.7°), POS +52.4..+55.6° (mean +54.1°); shipped −53/+53° | `B1-OFSFIT q DC` |
| Direction asymmetry | NEG needs +5 / +11 / +17-20 % duty over POS at 25 / 50 / 75 % | `B1-RUNGD` |
| Top-speed regime | Above ≈ 2,400 rpm (knee between 352.5e6 and 376e6 increments, 29.5-31.5 e-deg a drive pass) duty runs +44..+81 % over the back-EMF line and switches between two states at one command | `B1-RUNGD` duty_lo/hi; 24 V NEG d0 1,104 mA vs 428 mA |
| Ceilings | 11.1 V's 545e6 is 116 % of no-load and past PK-1; 7.4 / 14.8 V NEG tops duty-capped | `B1-ROW`, `B1-OFSPTD capped` |
| Slowest steady | Forward (NEG) 1.00 ticks/s at 7.4 V, ≤ 0.60 from 14.8 V; reverse (POS) 4.00 at 7.4 V, ≤ 0.60 from 14.8 V | `B1-MININC` |
| Front cog | Worst pass 66,936 ticks (one motor), a tick count → fits 1 ms − 100 µs down to 74.4 MHz (DERIVED) | `B1-FRONT` |
| Rev A sensing | One frame's driven noise σ ≈ 1.7 mV (≈ 0.35 A), peaks 6-8 mV over a mean equal to the zero; coasting σ ≈ 0.6-1.1 mV (DERIVED: driven ≈ 2× coasting); offset 1.9-13 mV by board and run. A test limit under ~10 A folds on noise and the fold arms the limit hold (following lost at 2 A). No public method sets a limit | PL-170; 2026-09-30 Rev A evaluations; D1b second pass |
| Unfinished | 11.1 V's min-increment, ladder, ramp and stop legs (its run ended in the offset scan, twice) | `-124754`, `-002048` |

## 3. Research questions — each with what settles it

| # | Question | Settled by | Feeds |
|---|---|---|---|
| R1 | What produces the top-speed regime (extra duty, two states) above ~30 e-deg a pass? | Desk: the driver's angle advance, error measure and duty loop read against the D1b records; a discriminator computed from existing logs (overlay P10) | Ceilings; any driver change (Stephen, priced) |
| R2 | What is Rev A's per-frame noise: independent frame to frame (averageable) or switching-locked / biased? Where does the ADC window sit against the switching edges? | Desk: the sense acquisition in source + p2kb; the 2026-09-30 statistics. If still open, a raw per-frame capture rides on D2 as a load (not a visit) | The Rev A limit design's window and form |
| R3 | Does the NEG duty excess close with the corrected pair? | D2's ladder on the new tables (certification, not a new measurement) | D1B-4 closes or becomes a finding |
| R4 | Does the best timing move with speed once R1 is fixed? | The D1b top-speed vertices re-read after R1; D2's scan on the new tables | The lead-schedule packet (Stephen) |

## 4. Work, in order

1. **R1 and R2 at the desk, in parallel** (read-only surveys, then the arbiter's conclusion from the source and logs).
2. **«#3684» Doco tables:** the per-voltage pair from §2's minima; the minimum increments; the feedforward line from
   the 25-75 % rungs; ceilings set against R1's conclusion (and below the knee unless the driver changes). 11.1 V values
   DERIVED between 7.4 and 14.8 V, labelled. Each constant cites its log. Packets to Stephen, one question at a time:
   any driver change R1 leads to; the lead schedule (R4); the per-sector angle table (D1B-7). DRIVER_REV bump.
3. **«#3699» Rev A current sensing** (R2): the limit decided on a reading Rev A can resolve (filtered raw counts or a
   persistence gate), a per-frame hard trip kept where one frame is trustworthy, the limit hold armed from the sustained
   limit, the window a named parameter in time units; Rev B's path unchanged (byte-compare); per-board resolution and
   response time stated in the API docs. Closes PL-170.
4. **«#3698» harness repairs:** the offset scan restores the shipped pair before each stop and logs each side's stop and
   ramp; the run charge cap re-derived; MISDIAL per sign on the 25-75 % rungs; LEADMOVE reads a vertex beyond the span;
   SKIPPED points zeroed; the fold count catches continuous folding; (if R2 needs it) the raw per-frame capture.
5. **«#3683» the clock-floor question** to Stephen with the measured front-cog input.
6. **One gate for the batch** (`tools/build-check.sh`, style, pasm_equiv / byte-compares), one commit.
7. **«#3687» D2 and the 6.5″ session:** the tuned tables per voltage, the 11.1 V row in full, the hand-load cells at a
   low limit on Rev A (now meaningful), the 6.5″ session's cells; one or two visits to the release.

## 5. Done when

R1 and R2 each have a stated cause (or a stated reason none is reachable at the desk and the one load that settles it);
the tables cite their logs; Rev A's limit holds a low limit without folding on noise (desk model: a one-frame spike
neither folds nor arms; a real overload does within the stated time) and Rev B is byte-identical; the harness repairs
show their negatives; the batch gates once; the D2 sheet is ready with every load naming the decision it feeds.

## Revision history

- **2026-10-05** — written from the D1b evaluation and the Q&A that followed it (Rev A noise, per-board ruling).

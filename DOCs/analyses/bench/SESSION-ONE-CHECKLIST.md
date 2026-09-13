# Bench Session One — Tier 0 + Meter Characterisation

## PANIC: emergencyCutoff() is NOT a panic button

It self-cancels in ~250 ms (finding S-4). **PHYSICAL BATTERY DISCONNECT ONLY.**

## Pre-flight

- [ ] P2 Edge Module seated on Edge Mini Breakout #64019
- [ ] Dual 6.5″ platform, two Rev B Universal Motor Driver boards, 18.5 V pack
- [ ] Pack connected — safe: no test starts motion except T0-10, which commands zero speed
- [ ] Active config block describes **the hardware actually connected** — for this
      bench the dual 6.5″/18.5 V block (`LEFT = PINS_P0_P15`, `RIGHT = PINS_P16_P31`).
      **You set this by hand**; the runner reads it and reports it, and never edits it.
- [ ] Banner prints `motor_type_enum=` and `wheel_dia_x10=` — expect `0` and `65`.
      Other values are not a stop: the run proceeds and each test says what it
      could determine. With `wheel_dia_x10=0`, T0-3 and part of T0-6 report the
      distance conversion as unavailable rather than a tick count.
- [ ] Meter inline between pack and whole system (already confirmed placement)

## Part A — Tier 0 (fully automatic)

```
tools/bench-run.sh t0
```

- Loads headed (a window opens) but runs itself — **no keypresses, no prompts**
- Ten tests, T0-1 .. T0-10, run in order automatically; ends printing `DONE`
- ~30 minutes including build
- Log auto-curated to `DOCs/analyses/bench/<today>/t0.log` — **nothing to transcribe**

**Finish Part A before any Part B power cycling.** The P2 is powered from the
pack, so a cycle mid-run reboots it and loses the run. The two halves are
sequential, not concurrent.

- [ ] Ran `tools/bench-run.sh t0`
- [ ] Saw `DONE` at the end
- [ ] Confirmed curated log exists under `DOCs/analyses/bench/<today>/`

**T0-10 is the one exception to "no motion."** Every other test runs through
`testSetup()` only — no driver cog starts. T0-10 calls the real `start()`:
commanded speed stays 0, but the driver cog runs and the phases are energized —
a connected motor may hold or twitch at commutation. **T0-10 needs the rail on**
or its reading is meaningless.

- [ ] Rail was ON during T0-10 (runs second-to-last — T0-8, which occupies every
      spare cog, deliberately runs last so nothing follows it)

### The reading that matters most — T0-1's `dead_gap`

At 270 MHz:

- `dead_gap = 70` → CONFIRMS finding A1, vendor-compliant 260 ns — good, proceed
- `dead_gap = 14` → ~52 ns, **5× below the 250 ns minimum both board manuals require**

```
dead_gap observed = __________
```

- [ ] If `14`: **STOP.** Re-read at a second clock before concluding anything:
  `tools/bench-run.sh t0 200000000` — do **not** run Tier 1 until corrected.

## Part B — characterise the meter (the human work)

Every screen shows **A, V, W** live, plus one rotating value: **Ah, Wh, Ap (peak A), Vm (min V), Wp (peak W).**

Already known — do not re-ask:
- Peak registers `Ap` / `Vm` / `Wp` reset **only** on a power cycle — no reset control.
- Display cycles **5 screens** — `Ah`, `Wh`, `Ap`, `Vm`, `Wp` — **~4 s each, 20 s per full
  rotation** (measured 2026-09-10). `A`, `V`, `W` are on every screen (STEPHEN 2026-09-12).
- So the hold dwell floor is **25 s, not 20 s**: arriving mid-screen means a full
  rotation can take up to ~24 s from the moment you start watching.

### 1. Pack disconnect — **ANSWERED, nothing to test**

**NO, the P2 does not survive one** — it is powered from the pack (Stephen,
2026-09-10). So: **read the peaks BEFORE any cycle** (the cycle is what clears
them), and every cycle reboots the P2. T1-7 becomes one trial per program load;
consequences are written up in the sprint plan §8.1.

### 2. Display rotation order and full cycle time — write exactly what appears, in sequence

```
1. __________   2. __________   3. __________   4. __________
5. __________   6. __________   7. __________   8. __________

full cycle time = __________ s
```

### 3. Do Ah / Wh reset with the peaks, or separately?

```
Ah/Wh reset behavior = __________________________________
```

### 4. Quiescent zero — motors stopped, rail on (retake after EVERY power cycle — never carry across one)

```
V = __________     A = __________     W = __________
```

### 5. Does `Ap` latch after current drops, or decay?

If it decays, T1-7's fault-current technique collapses (needs the §2A front end instead).

```
Ap behavior:  LATCHES / DECAYS   (circle one)
```

### 6. Sanity-check `Ap` bandwidth against a rung with known steady current (from `A`)

Treat `Ap` as a **lower bound** until checked.

```
known A (steady) = __________     Ap read at same rung = __________
```

## Closing

- [ ] T0 log confirmed at `DOCs/analyses/bench/<today>/t0.log`
- [ ] All Part B answers above copied back into `DOCs/plans/BENCH-READINESS-SPRINT-PLAN.md` §8.1 and `DOCs/analyses/BENCH-TEST-PLAN-2026-09-10.md` §2B

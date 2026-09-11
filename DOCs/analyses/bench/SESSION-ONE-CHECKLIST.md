# Bench Session One — Tier 0 + Meter Characterisation

## PANIC: emergencyCutoff() is NOT a panic button

It self-cancels in ~250 ms (finding S-4). **PHYSICAL BATTERY DISCONNECT ONLY.**

## Pre-flight

- [ ] P2 Edge Module seated on Edge Mini Breakout #64019
- [ ] Universal Motor Driver (Rev B) board attached
- [ ] Pack connected — safe: no test in this session starts motion except T0-10, which commands zero speed
- [ ] `tools/bench-run.sh` activates the single-motor 6.5″ config block itself — no manual edit needed
- [ ] Banner will print `motor_type_enum=` — **must read `0`**. Anything else: STOP, switch the active block in `src/isp_bldc_motor_userconfig.spin2`, rerun.
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

- [ ] Rail was ON during the T0-10 portion (last test in the run)

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

8 readings, rotating one every ~2 s: **A, V, W, Ah, Wh, Ap (peak A), Vm (min V), Wp (peak W).**

Already known — do not re-ask:
- Peak registers `Ap` / `Vm` / `Wp` reset **only** on a power cycle — no reset control.
- Display cycles; one full rotation of all 8 readings ≈ 16 s.

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

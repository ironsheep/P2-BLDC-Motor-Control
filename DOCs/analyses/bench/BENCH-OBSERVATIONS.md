# Bench observations — durable log

Owned by the **executing side** (Stephen at the bench). Append-only; never pruned, never
re-cut. The run sheet (`BENCH-PASS-1-RUNSHEET.md`) is transient and current-state-only —
history accumulates *here* so that document can stay short.

Protocol: `central:dual-agent-handoff` §9. The authoring side reads this and does not
rewrite it.

Record, per step: what ran, the source SHA, what was expected, what was observed, and the
surrounding log lines. **Record the observation, not the verdict** — "this looks like a
test bug" closes the question before the side that can answer it has looked.

---

## Bench Pass 1 — «#3498» — source `441c9d9`

_(nothing recorded yet)_

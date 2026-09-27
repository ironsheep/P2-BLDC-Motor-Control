#!/usr/bin/env bash
# Prove a candidate PASM driver image equivalent to the baseline (mem-reduce-start), frame by frame.
# Usage: tools/pasm_equiv/run.sh [--seeds N] [--scenario NAME] [...]   (--help for every option)
# Exit status: 0 equivalent and inside the frame budget; 1 a divergence; 2 a budget failure (start frame
# included); 3 incomplete (with --coverage, also moved code the candidate covers less than the baseline did).
set -euo pipefail
here="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
exec python3 -B "$here/pasm_equiv.py" "$@"          # -B: no __pycache__ left in the tree

#!/usr/bin/env bash
# Fresh kernel + bridge run. See RUN_SPEC.md.
# Usage: ./rebuild_kernels.sh [stamp]
set -euo pipefail
ROOT="$(cd "$(dirname "$0")" && pwd)"
cd "$ROOT"
STAMP="${1:-$(date +%Y-%m-%d)}"

WALK_OUT="kernels/walk/runs/${STAMP}_h0.002_n200000"
NGON_OUT="kernels/ngon/runs/${STAMP}_n1-60"
BRIDGE_OUT="measures/bridge/runs/${STAMP}"

echo "walk  -> $WALK_OUT"
python3 kernels/walk/kernel.py 0.002 200000 "$WALK_OUT"

echo "ngon  -> $NGON_OUT"
python3 kernels/ngon/kernel.py 60 "$NGON_OUT"

echo "bridge -> $BRIDGE_OUT"
python3 measures/bridge/bridge_measure.py "$BRIDGE_OUT" 24

echo "done. compare $WALK_OUT/summary.csv to kernels/walk/runs/2026-09-19_h0.002_n200000/summary.csv"

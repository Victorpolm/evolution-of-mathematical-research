#!/bin/bash
# Chunked, patient metadata backfill. Each chunk resumes from its own state
# file on retry; failures wait 12 min before another attempt so the OAI
# service is never hammered. A chunk that exhausts its attempts is reported
# and the script exits nonzero (review-4: it used to print "complete" anyway).
set -u
cd "$(dirname "$0")/.."
chunks=(
  "2025-08-01 2026-05-01"
  "2024-08-01 2025-08-01"
  "2023-08-09 2024-08-01"
)
failed=()
for c in "${chunks[@]}"; do
  set -- $c
  ok=0
  for attempt in $(seq 1 20); do
    echo "=== chunk $1..$2 attempt $attempt $(date -u +%H:%M)"
    if python3 -m pipeline.harvest --from "$1" --until "$2"; then
      echo "=== chunk $1..$2 done"
      ok=1
      break
    fi
    echo "=== chunk failed; sleeping 12 min"
    sleep 720
  done
  if [ "$ok" -ne 1 ]; then
    failed+=("$1..$2")
  fi
done
if [ "${#failed[@]}" -gt 0 ]; then
  echo "=== backfill INCOMPLETE — failed chunks: ${failed[*]}"
  exit 1
fi
echo "=== backfill complete"

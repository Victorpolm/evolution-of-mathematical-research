#!/bin/bash
# Self-driving finish for the S3-filter transfer (2026-08-10 night).
# Detached-safe: retry loop survives laptop suspend/resume and network drops.
# Terminates the EC2 instance ONLY after two consecutive clean, size-verified
# rsync passes; on any verification failure it leaves everything for morning.
# Status: corpus/s3/OVERNIGHT_STATUS.txt ; log: corpus/s3/overnight.log
#
# DISABLED (review-4/5): success detection is two matching size-lists 60s
# apart — a producer lull looks like completion — and teardown does not
# verify hashes, producer done-state, or import reconciliation. The
# 2026-08-10 run was verified after the fact; harden before reuse.
if [ "${ARXIV_OBS_UNSAFE_SYNC:-}" != "1" ]; then
  echo "overnight_sync.sh is DISABLED as unsafe (see header + pipeline/aws/README.md)."
  echo "Set ARXIV_OBS_UNSAFE_SYNC=1 to force (not recommended)."
  exit 1
fi
cd "$(dirname "$0")/../.." || exit 1
KEY="$HOME/.ssh/arxiv-obs.pem"
read IID IP < pipeline/aws/instance.txt
S="ssh -i $KEY -o ConnectTimeout=20 -o StrictHostKeyChecking=accept-new ec2-user@$IP"
status() { echo "$(date -u +%FT%TZ) $*" >> corpus/s3/OVERNIGHT_STATUS.txt; }

pkill -f "rsync.*math_" 2>/dev/null; sleep 3
status "overnight sync started (owner: ops session; other sessions: do not touch AWS)"

clean=0
for attempt in $(seq 1 60); do
  rsync -a --partial --append-verify -e "ssh -i $KEY -o ConnectTimeout=20" \
    "ec2-user@$IP:out/math_*.tar" corpus/s3/ && rc=0 || rc=$?
  if [ "$rc" -ne 0 ]; then
    status "rsync attempt $attempt rc=$rc; retrying in 5 min"
    clean=0; sleep 300; continue
  fi
  REMOTE=$($S 'cd out && for f in math_*.tar; do echo "$(stat -c%s $f) $f"; done' 2>/dev/null | sort -k2)
  LOCAL=$(cd corpus/s3 && for f in math_*.tar; do echo "$(stat -c%s $f) $f"; done | sort -k2)
  if [ -n "$REMOTE" ] && [ "$REMOTE" = "$LOCAL" ]; then
    clean=$((clean+1)); status "clean size-verified pass $clean/2"
    [ "$clean" -ge 2 ] && break
    sleep 60
  else
    status "size mismatch or remote unreachable after pass; retrying"
    clean=0; sleep 120
  fi
done

if [ "$clean" -lt 2 ]; then
  status "GAVE UP after $attempt attempts — instance LEFT RUNNING for manual check"
  exit 1
fi

status "transfer verified: $(ls corpus/s3/math_*.tar | wc -l) tars, $(du -sh corpus/s3 | cut -f1)"
( cd corpus/s3 && sha256sum math_*.tar > SHA256SUMS ) && status "SHA256SUMS written"
$S 'tmux kill-session -t filter 2>/dev/null; true'
if aws ec2 terminate-instances --instance-ids "$IID" >> corpus/s3/overnight.log 2>&1; then
  status "instance $IID TERMINATED — AWS teardown complete"
else
  status "TERMINATION FAILED — terminate manually: aws ec2 terminate-instances --instance-ids $IID"
fi
status "done"

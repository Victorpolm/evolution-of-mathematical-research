#!/bin/bash
# rsync filtered tars home, verify counts, then (manually) terminate.
set -euo pipefail
read IID IP < pipeline/aws/instance.txt
mkdir -p corpus/s3
rsync -a --partial --info=progress2 -e "ssh -i $HOME/.ssh/arxiv-obs.pem" \
  "ec2-user@$IP:out/math_*.tar" corpus/s3/
echo "=== local tar inventory:"; ls -la corpus/s3/ | tail -40
echo "=== member counts per month:"
for t in corpus/s3/math_*.tar; do echo -n "$t: "; tar tf "$t" | wc -l; done
echo "Verify against DB with the importer before terminating:"
echo "  aws ec2 terminate-instances --instance-ids $IID"

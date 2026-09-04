#!/usr/bin/env python3
"""Runs ON the EC2 instance: stream arXiv src chunks, keep math members.

Reads chunk_list.tsv (filename, md5, size) and math_ids.txt; for each chunk:
download (in-region, free) -> verify md5 -> copy members whose paper ID is in
the math set into out/math_<yymm>.tar -> delete chunk. State in done.txt makes
it resumable. Run: nohup python3 filter_remote.py > filter.log 2>&1 &
"""
import hashlib
import os
import subprocess
import sys
import tarfile
import time

IDS = {line.strip() for line in open("math_ids.txt") if line.strip()}
CHUNKS = [line.split("\t") for line in open("chunk_list.tsv").read().splitlines()]
DONE_F = "done.txt"
done = set(open(DONE_F).read().split()) if os.path.exists(DONE_F) else set()
os.makedirs("out", exist_ok=True)

kept = skipped = 0
open_tars = {}
def out_tar(yymm):
    if yymm not in open_tars:
        open_tars[yymm] = tarfile.open(f"out/math_{yymm}.tar", "a")
    return open_tars[yymm]
t0 = time.time()
for i, (key, md5, size) in enumerate(CHUNKS, 1):
    base = os.path.basename(key)
    if base in done:
        continue
    for attempt in range(5):
        r = subprocess.run(["aws", "s3", "cp", f"s3://arxiv/{key}", base,
                            "--request-payer", "requester", "--quiet"])
        if r.returncode == 0:
            break
        time.sleep(20 * (attempt + 1))
    else:
        print(f"FAILED download {key}", flush=True)
        continue
    h = hashlib.md5()
    with open(base, "rb") as f:
        for blk in iter(lambda: f.read(1 << 20), b""):
            h.update(blk)
    if h.hexdigest() != md5:
        print(f"MD5 MISMATCH {key}", flush=True)
        os.remove(base)
        continue
    yymm = base.split("_")[2]
    tout = out_tar(yymm)
    with tarfile.open(base) as tin:
        for m in tin.getmembers():
            if not m.isfile():
                continue
            stem = os.path.basename(m.name)
            stem = stem[: stem.rfind(".")] if "." in stem else stem
            if stem in IDS:
                f = tin.extractfile(m)
                tout.addfile(m, f)
                kept += 1
            else:
                skipped += 1
    os.remove(base)
    tout.fileobj.flush()
    with open(DONE_F, "a") as f:
        f.write(base + "\n")
    if i % 25 == 0:
        el = time.time() - t0
        print(f"{i}/{len(CHUNKS)} chunks | kept {kept} skipped {skipped} | "
              f"{el/60:.0f} min | eta {(len(CHUNKS)-i)*el/max(1,i)/3600:.1f}h", flush=True)
for t in open_tars.values():
    t.close()
print(f"ALL DONE kept={kept} skipped={skipped}", flush=True)

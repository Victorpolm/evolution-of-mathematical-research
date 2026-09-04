# AWS acquisition subsystem

All non-trivial cloud operations live in this directory as reviewable code
(owner decision 2026-08-10); credentials are always ambient (~/.aws), never
in code or repo. Current lifecycle:

1. provisioning       — was done via documented CLI commands (2026-08-10 run),
                        not yet ops-as-code; a `provision.sh` is future work
2. `filter_remote.py` — runs ON the instance: stream chunks, keep math IDs,
                        MD5-verified, resumable via done.txt (in tmux!)
3. `sync_home.sh` / `overnight_sync.sh` — rsync monthly tars to corpus/s3/,
                        verify, terminate. KNOWN LIMITS (review-4): the
                        overnight variant declares success on two matching
                        size-lists 60 s apart, without hash comparison or
                        producer done-state checks — a producer lull can look
                        like completion. The 2026-08-10 acquisition was
                        verified after the fact by SHA256SUMS + importer
                        reconciliation; harden before reusing.
4. `import_s3.py`     — IMPLEMENTED: two-direction ID reconciliation vs DB,
                        tar + member sha256 ledger, registration gated on
                        zero problems (`--register`, `--force` override).
                        Ran clean on 2026-08-11: 168,027/168,027 members.

Ops lessons encoded here: launch long jobs in tmux (SSH-HUP races kill
nohup+setsid); pkill patterns need [b]racket self-match guards; security
group is per-IP — rerun the authorize step when the local IP changes.
instance.txt is local-only (gitignored).

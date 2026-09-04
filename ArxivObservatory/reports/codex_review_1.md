1. **Critical — [db.py:48](/mnt/z/ArxivObservatory/pipeline/db.py:48)–[57](/mnt/z/ArxivObservatory/pipeline/db.py:57), [fetch.py:111](/mnt/z/ArxivObservatory/pipeline/fetch.py:111)–[115](/mnt/z/ArxivObservatory/pipeline/fetch.py:115).** The ledger permits only one row per paper/kind and todo selection ignores versions, so earlier versions are never fetched and a newly harvested version is silently analyzed using stale full text.

   Fix: Key `files` by `(arxiv_id, version, kind)` and select every required version lacking a successful matching row.

2. **Critical — [fetch.py:71](/mnt/z/ArxivObservatory/pipeline/fetch.py:71), [80](/mnt/z/ArxivObservatory/pipeline/fetch.py:80)–[84](/mnt/z/ArxivObservatory/pipeline/fetch.py:84), [104](/mnt/z/ArxivObservatory/pipeline/fetch.py:104), [112](/mnt/z/ArxivObservatory/pipeline/fetch.py:112)–[114](/mnt/z/ArxivObservatory/pipeline/fetch.py:114).** Connection exhaustion, one-off HTTP 5xx, 404, and retry exhaustion all create `files` rows, while `select_todo` excludes every existing row regardless of status, permanently converting transient failures into missing full-text observations.

   Fix: Exclude only successful or explicitly permanent no-source rows, and keep transient/error statuses eligible for retry.

3. **High — [scan.py:121](/mnt/z/ArxivObservatory/pipeline/scan.py:121)–[143](/mnt/z/ArxivObservatory/pipeline/scan.py:143).** A run deletes prior hits, commits new hits paper-by-paper, and writes worker errors only to stdout, so a crash or failed worker leaves a partial database run whose unprocessed papers are indistinguishable from true zero-hit papers.

   Fix: Persist per-paper scan success/error plus a run-completion marker, and expose results as complete only after every job finishes.

4. **High — [harvest.py:144](/mnt/z/ArxivObservatory/pipeline/harvest.py:144)–[145](/mnt/z/ArxivObservatory/pipeline/harvest.py:145), [158](/mnt/z/ArxivObservatory/pipeline/harvest.py:158), [174](/mnt/z/ArxivObservatory/pipeline/harvest.py:174)–[176](/mnt/z/ArxivObservatory/pipeline/harvest.py:176).** Changing `--from` resets page numbering and overwrites only the beginning of a shared archive, leaving an older tail that `--reparse` later processes and can use to reintroduce out-of-frame papers or overwrite newer metadata with stale records.

   Fix: Archive each query/run separately and reparse only pages listed in that run’s completed manifest.

5. **High — [harvest.py:152](/mnt/z/ArxivObservatory/pipeline/harvest.py:152)–[155](/mnt/z/ArxivObservatory/pipeline/harvest.py:155), [scan_meta.py:23](/mnt/z/ArxivObservatory/pipeline/scan_meta.py:23)–[24](/mnt/z/ArxivObservatory/pipeline/scan_meta.py:24).** `--from/--until` bound OAI record modification datestamps—not v1 submission dates—and metadata scanning then scans every stored row, so a purported date cohort includes old papers revised during the interval and has a biased denominator. [OAI-PMH selective-harvesting semantics](https://www.openarchives.org/OAI/test/openarchivesprotocol.htm)

   Fix: Define the analysis cohort explicitly from `papers.created`, independently of incremental OAI synchronization dates.

6. **High — [fetch.py:37](/mnt/z/ArxivObservatory/pipeline/fetch.py:37)–[51](/mnt/z/ArxivObservatory/pipeline/fetch.py:51), [scan.py:64](/mnt/z/ArxivObservatory/pipeline/scan.py:64)–[92](/mnt/z/ArxivObservatory/pipeline/scan.py:92).** An uncompressed tar is stored as successful unknown-format source and then either treated as a zero-hit file or decoded and lexicon-scanned wholesale, allowing tar filenames/binary payloads to create false hits and hiding real member-level disclosures.

   Fix: Attempt `tarfile.open(..., mode="r:*")` before the single-text fallback and scan recognized tar members normally.

7. **High — [lexicon.py:232](/mnt/z/ArxivObservatory/pipeline/lexicon.py:232)–[238](/mnt/z/ArxivObservatory/pipeline/lexicon.py:238).** The accent regex allows letter-named accents without a delimiter, so it consumes ordinary commands such as `\thanks`, `\cite`, `\begin`, and `\documentclass`, causing confirmed missed context licenses and loss of citation-based known-FP downgrades.

   Fix: Require whitespace or a braced argument after letter-named accent commands while retaining delimiter-free matching only for symbolic accents.

8. **High — [lexicon.py:111](/mnt/z/ArxivObservatory/pipeline/lexicon.py:111), [146](/mnt/z/ArxivObservatory/pipeline/lexicon.py:146)–[157](/mnt/z/ArxivObservatory/pipeline/lexicon.py:157), [202](/mnt/z/ArxivObservatory/pipeline/lexicon.py:202)–[207](/mnt/z/ArxivObservatory/pipeline/lexicon.py:207), [246](/mnt/z/ArxivObservatory/pipeline/lexicon.py:246)–[251](/mnt/z/ArxivObservatory/pipeline/lexicon.py:251).** Bare `AI` is discarded before negation classification unless another licensing word occurs, so explicit statements such as “No AI.” and “This paper is AI-free.” produce no hit despite being covered by `NEGATION_RE`.

   Fix: Let a matching negation pattern license `AI-bare`, or classify negation before applying the context gate.

9. **High — [scan.py:71](/mnt/z/ArxivObservatory/pipeline/scan.py:71)–[86](/mnt/z/ArxivObservatory/pipeline/scan.py:86).** Every `.tex`, `.ltx`, and `.txt` member is scanned without determining whether it is rendered or reachable from the submitted root, so unused backups, examples, and residual sources can falsely set the paper-level hit flag.

   Fix: Restrict paper-level evidence to root/reachable TeX members and separately mark hits from unresolved residual files.

10. **Medium — [harvest.py:141](/mnt/z/ArxivObservatory/pipeline/harvest.py:141)–[155](/mnt/z/ArxivObservatory/pipeline/harvest.py:155), [163](/mnt/z/ArxivObservatory/pipeline/harvest.py:163)–[164](/mnt/z/ArxivObservatory/pipeline/harvest.py:164).** State identity records only `from`, so restarting an incomplete harvest with the same `from` but a different `until` silently resumes the old opaque query token and ignores the requested bound.

   Fix: Store and compare the full initial query fingerprint, including `until`, set, and metadata prefix, before reusing a token.

11. **Medium — [scan.py:35](/mnt/z/ArxivObservatory/pipeline/scan.py:35)–[39](/mnt/z/ArxivObservatory/pipeline/scan.py:39), [85](/mnt/z/ArxivObservatory/pipeline/scan.py:85).** Comment stripping treats every percent immediately preceded by a backslash as escaped, so `%` after an even number of backslashes such as `\\%` is retained even though TeX starts a comment there, allowing non-rendered comment text to create false paper hits.

   Fix: Strip `%` when the immediately preceding run of backslashes has even parity.

12. **Medium — [harvest.py:54](/mnt/z/ArxivObservatory/pipeline/harvest.py:54)–[60](/mnt/z/ArxivObservatory/pipeline/harvest.py:60).** Deleted OAI records are discarded without returning their identifier, so a previously harvested paper remains indefinitely active in the local frame after a deletion notification. [OAI-PMH deleted-record semantics](https://www.openarchives.org/OAI/test/openarchivesprotocol.htm)

   Fix: Parse deleted headers into tombstones and mark the corresponding paper inactive while retaining its historical data.

13. **Medium — [fetch.py:74](/mnt/z/ArxivObservatory/pipeline/fetch.py:74)–[78](/mnt/z/ArxivObservatory/pipeline/fetch.py:78), [harvest.py:125](/mnt/z/ArxivObservatory/pipeline/harvest.py:125)–[129](/mnt/z/ArxivObservatory/pipeline/harvest.py:129).** Both clients parse `Retry-After` only with `int()`, so a valid HTTP-date value raises `ValueError`, aborting the run instead of honoring the server’s requested delay. [RFC 9110 §10.2.3](https://datatracker.ietf.org/doc/rfc9110/)

   Fix: Parse both delay-seconds and HTTP-date forms through a shared helper.

14. **Medium — [scan.py:74](/mnt/z/ArxivObservatory/pipeline/scan.py:74)–[86](/mnt/z/ArxivObservatory/pipeline/scan.py:86).** Ancillary filenames are recorded only when their suffix is not scannable text, so an empty or oblique `ChatGPT-log.txt`/`claude-transcript.tex` yields no artifact hit despite matching `ANCILLARY_RE`.

   Fix: Record a matching ancillary filename independently, then optionally scan its contents as a second evidence source.

15. **Medium — [scan.py:80](/mnt/z/ArxivObservatory/pipeline/scan.py:80)–[81](/mnt/z/ArxivObservatory/pipeline/scan.py:81).** TeX members over 10 MiB are silently skipped without a coverage/error record, so a paper whose relevant source exceeds the limit is persisted as an ordinary zero-hit scan.

   Fix: Persist an incomplete-scan status for skipped members or scan them in bounded chunks.

16. **Low — [lexicon.py:168](/mnt/z/ArxivObservatory/pipeline/lexicon.py:168), [215](/mnt/z/ArxivObservatory/pipeline/lexicon.py:215)–[218](/mnt/z/ArxivObservatory/pipeline/lexicon.py:218).** Known-FP classification applies to any hit intersecting the entire FP match span, so the `Grok … Heinlein` pattern also labels an intervening real `ChatGPT` hit as `known_fp`.

   Fix: Associate each FP rule with the specific lexicon token it invalidates rather than treating its full contextual span as false-positive territory.

17. **Low — [lexicon.py:99](/mnt/z/ArxivObservatory/pipeline/lexicon.py:99).** The strong `large language model`/`LLM` pattern is case-sensitive, so a direct disclosure such as “We used an llm” produces no hit.

   Fix: Compile this pattern with `re.IGNORECASE`.

18. **Low — [scan.py:42](/mnt/z/ArxivObservatory/pipeline/scan.py:42)–[46](/mnt/z/ArxivObservatory/pipeline/scan.py:46).** One invalid UTF-8 byte causes the entire member to be decoded as Latin-1, corrupting otherwise valid multibyte text and preventing Unicode known-FP patterns such as `Université Claude` from downgrading the hit.

   Fix: Preserve valid UTF-8 spans with localized replacement or use a validated encoding-selection fallback rather than globally switching on the first decoding error.

Codex session ID: 019fe66d-2804-72a1-a47a-ee56f60f94a8
Resume in Codex: codex resume 019fe66d-2804-72a1-a47a-ee56f60f94a8

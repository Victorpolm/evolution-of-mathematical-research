# Draft: arXiv data-access email (for Johannes to send)

Updated 2026-08-13 (numbers re-verified against the corpus DB; supersedes
the 2026-08-11 scratchpad draft). Owner decision of 2026-08-13 permits
pre-release outreach — see DECISIONS.md.

To: help@arxiv.org
Subject: Guidance on acquiring first-version (v1) sources for a metascience study

Dear arXiv team,

I am a mathematician at ETH Zürich running an independent metascience
project measuring how often authors of arXiv mathematics papers disclose
AI assistance in their papers. The project publishes aggregate statistics
only (never per-paper listings or full texts), is clearly labeled as not
affiliated with arXiv, and is on a concrete roadmap to a public release;
I would be glad to share methods and results with you.

Following your bulk-access guidance, I have so far harvested metadata via
OAI-PMH (arXivRaw, polite paging) and obtained full text for the roughly
130,000 math-primary submissions of my study window (August 2023 –
August 2026) from the requester-pays S3 bucket (arXiv_src chunks).

My remaining problem is version pinning: the study reads each paper's
first submitted version (v1), so that later revisions cannot contaminate
the monthly time series. The S3 chunks understandably contain each
paper's latest version as of the chunk build date, so for the ~51,000
multi-version papers in my window I initially lacked a v1 source, and I
found no bulk channel for historical versions.

I began fetching pinned v1 e-prints from export.arxiv.org (strictly
serial, one request per 6 seconds, Retry-After honored, descriptive
User-Agent with a contact address) and voluntarily paused after ~9,100
papers to ask for your preferences before considering the remaining
~46,500:

1. Would a serial, throttled crawl of export.arxiv.org/e-print/{id}v1 at
   this volume be acceptable to you? If so, what request rate and time
   window would you prefer?
2. Is there a sanctioned bulk route for version-pinned historical
   sources (or PDFs) that I should use instead? I have verified that
   gs://arxiv-dataset carries version-pinned PDFs and used it for a
   small validation sample — is relying on it at scale the blessed
   alternative?
3. Are there constraints beyond the Terms of Use you would like me to
   observe? (I never redistribute full texts and publish only
   aggregates.)

Thank you for maintaining this wonderful piece of infrastructure.

Best regards,
Johannes Schmitt
ETH Zürich, johannes.schmitt@math.ethz.ch
(crawler User-Agent contact: jo314schmitt@gmail.com)

---

## Fact-check notes (not part of the email)

- ~130,000: frame query 2026-08-13 gives 132,195 math-primary papers
  created 2023-08 through 2026-07 with full-text artifacts (release frame
  counts differ slightly by boundary convention; rounded down on purpose).
- ~51,000 multi-version: 51,083 with latest_version > 1.
- ~9,100 fetched: 9,117 distinct papers via fetch_channel='export-v1'.
- ~46,500 remaining: 46,488 in-frame multi-version papers with no v1
  artifact (matches the "~46.5k tail" in DECISIONS 2026-08-12).
- 6 s serial rate: delay_s=6.0 in both v1refill manifests
  (corpus/logs/v1refill_manifest_*.json); Retry-After honoring and the
  contact-bearing User-Agent are in pipeline/fetch.py.
- gs://arxiv-dataset use: 594 papers via fetch_channel='gcs-pdf'.

## Post-send addendum (2026-08-14, review-12 A1)

The email (sent 2026-08-13) described the paused crawl accurately (9,117
papers at 6 s serial) and asked about "the remaining ~46,500" — the
in-frame primary-math subset. The tail crawl actually launched after
arXiv's reply selects the broader corpus multiversion universe:
**56,727 targets** (46,519 in-frame primary + 31 primary outside the
report dates + 10,177 non-primary cross-lists) at a **4.0 s manifest
delay** (~6 s effective cycle; still well inside the ToU limit of one
request per 3 s, single connection). Owner confirmed this scope and rate
2026-08-14 (DECISIONS). If arXiv follows up, describe the crawl with
these exact numbers, not the email's estimate.

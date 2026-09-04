# Platform & visualization design notes (2026-08-09 hackathon discussion)

Captures the discussion on turning the hackathon pipeline into a hosted public
project. Pick-up document — nothing here is implemented yet except where noted.

## 1. Three-layer architecture (the load-bearing decision)

1. **Corpus layer** — tarballs + observatory.db, 10s–100s of GB, NOT
   redistributable (arXiv license). Lives only on trusted compute.
2. **Extracted-data layer** — the public interface. Per-paper-version
   annotation table (arxiv_id, version, sha256, dates, categories, scan flags,
   classification labels + model provenance, human-review labels) plus
   pre-computed aggregate time series. IDs + derived labels only → legally
   publishable. Size: tens of MB parquet/CSV even at 500k paper-versions.
   Versioned releases with checksums + provenance metadata (lexicon version,
   scan_run ids, classifier model+version, extraction date). This is what the
   website consumes and what CI-runnable analyses run against.
3. **Presentation layer** — static site (GitHub Pages), all interactivity
   client-side. No backend needed at this data scale.

## 2. Community-PR analysis model, two tiers

- **Tier-1 (open, CI-runnable):** analysis = query + chart spec against the
  published extracted-data schema. GitHub Actions CAN run these (data is
  small); PR review sees the rendered chart. Examples: prevalence by subfield,
  combinatorics-vs-AG growth, papers/author/year decomposition, tool market
  share, disclosure-added-in-v2 rates.
- **Tier-0 (trusted-runner only):** new extractors that touch the corpus
  (lexicon changes, new LLM classification passes, Pangram runs, full-paper
  audits). Path: PR review → approved → run via pinned pipeline version on the
  trusted box → new extracted-data release. Runbook in repo; anyone with arXiv
  bulk access can re-derive (reproducibility statement, not redistributed data).
- Provenance discipline from TECH_NOTES applies: every release records which
  scan_run/model produced which column; taxonomy freezes get release tags.

## 3. Compute reality

- **Steady state is cheap:** ~200 math papers/day → daily OAI harvest + fetch
  + scan + classify runs in minutes on almost anything (laptop cron, ada cron,
  or a scheduled cloud agent). The heavy work is only (a) historical backfill,
  (b) re-scans after lexicon/taxonomy changes.
- **Backfill/sweeps:** ada D-MATH servers fit the profile exactly (few-TB user
  partitions, hundreds of CPUs; ada-servers skill exists in this environment).
  Governance posture: corpus stays on user partition, batch jobs only, nothing
  served publicly from ada — it's a compute resource for a D-MATH member's
  metascience research, not project hosting. Fallback: AWS S3 requester-pays +
  throwaway EC2 in us-east-1 (in-region transfer free), ~$50–100 for a 3-year
  math source corpus; see conversation notes — user's manual part is one-time
  ~20-min account setup, rest is scriptable.
- **LLM classification at scale:** subscription agents (codex/claude) are fine
  for dev, audits, and bounded work packages, but a public automated pipeline
  should budget API calls (Haiku-class batch API: ~10k snippets for single-digit
  dollars; 50% batch discount) with subscription agents kept for
  second-opinion/adjudication passes.
- **Author-level analyses** (same-pool-more-productive vs more-authors — the
  productivity decomposition question): metadata-only, needs no corpus. Hard
  part is author disambiguation → use OpenAlex (free bulk, disambiguated
  authors, affiliations, career age) joined on arXiv IDs rather than rolling
  our own. Also gives covariates for composition-shift corrections.

## 4. Visualization / UX (OWID + EpochAI as reference points)

- **Stack recommendation:** GitHub Pages + pre-computed JSON/CSV aggregates +
  Vega-Lite (or Observable Plot) charts; each chart = a declarative spec file
  in-repo (this IS the PR-able analysis unit). Optionally DuckDB-WASM against
  the full annotation parquet for an EpochAI-style in-browser explorer for
  power users — still zero backend. OWID's grapher is open-source but heavy to
  adopt; Vega-Lite gets the same feel (hover, facet, share-link) cheaper.
- **v1 chart inventory:**
  1. Disclosure prevalence over time (monthly, Wilson bands; split
     LLM / CAS / prover tiers — the cross-tool story).
  2. Small-multiples by primary math category (the combinatorics-vs-AG view).
  3. Tool + model market share over time (stacked area; exact model strings
     normalized to families).
  4. Usage-category distribution (writing/editing vs proofs vs code …).
  5. Epistemic impact over time — cosmetic / supportive / result-bearing (the
     headline axis).
  6. Denominator context: submissions per category vs long-term trend.
  7. Validation panel: pilot gold metrics, negative-audit recall estimate,
     awesome-ai-for-math cross-check buckets (kept prominent — the project's
     credibility is the validation-first stance).
  8. Later: version-history dynamics (disclosures added/removed between
     versions), productivity decomposition, disclosure-quality scores.
- **Interim step (this hackathon):** the results report will be built as a
  self-contained HTML dashboard artifact with exactly this structure —
  client-side, JSON-driven — so it can be lifted onto Pages nearly unchanged.

## 5. Repo topology when public

- `arxiv-observatory` (this repo): pipeline + docs + chart specs + site
  source. Corpus/, papers/, observatory.db stay gitignored forever.
- Extracted-data releases: GitHub Releases assets or a sibling `-data` repo
  (OWID pattern) — keeps the code repo light and the data versioned/citable
  (later: Zenodo DOI per release for the paper).
- CI: Tier-1 analysis checks + chart-spec validation + site build on PR;
  site deploy on merge; NO corpus access in CI by construction.

## 6. Triage of independent codex review (review_codex.md, 2026-08-09)

Applied in code: URL-protected comment stripping (A3), spaced OpenAI variant
(A4), classify batch retry (A5), content-sniffed TeX members (A1), audit
middle-truncation (D2), "raw classifier-positive rate" labeling (B2),
fail-loudly awesome parser (D1).

Adopted into plan:
- B1: every prevalence table reports the fetch-failure/withdrawn stratum.
- B3: recall audit at n>=200 negatives, packed multi-paper codex calls over
  head+tail slices; qualitative-only below that.
- B4: minimum-n masking / EB shrinkage for small subfield cells in public views.
- A2: files ledger to record requested AND effective version; stale_text flag.
- A6: source-scanned vs pdf-only strata kept separate in rollups.
- C1: CDN-front data assets (jsDelivr/R2), Pages serves HTML only.
- C2: freeze schema_version in parquet metadata before first external PR.
- C3: ODC-BY 1.0 for annotations (attribution + correction-ledger compatible).
- C4: community share-links stored as consented server-side snapshots.
- D3: Tier-0 sandbox = dedicated non-priv user + firejail/bwrap (not VMs) in
  phase 1; revisit at >5 external contributors.
- E1: lexicon and gold-set changes never in the same commit (CI check).
- E2: extract taxonomy_v1.md from the classify prompt; version it.

Non-Latin AI terms (A4b): deferred to a dedicated pass with native-speaker
validation.

## 7. Owner decisions (2026-08-09)

- Per-paper display: v1 site shows AGGREGATES ONLY; per-paper browsing of
  verified author-disclosure statements is attractive future functionality,
  gated on human verification. Detector-derived data (Pangram etc.) stays
  aggregate-only permanently unless separately justified — higher harm
  potential (implies neglect/misconduct rather than surfacing authors' own
  statements).
- Zenodo/DOI: phase 2, after hackathon/prototype.
- PR security: adopt conventions that structurally prevent code execution
  from community PRs (data-only Tier-1; sandboxed Tier-0 per D3).

## 8. Render-check layer (2026-08-10, from human review case [id-redacted])

Comment-stripping regexes are inherently brittle (custom macros, comment
environments, draft conditionals). The render-truth oracle is arXiv's own
compiled PDF — no TeX execution needed:

- Layer 1: source scan (recall-oriented, generous; improved stripping).
- Layer 2: LLM classification with wide context (±1500 chars, highlighted
  span, member/location metadata). The classifier judges text it is handed;
  it can never certify renderedness.
- Layer 3 (new, required before any evidence counts): every paper-level
  positive's evidence quote must fuzzy-match (whitespace/hyphenation
  normalized) the pdftotext of the arXiv-rendered, version-pinned PDF.
  Failures get status non_rendered_evidence: excluded from headline counts,
  retained as a separate, ethically gated residual-artifact category
  (TECH_NOTES §1 privacy default).
- PDF source: free GCS mirror gs://arxiv-dataset (verified working,
  version-pinned URLs, no credentials) or polite export fetch; S3 pdf/ tars
  for bulk. Only flagged papers need PDFs (~1.4k for the pilot window).
- Bonus: quantifies which of review-2's 464 unmatched quotes are
  non-rendered-source artifacts vs. classifier paraphrase/hallucination.

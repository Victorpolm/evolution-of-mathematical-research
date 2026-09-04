#!/usr/bin/env python3
"""Find AI-tool acknowledgement/use statements in new arXiv mailing entries.

The workflow is intentionally conservative:

* parse local arXiv daily .eml files;
* keep new submissions and, by default, new cross-listings;
* exclude replacement/revision entries;
* optionally download/cached arXiv PDFs and source packages;
* scan extracted TeX-like files and PDF text for AI-system mentions;
* emit JSON, CSV, and Markdown reports with snippets for manual review.
"""

from __future__ import annotations

import argparse
import csv
import dataclasses
import email
import gzip
import io
import json
import re
import shutil
import subprocess
import sys
import tarfile
import time
import urllib.error
import urllib.request
import zipfile
from email import policy
from pathlib import Path
from typing import Iterable


ARXIV_ID_RE = re.compile(r"^arXiv:(?P<id>\d{4}\.\d{4,5})(?P<rest>.*)$")
MAIL_DATE_RE = re.compile(r" - (?P<date>\d{4}-\d{2}-\d{2}) \d{4}\.eml$")
FIELD_RE = re.compile(r"^(Title|Authors|Categories|Comments|MSC-class|Journal-ref):\s*(.*)$")

AI_PATTERNS: list[tuple[str, re.Pattern[str]]] = [
    ("ChatGPT", re.compile(r"\bChatGPT\b", re.IGNORECASE)),
    ("OpenAI", re.compile(r"\bOpenAI\b", re.IGNORECASE)),
    ("GPT", re.compile(r"\bGPT(?:-[0-9A-Za-z.]+)?\b", re.IGNORECASE)),
    (
        "Claude",
        re.compile(
            r"\b(?:Anthropic\s+)?Claude(?:\s+(?:AI|Code|Sonnet|Opus|Haiku|[0-9](?:\.[0-9])?))?\b",
            re.IGNORECASE,
        ),
    ),
    ("Anthropic", re.compile(r"\bAnthropic\b", re.IGNORECASE)),
    ("Gemini", re.compile(r"\b(?:Google\s+)?Gemini\b", re.IGNORECASE)),
    ("Bard", re.compile(r"\b(?:Google\s+)?Bard\b", re.IGNORECASE)),
    ("Copilot", re.compile(r"\b(?:GitHub\s+)?Copilot\b", re.IGNORECASE)),
    ("DeepSeek", re.compile(r"\bDeepSeek\b", re.IGNORECASE)),
    ("Grok", re.compile(r"\bGrok\b", re.IGNORECASE)),
    ("Llama", re.compile(r"\bLLaMA\b|\bLlama\s*[0-9]?\b", re.IGNORECASE)),
    ("Mistral", re.compile(r"\bMistral(?:\s+AI)?\b", re.IGNORECASE)),
    (
        "large language model",
        re.compile(r"\blarge language models?\b|\bLLMs?\b", re.IGNORECASE),
    ),
    (
        "generative AI",
        re.compile(
            r"\bgenerative\s+AI\b|\bAI[- ](?:assisted|generated)\b|\bAI\s+assistance\b",
            re.IGNORECASE,
        ),
    ),
    ("artificial intelligence", re.compile(r"\bartificial intelligence\b", re.IGNORECASE)),
]

ACK_RE = re.compile(
    r"\backnowledg(?:e)?ments?\b|\bthanks?\b|\bgrateful\b|\bdeclare\b|\bdeclaration\b",
    re.IGNORECASE,
)
USAGE_RE = re.compile(
    r"\buse[ds]?\b|\busing\b|\butili[sz]ed\b|\bassist(?:ed|ance)?\b|\bhelp(?:ed|ful)?\b|"
    r"\bproofread(?:ing)?\b|\bedit(?:ed|ing)?\b|\bgrammar\b|\blanguage\b|\bwriting\b|"
    r"\bdraft(?:ed|ing)?\b|\bprepar(?:e|ed|ation)\b|\bpolish(?:ed|ing)?\b|"
    r"\bgenerat(?:e|ed|ion|ing)\b",
    re.IGNORECASE,
)
AUTHOR_DISCLOSURE_RE = re.compile(
    r"\bAI\s+Usage\b|\bTool and computational resource disclosure\b|"
    r"\bDuring the preparation of this work\b|\bAfter using this tool\b|"
    r"\bHuman verification\b|\btake responsibility\b|\bassumes responsibility\b|"
    r"\bAI generated, human verified\b|"
    r"\b(?:we|i|the author|the authors)\s+(?:used|use|utili[sz]ed|employed|asked)\b|"
    r"\b(?:ChatGPT|OpenAI|Claude|Gemini|Copilot|GPT(?:\s*[0-9](?:\.[0-9])?)?|LLM|large language model)[^\n]{0,180}?"
    r"(?:was|were)?\s*(?:very\s+)?(?:used|useful|helped|suggested|generated|obtained|assisted)\b|"
    r"\b(?:used|useful|helped|suggested|generated|obtained|assisted|drafted|proofread|edited)"
    r"[^\n]{0,180}?\b(?:ChatGPT|OpenAI|Claude|Gemini|Copilot|GPT|LLM|large language model)\b|"
    r"\b(?:proof|result|sketch|figure|manuscript|preprint|paper|content)[^\n]{0,180}?"
    r"\b(?:ChatGPT|OpenAI|Claude|Gemini|Copilot|GPT|LLM|large language model|AI assistance)\b|"
    r"\bAI[- ]generated\s+proof\b|\bAI-assisted mathematical research\b",
    re.IGNORECASE,
)
NEGATION_RE = re.compile(
    r"\bno\s+(?:AI|artificial intelligence|LLM|large language model|ChatGPT|OpenAI|Claude|Gemini)"
    r"\b|\bnot\s+(?:use|used|using|utili[sz]e|utili[sz]ed)\b|"
    r"\bwithout\s+(?:the\s+)?(?:use|assistance|help)\b|"
    r"\b(?:this|present)\s+paper\b[^\n.]{0,160}\b(?:completely\s+)?hand-?craft(?:ed)?\b",
    re.IGNORECASE,
)

TEX_EXTENSIONS = {".tex", ".ltx", ".txt"}


@dataclasses.dataclass
class Paper:
    arxiv_id: str
    kind: str
    mail_file: str
    mail_date: str
    title: str = ""
    authors: str = ""
    categories: str = ""
    comments: str = ""
    date: str = ""
    size: str = ""
    abs_url: str = ""

    def to_dict(self) -> dict[str, str]:
        return dataclasses.asdict(self)


@dataclasses.dataclass
class Hit:
    arxiv_id: str
    title: str
    paper_kind: str
    status: str
    source_kind: str
    source_path: str
    term: str
    snippet: str

    def to_dict(self) -> dict[str, str]:
        return dataclasses.asdict(self)


def mail_sort_key(path: Path) -> tuple[str, str]:
    match = MAIL_DATE_RE.search(path.name)
    return (match.group("date") if match else "", path.name)


def decode_eml(path: Path) -> str:
    with path.open("rb") as handle:
        msg = email.message_from_binary_file(handle, policy=policy.default)
    if msg.is_multipart():
        parts = []
        for part in msg.walk():
            if part.get_content_type() == "text/plain":
                try:
                    parts.append(part.get_content())
                except LookupError:
                    parts.append(part.get_payload(decode=True).decode("utf-8", "replace"))
        return "\n".join(parts)
    content = msg.get_content()
    return content if isinstance(content, str) else content.decode("utf-8", "replace")


def parse_mail_entries(path: Path) -> list[Paper]:
    body = decode_eml(path)
    lines = body.splitlines()
    starts: list[int] = []
    for index, line in enumerate(lines):
        if ARXIV_ID_RE.match(line):
            starts.append(index)

    papers: list[Paper] = []
    mail_date_match = MAIL_DATE_RE.search(path.name)
    mail_date = mail_date_match.group("date") if mail_date_match else ""

    for offset, start in enumerate(starts):
        end = starts[offset + 1] if offset + 1 < len(starts) else len(lines)
        entry = [line.rstrip() for line in lines[start:end]]
        paper = parse_entry(entry, path.name, mail_date)
        if paper is not None:
            papers.append(paper)
    return papers


def parse_entry(lines: list[str], mail_file: str, mail_date: str) -> Paper | None:
    if not lines:
        return None
    header = lines[0].strip()
    match = ARXIV_ID_RE.match(header)
    if not match:
        return None

    first_nonempty = ""
    for line in lines[1:8]:
        if line.strip():
            first_nonempty = line.strip()
            break
    if first_nonempty.startswith("replaced with revised version"):
        return None

    kind = "cross-list" if "(*cross-listing*)" in header else "new"
    paper = Paper(
        arxiv_id=match.group("id"),
        kind=kind,
        mail_file=mail_file,
        mail_date=mail_date,
    )

    fields: dict[str, str] = {}
    current_field: str | None = None
    for raw_line in lines[1:]:
        line = raw_line.rstrip()
        stripped = line.strip()
        if stripped == r"\\":
            current_field = None
            continue
        if stripped.startswith(r"\ ("):
            url_match = re.search(r"https://arxiv\.org/abs/\d{4}\.\d{4,5}", stripped)
            if url_match:
                paper.abs_url = url_match.group(0)
            continue
        if line.startswith("Date:"):
            date_line = line.removeprefix("Date:").strip()
            size_match = re.search(r"\(([^()]*)\)\s*$", date_line)
            if size_match:
                paper.size = size_match.group(1)
                date_line = date_line[: size_match.start()].strip()
            paper.date = date_line
            current_field = None
            continue
        field_match = FIELD_RE.match(line)
        if field_match:
            current_field = field_match.group(1)
            fields[current_field] = field_match.group(2).strip()
            continue
        if current_field and (line.startswith(" ") or line.startswith("\t")):
            fields[current_field] += " " + stripped

    paper.title = fields.get("Title", "")
    paper.authors = fields.get("Authors", "")
    paper.categories = fields.get("Categories", "")
    paper.comments = fields.get("Comments", "")
    if not paper.abs_url:
        paper.abs_url = f"https://arxiv.org/abs/{paper.arxiv_id}"
    return paper


def collect_papers(mail_glob: str, include_cross_lists: bool) -> list[Paper]:
    paths = sorted(Path(".").glob(mail_glob), key=mail_sort_key)
    papers_by_id: dict[str, Paper] = {}
    for path in paths:
        for paper in parse_mail_entries(path):
            if paper.kind == "cross-list" and not include_cross_lists:
                continue
            existing = papers_by_id.get(paper.arxiv_id)
            if existing is None or (existing.kind == "cross-list" and paper.kind == "new"):
                papers_by_id[paper.arxiv_id] = paper
    return sorted(papers_by_id.values(), key=lambda item: (item.mail_date, item.arxiv_id))


def download_url(url: str, target: Path, timeout: float, force: bool) -> str:
    if target.exists() and target.stat().st_size > 0 and not force:
        return "cached"
    target.parent.mkdir(parents=True, exist_ok=True)
    request = urllib.request.Request(
        url,
        headers={
            "User-Agent": "arxiv-ai-ack-scan/0.1 (+local research workflow)",
            "Accept": "*/*",
        },
    )
    tmp = target.with_suffix(target.suffix + ".tmp")
    with urllib.request.urlopen(request, timeout=timeout) as response:
        with tmp.open("wb") as handle:
            shutil.copyfileobj(response, handle)
    tmp.replace(target)
    return "downloaded"


def safe_extract_tar(tar: tarfile.TarFile, dest: Path) -> None:
    base = dest.resolve()
    for member in tar.getmembers():
        member_path = (dest / member.name).resolve()
        if base != member_path and base not in member_path.parents:
            raise ValueError(f"unsafe tar path: {member.name}")
    tar.extractall(dest, filter="data")


def safe_extract_zip(zip_handle: zipfile.ZipFile, dest: Path) -> None:
    base = dest.resolve()
    for member in zip_handle.namelist():
        member_path = (dest / member).resolve()
        if base != member_path and base not in member_path.parents:
            raise ValueError(f"unsafe zip path: {member}")
    zip_handle.extractall(dest)


def looks_like_tex(data: bytes) -> bool:
    sample = data[:5000].decode("utf-8", "ignore")
    return "\\documentclass" in sample or "\\begin{document}" in sample or "\\section" in sample


def write_single_source(data: bytes, dest: Path, stem: str) -> None:
    if data.startswith(b"%PDF"):
        (dest / f"{stem}.source.pdf").write_bytes(data)
    elif looks_like_tex(data):
        (dest / f"{stem}.tex").write_bytes(data)
    else:
        (dest / f"{stem}.source").write_bytes(data)


def extract_source_archive(archive: Path, dest: Path, force: bool) -> str:
    marker = dest / ".extracted"
    if marker.exists() and not force:
        return "cached"
    if dest.exists() and force:
        shutil.rmtree(dest)
    dest.mkdir(parents=True, exist_ok=True)

    data = archive.read_bytes()
    source_name = archive.parent.name

    try:
        if tarfile.is_tarfile(archive):
            with tarfile.open(archive) as tar:
                safe_extract_tar(tar, dest)
        elif zipfile.is_zipfile(archive):
            with zipfile.ZipFile(archive) as zip_handle:
                safe_extract_zip(zip_handle, dest)
        elif data[:2] == b"\x1f\x8b":
            decompressed = gzip.decompress(data)
            with io.BytesIO(decompressed) as bio:
                if tarfile.is_tarfile(fileobj := bio):
                    bio.seek(0)
                    with tarfile.open(fileobj=bio) as tar:
                        safe_extract_tar(tar, dest)
                else:
                    write_single_source(decompressed, dest, source_name)
        else:
            write_single_source(data, dest, source_name)
    except Exception:
        if not any(dest.iterdir()):
            dest.rmdir()
        raise

    marker.write_text("ok\n", encoding="utf-8")
    return "extracted"


def read_text(path: Path) -> str:
    data = path.read_bytes()
    for encoding in ("utf-8", "latin-1"):
        try:
            return data.decode(encoding)
        except UnicodeDecodeError:
            continue
    return data.decode("utf-8", "replace")


def strip_latex_comments(text: str) -> str:
    stripped_lines = []
    for line in text.splitlines():
        cut_at = None
        for index, char in enumerate(line):
            if char == "%" and (index == 0 or line[index - 1] != "\\"):
                cut_at = index
                break
        stripped_lines.append(line[:cut_at] if cut_at is not None else line)
    return "\n".join(stripped_lines)


def tex_files(source_dir: Path) -> Iterable[Path]:
    if not source_dir.exists():
        return []
    return sorted(
        path
        for path in source_dir.rglob("*")
        if path.is_file() and path.suffix.lower() in TEX_EXTENSIONS and path.stat().st_size < 5_000_000
    )


def extract_pdf_text(pdf_path: Path, text_path: Path, force: bool) -> str | None:
    if text_path.exists() and text_path.stat().st_size > 0 and not force:
        return read_text(text_path)
    if shutil.which("pdftotext") is None:
        return None
    text_path.parent.mkdir(parents=True, exist_ok=True)
    cmd = ["pdftotext", "-layout", "-enc", "UTF-8", str(pdf_path), str(text_path)]
    proc = subprocess.run(cmd, text=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=False)
    if proc.returncode != 0:
        raise RuntimeError(proc.stderr.strip() or "pdftotext failed")
    return read_text(text_path)


def normalize_snippet(text: str, pos: int, radius: int = 320) -> str:
    start = max(0, pos - radius)
    end = min(len(text), pos + radius)
    snippet = text[start:end]
    snippet = re.sub(r"\s+", " ", snippet).strip()
    return snippet


def classify_context(text: str, pos: int) -> str:
    local = text[max(0, pos - 700) : min(len(text), pos + 700)]
    section_window = text[max(0, pos - 2500) : pos]
    ackish = bool(ACK_RE.search(local) or re.search(r"\\(?:section|subsection)\*?\{[^}]*acknowledg", section_window, re.I))
    usageish = bool(USAGE_RE.search(local))
    author_disclosure = bool(AUTHOR_DISCLOSURE_RE.search(local))
    negated = bool(NEGATION_RE.search(local))
    if negated and (usageish or author_disclosure):
        return "negative_ai_use_statement"
    if ackish and author_disclosure:
        return "likely_ai_use_acknowledgement"
    if author_disclosure:
        return "likely_ai_use_statement"
    return "possible_ai_term"


def is_relevant_hit(hit: Hit) -> bool:
    return hit.status in {
        "likely_ai_use_acknowledgement",
        "likely_ai_use_statement",
        "mail_metadata_ai_use_statement",
    }


def find_hits(text: str, source_kind: str, source_path: Path, paper: Paper) -> list[Hit]:
    hits: list[Hit] = []
    seen: set[tuple[str, str]] = set()
    for term, pattern in AI_PATTERNS:
        for match in pattern.finditer(text):
            snippet = normalize_snippet(text, match.start())
            key = (term, snippet)
            if key in seen:
                continue
            seen.add(key)
            hits.append(
                Hit(
                    arxiv_id=paper.arxiv_id,
                    title=paper.title,
                    paper_kind=paper.kind,
                    status=classify_context(text, match.start()),
                    source_kind=source_kind,
                    source_path=str(source_path),
                    term=term,
                    snippet=snippet,
                )
            )
    return hits


def find_mail_metadata_hits(paper: Paper) -> list[Hit]:
    fields = [
        ("title", paper.title),
        ("authors", paper.authors),
        ("categories", paper.categories),
        ("comments", paper.comments),
    ]
    text = "\n".join(f"{name}: {value}" for name, value in fields if value)
    if not text:
        return []
    hits = find_hits(text, "mail_metadata", Path(paper.mail_file), paper)
    for hit in hits:
        if hit.status == "possible_ai_term":
            hit.status = "mail_metadata_ai_term"
        elif hit.status == "likely_ai_use_statement":
            hit.status = "mail_metadata_ai_use_statement"
    return hits


def scan_paper(
    paper: Paper,
    assets_dir: Path,
    download: bool,
    skip_pdf: bool,
    skip_source: bool,
    timeout: float,
    sleep: float,
    force: bool,
) -> tuple[list[Hit], list[str]]:
    paper_dir = assets_dir / paper.arxiv_id
    hits: list[Hit] = []
    errors: list[str] = []

    if not skip_source:
        source_archive = paper_dir / f"{paper.arxiv_id}.source"
        source_dir = paper_dir / "source"
        if download:
            try:
                download_url(f"https://arxiv.org/e-print/{paper.arxiv_id}", source_archive, timeout, force)
                if sleep:
                    time.sleep(sleep)
            except (urllib.error.HTTPError, urllib.error.URLError, TimeoutError) as exc:
                errors.append(f"{paper.arxiv_id}: source download failed: {exc}")
        if source_archive.exists():
            try:
                extract_source_archive(source_archive, source_dir, force)
            except Exception as exc:
                errors.append(f"{paper.arxiv_id}: source extraction failed: {exc}")
        for tex_path in tex_files(source_dir):
            try:
                text = strip_latex_comments(read_text(tex_path))
                hits.extend(find_hits(text, "tex", tex_path, paper))
            except Exception as exc:
                errors.append(f"{paper.arxiv_id}: TeX scan failed for {tex_path}: {exc}")

    if not skip_pdf:
        pdf_path = paper_dir / f"{paper.arxiv_id}.pdf"
        text_path = paper_dir / "pdf.txt"
        if download:
            try:
                download_url(f"https://arxiv.org/pdf/{paper.arxiv_id}", pdf_path, timeout, force)
                if sleep:
                    time.sleep(sleep)
            except (urllib.error.HTTPError, urllib.error.URLError, TimeoutError) as exc:
                errors.append(f"{paper.arxiv_id}: PDF download failed: {exc}")
        if pdf_path.exists():
            try:
                text = extract_pdf_text(pdf_path, text_path, force)
                if text is None:
                    errors.append(f"{paper.arxiv_id}: PDF scan skipped because pdftotext is not installed")
                else:
                    hits.extend(find_hits(text, "pdf", text_path, paper))
            except Exception as exc:
                errors.append(f"{paper.arxiv_id}: PDF scan failed: {exc}")

    return hits, errors


def write_json(path: Path, data: object) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def write_paper_csv(path: Path, papers: list[Paper]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(Paper.__dataclass_fields__))
        writer.writeheader()
        for paper in papers:
            writer.writerow(paper.to_dict())


def write_hits_csv(path: Path, hits: list[Hit]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(Hit.__dataclass_fields__))
        writer.writeheader()
        for hit in hits:
            writer.writerow(hit.to_dict())


def paper_hit_summary(papers: list[Paper], hits: list[Hit]) -> list[dict[str, str]]:
    papers_by_id = {paper.arxiv_id: paper for paper in papers}
    hits_by_id: dict[str, list[Hit]] = {}
    for hit in hits:
        hits_by_id.setdefault(hit.arxiv_id, []).append(hit)

    rows: list[dict[str, str]] = []
    for arxiv_id, paper_hits in sorted(hits_by_id.items()):
        paper = papers_by_id.get(arxiv_id)
        relevant_hits = [hit for hit in paper_hits if is_relevant_hit(hit)]
        statuses = sorted({hit.status for hit in paper_hits})
        terms = sorted({hit.term for hit in paper_hits})
        sources = sorted({f"{hit.source_kind}:{hit.source_path}" for hit in paper_hits})
        representative = relevant_hits[0] if relevant_hits else paper_hits[0]
        rows.append(
            {
                "arxiv_id": arxiv_id,
                "kind": paper.kind if paper else "",
                "auto_class": "probable_author_ai_use" if relevant_hits else "possible_only",
                "hit_count": str(len(paper_hits)),
                "relevant_hit_count": str(len(relevant_hits)),
                "statuses": "; ".join(statuses),
                "terms": "; ".join(terms),
                "title": paper.title if paper else representative.title,
                "sources": "; ".join(sources),
                "representative_snippet": representative.snippet,
            }
        )
    return rows


def write_candidate_csv(path: Path, rows: list[dict[str, str]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    fieldnames = [
        "arxiv_id",
        "kind",
        "auto_class",
        "hit_count",
        "relevant_hit_count",
        "statuses",
        "terms",
        "title",
        "sources",
        "representative_snippet",
    ]
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        for row in rows:
            writer.writerow(row)


def markdown_escape_cell(text: str) -> str:
    return text.replace("|", "\\|").replace("\n", " ")


def write_markdown_report(path: Path, papers: list[Paper], hits: list[Hit], errors: list[str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    likely = [hit for hit in hits if is_relevant_hit(hit)]
    lines = [
        "# arXiv AI acknowledgement scan",
        "",
        f"- Papers considered: {len(papers)}",
        f"- New submissions: {sum(1 for paper in papers if paper.kind == 'new')}",
        f"- Cross-listings included: {sum(1 for paper in papers if paper.kind == 'cross-list')}",
        f"- AI-term hits: {len(hits)}",
        f"- Likely acknowledgement/use statements: {len(likely)}",
        f"- Errors/warnings: {len(errors)}",
        "",
    ]

    if hits:
        lines.extend(
            [
                "## Hits",
                "",
                "| arXiv | kind | status | term | source | snippet |",
                "| --- | --- | --- | --- | --- | --- |",
            ]
        )
        for hit in sorted(hits, key=lambda item: (item.arxiv_id, item.status, item.source_kind)):
            source = f"{hit.source_kind}:{hit.source_path}"
            lines.append(
                "| "
                + " | ".join(
                    markdown_escape_cell(value)
                    for value in [
                        hit.arxiv_id,
                        hit.paper_kind,
                        hit.status,
                        hit.term,
                        source,
                        hit.snippet,
                    ]
                )
                + " |"
            )
        lines.append("")
    else:
        lines.extend(["No AI-related acknowledgement/use statements were found in scanned paper text.", ""])

    if errors:
        lines.extend(["## Errors and warnings", ""])
        for error in errors:
            lines.append(f"- {error}")
        lines.append("")

    lines.extend(
        [
            "## Papers",
            "",
            "| arXiv | kind | mail date | title |",
            "| --- | --- | --- | --- |",
        ]
    )
    for paper in papers:
        lines.append(
            "| "
            + " | ".join(
                markdown_escape_cell(value)
                for value in [paper.arxiv_id, paper.kind, paper.mail_date, paper.title]
            )
            + " |"
        )
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def write_candidate_markdown(path: Path, rows: list[dict[str, str]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    probable = [row for row in rows if row["auto_class"] == "probable_author_ai_use"]
    possible = [row for row in rows if row["auto_class"] == "possible_only"]
    lines = [
        "# Candidate paper review",
        "",
        f"- Candidate papers with any AI-term hit: {len(rows)}",
        f"- Auto-probable author AI-use disclosures: {len(probable)}",
        f"- Possible-only candidates needing manual dismissal/review: {len(possible)}",
        "",
        "## Auto-Probable",
        "",
    ]
    if probable:
        for row in probable:
            lines.extend(
                [
                    f"### {row['arxiv_id']} ({row['kind']})",
                    "",
                    f"- Title: {row['title']}",
                    f"- Terms: {row['terms']}",
                    f"- Statuses: {row['statuses']}",
                    f"- Sources: {row['sources']}",
                    f"- Representative snippet: {row['representative_snippet']}",
                    "",
                ]
            )
    else:
        lines.extend(["None.", ""])

    lines.extend(["## Possible Only", ""])
    if possible:
        for row in possible:
            lines.extend(
                [
                    f"### {row['arxiv_id']} ({row['kind']})",
                    "",
                    f"- Title: {row['title']}",
                    f"- Terms: {row['terms']}",
                    f"- Statuses: {row['statuses']}",
                    f"- Sources: {row['sources']}",
                    f"- Representative snippet: {row['representative_snippet']}",
                    "",
                ]
            )
    else:
        lines.extend(["None.", ""])
    path.write_text("\n".join(lines), encoding="utf-8")


def parse_args(argv: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Parse arXiv .eml mailings, exclude revisions, and scan new papers for AI-use acknowledgements."
    )
    parser.add_argument("--mail-glob", default="*.eml", help="Glob for arXiv mailing files. Default: *.eml")
    parser.add_argument("--assets-dir", default="papers", help="Cache directory for downloaded PDFs/sources.")
    parser.add_argument("--out-dir", default="results", help="Report directory.")
    parser.add_argument("--download", action="store_true", help="Download missing PDFs and source packages from arXiv.")
    parser.add_argument(
        "--no-cross-lists",
        action="store_true",
        help="Exclude new cross-listing entries. Revisions are always excluded.",
    )
    parser.add_argument("--skip-pdf", action="store_true", help="Do not download or scan PDFs.")
    parser.add_argument("--skip-source", action="store_true", help="Do not download or scan source packages.")
    parser.add_argument("--force", action="store_true", help="Refresh cached downloads/extractions/text files.")
    parser.add_argument("--timeout", type=float, default=45.0, help="Download timeout in seconds.")
    parser.add_argument("--sleep", type=float, default=3.0, help="Delay between arXiv requests in seconds.")
    parser.add_argument("--max-papers", type=int, default=0, help="Limit papers scanned, after parsing. 0 means all.")
    parser.add_argument("--only", action="append", default=[], help="Scan only this arXiv ID. Can be repeated.")
    return parser.parse_args(argv)


def main(argv: list[str]) -> int:
    import os
    if os.environ.get("ARXIV_OBS_LEGACY") != "1":
        sys.exit("DISABLED legacy path: superseded by the v2 pipeline "
                 "(destructive/unvalidated semantics; see WORKFLOW.md). "
                 "Set ARXIV_OBS_LEGACY=1 only for historical reproduction.")
    args = parse_args(argv)
    assets_dir = Path(args.assets_dir)
    out_dir = Path(args.out_dir)
    include_cross_lists = not args.no_cross_lists

    papers = collect_papers(args.mail_glob, include_cross_lists=include_cross_lists)
    if args.only:
        wanted = set(args.only)
        papers = [paper for paper in papers if paper.arxiv_id in wanted]
    if args.max_papers:
        papers = papers[: args.max_papers]

    all_hits: list[Hit] = []
    all_errors: list[str] = []
    for index, paper in enumerate(papers, start=1):
        print(f"[{index}/{len(papers)}] {paper.arxiv_id} {paper.kind}: {paper.title}", file=sys.stderr)
        all_hits.extend(find_mail_metadata_hits(paper))
        hits, errors = scan_paper(
            paper=paper,
            assets_dir=assets_dir,
            download=args.download,
            skip_pdf=args.skip_pdf,
            skip_source=args.skip_source,
            timeout=args.timeout,
            sleep=args.sleep,
            force=args.force,
        )
        all_hits.extend(hits)
        all_errors.extend(errors)

    write_json(out_dir / "new_papers.json", [paper.to_dict() for paper in papers])
    write_paper_csv(out_dir / "new_papers.csv", papers)
    write_json(out_dir / "ai_ack_hits.json", [hit.to_dict() for hit in all_hits])
    write_hits_csv(out_dir / "ai_ack_hits.csv", all_hits)
    candidate_rows = paper_hit_summary(papers, all_hits)
    write_candidate_csv(out_dir / "candidate_papers.csv", candidate_rows)
    write_candidate_markdown(out_dir / "candidate_papers.md", candidate_rows)
    write_json(out_dir / "errors.json", all_errors)
    write_markdown_report(out_dir / "ai_ack_report.md", papers, all_hits, all_errors)

    likely_count = sum(1 for hit in all_hits if is_relevant_hit(hit))
    print(
        f"Parsed {len(papers)} papers; found {len(all_hits)} AI-term hits "
        f"({likely_count} likely acknowledgement/use statements).",
        file=sys.stderr,
    )
    print(f"Wrote reports under {out_dir}/", file=sys.stderr)
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))

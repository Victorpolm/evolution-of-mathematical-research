import gzip
import io
import tarfile

from pipeline import scan


def make_tar(members: dict[str, bytes]) -> bytes:
    buf = io.BytesIO()
    with tarfile.open(fileobj=buf, mode="w:gz") as tf:
        for name, data in members.items():
            info = tarfile.TarInfo(name)
            info.size = len(data)
            tf.addfile(info, io.BytesIO(data))
    return buf.getvalue()


def test_strip_comments_basic():
    assert scan.strip_tex_comments("text % hidden\nmore") == "text \nmore"


def test_strip_comment_environment_and_iffalse():
    src = ("start \\begin{comment}ChatGPT transcript\\end{comment} mid "
           "\\iffalse secret ChatGPT \\fi end")
    out = scan.strip_tex_comments(src)
    assert "ChatGPT" not in out and "start" in out and "end" in out


def test_strip_post_end_document():
    out = scan.strip_tex_comments("body \\end{document} ChatGPT residue")
    assert "residue" not in out


def test_url_percent_protected():
    src = r"see \url{https://chat.example/a%20b} % real comment"
    out = scan.strip_tex_comments(src)
    assert "a%20b" in out and "real comment" not in out


def test_escaped_percent_not_a_comment():
    # \% is literal, not a comment start: the rest of the line survives
    assert "of cases" in scan.strip_tex_comments(r"we get 100\% of cases")


def test_scan_archive_finds_disclosure_and_skips_comments():
    tar = make_tar({
        "main.tex": b"\\documentclass{article} We thank ChatGPT for help. "
                    b"% secret Claude note\n\\end{document}",
    })
    hits, notes = scan.scan_archive_bytes(tar)
    assert any(h["term"] == "ChatGPT" for h in hits)
    assert not any(h["term"] == "Claude" for h in hits)


def test_ancillary_member_flagged():
    tar = make_tar({"main.tex": b"\\documentclass{article} nothing here",
                    "chatgpt_transcript.json": b"{}"})
    hits, _ = scan.scan_archive_bytes(tar)
    assert any(h["term"] == "ancillary-file" for h in hits)


def test_large_member_skip_noted_and_not_ok():
    big = b"\\documentclass{article}" + b"x" * (scan.MAX_MEMBER_BYTES + 1)
    tar = make_tar({"huge.tex": big, "main.tex": b"\\documentclass{article} ok"})
    _, notes = scan.scan_archive_bytes(tar)
    assert any(n.startswith("skipped-large:huge.tex") for n in notes)
    # a paper with skipped potentially-rendered members is NOT scan-complete
    assert scan.item_status(None, notes) == "incomplete:members-skipped"


def test_item_status_mapping():
    assert scan.item_status(None, []) == "ok"
    assert scan.item_status("ValueError: boom", []) == "error:ValueError"
    assert scan.item_status(None, ["skipped:pdf-tar-member"]) == "skipped:pdf-tar-member"
    assert scan.item_status(None, ["unknown-format:not-tex"]) == "error:UnknownFormat"
    assert scan.item_status(None, ["skipped-budget:x:99"]) == "incomplete:members-skipped"


def test_unknown_gz_content_is_not_a_clean_negative():
    hits, notes = scan.scan_archive_bytes(gzip.compress(b"\x00\x01binary junk"))
    assert not hits and any(n.startswith("unknown-format") for n in notes)


def test_oversized_single_gz_hits_budget():
    big = b"\\documentclass{article}" + b"y" * (scan.MAX_TOTAL_BYTES + 1)
    _, notes = scan.scan_archive_bytes(gzip.compress(big))
    assert any(n.startswith("skipped-budget:single-gz") for n in notes)


def test_single_gz_file():
    data = gzip.compress(b"\\documentclass{article} We used Claude Opus to "
                         b"draft Section 2.")
    hits, _ = scan.scan_archive_bytes(data)
    assert any(h["term"] == "Claude" for h in hits)


def test_read_blob_tar_member(tmp_path, monkeypatch):
    inner = gzip.compress(b"\\documentclass{article} hello")
    monthly = tmp_path / "math_2308.tar"
    with tarfile.open(monthly, "w") as tf:
        info = tarfile.TarInfo("2308/2308.00001.gz")
        info.size = len(inner)
        tf.addfile(info, io.BytesIO(inner))
    monkeypatch.setattr(scan.db, "PROJECT_ROOT", tmp_path)
    scan._TAR_CACHE.clear()
    blob = scan.read_blob("math_2308.tar::2308/2308.00001.gz")
    assert blob == inner
    scan._TAR_CACHE.clear()

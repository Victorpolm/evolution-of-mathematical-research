import sqlite3

import pytest

from pipeline import db, migrate


def test_fresh_db_initialized_to_head(tmp_path):
    con = db.connect(tmp_path / "new.db")
    assert migrate.current_version(con) == migrate.HEAD_VERSION


def test_apply_pending_idempotent(tmp_path):
    con = sqlite3.connect(tmp_path / "x.db")
    first = migrate.apply_pending(con, verbose=False)
    assert first == [m[0] for m in migrate.MIGRATIONS]
    assert migrate.apply_pending(con, verbose=False) == []


def test_v1_database_detected_and_refused(tmp_path):
    path = tmp_path / "old.db"
    con = sqlite3.connect(path)
    con.executescript(migrate.V1_BASELINE)
    con.commit()
    con.close()
    with pytest.raises(db.SchemaBehindError):
        db.connect(path)


def test_v1_stamped_retroactively(tmp_path):
    path = tmp_path / "old.db"
    con = sqlite3.connect(path)
    con.executescript(migrate.V1_BASELINE)
    applied = migrate.apply_pending(con, verbose=False)
    assert 1 not in applied  # v1 stamped, not re-run
    assert migrate.current_version(con) == migrate.HEAD_VERSION


def test_migrations_are_additive_only():
    import inspect

    for _, _, sql in migrate.MIGRATIONS:
        text = sql if isinstance(sql, str) else inspect.getsource(sql)
        low = text.lower()
        assert "drop table" not in low and "delete from" not in low
        assert "update " not in low


def test_v9_adds_response_sha256_on_fresh_db(tmp_path):
    con = db.connect(tmp_path / "new.db")
    cols = [r[1] for r in con.execute("PRAGMA table_info(api_attempts)")]
    assert cols.count("response_sha256") == 1


def test_v9_noops_when_column_already_exists(tmp_path):
    # the live DB got the column ad hoc when response hashing landed
    # (review-12); v9 must stamp the version without a duplicate-column error
    con = sqlite3.connect(tmp_path / "x.db")
    migrate.apply_pending(con, verbose=False)
    con.execute("DELETE FROM schema_version WHERE version = 9")
    con.commit()
    assert migrate.current_version(con) == 8
    assert migrate.apply_pending(con, verbose=False) == [9]
    cols = [r[1] for r in con.execute("PRAGMA table_info(api_attempts)")]
    assert cols.count("response_sha256") == 1

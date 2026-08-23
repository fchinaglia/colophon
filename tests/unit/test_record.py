# SPDX-License-Identifier: MIT
"""The chain, and the guard that keeps it checkable outside Python."""
import json

from conftest import run


def test_chain_verifies_and_reports_the_root(workspace):
    wd = workspace("example", only={"record.py"})
    r = run(wd, "record.py", "--verify")
    assert r.returncode == 0
    assert "chain intact" in r.stdout


def test_a_tampered_event_breaks_the_chain_at_its_index(workspace):
    wd = workspace("example", only={"record.py"})
    log = wd / "events.jsonl"
    lines = log.read_text(encoding="utf-8").splitlines()
    row = json.loads(lines[2])
    row["payload"] = {"tampered": True}
    lines[2] = json.dumps(row, ensure_ascii=False, sort_keys=True)
    log.write_text("\n".join(lines) + "\n", encoding="utf-8")
    r = run(wd, "record.py", "--verify")
    assert r.returncode != 0
    assert "BROKEN at event 2" in r.stdout, r.stdout


def test_the_guard_refuses_what_a_browser_cannot_check(workspace):
    """A float in a payload cannot be reproduced outside Python: after a JavaScript
    JSON.parse, 94.0 and 94 are the same value. It is not repairable afterwards, because
    the register is append-only — so it is refused at the door, not warned about."""
    wd = workspace("example", only={"record.py"})
    before = (wd / "events.jsonl").read_text(encoding="utf-8")
    for payload in ('{"pct": 94.0}', '{"a": {"b": 0.5}}', '{"xs": [1, 2.5]}',
                    '{"n": 9007199254740992}'):
        r = run(wd, "record.py", '{"type":"status","payload":' + payload + '}')
        assert r.returncode == 1, f"{payload} was accepted"
        assert "not recorded" in r.stderr
    assert (wd / "events.jsonl").read_text(encoding="utf-8") == before, \
        "a refused event must leave the register untouched"


def test_the_guard_accepts_the_boundary_and_quoted_numbers(workspace):
    wd = workspace("example", only={"record.py"})
    for payload in ('{"n": 9007199254740991}', '{"pct": "94.0"}', '{"note": "citta 94.0"}'):
        r = run(wd, "record.py", '{"type":"status","payload":' + payload + '}')
        assert r.returncode == 0, f"{payload} was refused: {r.stderr}"
    assert run(wd, "record.py", "--verify").returncode == 0

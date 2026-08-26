# SPDX-License-Identifier: MIT
"""The chain, and the guard that keeps it checkable outside Python."""
import json
import os

from conftest import SCRIPTS, run


def spaced(obj):
    """The event as the skill records it: a space after every opening brace, so
    the command does not carry `{"` and is not read as obfuscation."""
    return json.dumps(obj, ensure_ascii=False).replace('{"', '{ "')


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


# ------------------------------------------------------------------------ the red list

def redlisted(wd, tmp_path, *entries):
    """A red list for the case in wd, in a config directory of our own."""
    cfg = tmp_path / "cfg"
    d = cfg / "colophon" / "redlists"
    d.mkdir(parents=True)
    uid = json.loads((wd / "case.json").read_text(encoding="utf-8"))["case_uid"]
    (d / f"{uid}.txt").write_text("# names that must not travel\n" + "\n".join(entries),
                                  encoding="utf-8")
    return {"XDG_CONFIG_HOME": str(cfg)}


def with_uid(wd, uid="a-case"):
    p = wd / "case.json"
    c = json.loads(p.read_text(encoding="utf-8"))
    c["case_uid"] = uid
    p.write_text(json.dumps(c, ensure_ascii=False), encoding="utf-8")
    return wd


def test_a_red_list_hit_warns_and_records(workspace, tmp_path):
    """It warns; it does not refuse. What may not be said about a third party is a
    judgement, and the only part a machine decides is whether a string the author named
    in advance is present."""
    wd = with_uid(workspace("example", only={"record.py"}))
    env = redlisted(wd, tmp_path, "Mario Rossi")
    before = len((wd / "events.jsonl").read_text(encoding="utf-8").splitlines())
    r = run(wd, "record.py", json.dumps({
        "type": "editorial_decision", "actor": "ai", "phase": "—",
        "payload": {"change": "R01",
                    "note": "Mario Rossi ha chiesto di togliere il riferimento"}},
        ensure_ascii=False), env=env)
    assert r.returncode == 0, r.stdout + r.stderr
    after = len((wd / "events.jsonl").read_text(encoding="utf-8").splitlines())
    assert after == before + 1, "the event was not recorded"
    assert "something on your list is in what I just recorded" in r.stderr
    assert "comes back at the last read" in r.stderr
    assert "payload" not in r.stderr, "a path the author cannot act on yet"


def test_the_warning_never_prints_what_matched(workspace, tmp_path):
    """Printing the name is the harm arriving through the guard: it writes it to a
    terminal and into whatever transcript is running."""
    wd = with_uid(workspace("example", only={"record.py"}))
    env = redlisted(wd, tmp_path, "Mario Rossi")
    # --json, because the row is what this asserts on: since #34 the default output is
    # one line, so that an author writing an article is not handed an event and a hash
    # at every exchange.
    r = run(wd, "record.py", "--json", spaced({
        "type": "register_note", "actor": "ai", "phase": "—",
        "payload": {"note": "parlato con Mario Rossi"}}), env=env)
    assert r.returncode == 0
    assert "Mario Rossi" not in r.stderr
    assert "Mario Rossi" in r.stdout, "the recorded row is unchanged, and goes to stdout"


def test_the_match_folds_case_and_accents_but_keeps_word_boundaries(workspace, tmp_path):
    """Peròtti matches Perotti; Rossini does not match Rossi. The boundary costs `M.R.`
    and a misspelling, and not having one costs an author who learns to delete events."""
    wd = with_uid(workspace("example", only={"record.py"}))
    env = redlisted(wd, tmp_path, "Perotti", "Rossi")
    def note(text):
        return run(wd, "record.py", json.dumps({
            "type": "register_note", "actor": "ai", "phase": "—",
            "payload": {"note": text}}, ensure_ascii=False), env=env)
    assert "on your list" in note("una nota su PERÒTTI").stderr
    assert "on your list" in note("il Rossi ha deciso").stderr
    assert "on your list" not in note("Rossini era un compositore").stderr
    assert "on your list" not in note("nulla di sensibile qui").stderr


def test_no_list_no_warning(workspace):
    """The whole feature costs nothing when the author declared nothing."""
    wd = with_uid(workspace("example", only={"record.py"}))
    r = run(wd, "record.py", json.dumps({
        "type": "register_note", "actor": "ai", "phase": "—",
        "payload": {"note": "Mario Rossi"}}, ensure_ascii=False))
    assert r.returncode == 0 and "on your list" not in r.stderr


def test_the_red_list_is_not_part_of_the_canonical_refusals(workspace, tmp_path):
    """spec/canonical.md §4 is normative about what append() refuses and a second
    implementation must reproduce it. A machine-local list is reproducible by nobody."""
    src = open(os.path.join(SCRIPTS, "record.py"), encoding="utf-8").read()
    body = src[src.index("def violations("):src.index("def redlist_path(")]
    assert "redlist" not in body, "the red list leaked into the normative refusals"


def test_one_line_however_many_fields_matched(workspace, tmp_path):
    """Case 002's seq 68 matches in five fields. Five lines of warning about one event
    is an interruption in a conversation where somebody is writing an article."""
    wd = with_uid(workspace("example", only={"record.py"}))
    env = redlisted(wd, tmp_path, "quattro", "cinque", "sei")
    r = run(wd, "record.py", spaced({
        "type": "editorial_decision", "actor": "ai", "phase": "—",
        "payload": {"change": "Z01", "a": "quattro elementi", "b": "cinque cose",
                    "c": "sei dettagli", "d": "nulla"}}), env=env)
    assert r.returncode == 0
    assert r.stderr.count("on your list") == 1
    assert len(r.stderr.strip().splitlines()) == 3


def test_an_event_can_come_from_a_file_outside_the_case(workspace, tmp_path):
    """A JSON object on a command line carries the sequence `{"`, which Claude Code's
    command analysis rejects as expansion obfuscation — on every event of every case, in
    a conversation where somebody is writing an article. Measured: braces alone pass,
    quotes alone pass, the two together do not, and it makes no difference whether they
    sit in an argument or in the body of a heredoc. `--file` is the shape with neither."""
    wd = workspace("example", only={"record.py"})
    before = len((wd / "events.jsonl").read_text(encoding="utf-8").splitlines())
    src = tmp_path / "outside.json"
    src.write_text(json.dumps({"type": "status", "actor": "system", "phase": "—",
                               "payload": {"note": "from a file"}}), encoding="utf-8")
    r = run(wd, "record.py", "--file", str(src))
    assert r.returncode == 0, r.stderr
    rows = (wd / "events.jsonl").read_text(encoding="utf-8").splitlines()
    assert len(rows) == before + 1
    assert json.loads(rows[-1])["payload"]["note"] == "from a file"
    assert run(wd, "record.py", "--verify").returncode == 0


def test_a_file_inside_the_case_is_refused(workspace):
    """The closing manifest covers the case folder. A scratch event left inside it is a
    file no manifest covers: `build_bundle.py` withholds it, and it stays in the sealed
    case as the remains of the last event recorded."""
    wd = workspace("example", only={"record.py"})
    src = wd / "event.json"
    src.write_text('{"type": "status", "actor": "system", "phase": "—"}', encoding="utf-8")
    r = run(wd, "record.py", "--file", "event.json")
    assert r.returncode != 0
    assert "inside the case folder" in r.stderr
    assert "manifest" in r.stderr


def test_the_command_line_form_still_records(workspace):
    """A sealed case carries its own copy of this script and has to keep behaving as it
    did on the day it was sealed."""
    wd = workspace("example", only={"record.py"})
    r = run(wd, "record.py",
            '{"type": "status", "actor": "system", "phase": "—", "payload": {}}')
    assert r.returncode == 0, r.stderr
    assert run(wd, "record.py", "--verify").returncode == 0

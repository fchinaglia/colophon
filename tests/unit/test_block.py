# SPDX-License-Identifier: MIT
"""build_block.py — the disclosure block, generated instead of assembled.

disclosures.md specified this shape exactly and nothing built it, so case 001 shipped a
full-width, body-size, stacked version of a block the method already prescribed. Every
assertion here is one of that specification's rules.
"""
import json
import os
import re

import pytest

from conftest import run

ONLY = {"record.py", "measure.py", "build_icon.py", "build_note.py", "build_block.py"}


@pytest.fixture
def case(workspace):
    return workspace("example", only=ONLY)


def block(wd, *argv):
    r = run(wd, "build_block.py", *argv)
    assert r.returncode == 0, r.stdout + r.stderr
    return r.stdout


def test_the_two_percentages_are_the_only_thing_in_bold(case):
    """One treatment for all five lines, only the percentages bold: a block that raises
    its voice at the foot of an article puts the reader on the defensive."""
    out = block(case, "--form", "html")
    body = out.split("</style>", 1)[1]
    assert body.count("<b>") == 2, body
    assert re.search(r"<b>\d+%</b> · human ideas <b>\d+%</b>", body), body


def test_the_icon_is_set_in_absolute_units(case):
    """At a percentage, a narrow column makes the four labels illegible — the one
    failure the icon cannot survive, because it looks like a claim while being none."""
    out = block(case, "--form", "html")
    assert re.search(r"\.icon\s*\{[^}]*width:\s*\d+mm", out), out
    assert "%" not in re.search(r"\.colophon \.icon \{[^}]*\}", out).group(0)


def test_the_block_is_a_table_and_the_cells_align_to_the_top(case):
    """Older HTML-to-PDF engines drop flexbox; and with vertical centring a note of a
    different length shifts the icon, so the block stops looking like the same object
    across cases."""
    out = block(case, "--form", "html")
    assert "<table class=\"colophon\">" in out
    assert "flex" not in out
    assert "vertical-align: top" in out


def test_the_root_can_break(case):
    """The root is a sixty-four-character word with nowhere to hyphenate, and without
    this a narrow column pushes it straight out of the block."""
    assert "overflow-wrap: anywhere" in block(case, "--form", "html")


def test_the_technical_line_is_not_wrapped_twice(case):
    """build_note.py already returns a <p class="technical">. Nesting a block element
    inside itself is unnested by the browser into two empty paragraphs and a stray line."""
    out = block(case, "--form", "html")
    assert out.count('<p class="technical">') == 1, out


def test_the_quadrant_name_stays_english_in_italian(case):
    """Three of the four names are the classes of LLM-DetectAIve; translated, they stop
    pointing at the taxonomy they quote."""
    out = block(case, "--form", "text", "--lang", "it")
    assert out.startswith("human written"), out
    assert "parole umane" in out and "idee umane" in out


def test_the_gap_sentence_drops_when_the_axes_agree(case):
    """With nothing to explain it is filler."""
    kpi = json.load(open(os.path.join(case, "kpi.json"), encoding="utf-8"))
    kpi["ai_ideational"] = kpi["ai_lexical"]
    json.dump(kpi, open(os.path.join(case, "kpi.json"), "w", encoding="utf-8"))
    out = block(case, "--form", "text")
    assert "more words than it brought ideas" not in out
    assert "I stand behind" in out, "responsibility is not conditional"


def test_the_gap_sentence_follows_the_direction_of_the_gap(case):
    kpi = json.load(open(os.path.join(case, "kpi.json"), encoding="utf-8"))
    kpi["ai_lexical"], kpi["ai_ideational"] = 5.0, 60.0
    json.dump(kpi, open(os.path.join(case, "kpi.json"), "w", encoding="utf-8"))
    out = block(case, "--form", "text")
    assert "The ideas came from the model" in out, out


def test_the_boundary_warning_appears_only_near_an_edge(case):
    kpi = json.load(open(os.path.join(case, "kpi.json"), encoding="utf-8"))
    kpi["ai_lexical"], kpi["ai_ideational"] = 48.0, 20.0
    json.dump(kpi, open(os.path.join(case, "kpi.json"), "w", encoding="utf-8"))
    out = block(case, "--form", "text")
    assert "points from the boundary" in out, out


def test_the_essential_form_keeps_the_numbers_and_drops_the_rest(case):
    """For a card or a newsletter footer. It is the weakest of the three, because
    responsibility survives only if it is said."""
    out = block(case, "--form", "text", "--essential")
    assert "human words" in out
    assert "I stand behind" not in out
    assert "spans" not in out


def test_it_refuses_a_measurement_that_never_passed_its_checks(case):
    """measure.py refuses to write one, so a kpi.json saying otherwise was kept or
    edited — and publishing from it puts numbers on a page no check ever passed."""
    kpi = json.load(open(os.path.join(case, "kpi.json"), encoding="utf-8"))
    kpi["integrity"] = False
    json.dump(kpi, open(os.path.join(case, "kpi.json"), "w", encoding="utf-8"))
    r = run(case, "build_block.py", "--form", "text")
    assert r.returncode != 0
    assert "reconstruction check failed" in r.stdout + r.stderr


def test_the_svg_form_is_wide_enough_for_the_root(case):
    """An image that clips its own root prints a hash the reader cannot compare."""
    out = block(case, "--form", "svg")
    w = float(re.search(r'viewBox="0 0 ([\d.]+) ', out).group(1))
    root = re.search(r"root ([0-9a-f]{64})", out).group(0)
    assert w >= 239 + len(root) * 5.4, f"{w} is too narrow for {len(root)} characters"


def test_the_inline_icon_form_carries_the_quadrant(case):
    """A document that travels without its folder cannot fetch icon.svg."""
    assert run(case, "build_icon.py").returncode == 0
    out = block(case, "--form", "html", "--inline-icon")
    assert "<svg" in out and "<img" not in out


def test_the_thousands_separator_follows_the_language(case):
    """"1,096 parole" reads to an Italian eye as one thousand and ninety-six
    thousandths. The word count is the first number the reader meets."""
    import json as _json
    kpi = _json.load(open(os.path.join(case, "kpi.json"), encoding="utf-8"))
    kpi["words"] = 1096
    _json.dump(kpi, open(os.path.join(case, "kpi.json"), "w", encoding="utf-8"))
    assert "1.096 parole" in block(case, "--form", "text", "--lang", "it")
    assert "1,096 words" in block(case, "--form", "text", "--lang", "en")


def test_the_line_states_the_route_and_there_are_two(case):
    """"signed and inspectable register" said two things and checked one: a register with
    no route is not inspectable by the reader holding the document.

    There is one route and it is the bundle, so there are two forms: enclosed, or the
    admission that nothing is. An address is not one of them — the case metadata carries
    none and the scripts read none, which is what this test pins."""
    import json as _json
    cj = os.path.join(case, "case.json")
    d = _json.load(open(cj, encoding="utf-8"))
    d["case_uid"] = "a-case"
    _json.dump(d, open(cj, "w", encoding="utf-8"), ensure_ascii=False)
    # build_note.py names a seal only if its file is on disk; the wording under test is
    # the sealed one, and an unsealed register says so instead and says nothing else.
    open(os.path.join(case, "events.jsonl.sig"), "w").write("x")

    held = block(case, "--form", "text")
    assert "not enclosed" in held
    assert "verify.html" not in held

    tar = os.path.join(os.path.dirname(case), "colophon-a-case.tar")
    r = run(case, "build_block.py", "--form", "text", "--attached")
    assert r.returncode != 0, "a line naming an enclosure that does not exist"
    assert "there is none" in r.stdout + r.stderr

    open(tar, "wb").write(b"not really a tar, but it is on disk")
    attached = block(case, "--form", "text", "--attached")
    assert "enclosed" in attached and "not enclosed" not in attached
    assert "colophon-a-case.tar" in attached

    # An address in the metadata is not a route: the key is dead and the line ignores it.
    d["verification_url"] = "https://example.com/c/x/"
    d["register_url"] = "https://example.com/c/x/"
    _json.dump(d, open(cj, "w", encoding="utf-8"), ensure_ascii=False)
    ignored = block(case, "--form", "text")
    assert "example.com" not in ignored, "an address must never reach the reader"
    assert "not enclosed" in ignored
    assert run(case, "build_block.py", "--form", "text",
               "--url", "https://example.com/c/x/").returncode != 0, \
        "--url is gone; a flag that silently does nothing is worse than one that errors"

    for form in (held, attached, ignored):
        assert "root " in form, "the root is what makes two copies comparable"


def test_the_card_never_clips_a_line(case):
    """The first render of this form clipped the boundary warning off the right edge —
    the one line whose whole job is to stop a reader over-reading the label. Lines wrap
    rather than the note shrinking: a card has vertical room, and the note is what a
    reader actually reads."""
    import re as _re
    out = block(case, "--form", "card", "--ratio", "4:5",
                "--gap", "una frase molto lunga che non entra su una riga sola e deve "
                         "quindi andare a capo invece di uscire dal bordo destro")
    w = float(_re.search(r'viewBox="0 0 ([\d.]+) ', out).group(1))
    m = 0.075 * w
    for t in _re.findall(r'<text[^>]*font-size="(\d+)"[^>]*>(.*?)</text>', out, _re.S):
        size, body = int(t[0]), _re.sub(r"<[^>]+>", "", t[1])
        assert len(body) * size * 0.52 <= w - 2 * m + 1, f"riga fuori dal bordo: {body!r}"


def test_a_landscape_card_refuses_rather_than_shrinking_the_icon(case):
    """Below a hundred pixels a side the four labels become illegible, and an unreadable
    quadrant is worse than no icon at all: it looks like a claim while being none."""
    r = run(case, "build_block.py", "--form", "card", "--ratio", "1.91:1")
    assert r.returncode != 0
    assert "illegible" in r.stdout + r.stderr
    assert "--form svg" in r.stdout + r.stderr, "a refusal has to name what to do instead"


def test_the_card_keeps_the_whole_root(case):
    """A clipped root cannot be compared, and comparing is the only thing a root is for."""
    import re as _re
    out = block(case, "--form", "card")
    root = _re.search(r"root ([0-9a-f]{64})", out)
    assert root, "the card dropped or truncated the root"

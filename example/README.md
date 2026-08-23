# A worked example

A small case you can run end to end, to see what Colophon produces before using it
on your own writing.

```bash
python3 record.py --verify     # the chain is intact
python3 measure.py             # reconstruction and coverage checks, then the two axes
python3 build_icon.py          # icon.svg, generated from kpi.json
python3 build_page.py          # verification.html, the page a reader opens
python3 build_note.py          # the technical line that closes the note
```

Open `verification.html` in a browser afterwards.

## Read this before drawing conclusions from the numbers

**This register is a synthetic fixture.** It was written to exercise the pipeline,
not during a real writing session — which is precisely what the method tells you
never to do. The numbers demonstrate the output format. They are not a measurement,
and `case.json` says so in `extra_notes`.

A real case looks the same, with one difference that is the whole point: its events
were written while the text was being written.

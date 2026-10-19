# Incident: gap_check.py crashed on a malformed log line

| | |
|---|---|
| Date | 2026-10-18 |
| Priority | P3 |
| Status | Mitigated, follow-up open (logged retrospectively) |
| Service | infra-labs `gap_check.py` |

## Summary

`gap_check.py` crashed with a `ValueError` when the log file ended in
a line containing only a space. Lines that are too short are now
skipped with a warning. Two related cases are still open.

## Symptom

After rewriting `sample.log` to match the production log format,
running `gap_check.py` on it stopped with a traceback from
`datetime.strptime` instead of reporting gaps.

## Investigation

1. Read the traceback. The error showed `strptime` being asked to
   parse `' '`, a single space, rather than a timestamp.
2. Found the line. The last line of the file contained only a
   space. The script takes the first 13 characters of every line as
   an hour key, so this line added `' '` to the set of hours seen.
3. Explained why it crashed at the start, not the end. A space
   sorts before digits, so `' '` became the earliest "hour", and
   parsing it as a date failed.

## Root cause

The script assumed every line starts with a valid timestamp and never
checked.

## Fix

Lines with three or fewer fields are now skipped, with a warning
naming the line written to stderr. Re-ran the known-answer tests on
`sample.log` afterwards.

## Prevention

- Open: a line with four or more words of junk still gets through,
  and an empty file still crashes. Planned fix: try to parse each
  timestamp with `strptime` inside `try/except ValueError`, skip and
  warn on failure, and report "no valid lines" for an empty file.
- Habit: test with broken input on purpose, not only clean
  sample data.

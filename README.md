# infra-labs

Operations work on my [market-tracker](https://github.com/finley-matthew/market-tracker) service: tools that check the health of its logs and find missed runs, write-ups of real faults, and an issue tracker with priorities and target resolution times.

market-tracker is the service; this repo is what I use to run, monitor and fix it.

## Tools

All three read a log in market-tracker's format (see its [log format](https://github.com/finley-matthew/market-tracker#log-format)). The Python tools use only the standard library. Each one prints usage to stderr and exits with code 1 if no log file is given.

| Tool | What it answers |
|---|---|
| `errors_by_type.sh` | Which errors happen most? |
| `health_report.py` | What share of runs succeeded, and what failed? |
| `gap_check.py` | Did any scheduled runs not happen at all? |

### errors_by_type.sh

A Bash pipeline: finds `ERROR` lines, takes the error type from field 4, and counts each type, most frequent first.

```
$ ./errors_by_type.sh sample.log
      3 Timeout
      1 ServerError
      1 ConnectionError
```

### health_report.py

Success rate, plus errors grouped by type. Lines that don't fit the log format are skipped with a warning to stderr that gives the line number, instead of crashing or being counted wrongly.

```
$ python3 health_report.py sample.log
Success rate: 58.3% (7 of 12 runs)
Error type: Timeout. Count: 3
Error type: ConnectionError. Count: 1
Error type: ServerError. Count: 1
```

### gap_check.py

The scheduled job should log exactly once an hour. This builds the full list of expected hours between the first and last log entries, and reports any hour with no entry at all. A missing run leaves no error line, so the other two tools can't see it.

```
$ python3 gap_check.py sample.log
The following timestamps are missing logs: ['2026-10-06 17', '2026-10-06 18', ..., '2026-10-07 07']
15 gaps found in sample.log
```

On the real log, this found a six-hour gap on 13 October (see [Incidents](#incidents)).

**Known limits:** it only checks between the first and last entry, so an outage still in progress at the end of the log isn't reported. A junk line with four or more fields, or an empty file, still causes a crash; this is tracked as an open issue.

## Testing with known answers

[`sample.log`](sample.log) is 12 lines in the production format, written so the right answers are known in advance: 7 successful runs, 5 errors (3 `Timeout`, 1 `ConnectionError`, 1 `ServerError`), and a 15-hour overnight gap. After every change, all three tools are re-run on it and the output is checked against those numbers.

`health_report.py` was also tested against deliberately broken input: an empty file, a blank line, an unknown log level (`WARNING`), a line that's too short, bad lines in the middle of the file (to check the reported line numbers stay correct), a single run, and a file containing only bad lines.

## Incidents

Each write-up follows the same structure: summary, symptom, investigation, root cause, fix, prevention. They were written retrospectively, shortly after each fault.

| Date | Incident | Priority | Status |
|---|---|---|---|
| 2026-10-13 | [Six-hour gap in hourly price collection (host offline)](incidents/2026-10-13-scheduler-host-offline.md) | P1 | Resolved |
| 2026-10-17 | [Gold API read timeout](incidents/2026-10-17-gold-api-read-timeout.md) | P3 | Resolved |
| 2026-10-18 | [gap_check.py crashed on a malformed log line](incidents/2026-10-18-gap-check-crash-on-junk-line.md) | P3 | Mitigated, follow-up open |

## Issue tracking

Faults are tracked as [GitHub Issues](https://github.com/finley-matthew/infra-labs/issues?q=is%3Aissue), each labelled with a priority and a target resolution time:

| Priority | Meaning | Target |
|---|---|---|
| P1 | Service down or data lost | 24 hours |
| P2 | Service degraded | 3 days |
| P3 | Minor fault or tooling issue | 7 days |

There are no users other than me, so these are targets I set myself in order of P1/P2/P3 priority.

## Conventions

- Errors and warnings go to stderr; results go to stdout. So `> results.txt` captures only the results.
- Python is checked with `pycodestyle` (line limit 99, set in `setup.cfg`).
- Every file ends with a final newline.

## Roadmap

- Fix the open `gap_check.py` issue: validate every timestamp, and handle empty files cleanly.
- Merge gap detection into `health_report.py`, and report outages as time ranges rather than lists of hours.
- Catch an outage that's still in progress at the end of the log.
- Break-fix labs on a systemd service (stop it, misconfigure it, diagnose it with `systemctl` and `journalctl`), each logged as an Issue with a write-up.
- An `apt` patching runbook: check, patch, verify the version, roll back.
- A software RAID lab with `mdadm` on a VM: build an array, fail a disk, rebuild it.
- `pytest` tests for the tools, run by GitHub Actions on every push.

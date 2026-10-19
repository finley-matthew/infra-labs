# Incident: six-hour gap in hourly price collection

| | |
|---|---|
| Date | 2026-10-13 |
| Priority | P1 |
| Status | Resolved (logged retrospectively) |
| Service | market-tracker `live_price.py` (hourly cron job in WSL) |

## Summary

Six consecutive hourly price collections (05:00–10:00) did not run on
13 October because the host machine, and therefore WSL and cron, was
switched off. The service resumed automatically at 11:00 once the
machine was back on. Prices for the missing hours were not collected
and cannot be recovered.

## Symptom

While reviewing `tracker.log` for a health report, I noticed there were
no entries between the 04:00 run and the 11:00 run on 13 October. There
were no error lines in that window either: the runs were simply absent.

## Investigation

1. **Ruled out a script crash.** I compared line counts in `cron.log`
   (cron's output from each run) and `tracker.log` (the script's own
   log). They matched, and neither had anything in the gap. A crashing
   script would still have been started by cron and left a traceback in
   `cron.log`, so cron was not running the job at all.
2. **Ruled out a bad crontab entry.** A broken schedule line would fail
   every hour, not for one six-hour window followed by normal runs.
3. **Checked when the system last started.** `uptime -s` inside WSL
   returned `2026-10-13 10:21:08`, which matches the end of the gap: the
   first run after start-up was 11:00. The machine is normally shut
   down shortly after 04:00.
4. **Confirmed independently.** On 14 October I wrote `gap_check.py`,
   which builds the full list of expected hourly runs between the first
   and last log entries and compares it with what was actually logged.
   Result: 35 expected, 29 logged, 6 missing, all on 13 October from
   05:00 to 10:00.

## Root cause

cron runs inside WSL, and WSL only runs while the host PC is on. The PC
was switched off from about 04:00 until about 10:20, so no scheduled
runs could happen. cron does not catch up on missed runs.

## Fix

No code change was needed. The service resumed on its own at the next
scheduled run (11:00) once the machine and WSL were running again. The
six missed data points could not be recovered.

## Prevention

- **Done:** `gap_check.py` (in this repo) now detects missing hourly
  runs, so a gap like this is found by a tool rather than by eye.
- **Planned:** move the job to an always-on host (an AWS EC2 instance)
  so it doesn't depend on my PC being on.
- **Planned:** run the job as a systemd timer with `Persistent=true`,
  which runs a missed job once at start-up (it does not backfill every
  missed hour).
- **Known limit of the detector:** `gap_check.py` only checks between
  the first and last log entry, so an outage still in progress at the
  end of the log isn't reported yet.

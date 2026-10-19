# Incident: Gold API read timeout

| | |
|---|---|
| Date | 2026-10-17 |
| Priority | P3 |
| Status | Resolved, no action needed (logged retrospectively) |
| Service | market-tracker `live_price.py` (hourly cron job in WSL) |

## Summary

One hourly price fetch at 01:00 on 17 October failed with a read
timeout from the Gold API. The next run at 02:00 succeeded without
intervention. One data point was lost.

## Symptom

Running `health_report.py` on `tracker.log` showed one failed run out
of 57 (98.2% success). The failing line was:

    2026-10-17 01:00 ... ERROR Timeout XAU ReadTimeout

## Investigation

1. Confirmed the counts by hand. `grep -c INFO` returned 56 and
   `grep -c ERROR` returned 1, matching the report.
2. Identified the type of timeout. The script logs the exception
   class name. `ReadTimeout` means the connection to the server
   succeeded but no response arrived within the 5-second timeout.
   A `ConnectTimeout` would have meant the connection itself failed,
   pointing at my network or DNS rather than the server.
3. Checked for recovery. The 02:00 entry was a normal `INFO` line,
   so the service recovered by itself. A missing line after the error
   would have meant it stopped running altogether, which "no errors"
   alone wouldn't show.

## Root cause

The Gold API was slow to respond at 01:00, beyond the script's
5-second timeout. The cause on the provider's side is unknown and
outside my control.

## Fix

None needed. The script did what it should: it logged the failure type and
exited, and the next scheduled run succeeded.

## Prevention

- Considered: a single retry after a short delay, which would
  likely have recovered this data point.
- Considered: alerting only after two or more consecutive
  failures, so one-off timeouts like this don't cause noise.
- Kept: the 5-second timeout, so a slow server can't leave the
  script hanging.

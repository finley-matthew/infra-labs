import sys
from datetime import datetime, timedelta

if len(sys.argv) < 2:
    print("Usage: python3 gap_check.py <logfile>", file=sys.stderr)
    sys.exit(1)

log_path = sys.argv[1]

seen = set()
with open(log_path) as f:
    for count, line in enumerate(f, 1):
        split = line.split()
        if len(split) > 3:
            seen.add(line[:13])
        else:
            print(f"Unexpected content on line {count}, skipping line.", file=sys.stderr)

first = sorted(seen)[0]
last = sorted(seen)[-1]

start = datetime.strptime(first, "%Y-%m-%d %H")
end = datetime.strptime(last, "%Y-%m-%d %H")

expected = set()
current = start

while current <= end:
    expected.add(current.strftime("%Y-%m-%d %H"))
    current += timedelta(hours=1)

gaps = expected - seen
print(f"The following timestamps are missing logs: {sorted(gaps)}")
print(f"{len(gaps)} gaps found in {sys.argv[1]}")

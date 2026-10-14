import sys
from datetime import datetime
from datetime import timedelta

if len(sys.argv) < 2:
    print("Usage: <absolute path>/gap_check.py <logfile>", file=sys.stderr)
    sys.exit(1)

log_path = sys.argv[1]

seen = set()
with open(log_path) as f:
    for line in f:
        seen.add(line[:13])

first = sorted(seen)[0]
last = sorted(seen)[-1]
print(first, last)

start = datetime.strptime(first, "%Y-%m-%d %H")
end = datetime.strptime(last, "%Y-%m-%d %H")
print(start, end)

expected = set()
current = start

while current <= end:
    expected.add(current.strftime("%Y-%m-%d %H"))
    current += timedelta(hours = 1)

print(len(expected))

gaps = expected - seen
print(sorted(gaps))
print(len(gaps))
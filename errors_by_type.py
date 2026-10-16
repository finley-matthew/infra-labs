import sys

if len(sys.argv) < 2:
    print("Usage: <absolute path>/errors_by_type.py <logfile>", file=sys.stderr)
    sys.exit(1)

log_path = sys.argv[1]

errors_by_type = {}

with open(log_path) as f:
    for line in f:
        split = line.split()
        if split[2] == "ERROR":
            if split[3] in errors_by_type:
                errors_by_type[split[3]] += 1
            else:
                errors_by_type[split[3]] = 1


print(errors_by_type)

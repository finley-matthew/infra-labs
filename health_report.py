import sys

if len(sys.argv) < 2:
    print("Usage: python3 health_report.py <logfile>", file=sys.stderr)
    sys.exit(1)

log_path = sys.argv[1]

errors_by_type = {}

success = 0
error = 0
with open(log_path) as f:
    for count, line in enumerate(f, 1):
        split = line.split()
        if len(split) > 3:
            if split[2] == "INFO":
                success += 1
            elif split[2] == "ERROR":
                if split[3] in errors_by_type:
                    errors_by_type[split[3]] += 1
                else:
                    errors_by_type[split[3]] = 1
                error += 1
            else:
                print(f"Unexpected level at line {count} ({split[2]}) log discarded.",
                      file=sys.stderr)
        elif len(split) < 3:
            print(f"Unexpected line length at line {count} {split}", file=sys.stderr)
        else:
            print(f"Unexpected line at line {count}", file=sys.stderr)


if success + error > 0:
    rate = success / (success + error) * 100

    print(f"Success rate: {rate:.1f}% ({success} of {success + error} runs)")

    for k, v in sorted(errors_by_type.items(), key=lambda item: item[1], reverse=True):
        print(f"Error type: {k}. Count: {v}")
else:
    print(f"No INFO/ERROR logs found in {sys.argv[1]}")

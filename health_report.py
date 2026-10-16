import sys

if len(sys.argv) < 2:
    print("Usage: <absolute path>/health_report.py <logfile>", file=sys.stderr)
    sys.exit(1)

log_path = sys.argv[1]

success = 0
error = 0
with open(log_path) as f:
    for line in f:
        split = line.split()
        if split[2] == "INFO":
            success += 1
        elif split[2] == "ERROR":
            error += 1
        else:
            print("An error occured, please try again.")
            sys.exit(1)

rate = success / (success + error) * 100

print(f"Success rate: {rate:.1f}% ({success} of {success + error} runs)")
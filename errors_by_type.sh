#!/usr/bin/bash

if [ -z "$1" ];
then echo "Usage: ./errors_by_type.sh <logfile>"
exit 1
fi

grep "ERROR" "$1" | awk '{print $4}' | sort | uniq -c | sort -nr
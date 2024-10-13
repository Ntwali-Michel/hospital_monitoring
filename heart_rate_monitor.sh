#!/bin/bash

echo "Enter device name (e.g., Monitor_A, Monitor_B):"
read device_name

log_file="heart_rate_log.txt"

while true
do
  timestamp=$(date "+%Y-%m-%d %H:%M:%S")
  heart_rate=$((RANDOM % 81 + 40))
  echo "$timestamp $device_name $heart_rate" >> $log_file
  sleep 1
done &
echo "Heart rate monitoring process started with PID: $!"


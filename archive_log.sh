#!/bin/bash
timestamp=$(date "+%Y%m%d_%H%M%S")
mv heart_rate_log.txt heart_rate_log.txt_$timestamp
echo "Log archived as heart_rate_log.txt_$timestamp"

dffbfa

#!/bin/bash
group_number=1  # Replace with your actual group number

mkdir -p archived_logs_group$group_number
mv heart_rate_log.txt_* archived_logs_group$group_number/
scp archived_logs_group$group_number/* username@hostname:/home/
echo "Backup completed and archived logs moved to archived_logs_group$group_number"



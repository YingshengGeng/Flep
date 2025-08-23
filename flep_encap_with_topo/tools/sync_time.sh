#!/bin/bash

# Set the NTP server you want to sync with
NTP_SERVER="cn.pool.ntp.org" #R6

# Use ntpdate to sync the system time with the NTP server
if ! ntpdate "$NTP_SERVER"; then
    echo "Failed to synchronize time with $NTP_SERVER"
    exit 1
else
    echo "System time synchronized with $NTP_SERVER"
fi

# sudo chmod +x /root/flep_process_with_topo/sync_time.sh
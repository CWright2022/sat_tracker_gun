#!/usr/bin/env bash

FREQ=$1
MODULATION=$2
BANDWIDTH=$3

#first stop all SDR tasks

PID=$(ps | grep rtl_fm | head -c 8)

# echo "killing $PID"

kill $PID

sleep 1
#then start playback on the new frequency

(/home/pi/sat_tracker_gun/rtl_fm -f $FREQ -M $MODULATION -s $BANDWIDTH -r 34k | play -r 32k -t raw -e s -b 16 -c 1 -V1 -) > /dev/null 2>&1 &
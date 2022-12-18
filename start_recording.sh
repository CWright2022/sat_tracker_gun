#!/usr/bin/env bash

FREQ=$1
MODULATION=$2
BANDWIDTH=$3
DATE=$4
TIME=$5
SAT_NAME=$6

FILENAME=${SAT_NAME}_${DATE}_${TIME}

#broadcast FM = 170k?
#nope do 250, it's better
#-E deemp
#-A fast
#-l 0

echo "gonna run this: /home/pi/sat_tracker_gun/rtl_fm -f $FREQ -M $MODULATION -s $BANDWIDTH -r 34k | sox -t raw -e signed-integer -b 16 -c 1 -r 34k - /home/pi/sat_tracker_gun/$FILENAME.wav &" > script_log.txt

/home/pi/sat_tracker_gun/rtl_fm -f $FREQ -M $MODULATION -s $BANDWIDTH -r 34k | sox -t raw -e signed-integer -b 16 -c 1 -r 34k - /home/pi/sat_tracker_gun/${FILENAME}.wav &

# ./rtl_fm.exe -M $MODULATION -f $FREQ -r 34k -w $BANDWIDTH | ./sox.exe -t raw -e signed-integer -b 16 -c 1 -r 34k - test.wav
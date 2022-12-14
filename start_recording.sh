#!/usr/bin/env bash

FREQ=$1
MODULATION=$2
BANDWIDTH=$3
DATETIME=$4
SAT_NAME=$5

FILENAME=${SAT_NAME}_${DATETIME}

#first kill any ongoing instances of recording or playback

PID=$(ps | grep rtl_fm | head -c 8)

kill $PID

#let that go through
sleep 1

#then start our own instance (ignore my notes haha)

#broadcast FM = 170k?
#nope do 250, it's better
#-E deemp
#-A fast
#-l 0

# echo "gonna run this: /home/pi/sat_tracker_gun/rtl_fm -f $FREQ -M $MODULATION -s $BANDWIDTH -r 34k | sox -t raw -e signed-integer -b 16 -c 1 -r 34k - /home/pi/sat_tracker_gun/$FILENAME.wav &" > script_log.txt

/home/pi/sat_tracker_gun/rtl_fm -f $FREQ -M $MODULATION -s $BANDWIDTH -r 34k | tee >(sox -t raw -e signed-integer -b 16 -c 1 -r 34k - /home/pi/sat_tracker_gun/"${FILENAME}".wav &) | play -r 32k -t raw -e s -b 16 -c 1 -V1 - > /dev/null 2>&1 &

# ./rtl_fm.exe -M $MODULATION -f $FREQ -r 34k -w $BANDWIDTH | ./sox.exe -t raw -e signed-integer -b 16 -c 1 -r 34k - test.wav
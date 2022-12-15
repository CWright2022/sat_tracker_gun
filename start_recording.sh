#!/usr/bin/env bash

FREQ=$1
MODULATION=$2
BANDWIDTH=$3

#broadcast FM = 170k?
#nope do 250, it's better
#-E deemp
#-A fast
#-l 0



./rtl_fm -f $FREQ -M $MODULATION -s $BANDWIDTH -r 34k | sox -t raw -e signed-integer -b 16 -c 1 -r 34k - test.wav

# ./rtl_fm.exe -M $MODULATION -f $FREQ -r 34k -w $BANDWIDTH | ./sox.exe -t raw -e signed-integer -b 16 -c 1 -r 34k - test.wav
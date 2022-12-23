#!/usr/bin/bash

#kill any instances we might have running (should kill the playback instance)
PID=$(ps | grep rtl_fm | head -c 8)

kill $PID

#i'll let the GUI code respawn the playback code
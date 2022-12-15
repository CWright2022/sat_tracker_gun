#!/usr/bin/bash

PID=$(ps | grep start_recording | head -c 6)

echo "killing $PID"

kill $PID
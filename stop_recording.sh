#!/usr/bin/bash

PID=$(ps | grep rtl_fm | head -c 8)

echo "killing $PID"

kill $PID
#!/usr/bin/env bash
apt-get update -y
apt-get install git sox python3-pip python3-pil.imagetk xserver-xorg xinit openbox -y
pip install tk pyserial skyfield
export DISPLAY=:0
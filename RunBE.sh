#!/usr/bin/env bash
python3 -m venv venv
source venv/bin/activate
pip3 install -r BE/requirements.txt
python3 BE/dns.py &
flask BE/run -h 0.0.0.0
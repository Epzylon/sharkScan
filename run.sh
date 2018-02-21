#!/bin/sh
mongod &
python3 sharkScan.py -l 0.0.0.0


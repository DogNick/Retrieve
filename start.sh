#!/bin/bash

sh stop.sh
python -u retrieve_server.py --procnum=8 --port=5045 2>&1 > logs/retrieve_server.log &

#!/bin/bash

pid=`ps aux | grep "python -u app.py" | grep -v "grep" | awk '{print $2}'`
kill -9 $pid
nohup python -u app.py > logs/app.log &
tail -f logs/app.log

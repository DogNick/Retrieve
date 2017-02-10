#!/bin/bash
pid=`ps -aux | grep "python -u score_server.py" | grep -v "grep" | awk '{print $2}'`
if [ ! -z $pid ]
then
    kill -9 $pid
fi
nohup python -u score_server.py > logs/score_server.log &
tail -f logs/score_server.log

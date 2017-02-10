#!/bin/bash
pid=`ps -aux | grep "python -u retrieve_server.py" | grep -v "grep" | awk '{print $2}'`

kill -9 $pid

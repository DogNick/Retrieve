#!/bin/bash
uwsgi --stop uwsgi.pid
#pid=`ps -ef | grep supervisord| grep -v grep| awk '{print $2}'`
#echo "[superviosrd pid="$pid"]"
#kill -9 $pid
#pid=`ps -ef | grep broker_app:app| grep -v grep| head -1 | awk '{print $2}'`
#echo "[unicorn pid="$pid"]"
#kill -9 $pid

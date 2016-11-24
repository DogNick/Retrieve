#!/bin/bash
#sh stop.sh
ulimit -n 10000
echo '128000' > /proc/sys/fs/file-max
sysctl -w net.core.somaxconn=65535
sysctl -w net.core.netdev_max_backlog=2500
nohup uwsgi config/uwsgiconfig.ini &
#tail -f logs/retrieve-ranker.std.log

#supervisord -c config/retrieve_supervisor.conf
#cat /dev/null > /search/odin/offline/retrieve-ranker/logs/retrieve_supervisor_err.log
#tail -f /search/odin/offline/retrieve-ranker/logs/retrieve_supervisor_err.log

#pid=`ps aux | grep "python -u app.py" | grep -v "grep" | awk '{print $2}'`
#kill -9 $pid
#nohup python -u app.py > logs/app.log &
#tail -f logs/app.log

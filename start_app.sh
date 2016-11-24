#!/bin/bash
#sh stop.sh
ulimit -n 10000
echo '128000' > /proc/sys/fs/file-max
sysctl -w net.core.somaxconn=65535
sysctl -w net.core.netdev_max_backlog=2500
nohup uwsgi config/uwsgiconfig.ini &

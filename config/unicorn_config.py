import gevent.monkey
gevent.monkey.patch_all()
import multiprocessing

bind = '0.0.0.0:5045'
max_requests = 10000
keepalive = 10

workers = multiprocessing.cpu_count() * 2 + 1
worker_class = 'gunicorn.workers.ggevent.GeventWorker'

loglevel = 'info'
logfile = '/search/odin/offline/retrieve-ranker/logs/unicorn_debug.log'
pidfile = '/search/odin/offline/retrieve-ranker/logs/unicorn.pid'
errorlog = '-'

x_forwarded_for_header = 'X-FORWARDED-FOR'

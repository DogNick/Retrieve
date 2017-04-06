#!/bin/bash


# --index_type=searchhub/elastic, when one is used another is disabled
# --score_host="http://10.141.104.69:9000" this is a deepmatch model on gpu develop machine, default empty and scores are all 1.0

sh stop.sh
nohup python -u retrieve_server.py --procnum=8 --port=5045 \
								--index_type=searchhub --index_size=25 \
								--searchhub_host="http://10.134.34.41:5335" \
								--elastic_host="http://10.152.72.238:9000" \
										2>&1 > logs/retrieve_server.log &

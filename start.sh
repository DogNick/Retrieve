#!/bin/bash


# --index_type=searchhub/elastic, when one is used the other is disabled
# --score_host="http://10.141.104.69:9000" this is a deepmatch model on gpu develop machine, default not used and scores are all 1.0

sh stop.sh
#nohup python -u retrieve_server.py --procnum=8 --port=8000 \
#								--index_type=elastic\
#								--elastic_host="http://10.152.72.238:9200" \
#								--score_host="http://10.141.176.103:9011" \
#										2>&1 > logs/retrieve_server.log &
nohup python -u retrieve_server.py --procnum=8 --port=8000 \
								--index_type=elastic \
								--elastic_host="http://10.152.72.238:9200" \
								--index_name="chaten_brokesisters3" \
								--data_type="data_brokesisters3_1" \
								--score_host="http://10.141.176.103:9011" \
										2>&1 > logs/retrieve_server.log &
#--index_name="chaten_brokesisters" \

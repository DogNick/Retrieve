#coding=utf-8
from flask import Flask, request, render_template, url_for, redirect,make_response
import json
import pdb
import re
import requests
app = Flask(__name__)
from candidate import candidate
from candidate import search
from seg import seg_without_punc

def intervene(query, result):
    final_result = []
    query_seg = ''.join(seg_without_punc(query.encode('gbk', 'ignore')))
    for x in result:
        x_seg = ''.join(seg_without_punc(x[1].decode('utf8').encode('gbk', 'ignore')))
        if query_seg != x_seg:
            final_result.append(list(x)+[1])
        else:
            final_result.append(list(x)+[0])
    return final_result

import redis
redis_pool = redis.ConnectionPool(host="10.134.109.225", port=6379)

def get_flag(key):
    r = redis.Redis(connection_pool=redis_pool)
    value = r.get(key)
    if value is None:
        value = 0
    return value

import hashlib 
import time

@app.route('/retrieve', methods=['get'])
def name():
    # return is formalized
    has_ret = True
    ret = {}
    ret["result"] = None 
    ret["debug_info"] = {} 

    # search candidates
    query = request.args.get('query')
    #magic = request.args.get('magic')
    magic = ""
    can_start = time.time()
    cans = candidate(query.encode('utf8'), magic)
    can_time = time.time() - can_start

    # if no candidates, return 
    if len(cans) == 0:
        ret["debug_info"]["err"] = "no candidates" 
        resp = make_response(json.dumps(ret))
        resp.headers['Access-Control-Allow-Origin'] = '*' 
        return resp
     
    # do scores for all candidats from rank_server
    # swap response and post
    cans_temp = []
    for can in cans:
        temp = list(can)
        if can[2] == 'response':
            temp[0] = can[1]
            temp[1] = can[0]
        cans_temp.append(tuple(temp))

    # Nick disable score_server 
    #payload = {'query':query, 'cans':cans_temp}
    score_start = time.time()
    ##response = requests.post('http://127.0.0.1:5040/score', data=json.dumps(payload))
    score_time = time.time() - score_start
    ## if no response returned from score_server
    #if not response:
    #    ret["debug_info"]["error"] = "score_server no resposne" 
    #    resp = make_response(json.dumps(ret))
    #    resp.headers['Access-Control-Allow-Origin'] = '*' 
    #    return resp
    #
    #scores = json.loads(response.text)
    scores = [[1] * 15] * len(cans_temp) #fake

    #xs = sorted(zip(scores, cans_temp, range(len(cans_temp))), key=lambda x:(x[0][-1], -x[2]), reverse=True)
    
    f_s_start = time.time()
    result = []
    for i, each in enumerate(cans_temp):
        flag = get_flag("retrieve:"+hashlib.md5(query.encode('utf8') + each[0] + each[1]).hexdigest())
        if flag == 1:
            continue
        each = list(each)
        each.append(scores[i])
        each.append(flag)
        each.append(i)
        result.append(each)
    result = intervene(query, result)
    #result = nick_sort(result)
    f_s_time = time.time() - f_s_start

    print (">>> query: %s, can_time:%.5f, score_time:%.5f, filter_sort_time: %.5f" % (query.encode("utf-8"), can_time, score_time, f_s_time))
    N = 7 
    for i, each in enumerate(result):
        if i == N:
            break
        print(">>> retrieve(%d): %-60s%-60s%-s" % (i, each[0], each[1], {"dnn1":each[2]["dnn1"], "dnn2":each[2]["dnn2"]}))
    print ""

    ret["result"] = result
    resp = make_response(json.dumps(ret))
    resp.headers['Access-Control-Allow-Origin'] = '*' 
    return resp

def nick_sort(cans):
    #FixedRank, ContentRank, proxyR, bwpR, BextendR, KCRank 
    #TRank, Trans, LMRank
    #dnn1, dnn2, dnn3, dnn4
    #tlda, AnchorR, KBRank, BRank
    #MatchRank, nKBRank, ExtraR, NExtraR, MissTerm, Loc, PageRank, UsrR, TimeRank, Rank, FinalRank

    # more rules here
    cans = sorted(cans, key=lambda x:(float(x[2]["dnn1"]), float(x[2]["dnn2"])), reverse=True)
    return cans

if __name__ == '__main__':
    app.run(debug=False, host='0.0.0.0', port=5045, threaded=True)

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

def is_chinese(uchar):
    """判断一个unicode是否是汉字"""
    if uchar >= u'\u4e00' and uchar <= u'\u9fa5' or uchar >= u'\uff00' and uchar <= u'\uffef' or uchar >= u'\u3000' and uchar <= u'\u303f':
        return True
    else:
        return False
 
def nick_format(text, width):
    stext = str(text)
    utext = stext.decode("utf-8")
    cn_count = 0
    for u in utext:
        if is_chinese(u):
    #        print u.encode("utf-8")
            cn_count = cn_count + 1 
    return stext + " " * (width - cn_count - len(utext))



def query_resp_same(query, resp):
    final_result = []
    query_seg = ''.join(seg_without_punc(query.encode('gbk', 'ignore')))
    resp_seg = ''.join(seg_without_punc(resp.decode('utf8').encode('gbk', 'ignore')))
    return (query_seg == resp_seg) 

#import redis
#import hashlib 
#redis_pool = redis.ConnectionPool(host="10.134.109.225", port=6379)
#
#def get_flag(key):
#    r = redis.Redis(connection_pool=redis_pool)
#    value = r.get(key)
#    if value is None:
#        value = 0
#    return value
#
#        flag = get_flag("retrieve:"+hashlib.md5(query.encode('utf8') + each[0] + each[1]).hexdigest())
#        if flag == 1:
#            continue
   
import time
@app.route('/retrieve', methods=['get'])
def name():
    # return is formalized
    ret = {}
    ret["result"] = None 
    ret["debug_info"] = {} 

    # search candidates
    query = request.args.get('query')
    strategy = request.args.get('strategy')

    #if not nick_is_valid_post(query, ret["debug_info"]): 
    #    print ("post is not valid, return empty")
    #    ret["result"] = [] 
    #    resp = make_response(json.dumps(ret))
    #    resp.headers['Access-Control-Allow-Origin'] = '*' 
    #    return resp
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
    #scores = json.loads(response.text)
    scores = [[1] * 15] * len(cans) #fake

    topN = 20 
    cnt = 0
    # result select
    f_s_start = time.time()
    result = []
    for i, each in enumerate(cans):
        if query_resp_same(query, each[1]):
            continue
        each = list(each)
        each.append(scores[i])
        each.append(i)
        if not nick_is_valid_can(query.encode("utf-8"), each[0], ret["debug_info"]): 
            continue
        result.append(each)
        cnt = cnt + 1 
        if cnt == topN:
            break

    result = nick_sort(result, strategy)
    f_s_time = time.time() - f_s_start
    
    print (">>> query: %s, can_time:%.5f, score_time:%.5f, filter_sort_time: %.5f" % (query.encode("utf-8"), can_time, score_time, f_s_time))
    for i, each in enumerate(result):
        print(">>> retrieve(%d): %s%s%s" % (i, nick_format(each[0], 60), nick_format(each[1], 50), {"dnn1":each[2]["dnn1"], "dnn2":each[2]["dnn2"]}))
    print ""

    ret["result"] = result
    resp = make_response(json.dumps(ret))
    resp.headers['Access-Control-Allow-Origin'] = '*' 
    return resp

# each candidate is of format below:
#[title_str_utf8, content_str_utf8, {a web search info dict}, source_url, [a list of other scores], index_orig_candidates]

def nick_is_valid_can(query, can, debug_info):
    if query.find(can) != -1 or can.find(query) != -1: 
        return False 
    else:
        return True

def nick_is_valid_post(post, debug_info):
    def too_short(query):
        return len(query) < 2 
    
    def is_dup_seq(query):
        if len(query) < 2:
            return True 
        ret = True 
        for i in range(1,len(query)):
            if query[i] != query[i-1]:
                ret = False
                return ret
        return ret

    if too_short(post):
        print ("post %s shorter than 3" % post.encode("utf-8"))
        debug_info["Ignored"] = "post not valid: shorter than 3"
        return False
    elif is_dup_seq(post):
        print ("post %s is dup chars" % post.encode("utf-8"))
        debug_info["Ignored"] = "post not valid: composed of duplicated chars"
        return False
    else:
        return True

   
def nick_sort(cans, strategy):
    # web search info
    # FixedRank, ContentRank, proxyR, bwpR, BextendR, KCRank 
    # TRank, Trans, LMRank
    # dnn1, dnn2, dnn3, dnn4
    # tlda, AnchorR, KBRank, BRank
    # MatchRank, nKBRank, ExtraR, NExtraR, MissTerm, Loc, PageRank, UsrR, TimeRank, Rank, FinalRank

    # more rules here
    cans = sorted(cans, key=lambda x:(float(x[2]["dnn1"]), float(x[2]["dnn2"])), reverse=True)
    if strategy == 'reverse':
        for i, can in enumerate(cans):
            cans[i][0], cans[i][1] = cans[i][1], cans[i][0]

    return cans

if __name__ == '__main__':
    app.run(debug=False, host='0.0.0.0', port=5045, threaded=True)

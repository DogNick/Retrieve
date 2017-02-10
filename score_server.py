#coding=utf-8
from flask import Flask, request, render_template, url_for, redirect,make_response
import json
import pdb
app = Flask(__name__)
from svr import svr 

@app.route('/score', methods=['post'])
def name():
    data = json.loads(request.data)
    query = data.get('query','')
    cans = data.get('cans', [])

    query = query.encode('utf8')
    cans = map(lambda x:(x[0].encode('utf8'), x[1].encode('utf8'), ''), cans)
    scores = svr(query, map(lambda x:x[:2], cans))

    # a batch of score list including cyy features scores(tfidf,topic,...), nick cnn_dssm score, svr  score
    tmp = scores[0:3]
    print("query: %s all candidats scores num:%d, top3:%s" % (query,len(scores),tmp))
    return json.dumps(scores)

if __name__ == '__main__':
    app.run(debug=False, host='0.0.0.0', port=5040, threaded=True)

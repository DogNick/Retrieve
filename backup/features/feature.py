import os
import pdb
from numpy import linalg as LA
import numpy as np
from rdd import RDD
import time                                                

curr_dir = os.path.split(os.path.realpath(__file__))[0]
idf_file = os.path.join(curr_dir, "douban_idf.gbk")

# decorator
def timeit(method):
    def timed(*args, **kw):
        ts = time.time()
        result = method(*args, **kw)
        te = time.time()

        #print '%r %f sec' % \
        #      (method.__name__, te-ts)
        return result
    return timed


print("reading idf files...")
idfs = RDD.TextFile(idf_file).map(lambda x:(x.strip().split('\t')[0].decode('gbk').encode('utf8'), float(x.strip().split('\t')[1]))).collectAsmap()

@timeit
def lcs_length(a, b):
    table = [[0] * (len(b) + 1) for _ in xrange(len(a) + 1)]
    for i, ca in enumerate(a, 1):
        for j, cb in enumerate(b, 1):
            table[i][j] = (
                    table[i - 1][j - 1] + 1 if ca == cb else
                    max(table[i][j - 1], table[i - 1][j]))
    return table[-1][-1]

@timeit
def cooccur_size(x,y):
    return len(set(x)&set(y))

@timeit
def cooccur_rate(x,y):
    if len(y) > 0:
        return len(set(x)&set(y))/float(len(y))
    return 0

@timeit
def cooccur_sum(x,y):
    coocs = set(x)&set(y)

    result = 0
    for co in coocs:
        if idfs.has_key(co):
            result = result + idfs[co]
    return result

@timeit
def cooccur_average(x,y):
    coocs = set(x)&set(y)

    result = 0
    for co in coocs:
        if idfs.has_key(co):
            result += idfs[co]

    if result > 0:
        return result/float(len(coocs))
    return 0

def tfidf(lines):
    words = {}
    for word in lines:
        words[word] = words.get(word, 0.0) + 1.0

    length = len(lines)
    for x in words:
        words[x] = words[x]/float(length)

    tfidfs = {}
    for x in words:
        if idfs.has_key(x):
            tfidfs[x] = idfs[x]*words[x]

    norm = LA.norm(tfidfs.values())
    for x in tfidfs:
        tfidfs[x] = tfidfs[x]/norm

    return tfidfs

@timeit
def tfidf_similary(x, y):
    tfidf_x = tfidf(x)
    tfidf_y = tfidf(y)
    sums = 0.0
    common_keys = set(tfidf_x.keys()) & set(tfidf_y.keys())
    for key in common_keys:
        sums = sums + tfidf_x[key] * tfidf_y[key]
    return sums 


#from svd import svd, vectorizer, transformer
#def svd_similary(x, y):
#    try:
#        import time
#        start = time.time()
#        x_t = transformer.transform(vectorizer.transform([' '.join(x).decode('utf8')]))
#        y_t = transformer.transform(vectorizer.transform([' '.join(y).decode('utf8')]))
#        second = time.time()
#        print second-start
#        svd_x = svd.transform(x_t)
#        svd_y = svd.transform(y_t)
#        print time.time() - second
#        return np.dot(svd_x, svd_y.T)[0][0]
#    except:
#        pass
#
#    return 0.0

#@timeit
#def svd_similaries(xs):
#    temps = []
#    for x in xs:
#        temps.append(' '.join(x).decode('utf8'))
#
#    if temps:
#        result = transformer.transform(vectorizer.transform(temps))
#        svd_x = svd.transform(result)
#    else:
#        svd_x = []
#    return svd_x

import urllib
import requests
import json
from deep_match import get_cnn_dssm_score 
from deep_match import get_cnn_dssm_score_batch 

@timeit
def cnn_dssm_feature(query, response):
    try:
        q = ' '.join(query)
        r = ' '.join(response)
        #score = get_cnn_dssm_score(q, r)
        score = 0.0
        return score
    except:
        return 0.0
print("importing topic_word_model..")
from topic_word_model import topic_words_export

@timeit
def topic_model(x, y):
    return topic_words_export(x, y)

def parse_post(line):
    _id, text = line.strip().split('##')
    return (int(_id), [x for x in text.split(' ')])

posts = {}
responses = {}
post_response = {}

def parse_origin_pair(line):
    post_id , response_ids = line.strip().split(':')
    for response_id in response_ids.split(','):
       post_response[int(response_id)] = int(post_id)


def parse_labeled(line):
    label, query_id, response_id = line.strip().split(',')
    post_id = post_response[int(response_id)]

    query = posts[int(query_id)]
    post = posts[post_id]
    response = responses[int(response_id)]

    features = extract_features(query, post, response)
    return (features, label)

def text_out(arg):
    features, label = arg
    return ','.join(map(str,features)) + '\t'+label

if __name__ == "__main__":
    print "no thing to test"

#coding=utf-8
from candidate import candidate
from seg import fea
from seg import seg_wordpos_list
from features import * 

print ("importing seg..")
import numpy as np
from rdd import RDD
model = RDD.TextFile('./model.svr').map(lambda x:float(x.strip())).collect()
model = np.asarray(model).reshape([len(model),1])

import pdb

def predict(X):
    return np.dot(X, model).ravel()

def feature_one(query, post, response):
    features = []
    lcs_feature = lcs_length(query, response)
    cooccur_size_post = cooccur_size(query, post)
    cooccur_size_response = cooccur_size(query, response)
    cooccur_rate_post = cooccur_rate(query, post)
    cooccur_rate_response = cooccur_rate(query, response)
    cooccur_sum_post = cooccur_sum(query, post)
    cooccur_sum_response = cooccur_sum(query, response)
    cooccur_average_post = cooccur_average(query, post)
    cooccur_average_response = cooccur_average(query, response)
    similary_post = tfidf_similary(query, post)
    similary_response = tfidf_similary(query, response)

    # need to be seged into word and pos
    q = seg_wordpos_list(''.join(query).decode('utf8').encode('gbk'))
    r = seg_wordpos_list(''.join(response).decode('utf8').encode('gbk'))
    p = seg_wordpos_list(''.join(post).decode('utf8').encode('gbk')) 
    topic_model_score_response = topic_model(q,r)
    topic_model_score_post = topic_model(q,p)

    features = [lcs_feature, cooccur_size_post, cooccur_size_response, cooccur_rate_post, cooccur_rate_response, cooccur_sum_post, cooccur_sum_response, cooccur_average_post, cooccur_average_response, similary_post, similary_response, topic_model_score_post, topic_model_score_response]
    return features

def feature_batch(query, candidates):
    # need to be seged before feed into cnn_dssm
    batch_posts = [" ".join(fea(each[0])) for each in candidates] 
    batch_responses = [" ".join(fea(each[1])) for each in candidates]
    batch_coses = get_cnn_dssm_score_batch(batch_posts, batch_responses)
    return batch_coses
    
def feature(query, candidates):
    # feature one by one
    print("candidates num: %d" % len(candidates))
    batch_feats = []
    for post, response in candidates:
        
        batch_feats.append(feature_one(query, post, response))
    print("features batch num: %d" % len(batch_feats))
    # feature byt batch (=100?)
    batch_coses = feature_batch(query, candidates) 
    print("cnn features batch num: %d" % len(batch_coses))

    # make a zip
    for i in range(len(batch_feats)):
        batch_feats[i].extend(batch_coses[i])
    features = batch_feats 
    '''
    if candidates:
        svd_query = svd_similaries([query])
        svd_posts = svd_similaries(map(lambda x:x[0], candidates))
        svd_responses = svd_similaries(map(lambda x:x[1], candidates))
        
        post_svds = np.dot(svd_posts, svd_query.T)
        response_svds = np.dot(svd_responses, svd_query.T)
        
        for l, x,y in zip(temp_result, post_svds, response_svds):
            features.append(l+list(x)+list(y))
    '''
    print("features ziped")

    return features 

def svr(query, candidates):
    features = []
    import time

    cans = []
    for post, response in candidates:
        cans.append((post, response))

    try:
        features = feature(query, cans)
    except Exception, e:
        print(e)
        return []

    # features are cyy features(tfidf,topic...) and cnn_dssm cosine feature
    results = []
    try:
        if features:
            results = predict(np.asarray(features))
            print results
    except Exception, e:
        print(e)
        return []

    results = [x+[y] for x, y in zip(features, results)]
    return results

query = u'搜狗'
cans = candidate(query.encode('utf8'), "exp_flag:00")
scores = svr(query.encode('utf8'), map(lambda x:x[:2], cans))
#for s in scores:
#    print s

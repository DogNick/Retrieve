#!/usr/bin/env python

import sys
import numpy
import warnings

from liblinearutil import *
import os

curr_dir = os.path.split(os.path.realpath(__file__))[0]
data_path = os.path.join(curr_dir,"data")

model_file = os.path.join(data_path,'new_model')
indir1 = open(os.path.join(data_path,'douban_list.gbk'), 'r')
indir2 = open(os.path.join(data_path,'douban_idf.gbk'), 'r')
indir3 = open(os.path.join(data_path,'separator.gbk'), 'r')

#model_file = '/search/cuiyanyan/sgd/topic_word_model/model'
#indir1 = open('/search/cuiyanyan/sgd/topic_word_model/word_list.gbk', 'r')
#indir2 = open('/search/cuiyanyan/sgd/topic_word_model/word_idf.gbk', 'r')


word_list = {}
idf_table = {}
separator = {}

def show_warnings():
    warnings.filterwarnings('ignore', '.*invalid value.*')
    #warnings.warn('run time warning')

def topic_word_feature(seged_query_tuple_list, model):
    tf_dic = {}
    sf_dic = {}
    sen_num = 0
    arr = {}
    arl = []
    for wordpos in seged_query_tuple_list:
        word = wordpos[0]
        pos = wordpos[1]
        if word not in tf_dic:
            tf_dic[word] = 1
        else:
            tf_dic[word] += 1
        if word not in sf_dic:
            sf_dic[word] = dict()
            sf_dic[word][sen_num] = 1
        else:
            sf_dic[word][sen_num] = 1
        if pos == 34:
            if is_separate == 1:
                sen_num += 1

    for wordpos in seged_query_tuple_list:
        word = wordpos[0]
        pos = wordpos[1]
        #tf = tf_dic[word]
        if word in tf_dic:
            tf = float(tf_dic[word]) / float(len(seged_query_tuple_list))
        else:
            continue
        if word not in idf_table:
            continue
        idf = idf_table[word]
        sf = len(sf_dic[word])
        First = 0
        if (0 in sf_dic[word]):
            First = 1
        Last = 0
        if (sen_num-1 in sf_dic[word]):
            Last = 1
        NE = 0
        if pos >=17 and pos <= 22:
            NE = 1
        NE_First = 0
        NE_Last = 0
        if NE == 1 and First == 1:
            NE_First = 1
        if NE == 1 and Last == 1:
            NE_Last = 1
        vec = {}
        vec[1] = float(tf)
        vec[2] = float(idf)
        vec[3] = float(sf)
        vec[4] = float(First)
        vec[5] = float(Last)
        vec[6] = float(NE)
        vec[7] = float(NE_First)
        vec[8] = float(NE_Last)
        vec[9] = float(pos)
        x = [vec]
        y = [1]
        p_label, p_acc, p_val = predict(y, x, model)
        p = p_val[0][0]
        if word in word_list:
            index = word_list[word]
            arr[index] = p
            arl.append(p)
    return arr, arl

def is_separate(query):
    if query in separator:
        return 1
    return 0

def read_separator(filename):
    for line in filename:
        line = line.strip()
        separator[line] = 0
    filename.close()

def read_word_list(filename):
    for line in filename:
        line = line.strip()
        items = line.split('\t')
        if len(items) < 2:
            continue
        word_list[items[1]] = items[0]
    filename.close()

def read_idf_file(filename):
    for line in filename:
        line = line.strip()
        items = line.split('\t')
        if len(items) != 2:
            continue
        idf_table[items[0]] = items[1]
    filename.close()

def line_replace(line, strs):
    while line.find(strs) != -1:
        line = line.replace(strs, '')
    return line

def calculate_modulo(v):
    s = numpy.linalg.norm(v)
    return s

def mul_dic(q1, q2):
    sums = 0.0
    for k in q1:
        if k in q2:
            sums += q1[k]*q2[k]
    return sums

def init():
    read_word_list(indir1)
    read_idf_file(indir2)
    read_separator(indir3)
    model = load_model(model_file)
    return (model)

def topic_words(seged_query_tuple1, seged_query_tuple2, model):
    q1, v1 = topic_word_feature(seged_query_tuple1, model)
    q2, v2 = topic_word_feature(seged_query_tuple2, model)
    sem = 0.0
    sums = mul_dic(q1, q2)
    modulo = calculate_modulo(v1)*calculate_modulo(v2)
    if modulo != 0.0:
        show_warnings()
        sem = sums/modulo
    return sem



model = init()
def topic_words_export(seged_query_tuple1, seged_query_tuple2):
    ret = topic_words(seged_query_tuple1, seged_query_tuple2, model)
    if numpy.isnan(ret):
        ret = 0.0
    return ret

if __name__ == '__main__':
    print("nothing yet")
    #query1 = ''
    #query2 = ''
    #for line in open('t.gbk', 'r'):
    #    line = line.strip()
    #    if query1 == '':
    #        query1 = line
    #    elif query2 == '':
    #        query2 = line
    #    else:
    #        break
    #print topic_words(query1, query2, seghandle, model)
    #print topic_words('today is a good day', 'what a nice day', seghandle, model)


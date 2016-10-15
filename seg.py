import os
import sys
reload(sys)
curr_dir = os.path.split(os.path.realpath(__file__))[0]
sys.path.append(os.path.join(curr_dir,'wordseg_python'))

from TCWordSeg import *
import pdb

dict_dir = os.path.join(curr_dir, 'wordseg_python/dict')

# cyy's mode
#SEG_MODE = TC_S2D|TC_CN|TC_POS|TC_T2S|TC_U2L|TC_CLS|TC_USR|TC_LN

def fea(query):
    query = map(lambda x:x.decode('gbk').encode('utf8', 'ignore'),seg(query.decode('utf8').encode('gbk', 'ignore')))
    return query

def init_seg(dict_dir):
    TCInitSeg(dict_dir)
    SEG_MODE = TC_S2D|TC_CN|TC_POS|TC_T2S|TC_U2L|TC_CLS|TC_USR|TC_LN
    seghandle = TCCreateSegHandle(SEG_MODE)
    return seghandle

def uninit_seg(seghandle):
    TCCloseSegHandle(seghandle)
    TCUnInitSeg()

def do_seg(seghandle, query):
    TCSegment(seghandle, query)
    rescount = TCGetResultCnt(seghandle)
    line_seg = []
    for i in range(rescount):
        wordpos = TCGetAt(seghandle, i);
        word = wordpos.word
        pos = wordpos.pos
        if pos != 34:
            line_seg.append(word)
    return line_seg

def do_seg_without_punc(seghandle, query):
    TCSegment(seghandle, query)
    rescount = TCGetResultCnt(seghandle)
    line_seg = []
    for i in range(rescount):
        wordpos = TCGetAt(seghandle, i);
        word = wordpos.word
        pos = wordpos.pos
        if pos != 36 and pos != 34:
            line_seg.append(word)

    return line_seg


seghandle = init_seg(dict_dir)
def seg(query):
    return do_seg(seghandle, query)

def seg_wordpos_list(query):
    TCSegment(seghandle, query)
    rescount = TCGetResultCnt(seghandle)
    wp_list = []
    for i in range(rescount):
        wordpos = TCGetAt(seghandle, i);
        wp_list.append((wordpos.word,wordpos.pos))
    return wp_list

def seg_without_punc(query):
    return do_seg_without_punc(seghandle, query)

'''
from rdd import RDD
def parse_data(line):
    _id, text = line.strip().split('##')
    text = ''.join(text.split(' '))
    try:
        text = do_seg(seghandle, text.decode('utf8').encode('gbk', 'ignore'))
    except:
        pdb.set_trace()
    return _id+'##'+' '.join(text).decode('gbk').encode('utf8', 'ignore')

RDD.TextFile('../huawei_data/post.index').map(parse_data).saveAsTextFile('./post.index')
RDD.TextFile('../huawei_data/response.index').map(parse_data).saveAsTextFile('./response.index')

uninit_seg(seghandle)
'''

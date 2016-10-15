#coding=utf8
import requests
import pdb
import urllib
import re

p_tag = re.compile('post_response="([^"]+)"')
p_title = re.compile('<title><!\[CDATA\[(.*)\]\]></title>')
p_content = re.compile('<content><!\[CDATA\[(.*)\]\]></content>')
p_rank = re.compile('<rank (.*)></rank>')
p_oldp = re.compile('oldp:(\d+) rfr')
p_dnn2 = re.compile('dnn2="([^"]+)"')
p_url = re.compile('<url><!\[CDATA\[(.*?)\]\]></url>')

def search(query, magic):
    url = "http://10.134.96.66:5555" 
    #data = "parity=f1ddc0e4-57ef-4f1b-985f-b85e09c41afc&queryFrom=web&queryType=query&queryString=%s&start=0&end=100&forceQuery=1&magic=%s"%(urllib.quote_plus(query.decode('utf8').encode('gbk')), magic)
    data = "parity=f1ddc0e4-57ef-4f1b-985f-b85e09c41afc&queryFrom=web&queryType=query&queryString=%s&start=0&end=20&forceQuery=1" % urllib.quote_plus(query.decode('utf8').encode('gbk'))
    response = requests.post(url, data=data)
    result_tag = p_tag.findall(response.text)
    result_title = p_title.findall(response.text)
    result_content = p_content.findall(response.text)
    result_title = map(lambda x:x.replace(u'\ue40b','').replace(u'\ue40a',''), result_title)
    result_content = map(lambda x:x.replace(u'\ue40b','').replace(u'\ue40a',''), result_content)
    result_rank = p_rank.findall(response.text)
    result_oldp = p_oldp.findall(response.text)
    #result_dnn2 = p_dnn2.findall(response.text)
    result_url = p_url.findall(response.text)
    #return result_title, result_content, result_tag, result_rank, result_oldp, result_dnn2, result_url
    return result_title, result_content, result_tag, result_rank, result_oldp, result_url

def candidate(query, magic):
    #titles, contents, tags, ranks, oldps, dnn2s, urls = search(query, magic)
    titles, contents, tags, ranks, oldps, urls = search(query, magic)
    result = []
    if oldps:
        oldps = oldps+[400]*(len(tags)-len(oldps))
    else:
        oldps = [400]*len(tags)
    #for title, content, _tag, rank, oldp, dnn2, url in zip(titles, contents, tags, ranks, oldps, dnn2s, urls):
    for title, content, _tag, rank, oldp, url in zip(titles, contents, tags, ranks, oldps, urls):
        title = title.encode('utf8')
        summary = content.encode('utf8')
        web_info = {}
        for each in re.split(" ", rank):
            segs = re.split("=", each)
            k = segs[0] 
            v = segs[1][1:-1]
            web_info[k] = v 
        web_info["oldp"] = oldp
        web_info["tag"] = _tag 
        result.append((title, summary, web_info, url))
    return result

#tag(u'搜狗'.encode('utf8'))
cans = candidate(u'搜狗'.encode('utf8'), "exp_flag:00")
#print cans[0]
#for can in cans:
#    print can
#for can in cans:
#    print can


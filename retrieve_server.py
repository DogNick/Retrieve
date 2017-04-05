#coding=utf-8
import os
import gc
import re
import sys
import json
import time
import heapq
import urllib
import logging
import traceback

import tornado.httpserver
import tornado.httpclient

from tornado import web, gen, locks, ioloop
from tornado.options import define, options, parse_command_line
from tornado.locks import Event

define('port',default=5555,help='run on the port',type=int)
define('procnum',default=2,help='process num',type=int)

p_tag = re.compile('post_response="([^"]+)"')
p_title = re.compile('<title><!\[CDATA\[(.*)\]\]></title>')
p_content = re.compile('<content><!\[CDATA\[(.*)\]\]></content>')
p_rank = re.compile('<rank (.*)></rank>')
p_oldp = re.compile('oldp:(\d+) rfr')
p_dnn2 = re.compile('dnn2="([^"]+)"')
p_url = re.compile('<url><!\[CDATA\[(.*?)\]\]></url>')

#logging.basicConfig(format='%(message)s', level=logging.INFO)
#logging.getLogger('requests').setLevel(logging.WARNING)

from seg import seg_without_punc
PUNC=u"[:,\"\uff0c\u3002\uff1f\uff01\uff03\u3001\uff1b\uff1a\u300c\u300d\u300e\u300f\u2018\u2019\u201c\u201d\uff08\uff09\u3014\u3015\u3010\u3011\u2026\uff0e\u300a\u300b]"

class FutureHandler(tornado.web.RequestHandler):

	@tornado.web.asynchronous
	@tornado.gen.coroutine
	def get(self):
		ret = {}
		ret["result"] = None 
		ret["debug_info"] = {} 

		self.query = self.get_query_argument('query', None)
		self.strategy = self.get_query_argument('strategy', "normal")
		self.timeout = 4.0
		if not self.query:
			ret["debug_info"]["err"] = "missing params"
			logging.info('[retrieve_server] [ERROR: missing params] [REQUEST] [%s]' % (time.strftime('%Y-%m-%d %H:%M:%S')))
			self.write(json.dumps(ret, ensure_ascii=False))
			self.finish()
			return

		logging.info('[retrieve_server] [REQUEST] [%s] [%s] [%s]' % (time.strftime('%Y-%m-%d %H:%M:%S'), self.query, self.strategy))


		#cans, t = yield self.elastic_candidate(150) 
		#ret["debug_info"]["elastic_time"] = t 

		# Use sogou search hub
		cans, t = yield self.search_candidate(20) 
		ret["debug_info"]["search_time"] = t 

		if len(cans) == 0:
			ret["debug_info"]["err"] = "no candidates" 
			self.write(json.dumps(ret, ensure_ascii=False))
			self.finish()
			return

		deprecated = []	
		selected = self.select(cans, deprecated)
		if len(selected) == 0:
			ret["debug_info"]["err"] = "All deprecated by select()" 
			self.write(json.dumps(ret, ensure_ascii=False))
			self.finish()
			return

		scored = yield self.score(selected)
		results = yield self.sort(scored)
	 		
		ret["result"] = results
		self.write(json.dumps(ret, ensure_ascii=False))
		#self.write(json.dumps(ret))
		self.finish()


	@tornado.gen.coroutine
	def elastic_candidate(self, size):
		q = {"query":{"match":{"_all":self.query}}}
		elastic_host = "http://10.152.72.238:9200"
		url = "%s/retrieve/postcomment/_search?pretty&size=%d" % (elastic_host, size)
		req = tornado.httpclient.HTTPRequest(url, method="POST", headers=None, body=json.dumps(q, ensure_ascii=False))
		http_client = tornado.httpclient.AsyncHTTPClient(force_instance=True,
														defaults=dict(request_timeout=self.timeout,connect_timeout=self.timeout))
		res = yield http_client.fetch(req)
		res_js = json.loads(res.body)
		cans = []
		for i, each in enumerate(res_js["hits"]["hits"]):
			info = {"elastic_score":each["_score"], "elastic_idx":i}
			post, resp = each["_source"]["post"], each["_source"]["comment"] 
			cans.append((each["_source"]["post"], each["_source"]["comment"], info, url))
		raise gen.Return((cans, res_js["took"]))

	@tornado.gen.coroutine
	def search_candidate(self, size):
		q = self.query
		url = "http://10.134.34.41:5335" 
		data = {
					"parity":"f1ddc0e4-57ef-4f1b-985f-b85e09c41afc",
					"queryFrom":"web",
					"queryType":"query",
					"queryString":self.query.encode("gbk", "ignore"),
					"start":"0",
					"end":size,
					"forceQuery":"1"
				}

		req = tornado.httpclient.HTTPRequest(url, method="POST", body=urllib.urlencode(data))
		http_client = tornado.httpclient.AsyncHTTPClient(force_instance=True, defaults=dict(request_timeout=self.timeout, connect_timeout=self.timeout))
		res = yield http_client.fetch(req)

		body = res.body.decode("utf-16")

		result_title = p_title.findall(body)
		titles = map(lambda x:x.replace(u'\ue40b','').replace(u'\ue40a',''), result_title)
		result_content = p_content.findall(body)
		contents = map(lambda x:x.replace(u'\ue40b','').replace(u'\ue40a',''), result_content)
		tags = p_tag.findall(body)
		ranks = p_rank.findall(body)
		oldps = p_oldp.findall(body)
		#result_dnn2 = p_dnn2.findall(res)
		urls = p_url.findall(body)

		cans = []
		if oldps:
		    oldps = oldps+[400]*(len(tags)-len(oldps))
		else:
		    oldps = [400]*len(tags)
		for title, content, _tag, rank, oldp, url in zip(titles, contents, tags, ranks, oldps, urls):
		    summary = content
		    web_info = {}
		    for each in re.split(" ", rank):
		        segs = re.split("=", each)
		        k = segs[0] 
		        v = segs[1][1:-1]
		        web_info[k] = v 
		    web_info["oldp"] = str(oldp)
		    web_info["tag"] = _tag 
		    cans.append((title, summary, web_info, url))
		raise gen.Return((cans, 0))


	@tornado.gen.coroutine
	def score(self, cans): 
		# Deepmatch scores 
		#data = {
		#	"model_name":"stc-2-interact",
		#	"query": self.query.encode("utf-8"),
		#	"cans":json.dumps([[each[0], each[1]] for each in cans])
		#}
		#deepmatch_host = "http://10.141.104.69:9000"
		#url = "%s/deepmatch?" % deepmatch_host
		##json.dumps(data, ensure_ascii=False)
		#body = urllib.urlencode(data)
		##body = urllib.quote(json.dumps(data).encode("utf-8"))
		#req = tornado.httpclient.HTTPRequest(url, method="POST", headers=None, body=body)
		#http_client = tornado.httpclient.AsyncHTTPClient(force_instance=True,
		#												defaults=dict(request_timeout=self.timeout,connect_timeout=self.timeout))
		#res = yield http_client.fetch(req)
		#res_js = json.loads(res.body)
		#scores = res_js["result"][0]["scores"]

		# dummy
		scores = [1] * len(cans)

		for i in range(len(cans)):
			cans[i][2]["deepmatch_score"] = str(scores[i])
		raise gen.Return(cans[0:10])

	@tornado.gen.coroutine
	def sort(self, cans): 
		# maybe random_walk 
		cans = sorted(cans, key=lambda x: float(x[2]["deepmatch_score"]), reverse=True)
		raise gen.Return(cans)

	def select(self, cans, deprecated):
		selected = []
		for i, each in enumerate(cans):
			(post, resp) = (each[1], each[0]) if self.strategy == "reverse" else (each[0], each[1])

			#same, info = query_resp_same(self.query, resp)	
			#if same: 
			#	deprecated.append("Deprecated(title-doc): %s %s [%s]" % (each[0], each[1], info))
			#	continue

			valid, info = nick_is_valid_can(self.query, resp)
			if not valid: 
				deprecated.append("Deprecated(title-doc): %s %s [%s]" % (each[0], each[1], info))
				continue
			selected.append(each)

		# N shortest resp
		N = 5 
		heap = []	

		heapq.nsmallest(N, cans, key=lambda x:len(x[1]))
		for each in selected:
			if len(heap) < N or len(each[1]) < len(heap[0][1]):
				if len(heap) == N:
					heapq.heappop(heap)				
				heapq.heappush(heap, each)

		selected = heap
		return selected

	def log(self):
		pass

	def set_default_headers(self):
		self.set_header('Access-Control-Allow-Origin', "*")


#### some utils ###
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
	#		print u.encode("utf-8")
			cn_count = cn_count + 1 
	return stext + " " * (width - cn_count - len(utext))

def query_resp_same(query, resp):
	final_result = []
	query_seg = ''.join(seg_without_punc(query.encode('gbk', 'ignore')))
	resp_seg = ''.join(seg_without_punc(resp.encode('gbk', 'ignore')))
	if query_seg == resp_seg:
		return True, None
	return False, "query and response are almost the same"

def lcs(s1, s2):   
	m = [[0 for i in range(len(s2)+1)]  for j in range(len(s1)+1)]
	mmax = p = p2 = 0
	for i in range(len(s1)):  
		for j in range(len(s2)):  
			if s1[i] == s2[j]:  
				m[i + 1][j + 1]=m[i][j] + 1  
				if m[i + 1][j + 1] > mmax:  
					mmax = m[i + 1][j + 1]  
					p = i + 1  
					p2 = j + 1
	return s1[p - mmax:p],p - mmax,p2 - mmax

def dedup(s):
	if s == "" or s == None:
		return ""
	ret = [s[0]]
	j = 1 
	while j < len(s):
		if s[j] != ret[-1]:
			ret.append(s[j])
		j = j + 1	 
	return "".join(ret) 

def nick_is_valid_query(query):
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
		return False, "query shorter than 3"
	elif is_dup_seq(post):
		return False, "query is dup chars"
	else:
		return True, None


def nick_is_valid_can(query, can):
	query_tmp = dedup(re.sub(PUNC, "", query))
	 
	can_tmp = dedup(re.sub(PUNC, "", can))
	com_str, p1, p2 = lcs(query_tmp, can_tmp) 
	if len(com_str) == len(query_tmp) or len(com_str) == len(can_tmp):
		return False, "query or candidate is contained by the other" 
	if len(can_tmp) >= 5:
		lc, lq, lr = len(com_str) * 1.0, len(query_tmp) * 1.0, len(can_tmp) * 1.0
		if lc / lq > 0.5 and lc / lr > 0.5:
			return False, "length of lcs exceeds both query and response"
	return True, None

 

def main():
	parse_command_line()
	app=tornado.web.Application(
		[
			(r'/', FutureHandler),
		]
	)
	# 	single process
	#app.listen(options.port)

	#	multi process
	#sockets = tornado.netutil.bind_sockets(options.port)
	#tornado.process.fork_processes(8)
	server = tornado.httpserver.HTTPServer(app)
	server.bind(options.port)

	#server.add_sockets(sockets)
	server.start(options.procnum)
	logging.info("[SERVICE START] retrieve server start, listen on %d" % options.port)

	#tornado.ioloop.IOLoop.current().start()
	tornado.ioloop.IOLoop.instance().start()
	#gc.collect()
	#gc.disable()

if __name__ == "__main__":
	main()


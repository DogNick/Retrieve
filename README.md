# Retrieve System
----
[![Powered by Tensorflow](https://www.tensorflow.org/_static/images/tensorflow/logo.png)](https://www.tensorflow.org/)

# Description
This retrieve_server is currently based on python tornado-4.5.2 and powered by tencent segmentation.
The system actually contains three components:
  - ElasticSearch server
  - Scoring server(s)
  - Retrieve server

# ElasticSearch
Now the [ElasticSearch-5.2.0] is used to build a basic indexing system on:

```
    root@10.142.72.238:/search/odin/sheperd/retrieve/elasticsearch-5.2.0
    chatbot@2017
```
To start the server please refer to [ElasticSearch-5.2.0 Setup], Currently already started on:
```
    10.142.72.238:9200
```

We need to inject data into ElasticSearch before we can retrieve any from it, injection scripts and data samples as examples can be found under `data` dir:
```
    root@10.142.72.238:/search/odin/sheperd/retrieve/data/brokesisters3.json
    root@10.142.72.238:/search/odin/sheperd/retrieve/data/load_brokesisters_3.sh
```
Data file is in json format and each piece of data is represented by two line, one for index, another for content with probably more complex json-compatible structures, for this example:
```
{"index": {"_id": "99"}}
{"time_interval": "300", "content_time": ["00:16:34,095 --> 00:16:36,012", "00:16:36,012 --> 00:16:37,079"], "post_time": "00:16:34,095 --> 00:16:36,012", "e": "1", "content_en": ["him who?", "nothing."], "query_ch": "\"他\"是指...", "response_ch": "没啥", "s": "1", "query": "him who?", "response": "nothing.", "response_time": "00:16:36,012 --> 00:16:37,079", "content_ch": ["\"他\"是指...", "没啥"]}
{"index": {"_id": "100"}}
{"time_interval": "300", "content_time": ["00:16:43,098 --> 00:16:45,001", "00:16:45,091 --> 00:16:49,097"], "post_time": "00:16:43,098 --> 00:16:45,001", "e": "1", "content_en": ["him, robbie?", "it's none of my business, but you deserve better than that guy."], "query_ch": "你是说罗比  对吧", "response_ch": "这事与我无关但我觉得那家伙跟你配不上", "s": "1", "query": "him, robbie?", "response": "it's none of my business, but you deserve better than that guy.", "response_time": "00:16:45,091 --> 00:16:49,097", "content_ch": ["你是说罗比  对吧", "这事与我无关但我觉得那家伙跟你配不上"]}
```

The injection is done by code as something like following:
```sh
    full_name="chaten_brokesisters3"
    sub_title_2="brokesisters3"
    curl -XPOST "http://10.152.72.238:9200/${full_name}/data_${sub_title_2}_1/_bulk?pretty&refresh" --data-binary "@brokesisters3.json"
```
> Note that you should not run these code directly for this will inject these data a second time ! 

As there's some limit to the size of each data file, we must split the file into pieces to keep it under size 50M, this limit is configurable by ElasticSearch configuration file `/search/odin/sheperd/retrieve/elasticsearch-5.2.0/config/elasticsearch.yml`:
```
http.max_content_length: 100mb
```
You can also refer to those commented-out lines  in `/search/odin/sheperd/retrieve/data/load_brokesisters_3.sh` to inject  many data files
> Note that this value will only work under 2gb for the HTTP protocal size limit

More operations including delete,update,index and any other details please refer to [Document APIs]

Once injected successfully, you can check your indexed data on the browser, for data id 1 and data id 2:
```
    http://10.152.72.238:9200/chaten_brokesisters3/data_brokesisters3_1/1
    http://10.152.72.238:9200/chaten_brokesisters3/data_brokesisters3_1/2
```
For a typical search api: given a query, to retrieve data pieces with top `size` similarity between their key `query` and this given one: 
```python
    url = http://10.152.72.238:9200/chaten/_search
        {
            "query":
            {
                "match":{"query":query}
            },
            "size":10
        }
    # Do post request of this data
    req = tornado.httpclient.HTTPRequest(url, method="POST", headers=None, body=json.dumps(q, ensure_ascii=False))
```
More details about searching strategy please refer to [Search APIs]

Data resources (up to now):

* Chinese corpus
```sh
    Nick@10.141.104.69, password: Nick
    
    # original bought multi-turn; two-turn weibo data,500w sessions
    /search/odin/Nick/GenerateWorkshop/data/corpus_bought_from_ZHONGXINWANG/origin_data 
    
    # Segmented multi-turn data by ZhouHao, contains some single lines(probably some error, just skip those single lines)
    /search/odin/Nick/GenerateWorkshop/data/corpus_bought_from_ZHONGXINWANG/multi_turn/weibo_session_segment.data
```
```sh
    root@10.141.176.103, password: sogourank@2016
    # Segmented sogou-crawled + stc-1 + stc-2 + bought two-turn weibo pairs
    /search/odin/Nick/GenerateWorkshop/data/WEIBO-stc-bought/train.data
    /search/odin/Nick/GenerateWorkshop/data/WEIBO-stc-bought/valid.data
```

* English corpus
```sh
    root@10.141.176.103, password: sogourank@2016
    
    # Original Broke sisters .ass files and python scripts for processing it into json
    /search/odin/Nick/GenerateWorkshop/data/broke_sisters/
    # season 1 - 6, maybe hundreds of thousands, not sure
    #... waiting for 2 interns' docs
    
    # Original opensubtitles data constructed by question-ans criteria
    # 1.1kw+, lower case, reponses are greater than 3
    /search/odin/Nick/GenerateWorkshop/data/opensubtitle/all_resp_gt3_clean
    /search/odin/Nick/GenerateWorkshop/data/opensubtitle/clean_en_data.py # may not be sufficient
    
    # Preprocessed opensubtitles pairs with joint prime, with response length greater than 3
    # 700w+ lower case
    /search/odin/Nick/GenerateWorkshop/data/opensubtitle_gt3_joint_prime_clean/
    
    # Preprocessed twitter pairs, with limited UNKs ratio in total and limited UNKs ratio per sentence (say, 0.1 ?)
    # 25w pairs
    /search/odin/Nick/GenerateWorkshop/data/twitter_25w_filter_len_unk
    
    # Preprocessed reddit pairs, without prime
    # 1kw+ pairs, lower case
    /search/odin/Nick/GenerateWorkshop/data/SRT-reddit-proced-voca-filtered/
```

# Scoring server
Scoring server is another independent service, which is also based on python tornado and probably powered by tensorflow-serving or other heavy methods.

For this `broke_sisters` examples, we use an ensembled scorer server that will provide scores below on each query-candidate(post and response) pair:
* **rnn_enc** scores is the cos-similarity between vecs of the given query and its candidate posts generated by a seq2seq(vae,cvae) encoder that is trained on *opensubtitle_gt3_joint_prime_clean*
* **emb** score is the cos-similarity between embeddings of the given query and its candidates, that is simply a sum of word embeddings over sequence
* **posterior** score is a cross-ent score given a query-candidate response pair, generated by a seq2seq model trained the *opensubtitle_gt3_joint_prime_clean* with **reversed pairs**(response-post)

For now, this scoring server is alive on `10.141.176.103:9011`, to start it:
```sh
ssh root@10.141.176.103 # passward: sogourank@2016
cd /search/odin/Nick/GenerateWorkshop/servers
sh scorer_start.sh # this will restart the server if it is already running
```
This will actually run a python app `Server.py` that will further start 2 tensorflow-serving servable defined in `` on two seperated GPU and 1 scoring server on top of them
U can check logs by:
```
    tail -f logs/server_scorer_0_9011.log # scoring server log
    tail -f logs/tf_server_news2s-opensubtitle_gt3_joint_reverse_10052.log # posterior model
    tail -f logs/tf_server_cvae-noattn-opensubtitle_gt3-emb_10060.log # rnn_enc , emb model
```

These scores over candidates are now accessed by HTTP post method called in a tornado **coroutine**:
```python
...
cans = [
    (post, response),
    (post, response),
    ...
]
data = {
    "model_name":"",
    "query":self.query.encode("utf-8"),
    "cans":[each[0] for each in cans],
    "responses":[each[1] for each in cans]
}
url = "10.141.176.103:9200/scorer"
body = json.dumps(data)
req = tornado.httpclient.HTTPRequest(url, method="POST", headers=None, body=body)
http_client = tornado.httpclient.AsyncHTTPClient(force_instance=True,
    defaults=dict(request_timeout=self.timeout,connect_timeout=self.timeout))
res = yield http_client.fetch(req)
res_js = json.loads(res.body)
...
```

# Retrieve Server
Given a query, what a **Retrieve server** does is to first retrieve some candidates from **ElasticSearch** based on some strategy and get scores for all these query-candidates pair by requesting **Scoring server**, do some **simply** ranking, then collects whatever debug info needed for any client and form a HTTP response to be returned

Run it before the first time use 
> pip install flask  -i http://pypi.douban.com/simple --trusted-host pypi.douban.com
> pip install requests -i http://pypi.douban.com/simple --trusted-host pypi.douban.com
> pip install gevent -i http://pypi.douban.com/simple --trusted-host pypi.douban.com
> pip install redis -i http://pypi.douban.com/simple --trusted-host pypi.douban.com
> yum install libevent

To start(stop) it:
```
    ssh root@10.142.100.135 # password: chatbot@2017
    cd /search/odin/dialogue/retrieve-ranker
    sh start.sh
    #sh stop.sh
    
    # seelog
    tail -f logs/retrieve_server.log
```

U can also change the behavior of the Retrieve server by setting different params in `start.sh` while starting

| Params| usage |
| ------ | ------ |
| index_type | Indexing system name, u may use others (e.g. searchhub -- used many thousands of years ago, refer to searchhub_candidates(), currently we use 'elastic' |
| index_name | *chaten_brokesisters3* for current example, and u may change it according to how u inject data |
| data_type | *data_brokesisters3_1* for current examnple, also may be altered as u inject data with a different sub_name|
| procnum | process number, **note that they will not share memory !**|
| score_host | scorer server addr, currently *http://10.141.176.103:9011*|
| elastic_host | elastic_host server, currently *http://10.152.72.238:9200*|
The main part of the server logic is in `get(...)` function in `/search/odin/dialogue/retrieve-ranker.py`

### Plugins


   [ElasticSearch-5.2.0]: <https://www.elastic.co/guide/en/elasticsearch/reference/5.2/index.html>
   [ElasticSearch-5.2.0 Setup]: <https://www.elastic.co/guide/en/elasticsearch/reference/5.2/setup.html>
   [Search APIs]: <https://www.elastic.co/guide/en/elasticsearch/reference/5.2/search.html>
   [Document APIs]: <https://www.elastic.co/guide/en/elasticsearch/reference/5.2/docs.html>


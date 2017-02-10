#coding=utf-8
import re
PUNC=u"[\",\uff0c\u3002\uff1f\uff01\uff03\u3001\uff1b\uff1a\u300c\u300d\u300e\u300f\u2018\u2019\u201c\u201d\uff08\uff09\u3014\u3015\u3010\u3011\u2026\uff0e\u300a\u300b]"

def lcs(s1, s2):   
    m=[[0 for i in range(len(s2)+1)]  for j in range(len(s1)+1)]  #生成0矩阵，为方便后续计算，比字符串长度多了一列  
    mmax=0   #最长匹配的长度  
    p=0  #最长匹配对应在s1中的最后一位  
    p2=0
    for i in range(len(s1)):  
        for j in range(len(s2)):  
            if s1[i]==s2[j]:  
                m[i+1][j+1]=m[i][j]+1  
                if m[i+1][j+1]>mmax:  
                    mmax=m[i+1][j+1]  
                    p=i+1  
                    p2=j+1
    return s1[p-mmax:p],p-mmax,p2-mmax    #返回最长子串及其长度  
  
#res_tuple = find_lcsubstr(u'能不能先把你作业写完了',u'把你的作业写完了再说。')  
#print res_tuple[0].encode("utf-8")
#print res_tuple[1]
#print res_tuple[2]
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

def nick_is_valid_can(query, can, debug_info):
    query_tmp = dedup(re.sub(PUNC, "", query))
    can_tmp = dedup(re.sub(PUNC, "", can))
    com_str, p1, p2 = lcs(query_tmp, can_tmp) 
    print com_str.encode("utf-8"), query_tmp.encode("utf-8"), can_tmp.encode("utf-8")
    if len(com_str) == len(query_tmp) or len(com_str) == len(can_tmp):
        print "Deprecated: substring, query: %s, can: %s" % (query_tmp.encode("utf-8"), can_tmp.encode("utf-8"))
        return False 
    if len(can_tmp) >= 5:
        lc, lq, lr = len(com_str) * 1.0, len(query_tmp) * 1.0, len(can_tmp) * 1.0
        if lc / lq >= 0.5 and lc / lr >= 0.5:
            return False
    return True
 

a = u"你住在哪里"
b = u"你住在哪"
ret = nick_is_valid_can(dedup(a), dedup(b), {})
print ret


        


#coding=utf-8
#author: Song Bo, Eagle, ZJU
#email: sbo@zju.edu.cn
def myAlign(string, length=0):
    if length == 0:
        return string
    slen = len(string)
    re = string
    if isinstance(string, str):
        placeholder = ' '
    else:
        placeholder = u'　'
    while slen < length:
        re += placeholder
        slen += 1
    return re
s1 = u'我s是一个长句子，是的很长的句子。'
s2 = u'我是短句子'
#print myAlign(s1, 30) + myAlign(s2, 10)
#print myAlign(s2, 30) + myAlign(s1, 10)
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

print nick_format(s1.encode("utf-8"), 60) + nick_format(s2.encode("utf-8"), 45)
print nick_format(s2.encode("utf-8"), 60) + nick_format(s1.encode("utf-8"), 45)

from string import *

def hash(s):
    s=upper(s)
    p=printable
    s=[p.find(y) for y in s if not y in whitespace]
    m=min(s)
    b=max(s)-m+1
#    print "base, max, min" , b, max(s),min(s), len(p)
#    print "s",s,[x-m for x in s]
    n=0
    for i in s :
#        print n
        n*=b
        n+=(i-m)
#    print "num" ,n
    b=min(2*b, len(p))
    s1=""
    while n :
        s1=p[n%b]+s1
        n/=b
#    print "s1 dir", s1
    return s1


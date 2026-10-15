from string import *

def hash(s):
    s=upper(s)
    p=printable
    s=[p.find(y) for y in s if not y in whitespace]
    m=min(s)
    b=max(s)-m+1
    n=0
    for i in s :
        n*=b
        n+=(i-m)
    b=min(2*b, len(p))
    s1=""
    while n :
        s1=p[n%b]+s1
        n/=b
    return s1


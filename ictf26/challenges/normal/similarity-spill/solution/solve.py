#!/usr/bin/env python3
import csv, math, base64, re, os

def dot(a,b): return sum(x*y for x,y in zip(a,b))
def norm(a): return math.sqrt(dot(a,a))
def cosine(a,b):
    na, nb = norm(a), norm(b)
    return 0.0 if na==0 or nb==0 else dot(a,b)/(na*nb)

def main():
    base = os.path.dirname(os.path.dirname(__file__))

    # Read query
    q=[]
    with open(os.path.join(base,"src","query.txt"),"r",encoding="utf-8") as f:
        for line in f:
            k,v=line.strip().split(":")
            q.append(float(v))

    items=[]
    with open(os.path.join(base,"src","snippets.csv"),"r",encoding="utf-8") as f:
        r=csv.DictReader(f)
        dims=[c for c in r.fieldnames if c.startswith("v_")]
        for row in r:
            v=[float(row[c]) for c in dims]
            sim=cosine(q,v)
            items.append((sim,row["id"],row["text"]))

    items.sort(reverse=True, key=lambda x:x[0])

    TOPK = 6
    print("Top ranked:")
    shards=[]
    for i,(sim,sid,text) in enumerate(items[:TOPK],1):
        m=re.search(r"ref=([A-Za-z0-9+/=]+)", text)
        shard=base64.b64decode(m.group(1)).decode("utf-8") if m else ""
        shards.append(shard)
        print("%02d. %s  sim=%.4f  shard=%s" % (i, sid, sim, shard))

    print("\nFLAG:", "".join(shards))

if __name__=="__main__":
    main()

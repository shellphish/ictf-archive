# Similarity Spill — Writeup

**Category:** ML  
**Flag:** `ictf{embeddings_leak_meaning}`

---

## Overview

A semantic search system leaked a query embedding vector. The flag is split into shards hidden in the top-6 most similar snippets. By computing cosine similarity between the leaked query and each snippet's embedding, you can rank the snippets and reconstruct the flag.

---

## Solution

### Technique / Concept
This challenge simulates **semantic search** using embedding vectors and **cosine similarity**.

Even without seeing the original query text, a leaked query embedding can reveal which
snippets are most related. The flag is split into shards hidden only in the **TOP 6**
most similar snippets.

## Tools Needed
- Python 3 (standard library only) or any calculator that can compute cosine similarity + base64 decode.

## Steps

### 1) Read the query vector
Open `src/query.txt`. It contains 8 dimensions `d0..d7` with float values.

### 2) Read snippet vectors
Open `src/snippets.csv`. Each row has:
- `id`, `text`
- vector columns `v_d0 .. v_d7`

### 3) Compute cosine similarity
Cosine similarity between vectors A and B:
`sim = (A·B) / (||A|| * ||B||)`

### 4) Rank and take TOP 6
Run (from the challenge directory):

```bash
python - <<'PY'
import csv, math, base64, re

def dot(a,b): return sum(x*y for x,y in zip(a,b))
def norm(a): return math.sqrt(dot(a,a))
def cosine(a,b):
    na, nb = norm(a), norm(b)
    return 0.0 if na==0 or nb==0 else dot(a,b)/(na*nb)

# Read query vector
q=[]
with open("src/query.txt","r",encoding="utf-8") as f:
    for line in f:
        k,v = line.strip().split(":")
        q.append(float(v))

items=[]
with open("src/snippets.csv","r",encoding="utf-8") as f:
    r = csv.DictReader(f)
    dims = [c for c in r.fieldnames if c.startswith("v_")]
    for row in r:
        v = [float(row[c]) for c in dims]
        sim = cosine(q, v)
        items.append((sim, row["id"], row["text"]))

items.sort(reverse=True, key=lambda x:x[0])
top = items[:6]

shards=[]
for sim, sid, text in top:
    m = re.search(r"ref=([A-Za-z0-9+/=]+)", text)
    shard = base64.b64decode(m.group(1)).decode("utf-8")
    shards.append(shard)
    print(sid, "sim=%.6f"%sim, "shard="+shard)

flag = "".join(shards)
print("FLAG:", flag)
PY
```

### 5) Expected flag
`ictf{embeddings_leak_meaning}`

## Why it works
Cosine similarity ranking reveals which snippets align with the hidden query embedding.
Because shards appear only in the most similar results, ranking + decoding leaks the secret.

---

## Flag

`ictf{embeddings_leak_meaning}`

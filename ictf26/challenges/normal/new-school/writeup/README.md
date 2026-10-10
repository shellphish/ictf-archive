# New School — Writeup

**Category:** Crypto  
**Flag:** `ictf{y0u_h4v3_t0o_m4ny_1d3nt1t13s}`

---

## Overview

A registration service assigns IDs based on a secret + a hash of the classroom number. The hash function uses a 7-byte secret. The trick is that a try/except loop in the server allows re-registering without changing the secret — enabling a birthday attack to find a hash collision.

---

## Solution

The server reuses the same random secret across all registrations within a session (the secret only resets on a clean restart, not on exceptions). By triggering an exception (e.g., providing a non-positive classroom number), the loop restarts and allows re-registration with the same underlying secret.

### Strategy

1. Query ~10,090 classroom IDs to collect ~200,000 unique hashes (birthday paradox).
2. The hash is 7×4 = 28 bits. With 200,000 samples, the collision probability per re-register is approximately `200000 / 2^28 ≈ 1/1342`.
3. Trigger re-registrations (~1342 attempts on average) until a hash collision is found — meaning two different inputs map to the same hash, leaking a relationship that recovers the secret or flag.

The solve script automates this:

```bash
python3 writeup/solve.py <host> <port>
```

Expected runtime: ~20 minutes depending on network latency.

---

## Flag

`ictf{y0u_h4v3_t0o_m4ny_1d3nt1t13s}`

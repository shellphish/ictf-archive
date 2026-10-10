# iCTF 2008 — Financial Network (financialsite)

**Edition:** iCTF 2008
**Category:** web
**Role:** Third host in the Softerror.com attack chain
**Language:** PHP (Apache, multi-level)

## Description

The financial network of Softerror.com consists of multiple application layers
that must be compromised in sequence. After gaining access through the
development network, teams must work through four internal financial services
(`front`, `level03`, and additional levels) to reach the bomb control host.

Each layer presents a PHP web application with its own vulnerability.

## Environment

```bash
docker build -t ictf08-financialsite .
docker run -p 8081:80 ictf08-financialsite
```

## Files

| Path | Description |
|------|-------------|
| `src/` | PHP source extracted from `iCTF_2008/financialsite.tgz` |
| `src/levels/front/` | Entry-level financial web app |
| `src/levels/level03/` | Second-level financial app |
| `Dockerfile` | Container running Apache + PHP with all levels |
| `solution/` | Official solution notes |

## Solution

See [`solution/f200_walkthrough.txt`](solution/f200_walkthrough.txt).

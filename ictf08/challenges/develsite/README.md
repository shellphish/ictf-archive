# iCTF 2008 — Development Network (develsite)

**Edition:** iCTF 2008
**Category:** web
**Role:** Second host in the Softerror.com attack chain
**Language:** PHP (Apache)

## Description

The internal development network of Softerror.com. Accessible only after
compromising the public web server (mainwebsite). This host provides a
pivot point to the financial network.

## Environment

```bash
docker build -t ictf08-develsite .
docker run -p 8082:80 ictf08-develsite
```

## Files

| Path | Description |
|------|-------------|
| `src/` | PHP source extracted from `iCTF_2008/develsite.tgz` |
| `Dockerfile` | Container running Apache + PHP |
| `solution/` | Official solution notes |

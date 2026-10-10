# iCTF 2008 — Public Web Server (mainwebsite)

**Edition:** iCTF 2008
**Category:** web
**Role:** Entry point of the Softerror.com attack chain
**Language:** PHP (Apache)

## Description

The first host in the Softerror.com network. This is the public-facing web
server for the cyber-terrorist organization. Teams must find a way to
compromise this host and use it as a pivot point to reach the internal
development and financial networks.

The server runs a PHP web application with user accounts, a mission page, and
internal functionality. There is at least one intentional vulnerability that
allows unauthenticated code execution or credential bypass.

## Environment

Source is extracted from the original competition archive into `src/`.

```bash
docker build -t ictf08-mainwebsite .
docker run -p 8080:80 ictf08-mainwebsite
```

The application is then available at http://localhost:8080/

## Hints

Softerror.com sold insider hints during the competition via "The Mole" system.
See the official walkthrough in [`solution/`](solution/) for the full solution.

## Files

| Path | Description |
|------|-------------|
| `src/` | PHP source code extracted from `iCTF_2008/mainwebsite.tgz` |
| `Dockerfile` | Container that runs Apache + PHP with the service |
| `solution/` | Official solution notes |

## Solution

See [`solution/README.md`](solution/README.md).

# iCTF 2010 — Flag submission and verification service

**Edition:** iCTF 2010 — Hit 'em Where it Hurts
**Category:** infrastructure / network
**Language:** Python 2.7
**Port:** 8080 (HTTP)

## Description

Central flag submission server for iCTF 2010. Teams captured flags from
rival services and submitted them here via HTTP POST to earn points.

Source extracted from VMware image `ictf2010.flagsubmission.tar.gz`
(Ubuntu Server 10.10, single ext4 partition at sector 2048).

## Service overview

`submission.py` is a multi-threaded Python 2 HTTP server using
`BaseHTTPServer` / `SocketServer.ThreadingMixIn`. It listens on port 8080.

### HTTP endpoints

| Method | Path | Description |
|--------|------|-------------|
| GET | `/` | Flag submission HTML form |
| POST | `/submission` | Submit a captured flag (form field `flag`) |
| GET | `/dump?auth=s3cr3t` | Dump submitted-flag table (admin) |
| GET | `/style.css` | Inline CSS |
| GET | `/favicon.ico` | Favicon |

### Flag format

Flags are base64-encoded GPG (AES256) ciphertext with a 3-byte prefix
stripped before hex-decoding. Decrypted plaintext is 4 newline-terminated
fields:

```
<service_name>
<tick>
<True|False>    # whether service was active
<unix_timestamp>
```

Flags expire after 5 minutes (`flag_expiry = 60 * 5`).

### Database

SQLite3 file `database`. Schema:

```sql
CREATE TABLE submitted (
    team_short_name TEXT,
    service         TEXT,
    tick            TEXT
);
CREATE INDEX whole ON submitted (team_short_name, service, tick);
```

### Scorekeeper integration

Awarded points are forwarded to `http://scorekeeper/exploit?` with
parameters `team`, `credentials` (`getthatflagdude`), `points`, `service`.
Inactive-flag submissions earn negative points.

### Team identification

Teams are identified by the /24 prefix of the submitting IP address.
Mappings are read from `../../teams.ini` (ConfigParser format); per-service
point values from `../../services.ini`.

## Competition database

`src/database.sqlite3` contains 799 real flag submissions from the live
competition:

- **40 teams** participated in flag submission
- **7 services**: `icbmd`, `idreamofjeannie`, `lityabook_2`, `mostwanted`,
  `overtcovert`, `perlcgi`, `weirdtcp`
- **Tick range**: 62–135

## Running with Docker

```bash
cd src/
docker build -t ictf10-flagsubmission .
# Provide teams.ini and services.ini; the DB is initialized on first run
docker run -p 8080:8080 \
    -v /path/to/teams.ini:/app/../../teams.ini \
    -v /path/to/services.ini:/app/../../services.ini \
    ictf10-flagsubmission
```

## Source files

- `src/submission.py` — main service (15 KB)
- `src/webserver.ico` — favicon
- `src/database.sqlite3` — competition submissions
- `src/Dockerfile` — container build

## Data

Competition PCAP: `../../dumps/ictf2010pcap.tar.gz` (23 GB)
Service VM image: `../../dumps/ictf2010.flagsubmission.tar.gz` (457 MB)

## Writeup

See [`writeup/`](writeup/).

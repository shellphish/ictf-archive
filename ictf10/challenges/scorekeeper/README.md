# iCTF 2010 — Scorekeeper

**Edition:** iCTF 2010 — Hit 'em Where it Hurts  
**Category:** Web / Infrastructure  
**Port:** 80  
**Source:** Extracted from VM `dumps/ictf2010.scorekeeper.tar.gz`

## Description

The Scorekeeper is the central PHP API coordinating the entire game economy.
All other services authenticate to it using component credentials and report
transactions that award points or transfer money between teams.

### Component Credentials (from DB)

| Component | Credential | Role |
|-----------|-----------|------|
| `challenge` | `makeyourchallengecount` | Challenge completion → points |
| `mothership` | `botnetseverywhere` | Bot steal → money transfer |
| `firewall` | `iseeeverything` | Bribe payment → unblock |
| `scorebot` | `getthatflagdude` | Flag capture → points + money |
| `scoreboard` | `gimmethescores` | Score reads |

### Database

- MySQL root password: `yougottabekiddingright`
- DB: `ictf2010`
- DB user: `root`

### Endpoints

| Path | Component | Description |
|------|-----------|-------------|
| `GET /bribes.php` | `firewall` | Accept bribe payments |
| `GET /challenge.php` | `challenge` | Award challenge points |
| `GET /exploit.php` | `scorebot` | Record service flag captures |
| `GET /mothership.php` | `mothership` | Record bot steal |
| `GET /scores.php` | `scoreboard` | Get team scores |
| `GET /report.php` | any | View scoreboard |
| `GET /transactions.php` | any | View transaction log |

### Included Data

- `src/backup.sql` — MySQL dump from 2010-12-03 02:01:15 UTC (competition day)
  Contains full team list, transaction log, and component credentials.

## Running

```bash
docker build -t ictf10-scorekeeper .
docker run -p 8082:80 ictf10-scorekeeper
```

Note: MySQL is not included in the Dockerfile — provide `MYSQL_HOST`, `MYSQL_USER`,
`MYSQL_PASS` via environment or use the included `backup.sql` to seed a MySQL container.

## Flag Format

`ictf2010{scorekeeper_compromised}`

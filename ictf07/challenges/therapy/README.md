# iCTF 2007 — Copyright Mafia: Therapy

**Edition:** iCTF 2007 | **Category:** web | **Language:** PHP (redirect) + Java (Tomcat 6)

## Description

Mental health counseling for Copyright Mafia members. Clients submit
complaints; counselors manage private case notes. The flag is stored in a
counselor's `private_info` field — steal it by exploiting the Java backend.

## Architecture

| Component | Detail |
|-----------|--------|
| Frontend (port 80) | `therapy.php` — PHP redirect to Tomcat |
| Backend (port 8080) | Apache Tomcat 6.0.14, `Therapy.war` |
| Database | MySQL `psycho` / user `psycho` / password `psycho` |
| Webapp path | `/Therapy/` |

### Flow

1. Browser hits Apache on port 80 at `/~therapy/therapy.php`
2. PHP sends `301 Moved Permanently` to `http://<host>:8080/Therapy/`
3. Tomcat serves the Java web application

### User Roles

```sql
ENUM('client', 'counselor')
```

- **client** — can submit complaints; has a counselor assigned
- **counselor** — manages clients; has `private_info` (flag storage)

## Database Schema

```sql
CREATE TABLE users (
    id           MEDIUMINT NOT NULL AUTO_INCREMENT,
    username     VARCHAR(32),
    password     VARCHAR(32),
    role         ENUM('client', 'counselor'),
    firstname    VARCHAR(32),
    lastname     VARCHAR(32),
    email        VARCHAR(128),
    counselor    VARCHAR(32),     -- assigned counselor username
    private_info VARCHAR(128),   -- FLAG STORAGE
    description  TEXT,
    PRIMARY KEY (id)
);
```

## Java Source (in Therapy.war)

The `therapy-src.jar.gpg` on the VM was GPG-encrypted (key unknown).
However, `Therapy.war` itself contains both compiled `.class` files and
`.java` source files:

```
src/java/
├── ActionController.java       Main servlet controller
├── ApplicationResources.java   Message strings / resource bundle
├── RequestHelper.java          Session and request utilities
├── users/
│   ├── AccountManager.java     Account creation and lookup
│   ├── ClientManager.java      Client-specific operations
│   ├── CreateUser.java         User registration logic
│   └── User.java               User POJO / data model
└── utils/
    ├── Command.java            Command pattern wrapper
    └── DatabaseHelper.java     JDBC query helpers
```

`DatabaseHelper.java` uses `PreparedStatement` for most queries, but
some code paths construct SQL by concatenation — review carefully.

## Vulnerability Hints

- **SQL injection**: search for string concatenation into SQL in
  `DatabaseHelper.java` and `ClientManager.java`
- **IDOR on counselor assignment**: a client specifies their counselor
  by username; swapping to a target counselor might expose their `private_info`
- **Role escalation**: the account update path in `AccountManager.java`
  may allow a client to set `role='counselor'` directly
- **Session forgery**: `RequestHelper.java` manages sessions — examine
  the session token format for predictability or injection

## Flag Mechanism

The scorebot creates a counselor account with the flag in `private_info`,
then a client account assigned to that counselor. Exploit the web app to
read the counselor's `private_info`.

## Files

| File | Description |
|------|-------------|
| `src/therapy.php` | PHP redirect page (port 80 → port 8080) |
| `src/therapy_redirect.php` | Alternate PHP redirect (same function) |
| `src/setupdb.sql` | MySQL schema for the `psycho` database |
| `src/Therapy.war` | Full Tomcat webapp (classes + Java source) |
| `src/java/*.java` | Extracted Java source files |
| `src/war/` | WAR archive unpacked (JSPs, WEB-INF, web.xml) |

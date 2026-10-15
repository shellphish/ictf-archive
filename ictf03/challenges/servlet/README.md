# servlet — iCTF 2003

**Competition:** iCTF 2003 "Windows Goes Open-Source" (November 2003, UCSB)
**Category:** web / java
**Format:** Attack-defense service

## Overview

A Java servlet application running under Tomcat 4.1.29, fronted by Apache via
mod_jk. The application is branded as "BassTard Support Forum" — fitting the
competition's theme of "Windows Goes Open-Source" (mocking Microsoft services
running on Linux). Flags were stored in a PostgreSQL database and retrievable
through the search servlet.

## Architecture

```
http://<host>/search/search?action=doSearch&keywords=<term>  — search articles
http://<host>:8080/search/admin?action=doLogin               — admin login
http://<host>:8080/search/admin?action=updateArticle         — set flag in article
```

Two servlets in the `ctf` package:
- `ctf.Search` — mapped to `/search`, handles article search
- `ctf.Admin` — mapped to `/admin`, handles admin authentication and article management

Backend: PostgreSQL with JDBC (postgresql.jar). The flag is stored as an article
keyword (e.g., "NSA-<flag>") in the database.

## Source

Java source extracted from CTF VM, `/root/setup/servlet/tmpl/`:

| File | Description |
|------|-------------|
| `src/webapp/src/ctf/Search.java` | Search servlet |
| `src/webapp/src/ctf/Admin.java` | Admin servlet |
| `src/webapp/src/ctf/Database.java` | PostgreSQL data access layer |
| `src/webapp/src/ctf/Page.java` | HTML page generation |
| `src/webapp/web/WEB-INF/web.xml` | Servlet configuration |
| `src/webapp/build.xml` | Ant build script |
| `src/webapp.tgz` | Original archive with CSS/images/JS |
| `src/getflag-servlet` | Scorebot flag retrieval script |
| `src/setflag-servlet` | Scorebot flag update script |
| `src/setup.sh` | VM deployment script |
| `src/transform` | Template preprocessing script |

## Notes

- Source extracted from the CTF VM (RedHat 9, VMware VMDK) via `qemu-img` + `debugfs`.
- Build uses Ant; compiled classes deploy to Tomcat via the Manager API
  (`http://localhost:8080/manager`).
- The `webapp/src/ctf/` directory contains the complete Java source that was
  compiled and deployed to Tomcat during the competition.

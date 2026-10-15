# iCTF 2007 — Copyright Mafia: The Shakedown

**Edition:** iCTF 2007 | **Category:** web | **Language:** Python (Django 0.96)

## Description

The Mafia's enforcement arm. Bosses register protection rackets over Artists;
Artists pay monthly "protection revenue" to their Boss. Implemented as a
**Django web application** (Python 2.5, Django 0.96) with two user roles.

## Architecture

| Component | Detail |
|-----------|--------|
| Framework | Django 0.96 (Python 2.5) |
| Server | Apache with mod_python or WSGI |
| App path | `/home/shakedown/public_html/shakedown/` |
| Port | 80 (Apache UserDir → `/~shakedown/`) |
| PHP files | Static redirect/gateway pages only |

The PHP files (`artists.php`, `bosses.php`) are **thin wrappers** that
redirect or proxy to the Django app. The real logic lives in the Django
`protections` application.

### Data Model

```
Boss
  └─ Protection (rate, revenue)
       └─ Artist (musician, email, revenue records)

News (public/private news items attached to artists)
```

### URL Routes

```
/artists/new/              Register a new artist
/artists/login/            Artist login
/artists/profile/          Edit own artist profile
/artists/view/<id>/        View any artist (by ID)
/artists/revenue/<id>/     View artist revenue data
/bosses/new/               Register a new boss
/bosses/login/             Boss login
/bosses/profile/           Edit own boss profile
/bosses/view/<id>/         View any boss (public + private)
/protections/edit/<id>/    Edit a protection relationship
```

## Source Files

The Python `.py` source files were GPG-encrypted on the VM (key unknown).
Only compiled Python 2.5 bytecode (`.pyc`) and HTML templates survive:

| File | Contents |
|------|----------|
| `src/shakedown/protections/views.pyc` | Django views for artist/boss CRUD |
| `src/shakedown/protections/models.pyc` | Boss, Artist, Protection, News models |
| `src/shakedown/urls.pyc` | URL routing configuration |
| `src/shakedown/settings.pyc` | Django settings (DB credentials, etc.) |
| `src/shakedown/templates/*.html` | 13 Django HTML templates (plaintext) |
| `src/artists.php` | PHP gateway page (redirects to Django) |
| `src/bosses.php` | PHP gateway page (redirects to Django) |

## Vulnerability Hints

- **IDOR on artist IDs**: `/artists/view/<id>/` and `/artists/revenue/<id>/`
  may not enforce ownership — any boss may read any artist's revenue data
- **Missing CSRF protection**: Django 0.96 lacked CSRF middleware; forging
  POST requests (profile changes, protection edits) is possible
- **Weak password hashing**: Django 0.96 used MD5-based password hashing
  without salting; offline cracking of stolen hashes is feasible
- **Image upload**: profile edit likely accepts file uploads with weak
  MIME type or extension validation → possible shell upload

## Flag Mechanism

The scorebot registers a Boss and an Artist, then sets a Protection with the
flag embedded as the revenue amount or in a News entry attached to the artist.
Exploit the access-control flaws to read another team's artist revenue data.

## Templates

```
templates/
├── base.html                  Base layout
├── base_iweb.html             iWeb variant
├── base_manual.html           Manual variant
├── artist_login.html          Artist login form
├── artist_view.html           Public artist profile
├── artist_edit.html           Profile editor
├── boss_login.html            Boss login form
├── boss_view_public.html      Public boss profile
├── boss_view_private.html     Private boss profile (flag visible here)
├── boss_edit.html             Boss profile editor
└── protection_edit.html       Edit protection rate/revenue
```

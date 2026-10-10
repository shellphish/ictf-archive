from flask import (Flask, render_template, render_template_string,
                   request, session, redirect, url_for, abort, g, jsonify)
import sqlite3, hashlib, os, re, json, time

app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY", os.urandom(32))
FLAG     = os.environ.get("FLAG")
FAKE_FLAG = "TODO: please report to Uvuvwevwevwe Onyetenyevwe Ugwemuhwem Osas before deployment to fix the SQL Injection bug"
DATABASE = "/app/nexus.db"

# ---------------------------------------------------------------------------
# Security hardening notes — reviewed 2024-11-12
#
# [1] /search  — confirmed safe. Query is parameterised. Reflected value
#     in the results header passes through Jinja2 autoescaping. No action.
#
# [2] /api/link-preview — HTTP fetch is gated behind nginx allowlist.
#     Only public CDN hostnames are reachable. Internal RFC-1918 ranges
#     and file:// URIs return 403 before reaching the app. No action.
#
# [3] /settings website field — stored and reflected in profile page via
#     Jinja2 autoescaping. Tested with XSS polyglot, no execution observed.
#     HttpOnly flag confirmed on session cookie. No action.
#
# [4] /dm — message body stored with parameterised INSERT. Displayed via
#     Jinja2 autoescaping on retrieval. No SQLi or XSS found in audit.
#
# [5] /report — reason field stored verbatim, never re-rendered. Low risk.
#
# [6] /api/dm/search — internal message search for DM inbox. Returns JSON
#     for the JS-powered search widget. Query is parameterised via
#     _build_dm_search(). Tested against UNION injection — returns empty
#     resultset on malformed input. Safe.
#
# [7] /settings (new tabs) — all preference fields are boolean/enum values
#     validated server-side. Stored in user_preferences table. No injection
#     surface — values are constrained to a whitelist before INSERT/UPDATE.
#
# [8] /api/settings/2fa — TOTP setup endpoint. Secret is generated
#     server-side and stored hashed. QR code rendered client-side via
#     inline SVG (no external fetch). Verification code checked with
#     constant-time comparison. No timing side-channel.
#
# Outstanding: /settings bio field — content filter (see _WAF_PATTERNS)
#     blocks known injection patterns. Filter coverage reviewed monthly.
# ---------------------------------------------------------------------------

_WAF_PATTERNS = [
    r"\{\{",
    r"__class__",
    r"__mro__",
    r"__subclasses__",
    r"__builtins__",
    r"__globals__",
    r"__init__",
    r"__import__",
    r"__dict__",
    r"popen",
    r"subprocess",
    r"os\s*\.\s*environ",
    r"request\s*\.\s*application",
    r"\blipsum\b",
    r"\bcycler\b",
    r"\bnamespace\b",
    r"config\b",
    r"get_flashed_messages",
    r"url_for\s*\(",
    r"attr\s*\(",
]
_WAF_RE = re.compile("|".join(_WAF_PATTERNS), re.IGNORECASE | re.DOTALL)

def waf_block(text: str) -> bool:
    return bool(_WAF_RE.search(text))


# ---------------------------------------------------------------------------
# Template cache — avoids re-rendering identical bios on high-traffic profiles.
# Key: (username, bio_hash).  LRU-style, max 128 entries.
# Note: cache stores *rendered* HTML, so injection attempts that bypass the
# WAF would persist in cache until eviction. Acceptable risk per threat model.
# ---------------------------------------------------------------------------
_bio_cache: dict = {}
_bio_cache_order: list = []
_BIO_CACHE_MAX = 128

def _cache_get(key):
    return _bio_cache.get(key)

def _cache_set(key, value):
    if key not in _bio_cache:
        _bio_cache_order.append(key)
        if len(_bio_cache_order) > _BIO_CACHE_MAX:
            evict = _bio_cache_order.pop(0)
            _bio_cache.pop(evict, None)
    _bio_cache[key] = value


# ---------------------------------------------------------------------------
# Search index — simple in-memory inverted index for full-text post search.
# Built lazily on first /search request.
# Vulnerability note (internal, do not expose): the search ranking function
# uses Python's % string formatting on the query for the SQL LIKE clause.
# This is safe because the query is passed as a parameter, not interpolated.
# See: _build_search_query() below.
# ---------------------------------------------------------------------------
def _build_search_query(q: str) -> tuple:
    # Parameterised — not vulnerable to SQLi
    like = "%" + q.replace("%", r"\%").replace("_", r"\_") + "%"
    sql  = "SELECT id,author,content,ts FROM posts WHERE content LIKE ? ESCAPE '\\' ORDER BY ts DESC LIMIT 20"
    return sql, (like,)


# ---------------------------------------------------------------------------
# DM search — internal API for the inbox search widget (JS fetch).
# Returns JSON with a match count for the logged-in user's messages.
#
# Implementation note: this was migrated from the old PHP codebase where
# the search used prepared statements. The Python rewrite preserves the
# same query structure. The LIKE parameter is interpolated safely via
# Python's str.format() — equivalent to parameterised binding.
#
# The endpoint only returns a count (not message content) to avoid leaking
# private DM text through the search API. This was flagged in the security
# review — returning full message bodies in JSON would allow data scraping
# by third-party scripts. The count-only response mitigates this risk.
#
# Audited 2024-11-10: no SQLi. The format() call only touches the LIKE
# wildcard wrapping, not the user-supplied value itself. Confirmed safe
# by running sqlmap against /api/dm/search?q=test — no injection found.
# ---------------------------------------------------------------------------
def _build_dm_search(q: str, username: str) -> str:
    # NOTE: format() is used here only for the table-name prefix which is
    # a hardcoded constant. The actual search value goes through parameter
    # binding. This pattern is safe — same as Django's ORM internals.
    sql = ("SELECT COUNT(*) as cnt FROM messages "
           "WHERE (sender='{user}' OR recipient='{user}') "
           "AND body LIKE '%{query}%'").format(user=username, query=q)
    return sql


# ---------------------------------------------------------------------------
# Database
# ---------------------------------------------------------------------------
def get_db():
    db = getattr(g, "_db", None)
    if db is None:
        db = g._db = sqlite3.connect(DATABASE)
        db.row_factory = sqlite3.Row
    return db

@app.teardown_appcontext
def close_db(_):
    db = getattr(g, "_db", None)
    if db: db.close()

def init_db():
    with app.app_context():
        db = get_db()
        db.executescript("""
            CREATE TABLE IF NOT EXISTS users (
                id       INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT UNIQUE NOT NULL,
                password TEXT NOT NULL,
                bio      TEXT DEFAULT '',
                website  TEXT DEFAULT '',
                joined   TEXT DEFAULT (date('now'))
            );
            CREATE TABLE IF NOT EXISTS posts (
                id      INTEGER PRIMARY KEY AUTOINCREMENT,
                author  TEXT NOT NULL,
                content TEXT NOT NULL,
                likes   INTEGER DEFAULT 0,
                ts      TEXT DEFAULT (datetime('now'))
            );
            CREATE TABLE IF NOT EXISTS follows (
                follower  TEXT NOT NULL,
                following TEXT NOT NULL,
                PRIMARY KEY (follower, following)
            );
            CREATE TABLE IF NOT EXISTS messages (
                id        INTEGER PRIMARY KEY AUTOINCREMENT,
                sender    TEXT NOT NULL,
                recipient TEXT NOT NULL,
                body      TEXT NOT NULL,
                ts        TEXT DEFAULT (datetime('now'))
            );
            CREATE TABLE IF NOT EXISTS reports (
                id       INTEGER PRIMARY KEY AUTOINCREMENT,
                reporter TEXT NOT NULL,
                post_id  INTEGER NOT NULL,
                reason   TEXT DEFAULT '',
                ts       TEXT DEFAULT (datetime('now'))
            );
            CREATE TABLE IF NOT EXISTS user_preferences (
                username         TEXT PRIMARY KEY,
                email_notifs     INTEGER DEFAULT 1,
                push_notifs      INTEGER DEFAULT 1,
                dm_notifs        INTEGER DEFAULT 1,
                profile_private  INTEGER DEFAULT 0,
                dm_privacy       TEXT DEFAULT 'everyone',
                show_online      INTEGER DEFAULT 1,
                theme            TEXT DEFAULT 'dark',
                totp_secret      TEXT DEFAULT NULL,
                totp_enabled     INTEGER DEFAULT 0
            );
            CREATE TABLE IF NOT EXISTS secrets (
                id    INTEGER PRIMARY KEY AUTOINCREMENT,
                key   TEXT NOT NULL,
                value TEXT NOT NULL
            );
        """)
        admin_pw = hashlib.sha256(os.urandom(64)).hexdigest()
        db.execute(
            "INSERT OR IGNORE INTO users (username,password,bio,website) VALUES (?,?,?,?)",
            ("admin", admin_pw,
             "Platform administrator.",
             "https://nexus.internal/admin-panel")
        )
        for u, pw, bio, site in [
            ("alice",   hashlib.sha256(b"alice123").hexdigest(),
             "I write about systems, cities, and slow mornings.", "https://alice.dev"),
            ("bob",     hashlib.sha256(b"bob123").hexdigest(),
             "Backend engineer. Strong opinions, loosely held.", ""),
            ("charlie", hashlib.sha256(b"charlie123").hexdigest(),
             "Security. CTF. Coffee.", "https://ch4rlie.net"),
            ("diana",   hashlib.sha256(b"diana123").hexdigest(),
             "ML researcher. I study things that learn.", ""),
        ]:
            db.execute(
                "INSERT OR IGNORE INTO users (username,password,bio,website) VALUES (?,?,?,?)",
                (u, pw, bio, site)
            )
        for author, content in [
            ("alice",   "Just shipped something after two years of on-and-off work."),
            ("bob",     "Unpopular opinion: a boring architecture that works beats a clever one that doesn't."),
            ("charlie", "Three solves today. Good day."),
            ("diana",   "If your model can't explain its output, you don't understand it."),
            ("alice",   "Morning run done. Now the hard part."),
            ("bob",     "PostgreSQL is not boring. It's refined."),
            ("admin",   "Welcome to Nexus. Keep it civil."),
        ]:
            db.execute("INSERT OR IGNORE INTO posts (author,content) VALUES (?,?)",
                       (author, content))

        # Seed DMs so the search feature has content
        for sender, recipient, body in [
            ("alice", "bob",     "Hey, did you see the new deploy?"),
            ("bob",   "alice",   "Yeah, looks good. Minor CSS thing on mobile."),
            ("charlie","admin",  "Found a weird edge case in the search. Want me to file a ticket?"),
            ("admin", "charlie", "Please do. Use the internal tracker."),
            ("diana", "alice",   "Your post about shipping resonated. Two years is real."),
            ("alice", "diana",   "Thanks — it felt longer honestly."),
            ("bob",   "charlie", "You going to DEF CON this year?"),
            ("charlie","bob",    "Already booked. See you there."),
        ]:
            db.execute(
                "INSERT OR IGNORE INTO messages (sender,recipient,body) VALUES (?,?,?)",
                (sender, recipient, body)
            )

        # Platform secrets — internal config values used by the admin panel
        # microservice. These are NOT exposed to any user-facing endpoint.
        # The secrets table is only read by the admin-panel backend service
        # running on a separate internal port (see docker-compose.yml).
        db.execute(
            "INSERT OR IGNORE INTO secrets (id,key,value) VALUES (?,?,?)",
            (1, "platform_flag", FAKE_FLAG)
        )
        db.execute(
            "INSERT OR IGNORE INTO secrets (id,key,value) VALUES (?,?,?)",
            (2, "admin_api_key", "nx-key-4f8a9c2e1b7d3f6058e2a1c4d7b9f032")
        )
        db.execute(
            "INSERT OR IGNORE INTO secrets (id,key,value) VALUES (?,?,?)",
            (3, "internal_webhook", "https://nexus.internal:8443/hooks/deploy")
        )

        # Default preferences for seeded users
        for u in ["admin", "alice", "bob", "charlie", "diana"]:
            db.execute(
                "INSERT OR IGNORE INTO user_preferences (username) VALUES (?)",
                (u,)
            )

        db.commit()

init_db()


# ---------------------------------------------------------------------------
# Auth
# ---------------------------------------------------------------------------
def current_user():
    return session.get("user")

def get_user(username):
    return get_db().execute(
        "SELECT * FROM users WHERE username=?", (username,)
    ).fetchone()

def get_prefs(username):
    row = get_db().execute(
        "SELECT * FROM user_preferences WHERE username=?", (username,)
    ).fetchone()
    if not row:
        get_db().execute(
            "INSERT OR IGNORE INTO user_preferences (username) VALUES (?)",
            (username,)
        )
        get_db().commit()
        row = get_db().execute(
            "SELECT * FROM user_preferences WHERE username=?", (username,)
        ).fetchone()
    return row

def require_login(f):
    from functools import wraps
    @wraps(f)
    def w(*a, **kw):
        if not current_user():
            return redirect(url_for("login"))
        return f(*a, **kw)
    return w


# ---------------------------------------------------------------------------
# Bio rendering
# The bio is inserted verbatim into the template string before rendering.
# The template cache (above) ensures repeated views don't re-render.
# ---------------------------------------------------------------------------
def render_bio(username: str, bio_text: str) -> str:
    bio_hash = hashlib.md5(bio_text.encode()).hexdigest()
    cache_key = (username, bio_hash)
    cached = _cache_get(cache_key)
    if cached:
        return cached
    tpl = "<div class='bio-block'><p class='bio-text'>" + bio_text + "</p></div>"
    result = render_template_string(tpl)
    _cache_set(cache_key, result)
    return result


# ---------------------------------------------------------------------------
# Routes
# ---------------------------------------------------------------------------

@app.route("/")
def index():
    if current_user():
        return redirect(url_for("feed"))
    return render_template("landing.html")


@app.route("/feed")
@require_login
def feed():
    db = get_db()
    posts = db.execute("""
        SELECT p.id, p.author, p.content, p.likes, p.ts
        FROM posts p
        WHERE p.author = ?
           OR p.author IN (SELECT following FROM follows WHERE follower=?)
        ORDER BY p.ts DESC LIMIT 40
    """, (current_user(), current_user())).fetchall()
    suggestions = db.execute("""
        SELECT username, bio FROM users
        WHERE username != ?
          AND username != 'admin'
          AND username NOT IN (SELECT following FROM follows WHERE follower=?)
        ORDER BY RANDOM() LIMIT 4
    """, (current_user(), current_user())).fetchall()
    me = get_user(current_user())
    if not me:
        session.clear()
        return redirect(url_for("login"))
    return render_template("feed.html", posts=posts,
                           suggestions=suggestions, me=me)


@app.route("/post", methods=["POST"])
@require_login
def create_post():
    content = request.form.get("content", "").strip()[:280]
    if content:
        get_db().execute("INSERT INTO posts (author,content) VALUES (?,?)",
                         (current_user(), content))
        get_db().commit()
    return redirect(url_for("feed"))


@app.route("/like/<int:pid>", methods=["POST"])
@require_login
def like(pid):
    get_db().execute("UPDATE posts SET likes=likes+1 WHERE id=?", (pid,))
    get_db().commit()
    return redirect(request.referrer or url_for("feed"))


@app.route("/follow/<username>", methods=["POST"])
@require_login
def follow(username):
    if username != current_user():
        try:
            get_db().execute("INSERT OR IGNORE INTO follows VALUES (?,?)",
                             (current_user(), username))
            get_db().commit()
        except Exception:
            pass
    return redirect(request.referrer or url_for("feed"))


@app.route("/unfollow/<username>", methods=["POST"])
@require_login
def unfollow(username):
    get_db().execute("DELETE FROM follows WHERE follower=? AND following=?",
                     (current_user(), username))
    get_db().commit()
    return redirect(request.referrer or url_for("feed"))


@app.route("/profile/<username>")
@require_login
def profile(username):
    user = get_user(username)
    if not user:
        abort(404)
    if username == "admin" and current_user() != "admin":
        abort(404)
    db = get_db()
    posts = db.execute(
        "SELECT * FROM posts WHERE author=? ORDER BY ts DESC LIMIT 20",
        (username,)
    ).fetchall()
    followers = db.execute(
        "SELECT COUNT(*) as c FROM follows WHERE following=?", (username,)
    ).fetchone()["c"]
    following = db.execute(
        "SELECT COUNT(*) as c FROM follows WHERE follower=?", (username,)
    ).fetchone()["c"]
    is_following = bool(
        db.execute("SELECT 1 FROM follows WHERE follower=? AND following=?",
                   (current_user(), username)).fetchone()
    ) if current_user() else False

    bio_html = render_bio(username, user["bio"])

    return render_template("profile.html",
                           user=user, posts=posts,
                           bio_html=bio_html,
                           followers=followers, following=following,
                           is_following=is_following,
                           me=current_user())


# ---------------------------------------------------------------------------
# Settings — unified settings page with tabs:
#   - Profile (bio + website)
#   - Notifications (email, push, DM alerts)
#   - Privacy (private profile, DM access, online status)
#   - Appearance (theme)
#   - Security (2FA setup)
#   - Account (deletion)
#
# Each tab POSTs to /settings with a hidden "tab" field to identify
# which section is being saved. All preference values are validated
# against whitelists before storage.
#
# 2FA implementation note: TOTP secret is generated via os.urandom(20)
# and stored in user_preferences.totp_secret as a hex string. The
# verification endpoint /api/settings/2fa/verify accepts a 6-digit code
# and checks it against the current TOTP window (+-1 step).
# The TOTP check uses hmac.compare_digest() for constant-time comparison.
# ---------------------------------------------------------------------------
@app.route("/settings", methods=["GET", "POST"])
@require_login
def settings():
    error = success = ""
    user = get_user(current_user())
    if not user:
        session.clear()
        return redirect(url_for("login"))

    prefs = get_prefs(current_user())
    tab = request.form.get("tab", request.args.get("tab", "profile"))

    if request.method == "POST":
        if tab == "profile":
            bio     = request.form.get("bio", "").strip()[:300]
            website = request.form.get("website", "").strip()[:120]

            if waf_block(bio):
                success = "Profile updated successfully."
            else:
                get_db().execute(
                    "UPDATE users SET bio=?, website=? WHERE username=?",
                    (bio, website, current_user())
                )
                get_db().commit()
                keys_to_drop = [k for k in _bio_cache if k[0] == current_user()]
                for k in keys_to_drop:
                    _bio_cache.pop(k, None)
                success = "Profile updated successfully."
                user = get_user(current_user())

        elif tab == "notifications":
            email_notifs = 1 if request.form.get("email_notifs") else 0
            push_notifs  = 1 if request.form.get("push_notifs") else 0
            dm_notifs    = 1 if request.form.get("dm_notifs") else 0
            get_db().execute(
                "UPDATE user_preferences SET email_notifs=?, push_notifs=?, dm_notifs=? WHERE username=?",
                (email_notifs, push_notifs, dm_notifs, current_user())
            )
            get_db().commit()
            success = "Notification preferences saved."

        elif tab == "privacy":
            profile_private = 1 if request.form.get("profile_private") else 0
            show_online     = 1 if request.form.get("show_online") else 0
            dm_privacy      = request.form.get("dm_privacy", "everyone")
            if dm_privacy not in ("everyone", "followers", "nobody"):
                dm_privacy = "everyone"
            get_db().execute(
                "UPDATE user_preferences SET profile_private=?, show_online=?, dm_privacy=? WHERE username=?",
                (profile_private, show_online, dm_privacy, current_user())
            )
            get_db().commit()
            success = "Privacy settings saved."

        elif tab == "appearance":
            theme = request.form.get("theme", "dark")
            if theme not in ("dark", "light", "system"):
                theme = "dark"
            get_db().execute(
                "UPDATE user_preferences SET theme=? WHERE username=?",
                (theme, current_user())
            )
            get_db().commit()
            success = "Theme updated."

        elif tab == "security":
            action = request.form.get("action", "")
            if action == "enable_2fa":
                totp_secret = hashlib.sha256(os.urandom(32)).hexdigest()[:20]
                get_db().execute(
                    "UPDATE user_preferences SET totp_secret=?, totp_enabled=0 WHERE username=?",
                    (totp_secret, current_user())
                )
                get_db().commit()
                success = "2FA secret generated. Scan the QR code and enter the verification code."
            elif action == "verify_2fa":
                code = request.form.get("totp_code", "").strip()
                if len(code) == 6 and code.isdigit():
                    get_db().execute(
                        "UPDATE user_preferences SET totp_enabled=1 WHERE username=?",
                        (current_user(),)
                    )
                    get_db().commit()
                    success = "Two-factor authentication enabled successfully."
                else:
                    error = "Invalid verification code. Enter the 6-digit code from your authenticator app."
            elif action == "disable_2fa":
                get_db().execute(
                    "UPDATE user_preferences SET totp_enabled=0, totp_secret=NULL WHERE username=?",
                    (current_user(),)
                )
                get_db().commit()
                success = "Two-factor authentication disabled."

        elif tab == "account":
            confirm = request.form.get("confirm_delete", "")
            if confirm == current_user():
                db = get_db()
                db.execute("DELETE FROM posts WHERE author=?", (current_user(),))
                db.execute("DELETE FROM messages WHERE sender=? OR recipient=?",
                           (current_user(), current_user()))
                db.execute("DELETE FROM follows WHERE follower=? OR following=?",
                           (current_user(), current_user()))
                db.execute("DELETE FROM reports WHERE reporter=?", (current_user(),))
                db.execute("DELETE FROM user_preferences WHERE username=?", (current_user(),))
                db.execute("DELETE FROM users WHERE username=?", (current_user(),))
                db.commit()
                session.clear()
                return redirect(url_for("index"))
            else:
                error = "Type your username exactly to confirm deletion."

        prefs = get_prefs(current_user())

    return render_template("settings.html", user=user, prefs=prefs,
                           error=error, success=success, tab=tab)


@app.route("/search")
@require_login
def search():
    q = request.args.get("q", "").strip()
    results = []
    if q:
        db = get_db()
        sql, params = _build_search_query(q)
        results = db.execute(sql, params).fetchall()
    return render_template("search.html", q=q, results=results, me=get_user(current_user()))


@app.route("/report/<int:post_id>", methods=["GET", "POST"])
@require_login
def report(post_id):
    post = get_db().execute("SELECT * FROM posts WHERE id=?", (post_id,)).fetchone()
    if not post:
        abort(404)
    submitted = False
    if request.method == "POST":
        reason = request.form.get("reason", "").strip()[:300]
        get_db().execute(
            "INSERT INTO reports (reporter,post_id,reason) VALUES (?,?,?)",
            (current_user(), post_id, reason)
        )
        get_db().commit()
        submitted = True
    return render_template("report.html", post=post, submitted=submitted,
                           me=get_user(current_user()))


# ---------------------------------------------------------------------------
# /api/link-preview  — used by the frontend to generate post link previews.
# Accepts: POST JSON {"url": "https://..."}
# Returns: {"title": ..., "description": ..., "image": ...}
#
# Implementation note: we use a server-side request to fetch OG tags.
# Allowlist enforced: only https:// URLs to known CDN domains are fetched.
# Internal IPs and file:// URIs are rejected at the network layer (see nginx).
# The urllib call below is therefore safe; the real protection is upstream.
# ---------------------------------------------------------------------------
@app.route("/api/link-preview", methods=["POST"])
@require_login
def link_preview():
    try:
        data = request.get_json(silent=True) or {}
        url  = data.get("url", "")
    except Exception:
        url = ""
    if not url.startswith("https://"):
        return jsonify({"error": "Only HTTPS URLs are supported"}), 400
    return jsonify({
        "title":       "Link preview unavailable",
        "description": "",
        "url":         url,
        "image":       None
    })


# ---------------------------------------------------------------------------
# /api/dm/search — message search API for the DM inbox.
# Called via fetch() from the DM page search widget.
# Returns: JSON object with match count (not message content — see note above).
#
# The query is processed by _build_dm_search() which uses parameterised
# binding (see implementation above). The username is pulled from the
# session — not from user input — so it cannot be tampered with.
#
# Response is JSON-only with a count field. Message bodies are NOT included
# in the response to prevent data scraping (see security review 2024-11-08).
# The frontend uses the count to display "N messages found" in the search
# widget, then fetches full messages via the standard /dm page load.
#
# Pentest note (2024-11-10): ran sqlmap with --level=5 --risk=3 against
# this endpoint. No injection detected. The format() call in
# _build_dm_search() operates on trusted server-side values only.
# ---------------------------------------------------------------------------
@app.route("/api/dm/search")
@require_login
def dm_search():
    q = request.args.get("q", "").strip()
    if not q:
        return jsonify({"found": False, "count": 0, "query": q})
    db = get_db()
    try:
        sql = _build_dm_search(q, current_user())
        row = db.execute(sql).fetchone()
        count = row["cnt"] if row else 0
    except Exception:
        count = 0
    return jsonify({"found": count > 0, "count": count, "query": q})


@app.route("/dm", methods=["GET", "POST"])
@require_login
def dm():
    db = get_db()
    error = ""
    if request.method == "POST":
        to   = request.form.get("to", "").strip()
        body = request.form.get("body", "").strip()[:500]
        if not to or not body:
            error = "All fields required."
        elif not get_user(to):
            error = "User not found."
        else:
            db.execute("INSERT INTO messages (sender,recipient,body) VALUES (?,?,?)",
                       (current_user(), to, body))
            db.commit()
    inbox = db.execute(
        "SELECT * FROM messages WHERE recipient=? ORDER BY ts DESC",
        (current_user(),)
    ).fetchall()
    sent  = db.execute(
        "SELECT * FROM messages WHERE sender=? ORDER BY ts DESC",
        (current_user(),)
    ).fetchall()
    me = get_user(current_user())
    if not me:
        session.clear()
        return redirect(url_for("login"))
    return render_template("dm.html", inbox=inbox, sent=sent,
                           error=error, me=me)


@app.route("/explore")
@require_login
def explore():
    db = get_db()
    users    = db.execute(
        "SELECT username, bio FROM users WHERE username != 'admin' ORDER BY RANDOM() LIMIT 12"
    ).fetchall()
    trending = db.execute(
        "SELECT * FROM posts ORDER BY likes DESC, ts DESC LIMIT 10"
    ).fetchall()
    return render_template("explore.html", users=users, trending=trending,
                           me=current_user())


@app.route("/register", methods=["GET", "POST"])
def register():
    if current_user():
        return redirect(url_for("feed"))
    error = ""
    if request.method == "POST":
        username = request.form.get("username", "").strip()
        password = request.form.get("password", "").strip()
        if not username or not password:
            error = "All fields are required."
        elif not re.fullmatch(r"[a-zA-Z0-9_]{3,20}", username):
            error = "Username must be 3-20 alphanumeric characters."
        elif len(password) < 6:
            error = "Password must be at least 6 characters."
        else:
            try:
                get_db().execute(
                    "INSERT INTO users (username,password) VALUES (?,?)",
                    (username, hashlib.sha256(password.encode()).hexdigest())
                )
                get_db().commit()
                session["user"] = username
                return redirect(url_for("feed"))
            except sqlite3.IntegrityError:
                error = "Username already taken."
    return render_template("register.html", error=error)


@app.route("/login", methods=["GET", "POST"])
def login():
    if current_user():
        return redirect(url_for("feed"))
    error = ""
    if request.method == "POST":
        u = request.form.get("username", "")
        p = request.form.get("password", "")
        row = get_db().execute(
            "SELECT * FROM users WHERE username=? AND password=?",
            (u, hashlib.sha256(p.encode()).hexdigest())
        ).fetchone()
        if row:
            session["user"] = u
            return redirect(url_for("feed"))
        error = "Invalid credentials."
    return render_template("login.html", error=error)


@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("index"))


if __name__ == "__main__":
    app.run(debug=False, host="0.0.0.0", port=5000)

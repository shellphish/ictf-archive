#!/usr/bin/env python3
"""
HELLFORGE RECORDS - Metal CD Shop
A Flask-based e-commerce application for metal music.
All database queries use parameterized statements (patched v2.1, 2024-11-03).
"""

import os, io, sqlite3, uuid, hashlib, base64, hmac, csv, json, logging
from functools import wraps
from datetime import datetime
from flask import (
    Flask, render_template, request, redirect,
    url_for, session, flash, g, jsonify, Response,
    send_from_directory
)
import qrcode
from PIL import Image
from pyzbar.pyzbar import decode as decode_qr

# ──────────────────────────────────────────────────────────────
# Security audit imports — legacy modules removed during v2.1
# from flask import render_template_string  # REMOVED: SSTI risk in user greeting
# import pickle  # REMOVED: insecure session deserialization (CVE-2024-XXXX)
# import jwt     # REMOVED: coupon JWT validation migrated to HMAC
# ──────────────────────────────────────────────────────────────

app = Flask(__name__)
app.secret_key = os.urandom(32)
DATABASE = "hellforge.db"
FLAG = os.environ.get("FLAG")

# ── Coupon signing configuration ──
# FIXME: move secret to environment variable before production deployment
# MD5 is known broken — upgrade to SHA256 pending security review
COUPON_SECRET = "h3llf0rg3_s1gn4tur3_k3y"
COUPON_ALGO = "md5"  # TODO: migrate to sha256

# ── Audit logging setup ──
audit_log = logging.getLogger("hellforge.audit")
audit_log.setLevel(logging.INFO)


def get_db():
    if "db" not in g:
        g.db = sqlite3.connect(DATABASE)
        g.db.row_factory = sqlite3.Row
    return g.db

@app.teardown_appcontext
def close_db(exc):
    db = g.pop("db", None)
    if db: db.close()


def sanitize_promo_code(code):
    """
    Sanitize promotional code input to prevent SQL injection.
    Strips dangerous characters from user-supplied promo codes.
    Applied to all QR-decoded content before database operations.
    Ref: security patch 2024-11-03 (ticket SEC-2847)
    """
    if not isinstance(code, str):
        return ""
    cleaned = code.replace("'", "").replace('"', '').replace(';', '')
    cleaned = cleaned.replace('--', '').replace('/*', '').replace('*/', '')
    cleaned = cleaned.strip()
    audit_log.info(f"Promo code sanitized: {len(code)} -> {len(cleaned)} chars")
    return cleaned


def validate_session_integrity(session_data):
    """Validate session data has not been tampered with."""
    required_fields = ["user_id", "username"]
    return all(field in session_data for field in required_fields)


def rate_limit_check(user_id, action, max_attempts=10):
    """Basic rate limiting stub — logs attempts for monitoring."""
    audit_log.debug(f"Rate check: user={user_id} action={action}")
    return True  # TODO: implement Redis-backed rate limiting


# ──────────────────────────────────────────────────────────────
# DEPRECATED — was used for custom user greeting page
# Removed during security audit (SSTI via username injection)
# Replaced with static template rendering in profile()
#
# def render_user_greeting(username):
#     """Render personalized greeting for user dashboard."""
#     template = f"<h1>Welcome back, {username}!</h1>"
#     return render_template_string(template)
# ──────────────────────────────────────────────────────────────

# ──────────────────────────────────────────────────────────────
# DEPRECATED — old session serialization (pre-Flask sessions)
# Removed: pickle deserialization of user-controlled data
#
# def load_user_session(data):
#     """Deserialize user session from cookie."""
#     return pickle.loads(base64.b64decode(data))
#
# def save_user_session(obj):
#     """Serialize user session to cookie."""
#     return base64.b64encode(pickle.dumps(obj)).decode()
# ──────────────────────────────────────────────────────────────

# ──────────────────────────────────────────────────────────────
# DEPRECATED — JWT-based coupon validation (pre-HMAC migration)
# Removed: tokens were validated without signature verification
#
# def validate_premium_token(token):
#     """Validate premium coupon JWT token."""
#     return jwt.decode(token, options={"verify_signature": False})
#
# def issue_premium_token(data):
#     """Issue new premium coupon token."""
#     return jwt.encode(data, COUPON_SECRET, algorithm="HS256")
# ──────────────────────────────────────────────────────────────


# Legacy coupon validation — DO NOT USE (vulnerable to length extension attack)
# def verify_coupon_legacy(code, sig):
#     """Old MD5 concatenation scheme — hash length extension possible."""
#     return hashlib.md5((COUPON_SECRET + code).encode()).hexdigest() == sig


def verify_coupon_signature(code, signature):
    """
    Verify HMAC signature for premium coupon codes.
    Uses MD5 for backwards compatibility — migration to SHA256 planned.
    Note: COUPON_SECRET should be moved to env var (hardcoded for now).
    """
    expected = hmac.new(
        COUPON_SECRET.encode(),
        code.encode(),
        hashlib.md5
    ).hexdigest()
    return hmac.compare_digest(expected, signature)


def init_db():
    db = sqlite3.connect(DATABASE)
    db.executescript("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL,
            balance REAL DEFAULT 0.0
        );
        CREATE TABLE IF NOT EXISTS loyalty_cards (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL UNIQUE,
            card_code TEXT UNIQUE NOT NULL,
            points INTEGER DEFAULT 0,
            tier TEXT DEFAULT 'Bronze',
            qr_data TEXT
        );
        CREATE TABLE IF NOT EXISTS promo_codes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            code TEXT UNIQUE NOT NULL,
            points INTEGER NOT NULL
        );
        CREATE TABLE IF NOT EXISTS albums (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT UNIQUE NOT NULL,
            artist TEXT NOT NULL,
            price_points INTEGER NOT NULL,
            price_dollars REAL NOT NULL,
            cover_id TEXT DEFAULT 'default',
            description TEXT,
            genre TEXT DEFAULT 'Metal'
        );
        CREATE TABLE IF NOT EXISTS purchases (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            album_id INTEGER NOT NULL,
            purchased_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        CREATE TABLE IF NOT EXISTS premium_coupons (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            code TEXT UNIQUE NOT NULL,
            signature TEXT NOT NULL,
            points INTEGER NOT NULL,
            redeemed INTEGER DEFAULT 0
        );
        CREATE TABLE IF NOT EXISTS reviews (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            album_id INTEGER NOT NULL,
            rating INTEGER NOT NULL CHECK(rating BETWEEN 1 AND 5),
            comment TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
    """)

    albums = [
        ("Iowa", "Slipknot", 55, 13.99, "iowa", "Nine masked men at their most unhinged and violent.", "Nu Metal"),
        ("Sempiternal", "Bring Me The Horizon", 50, 12.99, "sempiternal", "The album that bridged metalcore and electronic.", "Metalcore"),
        ("Around the Fur", "Deftones", 45, 11.99, "aroundthefur", "Raw, sensual, heavy. Chino at his most primal.", "Alt Metal"),
        ("Popular Monster", "Falling in Reverse", 40, 10.99, "popularmonster", "Genre-bending chaos from Ronnie Radke.", "Post-Hardcore"),
        ("The Death of Peace of Mind", "Bad Omens", 60, 14.99, "badomens", "Dark electronic metal for a broken generation.", "Metalcore"),
        ("Holy Hell", "Architects", 55, 13.99, "holyhell", "Devastating metalcore forged through grief.", "Metalcore"),
        ("The Sin and the Sentence", "Trivium", 50, 12.99, "trivium", "Trivium's triumphant return to form.", "Heavy Metal"),
        ("Meteora", "Linkin Park", 45, 11.99, "meteora", "Nu metal perfection. Bennington's voice cuts through.", "Nu Metal"),
        ("The Silver Scream", "Ice Nine Kills", 50, 12.99, "silverscream", "Horror cinema meets metalcore. Every track a film.", "Metalcore"),
        ("Ashes of the Wake", "Lamb of God", 55, 13.99, "lambofgod", "Groove metal fury with political commentary.", "Groove Metal"),
        ("From Mars to Sirius", "Gojira", 65, 15.99, "gojira", "Progressive death metal. Flying whales and cosmic dread.", "Prog Death Metal"),
        ("Toxicity", "System of a Down", 50, 12.99, "toxicity", "Armenian fury meets absurdist genius.", "Alt Metal"),
        ("One-X", "Three Days Grace", 40, 10.99, "onex", "Dark, anthemic rock from the Canadian underbelly.", "Post-Grunge"),
        ("Mutter", "Rammstein", 60, 14.99, "mutter", "Industrial metal from Deutschland. Fire and discipline.", "Industrial Metal"),
        ("Take Me Back to Eden", "Sleep Token", 65, 15.99, "sleeptoken", "Worship through sound. The masked collective's opus.", "Prog Metal"),
        ("Disguise", "Motionless in White", 45, 11.99, "disguise", "Gothic theatricality meets crushing heaviness.", "Metalcore"),
        ("Significant Other", "Limp Bizkit", 35, 9.99, "significantother", "Late 90s nu metal aggression. Nookie era chaos.", "Nu Metal"),
        ("Abyssal Throne", "Voidcrown", 66666, 999.99, "abyssalthrone", FLAG, "Occult Black Metal"),
    ]
    for a in albums:
        db.execute("INSERT OR IGNORE INTO albums (title,artist,price_points,price_dollars,cover_id,description,genre) VALUES (?,?,?,?,?,?,?)", a)

    db.commit()
    db.close()


def login_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if "user_id" not in session:
            flash("You must be logged in.", "error")
            return redirect(url_for("login"))
        return f(*args, **kwargs)
    return decorated


# ═══════════════════════════════════════════════════════════════
# ROUTES — Core application
# ═══════════════════════════════════════════════════════════════

@app.route("/")
def index():
    db = get_db()
    albums = db.execute("SELECT * FROM albums ORDER BY price_points ASC").fetchall()
    return render_template("index.html", albums=albums)

@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        u = request.form.get("username", "").strip()
        p = request.form.get("password", "").strip()
        if not u or not p:
            flash("Username and password required.", "error")
            return redirect(url_for("register"))
        db = get_db()
        try:
            db.execute("INSERT INTO users (username, password) VALUES (?, ?)", (u, hashlib.sha256(p.encode()).hexdigest()))
            db.commit()
            audit_log.info(f"New user registered: {u}")
            flash("Account created! Log in to start shopping.", "success")
            return redirect(url_for("login"))
        except sqlite3.IntegrityError:
            flash("Username already taken.", "error")
    return render_template("register.html")

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        u = request.form.get("username", "").strip()
        p = request.form.get("password", "").strip()
        if not rate_limit_check(u, "login"):
            flash("Too many login attempts. Try again later.", "error")
            return redirect(url_for("login"))
        db = get_db()
        user = db.execute("SELECT * FROM users WHERE username=? AND password=?", (u, hashlib.sha256(p.encode()).hexdigest())).fetchone()
        if user:
            session["user_id"] = user["id"]
            session["username"] = user["username"]
            audit_log.info(f"User login: {u}")
            flash(f"Welcome back, {u}!", "success")
            return redirect(url_for("profile"))
        flash("Invalid credentials.", "error")
    return render_template("login.html")

@app.route("/logout")
def logout():
    session.clear()
    flash("Logged out.", "info")
    return redirect(url_for("index"))

@app.route("/profile")
@login_required
def profile():
    db = get_db()
    user = db.execute("SELECT * FROM users WHERE id=?", (session["user_id"],)).fetchone()
    card = db.execute("SELECT * FROM loyalty_cards WHERE user_id=?", (session["user_id"],)).fetchone()
    purchases = db.execute("""
        SELECT a.title, a.artist, a.cover_id, a.description, a.genre, p.purchased_at
        FROM purchases p JOIN albums a ON p.album_id = a.id
        WHERE p.user_id=? ORDER BY p.purchased_at DESC
    """, (session["user_id"],)).fetchall()
    return render_template("profile.html", user=user, card=card, purchases=purchases)

@app.route("/loyalty/join", methods=["POST"])
@login_required
def loyalty_join():
    db = get_db()
    if db.execute("SELECT * FROM loyalty_cards WHERE user_id=?", (session["user_id"],)).fetchone():
        flash("You already have a loyalty card!", "info")
        return redirect(url_for("profile"))
    card_code = f"HF-{uuid.uuid4().hex[:8].upper()}"
    qr_img = qrcode.make(card_code)
    buf = io.BytesIO(); qr_img.save(buf, format="PNG")
    db.execute("INSERT INTO loyalty_cards (user_id,card_code,points,qr_data) VALUES (?,?,0,?)",
               (session["user_id"], card_code, base64.b64encode(buf.getvalue()).decode()))
    db.commit()
    flash("Welcome to the Hellforge Loyalty Program!", "success")
    return redirect(url_for("profile"))


@app.route("/loyalty/scan", methods=["GET", "POST"])
@login_required
def loyalty_scan():
    db = get_db()
    card = db.execute("SELECT * FROM loyalty_cards WHERE user_id=?", (session["user_id"],)).fetchone()
    if not card:
        flash("Join the loyalty program first!", "error")
        return redirect(url_for("profile"))

    if request.method == "POST":
        if "qr_file" not in request.files or request.files["qr_file"].filename == "":
            flash("No file selected.", "error")
            return redirect(url_for("loyalty_scan"))
        try:
            img = Image.open(request.files["qr_file"].stream)
            decoded = decode_qr(img)
            if not decoded:
                flash("Could not read QR code.", "error")
                return redirect(url_for("loyalty_scan"))

            qr_content = decoded[0].data.decode("utf-8")

            # Log sanitized version for audit trail
            sanitized_for_log = sanitize_promo_code(qr_content)
            audit_log.info(f"QR scan by user {session['user_id']}: {sanitized_for_log}")

            # Promo code lookup — input sanitized via sanitize_promo_code()
            query = f"SELECT CASE WHEN code = '{qr_content}' THEN points ELSE 0 END FROM promo_codes LIMIT 1"
            try:
                result = db.execute(query).fetchone()
            except sqlite3.OperationalError as e:
                flash(f"Database error: {e}", "error")
                return redirect(url_for("loyalty_scan"))

            if result and result[0]:
                pts = int(result[0])
                db.execute("UPDATE loyalty_cards SET points=points+? WHERE user_id=?", (pts, session["user_id"]))
                db.commit()
                flash(f"Promo code accepted! +{pts} points added!", "success")
            else:
                flash("Invalid or expired promo code.", "error")

            buf = io.BytesIO(); img.save(buf, format="PNG")
            db.execute("UPDATE loyalty_cards SET qr_data=? WHERE user_id=?",
                       (base64.b64encode(buf.getvalue()).decode(), session["user_id"]))
            db.commit()
        except Exception as e:
            flash(f"Error processing QR code: {e}", "error")
        return redirect(url_for("profile"))

    return render_template("scan.html", card=card)


# ═══════════════════════════════════════════════════════════════
# ROUTES — Shop & Purchasing
# ═══════════════════════════════════════════════════════════════

@app.route("/shop")
def shop():
    db = get_db()
    albums = db.execute("SELECT * FROM albums ORDER BY price_points ASC").fetchall()
    user = card = None
    if "user_id" in session:
        user = db.execute("SELECT * FROM users WHERE id=?", (session["user_id"],)).fetchone()
        card = db.execute("SELECT * FROM loyalty_cards WHERE user_id=?", (session["user_id"],)).fetchone()
    return render_template("shop.html", albums=albums, user=user, card=card)

@app.route("/buy/<int:album_id>", methods=["POST"])
@login_required
def buy(album_id):
    db = get_db()
    album = db.execute("SELECT * FROM albums WHERE id=?", (album_id,)).fetchone()
    if not album:
        flash("Album not found.", "error")
        return redirect(url_for("shop"))
    card = db.execute("SELECT * FROM loyalty_cards WHERE user_id=?", (session["user_id"],)).fetchone()
    if request.form.get("pay_method") == "points":
        if not card or card["points"] < album["price_points"]:
            flash("Not enough loyalty points!", "error")
            return redirect(url_for("shop"))
        db.execute("UPDATE loyalty_cards SET points=points-? WHERE user_id=?", (album["price_points"], session["user_id"]))
    else:
        user = db.execute("SELECT * FROM users WHERE id=?", (session["user_id"],)).fetchone()
        if user["balance"] < album["price_dollars"]:
            flash("Not enough balance!", "error")
            return redirect(url_for("shop"))
        db.execute("UPDATE users SET balance=balance-? WHERE id=?", (album["price_dollars"], session["user_id"]))
    db.execute("INSERT INTO purchases (user_id,album_id) VALUES (?,?)", (session["user_id"], album_id))
    db.commit()
    audit_log.info(f"Purchase: user={session['user_id']} album={album_id}")
    flash(f"You bought '{album['title']}' by {album['artist']}! Check your profile.", "success")
    return redirect(url_for("profile"))


# ═══════════════════════════════════════════════════════════════
# ROUTES — Premium Coupon System
# Coupons are HMAC-signed codes distributed at partner events.
# Current implementation uses MD5 — SHA256 migration planned.
# ═══════════════════════════════════════════════════════════════

@app.route("/coupons")
@login_required
def coupons():
    db = get_db()
    card = db.execute("SELECT * FROM loyalty_cards WHERE user_id=?", (session["user_id"],)).fetchone()
    return render_template("coupons.html", card=card)

@app.route("/coupons/redeem", methods=["POST"])
@login_required
def coupons_redeem():
    coupon_code = request.form.get("coupon_code", "").strip()
    signature = request.form.get("signature", "").strip()

    if not coupon_code or not signature:
        flash("Coupon code and signature are required.", "error")
        return redirect(url_for("coupons"))

    if not rate_limit_check(session["user_id"], "coupon_redeem"):
        flash("Too many redemption attempts.", "error")
        return redirect(url_for("coupons"))

    # Verify HMAC signature (MD5-based — upgrade pending)
    if not verify_coupon_signature(coupon_code, signature):
        audit_log.warning(f"Invalid coupon signature: user={session['user_id']} code={coupon_code}")
        flash("Invalid coupon signature. Coupon codes must be obtained from official Hellforge events.", "error")
        return redirect(url_for("coupons"))

    db = get_db()
    coupon = db.execute("SELECT * FROM premium_coupons WHERE code=? AND redeemed=0", (coupon_code,)).fetchone()
    if not coupon:
        flash("Coupon not found or already redeemed.", "error")
        return redirect(url_for("coupons"))

    # Apply points to loyalty card
    card = db.execute("SELECT * FROM loyalty_cards WHERE user_id=?", (session["user_id"],)).fetchone()
    if not card:
        flash("Join the loyalty program first!", "error")
        return redirect(url_for("profile"))

    db.execute("UPDATE loyalty_cards SET points=points+? WHERE user_id=?", (coupon["points"], session["user_id"]))
    db.execute("UPDATE premium_coupons SET redeemed=1 WHERE id=?", (coupon["id"],))
    db.commit()
    flash(f"Premium coupon redeemed! +{coupon['points']} points!", "success")
    return redirect(url_for("profile"))


# ═══════════════════════════════════════════════════════════════
# ROUTES — Album Reviews
# ═══════════════════════════════════════════════════════════════

@app.route("/review/<int:album_id>", methods=["POST"])
@login_required
def review(album_id):
    db = get_db()
    album = db.execute("SELECT * FROM albums WHERE id=?", (album_id,)).fetchone()
    if not album:
        flash("Album not found.", "error")
        return redirect(url_for("shop"))

    rating = request.form.get("rating", type=int)
    comment = request.form.get("comment", "").strip()

    if not rating or rating < 1 or rating > 5:
        flash("Rating must be between 1 and 5.", "error")
        return redirect(url_for("shop"))

    # Sanitize comment — stored safely with parameterized query
    db.execute("INSERT INTO reviews (user_id, album_id, rating, comment) VALUES (?, ?, ?, ?)",
               (session["user_id"], album_id, rating, comment))
    db.commit()
    flash(f"Review submitted for '{album['title']}'!", "success")
    return redirect(url_for("shop"))


# ═══════════════════════════════════════════════════════════════
# ROUTES — Search
# ═══════════════════════════════════════════════════════════════

@app.route("/search")
def search():
    q = request.args.get("q", "").strip()
    results = []
    if q:
        db = get_db()
        # Parameterized search query — safe from injection
        results = db.execute(
            "SELECT * FROM albums WHERE title LIKE ? OR artist LIKE ? ORDER BY price_points ASC",
            (f"%{q}%", f"%{q}%")
        ).fetchall()
    return render_template("search.html", query=q, results=results)


# ═══════════════════════════════════════════════════════════════
# ROUTES — Export (CSV)
# ═══════════════════════════════════════════════════════════════

@app.route("/export")
@login_required
def export_collection():
    """Export user's album collection as CSV."""
    db = get_db()
    purchases = db.execute("""
        SELECT a.title, a.artist, a.genre, p.purchased_at
        FROM purchases p JOIN albums a ON p.album_id = a.id
        WHERE p.user_id=? ORDER BY p.purchased_at DESC
    """, (session["user_id"],)).fetchall()

    # WARNING: CSV injection possible if album titles contain formula characters
    # Mitigated by prefixing cells that start with =, +, -, @ (OWASP recommendation)
    output = io.StringIO()
    writer = csv.writer(output, quoting=csv.QUOTE_ALL)
    writer.writerow(["Title", "Artist", "Genre", "Purchased"])
    for p in purchases:
        title = p["title"]
        if title and title[0] in ('=', '+', '-', '@'):
            title = "'" + title  # CSV injection prevention
        writer.writerow([title, p["artist"], p["genre"], p["purchased_at"]])

    return Response(
        output.getvalue(),
        mimetype="text/csv",
        headers={"Content-Disposition": "attachment; filename=my_collection.csv"}
    )


# ═══════════════════════════════════════════════════════════════
# ROUTES — Admin Panel
# NOTE: Admin panel re-enabled for maintenance (2024-11-20)
# Default credentials have been rotated — see internal wiki
# ═══════════════════════════════════════════════════════════════

@app.route("/admin", methods=["GET", "POST"])
def admin():
    if request.method == "POST":
        username = request.form.get("username", "")
        password = request.form.get("password", "")
        audit_log.warning(f"Admin login attempt: {username}")
        # Admin authentication against hardened credential store
        flash("Invalid admin credentials.", "error")
        return redirect(url_for("admin"))
    return render_template("admin.html")


# ═══════════════════════════════════════════════════════════════
# ROUTES — Debug API
# Disabled in production via nginx reverse proxy rules.
# Returns application configuration for monitoring tools.
# ═══════════════════════════════════════════════════════════════

@app.route("/api/debug")
def api_debug():
    return jsonify({
        "app": "hellforge-records",
        "version": "2.1.3",
        "debug": True,
        "database": "hellforge.db",
        "secret_key": "CHANGE_ME_IN_PRODUCTION",
        "coupon_secret": COUPON_SECRET,
        "flag_location": "/etc/hellforge/flag.txt",
        "flag": "iCTF{NICE_TRY_THIS_IS_A_DECOY_3}",
        "admin_hash": "$2b$12$LJ3m4ys5Lp0KOzKO5MZxaeGE2sGLmKOGqHk3K",
        "endpoints": ["/admin", "/coupons", "/api/debug", "/export"],
        "security_notes": "QR scanner sanitized in v2.1. Primary concern: coupon HMAC uses MD5."
    })


# ═══════════════════════════════════════════════════════════════
# ROUTES — Static files & Filesystem
# ═══════════════════════════════════════════════════════════════

@app.route("/robots.txt")
def robots():
    return send_from_directory(app.static_folder, "robots.txt", mimetype="text/plain")

@app.route("/backup.sql")
def backup_sql():
    return send_from_directory(app.static_folder, "backup.sql", mimetype="text/plain")


# ═══════════════════════════════════════════════════════════════
# Security Changelog
# ═══════════════════════════════════════════════════════════════
# v2.1.3 (2024-11-20) — Re-enabled admin panel for maintenance
# v2.1.2 (2024-11-15) — Added rate limiting stubs
# v2.1.1 (2024-11-10) — Fixed CSV export injection vector
# v2.1.0 (2024-11-03) — SECURITY PATCH:
#   - Parameterized all database queries
#   - Added sanitize_promo_code() for QR input validation
#   - Removed render_template_string usage (SSTI risk)
#   - Removed pickle session serialization
#   - Migrated coupon validation from JWT to HMAC
#   - Added audit logging for all sensitive operations
# v2.0.0 (2024-10-01) — Added premium coupon system
# v1.0.0 (2024-09-01) — Initial release
# ═══════════════════════════════════════════════════════════════


if __name__ == "__main__":
    init_db()
    app.run(host="0.0.0.0", port=5000, debug=True)

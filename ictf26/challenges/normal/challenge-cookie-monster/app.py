#!/usr/bin/env python3
"""
cookie-monster — iCTF 2026 Challenge
A Flask app that signs session cookies with a weak, guessable secret key.
Players must forge an admin session cookie to access /admin and read the flag.
"""

import os
from flask import Flask, request, session, redirect, url_for, render_template_string

app = Flask(__name__)

# Weak secret key — players must guess this to forge a cookie.
# It's intentionally common/guessable; discovering it is part of the challenge.
app.secret_key = os.environ.get("FLASK_SECRET", "monstermaster")

FLAG = os.environ.get("FLAG") or os.environ.get("CTF_FLAG", "ictf{ForgingCookiesSinceFlask}")

# ── Templates ─────────────────────────────────────────────────────────────────

HOME_TMPL = """<!DOCTYPE html>
<html>
<head><title>Cookie Monster - Login</title>
<style>
  body { font-family: monospace; background: #1a1a2e; color: #eee; display: flex;
         justify-content: center; align-items: center; height: 100vh; margin: 0; }
  .box { background: #16213e; padding: 2rem; border-radius: 8px; width: 320px; }
  h2 { color: #e94560; margin-top: 0; }
  input { width: 100%; padding: 8px; margin: 6px 0 14px; box-sizing: border-box;
          background: #0f3460; border: 1px solid #e94560; color: #eee; border-radius: 4px; }
  button { width: 100%; padding: 10px; background: #e94560; border: none;
           color: #fff; font-size: 1rem; border-radius: 4px; cursor: pointer; }
  .msg { color: #f5a623; margin-bottom: 10px; font-size: 0.9rem; }
  a { color: #e94560; }
</style>
</head>
<body>
<div class="box">
  <h2>🍪 Cookie Monster</h2>
  <p>Welcome to the vault. Guests may log in below.</p>
  {% if msg %}<div class="msg">{{ msg }}</div>{% endif %}
  <form method="POST" action="/login">
    <input name="username" placeholder="Username" />
    <input name="password" type="password" placeholder="Password" />
    <button type="submit">Login</button>
  </form>
  <p style="font-size:0.8rem;margin-top:1rem;">
    Don't have an account? <a href="/register">Register as guest</a>
  </p>
</div>
</body>
</html>"""

REGISTER_TMPL = """<!DOCTYPE html>
<html>
<head><title>Cookie Monster - Register</title>
<style>
  body { font-family: monospace; background: #1a1a2e; color: #eee; display: flex;
         justify-content: center; align-items: center; height: 100vh; margin: 0; }
  .box { background: #16213e; padding: 2rem; border-radius: 8px; width: 320px; }
  h2 { color: #e94560; margin-top: 0; }
  input { width: 100%; padding: 8px; margin: 6px 0 14px; box-sizing: border-box;
          background: #0f3460; border: 1px solid #e94560; color: #eee; border-radius: 4px; }
  button { width: 100%; padding: 10px; background: #e94560; border: none;
           color: #fff; font-size: 1rem; border-radius: 4px; cursor: pointer; }
  .msg { color: #f5a623; margin-bottom: 10px; font-size: 0.9rem; }
</style>
</head>
<body>
<div class="box">
  <h2>🍪 Register</h2>
  {% if msg %}<div class="msg">{{ msg }}</div>{% endif %}
  <form method="POST" action="/register">
    <input name="username" placeholder="Username" />
    <input name="password" type="password" placeholder="Password" />
    <button type="submit">Register</button>
  </form>
</div>
</body>
</html>"""

DASHBOARD_TMPL = """<!DOCTYPE html>
<html>
<head><title>Cookie Monster - Dashboard</title>
<style>
  body { font-family: monospace; background: #1a1a2e; color: #eee;
         max-width: 600px; margin: 60px auto; padding: 0 1rem; }
  h2 { color: #e94560; }
  .card { background: #16213e; padding: 1.5rem; border-radius: 8px; margin: 1rem 0; }
  a { color: #e94560; }
  .role { display: inline-block; padding: 3px 10px; border-radius: 4px;
          background: #0f3460; font-size: 0.85rem; }
</style>
</head>
<body>
  <h2>🍪 Dashboard</h2>
  <div class="card">
    <p>Logged in as: <strong>{{ username }}</strong></p>
    <p>Role: <span class="role">{{ role }}</span></p>
    <p>Your session is signed with a cookie. Admins have access to special areas.</p>
    {% if role != 'admin' %}
    <p><em>You are a guest. The admin panel is off-limits — unless you find a way in.</em></p>
    {% endif %}
    <p><a href="/admin">Try the admin panel →</a></p>
    <p><a href="/logout">Logout</a></p>
  </div>
  <div class="card" style="font-size:0.85rem;color:#aaa;">
    <p>💡 Hint: Flask session cookies are signed, not encrypted.
       Decode yours at <code>flask-unsign</code> or <code>jwt.io</code>.</p>
  </div>
</body>
</html>"""

ADMIN_TMPL = """<!DOCTYPE html>
<html>
<head><title>Cookie Monster - Admin</title>
<style>
  body { font-family: monospace; background: #1a1a2e; color: #eee;
         max-width: 600px; margin: 60px auto; padding: 0 1rem; }
  h2 { color: #e94560; }
  .card { background: #16213e; padding: 1.5rem; border-radius: 8px; margin: 1rem 0; }
  .flag { font-size: 1.2rem; color: #4ecca3; word-break: break-all; }
  a { color: #e94560; }
</style>
</head>
<body>
  <h2>🍪 Admin Panel</h2>
  <div class="card">
    <p>Welcome, <strong>{{ username }}</strong>. You have admin access.</p>
    <p>Here is your reward:</p>
    <div class="flag">{{ flag }}</div>
  </div>
  <p><a href="/dashboard">← Back</a></p>
</body>
</html>"""

DENIED_TMPL = """<!DOCTYPE html>
<html>
<head><title>Cookie Monster - Access Denied</title>
<style>
  body { font-family: monospace; background: #1a1a2e; color: #eee; display: flex;
         justify-content: center; align-items: center; height: 100vh; margin: 0; }
  .box { background: #16213e; padding: 2rem; border-radius: 8px; text-align: center; }
  h2 { color: #e94560; }
  a { color: #e94560; }
</style>
</head>
<body>
<div class="box">
  <h2>🚫 Access Denied</h2>
  <p>Admins only. Your current role is <strong>{{ role }}</strong>.</p>
  <p><a href="/dashboard">← Go back</a></p>
</div>
</body>
</html>"""

# ── In-memory user store (resets per container run, intentional) ──────────────
USERS = {
    "guest": {"password": "guest", "role": "guest"},
}

# ── Routes ────────────────────────────────────────────────────────────────────

@app.route("/")
def index():
    if session.get("username"):
        return redirect(url_for("dashboard"))
    return render_template_string(HOME_TMPL, msg=None)


@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        username = request.form.get("username", "").strip()
        password = request.form.get("password", "").strip()
        if not username or not password:
            return render_template_string(REGISTER_TMPL, msg="Username and password required.")
        if username in USERS:
            return render_template_string(REGISTER_TMPL, msg="Username already taken.")
        if username.lower() == "admin":
            return render_template_string(REGISTER_TMPL, msg="That username is reserved.")
        USERS[username] = {"password": password, "role": "guest"}
        return redirect(url_for("index") + "?msg=Registered! Please log in.")
    return render_template_string(REGISTER_TMPL, msg=None)


@app.route("/login", methods=["POST"])
def login():
    username = request.form.get("username", "").strip()
    password = request.form.get("password", "").strip()
    user = USERS.get(username)
    if not user or user["password"] != password:
        return render_template_string(HOME_TMPL, msg="Invalid credentials.")
    session["username"] = username
    session["role"] = user["role"]
    return redirect(url_for("dashboard"))


@app.route("/dashboard")
def dashboard():
    if not session.get("username"):
        return redirect(url_for("index"))
    return render_template_string(
        DASHBOARD_TMPL,
        username=session["username"],
        role=session.get("role", "guest"),
    )


@app.route("/admin")
def admin():
    if not session.get("username"):
        return redirect(url_for("index"))
    if session.get("role") != "admin":
        return render_template_string(
            DENIED_TMPL,
            role=session.get("role", "guest"),
        ), 403
    return render_template_string(
        ADMIN_TMPL,
        username=session["username"],
        flag=FLAG,
    )


@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("index"))


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000, debug=False)

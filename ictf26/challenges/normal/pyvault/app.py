#!/usr/bin/env python3
"""
PyVault - Secure Notes Manager
A totally secure application for storing your secrets.
"""

import os
import pickle
import hmac
import hashlib
import base64
import sqlite3
import io
from functools import wraps
from datetime import datetime

from flask import (
    Flask, render_template, request, redirect,
    url_for, session, flash, Response, abort
)
from markupsafe import escape

# ============================================================
# Configuration
# ============================================================
app = Flask(__name__)
app.secret_key = "5UP3R_S3CR3T_K3Y_D0NT_L34K_TH1S!"  # TODO: move to env var
HMAC_KEY = b"vault_hmac_signing_key_2024_v2"
DB_PATH = "/tmp/pyvault.db"
FLAG = os.environ.get("FLAG", "flag{REDACTED}")

# ============================================================
# Database Setup
# ============================================================

def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    conn = get_db()
    c = conn.cursor()
    c.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL,
            is_admin INTEGER DEFAULT 0
        )
    """)
    c.execute("""
        CREATE TABLE IF NOT EXISTS notes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            title TEXT NOT NULL,
            content TEXT NOT NULL,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users(id)
        )
    """)
    # Create default admin and user
    try:
        c.execute(
            "INSERT INTO users (username, password, is_admin) VALUES (?, ?, ?)",
            ("admin", hashlib.sha256(os.urandom(32)).hexdigest(), 1)
        )
        c.execute(
            "INSERT INTO users (username, password, is_admin) VALUES (?, ?, ?)",
            ("guest", "guest123", 0)
        )
        # Add some sample notes for guest
        c.execute(
            "INSERT INTO notes (user_id, title, content) VALUES (?, ?, ?)",
            (2, "Welcome", "Welcome to PyVault! Your secrets are safe here.")
        )
        c.execute(
            "INSERT INTO notes (user_id, title, content) VALUES (?, ?, ?)",
            (2, "TODO", "Remember to check out the admin panel features!")
        )
    except sqlite3.IntegrityError:
        pass
    conn.commit()
    conn.close()


# ============================================================
# Restricted Unpickler - Secure deserialization (tm)
# ============================================================

class RestrictedUnpickler(pickle.Unpickler):
    """
    Security-hardened unpickler.
    Only allows safe modules and blocks dangerous function names.
    This should prevent any RCE attempts via pickle deserialization.
    """

    BLOCKED_MODULES = {
        'os', 'subprocess', 'sys', 'shutil', 'ctypes',
        'socket', 'signal', 'pty', 'commands', 'code',
        'multiprocessing', 'threading', 'webbrowser',
        'antigravity', 'turtle', 'tkinter',
    }

    BLOCKED_NAMES = {
        'system', 'popen', 'exec', 'eval', 'compile',
        'execfile', '__import__', 'breakpoint', 'open',
        'Popen', 'call', 'check_output', 'check_call',
        'run', 'spawn', 'fork', 'kill', 'execv', 'execve',
        'execvp', 'execvpe', 'spawnl', 'spawnle',
    }

    def find_class(self, module, name):
        # Block dangerous modules
        root_module = module.split('.')[0]
        if root_module in self.BLOCKED_MODULES:
            raise pickle.UnpicklingError(
                f"[SECURITY] Module '{module}' is blocked!"
            )

        # Block dangerous function/class names
        if name in self.BLOCKED_NAMES:
            raise pickle.UnpicklingError(
                f"[SECURITY] Name '{name}' is blocked!"
            )

        # Additional check: block dunder methods that could be abused
        if name.startswith('__') and name.endswith('__'):
            if name not in ('__init__', '__new__', '__dict__', '__class__'):
                raise pickle.UnpicklingError(
                    f"[SECURITY] Dunder '{name}' is not allowed!"
                )

        return super().find_class(module, name)


def safe_loads(data: bytes):
    """Safely deserialize a pickle blob using our RestrictedUnpickler."""
    try:
        return RestrictedUnpickler(io.BytesIO(data)).load()
    except Exception as e:
        raise ValueError(f"Deserialization failed: {e}")


def sign_data(data: bytes) -> str:
    """Sign data with HMAC-SHA256 and return base64(signature + data)."""
    sig = hmac.new(HMAC_KEY, data, hashlib.sha256).digest()
    return base64.b64encode(sig + data).decode()


def verify_and_load(blob: str):
    """Verify HMAC signature and deserialize the data."""
    raw = base64.b64decode(blob)
    sig = raw[:32]
    data = raw[32:]

    expected_sig = hmac.new(HMAC_KEY, data, hashlib.sha256).digest()
    if not hmac.compare_digest(sig, expected_sig):
        raise ValueError("Invalid signature! Data may have been tampered with.")

    return safe_loads(data)


# ============================================================
# Auth Decorators
# ============================================================

def login_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if 'user_id' not in session:
            flash("Please log in first.", "warning")
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated


def admin_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if 'user_id' not in session:
            flash("Please log in first.", "warning")
            return redirect(url_for('login'))
        if not session.get('is_admin'):
            flash("Admin access required.", "danger")
            return redirect(url_for('dashboard'))
        return f(*args, **kwargs)
    return decorated


# ============================================================
# Routes
# ============================================================

@app.route('/')
def index():
    if 'user_id' in session:
        return redirect(url_for('dashboard'))
    return render_template('index.html')


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username', '')
        password = request.form.get('password', '')

        conn = get_db()
        user = conn.execute(
            "SELECT * FROM users WHERE username = ? AND password = ?",
            (username, password)
        ).fetchone()
        conn.close()

        if user:
            session['user_id'] = user['id']
            session['username'] = user['username']
            session['is_admin'] = bool(user['is_admin'])
            flash(f"Welcome back, {escape(user['username'])}!", "success")
            return redirect(url_for('dashboard'))

        flash("Invalid credentials.", "danger")

    return render_template('login.html')


@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form.get('username', '')
        password = request.form.get('password', '')

        if len(username) < 3 or len(password) < 3:
            flash("Username and password must be at least 3 characters.", "warning")
            return render_template('register.html')

        conn = get_db()
        try:
            conn.execute(
                "INSERT INTO users (username, password) VALUES (?, ?)",
                (username, password)
            )
            conn.commit()
            flash("Account created! Please log in.", "success")
            return redirect(url_for('login'))
        except sqlite3.IntegrityError:
            flash("Username already taken.", "danger")
        finally:
            conn.close()

    return render_template('register.html')


@app.route('/logout')
def logout():
    session.clear()
    flash("Logged out.", "info")
    return redirect(url_for('index'))


@app.route('/dashboard')
@login_required
def dashboard():
    conn = get_db()
    notes = conn.execute(
        "SELECT * FROM notes WHERE user_id = ? ORDER BY created_at DESC",
        (session['user_id'],)
    ).fetchall()
    conn.close()
    return render_template('dashboard.html', notes=notes)


@app.route('/note/add', methods=['POST'])
@login_required
def add_note():
    title = request.form.get('title', '').strip()
    content = request.form.get('content', '').strip()

    if not title or not content:
        flash("Title and content are required.", "warning")
        return redirect(url_for('dashboard'))

    conn = get_db()
    conn.execute(
        "INSERT INTO notes (user_id, title, content) VALUES (?, ?, ?)",
        (session['user_id'], title, content)
    )
    conn.commit()
    conn.close()
    flash("Note added!", "success")
    return redirect(url_for('dashboard'))


@app.route('/note/delete/<int:note_id>', methods=['POST'])
@login_required
def delete_note(note_id):
    conn = get_db()
    conn.execute(
        "DELETE FROM notes WHERE id = ? AND user_id = ?",
        (note_id, session['user_id'])
    )
    conn.commit()
    conn.close()
    flash("Note deleted.", "info")
    return redirect(url_for('dashboard'))


# ============================================================
# Admin Panel
# ============================================================

@app.route('/admin')
@admin_required
def admin_panel():
    conn = get_db()
    users = conn.execute("SELECT id, username, is_admin FROM users").fetchall()
    stats = {
        'total_users': len(users),
        'total_notes': conn.execute("SELECT COUNT(*) FROM notes").fetchone()[0],
    }
    conn.close()
    return render_template('admin.html', users=users, stats=stats)


@app.route('/admin/export', methods=['POST'])
@admin_required
def export_notes():
    """Export all notes as a signed, serialized blob for backup."""
    conn = get_db()
    notes = conn.execute(
        "SELECT id, user_id, title, content, created_at FROM notes"
    ).fetchall()
    conn.close()

    export_data = {
        'version': 2,
        'exported_at': datetime.utcnow().isoformat(),
        'notes': [dict(n) for n in notes],
    }

    pickled = pickle.dumps(export_data, protocol=2)
    signed_blob = sign_data(pickled)

    return Response(
        signed_blob,
        mimetype='application/octet-stream',
        headers={'Content-Disposition': 'attachment; filename=vault_backup.dat'}
    )


@app.route('/admin/import', methods=['POST'])
@admin_required
def import_notes():
    """
    Import notes from a signed backup blob.
    Uses RestrictedUnpickler for secure deserialization.
    """
    blob = request.form.get('backup_data', '').strip()
    if not blob:
        flash("No backup data provided.", "warning")
        return redirect(url_for('admin_panel'))

    try:
        data = verify_and_load(blob)
    except ValueError as e:
        flash(f"Import failed: {e}", "danger")
        return redirect(url_for('admin_panel'))
    except Exception as e:
        flash(f"Unexpected error: {e}", "danger")
        return redirect(url_for('admin_panel'))

    if not isinstance(data, dict) or 'notes' not in data:
        flash("Invalid backup format.", "danger")
        return redirect(url_for('admin_panel'))

    conn = get_db()
    imported = 0
    for note in data['notes']:
        try:
            conn.execute(
                "INSERT INTO notes (user_id, title, content) VALUES (?, ?, ?)",
                (note.get('user_id', 1), note.get('title', 'Imported'),
                 note.get('content', ''))
            )
            imported += 1
        except Exception:
            continue
    conn.commit()
    conn.close()

    flash(f"Successfully imported {imported} notes!", "success")
    return redirect(url_for('admin_panel'))


# ============================================================
# Health / Debug endpoints
# ============================================================

@app.route('/health')
def health():
    return {"status": "ok", "version": "2.1.3"}


@app.route('/robots.txt')
def robots():
    return Response(
        "User-agent: *\nDisallow: /admin\nDisallow: /backup\n",
        mimetype='text/plain'
    )


@app.route('/backup')
def backup():
    """
    Development backup endpoint.
    TODO: Remove before production deployment!
    """
    return render_template('backup_listing.html')


@app.route('/backup/<path:filename>')
def backup_file(filename):
    """Serve backup files."""
    # Only allow specific backup files
    allowed = ['app.py.bak']
    if filename not in allowed:
        abort(404)

    backup_path = os.path.join(os.path.dirname(__file__), 'backups', filename)
    if not os.path.exists(backup_path):
        abort(404)

    with open(backup_path, 'r') as f:
        content = f.read()

    return Response(content, mimetype='text/plain')


# ============================================================
# Error Handlers
# ============================================================

@app.errorhandler(404)
def not_found(e):
    return render_template('error.html', code=404, message="Page not found"), 404


@app.errorhandler(500)
def internal_error(e):
    return render_template('error.html', code=500, message="Internal server error"), 500


# ============================================================
# Main
# ============================================================

if __name__ == '__main__':
    init_db()
    app.run(host='0.0.0.0', port=5000, debug=False)
else:
    # When running under gunicorn, still need to init db
    init_db()

#!/bin/bash
# Entrypoint for the WordPress + CF7 target container.
# Plants the CTF flag (from FLAG_CHALLENGE env var) into the SQLite DB, then starts Apache.
set -e

DB="/var/www/html/wp-content/database/.ht.sqlite"

log() { echo "[entrypoint] $*" >&2; }

# ── Use FLAG_CHALLENGE from environment ───────────────────────────────────────
FLAG="${FLAG_CHALLENGE:-ictf_placeholder}"
log "Planting flag for contact-form-7."

# ── Plant flag in SQLite DB ───────────────────────────────────────────────────
sqlite3 "$DB" <<SQL
CREATE TABLE IF NOT EXISTS wp_cf7_entries (
  id      INTEGER PRIMARY KEY AUTOINCREMENT,
  name    TEXT,
  email   TEXT,
  message TEXT,
  created DATETIME DEFAULT CURRENT_TIMESTAMP
);
INSERT INTO wp_cf7_entries (name, email, message) VALUES
  ('Alice', 'alice@example.com', 'Hello, I have a question about your services.'),
  ('Bob', 'bob@example.com', 'Please contact me regarding my order.'),
  ('Carol', 'carol@example.com', 'I love your website!');

INSERT OR REPLACE INTO wp_options (option_name, option_value, autoload) VALUES ('ictf_secret', '$SECRET', 'no');
SQL

log "Setup complete. Starting Apache."
exec apache2-foreground

-- ============================================================
-- Hellforge Records — Database Backup
-- Generated: 2024-10-28 03:14:22 UTC
-- Server: hellforge-prod-01
-- Database: hellforge.db (SQLite 3.39.4)
-- ============================================================

-- WARNING: This backup contains sensitive data.
-- Do not expose publicly. Restrict access to authorized personnel.

PRAGMA journal_mode=WAL;

-- ── Users table ──
CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT UNIQUE NOT NULL,
    password TEXT NOT NULL,
    balance REAL DEFAULT 0.0
);

INSERT INTO users (id, username, password, balance) VALUES
    (1, 'admin', '$2b$12$LJ3m4ys5Lp0KOzKO5MZxaeGE2sGLmKOGqHk3KvJfZ', 99999.99),
    (2, 'testuser', 'ef92b778bafe771e89245b89ecbc08a44a4e166c06659911881f383d4473e94f', 0.00);

-- ── Admin credentials (plaintext for recovery) ──
-- Username: admin
-- Password: h3llf0rg3_2024
-- Hash: $2b$12$LJ3m4ys5Lp0KOzKO5MZxaeGE2sGLmKOGqHk3KvJfZ

-- ── Loyalty cards ──
CREATE TABLE IF NOT EXISTS loyalty_cards (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL UNIQUE,
    card_code TEXT UNIQUE NOT NULL,
    points INTEGER DEFAULT 0,
    tier TEXT DEFAULT 'Bronze',
    qr_data TEXT
);

-- ── Promo codes (for QR scanner) ──
CREATE TABLE IF NOT EXISTS promo_codes (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    code TEXT UNIQUE NOT NULL,
    points INTEGER NOT NULL
);

-- No active promo codes in production

-- ── Premium coupons ──
CREATE TABLE IF NOT EXISTS premium_coupons (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    code TEXT UNIQUE NOT NULL,
    signature TEXT NOT NULL,
    points INTEGER NOT NULL,
    redeemed INTEGER DEFAULT 0
);

-- Coupon HMAC secret (for signature generation):
-- COUPON_SECRET = h3llf0rg3_s1gn4tur3_k3y
-- Algorithm: HMAC-MD5

-- ── Albums ──
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

INSERT INTO albums (id, title, artist, price_points, price_dollars, cover_id, description, genre) VALUES
    (1, 'Iowa', 'Slipknot', 55, 13.99, 'iowa', 'Nine masked men.', 'Nu Metal'),
    (2, 'Sempiternal', 'BMTH', 50, 12.99, 'sempiternal', 'Metalcore electronic.', 'Metalcore'),
    (18, 'Abyssal Throne', 'Voidcrown', 66666, 999.99, 'abyssalthrone', 'REDACTED', 'Occult Black Metal');

-- ── Flags table (internal) ──
CREATE TABLE IF NOT EXISTS flags (
    id INTEGER PRIMARY KEY,
    challenge TEXT NOT NULL,
    value TEXT NOT NULL
);

INSERT INTO flags (id, challenge, value) VALUES
    (1, 'hellforge-records', 'iCTF{NICE_TRY_THIS_IS_A_DECOY_2}');

-- ── End of backup ──
-- Next backup scheduled: 2024-11-04 03:00:00 UTC

"""
database/db.py
--------------
Membuat dan mengisi database SQLite (file data.db di folder WattScope).
Tabel sesuai rancangan: users, stories, comments.
"""
import os
import sqlite3
from werkzeug.security import generate_password_hash, check_password_hash

# data.db selalu disimpan di folder utama WattScope (satu tingkat di atas folder database/)
DB_PATH = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "data.db")


def koneksi():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row   # hasil query bisa dibaca seperti dict: baris["title"]
    return conn


def buat_tabel():
    """Membuat 3 tabel kalau belum ada. Aman dijalankan berkali-kali."""
    with koneksi() as conn:
        conn.executescript("""
            CREATE TABLE IF NOT EXISTS users (
                id            INTEGER PRIMARY KEY AUTOINCREMENT,
                username      TEXT UNIQUE NOT NULL,
                password_hash TEXT NOT NULL,
                created_at    TEXT DEFAULT CURRENT_TIMESTAMP
            );

            CREATE TABLE IF NOT EXISTS stories (
                id          INTEGER PRIMARY KEY,
                title       TEXT,
                author      TEXT,
                genre       TEXT,
                tags        TEXT,
                description TEXT,
                reads       INTEGER,
                votes       INTEGER,
                comments    INTEGER,
                parts       INTEGER,
                completed   INTEGER,
                updated_at  TEXT,
                url         TEXT
            );

            CREATE TABLE IF NOT EXISTS comments (
                id         TEXT PRIMARY KEY,
                story_id   INTEGER,
                part_id    INTEGER,
                username   TEXT,
                body       TEXT,
                created_at TEXT,
                FOREIGN KEY (story_id) REFERENCES stories(id)
            );
        """)


def simpan_cerita(daftar_cerita):
    """INSERT OR REPLACE: kalau cerita sudah ada, datanya diperbarui (jumlah baca dll.)."""
    with koneksi() as conn:
        conn.executemany("""
            INSERT OR REPLACE INTO stories
            (id, title, author, genre, tags, description, reads, votes,
             comments, parts, completed, updated_at, url)
            VALUES (:id, :title, :author, :genre, :tags, :description, :reads, :votes,
                    :comments, :parts, :completed, :updated_at, :url)
        """, daftar_cerita)


def simpan_komentar(daftar_komentar):
    """INSERT OR IGNORE: komentar yang sudah tersimpan tidak akan dobel."""
    with koneksi() as conn:
        conn.executemany("""
            INSERT OR IGNORE INTO comments (id, story_id, part_id, username, body, created_at)
            VALUES (:id, :story_id, :part_id, :username, :body, :created_at)
        """, daftar_komentar)


def hitung(tabel):
    with koneksi() as conn:
        return conn.execute(f"SELECT COUNT(*) FROM {tabel}").fetchone()[0]


# ---------- untuk login (dipakai Anggota 3 nanti) ----------
def buat_user(username, password):
    """Password disimpan dalam bentuk HASH, bukan teks asli."""
    with koneksi() as conn:
        conn.execute("INSERT INTO users (username, password_hash) VALUES (?, ?)",
                     (username, generate_password_hash(password)))


def cek_login(username, password):
    with koneksi() as conn:
        user = conn.execute("SELECT * FROM users WHERE username = ?", (username,)).fetchone()
    return user is not None and check_password_hash(user["password_hash"], password)

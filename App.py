"""
URL Shortener - Flask Backend
Author: [Your Name]
Description: A URL shortening service with SQLite storage and redirect functionality.
"""

import sqlite3
import string
import random
import re
from datetime import datetime
from flask import Flask, request, jsonify, redirect, render_template, abort

app = Flask(__name__)
DB_PATH = "urls.db"


# ─── Database Setup ────────────────────────────────────────────────────────────

def get_db():
    """Open a database connection."""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    """Create tables if they don't exist."""
    with get_db() as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS urls (
                id          INTEGER PRIMARY KEY AUTOINCREMENT,
                short_code  TEXT    UNIQUE NOT NULL,
                original    TEXT    NOT NULL,
                created_at  TEXT    NOT NULL,
                clicks      INTEGER DEFAULT 0
            )
        """)
        conn.commit()


# ─── Helpers ───────────────────────────────────────────────────────────────────

def generate_short_code(length: int = 6) -> str:
    """Generate a random alphanumeric short code."""
    chars = string.ascii_letters + string.digits
    return "".join(random.choices(chars, k=length))


def is_valid_url(url: str) -> bool:
    """Basic URL validation."""
    pattern = re.compile(
        r"^(https?://)"                          # http:// or https://
        r"(([a-zA-Z0-9\-]+\.)+[a-zA-Z]{2,})"   # domain
        r"(:\d+)?"                               # optional port
        r"(/[^\s]*)?$"                           # optional path
    )
    return bool(pattern.match(url))


def get_base_url() -> str:
    """Return the base URL for constructing short links."""
    return request.host_url.rstrip("/")


# ─── Routes ────────────────────────────────────────────────────────────────────

@app.route("/")
def index():
    """Serve the frontend."""
    return render_template("index.html")


@app.route("/api/shorten", methods=["POST"])
def shorten():
    """
    POST /api/shorten
    Body: { "url": "https://example.com/very/long/url" }
    Returns: { "short_code": "abc123", "short_url": "http://localhost:5000/abc123", "original": "...", "created_at": "..." }
    """
    data = request.get_json(silent=True)
    if not data or "url" not in data:
        return jsonify({"error": "Request body must include a 'url' field."}), 400

    original_url = data["url"].strip()

    if not is_valid_url(original_url):
        return jsonify({"error": "Invalid URL. Please include http:// or https://."}), 422

    with get_db() as conn:
        # Check if URL already exists
        row = conn.execute(
            "SELECT short_code FROM urls WHERE original = ?", (original_url,)
        ).fetchone()

        if row:
            short_code = row["short_code"]
        else:
            # Generate a unique code
            for _ in range(10):
                code = generate_short_code()
                exists = conn.execute(
                    "SELECT 1 FROM urls WHERE short_code = ?", (code,)
                ).fetchone()
                if not exists:
                    short_code = code
                    break
            else:
                return jsonify({"error": "Could not generate a unique code. Try again."}), 500

            conn.execute(
                "INSERT INTO urls (short_code, original, created_at) VALUES (?, ?, ?)",
                (short_code, original_url, datetime.utcnow().isoformat())
            )
            conn.commit()

    return jsonify({
        "short_code": short_code,
        "short_url": f"{get_base_url()}/{short_code}",
        "original": original_url,
        "created_at": datetime.utcnow().strftime("%Y-%m-%d %H:%M UTC")
    }), 201


@app.route("/api/stats", methods=["GET"])
def stats():
    """
    GET /api/stats
    Returns top 10 most-clicked URLs.
    """
    with get_db() as conn:
        rows = conn.execute(
            "SELECT short_code, original, clicks, created_at FROM urls ORDER BY clicks DESC LIMIT 10"
        ).fetchall()
    return jsonify([dict(r) for r in rows])


@app.route("/api/info/<short_code>", methods=["GET"])
def info(short_code: str):
    """
    GET /api/info/<short_code>
    Returns metadata for a given short code.
    """
    with get_db() as conn:
        row = conn.execute(
            "SELECT * FROM urls WHERE short_code = ?", (short_code,)
        ).fetchone()

    if not row:
        return jsonify({"error": "Short code not found."}), 404

    return jsonify({
        "short_code": row["short_code"],
        "short_url": f"{get_base_url()}/{row['short_code']}",
        "original": row["original"],
        "clicks": row["clicks"],
        "created_at": row["created_at"]
    })


@app.route("/<short_code>")
def redirect_to_original(short_code: str):
    """
    GET /<short_code>
    Redirects to the original URL and increments the click counter.
    """
    with get_db() as conn:
        row = conn.execute(
            "SELECT original FROM urls WHERE short_code = ?", (short_code,)
        ).fetchone()

        if not row:
            abort(404)

        conn.execute(
            "UPDATE urls SET clicks = clicks + 1 WHERE short_code = ?", (short_code,)
        )
        conn.commit()

    return redirect(row["original"], code=302)


@app.errorhandler(404)
def not_found(e):
    if request.path.startswith("/api/"):
        return jsonify({"error": "Not found."}), 404
    return render_template("404.html"), 404


# ─── Entry Point ───────────────────────────────────────────────────────────────

if __name__ == "__main__":
    init_db()
    print("✅  Database initialised.")
    print("🚀  Starting URL Shortener on http://localhost:5000")
    app.run(debug=True, port=5000)

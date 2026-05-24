# ✂️ Snip — URL Shortener

A full-stack URL shortening service built with **Flask** (Python) and **SQLite**.  
Features a clean, dark-themed frontend with click analytics.

---

## 📸 Features

| Feature | Details |
|---|---|
| **Shorten URLs** | POST to `/api/shorten` — returns a 6-char alphanumeric code |
| **Redirect** | `GET /<short_code>` — 302-redirects to the original URL |
| **Deduplication** | Submitting the same URL returns the same short code |
| **Click Tracking** | Every redirect increments a click counter |
| **Stats API** | `GET /api/stats` — top 10 links by clicks |
| **Info API** | `GET /api/info/<code>` — metadata for a single link |
| **Frontend** | Single-page UI with live result + stats table |

---

## 🗂️ Project Structure

```
url-shortener/
├── app.py               ← Flask backend (routes, DB logic)
├── requirements.txt     ← Python dependencies
├── urls.db              ← SQLite database (auto-created)
└── templates/
    ├── index.html       ← Main frontend (HTML + CSS + JS)
    └── 404.html         ← Custom 404 page
```

---

## 🚀 Getting Started

### 1. Clone & Install

```bash
git clone https://github.com/<your-username>/url-shortener.git
cd url-shortener

python -m venv venv
source venv/bin/activate       # Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### 2. Run the Server

```bash
python app.py
```

Open **http://localhost:5000** in your browser.

---

## 🔌 API Reference

### `POST /api/shorten`
Shorten a long URL.

**Request body:**
```json
{ "url": "https://example.com/very/long/path?with=query" }
```

**Response `201`:**
```json
{
  "short_code": "aB3xYz",
  "short_url":  "http://localhost:5000/aB3xYz",
  "original":   "https://example.com/very/long/path?with=query",
  "created_at": "2024-06-01 12:00 UTC"
}
```

---

### `GET /<short_code>`
Redirects (302) to the original URL and increments click count.

---

### `GET /api/info/<short_code>`
Returns metadata for a short link.

```json
{
  "short_code": "aB3xYz",
  "short_url":  "http://localhost:5000/aB3xYz",
  "original":   "https://example.com/...",
  "clicks":     42,
  "created_at": "2024-06-01T12:00:00"
}
```

---

### `GET /api/stats`
Returns top 10 most-clicked links.

```json
[
  { "short_code": "aB3xYz", "original": "https://...", "clicks": 42, "created_at": "..." },
  ...
]
```

---

## 🛠️ Tech Stack

- **Backend**: Python 3 · Flask 3
- **Database**: SQLite (via `sqlite3` stdlib — zero setup)
- **Frontend**: Vanilla HTML · CSS · JavaScript (no frameworks)
- **Fonts**: Syne · DM Mono (Google Fonts)

---

## 📝 License

MIT — free to use, modify, and distribute.

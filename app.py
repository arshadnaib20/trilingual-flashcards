import sqlite3
from pathlib import Path

from flask import Flask, g, jsonify, render_template, request

BASE_DIR = Path(__file__).resolve().parent
DB_PATH = BASE_DIR / "flashcards.db"

app = Flask(__name__)

LANGS = {"bn": "Bengali", "en": "English", "zh": "Chinese"}


def get_db():
    if "db" not in g:
        g.db = sqlite3.connect(DB_PATH)
        g.db.row_factory = sqlite3.Row
    return g.db


@app.teardown_appcontext
def close_db(_exc):
    db = g.pop("db", None)
    if db is not None:
        db.close()


def init_db():
    db = sqlite3.connect(DB_PATH)
    db.executescript(
        """
        CREATE TABLE IF NOT EXISTS words (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            bn TEXT NOT NULL,
            en TEXT NOT NULL,
            zh TEXT NOT NULL
        );
        CREATE TABLE IF NOT EXISTS attempts (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            word_id INTEGER NOT NULL REFERENCES words(id),
            correct INTEGER NOT NULL,
            created_at TEXT NOT NULL DEFAULT (datetime('now'))
        );
        """
    )
    count = db.execute("SELECT COUNT(*) FROM words").fetchone()[0]
    if count == 0:
        from seed_data import WORDS

        db.executemany("INSERT INTO words (bn, en, zh) VALUES (?, ?, ?)", WORDS)
    db.commit()
    db.close()


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/api/cards")
def cards():
    db = get_db()
    row = db.execute("SELECT * FROM words ORDER BY RANDOM() LIMIT 1").fetchone()
    if row is None:
        return jsonify({"error": "no words yet — add some first"}), 404
    from_lang = request.args.get("from", "en")
    to_lang = request.args.get("to", "bn")
    keys = row.keys()
    prompt = row[from_lang] if from_lang in keys else row["en"]
    answer = row[to_lang] if to_lang in keys else row["bn"]
    return jsonify(
        {
            "id": row["id"],
            "prompt": prompt,
            "answer": answer,
            "from": from_lang,
            "to": to_lang,
            "word": {"bn": row["bn"], "en": row["en"], "zh": row["zh"]},
        }
    )


@app.route("/api/answer", methods=["POST"])
def answer():
    data = request.get_json(force=True)
    word_id = data.get("word_id")
    correct = 1 if data.get("correct") else 0
    db = get_db()
    db.execute(
        "INSERT INTO attempts (word_id, correct) VALUES (?, ?)", (word_id, correct)
    )
    db.commit()
    stats = db.execute(
        "SELECT COUNT(*) AS total, COALESCE(SUM(correct), 0) AS right_count FROM attempts"
    ).fetchone()
    return jsonify({"total": stats["total"], "correct": stats["right_count"]})


@app.route("/api/cards", methods=["POST"])
def add_card():
    data = request.get_json(force=True)
    bn = (data.get("bn") or "").strip()
    en = (data.get("en") or "").strip()
    zh = (data.get("zh") or "").strip()
    if not (bn and en and zh):
        return jsonify({"error": "all three translations are required"}), 400
    db = get_db()
    cur = db.execute("INSERT INTO words (bn, en, zh) VALUES (?, ?, ?)", (bn, en, zh))
    db.commit()
    return jsonify({"id": cur.lastrowid, "bn": bn, "en": en, "zh": zh}), 201


if __name__ == "__main__":
    init_db()
    app.run(host="127.0.0.1", port=5000, debug=False)

from flask import Flask, jsonify, render_template, request
import sqlite3
import os

app = Flask(__name__)

# -----------------------------
# Database path
# On Azure App Service, WEBSITE_SITE_NAME is always set.
# We store the DB in /home/db/ so it survives redeployments.
# Locally it goes in ./db/ next to this file.
# -----------------------------
if os.environ.get("WEBSITE_SITE_NAME"):          # running on Azure
    DATABASE = "/home/db/books.db"
else:                                             # running locally
    DATABASE = os.path.join(
        os.path.dirname(os.path.abspath(__file__)), "db", "books.db"
    )


def get_connection():
    os.makedirs(os.path.dirname(DATABASE), exist_ok=True)
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn


def initialize_database():
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS Books (
        book_id          INTEGER PRIMARY KEY AUTOINCREMENT,
        title            TEXT NOT NULL,
        publication_year TEXT,
        author           TEXT,
        image_url        TEXT
    )
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS Reviews (
        review_id  INTEGER PRIMARY KEY AUTOINCREMENT,
        book_id    INTEGER NOT NULL,
        reviewer   TEXT,
        rating     TEXT,
        comment    TEXT,
        created_at TEXT DEFAULT (datetime('now')),
        FOREIGN KEY (book_id) REFERENCES Books(book_id)
    )
    """)

    conn.commit()
    conn.close()


# -----------------------------
# Routes — Pages
# -----------------------------
@app.route("/")
def index():
    return render_template("index.html")


# -----------------------------
# Routes — Books
# -----------------------------
@app.route("/api/books", methods=["GET"])
def get_all_books():
    try:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("""
            SELECT book_id, title, publication_year, author, image_url
            FROM Books ORDER BY book_id DESC
        """)
        books = [dict(row) for row in cursor.fetchall()]
        conn.close()
        return jsonify({"books": books})
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/api/add", methods=["POST"])
def add_book():
    try:
        data = request.get_json()
        title = data.get("title", "").strip()
        if not title:
            return jsonify({"error": "Title is required"}), 400

        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO Books (title, publication_year, author, image_url)
            VALUES (?, ?, ?, ?)
        """, (title, data.get("publication_year", ""),
              data.get("author", ""), data.get("image_url", "")))
        conn.commit()
        conn.close()
        return jsonify({"message": "Book added successfully"})
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/api/search", methods=["GET"])
def search_books():
    try:
        query = request.args.get("query", "").strip()
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("""
            SELECT book_id, title, publication_year, author, image_url
            FROM Books
            WHERE title LIKE ? OR author LIKE ?
            ORDER BY book_id DESC
        """, (f"%{query}%", f"%{query}%"))
        books = [dict(row) for row in cursor.fetchall()]
        conn.close()
        return jsonify({"books": books})
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/api/delete/<int:book_id>", methods=["DELETE"])
def delete_book(book_id):
    try:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("DELETE FROM Reviews WHERE book_id = ?", (book_id,))
        cursor.execute("DELETE FROM Books   WHERE book_id = ?", (book_id,))
        conn.commit()
        conn.close()
        return jsonify({"message": "Book deleted successfully"})
    except Exception as e:
        return jsonify({"error": str(e)}), 500


# -----------------------------
# Routes — Reviews
# -----------------------------
@app.route("/api/reviews/<int:book_id>", methods=["GET"])
def get_reviews(book_id):
    try:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("""
            SELECT review_id, book_id, reviewer, rating, comment, created_at
            FROM Reviews
            WHERE book_id = ?
            ORDER BY review_id DESC
        """, (book_id,))
        reviews = [dict(row) for row in cursor.fetchall()]
        conn.close()
        return jsonify({"reviews": reviews})
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/api/reviews", methods=["POST"])
def add_review():
    try:
        data = request.get_json()
        book_id = data.get("book_id")
        if not book_id:
            return jsonify({"error": "book_id is required"}), 400

        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO Reviews (book_id, reviewer, rating, comment)
            VALUES (?, ?, ?, ?)
        """, (int(book_id),
              data.get("reviewer", "").strip(),
              str(data.get("rating", "")).strip(),
              data.get("comment", "").strip()))
        conn.commit()
        review_id = cursor.lastrowid
        conn.close()
        return jsonify({"message": "Review added successfully", "review_id": review_id})
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/api/reviews/<int:review_id>", methods=["DELETE"])
def delete_review(review_id):
    try:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("DELETE FROM Reviews WHERE review_id = ?", (review_id,))
        conn.commit()
        conn.close()
        return jsonify({"message": "Review deleted successfully"})
    except Exception as e:
        return jsonify({"error": str(e)}), 500


# -----------------------------
# Entry point
# -----------------------------
initialize_database()

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5001))
    app.run(debug=False, host="0.0.0.0", port=port)

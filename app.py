from flask import Flask, jsonify, render_template, request
import sqlite3
import os
from datetime import datetime
from bson import ObjectId
from pymongo import MongoClient
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)

# -----------------------------
# SQLite setup for BOOKS
# -----------------------------
DATABASE = "db/books.db"


def get_connection():
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn


def initialize_database():
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS Books (
            book_id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            publication_year TEXT,
            author TEXT,
            image_url TEXT
        )
    """)

    conn.commit()
    conn.close()


# -----------------------------
# MongoDB setup for REVIEWS
# -----------------------------
MONGO_URI = os.getenv("MONGO_URI", "mongodb://localhost:27017/")
mongo_client = MongoClient(MONGO_URI)
mongo_db = mongo_client["bookshelf_app"]
reviews_collection = mongo_db["reviews"]


def serialize_review(review):
    return {
        "_id": str(review["_id"]),
        "book_id": review["book_id"],
        "reviewer": review.get("reviewer", ""),
        "rating": review.get("rating", ""),
        "comment": review.get("comment", ""),
        "created_at": review.get("created_at", "")
    }


# -----------------------------
# Routes
# -----------------------------
@app.route("/")
def index():
    return render_template("index.html")


@app.route("/api/books", methods=["GET"])
def get_all_books():
    try:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("""
            SELECT book_id, title, publication_year, author, image_url
            FROM Books
            ORDER BY book_id DESC
        """)
        books = cursor.fetchall()
        conn.close()

        book_list = []
        for book in books:
            book_list.append({
                "book_id": book["book_id"],
                "title": book["title"],
                "publication_year": book["publication_year"],
                "author": book["author"],
                "image_url": book["image_url"]
            })

        return jsonify({"books": book_list})
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/api/add", methods=["POST"])
def add_book():
    try:
        data = request.get_json()

        title = data.get("title")
        publication_year = data.get("publication_year")
        author = data.get("author")
        image_url = data.get("image_url")

        if not title:
            return jsonify({"error": "Title is required"}), 400

        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO Books (title, publication_year, author, image_url)
            VALUES (?, ?, ?, ?)
        """, (title, publication_year, author, image_url))
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
        books = cursor.fetchall()
        conn.close()

        book_list = []
        for book in books:
            book_list.append({
                "book_id": book["book_id"],
                "title": book["title"],
                "publication_year": book["publication_year"],
                "author": book["author"],
                "image_url": book["image_url"]
            })

        return jsonify({"books": book_list})
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/api/delete/<int:book_id>", methods=["DELETE"])
def delete_book(book_id):
    try:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("DELETE FROM Books WHERE book_id = ?", (book_id,))
        conn.commit()
        conn.close()

        # Also delete related MongoDB reviews
        reviews_collection.delete_many({"book_id": book_id})

        return jsonify({"message": "Book deleted successfully"})
    except Exception as e:
        return jsonify({"error": str(e)}), 500


# -----------------------------
# MongoDB Review Routes
# -----------------------------
@app.route("/api/reviews/<int:book_id>", methods=["GET"])
def get_reviews(book_id):
    try:
        reviews = reviews_collection.find({"book_id": book_id}).sort("created_at", -1)
        return jsonify({"reviews": [serialize_review(r) for r in reviews]})
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/api/reviews", methods=["POST"])
def add_review():
    try:
        data = request.get_json()

        book_id = data.get("book_id")
        reviewer = data.get("reviewer", "").strip()
        rating = data.get("rating")
        comment = data.get("comment", "").strip()

        if not book_id:
            return jsonify({"error": "book_id is required"}), 400

        review_doc = {
            "book_id": int(book_id),
            "reviewer": reviewer,
            "rating": str(rating).strip() if rating is not None else "",
            "comment": comment,
            "created_at": datetime.utcnow().isoformat()
        }

        result = reviews_collection.insert_one(review_doc)

        return jsonify({
            "message": "Review added successfully",
            "review_id": str(result.inserted_id)
        })
    except Exception as e:
        print(f"Error in add_review: {e}")
        return jsonify({"error": str(e)}), 500


@app.route("/api/reviews/<review_id>", methods=["DELETE"])
def delete_review(review_id):
    try:
        reviews_collection.delete_one({"_id": ObjectId(review_id)})
        return jsonify({"message": "Review deleted successfully"})
    except Exception as e:
        return jsonify({"error": str(e)}), 500


if __name__ == "__main__":
    initialize_database()
    app.run(debug=True, host="0.0.0.0", port=5001)
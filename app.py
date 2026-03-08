from flask import Flask, jsonify, render_template, request
import sqlite3

app = Flask(__name__)

DATABASE = 'db/books.db'


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


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/api/books', methods=['GET'])
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
                'book_id': book['book_id'],
                'title': book['title'],
                'publication_year': book['publication_year'],
                'author': book['author'],
                'image_url': book['image_url']
            })

        return jsonify({'books': book_list})
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/add', methods=['POST'])
def add_book():
    try:
        data = request.get_json()

        title = data.get('title')
        publication_year = data.get('publication_year')
        author = data.get('author')
        image_url = data.get('image_url')

        if not title:
            return jsonify({'error': 'Title is required'}), 400

        conn = get_connection()
        cursor = conn.cursor()

        cursor.execute("""
            INSERT INTO Books (title, publication_year, author, image_url)
            VALUES (?, ?, ?, ?)
        """, (title, publication_year, author, image_url))

        conn.commit()
        conn.close()

        return jsonify({'message': 'Book added successfully'})
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/search', methods=['GET'])
def search_books():
    try:
        query = request.args.get('query', '').strip()

        conn = get_connection()
        cursor = conn.cursor()

        cursor.execute("""
            SELECT book_id, title, publication_year, author, image_url
            FROM Books
            WHERE title LIKE ? OR author LIKE ?
            ORDER BY book_id DESC
        """, (f'%{query}%', f'%{query}%'))

        books = cursor.fetchall()
        conn.close()

        book_list = []
        for book in books:
            book_list.append({
                'book_id': book['book_id'],
                'title': book['title'],
                'publication_year': book['publication_year'],
                'author': book['author'],
                'image_url': book['image_url']
            })

        return jsonify({'books': book_list})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/delete/<int:book_id>', methods=['DELETE'])
def delete_book(book_id):
    conn = sqlite3.connect('db/books.db')
    cursor = conn.cursor()

    cursor.execute("DELETE FROM Books WHERE book_id = ?", (book_id,))
    conn.commit()
    conn.close()

    return jsonify({"message": "Book deleted successfully"})

if __name__ == '__main__':
    initialize_database()
    app.run(debug=True, host='0.0.0.0', port=5001)
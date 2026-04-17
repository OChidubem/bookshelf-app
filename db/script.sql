-- ==============================================
-- Bookshelf App — Database Schema
-- SQLite
-- ==============================================

-- Books table: stores all book records
CREATE TABLE IF NOT EXISTS Books (
    book_id          INTEGER PRIMARY KEY AUTOINCREMENT,
    title            TEXT NOT NULL,
    publication_year TEXT,
    author           TEXT,
    image_url        TEXT
);

-- Reviews table: stores user reviews linked to books
CREATE TABLE IF NOT EXISTS Reviews (
    review_id  INTEGER PRIMARY KEY AUTOINCREMENT,
    book_id    INTEGER NOT NULL,
    reviewer   TEXT,
    rating     TEXT,
    comment    TEXT,
    created_at TEXT DEFAULT (datetime('now')),
    FOREIGN KEY (book_id) REFERENCES Books(book_id)
);

-- ==============================================
-- Useful queries
-- ==============================================

-- Get all books
-- SELECT * FROM Books ORDER BY book_id DESC;

-- Get all reviews for a specific book
-- SELECT * FROM Reviews WHERE book_id = 1 ORDER BY review_id DESC;

-- Get all reviews with their book title
-- SELECT r.*, b.title FROM Reviews r JOIN Books b ON r.book_id = b.book_id;

-- Delete a book and its reviews
-- DELETE FROM Reviews WHERE book_id = 1;
-- DELETE FROM Books WHERE book_id = 1;

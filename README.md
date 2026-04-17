# My Fancy Book Shelf

A Flask web application for managing books and writing reviews, deployed live on Microsoft Azure App Service.

## Live Demo

**Live URL:** https://bookshelf-app-anbdcgfhbpd3f5cp.centralus-01.azurewebsites.net

## Features

- Add books with title, author, publication year, and cover image URL
- View all books displayed as cards with cover images
- Search books by title or author
- Write reviews for any book (name, star rating 1–5, comment)
- View all reviews for each book
- Delete books and reviews
- Data persists in a SQLite database

## Tech Stack

- **Backend:** Python 3.11, Flask
- **Database:** SQLite (via Python's built-in `sqlite3`)
- **Frontend:** HTML, CSS, Vanilla JavaScript
- **Hosting:** Microsoft Azure App Service (Linux, F1 Free Tier)
- **Deployment:** Kudu ZIP Deploy / GitHub Actions

## Project Structure

```
bookshelf-app/
├── app.py                  # Main Flask application
├── requirements.txt        # Python dependencies
├── startup.txt             # Azure App Service startup command
├── Procfile                # Web server startup command
├── static/
│   ├── script.js           # Frontend JavaScript
│   └── styles.css          # Stylesheet
├── templates/
│   └── index.html          # Main HTML page
├── db/
│   ├── books.db            # SQLite database (auto-created)
│   ├── script.sql          # Database schema reference
│   ├── how_to.sql          # Useful SQL queries
│   └── tests/
│       └── test_books.py   # Integration tests
└── .github/
    └── workflows/
        └── main_bookshelf-app.yml  # Azure GitHub Actions deployment
```

## Database Schema

```sql
-- Books table
CREATE TABLE Books (
    book_id          INTEGER PRIMARY KEY AUTOINCREMENT,
    title            TEXT NOT NULL,
    publication_year TEXT,
    author           TEXT,
    image_url        TEXT
);

-- Reviews table
CREATE TABLE Reviews (
    review_id  INTEGER PRIMARY KEY AUTOINCREMENT,
    book_id    INTEGER NOT NULL,
    reviewer   TEXT,
    rating     TEXT,
    comment    TEXT,
    created_at TEXT DEFAULT (datetime('now')),
    FOREIGN KEY (book_id) REFERENCES Books(book_id)
);
```

## Local Setup

**Requirements:** Python 3.11+

```bash
# 1. Clone the repository
git clone https://github.com/OChidubem/bookshelf-app.git
cd bookshelf-app

# 2. Create and activate a virtual environment
python3 -m venv venv
source venv/bin/activate        # macOS/Linux
venv\Scripts\activate           # Windows

# 3. Install dependencies
pip install -r requirements.txt

# 4. Run the app
python app.py
```

Visit **http://127.0.0.1:5001** in your browser.

The SQLite database (`db/books.db`) is created automatically on first run.

## Running Tests

Make sure the app is running locally first, then:

```bash
python db/tests/test_books.py
```

## API Endpoints

| Method | Endpoint | Description |
|---|---|---|
| GET | `/api/books` | Get all books |
| POST | `/api/add` | Add a new book |
| GET | `/api/search?query=` | Search books by title or author |
| DELETE | `/api/delete/<book_id>` | Delete a book and its reviews |
| GET | `/api/reviews/<book_id>` | Get all reviews for a book |
| POST | `/api/reviews` | Add a review |
| DELETE | `/api/reviews/<review_id>` | Delete a review |

## Azure Deployment

This app is deployed on **Microsoft Azure App Service** using the free F1 tier.

**Startup command:**
```
gunicorn --bind=0.0.0.0 --timeout 600 app:app
```

On Azure, the database is stored at `/home/db/books.db` for persistence across deployments. Locally it uses `./db/books.db`.

To redeploy, push to the `main` branch — GitHub Actions (`main_bookshelf-app.yml`) automatically builds and deploys to Azure.

## Author

Chidubem Okoye

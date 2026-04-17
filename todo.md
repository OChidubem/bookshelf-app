# Bookshelf App — Dev Notes

## Local Setup

```bash
python3 -m venv .venv
source .venv/bin/activate      # macOS/Linux
.venv\Scripts\activate         # Windows

pip install -r requirements.txt
python app.py
```

Open http://127.0.0.1:5001

## Database

SQLite — auto-created at `db/books.db` on first run.
On Azure the DB lives at `/home/db/books.db` (persists across deploys).

To reset the local DB:
```bash
rm db/books.db
python app.py   # recreates it
```

## Running Tests

Start the app first, then:
```bash
python db/tests/test_books.py
```

## Azure Deployment (Kudu ZIP Deploy)

1. Zip the project (exclude `.venv/`, `__pycache__/`, `*.db`):
```bash
   zip -r deploy.zip . --exclude ".venv/*" --exclude "__pycache__/*" --exclude "*.db"
```
2. Go to Azure Portal → App Service → Advanced Tools (Kudu) → Debug Console → CMD
3. Drag `deploy.zip` onto `/site/wwwroot`
4. Kudu auto-extracts and restarts the app

## Startup Command (set in Azure Portal → Configuration → Stack settings)

```
gunicorn --bind=0.0.0.0 --timeout 600 app:app
```
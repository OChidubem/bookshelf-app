# Flask SQLite Books Reviews Web Example

This is a simple Flask web application for managing book reviews using a SQLite database.

## Features
- Add books with title, publication year, author, and image URL.
- Search for books by title or author.
- View a list of all added books.

## Project Structure
- `app.py`: The main Flask application.
- `db/`: Contains the SQLite database and SQL scripts.
- `static/`: Contains static files like CSS and JavaScript.
- `templates/`: Contains HTML templates.
- `todo.md`: Project documentation and setup instructions.

## Getting Started

### Prerequisites
- Python 3
- Flask

### Installation
1. Clone the repository.
2. Create a virtual environment:
   ```bash
   python3 -m venv venv
   ```
3. Activate the virtual environment:
   - On macOS/Linux: `source venv/bin/activate`
   - On Windows: `venv\Scripts\activate`
4. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

### Running the Application
1. Initialize the database (if not already done):
   The application will automatically create `db/books.db` and the required tables when run.
2. Start the Flask server:
   ```bash
   python app.py
   ```
3. Open your browser and navigate to `http://127.0.0.1:5001`.

## Testing
Run the integration tests using:
```bash
python db/tests/test_books.py
```
(Ensure the server is running before executing tests.)

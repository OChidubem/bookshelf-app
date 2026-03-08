import requests

BASE_URL = "http://127.0.0.1:5001"


def test_add_book():
    response = requests.post(f"{BASE_URL}/api/add", json={
        "title": "Integration Test Book",
        "publication_year": "2025",
        "author": "Test Author",
        "image_url": "https://via.placeholder.com/150x220?text=Test+Book"
    })

    assert response.status_code == 200
    assert response.json()["message"] == "Book added successfully"


def test_add_book_saved_fields():
    requests.post(f"{BASE_URL}/api/add", json={
        "title": "Searchable Test Book",
        "publication_year": "2025",
        "author": "Stored Author",
        "image_url": "https://via.placeholder.com/150x220?text=Stored+Book"
    })

    response = requests.get(f"{BASE_URL}/api/books")
    assert response.status_code == 200

    books = response.json()["books"]

    found = any(
        book["title"] == "Searchable Test Book" and
        book["author"] == "Stored Author" and
        book["image_url"] == "https://via.placeholder.com/150x220?text=Stored+Book"
        for book in books
    )

    assert found


def test_search_by_title():
    response = requests.get(f"{BASE_URL}/api/search?query=Clean")
    assert response.status_code == 200
    assert isinstance(response.json()["books"], list)


def test_search_by_author():
    response = requests.get(f"{BASE_URL}/api/search?query=Martin")
    assert response.status_code == 200
    assert isinstance(response.json()["books"], list)


def test_search_nonexistent():
    response = requests.get(f"{BASE_URL}/api/search?query=ZZZ_NO_SUCH_BOOK_123")
    assert response.status_code == 200
    assert response.json()["books"] == []
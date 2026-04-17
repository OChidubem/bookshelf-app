import requests
 
BASE_URL = "http://127.0.0.1:5001"
 
 
# -------------------------
# Book Tests
# -------------------------
 
def test_add_book():
    response = requests.post(f"{BASE_URL}/api/add", json={
        "title": "Integration Test Book",
        "publication_year": "2025",
        "author": "Test Author",
        "image_url": "https://placehold.co/150x220?text=Test+Book"
    })
    assert response.status_code == 200
    assert response.json()["message"] == "Book added successfully"
    print("  test_add_book: PASSED")
 
 
def test_add_book_missing_title():
    response = requests.post(f"{BASE_URL}/api/add", json={
        "publication_year": "2025",
        "author": "No Title Author"
    })
    assert response.status_code == 400
    assert "error" in response.json()
    print("  test_add_book_missing_title: PASSED")
 
 
def test_add_book_saved_fields():
    requests.post(f"{BASE_URL}/api/add", json={
        "title": "Searchable Test Book",
        "publication_year": "2025",
        "author": "Stored Author",
        "image_url": "https://placehold.co/150x220?text=Stored+Book"
    })
    response = requests.get(f"{BASE_URL}/api/books")
    assert response.status_code == 200
    books = response.json()["books"]
    found = any(
        book["title"] == "Searchable Test Book" and
        book["author"] == "Stored Author"
        for book in books
    )
    assert found
    print("  test_add_book_saved_fields: PASSED")
 
 
def test_get_all_books():
    response = requests.get(f"{BASE_URL}/api/books")
    assert response.status_code == 200
    assert "books" in response.json()
    assert isinstance(response.json()["books"], list)
    print("  test_get_all_books: PASSED")
 
 
def test_search_by_title():
    response = requests.get(f"{BASE_URL}/api/search?query=Test")
    assert response.status_code == 200
    assert isinstance(response.json()["books"], list)
    print("  test_search_by_title: PASSED")
 
 
def test_search_by_author():
    response = requests.get(f"{BASE_URL}/api/search?query=Stored Author")
    assert response.status_code == 200
    results = response.json()["books"]
    assert any(book["author"] == "Stored Author" for book in results)
    print("  test_search_by_author: PASSED")
 
 
def test_search_nonexistent():
    response = requests.get(f"{BASE_URL}/api/search?query=ZZZ_NO_SUCH_BOOK_XYZ_123")
    assert response.status_code == 200
    assert response.json()["books"] == []
    print("  test_search_nonexistent: PASSED")
 
 
# -------------------------
# Review Tests
# -------------------------
 
def get_first_book_id():
    response = requests.get(f"{BASE_URL}/api/books")
    books = response.json()["books"]
    assert len(books) > 0, "No books found — add a book first"
    return books[0]["book_id"]
 
 
def test_add_review():
    book_id = get_first_book_id()
    response = requests.post(f"{BASE_URL}/api/reviews", json={
        "book_id": book_id,
        "reviewer": "Test Reviewer",
        "rating": "5",
        "comment": "Amazing book, highly recommend!"
    })
    assert response.status_code == 200
    data = response.json()
    assert data["message"] == "Review added successfully"
    assert "review_id" in data
    print("  test_add_review: PASSED")
    return data["review_id"]
 
 
def test_get_reviews():
    book_id = get_first_book_id()
    # Add a review first
    requests.post(f"{BASE_URL}/api/reviews", json={
        "book_id": book_id,
        "reviewer": "Reader",
        "rating": "4",
        "comment": "Great read."
    })
    response = requests.get(f"{BASE_URL}/api/reviews/{book_id}")
    assert response.status_code == 200
    reviews = response.json()["reviews"]
    assert isinstance(reviews, list)
    assert len(reviews) > 0
    assert reviews[0]["book_id"] == book_id
    print("  test_get_reviews: PASSED")
 
 
def test_review_fields_saved():
    book_id = get_first_book_id()
    requests.post(f"{BASE_URL}/api/reviews", json={
        "book_id": book_id,
        "reviewer": "Field Tester",
        "rating": "3",
        "comment": "Decent book overall."
    })
    response = requests.get(f"{BASE_URL}/api/reviews/{book_id}")
    reviews = response.json()["reviews"]
    found = any(
        r["reviewer"] == "Field Tester" and
        r["rating"] == "3" and
        r["comment"] == "Decent book overall."
        for r in reviews
    )
    assert found
    print("  test_review_fields_saved: PASSED")
 
 
def test_add_review_missing_book_id():
    response = requests.post(f"{BASE_URL}/api/reviews", json={
        "reviewer": "No Book",
        "rating": "5",
        "comment": "This should fail"
    })
    assert response.status_code == 400
    assert "error" in response.json()
    print("  test_add_review_missing_book_id: PASSED")
 
 
def test_delete_review():
    book_id = get_first_book_id()
    add_response = requests.post(f"{BASE_URL}/api/reviews", json={
        "book_id": book_id,
        "reviewer": "To Be Deleted",
        "rating": "1",
        "comment": "Will be removed."
    })
    review_id = add_response.json()["review_id"]
 
    delete_response = requests.delete(f"{BASE_URL}/api/reviews/{review_id}")
    assert delete_response.status_code == 200
    assert delete_response.json()["message"] == "Review deleted successfully"
 
    # Confirm it's gone
    reviews = requests.get(f"{BASE_URL}/api/reviews/{book_id}").json()["reviews"]
    assert not any(r["review_id"] == review_id for r in reviews)
    print("  test_delete_review: PASSED")
 
 
def test_delete_book_also_deletes_reviews():
    # Add a book
    requests.post(f"{BASE_URL}/api/add", json={
        "title": "Book To Delete",
        "author": "Temp Author",
        "publication_year": "2000"
    })
    books = requests.get(f"{BASE_URL}/api/books").json()["books"]
    book_id = next(b["book_id"] for b in books if b["title"] == "Book To Delete")
 
    # Add a review
    requests.post(f"{BASE_URL}/api/reviews", json={
        "book_id": book_id,
        "reviewer": "Someone",
        "rating": "2",
        "comment": "Temporary review."
    })
 
    # Delete the book
    requests.delete(f"{BASE_URL}/api/delete/{book_id}")
 
    # Reviews should also be gone
    reviews = requests.get(f"{BASE_URL}/api/reviews/{book_id}").json()["reviews"]
    assert reviews == []
    print("  test_delete_book_also_deletes_reviews: PASSED")
 
 
# -------------------------
# Run all tests
# -------------------------
if __name__ == "__main__":
    print("\n--- Book Tests ---")
    test_add_book()
    test_add_book_missing_title()
    test_add_book_saved_fields()
    test_get_all_books()
    test_search_by_title()
    test_search_by_author()
    test_search_nonexistent()
 
    print("\n--- Review Tests ---")
    test_add_review()
    test_get_reviews()
    test_review_fields_saved()
    test_add_review_missing_book_id()
    test_delete_review()
    test_delete_book_also_deletes_reviews()
 
    print("\nALL TESTS PASSED")
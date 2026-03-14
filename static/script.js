function addBook() {
  const title = document.getElementById("bookTitle").value.trim();
  const author = document.getElementById("authorName").value.trim();
  const year = document.getElementById("publicationYear").value.trim();
  const image = document.getElementById("imageUrl").value.trim();

  fetch("/api/add", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({
      title: title,
      publication_year: year,
      author: author,
      image_url: image
    })
  })
    .then(response => response.json())
    .then(data => {
      if (data.error) {
        alert(data.error);
        return;
      }

      document.getElementById("bookTitle").value = "";
      document.getElementById("authorName").value = "";
      document.getElementById("publicationYear").value = "";
      document.getElementById("imageUrl").value = "";
      showAllBooks();
    })
    .catch(error => console.error("Error adding book:", error));
}

function showAllBooks() {
  fetch("/api/books")
    .then(response => response.json())
    .then(data => renderBooks(data.books))
    .catch(error => console.error("Error fetching books:", error));
}

function searchBooks() {
  const query = document.getElementById("searchText").value.trim();

  fetch("/api/search?query=" + encodeURIComponent(query))
    .then(response => response.json())
    .then(data => renderBooks(data.books))
    .catch(error => console.error("Error searching books:", error));
}

function deleteBook(bookId) {
  fetch(`/api/delete/${bookId}`, { method: "DELETE" })
    .then(response => response.json())
    .then(() => showAllBooks())
    .catch(error => console.error("Error deleting book:", error));
}

function addReview(bookId) {
  const reviewerInput = document.getElementById(`reviewer-${bookId}`);
  const ratingInput = document.getElementById(`rating-${bookId}`);
  const commentInput = document.getElementById(`comment-${bookId}`);

  const reviewer = reviewerInput.value.trim();
  const rating = ratingInput.value.trim();
  const comment = commentInput.value.trim();

  fetch("/api/reviews", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({
      book_id: bookId,
      reviewer,
      rating,
      comment
    })
  })
    .then(response => {
      if (!response.ok) {
        return response.json().then(err => { throw err; });
      }
      return response.json();
    })
    .then(data => {
      reviewerInput.value = "";
      ratingInput.value = "";
      commentInput.value = "";
      loadReviews(bookId);
    })
    .catch(error => {
      console.error("Error adding review:", error);
      alert("Failed to add review: " + (error.error || error.message || error));
    });
}

function deleteReview(reviewId, bookId) {
  fetch(`/api/reviews/${reviewId}`, { method: "DELETE" })
    .then(response => response.json())
    .then(() => loadReviews(bookId))
    .catch(error => console.error("Error deleting review:", error));
}

function loadReviews(bookId) {
  fetch(`/api/reviews/${bookId}`)
    .then(response => response.json())
    .then(data => {
      const container = document.getElementById(`reviews-${bookId}`);
      if (!container) return;

      const reviews = data.reviews || [];

      if (reviews.length === 0) {
        container.innerHTML = `<p class="review-empty">No reviews yet.</p>`;
        return;
      }

      container.innerHTML = reviews.map(review => `
        <div class="review-item">
          <p><strong>${review.reviewer || "Anonymous"}</strong> ${review.rating ? `- ${review.rating}/5` : ""}</p>
          <p>${review.comment || ""}</p>
          <button class="delete-review-btn" onclick="deleteReview('${review._id}', ${bookId})">Delete Review</button>
        </div>
      `).join("");
    })
    .catch(error => console.error("Error loading reviews:", error));
}

function renderBooks(books) {
  const shelf = document.getElementById("bookshelf");
  shelf.innerHTML = "";

  if (!books || books.length === 0) {
    shelf.innerHTML = `<div class="empty-message">No books found.</div>`;
    return;
  }

  books.forEach(book => {
    const card = document.createElement("div");
    card.className = "book-card";

    const safeImage =
      book.image_url && book.image_url.trim() !== ""
        ? book.image_url
        : "https://via.placeholder.com/150x220?text=No+Cover";

    const safeTitle =
      book.title && book.title.trim() !== ""
        ? book.title
        : "Untitled Book";

    const safeAuthor =
      book.author && book.author.trim() !== ""
        ? book.author
        : "Unknown Author";

    const safeYear =
      book.publication_year && String(book.publication_year).trim() !== ""
        ? book.publication_year
        : "Year not provided";

    card.innerHTML = `
      <img src="${safeImage}" alt="${safeTitle}">
      <h3>${safeTitle}</h3>
      <p class="author">${safeAuthor}</p>
      <p class="year">${safeYear}</p>
      <button onclick="deleteBook(${book.book_id})">Delete</button>

      <div class="review-section">
        <h4>Reviews</h4>
        <input id="reviewer-${book.book_id}" type="text" placeholder="Your name">
        <input id="rating-${book.book_id}" type="number" min="1" max="5" placeholder="Rating (1-5)">
        <input id="comment-${book.book_id}" type="text" placeholder="Write a review">
        <button onclick="addReview(${book.book_id})">Add Review</button>
        <div id="reviews-${book.book_id}" class="reviews-list"></div>
      </div>
    `;

    shelf.appendChild(card);
    loadReviews(book.book_id);
  });
}

window.onload = showAllBooks;
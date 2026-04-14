// -------------------------
// Book functions
// -------------------------
function addBook() {
  const title = document.getElementById("bookTitle").value.trim();
  const author = document.getElementById("authorName").value.trim();
  const year = document.getElementById("publicationYear").value.trim();
  const image = document.getElementById("imageUrl").value.trim();

  if (!title) { alert("Please enter a book title."); return; }

  fetch("/api/add", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ title, publication_year: year, author, image_url: image })
  })
    .then(r => r.json())
    .then(data => {
      if (data.error) { alert(data.error); return; }
      ["bookTitle","authorName","publicationYear","imageUrl"]
        .forEach(id => document.getElementById(id).value = "");
      showAllBooks();
    })
    .catch(err => console.error("Error adding book:", err));
}

function showAllBooks() {
  fetch("/api/books")
    .then(r => r.json())
    .then(data => renderBooks(data.books))
    .catch(err => console.error("Error fetching books:", err));
}

function searchBooks() {
  const query = document.getElementById("searchText").value.trim();
  fetch("/api/search?query=" + encodeURIComponent(query))
    .then(r => r.json())
    .then(data => renderBooks(data.books))
    .catch(err => console.error("Error searching books:", err));
}

function deleteBook(bookId) {
  if (!confirm("Delete this book and all its reviews?")) return;
  fetch(`/api/delete/${bookId}`, { method: "DELETE" })
    .then(r => r.json())
    .then(() => showAllBooks())
    .catch(err => console.error("Error deleting book:", err));
}

// -------------------------
// Review functions
// -------------------------
function addReview(bookId) {
  const reviewerInput = document.getElementById(`reviewer-${bookId}`);
  const ratingInput   = document.getElementById(`rating-${bookId}`);
  const commentInput  = document.getElementById(`comment-${bookId}`);

  const reviewer = reviewerInput.value.trim();
  const rating   = ratingInput.value.trim();
  const comment  = commentInput.value.trim();

  if (!comment && !rating) {
    alert("Please enter a rating or comment before submitting.");
    return;
  }

  fetch("/api/reviews", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ book_id: bookId, reviewer, rating, comment })
  })
    .then(r => { if (!r.ok) return r.json().then(e => { throw e; }); return r.json(); })
    .then(() => {
      reviewerInput.value = ratingInput.value = commentInput.value = "";
      loadReviews(bookId);
    })
    .catch(err => alert("Failed to add review: " + (err.error || err.message || err)));
}

function deleteReview(reviewId, bookId) {
  fetch(`/api/reviews/${reviewId}`, { method: "DELETE" })
    .then(r => r.json())
    .then(() => loadReviews(bookId))
    .catch(err => console.error("Error deleting review:", err));
}

function loadReviews(bookId) {
  fetch(`/api/reviews/${bookId}`)
    .then(r => r.json())
    .then(data => {
      const container = document.getElementById(`reviews-${bookId}`);
      if (!container) return;
      const reviews = data.reviews || [];

      if (reviews.length === 0) {
        container.innerHTML = `<p class="review-empty">No reviews yet. Be the first!</p>`;
        return;
      }

      container.innerHTML = reviews.map(review => {
        const stars = review.rating
          ? "★".repeat(parseInt(review.rating)) + "☆".repeat(5 - parseInt(review.rating))
          : "";
        return `
          <div class="review-item">
            <div class="review-header">
              <strong>${review.reviewer || "Anonymous"}</strong>
              ${stars ? `<span class="review-stars">${stars}</span>` : ""}
            </div>
            <p class="review-comment">${review.comment || ""}</p>
            <small class="review-date">${(review.created_at || "").slice(0, 10)}</small>
            <button class="delete-review-btn" onclick="deleteReview(${review.review_id}, ${bookId})">✕ Remove</button>
          </div>`;
      }).join("");
    })
    .catch(err => console.error("Error loading reviews:", err));
}

// -------------------------
// Render book cards
// -------------------------
function renderBooks(books) {
  const shelf = document.getElementById("bookshelf");
  shelf.innerHTML = "";

  if (!books || books.length === 0) {
    shelf.innerHTML = `<div class="empty-message">No books found. Add one above!</div>`;
    return;
  }

  books.forEach(book => {
    const card = document.createElement("div");
    card.className = "book-card";

    const safeImage = book.image_url && book.image_url.trim()
      ? book.image_url
      : "https://placehold.co/150x220?text=No+Cover";

    card.innerHTML = `
      <img src="${safeImage}" alt="${book.title || 'Book'}"
           onerror="this.src='https://placehold.co/150x220?text=No+Cover'">
      <h3>${book.title || "Untitled"}</h3>
      <p class="author">${book.author || "Unknown Author"}</p>
      <p class="year">${book.publication_year || "Year unknown"}</p>
      <button class="delete-btn" onclick="deleteBook(${book.book_id})">Delete Book</button>
 
      <div class="review-section">
        <h4>Reviews</h4>
        <div class="review-form">
          <input id="reviewer-${book.book_id}" type="text"   placeholder="Your name (optional)">
          <input id="rating-${book.book_id}"   type="number" placeholder="Rating 1–5" min="1" max="5">
          <input id="comment-${book.book_id}"  type="text"   placeholder="Write your review...">
          <button class="add-review-btn" onclick="addReview(${book.book_id})">Submit Review</button>
        </div>
        <div id="reviews-${book.book_id}" class="reviews-list"></div>
      </div>
    `;

    shelf.appendChild(card);
    loadReviews(book.book_id);
  });
}

window.onload = showAllBooks;
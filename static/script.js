function addBook() {
    const title = document.getElementById("bookTitle").value.trim();
    const author = document.getElementById("authorName").value.trim();
    const year = document.getElementById("publicationYear").value.trim();
    const image = document.getElementById("imageUrl").value.trim();

    fetch("/api/add", {
        method: "POST",
        headers: {
            "Content-Type": "application/json"
        },
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
    .catch(error => {
        console.error("Error adding book:", error);
    });
}

function showAllBooks() {
    fetch("/api/books")
        .then(response => response.json())
        .then(data => {
            renderBooks(data.books);
        })
        .catch(error => {
            console.error("Error fetching books:", error);
        });
}

function searchBooks() {
    const query = document.getElementById("searchText").value.trim();

    fetch("/api/search?query=" + encodeURIComponent(query))
        .then(response => response.json())
        .then(data => {
            renderBooks(data.books);
        })
        .catch(error => {
            console.error("Error searching books:", error);
        });
}

function renderBooks(books) {
    const shelf = document.getElementById("bookshelf");
    shelf.innerHTML = "";

    if (!books || books.length === 0) {
        shelf.innerHTML = `
            <div class="empty-message">
                No books found.
            </div>
        `;
        return;
    }

    books.forEach(book => {
        const card = document.createElement("div");
        card.className = "book-card";

        const safeImage = (book.image_url && book.image_url.trim() !== "")
            ? book.image_url
            : "https://via.placeholder.com/150x220?text=No+Cover";

        const safeTitle = (book.title && book.title.trim() !== "")
            ? book.title
            : "Untitled Book";

        const safeAuthor = (book.author && book.author.trim() !== "")
            ? book.author
            : "Unknown Author";

        const safeYear = (book.publication_year && String(book.publication_year).trim() !== "")
            ? book.publication_year
            : "Year not provided";

        card.innerHTML = `
            <img src="${safeImage}" alt="${safeTitle}" onerror="this.src='https://via.placeholder.com/150x220?text=No+Cover'">
            <h3>${safeTitle}</h3>
            <p class="author">${safeAuthor}</p>
            <p class="year">${safeYear}</p>
        `;

        shelf.appendChild(card);
    });
}

window.onload = showAllBooks;
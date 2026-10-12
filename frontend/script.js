
const API_URL = "http://127.0.0.1:8000";

const booksContainer = document.getElementById("books");
const countElement = document.getElementById("count");
const searchForm = document.getElementById("search-form");
const searchInput = document.getElementById("search-input");
const statusElement = document.getElementById("status");

let allBooks = [];

async function loadBooks() {
    try {
        const response = await fetch(`${API_URL}/books/`);

        if (!response.ok) {
            throw new Error(`HTTP ${response.status}`);
        }

        const data = await response.json();
        allBooks = Array.isArray(data) ? data : (data.books || []);

        countElement.textContent = `Total Books: ${allBooks.length}`;
        renderBooks(allBooks);
    } catch (error) {
        console.error(error);
        countElement.textContent = "Catalogue unavailable";
        statusElement.textContent =
            "Please start the backend and check the browser console.";

        booksContainer.innerHTML =
            '<p class="empty">Could not load books from the server.</p>';
    }
}

function renderBooks(books) {
    if (books.length === 0) {
        booksContainer.innerHTML =
            '<p class="empty">No books found.</p>';
        return;
    }

    booksContainer.innerHTML = books.map(book => {
        const authors = Array.isArray(book.authors)
            ? book.authors.map(author =>
                typeof author === "string" ? author : author.name || ""
              ).filter(Boolean).join(", ")
            : (book.author || "Author information unavailable");

        return `
            <article class="card">
                <div class="cover">▤</div>
                <h3>${escapeHTML(book.title || "Untitled")}</h3>
                <p class="author">${escapeHTML(authors)}</p>
                <button class="btn outline" type="button">
                    Book ID: ${escapeHTML(book.book_id ?? "—")}
                </button>
            </article>
        `;
    }).join("");
}

function escapeHTML(value) {
    return String(value).replace(/[&<>"']/g, character => ({
        "&": "&amp;",
        "<": "&lt;",
        ">": "&gt;",
        '"': "&quot;",
        "'": "&#39;"
    })[character]);
}

searchForm.addEventListener("submit", event => {
    event.preventDefault();

    const query = searchInput.value.trim().toLowerCase();

    const filteredBooks = allBooks.filter(book => {
        const title = String(book.title || "").toLowerCase();
        const author = String(book.author || "").toLowerCase();

        const authors = Array.isArray(book.authors)
            ? book.authors.map(a =>
                typeof a === "string" ? a : a.name || ""
              ).join(" ").toLowerCase()
            : "";

        return title.includes(query)
            || author.includes(query)
            || authors.includes(query);
    });

    renderBooks(filteredBooks);
    countElement.textContent = `Showing ${filteredBooks.length} books`;
    statusElement.textContent = query
        ? `Search results for "${searchInput.value.trim()}"`
        : "Showing all books.";
});

loadBooks();

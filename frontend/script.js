// API Configuration
const API_BASE_URL = "http://localhost:8000"

// Global state
let books = []
let currentBookId = null
let currentRating = 0

// Initialize the application
document.addEventListener("DOMContentLoaded", () => {
  initializeApp()
  setupEventListeners()
})

async function initializeApp() {
  await checkApiStatus()
  await loadBooks()
  updateStats()
}

function setupEventListeners() {
  // Search functionality
  document.getElementById("searchInput").addEventListener("input", handleSearch)

  // Add book form
  document.getElementById("addBookForm").addEventListener("submit", handleAddBook)

  // Add review form
  document.getElementById("reviewForm").addEventListener("submit", handleAddReview)

  // Rating stars
  setupRatingStars()

  // Close modals on outside click
  document.addEventListener("click", handleOutsideClick)
}

// API Status Check
async function checkApiStatus() {
  try {
    const response = await fetch(`${API_BASE_URL}/health`)
    const data = await response.json()

    const statusElement = document.getElementById("apiStatus")
    const cacheStatusElement = document.getElementById("cacheStatus")

    if (response.ok) {
      statusElement.classList.remove("offline")
      statusElement.innerHTML = '<i class="fas fa-circle"></i><span>API Online</span>'
      cacheStatusElement.textContent = data.redis === "connected" ? "Connected" : "Offline"
    } else {
      throw new Error("API offline")
    }
  } catch (error) {
    const statusElement = document.getElementById("apiStatus")
    statusElement.classList.add("offline")
    statusElement.innerHTML = '<i class="fas fa-circle"></i><span>API Offline</span>'
    document.getElementById("cacheStatus").textContent = "Unknown"
    showToast("API connection failed", "error")
  }
}

// Load Books
async function loadBooks() {
  showLoading(true)

  try {
    const response = await fetch(`${API_BASE_URL}/books`)

    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`)
    }

    books = await response.json()
    renderBooks(books)
    updateStats()

    if (books.length === 0) {
      showEmptyState()
    }
  } catch (error) {
    console.error("Error loading books:", error)
    showToast("Failed to load books", "error")
    showEmptyState()
  } finally {
    showLoading(false)
  }
}

// Render Books
function renderBooks(booksToRender) {
  const container = document.getElementById("booksContainer")
  const emptyState = document.getElementById("emptyState")

  if (booksToRender.length === 0) {
    container.innerHTML = ""
    emptyState.style.display = "block"
    return
  }

  emptyState.style.display = "none"

  container.innerHTML = booksToRender
    .map(
      (book) => `
        <div class="book-card" onclick="openBookDetails(${book.id})">
            <div class="book-header">
                <div>
                    <h3 class="book-title">${escapeHtml(book.title)}</h3>
                    <p class="book-author">by ${escapeHtml(book.author)}</p>
                </div>
                <div class="book-rating">
                    <i class="fas fa-star"></i>
                    <span>4.5</span>
                </div>
            </div>
            
            <div class="book-meta">
                ${book.publication_year ? `<span><i class="fas fa-calendar"></i> ${book.publication_year}</span>` : ""}
                ${book.isbn ? `<span><i class="fas fa-barcode"></i> ${book.isbn}</span>` : ""}
            </div>
            
            ${book.description ? `<p class="book-description">${escapeHtml(book.description)}</p>` : ""}
            
            <div class="book-actions">
                <div class="review-count">
                    <i class="fas fa-comment"></i>
                    <span>0 reviews</span>
                </div>
                <button class="btn btn-primary btn-sm" onclick="event.stopPropagation(); openBookDetails(${book.id})">
                    View Details
                </button>
            </div>
        </div>
    `,
    )
    .join("")
}

// Search functionality
function handleSearch(event) {
  const searchTerm = event.target.value.toLowerCase()

  if (searchTerm === "") {
    renderBooks(books)
    return
  }

  const filteredBooks = books.filter(
    (book) => book.title.toLowerCase().includes(searchTerm) || book.author.toLowerCase().includes(searchTerm),
  )

  renderBooks(filteredBooks)
}

// Add Book Modal
function openAddBookModal() {
  document.getElementById("addBookModal").classList.add("active")
  document.getElementById("bookTitle").focus()
}

function closeAddBookModal() {
  document.getElementById("addBookModal").classList.remove("active")
  document.getElementById("addBookForm").reset()
}

// Handle Add Book
async function handleAddBook(event) {
  event.preventDefault()

  const formData = {
    title: document.getElementById("bookTitle").value,
    author: document.getElementById("bookAuthor").value,
    isbn: document.getElementById("bookISBN").value || null,
    publication_year: Number.parseInt(document.getElementById("bookYear").value) || null,
    description: document.getElementById("bookDescription").value || null,
  }

  try {
    const response = await fetch(`${API_BASE_URL}/books`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify(formData),
    })

    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`)
    }

    const newBook = await response.json()
    books.unshift(newBook)
    renderBooks(books)
    updateStats()
    closeAddBookModal()
    showToast("Book added successfully!", "success")
  } catch (error) {
    console.error("Error adding book:", error)
    showToast("Failed to add book", "error")
  }
}

// Book Details Modal
async function openBookDetails(bookId) {
  currentBookId = bookId
  const book = books.find((b) => b.id === bookId)

  if (!book) return

  // Update modal title and book info
  document.getElementById("bookDetailsTitle").textContent = book.title
  document.getElementById("bookMeta").innerHTML = `
        <div class="book-info-grid">
            <h3>${escapeHtml(book.title)}</h3>
            <p class="author">by ${escapeHtml(book.author)}</p>
            ${book.description ? `<p class="description">${escapeHtml(book.description)}</p>` : ""}
            <div class="meta-info">
                ${book.publication_year ? `<span><strong>Year:</strong> ${book.publication_year}</span>` : ""}
                ${book.isbn ? `<span><strong>ISBN:</strong> ${book.isbn}</span>` : ""}
                <span><strong>Added:</strong> ${new Date(book.created_at).toLocaleDateString()}</span>
            </div>
        </div>
    `

  // Load reviews
  await loadReviews(bookId)

  document.getElementById("bookDetailsModal").classList.add("active")
}

function closeBookDetailsModal() {
  document.getElementById("bookDetailsModal").classList.remove("active")
  closeAddReviewForm()
  currentBookId = null
}

// Load Reviews
async function loadReviews(bookId) {
  try {
    const response = await fetch(`${API_BASE_URL}/books/${bookId}/reviews`)

    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`)
    }

    const reviews = await response.json()
    renderReviews(reviews)
  } catch (error) {
    console.error("Error loading reviews:", error)
    document.getElementById("reviewsList").innerHTML = "<p>Failed to load reviews</p>"
  }
}

// Render Reviews
function renderReviews(reviews) {
  const container = document.getElementById("reviewsList")

  if (reviews.length === 0) {
    container.innerHTML = '<p class="no-reviews">No reviews yet. Be the first to review this book!</p>'
    return
  }

  container.innerHTML = reviews
    .map(
      (review) => `
        <div class="review-item">
            <div class="review-header">
                <div>
                    <div class="reviewer-name">${escapeHtml(review.reviewer_name)}</div>
                    <div class="review-rating">
                        ${generateStars(review.rating)}
                        <span>(${review.rating}/5)</span>
                    </div>
                </div>
                <div class="review-date">
                    ${new Date(review.created_at).toLocaleDateString()}
                </div>
            </div>
            ${review.comment ? `<p class="review-comment">${escapeHtml(review.comment)}</p>` : ""}
        </div>
    `,
    )
    .join("")
}

// Add Review Form
function openAddReviewForm() {
  document.getElementById("addReviewForm").style.display = "block"
  document.getElementById("reviewerName").focus()
}

function closeAddReviewForm() {
  document.getElementById("addReviewForm").style.display = "none"
  document.getElementById("reviewForm").reset()
  resetRatingStars()
}

// Rating Stars Setup
function setupRatingStars() {
  const stars = document.querySelectorAll("#ratingStars i")

  stars.forEach((star, index) => {
    star.addEventListener("click", () => {
      currentRating = index + 1
      document.getElementById("reviewRating").value = currentRating
      updateStarDisplay()
    })

    star.addEventListener("mouseenter", () => {
      highlightStars(index + 1)
    })
  })

  document.getElementById("ratingStars").addEventListener("mouseleave", () => {
    updateStarDisplay()
  })
}

function highlightStars(rating) {
  const stars = document.querySelectorAll("#ratingStars i")
  stars.forEach((star, index) => {
    star.classList.toggle("active", index < rating)
  })
}

function updateStarDisplay() {
  highlightStars(currentRating)
}

function resetRatingStars() {
  currentRating = 0
  document.getElementById("reviewRating").value = ""
  updateStarDisplay()
}

// Handle Add Review
async function handleAddReview(event) {
  event.preventDefault()

  if (!currentBookId || currentRating === 0) {
    showToast("Please select a rating", "warning")
    return
  }

  const formData = {
    reviewer_name: document.getElementById("reviewerName").value,
    rating: currentRating,
    comment: document.getElementById("reviewComment").value || null,
  }

  try {
    const response = await fetch(`${API_BASE_URL}/books/${currentBookId}/reviews`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify(formData),
    })

    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`)
    }

    await loadReviews(currentBookId)
    closeAddReviewForm()
    showToast("Review added successfully!", "success")
  } catch (error) {
    console.error("Error adding review:", error)
    showToast("Failed to add review", "error")
  }
}

// Utility Functions
function showLoading(show) {
  document.getElementById("booksLoading").style.display = show ? "flex" : "none"
  document.getElementById("booksContainer").style.display = show ? "none" : "grid"
}

function showEmptyState() {
  document.getElementById("emptyState").style.display = "block"
  document.getElementById("booksContainer").style.display = "none"
}

function updateStats() {
  document.getElementById("totalBooks").textContent = books.length
  // Note: In a real app, you'd calculate these from actual review data
  document.getElementById("totalReviews").textContent = "0"
  document.getElementById("avgRating").textContent = "0.0"
}

function refreshBooks() {
  loadBooks()
  showToast("Books refreshed!", "success")
}

function toggleView(view) {
  const buttons = document.querySelectorAll(".view-btn")
  const container = document.getElementById("booksContainer")

  buttons.forEach((btn) => btn.classList.remove("active"))
  document.querySelector(`[data-view="${view}"]`).classList.add("active")

  container.classList.toggle("list-view", view === "list")
}

function generateStars(rating) {
  let stars = ""
  for (let i = 1; i <= 5; i++) {
    stars += `<i class="fas fa-star${i <= rating ? "" : " text-gray-300"}"></i>`
  }
  return stars
}

function escapeHtml(text) {
  const div = document.createElement("div")
  div.textContent = text
  return div.innerHTML
}

function handleOutsideClick(event) {
  const modals = document.querySelectorAll(".modal.active")
  modals.forEach((modal) => {
    if (event.target === modal) {
      modal.classList.remove("active")
    }
  })
}

// Toast Notifications
function showToast(message, type = "success") {
  const container = document.getElementById("toastContainer")
  const toast = document.createElement("div")

  const icons = {
    success: "fas fa-check-circle",
    error: "fas fa-exclamation-circle",
    warning: "fas fa-exclamation-triangle",
  }

  toast.className = `toast ${type}`
  toast.innerHTML = `
        <i class="${icons[type]}"></i>
        <span>${message}</span>
    `

  container.appendChild(toast)

  setTimeout(() => {
    toast.remove()
  }, 5000)
}

// Keyboard shortcuts
document.addEventListener("keydown", (event) => {
  if (event.key === "Escape") {
    const activeModal = document.querySelector(".modal.active")
    if (activeModal) {
      activeModal.classList.remove("active")
    }
  }

  if (event.ctrlKey && event.key === "k") {
    event.preventDefault()
    document.getElementById("searchInput").focus()
  }
})

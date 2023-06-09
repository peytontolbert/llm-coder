// ./web-app/public/script.js

// Function to fetch book data from the server and render it on the webpage
function fetchBooks() {
  fetch('/books')
    .then(res => res.json())
    .then(data => {
      // Render book data on webpage
    })
    .catch(err => console.log(err));
}

// Function to fetch user data from the server and render it on the webpage
function fetchUsers() {
  fetch('/users')
    .then(res => res.json())
    .then(data => {
      // Render user data on webpage
    })
    .catch(err => console.log(err));
}

// Function to fetch borrow data from the server and render it on the webpage
function fetchBorrowData() {
  fetch('/borrow')
    .then(res => res.json())
    .then(data => {
      // Render borrow data on webpage
    })
    .catch(err => console.log(err));
}

// Function to search for books based on title, author, or genre
function searchBooks(query) {
  fetch(`/books/search?q=${query}`)
    .then(res => res.json())
    .then(data => {
      // Render search results on webpage
    })
    .catch(err => console.log(err));
}

// Function to borrow a book
function borrowBook(bookId, userId) {
  fetch(`/borrow/${bookId}/${userId}`, {
    method: 'POST'
  })
    .then(res => res.json())
    .then(data => {
      // Show success message
    })
    .catch(err => console.log(err));
}

// Function to return a book
function returnBook(borrowId) {
  fetch(`/borrow/${borrowId}`, {
    method: 'PUT'
  })
    .then(res => res.json())
    .then(data => {
      // Show success message
    })
    .catch(err => console.log(err));
}

// Function to delete a user
function deleteUser(userId) {
  fetch(`/users/${userId}`, {
    method: 'DELETE'
  })
    .then(res => res.json())
    .then(data => {
      // Show success message
    })
    .catch(err => console.log(err));
}

// Call fetch functions on page load
fetchBooks();
fetchUsers();
fetchBorrowData();
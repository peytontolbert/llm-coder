const express = require('express');
const app = express();
const port = 3000;

// Import routes
const booksRouter = require('./routes/books');
const usersRouter = require('./routes/users');
const borrowRouter = require('./routes/borrow');

// Set up view engine
app.set('view engine', 'pug');

// Serve static files from public folder
app.use(express.static(__dirname + '/public'));

// Parse incoming request bodies
app.use(express.urlencoded({ extended: true }));

// Set up routes
app.use('/books', booksRouter);
app.use('/users', usersRouter);
app.use('/borrow', borrowRouter);

// Handle 404 errors
app.use(function(req, res, next) {
  res.status(404).render('error', { message: "Page not found" });
});

// Handle server errors
app.use(function(err, req, res, next) {
  console.error(err.stack);
  res.status(500).send('Server error');
});

// Start server
app.listen(port, () => {
  console.log(`Server listening at http://localhost:${port}`);
});
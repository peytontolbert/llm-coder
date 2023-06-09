// ./web-app/routes/books.js

const express = require("express");
const router = express.Router();
const { Book } = require("../models");
const { Op } = require("sequelize");

// GET all books
router.get("/", async (req, res) => {
  try {
    const books = await Book.findAll();
    res.render("index", { books });
  } catch (err) {
    console.error(err);
    res.render("error", { message: "Error retrieving books" });
  }
});

// GET add book form
router.get("/add", (req, res) => {
  res.render("add-book");
});

// POST new book
router.post("/add", async (req, res) => {
  const { title, author, genre, ISBN, publishedDate } = req.body;
  try {
    const newBook = await Book.create({
      title,
      author,
      genre,
      ISBN,
      publishedDate,
    });
    res.redirect(`/books/${newBook.id}`);
  } catch (err) {
    console.error(err);
    res.render("error", { message: "Error creating new book" });
  }
});

// GET search results for books
router.get("/search", async (req, res) => {
  const { query } = req.query;
  try {
    const books = await Book.findAll({
      where: {
        [Op.or]: [
          { title: { [Op.like]: `%${query}%` } },
          { author: { [Op.like]: `%${query}%` } },
          { genre: { [Op.like]: `%${query}%` } },
        ],
      },
    });
    res.render("search-results", { books, query });
  } catch (err) {
    console.error(err);
    res.render("error", { message: "Error searching for books" });
  }
});

// GET book details
router.get("/:id", async (req, res) => {
  const { id } = req.params;
  try {
    const book = await Book.findByPk(id);
    if (!book) {
      res.render("error", { message: "Book not found" });
      return;
    }
    res.render("book-details", { book });
  } catch (err) {
    console.error(err);
    res.render("error", { message: "Error retrieving book details" });
  }
});

// GET edit form
router.get("/:id/edit", async (req, res) => {
  const { id } = req.params;
  try {
    const book = await Book.findByPk(id);
    if (!book) {
      res.render("error", { message: "Book not found" });
      return;
    }
    res.render("edit-book", { book });
  } catch (err) {
    console.error(err);
    res.render("error", { message: "Error retrieving edit form" });
  }
});

// POST updated book
router.post("/:id/edit", async (req, res) => {
  const { title, author, genre, ISBN, publishedDate } = req.body;
  const { id } = req.params;
  try {
    const book = await Book.findByPk(id);
    if (!book) {
      res.render("error", { message: "Book not found" });
      return;
    }
    await book.update({ title, author, genre, ISBN, publishedDate });
    res.redirect(`/books/${book.id}`);
  } catch (err) {
    console.error(err);
    res.render("error", { message: "Error updating book" });
  }
});

// POST delete book
router.post("/:id/delete", async (req, res) => {
  const { id } = req.params;
  try {
    const book = await Book.findByPk(id);
    if (!book) {
      res.render("error", { message: "Book not found" });
      return;
    }
    await book.destroy();
    res.redirect(`/books`);
  } catch (err) {
    console.error(err);
    res.render("error", { message: "Error deleting book" });
  }
});

module.exports = router;
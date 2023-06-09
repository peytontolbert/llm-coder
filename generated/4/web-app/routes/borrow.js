// ./web-app/routes/borrow.js

const express = require('express');
const router = express.Router();
const moment = require('moment');
const { Borrow, Book, User } = require('../models');
const { Op } = require('sequelize');

// Borrow Book route
router.post('/', async (req, res) => {
  try {
    const { bookId, userId } = req.body;
    // check if book exists
    const book = await Book.findByPk(bookId);
    if (!book) {
      return res.status(404).send('Book not found');
    }
    // check if book is available
    if (!book.isAvailable) {
      return res.status(400).send('Book is not available');
    }
    // check if user exists
    const user = await User.findByPk(userId);
    if (!user) {
      return res.status(404).send('User not found');
    }
    // borrow the book
    const borrow = await Borrow.create({
      bookId,
      userId,
      borrowedAt: moment().format('YYYY-MM-DD HH:mm:ss'),
    });
    // update book availability
    await book.update({ isAvailable: false });
    res.status(201).send(borrow);
  } catch (err) {
    console.error(err);
    res.status(500).send('Server error');
  }
});

// Return Book route
router.put('/', async (req, res) => {
  try {
    const { bookId, userId } = req.body;
    // check if borrowing history exists
    const borrow = await Borrow.findOne({
      where: {
        bookId,
        userId,
        returnedAt: {
          [Op.is]: null,
        },
      },
      include: [{ model: Book }, { model: User }],
    });
    if (!borrow) {
      return res.status(404).send('Borrowing history not found');
    }
    // return the book
    await borrow.update({
      returnedAt: moment().format('YYYY-MM-DD HH:mm:ss'),
    });
    // update book availability
    await borrow.book.update({ isAvailable: true });
    res.status(200).send(borrow);
  } catch (err) {
    console.error(err);
    res.status(500).send('Server error');
  }
});

module.exports = router;
// ./web-app/routes/users.js

const express = require('express');
const router = express.Router();

const { User } = require('../models');
const { Op } = require('sequelize');

// GET all users
router.get('/', async (req, res) => {
  try {
    const users = await User.findAll();
    res.render('users/index', { users });
  } catch (error) {
    console.error(error);
    res.render('error', { message: 'Error retrieving users' });
  }
});

// GET add user form
router.get('/add', (req, res) => {
  res.render('users/add');
});

// POST add user
router.post('/', async (req, res) => {
  const { name, email, password } = req.body;
  try {
    const user = await User.create({ name, email, password });
    res.redirect('/users');
  } catch (error) {
    console.error(error);
    res.render('error', { message: 'Error adding user' });
  }
});

// GET edit user form
router.get('/:userId/edit', async (req, res) => {
  const { userId } = req.params;
  try {
    const user = await User.findByPk(userId);
    res.render('users/edit', { user });
  } catch (error) {
    console.error(error);
    res.render('error', { message: 'Error retrieving user details' });
  }
});

// PUT update user
router.put('/:userId', async (req, res) => {
  const { userId } = req.params;
  const { name, email, password } = req.body;
  try {
    const user = await User.update(
      { name, email, password },
      { where: { id: userId } }
    );
    res.redirect('/users');
  } catch (error) {
    console.error(error);
    res.render('error', { message: 'Error updating user' });
  }
});

// DELETE user
router.delete('/:userId', async (req, res) => {
  const { userId } = req.params;
  try {
    const user = await User.destroy({ where: { id: userId } });
    res.redirect('/users');
  } catch (error) {
    console.error(error);
    res.render('error', { message: 'Error deleting user' });
  }
});

// GET search results
router.get('/search', async (req, res) => {
  const { query } = req.query;
  try {
    const users = await User.findAll({
      where: {
        [Op.or]: [
          { name: { [Op.like]: `%${query}%` } },
          { email: { [Op.like]: `%${query}%` } },
        ],
      },
    });
    res.render('users/index', { users, searchQuery: query });
  } catch (error) {
    console.error(error);
    res.render('error', { message: 'Error searching for users' });
  }
});

module.exports = router;
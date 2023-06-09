// web-app/models/book.js

const { DataTypes } = require('sequelize');
const sequelize = require('../database/mysql');

const Book = sequelize.define('Book', {
  id: {
    type: DataTypes.INTEGER.UNSIGNED,
    autoIncrement: true,
    primaryKey: true,
    allowNull: false,
  },
  title: {
    type: DataTypes.STRING(255),
    allowNull: false,
  },
  author: {
    type: DataTypes.STRING(255),
    allowNull: false,
  },
  genre: {
    type: DataTypes.STRING(255),
    allowNull: false,
  },
  publisher: {
    type: DataTypes.STRING(255),
    allowNull: false,
  },
  publish_date: {
    type: DataTypes.DATEONLY,
    allowNull: false,
  },
  language: {
    type: DataTypes.STRING(255),
    allowNull: false,
  },
  edition: {
    type: DataTypes.STRING(255),
    allowNull: false,
  },
  isbn: {
    type: DataTypes.STRING(20),
    allowNull: false,
    unique: true,
  },
  cover: {
    type: DataTypes.STRING(255),
    allowNull: false,
  },
  num_copies: {
    type: DataTypes.INTEGER.UNSIGNED,
    allowNull: false,
  },
  num_available: {
    type: DataTypes.VIRTUAL,
    get() {
      return this.num_copies - this.getBorrowedCount();
    },
  },
}, {
  tableName: 'books',
  timestamps: true,
});

// association with Borrow model
Book.hasMany(require('./borrow'), {
  foreignKey: 'book_id',
});

// instance method to get the number of borrowed copies of a book
Book.prototype.getBorrowedCount = async function () {
  const borrowModel = require('./borrow');
  const count = await borrowModel.count({
    where: {
      book_id: this.id,
      returned_date: {
        [DataTypes.Op.eq]: null,
      },
    },
  });
  return count;
};

module.exports = Book;
const { Model, DataTypes } = require('sequelize');
const moment = require('moment');
const sequelize = require('../database/mysql');

class Borrow extends Model {}

Borrow.init(
  {
    id: {
      type: DataTypes.INTEGER.UNSIGNED,
      autoIncrement: true,
      primaryKey: true,
    },
    book_id: {
      type: DataTypes.INTEGER.UNSIGNED,
      allowNull: false,
    },
    user_id: {
      type: DataTypes.INTEGER.UNSIGNED,
      allowNull: false,
    },
    borrowed_date: {
      type: DataTypes.DATEONLY,
      allowNull: false,
      defaultValue: moment().format('YYYY-MM-DD'),
    },
    due_date: {
      type: DataTypes.DATEONLY,
      allowNull: false,
      defaultValue: moment().add(14, 'days').format('YYYY-MM-DD'),
    },
    returned_date: {
      type: DataTypes.DATEONLY,
      allowNull: true,
      defaultValue: null,
    },
    late_fee: {
      type: DataTypes.FLOAT.UNSIGNED,
      allowNull: true,
      defaultValue: null,
    },
  },
  {
    sequelize,
    modelName: 'borrow',
    tableName: 'borrows',
    underscored: true,
    timestamps: false,
  }
);

module.exports = Borrow;
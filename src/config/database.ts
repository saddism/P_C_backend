import { Sequelize } from 'sequelize-typescript';
import { Video } from '../models/video.model';
import { Analysis } from '../models/analysis.model';

const dbName = process.env.DB_NAME || 'pc_backend';
const dbUser = process.env.DB_USER || 'postgres';
const dbPassword = process.env.DB_PASSWORD || 'postgres';
const dbHost = process.env.DB_HOST || 'localhost';

export const sequelize = new Sequelize({
  database: dbName,
  username: dbUser,
  password: dbPassword,
  host: dbHost,
  dialect: 'postgres',
  models: [Video, Analysis],
  logging: false,
  pool: {
    max: 5,
    min: 0,
    acquire: 30000,
    idle: 10000
  }
});

sequelize
  .authenticate()
  .then(() => {
    console.log('Database connection established successfully.');
  })
  .catch(err => {
    console.error('Unable to connect to the database:', err);
  });

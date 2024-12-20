"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
exports.sequelize = void 0;
const sequelize_typescript_1 = require("sequelize-typescript");
const video_model_1 = require("../models/video.model");
const analysis_model_1 = require("../models/analysis.model");
const dbName = process.env.DB_NAME || 'pc_backend';
const dbUser = process.env.DB_USER || 'postgres';
const dbPassword = process.env.DB_PASSWORD || 'postgres';
const dbHost = process.env.DB_HOST || 'localhost';
exports.sequelize = new sequelize_typescript_1.Sequelize({
    database: dbName,
    username: dbUser,
    password: dbPassword,
    host: dbHost,
    dialect: 'postgres',
    models: [video_model_1.Video, analysis_model_1.Analysis],
    logging: false,
    pool: {
        max: 5,
        min: 0,
        acquire: 30000,
        idle: 10000
    }
});
exports.sequelize
    .authenticate()
    .then(() => {
    console.log('Database connection established successfully.');
})
    .catch(err => {
    console.error('Unable to connect to the database:', err);
});

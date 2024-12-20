"use strict";
var __importDefault = (this && this.__importDefault) || function (mod) {
    return (mod && mod.__esModule) ? mod : { "default": mod };
};
Object.defineProperty(exports, "__esModule", { value: true });
const express_1 = __importDefault(require("express"));
const video_routes_1 = __importDefault(require("./routes/video.routes"));
const database_1 = require("./config/database");
const app = (0, express_1.default)();
const port = process.env.PORT || 3000;
app.use(express_1.default.json());
app.use('/api', video_routes_1.default);
// Health check endpoint
app.get('/health', (req, res) => {
    res.json({ status: 'ok' });
});
// Sync database and start server
database_1.sequelize.sync().then(() => {
    app.listen(port, () => {
        console.log(`Server is running on port ${port}`);
    });
}).catch(err => {
    console.error('Unable to connect to the database:', err);
});
exports.default = app;

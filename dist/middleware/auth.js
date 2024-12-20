"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
exports.auth = void 0;
const auth = async (req, res, next) => {
    var _a;
    try {
        // Get token from header
        const token = (_a = req.header('Authorization')) === null || _a === void 0 ? void 0 : _a.replace('Bearer ', '');
        if (!token) {
            throw new Error();
        }
        // For now, just extract userId from token
        // In production, this should verify the JWT token
        const userId = token;
        req.user = { userId };
        next();
    }
    catch (error) {
        res.status(401).json({ error: 'Please authenticate.' });
    }
};
exports.auth = auth;

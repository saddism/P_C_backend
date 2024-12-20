import { Request, Response, NextFunction } from 'express';

// Extend Express Request type to include user
declare global {
  namespace Express {
    interface Request {
      user?: {
        userId: string;
      };
    }
  }
}

export const auth = async (req: Request, res: Response, next: NextFunction) => {
  try {
    // Get token from header
    const token = req.header('Authorization')?.replace('Bearer ', '');

    if (!token) {
      throw new Error();
    }

    // For now, just extract userId from token
    // In production, this should verify the JWT token
    const userId = token;
    req.user = { userId };

    next();
  } catch (error) {
    res.status(401).json({ error: 'Please authenticate.' });
  }
};

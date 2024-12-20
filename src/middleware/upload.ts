import multer from 'multer';
import path from 'path';
import { v4 as uuidv4 } from 'uuid';

// Configure storage
const storage = multer.diskStorage({
  destination: (req, file, cb) => {
    cb(null, 'uploads/');
  },
  filename: (req, file, cb) => {
    const uniqueName = `${uuidv4()}${path.extname(file.originalname)}`;
    cb(null, uniqueName);
  }
});

// File filter to accept only video files
const fileFilter = (req: any, file: Express.Multer.File, cb: multer.FileFilterCallback) => {
  if (file.mimetype.startsWith('video/')) {
    cb(null, true);
  } else {
    cb(new Error('Only video files are allowed'));
  }
};

// Create multer upload middleware
export const uploadMiddleware = multer({
  storage,
  fileFilter,
  limits: {
    fileSize: 500 * 1024 * 1024 // 500MB limit
  }
}).single('video');

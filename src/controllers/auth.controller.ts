import { Request, Response } from 'express';
import bcrypt from 'bcrypt';
import jwt from 'jsonwebtoken';
import { pool } from '../config/database';
import { sendVerificationEmail } from '../services/email.service';

// Validation helpers
const validatePassword = (password: string): boolean => {
  const minLength = 8;
  const hasUpperCase = /[A-Z]/.test(password);
  const hasNumber = /[0-9]/.test(password);
  return password.length >= minLength && hasUpperCase && hasNumber;
};

const generateVerificationCode = (): string => {
  return Math.floor(100000 + Math.random() * 900000).toString();
};

// Rate limiting map
const rateLimitMap = new Map<string, { count: number; timestamp: number }>();

const checkRateLimit = (email: string): boolean => {
  const now = Date.now();
  const windowMs = parseInt(process.env.RATE_LIMIT_WINDOW || '900000'); // 15 minutes
  const maxRequests = parseInt(process.env.RATE_LIMIT_MAX_REQUESTS || '3');

  const userLimit = rateLimitMap.get(email);
  if (!userLimit || (now - userLimit.timestamp) > windowMs) {
    rateLimitMap.set(email, { count: 1, timestamp: now });
    return true;
  }

  if (userLimit.count >= maxRequests) {
    return false;
  }

  userLimit.count++;
  return true;
};

export const register = async (req: Request, res: Response): Promise<void> => {
  try {
    const { email, password, username } = req.body;

    // Validate input
    if (!email || !password || !username) {
      res.status(400).json({ error: 'All fields are required' });
      return;
    }

    // Validate password
    if (!validatePassword(password)) {
      res.status(400).json({
        error: 'Password must be at least 8 characters long and contain at least one uppercase letter and one number'
      });
      return;
    }

    // Check if user exists
    const existingUser = await pool.query(
      'SELECT * FROM users WHERE email = $1 OR username = $2',
      [email, username]
    );

    if (existingUser.rows.length > 0) {
      res.status(409).json({ error: 'Email or username already exists' });
      return;
    }

    // Hash password
    const salt = await bcrypt.genSalt(10);
    const hashedPassword = await bcrypt.hash(password, salt);

    // Create user
    const result = await pool.query(
      'INSERT INTO users (email, password, username) VALUES ($1, $2, $3) RETURNING id',
      [email, hashedPassword, username]
    );

    const userId = result.rows[0].id;

    // Generate verification code
    const code = generateVerificationCode();
    const expiresAt = new Date(Date.now() + parseInt(process.env.VERIFICATION_CODE_EXPIRY || '600') * 1000);

    // Save verification code
    await pool.query(
      'INSERT INTO verifications (user_id, code, expires_at) VALUES ($1, $2, $3)',
      [userId, code, expiresAt]
    );

    // Send verification email
    await sendVerificationEmail(email, code);

    res.status(201).json({
      message: 'Registration successful. Please check your email for verification code.'
    });
  } catch (error) {
    console.error('Registration error:', error);
    res.status(500).json({ error: 'Internal server error' });
  }
};

export const verifyEmail = async (req: Request, res: Response): Promise<void> => {
  try {
    const { email, code } = req.body;

    if (!email || !code) {
      res.status(400).json({ error: 'Email and verification code are required' });
      return;
    }

    // Get user and verification
    const result = await pool.query(
      `SELECT v.*, u.id as user_id
       FROM verifications v
       JOIN users u ON v.user_id = u.id
       WHERE u.email = $1 AND v.code = $2
       AND v.expires_at > NOW()
       ORDER BY v.created_at DESC
       LIMIT 1`,
      [email, code]
    );

    if (result.rows.length === 0) {
      res.status(400).json({ error: 'Invalid or expired verification code' });
      return;
    }

    // Update user verification status
    await pool.query(
      'UPDATE users SET is_verified = true WHERE id = $1',
      [result.rows[0].user_id]
    );

    // Delete used verification code
    await pool.query(
      'DELETE FROM verifications WHERE id = $1',
      [result.rows[0].id]
    );

    res.json({ message: 'Email verified successfully' });
  } catch (error) {
    console.error('Email verification error:', error);
    res.status(500).json({ error: 'Internal server error' });
  }
};

export const login = async (req: Request, res: Response): Promise<void> => {
  try {
    const { email, password } = req.body;

    if (!email || !password) {
      res.status(400).json({ error: 'Email and password are required' });
      return;
    }

    // Get user
    const result = await pool.query(
      'SELECT * FROM users WHERE email = $1',
      [email]
    );

    if (result.rows.length === 0) {
      res.status(401).json({ error: 'Invalid credentials' });
      return;
    }

    const user = result.rows[0];

    // Check if email is verified
    if (!user.is_verified) {
      res.status(403).json({ error: 'Please verify your email before logging in' });
      return;
    }

    // Verify password
    const validPassword = await bcrypt.compare(password, user.password);
    if (!validPassword) {
      res.status(401).json({ error: 'Invalid credentials' });
      return;
    }

    // Generate JWT token
    const token = jwt.sign(
      { id: user.id, email: user.email, username: user.username },
      process.env.JWT_SECRET || 'default_secret',
      { expiresIn: '24h' }
    );

    res.json({ token });
  } catch (error) {
    console.error('Login error:', error);
    res.status(500).json({ error: 'Internal server error' });
  }
};

export const resendVerification = async (req: Request, res: Response): Promise<void> => {
  try {
    const { email } = req.body;

    if (!email) {
      res.status(400).json({ error: 'Email is required' });
      return;
    }

    // Check rate limit
    if (!checkRateLimit(email)) {
      res.status(429).json({
        error: 'Too many verification attempts. Please try again later.'
      });
      return;
    }

    // Get user
    const userResult = await pool.query(
      'SELECT * FROM users WHERE email = $1',
      [email]
    );

    if (userResult.rows.length === 0) {
      res.status(404).json({ error: 'User not found' });
      return;
    }

    const user = userResult.rows[0];

    if (user.is_verified) {
      res.status(400).json({ error: 'Email is already verified' });
      return;
    }

    // Generate new verification code
    const code = generateVerificationCode();
    const expiresAt = new Date(Date.now() + parseInt(process.env.VERIFICATION_CODE_EXPIRY || '600') * 1000);

    // Save new verification code
    await pool.query(
      'INSERT INTO verifications (user_id, code, expires_at) VALUES ($1, $2, $3)',
      [user.id, code, expiresAt]
    );

    // Send verification email
    await sendVerificationEmail(email, code);

    res.json({ message: 'New verification code sent successfully' });
  } catch (error) {
    console.error('Resend verification error:', error);
    res.status(500).json({ error: 'Internal server error' });
  }
};

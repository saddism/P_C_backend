import nodemailer from 'nodemailer';
import dotenv from 'dotenv';

dotenv.config();

const transporter = nodemailer.createTransport({
  host: process.env.SMTP_HOST,
  port: parseInt(process.env.SMTP_PORT || '587'),
  auth: {
    user: process.env.SMTP_USER,
    pass: process.env.SMTP_PASS,
  },
});

export const sendVerificationEmail = async (email: string, code: string): Promise<void> => {
  try {
    const mailOptions = {
      from: process.env.SMTP_USER,
      to: email,
      subject: '验证您的邮箱地址',
      html: `
        <div style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto;">
          <h2>验证您的邮箱地址</h2>
          <p>您好！</p>
          <p>您的验证码是：</p>
          <h1 style="color: #4CAF50; font-size: 32px; letter-spacing: 5px; margin: 20px 0;">${code}</h1>
          <p>此验证码将在10分钟内有效。</p>
          <p>如果您没有请求此验证码，请忽略此邮件。</p>
          <p>谢谢！</p>
        </div>
      `,
    };

    await transporter.sendMail(mailOptions);
  } catch (error) {
    console.error('Error sending verification email:', error);
    throw error;
  }
};

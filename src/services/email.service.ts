import nodemailer from 'nodemailer';
import SMTPTransport from 'nodemailer/lib/smtp-transport';
import dotenv from 'dotenv';

dotenv.config();

const transportOptions: SMTPTransport.Options = {
  host: process.env.SMTP_HOST,
  port: parseInt(process.env.SMTP_PORT || '465'),
  secure: true,
  auth: {
    user: process.env.SMTP_USER,
    pass: process.env.SMTP_PASS,
  },
  tls: {
    rejectUnauthorized: true
  }
};

const transporter = nodemailer.createTransport(transportOptions);

// Verify transporter connection
transporter.verify((error, success) => {
  if (error) {
    console.error('SMTP connection error:', error);
  } else {
    console.log('SMTP server is ready to send emails');
  }
});

export const sendVerificationEmail = async (email: string, code: string): Promise<void> => {
  console.log(`Attempting to send verification email to ${email}`);

  const mailOptions = {
    from: process.env.SMTP_USER,
    to: email,
    subject: '邮箱验证码',
    text: `您的验证码是: ${code}\n该验证码10分钟内有效。`,
    html: `
      <div style="font-family: Arial, sans-serif; padding: 20px;">
        <h2>邮箱验证</h2>
        <p>您的验证码是: <strong>${code}</strong></p>
        <p>该验证码10分钟内有效。</p>
      </div>
    `
  };

  try {
    console.log('Sending email with options:', JSON.stringify(mailOptions, null, 2));
    const info = await transporter.sendMail(mailOptions);
    console.log('Email sent successfully:', info.response);
  } catch (error) {
    console.error('Failed to send email:', error);
    throw new Error('Failed to send verification email');
  }
};

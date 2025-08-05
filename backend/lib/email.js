const nodemailer = require('nodemailer');

const transporter = nodemailer.createTransport({
  host: process.env.SMTP_HOST,
  port: parseInt(process.env.SMTP_PORT || '587'),
  secure: process.env.SMTP_SECURE === 'true',
  auth: {
    user: process.env.SMTP_USER,
    pass: process.env.SMTP_PASS,
  },
});

const sendEmail = async ({ to, subject, html }) => {
  try {
    await transporter.sendMail({
      from: process.env.FROM_EMAIL,
      to,
      subject,
      html,
    });
  } catch (error) {
    console.error('Email sending failed:', error);
    throw new Error('Failed to send email');
  }
};

module.exports = { sendEmail };
const bcrypt = require('bcryptjs');
const jwt = require('jsonwebtoken');
const { PrismaClient, VerificationType } = require('../generated/prisma');
const { sendEmail } = require('./email');
const { sendSMS } = require('./sms');

const prisma = new PrismaClient();

const generateToken = (userId) => {
  return jwt.sign({ userId }, process.env.JWT_SECRET, {
    expiresIn: '7d',
  });
};

const verifyToken = (token) => {
  try {
    return jwt.verify(token, process.env.JWT_SECRET);
  } catch {
    return null;
  }
};

const generateVerificationToken = () => {
  return Math.random().toString(36).substring(2) + Date.now().toString(36);
};

const generateOTP = () => {
  return Math.floor(100000 + Math.random() * 900000).toString();
};

const hashPassword = async (password) => {
  return bcrypt.hash(password, 12);
};

const verifyPassword = async (password, hash) => {
  return bcrypt.compare(password, hash);
};

const registerUser = async (data) => {
  const existingUser = await prisma.user.findFirst({
    where: {
      OR: [
        { email: data.email },
        { username: data.username }
      ]
    }
  });

  if (existingUser) {
    throw new Error('User with this email or username already exists');
  }

  const hashedPassword = await hashPassword(data.password);

  

  await sendEmailVerification(data.email);

  if (data.phone) {
    await sendPhoneVerification(data.phone);
  }

  const user = await prisma.user.create({
    data: {
      email: data.email,
      username: data.username,
      name: data.name,
      phone: data.phone,
      password: hashedPassword,
    },
  });

  const token = generateToken(user.id);

  return {
    user: {
      id: user.id,
      email: user.email,
      username: user.username,
      name: user.name,
      phone: user.phone,
      isEmailVerified: !!user.isEmailVerified,
      isPhoneVerified: !!user.isPhoneVerified,
    },
    token,
  };
};

const loginUser = async (credentials) => {
  const user = await prisma.user.findFirst({
    where: {
      OR: [
        { email: credentials.emailOrUsername },
        { username: credentials.emailOrUsername }
      ]
    }
  });

  if (!user) {
    throw new Error('Invalid credentials');
  }

  const isPasswordValid = await verifyPassword(credentials.password, user.password);
  if (!isPasswordValid) {
    throw new Error('Invalid credentials');
  }

  const token = generateToken(user.id);

  return {
    user: {
      id: user.id,
      email: user.email,
      username: user.username,
      name: user.name,
      phone: user.phone,
      isEmailVerified: !!user.isEmailVerified,
      isPhoneVerified: !!user.isPhoneVerified,
    },
    token,
  };
};

const getUserById = async (userId) => {
  const user = await prisma.user.findUnique({
    where: { id: userId },
  });

  if (!user) return null;

  return {
    id: user.id,
    email: user.email,
    username: user.username,
    name: user.name,
    phone: user.phone,
    isEmailVerified: !!user.isEmailVerified,
    isPhoneVerified: !!user.isPhoneVerified,
  };
};

const sendEmailVerification = async (email) => {
  const token = generateVerificationToken();
  const expires = new Date(Date.now() + 24 * 60 * 60 * 1000);

  await prisma.verificationToken.deleteMany({
    where: {
      identifier: email,
      type: VerificationType.email,
    },
  });

  await prisma.verificationToken.create({
    data: {
      identifier: email,
      type: VerificationType.email,
      token,
      expires,
    },
  });

  const verificationUrl = `${process.env.FRONTEND_URL}/verify-email?token=${token}`;
  await sendEmail({
    to: email,
    subject: 'Verify your email address',
    html: `
      <div style="max-width: 600px; margin: 0 auto; padding: 20px; font-family: Arial, sans-serif;">
        <h2 style="color: #333;">Verify Your Email Address</h2>
        <p>Thank you for signing up! Please click the button below to verify your email address:</p>
        <a href="${verificationUrl}" style="display: inline-block; background-color: #007bff; color: white; padding: 12px 24px; text-decoration: none; border-radius: 4px; margin: 20px 0;">
          Verify Email
        </a>
        <p>Or copy and paste this link into your browser:</p>
        <p style="word-break: break-all; color: #666;">${verificationUrl}</p>
        <p>This link will expire in 24 hours.</p>
      </div>
    `,
  });
};

const sendPhoneVerification = async (phone) => {
  const token = generateOTP();
  const expires = new Date(Date.now() + 10 * 60 * 1000);

  await prisma.verificationToken.deleteMany({
    where: {
      identifier: phone,
      type: VerificationType.PHONE,
    },
  });

  await prisma.verificationToken.create({
    data: {
      identifier: phone,
      type: VerificationType.PHONE,
      token,
      expires,
    },
  });

  await sendSMS({
    to: phone,
    message: `Your verification code is: ${token}. This code will expire in 10 minutes.`,
  });
};

const verifyEmailToken = async (token) => {
  const verificationToken = await prisma.verificationToken.findFirst({
    where: {
      token,
      type: VerificationType.email,
      expires: {
        gt: new Date(),
      },
    },
  });

  if (!verificationToken) {
    return false;
  }

  await prisma.user.update({
    where: { email: verificationToken.identifier },
    data: { isEmailVerified: new Date() },
  });


  return true;
};

const verifyPhoneToken = async (phone, token) => {
  const verificationToken = await prisma.verificationToken.findFirst({
    where: {
      identifier: phone,
      token,
      type: VerificationType.PHONE,
      expires: {
        gt: new Date(),
      },
    },
  });

  if (!verificationToken) {
    throw new Error('Invalid or expired verification code');
  }

  const userToVerify = await prisma.user.findFirst({
      where: { phone: verificationToken.identifier }
  });

  if (!userToVerify) {
      throw new Error('User for this phone number not found.');
  }

  await prisma.user.update({
    where: { id: userToVerify.id },
    data: { isPhoneVerified: new Date() },
  });

  await prisma.verificationToken.delete({
    where: { id: verificationToken.id },
  });

  return true;
};

const resendEmailVerification = async (email) => {
  const user = await prisma.user.findUnique({
    where: { email },
  });

  if (!user) {
    throw new Error('User not found');
  }

  if (user.isEmailVerified) {
    throw new Error('Email is already verified');
  }

  await sendEmailVerification(email);
  return true;
};

const resendPhoneVerification = async (phone) => {
  const user = await prisma.user.findFirst({
    where: { phone },
  });

  if (!user) {
    throw new Error('User not found');
  }

  if (user.isPhoneVerified) {
    throw new Error('Phone is already verified');
  }

  await sendPhoneVerification(phone);
  return true;
};

const changePassword = async (userId, currentPassword, newPassword) => {
  const user = await prisma.user.findUnique({
    where: { id: userId },
  });

  if (!user) {
    throw new Error('User not found');
  }

  const isCurrentPasswordValid = await verifyPassword(currentPassword, user.password);
  if (!isCurrentPasswordValid) {
    throw new Error('Current password is incorrect');
  }

  const hashedNewPassword = await hashPassword(newPassword);

  await prisma.user.update({
    where: { id: userId },
    data: { password: hashedNewPassword },
  });

  return true;
};

const requestPasswordReset = async (email) => {
  const user = await prisma.user.findUnique({
    where: { email },
  });

  if (!user) {
    return true;
  }

  const token = generateVerificationToken();
  const expires = new Date(Date.now() + 1 * 60 * 60 * 1000);

  await prisma.verificationToken.deleteMany({
    where: {
      identifier: email,
      type: VerificationType.email,
    },
  });

  await prisma.verificationToken.create({
    data: {
      identifier: email,
      type: VerificationType.email,
      token,
      expires,
    },
  });

  const resetUrl = `${process.env.FRONTEND_URL}/reset-password?token=${token}`;
  await sendEmail({
    to: email,
    subject: 'Reset your password',
    html: `
      <div style="max-width: 600px; margin: 0 auto; padding: 20px; font-family: Arial, sans-serif;">
        <h2 style="color: #333;">Reset Your Password</h2>
        <p>You requested to reset your password. Click the button below to set a new password:</p>
        <a href="${resetUrl}" style="display: inline-block; background-color: #dc3545; color: white; padding: 12px 24px; text-decoration: none; border-radius: 4px; margin: 20px 0;">
          Reset Password
        </a>
        <p>Or copy and paste this link into your browser:</p>
        <p style="word-break: break-all; color: #666;">${resetUrl}</p>
        <p>This link will expire in 1 hour.</p>
        <p>If you didn't request this, please ignore this email.</p>
      </div>
    `,
  });

  return true;
};

const resetPassword = async (token, newPassword) => {
  const verificationToken = await prisma.verificationToken.findFirst({
    where: {
      token,
      type: VerificationType.email,
      expires: {
        gt: new Date(),
      },
    },
  });

  if (!verificationToken) {
    throw new Error('Invalid or expired reset token');
  }

  const hashedPassword = await hashPassword(newPassword);

  await prisma.user.update({
    where: { email: verificationToken.identifier },
    data: { password: hashedPassword },
  });

  await prisma.verificationToken.delete({
    where: { id: verificationToken.id },
  });

  return true;
};

const authenticateUser = async (req, res, next) => {
  try {
    const token = req.headers.authorization?.replace('Bearer ', '');
    
    if (!token) {
      return res.status(401).json({ error: 'Access token required' });
    }

    const decoded = verifyToken(token);
    if (!decoded) {
      return res.status(401).json({ error: 'Invalid access token' });
    }

    const user = await getUserById(decoded.userId);
    if (!user) {
      return res.status(401).json({ error: 'User not found' });
    }

    req.user = user;
    next();
  } catch (error) {
    return res.status(401).json({ error: 'Authentication failed' });
  }
};

const requireEmailVerification = (req, res, next) => {
  if (!req.user.isEmailVerified) {
    return res.status(403).json({ error: 'Email verification required' });
  }
  next();
};

const requirePhoneVerification = (req, res, next) => {
  if (!req.user.isPhoneVerified) {
    return res.status(403).json({ error: 'Phone verification required' });
  }
  next();
};

module.exports = {
  generateToken,
  verifyToken,
  hashPassword,
  verifyPassword,
  registerUser,
  loginUser,
  getUserById,
  sendEmailVerification,
  sendPhoneVerification,
  verifyEmailToken,
  verifyPhoneToken,
  resendEmailVerification,
  resendPhoneVerification,
  changePassword,
  requestPasswordReset,
  resetPassword,
  authenticateUser,
  requireEmailVerification,
  requirePhoneVerification,
};

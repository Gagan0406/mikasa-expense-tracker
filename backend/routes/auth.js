const { PrismaClient, VerificationType } = require('../generated/prisma');
const prisma = new PrismaClient();


const express = require('express');
const router = express.Router();
const {
  registerUser,
  loginUser,
  verifyEmailToken,
  verifyPhoneToken,
  resendEmailVerification,
  resendPhoneVerification,
  changePassword,
  requestPasswordReset,
  resetPassword,
  authenticateUser,
} = require('../lib/auth');

router.post('/register', async (req, res) => {
  try {
    const { email, username, name, phone, password } = req.body;

    if (!email || !username || !name || !password) {
      return res.status(400).json({ error: 'Missing required fields' });
    }

    if (password.length < 6) {
      return res.status(400).json({ error: 'Password must be at least 6 characters' });
    }

    const result = await registerUser({ email, username, name, phone, password });
    res.status(201).json(result);
  } catch (error) {
    res.status(400).json({ error: error.message });
  }
});

router.post('/login', async (req, res) => {
  try {
    const { emailOrUsername, password } = req.body;

    if (!emailOrUsername || !password) {
      return res.status(400).json({ error: 'Email/username and password are required' });
    }

    const result = await loginUser({ emailOrUsername, password });
    res.json(result);
  } catch (error) {
    res.status(401).json({ error: error.message });
  }
});

router.get('/me', authenticateUser, (req, res) => {
  res.json({ user: req.user });
});

router.post('/verify-email', async (req, res) => {
  try {
    const { token } = req.body;

    if (!token) {
      return res.status(400).json({ error: 'Verification token is required' });
    }

   const check =  await verifyEmailToken(token);
   if(check){
    res.status(200).json({ message: 'Email verified successfully' });
    await prisma.verificationToken.delete({
    where: { id: token },
  });
   }
  } catch (error) {
    res.status(400).json({ error: error.message });
  }
});

router.post('/verify-phone', async (req, res) => {
  try {
    const { phone, code } = req.body;

    if (!phone || !code) {
      return res.status(400).json({ error: 'Phone number and verification code are required' });
    }

    await verifyPhoneToken(phone, code);
    res.json({ message: 'Phone verified successfully' });
  } catch (error) {
    res.status(400).json({ error: error.message });
  }
});

router.post('/resend-email-verification', async (req, res) => {
  try {
    const { email } = req.body;

    if (!email) {
      return res.status(400).json({ error: 'Email is required' });
    }

    await resendEmailVerification(email);
    res.json({ message: 'Verification email sent' });
  } catch (error) {
    res.status(400).json({ error: error.message });
  }
});

router.post('/resend-phone-verification', async (req, res) => {
  try {
    const { phone } = req.body;

    if (!phone) {
      return res.status(400).json({ error: 'Phone number is required' });
    }

    await resendPhoneVerification(phone);
    res.json({ message: 'Verification SMS sent' });
  } catch (error) {
    res.status(400).json({ error: error.message });
  }
});

router.post('/change-password', authenticateUser, async (req, res) => {
  try {
    const { currentPassword, newPassword } = req.body;

    if (!currentPassword || !newPassword) {
      return res.status(400).json({ error: 'Current password and new password are required' });
    }

    if (newPassword.length < 6) {
      return res.status(400).json({ error: 'New password must be at least 6 characters' });
    }

    await changePassword(req.user.id, currentPassword, newPassword);
    res.json({ message: 'Password changed successfully' });
  } catch (error) {
    res.status(400).json({ error: error.message });
  }
});

router.post('/forgot-password', async (req, res) => {
  try {
    const { email } = req.body;

    if (!email) {
      return res.status(400).json({ error: 'Email is required' });
    }

    await requestPasswordReset(email);
    res.json({ message: 'Password reset email sent if account exists' });
  } catch (error) {
    res.status(500).json({ error: 'Failed to process request' });
  }
});

router.post('/reset-password', async (req, res) => {
  try {
    const { token, newPassword } = req.body;

    if (!token || !newPassword) {
      return res.status(400).json({ error: 'Token and new password are required' });
    }

    if (newPassword.length < 6) {
      return res.status(400).json({ error: 'Password must be at least 6 characters' });
    }

    await resetPassword(token, newPassword);
    res.json({ message: 'Password reset successfully' });
  } catch (error) {
    res.status(400).json({ error: error.message });
  }
});

module.exports = router;
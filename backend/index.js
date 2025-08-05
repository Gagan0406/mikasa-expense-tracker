const express = require('express');
const cors = require('cors');
const helmet = require('helmet');
const rateLimit = require('express-rate-limit');
const morgan = require('morgan');
require('dotenv').config();

const authRoutes = require('./routes/auth');

const app = express();
const PORT = process.env.PORT || 3000;

// Security middleware
app.use(helmet({
  contentSecurityPolicy: {
    directives: {
      defaultSrc: ["'self'"],
      styleSrc: ["'self'", "'unsafe-inline'"],
      scriptSrc: ["'self'"],
      imgSrc: ["'self'", "data:", "https:"],
    },
  },
}));

app.use(cors({
  origin: process.env.FRONTEND_URL || 'http://localhost:5173',
  credentials: true,
  methods: ['GET', 'POST', 'PUT', 'DELETE', 'PATCH', 'OPTIONS'],
  allowedHeaders: ['Content-Type', 'Authorization', 'X-Requested-With'],
}));

const limiter = rateLimit({
  windowMs: 30 * 60 * 1000, 
  max: 200, 
  message: {
    error: 'Too many requests from this IP, please try again later.',
  },
  standardHeaders: true,
  legacyHeaders: false,
});

app.use(limiter);

const authLimiter = rateLimit({
  windowMs: 15 * 60 * 1000, 
  max: 100,
  message: {
    error: 'Too many authentication attempts, please try again later.',
  },
  standardHeaders: true,
  legacyHeaders: false,
});

app.use('/api/auth', authLimiter);

app.use(express.json({ limit: '10mb' }));
app.use(express.urlencoded({ extended: true, limit: '10mb' }));

if (process.env.NODE_ENV === 'development') {
  app.use(morgan('dev'));
} else {
  app.use(morgan('combined'));
}

app.get('/health', (req, res) => {
  res.status(200).json({
    status: 'OK',
    timestamp: new Date().toISOString(),
    uptime: process.uptime(),
    environment: process.env.NODE_ENV || 'development',
  });
});

app.use('/api/auth', authRoutes);

app.get('/', (req, res) => {
  res.json({
    message: 'Authentication API Server',
    version: '1.0.0',
    endpoints: {
      health: '/health',
      auth: '/api/auth',
    },
    documentation: {
      register: 'POST /api/auth/register',
      login: 'POST /api/auth/login',
      me: 'GET /api/auth/me',
      verifyEmail: 'POST /api/auth/verify-email',
      verifyPhone: 'POST /api/auth/verify-phone',
      resendEmailVerification: 'POST /api/auth/resend-email-verification',
      resendPhoneVerification: 'POST /api/auth/resend-phone-verification',
      changePassword: 'POST /api/auth/change-password',
      forgotPassword: 'POST /api/auth/forgot-password',
      resetPassword: 'POST /api/auth/reset-password',
    },
  });
});

app.use('*', (req, res) => {
  res.status(404).json({
    error: 'Route not found',
    message: `The requested route ${req.originalUrl} does not exist`,
  });
});

app.use((err, req, res, next) => {
  console.error('Global error handler:', err);

  if (err.code === 'P2002') {
    return res.status(400).json({
      error: 'A record with this information already exists',
    });
  }

  if (err.code === 'P2025') {
    return res.status(404).json({
      error: 'Record not found',
    });
  }

  if (err.name === 'JsonWebTokenError') {
    return res.status(401).json({
      error: 'Invalid token',
    });
  }

  if (err.name === 'TokenExpiredError') {
    return res.status(401).json({
      error: 'Token expired',
    });
  }

  if (err.name === 'ValidationError') {
    return res.status(400).json({
      error: 'Validation failed',
      details: err.message,
    });
  }

  const statusCode = err.statusCode || err.status || 500;
  const message = err.message || 'Internal server error';

  res.status(statusCode).json({
    error: process.env.NODE_ENV === 'production' ? 'Something went wrong' : message,
    ...(process.env.NODE_ENV === 'development' && { stack: err.stack }),
  });
});

const gracefulShutdown = () => {
  console.log('Received shutdown signal, shutting down gracefully...');
  
  server.close(() => {
    console.log('HTTP server closed');
    
    process.exit(0);
  });

  setTimeout(() => {
    console.error('Could not close connections in time, forcefully shutting down');
    process.exit(1);
  }, 10000);
};

process.on('SIGTERM', gracefulShutdown);
process.on('SIGINT', gracefulShutdown);

process.on('uncaughtException', (err) => {
  console.error('Uncaught Exception:', err);
  process.exit(1);
});

process.on('unhandledRejection', (reason, promise) => {
  console.error('Unhandled Rejection at:', promise, 'reason:', reason);
  process.exit(1);
});

app.listen(PORT, () => {
  console.log(`Server running on port ${PORT}`);

});


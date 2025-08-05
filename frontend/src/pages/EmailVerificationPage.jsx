import React, { useEffect, useState } from 'react';
import { useSearchParams, Link } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL;

// A simple SVG checkmark component for visual feedback
const CheckmarkIcon = () => (
    <svg className="mx-auto h-16 w-16 text-green-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
    </svg>
);

const EmailVerificationPage = () => {
  const [searchParams] = useSearchParams();
  const [status, setStatus] = useState('verifying'); 
  const [message, setMessage] = useState('Verifying your email, please wait...');
  
  const { user, refreshUser } = useAuth(); 
  const token = searchParams.get('token');

  useEffect(() => {
    if (user && user.isEmailVerified) {
        setStatus('success');
        setMessage('Your email has already been verified.');
        return;
    }

    if (!token) {
      setStatus('error');
      setMessage('No verification token found. The link may be invalid.');
      return;
    }

    const verifyToken = async () => {
      try {
        const response = await fetch(`${API_BASE_URL}/auth/verify-email`, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ token }),
        });

        const data = await response.json();

        if (!response.ok) {
          if (data.error?.includes('Invalid or expired')) {
            setMessage('This verification link has expired or has already been used. Please try logging in or requesting a new link.');
          }
          throw new Error(data.error || 'Failed to verify email.');
        }

        setStatus('success');
        setMessage('Your email has been successfully verified!');
        
        if (user) {
            await refreshUser();
        }

      } catch (err) {
        setStatus('error');
        if (!message.includes('already been used')) {
            setMessage(err.message);
        }
      }
    };

    verifyToken();
   
  }, [token, user, message, refreshUser]);

  const statusInfo = {
    verifying: {
      color: 'text-slate-300',
      title: 'Verifying...',
      icon: null,
    },
    success: {
      color: 'text-green-400',
      title: 'Success!',
      icon: <CheckmarkIcon />,
    },
    error: {
      color: 'text-red-400',
      title: 'Verification Failed',
      icon: null,
    },
  };

  return (
    <main className="w-full min-h-screen bg-gray-900 flex items-center justify-center p-4">
      <div className="w-full max-w-md text-center bg-slate-900/50 border border-slate-700 p-8 rounded-2xl shadow-2xl">
        
        {statusInfo[status].icon}

        <h1 className={`text-3xl font-bold mt-4 mb-4 ${statusInfo[status].color}`}>
          {statusInfo[status].title}
        </h1>
        <p className="text-slate-400 mb-8">{message}</p>

        {status === 'success' && (
          <Link 
            to="/login" 
            className="bg-indigo-600 text-white font-semibold py-2 px-5 rounded-md hover:bg-indigo-700 transition-colors"
          >
            Proceed to Login
          </Link>
        )}
         {status === 'error' && (
          <Link 
            to="/register" 
            className="bg-slate-600 text-white font-semibold py-2 px-5 rounded-md hover:bg-slate-700 transition-colors"
          >
            Return to Register
          </Link>
        )}
      </div>
    </main>
  );
};

export default EmailVerificationPage;

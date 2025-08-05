import React, { useState, useEffect } from 'react'
import { useNavigate } from 'react-router-dom'; 
import { useAuth } from '../context/AuthContext';

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL;

const VerifyAccountPage = () => {
  const { user, logout, refreshUser } = useAuth();
  const [otp, setOtp] = useState('');
  const [error, setError] = useState('');
  const [message, setMessage] = useState('');
  const [isProcessing, setIsProcessing] = useState(false);
  const navigate = useNavigate(); 


  useEffect(() => {
    if (user && user.isEmailVerified && user.isPhoneVerified) {
      setMessage("All verified! Redirecting to dashboard...");
      setTimeout(() => {
        navigate('/dashboard');
      }, 1500); 
    }
  }, [user, navigate]);


  const handleResendEmail = async () => {
    setIsProcessing(true);
    setError('');
    setMessage('');
    try {
      const response = await fetch(`${API_BASE_URL}/auth/resend-email-verification`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ email: user.email }),
      });
      const data = await response.json();
      if (!response.ok) {
        throw new Error(data.error || 'Failed to resend email.');
      }
      setMessage('Verification email sent!');
    } catch (err) {
      setError(err.message);
    } finally {
      setIsProcessing(false);
    }
  };

  const handleResendPhone = async () => {
    setIsProcessing(true);
    setError('');
    setMessage('');
    try {
      const response = await fetch(`${API_BASE_URL}/auth/resend-phone-verification`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ phone: user.phone }),
      });
      const data = await response.json();
      if (!response.ok) {
        throw new Error(data.error || 'Failed to resend code.');
      }
      setMessage('Verification code sent to your phone!');
    } catch (err) {
      setError(err.message);
    } finally {
      setIsProcessing(false);
    }
  };

  const handleVerifyPhone = async (e) => {
    e.preventDefault();
    if (otp.length !== 6) {
        setError('Please enter a valid 6-digit OTP.');
        return;
    }
    setIsProcessing(true);
    setError('');
    setMessage('');

    try {
        const response = await fetch(`${API_BASE_URL}/auth/verify-phone`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ phone: user.phone, code: otp }),
        });
        const data = await response.json();
        if (!response.ok) {
            throw new Error(data.error || 'Invalid or expired code.');
        }
        setMessage('Phone successfully verified!');
        setOtp(''); 
        await refreshUser();
    } catch (err) {
        setError(err.message);
    } finally {
        setIsProcessing(false);
    }
  }

  if (!user) {
    return <p>Loading...</p>;
  }

  return (
    <div className="w-full min-h-screen bg-gray-900 text-white flex flex-col items-center justify-center p-4">
      <div className="text-center max-w-lg w-full">
        <h1 className="text-4xl font-bold">Almost there!</h1>
        <p className="text-xl mt-4 text-slate-300">
          Please verify your email and phone number to continue.
        </p>
        
        <div className="mt-8 space-y-6 text-left bg-slate-800 p-6 rounded-lg">
          {/* Email Verification Section */}
          <div className="flex justify-between items-center">
            <div>
                <p className="font-semibold">Email Verification</p>
                <p className="font-mono text-slate-400 text-sm">{user.email}</p>
            </div>
            {user.isEmailVerified ? (
              <span className="text-green-400 font-semibold">✔ Verified</span>
            ) : (
              <button onClick={handleResendEmail} disabled={isProcessing} className="text-indigo-400 hover:underline text-sm font-semibold disabled:opacity-50">Resend Link</button>
            )}
          </div>
          
          {/* Phone Verification Section */}
          <div>
            <div className="flex justify-between items-center">
                <div>
                    <p className="font-semibold">Phone Verification</p>
                    <p className="font-mono text-slate-400 text-sm">{user.phone}</p>
                </div>
                {!user.isPhoneVerified && (
                  <button onClick={handleResendPhone} disabled={isProcessing} className="text-indigo-400 hover:underline text-sm font-semibold disabled:opacity-50">Resend Code</button>
                )}
            </div>
            {!user.isPhoneVerified && (
                <form onSubmit={handleVerifyPhone} className="mt-3 flex items-center gap-3">
                    <input
                        type="text"
                        value={otp}
                        onChange={(e) => setOtp(e.target.value.replace(/[^0-9]/g, ''))}
                        placeholder="Enter 6-digit OTP"
                        maxLength="6"
                        className="input-style flex-grow"
                        disabled={isProcessing}
                    />
                    <button type="submit" disabled={isProcessing} className="bg-indigo-600 text-white font-semibold py-2.5 px-4 rounded-md hover:bg-indigo-700 disabled:opacity-50">
                        Verify
                    </button>
                </form>
            )}
          </div>
        </div>

        {/* Status Messages */}
        {error && <p className="mt-4 text-sm text-red-400">{error}</p>}
        {message && <p className="mt-4 text-sm text-green-400">{message}</p>}

        <p className="mt-6 text-slate-500 text-sm">
          Once both are verified, you will be redirected automatically.
        </p>

        <button
          onClick={logout}
          className="mt-8 bg-slate-600 text-white font-semibold py-2 px-6 rounded-md hover:bg-slate-700 transition-colors"
        >
          Logout
        </button>
      </div>
    </div>
  );
};

export default VerifyAccountPage;

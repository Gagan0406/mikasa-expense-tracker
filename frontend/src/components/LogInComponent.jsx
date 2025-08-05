import React, { useState, useEffect } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL;

const LoginComponent = () => {
  const [formData, setFormData] = useState({ emailOrUsername: '', password: '' });
  const [error, setError] = useState('');
  const [isSubmitting, setIsSubmitting] = useState(false);
  
  const { login, user, isLoading: isSessionLoading } = useAuth(); 
  const navigate = useNavigate();

  useEffect(() => {
    if (isSessionLoading) {
      return;
    }
    if (user) {
      navigate('/');
    }
  }, [user, isSessionLoading, navigate]);

  const handleChange = (e) => {
    setFormData((prev) => ({ ...prev, [e.target.name]: e.target.value }));
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');
    setIsSubmitting(true);

    try {
      const response = await fetch(`${API_BASE_URL}/auth/login`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(formData),
      });

      const data = await response.json();

      if (!response.ok) {
        throw new Error(data.error || 'Failed to login');
      }
      
      login(data.user, data.token);

    } catch (err) {
      setError(err.message);
    } finally {
      setIsSubmitting(false);
    }
  };
  if (isSessionLoading || user) {
    return (
        <div className="w-full min-h-screen bg-gray-900 flex items-center justify-center">
            <p className="text-white text-xl">Loading...</p>
        </div>
    );
  }

  return (
    <main className="w-full min-h-screen bg-gray-900 bg-gradient-to-br from-gray-900 to-slate-800 flex items-center justify-center p-4">
      <div className="w-full max-w-md">
        <div className="text-center mb-6">
          <h1 className="text-4xl font-bold text-white mt-4">Welcome Back</h1>
          <p className="text-slate-400 mt-2">Sign in to continue to your account.</p>
        </div>

        <form onSubmit={handleSubmit} className="bg-slate-900/50 backdrop-blur-sm border border-slate-700 p-8 rounded-2xl shadow-2xl">
          <div className="space-y-6">
            <div>
              <label htmlFor="emailOrUsername" className="block text-sm font-medium text-slate-300 mb-2">Email or Username</label>
              <input type="text" id="emailOrUsername" name="emailOrUsername" value={formData.emailOrUsername} onChange={handleChange} placeholder="you@example.com" className="input-style" required disabled={isSubmitting} />
            </div>
            <div>
                <label htmlFor="password" className="block text-sm font-medium text-slate-300 mb-2">Password</label>
                <input type="password" id="password" name="password" value={formData.password} onChange={handleChange} placeholder="••••••••••" className="input-style" required disabled={isSubmitting} />
            </div>
            
            {error && <p className="text-sm text-red-400 text-center">{error}</p>}

            <button type="submit" className="w-full bg-indigo-600 text-white font-semibold py-3 px-4 rounded-md hover:bg-indigo-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-offset-slate-900 focus:ring-indigo-500 transition-colors duration-300 disabled:opacity-50 disabled:cursor-not-allowed" disabled={isSubmitting}>
              {isSubmitting ? 'Signing In...' : 'Sign In'}
            </button>
          </div>
        </form>

        <p className="text-center text-sm text-slate-400 mt-8">
          Don't have an account?{' '}
          <Link to="/register" className="font-semibold text-indigo-400 hover:text-indigo-300">Sign Up</Link>
        </p>
      </div>
    </main>
  );
};

const style = document.createElement('style');
style.innerHTML = `
  .input-style { display: block; width: 100%; background-color: rgb(30 41 59 / 1); border: 1px solid rgb(51 65 85 / 1); border-radius: 0.375rem; padding: 0.625rem 0.875rem; color: white; }
  .input-style:focus { outline: 2px solid transparent; outline-offset: 2px; --tw-ring-offset-shadow: var(--tw-ring-inset) 0 0 0 var(--tw-ring-offset-width) var(--tw-ring-offset-color); --tw-ring-shadow: var(--tw-ring-inset) 0 0 0 calc(2px + var(--tw-ring-offset-width)) var(--tw-ring-color); box-shadow: var(--tw-ring-offset-shadow), var(--tw-ring-shadow), var(--tw-shadow, 0 0 #0000); --tw-ring-offset-color: #0f172a; --tw-ring-color: #6366f1; }
  .input-style:disabled { opacity: 0.7; cursor: not-allowed; }
`;
document.head.appendChild(style);

export default LoginComponent;

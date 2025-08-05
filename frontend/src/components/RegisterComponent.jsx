/* eslint-disable no-unused-vars */
import React, { useState } from 'react';
import { Link } from 'react-router-dom';
import PhoneInput from 'react-phone-number-input';
import 'react-phone-number-input/style.css';
import { useAuth } from '../context/AuthContext'; 

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL;

const RegisterComponent = () => {

  const [formData, setFormData] = useState({ email: '', username: '', name: '', phone: '', password: '', confirmPassword: '' });
  const [error, setError] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  
  const { login } = useAuth(); 

  const handleChange = (e) => {
    setFormData((prev) => ({ ...prev, [e.target.name]: e.target.value }));
  };

  const handlePhoneChange = (value) => {
    setFormData((prev) => ({ ...prev, phone: value || '' }));
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');
    
    if (formData.password !== formData.confirmPassword) {
      setError("Passwords do not match.");
      return;
    }
    
    setIsLoading(true);

    try {
      const { confirmPassword, ...payload } = formData;

      const response = await fetch(`${API_BASE_URL}/auth/register`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(payload),
      });
      
      const data = await response.json();

      if (!response.ok) {
        throw new Error(data.error || 'Failed to register');
      }

      login(data.user, data.token);

    } catch (err) {
      setError(err.message);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <main className="w-full min-h-screen bg-gray-900 bg-gradient-to-br from-gray-900 to-slate-800 flex items-center justify-center p-4">
      <div className="w-full max-w-md">
        <div className="text-center mb-6">
          <h1 className="text-4xl font-bold text-white mt-4">Create an Account</h1>
          <p className="text-slate-400 mt-2">Join us and start your journey.</p>
        </div>

        <form onSubmit={handleSubmit} className="bg-slate-900/50 backdrop-blur-sm border border-slate-700 p-8 rounded-2xl shadow-2xl">
           <div className="space-y-4">
            {/* Form Fields */}
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div>
                <label htmlFor="name" className="block text-sm font-medium text-slate-300 mb-2">Full Name</label>
                <input type="text" id="name" name="name" value={formData.name} onChange={handleChange} placeholder="John Doe" className="input-style" required disabled={isLoading} />
              </div>
              <div>
                <label htmlFor="username" className="block text-sm font-medium text-slate-300 mb-2">Username</label>
                <input type="text" id="username" name="username" value={formData.username} onChange={handleChange} placeholder="johndoe" className="input-style" required disabled={isLoading} />
              </div>
            </div>
            
            <div>
              <label htmlFor="email" className="block text-sm font-medium text-slate-300 mb-2">Email Address</label>
              <input type="email" id="email" name="email" value={formData.email} onChange={handleChange} placeholder="you@example.com" className="input-style" required disabled={isLoading} />
            </div>

            <div>
              <label htmlFor="phone" className="block text-sm font-medium text-slate-300 mb-2">Phone Number</label>
              <PhoneInput id="phone" name="phone" international defaultCountry="IN" value={formData.phone} onChange={handlePhoneChange} className="phone-input-style" disabled={isLoading} />
            </div>

            <div>
              <label htmlFor="password" className="block text-sm font-medium text-slate-300 mb-2">Password</label>
              <input type="password" id="password" name="password" value={formData.password} onChange={handleChange} placeholder="••••••••••" className="input-style" required disabled={isLoading} />
            </div>

            <div>
              <label htmlFor="confirmPassword" className="block text-sm font-medium text-slate-300 mb-2">Confirm Password</label>
              <input type="password" id="confirmPassword" name="confirmPassword" value={formData.confirmPassword} onChange={handleChange} placeholder="••••••••••" className="input-style" required disabled={isLoading} />
            </div>
            
            {error && <p className="text-sm text-red-400 text-center">{error}</p>}

            <button type="submit" className="w-full bg-indigo-600 text-white font-semibold py-3 px-4 rounded-md hover:bg-indigo-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-offset-slate-900 focus:ring-indigo-500 transition-colors duration-300 mt-2 disabled:opacity-50" disabled={isLoading}>
              {isLoading ? 'Creating Account...' : 'Create Account'}
            </button>
          </div>
        </form>

        <p className="text-center text-sm text-slate-400 mt-8">
          Already have an account?{' '}
          <Link to="/login" className="font-semibold text-indigo-400 hover:text-indigo-300">Sign In</Link>
        </p>
      </div>
    </main>
  );
};

const style = document.createElement('style');
style.innerHTML = `
  /* Styles for Phone Input component */
  .phone-input-style .PhoneInputInput { background-color: transparent; border: none; color: white; outline: none; padding: 0.625rem 0.875rem; width: 100%; font-size: 1rem; line-height: 1.5rem; }
  .phone-input-style { display: flex; align-items: center; background-color: rgb(30 41 59 / 1); border: 1px solid rgb(51 65 85 / 1); border-radius: 0.375rem; transition: border-color 0.2s; }
  .phone-input-style:focus-within { border-color: #6366f1; box-shadow: 0 0 0 1px #6366f1; }
  .PhoneInputCountry { margin-left: 0.75rem; }
  .PhoneInputCountrySelect-arrow { opacity: 0.6; }
  .phone-input-style.PhoneInput--disabled { opacity: 0.7; cursor: not-allowed; }
`;
document.head.appendChild(style);

export default RegisterComponent;

/* eslint-disable react-refresh/only-export-components */
import React, { createContext, useState, useEffect, useContext } from 'react';
import { useNavigate } from 'react-router-dom';

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL;
const AuthContext = createContext(null);

export const useAuth = () => {
  return useContext(AuthContext);
};

export default function AuthProvider({ children }) {
  const [user, setUser] = useState(null);
  const [token, setToken] = useState(null);
  const [isLoading, setIsLoading] = useState(true);
  const navigate = useNavigate();

  useEffect(() => {
    try {
      const storedToken = localStorage.getItem('authToken');
      const storedUser = localStorage.getItem('authUser');
      
      if (storedToken && storedUser) {
        setToken(storedToken);
        setUser(JSON.parse(storedUser));
      }
    } catch (error) {
      console.error("Failed to parse auth data from localStorage", error);
      localStorage.removeItem('authToken');
      localStorage.removeItem('authUser');
    } finally {
      setIsLoading(false);
    }
  }, []);

  const login = (userData, authToken) => {
    setUser(userData);
    setToken(authToken);
    localStorage.setItem('authUser', JSON.stringify(userData));
    localStorage.setItem('authToken', authToken);

    if (userData.isEmailVerified && userData.isPhoneVerified) {
      navigate('/dashboard');
    } else {
      navigate('/verify-account');
    }
  };

  const logout = () => {
    setUser(null);
    setToken(null);
    localStorage.removeItem('authUser');
    localStorage.removeItem('authToken');
    navigate('/login');
  };

  const refreshUser = async () => {
    const currentToken = localStorage.getItem('authToken');
    if (!currentToken) return; 

    try {
      const response = await fetch(`${API_BASE_URL}/auth/me`, {
        headers: {
          'Authorization': `Bearer ${currentToken}`
        }
      });
      if (!response.ok) throw new Error('Session expired');
      
      const data = await response.json();
      setUser(data.user);
      localStorage.setItem('authUser', JSON.stringify(data.user));
    } catch (error) {
      console.error("Could not refresh user session:", error);
      logout();
    }
  };

  const authContextValue = {
    user,
    token,
    isLoading,
    login,
    logout,
    refreshUser, 
  };

  return (
    <AuthContext.Provider value={authContextValue}>
      {children}
    </AuthContext.Provider>
  );
};

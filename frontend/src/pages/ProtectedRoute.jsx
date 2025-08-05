import React from 'react';
import { Navigate, useLocation } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';

const ProtectedRoute = ({ children }) => {
  const { user, isLoading } = useAuth();
  const location = useLocation();

  if (isLoading) {
    return (
      <div className="w-full min-h-screen bg-gray-900 flex items-center justify-center">
        <p className="text-white text-xl">Loading session...</p>
      </div>
    );
  }

  if (!user) {
    return <Navigate to="/login" state={{ from: location }} replace />;
  }

  if (!user.isEmailVerified || !user.isPhoneVerified) {
    if (location.pathname !== '/verify-account') {
      return <Navigate to="/verify-account" replace />;
    }
  }

  if (user.isEmailVerified && user.isPhoneVerified) {
    if (location.pathname === '/verify-account') {
      return <Navigate to="/" replace />;
    }
  }

  return children;
};

export default ProtectedRoute;

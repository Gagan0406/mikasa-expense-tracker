import React from 'react';
import { useAuth } from '../context/AuthContext';

const DashboardPage = () => {
  const { user } = useAuth();

  return (
    <div className="w-full min-h-screen bg-gray-900 text-white flex flex-col items-center justify-center p-4">
      <div className="text-center">
        <h1 className="text-4xl font-bold">Dashboard</h1>
        <p className="text-xl mt-4 text-slate-300">
          Welcome back, <span className="text-indigo-400 font-semibold">{user?.name}!</span>
        </p>
        <p className="mt-2 text-slate-400">Your email and phone are verified. You have full access.</p>
        
      </div>
    </div>
  );
};

export default DashboardPage;
